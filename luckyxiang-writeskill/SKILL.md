---
name: luckyxiang-writeskill
description: |
  日常 Skill 创建工具：从需求到成品，三步完成 Claude Code Skill 的创建。
  内置 4 类模板（content_creation / analysis / workflow / utility），自动分类、模板填充、质量验证。

  USE FOR: 创建skill、写skill、新建skill、writeskill、创建一个skill、帮我写个skill、写一个新的skill、新建一个skill、做个skill、搞个skill、需要一个skill、需要一个工具、做一个工具、做个工具、新建工具、创建工具、定制一个skill、定制一个工具。
  当用户说"帮我创建一个skill""我想写一个新的skill""做个skill""搞个工具""需要一个XX的skill/tool"时应触发。
  即使用户只是说"能不能帮我搞个XX工具"或"我们需要一个XX的skill"，只要上下文暗示需要创建新的skill/tool，都应触发。

  DO NOT USE FOR: 评估skill（用howskill）、修改已有skill（直接改）、删除skill、skill-creator的基准测试。
version: "1.0"
author: luckyxiang
tags: [skill-creation, template, quality, workflow]
---

# luckyxiang-writeskill

> 日常 Skill 创建工具：从需求到成品，三步完成。内置模板 + 质量验证，确保生成的 skill 通过 howskill 评估。

## 概述

luckyxiang-writeskill 帮助用户快速创建高质量的 Claude Code Skill。核心特色：三步工作流（需求采集 → Skill 生成 → 质量验证）；4 类内置模板确保结构一致性；自动调用 howskill 验证质量，确保得分 ≥ 0.85。

## 快速参考

| 命令 | 说明 |
|------|------|
| `/writeskill` | 交互式创建（逐步采访） |
| `/writeskill "创建一个XXX的skill"` | 带描述创建（跳过部分采访） |
| `/writeskill --type analysis` | 指定类型创建 |
| `/writeskill --from deepreport` | 参考已有 skill 创建 |

## 示例

```bash
# 交互式创建
/writeskill

# 带描述创建
/writeskill "创建一个将markdown转为微信公众号格式的skill"

# 指定类型
/writeskill "创建一个代码审查skill" --type analysis

# 参考已有 skill
/writeskill "创建一个通俗解读skill" --from deepreport
```

## 工作流总览

```
步骤1: 需求采集 → 采访用户，确定 skill 的 5 个核心要素
步骤2: Skill 生成 → 从模板生成完整 skill 目录（SKILL.md + references/）
步骤3: 质量验证 → 调用 howskill 评估，反馈改进建议
```

## 步骤 1：需求采集

通过 5 个核心问题确定 skill 的全部参数。按 `references/interview-guide.md` 中的采访模板执行。

| # | 问题 | 对应内容 |
|---|------|---------|
| 1 | 这个 skill 做什么？ | description 第 1 句 |
| 2 | 什么时候应该触发？ | USE FOR 触发词 |
| 3 | 什么时候不该触发？ | DO NOT USE FOR 反触发词 |
| 4 | 输入是什么？输出是什么？ | 能力边界章节 |
| 5 | 有没有参考的现有 skill？ | 工作流步骤模板 |

### 采集规则

- 如果用户一次说清了所有 5 个要素，直接跳到步骤 2
- 如果信息不完整，按模板逐个追问，最多追问 2 轮
- 如果用户说"你看着办"或"随便"，使用默认值填充
- 触发词至少 3 个（howskill trigger_design 维度要求）

### 自动分类

根据 description 中的关键词，自动分类为 4 种类型之一：

| 类型 | 关键词 | 典型 skill |
|------|--------|-----------|
| content_creation | 写、生成、创建、报告、文章、解读 | deepreport, plainreport, writer |
| analysis | 分析、研究、评估、解读、检查 | graphify, howskill |
| workflow | 步骤、流程、转换、管道、处理 | mdtohtml, docsummer |
| utility | 工具、格式化、验证、辅助 | skill-lint |

## 步骤 2：Skill 生成

### 2.1 确定目录

Skill 目录固定在 `~/.claude/skills/` 下，命名规则：`luckyxiang-{skill-name}`。

### 2.2 从模板生成 SKILL.md

按 `references/templates.md` 中的对应类型模板生成 SKILL.md。

所有模板都包含这些固定章节（howskill 评分所需）：

1. **概述** — 一段话说明 skill 做什么、核心特色
2. **快速参考** — 命令表（命令 + 说明）
3. **示例** — 3-5 个使用示例（代码块）
4. **工作流/步骤** — 分步骤说明执行流程
5. **能力边界** — 输入类型表 + 独立性声明
6. **异常处理** — 场景 + 处理方式表
7. **References** — references/ 文件列表

### 2.3 生成 references/（如需要）

根据 skill 类型决定是否生成 references/ 文件：

| 类型 | 典型 references |
|------|----------------|
| content_creation | prompts.md, style 模板, schema 定义 |
| analysis | prompts.md, 评估标准 |
| workflow | prompts.md, 转换规则 |
| utility | 配置说明 |

### 2.4 质量内建

生成过程中实时检查 `references/quality-checklist.md` 中的质量标准：

- description 长度 ≥ 300 字符
- USE FOR 触发词 ≥ 3 个
- DO NOT USE FOR 反触发词 ≥ 2 个
- SKILL.md 包含概述、快速参考、示例、工作流、异常处理
- 代码块 ≥ 1 个，表格 ≥ 1 个
- 无硬编码密钥/路径
- SKILL.md ≤ 500 行

## 步骤 3：质量验证

生成完成后，调用 howskill 进行完整评估（静态 + 动态）。

### 执行方式

```bash
python3 "{howskill_path}/scripts/run_eval.py" "{skill_path}" --verbose --timeout 300
```

### 结果处理

| 得分 | 处理 |
|------|------|
| ≥ 0.85 | 直接完成，报告结果 |
| 0.7 - 0.85 | 列出扣分项，建议修改，等待用户确认 |
| < 0.7 | 自动修正扣分最多的维度，重新评估（最多 1 次） |

### 常见扣分项及修正

| 扣分维度 | 常见原因 | 修正方式 |
|---------|---------|---------|
| trigger_design | 触发词 < 3 个 | 从 skill 描述中提取更多触发词 |
| content_structure | 缺少示例或表格 | 添加示例代码块和能力边界表格 |
| user_experience | description 太短 | 扩展 description，补充触发说明 |
| token_budget | SKILL.md 过长 | 将详细内容移至 references/ |
| security | 硬编码绝对路径 | 替换为相对路径或变量 |

## 能力边界

这个 skill 做一件事：**从需求创建高质量的 Claude Code Skill**。

| 输入 | 处理方式 |
|------|---------|
| 用户描述 | 解析为 5 个核心要素 |
| 已有 skill 路径 | 读取并参考其结构 |
| --type 参数 | 直接使用指定类型模板 |

**完全独立**，不依赖 skill-creator。质量验证调用 howskill 的 Python 脚本。

## 异常处理

| 场景 | 处理 |
|------|------|
| 用户描述太模糊 | 追问具体用途和触发场景 |
| skill 名称已存在 | 提示用户选择新名称或覆盖 |
| howskill 不可用 | 跳过步骤 3，手动检查质量清单 |
| 生成后评估 < 0.7 | 自动修正 1 次后报告 |
| references/ 不需要 | 不创建空目录 |

## References

| 任务 | 读 |
|------|------|
| 需求采访模板 | `references/interview-guide.md` |
| 4 类 Skill 模板 | `references/templates.md` |
| 质量检查清单 | `references/quality-checklist.md` |

## 核心提醒

- **模板优先**：所有 skill 从模板生成，确保结构一致性和 howskill 高分。
- **质量内建**：生成过程中实时检查质量清单，不等到最后才发现问题。
- **触发词 ≥ 3**：howskill 对 trigger_design 维度要求至少 3 个触发短语。
- **description ≥ 300 字符**：howskill 对 user_experience 维度要求信息丰富的 description。
- **完全独立**：不调用 skill-creator，质量验证通过 howskill 脚本完成。
