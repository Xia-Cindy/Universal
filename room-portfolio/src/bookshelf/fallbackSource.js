/**
 * Self-contained bookshelf scene used when the original visual reference is
 * unavailable. It intentionally contains no upstream source or assets: the
 * parent injects the current Knowledge/Wordbook catalog and reader bridge.
 */
export const FALLBACK_BOOKSHELF_SOURCE = String.raw`<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Universe Bookshelf</title>
  <style>
    :root { color-scheme: dark; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    * { box-sizing: border-box; }
    html, body { margin: 0; min-height: 100%; background: #10162f; color: #fdfbf4; }
    body { min-height: 100vh; overflow: hidden; background: radial-gradient(circle at 50% 15%, rgba(89, 104, 175, .22), transparent 38%), #10162f; }
    body::before { content: ""; position: fixed; inset: 0; pointer-events: none; opacity: .7; background-image: radial-gradient(circle at 13% 25%, rgba(253,251,244,.9) 0 1px, transparent 2px), radial-gradient(circle at 72% 19%, rgba(253,251,244,.65) 0 1px, transparent 2px), radial-gradient(circle at 86% 66%, rgba(253,251,244,.5) 0 1px, transparent 2px), radial-gradient(circle at 31% 78%, rgba(253,251,244,.38) 0 1px, transparent 2px); background-size: 260px 220px, 330px 270px, 290px 250px, 370px 310px; }
    #dp { position: relative; min-height: 100vh; padding: 28px clamp(20px, 5vw, 76px) 96px; isolation: isolate; }
    .topbar { position: relative; z-index: 3; display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    .menu-btn, .cta { border: 0; cursor: pointer; }
    .menu-btn { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 50%; background: rgba(253,251,244,.94); color: #121831; font-size: 0; box-shadow: 0 8px 24px rgba(0,0,0,.24); }
    .logo { color: #c9d0ee; font-size: 12px; font-weight: 800; letter-spacing: .18em; text-transform: uppercase; }
    .cta { min-height: 42px; padding: 0 18px; border-radius: 999px; background: #fdfbf4; color: #141a32; font-weight: 800; box-shadow: 0 10px 30px rgba(0,0,0,.2); }
    .hero { position: relative; z-index: 2; max-width: 720px; margin: clamp(64px, 12vh, 130px) auto 32px; text-align: center; }
    .hero p { margin: 0 0 12px; color: #f591ac; font-size: 11px; font-weight: 800; letter-spacing: .2em; }
    .hero h1 { margin: 0; font: 700 clamp(36px, 7vw, 84px)/.96 Georgia, serif; letter-spacing: -.04em; }
    .hero span { display: block; margin-top: 16px; color: #c9d0ee; font-size: 14px; }
    #gl { position: relative; z-index: 1; display: grid; grid-template-columns: repeat(3, minmax(150px, 1fr)); align-items: end; gap: clamp(18px, 4vw, 54px); max-width: 980px; min-height: 310px; margin: 42px auto 0; padding: 30px clamp(18px, 5vw, 60px) 36px; perspective: 1300px; border-bottom: 7px solid #343b62; border-radius: 12px; background: linear-gradient(180deg, rgba(41,49,87,.08), rgba(41,49,87,.4)); box-shadow: 0 34px 70px rgba(0,0,0,.26), inset 0 -18px 20px rgba(0,0,0,.16); }
    #gl::before { content: ""; position: absolute; inset: auto 4% -7px; height: 10px; border-radius: 10px; background: #59618e; box-shadow: 0 10px 24px rgba(0,0,0,.35); }
    .shelf-book { position: relative; z-index: 2; min-width: 0; cursor: pointer; transform: rotateY(-8deg) translateZ(0); transform-style: preserve-3d; transition: transform .45s cubic-bezier(.2,.85,.2,1), filter .35s ease; }
    .shelf-book:hover, .shelf-book:focus-within { transform: rotateY(-8deg) translateY(-18px) rotateZ(-1deg) scale(1.04); filter: drop-shadow(0 24px 18px rgba(0,0,0,.35)); }
    .shelf-book canvas { display: block; width: 100%; aspect-ratio: .72; border-radius: 5px 10px 9px 5px; box-shadow: 13px 12px 0 -5px rgba(31,36,67,.72), 21px 21px 20px rgba(0,0,0,.28); }
    .shelf-book button { position: absolute; inset: 0; width: 100%; border: 0; background: transparent; cursor: pointer; }
    .shelf-book figcaption { position: absolute; right: 8px; bottom: 10px; left: 8px; overflow: hidden; color: rgba(253,251,244,.86); font-size: 11px; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; text-shadow: 0 1px 6px rgba(0,0,0,.8); pointer-events: none; }
    .empty { grid-column: 1 / -1; padding: 70px 20px; color: #c9d0ee; text-align: center; }
    #closeBtn { display: none; }
    body.detail-open .hero, body.detail-open #gl { opacity: .38; filter: blur(1px); transition: opacity .3s ease; }
    @media (max-width: 680px) { #dp { padding-inline: 16px; } .hero { margin-top: 58px; } #gl { grid-template-columns: repeat(3, minmax(82px, 1fr)); gap: 10px; padding-inline: 8px; } .shelf-book figcaption { font-size: 9px; } }
  </style>
</head>
<body>
  <main id="dp">
    <header class="topbar"><button class="menu-btn" aria-label="Menu">=</button><div class="logo">Bestsellers</div><button class="cta">Get Tickets</button></header>
    <section class="hero"><p>UNIVERSE · PERSONAL KNOWLEDGE</p><h1>把知识翻开，<br />让它成为自己的能力。</h1><span>每一本资料都保留来源、上下文与可复习的阅读入口。</span></section>
    <section id="gl" aria-label="知识书架"></section>
    <button id="closeBtn" type="button" aria-label="关闭">关闭</button>
  </main>
  <script>
    function drawSpaced(context, value, centerX, y, spacing) {
      const text = String(value || '');
      const width = context.measureText(text).width + Math.max(0, text.length - 1) * spacing;
      let cursor = centerX - width / 2;
      Array.from(text).forEach((character) => {
        context.fillText(character, cursor, y);
        cursor += context.measureText(character).width + spacing;
      });
    }
    const BOOKS = [
      ];
    const books = BOOKS.map((cfg) => ({ cfg }));
    const state = { hovered: null, pillLock: null };
    const shelf = document.getElementById('gl');
    const cta = document.querySelector('.cta');
    cta.id = 'openBtn';
    function render() {
      shelf.innerHTML = '';
      if (!books.length) { shelf.innerHTML = '<p class="empty">书架正在等待第一份知识资料。</p>'; return; }
      books.forEach((book) => {
        const figure = document.createElement('figure');
        figure.className = 'shelf-book';
        figure.tabIndex = 0;
        const canvas = document.createElement('canvas');
        canvas.width = 420; canvas.height = 580;
        const context = canvas.getContext('2d');
        if (context && book.cfg.front) book.cfg.front(context, canvas.width, canvas.height);
        const button = document.createElement('button');
        button.type = 'button'; button.setAttribute('aria-label', '打开 ' + (book.cfg.title || '知识资料'));
        button.addEventListener('click', () => open(book));
        figure.append(canvas, button);
        const caption = document.createElement('figcaption');
        caption.textContent = book.cfg.title || '知识资料';
        figure.append(caption);
        figure.addEventListener('mouseenter', () => { state.hovered = book; });
        figure.addEventListener('focusin', () => { state.hovered = book; });
        shelf.append(figure);
      });
    }
    function open(book) {
      state.pillLock = book;
      document.body.classList.add('detail-open');
    }
    function close() { document.body.classList.remove('detail-open'); state.pillLock = null; }
    document.getElementById("closeBtn").addEventListener("click", close);
    render();
  </script>
</body>
</html>`;
