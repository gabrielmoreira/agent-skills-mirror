"""Tests for comments.py: python3 -m unittest discover -s skills/comment-sweep/scripts"""

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import comments  # noqa: E402

SCRIPT = Path(__file__).with_name("comments.py")


def lexed(name, src):
    tokens, found = comments.lex(name, textwrap.dedent(src).lstrip("\n"))
    return [t for t, _ in tokens], [(text, kind) for text, _, kind in found]


def same_code(name, before, after):
    return lexed(name, before)[0] == lexed(name, after)[0]


class Lexing(unittest.TestCase):
    def test_js_strings_regexes_and_templates_hide_comment_markers(self):
        code, found = lexed("a.ts", """
            const url = "http://x.dev/*not*/"; // real
            const re = /\\/\\/[^/]*/g; /* real */
            const t = `a ${ "//" + `${b /* real */}` } // still template`;
        """)
        self.assertEqual([text for text, _ in found], ["// real", "/* real */", "/* real */"])
        self.assertIn('"http://x.dev/*not*/"', code)

    def test_removing_comments_keeps_the_code(self):
        before = """
            // narrate
            export function f(a: number) { /* inline */ return a + 1 } // trailing
        """
        self.assertTrue(same_code("a.ts", before, "export function f(a: number) { return a + 1 }\n"))
        self.assertFalse(same_code("a.ts", before, "export function f(a: number) { return a + 2 }\n"))
        self.assertFalse(same_code("a.ts", "a/*x*/b", "ab"))

    def test_directives(self):
        _, found = lexed("a.ts", """
            // eslint-disable-next-line no-console
            // @ts-expect-error upstream types lag
            /// <reference types="vite/client" />
            const x = /*#__PURE__*/ make();
            /** @deprecated use g */
            // global cache for users
            // This function does the thing
        """)
        kinds = [kind for _, kind in found]
        self.assertEqual(kinds, ["directive"] * 5 + ["comment"])
        self.assertEqual(found[-1][0], "// global cache for users\n// This function does the thing")

    def test_jsdoc_types_are_directives_only_in_javascript(self):
        src = "/** @param {string} id */\nfunction f(id) {}\n"
        self.assertEqual(lexed("a.js", src)[1][0][1], "directive")
        self.assertEqual(lexed("a.ts", src)[1][0][1], "comment")

    def test_python(self):
        code, found = lexed("a.py", '''
            """Module doc."""
            import os  # type: ignore[import]

            def f():
                """Add one.

                >>> f()
                1
                """
                # narrate
                return 1  # noqa: E501
        ''')
        self.assertEqual([kind for _, kind in found], ["doc", "directive", "directive", "comment", "directive"])
        self.assertNotIn('"""Module doc."""', code)

    def test_python_docstring_deletion_keeps_the_code(self):
        self.assertTrue(same_code("a.py", 'def f():\n    """Doc."""  # note\n    return 1\n', "def f():\n    return 1\n"))
        self.assertTrue(same_code("a.py", '"""Module."""\nimport os\n', "import os\n"))
        self.assertTrue(same_code("a.py", 'class A:\n    """Doc."""\n    x = 1\n', "class A:\n    x = 1\n"))
        self.assertFalse(same_code("a.py", 'def f():\n    """Only statement."""\n', "def f():\n"))

    def test_python_indentation_counts(self):
        before = "if a:\n    b()\n    # c\n    d()\n"
        self.assertTrue(same_code("a.py", before, "if a:\n    b()\n    d()\n"))
        self.assertFalse(same_code("a.py", before, "if a:\n    b()\nd()\n"))

    def test_go(self):
        code, found = lexed("a.go", """
            //go:build linux
            package x

            // Deprecated: use Bar.
            //export Foo
            func Foo() string { return `// raw` } // plain
        """)
        self.assertEqual([kind for _, kind in found], ["directive", "directive", "directive", "comment"])
        self.assertIn("`// raw`", code)

    def test_shell(self):
        code, found = lexed("a.sh", """
            #!/usr/bin/env bash
            n=${#arr[@]} # count
            cat <<EOF > out.conf
            # data, not a comment
            EOF
            echo done
        """)
        self.assertEqual(found, [("#!/usr/bin/env bash", "directive"), ("# count", "comment")])
        self.assertTrue(any("# data, not a comment" in t for t in code))
        self.assertFalse(same_code("a.sh", "a # c\nb\n", "a b\n"))

    def test_shebang_is_a_directive(self):
        self.assertEqual(lexed("a.sh", "#!/bin/sh\necho\n")[1], [("#!/bin/sh", "directive")])

    def test_rust(self):
        code, found = lexed("a.rs", """
            /// Adds.
            /// ```
            /// assert_eq!(add(1), 2);
            /// ```
            fn add<'a>(x: &'a i32) -> char { /* outer /* nested */ still */ '"' }
            // SAFETY: pointer is valid
        """)
        self.assertEqual([kind for _, kind in found], ["directive", "comment", "directive"])
        self.assertTrue(found[0][0].startswith("/// Adds.\n/// ```"))
        self.assertIn("'\"'", code)

    def test_sql_tool_comments(self):
        _, found = lexed("q.sql", "-- name: GetUser :one\nSELECT /*+ INDEX(u) */ * FROM u; -- plain\n")
        self.assertEqual([kind for _, kind in found], ["directive", "directive", "comment"])


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.env = {**os.environ, "TMPDIR": self.tmp.name + "/snap", "GIT_CONFIG_GLOBAL": os.devnull}
        os.mkdir(self.env["TMPDIR"])
        self.git("init", "-q", "-b", "main")
        self.write("old.ts", "// untouched old comment\nexport const a = 1\n")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base")
        self.git("checkout", "-qb", "feature")
        self.write("old.ts", "// untouched old comment\nexport const a = 1\n// added note\nexport const b = 2\n")
        self.write("new.ts", "// eslint-disable-next-line no-console\nconsole.log(1) // log it\n")
        self.write("vendor/lib.ts", "// vendored\n")

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, env=self.env)

    def write(self, rel, text):
        (self.repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.repo / rel).write_text(text)

    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.repo, capture_output=True, text=True, env=self.env)

    def test_list_then_check(self):
        listed = self.run_script("list", "--base", "main").stdout
        self.assertIn("old.ts:3: comment: // added note", listed)
        self.assertNotIn("untouched", listed)
        self.assertIn("new.ts:1: directive", listed)
        self.assertIn("new.ts:2: comment: // log it", listed)
        self.assertIn("vendor/lib.ts: skip: vendored", listed)

        self.write("old.ts", "// untouched old comment\nexport const a = 1\nexport const b = 2\n")
        self.write("new.ts", "// eslint-disable-next-line no-console\nconsole.log(1)\n")
        done = self.run_script("check")
        self.assertEqual(done.returncode, 0, done.stdout)
        self.assertIn("ok         new.ts  -1 +0 comments", done.stdout)

        self.write("new.ts", "console.log(2)\n")
        done = self.run_script("check")
        self.assertEqual(done.returncode, 1)
        self.assertIn("CODE       new.ts:1", done.stdout)
        self.assertIn("DIRECTIVE  new.ts:1", done.stdout)

    def test_paths_narrow_the_branch_diff(self):
        listed = self.run_script("list", "--base", "main", "old.ts").stdout
        self.assertIn("old.ts:3: comment: // added note", listed)
        self.assertNotIn("untouched", listed)
        self.assertNotIn("new.ts", listed)

    def test_nothing_in_scope(self):
        done = self.run_script("list", "--base", "main", "src")
        self.assertEqual(done.returncode, 1)
        self.assertIn("Nothing in scope", done.stderr)


if __name__ == "__main__":
    unittest.main()
