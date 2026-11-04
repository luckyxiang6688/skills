"""Re-evaluate a skill after fixes and compare with previous scores."""

import json
import subprocess
import sys
from pathlib import Path

HOWSKILL_DIR = Path.home() / ".claude" / "skills" / "luckyxiang-howskill"

# Dimension weights (must match howskill's static_analysis.py)
DIMENSION_WEIGHTS = {
    "frontmatter": 0.30,
    "trigger_design": 0.25,
    "content_structure": 0.20,  # was content_structure, mapped from 结构
    "user_experience": 0.20,
    "security": 0.10,
    "token_budget": 0.15,
}


def re_evaluate(skill_path: Path) -> dict:
    """Run static analysis on a skill via howskill subprocess.

    Delegates to howskill's run_full_eval() which auto-generates report files
    (both in skill's eval/ dir and D:/work/claude/howskill/).
    """
    script = (
        "import json, sys; from pathlib import Path; "
        "sys.path.insert(0, r'" + str(HOWSKILL_DIR) + "'); "
        "from scripts.run_eval import run_full_eval; "
        "result = run_full_eval(Path(r'" + str(skill_path) + "'), "
        "skip_dynamic=True, verbose=False); "
        "static = result['static_result']; "
        "static['report_files'] = {"
        "'skill_eval_json': static.get('report_files', {}).get('json', ''), "
        "'skill_eval_html': static.get('report_files', {}).get('html', ''), "
        "'howskill_json': result.get('json_path', ''), "
        "'howskill_html': result.get('html_path', '')}; "
        "print(json.dumps(static, ensure_ascii=False))"
    )
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", "-c", script],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        return {"dimensions": [], "overall_score": 0.0, "suggestions": []}
    return json.loads(proc.stdout.strip())


def compare_scores(old_result: dict, new_result: dict) -> dict:
    """Compare old and new evaluation results."""
    old_dims = {d["dimension"]: d["score"] for d in old_result.get("dimensions", [])}
    new_dims = {d["dimension"]: d["score"] for d in new_result.get("dimensions", [])}

    comparison = {
        "old_overall": old_result.get("overall_score", 0.0),
        "new_overall": new_result.get("overall_score", 0.0),
        "delta_overall": round(new_result.get("overall_score", 0.0) - old_result.get("overall_score", 0.0), 2),
        "dimensions": {},
    }

    DIM_CN = {
        "frontmatter": "元数据规范性",
        "trigger_design": "触发设计",
        "content_structure": "内容结构",
        "user_experience": "用户体验",
        "security": "安全性",
        "token_budget": "Token 预算",
    }

    all_dims = set(old_dims.keys()) | set(new_dims.keys())
    for dim in all_dims:
        old_score = old_dims.get(dim, 0.0)
        new_score = new_dims.get(dim, 0.0)
        delta = round(new_score - old_score, 2)
        comparison["dimensions"][dim] = {
            "name": DIM_CN.get(dim, dim),
            "old": old_score,
            "new": new_score,
            "delta": delta,
            "improved": delta > 0,
        }

    comparison["improved"] = comparison["delta_overall"] > 0
    comparison["unchanged"] = comparison["delta_overall"] == 0

    return comparison


def format_comparison(comparison: dict) -> str:
    """Format comparison results as a readable string."""
    lines = []
    lines.append(f"总分：{comparison['old_overall']:.2f} → {comparison['new_overall']:.2f} ({comparison['delta_overall']:+.2f})")
    lines.append("")

    for dim, data in comparison["dimensions"].items():
        arrow = "↑" if data["improved"] else ("↓" if data["delta"] < 0 else "→")
        lines.append(f"  {data['name']}: {data['old']:.2f} → {data['new']:.2f} ({data['delta']:+.2f}) {arrow}")

    if comparison["improved"]:
        lines.append("\n✅ 分数提升，修复有效")
    elif comparison["unchanged"]:
        lines.append("\n➡️ 分数未变化")
    else:
        lines.append("\n⚠️ 分数下降，建议回滚")

    return "\n".join(lines)
