/**
 * Tech Digest — GitHub Pages 前端逻辑
 * 从 ../data/feed.json 读取数据，渲染卡片
 */

const SOURCE_LABELS = {
  github:     { name: "GitHub",     icon: "🐙", cls: "source-github" },
  arxiv:      { name: "arXiv",      icon: "📄", cls: "source-arxiv" },
  hackernews: { name: "Hacker News",icon: "🔥", cls: "source-hackernews" },
  reddit:     { name: "Reddit",     icon: "🤖", cls: "source-reddit" },
  zhihu:      { name: "知乎",       icon: "💬", cls: "source-zhihu" },
};

let allItems = [];
let currentFilter = "all";

// ============================================
// 初始化
// ============================================
document.addEventListener("DOMContentLoaded", async () => {
  setupFilters();
  await loadData();
  render();
});

// ============================================
// 筛选按钮
// ============================================
function setupFilters() {
  const bar = document.getElementById("filter-bar");
  bar.addEventListener("click", (e) => {
    const btn = e.target.closest(".filter-btn");
    if (!btn) return;
    currentFilter = btn.dataset.source;
    bar.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    render();
  });
}

// ============================================
// 加载数据
// ============================================
async function loadData() {
  try {
    const resp = await fetch("data/feed.json");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    allItems = data.items || [];

    // 更新时间
    const el = document.getElementById("update-time");
    if (data.updated_at) {
      const d = new Date(data.updated_at);
      el.textContent = `🕐 最后更新: ${d.toLocaleString("zh-CN")}`;
    }
  } catch (err) {
    console.error("加载 feed.json 失败:", err);
    document.getElementById("feed-list").innerHTML = `
      <div class="empty-state">
        <div class="icon">📭</div>
        <p>暂无数据</p>
        <p style="font-size:12px;color:#bbb">请先运行爬虫生成 data/feed.json</p>
      </div>`;
  }
}

// ============================================
// 渲染
// ============================================
function render() {
  const filtered = currentFilter === "all"
    ? allItems
    : allItems.filter(it => it.source === currentFilter);

  // 统计
  document.getElementById("stats").textContent =
    `共 ${filtered.length} 条${currentFilter === "all" ? "" : " · 筛选: " + (SOURCE_LABELS[currentFilter]?.name || currentFilter)}`;

  // 卡片
  const list = document.getElementById("feed-list");
  if (!filtered.length) {
    list.innerHTML = `<div class="empty-state"><div class="icon">🔍</div><p>该分类下暂无内容</p></div>`;
    return;
  }

  list.innerHTML = filtered.map(item => buildCard(item)).join("");
}

// ============================================
// 构建单张卡片
// ============================================
function buildCard(item) {
  const src = SOURCE_LABELS[item.source] || { name: item.source, icon: "📌", cls: "" };
  const extra = item.extra || {};

  // 元数据标签
  let metaHtml = "";
  if (extra.stars)    metaHtml += `<span>⭐ ${fmtNum(extra.stars)}</span>`;
  if (extra.language) metaHtml += `<span class="tag">${escHtml(extra.language)}</span>`;
  if (extra.score)    metaHtml += `<span>👍 ${fmtNum(extra.score)}</span>`;
  if (extra.comments) metaHtml += `<span>💬 ${fmtNum(extra.comments)}</span>`;
  if (extra.hot_score)metaHtml += `<span>🔥 ${escHtml(String(extra.hot_score))}</span>`;
  if (extra.subreddit)metaHtml += `<span class="tag">${escHtml(extra.subreddit)}</span>`;
  if (extra.by)       metaHtml += `<span>👤 ${escHtml(extra.by)}</span>`;
  if (extra.authors && extra.authors.length) {
    metaHtml += `<span>👥 ${escHtml(extra.authors.slice(0, 2).join(", "))}</span>`;
  }

  const summary = item.summary || item.description || "";

  return `
    <article class="card" data-id="${escHtml(item.id)}">
      <div class="card-header">
        <span class="source-badge ${src.cls}">${src.icon} ${src.name}</span>
      </div>
      <h2 class="card-title">
        <a href="${escHtml(item.url)}" target="_blank" rel="noopener">${escHtml(item.title)}</a>
      </h2>
      ${summary ? `<p class="card-summary">${escHtml(summary)}</p>` : ""}
      ${metaHtml ? `<div class="card-meta">${metaHtml}</div>` : ""}
    </article>`;
}

// ============================================
// 工具函数
// ============================================
function escHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function fmtNum(n) {
  if (n >= 10000) return (n / 1000).toFixed(1) + "k";
  if (n >= 1000)  return (n / 1000).toFixed(1) + "k";
  return String(n);
}
