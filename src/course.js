(() => {
  'use strict';
  document.documentElement.classList.remove('no-js');
  const storageKey = 'chemistry.lesson01.v1';
  const chapters = [...document.querySelectorAll('[data-chapter]')];
  const chapterIds = chapters.map(section => section.id);
  const validIds = new Set(chapterIds);
  const sections = [...document.querySelectorAll('.lesson-section')];
  const tocLinks = [...document.querySelectorAll('.toc-link')];
  const statuses = [...document.querySelectorAll('[data-storage-status]')];
  let state = { complete: [], size: 18, last: null };
  let storageAvailable = true;

  function storageFallback() {
    storageAvailable = false;
    statuses.forEach(status => { status.textContent = '当前浏览器无法保存；进度仅在本次打开时有效。'; });
  }
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || 'null');
    if (saved && typeof saved === 'object') {
      state.complete = [...new Set(Array.isArray(saved.complete) ? saved.complete.filter(id => validIds.has(id)) : [])];
      state.size = [18, 20, 22, 24].includes(saved.size) ? saved.size : 18;
      state.last = validIds.has(saved.last) ? saved.last : null;
    }
    localStorage.setItem(storageKey, JSON.stringify(state));
  } catch (_) { storageFallback(); }

  function save() {
    if (!storageAvailable) return;
    try { localStorage.setItem(storageKey, JSON.stringify(state)); }
    catch (_) { storageFallback(); }
  }
  function announce(message) { document.getElementById('announcement').textContent = message; }
  function renderProgress() {
    document.querySelectorAll('[data-completion-count]').forEach(el => { el.textContent = `${state.complete.length} / 10`; });
    document.querySelectorAll('.completion-bar').forEach(el => { el.value = state.complete.length; });
    document.querySelectorAll('[data-complete]').forEach(button => {
      const done = state.complete.includes(button.dataset.complete);
      button.setAttribute('aria-pressed', String(done));
      const number = Number(button.dataset.complete.slice(-2));
      button.setAttribute('aria-label', done ? `取消第 ${number} 小节的完成标记` : `标记第 ${number} 小节已完成`);
      button.querySelector('.button-label').textContent = done ? '已完成 · 点击取消' : '标记本节已完成';
      button.querySelector('.check-box').textContent = done ? '✓' : '';
    });
    tocLinks.forEach(link => {
      const done = state.complete.includes(link.hash.slice(1));
      link.classList.toggle('is-complete', done);
      const text = link.dataset.label;
      link.setAttribute('aria-label', text + (done ? '，已完成' : ''));
    });
    if (storageAvailable) statuses.forEach(status => {
      status.textContent = state.complete.length === 10
        ? '十个小节均已标记完成。可以继续做观察和自测。'
        : '进度仅保存在当前浏览器，不会上传。';
    });
  }
  function renderSize() {
    document.documentElement.style.setProperty('--body-size', `${state.size}px`);
    document.getElementById('font-value').textContent = String(state.size);
    document.getElementById('font-minus').disabled = state.size <= 18;
    document.getElementById('font-plus').disabled = state.size >= 24;
  }
  document.querySelectorAll('[data-complete]').forEach(button => {
    button.addEventListener('click', () => {
      const id = button.dataset.complete;
      if (state.complete.includes(id)) state.complete = state.complete.filter(value => value !== id);
      else state.complete.push(id);
      renderProgress(); save();
      announce(`已标记完成 ${state.complete.length} 个小节，共 10 个。`);
    });
  });
  [-1, 1].forEach(direction => {
    document.getElementById(direction === -1 ? 'font-minus' : 'font-plus').addEventListener('click', () => {
      state.size = Math.max(18, Math.min(24, state.size + direction * 2));
      renderSize(); save(); updatePosition();
    });
  });
  if (state.last && state.last !== 'chapter-01') {
    const start = document.getElementById('start-link');
    start.href = `#${state.last}`;
    const number = Number(state.last.slice(-2));
    start.replaceChildren(document.createTextNode(`继续阅读第 ${number} 小节 `));
    const arrow = document.createElement('span');
    arrow.setAttribute('aria-hidden', 'true'); arrow.textContent = '↗'; start.append(arrow);
  }
  renderProgress(); renderSize();

  let queued = false;
  let saveTimer;
  let activeId = '';
  function updatePosition() {
    queued = false;
    const maxScroll = document.documentElement.scrollHeight - innerHeight;
    const ratio = maxScroll > 0 ? Math.min(1, Math.max(0, scrollY / maxScroll)) : 0;
    document.getElementById('scroll-progress').style.width = `${ratio * 100}%`;
    let nextActive = '';
    const trigger = Math.min(210, innerHeight * .3);
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= trigger) nextActive = section.id;
      else break;
    }
    if (!nextActive || nextActive === activeId) return;
    activeId = nextActive;
    tocLinks.forEach(link => {
      if (link.hash === `#${activeId}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    if (validIds.has(activeId)) {
      state.last = activeId;
      clearTimeout(saveTimer); saveTimer = setTimeout(save, 450);
    }
  }
  window.addEventListener('scroll', () => {
    if (!queued) { queued = true; requestAnimationFrame(updatePosition); }
  }, { passive: true });
  window.addEventListener('resize', updatePosition);
  window.addEventListener('pagehide', save);
  const mobileToc = document.getElementById('mobile-toc');
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', event => {
      const target = document.getElementById(link.hash.slice(1));
      if (!target) return;
      if (mobileToc.contains(link)) {
        event.preventDefault();
        mobileToc.open = false;
        requestAnimationFrame(() => {
          target.scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
          try { history.replaceState(null, '', link.hash); } catch (_) { /* file URLs may restrict history */ }
          const heading = target.querySelector('h2');
          if (heading) { heading.setAttribute('tabindex', '-1'); heading.focus({ preventScroll: true }); }
        });
      }
    });
  });

  let printOpenState = null;
  window.addEventListener('beforeprint', () => {
    if (printOpenState) return;
    printOpenState = [...document.querySelectorAll('.answer')].map(el => [el, el.open]);
    printOpenState.forEach(([el]) => { el.open = true; });
  });
  window.addEventListener('afterprint', () => {
    if (!printOpenState) return;
    printOpenState.forEach(([el, open]) => { el.open = open; }); printOpenState = null;
  });
  document.getElementById('print-page').addEventListener('click', () => window.print());
  updatePosition();
})();
