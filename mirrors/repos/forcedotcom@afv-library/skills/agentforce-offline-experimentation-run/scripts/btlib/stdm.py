"""Read STDM query results.

The skill's fetch phases run Apex with `sf apex run --json` and print each result as one
debug line, `...|DEBUG|STDM_RESULT:<json>` (or `STDM_RESULT_<suffix>:` when one script
prints several). The source echo of the script also contains `STDM_RESULT:`, which is why
only the `|DEBUG|` form is matched. Inside a debug message the log writes '|' as '&#124;';
that is undone before parsing (the old skill parser kept the entity, e.g. in prompts).
bt_fetch.py's scripts print several pages per query, `STDM_RESULT_<query>_<page>:`.
"""

import json
import re

from .redact import redact

_MARKER = re.compile(r"\|DEBUG\|(STDM_RESULT(?:_[A-Za-z0-9_]+)?):")


class StdmError(Exception):
    pass


def parse_apex_logs(logs):
    """{marker: parsed JSON} for every STDM_RESULT debug line in an Apex log."""
    found = {}
    for m in _MARKER.finditer(logs):
        line_end = logs.find("\n", m.end())
        raw = logs[m.end():] if line_end < 0 else logs[m.end():line_end]
        # The debug log escapes its own field separator inside messages: '|' -> '&#124;'.
        raw = raw.strip().replace("&#124;", "|")
        try:
            found[m.group(1)] = json.loads(raw)
        except json.JSONDecodeError as e:
            raise StdmError(
                f"{m.group(1)}: debug line is not valid JSON ({e.msg} at char {e.pos} of {len(raw)}). "
                "The debug log was probably truncated (Apex caps a log at 20 MB); "
                "fetch fewer sessions or steps per batch.") from None
    return found


def parse_sf_output(data, where):
    """{marker: payload} from the parsed output of `sf apex run --json`: {} when its log has no
    STDM_RESULT line, None when data is not that output. A run that failed to compile or threw,
    and an error of the sf CLI itself (no org, expired session), raise StdmError."""
    if not isinstance(data, dict):
        return None
    res = data.get("result")
    if isinstance(res, dict) and "logs" in res:
        if res.get("success") is False or res.get("compiled") is False:
            msg = str(res.get("compileProblem") or res.get("exceptionMessage") or "unknown error")
            if res.get("compiled") is False and isinstance(res.get("line"), int) and res["line"] > 0:
                msg += f" (line {res['line']}, column {res.get('column')})"
            raise StdmError(f"{where}: Apex run failed: {redact(msg)[:300]}")
        return parse_apex_logs(res.get("logs") or "")
    if data.get("status") not in (None, 0) and isinstance(data.get("message"), str):
        name = data.get("name")
        raise StdmError(f"{where}: sf failed" + (f" ({name})" if isinstance(name, str) else "")
                        + f": {redact(data['message'])[:300]}")
    return None


def load_result_file(path):
    """{marker: payload} from an `sf apex run --json` output file.

    A file holding plain JSON (a list or an object without the sf CLI envelope) is
    returned as {None: payload}, so already-extracted files work too.
    """
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    found = parse_sf_output(data, path)
    if found is None:
        return {None: data}
    if not found:
        raise StdmError(f"{path}: no |DEBUG|STDM_RESULT line in the Apex log")
    return found


def load_conversations(paths):
    """Merge ConversationData lists from one or more details files.

    Accepts getMultipleConversationDetails output (a list), getConversationDetails output
    (one object), or several markers per file. The first copy of a session wins.
    Returns (conversations, duplicate_count).
    """
    convos, seen, dupes = [], set(), 0
    for path in paths:
        for payload in load_result_file(path).values():
            items = payload if isinstance(payload, list) else [payload]
            for c in items:
                if not isinstance(c, dict) or "turns" not in c or not isinstance(c.get("session_id"), str) \
                        or not c["session_id"].strip():
                    raise StdmError(f"{path}: expected ConversationData objects (a session_id, turns)")
                if c["session_id"] in seen:
                    dupes += 1
                    continue
                seen.add(c["session_id"])
                convos.append(c)
    return convos, dupes
