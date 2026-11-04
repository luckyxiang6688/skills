# 报告章节结构规范

## 标准 8 节结构（depth: standard）

### 第 1 节：总览与脉络

**目的**：让读者快速建立全局认知。

**内容要素**：
- 一句话定义（核心概念 + 生动类比）
- 演进/背景时间线（关键节点 + 年份 + 核心贡献）
- 核心价值主张（为什么重要）

**必配图表**：时间线 SVG（横向，节点 + 年份 + 简述）

**HTML 结构**：
```html
<div class="section" id="s1">
  <div class="section-title"><span class="num">1</span> 总览与脉络</div>
  <div class="section-desc">...</div>
  <div class="highlight">
    <h5>一句话理解 XXX</h5>
    <p>...</p>
  </div>
  <div class="subsection">
    <div class="subsection-title">演进时间线</div>
    <div class="svg-wrap">
      <svg><!-- 时间线图 --></svg>
    </div>
  </div>
</div>
```

### 第 2 节：核心原理

**目的**：讲清楚"为什么能工作"。

**内容要素**：
- 核心概念解释（每个概念：定义 + 直觉类比 + 数学公式）
- 关键机制（如何运作，配原理示意图）
- 数学直觉（公式用 `.formula` 样式）

**必配图表**：原理示意图 SVG（至少 1 个）

**HTML 结构**：
```html
<div class="section" id="s2">
  <div class="section-title"><span class="num">2</span> 核心原理</div>
  <div class="section-desc">...</div>
  <div class="subsection" id="s2-1">
    <div class="subsection-title">2.1 概念名</div>
    <p>...</p>
    <div class="formula">公式</div>
    <div class="svg-wrap">
      <svg><!-- 原理图 --></svg>
    </div>
  </div>
</div>
```

### 第 3 节：完整流程

**目的**：展示端到端的数据流/处理管线。

**内容要素**：
- 流程概述（输入 → 处理 → 输出）
- 每步的数据变化（维度、格式、含义）
- 关键决策点

**必配图表**：流程图 SVG（带维度标注）

**HTML 结构**：
```html
<div class="section" id="s3">
  <div class="section-title"><span class="num">3</span> 完整流程</div>
  <div class="section-desc">...</div>
  <div class="svg-wrap">
    <svg><!-- 流程图 --></svg>
  </div>
  <div class="table-wrap">
    <table><!-- 每步数据变化表 --></table>
  </div>
</div>
```

### 第 4 节：模块详解

**目的**：拆解每个核心模块的作用和原理。

**内容要素**：
- 每个模块：定义 + 作用 + 原理 + 变体
- 模块间的协作关系
- 每个模块配结构图

**必配图表**：每个模块一个结构图 SVG

**HTML 结构**：
```html
<div class="section" id="s4">
  <div class="section-title"><span class="num">4</span> 模块详解</div>
  <div class="section-desc">...</div>
  <div class="subsection" id="s4-1">
    <div class="subsection-title">4.1 模块名</div>
    <p>...</p>
    <div class="svg-wrap">
      <svg><!-- 结构图 --></svg>
    </div>
  </div>
  <!-- 更多模块... -->
</div>
```

### 第 5 节：框架/实现详解

**目的**：对比主要实现方案，展示架构细节。

**内容要素**：
- 每个框架/方案：核心创新 + 架构细节 + 关键数据 + 适用场景
- 框架间对比

**必配图表**：架构图 SVG + 折叠面板

**HTML 结构**：
```html
<div class="section" id="s5">
  <div class="section-title"><span class="num">5</span> 框架详解</div>
  <div class="section-desc">...</div>

  <!-- 折叠面板 -->
  <div class="collapse-header" onclick="toggleCollapse(this)">
    <h4>框架名</h4>
    <span class="arrow">▼</span>
  </div>
  <div class="collapse-body">
    <div class="collapse-inner">
      <div class="svg-wrap">
        <svg><!-- 架构图 --></svg>
      </div>
      <p>...</p>
      <div class="table-wrap">
        <table><!-- 关键数据 --></table>
      </div>
    </div>
  </div>
</div>
```

### 第 6 节：场景应用

**目的**：展示实际应用场景。

**内容要素**：
- 每个场景：描述 + 典型方法 + 效果
- 应用卡片布局

**必配图表**：应用卡片（grid3 布局）

**HTML 结构**：
```html
<div class="section" id="s6">
  <div class="section-title"><span class="num">6</span> 场景应用</div>
  <div class="section-desc">...</div>
  <div class="grid3">
    <div class="card">
      <h4>场景名</h4>
      <p>描述</p>
    </div>
    <!-- 更多卡片... -->
  </div>
</div>
```

### 第 7 节：难点与解决方案

**目的**：列出常见挑战和经典解决方案。

**内容要素**：
- 难点 → 解决方案 对应关系
- 对比表格

**必配图表**：对比表格

**HTML 结构**：
```html
<div class="section" id="s7">
  <div class="section-title"><span class="num">7</span> 难点与解决方案</div>
  <div class="section-desc">...</div>
  <div class="table-wrap">
    <table>
      <tr><th>难点</th><th>原因</th><th>解决方案</th><th>代表工作</th></tr>
      <!-- 数据行 -->
    </table>
  </div>
</div>
```

### 第 8 节：优劣势与展望

**目的**：客观评价，展望未来。

**内容要素**：
- 优势 vs 劣势（双栏布局）
- 横向对比表
- 未来方向

**必配图表**：优劣势双栏 + 对比表格

**HTML 结构**：
```html
<div class="section" id="s8">
  <div class="section-title"><span class="num">8</span> 优劣势与展望</div>
  <div class="section-desc">...</div>
  <div class="pros-cons">
    <div class="pros"><h5>优势</h5><ul>...</ul></div>
    <div class="cons"><h5>劣势</h5><ul>...</ul></div>
  </div>
  <div class="table-wrap">
    <table><!-- 横向对比 --></table>
  </div>
  <div class="subsection">
    <div class="subsection-title">未来方向</div>
    <div class="highlight"><h5>...</h5><p>...</p></div>
  </div>
</div>
```

## 动态调整规则

| 条件 | 调整 |
|------|------|
| 源文件 < 3 个 | 合并第 4、5 节为"模块与框架" |
| 源文件 > 10 个 | 第 5 节拆分为多节（按类别分组） |
| 代码为主 | 增加"架构设计"和"API 接口"章节 |
| 数据为主 | 增加"数据结构"和"统计分析"章节 |
| depth: brief | 仅保留 1/2/3/5/8 五节 |
| depth: deep | 增加"数学推导"和"实验复现"章节 |

## 导航栏生成规则

根据实际章节结构动态生成导航链接：
- 主章节：`<a href="#sN">N. 章节名</a>`
- 子章节：`<a class="sub" href="#sN-M">N.M 子章节名</a>`
