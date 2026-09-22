import contextlib
import csv
import importlib.util
import io
import json
import random
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_data.py"
SPEC = importlib.util.spec_from_file_location("audit_data", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit)


class AuditDataTests(unittest.TestCase):
    def test_chi2_sf_matches_critical_values(self):
        for statistic, df in [(3.841, 1), (5.991, 2), (15.507, 8), (16.919, 9)]:
            self.assertAlmostEqual(audit.chi2_sf(statistic, df), 0.05, places=3)

    def test_grim(self):
        self.assertFalse(audit.grim("5.19", 28)["consistent"])
        self.assertTrue(audit.grim("5.18", 28)["consistent"])
        self.assertTrue(audit.grim("45.8", 24, percent=True)["consistent"])
        self.assertFalse(audit.grim("45.9", 24, percent=True)["consistent"])
        self.assertTrue(audit.grim("3.47", 25, items=3)["consistent"])
        self.assertFalse(audit.grim("3.46", 25, items=3)["consistent"])
        self.assertFalse(audit.grim("3.47", 25, items=4)["testable"])
        self.assertFalse(audit.grim("3.47", 200)["testable"])

    def test_grimmer(self):
        self.assertTrue(audit.grimmer("3.00", "1.58", 5)["consistent"])  # 1, 2, 3, 4, 5
        self.assertFalse(audit.grimmer("3.00", "1.60", 5)["consistent"])  # no integer sum of squares
        self.assertFalse(audit.grimmer("3.00", "1.66", 5)["consistent"])  # sum of squares 56 has the wrong parity
        self.assertTrue(audit.grimmer("2.33", "0.58", 3, items=3)["consistent"])  # item sums 6, 6, 9
        self.assertFalse(audit.grimmer("3.00", "1.6", 500)["testable"])

    def test_p_value_distributions(self):
        for test, statistic, df1, df2 in [("t", 2.228, 10, None), ("F", 4.171, 1, 30), ("F", 3.4928, 2, 20), ("z", 1.96, None, None)]:
            self.assertAlmostEqual(audit.p_value(test, statistic, df1, df2), 0.05, places=3)

    def test_statcheck(self):
        self.assertTrue(audit.statcheck("t(18) = 2.31, p = .033")["consistent"])
        self.assertTrue(audit.statcheck("χ2(1, N = 90) = 4.5, p = .03")["consistent"])
        self.assertTrue(audit.statcheck("t(12.7) = \u22121.70, p = .11")["consistent"])
        result = audit.statcheck("F(1, 30) = 2.10, p < .05")
        self.assertEqual((result["consistent"], result["decision_error"]), (False, True))
        result = audit.statcheck("t(30) = 1.80, p = .041")
        self.assertFalse(result["consistent"])
        self.assertIn("consistent if one-tailed", result["detail"])
        self.assertTrue(audit.statcheck("t(30) = 1.80, p = .041", tails=1)["consistent"])
        with self.assertRaises(ValueError):
            audit.statcheck("t = 2.1, p = .04")

    def test_terminal_digits_keep_dropped_trailing_zeros(self):
        self.assertEqual(audit.last_digits(["12.30", "45.6", "7.81", "0.05"]), ["0", "0", "1"])

    def test_fixed_relations(self):
        a = ["12.31", "15.07", "18.94", "21.12", "25.63"]
        self.assertEqual(audit.fixed_relation(a, [f"{float(v) + 1.37:.2f}" for v in a])["relation"], "difference")
        self.assertEqual(audit.fixed_relation(a, [f"{float(v) * 1.5:.2f}" for v in a])["relation"], "ratio")
        self.assertEqual(audit.fixed_relation(a, [f"{float(v) * 2.1 + 3.3:.2f}" for v in a])["relation"], "linear")
        self.assertIsNone(audit.fixed_relation(a, ["30.12", "22.84", "27.51", "19.66", "33.09"]))

    def test_shared_run_reports_copied_block_once(self):
        series = [
            {"id": "A", "values": ["1.2", "3.4", "5.6", "7.8", "9.1", "2.3"]},
            {"id": "B", "values": ["8.8", "3.4", "5.6", "7.8", "9.1", "4.4", "6.6"]},
        ]
        runs = audit.shared_runs(series, 4)
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["n"], 4)
        self.assertIn("items 2-5 of A equal items 2-5 of B", runs[0]["detail"])

    def test_prepare_and_scan_flag_derived_column_but_not_independent_data(self):
        rng = random.Random(7)
        rows = []
        for index in range(1, 61):
            control = rng.uniform(10, 60)
            rows.append([index, f"{control:.2f}", f"{control * 1.25:.2f}", f"{rng.uniform(10, 60):.2f}"])
        for row in rows[40:45]:
            row[3] = rows[len(rows) - 50 + int(row[0]) - 41][1]  # rows 11-15 of control pasted into other
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            table = root / "source.csv"
            with table.open("w", newline="") as handle:
                csv.writer(handle).writerows([["id", "control", "treated", "other"], *rows])
            workspace = root / "audit"
            with contextlib.redirect_stdout(io.StringIO()):
                audit.main(["prepare", "--input", str(table), "--output", str(workspace)])
                manifest = json.loads((workspace / "series.json").read_text())
                self.assertEqual([item["label"] for item in manifest["series"] if not item["include"]], ["id"])
                manifest["means"] = [{"id": "Table1-score", "mean": "3.00", "sd": "1.66", "n": 5}]
                manifest["tests"] = [{"id": "Fig1c", "report": "t(18) = 1.50, p = .01"}]
                (workspace / "series.json").write_text(json.dumps(manifest))
                audit.main(["scan", "--workspace", str(workspace)])
            findings = json.loads((workspace / "findings.json").read_text())
            flagged = {(row["check"], row["series_a"], row["series_b"]) for row in findings if row["flagged"]}
            self.assertEqual(
                flagged,
                {
                    ("fixed_ratio", "source.csv:source!B2:B61", "source.csv:source!C2:C61"),
                    ("shared_run", "source.csv:source!B2:B61", "source.csv:source!D2:D61"),
                    ("grimmer", "Table1-score", ""),
                    ("statcheck", "Fig1c", ""),
                },
            )


if __name__ == "__main__":
    unittest.main()
