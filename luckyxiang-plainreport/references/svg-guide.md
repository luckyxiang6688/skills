# 通俗易懂解读 — 解释性 SVG 图表绘制指南

## 设计理念

- **解释性而非文档性**：SVG 图表的目的是"让读者看懂原理"，不是"记录技术细节"
- **浅色主题**：浅色填充 + 深色描边（与 deepreport 的深色填充 + 浅色描边相反）
- **类比可视化**：图表中的标签尽量用类比语言，不用技术术语
- **颜色编码**：6 色强调色系（蓝/绿/紫/橙/红/青），每层一个颜色
- **流程箭头**：所有数据/控制流用箭头标明方向

## 配色规则

| 用途 | 颜色 | CSS 变量 | 填充示例 | 描边示例 |
|------|------|---------|---------|---------|
| 蓝色层 | #2b6cb0 | --accent | #ebf8ff | #2b6cb0 |
| 绿色层 | #2f855a | --accent2 | #f0fff4 | #2f855a |
| 紫色层 | #6b46c1 | --accent3 | #faf5ff | #6b46c1 |
| 橙色层 | #c05621 | --accent4 | #fffff0 | #c05621 |
| 红色层 | #c53030 | --accent5 | #fff5f5 | #c53030 |
| 青色层 | #2c7a7b | --accent6 | #e6fffa | #2c7a7b |
| 灰色辅助 | #718096 | --text3 | #e8edf2 | #718096 |
| 渐变标题 | 蓝→绿 | — | url(#headerGrad) | — |

**规则**：
- 层/区域背景：浅色填充（如 #ebf8ff）
- 内部框：白色填充 + 对应色描边
- 文字：深色（对应色或 #4a5568）
- 箭头：灰色（#718096）或对应色
- 标题栏：渐变填充（蓝→绿）

## 6 类解释性 SVG 模板

### 模板 1：分层架构图

**用途**：展示系统/产品的分层结构（如传感器→驱动→核心→执行）

**布局**：垂直堆叠的彩色层带，每层内含白色功能框

**SVG 骨架**：
```svg
<svg viewBox="0 0 860 480" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="headerGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2b6cb0"/>
      <stop offset="100%" stop-color="#2f855a"/>
    </linearGradient>
    <marker id="arrowG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#718096"/>
    </marker>
  </defs>

  <!-- 标题栏 -->
  <rect x="0" y="0" width="860" height="40" rx="8" fill="url(#headerGrad)"/>
  <text x="430" y="27" text-anchor="middle" fill="#fff" font-size="16" font-weight="700">{架构标题}</text>

  <!-- 第1层（蓝色） -->
  <rect x="20" y="56" width="820" height="64" rx="10" fill="#ebf8ff" stroke="#2b6cb0" stroke-width="1.5"/>
  <text x="40" y="78" fill="#2b6cb0" font-size="13" font-weight="700">{层名}</text>
  <rect x="120" y="64" width="100" height="40" rx="6" fill="#fff" stroke="#2b6cb0" stroke-width="1"/>
  <text x="170" y="88" text-anchor="middle" fill="#2b6cb0" font-size="11" font-weight="600">{组件1}</text>
  <!-- 更多组件框... -->

  <!-- 层间箭头 -->
  <line x1="430" y1="120" x2="430" y2="140" stroke="#718096" stroke-width="1.5" marker-end="url(#arrowG)"/>

  <!-- 第2层（绿色） -->
  <!-- ... -->

  <!-- 第N层（橙色） -->
  <!-- ... -->
</svg>
```

**关键参数**：
- viewBox 宽度：860（适配 900px 容器）
- 层高度：64-100px（根据内容量调整）
- 层间距：20px（含箭头）
- 内部框：白色填充 + 对应色 1px 描边 + 6px 圆角
- 标题栏：渐变填充 + 白色文字

---

### 模板 2：数据流图（发布/订阅）

**用途**：展示模块间的数据交换关系（如 uORB 消息总线）

**布局**：左侧发布者 → 中间总线 → 右侧订阅者

**SVG 骨架**：
```svg
<svg viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg">
  <!-- 发布者框（左侧） -->
  <rect x="20" y="60" width="130" height="44" rx="8" fill="#ebf8ff" stroke="#2b6cb0" stroke-width="1.5"/>
  <text x="85" y="80" text-anchor="middle" fill="#2b6cb0" font-size="12" font-weight="600">{发布者1}</text>
  <text x="85" y="96" text-anchor="middle" fill="#718096" font-size="9">{发布内容}</text>

  <!-- 箭头到总线 -->
  <line x1="150" y1="82" x2="270" y2="120" stroke="#2b6cb0" stroke-width="1.5" marker-end="url(#arrowG)"/>

  <!-- 消息总线（中间，虚线边框） -->
  <rect x="270" y="60" width="260" height="180" rx="12" fill="#fffff0" stroke="#c05621" stroke-width="2" stroke-dasharray="8,4"/>
  <text x="400" y="88" text-anchor="middle" fill="#c05621" font-size="14" font-weight="700">{总线名称}</text>
  <!-- 频道列表 -->
  <rect x="290" y="100" width="220" height="22" rx="4" fill="#fff"/>
  <text x="400" y="115" text-anchor="middle" fill="#718096" font-size="10">{频道1}</text>

  <!-- 箭头到订阅者 -->
  <line x1="530" y1="111" x2="620" y2="82" stroke="#2b6cb0" stroke-width="1.5" marker-end="url(#arrowG)"/>

  <!-- 订阅者框（右侧） -->
  <rect x="620" y="60" width="160" height="44" rx="8" fill="#ebf8ff" stroke="#2b6cb0" stroke-width="1.5"/>
  <text x="700" y="80" text-anchor="middle" fill="#2b6cb0" font-size="12" font-weight="600">{订阅者1}</text>
  <text x="700" y="96" text-anchor="middle" fill="#718096" font-size="9">{订阅内容}</text>
</svg>
```

**关键参数**：
- 总线框：虚线描边（stroke-dasharray="8,4"）+ 浅黄填充
- 频道行：白色填充 + 灰色文字
- 箭头：对应色描边 + 灰色箭头

---

### 模板 3：融合/处理图

**用途**：展示多输入→中心处理→统一输出的过程（如 EKF2 传感器融合）

**布局**：左侧多输入 → 中间处理框 → 右侧统一输出

**SVG 骨架**：
```svg
<svg viewBox="0 0 820 340" xmlns="http://www.w3.org/2000/svg">
  <!-- 输入传感器（左侧，垂直排列） -->
  <rect x="10" y="50" width="120" height="40" rx="6" fill="#ebf8ff" stroke="#2b6cb0" stroke-width="1"/>
  <text x="70" y="74" text-anchor="middle" fill="#2b6cb0" font-size="11" font-weight="600">{输入1} (频率)</text>
  <!-- 更多输入... -->

  <!-- 箭头汇聚到中心 -->
  <line x1="130" y1="120" x2="240" y2="170" stroke="#718096" stroke-width="1" marker-end="url(#arrowG)"/>

  <!-- 中心处理框（紫色，大框） -->
  <rect x="240" y="130" width="200" height="150" rx="12" fill="#faf5ff" stroke="#6b46c1" stroke-width="2"/>
  <text x="340" y="158" text-anchor="middle" fill="#6b46c1" font-size="14" font-weight="700">{处理器名}</text>
  <text x="340" y="180" text-anchor="middle" fill="#718096" font-size="10">{处理步骤1}</text>
  <text x="340" y="198" text-anchor="middle" fill="#718096" font-size="10">{处理步骤2}</text>

  <!-- 箭头到输出 -->
  <line x1="440" y1="205" x2="520" y2="205" stroke="#6b46c1" stroke-width="2" marker-end="url(#arrowG)"/>

  <!-- 统一输出框（绿色） -->
  <rect x="520" y="110" width="280" height="190" rx="12" fill="#f0fff4" stroke="#2f855a" stroke-width="2"/>
  <text x="660" y="138" text-anchor="middle" fill="#2f855a" font-size="14" font-weight="700">{输出标题}</text>
  <rect x="540" y="150" width="240" height="24" rx="4" fill="#fff"/>
  <text x="660" y="166" text-anchor="middle" fill="#2b6cb0" font-size="11">{输出项1}</text>
</svg>
```

---

### 模板 4：级联/链图

**用途**：展示多级串联的处理链（如级联 PID 控制）

**布局**：水平排列的圆角矩形 + 层间箭头 + 底部反馈虚线

**SVG 骨架**：
```svg
<svg viewBox="0 0 820 280" xmlns="http://www.w3.org/2000/svg">
  <!-- 第1级（蓝色） -->
  <rect x="20" y="60" width="160" height="90" rx="10" fill="#ebf8ff" stroke="#2b6cb0" stroke-width="2"/>
  <text x="100" y="85" text-anchor="middle" fill="#2b6cb0" font-size="13" font-weight="700">{级1名}</text>
  <text x="100" y="105" text-anchor="middle" fill="#718096" font-size="10">"{类比描述}"</text>
  <text x="100" y="122" text-anchor="middle" fill="#718096" font-size="10">输入：{输入}</text>
  <text x="100" y="139" text-anchor="middle" fill="#2b6cb0" font-size="10" font-weight="600">输出：{输出}</text>

  <!-- 箭头 -->
  <line x1="180" y1="105" x2="220" y2="105" stroke="#2b6cb0" stroke-width="2" marker-end="url(#arrowG)"/>

  <!-- 第2级（绿色） -->
  <!-- ... -->

  <!-- 频率标签 -->
  <text x="100" y="168" text-anchor="middle" fill="#2b6cb0" font-size="11" font-weight="600">{频率}</text>

  <!-- 底部反馈虚线 -->
  <path d="M 705 150 L 705 210 L 100 210 L 100 150" fill="none" stroke="#718096" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="402" y="230" text-anchor="middle" fill="#718096" font-size="11">{反馈说明}</text>
</svg>
```

**关键参数**：
- 每级宽度：160px
- 级间距：60px（含箭头）
- 反馈路径：底部虚线弧
- 频率标签：级下方，对应色

---

### 模板 5：过渡/状态图

**用途**：展示状态之间的转换过程（如 VTOL 模式切换）

**布局**：药丸形状态框 + 方框过渡区 + 标签箭头

**SVG 骨架**：
```svg
<svg viewBox="0 0 820 200" xmlns="http://www.w3.org/2000/svg">
  <!-- 状态1（药丸形，蓝色） -->
  <rect x="20" y="60" width="140" height="60" rx="30" fill="#ebf8ff" stroke="#2b6cb0" stroke-width="2"/>
  <text x="90" y="86" text-anchor="middle" fill="#2b6cb0" font-size="13" font-weight="700">{状态1}</text>
  <text x="90" y="106" text-anchor="middle" fill="#718096" font-size="10">{权重}</text>

  <!-- 箭头+标签 -->
  <line x1="160" y1="90" x2="220" y2="90" stroke="#718096" stroke-width="1.5" marker-end="url(#arrowG)"/>
  <text x="190" y="80" text-anchor="middle" fill="#c05621" font-size="10">{触发条件}</text>

  <!-- 过渡区（方框，橙色） -->
  <rect x="220" y="50" width="200" height="80" rx="10" fill="#fffff0" stroke="#c05621" stroke-width="2"/>
  <text x="320" y="76" text-anchor="middle" fill="#c05621" font-size="13" font-weight="700">{过渡名}</text>
  <text x="320" y="96" text-anchor="middle" fill="#718096" font-size="10">{权重变化1}</text>
  <text x="320" y="114" text-anchor="middle" fill="#718096" font-size="10">{权重变化2}</text>

  <!-- 状态2（药丸形，绿色） -->
  <rect x="480" y="60" width="140" height="60" rx="30" fill="#f0fff4" stroke="#2f855a" stroke-width="2"/>
  <text x="550" y="86" text-anchor="middle" fill="#2f855a" font-size="13" font-weight="700">{状态2}</text>
  <text x="550" y="106" text-anchor="middle" fill="#718096" font-size="10">{权重}</text>
</svg>
```

**关键参数**：
- 稳定状态：药丸形（rx=30，高度一半），对应色填充
- 过渡区：方框（rx=10），橙色填充+描边
- 箭头标签：触发条件

---

### 模板 6：径向总结图

**用途**：第 9 节"一图总结"，中心主题 + 周围 7 框概括

**布局**：中心圆 + 上下左右 7 个信息框 + 连线

**SVG 骨架**：
```svg
<svg viewBox="0 0 820 420" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sumGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2b6cb0"/>
      <stop offset="50%" stop-color="#6b46c1"/>
      <stop offset="100%" stop-color="#2f855a"/>
    </linearGradient>
  </defs>

  <rect x="0" y="0" width="820" height="420" rx="16" fill="#f7fafc" stroke="#e2e8f0" stroke-width="2"/>

  <!-- 中心圆 -->
  <circle cx="410" cy="210" r="60" fill="url(#sumGrad)" opacity="0.9"/>
  <text x="410" y="200" text-anchor="middle" fill="#fff" font-size="18" font-weight="800">{主题}</text>
  <text x="410" y="222" text-anchor="middle" fill="#fff" font-size="12" font-weight="600">{副标题}</text>

  <!-- 上方框：是什么 -->
  <rect x="300" y="20" width="220" height="70" rx="10" fill="#ebf8ff" stroke="#2b6cb0" stroke-width="1.5"/>
  <text x="410" y="44" text-anchor="middle" fill="#2b6cb0" font-size="13" font-weight="700">是什么？</text>
  <text x="410" y="62" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <text x="410" y="78" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <line x1="410" y1="90" x2="410" y2="150" stroke="#2b6cb0" stroke-width="1.5"/>

  <!-- 左上框：支持哪些能力 -->
  <rect x="20" y="50" width="220" height="70" rx="10" fill="#e6fffa" stroke="#2c7a7b" stroke-width="1.5"/>
  <text x="130" y="74" text-anchor="middle" fill="#2c7a7b" font-size="13" font-weight="700">支持哪些能力？</text>
  <text x="130" y="92" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <text x="130" y="108" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <line x1="240" y1="100" x2="350" y2="180" stroke="#2c7a7b" stroke-width="1.5"/>

  <!-- 左侧框：怎么做 -->
  <rect x="20" y="180" width="220" height="80" rx="10" fill="#f0fff4" stroke="#2f855a" stroke-width="1.5"/>
  <text x="130" y="204" text-anchor="middle" fill="#2f855a" font-size="13" font-weight="700">怎么做？</text>
  <text x="130" y="222" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <text x="130" y="238" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <line x1="240" y1="220" x2="350" y2="220" stroke="#2f855a" stroke-width="1.5"/>

  <!-- 右侧框：效果如何 -->
  <rect x="580" y="180" width="220" height="80" rx="10" fill="#faf5ff" stroke="#6b46c1" stroke-width="1.5"/>
  <text x="690" y="204" text-anchor="middle" fill="#6b46c1" font-size="13" font-weight="700">效果如何？</text>
  <text x="690" y="222" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <text x="690" y="238" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <line x1="470" y1="220" x2="580" y2="220" stroke="#6b46c1" stroke-width="1.5"/>

  <!-- 左下框：解决什么痛点 -->
  <rect x="60" y="310" width="220" height="90" rx="10" fill="#fffff0" stroke="#c05621" stroke-width="1.5"/>
  <text x="170" y="334" text-anchor="middle" fill="#c05621" font-size="13" font-weight="700">解决什么痛点？</text>
  <text x="170" y="352" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <text x="170" y="368" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <line x1="280" y1="310" x2="380" y2="270" stroke="#c05621" stroke-width="1.5"/>

  <!-- 中下框：还有哪些问题 -->
  <rect x="300" y="310" width="220" height="90" rx="10" fill="#fff5f5" stroke="#c53030" stroke-width="1.5"/>
  <text x="410" y="334" text-anchor="middle" fill="#c53030" font-size="13" font-weight="700">还有哪些问题？</text>
  <text x="410" y="352" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <text x="410" y="368" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <line x1="410" y1="310" x2="410" y2="270" stroke="#c53030" stroke-width="1.5"/>

  <!-- 右下框：应用场景 -->
  <rect x="540" y="310" width="220" height="90" rx="10" fill="#e8edf2" stroke="#718096" stroke-width="1.5"/>
  <text x="650" y="334" text-anchor="middle" fill="#2c7a7b" font-size="13" font-weight="700">应用场景</text>
  <text x="650" y="352" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <text x="650" y="368" text-anchor="middle" fill="#4a5568" font-size="11">{精炼概括}</text>
  <line x1="540" y1="310" x2="440" y2="270" stroke="#718096" stroke-width="1.5"/>
</svg>
```

**关键参数**：
- 中心圆：r=60，渐变填充
- 周围框：220×70~90px，对应色填充+描边
- 连线：对应色，1.5px
- 每框 2-3 行精炼文字（11px）

## 通用 SVG 规范

### 箭头标记定义

每个 SVG 开头必须包含箭头标记定义：

```svg
<defs>
  <marker id="arrowG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#718096"/>
  </marker>
</defs>
```

如需彩色箭头，额外定义对应色标记。

### 字体

```css
font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;
```

### 尺寸规范

| 元素 | 字号 | 字重 |
|------|------|------|
| 图表标题 | 15-16px | 700 |
| 层名/框名 | 13-14px | 700 |
| 内部标签 | 11-12px | 600 |
| 说明文字 | 10-11px | 400 |
| 底部注释 | 11px | 400 |

### viewBox 标准

- 宽度：800-860px
- 高度：根据内容调整（200-480px）
- SVG 元素不加 width/height 属性，由 CSS `max-width:100%` 控制

### 圆角规范

| 元素 | 圆角 |
|------|------|
| 层/区域 | 10-12px |
| 内部框 | 6-8px |
| 状态药丸 | 30px（高度的一半） |
| 频道行 | 4px |
