"""Trigger evaluation executor.

Runs positive and negative trigger test prompts via claude -p,
detects whether the skill was invoked, and computes
precision / recall / F1 / accuracy.
"""

import argparse
import json
import sys
from pathlib import Path

from scripts.utils import parse_skill_md, run_trigger_check, find_project_root


def run_trigger_eval(
    trigger_tests: dict,
    skill_path: Path,
    timeout: int = 30,
    model: str | None = None,
    verbose: bool = False,
) -> dict:
    """Run trigger evaluation and return structured results.

    Args:
        trigger_tests: Dict from trigger_tests.yaml with should_trigger_prompts
                       and should_not_trigger_prompts.
        skill_path: Path to the skill directory.
        timeout: Seconds per claude -p call.
        model: Optional model override.
        verbose: Print progress to stderr.

    Returns:
        Dict with trigger_metrics and per-prompt results.
    """
    skill = parse_skill_md(skill_path)
    project_root = find_project_root()

    results = []

    # Positive tests (should trigger)
    for item in trigger_tests.get("should_trigger_prompts", []):
        prompt = item["prompt"]
        if verbose:
            print(f"  [POS] {prompt[:60]}...", file=sys.stderr)

        triggered = run_trigger_check(
            query=prompt,
            skill_name=skill["name"],
            skill_description=skill["description"],
            timeout=timeout,
            project_root=project_root,
            model=model,
        )

        results.append({
            "prompt": prompt,
            "expected": True,
            "actual": triggered,
            "correct": triggered is True,
            "reason": item.get("reason", ""),
            "confidence": item.get("confidence", "medium"),
        })

    # Negative tests (should NOT trigger)
    for item in trigger_tests.get("should_not_trigger_prompts", []):
        prompt = item["prompt"]
        if verbose:
            print(f"  [NEG] {prompt[:60]}...", file=sys.stderr)

        triggered = run_trigger_check(
            query=prompt,
            skill_name=skill["name"],
            skill_description=skill["description"],
            timeout=timeout,
            project_root=project_root,
            model=model,
        )

        results.append({
            "prompt": prompt,
            "expected": False,
            "actual": triggered,
            "correct": triggered is False,
            "reason": item.get("reason", ""),
            "confidence": item.get("confidence", "medium"),
        })

    # Compute metrics
    tp = sum(1 for r in results if r["expected"] is True and r["actual"] is True)
    fp = sum(1 for r in results if r["expected"] is False and r["actual"] is True)
    fn = sum(1 for r in results if r["expected"] is True and r["actual"] is False)
    tn = sum(1 for r in results if r["expected"] is False and r["actual"] is False)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(results) if results else 0.0

    return {
        "trigger_metrics": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1": round(f1, 2),
            "accuracy": round(accuracy, 2),
        },
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--trigger-tests", required=True, help="Path to trigger_tests.yaml")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query (seconds)")
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    trigger_tests = yaml.safe_load(Path(args.trigger_tests).read_text())
    skill_path = Path(args.skill_path)

    output = run_trigger_eval(
        trigger_tests=trigger_tests,
        skill_path=skill_path,
        timeout=args.timeout,
        model=args.model,
        verbose=args.verbose,
    )

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import yaml
    main()