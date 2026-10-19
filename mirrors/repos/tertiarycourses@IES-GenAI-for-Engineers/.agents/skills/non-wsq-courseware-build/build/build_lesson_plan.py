#!/usr/bin/env python3
"""Generate the non-WSQ Lesson Plan (LP) DOCX in the Tertiary house format.

Cover page + Document Version Control Record + auto TOC + Arial 11pt body +
colour-coded daily schedule tables (9:30am-6:30pm, 8 training hours/day, 1h
lunch, tea within). NO assessment, funding, SSG or TRAQOM content. Day themes,
topics, schedule and labs all come from course_data + the domain data files so
the LP stays aligned with the deck, guide and labs.
"""
import os, sys
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import course_data as C
# Dynamic domain import — supports ANY number of data_domainN.py files.
import importlib, glob as _glob
def _load_domains():
    acts=[]
    for f in sorted(_glob.glob(os.path.join(HERE,"data_domain[0-9]*.py")),
                    key=lambda q:int("".join(c for c in os.path.basename(q) if c.isdigit()) or 0)):
        n="".join(c for c in os.path.basename(f) if c.isdigit())
        acts+=getattr(importlib.import_module(os.path.basename(f)[:-3]),f"DOMAIN{n}",[])
    return acts
ACT=_load_domains()
import prodoc
def _find_repo(start):
    env=os.environ.get("COURSE_REPO")
    if env and os.path.isdir(env): return env
    d=start
    for _ in range(8):
        d=os.path.dirname(d)
        if os.path.isdir(os.path.join(d,"courseware")) and os.path.isdir(os.path.join(d,"labs")): return d
    return os.path.dirname(os.path.dirname(HERE))
REPO=_find_repo(HERE); ASSETS=os.path.join(os.path.dirname(HERE),"assets")

BRAND=RGBColor(0x1F,0x6F,0xEB); DARK=RGBColor(0x11,0x18,0x27); GREY=RGBColor(0x55,0x5B,0x66)
HEADER_FILL="1F6FEB"; TOPIC_FILL="E8F0FE"; BREAK_FILL="FFF4E5"; LUNCH_FILL="FDE9D9"; ASSESS_FILL="E8F7EE"

def lab_titles(nums):
    return "; ".join(f"Lab {a['num']}" + (f" ({a['theme']})" if a.get("theme") else "") + f": {a['title']}"
                     for a in ACT if a['num'] in nums)

# ------------------------------------------------ schedule
# NON-WSQ: no assessment blocks. The schedule is supplied by course_data.SCHEDULE
# as {day: (theme, [(start, end, mins, kind, text), ...])} where kind is one of
# admin/topic/lab/break/lunch/recap. `lab_titles([...])` is available to course
# authors for building the activity text from the lab data.
SCHEDULE=C.SCHEDULE(lab_titles) if callable(getattr(C,"SCHEDULE",None)) else getattr(C,"SCHEDULE",{})
if not SCHEDULE:
    raise SystemExit("course_data.py must define SCHEDULE (dict or callable taking lab_titles)")

# Scheduled minutes per training day, excluding lunch. Defaults to the 8-hour day
# (480) but non-WSQ courses set their own — e.g. a 15-hour, 2-day course is 450.
DAY_MINUTES=getattr(C,"DAY_MINUTES",480)
INSTRUCTIONAL_MINUTES=getattr(C,"INSTRUCTIONAL_MINUTES",DAY_MINUTES)

# ------------------------------------------------ build document
doc=Document()
normal=doc.styles["Normal"]; normal.font.name="Arial"; normal.font.size=Pt(11)
prodoc.style_headings(doc)

prodoc.add_cover_page(doc,"LESSON PLAN",C.TITLE,C.VERSION.lstrip("v"),
                      org_logo=getattr(C,"ORG_LOGO",os.path.join(ASSETS,"tertiary-infotech-logo.png")),
                      course_logo=None, course_code=C.COURSE_CODE or None)
prodoc.add_version_control(doc,getattr(C,"VERSION_HISTORY",[(C.VERSION.lstrip("v"),C.VERSION_DATE,"Initial release.",C.TRAINER)]))
prodoc.add_toc(doc)

def H(text,level=1):
    h=doc.add_heading(text,level=level)
    h.paragraph_format.keep_with_next=True
    return h

def prevent_row_split(row):
    trPr=row._tr.get_or_add_trPr()
    if trPr.find(qn("w:cantSplit")) is None:
        trPr.append(OxmlElement("w:cantSplit"))

def repeat_header(row):
    trPr=row._tr.get_or_add_trPr()
    if trPr.find(qn("w:tblHeader")) is None:
        flag=OxmlElement("w:tblHeader")
        flag.set(qn("w:val"),"true")
        trPr.append(flag)

H("Course Information",1)
info=[("Course Title",C.TITLE)]+([("Course Reference",C.COURSE_CODE)] if C.COURSE_CODE else [])+[
      ("Training Provider",C.ORG+("  ("+C.UEN.replace('UEN: ','UEN ')+")" if C.UEN else "")),
      ("Duration",
       f"{C.DAYS} day{'s' if C.DAYS>1 else ''} · "
       f"{C.DAYS*INSTRUCTIONAL_MINUTES/60:g} instructional hours "
       f"({C.DAYS*DAY_MINUTES/60:g} scheduled hours excluding lunch, including tea breaks)"),
      ("Daily Timing",getattr(C,"DAILY_TIMING","9:30 am – 6:30 pm (1-hour lunch; tea breaks within training time)")),
      ("Mode",getattr(C,"MODE","Instructor-led, hands-on practical labs")),
      ("Trainer",C.TRAINER)]
t=doc.add_table(rows=0,cols=2); t.style="Table Grid"
for k,v in info:
    c=t.add_row().cells; c[0].text=""; r=c[0].paragraphs[0].add_run(k); r.bold=True; r.font.size=Pt(10)
    prevent_row_split(t.rows[-1])
    prodoc._shade_cell(c[0],TOPIC_FILL)
    c[1].text=""; c[1].paragraphs[0].add_run(v).font.size=Pt(10)
prodoc.set_col_widths(t,[Inches(1.7),Inches(4.8)])

H("Learning Outcomes",1)
doc.add_paragraph("On completion of this course, learners will be able to:")
for lo in C.LEARNING_OUTCOMES:
    p=doc.add_paragraph(style="List Bullet"); p.add_run(lo).font.size=Pt(10.5)

# NON-WSQ: there is NO assessment for this course. Learning is reinforced through
# the hands-on labs and their verification steps instead.
H("Learning Reinforcement",1)
for a_ in ["Every topic is followed by hands-on labs that learners complete on their own machine.",
           "Each lab ends with a 'Test it' verification step so learners can confirm their own progress.",
           "The trainer circulates during lab time to give individual feedback and unblock learners.",
           "Each topic closes with a recap mapped back to the course learning outcomes."]:
    p_=doc.add_paragraph(style="List Bullet"); p_.add_run(a_).font.size=Pt(10.5)

def set_cell(cell,text,bold=False,size=9.5,color=None,fill=None,align=None):
    cell.text=""; p=cell.paragraphs[0]
    if align: p.alignment=align
    r=p.add_run(text); r.bold=bold; r.font.size=Pt(size); r.font.name="Arial"
    if color: r.font.color.rgb=color
    if fill: prodoc._shade_cell(cell,fill)

KIND_FILL={"topic":TOPIC_FILL,"break":BREAK_FILL,"lunch":LUNCH_FILL,
           "admin":"F3F5F8","recap":"F3F5F8","lab":None}

H("Course Schedule",1)
for day,(theme,rows) in SCHEDULE.items():
    H(f"Day {day} — {theme}",2)
    tbl=doc.add_table(rows=0,cols=3); tbl.style="Table Grid"; tbl.alignment=WD_TABLE_ALIGNMENT.CENTER
    hdr=tbl.add_row().cells
    repeat_header(tbl.rows[0]); prevent_row_split(tbl.rows[0])
    for i,htext in enumerate(["Time","Duration","Topic / Activity"]):
        set_cell(hdr[i],htext,bold=True,size=10,color=RGBColor(0xFF,0xFF,0xFF),fill=HEADER_FILL)
    training=0
    for start,end,mins,kind,text in rows:
        cells=tbl.add_row().cells; fill=KIND_FILL.get(kind)
        prevent_row_split(tbl.rows[-1])
        set_cell(cells[0],f"{start}–{end}",bold=(kind=="topic"),size=9.5,fill=fill)
        set_cell(cells[1],f"{mins} min",size=9.5,fill=fill)
        set_cell(cells[2],text,bold=(kind=="topic"),size=9.5,fill=fill)
        if kind!="lunch": training+=mins
    # widths
    prodoc.set_col_widths(tbl,[Inches(1.1),Inches(0.85),Inches(4.55)])
    # `training` excludes lunch but still counts tea breaks, so report both it and
    # the instructional total (tea breaks removed) — the latter is the figure the
    # advertised course duration is based on.
    tea=sum(m for _s,_e,m,k,_t in rows if k=="break")
    inst=training-tea
    r=doc.add_paragraph().add_run(
        f"Total scheduled time: {training} minutes ({training/60:g} hours) excluding lunch — "
        f"of which {inst} minutes ({inst/60:g} hours) are instructional, plus {tea} minutes of tea breaks.")
    r.italic=True; r.font.size=Pt(9.5); r.font.color.rgb=GREY
    assert training==DAY_MINUTES, f"Day {day} scheduled minutes = {training}, expected {DAY_MINUTES}"

H("Lab Reference (aligned to course topics)",1)
tt=doc.add_table(rows=0,cols=3); tt.style="Table Grid"
hdr=tt.add_row().cells
repeat_header(tt.rows[0]); prevent_row_split(tt.rows[0])
for i,htext in enumerate(["Topic","Coverage","Labs"]):
    set_cell(hdr[i],htext,bold=True,size=10,color=RGBColor(0xFF,0xFF,0xFF),fill=HEADER_FILL)
# NON-WSQ: there is no exam to weight against, so "Coverage" reports each topic's
# share of the hands-on labs — derived, so it can never drift from the lab data.
_total_labs=len(ACT) or 1
for tp in C.TOPICS:
    acts=[a for a in ACT if a["topic"]==tp["num"]]
    cells=tt.add_row().cells
    prevent_row_split(tt.rows[-1])
    set_cell(cells[0],f"Topic {tp['code']}: {tp['title']}",bold=True,size=9.5,fill=TOPIC_FILL)
    coverage=tp.get("weighting") or f"{len(acts)} of {_total_labs} labs ({round(100*len(acts)/_total_labs)}%)"
    set_cell(cells[1],coverage,size=9.5,fill=TOPIC_FILL)
    set_cell(cells[2],", ".join(f"Lab {a['num']}" for a in acts),size=9.5)
prodoc.set_col_widths(tt,[Inches(3.4),Inches(1.3),Inches(1.8)])

prodoc.add_page_numbers(doc)
prodoc.enable_update_fields(doc)
OUT=os.path.join(REPO,"courseware",f"LP-{C.SHORT_TITLE}.docx")
doc.save(OUT)
print("Saved",OUT)
