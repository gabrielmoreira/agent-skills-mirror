#!/usr/bin/env python3
"""Evaluate benchmark results and compute aggregate scores.

Two-phase workflow:
  1. prepare  — reads results and rubric, outputs evaluation template
  2. finalize — reads scored evaluation, computes aggregates, outputs scores.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Phase 1: prepare
# ---------------------------------------------------------------------------

def _read_result_file(path: Path) -> str | None:
    """Read a result file if it exists, otherwise return None."""
    return path.read_text(encoding="utf-8") if path.is_file() else None


def cmd_prepare(args: argparse.Namespace) -> int:
    """Read benchmark.json + results/ and produce evaluation.json for scoring."""
    benchmark_path: Path = args.benchmark
    results_dir: Path = args.results_dir
    output_path: Path = args.output
    num_runs: int = args.runs

    if not benchmark_path.is_file():
        print(f"Error: benchmark file not found at '{benchmark_path}'", file=sys.stderr)
        return 1
    if not results_dir.is_dir():
        print(f"Error: results directory not found at '{results_dir}'", file=sys.stderr)
        return 1

    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    evaluations = []

    for task in benchmark.get("tasks", []):
        task_id = task["id"]
        rubric = task.get("rubric", {})
        dimensions = list(rubric.keys())
        score_template = {dim: None for dim in dimensions}

        runs = []
        for run_idx in range(1, num_runs + 1):
            if num_runs == 1:
                # Backward compat: try old-style names first, then run-1 names
                with_content = _read_result_file(results_dir / f"{task_id}-with.md")
                if with_content is None:
                    with_content = _read_result_file(results_dir / f"{task_id}-run-1-with.md")
                without_content = _read_result_file(results_dir / f"{task_id}-without.md")
                if without_content is None:
                    without_content = _read_result_file(results_dir / f"{task_id}-run-1-without.md")
            else:
                with_content = _read_result_file(results_dir / f"{task_id}-run-{run_idx}-with.md")
                without_content = _read_result_file(results_dir / f"{task_id}-run-{run_idx}-without.md")

            if with_content is None:
                suffix = "" if num_runs == 1 else f" run {run_idx}"
                print(f"Warning: missing with-skill output for {task_id}{suffix}, skipping run", file=sys.stderr)
                continue
            if without_content is None:
                suffix = "" if num_runs == 1 else f" run {run_idx}"
                print(f"Warning: missing without-skill output for {task_id}{suffix}, skipping run", file=sys.stderr)
                continue

            runs.append(
                {
                    "run": run_idx,
                    "output_with_skill": with_content,
                    "output_without_skill": without_content,
                    "scores_with": dict(score_template),
                    "scores_without": dict(score_template),
                }
            )

        if not runs:
            print(f"Warning: no valid runs for {task_id}, skipping task", file=sys.stderr)
            continue

        evaluations.append(
            {
                "task_id": task_id,
                "prompt": task.get("prompt", ""),
                "rubric": rubric,
                "runs": runs,
            }
        )

    evaluation_doc = {
        "skill": benchmark.get("skill", "unknown"),
        "total_tasks": len(evaluations),
        "runs_per_task": num_runs,
        "instructions": (
            "For each task and each run, read both outputs and the rubric criteria. "
            "Assign a score from 0.0 to 1.0 for each dimension in scores_with "
            "and scores_without. Replace null values with numeric scores."
        ),
        "evaluations": evaluations,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(evaluation_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Evaluation template written to {output_path}")
    print(f"  Tasks to score: {len(evaluations)}")
    print(f"  Runs per task: {num_runs}")
    print(f"  Fill null scores in scores_with and scores_without for each run.")
    return 0


# ---------------------------------------------------------------------------
# Phase 2: finalize
# ---------------------------------------------------------------------------

def cmd_finalize(args: argparse.Namespace) -> int:
    """Read scored evaluation.json, compute aggregates, output scores.json."""
    evaluation_path: Path = args.evaluation
    output_path: Path = args.output

    if not evaluation_path.is_file():
        print(f"Error: evaluation file not found at '{evaluation_path}'", file=sys.stderr)
        return 1

    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    evaluations = evaluation.get("evaluations", [])
    runs_per_task = evaluation.get("runs_per_task", 1)

    if not evaluations:
        print("Error: no evaluations found in the file", file=sys.stderr)
        return 1

    # Validate that all scores are filled
    for ev in evaluations:
        for run_entry in ev.get("runs", []):
            for key in ("scores_with", "scores_without"):
                for dim, val in run_entry.get(key, {}).items():
                    if val is None:
                        print(
                            f"Error: {ev['task_id']}.run-{run_entry['run']}.{key}.{dim} "
                            f"is still null. Fill all scores before finalizing.",
                            file=sys.stderr,
                        )
                        return 1

    # Compute per-task scores (averaged across runs)
    task_results = []
    all_dimensions: set[str] = set()

    for ev in evaluations:
        runs = ev.get("runs", [])
        if not runs:
            continue

        # Collect all dimension names from first run
        first_run_dims = list(runs[0]["scores_with"].keys())
        all_dimensions.update(first_run_dims)

        # Average scores across runs
        avg_dims_with: dict[str, float] = {}
        avg_dims_without: dict[str, float] = {}
        for dim in first_run_dims:
            with_vals = [r["scores_with"].get(dim, 0) for r in runs]
            without_vals = [r["scores_without"].get(dim, 0) for r in runs]
            avg_dims_with[dim] = round(sum(with_vals) / len(with_vals), 4)
            avg_dims_without[dim] = round(sum(without_vals) / len(without_vals), 4)

        avg_with = sum(avg_dims_with.values()) / len(avg_dims_with) if avg_dims_with else 0
        avg_without = sum(avg_dims_without.values()) / len(avg_dims_without) if avg_dims_without else 0
        delta = avg_with - avg_without

        per_dim_delta = {}
        for dim in first_run_dims:
            per_dim_delta[dim] = round(avg_dims_with[dim] - avg_dims_without.get(dim, 0), 4)

        # Per-run scores for transparency
        per_run_scores = []
        for r in runs:
            dw = r["scores_with"]
            dwo = r["scores_without"]
            rw = sum(dw.values()) / len(dw) if dw else 0
            rwo = sum(dwo.values()) / len(dwo) if dwo else 0
            per_run_scores.append(
                {
                    "run": r["run"],
                    "scores_with": dw,
                    "scores_without": dwo,
                    "average_with": round(rw, 4),
                    "average_without": round(rwo, 4),
                    "delta": round(rw - rwo, 4),
                }
            )

        task_results.append(
            {
                "task_id": ev["task_id"],
                "prompt": ev.get("prompt", ""),
                "scores_with": avg_dims_with,
                "scores_without": avg_dims_without,
                "average_with": round(avg_with, 4),
                "average_without": round(avg_without, 4),
                "delta": round(delta, 4),
                "per_dimension_delta": per_dim_delta,
                "winner": "with" if delta > 0.01 else ("without" if delta < -0.01 else "tie"),
                "runs_count": len(runs),
                "per_run_scores": per_run_scores,
            }
        )

    # Compute aggregate
    sorted_dims = sorted(all_dimensions)
    dim_agg: dict[str, dict[str, float]] = {}
    for dim in sorted_dims:
        with_scores = [t["scores_with"].get(dim, 0) for t in task_results if dim in t["scores_with"]]
        without_scores = [t["scores_without"].get(dim, 0) for t in task_results if dim in t["scores_without"]]
        dim_agg[dim] = {
            "avg_with": round(sum(with_scores) / len(with_scores), 4) if with_scores else 0,
            "avg_without": round(sum(without_scores) / len(without_scores), 4) if without_scores else 0,
            "avg_delta": round(
                (sum(with_scores) / len(with_scores) - sum(without_scores) / len(without_scores)), 4
            )
            if with_scores and without_scores
            else 0,
        }

    total_tasks = len(task_results)
    wins = sum(1 for t in task_results if t["winner"] == "with")
    losses = sum(1 for t in task_results if t["winner"] == "without")
    ties = total_tasks - wins - losses

    overall_delta = (
        round(sum(t["delta"] for t in task_results) / total_tasks, 4)
        if total_tasks
        else 0
    )

    total_calls = total_tasks * runs_per_task * 2

    scores_doc = {
        "skill": evaluation.get("skill", "unknown"),
        "summary": {
            "total_tasks": total_tasks,
            "runs_per_task": runs_per_task,
            "total_calls": total_calls,
            "wins": wins,
            "losses": losses,
            "ties": ties,
            "win_rate": round(wins / total_tasks, 4) if total_tasks else 0,
            "overall_delta": overall_delta,
        },
        "dimensions": dim_agg,
        "tasks": task_results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(scores_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Scores written to {output_path}")
    print(f"  Overall delta: {overall_delta:+.4f}")
    print(f"  Win rate: {wins}/{total_tasks} ({scores_doc['summary']['win_rate']:.0%})")
    for dim, agg in dim_agg.items():
        print(f"  {dim}: with={agg['avg_with']:.2f}  without={agg['avg_without']:.2f}  Δ={agg['avg_delta']:+.4f}")
    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate benchmark results. Two phases: prepare → finalize.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Workflow:\n"
            "  1. python evaluate.py prepare  --benchmark benchmark.json --results-dir results/ --output evaluation.json\n"
            "     → Generates evaluation template for the agent to score\n\n"
            "  2. python evaluate.py finalize --evaluation evaluation.json --output scores.json\n"
            "     → Computes aggregates from scored evaluation\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # prepare
    p_prep = sub.add_parser("prepare", help="Prepare evaluation template from results")
    p_prep.add_argument("--benchmark", type=Path, required=True, help="Path to benchmark.json")
    p_prep.add_argument("--results-dir", type=Path, required=True, help="Path to results/ directory")
    p_prep.add_argument("--output", type=Path, default=Path("evaluation.json"), help="Output evaluation template path")
    p_prep.add_argument("--runs", type=int, default=1, help="Number of runs per task (default: 1, recommended: 3)")

    # finalize
    p_fin = sub.add_parser("finalize", help="Compute aggregates from scored evaluation")
    p_fin.add_argument("--evaluation", type=Path, required=True, help="Path to scored evaluation.json")
    p_fin.add_argument("--output", type=Path, default=Path("scores.json"), help="Output scores path")

    args = parser.parse_args(argv)

    if args.command == "prepare":
        return cmd_prepare(args)
    elif args.command == "finalize":
        return cmd_finalize(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
