#!/usr/bin/env python3
"""Main evaluation orchestrator.

Runs the full two-layer evaluation pipeline:
  Phase 1: Static analysis (always)
  Phase 2: Dynamic evaluation (optional, requires user confirmation)

Outputs: HTML report + JSON results file.
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import yaml

from scripts.utils import parse_skill_md, load_eval_suite, find_project_root
from scripts.static_analysis import run_static_analysis
from scripts.run_trigger_eval import run_trigger_eval
from scripts.run_task import run_single_task
from scripts.aggregate import aggregate_task_results, add_trigger_metrics, score_to_label
from scripts.auto_generate import auto_generate_eval_suite
from scripts.report_html import generate_html_report, save_json_results


def run_full_eval(
    skill_path: str | Path,
    skip_dynamic: bool = False,
    timeout: int = 120,
    model: str | None = None,
    judge_model: str | None = None,
    verbose: bool = False,
) -> dict:
    """Run the complete evaluation pipeline.

    Args:
        skill_path: Path to the skill directory.
        skip_dynamic: Skip dynamic evaluation (static only).
        timeout: Timeout per claude -p call (seconds).
        model: Model for skill execution.
        judge_model: Model for LLM-as-Judge.
        verbose: Print progress.

    Returns:
        Complete evaluation result dict.
    """
    skill_path = Path(skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    skill = parse_skill_md(skill_path)
    skill_name = skill["name"] or skill_path.name

    if verbose:
        print(f"\n=== Evaluating skill: {skill_name} ===\n", file=sys.stderr)

    # --- Phase 1: Static Analysis ---
    if verbose:
        print("Phase 1: Static Analysis...", file=sys.stderr)

    static_result = run_static_analysis(skill_path)

    if verbose:
        print(f"  Static score: {static_result['overall_score']:.2f}", file=sys.stderr)
        for dim in static_result["dimensions"]:
            print(f"    {dim['dimension']}: {dim['score']:.2f}", file=sys.stderr)

    # --- Phase 2: Dynamic Evaluation ---
    dynamic_result = None
    aggregate_result = None
    auto_generated_eval_dir = None

    if not skip_dynamic:
        # Look for existing eval suite
        eval_dir = skill_path / "evals"
        eval_file = eval_dir / "eval.yaml"

        if not eval_file.exists():
            # Try alternate location
            alt_eval = skill_path / "eval.yaml"
            if alt_eval.exists():
                eval_file = alt_eval
                eval_dir = skill_path
            else:
                if verbose:
                    print("  No eval suite found. Auto-generating...", file=sys.stderr)
                eval_file = auto_generate_eval_suite(skill_path)
                eval_dir = eval_file.parent
                auto_generated_eval_dir = eval_dir
                if verbose:
                    print(f"  Generated at: {eval_dir}", file=sys.stderr)

        eval_spec = load_eval_suite(eval_file)
        config = eval_spec.get("config", {})
        effective_timeout = config.get("timeout_seconds", timeout)
        effective_model = model or config.get("model")
        effective_judge = judge_model or config.get("judge_model")

        # Run trigger tests
        trigger_tests = eval_spec.get("trigger_tests")
        trigger_result = None

        if trigger_tests:
            if verbose:
                print("  Running trigger evaluation...", file=sys.stderr)
            trigger_result = run_trigger_eval(
                trigger_tests=trigger_tests,
                skill_path=skill_path,
                timeout=30,
                model=effective_model,
                verbose=verbose,
            )

        # Run task evaluation
        tasks = eval_spec.get("tasks", [])
        global_graders = eval_spec.get("graders", [])
        task_results = []

        if tasks:
            if verbose:
                print(f"  Running {len(tasks)} task(s)...", file=sys.stderr)
            for task in tasks:
                tr = run_single_task(
                    task=task,
                    eval_dir=eval_dir,
                    timeout=effective_timeout,
                    model=effective_model,
                    judge_model=effective_judge,
                    global_graders=global_graders,
                    verbose=verbose,
                )
                task_results.append(tr)

        # Aggregate
        metrics = eval_spec.get("metrics", [])
        aggregate_result = aggregate_task_results(task_results, metrics)
        if trigger_result:
            aggregate_result = add_trigger_metrics(aggregate_result, trigger_result, metrics)

        dynamic_result = {
            "trigger_result": trigger_result,
            "task_results": task_results,
        }

        if verbose:
            print(f"  Dynamic score: {aggregate_result['overall_score']:.2f}", file=sys.stderr)

    # --- Generate Reports ---
    # 固定输出目录：D:\work\claude\howskill
    results_dir = Path("D:/work/claude/howskill")
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    html_path = results_dir / f"{skill_name}_eval_{timestamp}.html"
    json_path = results_dir / f"{skill_name}_eval_{timestamp}.json"

    generate_html_report(
        skill_name=skill_name,
        static_result=static_result,
        dynamic_result=dynamic_result,
        aggregate_result=aggregate_result,
        output_path=html_path,
    )

    save_json_results(
        skill_name=skill_name,
        static_result=static_result,
        dynamic_result=dynamic_result,
        aggregate_result=aggregate_result,
        output_path=json_path,
    )

    if verbose:
        print(f"\n=== Report saved ===", file=sys.stderr)
        print(f"  HTML: {html_path}", file=sys.stderr)
        print(f"  JSON: {json_path}", file=sys.stderr)

    # --- Cleanup auto-generated evals ---
    if auto_generated_eval_dir and auto_generated_eval_dir.exists():
        shutil.rmtree(auto_generated_eval_dir)
        if verbose:
            print(f"  Cleaned up auto-generated evals: {auto_generated_eval_dir}", file=sys.stderr)

    return {
        "skill_name": skill_name,
        "static_result": static_result,
        "dynamic_result": dynamic_result,
        "aggregate_result": aggregate_result,
        "html_path": str(html_path),
        "json_path": str(json_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate a Claude Code skill")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--static-only", action="store_true", help="Run static analysis only")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout per task (seconds)")
    parser.add_argument("--model", default=None, help="Model for skill execution")
    parser.add_argument("--judge-model", default=None, help="Model for LLM-as-Judge")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print progress")
    args = parser.parse_args()

    result = run_full_eval(
        skill_path=args.skill_path,
        skip_dynamic=args.static_only,
        timeout=args.timeout,
        model=args.model,
        judge_model=args.judge_model,
        verbose=args.verbose,
    )

    # Print summary to stdout
    summary = {
        "skill": result["skill_name"],
        "static_score": result["static_result"]["overall_score"],
        "html_report": result["html_path"],
        "json_results": result["json_path"],
    }
    if result["aggregate_result"]:
        summary["dynamic_score"] = result["aggregate_result"]["overall_score"]

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()