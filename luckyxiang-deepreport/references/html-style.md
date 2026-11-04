# HTML/CSS 样式模板

> 从 CNN 深度分析报告提取的完整样式系统。生成报告时必须严格使用此样式。

## 完整 CSS

```css
:root {
  --bg: #0f1117;
  --bg2: #161822;
  --bg3: #1e2030;
  --card: #1a1d2e;
  --border: #2a2d42;
  --text: #e0e0e8;
  --text2: #9ca0b0;
  --accent: #6c8cff;
  --accent2: #a78bfa;
  --accent3: #34d399;
  --accent4: #f59e0b;
  --accent5: #f472b6;
  --accent6: #22d3ee;
  --grad1: linear-gradient(135deg, #6c8cff, #a78bfa);
  --grad2: linear-gradient(135deg, #34d399, #22d3ee);
  --grad3: linear-gradient(135deg, #f59e0b, #f472b6);
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: -apple-system, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: var(--bg); color: var(--text); line-height: 1.8; }
a { color: var(--accent); text-decoration: none; }

/* Nav */
.nav { position: fixed; top:0; left:0; width:260px; height:100vh; background: var(--bg2); border-right:1px solid var(--border); padding:24px 0; overflow-y:auto; z-index:100; }
.nav h2 { font-size:18px; padding:0 24px 16px; color: var(--accent); letter-spacing:1px; }
.nav a { display:block; padding:8px 24px; color:var(--text2); font-size:14px; transition: all .2s; border-left:3px solid transparent; }
.nav a:hover, .nav a.active { color:var(--accent); background:rgba(108,140,255,.08); border-left-color:var(--accent); }
.nav .sub { padding-left:40px; font-size:13px; }

/* Main */
.main { margin-left:260px; padding:40px 60px 80px; max-width:1100px; }
.hero { text-align:center; padding:60px 0 40px; }
.hero h1 { font-size:42px; background: var(--grad1); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:12px; }
.hero p { color:var(--text2); font-size:18px; max-width:700px; margin:0 auto; }

.section { margin-bottom:64px; scroll-margin-top:24px; }
.section-title { font-size:28px; font-weight:700; margin-bottom:8px; display:flex; align-items:center; gap:12px; }
.section-title .num { display:inline-flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:10px; background:var(--grad1); color:#fff; font-size:16px; font-weight:700; flex-shrink:0; }
.section-desc { color:var(--text2); font-size:15px; margin-bottom:32px; padding-left:48px; }

.subsection { margin-bottom:40px; }
.subsection-title { font-size:20px; font-weight:600; margin-bottom:16px; color:var(--accent); padding-left:16px; border-left:3px solid var(--accent); }

/* Cards */
.card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:24px; margin-bottom:20px; }
.card h4 { font-size:16px; margin-bottom:8px; color:var(--accent); }
.card p { color:var(--text2); font-size:14px; }

/* Grid */
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:20px; }

/* SVG container */
.svg-wrap { background:var(--bg3); border:1px solid var(--border); border-radius:12px; padding:24px; margin:20px 0; overflow-x:auto; text-align:center; }
.svg-wrap svg { max-width:100%; height:auto; }
.svg-caption { text-align:center; color:var(--text2); font-size:13px; margin-top:8px; }

/* Table */
.table-wrap { overflow-x:auto; margin:16px 0; }
table { width:100%; border-collapse:collapse; font-size:14px; }
th { background:var(--bg3); color:var(--accent); padding:12px 16px; text-align:left; font-weight:600; border-bottom:2px solid var(--border); }
td { padding:10px 16px; border-bottom:1px solid var(--border); color:var(--text2); }
tr:hover td { background:rgba(108,140,255,.04); }

/* Formula */
.formula { background:var(--bg3); border:1px solid var(--border); border-radius:8px; padding:16px 24px; margin:12px 0; font-family:'Courier New',monospace; font-size:15px; color:var(--accent3); text-align:center; }

/* Tag */
.tag { display:inline-block; padding:2px 10px; border-radius:12px; font-size:12px; font-weight:600; }
.tag-blue { background:rgba(108,140,255,.15); color:var(--accent); }
.tag-green { background:rgba(52,211,153,.15); color:var(--accent3); }
.tag-yellow { background:rgba(245,158,11,.15); color:var(--accent4); }
.tag-pink { background:rgba(244,114,182,.15); color:var(--accent5); }

/* Collapsible */
.collapse-header { display:flex; align-items:center; justify-content:space-between; padding:16px 20px; background:var(--card); border:1px solid var(--border); border-radius:10px; cursor:pointer; margin-bottom:8px; transition:all .2s; }
.collapse-header:hover { border-color:var(--accent); }
.collapse-header h4 { margin:0; font-size:16px; }
.collapse-header .arrow { transition:transform .3s; color:var(--text2); font-size:14px; }
.collapse-header.open .arrow { transform:rotate(180deg); }
.collapse-body { max-height:0; overflow:hidden; transition:max-height .4s ease; }
.collapse-body.open { max-height:3000px; }
.collapse-inner { padding:16px 20px; background:var(--bg3); border:1px solid var(--border); border-top:none; border-radius:0 0 10px 10px; margin-top:-8px; margin-bottom:16px; }

/* Pros/Cons */
.pros-cons { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.pros, .cons { padding:20px; border-radius:10px; }
.pros { background:rgba(52,211,153,.06); border:1px solid rgba(52,211,153,.2); }
.cons { background:rgba(244,114,182,.06); border:1px solid rgba(244,114,182,.2); }
.pros h5 { color:var(--accent3); margin-bottom:8px; }
.cons h5 { color:var(--accent5); margin-bottom:8px; }
.pros li, .cons li { font-size:14px; color:var(--text2); margin-bottom:4px; }

/* Timeline */
.timeline { position:relative; padding-left:32px; }
.timeline::before { content:''; position:absolute; left:12px; top:0; bottom:0; width:2px; background:var(--grad1); }
.timeline-item { position:relative; margin-bottom:28px; }
.timeline-item::before { content:''; position:absolute; left:-24px; top:6px; width:12px; height:12px; border-radius:50%; background:var(--accent); box-shadow:0 0 12px rgba(108,140,255,.4); }
.timeline-item .year { font-size:13px; color:var(--accent); font-weight:700; }
.timeline-item .title { font-size:16px; font-weight:600; margin:2px 0; }
.timeline-item .desc { font-size:13px; color:var(--text2); }

/* Highlight box */
.highlight { background:linear-gradient(135deg, rgba(108,140,255,.08), rgba(167,139,250,.08)); border:1px solid rgba(108,140,255,.2); border-radius:10px; padding:20px; margin:16px 0; }
.highlight h5 { color:var(--accent2); margin-bottom:8px; }

/* Responsive */
@media(max-width:900px) {
  .nav { display:none; }
  .main { margin-left:0; padding:20px; }
  .grid2, .grid3, .pros-cons { grid-template-columns:1fr; }
  .hero h1 { font-size:28px; }
}

/* Scrollbar */
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:var(--bg2); }
::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
```

## 完整 JS

```javascript
// Collapsible sections
function toggleCollapse(el) {
  el.classList.toggle('open');
  const body = el.nextElementSibling;
  body.classList.toggle('open');
}

// Nav active state
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

// Smooth scroll
navLinks.forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(a.getAttribute('href'));
    if (target) target.scrollIntoView({ behavior: 'smooth' });
  });
});
```

## HTML 骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{报告标题}} — 深度专业分析</title>
<style>
/* 完整 CSS 如上 */
</style>
</head>
<body>

<!-- Nav -->
<nav class="nav" id="nav">
  <h2>{{报告短标题}}</h2>
  <!-- 目录链接由报告结构动态生成 -->
</nav>

<!-- Main Content -->
<div class="main">

<!-- Hero -->
<div class="hero">
  <h1>{{报告主标题}}</h1>
  <p>{{一句话描述}}</p>
</div>

<!-- Sections（按 report-schema.md 的结构生成）-->

<!-- Footer -->
<div style="text-align:center; padding:40px 0 20px; color:var(--text2); font-size:13px; border-top:1px solid var(--border); margin-top:40px;">
  <p>{{报告标题}} 深度专业分析 | 基于素材来源</p>
</div>

</div><!-- end main -->

<script>
/* 完整 JS 如上 */
</script>
</body>
</html>
```
