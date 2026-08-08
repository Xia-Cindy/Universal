/* eslint-disable react/prop-types */
import { useEffect, useMemo, useRef, useState } from 'react';

const REFERENCE_URL = 'https://books-sigma-ashen.vercel.app/';

function readerBridge(canDelete, canEdit, readerLabel, mode) {
    return `
<style>
  #universe-reader { display: none; margin-top: 18px; padding: 14px 16px; border: 1px solid rgba(201,208,238,.36); border-radius: 14px; background: rgba(9,13,30,.48); color: #fdfbf4; }
  body.detail-open:not(.universe-reading) #universe-reader { display: block; }
  #universe-reader .ur-kicker { margin: 0 0 7px; color: #f591ac; font-size: 11px; font-weight: 800; letter-spacing: .13em; }
  #universe-reader .ur-hint { margin: 0; color: #fdfbf4; font: 600 14px/1.5 Georgia, serif; }
  #universe-bookstage { position: fixed; z-index: 26; left: 50%; top: 53%; width: min(900px, 76vw); opacity: 0; pointer-events: none; transform: translate(-50%, -48%) scale(.94); transition: opacity .35s ease, transform .6s cubic-bezier(.2,.86,.22,1); }
  body.universe-reading #universe-bookstage { opacity: 1; pointer-events: auto; transform: translate(-50%, -50%) scale(1); }
  body.universe-reading #dp > * { opacity: 0 !important; pointer-events: none !important; transform: translateY(20px) !important; }
  .ub-book { position: relative; display: grid; grid-template-columns: 1fr 1fr; min-height: min(520px, 60vh); perspective: 1800px; filter: drop-shadow(0 28px 32px rgba(0,0,0,.35)); }
  .ub-page { position: relative; overflow: auto; padding: clamp(24px, 4vw, 56px); background: repeating-linear-gradient(90deg, rgba(108,81,43,.026) 0 1px, transparent 1px 6px), #fbf7ea; color: #273840; box-shadow: inset 0 0 0 1px rgba(68,46,22,.12), inset 14px 0 22px rgba(54,34,16,.08); }
  .ub-page:first-of-type { border-radius: 11px 3px 3px 11px; box-shadow: inset -16px 0 20px rgba(54,34,16,.09), inset 0 0 0 1px rgba(68,46,22,.12); }
  .ub-page:last-of-type { border-radius: 3px 11px 11px 3px; }
  .ub-spine { position: absolute; z-index: 4; left: calc(50% - 5px); top: 0; width: 10px; height: 100%; background: linear-gradient(90deg, rgba(47,29,13,.34), rgba(255,255,255,.48), rgba(47,29,13,.28)); box-shadow: 0 0 18px rgba(0,0,0,.16); }
  .ub-front { position: absolute; z-index: 7; inset: 0 auto 0 0; width: 50%; padding: 42px 30px; display: flex; flex-direction: column; justify-content: space-between; background: linear-gradient(145deg, #ce7d92, #9d516c); border: 10px solid #edc0ca; border-right-color: #7d3f55; border-radius: 10px 3px 3px 10px; color: #fff7e7; box-shadow: inset 0 0 0 2px rgba(87,34,52,.28); transform-origin: right center; }
  .ub-front strong { display: block; font: 700 clamp(32px, 5vw, 70px)/.98 Georgia, serif; }
  .ub-front span { font: 700 11px/1.4 Arial, sans-serif; letter-spacing: .16em; text-transform: uppercase; }
  .ub-book.is-cover-turning .ub-front { animation: ub-cover-open .8s cubic-bezier(.18,.8,.2,1) both; }
  .ub-book.is-flipping-next .ub-page:last-of-type { transform-origin: left center; animation: ub-page-next .54s ease both; }
  .ub-book.is-flipping-prev .ub-page:first-of-type { transform-origin: right center; animation: ub-page-prev .54s ease both; }
  .ub-kicker { margin: 0 0 13px; color: #a64f62; font: 800 11px/1.4 Arial, sans-serif; letter-spacing: .14em; text-transform: uppercase; }
  .ub-title { margin: 0; color: #183741; font: 700 clamp(30px, 4.2vw, 64px)/.98 Georgia, serif; overflow-wrap: anywhere; }
  .ub-subtitle { margin: 14px 0 22px; color: #54746d; font: 700 14px/1.45 Arial, sans-serif; }
  .ub-copy { margin: 0; white-space: pre-wrap; color: #29424a; font: 16px/1.76 Georgia, serif; }
  .ub-number { position: absolute; bottom: 22px; color: #82908a; font-size: 11px; font-weight: 700; }
  .ub-page:first-of-type .ub-number { left: 28px; } .ub-page:last-of-type .ub-number { right: 28px; }
  .ub-controls { display: flex; align-items: center; gap: 10px; margin: 17px auto 0; width: max-content; padding: 8px; border: 1px solid rgba(253,251,244,.28); border-radius: 999px; background: rgba(16,22,48,.78); box-shadow: 0 16px 40px rgba(0,0,0,.28); }
  .ub-controls button { min-height: 37px; padding: 0 15px; border-radius: 999px; background: #fdfbf4; color: #141a32; font-weight: 800; }
  .ub-controls button:disabled { opacity: .4; cursor: default; } .ub-controls .ub-fold { background: transparent; color: #c9d0ee; }
  .ub-controls .ub-delete { background: transparent; color: #f591ac; font-size: 12px; } .ub-page-count { min-width: 88px; text-align: center; color: #fdfbf4; font-size: 12px; font-weight: 700; }
  @keyframes ub-cover-open { 0% { transform: rotateY(0deg); opacity: 1; } 72% { opacity: 1; } 100% { transform: rotateY(165deg); opacity: 0; visibility: hidden; } }
  @keyframes ub-page-next { 0% { transform: rotateY(0deg); opacity: 1; } 49% { opacity: .76; } 100% { transform: rotateY(-178deg); opacity: .06; } }
  @keyframes ub-page-prev { 0% { transform: rotateY(0deg); opacity: 1; } 49% { opacity: .76; } 100% { transform: rotateY(178deg); opacity: .06; } }
  @media (max-width: 760px) { #universe-bookstage { width: 94vw; top: 49%; } .ub-book { min-height: 57vh; } .ub-page { padding: 22px 16px 42px; } .ub-copy { font-size: 13px; } .ub-controls { gap: 4px; } .ub-controls button { padding: 0 10px; } .ub-page:first-of-type .ub-number { left: 16px; } .ub-page:last-of-type .ub-number { right: 16px; } }
</style>
<script>
  (function () {
    var reader = document.createElement('section');
    reader.id = 'universe-reader';
    reader.setAttribute('aria-live', 'polite');
    reader.innerHTML = '<p class="ur-kicker">${readerLabel}</p><p class="ur-hint">轻点左侧书本封面，把它翻开后开始阅读。</p>';
    document.getElementById('dp').appendChild(reader);
    var stage = document.createElement('section');
    stage.id = 'universe-bookstage';
    stage.setAttribute('aria-live', 'polite');
    stage.innerHTML = '<div class="ub-book"><article class="ub-page ub-left"><p class="ub-kicker"></p><h2 class="ub-title"></h2><p class="ub-subtitle"></p><p class="ub-copy"></p><span class="ub-number"></span></article><article class="ub-page ub-right"><p class="ub-kicker"></p><h2 class="ub-title"></h2><p class="ub-subtitle"></p><p class="ub-copy"></p><span class="ub-number"></span></article><i class="ub-spine"></i><button class="ub-front" type="button" aria-label="翻开封面"><span></span><strong></strong><span>点击封面翻开</span></button></div><div class="ub-controls"><button type="button" data-reader-prev>上一页</button><span class="ub-page-count"></span><button type="button" data-reader-next>下一页</button>${mode === 'wordbook' ? '<button type="button" data-reader-speak>发音</button>' : ''}<button class="ub-fold" type="button" data-reader-fold>合上书本</button>${canEdit ? '<button class="ub-fold" type="button" data-reader-edit>编辑</button>' : ''}${canDelete ? `<button class="ub-delete" type="button" data-reader-delete>${mode === 'wordbook' ? '删除单词' : '删除资料'}</button>` : ''}</div>';
    document.body.appendChild(stage);
    var pages = [];
    var spreadIndex = 0;
    var documentId = null;
    var activeEntryId = null;
    var metadata = {};
    var book = stage.querySelector('.ub-book');
    var cover = stage.querySelector('.ub-front');
    var left = stage.querySelector('.ub-left');
    var right = stage.querySelector('.ub-right');
    var previous = stage.querySelector('[data-reader-prev]');
    var next = stage.querySelector('[data-reader-next]');
    var fold = stage.querySelector('[data-reader-fold]');
    var remove = stage.querySelector('[data-reader-delete]');
    var edit = stage.querySelector('[data-reader-edit]');
    var speak = stage.querySelector('[data-reader-speak]');
    var pageCount = stage.querySelector('.ub-page-count');
    var tap = null;
    function setPage(root, item, pageNumber) {
      item = item || { title: '', content: '' };
      root.querySelector('.ub-kicker').textContent = item.eyebrow || '';
      root.querySelector('.ub-title').textContent = item.title || '';
      root.querySelector('.ub-subtitle').textContent = item.subtitle || '';
      root.querySelector('.ub-copy').textContent = item.content || (pageNumber ? '本页留白。' : '资料正在准备可翻阅的页面。');
      root.querySelector('.ub-number').textContent = pageNumber ? pageNumber : '';
    }
    function renderSpread() {
      var total = pages.length;
      setPage(left, pages[spreadIndex], total ? spreadIndex + 1 : 0);
      setPage(right, pages[spreadIndex + 1], total > spreadIndex + 1 ? spreadIndex + 2 : 0);
      pageCount.textContent = total ? '第 ' + (spreadIndex + 1) + (total > spreadIndex + 1 ? '-' + (spreadIndex + 2) : '') + ' / ' + total + ' 页' : '处理中';
      previous.disabled = spreadIndex <= 0;
      next.disabled = spreadIndex + 2 >= total;
      activeEntryId = pages[spreadIndex] && pages[spreadIndex].entryId || null;
      if (speak) speak.disabled = !activeEntryId;
    }
    function closeReading() { document.body.classList.remove('universe-reading'); }
    function openReading() {
      if (!document.body.classList.contains('detail-open') || document.body.classList.contains('universe-reading')) return;
      document.body.classList.add('universe-reading');
      cover.querySelector('strong').textContent = metadata.title || '阅读';
      cover.querySelector('span').textContent = metadata.author || '${readerLabel}';
      book.classList.remove('is-cover-turning');
      void book.offsetWidth;
      book.classList.add('is-cover-turning');
      renderSpread();
    }
    function turn(delta) {
      var nextIndex = spreadIndex + delta * 2;
      if (nextIndex < 0 || nextIndex >= pages.length) return;
      book.classList.remove('is-flipping-next', 'is-flipping-prev');
      void book.offsetWidth;
      book.classList.add(delta > 0 ? 'is-flipping-next' : 'is-flipping-prev');
      window.setTimeout(function () { spreadIndex = nextIndex; renderSpread(); }, 250);
      window.setTimeout(function () { book.classList.remove('is-flipping-next', 'is-flipping-prev'); }, 570);
    }
    previous.addEventListener('click', function () { turn(-1); });
    next.addEventListener('click', function () { turn(1); });
    fold.addEventListener('click', closeReading);
    if (speak) speak.addEventListener('click', function () {
      if (activeEntryId) window.parent.postMessage({ source: 'universe-books', type: 'speak', id: activeEntryId, word: pages[spreadIndex].title }, '*');
    });
    if (edit) edit.addEventListener('click', function () {
      var id = '${mode}' === 'wordbook' ? activeEntryId : documentId;
      if (id) window.parent.postMessage({ source: 'universe-books', type: '${mode}' === 'wordbook' ? 'edit-word' : 'edit', id: id }, '*');
    });
    cover.addEventListener('click', openReading);
    if (remove) remove.addEventListener('click', function () {
      if (documentId && window.confirm('确定删除这本资料吗？此操作会同步删除关联的知识记录。')) {
        window.parent.postMessage({ source: 'universe-books', type: '${mode}' === 'wordbook' ? 'delete-word' : 'delete', id: '${mode}' === 'wordbook' ? activeEntryId : documentId }, '*');
      }
    });
    document.getElementById('closeBtn').addEventListener('click', closeReading);
    window.addEventListener('pointerdown', function (event) {
      if (document.body.classList.contains('detail-open') && event.target && event.target.id === 'gl') tap = { x: event.clientX, y: event.clientY, at: Date.now() };
    }, true);
    window.addEventListener('pointerup', function (event) {
      if (!tap || !document.body.classList.contains('detail-open') || event.target.id !== 'gl') { tap = null; return; }
      var moved = Math.abs(event.clientX - tap.x) + Math.abs(event.clientY - tap.y);
      var duration = Date.now() - tap.at;
      tap = null;
      if (moved < 24 && duration < 1000) openReading();
    }, true);
    new MutationObserver(function () {
      if (!document.body.classList.contains('detail-open') && document.body.classList.contains('universe-reading')) closeReading();
    }).observe(document.body, { attributes: true, attributeFilter: ['class'] });
    window.addEventListener('message', function (event) {
      var data = event.data;
      if (!data || data.source !== 'universe-books' || data.type !== 'reader-pages') return;
      documentId = data.id || null;
      metadata = data.book || {};
      pages = Array.isArray(data.pages) && data.pages.length ? data.pages : [{ content: data.emptyMessage || '资料正在准备可翻阅的页面。' }];
      spreadIndex = 0;
      renderSpread();
    });
  })();
</script>`;
}

const escapeHtml = (value) => String(value || '').replace(/[&<>'"]/g, (character) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
}[character]));

function shelfFilterBridge(subjects, selectedSubject, label = '全部学科') {
    if (subjects.length < 2) return '';
    const options = [
        `<option value="">${escapeHtml(label)}</option>`,
        ...subjects.map((subject) => `<option value="${escapeHtml(subject)}" ${subject === selectedSubject ? 'selected' : ''}>${escapeHtml(subject)}</option>`)
    ].join('');
    return `
<style>
  #universe-shelf-filter { position: fixed; z-index: 45; left: 42px; bottom: 28px; }
  #universe-shelf-filter select { min-height: 38px; padding: 0 32px 0 14px; border: 1px solid rgba(201,208,238,.3); border-radius: 999px; appearance: none; background: rgba(20,26,50,.72); color: #fdfbf4; font: 700 12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; backdrop-filter: blur(12px); }
  @media (max-width: 700px) { #universe-shelf-filter { left: 18px; bottom: 18px; } }
</style>
<div id="universe-shelf-filter"><select aria-label="按学科筛选" onchange="window.parent.postMessage({source: 'universe-books', type: 'shelf-filter', subject: this.value}, '*')">${options}</select></div>`;
}

function shelfPagerBridge(page, totalPages) {
    if (totalPages <= 1) return '';
    return `
<style>
  #universe-shelf-pager { position: fixed; z-index: 45; left: 50%; bottom: 26px; display: flex; align-items: center; gap: 10px; transform: translateX(-50%); padding: 7px; border: 1px solid rgba(201,208,238,.25); border-radius: 999px; background: rgba(20,26,50,.72); box-shadow: 0 16px 36px rgba(0,0,0,.22); backdrop-filter: blur(12px); }
  #universe-shelf-pager button { width: 37px; height: 37px; border-radius: 50%; background: #fdfbf4; color: #141a32; font-size: 22px; font-weight: 800; }
  #universe-shelf-pager button:disabled { opacity: .38; cursor: default; }
  #universe-shelf-pager span { min-width: 68px; text-align: center; color: #fdfbf4; font-size: 12px; font-weight: 700; }
  @media (max-width: 700px) { #universe-shelf-pager { bottom: 18px; } }
</style>
<div id="universe-shelf-pager" aria-label="书架分页">
  <button type="button" aria-label="上一页书架" ${page === 0 ? 'disabled' : ''} onclick="window.parent.postMessage({source: 'universe-books', type: 'shelf-previous'}, '*')">‹</button>
  <span>书架 ${page + 1} / ${totalPages}</span>
  <button type="button" aria-label="下一页书架" ${page >= totalPages - 1 ? 'disabled' : ''} onclick="window.parent.postMessage({source: 'universe-books', type: 'shelf-next'}, '*')">›</button>
</div>`;
}

function moduleSwitcherBridge(activeModule, canOpenKnowledge, canOpenWordbook) {
    if (!canOpenKnowledge && !canOpenWordbook) return '';
    const knowledgeButton = canOpenKnowledge
        ? `<button class="${activeModule === 'knowledge' ? 'is-active' : ''}" type="button" onclick="window.parent.postMessage({source: 'universe-books', type: 'knowledge'}, '*')">Knowledge</button>`
        : '';
    const wordbookButton = canOpenWordbook
        ? `<button class="${activeModule === 'wordbook' ? 'is-active' : ''}" type="button" onclick="window.parent.postMessage({source: 'universe-books', type: 'wordbook'}, '*')">Wordbook</button>`
        : '';
    return `
<style>
  #universe-module-switcher { display: inline-flex; gap: 4px; padding: 4px; border: 1px solid rgba(201,208,238,.23); border-radius: 8px; background: rgba(20,26,50,.68); backdrop-filter: blur(12px); }
  #universe-module-switcher button { min-height: 31px; padding: 0 11px; border: 0; border-radius: 5px; background: transparent; color: #c9d0ee; font-size: 11px; font-weight: 700; }
  #universe-module-switcher button.is-active { background: rgba(253,251,244,.14); color: #fdfbf4; }
</style>
<nav id="universe-module-switcher" aria-label="知识书架模块">${knowledgeButton}${wordbookButton}</nav>`;
}

const painter = `
      function paintUniverseBook(x, w, h, cfg) {
        const v = cfg.universeVariant % 3;
        const palettes = [
          { bg: '#c8e4a3', ink: '#163521', panel: '#eaf1cf', accent: '#4a9360' },
          { bg: '#cf6543', ink: '#55241f', panel: '#a5412d', accent: '#e8bf59' },
          { bg: '#73b8cc', ink: '#163d52', panel: '#dcefe0', accent: '#e5cc85' }
        ];
        const p = palettes[v];
        x.fillStyle = p.bg;
        x.fillRect(0, 0, w, h);
        x.fillStyle = p.panel;
        x.fillRect(62, 62, w - 124, h - 124);
        if (v === 1) {
          x.fillStyle = p.accent;
          x.beginPath();
          x.arc(w / 2, h * 0.56, w * 0.27, 0, Math.PI * 2);
          x.fill();
          x.strokeStyle = '#f9e5a5';
          x.lineWidth = 9;
          x.beginPath();
          x.arc(w / 2, h * 0.56, w * 0.19, 0, Math.PI * 2);
          x.stroke();
        } else if (v === 2) {
          x.fillStyle = p.accent;
          x.beginPath();
          x.arc(w / 2, h * 0.57, w * 0.27, 0, Math.PI * 2);
          x.fill();
          x.strokeStyle = '#f7f5d4';
          x.lineWidth = 9;
          x.beginPath();
          x.arc(w / 2 + 24, h * 0.55, w * 0.16, 0, Math.PI * 2);
          x.stroke();
        } else {
          x.fillStyle = p.accent;
          for (let i = 0; i < 11; i++) {
            x.save();
            x.translate(w / 2 + Math.sin(i * 1.7) * 160, h * 0.66 + Math.cos(i * 1.25) * 150);
            x.rotate(i * 0.58);
            x.beginPath();
            x.ellipse(0, 0, 25, 74, 0, 0, Math.PI * 2);
            x.fill();
            x.restore();
          }
        }
        x.textAlign = 'center';
        x.fillStyle = p.ink;
        x.font = '700 31px Arial';
        drawSpaced(x, String(cfg.author || 'KNOWLEDGE').toUpperCase(), w / 2, 148, 4);
        x.font = '700 108px Georgia';
        const words = String(cfg.title || 'Knowledge').split(/\\s+/);
        const lines = [];
        let line = '';
        words.forEach((word) => {
          const next = (line + ' ' + word).trim();
          if (x.measureText(next).width > w - 180 && line) { lines.push(line); line = word; }
          else line = next;
        });
        if (line) lines.push(line);
        lines.slice(0, 3).forEach((line, i) => x.fillText(line, w / 2, 345 + i * 116));
        x.font = '600 29px Arial';
        x.fillStyle = p.ink;
        drawSpaced(x, String(cfg.year || 'STUDY').toUpperCase(), w / 2, h - 125, 3);
        x.textAlign = 'left';
      }
`;

function asReferenceBook(book, index) {
    const variants = [
        { backBg: '#6fa55f', backInk: '19,49,32', edge: '#e6efcf', spineBg: '#6fa55f', spineInk: '#143421' },
        { backBg: '#af3b2b', backInk: '253,230,184', edge: '#edcf91', spineBg: '#af3b2b', spineInk: '#f2c960' },
        { backBg: '#1687a4', backInk: '255,255,255', edge: '#d8e9e1', spineBg: '#1687a4', spineInk: '#f3d16d' }
    ];
    return {
        id: String(book.id || index),
        title: book.title || book.fileName || '学习资料',
        author: book.subtitle || book.fileType || 'KNOWLEDGE',
        year: book.status || book.processingStatus || 'READY',
        stars: 4,
        desc: book.description || book.summary || `${book.subject || '未分类'} · ${book.topic || '未分类主题'}\n${book.processingStatus || book.status || '资料已加入书架'}`,
        spineFont: '700 42px Georgia',
        universeVariant: index % 3,
        ...variants[index % variants.length]
    };
}

function buildDocument(source, books, shelfPage, totalPages, subjects, subjectFilter, {
    canDelete,
    canEdit,
    canOpenKnowledge,
    canOpenWordbook,
    filterLabel,
    mode
}) {
    const safeBooks = JSON.stringify(books.map(asReferenceBook)).replace(/</g, '\\u003c');
    const injectedBooks = `${painter}
      const BOOKS = (window.__UNIVERSE_BOOKS__ || []).map((cfg) => ({ ...cfg, front: (x, w, h) => paintUniverseBook(x, w, h, cfg), coverURL: null }));`;
    return `<script>window.__UNIVERSE_BOOKS__=${safeBooks};</script>${source
        .replace(/const BOOKS = \[[\s\S]*?\n\s{6}\];/, injectedBooks)
        .replace('<button class="menu-btn" aria-label="Menu">=</button>', '<button class="menu-btn" aria-label="返回房间" title="返回房间" onclick="window.parent.postMessage({source: \'universe-books\', type: \'return\'}, \'*\')"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M3 10.8 12 3l9 7.8v9.7a.5.5 0 0 1-.5.5h-5.7v-6.4H9.2V21H3.5a.5.5 0 0 1-.5-.5v-9.7Zm4 8.2h1.2v-6.4h7.6V19H17v-8.2L12 6.5 7 10.8V19Z"/></svg></button>')
        .replace('<div class="logo">Bestsellers</div>', moduleSwitcherBridge(mode, canOpenKnowledge, canOpenWordbook))
        .replace('<button class="cta">Get Tickets</button>', `<button class="cta" onclick="window.parent.postMessage({source: 'universe-books', type: 'create'}, '*')">${mode === 'wordbook' ? '新建单词' : '新建知识'}</button>`)
        .replace('function open(book) {', "function open(book) { window.parent.postMessage({ source: 'universe-books', type: 'open', id: book.cfg.id }, '*');")
        .replace('const limit = isTouch() ? 650 : 450;', 'const limit = isTouch() ? 1400 : 900;')
        .replace(
            'document.getElementById("closeBtn").addEventListener("click", close);',
            `document.getElementById("closeBtn").addEventListener("click", close);
      const universeOpenButton = document.getElementById("openBtn");
      universeOpenButton.style.pointerEvents = "auto";
      universeOpenButton.setAttribute("aria-label", "打开当前词汇书阅读");
      universeOpenButton.addEventListener("click", () => open(state.hovered || state.pillLock || books[1] || books[0]));`
        )
        .replace('</body>', `${shelfFilterBridge(subjects, subjectFilter, filterLabel)}${shelfPagerBridge(shelfPage, totalPages)}${readerBridge(canDelete, canEdit, mode === 'wordbook' ? 'VOCABULARY PAGES' : 'KNOWLEDGE PAGES', mode)}</body>`)} `;
}

function readerPages(detail, documentId, book) {
    const metadata = {
        title: book?.title || book?.fileName || '阅读',
        author: book?.subtitle || book?.fileType || 'KNOWLEDGE'
    };
    if (Array.isArray(detail?.pages)) return { id: documentId, book: metadata, pages: detail.pages };
    const chunks = detail?.chunks || [];
    const pages = chunks.flatMap((chunk) => {
        const content = String(chunk.content || '').trim();
        return content.match(/[\s\S]{1,680}(?:\s|$)|[\s\S]{1,680}/g) || [];
    }).filter(Boolean).map((content) => ({ content }));
    if (pages.length) return { id: documentId, book: metadata, pages };
    const document = detail?.document || {};
    const isProcessing = ['parsing', 'chunking'].includes(document.processingStatus);
    const provider = document.provider === 'ragflow' ? 'RAGFlow' : '本地知识库';
    return {
        id: documentId,
        book: metadata,
        pages: [],
        emptyMessage: isProcessing
            ? `${provider} 正在处理这本资料，尚未返回可翻阅的页面。\n状态：${document.providerStatus || document.processingStatus || '处理中'}。`
            : document.errorMessage || '这本资料还没有生成可翻阅的页面。'
    };
}

export default function DeployedBooks({
    books,
    goals = [],
    loadError = '',
    mode = 'knowledge',
    onCreate,
    onDelete,
    onDeleteWord,
    onEditKnowledge,
    onEditWord,
    onSpeakWord,
    onOpen,
    onOpenKnowledge,
    onOpenWordbook,
    onRetry,
    onReturn
}) {
    const [source, setSource] = useState('');
    const [composerOpen, setComposerOpen] = useState(false);
    const [file, setFile] = useState(null);
    const [subject, setSubject] = useState('');
    const [topic, setTopic] = useState('');
    const [bookTitle, setBookTitle] = useState('');
    const [word, setWord] = useState('');
    const [meaning, setMeaning] = useState('');
    const [language, setLanguage] = useState('English');
    const [tags, setTags] = useState('');
    const [status, setStatus] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [reader, setReader] = useState(null);
    const [shelfPage, setShelfPage] = useState(0);
    const [subjectFilter, setSubjectFilter] = useState('');
    const [goalId, setGoalId] = useState('');
    const [editing, setEditing] = useState(null);
    const frame = useRef(null);
    const subjects = useMemo(
        () => [...new Set(books.map((book) => book.subject).filter(Boolean))].sort((a, b) => a.localeCompare(b, mode === 'wordbook' ? 'en' : 'zh-CN')),
        [books, mode]
    );
    const filteredBooks = useMemo(
        () => subjectFilter ? books.filter((book) => book.subject === subjectFilter) : books,
        [books, subjectFilter]
    );
    const totalPages = Math.max(1, Math.ceil(filteredBooks.length / 3));
    const visibleBooks = useMemo(() => filteredBooks.slice(shelfPage * 3, shelfPage * 3 + 3), [filteredBooks, shelfPage]);
    const bookDocument = useMemo(
        () => source ? buildDocument(source, visibleBooks, shelfPage, totalPages, subjects, subjectFilter, {
            canDelete: Boolean(onDelete || onDeleteWord),
            canEdit: Boolean(onEditKnowledge || onEditWord),
            canOpenKnowledge: Boolean(onOpenKnowledge),
            canOpenWordbook: Boolean(onOpenWordbook),
            filterLabel: mode === 'wordbook' ? '全部语言' : '全部学科',
            mode
        }) : '',
        [mode, onDelete, onDeleteWord, onEditKnowledge, onEditWord, onOpenKnowledge, onOpenWordbook, shelfPage, source, subjectFilter, subjects, totalPages, visibleBooks]
    );

    useEffect(() => {
        setShelfPage((page) => Math.min(page, totalPages - 1));
    }, [totalPages]);

    useEffect(() => {
        let active = true;
        fetch(REFERENCE_URL)
            .then((response) => {
                if (!response.ok) throw new Error('无法读取参考书本场景。');
                return response.text();
            })
            .then((html) => {
                if (active) setSource(html);
            })
            .catch(() => {
                if (active) setSource('');
            });
        return () => {
            active = false;
        };
    }, []);

    useEffect(() => {
        const receive = (event) => {
            if (event.source !== frame.current?.contentWindow || event.data?.source !== 'universe-books') return;
            if (event.data.type === 'return') {
                onReturn?.();
                return;
            }
            if (event.data.type === 'create') {
                setEditing(null);
                setComposerOpen(true);
                setStatus('');
                return;
            }
            if (event.data.type === 'wordbook') {
                onOpenWordbook?.();
                return;
            }
            if (event.data.type === 'knowledge') {
                onOpenKnowledge?.();
                return;
            }
            if (event.data.type === 'shelf-previous') {
                setShelfPage((page) => Math.max(0, page - 1));
                return;
            }
            if (event.data.type === 'shelf-next') {
                setShelfPage((page) => Math.min(totalPages - 1, page + 1));
                return;
            }
            if (event.data.type === 'shelf-filter') {
                setSubjectFilter(event.data.subject || '');
                setShelfPage(0);
                return;
            }
            if (event.data.type === 'speak') {
                onSpeakWord?.(event.data.word);
                return;
            }
            if (event.data.type === 'edit-word') {
                const entry = books.flatMap((item) => item.entries || []).find((item) => String(item.id) === String(event.data.id));
                if (!entry) return;
                setEditing({ kind: 'wordbook', item: entry });
                setWord(entry.word || '');
                setMeaning(entry.meaning || '');
                setLanguage(entry.language || 'English');
                setTags((entry.tags || []).join(', '));
                setGoalId(entry.goalId || '');
                setStatus('');
                setComposerOpen(true);
                return;
            }
            if (event.data.type === 'delete-word') {
                const entry = books.flatMap((item) => item.entries || []).find((item) => String(item.id) === String(event.data.id));
                if (!entry) return;
                Promise.resolve(onDeleteWord?.(entry))
                    .then(() => { setReader(null); setShelfPage(0); })
                    .catch((error) => setStatus(error instanceof Error ? error.message : '删除单词失败。'));
                return;
            }
            const book = books.find((item) => String(item.id) === String(event.data.id));
            if (!book) return;
            if (event.data.type === 'edit') {
                setEditing({ kind: 'knowledge', item: book });
                setBookTitle(book.title || book.fileName || '');
                setSubject(book.subject || '');
                setTopic(book.topic || '');
                setGoalId(book.goalId || '');
                setStatus('');
                setComposerOpen(true);
                return;
            }
            if (event.data.type === 'delete') {
                Promise.resolve(onDelete?.(book))
                    .then(() => {
                        setReader(null);
                        setShelfPage(0);
                    })
                    .catch((error) => {
                        setReader({ id: book.id, pages: [], emptyMessage: error instanceof Error ? error.message : '删除资料失败。' });
                    });
                return;
            }
            Promise.resolve(onOpen?.(book))
                .then((detail) => {
                    if (detail) setReader(readerPages(detail, book.id, book));
                })
                .catch((error) => {
                    setReader({ pages: [], emptyMessage: error instanceof Error ? error.message : '无法读取这本资料。' });
                });
        };
        window.addEventListener('message', receive);
        return () => window.removeEventListener('message', receive);
    }, [books, onDelete, onDeleteWord, onOpen, onOpenKnowledge, onOpenWordbook, onReturn, onSpeakWord, totalPages]);

    useEffect(() => {
        if (!reader || !frame.current?.contentWindow) return;
        frame.current.contentWindow.postMessage({ source: 'universe-books', type: 'reader-pages', ...reader }, '*');
    }, [reader, bookDocument]);

    const selectFile = (event) => {
        const nextFile = event.target.files?.[0] || null;
        setFile(nextFile);
        if (nextFile && !topic) setTopic(nextFile.name.replace(/\.[^.]+$/, ''));
        setStatus('');
    };

    const submit = async (event) => {
        event.preventDefault();
        if (mode === 'wordbook') {
            if (!word.trim()) {
                setStatus('请填写一个单词。');
                return;
            }
            setSubmitting(true);
            setStatus(editing ? '正在保存单词…' : '正在加入词汇书…');
            try {
                const payload = {
                    word: word.trim(),
                    meaning: meaning.trim(),
                    language: language.trim() || 'English',
                    tags: tags.split(/[，,]/).map((item) => item.trim()).filter(Boolean),
                    goalId: goalId || null
                };
                if (editing) await onEditWord?.(editing.item, payload);
                else await onCreate?.(payload);
                setComposerOpen(false);
                setEditing(null);
                setWord('');
                setMeaning('');
                setLanguage('English');
                setTags('');
                setGoalId('');
            } catch (error) {
                setStatus(error instanceof Error ? error.message : '新建单词失败。');
            } finally {
                setSubmitting(false);
            }
            return;
        }
        if ((!editing && !file) || !subject.trim() || !topic.trim() || (editing && !bookTitle.trim())) {
            setStatus('请选择资料，并填写学科与主题。');
            return;
        }
        setSubmitting(true);
        setStatus(editing ? '正在保存资料…' : '正在加入知识库…');
        try {
            if (editing) {
                await onEditKnowledge?.(editing.item, { fileName: bookTitle.trim(), goalId: goalId || null, subject: subject.trim(), topic: topic.trim() });
            } else {
                await onCreate?.({ file, goalId: goalId || null, subject: subject.trim(), topic: topic.trim() });
            }
            setComposerOpen(false);
            setEditing(null);
            setFile(null);
            setSubject('');
            setTopic('');
            setGoalId('');
        } catch (error) {
            setStatus(error instanceof Error ? error.message : '新建知识失败。');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <section className="deployed-books" aria-label={`${mode === 'wordbook' ? 'Wordbook' : 'Knowledge'} 3D books`}>
            {bookDocument ? (
                <iframe ref={frame} srcDoc={bookDocument} title="Knowledge books" />
            ) : (
                <p>正在装配书本场景…</p>
            )}
            {loadError && (
                <div className="knowledge-load-notice" role="status">
                    <strong>知识书架暂时无法连接</strong>
                    <span>已上传资料没有被删除；恢复 API 后会重新出现。</span>
                    <button onClick={onRetry} type="button">重试</button>
                </div>
            )}
            {!loadError && !books.length && source && (
                <div className="knowledge-load-notice" role="status">
                    <strong>{mode === 'wordbook' ? '还没有可显示的词汇书' : '还没有可显示的资料'}</strong>
                    <span>{mode === 'wordbook' ? '点击右上角“新建单词”加入第一本词汇书。' : '点击右上角“新建知识”加入第一本书。'}</span>
                </div>
            )}
            {composerOpen && (
                <div className="knowledge-composer" role="dialog" aria-modal="true" aria-label={editing ? '编辑资料' : mode === 'wordbook' ? '新建单词' : '新建知识'}>
                    <form onSubmit={submit}>
                        <button className="knowledge-composer-close" type="button" aria-label={editing ? '关闭编辑' : mode === 'wordbook' ? '关闭新建单词' : '关闭新建知识'} onClick={() => setComposerOpen(false)}>×</button>
                        <p>{editing ? 'EDIT DETAILS' : mode === 'wordbook' ? 'NEW VOCABULARY' : 'NEW KNOWLEDGE'}</p>
                        <h2>{editing ? mode === 'wordbook' ? '编辑单词' : '编辑这本书' : mode === 'wordbook' ? '加入一册词汇书' : '加入一本新书'}</h2>
                        {mode === 'wordbook' ? (
                            <>
                                <label>
                                    单词
                                    <input autoFocus value={word} onChange={(event) => setWord(event.target.value)} placeholder="例如：serendipity" />
                                </label>
                                <label>
                                    释义
                                    <input value={meaning} onChange={(event) => setMeaning(event.target.value)} placeholder="可选，词典会补充英文参考" />
                                </label>
                                <label>
                                    语言
                                    <input value={language} onChange={(event) => setLanguage(event.target.value)} placeholder="English" />
                                </label>
                                <label>
                                    标签
                                    <input value={tags} onChange={(event) => setTags(event.target.value)} placeholder="用逗号分隔，例如：GRE, 阅读" />
                                </label>
                            </>
                        ) : (
                            <>
                                {!editing && <label>
                                    资料文件
                                    <input accept=".txt,.md,.markdown,.pdf" onChange={selectFile} type="file" />
                                    <span>{file?.name || '支持 TXT、Markdown、PDF'}</span>
                                </label>}
                                {editing && <label>
                                    书名
                                    <input autoFocus value={bookTitle} onChange={(event) => setBookTitle(event.target.value)} />
                                </label>}
                                <label>
                                    学科
                                    <input value={subject} onChange={(event) => setSubject(event.target.value)} placeholder="例如：计算机科学" />
                                </label>
                                <label>
                                    主题
                                    <input value={topic} onChange={(event) => setTopic(event.target.value)} placeholder="例如：操作系统" />
                                </label>
                            </>
                        )}
                        {goals.length > 0 && (
                            <label>
                                关联学习目标
                                <select value={goalId} onChange={(event) => setGoalId(event.target.value)}>
                                    <option value="">独立知识（不关联目标）</option>
                                    {goals.map((goal) => <option key={goal.id} value={goal.id}>{goal.goalName}</option>)}
                                </select>
                            </label>
                        )}
                        <button className="knowledge-composer-submit" disabled={submitting} type="submit">
                            {submitting ? '正在保存…' : editing ? '保存修改' : mode === 'wordbook' ? '加入词汇书' : '加入书架'}
                        </button>
                        {status && <small>{status}</small>}
                    </form>
                </div>
            )}
        </section>
    );
}
