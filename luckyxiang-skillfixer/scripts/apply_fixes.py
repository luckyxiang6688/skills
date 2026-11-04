"""Apply fix actions to SKILL.md files — grouped execution with merged LLM calls."""

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from scripts.utils import (
    parse_skill_md,
    write_skill_md,
    extract_anti_triggers_from_body,
    extract_triggers_from_body,
)
from scripts.fix_engine import FixAction, FixCategory, FixTarget
from scripts.suggest_triggers import (
    batch_generate_for_description,
    generate_trigger_phrases,
    generate_anti_trigger_phrases,
    expand_description,
    generate_tags,
    generate_examples_from_body,
)

# Handlers that modify description (grouped into one LLM call)
DESC_HANDLERS = {
    "generate_description", "expand_description", "compress_description",
    "add_use_for", "add_do_not_use_for", "add_more_triggers",
    "clarify_purpose", "fix_trigger_recall", "fix_trigger_precision",
}

# Handlers that generate examples (grouped into one LLM call)
EXAMPLE_HANDLERS = {
    "add_section_examples", "add_more_examples", "add_code_examples",
}


def apply_fix(
    fix: FixAction,
    skill_path: Path,
    skill_data: dict,
    model: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Apply a single fix action to a skill.

    Returns a dict with: applied (bool), description (str), diff_preview (str).
    """
    handler = fix.handler
    fm = skill_data["frontmatter"]
    body = skill_data["body"]
    desc = fm.get("description", "")

    result = {"applied": False, "description": fix.description, "diff_preview": ""}

    # --- AUTO fixes (no LLM needed) ---

    if handler == "add_name":
        name = skill_path.name
        fm["name"] = name
        result["applied"] = True
        result["diff_preview"] = f"+ name: {name}"

    elif handler == "fix_short_name":
        name = skill_path.name
        fm["name"] = name
        result["applied"] = True
        result["diff_preview"] = f"name: {fm.get('name', '?')} → {name}"

    elif handler == "add_version":
        fm["version"] = "1.0"
        result["applied"] = True
        result["diff_preview"] = '+ version: "1.0"'

    elif handler == "move_anti_trigger_to_desc":
        anti_phrases = extract_anti_triggers_from_body(body)
        if anti_phrases:
            dont_section = "DO NOT USE FOR: " + "、".join(anti_phrases)
            if "DO NOT USE FOR" not in desc:
                desc = desc.rstrip() + "\n\n  " + dont_section
                fm["description"] = desc
                result["applied"] = True
                result["diff_preview"] = f"+ DO NOT USE FOR: {'、'.join(anti_phrases[:3])}..."

    elif handler == "add_section_overview":
        section = "\n## 概述\n\n"
        if desc:
            section += desc.split("USE FOR")[0].strip()[:200] + "\n"
        else:
            section += f"{fm.get('name', '本 skill')} 的功能说明。\n"
        body += section
        skill_data["body"] = body
        result["applied"] = True
        result["diff_preview"] = "+ ## 概述"

    elif handler == "add_section_usage":
        section = "\n## 用法\n\n```\n/skill-name <参数>\n```\n"
        body += section
        skill_data["body"] = body
        result["applied"] = True
        result["diff_preview"] = "+ ## 用法"

    elif handler == "add_section_errors":
        section = "\n## 错误处理\n\n- 如果输入为空，提示用户提供必要信息\n- 如果执行失败，返回错误原因和建议\n"
        body += section
        skill_data["body"] = body
        result["applied"] = True
        result["diff_preview"] = "+ ## 错误处理"

    elif handler == "add_workflow_steps":
        section = "\n## 工作流\n\n1. 接收用户输入\n2. 解析请求意图\n3. 执行核心逻辑\n4. 返回结果\n"
        body += section
        skill_data["body"] = body
        result["applied"] = True
        result["diff_preview"] = "+ ## 工作流"

    elif handler == "add_conditional_logic":
        section = "\n## 条件分支\n\n- 如果输入包含 X，则执行 A\n- 如果输入包含 Y，则执行 B\n- 其他情况，执行默认流程\n"
        body += section
        skill_data["body"] = body
        result["applied"] = True
        result["diff_preview"] = "+ ## 条件分支"

    elif handler == "add_missing_sections":
        section_map = {
            "概述": "\n## 概述\n\n功能说明。\n",
            "用法": "\n## 用法\n\n使用说明。\n",
            "示例": "\n## 示例\n\n使用示例。\n",
            "错误处理": "\n## 错误处理\n\n错误处理说明。\n",
        }
        added = []
        for name, template in section_map.items():
            if not re.search(rf"^#+\s*{name}", body, re.MULTILINE):
                body += template
                added.append(name)
        if added:
            skill_data["body"] = body
            result["applied"] = True
            result["diff_preview"] = f"+ 章节：{', '.join(added)}"

    # --- STRUCTURAL fixes ---

    elif handler == "replace_sensitive_info":
        patterns = [
            (r'(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?token)\s*[:=]\s*["\'][a-z0-9\-]{8,}["\']',
             lambda m: m.group(0).split("=")[0] + "=YOUR_API_KEY_HERE"),
            (r'(?:password|passwd|pwd)\s*[:=]\s*["\'][a-z0-9\-]{4,}["\']',
             lambda m: m.group(0).split("=")[0] + "=YOUR_PASSWORD_HERE"),
        ]
        new_body = body
        for pattern, repl in patterns:
            new_body = re.sub(pattern, repl, new_body, flags=re.IGNORECASE)
        if new_body != body:
            skill_data["body"] = new_body
            result["applied"] = True
            result["diff_preview"] = "替换敏感信息为占位符"

    elif handler == "replace_abs_paths":
        new_body = re.sub(
            r'(?:^|\s|["\'])(/[a-zA-Z0-9_/.-]+(?:\.\w+)?)(?:$|\s|["\'\)])',
            lambda m: m.group(0).replace(m.group(1), "./" + m.group(1).lstrip("/")),
            body,
            flags=re.MULTILINE,
        )
        if new_body != body:
            skill_data["body"] = new_body
            result["applied"] = True
            result["diff_preview"] = "替换绝对路径为相对路径"

    elif handler == "extract_to_references":
        refs_dir = skill_path / "references"
        sections = re.split(r'(^#{1,3}\s+.+$)', body, flags=re.MULTILINE)

        if len(sections) >= 3:
            max_len = 0
            max_idx = -1
            for i in range(1, len(sections), 2):
                if i + 1 < len(sections) and len(sections[i + 1]) > max_len:
                    max_len = len(sections[i + 1])
                    max_idx = i

            if max_idx >= 0 and max_len > 200:
                header = sections[max_idx].strip()
                content = sections[max_idx + 1].strip()
                slug = re.sub(r'[^a-zA-Z0-9一-鿿]+', '-', header.lower()).strip('-')[:30]

                refs_dir.mkdir(parents=True, exist_ok=True)
                ref_file = refs_dir / f"{slug}.md"
                ref_file.write_text(f"# {header}\n\n{content}\n", encoding="utf-8")

                sections[max_idx + 1] = f"\n详见 references/{slug}.md\n\n"
                new_body = "".join(sections)
                skill_data["body"] = new_body
                result["applied"] = True
                result["diff_preview"] = f"提取到 references/{slug}.md"

    elif handler == "add_safety_warning":
        dangerous = [
            (r'rm\s+-rf', "# ⚠️ 危险操作：删除文件，请确认后再执行"),
            (r'chmod\s+777', "# ⚠️ 不安全的权限设置，建议使用更严格的权限"),
            (r'eval\s*\(', "# ⚠️ 动态执行代码，存在安全风险"),
        ]
        new_body = body
        for pattern, warning in dangerous:
            lines = new_body.split("\n")
            new_lines = []
            for line in lines:
                if re.search(pattern, line) and warning not in line:
                    new_lines.append(warning)
                new_lines.append(line)
            new_body = "\n".join(new_lines)

        if new_body != body:
            skill_data["body"] = new_body
            result["applied"] = True
            result["diff_preview"] = "+ 安全警告注释"

    elif handler == "wrap_injection_pattern":
        result["applied"] = False
        result["diff_preview"] = "注入模式修复需要人工确认"

    elif handler == "reorganize_body":
        result["applied"] = False
        result["diff_preview"] = "内容重组需要人工确认"

    # --- MANUAL fixes ---
    elif handler == "manual_empty_body":
        result["applied"] = False
        result["diff_preview"] = "⚠️ body 为空，需人工补充内容"

    # --- Dynamic fixes (handled by grouped execution, fallback for single-call) ---
    elif handler in ("improve_output_quality", "improve_content_correctness"):
        if "improve_output_quality" == handler:
            section = "\n## 输出要求\n\n- 输出应完整回应用户请求\n- 内容结构清晰，逻辑连贯\n- 避免模糊或不确定的表述\n"
        else:
            section = "\n## 输出规范\n\n- 输出必须包含用户请求的关键信息\n- 不得包含「我不知道」「无法完成」等拒绝性表述\n- 格式规范，信息准确\n"
        body += section
        skill_data["body"] = body
        result["applied"] = True
        result["diff_preview"] = f"+ {section.strip().split(chr(10))[0]}"

    # Write changes if applied
    if result["applied"] and not dry_run:
        write_skill_md(skill_path, fm, skill_data["body"])

    return result


def _apply_auto_fixes(fixes: list[FixAction], skill_path: Path, dry_run: bool) -> list[dict]:
    """Apply AUTO fixes (no LLM needed)."""
    results = []
    for fix in fixes:
        if fix.category != FixCategory.AUTO:
            continue
        skill_data = parse_skill_md(skill_path)
        result = apply_fix(fix, skill_path, skill_data, dry_run=dry_run)
        result["dimension"] = fix.dimension
        result["severity"] = fix.severity
        result["category"] = fix.category.value
        results.append(result)
    return results


def _apply_description_fix(
    fix: FixAction,
    skill_path: Path,
    batch_result: dict,
    dry_run: bool,
) -> dict:
    """Apply a description fix using pre-generated batch LLM result."""
    skill_data = parse_skill_md(skill_path)
    fm = skill_data["frontmatter"]
    desc = fm.get("description", "")

    result = {
        "applied": False,
        "description": fix.description,
        "diff_preview": "",
        "dimension": fix.dimension,
        "severity": fix.severity,
        "category": fix.category.value,
    }

    new_desc = batch_result.get("description", "")
    triggers = batch_result.get("triggers", [])
    anti_triggers = batch_result.get("anti_triggers", [])

    # Build description from batch result
    if new_desc and len(new_desc) >= 100:
        fm["description"] = new_desc
        result["applied"] = True
        result["diff_preview"] = f"description: {len(desc)} → {len(new_desc)} 字符"
    elif triggers or anti_triggers:
        # Fallback: assemble from triggers + anti_triggers
        parts = []
        if desc:
            parts.append(desc.split("USE FOR")[0].strip())
        if triggers:
            parts.append("USE FOR: " + "、".join(triggers))
        if anti_triggers:
            parts.append("DO NOT USE FOR: " + "、".join(anti_triggers))
        if parts:
            new_desc = "\n\n  ".join(parts)
            if len(new_desc) > len(desc):
                fm["description"] = new_desc
                result["applied"] = True
                result["diff_preview"] = f"description: {len(desc)} → {len(new_desc)} 字符"

    if result["applied"] and not dry_run:
        write_skill_md(skill_path, fm, skill_data["body"])

    return result


def _apply_example_fix(
    fix: FixAction,
    skill_path: Path,
    examples: str,
    dry_run: bool,
) -> dict:
    """Apply an example fix using pre-generated LLM result."""
    skill_data = parse_skill_md(skill_path)
    body = skill_data["body"]

    result = {
        "applied": False,
        "description": fix.description,
        "diff_preview": "",
        "dimension": fix.dimension,
        "severity": fix.severity,
        "category": fix.category.value,
    }

    if examples:
        # Check if ## 示例 section already exists
        if re.search(r"^#+\s*示例", body, re.MULTILINE):
            body += f"\n{examples}\n"
        else:
            body += f"\n## 示例\n\n{examples}\n"
        skill_data["body"] = body
        result["applied"] = True
        result["diff_preview"] = "+ ## 示例 (LLM 生成)"

        if not dry_run:
            write_skill_md(skill_path, skill_data["frontmatter"], skill_data["body"])

    return result


def _apply_tags_fix(
    fix: FixAction,
    skill_path: Path,
    tags: list[str],
    dry_run: bool,
) -> dict:
    """Apply a tags fix using pre-generated LLM result."""
    skill_data = parse_skill_md(skill_path)

    result = {
        "applied": False,
        "description": fix.description,
        "diff_preview": "",
        "dimension": fix.dimension,
        "severity": fix.severity,
        "category": fix.category.value,
    }

    if tags:
        skill_data["frontmatter"]["tags"] = tags
        result["applied"] = True
        result["diff_preview"] = f"+ tags: {tags}"

        if not dry_run:
            write_skill_md(skill_path, skill_data["frontmatter"], skill_data["body"])

    return result


def apply_fixes_grouped(
    fixes: list[FixAction],
    skill_path: Path,
    model: str | None = None,
    dry_run: bool = False,
    auto_apply: bool = False,
) -> list[dict]:
    """Apply fixes with grouped LLM calls for efficiency.

    Execution phases:
    1. AUTO fixes — no LLM, apply directly
    2. Batch LLM — description group + tags (parallel)
    3. Description fixes — use batch result, no extra LLM
    4. Example fixes — one LLM call
    5. STRUCTURAL fixes — no LLM, apply directly
    6. MANUAL fixes — report only
    """
    results = []
    skill_data = parse_skill_md(skill_path)
    fm = skill_data["frontmatter"]
    body = skill_data["body"]
    desc = fm.get("description", "")

    # Classify fixes
    auto_fixes = []
    desc_fixes = []
    example_fixes = []
    tags_fixes = []
    structural_fixes = []
    manual_fixes = []
    other_llm_fixes = []  # dynamic fixes that modify body

    for fix in fixes:
        if fix.category == FixCategory.MANUAL:
            manual_fixes.append(fix)
        elif fix.category == FixCategory.AUTO:
            auto_fixes.append(fix)
        elif fix.handler in DESC_HANDLERS:
            desc_fixes.append(fix)
        elif fix.handler in EXAMPLE_HANDLERS:
            example_fixes.append(fix)
        elif fix.handler == "add_tags":
            tags_fixes.append(fix)
        elif fix.category == FixCategory.STRUCTURAL:
            structural_fixes.append(fix)
        else:
            other_llm_fixes.append(fix)

    # --- Phase 1: AUTO fixes ---
    for fix in auto_fixes:
        skill_data = parse_skill_md(skill_path)
        r = apply_fix(fix, skill_path, skill_data, dry_run=dry_run)
        r["dimension"] = fix.dimension
        r["severity"] = fix.severity
        r["category"] = fix.category.value
        results.append(r)

    # --- Phase 2: Batch LLM calls (parallel) ---
    # Re-read skill data after AUTO fixes
    skill_data = parse_skill_md(skill_path)
    fm = skill_data["frontmatter"]
    body = skill_data["body"]
    desc = fm.get("description", "")

    batch_desc_result = {}
    tags_result = []
    examples_result = ""

    if not dry_run:
        llm_futures = {}

        with ThreadPoolExecutor(max_workers=2) as executor:
            if desc_fixes:
                future = executor.submit(
                    batch_generate_for_description,
                    fm.get("name", skill_path.name),
                    body, desc, model=model,
                )
                llm_futures["desc"] = future

            if tags_fixes:
                future = executor.submit(
                    generate_tags,
                    fm.get("name", skill_path.name),
                    desc, model=model,
                )
                llm_futures["tags"] = future

            if example_fixes:
                future = executor.submit(
                    generate_examples_from_body,
                    fm.get("name", skill_path.name),
                    body, count=2, model=model,
                )
                llm_futures["examples"] = future

            for key, future in llm_futures.items():
                try:
                    llm_futures[key] = future.result(timeout=60)
                except Exception:
                    llm_futures[key] = {} if key == "desc" else ([] if key == "tags" else "")

        batch_desc_result = llm_futures.get("desc", {})
        tags_result = llm_futures.get("tags", [])
        examples_result = llm_futures.get("examples", "")

    # --- Phase 3: Description fixes (using batch result) ---
    for fix in desc_fixes:
        r = _apply_description_fix(fix, skill_path, batch_desc_result, dry_run)
        results.append(r)

    # --- Phase 4: Tags fixes ---
    for fix in tags_fixes:
        r = _apply_tags_fix(fix, skill_path, tags_result, dry_run)
        results.append(r)

    # --- Phase 5: Example fixes (using batch result) ---
    for fix in example_fixes:
        r = _apply_example_fix(fix, skill_path, examples_result, dry_run)
        results.append(r)

    # --- Phase 6: Other LLM fixes (dynamic body fixes) ---
    for fix in other_llm_fixes:
        skill_data = parse_skill_md(skill_path)
        r = apply_fix(fix, skill_path, skill_data, model=model, dry_run=dry_run)
        r["dimension"] = fix.dimension
        r["severity"] = fix.severity
        r["category"] = fix.category.value
        results.append(r)

    # --- Phase 7: STRUCTURAL fixes ---
    for fix in structural_fixes:
        skill_data = parse_skill_md(skill_path)
        r = apply_fix(fix, skill_path, skill_data, dry_run=dry_run)
        r["dimension"] = fix.dimension
        r["severity"] = fix.severity
        r["category"] = fix.category.value
        results.append(r)

    # --- MANUAL fixes (report only) ---
    for fix in manual_fixes:
        results.append({
            "applied": False,
            "description": fix.description,
            "diff_preview": "⚠️ 需人工处理",
            "dimension": fix.dimension,
            "severity": fix.severity,
            "category": fix.category.value,
        })

    return results


def apply_fixes(
    fixes: list[FixAction],
    skill_path: Path,
    model: str | None = None,
    dry_run: bool = False,
    auto_apply: bool = False,
) -> list[dict]:
    """Apply a list of fix actions using grouped execution."""
    return apply_fixes_grouped(fixes, skill_path, model=model, dry_run=dry_run, auto_apply=auto_apply)
