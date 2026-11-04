"""Text grader: validates output using substring and regex matching.

Checks:
- contains: 子串必须出现（不区分大小写）
- not_contains: 子串必须不出现（不区分大小写）
- contains_cs: 子串必须出现（区分大小写）
- not_contains_cs: 子串必须不出现（区分大小写）
- regex_match: 正则必须匹配
- regex_not_match: 正则必须不匹配

Score = 通过检查数 / 总检查数 (0.0 to 1.0)。
"""

import re


def grade_text(output: str, config: dict) -> dict:
    checks = []
    total = 0
    passed = 0

    output_lower = output.lower()

    for pattern in config.get("contains", []):
        total += 1
        if pattern.lower() in output_lower:
            checks.append({"rule": "contains", "pattern": pattern, "result": "PASS"})
            passed += 1
        else:
            checks.append({"rule": "contains", "pattern": pattern, "result": "FAIL"})

    for pattern in config.get("not_contains", []):
        total += 1
        if pattern.lower() not in output_lower:
            checks.append({"rule": "not_contains", "pattern": pattern, "result": "PASS"})
            passed += 1
        else:
            checks.append({"rule": "not_contains", "pattern": pattern, "result": "FAIL"})

    for pattern in config.get("contains_cs", []):
        total += 1
        if pattern in output:
            checks.append({"rule": "contains_cs", "pattern": pattern, "result": "PASS"})
            passed += 1
        else:
            checks.append({"rule": "contains_cs", "pattern": pattern, "result": "FAIL"})

    for pattern in config.get("not_contains_cs", []):
        total += 1
        if pattern not in output:
            checks.append({"rule": "not_contains_cs", "pattern": pattern, "result": "PASS"})
            passed += 1
        else:
            checks.append({"rule": "not_contains_cs", "pattern": pattern, "result": "FAIL"})

    for pattern in config.get("regex_match", []):
        total += 1
        try:
            if re.search(pattern, output):
                checks.append({"rule": "regex_match", "pattern": pattern, "result": "PASS"})
                passed += 1
            else:
                checks.append({"rule": "regex_match", "pattern": pattern, "result": "FAIL"})
        except re.error as e:
            checks.append({"rule": "regex_match", "pattern": pattern, "result": "ERROR", "error": str(e)})

    for pattern in config.get("regex_not_match", []):
        total += 1
        try:
            if not re.search(pattern, output):
                checks.append({"rule": "regex_not_match", "pattern": pattern, "result": "PASS"})
                passed += 1
            else:
                checks.append({"rule": "regex_not_match", "pattern": pattern, "result": "FAIL"})
        except re.error as e:
            checks.append({"rule": "regex_not_match", "pattern": pattern, "result": "ERROR", "error": str(e)})

    if total == 0:
        score = 1.0
        feedback = "未配置文本检查项，默认通过"
    else:
        score = passed / total
        failed_checks = [c for c in checks if c["result"] == "FAIL"]
        if failed_checks:
            feedback = f"{len(failed_checks)}/{total} 项文本检查未通过"
        else:
            feedback = f"全部 {total} 项文本检查通过"

    return {
        "type": "text",
        "score": round(score, 2),
        "passed": score >= 0.8,
        "feedback": feedback,
        "details": checks,
    }