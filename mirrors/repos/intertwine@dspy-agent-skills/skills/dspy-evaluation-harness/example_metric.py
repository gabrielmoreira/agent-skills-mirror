"""Runnable example: rich-feedback metric + dspy.Evaluate harness.

Usage:
    uv run python example_metric.py --dry-run   # validates Signature/metric construction
    OPENAI_API_KEY=... uv run python example_metric.py
"""

from __future__ import annotations

import argparse


def build():
    import dspy

    class QA(dspy.Signature):
        """Answer concisely and correctly."""

        question: str = dspy.InputField()
        answer: str = dspy.OutputField()

    program = dspy.ChainOfThought(QA)

    trainset = [
        dspy.Example(question="What is 2 + 2?", answer="4").with_inputs("question"),
        dspy.Example(question="Capital of France?", answer="Paris").with_inputs(
            "question"
        ),
        dspy.Example(question="Speed of light (m/s)?", answer="299792458").with_inputs(
            "question"
        ),
    ]

    def rich_metric(gold, pred, trace=None, pred_name=None, pred_trace=None):
        pred_ans = getattr(pred, "answer", "")
        correctness = (
            1.0 if pred_ans.strip().lower() == gold.answer.strip().lower() else 0.0
        )
        concise = 1.0 if 0 < len(pred_ans.split()) <= 20 else 0.5
        score = 0.8 * correctness + 0.2 * concise
        if correctness < 1.0:
            feedback = (
                f"Answer mismatch. Predicted: {pred_ans!r}. Expected: {gold.answer!r}. "
                f"Check reasoning for arithmetic/unit errors."
            )
        elif concise < 1.0:
            feedback = "Correct but verbose — tighten to under 20 words."
        else:
            feedback = "Correct and concise."
        return dspy.Prediction(score=score, feedback=feedback)

    return program, trainset, rich_metric


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model", default="openai/gpt-4o")
    args = ap.parse_args()

    import dspy

    program, trainset, rich_metric = build()

    if args.dry_run:
        fake_pred = dspy.Prediction(answer="4")
        out = rich_metric(trainset[0], fake_pred)
        # dspy.Prediction supports both attribute access and __getitem__.
        assert hasattr(out, "score") and hasattr(out, "feedback")
        print(
            f"OK metric returns score={out['score']:.2f} feedback={out['feedback']!r}"
        )
        return 0

    dspy.configure(lm=dspy.LM(args.model))
    evaluator = dspy.Evaluate(
        devset=trainset,
        metric=rich_metric,
        num_threads=4,
        display_progress=True,
        provide_traceback=True,
    )
    result = evaluator(program)
    print(f"Overall: {result.score:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
