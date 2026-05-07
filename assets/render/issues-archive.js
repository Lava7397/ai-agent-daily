// 所有归档数据（按日期降序）: [date_str, headline, total_items]
const ALL_ARCHIVES = __ALL_ARCHIVES_JSON__;

const PER_PAGE = __PER_PAGE__;
const totalPages = Math.max(1, Math.ceil(ALL_ARCHIVES.length / PER_PAGE));

function renderPage(p) {
  p = Math.max(1, Math.min(p, totalPages));
  const start = (p - 1) * PER_PAGE;
  const end = start + PER_PAGE;
  const pageItems = ALL_ARCHIVES.slice(start, end);

  const dayNames = ['周日','周一','周二','周三','周四','周五','周六'];
  const listEl = document.getElementById('archiveList');
  listEl.innerHTML = pageItems.map(([d, headline, total, summary]) => {
    const dn = dayNames[new Date(d + 'T00:00:00').getDay()];
    const n = total ? (parseInt(total, 10) || 0) : 0;
    const rightInner = n > 0
      ? `<span class="date-arrow-stack" aria-label="${n} 条内容" title="${n} 条内容"><span class="date-count-num">${n}</span><span class="date-arrow" aria-hidden="true">→</span></span>`
      : `<span class="date-arrow-stack date-arrow-stack--empty" aria-hidden="true"><span class="date-arrow">→</span></span>`;
    const summaryHtml = summary ? `<p class="date-summary">${summary}</p>` : '';
    return `<a class="date-card" href="archives/${d}.html">
      <div class="date-meta-wrap">
        <span class="date-main">${d}</span>
        <span class="date-day">${dn}</span>
      </div>
      <div class="date-text-wrap">
        <p class="date-headline">${headline || '暂无摘要'}</p>
        ${summaryHtml}
      </div>
      <div class="date-right">
        ${rightInner}
      </div>
    </a>`;
  }).join('');

  // 更新分页按钮
  const pager = document.getElementById('pagination');
  const btns = pager.querySelectorAll('.page-btn[data-page]');
  btns.forEach(b => {
    b.classList.toggle('active', parseInt(b.dataset.page) === p);
    b.disabled = parseInt(b.dataset.page) < 1 || parseInt(b.dataset.page) > totalPages;
  });

  // 更新 page info
  let info = pager.querySelector('.page-info');
  if (info) info.textContent = `第 ${p} / ${totalPages} 页`;

  // 更新 URL hash
  history.replaceState(null, '', p > 1 ? `#page=${p}` : window.location.pathname);
}

// 绑定分页按钮点击
document.getElementById('pagination').addEventListener('click', e => {
  const btn = e.target.closest('.page-btn');
  if (!btn || btn.disabled) return;
  renderPage(parseInt(btn.dataset.page));
});

// 初始化：读取 hash 或默认第1页
const hash = window.location.hash;
const initPage = hash ? parseInt(hash.replace('#page=', '')) || 1 : 1;
renderPage(initPage);
