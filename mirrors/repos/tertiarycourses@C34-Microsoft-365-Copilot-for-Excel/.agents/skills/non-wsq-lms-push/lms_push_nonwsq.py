#!/usr/bin/env python3
"""
lms_push_nonwsq.py — publish a NON-WSQ course's Google Drive courseware links onto
its course record in the tertiarycourses.com.sg storefront admin.

Reads the current files from the course's Drive folder (via rclone), takes their
"anyone with the link can view" URLs, and writes them to the storefront:

    Trainer Slides URL  <- the .pptx in  Trainer Slides
    Learner Slides URL  <- the .pdf  in  Learner Slides
    Lesson Plan URL     <- the LP-*.pdf in  Lesson Plan
    Learner Guide URL   <- the LG-*.pdf in  Learner Guide
    Lab URL             <- the  Activities  FOLDER itself (not a file)

Lab URL is a folder link because a lab set is many worksheets plus the trainer's
datasets and templates — there is no single file to point at.

Transport: POST /courses/api_courseware on the storefront, authed with an
X-API-Key header. Unlike the WSQ LMS-TMS endpoint this IS a partial update — it
writes only the keys present in the body — so no read-modify-write dance is
needed and fields this script does not manage (courseware_link, brochure_link)
are left untouched.

Credentials:
    TC_API_KEY   the X-API-Key shared secret (required)
    TC_API       storefront base URL (default https://www.tertiarycourses.com.sg)

Usage:
    python3 lms_push_nonwsq.py --sku C524 [--drive-folder <link>] [--dry-run]

The Drive folder defaults to the course's existing `courseware_link` on the
storefront, so after one $non-wsq-gdrive-push the SKU alone is enough.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

REMOTE = os.environ.get("GDRIVE_REMOTE", "gdrive")
API = os.environ.get("TC_API", "https://www.tertiarycourses.com.sg").rstrip("/")

# storefront field -> (Drive folder canonical name, lowercase fuzzy hint)
FOLDERS = {
    "trainer_slides_url": ("Trainer Slides", "trainer slide"),
    "learner_slides_url": ("Learner Slides", "learner slide"),
    "lesson_plan_url":    ("Lesson Plan", "lesson plan"),
    "learner_guide_url":  ("Learner Guide", "learner guide"),
    "lab_url":            ("Activities", "activit"),
}
LABELS = {
    "trainer_slides_url": "Trainer Slides URL",
    "learner_slides_url": "Learner Slides URL",
    "lesson_plan_url":    "Lesson Plan URL",
    "learner_guide_url":  "Learner Guide URL",
    "lab_url":            "Lab URL",
}


# ---------------------------------------------------------------- Google Drive

def rc(args, root, parse=False):
    r = subprocess.run(["rclone", *args, "--drive-root-folder-id", root],
                       capture_output=True, text=True)
    if r.returncode != 0:
        err = r.stderr.strip()
        if "couldn't fetch token" in err or "didn't find section" in err:
            raise SystemExit(
                f"rclone is not authorised yet.\nRun once:  rclone config create {REMOTE} drive scope=drive\n"
                f"and complete the Google sign-in in the browser.\n\nrclone said: {err[:300]}")
        raise SystemExit(f"rclone {' '.join(args[:2])} failed: {err[:600]}")
    return json.loads(r.stdout or "[]") if parse else r.stdout.strip()


def folder_id(link):
    """Accept a Drive folder URL or a bare folder ID. A '/u/N/' segment only
    selects a browser profile and is not part of the ID."""
    m = re.search(r"(?:folders/|[?&]id=)([A-Za-z0-9_-]{10,})", link or "")
    fid = m.group(1) if m else (link or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{10,}", fid):
        raise SystemExit(f"Not a Google Drive folder link or ID: {link!r}")
    return fid


def find_dir(root, canonical, hint):
    dirs = rc(["lsjson", f"{REMOTE}:", "--dirs-only"], root, parse=True)
    match = (next((d for d in dirs if d["Name"].strip().lower() == canonical.lower()), None)
             or next((d for d in dirs if hint in d["Name"].strip().lower()), None))
    if not match:
        return None, [d["Name"] for d in dirs]
    return match, None


def files_in(root, path):
    """Current files in a folder (archive/ is a subfolder, so it is not listed)."""
    return rc(["lsjson", f"{REMOTE}:{path}", "--files-only"], root, parse=True)


def pick(files, pred):
    """Best match by predicate; ties broken by newest ModTime."""
    hits = [f for f in files if pred(f["Name"])]
    if not hits:
        return None, []
    hits.sort(key=lambda f: f.get("ModTime", ""), reverse=True)
    return hits[0], hits


def collect_links(root):
    """Resolve the five links on Drive.

    Returns ({field: (label, url)}, [descriptions of what could not be resolved])."""
    pptx = lambda n: n.lower().endswith(".pptx")
    pdf = lambda n: n.lower().endswith(".pdf")
    lg = lambda n: pdf(n) and re.match(r"^lg[-_ ]", n.lower())
    lp = lambda n: pdf(n) and re.match(r"^lp[-_ ]", n.lower())

    out, missing = {}, []

    def take(field, pred, what):
        canonical, hint = FOLDERS[field]
        d, available = find_dir(root, canonical, hint)
        if not d:
            missing.append(f"{LABELS[field]}: Drive folder '{canonical}' not found "
                           f"(present: {', '.join(available) or 'nothing'}). "
                           "Run $non-wsq-gdrive-push first.")
            return
        name = d["Name"]

        # Lab URL points at the Activities FOLDER, not a file inside it.
        if field == "lab_url":
            rc(["link", f"{REMOTE}:{name}"], root)   # ensure anyone-with-link
            out[field] = (f"{name}/", f"https://drive.google.com/drive/folders/{d['ID']}")
            return

        files = files_in(root, name)
        f, hits = pick(files, pred)
        if not f:
            missing.append(f"{LABELS[field]}: no {what} in Drive folder '{name}' "
                           f"(present: {', '.join(x['Name'] for x in files) or 'nothing'})")
            return
        if len(hits) > 1:
            print(f"  ! {len(hits)} candidates in '{name}' — using '{f['Name']}' "
                  f"(not: {', '.join(h['Name'] for h in hits[1:])})")
        rc(["link", f"{REMOTE}:{name}/{f['Name']}"], root)   # ensure anyone-with-link
        out[field] = (f["Name"], f"https://drive.google.com/file/d/{f['ID']}/view?usp=sharing")

    take("trainer_slides_url", pptx, ".pptx slide deck")
    take("learner_slides_url", pdf, ".pdf slide deck")
    take("lesson_plan_url", lp, "LP-*.pdf")
    take("learner_guide_url", lg, "LG-*.pdf")
    take("lab_url", None, "Activities folder")
    return out, missing


# ---------------------------------------------------------------- storefront API

def api_key():
    key = os.environ.get("TC_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "TC_API_KEY is not set.\n"
            "It is the storefront's shared API secret (Magento config "
            "courses/general/wsq_schedule_api_key).\n"
            "Export it, ideally from your shell profile so it stays out of this repo:\n"
            "    export TC_API_KEY='…'")
    return key


def api(method, payload=None, sku=None):
    url = f"{API}/courses/api_courseware"
    data = None
    if method == "GET" and sku:
        url += f"?sku={urllib.parse.quote(sku)}"
    if payload is not None:
        data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method=method, headers={
        "X-API-Key": api_key(),
        "Content-Type": "application/json",
        "Accept": "application/json",
        # The storefront's bot filter 403s the default "Python-urllib/x.y"
        # User-Agent before the request ever reaches the controller.
        "User-Agent": "tertiary-courseware-push/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:400]
        try:
            msg = json.loads(body).get("message", body)
        except Exception:
            msg = body
        raise SystemExit(f"{method} {url} -> HTTP {e.code}: {msg}")
    except urllib.error.URLError as e:
        raise SystemExit(f"Could not reach {url}: {e.reason}")


def main():
    ap = argparse.ArgumentParser(description="Push non-WSQ courseware links to tertiarycourses.com.sg")
    ap.add_argument("--sku", required=True, help="course code, e.g. C524")
    ap.add_argument("--drive-folder", help="Drive folder link/ID (default: the course's courseware_link)")
    ap.add_argument("--dry-run", action="store_true", help="show what would be written; change nothing")
    args = ap.parse_args()

    print(f"Course: {args.sku}   ({API})")
    current = api("GET", sku=args.sku)
    print(f"  {current.get('name', '?')}")

    link = args.drive_folder or current.get("courseware", {}).get("courseware_link", "")
    if not link:
        raise SystemExit(
            "No Drive folder to read from: the course has no Courseware Link and "
            "--drive-folder was not given.\n"
            "Set the Courseware Link on the course, or pass --drive-folder <link>.")
    root = folder_id(link)
    print(f"  Drive folder: {root}{' (from courseware_link)' if not args.drive_folder else ''}")

    resolved, missing = collect_links(root)
    print()
    for field in FOLDERS:
        if field in resolved:
            name, url = resolved[field]
            print(f"  {LABELS[field]:<20} {url}")
            print(f"  {'':<20} [{name}]")
    for m in missing:
        print(f"  !! {m}")

    if not resolved:
        raise SystemExit("\nNothing resolved on Drive — nothing to push.")

    payload = {"sku": args.sku}
    changed = []
    for field, (_name, url) in resolved.items():
        if current.get("courseware", {}).get(field, "") != url:
            payload[field] = url
            changed.append(field)

    print()
    if not changed:
        print("All five links already match what is on the course — nothing to write.")
        return
    print(f"Will write {len(changed)} field(s): {', '.join(LABELS[f] for f in changed)}")

    if args.dry_run:
        print("Dry run — nothing was modified.")
        return

    result = api("POST", payload)
    if not result.get("ok"):
        raise SystemExit(f"Write failed: {result}")
    print(f"Written: {', '.join(LABELS[f] for f in result.get('written', []))}")
    if missing:
        print(f"\n!! {len(missing)} link(s) could NOT be resolved (see above) and were left unchanged.")
    print("Done.")


if __name__ == "__main__":
    main()
