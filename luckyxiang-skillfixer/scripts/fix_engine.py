"""Fix engine: maps evaluation suggestions to concrete fix actions."""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class FixCategory(Enum):
    AUTO = "AUTO"
    LLM_ASSISTED = "LLM_ASSISTED"
    STRUCTURAL = "STRUCTURAL"
    MANUAL = "MANUAL"


class FixTarget(Enum):
    FRONTMATTER = "frontmatter"
    FRONTMATTER_DESC = "frontmatter_description"
    BODY = "body"
    BODY_AND_REFS = "body_and_references"


@dataclass
class FixAction:
    dimension: str
    severity: str
    message: str
    category: FixCategory
    target: FixTarget
    handler: str  # handler function name
    description: str = ""  # human-readable fix description
    data: dict = field(default_factory=dict)  # extra data for the handler


# Dimension name mapping (CN → EN)
DIM_EN = {
    "元数据规范性": "frontmatter",
    "触发设计": "trigger_design",
    "内容结构": "content_structure",
    "用户体验": "user_experience",
    "安全性": "security",
    "Token 预算": "token_budget",
    "路由清晰度": "routing_clarity",
}


def _match(message: str, patterns: list[str]) -> bool:
    """Check if message contains any of the patterns."""
    for p in patterns:
        if p in message:
            return True
    return False


def map_suggestion_to_fix(suggestion: dict, skill_data: dict) -> FixAction | None:
    """Map a single suggestion to a FixAction.

    Args:
        suggestion: {dimension, severity, message} from howskill.
        skill_data: Parsed SKILL.md data from utils.parse_skill_md().

    Returns:
        FixAction or None if no fix is applicable.
    """
    dim = suggestion.get("dimension", "")
    sev = suggestion.get("severity", "INFO")
    msg = suggestion.get("message", "")
    dim_en = DIM_EN.get(dim, dim)

    # --- frontmatter ---
    if dim_en == "frontmatter":
        if "缺少 name 字段" in msg:
            dirname = skill_data.get("frontmatter", {}).get("path", "")
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.FRONTMATTER,
                             "add_name", "从目录名添加 name 字段")
        if "name 字段过短" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.FRONTMATTER,
                             "fix_short_name", "从目录名扩展 name")
        if "缺少 description 字段" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "generate_description", "LLM 从 body 生成 description")
        if "description 过短" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "expand_description", "LLM 扩展 description，添加 USE FOR")
        if "description 过长" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "compress_description", "LLM 压缩 description，保留触发短语")
        if "缺少 version 字段" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.FRONTMATTER,
                             "add_version", "添加 version: \"1.0\"")
        if "缺少 tags 字段" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER,
                             "add_tags", "LLM 从 description 提取标签")

    # --- trigger_design ---
    if dim_en == "trigger_design":
        if "缺少 USE FOR 触发模式" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "add_use_for", "LLM 生成 USE FOR 触发短语")
        if "缺少反触发模式" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "add_do_not_use_for", "LLM 生成 DO NOT USE FOR 反触发短语")
        if "反触发仅在 body 中" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.FRONTMATTER_DESC,
                             "move_anti_trigger_to_desc", "将 body 中的反触发短语移至 description")
        if "触发覆盖度有限" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "add_more_triggers", "LLM 补充更多触发短语")

    # --- content_structure ---
    if dim_en == "content_structure":
        if "skill body 为空" in msg:
            return FixAction(dim, sev, msg, FixCategory.MANUAL, FixTarget.BODY,
                             "manual_empty_body", "body 为空，需人工补充")
        if "缺少「概述」章节" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.BODY,
                             "add_section_overview", "添加 ## 概述 章节")
        if "缺少「用法" in msg or "缺少「快速参考」章节" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.BODY,
                             "add_section_usage", "添加 ## 用法 章节")
        if "缺少「示例」章节" in msg or "缺少「范例」章节" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.BODY,
                             "add_section_examples", "添加 ## 示例 章节")
        if "缺少「错误处理」章节" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.BODY,
                             "add_section_errors", "添加 ## 错误处理 章节")
        if "未找到代码/示例块" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.BODY,
                             "add_code_examples", "LLM 生成示例代码块")
        if "未找到表格" in msg:
            return FixAction(dim, sev, msg, FixCategory.STRUCTURAL, FixTarget.BODY,
                             "convert_list_to_table", "将相关列表转为表格")

    # --- user_experience ---
    if dim_en == "user_experience":
        if "用途说明不清晰" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "clarify_purpose", "重写 description 以 USE FOR 开头")
        if "description 过于简短" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "expand_description", "大幅扩展 description")
        if "description 信息量适中" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "expand_description", "LLM 扩展 description，补充上下文")
        if "缺少工作流指引" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.BODY,
                             "add_workflow_steps", "添加工作流步骤说明")
        if "缺少条件分支说明" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.BODY,
                             "add_conditional_logic", "添加条件分支说明")
        if "缺少使用示例" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.BODY,
                             "add_section_examples", "LLM 生成使用示例")
        if "示例有限" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.BODY,
                             "add_more_examples", "LLM 补充更多用例")
        if "缺少「不适用场景」说明" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "add_do_not_use_for", "添加 DO NOT USE FOR 到 description")
        if "「不适用场景」仅在 body 中" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.FRONTMATTER_DESC,
                             "move_anti_trigger_to_desc", "将 body 中的不适用场景移至 description")
        if "内容组织较弱" in msg:
            return FixAction(dim, sev, msg, FixCategory.STRUCTURAL, FixTarget.BODY,
                             "reorganize_body", "LLM 识别逻辑段落，添加标题")
        if "内容组织尚可" in msg:
            return FixAction(dim, sev, msg, FixCategory.AUTO, FixTarget.BODY,
                             "add_missing_sections", "补充缺失的标准章节")

    # --- security ---
    if dim_en == "security":
        if "发现潜在敏感信息" in msg:
            return FixAction(dim, sev, msg, FixCategory.STRUCTURAL, FixTarget.BODY,
                             "replace_sensitive_info", "用环境变量占位符替换敏感信息")
        if "发现注入风险模式" in msg:
            return FixAction(dim, sev, msg, FixCategory.STRUCTURAL, FixTarget.BODY,
                             "wrap_injection_pattern", "将注入模式包裹在代码块中")
        if "发现危险操作模式" in msg:
            return FixAction(dim, sev, msg, FixCategory.STRUCTURAL, FixTarget.BODY,
                             "add_safety_warning", "添加安全警告注释")
        if "硬编码绝对路径" in msg:
            return FixAction(dim, sev, msg, FixCategory.STRUCTURAL, FixTarget.BODY,
                             "replace_abs_paths", "替换绝对路径为相对路径")
        if "缺少使用边界声明" in msg:
            return FixAction(dim, sev, msg, FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                             "add_do_not_use_for", "添加 DO NOT USE FOR")

    # --- token_budget ---
    if dim_en == "token_budget":
        if "SKILL.md 过长" in msg or "预估 token 过高" in msg:
            return FixAction(dim, sev, msg, FixCategory.STRUCTURAL, FixTarget.BODY_AND_REFS,
                             "extract_to_references", "提取大段内容到 references/")
        if "body 占比过大" in msg:
            return FixAction(dim, sev, msg, FixCategory.STRUCTURAL, FixTarget.BODY_AND_REFS,
                             "extract_to_references", "提取详细内容到 references/")

    return None


def map_dynamic_results(eval_result: dict, skill_data: dict) -> list[FixAction]:
    """Map dynamic evaluation results to fix actions."""
    fixes = []
    aggregate = eval_result.get("aggregate", {})
    if not aggregate:
        return fixes

    metrics = aggregate.get("metrics", {})

    # Trigger accuracy issues
    trigger_acc = metrics.get("trigger_accuracy", {})
    if trigger_acc.get("value", 1.0) < 0.9:
        details = trigger_acc.get("details", {})
        tp = details.get("true_positives", 0)
        fp = details.get("false_positives", 0)
        fn = details.get("false_negatives", 0)

        if fn > 0:
            fixes.append(FixAction(
                "触发准确性", "WARN", f"触发召回率低（{fn} 个正 prompt 未触发）",
                FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                "fix_trigger_recall", "LLM 分析未触发的 prompt，补充 USE FOR 短语",
                data={"false_negatives": fn},
            ))
        if fp > 0:
            fixes.append(FixAction(
                "触发准确性", "WARN", f"触发精确率低（{fp} 个负 prompt 误触发）",
                FixCategory.LLM_ASSISTED, FixTarget.FRONTMATTER_DESC,
                "fix_trigger_precision", "LLM 分析误触发的 prompt，补充 DO NOT USE FOR 短语",
                data={"false_positives": fp},
            ))

    # Output quality issues
    output_q = metrics.get("output_quality", {})
    if output_q.get("value", 1.0) < 0.8:
        fixes.append(FixAction(
            "输出质量", "WARN", f"输出质量评分低（{output_q.get('value', 0):.2f}）",
            FixCategory.LLM_ASSISTED, FixTarget.BODY,
            "improve_output_quality", "LLM 分析低分任务的 grader feedback，改进 body 指令",
        ))

    # Content correctness issues
    content_c = metrics.get("content_correctness", {})
    if content_c.get("value", 1.0) < 0.7:
        fixes.append(FixAction(
            "内容正确性", "WARN", f"内容正确性评分低（{content_c.get('value', 0):.2f}）",
            FixCategory.LLM_ASSISTED, FixTarget.BODY,
            "improve_content_correctness", "LLM 分析失败的 text grader 规则，补充输出要求",
        ))

    return fixes


def generate_fix_plan(eval_result: dict, skill_data: dict) -> list[FixAction]:
    """Generate a complete fix plan from evaluation results.

    Returns fix actions sorted by priority: CRITICAL > WARN > INFO.
    """
    fixes = []

    # Map static suggestions
    static = eval_result.get("static_analysis", {})
    for suggestion in static.get("suggestions", []):
        fix = map_suggestion_to_fix(suggestion, skill_data)
        if fix:
            fixes.append(fix)

    # Also check INFO-level checks that weren't in suggestions
    for dim in static.get("dimensions", []):
        dim_name = dim.get("dimension", "")
        dim_cn = {
            "frontmatter": "元数据规范性",
            "trigger_design": "触发设计",
            "content_structure": "内容结构",
            "user_experience": "用户体验",
            "security": "安全性",
            "token_budget": "Token 预算",
        }.get(dim_name, dim_name)

        for text, deduction, severity in dim.get("checks", []):
            if severity == "INFO" and deduction > 0:
                # Check if already covered by a suggestion
                already = any(f.message == text for f in fixes)
                if not already:
                    fix = map_suggestion_to_fix(
                        {"dimension": dim_cn, "severity": "INFO", "message": text},
                        skill_data,
                    )
                    if fix:
                        fixes.append(fix)

    # Map dynamic results
    dynamic_fixes = map_dynamic_results(eval_result, skill_data)
    fixes.extend(dynamic_fixes)

    # Sort by priority
    sev_order = {"CRITICAL": 0, "WARN": 1, "INFO": 2}
    fixes.sort(key=lambda f: sev_order.get(f.severity, 3))

    # Deduplicate: same target, keep highest severity (MANUAL always kept)
    deduped = []
    seen_targets = {}  # target → (severity_order, index)
    for i, fix in enumerate(fixes):
        if fix.category == FixCategory.MANUAL:
            deduped.append(fix)
            continue
        key = (fix.target, fix.handler)
        if key not in seen_targets:
            seen_targets[key] = (sev_order.get(fix.severity, 3), i)
            deduped.append(fix)
        else:
            prev_sev, prev_idx = seen_targets[key]
            curr_sev = sev_order.get(fix.severity, 3)
            if curr_sev < prev_sev:
                # Replace previous with this higher-priority one
                deduped[prev_idx] = fix
                seen_targets[key] = (curr_sev, prev_idx)

    # Also deduplicate by target: same FixTarget with different handlers that
    # modify the same thing (e.g. expand_description + add_use_for both modify desc)
    # Keep only the most comprehensive one per target
    desc_handlers = {
        "generate_description", "expand_description", "compress_description",
        "add_use_for", "add_do_not_use_for", "add_more_triggers",
        "clarify_purpose", "fix_trigger_recall", "fix_trigger_precision",
    }
    desc_fixes = [f for f in deduped if f.handler in desc_handlers]
    other_fixes = [f for f in deduped if f.handler not in desc_handlers]

    if desc_fixes:
        # Keep only the highest-severity description fix — the grouped
        # execution will handle all desc needs in one LLM call
        best_desc = min(desc_fixes, key=lambda f: sev_order.get(f.severity, 3))
        deduped = other_fixes + [best_desc]

    return deduped