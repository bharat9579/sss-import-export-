/* SSS Import Export — shared site behaviour */
(function () {
  'use strict';

  var doc = document.documentElement;
  doc.classList.add('js');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var cfg = window.SSS_CONFIG || {};
  var isSet = function (v) { return typeof v === 'string' && v.trim() !== '' && v.indexOf('[') === -1; };
  var hasGSAP = typeof window.gsap !== 'undefined' && typeof window.ScrollTrigger !== 'undefined';

  /* ------------------------------------------------ contact details from config */
  function waHref(text) {
    if (!isSet(cfg.whatsappNumber)) return 'contact.html';
    return 'https://wa.me/' + cfg.whatsappNumber.replace(/\D/g, '') + (text ? '?text=' + encodeURIComponent(text) : '');
  }
  window.SSS_waHref = waHref;
  document.querySelectorAll('[data-wa]').forEach(function (a) {
    a.href = waHref(a.getAttribute('data-wa-text') || 'Hi SSS Import Export, I would like to enquire about your products.');
    if (isSet(cfg.whatsappNumber)) { a.target = '_blank'; a.rel = 'noopener'; }
  });
  document.querySelectorAll('[data-tel]').forEach(function (a) { var n = a.getAttribute('data-tel') === '2' ? cfg.phone2Dial : cfg.phoneDial; a.href = isSet(n) ? 'tel:' + n : 'contact.html'; });
  document.querySelectorAll('[data-mail]').forEach(function (a) { a.href = isSet(cfg.email) ? 'mailto:' + cfg.email : 'contact.html'; });
  document.querySelectorAll('[data-cfg]').forEach(function (el) {
    var v = cfg[el.getAttribute('data-cfg')];
    if (isSet(v)) { el.textContent = v; el.classList.remove('ph'); }
    else { el.classList.add('ph'); }
  });
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ------------------------------------------------ onion-belt satellite flyover: load near view, play, loop */
  document.querySelectorAll('[data-onion-map]').forEach(function (map) {
    var pins = map.querySelectorAll('.om-pin');
    var sat = map.querySelector('.om-sat');
    var nameEl = map.querySelector('[data-om-name]');
    var coordEl = map.querySelector('[data-om-coord]');
    var timers = [];
    function show(i) {
      pins.forEach(function (p, k) { p.classList.toggle('is-spot', k === i); });
      if (nameEl) nameEl.textContent = pins[i].querySelector('text').textContent;
      if (coordEl) coordEl.textContent = pins[i].getAttribute('data-coord');
    }
    function play() {
      timers.forEach(clearTimeout); timers = [];
      pins.forEach(function (p) { p.classList.remove('is-spot'); });
      map.classList.remove('is-live');
      void map.getBoundingClientRect();     // restart CSS animations
      map.classList.add('is-live');
      if (reduceMotion || !pins.length) return;
      // after the camera lands, spotlight each town, then fly in again
      for (var i = 0; i < pins.length; i++) {
        timers.push(setTimeout(show.bind(null, i), 6800 + i * 2600));
      }
      timers.push(setTimeout(function () { if (document.hidden) { timers.push(setTimeout(play, 4000)); } else { play(); } },
        6800 + pins.length * 2600 + 1800));
    }
    function load(cb) {
      if (!sat || sat.getAttribute('href')) { cb(); return; }
      var img = new Image();
      img.onload = img.onerror = function () { sat.setAttribute('href', img.src); sat.classList.add('is-loaded'); cb(); };
      img.src = sat.getAttribute('data-href');
    }
    if (!('IntersectionObserver' in window)) { load(play); return; }
    var started = false;
    new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        if (e.intersectionRatio < 0.35) { load(function () {}); return; }
        if (!started) { started = true; load(play); obs.disconnect(); }
      });
    }, { threshold: [0, 0.35], rootMargin: '400px 0px 0px 0px' }).observe(map);
  });

  /* ------------------------------------------------ why choose us: a short clip plays in the hovered box */
  (function () {
    var cards = document.querySelectorAll('[data-feature-video]');
    if (!cards.length) return;
    var prime = function (card) {
      var v = card.querySelector('video');
      if (v && !v.getAttribute('src')) { v.setAttribute('poster', v.getAttribute('data-poster')); v.setAttribute('src', v.getAttribute('data-src')); }
      return v;
    };
    var start = function (card) {
      if (reduceMotion) return;
      var v = prime(card);
      card.classList.add('is-playing');
      var pr = v.play(); if (pr && pr.catch) pr.catch(function () {});
    };
    var stop = function (card) {
      var v = card.querySelector('video');
      card.classList.remove('is-playing');
      if (v && v.getAttribute('src')) v.pause();
    };
    if (canHover) {
      cards.forEach(function (card) {
        card.addEventListener('pointerenter', function () { start(card); });
        card.addEventListener('pointerleave', function () { stop(card); });
        card.addEventListener('focusin', function () { start(card); });
        card.addEventListener('focusout', function () { stop(card); });
      });
      // fetch the posters once the section is near, so the first hover is instant
      if ('IntersectionObserver' in window) {
        var near = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { prime(e.target); near.unobserve(e.target); } }); }, { rootMargin: '300px 0px' });
        cards.forEach(function (c) { near.observe(c); });
      }
    } else if ('IntersectionObserver' in window) {
      // touch screens have no hover: play the box that is in the middle of the screen
      var mid = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) start(e.target); else stop(e.target); }); }, { rootMargin: '-35% 0px -35% 0px' });
      cards.forEach(function (c) { mid.observe(c); });
    }
  })();

  /* ------------------------------------------------ hero product mosaic: tiles cross-fade one at a time */
  document.querySelectorAll('[data-mosaic]').forEach(function (mosaic) {
    var tiles = Array.prototype.filter.call(mosaic.querySelectorAll('[data-tile]'), function (t) {
      return t.querySelectorAll('.hm-slide').length > 1;
    });
    if (reduceMotion || !tiles.length) return;
    var turn = 0;
    setInterval(function () {
      if (document.hidden) return;
      // the big onion tile changes every other turn, so it stays the focus
      var tile = turn % 2 === 0 ? tiles[0] : tiles[1 + ((turn - 1) / 2) % (tiles.length - 1)];
      turn++;
      if (!tile || tile.offsetParent === null) return;
      var slides = tile.querySelectorAll('.hm-slide');
      var cur = tile.querySelector('.hm-slide.is-on');
      var idx = Array.prototype.indexOf.call(slides, cur);
      cur.classList.remove('is-on');
      slides[(idx + 1) % slides.length].classList.add('is-on');
    }, 1600);
  });

  /* ------------------------------------------------ refractive glass (Chromium supports url() in backdrop-filter) */
  var brands = (navigator.userAgentData && navigator.userAgentData.brands) || [];
  if (!reduceMotion && brands.some(function (b) { return /Chromium/.test(b.brand); })) doc.classList.add('liquid-ok');

  /* ------------------------------------------------ smooth scroll (Lenis) */
  var lenis = null;
  if (!reduceMotion && typeof window.Lenis !== 'undefined') {
    lenis = new window.Lenis({ duration: 1.15, easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); }, smoothWheel: true });
    window.__lenis = lenis;
    if (hasGSAP) {
      lenis.on('scroll', window.ScrollTrigger.update);
      window.gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
      window.gsap.ticker.lagSmoothing(0);
    } else {
      var raf = function (t) { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
  }
  // same-page anchors go through Lenis so they glide instead of jumping
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href*="#"]');
    if (!a) return;
    var url = new URL(a.href, location.href);
    if (url.pathname !== location.pathname || !url.hash || url.hash === '#') return;
    var target = document.querySelector(url.hash);
    if (!target) return;
    e.preventDefault();
    closeMenu();
    if (lenis) lenis.scrollTo(target, { offset: -84 });
    else target.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
    history.replaceState(null, '', url.hash);
  });

  /* ------------------------------------------------ nav: glass on scroll + mobile menu */
  var nav = document.getElementById('nav');
  var onScroll = function () { if (nav) nav.classList.toggle('is-scrolled', window.scrollY > 40); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var toggle = document.querySelector('.nav__toggle');
  var menu = document.getElementById('menu');
  var scrim = document.querySelector('.menu-scrim');
  function setMenu(open) {
    if (!menu || !toggle) return;
    menu.classList.toggle('is-open', open);
    if (scrim) scrim.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('no-scroll', open);
    if (lenis) { open ? lenis.stop() : lenis.start(); }
    if (open) { var first = menu.querySelector('a'); if (first) first.focus({ preventScroll: true }); }
  }
  function closeMenu() { if (menu && menu.classList.contains('is-open')) setMenu(false); }
  if (toggle) toggle.addEventListener('click', function () { setMenu(!menu.classList.contains('is-open')); });
  if (scrim) scrim.addEventListener('click', closeMenu);
  if (menu) menu.addEventListener('click', function (e) { if (e.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu && menu.classList.contains('is-open')) { setMenu(false); toggle.focus(); } });
  window.matchMedia('(min-width: 981px)').addEventListener('change', function (m) { if (m.matches) closeMenu(); });

  /* ------------------------------------------------ glass: cursor-tracked specular highlight */
  if (canHover && !reduceMotion) {
    document.addEventListener('pointermove', function (e) {
      var g = e.target.closest && e.target.closest('[data-glass]');
      if (!g) return;
      var r = g.getBoundingClientRect();
      g.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      g.style.setProperty('--my', (e.clientY - r.top) + 'px');
    }, { passive: true });
  }

  /* ------------------------------------------------ magnetic buttons */
  if (canHover && !reduceMotion) {
    document.querySelectorAll('[data-magnetic]').forEach(function (btn) {
      btn.addEventListener('pointermove', function (e) {
        var r = btn.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) * 0.22;
        var y = (e.clientY - r.top - r.height / 2) * 0.35;
        btn.style.transform = 'translate(' + x + 'px,' + y + 'px)';
      });
      btn.addEventListener('pointerleave', function () { btn.style.transform = ''; });
    });
  }

  /* ------------------------------------------------ carousel */
  document.querySelectorAll('[data-carousel]').forEach(function (track) {
    var section = track.closest('section') || document;
    var step = function () { var c = track.firstElementChild; return c ? c.getBoundingClientRect().width + 18 : track.clientWidth; };
    var prev = section.querySelector('[data-carousel-prev]');
    var next = section.querySelector('[data-carousel-next]');
    if (prev) prev.addEventListener('click', function () { track.scrollBy({ left: -step(), behavior: reduceMotion ? 'auto' : 'smooth' }); });
    if (next) next.addEventListener('click', function () { track.scrollBy({ left: step(), behavior: reduceMotion ? 'auto' : 'smooth' }); });
  });

  /* ------------------------------------------------ split headline into words */
  function splitWords(el) {
    var walk = function (node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'w';
            var i = document.createElement('span'); i.className = 'wi'; i.textContent = part;
            w.appendChild(i); frag.appendChild(w);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) { walk(child); }
      });
    };
    el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
    walk(el);
    el.querySelectorAll('.w').forEach(function (w) { w.setAttribute('aria-hidden', 'true'); });
    return el.querySelectorAll('.wi');
  }

  /* ------------------------------------------------ counters */
  function countUp(el) {
    var target = parseInt(el.getAttribute('data-count'), 10) || 0;
    if (reduceMotion) { el.textContent = target; return; }
    // the real number stays in the HTML until the first frame, so a stalled animation never shows "0"
    var start = null, dur = 1600;
    var tick = function (ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      el.textContent = Math.max(1, Math.round((1 - Math.pow(1 - p, 4)) * target));
      if (p < 1) requestAnimationFrame(tick); else el.textContent = target;
    };
    requestAnimationFrame(tick);
  }

  /* ------------------------------------------------ animations */
  var reveals = document.querySelectorAll('[data-reveal]');
  var counters = document.querySelectorAll('[data-count]');

  if (!hasGSAP || reduceMotion) {
    // graceful fallback: simple fade-in, no scroll-linked effects
    var show = function (el) { el.style.transition = 'opacity .9s cubic-bezier(.22,1,.36,1), transform .9s cubic-bezier(.22,1,.36,1)'; el.style.opacity = 1; el.style.transform = 'none'; };
    if ('IntersectionObserver' in window && !reduceMotion) {
      var io = new IntersectionObserver(function (entries) { entries.forEach(function (en) { if (en.isIntersecting) { show(en.target); io.unobserve(en.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
      reveals.forEach(function (el) { io.observe(el); });
    } else { reveals.forEach(show); }
    counters.forEach(function (el) { el.textContent = el.getAttribute('data-count'); });
    document.querySelectorAll('.step').forEach(function (s) { s.classList.add('is-done'); });
    return;
  }

  var gsap = window.gsap, ST = window.ScrollTrigger;
  gsap.registerPlugin(ST);
  var EASE = 'power3.out';

  // while the logo intro is on screen, hold the hero animations until it lifts
  var introAt = Date.now() + (doc.classList.contains('sl-on') ? Math.max(0, 3450 - performance.now()) : 0);
  var introWait = function () { return Math.max(0, (introAt - Date.now()) / 1000); };

  // hero headline: word-by-word rise
  document.querySelectorAll('[data-split]').forEach(function (el) {
    var words = splitWords(el);
    gsap.from(words, { yPercent: 115, opacity: 0, duration: 1.3, ease: 'power4.out', stagger: 0.06, delay: 0.15 + introWait() });
  });

  // reveal on scroll: fade + 24px rise, staggered per batch
  gsap.set(reveals, { opacity: 0, y: 24 });
  ST.batch(reveals, {
    start: 'top 90%',
    onEnter: function (batch) { gsap.to(batch, { opacity: 1, y: 0, duration: 1.1, ease: EASE, stagger: 0.09, delay: introWait(), overwrite: true }); }
  });

  // counters
  counters.forEach(function (el) {
    ST.create({ trigger: el, start: 'top 92%', once: true, onEnter: function () { countUp(el); } });
  });

  // slow parallax on imagery
  document.querySelectorAll('[data-parallax]').forEach(function (el) {
    var n = parseFloat(el.getAttribute('data-parallax')) || 8;
    var trigger = el.closest('section') || el;
    gsap.fromTo(el, { yPercent: -n / 2 }, { yPercent: n / 2, ease: 'none', scrollTrigger: { trigger: trigger, start: 'top bottom', end: 'bottom top', scrub: true } });
  });

  // heritage timeline line fills as you read
  document.querySelectorAll('[data-timeline]').forEach(function (tl) {
    var fill = tl.querySelector('.timeline__fill');
    if (fill) gsap.to(fill, { height: 'calc(100% - 12px)', ease: 'none', scrollTrigger: { trigger: tl, start: 'top 75%', end: 'bottom 60%', scrub: true } });
  });

  // quality process: progress line + steps light up in order
  document.querySelectorAll('[data-process]').forEach(function (proc) {
    var steps = proc.querySelectorAll('.step');
    var fill = proc.querySelector('.process__fill');
    ST.create({
      trigger: proc, start: 'top 75%', end: 'bottom 45%', scrub: true,
      onUpdate: function (self) {
        if (fill) fill.style.width = (self.progress * 100) + '%';
        var lit = Math.round(self.progress * steps.length);
        steps.forEach(function (s, i) { s.classList.toggle('is-done', i < lit); });
      }
    });
  });

  // global reach: draw trade routes from India
  document.querySelectorAll('[data-map]').forEach(function (map) {
    var paths = map.querySelectorAll('.route, .route-glow');
    paths.forEach(function (p) { var len = p.getTotalLength(); p.style.strokeDasharray = len; p.style.strokeDashoffset = len; });
    var pins = map.querySelectorAll('.pin');
    gsap.set(pins, { opacity: 0 });
    ST.create({
      trigger: map, start: 'top 75%', once: true,
      onEnter: function () {
        gsap.to(pins[0], { opacity: 1, duration: 0.6 });
        gsap.to(paths, { strokeDashoffset: 0, duration: 2.2, ease: 'power2.inOut', stagger: 0.12, delay: 0.2 });
        gsap.to(Array.prototype.slice.call(pins, 1), { opacity: 1, duration: 0.7, stagger: 0.25, delay: 1.2 });
      }
    });
  });

  // nav glass also reacts to Lenis scroll (scroll event can lag behind on some trackpads)
  if (lenis) lenis.on('scroll', onScroll);
  window.addEventListener('load', function () { ST.refresh(); });
  window.SSS_refresh = function () { ST.refresh(); };
})();
