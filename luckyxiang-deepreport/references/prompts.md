# 提取与验证 Prompt 模板

## 素材提取 Prompt（步骤 1a：初稿）

```xml
<role>
你是一个精确信息提取引擎。从文档中提取关键信息，不做评价、不添加背景知识、不推断。
</role>

<constraints>
C1. 忠实约束：所有内容必须源自文档原文。绝不添加原文没有的信息。
C2. 精确约束：数据（数字、比例、日期、名称）必须与原文完全一致。
C3. 不确定约束：原文模糊或矛盾处，标注 [原文表述不清]，而非自行解释。
</constraints>

<task>
从以下文档中提取：
1. 核心主题（一句话）
2. 关键数据点（5-15个，精确数值，标注原文位置）
3. 核心结论（3-5条）
4. 关键术语定义（3-10个）
5. 因果关系（2-5条）
6. 与其他工作的关系/引用
7. 可视化素材建议（适合画什么图）
</task>

<content>
{document_content}
</content>
```

## 密度增强 Prompt（步骤 1b：1-2轮）

```xml
<role>
你正在进行信息密度增强。对比当前提取结果与原文，识别遗漏的关键实体。
</role>

<task>
1. 读取 <extract> 中的当前提取结果
2. 读取 <source> 中的原文
3. 识别遗漏的关键实体（Relevant + Specific + Novel + Faithful）
4. 列出遗漏实体（最多 5 个），格式：[ENTITY: 内容 | 类型: 数据/结论/因果/定义]
5. 融入遗漏实体，保持总长度不超过 600 字
6. 如果已无重要遗漏，输出 "DENSITY_COMPLETE"
</task>

<extract>
{current_extraction}
</extract>

<source>
{document_content}
</source>
```

终止条件：输出 `DENSITY_COMPLETE` 或已执行 2 轮。

## 事实验证 Prompt（步骤 4：不可跳过）

```xml
<role>
你正在进行事实验证。检查报告内容中的每个关键声明是否与源文件一致。
</role>

<task>
1. 从 <chapter> 中提取所有关键声明（包含数据、结论、因果关系的句子）
2. 对每个声明生成验证问题："源文件是否确实说了 [具体声明内容]？"
3. 回到 <sources> 中的素材卡片和原文查找答案
4. 分类：
   - VERIFIED：源文件明确支持 → 保留
   - PARTIALLY_VERIFIED：源文件部分支持 → 修正为与原文一致的版本
   - UNVERIFIED：源文件中找不到 → 删除
   - CONTRADICTED：与源文件矛盾 → 删除
5. 输出修正后的章节内容（不输出验证过程）
</task>

<chapter>
{chapter_content}
</chapter>

<sources>
{material_cards_and_original_excerpts}
</sources>
```

## 内容生成约束（步骤 3）

```xml
<constraints>
C1. 每个事实声明必须能追溯到某个源文件的素材卡片
C2. 数值数据必须与源文件完全一致，不可近似或替换
C3. 素材中模糊或矛盾处，标注 [原文表述不清]，不自行解释或调和
C4. 不添加源文件中没有的背景知识、评价或推断
C5. SVG 图表中的标注数据必须与正文一致
C6. 类比和解释可以用通俗语言，但底层事实必须来自素材
C7. 如果某个章节素材不足，标注 [素材不足，以下内容基于有限信息] 而非编造
</constraints>
```
