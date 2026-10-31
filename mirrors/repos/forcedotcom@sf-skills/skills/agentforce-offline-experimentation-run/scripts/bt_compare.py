#!/usr/bin/env python3
"""Compare two replay runs of the same units, unit by unit, against the noise between repeats.

    python3 scripts/bt_compare.py runs/base runs/cand [--noise-from runs/v0] [--out FILE]

Each unit x repeat scored in both runs is a pair. Per group (overall, step kind, node, golden tool)
the delta is in units: the sum of each unit's cand - base score, averaged over its repeats. Per
failure bucket, the net is the pairs that scored lower and ended in it, minus those that scored
higher and left it. A metric's tolerance is the largest difference on it between two repeats of
the noise run (default: BASE), at least 1 unit; a delta beyond it is a regression or a gain. A
bootstrap over sessions gives a 95% interval of the mean unit delta, for reading only. A failure
drops the pair from both runs, except a no answer: a timeout where the other run answered another
request or model scores 0, in the bucket no_answer.

Exit 0: no metric got worse beyond its tolerance. Exit 1: some did. Exit 2: the runs are not
comparable (other units, judge, k, seed, steps, router nodes, equivalent tools, timeout or btlib
code; or more than 10% infra errors, or more than 10% no answers, in a run). --force compares them
anyway, on the units both share. Exit 2 also when a dir is not a finished run, or bt_compare
fails: never a verdict.

Writes the comparison to --out (default CAND/compare.json, bt.compare/1). It lists the units that
moved by unit id, so keep it with the run dirs, out of git.
"""

import argparse
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from btlib import compare as comparelib  # noqa: E402
from btlib import results  # noqa: E402
from btlib.redact import redact  # noqa: E402


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("base", help="run dir of the baseline (sfap_replay.py --out-dir)")
    p.add_argument("cand", help="run dir of the candidate, on the same units")
    p.add_argument("--noise-from", metavar="DIR",
                   help="run dir whose repeats set the tolerances (default: BASE); same units, judge, steps, "
                        "router nodes, equivalent tools and btlib code as BASE")
    p.add_argument("--out", metavar="FILE", help="where to write the comparison (default CAND/compare.json)")
    p.add_argument("--force", action="store_true",
                   help="compare runs that are not comparable, on the units both share (recorded in the output)")
    p.add_argument("--bootstrap-samples", type=int, default=comparelib.BOOTSTRAP_SAMPLES, metavar="N",
                   help="session resamples for the 95%% intervals (default %(default)s; 0: none)")
    args = p.parse_args(argv)
    if args.bootstrap_samples < 0:
        p.error("--bootstrap-samples must be >= 0")
    return args


def main(argv=None):
    args = parse_args(argv)
    out = args.out or os.path.join(args.cand, "compare.json")
    try:
        res = comparelib.compare(args.base, args.cand, args.noise_from, force=args.force,
                                 samples=args.bootstrap_samples)
        results.write_json(out, res)  # 0600: unit ids name sessions
        lines = comparelib.report_lines(res)
    except comparelib.CompareError as e:
        print(f"error: {redact(str(e))}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"error: cannot write {out}: {e.strerror or e}", file=sys.stderr)
        return 2
    except Exception as e:  # a bug, or a run dir it did not foresee: exit 1 would read as a regression
        frame = traceback.extract_tb(e.__traceback__)[-1]
        print(f"error: bt_compare failed ({type(e).__name__} at {os.path.basename(frame.filename)}:{frame.lineno}); "
              "no verdict (exit 2)", file=sys.stderr)
        return 2
    for line in lines:
        print(redact(line))
    print(f"comparison: {out}")
    return comparelib.exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
