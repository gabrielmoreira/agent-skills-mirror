"""
build_reaction_scheme.py — Assemble a multi-step reaction scheme as ChemDraw CDXML
and render it to PNG, with automatic grid layout, globally unique object ids, and
conditions text placed in the clear gap over each arrow (never on a structure).

Why this exists: hand-assembling scheme CDXML repeatedly produces the same defects
— duplicate object ids, each arrow emitted twice, and conditions text overlapping
the neighbouring structure. This helper does the bookkeeping mechanically so those
classes of bug cannot occur, and always writes the PNG alongside the CDXML.

Usage (library):
    from build_reaction_scheme import build_scheme
    steps = [
        {"smiles": "O=C1CCCC1", "name": "cyclopentanone"},
        # `conditions` are the reagents for the arrow LEADING INTO this step:
        {"smiles": "O=C1C(Br)C(Br)C(Br)C1Br", "name": "tetrabromide",
         "conditions": ["Br2 (excess)", "AcOH, 25 C"]},
        ...
    ]
    build_scheme(steps, "scheme.cdxml", "scheme.png", title="My Synthesis", cols=4)

Usage (CLI):
    python build_reaction_scheme.py steps.json scheme.cdxml scheme.png "My Synthesis"
    # steps.json is a JSON list of the step dicts shown above.

Requires: rdkit (built with ChemDraw write support); epam.indigo only if a PNG is
requested. Runnable from the repo root.
"""
from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import rdChemDraw, rdDepictor

# Layout constants (ChemDraw units; default bond length 30, y increases downward).
CELL_W = 320.0   # horizontal pitch between structure centers
CELL_H = 320.0   # vertical pitch between rows
MARGIN = 60.0
ARROW_GAP = 14.0  # clearance between a structure edge and an arrow end
COND_DY = 22.0    # first conditions line offset above a horizontal arrow


def _fragment_for(smiles: str, frag_id: int, first_atom_id: int):
    """Return (fragment_element, next_id, bbox) with globally unique ids, centered on 0,0."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"invalid SMILES: {smiles}")
    rdDepictor.SetPreferCoordGen(True)
    rdDepictor.Compute2DCoords(mol)
    frag = ET.fromstring(rdChemDraw.MolToChemDrawBlock(mol)).find("page/fragment")

    # Renumber every id in the fragment into a private block so no two fragments collide.
    remap: dict[str, str] = {}
    nid = first_atom_id
    frag.set("id", str(frag_id))
    for el in list(frag.iter("n")) + list(frag.iter("b")):
        remap[el.get("id")] = str(nid)
        el.set("id", str(nid))
        nid += 1
    for b in frag.iter("b"):
        b.set("B", remap[b.get("B")])
        b.set("E", remap[b.get("E")])

    # Center the fragment on the origin so callers can translate it to a cell center.
    xs, ys = [], []
    for n in frag.iter("n"):
        x, y = map(float, n.get("p").split())
        xs.append(x)
        ys.append(y)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    for n in frag.iter("n"):
        x, y = map(float, n.get("p").split())
        n.set("p", f"{x - cx} {y - cy}")
    half_w, half_h = (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2
    return frag, nid, (half_w, half_h)


def _place(frag, cx: float, cy: float):
    """Translate a centered fragment to canvas center (cx, cy)."""
    for n in frag.iter("n"):
        x, y = map(float, n.get("p").split())
        n.set("p", f"{x + cx} {y + cy}")


def _cell_center(i: int, cols: int, cell_w: float, cell_h: float):
    """Boustrophedon (snake) grid: row 0 left->right, row 1 right->left, ..."""
    row, col = divmod(i, cols)
    vis_col = col if row % 2 == 0 else (cols - 1 - col)
    cx = MARGIN + vis_col * cell_w + cell_w / 2
    cy = MARGIN + row * cell_h + cell_h / 2
    return cx, cy, row, vis_col


def build_scheme(steps, out_cdxml, out_png=None, title=None, cols=4):
    """Build a scheme CDXML from a list of step dicts; optionally render a PNG.

    Returns (cdxml_path, png_path_or_None).
    """
    root = ET.Element("CDXML", {"BondLength": "30", "LabelFont": "21",
                                "LabelSize": "10", "CaptionFont": "21", "CaptionSize": "10"})
    ft = ET.SubElement(root, "fonttable")
    ET.SubElement(ft, "font", {"id": "21", "charset": "iso-8859-1", "name": "Arial"})
    ct = ET.SubElement(root, "colortable")
    for r, g, b in [(1, 1, 1), (0, 0, 0)]:
        ET.SubElement(ct, "color", {"r": str(r), "g": str(g), "b": str(b)})
    page = ET.SubElement(root, "page")
    scheme = ET.SubElement(page, "scheme", {"id": "1"})

    next_id = 1000          # atom/bond id counter (fragment interiors)
    obj_id = 100            # ids for fragments, arrows, text, steps
    def new_obj():
        nonlocal obj_id
        obj_id += 1
        return obj_id

    # Pass 1: build every fragment centered on the origin and measure it, so the
    # cell size can be derived from the LARGEST structure. Fixed cells overlap once
    # a structure is wider than the cell; sizing to the biggest bbox prevents that.
    built = []
    for step in steps:
        fid = new_obj()
        frag, next_id, bbox = _fragment_for(step["smiles"], fid, next_id)
        built.append((fid, frag, bbox, step))
    max_w = max(2 * b[0] for _, _, b, _ in built)
    max_h = max(2 * b[1] for _, _, b, _ in built)
    cell_w = max(CELL_W, max_w + 150)   # + room for the arrow and conditions text
    cell_h = max(CELL_H, max_h + 130)   # + room for the name label and conditions

    # Pass 2: place each fragment at its cell center; add the name label.
    frag_ids, centers, bboxes = [], [], []
    for i, (fid, frag, bbox, step) in enumerate(built):
        cx, cy, _, _ = _cell_center(i, cols, cell_w, cell_h)
        _place(frag, cx, cy)
        page.append(frag)
        frag_ids.append(fid)
        centers.append((cx, cy))
        bboxes.append(bbox)
        if step.get("name"):
            # A structure that ends a row gets a vertical arrow out of its bottom;
            # put its name ABOVE so the label never sits on that arrow.
            vertical_source = (i % cols == cols - 1) and (i < len(built) - 1)
            name_y = cy - bbox[1] - 22 if vertical_source else cy + bbox[1] + 34
            t = ET.SubElement(page, "t", {"id": str(new_obj()),
                                          "p": f"{cx} {name_y}", "Justification": "Center"})
            ET.SubElement(t, "s", {"font": "21", "size": "10", "color": "0",
                                   "face": "0"}).text = step["name"]

    # Arrows + conditions between consecutive structures.
    for i in range(len(steps) - 1):
        (ax, ay), (bx, by) = centers[i], centers[i + 1]
        (ahw, ahh), (bhw, bhh) = bboxes[i], bboxes[i + 1]
        cond = steps[i + 1].get("conditions", [])
        arrow_id = new_obj()
        if abs(ay - by) < 1.0:          # same row -> horizontal arrow in the gap
            if bx > ax:                 # pointing right
                tail_x, head_x = ax + ahw + ARROW_GAP, bx - bhw - ARROW_GAP
            else:                       # snake row: pointing left
                tail_x, head_x = ax - ahw - ARROW_GAP, bx + bhw + ARROW_GAP
            ET.SubElement(page, "arrow", {
                "id": str(arrow_id), "FillType": "None", "ArrowheadType": "Solid",
                "ArrowheadHead": "Full", "HeadSize": "1500",
                "Head3D": f"{head_x} {ay} 0", "Tail3D": f"{tail_x} {ay} 0"})
            mid_x = (tail_x + head_x) / 2
            for k, line in enumerate(cond):
                t = ET.SubElement(page, "t", {"id": str(new_obj()),
                                              "p": f"{mid_x} {ay - COND_DY - 14 * (len(cond) - 1 - k)}",
                                              "Justification": "Center"})
                ET.SubElement(t, "s", {"font": "21", "size": "9", "color": "0",
                                       "face": "0"}).text = line
        else:                           # row change -> vertical arrow (same column)
            tail_y, head_y = ay + ahh + ARROW_GAP, by - bhh - ARROW_GAP
            ET.SubElement(page, "arrow", {
                "id": str(arrow_id), "FillType": "None", "ArrowheadType": "Solid",
                "ArrowheadHead": "Full", "HeadSize": "1500",
                "Head3D": f"{ax} {head_y} 0", "Tail3D": f"{ax} {tail_y} 0"})
            mid_y = (tail_y + head_y) / 2
            for k, line in enumerate(cond):
                t = ET.SubElement(page, "t", {"id": str(new_obj()),
                                              "p": f"{ax + 16} {mid_y - 7 + 14 * k}",
                                              "Justification": "Left"})
                ET.SubElement(t, "s", {"font": "21", "size": "9", "color": "0",
                                       "face": "0"}).text = line
        # Wire the reaction step (ids only; geometry lives on the page objects).
        ET.SubElement(scheme, "step", {
            "id": str(new_obj()),
            "ReactionStepReactants": str(frag_ids[i]),
            "ReactionStepProducts": str(frag_ids[i + 1]),
            "ReactionStepArrows": str(arrow_id)})

    if title:
        t = ET.SubElement(page, "t", {"id": str(new_obj()),
                                      "p": f"{MARGIN} {MARGIN - 34}", "Justification": "Left"})
        ET.SubElement(t, "s", {"font": "21", "size": "16", "color": "0", "face": "1"}).text = title

    cdxml = ET.tostring(root, encoding="unicode")
    # Fail loudly on malformed XML instead of writing a file ChemDraw would reject.
    ET.fromstring(cdxml)
    Path(out_cdxml).write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + cdxml, encoding="utf-8")

    # The PNG is not optional: a .cdxml is not viewable without ChemDraw, so the
    # preview is the only evidence the file is correct. Render it or raise.
    if out_png is None:
        out_png = str(Path(out_cdxml).with_suffix(".png"))
    try:
        from indigo import Indigo
        from indigo.renderer import IndigoRenderer
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "PNG rendering needs the 'epam.indigo' package (pip install epam.indigo). "
            "Never deliver a .cdxml without its PNG preview."
        ) from exc
    ind = Indigo()
    rnd = IndigoRenderer(ind)
    ind.setOption("render-output-format", "png")
    ind.setOption("render-background-color", "1,1,1")
    ind.setOption("render-image-width", 1800)
    rnd.renderToFile(ind.loadReaction(cdxml), out_png)
    return out_cdxml, out_png


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    steps = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out_cdxml = sys.argv[2]
    out_png = sys.argv[3] if len(sys.argv) > 3 else None
    title = sys.argv[4] if len(sys.argv) > 4 else None
    c, p = build_scheme(steps, out_cdxml, out_png, title=title)
    print(f"Wrote {c}" + (f" + {p}" if p else ""))
