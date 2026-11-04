"""Static analysis of a SKILL.md file.

Evaluates 5 dimensions:
1. 内容结构 (Content structure + Frontmatter)
2. 触发设计 (Trigger design)
3. 用户体验 (User experience)
4. 安全性 (Security)
5. Token 预算 (Token budget)

Returns a scored report with specific improvement suggestions (in Chinese).
"""

import json
import re
from pathlib import Path

from scripts.utils import parse_skill_md, estimate_tokens


EXPECTED_SECTIONS = [
    (r"^#+\s*(overview|概述|简介)", "概述"),
    (r"^#+\s*(usage|用法|使用|quick\s*reference)", "用法/快速参考"),
    (r"^#+\s*(example|示例|范例)", "示例"),
    (r"^#+\s*(error|错误|异常|troubleshoot)", "错误处理"),
]

ROUTING_MARKERS = [
    r"INVOKES:",
    r"FOR\s+SINGLE\s+OPERATIONS?:",
    r"WORKFLOW\s+SKILL",
    r"UTILITY\s+SKILL",
]

# Sensitive patterns for security checks
SENSITIVE_PATTERNS = [
    (r'(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*["\'][a-z0-9\-]{8,}["\']', "硬编码密钥/Token"),
    (r'(?:password|passwd|pwd)\s*[:=]\s*["\'][a-z0-9\-]{4,}["\']', "硬编码密码"),
    (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API Key 格式"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Token 格式"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key 格式"),
    (r'https?://[^\s\)"\']+(?:api|internal|admin|staging)[^\s\)"\']*', "内部/管理 URL"),
]

INJECTION_PATTERNS = [
    (r'\$\{.*\}', "YAML/Shell 变量注入模式"),
    (r'{{.*}}', "模板注入模式"),
    (r'<script[^>]*>', "XSS 脚本标签"),
    (r'javascript:', "JavaScript 协议注入"),
]

UNSAFE_OPERATION_PATTERNS = [
    (r'rm\s+-rf\s+/', "危险删除命令 (rm -rf /)"),
    (r'del\s+/[sS]\s+/[qQ]', "Windows 危险删除命令"),
    (r'format\s+[a-zA-Z]:', "格式化磁盘命令"),
    (r'sudo\s+rm', "sudo 删除操作"),
    (r'chmod\s+777', "不安全的权限设置"),
    (r'eval\s*\(', "eval() 动态执行"),
    (r'exec\s*\(', "exec() 动态执行"),
    (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "shell=True 子进程调用"),
]

# Weight distribution: 结构 30% + 触发设计 25% + 用户体验 20% + 安全性 10% + Token 预算 15%
DIMENSION_WEIGHTS = {
    "content_structure": 0.30,
    "trigger_design": 0.25,
    "user_experience": 0.20,
    "security": 0.10,
    "token_budget": 0.15,
}


def check_trigger_design(skill: dict) -> dict:
    checks = []
    deductions = 0.0
    desc = skill["description"]
    body = skill["body"]

    has_use_for = bool(re.search(r"USE\s+FOR[:\s]", desc, re.IGNORECASE))
    if has_use_for:
        checks.append(("包含 USE FOR 触发模式", 0.0, "PASS"))
    else:
        if skill["triggers"]:
            checks.append(("使用 triggers 字段代替 USE FOR", 0.0, "PASS"))
        else:
            checks.append(("description 中缺少 USE FOR 触发模式", 0.2, "WARN"))
            deductions += 0.2

    has_anti_trigger = bool(re.search(r"DO\s+NOT\s+USE\s+FOR[:\s]", desc, re.IGNORECASE))
    if has_anti_trigger:
        checks.append(("包含 DO NOT USE FOR 反触发模式", 0.0, "PASS"))
    else:
        body_anti = bool(re.search(r"(do\s+not|不应|不要|避免)", body, re.IGNORECASE))
        if body_anti:
            checks.append(("反触发仅在 body 中（建议移至 description）", 0.1, "WARN"))
            deductions += 0.1
        else:
            checks.append(("缺少反触发模式（DO NOT USE FOR）", 0.15, "WARN"))
            deductions += 0.15

    use_for_match = re.search(r"USE\s+FOR[:\s]+(.*?)(?:DO\s+NOT|$)", desc, re.IGNORECASE | re.DOTALL)
    if use_for_match:
        triggers_text = use_for_match.group(1)
        trigger_phrases = [t.strip().strip('",') for t in re.split(r'[,;，；]', triggers_text) if t.strip()]
        if len(trigger_phrases) >= 3:
            checks.append((f"触发覆盖度良好（{len(trigger_phrases)} 个触发短语）", 0.0, "PASS"))
        elif len(trigger_phrases) >= 1:
            checks.append((f"触发覆盖度有限（{len(trigger_phrases)} 个短语，建议 3+）", 0.05, "INFO"))
            deductions += 0.05

    score = max(0.0, 1.0 - deductions)
    return {"dimension": "trigger_design", "score": round(score, 2), "checks": checks}


def check_content_structure(skill: dict) -> dict:
    checks = []
    deductions = 0.0
    body = skill["body"]

    if not body:
        checks.append(("skill body 为空", 0.5, "CRITICAL"))
        return {"dimension": "content_structure", "score": 0.5, "checks": checks}

    # Frontmatter checks
    if not skill["name"]:
        checks.append(("缺少 name 字段", 0.3, "CRITICAL"))
        deductions += 0.3
    elif len(skill["name"]) < 2:
        checks.append(("name 字段过短（< 2 字符）", 0.1, "WARN"))
        deductions += 0.1

    desc = skill["description"]
    if not desc:
        checks.append(("缺少 description 字段", 0.3, "CRITICAL"))
        deductions += 0.3
    else:
        desc_len = len(desc)
        if desc_len < 150:
            checks.append((f"description 过短（{desc_len} 字符，最低 150）", 0.2, "WARN"))
            deductions += 0.2
        elif desc_len > 1024:
            checks.append((f"description 过长（{desc_len} 字符，上限 1024）", 0.1, "WARN"))
            deductions += 0.1
        else:
            checks.append((f"description 长度合格（{desc_len} 字符）", 0.0, "PASS"))

    if not skill["version"]:
        checks.append(("缺少 version 字段（建议补充）", 0.05, "INFO"))
        deductions += 0.05

    if not skill["tags"]:
        checks.append(("缺少 tags 字段（建议补充，提升可发现性）", 0.05, "INFO"))
        deductions += 0.05

    # Body structure checks
    for pattern, name in EXPECTED_SECTIONS:
        if re.search(pattern, body, re.MULTILINE | re.IGNORECASE):
            checks.append((f"包含「{name}」章节", 0.0, "PASS"))
        else:
            checks.append((f"缺少「{name}」章节", 0.1, "INFO"))
            deductions += 0.1

    code_blocks = len(re.findall(r'```[\s\S]*?```', body))
    if code_blocks > 0:
        checks.append((f"包含 {code_blocks} 个代码/示例块", 0.0, "PASS"))
    else:
        checks.append(("未找到代码/示例块", 0.05, "INFO"))
        deductions += 0.05

    tables = len(re.findall(r'\|.*\|.*\n\|[-:| ]+\|', body))
    if tables > 0:
        checks.append((f"包含 {tables} 个表格", 0.0, "PASS"))
    else:
        checks.append(("未找到表格（表格可提升可读性）", 0.02, "INFO"))
        deductions += 0.02

    score = max(0.0, 1.0 - deductions)
    return {"dimension": "content_structure", "score": round(score, 2), "checks": checks}


def check_token_budget(skill: dict) -> dict:
    checks = []
    deductions = 0.0

    line_count = skill["total_lines"]
    body_lines = skill["body_lines"]
    token_est = estimate_tokens(skill["content"])

    if line_count > 500:
        over_pct = (line_count - 500) / 500
        deduction = min(0.3, over_pct * 0.1)
        checks.append((f"SKILL.md 过长（{line_count} 行，软限制 500）", deduction, "WARN"))
        deductions += deduction
    else:
        checks.append((f"SKILL.md 行数合格（{line_count} 行）", 0.0, "PASS"))

    if token_est > 5000:
        checks.append((f"预估 token 过高（{token_est}，硬限制 5000）", 0.3, "CRITICAL"))
        deductions += 0.3
    elif token_est > 3000:
        checks.append((f"预估 token 偏高（{token_est}）", 0.05, "INFO"))
        deductions += 0.05
    else:
        checks.append((f"预估 token 合格（{token_est}）", 0.0, "PASS"))

    if body_lines > 0 and line_count > 0:
        body_ratio = body_lines / line_count
        if body_ratio > 0.9:
            checks.append(("body 占比过大，建议将额外内容移至 references/", 0.05, "INFO"))
            deductions += 0.05

    score = max(0.0, 1.0 - deductions)
    return {"dimension": "token_budget", "score": round(score, 2), "checks": checks}


def check_routing_clarity(skill: dict) -> dict:
    checks = []
    deductions = 0.0
    desc = skill["description"]

    found_markers = []
    for marker_pattern in ROUTING_MARKERS:
        if re.search(marker_pattern, desc, re.IGNORECASE):
            marker_name = marker_pattern.replace(r"\s+", " ").replace(r":", "")
            found_markers.append(marker_name)

    if found_markers:
        checks.append((f"包含路由标记：{', '.join(found_markers)}", 0.0, "PASS"))
    else:
        checks.append(("缺少路由标记（INVOKES、FOR SINGLE OPERATIONS 等）", 0.1, "INFO"))
        deductions += 0.1

    if desc:
        vague_patterns = ["help with", "assist", "general purpose", "various tasks"]
        for vp in vague_patterns:
            if vp in desc.lower():
                checks.append((f"description 包含模糊短语：'{vp}'", 0.1, "WARN"))
                deductions += 0.1
                break
        else:
            checks.append(("description 具体明确", 0.0, "PASS"))

    use_match = re.search(r"USE\s+FOR[:\s]+(.*?)(?:DO\s+NOT|$)", desc, re.IGNORECASE | re.DOTALL)
    dont_match = re.search(r"DO\s+NOT\s+USE\s+FOR[:\s]+(.*?)$", desc, re.IGNORECASE | re.DOTALL)
    if use_match and dont_match:
        use_text = use_match.group(1).lower()
        dont_text = dont_match.group(1).lower()
        use_words = set(re.findall(r'\b\w{3,}\b', use_text))
        dont_words = set(re.findall(r'\b\w{3,}\b', dont_text))
        overlap = use_words & dont_words - {"use", "for", "the", "and", "this", "that"}
        if overlap:
            checks.append((f"触发冲突：关键词同时出现在 USE FOR 和 DO NOT USE FOR 中：{overlap}", 0.1, "WARN"))
            deductions += 0.1
        else:
            checks.append(("未检测到触发冲突", 0.0, "PASS"))

    score = max(0.0, 1.0 - deductions)
    return {"dimension": "routing_clarity", "score": round(score, 2), "checks": checks}


def check_security(skill: dict) -> dict:
    """安全性检查：扫描 SKILL.md 中的敏感信息、注入模式和危险操作。"""
    checks = []
    deductions = 0.0
    content = skill["content"]
    body = skill["body"]

    # 1. 敏感信息泄露检测
    found_secrets = []
    for pattern, desc in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            found_secrets.append(desc)

    if found_secrets:
        checks.append((f"发现潜在敏感信息：{', '.join(found_secrets)}", 0.3, "CRITICAL"))
        deductions += 0.3
    else:
        checks.append(("未发现硬编码密钥或敏感信息", 0.0, "PASS"))

    # 2. 注入模式检测
    found_injections = []
    for pattern, desc in INJECTION_PATTERNS:
        if re.search(pattern, content):
            # Allow template patterns in examples/code blocks
            in_code_block = False
            for block in re.findall(r'```[\s\S]*?```', content):
                if re.search(pattern, block):
                    in_code_block = True
                    break
            if not in_code_block:
                found_injections.append(desc)

    if found_injections:
        checks.append((f"发现注入风险模式：{', '.join(found_injections)}", 0.2, "WARN"))
        deductions += 0.2
    else:
        checks.append(("未发现注入风险模式", 0.0, "PASS"))

    # 3. 危险操作检测
    found_unsafe = []
    for pattern, desc in UNSAFE_OPERATION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            found_unsafe.append(desc)

    if found_unsafe:
        checks.append((f"发现危险操作模式：{', '.join(found_unsafe)}", 0.2, "WARN"))
        deductions += 0.2
    else:
        checks.append(("未发现危险操作模式", 0.0, "PASS"))

    # 4. 文件路径安全
    abs_paths = re.findall(r'(?:^|\s|["\'])(/[a-zA-Z0-9_/.-]+(?:\.\w+)?)(?:$|\s|["\'\)])', body, re.MULTILINE)
    if abs_paths:
        checks.append((f"包含 {len(abs_paths)} 个硬编码绝对路径（建议使用相对路径或变量）", 0.05, "INFO"))
        deductions += 0.05
    else:
        checks.append(("未使用硬编码绝对路径", 0.0, "PASS"))

    # 5. 数据边界声明
    has_scope = bool(re.search(r'(?:DO\s+NOT\s+USE|不应|不要|避免|不得)', body, re.IGNORECASE))
    if has_scope:
        checks.append(("包含使用边界/限制声明", 0.0, "PASS"))
    else:
        checks.append(("缺少使用边界声明（建议添加 DO NOT USE FOR）", 0.05, "INFO"))
        deductions += 0.05

    score = max(0.0, 1.0 - deductions)
    return {"dimension": "security", "score": round(score, 2), "checks": checks}


def check_user_experience(skill: dict) -> dict:
    """用户体验评估：检查工作流指引、示例质量、范围边界和内容组织。"""
    checks = []
    deductions = 0.0
    desc = skill["description"]
    body = skill["body"]

    # 1. 目的清晰度 (30% of UX score)
    has_clear_purpose = bool(re.search(r'(?:USE\s+FOR|用于|适用于|目标|purpose)', desc, re.IGNORECASE))
    if has_clear_purpose:
        checks.append(("用途说明清晰（description 包含 USE FOR 或用途描述）", 0.0, "PASS"))
    else:
        checks.append(("用途说明不清晰（建议在 description 中明确 USE FOR）", 0.15, "WARN"))
        deductions += 0.15

    desc_len = len(desc)
    if desc_len >= 300:
        checks.append((f"description 信息丰富（{desc_len} 字符）", 0.0, "PASS"))
    elif desc_len >= 150:
        checks.append((f"description 信息量适中（{desc_len} 字符，建议 300+）", 0.05, "INFO"))
        deductions += 0.05
    else:
        checks.append((f"description 过于简短（{desc_len} 字符），用户难以理解 skill 用途", 0.1, "WARN"))
        deductions += 0.1

    # 2. 工作流指引 (30% of UX score)
    has_workflow = bool(re.search(
        r'(?:步骤|step|流程|workflow|工作流|先.*然后|[12]\.\s)',
        body, re.IGNORECASE
    ))
    if has_workflow:
        checks.append(("包含工作流/步骤指引", 0.0, "PASS"))
    else:
        checks.append(("缺少工作流指引（建议添加步骤说明，帮助用户理解执行流程）", 0.1, "WARN"))
        deductions += 0.1

    has_decision = bool(re.search(
        r'(?:如果|when|如果.*则|条件|根据|判断|case|switch)',
        body, re.IGNORECASE
    ))
    if has_decision:
        checks.append(("包含决策点/条件分支说明", 0.0, "PASS"))
    else:
        checks.append(("缺少条件分支说明（建议描述不同场景的处理方式）", 0.05, "INFO"))
        deductions += 0.05

    # 3. 示例质量 (20% of UX score)
    examples = re.findall(r'(?:例子|示例|example|范例)[：:\s]*', body, re.IGNORECASE)
    code_blocks = re.findall(r'```[\s\S]*?```', body)

    if examples or (code_blocks and len(code_blocks) >= 2):
        checks.append((f"包含充分的示例（{len(examples)} 个示例标记，{len(code_blocks)} 个代码块）", 0.0, "PASS"))
    elif code_blocks:
        checks.append((f"示例有限（{len(code_blocks)} 个代码块，建议添加更多用例）", 0.05, "INFO"))
        deductions += 0.05
    else:
        checks.append(("缺少使用示例（建议添加输入→输出的完整示例）", 0.1, "WARN"))
        deductions += 0.1

    # 4. 范围边界 (10% of UX score)
    has_anti = bool(re.search(r'(?:DO\s+NOT\s+USE|不适用|不要用于|避免在.*使用)', desc, re.IGNORECASE))
    if has_anti:
        checks.append(("包含明确的「不适用场景」说明", 0.0, "PASS"))
    else:
        body_anti = bool(re.search(r'(?:不要|不应|避免|不得|不支持)', body, re.IGNORECASE))
        if body_anti:
            checks.append(("「不适用场景」仅在 body 中（建议移至 description）", 0.05, "WARN"))
            deductions += 0.05
        else:
            checks.append(("缺少「不适用场景」说明（帮助用户避免误用）", 0.05, "INFO"))
            deductions += 0.05

    # 5. 内容组织 (10% of UX score)
    headers = re.findall(r'^#{1,3}\s+\S+', body, re.MULTILINE)
    if len(headers) >= 5:
        checks.append((f"内容结构清晰（{len(headers)} 个标题段落）", 0.0, "PASS"))
    elif len(headers) >= 3:
        checks.append((f"内容组织尚可（{len(headers)} 个标题，建议 5+）", 0.03, "INFO"))
        deductions += 0.03
    else:
        checks.append((f"内容组织较弱（仅 {len(headers)} 个标题，建议增加段落划分）", 0.05, "WARN"))
        deductions += 0.05

    # Check for table of contents or navigation
    has_toc = bool(re.search(r'(?:目录|TOC|table\s+of\s+contents|##\s*\d)', body, re.IGNORECASE))
    if has_toc:
        checks.append(("包含目录/导航结构", 0.0, "PASS"))

    score = max(0.0, 1.0 - deductions)
    return {"dimension": "user_experience", "score": round(score, 2), "checks": checks}


def run_static_analysis(skill_path: Path) -> dict:
    skill = parse_skill_md(skill_path)

    dimensions = [
        check_content_structure(skill),
        check_trigger_design(skill),
        check_user_experience(skill),
        check_security(skill),
        check_token_budget(skill),
    ]

    # Weighted overall score
    weighted_sum = 0.0
    total_weight = 0.0
    for d in dimensions:
        w = DIMENSION_WEIGHTS.get(d["dimension"], 0.1)
        weighted_sum += d["score"] * w
        total_weight += w
    overall = weighted_sum / total_weight if total_weight > 0 else 0.0

    DIM_CN = {
        "content_structure": "内容结构",
        "trigger_design": "触发设计",
        "user_experience": "用户体验",
        "security": "安全性",
        "token_budget": "Token 预算",
    }

    suggestions = []
    for dim in dimensions:
        for text, deduction, severity in dim["checks"]:
            if deduction > 0 and severity in ("WARN", "CRITICAL"):
                suggestions.append({
                    "dimension": DIM_CN.get(dim["dimension"], dim["dimension"]),
                    "severity": severity,
                    "message": text,
                })

    result = {
        "skill_name": skill["name"],
        "skill_path": str(skill_path),
        "dimensions": dimensions,
        "overall_score": round(overall, 2),
        "suggestions": suggestions,
        "metadata": {
            "line_count": skill["total_lines"],
            "estimated_tokens": estimate_tokens(skill["content"]),
        },
    }

    return result
