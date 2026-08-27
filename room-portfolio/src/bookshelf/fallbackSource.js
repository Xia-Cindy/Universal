/**
 * Clean-room replacement for the unavailable visual reference. It preserves
 * the original full-screen, floating-book art direction without embedding an
 * upstream page, source code, or assets.
 */
export const FALLBACK_BOOKSHELF_SOURCE = String.raw`<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>Universe Books</title>
  <style>
    :root { --navy:#141a32; --pink:#f591ac; --cream:#fdfbf4; --lav:#c9d0ee; }
    * { box-sizing:border-box; -webkit-tap-highlight-color:transparent; }
    html, body { width:100%; height:100%; margin:0; overflow:hidden; }
    body { background:radial-gradient(120% 100% at 50% 0%, #1b2246 0%, #141a33 55%, #0f142a 100%); color:var(--cream); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; }
    button { border:0; font:inherit; cursor:pointer; }
    button:focus-visible { outline:2px solid var(--pink); outline-offset:3px; }
    #dp { position:relative; width:100%; height:100%; isolation:isolate; }
    .hero-word { position:fixed; z-index:1; top:18vh; left:50%; user-select:none; pointer-events:none; transform:translateX(-50%); transition:opacity .5s ease, transform .5s ease; }
    .hero-word span { display:block; color:var(--pink); font-size:min(22vw,43vh); font-weight:800; letter-spacing:-.04em; line-height:.82; white-space:nowrap; animation:rise .85s cubic-bezier(.22,1,.36,1) both; }
    @keyframes rise { from { opacity:0; transform:translateY(48px); } to { opacity:1; transform:translateY(0); } }
    body.detail-open .hero-word, body.universe-reading .hero-word { opacity:0; transform:translateX(-50%) translateY(-40px); }
    #dp > nav { position:fixed; z-index:40; inset:0 0 auto; display:flex; align-items:center; justify-content:space-between; padding:26px 42px; pointer-events:none; }
    #dp > nav > * { pointer-events:auto; }
    .logo { color:var(--pink); font-size:clamp(20px,2.2vw,29px); font-weight:800; letter-spacing:-.02em; }
    .menu-btn { width:48px; height:48px; border-radius:50%; background:var(--cream); color:var(--navy); font-size:0; transition:transform .25s cubic-bezier(.34,1.56,.64,1); }
    .menu-btn:hover { transform:scale(1.06); }
    #openBtn { position:fixed; z-index:30; left:50%; top:50%; padding:15px 34px 17px; border-radius:0; background:repeating-linear-gradient(92deg,rgba(90,74,40,.03) 0 2px,transparent 2px 6px),radial-gradient(125% 150% at 28% 0%,#fffdf7 0%,#f8f2e3 58%,#ede4cf 100%); color:var(--navy); font-size:14px; font-weight:800; letter-spacing:.1em; text-transform:uppercase; clip-path:polygon(0 3%,12% 0,23% 5%,36% 1%,49% 6%,60% 0,74% 5%,87% 1%,100% 5%,97% 95%,84% 100%,72% 95%,60% 100%,48% 94%,35% 99%,23% 94%,10% 99%,0 95%); filter:drop-shadow(0 2px 1px rgba(0,0,0,.16)) drop-shadow(0 14px 26px rgba(0,0,0,.4)); opacity:0; pointer-events:none; transform:translate(-50%,-50%) rotate(-1.6deg) scale(.94); transition:opacity .2s ease,transform .3s cubic-bezier(.22,1,.36,1); }
    #openBtn.on { opacity:1; transform:translate(-50%,-50%) rotate(-1.6deg) scale(1); pointer-events:auto; }
    #closeBtn { position:fixed; z-index:42; top:30px; left:50%; width:52px; height:52px; border:1.5px solid rgba(253,251,244,.4); border-radius:50%; background:transparent; color:var(--cream); opacity:0; pointer-events:none; transform:translateX(-50%); transition:opacity .3s ease; }
    body.detail-open #closeBtn { opacity:1; pointer-events:auto; }
    #gl { position:fixed; z-index:2; inset:0; overflow:hidden; touch-action:none; perspective:1500px; --tilt-x:0deg; --tilt-y:0deg; }
    .orbit { position:absolute; inset:0; transform-style:preserve-3d; transform:rotateX(var(--tilt-x)) rotateY(var(--tilt-y)); transition:transform .28s ease-out; }
    .shelf-book { position:absolute; width:clamp(145px,20vw,290px); margin:0; transform-style:preserve-3d; filter:drop-shadow(0 34px 22px rgba(0,0,0,.34)); transition:transform .42s cubic-bezier(.22,1,.36,1), filter .3s ease; }
    .shelf-book:nth-child(1) { left:12%; top:43%; transform:rotateY(28deg) rotateZ(-7deg) translateZ(10px); }
    .shelf-book:nth-child(2) { left:40%; top:31%; transform:rotateY(-4deg) rotateZ(2deg) translateZ(80px); }
    .shelf-book:nth-child(3) { right:12%; top:44%; transform:rotateY(-27deg) rotateZ(7deg) translateZ(16px); }
    .shelf-book:hover, .shelf-book:focus-within { filter:drop-shadow(0 48px 28px rgba(0,0,0,.48)); }
    .shelf-book:nth-child(1):hover, .shelf-book:nth-child(1):focus-within { transform:rotateY(28deg) rotateZ(-7deg) translateY(-28px) translateZ(34px) scale(1.04); }
    .shelf-book:nth-child(2):hover, .shelf-book:nth-child(2):focus-within { transform:rotateY(-4deg) rotateZ(2deg) translateY(-30px) translateZ(105px) scale(1.04); }
    .shelf-book:nth-child(3):hover, .shelf-book:nth-child(3):focus-within { transform:rotateY(-27deg) rotateZ(7deg) translateY(-28px) translateZ(42px) scale(1.04); }
    .shelf-book canvas { display:block; width:100%; aspect-ratio:.724; border-radius:5px 10px 10px 5px; background:#26305a; box-shadow:inset -14px 0 0 rgba(0,0,0,.16); }
    .shelf-book::after { content:""; position:absolute; z-index:-1; top:1%; bottom:1%; left:-17px; width:20px; background:linear-gradient(90deg,rgba(253,251,244,.65),rgba(26,30,57,.86)); transform:rotateY(90deg); transform-origin:right; }
    .shelf-book button { position:absolute; inset:0; width:100%; background:transparent; }
    .shelf-book figcaption { position:absolute; right:10px; bottom:12px; left:12px; overflow:hidden; color:rgba(253,251,244,.9); font-size:11px; font-weight:800; letter-spacing:.04em; text-overflow:ellipsis; white-space:nowrap; text-shadow:0 2px 8px rgba(0,0,0,.82); pointer-events:none; }
    .empty { position:absolute; top:57%; left:50%; margin:0; color:var(--lav); transform:translate(-50%,-50%); }
    body.detail-open .orbit { opacity:.35; filter:blur(1px); }
    @media (max-width:700px) { nav { padding:18px; } .menu-btn { width:42px; height:42px; } .hero-word { top:24vh; } .hero-word span { font-size:22vw; } .shelf-book { width:31vw; } .shelf-book:nth-child(1) { left:3%; top:48%; } .shelf-book:nth-child(2) { left:35%; top:41%; } .shelf-book:nth-child(3) { right:3%; top:49%; } }
  </style>
</head>
<body>
  <main id="dp">
    <div class="hero-word"><span>Knowledge</span></div>
    <nav><button class="menu-btn" aria-label="Menu">=</button><div class="logo">Bestsellers</div><button class="cta">Get Tickets</button></nav>
    <section id="gl" aria-label="知识书架"><div class="orbit"></div></section>
    <button id="closeBtn" type="button" aria-label="关闭">×</button>
  </main>
  <script>
    function drawSpaced(context, value, centerX, y, spacing) {
      const text = String(value || ''); const width = context.measureText(text).width + Math.max(0, text.length - 1) * spacing; let cursor = centerX - width / 2;
      Array.from(text).forEach((character) => { context.fillText(character, cursor, y); cursor += context.measureText(character).width + spacing; });
    }
    const BOOKS = [
      ];
    const books = BOOKS.map((cfg) => ({ cfg }));
    const state = { hovered:null, pillLock:null };
    const scene = document.querySelector('.orbit');
    const openButton = document.querySelector('.cta');
    const limit = isTouch() ? 650 : 450;
    openButton.id = 'openBtn';
    function isTouch() { return matchMedia('(pointer:coarse)').matches; }
    function showOpen(book, x, y) { state.hovered = book; openButton.style.left = x + 'px'; openButton.style.top = y + 'px'; openButton.classList.add('on'); }
    function hideOpen() { if (!state.pillLock) openButton.classList.remove('on'); }
    function render() {
      scene.innerHTML = '';
      if (!books.length) { scene.innerHTML = '<p class="empty">把第一份资料放入这里。</p>'; return; }
      books.slice(0, 3).forEach((book) => {
        const figure = document.createElement('figure'); figure.className = 'shelf-book'; figure.tabIndex = 0;
        const canvas = document.createElement('canvas'); canvas.width = 420; canvas.height = 580;
        const context = canvas.getContext('2d'); if (context && book.cfg.front) book.cfg.front(context, canvas.width, canvas.height);
        const action = document.createElement('button'); action.type = 'button'; action.setAttribute('aria-label', '打开 ' + (book.cfg.title || '知识资料')); action.addEventListener('click', () => open(book));
        const caption = document.createElement('figcaption'); caption.textContent = book.cfg.title || '知识资料';
        figure.append(canvas, action, caption);
        figure.addEventListener('pointermove', (event) => showOpen(book, event.clientX, event.clientY));
        figure.addEventListener('pointerleave', hideOpen); figure.addEventListener('focusin', () => showOpen(book, innerWidth / 2, innerHeight * .7));
        scene.append(figure);
      });
    }
    function open(book) {
      state.pillLock = book; document.body.classList.add('detail-open'); openButton.classList.remove('on');
    }
    function close() { document.body.classList.remove('detail-open'); state.pillLock = null; }
    document.getElementById("closeBtn").addEventListener("click", close);
    window.addEventListener('pointermove', (event) => { const x = (event.clientX / innerWidth - .5) * 5; const y = (event.clientY / innerHeight - .5) * -4; document.getElementById('gl').style.setProperty('--tilt-x', y + 'deg'); document.getElementById('gl').style.setProperty('--tilt-y', x + 'deg'); });
    window.addEventListener('pointerdown', (event) => { if (event.target === document.getElementById('gl')) hideOpen(); });
    render();
  </script>
</body>
</html>`;
