"""
Parse a lab's steps (data_domainN.py) into its ordered Copilot prompts. Shared by
build_prompts_page.py (the web page) and build_labs.py (the pre-filled Prompt_Log
sheet in each lab workbook), so both always list the same prompts.

A step's code block holds prompts, check formulas or reference info. Labelled
paragraphs ("CHAT ONLY:", "CHECK (Allow editing):", "FOLLOW-UP:" ...) say which.
"""
import re

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# A step's code block holds prompts, check formulas or reference info. Labelled
# paragraphs ("CHAT ONLY:", "CHECK:", "FOLLOW-UP:" ...) say which.
LABEL = re.compile(r"^(CHAT ONLY|ALLOW EDITING|PLAN MODE|PROMPT|CHECK FORMULAS|CHECK|LOG|FOLLOW-UP EXAMPLE|FOLLOW-UP|"
                   r"OPTION [A-Z]|Then|Expected after refresh)([^:\n]*):[ \t]*(.*)$")
MODES = [("Chat only", "Chat only"), ("Plan mode", "Plan"), ("Allow editing", "Allow editing")]
INFO_LINE = re.compile(r"^[A-Za-z_][A-Za-z_ ]*\s+:\s")      # "Table name : tblApplications"
FORMULA_LINE = re.compile(r"^(.*?\S)\s+(=\S.*)$")           # "Active headcount   =COUNTIFS(...)"
CELL_PAIR = re.compile(r"^(A\d+)\s+(.*?)\s+(B\d+)\s+(=.*)$")  # "A3 Total fee   B3 =SUM(...)"

STRUCT = re.compile(r"^(\(?\d+\)\s|[A-Z][A-Za-z0-9_]*( [A-Za-z0-9_]+)?:|- |=|[A-Z]\d+ )|\s=[A-Z<(]")


def unwrap(body):
    """Undo the source's ~100-column hard wraps; keep structural breaks (labels, numbered/indented items)."""
    out = []
    for line in body.split("\n"):
        s, indent = line.lstrip(), len(line) - len(line.lstrip())
        prev = out[-1].rstrip() if out else ""
        structural = (not out or not s or prev.endswith(":") or STRUCT.search(s)
                      or (1 <= indent <= 4 and s[0].isupper())
                      # one rule / one sentence per line: rules lists and "## HEADING" lines stay separate
                      or s.startswith("##") or prev.startswith("##")
                      or (prev.endswith((".", "?")) and s[0].isupper()))
        if structural:
            out.append(line.rstrip())
        else:
            out[-1] = out[-1].rstrip() + " " + s.rstrip()
    return "\n".join(out)


def reflow(cmd):
    """A step's code block for print: prompt paragraphs are unwrapped so they wrap naturally;
    reference blocks ("Table : ...") and formula lines keep their line breaks."""
    out = []
    for para in re.split(r"\n\s*\n", cmd.strip("\n")):
        lines = para.split("\n")
        out.append(para if any(INFO_LINE.match(l.strip()) for l in lines) else unwrap(para))
    return "\n\n".join(out)


def modes_in(text):
    hits = sorted((m.start(), name) for pat, name in MODES for m in re.finditer(pat, text))
    return [name for _, name in hits]


def split_formulas(body):
    """One item per line starting with '='; indented continuation lines are joined."""
    out = []
    for line in body.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith("=") or not out:
            out.append(s)
        else:
            out[-1] += " " + s
    return [("", f) for f in out]


def setup_formulas(body):
    out = []
    for line in body.split("\n"):
        m = CELL_PAIR.match(line.strip())
        if m:
            out.append((f"{m.group(1)} {m.group(2)} · {m.group(3)}", m.group(4)))
        else:
            m = FORMULA_LINE.match(line.strip())
            out.append((m.group(1), m.group(2)))
    return out


def split_changes(body):
    """'One change at a time' blocks: one prompt per numbered item or per line."""
    if re.search(r"^\d\)\s", body, re.M):
        parts = re.split(r"^\d\)\s+", body, flags=re.M)
        return [re.sub(r"\s*\n\s*", " ", p).strip() for p in parts if p.strip()]
    return [l.strip() for l in body.split("\n") if l.strip()]


def parse_step(num, instr, cmd, mode):
    """Return (items, carried_mode). Items: ('prompt', tag, text) | ('formulas', tag, [(label, f)])
    | ('info', tag, text)."""
    found = modes_in(instr)
    step_mode = found[0] if found else mode
    if re.search(r"^(CHAT ONLY|ALLOW EDITING|PLAN MODE):", cmd, re.M):   # explicit labels mark the exceptions
        step_mode = mode or step_mode
    carry = next(iter(reversed(found)), mode)
    items = []
    if not cmd.strip():
        return items, carry
    one_by_one = re.search(r"one change at a time|one prompt per change", instr)
    for para in re.split(r"\n\s*\n", cmd.strip("\n")):
        lines = para.rstrip().split("\n")
        m = LABEL.match(lines[0].strip())
        label = (m.group(1) + m.group(2)).strip() if m else None
        body = "\n".join(([m.group(3)] if m and m.group(3) else []) + lines[1:]) if m else para
        body = "\n".join(l.rstrip() for l in body.split("\n")).strip("\n")
        if label is None and one_by_one:
            for chunk in split_changes(body):
                cm = LABEL.match(chunk)
                if cm:
                    items.append(("prompt", cm.group(1).capitalize(), cm.group(3)))
                else:
                    items.append(("prompt", step_mode, chunk))
            continue
        if label is None:
            if num == 1 or INFO_LINE.match(lines[0]):
                items.append(("info", "Reference", body))
            elif all(FORMULA_LINE.match(l.strip()) or l.strip().startswith("=") for l in lines if l.strip()):
                items.append(("formulas", "Type these yourself", setup_formulas(body)))
            elif body.startswith("If ") and 'ask: "' in body:
                cond, ask = body.split('ask: "', 1)
                items.append(("prompt", "If needed · " + cond[3:].strip(" ,"), ask.rstrip('"')))
            else:
                items.append(("prompt", step_mode, body))
        elif label.startswith(("CHECK", "LOG")) and not body.lstrip().startswith("="):
            # a check or log done by Copilot: "CHECK (Allow editing)" -> "Check · Allow editing"
            pm = re.search(r"\(([^)]*)\)", label)
            items.append(("prompt", label.split(" ")[0].capitalize() + (" · " + pm.group(1) if pm else ""), body))
        elif label.startswith("CHECK"):
            sub = label[len("CHECK FORMULAS") if label.startswith("CHECK FORMULAS") else len("CHECK"):].strip()
            items.append(("formulas", "Check " + sub if sub else "Check", split_formulas(body)))
        elif label.startswith("Expected"):
            items.append(("info", label, body))
        elif label.startswith("OPTION"):
            if body.lstrip().startswith("="):
                items.append(("formulas", "Option" + label[6:], [("", re.sub(r"\s*\n\s*", " ", body.strip()))]))
            else:
                items.append(("prompt", "Option" + label[6:], body))
        elif label in ("CHAT ONLY", "ALLOW EDITING", "PLAN MODE"):
            items.append(("prompt", "Plan" if label == "PLAN MODE" else label.capitalize(), body))
        elif label.startswith("PROMPT"):
            pm = re.search(r"\(([^)]*)\)", label)
            items.append(("prompt", pm.group(1) if pm else step_mode, body))
        else:  # Then / FOLLOW-UP*
            items.append(("prompt", "Follow-up" if label == "Then" else label.capitalize(), body))
    return items, carry


# Prompt_Log "Mode (Chat only / Plan / Allow editing)" column
_LOG_MODE = {"Chat only": "Chat only", "Plan": "Plan", "Allow editing": "Allow editing"}


def prompt_rows(lab):
    """Every Copilot prompt in step order: dicts with step, letter, tag, mode and the unwrapped text."""
    rows, mode = [], None
    for i, (instr, cmd) in enumerate(lab["steps"], 1):
        items, mode_next = parse_step(i, instr, cmd, mode)
        for kind, tag, body in items:
            if kind != "prompt":
                continue
            m = tag if tag.endswith("Copilot web") else next((v for k, v in _LOG_MODE.items() if k in tag), None)
            if m is None:  # follow-ups and options run in the mode of the prompt before them
                m = rows[-1]["mode"] if rows and rows[-1]["step"] == i else _LOG_MODE.get(mode_next or mode, "Allow editing")
            rows.append(dict(step=i, letter=LETTERS[len(rows)], tag=tag, mode=m, text=unwrap(body)))
        mode = mode_next
    return rows
