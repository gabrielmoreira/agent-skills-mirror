"""End-to-end DSPy pipeline: spec → program → metric → baseline → GEPA → save.

Dry-run validates every construction path without invoking an LM. Live mode
runs a light GEPA optimization and saves an artifact.

Usage:
    uv run python example_pipeline.py --dry-run
    OPENAI_API_KEY=... uv run python example_pipeline.py --auto light
"""

from __future__ import annotations

import argparse
from pathlib import Path


def build():
    import dspy

    class SentimentClassify(dspy.Signature):
        """Classify the sentiment of a short review as positive, negative, or neutral."""

        review: str = dspy.InputField()
        sentiment: str = dspy.OutputField(desc="one of: positive, negative, neutral")

    class SentimentProgram(dspy.Module):
        def __init__(self):
            super().__init__()
            self.classify = dspy.ChainOfThought(SentimentClassify)

        def forward(self, review: str):
            return self.classify(review=review)

    program = SentimentProgram()

    def ex(review, sentiment):
        return dspy.Example(review=review, sentiment=sentiment).with_inputs("review")

    trainset = [
        ex("Loved every minute, best purchase this year.", "positive"),
        ex("Total waste of money, broke in a week.", "negative"),
        ex("It's fine, does the job.", "neutral"),
        ex("Absolutely stunning craftsmanship!", "positive"),
        ex("Customer service was unhelpful and rude.", "negative"),
    ]
    valset = [
        ex("Works as advertised, no complaints.", "positive"),
        ex("Disappointed — missing parts and poor instructions.", "negative"),
        ex("Average product for an average price.", "neutral"),
    ]

    def rich_metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
        pred_s = str(getattr(pred, "sentiment", "")).strip().lower()
        gold_s = gold.sentiment.strip().lower()
        correct = pred_s == gold_s
        format_ok = pred_s in {"positive", "negative", "neutral"}
        score = 1.0 if correct else (0.2 if format_ok else 0.0)
        if correct:
            feedback = "Correct label and valid format."
        elif format_ok:
            feedback = (
                f"Wrong label (predicted {pred_s!r}, expected {gold_s!r}). "
                f"Re-read the review for the dominant emotional valence; "
                f"don't over-index on neutral when there's a clear strong word."
            )
        else:
            feedback = (
                f"Invalid format: {pred_s!r}. "
                f"Output exactly one of: positive, negative, neutral — no extra words."
            )
        return dspy.Prediction(score=score, feedback=feedback)

    return program, trainset, valset, rich_metric


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model", default="openai/gpt-4o")
    ap.add_argument("--auto", default="light", choices=["light", "medium", "heavy"])
    args = ap.parse_args()

    import dspy

    program, trainset, valset, rich_metric = build()

    if args.dry_run:
        evaluator = dspy.Evaluate(
            devset=valset,
            metric=rich_metric,
            num_threads=1,
            display_progress=False,
            provide_traceback=True,
        )
        # dspy.LM(...) construction does not call the network; safe offline.
        stub_reflection_lm = dspy.LM(args.model, temperature=1.0, max_tokens=8000)
        optimizer = dspy.GEPA(
            metric=rich_metric,
            auto=args.auto,
            reflection_lm=stub_reflection_lm,
            track_stats=True,
            log_dir="./gepa_logs",
        )
        print(
            f"OK: pipeline objects constructed "
            f"(program={type(program).__name__}, trainset={len(trainset)}, "
            f"valset={len(valset)}, auto={args.auto})."
        )
        _ = evaluator, optimizer
        return 0

    dspy.configure(lm=dspy.LM(args.model), track_usage=True)
    evaluator = dspy.Evaluate(
        devset=valset,
        metric=rich_metric,
        num_threads=4,
        display_progress=True,
        provide_traceback=True,
        save_as_json="runs/baseline.json",
    )
    Path("runs").mkdir(exist_ok=True)

    print(f"Baseline: {evaluator(program).score:.3f}")

    optimizer = dspy.GEPA(
        metric=rich_metric,
        auto=args.auto,
        reflection_lm=dspy.LM(args.model, temperature=1.0, max_tokens=8000),
        candidate_selection_strategy="pareto",
        track_stats=True,
        track_best_outputs=True,
        log_dir="./gepa_logs",
        num_threads=4,
        seed=0,
    )
    optimized = optimizer.compile(student=program, trainset=trainset, valset=valset)
    print(f"Optimized: {evaluator(optimized).score:.3f}")

    Path("artifacts").mkdir(exist_ok=True)
    optimized.save("artifacts/program.json", save_program=False)
    print("Saved artifacts/program.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
