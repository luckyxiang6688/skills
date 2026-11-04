"""Score aggregation and metric calculation."""

from typing import Any


def aggregate_task_results(task_results: list[dict], metrics: list[dict]) -> dict:
    """Aggregate task-level results into metric-level scores.

    Args:
        task_results: List of task result dicts (each has score, grader_results).
        metrics: List of metric definitions (name, weight, threshold).

    Returns:
        Dict with per-metric scores, overall score, pass/fail status.
    """
    if not task_results:
        return {
            "metrics": {},
            "overall_score": 0.0,
            "overall_passed": False,
            "success_rate": 0.0,
        }

    # Basic aggregation: average task scores
    completed = [t for t in task_results if t["status"] == "completed"]
    success_rate = len(completed) / len(task_results) if task_results else 0.0

    # For each metric, compute score based on matching grader results
    metric_scores = {}
    for metric_def in metrics:
        mname = metric_def["name"]
        mweight = metric_def.get("weight", 1.0)
        mthreshold = metric_def.get("threshold", 0.7)

        if mname == "trigger_accuracy":
            # Will be filled separately
            continue

        # Match metric to grader results by name similarity
        matching_scores = []
        for task in completed:
            for gr in task.get("grader_results", []):
                gr_name = gr.get("name", "").lower()
                mname_lower = mname.lower()
                # Match by name overlap
                if any(word in gr_name for word in mname_lower.split("_")):
                    matching_scores.append(gr["score"])

        if matching_scores:
            metric_scores[mname] = {
                "value": round(sum(matching_scores) / len(matching_scores), 2),
                "threshold": mthreshold,
                "weight": mweight,
                "passed": (sum(matching_scores) / len(matching_scores)) >= mthreshold,
            }
        else:
            # No matching graders found — use task average score
            task_avg = sum(t["score"] for t in completed) / len(completed) if completed else 0.0
            metric_scores[mname] = {
                "value": round(task_avg, 2),
                "threshold": mthreshold,
                "weight": mweight,
                "passed": task_avg >= mthreshold,
            }

    # Compute overall weighted score
    total_weight = sum(m.get("weight", 1.0) for m in metrics if m["name"] != "trigger_accuracy")
    weighted_sum = sum(
        metric_scores[m["name"]]["value"] * m.get("weight", 1.0)
        for m in metrics
        if m["name"] != "trigger_accuracy" and m["name"] in metric_scores
    )
    overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    return {
        "metrics": metric_scores,
        "overall_score": round(overall_score, 2),
        "overall_passed": overall_score >= 0.7,
        "success_rate": round(success_rate, 2),
        "total_tasks": len(task_results),
        "completed_tasks": len(completed),
        "failed_tasks": len(task_results) - len(completed),
    }


def add_trigger_metrics(aggregate_result: dict, trigger_result: dict | None, metrics: list[dict]) -> dict:
    """Add trigger metrics to the aggregate result.

    Args:
        aggregate_result: Result from aggregate_task_results.
        trigger_result: Result from run_trigger_eval (or None).
        metrics: Metric definitions.

    Returns:
        Updated aggregate_result with trigger_accuracy metric.
    """
    if not trigger_result:
        return aggregate_result

    tm = trigger_result["trigger_metrics"]

    # Find trigger_accuracy metric definition
    trigger_metric_def = None
    for m in metrics:
        if m["name"] == "trigger_accuracy":
            trigger_metric_def = m
            break

    if trigger_metric_def:
        aggregate_result["metrics"]["trigger_accuracy"] = {
            "value": tm["f1"],
            "threshold": trigger_metric_def.get("threshold", 0.9),
            "weight": trigger_metric_def.get("weight", 0.3),
            "passed": tm["f1"] >= trigger_metric_def.get("threshold", 0.9),
            "details": tm,
        }

        # Recompute overall score including trigger
        total_weight = sum(m.get("weight", 1.0) for m in metrics)
        weighted_sum = sum(
            aggregate_result["metrics"][m["name"]]["value"] * m.get("weight", 1.0)
            for m in metrics
            if m["name"] in aggregate_result["metrics"]
        )
        aggregate_result["overall_score"] = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0
        aggregate_result["overall_passed"] = aggregate_result["overall_score"] >= 0.7

    aggregate_result["trigger_metrics"] = tm
    aggregate_result["trigger_results"] = trigger_result["results"]

    return aggregate_result


def score_to_label(score: float) -> str:
    """Convert a 0-1 score to a human-readable label (Chinese)."""
    if score >= 0.9:
        return "优秀"
    elif score >= 0.7:
        return "良好"
    elif score >= 0.5:
        return "需改进"
    elif score >= 0.3:
        return "较差"
    else:
        return "不合格"


def status_to_emoji(status: str) -> str:
    """Convert status to emoji indicator."""
    mapping = {
        "PASS": "&#x2705;",
        "PASS": "&#x2705;",
        "WARN": "&#x26A0;&#xFE0F;",
        "CRITICAL": "&#x274C;",
        "INFO": "&#x2139;&#xFE0F;",
        "FAIL": "&#x274C;",
    }
    return mapping.get(status, "&#x2753;")
