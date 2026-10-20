#!/usr/bin/env python3
"""Generate a NON-WSQ course slide deck (all-white Tertiary house style).

Design helpers match the Tertiary house system (cover, section, content,
two_col, cards3, big_statement, step_slide, test_slide, brk). Content is driven
entirely by course_data.py + data_domainN.py so the deck stays 100% aligned with
the LP, LG and labs.

NON-WSQ: contains NO assessment, funding, SSG/SkillsFuture, TRAQOM or digital
attendance content. The assessment block a WSQ deck would carry is replaced by a
"How You'll Learn" flow, and the deck closes on the wrap-up + Thank You.
"""
import os, sys, re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import course_data as C

# Import data_domain1..N dynamically so a course can have ANY number of domains
# (the WSQ engine hard-coded exactly five). Domains are loaded in order and
# concatenated into one contiguous activity list.
import importlib, glob as _glob
def _load_domains():
    acts=[]
    files=sorted(_glob.glob(os.path.join(HERE,"data_domain[0-9]*.py")),
                 key=lambda p:int("".join(ch for ch in os.path.basename(p) if ch.isdigit()) or 0))
    for f in files:
        mod=importlib.import_module(os.path.basename(f)[:-3])
        n="".join(ch for ch in os.path.basename(f) if ch.isdigit())
        acts+=getattr(mod,f"DOMAIN{n}",[])
    return acts
ACTIVITIES = _load_domains()

def _find_repo(start):
    """Locate the course repo (a dir containing both courseware/ and labs/).
    Env COURSE_REPO overrides. Keeps the build working wherever the skill lives."""
    env = os.environ.get("COURSE_REPO")
    if env and os.path.isdir(env):
        return env
    d = start
    for _ in range(8):
        d = os.path.dirname(d)
        if os.path.isdir(os.path.join(d, "courseware")) and os.path.isdir(os.path.join(d, "labs")):
            return d
    return os.path.dirname(os.path.dirname(HERE))
REPO = _find_repo(HERE)
ASSETS = os.path.join(os.path.dirname(HERE), "assets")   # co-located with the skill

# ---------------- palette (matches reference) ----------------
# Charcoal / cream / burnt-orange design system (same as the Tertiary
# "Multi AI Agents Workflow" deck). BLUE keeps its name but is the primary accent.
BLUE=RGBColor(0xD9,0x77,0x57); TEAL=RGBColor(0x3A,0x7D,0x7B); AMBER=RGBColor(0xC2,0x60,0x3F)
INK=RGBColor(0x21,0x20,0x1C); GREY=RGBColor(0x6B,0x68,0x62)
LIGHT=RGBColor(0xFF,0xFF,0xFE)   # card fill; rect() draws this as a rounded, bordered card
WHITE=RGBColor(0xFF,0xFF,0xFF); LINE=RGBColor(0xDC,0xD8,0xCF); VIOLET=RGBColor(0x5B,0x4B,0x8A)
ORANGE=RGBColor(0xD9,0x77,0x57); RED=RGBColor(0xB4,0x48,0x3A)
CREAM=RGBColor(0xFA,0xF9,0xF5); CHARCOAL=RGBColor(0x21,0x20,0x1C)
ON_DARK=RGBColor(0xB9,0xB4,0xA9); FOOT_DARK=RGBColor(0x8A,0x86,0x7D)
TITLE_FONT="Cambria"; BODY_FONT="Calibri"
# Per-topic accent themes for the section covers — cycled so ANY number of
# topics gets a distinct colour without hard-coding a specific course.
_ACCENTS=[ORANGE,TEAL,VIOLET,AMBER]
CARD_COLORS=[BLUE,TEAL,VIOLET]
TOPIC_THEME={t["num"]:_ACCENTS[i%len(_ACCENTS)] for i,t in enumerate(C.TOPICS)}
# Topic → its labs. Hoisted here (the WSQ engine defined it late) so the admin
# overview slides can render the schedule straight from the data.
TOPIC_ACTS = {t["num"]: [a for a in ACTIVITIES if a["topic"]==t["num"]] for t in C.TOPICS}

# ---------------- dark "masterclass" palette (opt-in via course_data.DARK_THEME) ----------------
DK_BG   = RGBColor(0x0D,0x0E,0x0B)   # slide background
DK_PANEL= RGBColor(0x15,0x17,0x12)   # cards/rows/panels
DK_AMBER= RGBColor(0xF5,0xA6,0x23)   # headlines, kickers, accents, number chips
DK_IVORY= RGBColor(0xE8,0xE6,0xDD)   # body text
DK_FAINT= RGBColor(0x2A,0x2C,0x28)   # divider rules
DK_DIM  = RGBColor(0x8A,0x8D,0x86)   # captions/footers
DK_GREEN= RGBColor(0x4A,0xDE,0x80)   # success/test-it accents

# Module-level theme switch — dark "masterclass" theme for the ENTIRE deck.
THEME={"dark":False}
def _bg():   return DK_BG    if THEME["dark"] else CREAM
def _panel():return DK_PANEL if THEME["dark"] else LIGHT
def _ink():  return DK_IVORY if THEME["dark"] else INK
def _grey(): return DK_DIM   if THEME["dark"] else GREY
def _line(): return DK_FAINT if THEME["dark"] else LINE
def _acc(c): return DK_AMBER if THEME["dark"] else c
# Non-WSQ house standard is the ALL-WHITE deck. A course may opt into the dark
# "masterclass" look with course_data.DARK_THEME = True.
THEME["dark"]=bool(getattr(C,"DARK_THEME",False))

prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
SW,SH=prs.slide_width,prs.slide_height
BLANK=prs.slide_layouts[6]

def slide(): return prs.slides.add_slide(BLANK)
def rect(s,x,y,w,h,color,line=None):
    card=(color==LIGHT and not THEME["dark"])          # panels render as white rounded cards
    sp=s.shapes.add_shape(5 if card else 1,x,y,w,h); sp.fill.solid(); sp.fill.fore_color.rgb=color
    if card:
        sp.adjustments[0]=min(0.06,0.06*Inches(4)/max(1,min(w,h))); line=LINE
    if line is None: sp.line.fill.background()
    else: sp.line.color.rgb=line; sp.line.width=Pt(1)
    sp.shadow.inherit=False; _flat(sp); return sp
def _flat(sp):
    """Drop the theme shape style so no default shadow/effect is rendered (flat cards)."""
    st=sp._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}style')
    if st is not None: sp._element.remove(st)
def oval(s,x,y,w,h,color):
    sp=s.shapes.add_shape(9,x,y,w,h); sp.fill.solid(); sp.fill.fore_color.rgb=color
    sp.line.fill.background(); sp.shadow.inherit=False; _flat(sp); return sp
def txt(s,x,y,w,h,runs,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP,space=4,font=None):
    tb=s.shapes.add_textbox(x,y,w,h); tf=tb.text_frame; tf.word_wrap=True; tf.vertical_anchor=anchor
    for i,line in enumerate(runs):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.alignment=align; p.space_after=Pt(space)
        for t,sz,col,bold in line:
            r=p.add_run(); r.text=t; r.font.size=Pt(sz); r.font.bold=bold
            r.font.color.rgb=col
            r.font.name=font or (TITLE_FONT if (bold and sz>=17) else BODY_FONT)
    return tb
def bullets(s,x,y,w,h,items,size=18,color=None,gap=10,mcolor=BLUE):
    tb=s.shapes.add_textbox(x,y,w,h); tf=tb.text_frame; tf.word_wrap=True
    body=color if color is not None else _ink()
    for i,it in enumerate(items):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph(); p.space_after=Pt(gap)
        lvl=it[1] if isinstance(it,tuple) else 0
        text=it[0] if isinstance(it,tuple) else it
        r=p.add_run(); r.text=("•  " if lvl==0 else "–  ")+text
        r.font.size=Pt(size if lvl==0 else size-2); r.font.color.rgb=body if lvl==0 else _grey()
        r.font.name=BODY_FONT; r.font.bold=(lvl==0 and isinstance(it,tuple) and len(it)>2 and it[2])
    return tb

PAGE={"n":0}
def footer(s,dark=False):
    PAGE["n"]+=1; fc=FOOT_DARK if dark else _grey()
    txt(s,Inches(0.5),Inches(7.08),Inches(6.2),Inches(0.3),
        [[(getattr(C,"COPYRIGHT_SHORT","© Tertiary Infotech Academy Pte Ltd"),9,fc,False)]])
    txt(s,Inches(7.0),Inches(7.08),Inches(5.3),Inches(0.3),
        [[(getattr(C,"FOOTER_TAG",f"{C.SHORT_TITLE}  ·  {C.COURSE_CODE}"),9,fc,False)]],align=PP_ALIGN.RIGHT)
    txt(s,Inches(12.43),Inches(7.08),Inches(0.5),Inches(0.3),
        [[(str(PAGE["n"]),9,fc,False)]],align=PP_ALIGN.RIGHT)
def dark_bg(s):
    """Charcoal canvas with the two signature circles (cover, dividers, closing)."""
    rect(s,0,0,SW,SH,CHARCOAL)
    oval(s,Inches(10.4),Inches(-1.6),Inches(4.6),Inches(4.6),ORANGE)
    oval(s,Inches(11.6),Inches(4.4),Inches(3.4),Inches(3.4),TEAL)
def head(s,title,kicker=None,kcolor=BLUE):
    rect(s,0,0,SW,SH,_bg())
    # Small orange kicker, then a Cambria title - no side bar, no divider rule.
    if kicker: txt(s,Inches(0.85),Inches(0.42),Inches(11.9),Inches(0.32),[[(str(kicker).upper(),12,_acc(BLUE),True)]])
    # Auto-fit the title so long lab titles stay on one line.
    L=len(str(title)); tsize = 30 if L<=46 else (26 if L<=58 else 22)
    txt(s,Inches(0.85),Inches(0.78),Inches(11.95),Inches(0.85),[[(title,tsize,_ink(),False)]],
        anchor=MSO_ANCHOR.MIDDLE,font=TITLE_FONT)
    return s
def _logo(name):
    p=os.path.join(ASSETS,name)
    return p if os.path.exists(p) else None

# ---------------- slide templates ----------------
def cover():
    s=slide(); dark_bg(s)
    txt(s,Inches(0.9),Inches(1.5),Inches(8.5),Inches(0.4),
        [[(getattr(C,"COVER_TAG",f"NON-WSQ COURSE  •  {C.COURSE_CODE}"),14,ORANGE,True)]],font=BODY_FONT)
    # under the title on plain charcoal - top right sits on the orange circle and is hard to read
    txt(s,Inches(0.9),Inches(4.75),Inches(8.5),Inches(0.4),
        [[(f"Version {C.VERSION}  ·  {C.VERSION_DATE}",13,ON_DARK,False)]],font=BODY_FONT)
    txt(s,Inches(0.85),Inches(2.0),Inches(11.2),Inches(2.6),[[(C.TITLE,52,WHITE,True)]],font=TITLE_FONT)
    txt(s,Inches(0.9),Inches(5.7),Inches(11),Inches(0.8),
        [[(C.ORG,15,WHITE,True)]]+([[(C.UEN,13,ON_DARK,False)]] if C.UEN else []),font=BODY_FONT,space=2)
    txt(s,Inches(0.9),Inches(6.75),Inches(11.5),Inches(0.35),
        [[(getattr(C,"CONTACT_LINE","www.tertiarycourses.com.sg   |   enquiry@tertiaryinfotech.com   |   +65 6100 0613"),12,ON_DARK,False)]])
    txt(s,Inches(7.83),Inches(6.95),Inches(5.0),Inches(0.3),
        [[(getattr(C,"COPYRIGHT_SHORT","© Tertiary Infotech Academy Pte Ltd"),9,FOOT_DARK,False)]],align=PP_ALIGN.RIGHT)

def section(kicker,title,n,sub="",accent=BLUE):
    s=slide(); dark_bg(s)
    txt(s,Inches(0.9),Inches(2.05),Inches(9.2),Inches(0.45),[[(str(kicker).upper(),14,ORANGE,True)]],font=BODY_FONT)
    txt(s,Inches(0.85),Inches(2.5),Inches(9.4),Inches(1.9),[[(title,40,WHITE,False)]],
        anchor=MSO_ANCHOR.MIDDLE,font=TITLE_FONT)
    rect(s,Inches(0.92),Inches(4.6),Inches(1.25),Inches(0.07),accent if accent!=VIOLET else ORANGE)
    if sub: txt(s,Inches(0.9),Inches(4.85),Inches(9.2),Inches(1.2),[[(sub,15,ON_DARK,False)]])
    footer(s,dark=True)
def content(title,items,kicker=None,size=20):
    # HARD RULE: no bullet-wall slides — every content slide renders as numbered
    # visual cards (LIGHT card, accent bar, number chip), never plain bullets.
    import math as _m
    s=head(slide(),title,kicker)
    xs=[(i[0] if isinstance(i,tuple) else i) for i in items]
    n=max(1,len(xs)); cols=2 if n>3 else 1; rows=_m.ceil(n/cols)
    x0,y0=Inches(0.85),Inches(2.0); gw=Inches(11.63); gap=Inches(0.18)
    cw=int((gw-gap*(cols-1))/cols); ch=int((Inches(4.7)-gap*(rows-1))/rows)
    fs=(16 if rows<=2 else 14 if rows==3 else 12) if cols==2 else (17 if rows<=3 else 14)
    for idx,it in enumerate(xs):
        r,c=divmod(idx,cols)
        cx=x0+c*(cw+gap); cy=y0+r*(ch+gap)
        rect(s,cx,cy,cw,ch,_panel()); rect(s,cx,cy,cw,Inches(0.07),_acc(BLUE))
        oval(s,cx+Inches(0.2),int(cy+ch/2-Inches(0.19)),Inches(0.38),Inches(0.38),_acc(BLUE))
        txt(s,cx+Inches(0.2),int(cy+ch/2-Inches(0.17)),Inches(0.38),Inches(0.34),
            [[(str(idx+1),13,DK_BG if THEME["dark"] else WHITE,True)]],align=PP_ALIGN.CENTER)
        txt(s,cx+Inches(0.74),cy+Inches(0.08),cw-Inches(0.98),ch-Inches(0.16),
            [[(it,fs,_ink(),False)]],anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
def prompt_explain(title,rows,kicker=None):
    """Sample prompts with a 'What it does' column: one numbered card per prompt.
    rows: list of (label, prompt, explanation)."""
    s=head(slide(),title,kicker)
    n=max(1,len(rows)); x0=Inches(0.85); W=Inches(11.63); y0=Inches(2.2); gap=Inches(0.1)
    ch=int((Inches(4.6)-gap*(n-1))/n); split=Inches(6.55)
    txt(s,x0+Inches(0.75),Inches(1.8),Inches(4),Inches(0.32),[[("PROMPT",12,_acc(BLUE),True)]])
    txt(s,x0+split+Inches(0.25),Inches(1.8),Inches(4),Inches(0.32),[[("WHAT IT DOES",12,_acc(TEAL),True)]])
    fs=12 if max(len(p)+len(e) for _l,p,e in rows)<=330 else 11
    for i,(lbl,pr,ex) in enumerate(rows):
        y=int(y0+(ch+gap)*i); col=PALETTE[i%len(PALETTE)]
        rect(s,x0,y,W,ch,_panel())
        bd=Inches(0.38); oval(s,x0+Inches(0.2),int(y+ch/2-bd/2),bd,bd,col)
        txt(s,x0+Inches(0.2),int(y+ch/2-bd/2),bd,bd,[[(str(i+1),12,WHITE,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
        txt(s,x0+Inches(0.75),y,split-Inches(0.9),ch,[[(f"{lbl}:  ",fs,col,True),(pr,fs,_ink(),False)]],anchor=MSO_ANCHOR.MIDDLE)
        rect(s,x0+split,y+Inches(0.12),Inches(0.015),ch-Inches(0.24),_line())
        txt(s,x0+split+Inches(0.25),y,W-split-Inches(0.4),ch,[[(ex,fs,_grey(),False)]],anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
def two_col(title,left,right,kicker=None,lhead="",rhead="",size=16):
    s=head(slide(),title,kicker)
    rect(s,Inches(0.85),Inches(1.95),Inches(5.7),Inches(4.7),_panel()); rect(s,Inches(6.95),Inches(1.95),Inches(5.53),Inches(4.7),_panel())
    rect(s,Inches(0.85),Inches(1.95),Inches(5.7),Inches(0.07),_acc(BLUE)); rect(s,Inches(6.95),Inches(1.95),Inches(5.53),Inches(0.07),_acc(TEAL))
    if lhead: txt(s,Inches(1.1),Inches(2.15),Inches(5.2),Inches(0.4),[[(lhead,16,_acc(BLUE),True)]])
    if rhead: txt(s,Inches(7.2),Inches(2.15),Inches(5.0),Inches(0.4),[[(rhead,16,_acc(TEAL),True)]])
    bullets(s,Inches(1.1),Inches(2.7),Inches(5.2),Inches(3.8),left,size=size,color=_ink())
    bullets(s,Inches(7.2),Inches(2.7),Inches(5.05),Inches(3.8),right,size=size,color=_ink(),mcolor=TEAL); footer(s); return s
def cards3(title,cards,kicker,size=14):
    # 1-3 cards share the width of the title rule (0.85in -> 12.48in) exactly.
    s=head(slide(),title,kicker); cards=cards[:3]; k=max(1,len(cards)); gap=Inches(0.2)
    cw=int((Inches(11.63)-gap*(k-1))/k)
    for i,c in enumerate(cards):
        x=Inches(0.85)+i*(cw+gap); col=c[0]
        rect(s,x,Inches(1.95),cw,Inches(4.7),_panel()); rect(s,x,Inches(1.95),cw,Inches(0.07),col)
        txt(s,x+Inches(0.25),Inches(2.2),cw-Inches(0.45),Inches(0.6),[[(c[1],19,col,True)]])
        bullets(s,x+Inches(0.25),Inches(2.95),cw-Inches(0.45),Inches(3.4),c[2],size=size,color=_ink(),mcolor=col,gap=9)
    footer(s); return s
def big_statement(line1,line2,kicker,color=BLUE):
    s=slide(); dark_bg(s)
    txt(s,Inches(1.0),Inches(2.0),Inches(9.2),Inches(0.5),[[(str(kicker).upper(),14,ORANGE,True)]],font=BODY_FONT)
    txt(s,Inches(0.95),Inches(2.55),Inches(9.3),Inches(2.3),[[(line1,40,WHITE,True)]],font=TITLE_FONT)
    if line2: txt(s,Inches(1.0),Inches(4.95),Inches(9.2),Inches(1.4),[[(line2,18,ON_DARK,False)]])
    footer(s,dark=True); return s
import math
PALETTE=[BLUE,TEAL,VIOLET,AMBER]
"""Max tiles per slide. The grid divides a fixed-height area by the row count,
so past this the cards shrink below their own text and collide. Beyond it,
tile_grid paginates onto continuation slides instead of shrinking."""
TILE_MAX=6

def tile_grid(title,items,kicker=None,cols=2,size=15,icons=None,accent=BLUE,_start=0):
    """Grid of light panels, each with a coloured icon/number badge + text.
    items: list of strings (or (title,caption) tuples). Much richer than a bullet list.
    More than TILE_MAX items paginate onto '(cont.)' slides; returns the last slide.
    _start offsets the badge numbers so continuation slides keep counting up."""
    if len(items)>TILE_MAX:
        last=None
        for i in range(0,len(items),TILE_MAX):
            part=items[i:i+TILE_MAX]
            ic=icons[i:i+TILE_MAX] if icons else None
            last=tile_grid(title if i==0 else f"{title} (cont.)",part,
                           kicker=kicker,cols=cols,size=size,icons=ic,accent=accent,_start=i)
        return last
    s=head(slide(),title,kicker,kcolor=accent)
    n=len(items); rows=math.ceil(n/cols)
    X0=Inches(0.85); Y0=Inches(1.95); TOTW=Inches(11.63); AREAH=Inches(4.78)
    gx=Inches(0.3); gy=Inches(0.26)
    cw=int((TOTW-gx*(cols-1))/cols)
    # Card height comes from a FULL page's row count, so a short continuation page
    # keeps the same card size as the page before it instead of stretching each
    # card over the whole area. Capped so a short standalone grid still fills.
    _rows_h=math.ceil(TILE_MAX/cols) if _start else rows
    ch=int((AREAH-gy*(_rows_h-1))/_rows_h)
    bd=Inches(0.6)
    for i,it in enumerate(items):
        g=_start+i          # global index across continuation slides
        r=i//cols; c=i%cols
        x=int(X0+(cw+gx)*c); y=int(Y0+(ch+gy)*r); col=PALETTE[g%len(PALETTE)]
        rect(s,x,y,cw,ch,_panel()); rect(s,x,y,cw,Inches(0.07),col)
        oval(s,x+Inches(0.28),int(y+ch/2-bd/2),bd,bd,col)
        ic=icons[i] if icons else str(g+1)
        txt(s,x+Inches(0.28),int(y+ch/2-bd/2),bd,bd,[[(ic,19,WHITE,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
        tx=x+Inches(1.08); tw=cw-Inches(1.32)
        if isinstance(it,tuple):
            txt(s,tx,int(y+Inches(0.14)),tw,int(ch-Inches(0.2)),
                [[(it[0],size+2,_ink(),True)],[(it[1],size-2,_grey(),False)]],anchor=MSO_ANCHOR.MIDDLE,space=3)
        else:
            txt(s,tx,int(y+Inches(0.1)),tw,int(ch-Inches(0.16)),[[(it,size,_ink(),False)]],anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
def flow_h(title,steps,kicker=None,color=BLUE):
    """Horizontal numbered flow: coloured chips connected by chevrons."""
    s=head(slide(),title,kicker,kcolor=color)
    n=len(steps); X0=Inches(0.85); TOTW=Inches(11.63); gap=Inches(0.34)
    cw=int((TOTW-gap*(n-1))/n); y=Inches(2.55); ch=Inches(3.15); bd=Inches(0.82)
    for i,st in enumerate(steps):
        x=int(X0+(cw+gap)*i)
        rect(s,x,y,cw,ch,_panel()); rect(s,x,y,cw,Inches(0.07),color)
        oval(s,int(x+cw/2-bd/2),int(y+Inches(0.42)),bd,bd,color)
        txt(s,int(x+cw/2-bd/2),int(y+Inches(0.42)),bd,bd,[[(str(i+1),30,WHITE,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
        txt(s,x+Inches(0.16),int(y+Inches(1.55)),cw-Inches(0.32),int(ch-Inches(1.7)),[[(st,14,_ink(),False)]],align=PP_ALIGN.CENTER)
        if i<n-1:
            txt(s,int(x+cw-Inches(0.04)),int(y+ch/2-Inches(0.3)),int(gap+Inches(0.08)),Inches(0.6),
                [[("▶",15,color,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
def trainer_slide(kicker,name,role,rows,initials,accent=BLUE):
    """Profile-card layout: avatar badge + name/role panel on the left, labelled
    info tiles on the right. rows: list of (LABEL, value); blank value → fill-in line."""
    s=head(slide(),"About the Trainer",kicker,kcolor=accent)
    lx=Inches(0.85); lw=Inches(3.65)
    rect(s,lx,Inches(1.95),lw,Inches(4.7),_panel()); rect(s,lx,Inches(1.95),lw,Inches(0.12),accent)
    bd=Inches(1.7); ax=int(lx+(lw-bd)/2)
    oval(s,ax,Inches(2.5),bd,bd,accent)
    txt(s,ax,Inches(2.5),bd,bd,[[(initials,44,WHITE,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    txt(s,lx+Inches(0.15),Inches(4.55),lw-Inches(0.3),Inches(0.6),[[(name,21,_ink(),True)]],align=PP_ALIGN.CENTER)
    txt(s,lx+Inches(0.15),Inches(5.2),lw-Inches(0.3),Inches(1.2),[[(role,13,_grey(),False)]],align=PP_ALIGN.CENTER)
    rx=Inches(4.9); rw=Inches(7.6); ry=Inches(1.95); rh=Inches(4.7)
    n=len(rows); gy=Inches(0.2); th=int((rh-gy*(n-1))/n)
    for i,(label,val) in enumerate(rows):
        y=int(ry+(th+gy)*i); col=PALETTE[i%len(PALETTE)]
        rect(s,rx,y,rw,th,_panel()); rect(s,rx,y,rw,Inches(0.07),col)
        vruns=[(val,14,_ink(),False)] if val else [("____________________________________________",13,_line(),False)]
        txt(s,rx+Inches(0.32),y,rw-Inches(0.6),th,
            [[(label.upper(),11,col,True)],vruns],anchor=MSO_ANCHOR.MIDDLE,space=3)
    footer(s); return s
def trainer_profile(prof):
    """'About the Trainer' (reference design): charcoal name card on the left,
    icon rows on the right, LinkedIn / GitHub along the bottom."""
    s=head(slide(),"About the Trainer","INTRODUCTION")
    def icon(name,x,y,d,col):
        oval(s,x,y,d,d,col)
        f=os.path.join(ASSETS,"icons",f"{name}.png")
        if os.path.exists(f):
            k=int(d*0.52); s.shapes.add_picture(f,int(x+(d-k)/2),int(y+(d-k)/2),k,k)
    cx,cy,cw=Inches(0.85),Inches(1.9),Inches(3.6)
    sp=s.shapes.add_shape(5,cx,cy,cw,cw); sp.fill.solid(); sp.fill.fore_color.rgb=CHARCOAL
    sp.line.fill.background(); sp.adjustments[0]=0.06; _flat(sp)
    icon("person",int(cx+(cw-Inches(0.7))/2),Inches(2.3),Inches(0.7),ORANGE)
    txt(s,cx,Inches(3.2),cw,Inches(0.6),[[(prof["name"],22,WHITE,True)]],align=PP_ALIGN.CENTER,font=TITLE_FONT)
    txt(s,cx,Inches(3.75),cw,Inches(0.4),[[(prof["role"],13,ORANGE,False)]],align=PP_ALIGN.CENTER)
    for i,(ic,text) in enumerate(prof.get("points",[])):
        y=Inches(2.0)+i*Inches(0.88)
        icon(ic,Inches(4.85),y,Inches(0.55),TEAL)
        txt(s,Inches(5.6),y-Inches(0.17),Inches(7.0),Inches(0.9),[[(text,15,_ink(),False)]],anchor=MSO_ANCHOR.MIDDLE)
    for i,(ic,text) in enumerate(prof.get("links",[])):
        x=Inches(4.85)+i*Inches(4.4); y=Inches(5.57)
        icon(ic,x,y,Inches(0.55),ORANGE)
        txt(s,x+Inches(0.75),y-Inches(0.03),Inches(3.4),Inches(0.6),[[(text,15,_ink(),False)]],anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
def activity_overview(tag,title,desc,build,services,kicker,workflow=None):
    s=head(slide(),title,kicker,kcolor=TEAL)
    rect(s,Inches(0.85),Inches(1.85),Inches(1.7),Inches(0.5),_acc(BLUE))
    txt(s,Inches(0.85),Inches(1.9),Inches(1.7),Inches(0.4),[[(tag,16,DK_BG if THEME["dark"] else WHITE,True)]],align=PP_ALIGN.CENTER)
    # Auto-fit the description so long lab goals never clip into the panel below.
    dL=len(str(desc)); dsize = 21 if dL<=200 else (17 if dL<=320 else 15)
    txt(s,Inches(0.85),Inches(2.55),Inches(11.63),Inches(1.25),[[(desc,dsize,_ink(),False)]])
    rect(s,Inches(0.85),Inches(4.0),Inches(11.63),Inches(2.5),_panel()); rect(s,Inches(0.85),Inches(4.0),Inches(0.07),Inches(2.5),_acc(BLUE))
    txt(s,Inches(1.1),Inches(4.18),Inches(11),Inches(0.35),[[("You'll build",14,_acc(BLUE),True)]])
    bL=len(str(build)); bsize=18 if bL<=120 else (16 if bL<=190 else 14)
    txt(s,Inches(1.1),Inches(4.48),Inches(11),Inches(0.72),[[(build,bsize,_ink(),True)]])
    if workflow:
        # Lay out up to five workflow chips evenly across the 11-inch panel.
        wf=workflow[:5]; k=len(wf); gap=Inches(0.18)
        cw=int((Inches(11.0)-gap*(k-1))/k)
        for i,item in enumerate(wf):
            x=Inches(1.1)+i*(cw+gap)
            rect(s,x,Inches(5.28),cw,Inches(0.52),_bg(),line=_line())
            txt(s,x+Inches(0.06),Inches(5.34),cw-Inches(0.12),Inches(0.38),
                [[(f"{i+1}  {item}",12 if k<=4 else 11,_ink(),True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    txt(s,Inches(1.1),Inches(6.02),Inches(11.2),Inches(0.3),[[("Tools:  ",12,_grey(),True),(services,12,_grey(),False)]]); footer(s); return s
def step_slide(kicker,act_title,n,total,text,cmd=""):
    s=head(slide(),act_title,kicker,TEAL)
    oval(s,Inches(0.85),Inches(2.5),Inches(1.4),Inches(1.4),_acc(TEAL))
    txt(s,Inches(0.85),Inches(2.74),Inches(1.4),Inches(0.9),[[(str(n),38,DK_BG if THEME["dark"] else WHITE,True)]],align=PP_ALIGN.CENTER)
    txt(s,Inches(0.95),Inches(1.95),Inches(11),Inches(0.4),[[(f"STEP {n} OF {total}",13,_grey(),True)]])
    tL=len(str(text)); tsize=23 if tL<=185 else (20 if tL<=285 else 17)
    txt(s,Inches(2.55),Inches(2.25),Inches(10.1),Inches(1.65),[[(text,tsize,_ink(),False)]],anchor=MSO_ANCHOR.MIDDLE)
    # HARD RULE: never render a comment-only "command" (# …) on a slide — the
    # code box appears only for a real, runnable command.
    if cmd and not cmd.lstrip().startswith("#"):
        cL=len(str(cmd)); cLines=cmd.count("\n")+1
        csize=13 if cL<=105 and cLines<=2 else (10 if cL<=280 and cLines<=6 else 8)
        boxh=Inches(0.95 if csize==13 else 1.3)
        if THEME["dark"]:
            # slightly lighter fill + faint border so the box reads against the dark bg
            rect(s,Inches(2.55),Inches(4.05),Inches(10.1),boxh,RGBColor(0x10,0x14,0x1E),line=DK_FAINT)
        else:
            rect(s,Inches(2.55),Inches(4.05),Inches(10.1),boxh,RGBColor(0x0B,0x12,0x20))
        txt(s,Inches(2.8),Inches(4.14),Inches(9.7),boxh-Inches(0.18),
            [[("$ "+cmd,csize,RGBColor(0x9C,0xDC,0xFE),False)]],anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
def dark_rows(tag,title_lines,sub_lines,rows,warn=None,accent=None,numbered=True):
    """Masterclass-style dark feature slide: terminal tag, amber (or custom
    accent) headline, light subtitle lines, numbered/bulleted row-cards. Rows
    may be strings, (amber,white) tuples, or lists of (text,colorkey) pairs
    (keys: w/a/b/g/d). warn=(BADGE, text) renders a red warning chip."""
    DKBG=RGBColor(0x0D,0x0E,0x0B); AMBER=RGBColor(0xF5,0xA6,0x23)
    ROWBG=RGBColor(0x15,0x17,0x12); FAINT=RGBColor(0x2A,0x2C,0x28); IVORY=RGBColor(0xE8,0xE6,0xDD)
    WARNRED=RGBColor(0xE0,0x5A,0x5A)
    ACC=accent or AMBER
    s=slide(); rect(s,0,0,SW,SH,DKBG)
    txt(s,Inches(0.85),Inches(0.4),Inches(11.6),Inches(0.35),[[("> "+tag,13,ACC,True)]])
    rect(s,Inches(0.85),Inches(0.82),Inches(11.63),Inches(0.02),FAINT)
    y=0.98
    for tl in title_lines:
        txt(s,Inches(0.85),Inches(y),Inches(11.9),Inches(0.78),[[(tl.upper(),40,ACC,True)]]); y+=0.76
    y+=0.08
    for sl in sub_lines:
        txt(s,Inches(0.85),Inches(y),Inches(11.9),Inches(0.38),[[(sl,15,IVORY,False)]]); y+=0.4
    y+=0.22
    n=max(1,len(rows)); gap=0.14
    bottom=6.35 if warn else 6.85
    rh=min(0.78,(bottom-y-gap*(n-1))/n)
    for i,r in enumerate(rows):
        ry=Inches(y+i*(rh+gap))
        rect(s,Inches(0.85),ry,Inches(11.63),Inches(rh),ROWBG)
        rect(s,Inches(0.85),ry,Inches(0.05),Inches(rh),ACC)
        if numbered:
            txt(s,Inches(1.1),ry,Inches(0.75),Inches(rh),[[(f"{i+1:02d}",16,ACC,True)]],anchor=MSO_ANCHOR.MIDDLE)
            tx,tw=Inches(1.9),Inches(10.35)
        else:
            txt(s,Inches(1.1),ry,Inches(0.4),Inches(rh),[[("▸",14,ACC,True)]],anchor=MSO_ANCHOR.MIDDLE)
            tx,tw=Inches(1.55),Inches(10.7)
        txt(s,tx,ry,tw,Inches(rh),[_dkruns(r,16)],anchor=MSO_ANCHOR.MIDDLE)
    if warn:
        wy=y+n*(rh+gap)+0.08
        rect(s,Inches(0.85),Inches(wy),Inches(1.15),Inches(0.34),WARNRED)
        txt(s,Inches(0.85),Inches(wy+0.02),Inches(1.15),Inches(0.3),[[(warn[0],12,DKBG,True)]],align=PP_ALIGN.CENTER)
        txt(s,Inches(2.2),Inches(wy),Inches(10.2),Inches(0.34),[[(warn[1],13,IVORY,False)]],anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
_DKC={"w":RGBColor(0xE8,0xE6,0xDD),"a":RGBColor(0xF5,0xA6,0x23),"b":RGBColor(0x6E,0xA8,0xFF),
      "g":RGBColor(0x4A,0xDE,0x80),"d":RGBColor(0x8A,0x8D,0x86),"r":RGBColor(0xE8,0x6A,0x8A)}
def _dkruns(spec,size=16):
    """spec: str | (amber,white) tuple | list of (text,colorkey) pairs -> txt() runs line."""
    if isinstance(spec,str): return [(spec,size,_DKC["w"],False)]
    if isinstance(spec,tuple): return [(spec[0],size,_DKC["a"],True),(spec[1],size,_DKC["w"],False)]
    return [(t,size,_DKC.get(k,_DKC["w"]),k in ("a","b","g","r")) for t,k in spec]
def dark_table(tag,title,col1,col2,rows,foot=None):
    """Masterclass-style dark comparison table: amber vs blue column headers,
    white row labels, thin divider rules, optional mixed-colour footer line."""
    DKBG=RGBColor(0x0D,0x0E,0x0B); AMBER=_DKC["a"]; HBLUE=_DKC["b"]
    FAINT=RGBColor(0x2A,0x2C,0x28); IVORY=_DKC["w"]; DIM=_DKC["d"]
    s=slide(); rect(s,0,0,SW,SH,DKBG)
    txt(s,Inches(0.85),Inches(0.4),Inches(8.0),Inches(0.35),[[("> "+tag,13,AMBER,True)]])
    txt(s,Inches(8.9),Inches(0.4),Inches(3.6),Inches(0.35),[[("● WHEN TO USE WHICH",12,DIM,True)]],align=PP_ALIGN.RIGHT)
    rect(s,Inches(0.85),Inches(0.82),Inches(11.63),Inches(0.02),FAINT)
    txt(s,Inches(0.85),Inches(1.0),Inches(11.9),Inches(0.8),[[(title.upper(),40,AMBER,True)]])
    LX,C1,C2=Inches(0.85),Inches(3.3),Inches(8.1)
    y=2.05
    txt(s,C1,Inches(y),Inches(4.6),Inches(0.4),[[(col1.upper(),15,AMBER,True)]])
    txt(s,C2,Inches(y),Inches(4.3),Inches(0.4),[[(col2.upper(),15,HBLUE,True)]])
    y+=0.5
    rh=0.62
    for label,v1,v2 in rows:
        rect(s,LX,Inches(y),Inches(11.63),Inches(0.015),FAINT)
        txt(s,LX,Inches(y+0.08),Inches(2.3),Inches(rh),[[(label,15,IVORY,True)]])
        txt(s,C1,Inches(y+0.08),Inches(4.6),Inches(rh),[[(v1,15,IVORY,False)]])
        txt(s,C2,Inches(y+0.08),Inches(4.3),Inches(rh),[[(v2,15,IVORY,False)]])
        y+=rh
    rect(s,LX,Inches(y),Inches(11.63),Inches(0.015),FAINT)
    if foot:
        txt(s,Inches(0.85),Inches(y+0.3),Inches(11.63),Inches(0.45),[_dkruns(foot,15)],align=PP_ALIGN.CENTER)
    footer(s); return s
def dark_code(tag,title,sub,code_lines,foot=None,win_title="",right_tag=None):
    """Masterclass-style dark slide with a terminal/code window: amber headline,
    window chrome (● ● ● + title), monospace coloured code lines, amber footer."""
    DKBG=RGBColor(0x0D,0x0E,0x0B); AMBER=_DKC["a"]; IVORY=_DKC["w"]; FAINT=RGBColor(0x2A,0x2C,0x28)
    CODEBG=RGBColor(0x08,0x0A,0x08); CHROME=RGBColor(0x14,0x16,0x12); DIM=_DKC["d"]
    s=slide(); rect(s,0,0,SW,SH,DKBG)
    txt(s,Inches(0.85),Inches(0.4),Inches(8.0),Inches(0.35),[[("> "+tag,13,AMBER,True)]])
    if right_tag:
        txt(s,Inches(8.9),Inches(0.4),Inches(3.6),Inches(0.35),[[("● "+right_tag,12,DIM,True)]],align=PP_ALIGN.RIGHT)
    rect(s,Inches(0.85),Inches(0.82),Inches(11.63),Inches(0.02),FAINT)
    txt(s,Inches(0.85),Inches(0.95),Inches(11.9),Inches(0.75),[[(title.upper(),38,AMBER,True)]])
    y=1.72
    if sub:
        txt(s,Inches(0.85),Inches(y),Inches(11.9),Inches(0.4),[[(sub,15,IVORY,False)]]); y+=0.46
    # window chrome
    ch=0.34
    rect(s,Inches(0.85),Inches(y),Inches(11.63),Inches(ch),CHROME)
    for k,cc in enumerate((RGBColor(0xE0,0x5A,0x5A),RGBColor(0xF5,0xA6,0x23),RGBColor(0x4A,0xDE,0x80))):
        oval(s,Inches(1.02+k*0.22),Inches(y+0.11),Inches(0.12),Inches(0.12),cc)
    if win_title:
        txt(s,Inches(1.8),Inches(y+0.02),Inches(9.5),Inches(0.3),[[(win_title,11,DIM,False)]])
    y+=ch
    n=len(code_lines); lh=min(0.34,(6.35-y)/max(1,n))
    rect(s,Inches(0.85),Inches(y),Inches(11.63),Inches(lh*n+0.2),CODEBG)
    for i,ln in enumerate(code_lines):
        runs=_dkruns(ln,13)
        # monospace look: Courier New via manual run construction
        tb=s.shapes.add_textbox(Inches(1.1),Inches(y+0.08+i*lh),Inches(11.1),Inches(lh))
        tf=tb.text_frame; tf.word_wrap=False
        p=tf.paragraphs[0]
        for t_,sz,col,bold in runs:
            r=p.add_run(); r.text=t_; r.font.size=Pt(12.5); r.font.bold=bold
            r.font.color.rgb=col; r.font.name="Courier New"
    if foot:
        txt(s,Inches(0.85),Inches(6.62),Inches(11.63),Inches(0.4),[[(foot,14,AMBER,True)]],align=PP_ALIGN.CENTER)
    footer(s); return s
def dark_catalog(tag,title,cards,scope=None,right_tag=None):
    """Masterclass-style dark slide: a row of amber-outlined cards, each with a
    heading + a list of tool names, plus an optional SCOPE note panel below."""
    DKBG=RGBColor(0x0D,0x0E,0x0B); AMBER=_DKC["a"]; IVORY=_DKC["w"]
    FAINT=RGBColor(0x2A,0x2C,0x28); CARDBG=RGBColor(0x10,0x12,0x0E); DIM=_DKC["d"]
    s=slide(); rect(s,0,0,SW,SH,DKBG)
    txt(s,Inches(0.85),Inches(0.4),Inches(8.0),Inches(0.35),[[("> "+tag,13,AMBER,True)]])
    if right_tag:
        txt(s,Inches(8.4),Inches(0.4),Inches(4.1),Inches(0.35),[[("● "+right_tag,12,DIM,True)]],align=PP_ALIGN.RIGHT)
    rect(s,Inches(0.85),Inches(0.82),Inches(11.63),Inches(0.02),FAINT)
    txt(s,Inches(0.85),Inches(0.98),Inches(11.9),Inches(0.78),[[(title.upper(),40,AMBER,True)]])
    y=1.95
    n=len(cards); gap=Inches(0.18); cw=int((Inches(11.63)-gap*(n-1))/n); chh=Inches(3.0); b=Inches(0.02)
    for i,(headt,items) in enumerate(cards):
        x=int(Inches(0.85)+i*(cw+gap)); yv=Inches(y)
        rect(s,x,yv,cw,chh,CARDBG)
        rect(s,x,yv,cw,b,AMBER); rect(s,x,int(yv+chh-b),cw,b,AMBER)
        rect(s,x,yv,b,chh,AMBER); rect(s,int(x+cw-b),yv,b,chh,AMBER)
        txt(s,x,int(yv+Inches(0.14)),cw,Inches(0.34),[[(headt.upper(),13,AMBER,True)]],align=PP_ALIGN.CENTER)
        rows=[[(it,12,IVORY if not it.startswith("+") and "·" not in it else DIM,False)] for it in items]
        txt(s,x+Inches(0.18),int(yv+Inches(0.58)),cw-Inches(0.3),int(chh-Inches(0.7)),rows,space=6)
    if scope:
        sy=y+3.0+0.25
        rect(s,Inches(0.85),Inches(sy),Inches(11.63),Inches(1.15),CARDBG)
        rect(s,Inches(0.85),Inches(sy),Inches(0.05),Inches(1.15),AMBER)
        txt(s,Inches(1.1),Inches(sy+0.12),Inches(1.3),Inches(0.35),[[("SCOPE",15,AMBER,True)]])
        txt(s,Inches(2.5),Inches(sy+0.1),Inches(9.7),Inches(0.98),[[(scope,12.5,IVORY,False)]])
    footer(s); return s
def dark_panels(tag,title,panels,foot=None,right_tag=None):
    """Masterclass-style dark slide: coloured outlined panels ('// HEAD' + body
    run-lines) and a mixed-colour footer. panels: (colorkey, head, [runlines])."""
    DKBG=RGBColor(0x0D,0x0E,0x0B); FAINT=RGBColor(0x2A,0x2C,0x28); PBG=RGBColor(0x10,0x12,0x0E)
    AMBER=_DKC["a"]; DIM=_DKC["d"]
    PCOL={"a":_DKC["a"],"b":_DKC["b"],"g":_DKC["g"],"r":RGBColor(0xE8,0x6A,0x8A)}
    s=slide(); rect(s,0,0,SW,SH,DKBG)
    txt(s,Inches(0.85),Inches(0.4),Inches(8.0),Inches(0.35),[[("> "+tag,13,AMBER,True)]])
    if right_tag:
        txt(s,Inches(8.4),Inches(0.4),Inches(4.1),Inches(0.35),[[("● "+right_tag,12,DIM,True)]],align=PP_ALIGN.RIGHT)
    rect(s,Inches(0.85),Inches(0.82),Inches(11.63),Inches(0.02),FAINT)
    txt(s,Inches(0.85),Inches(0.98),Inches(11.9),Inches(0.78),[[(title.upper(),40,AMBER,True)]])
    y=2.0; n=len(panels); gap=Inches(0.25)
    pw=int((Inches(11.63)-gap*(n-1))/n); ph=Inches(3.3); b=Inches(0.02)
    for i,(ck,head,body) in enumerate(panels):
        col=PCOL.get(ck,AMBER); x=int(Inches(0.85)+i*(pw+gap)); yv=Inches(y)
        rect(s,x,yv,pw,ph,PBG)
        rect(s,x,yv,pw,b,col); rect(s,x,int(yv+ph-b),pw,b,col)
        rect(s,x,yv,b,ph,col); rect(s,int(x+pw-b),yv,b,ph,col)
        txt(s,x+Inches(0.28),int(yv+Inches(0.2)),pw-Inches(0.5),Inches(0.4),[[("// "+head.upper(),15,col,True)]])
        txt(s,x+Inches(0.28),int(yv+Inches(0.72)),pw-Inches(0.52),int(ph-Inches(0.9)),
            [_dkruns(ln,13) for ln in body],space=6)
    if foot:
        txt(s,Inches(0.85),Inches(y+3.3+0.28),Inches(11.63),Inches(0.45),[_dkruns(foot,15)],align=PP_ALIGN.CENTER)
    footer(s); return s
def dark_flow(tag,title,steps,foot=None,right_tag=None):
    """Masterclass-style dark slide: amber-outlined step boxes joined by arrows,
    plus a mixed-colour footer. steps: (head, body)."""
    DKBG=RGBColor(0x0D,0x0E,0x0B); FAINT=RGBColor(0x2A,0x2C,0x28); PBG=RGBColor(0x10,0x12,0x0E)
    AMBER=_DKC["a"]; IVORY=_DKC["w"]; DIM=_DKC["d"]
    s=slide(); rect(s,0,0,SW,SH,DKBG)
    txt(s,Inches(0.85),Inches(0.4),Inches(8.0),Inches(0.35),[[("> "+tag,13,AMBER,True)]])
    if right_tag:
        txt(s,Inches(8.4),Inches(0.4),Inches(4.1),Inches(0.35),[[("● "+right_tag,12,DIM,True)]],align=PP_ALIGN.RIGHT)
    rect(s,Inches(0.85),Inches(0.82),Inches(11.63),Inches(0.02),FAINT)
    txt(s,Inches(0.85),Inches(1.05),Inches(11.9),Inches(0.85),[[(title.upper(),44,AMBER,True)]])
    y=2.55; n=len(steps); ag=Inches(0.38); b=Inches(0.02)
    bw=int((Inches(11.63)-ag*(n-1))/n); bh=Inches(1.55)
    for i,(head,body) in enumerate(steps):
        x=int(Inches(0.85)+i*(bw+ag)); yv=Inches(y)
        rect(s,x,yv,bw,bh,PBG)
        rect(s,x,yv,bw,b,AMBER); rect(s,x,int(yv+bh-b),bw,b,AMBER)
        rect(s,x,yv,b,bh,AMBER); rect(s,int(x+bw-b),yv,b,bh,AMBER)
        txt(s,x,int(yv+Inches(0.16)),bw,Inches(0.36),[[(head.upper(),14,AMBER,True)]],align=PP_ALIGN.CENTER)
        txt(s,x+Inches(0.12),int(yv+Inches(0.6)),bw-Inches(0.24),Inches(0.85),[[(body,11.5,IVORY,False)]],align=PP_ALIGN.CENTER)
        if i<n-1:
            txt(s,int(x+bw),int(yv+bh/2-Inches(0.2)),ag,Inches(0.4),[[("→",18,AMBER,True)]],align=PP_ALIGN.CENTER)
    if foot:
        txt(s,Inches(0.85),Inches(y+1.55+0.45),Inches(11.63),Inches(0.8),[_dkruns(foot,15)],align=PP_ALIGN.CENTER)
    footer(s); return s
def dark_cards(tag,title_lines,cards,notes=(),badge=None):
    """Masterclass-style dark slide: amber headline + a row of green-outlined cards
    (name + subtitle) + optional AUTO-INSTALLED badge line and dim footnotes."""
    DKBG=RGBColor(0x0D,0x0E,0x0B); AMBER=RGBColor(0xF5,0xA6,0x23); GREEN=RGBColor(0x4A,0xDE,0x80)
    IVORY=RGBColor(0xE8,0xE6,0xDD); FAINT=RGBColor(0x2A,0x2C,0x28); CARDBG=RGBColor(0x10,0x12,0x0E)
    DIM=RGBColor(0x8A,0x8D,0x86)
    s=slide(); rect(s,0,0,SW,SH,DKBG)
    txt(s,Inches(0.85),Inches(0.4),Inches(11.6),Inches(0.35),[[("> "+tag,13,AMBER,True)]])
    rect(s,Inches(0.85),Inches(0.82),Inches(11.63),Inches(0.02),FAINT)
    y=0.98
    for tl in title_lines:
        txt(s,Inches(0.85),Inches(y),Inches(11.9),Inches(0.78),[[(tl.upper(),40,AMBER,True)]]); y+=0.76
    y+=0.35
    n=len(cards); gap=Inches(0.25); cw=int((Inches(11.63)-gap*(n-1))/n); ch=Inches(1.55); b=Inches(0.025)
    for i,(name,sub) in enumerate(cards):
        x=int(Inches(0.85)+i*(cw+gap)); yv=Inches(y)
        rect(s,x,yv,cw,ch,CARDBG)
        rect(s,x,yv,cw,b,GREEN); rect(s,x,int(yv+ch-b),cw,b,GREEN)
        rect(s,x,yv,b,ch,GREEN); rect(s,int(x+cw-b),yv,b,ch,GREEN)
        txt(s,x,int(yv+Inches(0.2)),cw,Inches(0.62),[[(name,26,GREEN,True)]],align=PP_ALIGN.CENTER)
        txt(s,x,int(yv+Inches(0.92)),cw,Inches(0.42),[[(sub,15,IVORY,False)]],align=PP_ALIGN.CENTER)
    y+=1.55+0.4
    rest=list(notes)
    if badge and rest:
        rect(s,Inches(0.85),Inches(y),Inches(2.0),Inches(0.36),AMBER)
        txt(s,Inches(0.85),Inches(y+0.02),Inches(2.0),Inches(0.32),[[(badge,12,DKBG,True)]],align=PP_ALIGN.CENTER)
        txt(s,Inches(3.0),Inches(y),Inches(9.4),Inches(0.36),[[(rest.pop(0),14,IVORY,True)]],anchor=MSO_ANCHOR.MIDDLE)
        y+=0.5
    for nt in rest:
        txt(s,Inches(0.85),Inches(y),Inches(11.6),Inches(0.34),[[(nt,12,DIM,False)]]); y+=0.36
    footer(s); return s
def dark_pairs(tag,title_lines,sub,pairs):
    """Masterclass-style dark slide: amber headline + a 2-column grid of
    command/description cells (amber command, light description)."""
    import math as _m
    DKBG=RGBColor(0x0D,0x0E,0x0B); AMBER=RGBColor(0xF5,0xA6,0x23)
    IVORY=RGBColor(0xE8,0xE6,0xDD); FAINT=RGBColor(0x2A,0x2C,0x28); ROWBG=RGBColor(0x15,0x17,0x12)
    DIM=RGBColor(0x8A,0x8D,0x86)
    s=slide(); rect(s,0,0,SW,SH,DKBG)
    txt(s,Inches(0.85),Inches(0.4),Inches(11.6),Inches(0.35),[[("> "+tag,13,AMBER,True)]])
    rect(s,Inches(0.85),Inches(0.82),Inches(11.63),Inches(0.02),FAINT)
    y=0.98
    for tl in title_lines:
        txt(s,Inches(0.85),Inches(y),Inches(11.9),Inches(0.78),[[(tl.upper(),40,AMBER,True)]]); y+=0.76
    if sub:
        txt(s,Inches(0.85),Inches(y+0.02),Inches(11.9),Inches(0.36),[[(sub,14,DIM,False)]]); y+=0.44
    y+=0.18
    cols=2; rows=_m.ceil(len(pairs)/cols); gx=Inches(0.3); gy=0.13
    cw=int((Inches(11.63)-gx)/cols); rh=min(0.8,(6.8-y-gy*(rows-1))/rows)
    for i,(cmd,desc) in enumerate(pairs):
        r,c=i%rows,i//rows   # fill column-first like the reference
        x=int(Inches(0.85)+c*(cw+gx)); yv=Inches(y+r*(rh+gy))
        rect(s,x,yv,cw,Inches(rh),ROWBG)
        rect(s,x,yv,Inches(0.045),Inches(rh),AMBER)
        txt(s,x+Inches(0.22),yv,Inches(2.35),Inches(rh),[[(cmd,14,AMBER,True)]],anchor=MSO_ANCHOR.MIDDLE)
        txt(s,x+Inches(2.6),yv,cw-Inches(2.8),Inches(rh),[[(desc,12.5,IVORY,False)]],anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
def shot(title,img,kicker=None,caption="",accent=TEAL):
    """Screenshot slide — a framed, real UI capture with a caption, fitted to its own aspect."""
    s=head(slide(),title,kicker,accent)
    from PIL import Image as _Im
    iw,ih=_Im.open(img).size
    H=Inches(4.5); W=int(H*iw/ih)
    if W>Inches(11.6): W=Inches(11.6); H=int(W*ih/iw)
    x=int((SW-W)/2); y=Inches(2.02)
    rect(s,x-Inches(0.06),y-Inches(0.06),W+Inches(0.12),H+Inches(0.12),_line())
    s.shapes.add_picture(img,x,y,height=H)
    if caption:
        txt(s,Inches(0.85),Inches(6.68),Inches(11.6),Inches(0.35),[[(caption,12,_grey(),False)]],align=PP_ALIGN.CENTER)
    footer(s); return s
def shot_callouts(title,img,items,kicker=None,accent=BLUE):
    """Portrait UI screenshot on the left, numbered (label, caption) callouts on the right."""
    s=head(slide(),title,kicker,kcolor=accent)
    from PIL import Image as _Im
    iw,ih=_Im.open(img).size
    H=Inches(4.75); W=int(H*iw/ih); x=Inches(0.85); y=Inches(1.98)
    rect(s,x-Inches(0.05),y-Inches(0.05),W+Inches(0.1),H+Inches(0.1),_line())
    s.shapes.add_picture(img,x,y,height=H)
    rx=x+W+Inches(0.4); rw=Inches(12.48)-rx
    n=len(items); gy=Inches(0.12); th=int((H-gy*(n-1))/n); bd=Inches(0.42)
    for i,(label,cap) in enumerate(items):
        ty=int(y+(th+gy)*i); col=PALETTE[i%len(PALETTE)]
        rect(s,rx,ty,rw,th,_panel()); rect(s,rx,ty,rw,Inches(0.07),col)
        oval(s,rx+Inches(0.2),int(ty+th/2-bd/2),bd,bd,col)
        txt(s,rx+Inches(0.2),int(ty+th/2-bd/2),bd,bd,[[(str(i+1),14,WHITE,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
        txt(s,rx+Inches(0.8),ty,rw-Inches(1.0),th,[[(label,14,_ink(),True)],[(cap,12,_grey(),False)]],
            anchor=MSO_ANCHOR.MIDDLE,space=2)
    footer(s); return s
def shot_pair(title,shots,kicker=None,accent=BLUE):
    """Two portrait UI screenshots side by side, each with a bold label and caption under it."""
    s=head(slide(),title,kicker,kcolor=accent)
    from PIL import Image as _Im
    H=Inches(4.1); y=Inches(1.95); gap=Inches(0.5); cw=int((Inches(11.63)-gap)/2)
    for i,(img,label,cap) in enumerate(shots[:2]):
        iw,ih=_Im.open(img).size; W=int(H*iw/ih)
        cx=int(Inches(0.85)+i*(cw+gap)); x=int(cx+(cw-W)/2)
        rect(s,x-Inches(0.05),y-Inches(0.05),W+Inches(0.1),H+Inches(0.1),_line())
        s.shapes.add_picture(img,x,y,height=H)
        txt(s,cx,y+H+Inches(0.12),cw,Inches(0.72),[[(label,14,_ink(),True)],[(cap,12,_grey(),False)]],
            align=PP_ALIGN.CENTER,space=2)
    footer(s); return s
def hub(title,center,spokes,flow=None,kicker=None,accent=BLUE):
    """Hub-and-spoke relationship diagram: a central circle linked to four corner cards.
    center=(name,caption); spokes=[(name,caption,hex colour)] x4 in TL,TR,BL,BR order; flow=optional strip text."""
    from pptx.enum.shapes import MSO_CONNECTOR
    s=head(slide(),title,kicker,kcolor=accent)
    cx,cy,d=int(SW/2),Inches(4.2),Inches(2.7)
    cw,ch=Inches(3.75),Inches(1.45)
    pos=[(Inches(0.85),Inches(1.95)),(SW-Inches(0.85)-cw,Inches(1.95)),(Inches(0.85),Inches(4.95)),(SW-Inches(0.85)-cw,Inches(4.95))]
    for (x,y),(_n,_c,col) in zip(pos,spokes):           # connectors first so they sit behind the shapes
        ex=x+cw if x<cx else x; ey=y+ch//2
        ln=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,cx,cy,int(ex),int(ey))
        ln.line.color.rgb=RGBColor.from_string(col); ln.line.width=Pt(3)
    oval(s,cx-d//2-Inches(0.12),cy-d//2-Inches(0.12),d+Inches(0.24),d+Inches(0.24),_line())
    oval(s,cx-d//2,cy-d//2,d,d,accent)
    txt(s,cx-d//2+Inches(0.15),cy-d//2,d-Inches(0.3),d,[[(center[0],22,WHITE,True)],[(center[1],14,WHITE,False)]],
        align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE,space=6)
    for (x,y),(name,cap,col) in zip(pos,spokes):
        c=RGBColor.from_string(col)
        rect(s,int(x),int(y),cw,ch,_panel()); rect(s,int(x),int(y),Inches(0.12),ch,c)
        txt(s,int(x+Inches(0.3)),int(y+Inches(0.1)),cw-Inches(0.45),ch-Inches(0.2),[[(name,20,c,True)],[(cap,14,_grey(),False)]],
            anchor=MSO_ANCHOR.MIDDLE,space=3)
    if flow:
        txt(s,Inches(0.85),Inches(6.5),SW-Inches(1.7),Inches(0.4),[[(flow,15,_ink(),True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
def compare_table(title,headers,rows,kicker=None,accent=BLUE):
    """Side-by-side comparison: a label column plus one coloured column per option."""
    s=head(slide(),title,kicker,kcolor=accent)
    X0=Inches(0.85); TOTW=Inches(11.63); lw=Inches(1.75); y0=Inches(1.95)
    n=len(headers)-1; cw=int((TOTW-lw)/n); hh=Inches(0.5)
    rh=int((Inches(6.75)-y0-hh)/len(rows)); fs=12 if len(rows)<=6 else 11.5
    for j,hd in enumerate(headers[1:]):
        x=int(X0+lw+cw*j); col=PALETTE[j%len(PALETTE)]
        rect(s,x+Inches(0.03),y0,cw-Inches(0.06),hh,col)
        txt(s,x+Inches(0.03),y0,cw-Inches(0.06),hh,[[(hd,15,WHITE,True)]],align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE)
    for i,row in enumerate(rows):
        y=int(y0+hh+Inches(0.06)+rh*i)
        if i%2==0: rect(s,X0,y,TOTW,rh,_panel())
        txt(s,X0+Inches(0.12),y,lw-Inches(0.16),rh,[[(row[0],12.5,_ink(),True)]],anchor=MSO_ANCHOR.MIDDLE)
        for j,cell in enumerate(row[1:]):
            x=int(X0+lw+cw*j)
            txt(s,x+Inches(0.12),y,cw-Inches(0.24),rh,[[(cell,fs,_ink(),False)]],anchor=MSO_ANCHOR.MIDDLE)
    footer(s); return s
def test_slide(act_title,text,kicker):
    s=head(slide(),act_title,kicker,TEAL)
    rect(s,Inches(0.85),Inches(2.3),Inches(11.7),Inches(2.8),DK_PANEL if THEME["dark"] else RGBColor(0xE8,0xF7,0xEE))
    txt(s,Inches(1.2),Inches(2.6),Inches(11),Inches(0.5),[[("✅  Test it",20,DK_GREEN if THEME["dark"] else RGBColor(0x12,0x7A,0x3E),True)]])
    tsize=18 if len(str(text))<=380 else (16 if len(str(text))<=520 else 14)
    txt(s,Inches(1.2),Inches(3.25),Inches(11),Inches(1.65),[[(text,tsize,_ink(),False)]]); footer(s); return s
def brk(kind,dur,color=AMBER):
    s=slide(); rect(s,0,0,SW,SH,_bg())
    rect(s,0,0,SW,Inches(0.22),color); rect(s,0,Inches(7.28),SW,Inches(0.22),color)
    rect(s,Inches(5.4),Inches(2.35),Inches(2.53),Inches(0.1),color)
    txt(s,0,Inches(2.75),SW,Inches(1.2),[[(kind,48,_ink(),True)]],align=PP_ALIGN.CENTER)
    txt(s,0,Inches(4.05),SW,Inches(0.8),[[(dur,22,color,True)]],align=PP_ALIGN.CENTER); PAGE["n"]+=1

# ============================================================ BUILD
cover()

# ---------------- ADMIN ----------------
section("COURSE ADMINISTRATION","Welcome & Housekeeping","")
if getattr(C,"TRAINER_PROFILE",None):
    trainer_profile(C.TRAINER_PROFILE)
elif getattr(C,"TRAINER_TEAM",None):
    tile_grid("Course Trainer Profiles",C.TRAINER_TEAM,
              kicker=f"TRAINERS LISTED FOR {C.COURSE_CODE or C.SHORT_TITLE}",cols=2,size=15,accent=BLUE)
content("Let's Know Each Other",getattr(C,"ICE_BREAKER",[
 "Your name and organisation / role.",
 "Your experience with this subject (if any).",
 "What you want to be able to do after this course."]),kicker="ICE-BREAKER")
tile_grid("Ground Rules",[
 "Set your mobile phone to silent mode.","Participate actively — no question is too small.",
 "Mutual respect: agree to disagree.","One conversation at a time.",
 "Be punctual; return from breaks on time.","Learn by doing — try every hands-on lab."],
 kicker="HOUSEKEEPING",cols=2,size=15)
_dl=flow_h("Access Course Materials",[
 getattr(C,"MATERIALS_STEP",f"Open the {C.COURSE_CODE} course page or the trainer-supplied Drive folder"),
 "Open the courseware links for this course",
 "Download the Slides, Learner Guide and Lesson Plan",
 f"Open the labs folder for all {len(ACTIVITIES)} lab folders",
 "Keep the files together as you work"],kicker="COURSE MATERIALS")
# Course-page URL as a wide caption (kept out of the narrow chips so it never wraps mid-token)
txt(_dl,Inches(0.85),Inches(6.5),Inches(11.6),Inches(0.4),
    [[(getattr(C,"MATERIALS_CAPTION",f"Course page:  {getattr(C,'COURSE_PAGE','www.tertiarycourses.com.sg')}"),15,_acc(BLUE),True)]],align=PP_ALIGN.CENTER)
# Optional classroom sign-in accounts (course_data.TRAINING_ACCOUNTS).
_acct=getattr(C,"TRAINING_ACCOUNTS",None)
if _acct:
    cards3(_acct.get("title","Training Accounts"),
           [(CARD_COLORS[i%3],h,b) for i,(h,b) in enumerate(_acct["cards"])],
           kicker=_acct.get("kicker","CLASSROOM ACCESS"),size=16)
# Lesson plan overview — derived entirely from course_data (day themes + the
# topic→lab mapping) so it can never drift from the LP or the labs.
def _lab_range(acts):
    """Render a lab list compactly: contiguous runs collapse to 'Labs 2-5',
    gaps are listed ('Labs 2-5, 11'), and a single lab reads 'Lab 1'."""
    ns=sorted(a["num"] for a in acts)
    if not ns: return ""
    runs=[]; s=p=ns[0]
    for n in ns[1:]:
        if n==p+1: p=n; continue
        runs.append((s,p)); s=p=n
    runs.append((s,p))
    parts=[str(a) if a==b else f"{a}–{b}" for a,b in runs]
    return f" ({'Lab' if len(ns)==1 else 'Labs'} {', '.join(parts)})"
def _topic_line(t):
    return (f"Topic {t['num']}: {t['title']}{_lab_range(TOPIC_ACTS.get(t['num'],[]))}",1)
def _topics_by_day():
    """Which topics are taught on which day — read from the SAME schedule the
    Lesson Plan is built from, so the deck can never contradict the LP. Falls
    back to an even split only if the schedule can't be resolved."""
    try:
        def _lt(nums): return ""      # schedule text isn't needed, only the rows
        sched=C.SCHEDULE(_lt) if callable(getattr(C,"SCHEDULE",None)) else getattr(C,"SCHEDULE",{})
        by_day={}
        for day,(_theme,rows) in sched.items():
            found=[]
            for row in rows:
                if row[3] not in ("topic","lab"): continue
                text=row[4]; low=text.lower()
                for t in C.TOPICS:
                    if t["num"] in found: continue
                    head=t["title"].split(" — ")[0].strip()   # e.g. "Define" from "Define — Scope the Problem"
                    # Also match any significant word of the title as an
                    # ALL-CAPS phase label ("FOUNDATIONS", "MEASURE", …).
                    caps=[w.upper() for w in re.findall(r"[A-Za-z]{4,}",t["title"])]
                    if (f"topic {t['num']}" in low or t["title"].lower() in low
                            or head.upper() in text
                            or any(c in text for c in caps)):
                        found.append(t["num"])
            by_day[day]=found
        if any(by_day.values()):
            seen=set(); out={}
            for day in sorted(by_day):                 # a topic belongs to the first day it appears
                out[day]=[n for n in by_day[day] if not (n in seen or seen.add(n))]
            return out
    except Exception:
        pass
    half=(len(C.TOPICS)+1)//2
    return {1:[t["num"] for t in C.TOPICS[:half]], 2:[t["num"] for t in C.TOPICS[half:]]}

_BY_DAY=_topics_by_day()
_TB={t["num"]:t for t in C.TOPICS}
_left=([(_topic_line(t)[0],0) for t in C.TOPICS] if C.DAYS==1 else
       [(f"Day 1 — {C.DAY_THEMES[1]}",0)]+[_topic_line(_TB[n]) for n in _BY_DAY.get(1,[]) if n in _TB])
_inst=getattr(C,"INSTRUCTIONAL_MINUTES",getattr(C,"DAY_MINUTES",480))
if C.DAYS==1:
    _right=[
        ("Daily timing",0),(getattr(C,"DAILY_TIMING","9:30am–6:30pm"),1),
        ("Instructional time",0),(f"{_inst/60:g} hours · {len(ACTIVITIES)} connected labs",1),
        ("Learning arc",0),("Concept → demonstrate → build → verify → discuss → recap",1),
    ]
    _rhead="Day format"
else:
    _d2=min(2,C.DAYS)
    _right=[(f"Day {_d2} — {C.DAY_THEMES[_d2]}",0)]+[_topic_line(_TB[n]) for n in _BY_DAY.get(_d2,[]) if n in _TB]+[
        ("Daily timing",0),(getattr(C,"DAILY_TIMING","9:30am–6:30pm"),1)]
    _rhead=f"Day {_d2}"
two_col(f"Lesson Plan — {C.DAYS} Day{'s' if C.DAYS>1 else ''}, {_inst*C.DAYS/60:g} instructional hours",
        _left,_right,kicker="SCHEDULE",lhead="Course sequence",rhead=_rhead)
# COURSE_OVERVIEW["after_schedule"] lists overview parts shown right after the
# Lesson Plan slide (e.g. the course roadmap) instead of in the concepts section.
_AFTER_SCHED=set((getattr(C,"COURSE_OVERVIEW",None) or {}).get("after_schedule",[]))
if "pillars" in _AFTER_SCHED and C.COURSE_OVERVIEW.get("pillars"):
    cards3(C.COURSE_OVERVIEW.get("pillars_title","What You'll Build"),
           [(CARD_COLORS[i%3],t,b) for i,(t,b) in enumerate(C.COURSE_OVERVIEW["pillars"])],
           kicker="COURSE ROADMAP")
# Learning-outcome tiles built straight from course_data. Optional per-course
# short titles via course_data.LO_TITLES; otherwise fall back to "LO1", "LO2", …
_LO_TITLES=getattr(C,"LO_TITLES",[])
_lo_tiles=[(_LO_TITLES[i] if i<len(_LO_TITLES) else f"LO{i+1}",
            lo.split(": ",1)[1] if ": " in lo else lo)
           for i,lo in enumerate(C.LEARNING_OUTCOMES)]
tile_grid("Learning Outcomes",_lo_tiles,kicker="WHAT YOU'LL ACHIEVE",cols=2,size=15)
# NON-WSQ: there is NO assessment. Instead, set out how learning is reinforced
# in class — practice, feedback and self-check against the learning outcomes.
flow_h("How You'll Learn",[
 "Trainer demonstrates the concept",
 "You build it yourself in the hands-on lab",
 "Verify with the lab's 'Test it' step",
 "Discuss and troubleshoot together",
 "Recap against the learning outcomes"],kicker="LEARNING APPROACH")

# ---------------- CORE CONCEPTS ----------------
# Generic, data-driven course-concepts section. A course supplies its own
# framing via optional course_data fields; nothing here is tied to a specific
# subject, so the same engine builds any non-WSQ course.
_OVERVIEW=getattr(C,"COURSE_OVERVIEW",None)
# COURSE_OVERVIEW["move_to_first_topic"] lists parts (statement, pillars, arc,
# deep_dives, ...) rendered at the start of the first topic instead of here.
_MOVED=set((_OVERVIEW or {}).get("move_to_first_topic",[]))
def _overview_parts(want):
    O=_OVERVIEW
    if "concepts" in want and O.get("concepts"):
        tile_grid(O.get("concepts_title","Key Concepts"),O["concepts"],kicker="OVERVIEW",cols=2,size=15)
    if "framework" in want and O.get("framework"):
        tile_grid(O.get("framework_title","The Framework"),O["framework"],
                  kicker="THE BUILDING BLOCKS",cols=2,size=14)
    if "statement" in want and O.get("statement"):
        st=O["statement"]
        big_statement(st.get("headline",""),st.get("body",""),st.get("kicker",""),color=BLUE)
    if "pillars" in want and O.get("pillars"):
        cards3(O.get("pillars_title","What You'll Build"),
               [(CARD_COLORS[i%3],t,b) for i,(t,b) in enumerate(O["pillars"])],
               kicker="COURSE ROADMAP")
    if "arc" in want and O.get("arc"):
        content(O.get("arc_title","How Every Lab Progresses"),O["arc"],kicker="THE LEARNING ARC")
    if "deep_dives" in want:
        for _deep in O.get("deep_dives",[]):
            tile_grid(_deep["title"],_deep["items"],
                      kicker=_deep.get("kicker","CONCEPT DEEP DIVE"),cols=2,size=14,accent=BLUE)
_PARTS=[p for p in ["concepts","framework","statement","pillars","arc","deep_dives"] if p not in _AFTER_SCHED]
if _OVERVIEW and [p for p in _PARTS if p not in _MOVED]:
    section("CORE CONCEPTS",_OVERVIEW.get("section_title","Course Fundamentals"),"")
    _overview_parts([p for p in _PARTS if p not in _MOVED])

# ---------------- TOPICS + ACTIVITIES ----------------
# Optional per-lab screenshot slides. A course drops images into
# courseware/assets/screenshots/ and maps them in course_data.LAB_SHOTS:
#   LAB_SHOTS = {2: [("file.png", "Label", "Caption"), ...]}
_SHOTDIR=os.path.join(REPO,"courseware","assets","screenshots")
_SHOTS=getattr(C,"LAB_SHOTS",{})
def _lab_extras(num):
    for fn,label,cap in _SHOTS.get(num,[]):
        p=os.path.join(_SHOTDIR,fn)
        if os.path.exists(p):
            shot(f"{label}",p,kicker=f"LAB {num} · SCREENSHOT",caption=cap)


# Concept slides for one sub-topic. `tag` is the kicker prefix: 'LAB n' when the
# section is taught right before lab n, else 'TOPIC nn'.
def _render_section(t,sec,accent,tag):
    _b=sec.get("brief")
    if _b:
        # Slide-ready brief: one 3-card concept slide + one "Try it" slide.
        # The full definition/why/how/example text lives in the Learner Guide.
        # brief["single"]: one explainer slide only (no 3-card concept slide).
        if not _b.get("single"):
            cards3(sec["title"],[(accent,"WHAT IT IS",[_b["what"]]),
                                 (TEAL,"WHY IT MATTERS",[_b["why"]]),
                                 (VIOLET,"CHECK IT",[_b["check"]])],
                   kicker=f"{tag} · CONCEPT",size=19)
        # Optional tile slide for a sub-topic (e.g. interface tour, five principles, Agent Builder fields).
        if sec.get("tiles"):
            _t=sec["tiles"]
            tile_grid(_t["title"],_t["items"],kicker=f"{tag} · {_t.get('kicker','KEY POINTS')}",
                      cols=_t.get("cols",2),size=_t.get("size",15),accent=accent)
        if sec.get("compare"):   # side-by-side comparison after the key-point tiles
            _c=sec["compare"]
            compare_table(_c.get("title",sec["title"]),_c["headers"],_c["rows"],kicker=f"{tag} · COMPARE",accent=accent)
        if _b.get("flow"):
            flow_h(_b["flow"]["title"],_b["flow"]["steps"],kicker=f"{tag} · HOW IT WORKS",color=accent)
        _chars=sum(len(x) for x in _b["prompts"])
        _tt=sec["title"] if _b.get("single") else f"{_b.get('try_title','Try It in Copilot')} — {sec['title']}"
        two_col(_tt,_b["prompts"],_b.get("verify",[]),
                kicker=f"{tag} · {_b.get('kicker','HOW TO USE IT')}",
                lhead=_b.get("try_head","TYPE THIS IN COPILOT"),rhead=_b.get("check_head","THEN CHECK"),
                size=16 if _chars<=330 else 15)
        # Optional real UI screenshots for this sub-topic (files in courseware/assets/screenshots/).
        for _sh in _b.get("shots",[]):
            _k=f"{tag} · SCREENSHOT"
            if _sh["kind"]=="pair":
                _ps=[(os.path.join(_SHOTDIR,f),l,c) for f,l,c in _sh["images"]]
                if all(os.path.isfile(p) for p,_l,_c in _ps):
                    shot_pair(_sh["title"],_ps,kicker=_k,accent=accent)
                continue
            _img=os.path.join(_SHOTDIR,_sh["file"])
            if not os.path.isfile(_img):
                continue
            if _sh["kind"]=="callouts":
                shot_callouts(_sh["title"],_img,_sh["items"],kicker=_k,accent=accent)
            else:
                shot(_sh["title"],_img,kicker=_k,caption=_sh.get("caption",""),accent=accent)
        _tour=getattr(C,"INTERFACE_TOUR",None)
        if _tour and _tour.get("after")==sec["title"]:
            _img=os.path.join(_SHOTDIR,_tour.get("screenshot",""))
            if _tour.get("screenshot") and os.path.isfile(_img):
                shot_callouts(_tour["title"],_img,_tour["items"],kicker=f"{tag} · INTERFACE",accent=accent)
            else:
                tile_grid(_tour["title"],_tour["items"],kicker=f"{tag} · INTERFACE",cols=2,size=15,accent=accent)
            _mimg=os.path.join(_SHOTDIR,_tour.get("models_screenshot",""))
            if _tour.get("models") and _tour.get("models_screenshot") and os.path.isfile(_mimg):
                shot_callouts(_tour.get("models_title","Choosing a Model"),_mimg,_tour["models"],
                              kicker=f"{tag} · INTERFACE",accent=accent)
            elif _tour.get("models"):
                tile_grid(_tour.get("models_title","Choosing a Model"),_tour["models"],
                          kicker=f"{tag} · INTERFACE",cols=2,size=16,accent=accent)
        return
    cards3(
        sec["title"],
        [
            (accent,"WHAT",[sec["definition"]]),
            (TEAL,"WHY IT MATTERS",[sec["why"]]),
            (VIOLET,"HUMAN CHECK",[
                "Ground the task in approved facts.",
                "Review evidence, privacy, rights and tone.",
                "Approve, edit or stop before use.",
            ]),
        ],
        kicker=f"{tag} · CONCEPT",
    )
    flow_h(
        f"How It Works — {sec['title']}",
        sec.get("how",[]),
        kicker=f"{tag} · PROCESS",
        color=accent,
    )
    _decision=[]
    if sec.get("use_when"):
        _decision.append(("Use when",0,True))
        _decision.extend((x,1) for x in sec["use_when"])
    if sec.get("avoid_when"):
        _decision.append(("Avoid when",0,True))
        _decision.extend((x,1) for x in sec["avoid_when"])
    two_col(
        f"In Practice — {sec['title']}",
        sec.get("example",[]),
        _decision,
        kicker=f"{tag} · WORKED EXAMPLE",
        lhead="WORKED EXAMPLE",
        rhead="DECISION GUIDE",
    )
    if sec.get("quality"):
        cards3(
            f"Quality Lens — {sec['title']}",
            [
                (CARD_COLORS[i % len(CARD_COLORS)], heading, [body])
                for i, (heading, body) in enumerate(sec["quality"])
            ],
            kicker=f"{tag} · PRACTITIONER CONTROL",
        )

try:
    from prompt_explanations import SAMPLE_EXPLAIN as _SAMPLE_EXPLAIN
except ImportError:
    _SAMPLE_EXPLAIN={}
# All slides for one lab: overview, screenshots, sample prompts and checks.
def _render_lab(t,a):
    activity_overview(
        f"LAB {a['num']}", a["title"], ". ".join(a["desc"].split(". ")[:2])+".", a["build"], a["services"],
        kicker=(f"LAB {a['num']} THEME · {a['theme'].upper()}" if a.get("theme") else f"TOPIC {t['code']} · HANDS-ON"),
        workflow=a.get("workflow", []),
    )
    _lab_extras(a["num"])
    if a.get("sample_prompts"):
        _ex=_SAMPLE_EXPLAIN.get(a["num"])
        if _ex:   # prompt + what it does (and the formula Copilot writes)
            prompt_explain(f"Sample Prompts — Lab {a['num']}",
                           [(lbl,pr,ex) for (lbl,pr),ex in zip(a["sample_prompts"][:5],_ex)],
                           kicker=f"LAB {a['num']} · PROMPTS TO TRY")
        else:
            content(f"Sample Prompts — Lab {a['num']}",
                    [f"{lbl}: {pr}" for lbl,pr in a["sample_prompts"][:5]],
                    kicker=f"LAB {a['num']} · PROMPTS TO TRY",size=14)
    # Keep the deck concept-first: the overview above carries objective,
    # context, outcome and key workflow; click-by-click detail lives in the
    # aligned lab Markdown and Learner Guide.
    if a.get("checks"):
        # Checklist of (what to check, expected result) - easier to follow than a paragraph.
        tile_grid(f"Check Your Results — Lab {a['num']}", a["checks"],
                  kicker=f"LAB {a['num']} · VERIFY", cols=2, size=15, accent=TEAL)
    else:
        test_slide(a["title"], a["test"], kicker=f"LAB {a['num']} · VERIFY")

for t in C.TOPICS:
    accent=TOPIC_THEME.get(t["num"],BLUE)
    section(f"TOPIC {t['code']}", t["title"], t["code"], t["subtitle"], accent=accent)
    # The big picture opens Topic 1: Copilot is the agentic AI interface, the Office apps are its tools.
    _hub=getattr(C,"COPILOT_HUB",None)
    if _hub and t is C.TOPICS[0]:
        hub(_hub["title"],_hub["center"],_hub["apps"],flow=_hub.get("flow"),kicker=_hub.get("kicker","THE BIG PICTURE"),accent=TEAL)
    if _MOVED and t is C.TOPICS[0]:
        _overview_parts([p for p in _PARTS if p in _MOVED])
    # concept slide(s) — visual tile grid instead of a bullet list (topic-accented)
    # Non-WSQ: no exam, so the kicker shows the topic's share of course time
    # (course_data may omit `weighting` entirely).
    _w=t.get("weighting")
    # tile_grid paginates past TILE_MAX items, so a long concept list is safe here.
    tile_grid(f"Key Concepts — {t['title']}", t["concepts"],
              kicker=(f"KEY CONCEPTS · {_w.upper()}" if _w else "KEY CONCEPTS"),
              cols=3 if len(t["concepts"])==3 else 2, size=16, accent=accent)
    # Every stated sub-topic receives full concept teaching before its labs:
    # what/why, a visual process, a worked example and a use/avoid comparison.
    acts=TOPIC_ACTS[t["num"]]
    # a card summary of the labs in this topic
    # Split the topic's labs into at most three cards. Only emit cards that
    # actually hold labs — a topic with one or two labs renders one or two
    # cards rather than padding the row with empty "—" placeholders.
    third=max(1,(len(acts)+2)//3)
    groups=[g for g in (acts[i:i+third] for i in range(0,len(acts),third)) if g][:3]
    cards=[(CARD_COLORS[gi], _lab_range(g).strip(" ()"),
            [x for a in g for x in ([(a["theme"],0,True),(a["title"],1)] if a.get("theme") else [a["title"]])])
           for gi,g in enumerate(groups)]
    cards3(f"Hands-On Labs — {t['title']}", cards, kicker="WHAT YOU'LL DO")
    # per activity
    # Interleave: concepts for Lab n, then Lab n. Sections without a `lab` key
    # are taught first, before the topic's first lab.
    _secs=t.get("sections",[])
    for sec in [x for x in _secs if not x.get("lab")]:
        _render_section(t,sec,accent,f"TOPIC {t['code']}")
    for a in acts:
        from maintenance_visuals import add_visuals
        add_visuals(a["num"],globals())
        for sec in [x for x in _secs if x.get("lab")==a["num"]]:
            _render_section(t,sec,accent,f"LAB {a['num']}")
        _render_lab(t,a)
    # topic recap
    _topic_recaps=getattr(C,"TOPIC_RECAPS",{}).get(t["num"],[])
    _recap_lines=(
        [f"{label}: {evidence}" for label,evidence in _topic_recaps]
        if _topic_recaps
        else ["You can now: "+a["objective"] for a in {x["objective"]:x for x in acts}.values()][:6]
    )
    content(f"Recap - {t['title']}",_recap_lines,kicker="TOPIC RECAP",size=17)

# ---------------- CLOSE ----------------
section("WRAP-UP","Course Summary & Next Steps","")
# "What You Achieved" tiles built straight from the learning outcomes so they can never drift
# Achievement tiles reuse the learning-outcome titles so they can never drift.
_ach_tiles=[(_LO_TITLES[i] if i<len(_LO_TITLES) else f"LO{i+1}",
             lo.split(": ",1)[1] if ": " in lo else lo)
            for i,lo in enumerate(C.LEARNING_OUTCOMES)]
tile_grid("What You Achieved",_ach_tiles,kicker="LEARNING OUTCOMES",cols=2,size=15)
_next=getattr(C,"NEXT_STEPS",None)
if _next:
    content(_next.get("title","Continuing Your Journey"),_next["items"],kicker="NEXT STEPS")
content("Keep Practising After the Course",[
 "Re-run the labs on your own machine — repetition is what makes the skills stick.",
 "Apply the techniques to a real process or project in your own organisation.",
 *getattr(C,"WRAP_UP_LINES",[f"Keep your downloaded {C.COURSE_CODE} course files and use the lab checkpoints to restart safely.",
 "Explore the follow-on courses at www.tertiarycourses.com.sg."])],kicker="WRAP-UP")
# Optional closing message tiles (course_data.CLOSING_TILES), shown right before Thank You.
_close=getattr(C,"CLOSING_TILES",None)
if _close:
    tile_grid(_close["title"],_close["items"],kicker=_close.get("kicker","CLOSING"),
              cols=_close.get("cols",2),size=_close.get("size",15),accent=TEAL)
_ty=getattr(C,"THANK_YOU",{})
big_statement("Thank You!",
              _ty.get("body","You now have the practical skills from every lab in this course — keep applying them to your own work."),
              _ty.get("kicker","THANK YOU FOR ATTENDING"),color=TEAL)

# Fade slide transition on every slide — matches the source masterclass deck's
# fade aesthetic. python-pptx has no transition API, so inject the XML directly.
from lxml import etree as _et
from pptx.oxml.ns import qn as _qn
_TRANS=('<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'spd="med"><p:fade/></p:transition>')
for _s in prs.slides:
    if _s.element.find(_qn('p:transition')) is None:
        _s.element.append(_et.fromstring(_TRANS))

OUT=os.path.join(REPO,"courseware",f"{C.SHORT_TITLE}-{C.VERSION}.pptx")
prs.save(OUT)
print(f"Saved {OUT}  ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
