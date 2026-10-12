#!/usr/bin/env python3
"""
Generate the copy-ready Lab Prompts web page (GitHub Pages) from the SAME
single source (course_data.py + data_domainN.py) that drives the lab READMEs:

  docs/prompts/index.html   one section per lab: steps, prompt cards with a
                            Copy button, check formulas, sample prompts, Test It
  docs/index.html           redirect to prompts/
  docs/.nojekyll

Serve with GitHub Pages from the main branch /docs folder.
"""
import datetime, glob, html, importlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import course_data as C


def find_repo(start):
    env = os.environ.get("COURSE_REPO")
    if env and os.path.isdir(env):
        return env
    d = start
    for _ in range(8):
        d = os.path.dirname(d)
        if os.path.isdir(os.path.join(d, "courseware")) and os.path.isdir(os.path.join(d, "labs")):
            return d
    return os.path.dirname(os.path.dirname(start))


REPO = find_repo(HERE)
DOCS = os.path.join(REPO, "docs")
GH = f"https://github.com/{C.GITHUB_REPO}"

labs = []
for path in sorted(glob.glob(os.path.join(HERE, "data_domain[0-9]*.py"))):
    mod = importlib.import_module(os.path.basename(path)[:-3])
    for name in dir(mod):
        if re.fullmatch(r"DOMAIN\d+", name):
            labs.extend(getattr(mod, name))
labs.sort(key=lambda l: l["num"])
TOPICS = {t["num"]: t for t in C.TOPICS}


def slug(s):
    s = s.lower().replace("&", " and ")
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")


def folder_name(lab):
    # Folder named after the short lab theme (falls back to the full title).
    return f"lab-{lab['num']:02d}-{slug(lab.get('theme') or lab['title'])}"


from lab_prompts import LETTERS, parse_step, unwrap  # noqa: E402
from prompt_explanations import EXPLAIN, FORMULAS  # noqa: E402


# =========================================================================== render
def esc(s):
    return html.escape(s, quote=False)


def marked(s):
    """Escape, then highlight <placeholders> the learner must replace."""
    return re.sub(r"&lt;([a-z][^&\n]*?)&gt;", r"<mark>&lt;\1&gt;</mark>", esc(s))


def attr(s):
    return html.escape(s, quote=True)


def copy_btn(text, small=False):
    cls = "copy small" if small else "copy"
    return f'<button class="{cls}" type="button" data-copy="{attr(text)}">Copy</button>'



def _formulas_html(entry):
    """'Formulas explained' block: each formula with what every part of it does."""
    if not entry:
        return ""
    title, rows = entry
    items = "".join(f'<li><code>{esc(f)}</code><span>{esc(m)}</span></li>' for f, m in rows)
    return f'<div class="fx"><b>{esc(title)}</b><ul>{items}</ul></div>'


def render_lab(lab):
    n, fname = lab["num"], folder_name(lab)
    topic = TOPICS.get(lab["topic"], {})
    base_blob, base_raw = f"{GH}/blob/main/labs/{fname}", f"{GH}/raw/main/labs/{fname}"
    files = [f'<a href="{base_blob}/Lab-{n:02d}-Instructions.pdf">Instructions PDF</a>',
             f'<a href="{GH}/tree/main/labs/{fname}">Lab folder on GitHub</a>']
    files += [f'<a href="{base_raw}/{d}">Download {esc(os.path.basename(d))}</a>' for d in lab.get("data_files", [])]

    mode, steps_html, blocks, has_ph, k = None, [], [], False, 0
    what = EXPLAIN.get(n, {})
    for i, (instr, cmd) in enumerate(lab["steps"], 1):
        items, mode_next = parse_step(i, instr, cmd, mode)
        info = "".join(f'<pre class="info">{esc(t)}</pre>' for kind, _, t in items if kind == "info")
        prompts_here = sum(1 for it in items if it[0] == "prompt")
        tail = (f' <span class="see">→ Prompt{"s" if prompts_here > 1 else ""} '
                f'{", ".join(LETTERS[k + j] for j in range(prompts_here))}</span>') if prompts_here else ""
        steps_html.append(f"<li>{esc(instr)}{tail}{info}</li>")
        if i > 1 and items and all(kind == "info" for kind, _, _ in items):
            # a hands-on Excel step with no Copilot prompt (e.g. create the table) — show it in sequence
            blocks.append(
                f'<article class="prompt manual"><header><div><span class="pname">Lab {n} · Step {i}</span>'
                f'<span class="ptool">Do this in Excel first — no Copilot prompt</span></div></header>'
                f'<p>{esc(instr)}</p>{info}</article>')
        for kind, tag, body in items:
            if kind == "prompt":
                body = unwrap(body)
                has_ph |= "<mark>" in marked(body)
                assert LETTERS[k] in what, f"prompt_explanations.py: no explanation for Lab {n} Prompt {LETTERS[k]}"
                blocks.append(
                    f'<article class="prompt"><header><div><span class="pname">Lab {n} · Prompt {LETTERS[k]}</span>'
                    f'<span class="ptool">Step {i} · {esc(tag)}</span></div></header>'
                    f'<p class="what"><b>What it does:</b> {esc(what[LETTERS[k]])}</p>'
                    + _formulas_html(FORMULAS.get(n, {}).get(LETTERS[k])) +
                    f'<div class="pbar"><span>Prompt</span>{copy_btn(body)}</div>'
                    f"<pre>{marked(body)}</pre></article>")
                k += 1
            elif kind == "formulas":
                rows = []
                for lbl, f in body:
                    has_ph |= "<mark>" in marked(f)
                    lab_html = f'<span class="when">{esc(lbl)}</span>' if lbl else ""
                    rows.append(f'<li>{lab_html}<code class="q">{marked(f)}</code>{copy_btn(f, True)}</li>')
                blocks.append(
                    f'<article class="prompt formulas"><header><div><span class="pname">Lab {n} · Step {i}</span>'
                    f'<span class="ptool">{esc(tag)}{"" if tag.startswith("Option") else " — paste into an empty cell"}</span></div></header>'
                    f'<ul>{"".join(rows)}</ul></article>')
        mode = mode_next
    fx_extra = sorted(set(FORMULAS.get(n, {})) - set(LETTERS[:k]))
    assert not fx_extra, f"prompt_explanations.py: Lab {n} FORMULAS for prompts it does not have: {fx_extra}"
    extra = sorted(set(what) - set(LETTERS[:k]))
    assert not extra, f"prompt_explanations.py: Lab {n} explains prompts it does not have: {extra}"

    tables = list(dict.fromkeys(re.findall(r"\btbl[A-Z]\w+", " ".join(i + " " + c for i, c in lab["steps"]))))
    books = ", ".join(f"<b>{esc(os.path.basename(d))}</b>" for d in lab.get("data_files", []))
    first = re.search(r"Name the table (tbl\w+)", lab["steps"][1][1]) if len(lab["steps"]) > 1 else None
    make = (f" Start with Prompt A: Copilot turns the raw data into the table <code>{first.group(1)}</code>,"
            f" which every later prompt uses.") if first else ""
    banner = (f'<p class="open">Open {books} first. These prompts use '
              f'{", ".join(f"<code>{t}</code>" for t in tables)}.{make} '
              f"A prompt that names a different table belongs to another lab.</p>")
    asks = "".join(
        f'<li><span class="when">{esc(lbl)}</span><span class="q">{esc(p)}</span>{copy_btn(p, True)}</li>'
        for lbl, p in lab.get("sample_prompts", []))
    hint = ('<p class="hint">Replace the <mark>highlighted</mark> parts before you send.</p>' if has_ph else "")
    return (
        f'<section class="lab" data-lab="{n}" id="lab-{n}-section">'
        f'<p class="eyebrow">Lab {n}' + (f' · {esc(lab["theme"])}' if lab.get("theme") else '')
        + f' · Topic {lab["topic"]} · {lab.get("duration", "—")} min</p>'
        f'<h2>{esc(lab["title"])}</h2>'
        f'<p class="use"><b>Topic {lab["topic"]}:</b> {esc(topic.get("title", ""))}<br>'
        f'<b>Use:</b> {esc(lab["services"])}</p>'
        f'<p class="files">{" · ".join(files)}</p>{banner}'
        f'<details><summary>The steps</summary><ol>{"".join(steps_html)}</ol></details>'
        f"<h3>The prompts</h3>{hint}{''.join(blocks)}"
        f'<section class="ask"><h3>More prompts to try</h3><p>Copy one at a time, adapt it, and verify '
        f"every result with a formula.</p><ul>{asks}</ul></section>"
        f'<details class="test"><summary>Test it — what you should see</summary>' + ('<ul>' + ''.join(f'<li><b>{esc(c)}:</b> {esc(e)}</li>' for c, e in lab["checks"]) + '</ul>'
               if lab.get("checks") else f'<p>{esc(lab["test"])}</p>') + '</details>'
        f"</section>")


CSS = """
:root{--bg:#F7F9F7;--panel:#fff;--ink:#1D211F;--muted:#5D6762;--rule:#D5DDD8;
--accent:#107C41;--on-accent:#fff;--accent-bg:#EEF6F1;--ok:#185ABD;--mark:#FCE9B8;--code:#F1F4F2;--warn:#B7791F;--warn-bg:#FDF4E3}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--bg:#161A18;--panel:#1F2421;--ink:#ECF0EE;--muted:#AAB5AF;--rule:#36403B;
--accent:#4CC38A;--on-accent:#0E1A13;--accent-bg:#1E2B24;--ok:#7AB4FF;--mark:#5A4A1E;--code:#262C29;--warn:#E0A84A;--warn-bg:#2E2618}}
:root[data-theme="dark"]{--bg:#161A18;--panel:#1F2421;--ink:#ECF0EE;--muted:#AAB5AF;--rule:#36403B;
--accent:#4CC38A;--on-accent:#0E1A13;--accent-bg:#1E2B24;--ok:#7AB4FF;--mark:#5A4A1E;--code:#262C29;--warn:#E0A84A;--warn-bg:#2E2618}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:17px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Calibri,sans-serif}
.wrap{max-width:860px;margin:0 auto;padding:24px 16px 80px}
a{color:var(--accent)}
h1,h2{font-family:Cambria,Georgia,serif;font-weight:600;line-height:1.2}
h1{font-size:30px;margin:4px 0 6px}h2{font-size:26px;margin:4px 0 8px}
h3{font-size:15px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:28px 0 10px}
.eyebrow{margin:0;color:var(--accent);font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.sub{color:var(--muted);margin:0 0 18px}
nav{position:sticky;top:0;z-index:2;background:var(--bg);padding:10px 0;
border-bottom:1px solid var(--rule);display:flex;flex-wrap:wrap;gap:6px}
@media (max-width:600px){nav{flex-wrap:nowrap;overflow-x:auto}nav a{flex:none}}
nav a{display:inline-block;min-width:44px;text-align:center;padding:8px 10px;
border:1.5px solid var(--rule);border-radius:999px;color:var(--ink);text-decoration:none;font-weight:600;font-size:15px}
nav a[aria-current="true"]{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
.lab{padding-top:22px}
.use{color:var(--muted);margin:0 0 6px}
.files{margin:0 0 12px;font-size:15px}
details{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:8px 14px;margin:0 0 6px}
summary{cursor:pointer;font-weight:600}
details ol{margin:8px 0 4px;padding-left:22px}details li{margin:8px 0}
details.test{margin-top:24px}details.test p{margin:8px 0 4px}
.see{color:var(--accent);font-weight:700;font-size:15px;white-space:nowrap}
pre.info{margin:6px 0 2px;padding:8px 10px;background:var(--code);border-radius:6px;font-size:13px;color:var(--muted)}
.hint{margin:0 0 10px;color:var(--muted);font-size:15px}
mark{background:var(--mark);color:inherit;border-radius:3px;padding:0 2px}
.prompt{background:var(--panel);border:1px solid var(--rule);border-left:4px solid var(--accent);
border-radius:10px;margin:0 0 14px;overflow:hidden}
.prompt header{display:flex;justify-content:space-between;align-items:center;gap:12px;
padding:10px 14px;background:var(--accent-bg)}
.pname{font-weight:700;margin-right:8px}.ptool{color:var(--muted);font-size:15px}
pre{margin:0;padding:14px;white-space:pre-wrap;word-wrap:break-word;
font:15px/1.5 ui-monospace,Menlo,Consolas,monospace}
.what{margin:0;padding:12px 14px 0}
.fx{margin:10px 14px 0;padding:10px 12px;border:1px solid var(--rule);border-radius:8px;background:var(--code)}
.fx>b{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.fx ul{list-style:none;margin:6px 0 0;padding:0}.fx li{padding:8px 0;border-top:1px solid var(--rule)}
.fx li:first-child{border-top:0}
.fx code{display:block;font:13.5px/1.5 ui-monospace,Menlo,Consolas,monospace;word-break:break-word;margin-bottom:3px}
.fx span{font-size:15px}
.pbar{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 14px 0}
.pbar span{font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.prompt>pre{margin:8px 14px 14px;background:var(--code);border-radius:8px}
.copy{flex:none;font:inherit;font-weight:700;font-size:15px;color:var(--on-accent);background:var(--accent);
border:0;border-radius:8px;padding:9px 18px;cursor:pointer;min-height:40px}
.copy:hover{filter:brightness(1.08)}
.copy.done{background:var(--ok)}
.copy.small{font-size:13px;padding:5px 12px;min-height:32px}
.formulas{border-left-color:var(--ok)}
.manual{border-left-color:var(--warn);border-width:1.5px 1.5px 1.5px 4px;border-color:var(--warn)}
.manual header{background:var(--warn-bg)}
.manual p{margin:0;padding:12px 14px 4px}.manual pre.info{margin:4px 14px 14px}
.formulas ul,.ask ul{list-style:none;padding:0;margin:0}
.formulas li{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;padding:10px 14px;border-top:1px solid var(--rule)}
.formulas li:first-child{border-top:0}
code.q{flex:1 1 300px;font:14px/1.5 ui-monospace,Menlo,Consolas,monospace;word-break:break-word}
.ask li{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;background:var(--panel);
border:1px solid var(--rule);border-radius:10px;padding:10px 14px;margin:0 0 8px}
.ask .q{flex:1 1 300px}
.when{flex-basis:100%;font-size:13px;font-weight:700;color:var(--accent)}
.ask p{color:var(--muted);margin:0 0 10px;font-size:15px}
footer{margin-top:40px;color:var(--muted);font-size:14px}
.open{margin:0 0 12px;padding:10px 14px;border-radius:10px;background:var(--accent-bg);
border:1.5px solid var(--accent);font-size:15px}
.open code{font:14px ui-monospace,Menlo,Consolas,monospace;font-weight:700}
.pick{margin:28px 0;padding:18px 20px;border:2px dashed var(--accent);border-radius:12px}
.pick p{font-size:18px;font-weight:600;margin:0 0 10px}
.pick h4{margin:14px 0 4px;font-size:14px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.pick ul{margin:0;padding-left:20px}.pick li{margin:4px 0}
"""

JS = """
const labs=[...document.querySelectorAll('.lab')];
const links=[...document.querySelectorAll('nav a')];
function show(){
  const m=location.hash.match(/^#lab-(\\d+)$/);
  const n=m?m[1]:null;
  document.getElementById('pick').hidden=!!n;
  labs.forEach(s=>s.hidden=s.dataset.lab!==n);
  links.forEach(a=>a.setAttribute('aria-current',a.getAttribute('href')==='#lab-'+n));
}
addEventListener('hashchange',()=>{show();scrollTo(0,0)});
show();addEventListener('load',()=>scrollTo(0,0));
function fallback(t){const a=document.createElement('textarea');a.value=t;
  a.style.position='fixed';a.style.opacity='0';document.body.appendChild(a);
  a.select();try{document.execCommand('copy')}catch(e){}a.remove()}
document.addEventListener('click',async e=>{
  const b=e.target.closest('.copy');if(!b)return;
  const t=b.dataset.copy;
  try{await navigator.clipboard.writeText(t)}catch(err){fallback(t)}
  const old=b.textContent;b.textContent='Copied \\u2713';b.classList.add('done');
  setTimeout(()=>{b.textContent=old;b.classList.remove('done')},1800);
});
"""


def build_page():
    nav = "".join(f'<a href="#lab-{l["num"]}">{l["num"]}</a>' for l in labs)
    pick = ['<div id="pick" class="pick"><p>Which lab are you on? Click its number above — every prompt is '
            "labelled with its lab, so check it before you copy.</p>"]
    for t in C.TOPICS:
        pick.append(f'<h4>Topic {t["num"]} · {esc(t["title"])}</h4><ul>')
        pick += [f'<li><a href="#lab-{l["num"]}">Lab {l["num"]}'
                 + (f' · {esc(l["theme"])}' if l.get("theme") else '') + f' — {esc(l["title"])}</a></li>'
                 for l in labs if l["topic"] == t["num"]]
        pick.append("</ul>")
    pick.append("</div>")
    today = datetime.date.today().strftime("%-d %B %Y")
    return f"""<!doctype html>
<html lang="en-SG"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>Lab Prompts · Copilot in Excel</title>
<meta name="description" content="Copy-ready prompts for every lab of {esc(C.TITLE)} ({C.COURSE_CODE}).">
<style>{CSS}</style></head><body><div class="wrap">
<p class="eyebrow">{C.COURSE_CODE} · Copilot in Excel · {C.VERSION}</p>
<h1>Lab Prompts</h1>
<p class="sub">{esc(C.TITLE)}. Pick your lab, click <b>Copy</b>, then paste into the Copilot pane in Excel
(or into a cell, for check formulas). Verify every result. <a href="{GH}">Course repository</a>.</p>
<nav aria-label="Labs">{nav}</nav>
{"".join(pick)}
{"".join(render_lab(l) for l in labs)}
<footer>Built from the course source on {today}. BrightPath Talent Solutions and all lab data are
fictitious, for training only. Use only data you are authorised to process. © {esc(C.ORG)}.</footer>
</div><script>{JS}</script></body></html>
"""


os.makedirs(os.path.join(DOCS, "prompts"), exist_ok=True)
with open(os.path.join(DOCS, "prompts", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_page())
with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
    f.write('<!doctype html><meta charset="utf-8"><title>Lab Prompts</title>'
            '<meta http-equiv="refresh" content="0; url=prompts/"><a href="prompts/">Lab Prompts</a>\n')
open(os.path.join(DOCS, ".nojekyll"), "w").close()
print(f"Saved prompts page for {len(labs)} labs to {os.path.join(DOCS, 'prompts', 'index.html')}")
