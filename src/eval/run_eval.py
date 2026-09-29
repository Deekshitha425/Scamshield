"""
Runs the full pipeline against a labeled CSV and prints detection metrics
(precision/recall/F1/accuracy) plus explanation readability stats.

Usage:
    python -m src.eval.run_eval --input data/eval_sets/sample_eval_set.csv

CSV must have columns: text,label   (label is "scam" or "legitimate")
"needs_human_review" verdicts are reported separately, not scored as wrong,
since the system is explicitly designed to abstain rather than guess.
"""
from __future__ import annotations
import argparse
import csv
import sys
import time

from src.graph import analyze
from src.agents.schemas import Verdict

try:
    import textstat
    _HAS_TEXTSTAT = True
except ImportError:
    _HAS_TEXTSTAT = False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to labeled CSV (text,label)")
    parser.add_argument("--delay", type=float, default=2.5,
        help="Seconds to wait between cases, to stay under Groq's free-tier rate limit (default 2.5)")
    args = parser.parse_args()

    rows = []
    with open(args.input, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append((row["text"], row["label"].strip().lower()))

    if not rows:
        print("No rows found in input CSV.")
        sys.exit(1)

    tp = fp = tn = fn = abstained = 0
    latencies = []
    readability_scores = []

    for i, (text, true_label) in enumerate(rows, 1):
        if i > 1:
            time.sleep(args.delay)
        start = time.time()
        try:
            result = analyze(text)
        except Exception as e:
            print(f"[{i}/{len(rows)}] ERROR analyzing case: {e}")
            continue
        latencies.append(time.time() - start)

        pred = result.verdict.value  # "scam" | "legitimate" | "needs_human_review"
        print(f"[{i}/{len(rows)}] true={true_label:<12} pred={pred:<20} conf={result.confidence_score:.2f}")

        if pred == Verdict.NEEDS_HUMAN_REVIEW.value:
            abstained += 1
        elif pred == "scam" and true_label == "scam":
            tp += 1
        elif pred == "scam" and true_label == "legitimate":
            fp += 1
        elif pred == "legitimate" and true_label == "legitimate":
            tn += 1
        elif pred == "legitimate" and true_label == "scam":
            fn += 1

        if _HAS_TEXTSTAT and result.explanation:
            readability_scores.append(textstat.flesch_reading_ease(result.explanation))

    scored = tp + fp + tn + fn
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else float("nan")
    accuracy = (tp + tn) / scored if scored else float("nan")

    print("\n" + "=" * 50)
    print(f"Total cases:              {len(rows)}")
    print(f"Abstained (human review): {abstained}  ({abstained/len(rows):.1%})")
    print(f"Scored cases:             {scored}")
    print(f"  True Positives:  {tp}")
    print(f"  False Positives: {fp}")
    print(f"  True Negatives:  {tn}")
    print(f"  False Negatives: {fn}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall:    {recall:.3f}")
    print(f"F1 score:  {f1:.3f}")
    print(f"Accuracy (on scored cases only): {accuracy:.3f}")
    if latencies:
        print(f"Avg latency per case: {sum(latencies)/len(latencies):.2f}s")
    if readability_scores:
        avg_read = sum(readability_scores) / len(readability_scores)
        print(f"Avg explanation Flesch Reading Ease: {avg_read:.1f} (higher = easier to read)")
    print("=" * 50)
    print(
        "\nNote: this sample eval set has only 6 rows — good for a smoke test, "
        "NOT a number to put in a paper/PPT. Build a larger held-out test set "
        "per docs/evaluation_plan.md before reporting these as headline results."
    )


if __name__ == "__main__":
    main()