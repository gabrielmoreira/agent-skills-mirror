"""Publish a C34-style, copy-ready prompt library from the authoritative lab steps."""
from pathlib import Path
from html import escape
import re
import course_data as C
from maintenance_labs import LABS

import os
ROOT = Path(os.environ['COURSE_REPO']) if os.environ.get('COURSE_REPO') else Path(__file__).resolve().parents[4]
REL = getattr(C, 'PROMPTS_RELATIVE', False)  # bundled page: link files relative to docs/prompts/
REPO = '../..' if REL else f'https://github.com/{C.GITHUB_REPO}'
RAW = '../..' if REL else f'https://raw.githubusercontent.com/{C.GITHUB_REPO}/main'
TREE = '../..' if REL else f'{REPO}/tree/main'
CSS = '''
:root{color-scheme:light;--bg:#f4f1e8;--panel:#fff;--ink:#232923;--muted:#596359;--accent:#405c42;--rule:#d5d9cd;--code:#f0f3ed;--accent-bg:#e8eee4}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Calibri,sans-serif}
.wrap{overflow-wrap:anywhere;max-width:860px;margin:auto;padding:24px 16px 70px}a{color:var(--accent)}h1,h2{font-family:Cambria,Georgia,serif;line-height:1.2;font-weight:600}h1{font-size:34px;margin:6px 0}h2{font-size:28px;margin:8px 0 12px}
.eyebrow{color:var(--accent);font-size:13px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;margin:0}.sub,.use{color:var(--muted)}nav{max-width:100%;position:sticky;top:0;z-index:2;background:var(--bg);padding:10px 0;border-bottom:1px solid var(--rule);display:flex;gap:6px;flex-wrap:wrap}
nav a{min-width:44px;padding:8px 12px;border:1.5px solid var(--rule);border-radius:24px;text-align:center;text-decoration:none;font-weight:600;color:var(--ink)}nav a[aria-current="true"]{background:var(--accent);color:white;border-color:var(--accent)}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #1f6feb;outline-offset:4px}
.pick{margin:28px 0;padding:18px 20px;border:2px dashed var(--accent);border-radius:12px}.pick h3{font-size:15px;margin:18px 0 6px}.pick ul{padding-left:22px}.pick li{margin:6px 0}.lab{padding-top:22px}.files{font-size:15px}.files a{display:inline-block;margin-bottom:7px}.open{padding:12px 14px;background:var(--accent-bg);border:1px solid var(--rule);border-radius:10px;font-size:15px}details{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:10px 14px;margin:14px 0}summary{cursor:pointer;font-weight:600}details li{margin:10px 0}h3{font-size:15px;letter-spacing:.04em;text-transform:uppercase;color:var(--accent);margin:26px 0 10px}
.prompt{background:var(--panel);border:1px solid var(--rule);border-left:4px solid var(--accent);border-radius:10px;margin:0 0 16px;overflow:hidden}.prompt header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 14px;background:var(--accent-bg)}.ptool{font-size:14px;color:var(--muted);display:block}.copy{font:inherit;font-size:15px;font-weight:700;padding:9px 18px;min-height:44px;border:0;border-radius:8px;background:var(--accent);color:white;cursor:pointer;flex:none}.copy:hover{filter:brightness(1.12)}.copy.done{background:#1d6f40}
pre{margin:12px 14px 14px;padding:14px;background:var(--code);border-radius:8px;white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.5 ui-monospace,Menlo,Consolas,monospace}footer{margin-top:40px;border-top:1px solid var(--rule);padding-top:18px;color:var(--muted);font-size:14px}[hidden]{display:none!important}.status{font-size:14px;min-height:22px;color:var(--muted)}
.step{background:var(--panel);border:1px solid var(--rule);border-radius:10px;padding:14px 16px;margin:16px 0}.step h4{margin:0 0 6px;font-size:16px;color:var(--accent)}.step p{margin:0 0 10px}.step .prompt{margin:10px 0 0}
@media(max-width:600px){nav{flex-wrap:nowrap;overflow:auto}nav a{flex:none}.prompt header{align-items:flex-start}h1{font-size:30px}h2{font-size:25px}.wrap{padding-top:16px}pre{font-size:13px}}
'''
JS = '''
const sections=[...document.querySelectorAll('.lab')];
function selectLab(){const match=location.hash.match(/^#lab-(1[0-9]|[1-9])$/);const active=match?match[1]:null;sections.forEach(s=>s.hidden=active!==s.dataset.lab);document.getElementById('pick').hidden=!!active;document.querySelectorAll('nav a').forEach(a=>{if(a.hash===location.hash&&active)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')});if(active)window.scrollTo(0,0)}
window.addEventListener('hashchange',selectLab);selectLab();
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{const target=document.getElementById(button.dataset.copy);const text=target.textContent;const status=document.getElementById('copy-status');try{await navigator.clipboard.writeText(text);button.textContent='Copied';button.classList.add('done');status.textContent=button.dataset.label+' copied.';setTimeout(()=>{button.textContent='Copy';button.classList.remove('done')},1800)}catch(e){const selection=window.getSelection();const range=document.createRange();range.selectNodeContents(target);selection.removeAllRanges();selection.addRange(range);status.textContent='Clipboard unavailable. The prompt is selected; press Ctrl+C or Cmd+C.'}}));
'''

def split_prompts(command):
    """App/mode labels are metadata; each Copy button contains one request only."""
    pattern=r'(?m)^(EXCEL - [A-Z ]+|WORD COPILOT|POWERPOINT COPILOT|OUTLOOK COPILOT|MICROSOFT 365 COPILOT WEB|AGENT BUILDER - [A-Z ]+|AGENT - [A-Z ]+):\s*\n'
    hits=list(re.finditer(pattern,command))
    if not hits:return [('Copilot',command.strip())]
    return [(hit.group(1),command[hit.end():(hits[i+1].start() if i+1<len(hits) else len(command))].strip()) for i,hit in enumerate(hits)]

def build_page(labs):
    parts=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',f'<title>Lab Prompts | {escape(C.TITLE)}</title>',f'<meta name="description" content="Copy-ready prompts for {escape(C.TITLE)}: step-by-step lab instructions with one-click Copy buttons."><style>{CSS}</style></head><body><main class="wrap">',f'<p class="eyebrow">{escape(getattr(C,"PROMPTS_EYEBROW",C.COURSE_CODE))} · Microsoft 365 Copilot · {C.VERSION}</p><h1>Lab Prompts</h1>',f'<p class="sub">{escape(C.TITLE)}. {escape(getattr(C,"PROMPTS_TAGLINE",""))}<br>Pick your lab, follow each step in order, click <b>Copy</b> on the step\'s prompt and paste it into the app named on the card. Verify every result.</p>', '<nav aria-label="Labs">'+''.join(f'<a href="#lab-{a["num"]}" aria-label="Lab {a["num"]}">Lab {a["num"]}</a>' for a in labs)+'</nav><p id="copy-status" class="status" role="status" aria-live="polite"></p>', '<div id="pick" class="pick"><b>Which lab are you on?</b><p>Choose a lab number. Each lab has an instruction PDF and a data folder. Use the PDF for the complete procedure.</p><p><b>One coherent theme:</b> Northstar Water Services, a fictional water-pipe maintenance and service company. Carry the same work orders from Excel cleaning into a Word brief, reusable skill, interactive dashboard and PowerPoint decision deck.</p>'+getattr(C,'PROMPTS_DAY_NOTE','')+'']
    for topic in C.TOPICS:
        parts.append(f'<h3>Topic {topic["num"]} · {escape(topic["title"])}</h3><ul>')
        parts.extend(f'<li><a href="#lab-{a["num"]}">Lab {a["num"]} · {escape(a["title"])}</a></li>' for a in labs if a['topic']==topic['num'])
        parts.append('</ul>')
    parts.append('</div>')
    md=[f'# {C.TITLE} - Prompt Library\n',f'[Open the prompts page with Copy buttons]({C.PROMPTS_PAGE})\n']
    for lab in labs:
        n=lab['num'];folder='lab-'+f'{n:02d}-'+re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', lab['theme'].lower())).strip('-');path=f'labs/{folder}';pdf=f'{path}/Lab-{n:02d}-Instructions.pdf'
        parts.extend([f'<section class="lab" data-lab="{n}" id="lab-{n}" hidden><p class="eyebrow">Lab {n} · Topic {lab["topic"]} · {lab["duration"]} min</p><h2>{escape(lab["title"])}</h2>', f'<p class="use">{escape(lab["services"])}</p>',f'<p class="files"><a href="{RAW}/{pdf}">Instructions PDF</a> · <a href="{TREE}/{path}/data/">Data folder</a> · <a href="{TREE}/{path}/">Lab folder</a></p>',f'<p class="open">{escape(lab["goal"])}<br>Provide the actual source file or verified evidence in each app. App chats do not share context.</p>'])
        md.extend([f'\n## Lab {n}: {lab["title"]}\n',f'[Instruction PDF](../../{pdf}) · [Data folder](../../{path}/data/) · [Copy buttons]({C.PROMPTS_PAGE}#lab-{n})\n'])
        for i,(instr,cmd) in enumerate(lab['steps'],1):
            parts.append(f'<div class="step" id="lab-{n}-step-{i}"><h4>Step {i}</h4><p>{escape(instr)}</p>')
            md.extend([f'### Step {i}\n',f'{instr}\n'])
            if cmd:
                for part,(app,prompt) in enumerate(split_prompts(cmd),1):
                    label=f'Lab {n} · Step {i} · Prompt {part}';pid=f'prompt-{n}-{i}-{part}'
                    parts.append(f'<article class="prompt"><header><div><b>{label}</b><span class="ptool">{escape(app)}</span></div><button type="button" class="copy" data-copy="{pid}" data-label="{label}" aria-label="Copy {label}">Copy</button></header><pre id="{pid}">{escape(prompt)}</pre></article>')
                md.append(f'```text\n{cmd}\n```\n')
            parts.append('</div>')
        parts.append('<details><summary>Test it</summary><ul>'+''.join(f'<li><b>{escape(key)}:</b> {escape(value)}</li>' for key,value in lab['checks'])+'</ul></details></section>')
    parts.extend([f'<footer>{escape(C.LAB_NOTE)}<p class="powered-by">{escape(getattr(C,"PROMPTS_FOOTER","Powered by Tertiary Infotech Academy Pte Ltd"))}</p></footer></main>',f'<script>{JS}</script></body></html>'])
    docs=ROOT/'docs/prompts';docs.mkdir(parents=True,exist_ok=True)
    (docs/'index.html').write_text('\n'.join(parts))
    (docs/'README.md').write_text('\n'.join(md))
    print(f'Built {len(labs)} linked prompt sections.')

if __name__=='__main__':build_page(LABS)
