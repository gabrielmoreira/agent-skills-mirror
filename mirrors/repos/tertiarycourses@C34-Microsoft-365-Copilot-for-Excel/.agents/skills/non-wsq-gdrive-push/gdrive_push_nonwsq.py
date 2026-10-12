#!/usr/bin/env python3
"""Push NON-WSQ courseware + labs to a Google Drive course folder via rclone,
archiving superseded versions. Upload-and-move only — nothing is ever deleted.

Usage:  python3 gdrive_push_nonwsq.py <drive-folder-link-or-id> [--repo DIR] [--dry-run]

Non-WSQ courses are commercial short courses: there is NO assessment, no SSG/WSQ
funding and no LMS Courseware-Link lookup. The destination folder is therefore
ALWAYS supplied by the user on the command line — there is no default and no
remembered folder, so material can never be published into the wrong course.

Routing (folders matched case-insensitively under the given root; created if missing):
  Trainer Slides  : the slide deck .pptx
  Learner Slides  : the slide deck .pdf
  Learner Guide   : LG .docx + .pdf
  Lesson Plan     : LP .docx + .pdf
  Activities      : the whole labs/ tree (rclone sync with --backup-dir)

There is deliberately NO Assessment routing — a non-WSQ course has no assessment.
If an assessment/ folder exists locally it is reported and SKIPPED, never uploaded.

Change detection: files whose MD5 already matches the Drive copy are SKIPPED (no
re-upload, no archiving). Only changed/new files are pushed.

Archiving: in each folder, every pre-existing file not identical to one being
pushed is MOVED server-side into that folder's lowercase "archive" subfolder.
Any "Archive"/"archives" variant is renamed to the canonical "archive", and any
"old versions"-style folder is merged into it. For labs, changed/removed files
are moved to Activities/archive by rclone's --backup-dir. Nothing is deleted.

Every newly uploaded file is set to "anyone with the link can view".

Prerequisite (one-time): `rclone config create gdrive drive scope=drive`.
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

REMOTE = os.environ.get("GDRIVE_REMOTE", "gdrive")


def folder_id(link):
    """Accept a Drive folder URL, an 'open?id=' URL, or a bare id.
    A '/u/N/' segment only selects a browser profile and is NOT part of the id."""
    if not link:
        return None
    m = re.search(r"(?:folders/|[?&]id=)([A-Za-z0-9_-]{10,})", link)
    return m.group(1) if m else link.strip()


def rc(args, root, parse=False, ok_codes=(0,)):
    cmd = ["rclone", *args, "--drive-root-folder-id", root]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode not in ok_codes:
        err = r.stderr.strip()
        if "couldn't fetch token" in err or "didn't find section" in err:
            raise SystemExit(f"rclone is not authorised yet.\nRun once:  rclone config create {REMOTE} drive scope=drive\n"
                             f"and complete the Google sign-in in the browser.\n\nrclone said: {err[:300]}")
        raise SystemExit(f"rclone {' '.join(args[:2])} failed: {err[:600]}")
    return json.loads(r.stdout or "[]") if parse else (r.stdout + r.stderr)


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def list_dirs(root, path=""):
    return rc(["lsjson", f"{REMOTE}:{path}", "--dirs-only"], root, parse=True)


def list_files(root, path):
    return rc(["lsjson", f"{REMOTE}:{path}", "--files-only", "--hash"], root, parse=True)


def find_or_create_dir(root, parent_path, canonical, hint, dry):
    dirs = list_dirs(root, parent_path)
    match = next((d for d in dirs if d["Name"].strip().lower() == canonical.lower()), None) \
        or next((d for d in dirs if hint in d["Name"].strip().lower()), None)
    if match:
        d = match
        return (f"{parent_path}/{d['Name']}" if parent_path else d["Name"]), d["Name"], False
    path = f"{parent_path}/{canonical}" if parent_path else canonical
    if not dry:
        rc(["mkdir", f"{REMOTE}:{path}"], root)
    return path, canonical, True


def ensure_archive(root, folder_path, dry):
    """Return <folder>/archive, creating it if absent and renaming any Archive/archives
    variant to the canonical lowercase 'archive'."""
    for d in list_dirs(root, folder_path):
        name = d["Name"]
        if not name.strip().lower().startswith("archiv"):
            continue
        if name == "archive":
            return f"{folder_path}/archive"
        print(f"    rename: {name}/  ->  archive/")
        if not dry:
            if name.lower() == "archive":  # case-only rename needs a two-step move
                rc(["moveto", f"{REMOTE}:{folder_path}/{name}", f"{REMOTE}:{folder_path}/__archive_tmp__"], root)
                rc(["moveto", f"{REMOTE}:{folder_path}/__archive_tmp__", f"{REMOTE}:{folder_path}/archive"], root)
            else:
                rc(["moveto", f"{REMOTE}:{folder_path}/{name}", f"{REMOTE}:{folder_path}/archive"], root)
        return f"{folder_path}/archive"
    print("    create: archive/")
    if not dry:
        rc(["mkdir", f"{REMOTE}:{folder_path}/archive"], root)
    return f"{folder_path}/archive"


def merge_old_versions(root, folder_path, archive_path, dry):
    """Merge any 'old versions'-style folder into archive/ (contents moved in,
    the emptied folder removed). Upload/move only — no file is ever deleted."""
    for d in list_dirs(root, folder_path):
        name = d["Name"]; low = name.strip().lower()
        if "old" in low and "version" in low:
            print(f"    merge:   {name}/  ->  archive/")
            if dry:
                continue
            for e in rc(["lsjson", f"{REMOTE}:{folder_path}/{name}"], root, parse=True):
                rc(["moveto", f"{REMOTE}:{folder_path}/{name}/{e['Name']}",
                    f"{REMOTE}:{archive_path}/{e['Name']}"], root)
            rc(["rmdir", f"{REMOTE}:{folder_path}/{name}"], root)


def push_folder(root, folder_path, files, dry, exists=True):
    """Push files into folder_path. Unchanged files are kept in place; EVERY other
    pre-existing file in the folder (old versions, old names, Google-native docs)
    is moved to <folder>/archive first. Nothing is ever deleted.

    `exists` is False when the folder is only going to be created (a dry run never
    creates it), in which case there is nothing on Drive to list or archive —
    listing it would fail with "directory not found"."""
    if not exists:
        print("    create: archive/")
        for path in files:
            print(f"    upload:  {os.path.basename(path)}")
        return
    archive_path = ensure_archive(root, folder_path, dry)
    merge_old_versions(root, folder_path, archive_path, dry)
    remote_files = list_files(root, folder_path)
    keep, to_upload = set(), []
    for path in files:
        fn = os.path.basename(path)
        same = next((f for f in remote_files if f["Name"] == fn), None)
        if same and (same.get("Hashes") or {}).get("md5") == md5(path):
            print(f"    unchanged: {fn} — skipped")
            keep.add(fn)
        else:
            to_upload.append(path)
    for f in remote_files:
        name = f["Name"]
        if name in keep:
            continue
        print(f"    archive: {name}  ->  archive/")
        if not dry:
            try:
                rc(["moveto", f"{REMOTE}:{folder_path}/{name}", f"{REMOTE}:{archive_path}/{name}"], root)
            except SystemExit as e:
                print(f"      WARNING: could not archive '{name}' — {str(e)[:200]}; continuing")
    for path in to_upload:
        fn = os.path.basename(path)
        print(f"    upload:  {fn}")
        if not dry:
            rc(["copyto", path, f"{REMOTE}:{folder_path}/{fn}"], root)
            link = rc(["link", f"{REMOTE}:{folder_path}/{fn}"], root).strip()
            print(f"      view link (anyone with the link): {link}")


def push_labs(root, labs_dir, dry, mirror=False):
    """Push labs/ into Activities.

    ADDITIVE by default (rclone copy): lab files are uploaded and updated, and
    anything else already in Activities is LEFT ALONE. That matters because the
    Activities folder is also where the trainer's working material lives —
    Excel datasets and .xlsx templates that have no counterpart in the repo. A
    mirroring sync would sweep all of it into archive/ on the first push.

    With --mirror, Activities is made to match labs/ exactly and the extras are
    moved to Activities/archive/ (never deleted)."""
    folder_path, real_name, created = find_or_create_dir(root, "", "Activities", "activit", dry)
    arch_name = "archive"
    excludes = {arch_name}
    if not created:
        # remember every archiv* variant so a pending (dry-run) rename can't leak
        # the old archive's contents into the plan
        excludes |= {d["Name"] for d in list_dirs(root, folder_path)
                     if d["Name"].strip().lower().startswith("archiv")}
        if mirror:
            ensure_archive(root, folder_path, dry)

    if mirror:
        print(f"  {real_name}{' (will be created)' if created else ''}:  MIRRORING labs/ "
              f"(replaced/removed files -> {real_name}/{arch_name}/)")
        args = ["sync", labs_dir, f"{REMOTE}:{folder_path}",
                "--backup-dir", f"{REMOTE}:{folder_path}/{arch_name}"]
    else:
        print(f"  {real_name}{' (will be created)' if created else ''}:  updating labs/ "
              f"(additive — existing datasets/templates are left untouched)")
        args = ["copy", labs_dir, f"{REMOTE}:{folder_path}"]
    args += ["--exclude", ".DS_Store", "--exclude", "~$*",
             "--checksum", "-v", "--stats-log-level", "NOTICE"]
    for e in excludes:
        args += ["--exclude", f"/{e}/**"]
    if dry:
        args.append("--dry-run")
    out = rc(args, root)
    moved, copied = [], []
    for line in out.splitlines():
        m = re.search(r"(?:INFO|NOTICE)\s*:\s*(.+?):\s*(Copied|Moved|Skipped copy|Skipped move)", line)
        if not m:
            continue
        name, action = m.group(1), m.group(2)
        (copied if "opy" in action or "opied" in action else moved).append(name)
    for name in sorted(set(moved)):
        print(f"    archive: {name}  ->  {arch_name}/")
    for name in sorted(set(copied)):
        print(f"    upload:  {name}")
    verb = "labs mirror" if mirror else "labs update"
    print(f"    {verb}: {len(set(copied))} file(s) uploaded, {len(set(moved))} archived "
          f"(unchanged files skipped automatically)")




# ------------------------------------------------------------------ link block

def print_link_block(root):
    """Emit the link block for what is CURRENTLY in the folder (archive/ excluded),
    ensuring each file is 'anyone with the link can view'. Safe to run on an
    unchanged push, where nothing was re-uploaded and so no link was printed."""

    def files_of(canonical, hint):
        dirs = list_dirs(root, "")
        d = (next((x for x in dirs if x["Name"].strip().lower() == canonical.lower()), None)
             or next((x for x in dirs if hint in x["Name"].strip().lower()), None))
        if not d:
            return None, []
        return d["Name"], rc(["lsjson", f"{REMOTE}:{d['Name']}", "--files-only"], root, parse=True)

    def link_for(folder, f):
        rc(["link", f"{REMOTE}:{folder}/{f['Name']}"], root)  # creates the reader permission
        return f"https://drive.google.com/file/d/{f['ID']}/view?usp=sharing"

    def one(canonical, hint, pred, label):
        folder, files = files_of(canonical, hint)
        hits = [f for f in files if pred(f["Name"])]
        if not hits:
            print(f"{label}: !! MISSING in '{canonical}'")
            return
        hits.sort(key=lambda f: f.get("ModTime", ""), reverse=True)
        if len(hits) > 1:
            print(f"  ! {len(hits)} candidates in '{folder}' — using '{hits[0]['Name']}' "
                  f"(not: {', '.join(h['Name'] for h in hits[1:])})")
        print(f"{label}: {link_for(folder, hits[0])}   [{hits[0]['Name']}]")

    pptx = lambda n: n.lower().endswith(".pptx")
    pdf = lambda n: n.lower().endswith(".pdf")
    docx = lambda n: n.lower().endswith(".docx")

    print("\n--- Course material link block ---")
    one("Trainer Slides", "trainer slide", pptx, "Trainer Slides — PPT")
    one("Learner Slides", "learner slide", pdf, "Learner Slides — PDF")
    one("Learner Guide", "learner guide", pdf, "Learner Guide — PDF")
    one("Learner Guide", "learner guide", docx, "Learner Guide — DOCX")
    one("Lesson Plan", "lesson plan", pdf, "Lesson Plan — PDF")
    one("Lesson Plan", "lesson plan", docx, "Lesson Plan — DOCX")


def newest(pattern):
    hits = sorted((h for h in glob.glob(pattern)
                   if not os.path.basename(h).startswith("~$")), key=os.path.getmtime)
    return hits[-1] if hits else None


def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    repo = "."
    args = [a for a in argv if not a.startswith("--")]
    if "--repo" in argv:
        repo = argv[argv.index("--repo") + 1]
        args = [a for a in args if a != repo]

    # The destination is ALWAYS user-supplied — never inferred, never remembered.
    if not args:
        raise SystemExit(
            "No Google Drive folder given.\n"
            "Usage: python3 gdrive_push_nonwsq.py <drive-folder-link-or-id> [--repo DIR] [--dry-run]\n"
            "Pass the course's Drive folder link explicitly — this script never guesses a "
            "destination, so one course's material can't land in another course's folder.")
    root = folder_id(args[0])
    if not root:
        raise SystemExit(f"Could not read a Drive folder id from: {args[0]}")

    if "--links-only" in argv:
        print_link_block(root)
        return

    cw = os.path.join(repo, "courseware")
    deck_ppt = newest(os.path.join(cw, "*v[0-9]*.pptx"))
    if not deck_ppt:
        raise SystemExit(f"No versioned slide deck found in {cw}")
    deck_pdf = os.path.splitext(deck_ppt)[0] + ".pdf"
    if not os.path.exists(deck_pdf):
        raise SystemExit(
            f"The slide-deck PDF is missing: {deck_pdf}\n"
            "Learners get the PDF, so build it first:\n"
            "  COURSE_REPO=<course-repo> bash "
            "<non-wsq-courseware-build-skill-dir>/build/build_courseware.sh")
    lg_docx = newest(os.path.join(cw, "LG-*.docx")); lg_pdf = newest(os.path.join(cw, "LG-*.pdf"))
    lp_docx = newest(os.path.join(cw, "LP-*.docx")); lp_pdf = newest(os.path.join(cw, "LP-*.pdf"))

    # NON-WSQ: there is no assessment. Never upload one, even if the folder exists.
    stray = [p for p in glob.glob(os.path.join(repo, "assessment", "*"))
             if os.path.isfile(p)]
    if stray:
        print(f"  ! assessment/ holds {len(stray)} file(s) — NOT uploaded "
              "(a non-WSQ course has no assessment).")

    routing = [
        ("Trainer Slides", "trainer slide", [deck_ppt]),
        ("Learner Slides", "learner slide", [deck_pdf]),
        ("Learner Guide", "learner guide", [lg_docx, lg_pdf]),
        ("Lesson Plan", "lesson plan", [lp_docx, lp_pdf]),
    ]
    print(f"Root folder: {root}{'  (DRY RUN — no changes will be made)' if dry else ''}")
    for canonical, hint, files in routing:
        files = [f for f in files if f and os.path.exists(f)
                 and not os.path.basename(f).startswith("~$")]
        if not files:
            print(f"  {canonical}: no local files found — skipped"); continue
        folder_path, real_name, created = find_or_create_dir(root, "", canonical, hint, dry)
        print(f"  {real_name}{' (will be created)' if created else ''}:")
        # On a dry run a "created" folder does not actually exist yet, so it
        # cannot be listed — treat it as empty rather than crashing.
        push_folder(root, folder_path, files, dry, exists=not (created and dry))

    labs_dir = os.path.join(repo, "labs")
    if os.path.isdir(labs_dir):
        push_labs(root, labs_dir, dry, mirror="--mirror" in argv)
    else:
        print("  Activities: no labs/ folder found — skipped")

    if dry:
        print("Dry run complete — nothing was modified.")
        return
    print("Done.")
    print_link_block(root)


if __name__ == "__main__":
    main()
