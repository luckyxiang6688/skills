# 通俗易懂解读 — 浅色主题 HTML/CSS 样式模板

> **强制粘贴规则**：以下 CSS 和 JS 是固定模板，生成 HTML 时必须**完整原样粘贴**到 `<style>` 和 `<script>` 标签中。
> - 禁止修改任何变量值、颜色、字号、间距
> - 禁止新增 CSS 类名或规则
> - 禁止替换为深色主题
> - 禁止省略任何规则
> - 如果觉得某处样式不合适，那是规范问题，不是执行时可以自行修改的

## 设计理念

- **浅色主题**：白/灰底 + 蓝/绿/紫/橙/红/青 6 色强调色系
- **左侧导航 + 主内容区**：固定左侧导航栏 + 右侧可滚动内容区（参考 deepreport 布局，保持浅色风格）
- **类比优先**：.analogy 和 .key-point 是核心特色组件
- **解释性 SVG**：浅色填充 + 深色描边（与 deepreport 的深色填充 + 浅色描边相反）
- **口语化排版**：宽松行高、大字号、卡片阴影

## 完整 CSS

```css
:root {
  --bg: #fafbfc;
  --bg2: #ffffff;
  --bg3: #f0f4f8;
  --bg4: #e8edf2;
  --text: #1a202c;
  --text2: #4a5568;
  --text3: #718096;
  --accent: #2b6cb0;
  --accent2: #2f855a;
  --accent3: #6b46c1;
  --accent4: #c05621;
  --accent5: #c53030;
  --accent6: #2c7a7b;
  --border: #e2e8f0;
  --shadow: 0 2px 8px rgba(0,0,0,0.08);
  --radius: 12px;
  --nav-width: 260px;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif; line-height:1.8; font-size:16px; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }

/* 左侧导航栏 */
.nav { position:fixed; top:0; left:0; width:var(--nav-width); height:100vh; background:var(--bg2); border-right:1px solid var(--border); padding:24px 0; overflow-y:auto; z-index:100; }
.nav h2 { font-size:16px; padding:0 20px 16px; color:var(--accent); letter-spacing:1px; font-weight:700; border-bottom:1px solid var(--border); margin-bottom:8px; }
.nav a { display:block; padding:8px 20px; color:var(--text3); font-size:14px; transition:all .2s; border-left:3px solid transparent; text-decoration:none; }
.nav a:hover { color:var(--accent); background:rgba(43,108,176,.06); border-left-color:var(--accent); text-decoration:none; }
.nav a.active { color:var(--accent); background:rgba(43,108,176,.08); border-left-color:var(--accent); font-weight:600; }
.nav .sub { padding-left:36px; font-size:13px; }

/* 主内容区 */
.main { margin-left:var(--nav-width); padding:0 48px 80px; max-width:960px; }

.hero {
  text-align:center; padding:64px 0 48px;
  background: linear-gradient(135deg, #ebf4ff 0%, #f0fff4 50%, #faf5ff 100%);
  margin-bottom:40px; border-radius:0 0 32px 32px;
}
.hero h1 { font-size:36px; font-weight:800; margin-bottom:12px; color:var(--text); }
.hero .subtitle { color:var(--text2); font-size:18px; max-width:640px; margin:0 auto; line-height:1.6; }
.hero .tagline { margin-top:16px; color:var(--accent); font-size:14px; font-weight:600; letter-spacing:2px; text-transform:uppercase; }

.section { margin-bottom:56px; scroll-margin-top:24px; }
.section-title {
  font-size:26px; font-weight:800; margin-bottom:24px; padding-bottom:12px;
  border-bottom:3px solid var(--accent); display:flex; align-items:center; gap:12px;
}
.section-num {
  background:var(--accent); color:#fff; width:36px; height:36px; border-radius:50%;
  display:inline-flex; align-items:center; justify-content:center; font-size:16px; font-weight:700; flex-shrink:0;
}

.subsection { margin:28px 0 20px; }
.subsection-title { font-size:20px; font-weight:700; color:var(--accent); margin-bottom:12px; }

p { margin:10px 0; text-align:justify; }

/* 类比块 — 核心特色组件 */
.analogy {
  background:linear-gradient(135deg, #ebf8ff, #f0fff4);
  border-left:4px solid var(--accent6);
  padding:16px 20px; border-radius:0 var(--radius) var(--radius) 0;
  margin:16px 0; font-size:15px; color:var(--text2); line-height:1.8;
}
.analogy::before { content:'💡 通俗理解：'; color:var(--accent6); font-weight:700; }

/* 关键要点块 */
.key-point {
  background:#fffff0; border-left:4px solid var(--accent4);
  padding:14px 20px; border-radius:0 var(--radius) var(--radius) 0;
  margin:16px 0; font-size:15px; color:var(--text2);
}
.key-point::before { content:'🔑 关键要点：'; color:var(--accent4); font-weight:700; }

/* 表格 */
.table-wrap { overflow-x:auto; margin:16px 0; border-radius:var(--radius); border:1px solid var(--border); background:var(--bg2); }
table { width:100%; border-collapse:collapse; font-size:14px; }
th { background:var(--bg3); color:var(--accent); padding:12px 16px; text-align:left; font-weight:700; border-bottom:2px solid var(--border); }
td { padding:10px 16px; border-bottom:1px solid var(--border); }
tr:last-child td { border-bottom:none; }
tr:hover td { background:var(--bg3); }

/* SVG 容器 */
.svg-wrap { margin:24px 0; text-align:center; }
.svg-wrap svg { max-width:100%; height:auto; }
.svg-caption { color:var(--text3); font-size:13px; margin-top:8px; font-style:italic; }

/* 卡片网格 */
.card-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); gap:16px; margin:20px 0; }
.card { background:var(--bg2); border:1px solid var(--border); border-radius:var(--radius); padding:20px; box-shadow:var(--shadow); }
.card h4 { color:var(--accent); font-size:16px; margin-bottom:8px; }
.card p { font-size:14px; color:var(--text2); margin:4px 0; line-height:1.7; }

/* 优缺点双栏 */
.pros-cons { display:grid; grid-template-columns:1fr 1fr; gap:20px; margin:20px 0; }
.pros-cons>div { background:var(--bg2); border:1px solid var(--border); border-radius:var(--radius); padding:20px; box-shadow:var(--shadow); }
.pros-cons h4 { margin-bottom:12px; font-size:18px; }
.pros-cons .pro h4 { color:var(--accent2); }
.pros-cons .con h4 { color:var(--accent5); }
.pros-cons li { font-size:14px; margin:6px 0; color:var(--text2); line-height:1.7; }

/* 彩色标签 */
.tag { display:inline-block; padding:3px 10px; border-radius:16px; font-size:12px; font-weight:600; margin:2px; }
.tag-blue { background:rgba(43,108,176,0.1); color:var(--accent); }
.tag-green { background:rgba(47,133,90,0.1); color:var(--accent2); }
.tag-purple { background:rgba(107,70,193,0.1); color:var(--accent3); }
.tag-orange { background:rgba(192,86,33,0.1); color:var(--accent4); }
.tag-red { background:rgba(197,48,48,0.1); color:var(--accent5); }
.tag-teal { background:rgba(44,122,123,0.1); color:var(--accent6); }

/* 统计数字行 */
.stat-row { display:flex; gap:16px; flex-wrap:wrap; margin:20px 0; }
.stat-box { background:var(--bg2); border:1px solid var(--border); border-radius:var(--radius); padding:20px 28px; text-align:center; flex:1; min-width:120px; box-shadow:var(--shadow); }
.stat-box .num { font-size:32px; font-weight:800; color:var(--accent); }
.stat-box .label { font-size:13px; color:var(--text3); margin-top:4px; }

/* 场景卡片网格 */
.scenario-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:16px; margin:20px 0; }
.scenario-card { background:var(--bg2); border:1px solid var(--border); border-radius:var(--radius); padding:20px; text-align:center; box-shadow:var(--shadow); transition:transform 0.2s; }
.scenario-card:hover { transform:translateY(-2px); }
.scenario-card .icon { font-size:40px; margin-bottom:8px; }
.scenario-card h4 { color:var(--accent); font-size:15px; margin-bottom:6px; }
.scenario-card p { font-size:13px; color:var(--text3); margin:0; }

/* 编号示例步骤 */
.example-box {
  background:var(--bg2); border:1px solid var(--border); border-radius:var(--radius);
  padding:24px; margin:20px 0; box-shadow:var(--shadow);
}
.example-box h4 { color:var(--accent3); font-size:16px; margin-bottom:12px; }
.example-box .step { display:flex; gap:12px; margin:10px 0; align-items:flex-start; }
.example-box .step-num { background:var(--accent3); color:#fff; width:24px; height:24px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:700; flex-shrink:0; margin-top:2px; }
.example-box .step-text { font-size:14px; color:var(--text2); line-height:1.7; }

/* 页脚 */
.footer { text-align:center; padding:40px 0 24px; color:var(--text3); font-size:13px; border-top:1px solid var(--border); margin-top:48px; }

/* 响应式 */
@media(max-width:900px) {
  .nav { display:none; }
  .main { margin-left:0; padding:0 16px 80px; }
  .hero h1 { font-size:24px; }
  .pros-cons { grid-template-columns:1fr; }
  .section-title { font-size:20px; }
}

/* 滚动条美化 */
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:var(--bg3); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
```

## 完整 JS

```javascript
// 导航栏高亮 — 滚动时自动激活当前节
const sections = document.querySelectorAll('.section');
const navLinks = document.querySelectorAll('.nav a');
window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(s => {
    const top = s.offsetTop - 100;
    if (window.scrollY >= top) current = s.id;
  });
  navLinks.forEach(a => {
    a.classList.remove('active');
    if (a.getAttribute('href') === '#' + current) a.classList.add('active');
  });
});

// 导航栏平滑滚动
navLinks.forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(a.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});
```

## 完整 HTML 骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{主题} — 通俗易懂全解读</title>
<style>
/* 上述完整 CSS 粘贴于此 */
</style>
</head>
<body>

<!-- 左侧导航栏 -->
<nav class="nav" id="nav">
  <h2>{报告短标题}</h2>
  <a href="#s1">1. {主题} 是什么？</a>
  <a href="#s2">2. 支持哪些能力？</a>
  <a href="#s3">3. {主题} 怎么做的？</a>
  <a href="#s3-1" class="sub">3.1 整体架构</a>
  <a href="#s3-2" class="sub">3.2 {机制名}</a>
  <a href="#s4">4. 举例说明</a>
  <a href="#s5">5. 效果怎么样？</a>
  <a href="#s6">6. 解决了哪些痛点？</a>
  <a href="#s7">7. 目前还有哪些问题？</a>
  <a href="#s8">8. 主要应用场景</a>
  <a href="#s9">9. 一图总结</a>
</nav>

<!-- 主内容区 -->
<div class="main">

  <!-- Hero -->
  <div class="hero">
    <div class="tagline">{英文标签/分类}</div>
    <h1>{主题标题}</h1>
    <p class="subtitle">{一句话描述——让读者用最快速度知道这是关于什么的}</p>
  </div>

  <!-- 第 1 节：是什么？ -->
  <div class="section" id="s1">
    <div class="section-title"><span class="section-num">1</span> {主题} 是什么？</div>
    <!-- 按 section-schema.md 第1节规范填充 -->
  </div>

  <!-- 第 2 节：支持哪些能力？ -->
  <div class="section" id="s2">
    <div class="section-title"><span class="section-num">2</span> 支持哪些能力？</div>
    <!-- 按 section-schema.md 第2节规范填充 -->
  </div>

  <!-- 第 3 节：怎么做？ -->
  <div class="section" id="s3">
    <div class="section-title"><span class="section-num">3</span> {主题} 怎么做的？</div>
    <div class="subsection" id="s3-1">
      <div class="subsection-title">3.1 整体架构</div>
      <!-- 按 section-schema.md 第3节规范填充 -->
    </div>
    <div class="subsection" id="s3-2">
      <div class="subsection-title">3.2 {机制名}</div>
      <!-- 按素材内容生成更多子节 -->
    </div>
  </div>

  <!-- 第 4 节：举例说明 -->
  <div class="section" id="s4">
    <div class="section-title"><span class="section-num">4</span> 举例说明</div>
    <!-- 按 section-schema.md 第4节规范填充 -->
  </div>

  <!-- 第 5 节：效果怎么样？ -->
  <div class="section" id="s5">
    <div class="section-title"><span class="section-num">5</span> 效果怎么样？</div>
    <!-- 按 section-schema.md 第5节规范填充 -->
  </div>

  <!-- 第 6 节：解决了哪些痛点？ -->
  <div class="section" id="s6">
    <div class="section-title"><span class="section-num">6</span> 解决了哪些痛点？</div>
    <!-- 按 section-schema.md 第6节规范填充 -->
  </div>

  <!-- 第 7 节：目前还有哪些问题？ -->
  <div class="section" id="s7">
    <div class="section-title"><span class="section-num">7</span> 目前还有哪些问题？</div>
    <!-- 按 section-schema.md 第7节规范填充 -->
  </div>

  <!-- 第 8 节：主要应用场景 -->
  <div class="section" id="s8">
    <div class="section-title"><span class="section-num">8</span> 主要应用场景</div>
    <!-- 按 section-schema.md 第8节规范填充 -->
  </div>

  <!-- 第 9 节：一图总结 -->
  <div class="section" id="s9">
    <div class="section-title"><span class="section-num">9</span> 一图总结</div>
    <!-- 按 section-schema.md 第9节规范填充 -->
  </div>

  <!-- 页脚 -->
  <div class="footer">
    <p>基于 {素材来源描述} | 内容零幻觉</p>
  </div>

</div><!-- end main -->

<script>
/* 上述完整 JS 粘贴于此 */
</script>
</body>
</html>
```

## 与 deepreport 样式的关键差异

| 组件 | deepreport（深色） | plainreport（浅色） |
|------|-------------------|-------------------|
| 背景 | #0f1117 深黑 | #fafbfc 浅灰白 |
| 导航 | 左侧固定导航栏（深色） | 左侧固定导航栏（白色背景） |
| 主题色 | 霓虹蓝/绿 | 蓝/绿/紫/橙/红/青 6色 |
| 类比块 | 无 | .analogy（蓝绿渐变+青色左边框） |
| 关键要点 | 无 | .key-point（黄色+橙色左边框） |
| 统计行 | 无 | .stat-row（大数字+标签） |
| 场景卡片 | 无 | .scenario-grid（emoji+标题+描述） |
| 示例步骤 | 无 | .example-box（编号圆+步骤文本） |
| 优缺点 | 无 | .pros-cons（双栏对比） |
| SVG 填充 | 深色底+浅色框 | 浅色底+深色框 |
| SVG 描边 | 浅色 | 深色 |
| 代码块 | 有 | 无 |
| 公式块 | 有 | 无 |
| 折叠面板 | 有 | 无 |
| 时间线 | 有 | 无 |
