/* Products page: search, category filter, detail modal */
(function () {
  'use strict';
  var data = window.SSS_DATA;
  if (!data) return;
  var byId = {};
  data.products.forEach(function (p) { byId[p.id] = p; });
  var catName = {};
  data.categories.forEach(function (c) { catName[c.id] = c; });

  var cards = Array.prototype.slice.call(document.querySelectorAll('.pcard'));
  var q = document.getElementById('q');
  var chipsBox = document.getElementById('cats');
  var countEl = document.getElementById('count');
  var emptyEl = document.getElementById('empty');
  var resetBtn = document.getElementById('reset');
  var state = { q: '', cat: '' };

  /* ---------- build filters */
  var chip = function (id, label, n) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'chip'; b.dataset.cat = id;
    b.setAttribute('aria-pressed', 'false');
    b.innerHTML = label + ' <small>' + n + '</small>';
    chipsBox.appendChild(b);
  };
  chip('', 'All', data.products.length);
  data.categories.forEach(function (c) {
    chip(c.id, c.name, data.products.filter(function (p) { return p.category === c.id; }).length);
  });

  /* ---------- filtering */
  function apply() {
    var term = state.q.trim().toLowerCase();
    var shown = 0;
    cards.forEach(function (card) {
      var ok = (!state.cat || card.dataset.cat === state.cat) &&
               (!term || card.dataset.search.indexOf(term) !== -1);
      card.hidden = !ok;
      if (ok) shown++;
    });
    chipsBox.querySelectorAll('.chip').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.cat === state.cat ? 'true' : 'false'); });
    var label = state.cat ? catName[state.cat].name.toLowerCase() : 'products';
    countEl.textContent = shown === data.products.length ? 'Showing all ' + shown + ' products' : 'Showing ' + shown + ' ' + (shown === 1 ? 'product' : label) + ' · ' + data.products.length + ' in total';
    emptyEl.classList.toggle('is-shown', shown === 0);
    resetBtn.hidden = !(state.q || state.cat);
    // keep the URL shareable
    var p = new URLSearchParams();
    if (state.cat) p.set('category', state.cat);
    if (state.q) p.set('q', state.q);
    var qs = p.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
    if (window.SSS_refresh) window.SSS_refresh();
  }
  var debounce;
  q.addEventListener('input', function () { clearTimeout(debounce); debounce = setTimeout(function () { state.q = q.value; apply(); }, 120); });
  chipsBox.addEventListener('click', function (e) { var b = e.target.closest('.chip'); if (!b) return; state.cat = b.dataset.cat; apply(); });
  function reset() { state = { q: '', cat: '' }; q.value = ''; apply(); }
  resetBtn.addEventListener('click', reset);
  document.querySelectorAll('[data-reset]').forEach(function (b) { b.addEventListener('click', reset); });

  var params = new URLSearchParams(location.search);
  if (params.get('category') && catName[params.get('category')]) state.cat = params.get('category');
  if (params.get('q')) { state.q = params.get('q'); q.value = state.q; }
  apply();

  /* ---------- modal */
  var modal = document.getElementById('modal');
  var lastFocus = null;
  var $ = function (id) { return document.getElementById(id); };
  var list = function (arr) { return arr.join(' · '); };

  function openModal(id, fromHash) {
    var p = byId[id];
    if (!p) return;
    lastFocus = document.activeElement;
    var img = $('m-img');
    img.src = 'assets/img/products/' + p.img + '-1600.webp';
    img.alt = p.name;
    $('m-cat').textContent = catName[p.category].name;
    $('m-title').textContent = p.name;
    $('m-varieties').textContent = list(p.varieties);
    $('m-grades').textContent = list(p.grades);
    $('m-packaging').textContent = list(p.packaging);
    $('m-enquire').href = 'contact.html?product=' + encodeURIComponent(p.name);
    if (window.SSS_waHref) {
      var wa = $('m-wa');
      wa.href = window.SSS_waHref('Hi SSS Import Export, I would like a quote for ' + p.name + '.');
    }
    modal.hidden = false;
    void modal.offsetWidth; // flush layout so the fade-in transition still plays
    modal.classList.add('is-open');
    document.body.classList.add('no-scroll');
    if (window.__lenis) window.__lenis.stop();
    modal.querySelector('.modal__close').focus({ preventScroll: true });
    if (!fromHash) history.replaceState(null, '', location.pathname + location.search + '#' + p.id);
  }
  function closeModal() {
    if (modal.hidden) return;
    modal.classList.remove('is-open');
    document.body.classList.remove('no-scroll');
    if (window.__lenis) window.__lenis.start();
    setTimeout(function () { modal.hidden = true; }, 400);
    history.replaceState(null, '', location.pathname + location.search);
    if (lastFocus) lastFocus.focus({ preventScroll: true });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-open]');
    if (b) { openModal(b.dataset.open); return; }
    if (e.target.closest('[data-close]')) closeModal();
  });
  document.addEventListener('keydown', function (e) {
    if (modal.hidden) return;
    if (e.key === 'Escape') { closeModal(); return; }
    if (e.key === 'Tab') { // keep focus inside the dialog
      var f = modal.querySelectorAll('a[href], button:not([disabled])');
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  if (location.hash && byId[location.hash.slice(1)]) openModal(location.hash.slice(1), true);
})();
