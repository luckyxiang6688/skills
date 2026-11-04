#!/usr/bin/env python3
"""Main runner for skillfixer: loads eval results, generates fix plan, applies fixes."""

import argparse
import json
import sys
from pathlib import Path

from scripts.utils import (
    parse_skill_md,
    backup_skill_md,
    restore_skill_md,
    load_eval_result,
    find_latest_eval,
    compute_diff,
)
from scripts.fix_engine import generate_fix_plan, FixCategory
from scripts.apply_fixes import apply_fixes
from scripts.re_eval import re_evaluate, compare_scores, format_comparison

RESULTS_DIR = Path("D:/work/claude/howskill")


def run_fix(
    skill_path: str | Path,
    eval_json: str | None = None,
    dry_run: bool = False,
    auto_apply: bool = False,
    model: str | None = None,
    verbose: bool = False,
) -> dict:
    """Run the fix pipeline.

    Args:
        skill_path: Path to the skill directory.
        eval_json: Path to evaluation JSON (or None to auto-find).
        dry_run: Only show plan, don't apply.
        auto_apply: Auto-apply AUTO category fixes.
        model: Optional model override for LLM calls.
        verbose: Print progress.

    Returns:
        Summary dict.
    """
    skill_path = Path(skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    skill_data = parse_skill_md(skill_path)
    skill_name = skill_data["frontmatter"].get("name", skill_path.name)

    if verbose:
        print(f"\n=== 修复 skill: {skill_name} ===\n", file=sys.stderr)

    # Step 1: Load evaluation results
    if eval_json:
        eval_path = Path(eval_json)
    else:
        eval_path = find_latest_eval(skill_name, RESULTS_DIR)

    if not eval_path or not eval_path.exists():
        print(f"Error: 未找到 {skill_name} 的评估结果。请先运行 howskill 评估。", file=sys.stderr)
        sys.exit(1)

    eval_result = load_eval_result(eval_path)
    if verbose:
        print(f"读取评估结果: {eval_path}", file=sys.stderr)

    # Step 2: Generate fix plan
    fixes = generate_fix_plan(eval_result, skill_data)

    if not fixes:
        print("未发现可修复的问题。", file=sys.stderr)
        return {"skill": skill_name, "fixes": 0, "applied": 0}

    if verbose:
        print(f"\n修复计划 ({len(fixes)} 项):", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        for i, fix in enumerate(fixes, 1):
            cat = fix.category.value
            print(f"  {i}. [{fix.severity}] {fix.dimension}: {fix.message}", file=sys.stderr)
            print(f"     修复: {fix.description} ({cat})", file=sys.stderr)
        print("-" * 60, file=sys.stderr)

    if dry_run:
        print("\n[dry-run] 仅展示修复计划，未应用任何修改。", file=sys.stderr)
        return {
            "skill": skill_name,
            "fixes": len(fixes),
            "applied": 0,
            "dry_run": True,
        }

    # Step 3: Backup
    old_content = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    backup_path = backup_skill_md(skill_path)
    if verbose:
        print(f"\n备份: {backup_path}", file=sys.stderr)

    # Step 4: Apply fixes
    results = apply_fixes(fixes, skill_path, model=model, dry_run=dry_run, auto_apply=auto_apply)

    applied = sum(1 for r in results if r.get("applied"))
    skipped = sum(1 for r in results if not r.get("applied"))

    if verbose:
        print(f"\n应用结果: {applied} 成功, {skipped} 跳过", file=sys.stderr)
        for r in results:
            status = "✓" if r.get("applied") else "○"
            print(f"  {status} [{r.get('severity', '?')}] {r.get('description', '')}", file=sys.stderr)
            if r.get("diff_preview"):
                print(f"    {r['diff_preview']}", file=sys.stderr)

    # Step 5: Re-evaluate
    new_content = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    if new_content != old_content and verbose:
        print(f"\n--- Diff ---", file=sys.stderr)
        diff = compute_diff(old_content, new_content)
        for line in diff.split("\n"):
            if line.startswith("+") and not line.startswith("+++"):
                print(f"  {line}", file=sys.stderr)
            elif line.startswith("-") and not line.startswith("---"):
                print(f"  {line}", file=sys.stderr)
        print("--- End Diff ---\n", file=sys.stderr)

    old_static = eval_result.get("static_analysis", {})
    new_static = re_evaluate(skill_path)
    comparison = compare_scores(old_static, new_static)

    if verbose:
        print(f"\n重评估结果:", file=sys.stderr)
        print(format_comparison(comparison), file=sys.stderr)

    return {
        "skill": skill_name,
        "eval_path": str(eval_path),
        "fixes_planned": len(fixes),
        "fixes_applied": applied,
        "fixes_skipped": skipped,
        "old_score": comparison["old_overall"],
        "new_score": comparison["new_overall"],
        "delta": comparison["delta_overall"],
        "improved": comparison["improved"],
    }


def main():
    parser = argparse.ArgumentParser(description="Fix a Claude Code skill based on evaluation results")
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--eval", default=None, help="Path to evaluation JSON")
    parser.add_argument("--dry-run", action="store_true", help="Only show fix plan, don't apply")
    parser.add_argument("--yes", action="store_true", help="Auto-apply AUTO category fixes")
    parser.add_argument("--model", default=None, help="Model override for LLM calls")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print progress")
    args = parser.parse_args()

    result = run_fix(
        skill_path=args.skill_path,
        eval_json=args.eval,
        dry_run=args.dry_run,
        auto_apply=args.yes,
        model=args.model,
        verbose=args.verbose,
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
