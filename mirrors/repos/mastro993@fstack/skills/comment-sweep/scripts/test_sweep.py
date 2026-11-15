#!/usr/bin/env python3
"""Tests for sweep.py: python3 test_sweep.py"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SWEEP = Path(__file__).with_name("sweep.py")

APP = """\
// Copyright 2026 Acme
import { log } from "./log";

/**
 * Gets the user.
 * @param id the id
 */
export function getUser(id: string) {
  // call the api
  const url = "https://api.example.com/users"; // build the url
  /* old: fetch(url)
     .then(parse) */
  return fetch(url); // eslint-disable-line no-undef
}
"""

PAGE = """\
<!-- Main content -->
<main>{# loop over items #}</main>
{{!-- render the name --}}
<p>{/* the bell */}</p>
"""

INVENTORY = """\
src/app.ts:1: directive: Copyright 2026 Acme => keep: licence
src/app.ts:4-7: doc: Gets the user. @param id the id => delete: restated
src/app.ts:9: comment: call the api => delete: narration
src/app.ts:10: comment: build the url => delete: narration
src/app.ts:11-12: comment: old: fetch(url) .then(parse) => delete: dead code
src/app.ts:13: directive: eslint-disable-line no-undef => keep: directive
web/page.html:1: comment: Main content => delete: banner
web/page.html:2: comment: loop over items => delete: narration
web/page.html:3: comment: render the name => delete: narration
web/page.html:4: comment: the bell => delete: narration
"""


class SweepTest(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.repo, True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "T")
        self.write("README.md", "# App\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "base")
        self.git("checkout", "-qb", "feature")
        self.write("src/app.ts", APP)
        self.write("web/page.html", PAGE)
        self.write("vendor/lib.js", "// vendored\n")
        self.write("src/api.gen.ts", "// Code generated. DO NOT EDIT.\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "feature")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def read(self, rel):
        return (self.repo / rel).read_text()

    def sweep(self, *args):
        done = subprocess.run([sys.executable, str(SWEEP), *args], cwd=self.repo, capture_output=True, text=True)
        return done.returncode, done.stdout + done.stderr

    def scope(self, *args):
        code, out = self.sweep("scope", *args)
        self.assertEqual(code, 0, out)
        self.work = Path(out.splitlines()[0].removeprefix("work: "))
        self.addCleanup(shutil.rmtree, self.work, True)
        return out

    def scope_in(self, sub, *args):
        done = subprocess.run([sys.executable, str(SWEEP), "scope", *args], cwd=self.repo / sub, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.addCleanup(shutil.rmtree, Path(done.stdout.splitlines()[0].removeprefix("work: ")), True)
        return done.stdout

    def swept(self, inventory=INVENTORY):
        self.scope()
        (self.work / "inventory.txt").write_text(inventory)
        return self.sweep("apply")[1]

    def test_scope_lists_branch_files_and_skips(self):
        self.write("notes.txt", "# untracked\n")
        out = self.scope()
        self.assertIn("skip: vendor/lib.js — vendored or build output", out)
        self.assertIn("skip: src/api.gen.ts — generated or minified", out)
        self.assertIn("small: 3 files, 19 lines in scope, 1 batch", out)
        self.assertEqual((self.work / "batch-1.files").read_text().split(), ["notes.txt", "src/app.ts", "web/page.html"])
        diff = (self.work / "batch-1.diff").read_text()
        self.assertIn("+# untracked", diff)
        self.assertNotIn("README", diff)

    def test_scope_narrows_to_paths_and_full_takes_every_file(self):
        self.assertIn("small: 1 file, 4 lines", self.scope("web"))
        out = self.scope("--full")
        self.assertIn("small: 3 files, 19 lines in scope", out)
        self.assertFalse((self.work / "batch-1.diff").exists())
        self.assertIn("README.md", (self.work / "batch-1.files").read_text())

    def test_scope_covers_the_whole_repo_from_a_subdirectory(self):
        self.write("web/notes.txt", "# untracked\n")
        out = self.scope_in("web", "--full")
        self.assertIn("small: 4 files, 20 lines in scope", out)  # README.md and src/app.ts too
        self.assertIn("small: 2 files, 5 lines", self.scope_in("web", "--full", "."))  # a path stays relative to the cwd
        self.assertIn("small: 3 files, 19 lines", self.scope_in("web"))

    def test_scope_with_nothing_in_it(self):
        self.assertIn("small: 0 files, 0 lines in scope, 0 batches", self.scope("--full", "no/such/dir"))
        code, out = self.sweep("scope", "--full", "..")
        self.assertEqual((code, out.strip()), (1, f"..: outside the repository at {self.repo}"))

    def test_scope_splits_a_big_branch_into_batches(self):
        for n in range(45):
            self.write(f"src/m{n:02}.ts", "export const x = 1;\n" * 100)
        out = self.scope()
        self.assertIn("big: 47 files, 4518 lines in scope, 4 batches", out)
        self.assertIn("batch-1: 12 files, 1114 lines", out)

    def test_apply_deletes_exact_matches_and_leaves_the_rest(self):
        out = self.swept()
        self.assertIn("applied 6 of 8 deletes", out)
        self.assertIn("by hand (no exact match): web/page.html:2", out)  # a comment in the middle of a line
        self.assertIn("by hand (no exact match): web/page.html:4", out)
        app = self.read("src/app.ts")
        self.assertNotIn("Gets the user", app)
        self.assertNotIn("call the api", app)
        self.assertNotIn("old: fetch", app)
        self.assertIn('const url = "https://api.example.com/users";\n', app)
        self.assertIn("// eslint-disable-line no-undef", app)
        self.assertEqual(self.read("web/page.html"), "<main>{# loop over items #}</main>\n<p>{/* the bell */}</p>\n")

    def test_apply_runs_again_after_the_inventory_changes(self):
        late = "src/app.ts:13: directive: eslint-disable-line no-undef => "
        self.swept(INVENTORY.replace("id the id => delete: restated", "id the id => trim: restated"))
        self.write("src/app.ts", self.read("src/app.ts").replace(" * @param id the id\n", ""))
        (self.work / "inventory.txt").write_text(INVENTORY.replace(late + "keep: directive", late + "delete: unused directive"))
        out = self.sweep("apply")[1]
        self.assertIn("applied 1 of 3 deletes", out)  # the two left are the comments in the middle of a line
        self.assertNotIn("src/app.ts", out.split("unlisted")[0])  # the trim is done, so it is off the list
        self.assertIn("  return fetch(url);\n", self.read("src/app.ts"))
        self.assertIn(" * Gets the user.\n", self.read("src/app.ts"))

    def test_apply_cuts_a_trailing_comment_at_its_own_marker(self):
        self.write("src/loop.c", "i--; /* step down */\nprintf(\"x\"); /* say x */\nx = y - 1; // -- note --\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "c")
        out = self.swept(
            "src/loop.c:1: comment: step down => delete: narration\n"
            "src/loop.c:2: comment: say x => delete: narration\n"
            "src/loop.c:3: comment: -- note -- => delete: narration\n"
        )
        self.assertIn("applied 3 of 3 deletes", out)
        self.assertEqual(self.read("src/loop.c"), 'i--;\nprintf("x");\nx = y - 1;\n')
        self.assertEqual(self.sweep("check")[1].splitlines()[-1], "ok")
        self.write("src/loop.c", 'i\nprintf("x");\nx = y - 1;\n')  # a cut that took the code's `--;`
        self.assertIn("CUT src/loop.c:1: was: i--; /* step down */ now: i", self.sweep("check")[1])

    def test_scope_keeps_files_with_spaces_and_quotes_in_their_names(self):
        self.write("src/my file.py", "# one\n")
        self.write('src/say "hi".py', "# two\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "odd names")
        out = self.scope()
        self.assertIn("small: 4 files, 20 lines in scope", out)
        self.assertIn("+# one", (self.work / "batch-1.diff").read_text())
        self.assertIn('src/say "hi".py', (self.work / "batch-1.files").read_text())

    def test_apply_leaves_what_it_cannot_prove(self):
        self.write("src/app.ts", '"""Docstring."""\n/* a /* nested */ block */\n} // end of loop\n// two\n')
        self.git("commit", "-qam", "more")
        out = self.swept(
            "src/app.ts:1: doc: Docstring. => delete: restated\n"
            "src/app.ts:2: comment: a nested block => delete: dead code\n"
            "src/app.ts:3: comment: end of loop => delete: narration\n"
            "src/app.ts:4: comment: one => delete: narration\n"
        )
        self.assertIn("applied 1 of 4 deletes", out)
        self.assertEqual(self.read("src/app.ts"), '"""Docstring."""\n/* a /* nested */ block */\n}\n// two\n')

    def test_apply_keeps_the_wider_gap_and_lists_what_the_inventory_missed(self):
        self.write("jobs.py", 'URL = "https://example.com"\n\n\n# ---- helpers ----\n\n\ndef run():\n    pass  # nothing yet\n# the end\n')
        self.write("README.md", "# App\n\n# Usage\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "more")
        out = self.swept("jobs.py:4: comment: ---- helpers ---- => delete: banner\njobs.py:9: comment: the end => delete: narration\n")
        self.assertEqual(self.read("jobs.py"), 'URL = "https://example.com"\n\n\ndef run():\n    pass  # nothing yet\n')
        self.assertIn("unlisted: jobs.py:8: pass # nothing yet", out)
        self.assertIn("unlisted: src/app.ts:1: // Copyright 2026 Acme", out)
        self.assertNotIn("unlisted: jobs.py:1", out)  # a URL is not a comment
        self.assertNotIn("README.md", out)  # nor is a Markdown heading

    def test_check_passes_a_clean_sweep_and_maps_lines(self):
        self.swept()
        self.write("web/page.html", "<main></main>\n<p></p>\n")
        code, out = self.sweep("check")
        self.assertEqual(code, 0, out)
        self.assertIn("10 comments in 2 files: 8 delete, 2 keep", out)
        self.assertIn("  5 delete: narration", out)
        self.assertEqual(out.splitlines()[-1], "ok, once you have read the 2 above")
        self.assertIn("CUT web/page.html:2: was: <main>{# loop over items #}</main> now: <main></main>", out)
        self.assertIn("  src/app.ts:6: directive: eslint-disable-line no-undef => keep: directive", out)
        self.assertIn("  src/app.ts:9 (before): comment: call the api => delete: narration", out)

    def test_check_flags_code_directives_and_unfinished_work(self):
        self.swept()
        (self.work / "inventory.txt").write_text(INVENTORY.replace("the bell => delete: narration", "the bell"))
        app = self.read("src/app.ts").replace("return fetch(url); // eslint-disable-line no-undef", "return fetch(url, {});")
        self.write("src/app.ts", app.replace("// Copyright 2026 Acme\n", ""))
        self.write("build.log", "x\n")
        code, out = self.sweep("check")
        self.assertEqual(code, 1, out)
        self.assertIn("UNJUDGED web/page.html:4: the bell", out)
        self.assertIn("DIRECTIVE src/app.ts:1: // Copyright 2026 Acme", out)
        self.assertIn("DIRECTIVE src/app.ts:13: return fetch(url); // eslint-disable-line no-undef", out)
        self.assertIn("UNAPPLIED web/page.html:2: loop over items", out)
        self.assertIn("STRAY build.log", out)
        self.assertIn("FAILED: 5 to fix", out)
        (self.work / "inventory.txt").write_text(INVENTORY.replace("no-undef => keep: directive", "no-undef => delete: unused directive, eslint reports it"))
        out = self.sweep("check")[1]
        self.assertNotIn("DIRECTIVE src/app.ts:13", out.split("STRAY")[0])  # read, no longer counted
        self.assertIn("CUT src/app.ts:13: was: return fetch(url); // eslint-disable-line no-undef now: return fetch(url, {});", out)
        self.assertIn("FAILED: 4 to fix, 2 to read", out)

    def test_an_entry_outside_the_scope_stops_apply_and_fails_check(self):
        self.write("README.md", "# App\nMore.\n")  # line 1 is main's
        self.git("commit", "-qam", "more")
        stray = "README.md:1: comment: App => delete: banner\nvendor/lib.js:1: comment: vendored => delete: narration\n"
        out = self.swept(INVENTORY + stray)
        self.assertIn("OUTSIDE README.md:1: no line of it is in scope: App", out)
        self.assertIn("OUTSIDE vendor/lib.js:1: not a file in scope: vendored", out)
        self.assertIn("call the api", self.read("src/app.ts"))  # nothing applied until the inventory is right
        self.assertEqual(self.sweep("check")[0], 1)

    def test_check_shows_trims_and_rejects_new_code(self):
        self.swept(INVENTORY.replace("id the id => delete: restated", "id the id => trim: restated"))
        app = self.read("src/app.ts").replace(" * @param id the id\n", "").replace("return fetch(url);", "log(url);\n  return fetch(url);")
        self.write("src/app.ts", app)
        self.write("web/page.html", "<main></main>\n<p></p>\n")
        code, out = self.sweep("check")
        self.assertEqual(code, 1, out)
        self.assertIn("CUT src/app.ts:4-7: trimmed to: /** * Gets the user. */", out)
        self.assertIn("CODE src/app.ts:+9: log(url);", out)

    def test_check_allows_respacing_but_not_reindenting(self):
        self.write("src/app.ts", "const a   = 1; // one\nif (a) {\n  run();\n}\n")
        self.git("commit", "-qam", "more")
        self.swept("src/app.ts:1: comment: one => delete: narration\n")
        self.write("src/app.ts", "const a = 1;\nif (a) {\n    run();\n}\n")
        code, out = self.sweep("check")
        self.assertEqual(code, 1, out)
        self.assertEqual([row for row in out.splitlines() if row.startswith(("CODE", "CUT"))], ["CODE src/app.ts:3: run();"])


if __name__ == "__main__":
    unittest.main()
