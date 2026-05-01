"""End-to-end GEPA optimization demo.

Dry-run mode verifies construction paths without calling any LM; the live run
requires OPENAI_API_KEY (or equivalent) and will consume tokens.

Usage:
    uv run python example_gepa.py --dry-run
    OPENAI_API_KEY=... uv run python example_gepa.py --auto light
"""

from __future__ import annotations

import argparse
from pathlib import Path


def build():
    import dspy

    class QA(dspy.Signature):
        """Answer the question concisely."""

        question: str = dspy.InputField()
        answer: str = dspy.OutputField()

    program = dspy.ChainOfThought(QA)

    def make_example(q, a):
        return dspy.Example(question=q, answer=a).with_inputs("question")

    trainset = [
        make_example("2 + 2?", "4"),
        make_example("Capital of Japan?", "Tokyo"),
        make_example("H2O is the formula for?", "water"),
        make_example("Largest planet?", "Jupiter"),
        make_example("sqrt(144)?", "12"),
    ]
    valset = [
        make_example("5 * 6?", "30"),
        make_example("Capital of Italy?", "Rome"),
        make_example("Boiling point of water in C?", "100"),
    ]

    def rich_metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
        pred_ans = str(getattr(pred, "answer", "")).strip().lower()
        gold_ans = gold.answer.strip().lower()
        correct = gold_ans in pred_ans or pred_ans in gold_ans
        score = 1.0 if correct else 0.0
        if correct:
            feedback = "Correct — the answer matched expected output."
        else:
            feedback = (
                f"Incorrect. Got {pred_ans!r}, expected {gold_ans!r}. "
                f"Likely issue: reasoning overshot the concise final answer. "
                f"Next time, end with only the answer value, no prose."
            )
        return dspy.Prediction(score=score, feedback=feedback)

    return program, trainset, valset, rich_metric


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model", default="openai/gpt-4o")
    ap.add_argument("--reflection-model", default=None)
    ap.add_argument("--auto", default="light", choices=["light", "medium", "heavy"])
    ap.add_argument("--log-dir", default="./gepa_logs")
    args = ap.parse_args()

    import dspy

    program, trainset, valset, rich_metric = build()

    if args.dry_run:
        # dspy.LM(...) construction is a no-op on the network; safe without API key.
        stub_reflection_lm = dspy.LM(args.model, temperature=1.0, max_tokens=8000)
        optimizer = dspy.GEPA(
            metric=rich_metric,
            auto=args.auto,
            reflection_lm=stub_reflection_lm,
            track_stats=True,
            log_dir=args.log_dir,
        )
        print(
            f"OK: constructed dspy.GEPA (auto={args.auto}) with "
            f"{len(trainset)} trainset / {len(valset)} valset examples."
        )
        _ = optimizer
        return 0

    dspy.configure(lm=dspy.LM(args.model))
    reflection_lm = dspy.LM(
        args.reflection_model or args.model, temperature=1.0, max_tokens=8000
    )

    evaluator = dspy.Evaluate(
        devset=valset,
        metric=rich_metric,
        num_threads=4,
        display_progress=True,
        provide_traceback=True,
    )
    print(f"Baseline: {evaluator(program).score:.3f}")

    optimizer = dspy.GEPA(
        metric=rich_metric,
        auto=args.auto,
        reflection_lm=reflection_lm,
        candidate_selection_strategy="pareto",
        use_merge=True,
        num_threads=4,
        track_stats=True,
        track_best_outputs=True,
        log_dir=args.log_dir,
        seed=0,
    )
    optimized = optimizer.compile(student=program, trainset=trainset, valset=valset)

    print(f"Optimized: {evaluator(optimized).score:.3f}")
    out = Path("optimized_program.json")
    optimized.save(str(out), save_program=False)
    print(f"Saved → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
