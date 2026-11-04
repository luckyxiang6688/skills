---
name: luckyxiang-docsummer
description: |
  用 CoD+CoVe 混合框架（Chain-of-Density 密度迭代 + Chain-of-Verification 事实验证）对文档进行高精度总结。
  支持 doc/docx/pdf/md/ppt/pptx 及任意 markitdown 可处理的格式。
  输出 MD + HTML 双格式。4 级精度：brief/medium/long/deep。
  触发词：总结文档、文档摘要、概括这个文件、summarize this doc、pdf总结、ppt总结、word总结、
  docsummer、文档总结、帮我总结、read and summarize、what does this document say。
  即使用户只是说「帮我看看这个PDF讲了什么」「概括一下这个PPT」也应触发。
  不用于 URL 总结（那是 summarize skill）、不用于写文章（那是 writer skill）。
---

# luckyxiang-docsummer

> 万物皆可总结：PDF、Word、PPT、Markdown……CoD 密度迭代 + CoVe 事实验证，零幻觉。

## 能力边界

这个 skill 只做一件事：**文档 → 高精度结构化总结**。输出 MD 文件 + HTML 文件。

| 输入格式 | 预处理方式 |
|---------|-----------|
| .md | 直接读取，无需预处理 |
| .pdf | Claude Code Read 工具（支持 pages 参数，每次最多 20 页） |
| .doc / .docx | Claude Code Read 工具 |
| .ppt / .pptx | anytomd 脚本转为 MD |
| 其他格式 | anytomd 脚本转为 MD |

## 工作流总览

```
步骤0: 预处理 → 文件转为可读文本
步骤1: DRAFT → 生成初稿（允许信息稀疏）
步骤2: DENSITY → CoD 密度迭代（识别缺失实体 → 融入，重复 2-3 次）
步骤3: VERIFY → CoVe 事实验证（提取声明 → 回原文核实 → 修正）
步骤4: 输出 → 写入 MD 文件 + 转为 HTML 文件
```

## 步骤 0：文件预处理

### .md 文件
直接用 Read 工具读取全文。

### .pdf 文件
用 Read 工具分批读取（每次最多 20 页）：
- 第一轮：读取前 5 页，提取标题、作者、目录、文档类型
- 后续轮：每次读取 20 页，直到读完

### .doc / .docx 文件
用 Read 工具直接读取。

### .ppt / .pptx 及其他格式
调用 anytomd 脚本预处理为 MD：
```bash
python3 "{luckyxiang-anytomd}/scripts/any_to_md.py" "<input_path>" -o "<temp_md_path>"
```
然后读取生成的 MD 文件。

### 文档评估（所有格式）
预处理后，内部评估（不输出给用户）：
- 标题、作者、文档类型
- 总长度（字数估算）
- 章节结构（如果有标题层级）
- 是否为英文文档（中文字符 <30%）
- 长度策略：≤8000字用单次总结，>8000字用分层总结

### 英文文档处理
如果文档为英文（中文字符 <30%）：
- 总结默认用中文输出
- 关键术语保留英文原文，括号附中文释义，如：Transformer（变换器）
- 用户可指定输出语言

## 步骤 1：DRAFT（生成初稿）

### 短文档（≤8000字）—— 单次 DRAFT

读取全文后，用以下 prompt 生成初稿。prompt 框架详见 `references/prompt-framework.md`。

```xml
<role>
你是一个精确文档总结引擎。你的职责是从文档中提取信息，生成结构化总结。
你不是评论者、不是分析师、不是补充者——你只做提取和重组。
</role>

<constraints>
C1. 忠实约束：所有内容必须源自文档原文。绝不添加原文没有的信息、推断、评价或背景知识。
C2. 精确约束：数据（数字、比例、日期、名称）必须与原文完全一致，不可近似或替换。
C3. 结构约束：按 {structure_spec} 组织输出。不自行创造新的分类框架。
C4. 语言约束：输出语言为{output_lang}。英文文档保留关键术语原文（括号附中文释义）。
C5. 长度约束：目标 {target_chars} 字（{min_chars}-{max_chars}）。宁可精简也不凑字数。
C6. 不确定约束：原文模糊或矛盾处，标注 [原文表述不清]，而非自行解释或调和。
</constraints>

<output-spec>
{output_spec}
</output-spec>

<content>
{document_content}
</content>
```

### 长文档（>8000字）—— 分层 DRAFT

分 3 个子步骤：

**子步骤 1a：全局扫描**
读取文档前 5%（目录、引言、各章节首段），输出文档地图：
```
文档地图（≤500字）：
- 标题：...
- 类型：报告/论文/书籍/手册/...
- 核心论点（一句话）：...
- 章节结构：
  1. [章节名]：[一句话核心命题]
  2. [章节名]：[一句话核心命题]
  ...
```

**子步骤 1b：分块精读**
按章节/逻辑段落分块（每块 ≤4000字），对每个块输出：
- 核心命题（1-2句）
- 关键论据（3-5条）
- 重要数据（原文中的关键数字、定义、结论，精确转述）

**子步骤 1c：整合**
基于文档地图 + 块级总结，按用户请求的长度级别组装初稿。

## 步骤 2：DENSITY（CoD 密度迭代）

对比初稿与原文（或块级总结），执行 2-3 轮密度增强。每轮：

```xml
<role>
你正在进行信息密度增强。对比当前总结与原文，识别缺失的关键实体并融入。
</role>

<task>
1. 读取下方 <summary> 中的当前总结
2. 读取下方 <source> 中的原文
3. 识别当前总结中缺失的关键实体：
   - Relevant：与文档核心论点直接相关
   - Specific：具体的数据、名称、日期、结论（不是泛泛描述）
   - Novel：当前总结中未出现的
   - Faithful：原文中确实存在的（不是推断的）
4. 列出缺失实体（最多 5 个），格式：[ENTITY: 内容 | 类型: 数据/结论/因果/定义]
5. 在保持同等长度（不超过 {max_chars} 字）的前提下融入缺失实体
6. 融入方式：替换泛泛描述为具体信息，而非追加新段落
</task>

<constraints>
C1. 融入实体时不可增加总长度。用具体信息替换模糊描述。
C2. 只融入原文中确实存在的实体，不推断。
C3. 如果已无重要缺失实体，输出 "DENSITY_COMPLETE" 并返回当前总结。
</constraints>

<summary>
{current_summary}
</summary>

<source>
{document_content_or_chunk_summaries}
</source>
```

终止条件：LLM 输出 `DENSITY_COMPLETE`，或已执行 3 轮。

## 步骤 3：VERIFY（CoVe 事实验证）

从密度增强版中提取关键声明，回到原文逐条核实：

```xml
<role>
你正在进行事实验证。检查总结中的每个关键声明是否与原文一致。
</role>

<task>
1. 从 <summary> 中提取所有关键声明（包含数据、结论、因果关系的句子）
2. 对每个声明生成验证问题："原文是否确实说了 [具体声明内容]？"
3. 回到 <source> 中查找每个验证问题的答案
4. 分类：
   - VERIFIED：原文明确支持 → 保留
   - PARTIALLY_VERIFIED：原文部分支持 → 修正为与原文一致的版本
   - UNVERIFIED：原文中找不到 → 删除
   - CONTRADICTED：原文内容与声明矛盾 → 修正或删除
5. 输出修正后的最终总结
</task>

<output>
直接输出修正后的最终总结。不要输出验证过程。
</output>

<summary>
{density_enhanced_summary}
</summary>

<source>
{document_content_or_key_passages}
</source>
```

## 步骤 4：输出文件

### 写入 MD 文件
用 Write 工具将最终总结写入 `<input_stem>-summary.md`。

### 转为 HTML 文件
调用 mdtohtml 脚本：
```bash
python3 "{luckyxiang-mdtohtml}/scripts/md_to_html.py" "<summary_md_path>" --theme interactive -o "<output_html_path>"
```

主题选择规则：
- brief / medium → `reading`（极简阅读）
- long → `article`（Tufte 风）
- deep → `interactive`（长文档导航+目录+折叠）

如果 mdtohtml 不可用（pandoc 未安装），跳过 HTML 输出并告知用户。

## 长度级别

用户通过参数指定，默认根据文档长度自动选择：

| 级别 | 目标字数 | 默认触发 | 输出结构 |
|------|---------|---------|---------|
| brief | 300-500字 | 用户指定 | 1-2段纯文本，无标题 |
| medium | 800-1500字 | ≤8000字文档默认 | 3-5个 `##` 标题节 |
| long | 2000-4000字 | >8000字文档默认 | `##` + `###` 标题层级 |
| deep | 不限 | 用户指定 | 全局概览→章节详解→数据表→引述 |

各级别的完整输出规范见 `references/output-schema.md`。

## 输入解析

当用户触发此 skill 时，从请求中提取：

1. **文件路径**（必填）：接受 .md / .pdf / .doc / .docx / .ppt / .pptx 及任意文件
2. **精度级别**（可选）：brief / medium / long / deep。默认自动选择
3. **输出语言**（可选）：默认中文（英文文档保留术语原文）
4. **聚焦领域**（可选）：用户指定的重点主题
5. **输出目录**（可选）：默认与源文件同目录

## 调用示例

```
/docsummer report.pdf
/docsummer paper.pdf deep
/docsummer presentation.pptx brief
/docsummer readme.md long
/docsummer C:/docs/whitepaper.pdf medium
```

## 一条龙衔接

```bash
# 任意文件 → 总结 MD + HTML
/docsummer whitepaper.pdf long
# 产出：whitepaper-summary.md + whitepaper-summary.html

# 总结后想要更精美的 HTML，手动调用 mdtohtml
python3 "{luckyxiang-mdtohtml}/scripts/md_to_html.py" summary.md --theme report -o summary-fancy.html

# 不在支持列表中的格式，先用 anytomd 转换
python3 "{luckyxiang-anytomd}/scripts/any_to_md.py" data.xlsx -o data.md
/docsummer data.md brief
```

## 依赖

- markitdown（仅处理 PPT 等非原生格式时需要）：`python3 -m pip install 'markitdown[all]'`
- pandoc（仅 HTML 输出时需要）：`brew install pandoc`

缺依赖不阻塞核心功能（总结 + MD 输出），只是跳过对应步骤并提示。

## 异常处理

| 场景 | 处理 |
|------|------|
| 文件不存在 | 立即报错，给出正确路径建议 |
| 文件无法读取 | 报告已读内容，标记不可读部分 |
| 扫描 PDF（无文字层） | 提示用户用 `--llm-describe` 参数或 OCR 工具 |
| 文档超长（>500页） | 建议用户指定 deep 级别，或聚焦特定章节 |
| HTML 转换失败 | 输出 MD 文件，提示 pandoc 可能未安装 |

## References

| 任务 | 读 |
|------|-----|
| CoD + CoVe 混合框架详细说明 | `references/prompt-framework.md` |
| 4 级输出结构规范 | `references/output-schema.md` |
| 反幻觉协议 | `references/anti-hallucination.md` |

## 核心提醒

- **零幻觉**：CoVe 验证步骤会逐条核实关键声明，删除无法验证的内容。
- **密度优先**：CoD 迭代确保信息密度最大化，不遗漏关键实体。
- **复用现有 skill**：文件预处理用 anytomd，HTML 输出用 mdtohtml，本 skill 只负责总结逻辑。
- **长文档分块**：>8000字自动切换分层模式，按章节边界分块。
- **英文文档**：保留关键术语原文（括号附中文释义），不纯翻译。
