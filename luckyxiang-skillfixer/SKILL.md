---
name: luckyxiang-skillfixer
description: |
  根据 luckyxiang-howskill 的评估结果自动修复 SKILL.md，提升 skill 质量。支持静态分析修复（元数据、触发设计、内容结构、用户体验、安全性、Token 预算）和动态评估修复（触发准确性、输出质量、内容正确性）。

  USE FOR: 修复skill、改进skill、根据评估结果修skill、自动修复SKILL.md、提升skill质量、skillfixer、/fix-skill、修复一下这个skill、帮我改进skill、根据评估报告修skill

  DO NOT USE FOR: 评估skill（用luckyxiang-howskill）、创建新skill（用skill-creator）、写skill代码、安装skill
version: "1.0"
author: luckyxiang-skillfixer
tags: [fix, improve, skill, quality]
---

# LuckyXiang SkillFixer — Skill 自动修复工具

根据评估结果自动修复 SKILL.md，提升 skill 质量。

## 快速参考

| 命令 | 说明 |
|------|------|
| `/fix-skill <path>` | 修复 skill（交互式确认） |
| `/fix-skill <path> --eval <json>` | 指定评估结果文件 |
| `/fix-skill <path> --dry-run` | 仅展示修复计划，不应用 |
| `/fix-skill <path> --yes` | 自动应用 AUTO 类修复 |

## 修复类别

| 类别 | 说明 | 默认行为 |
|------|------|---------|
| AUTO | 安全自动应用（添加 version/tags、章节标题） | --yes 时自动，否则确认 |
| LLM_ASSISTED | 需要 LLM 生成内容（触发短语、扩展 description） | 始终确认 |
| STRUCTURAL | 修改内容结构（提取到 references/、替换敏感信息） | 始终确认 |
| MANUAL | 无法自动处理（空 body） | 仅报告 |

## 工作流

1. 加载评估结果（默认从 D:\work\claude\howskill\ 扫描最新）
2. 解析建议 → 映射修复动作
3. 展示修复计划（维度 + 严重性 + 修复预览）
4. 用户确认后应用修复（自动备份 SKILL.md.bak）
5. 重评估验证（对比旧分数 vs 新分数）
6. 最多迭代 3 轮

## 异常处理

- 无评估结果 → 先跑 howskill 静态分析
- 分数未提升 → 可回滚到备份
- 修复冲突 → 跳过并报告
