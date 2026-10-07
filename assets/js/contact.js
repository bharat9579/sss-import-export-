/* Contact page: product list, prefill, validation, submit (form endpoint → WhatsApp → email fallback) */
(function () {
  'use strict';
  var cfg = window.SSS_CONFIG || {};
  var data = window.SSS_DATA;
  var isSet = function (v) { return typeof v === 'string' && v.trim() !== '' && v.indexOf('[') === -1; };
  var form = document.getElementById('quote-form');
  if (!form) return;
  var sel = document.getElementById('product-select');
  var status = document.getElementById('form-status');

  /* ---------- product options grouped by category */
  if (data) {
    data.categories.forEach(function (c) {
      var g = document.createElement('optgroup'); g.label = c.name;
      var any = document.createElement('option'); any.value = c.name; any.textContent = c.name + ' — any / several';
      g.appendChild(any);
      data.products.filter(function (p) { return p.category === c.id; }).forEach(function (p) {
        var o = document.createElement('option'); o.value = p.name; o.textContent = p.name; g.appendChild(o);
      });
      sel.appendChild(g);
    });
  }
  var mixed = document.createElement('option'); mixed.value = 'Mixed container / multiple products'; mixed.textContent = 'Mixed container / multiple products'; sel.appendChild(mixed);
  var other = document.createElement('option'); other.value = 'Other'; other.textContent = 'Other (describe in message)'; sel.appendChild(other);

  var wanted = new URLSearchParams(location.search).get('product');
  if (wanted) {
    var match = Array.prototype.find.call(sel.options, function (o) { return o.value.toLowerCase() === wanted.toLowerCase(); });
    if (match) sel.value = match.value;
  }

  /* ---------- validation */
  function setStatus(msg, ok) {
    status.textContent = msg;
    status.className = 'form__status ' + (ok ? 'is-ok' : 'is-err');
  }
  function validate() {
    var bad = [];
    form.querySelectorAll('[required]').forEach(function (f) {
      var ok = f.value.trim() !== '' && (f.type !== 'email' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.value.trim()));
      f.setAttribute('aria-invalid', ok ? 'false' : 'true');
      f.style.borderColor = ok ? '' : '#B42318';
      if (!ok) bad.push(f);
    });
    if (bad.length) {
      setStatus('Please complete the highlighted fields' + (bad.some(function (f) { return f.type === 'email'; }) ? ' (check the email address)' : '') + '.', false);
      bad[0].focus();
      return false;
    }
    return true;
  }
  form.addEventListener('input', function (e) { if (e.target.getAttribute('aria-invalid') === 'true') { e.target.style.borderColor = ''; e.target.setAttribute('aria-invalid', 'false'); } });

  function summary() {
    var d = new FormData(form);
    var lines = [
      'Quote request — SSS Import Export',
      'Name: ' + d.get('name'),
      d.get('company') ? 'Company: ' + d.get('company') : '',
      'Email: ' + d.get('email'),
      d.get('phone') ? 'Phone: ' + d.get('phone') : '',
      'Country: ' + d.get('country'),
      'Product: ' + d.get('product'),
      'Quantity: ' + d.get('quantity') + ' ' + d.get('unit'),
      d.get('packaging') ? 'Packaging: ' + d.get('packaging') : '',
      d.get('message') ? 'Message: ' + d.get('message') : ''
    ];
    return lines.filter(Boolean).join('\n');
  }
  function viaWhatsApp() {
    window.open('https://wa.me/' + cfg.whatsappNumber.replace(/\D/g, '') + '?text=' + encodeURIComponent(summary()), '_blank', 'noopener');
    setStatus('WhatsApp opened with your enquiry — just press send.', true);
  }
  function viaEmail() {
    location.href = 'mailto:' + cfg.email + '?subject=' + encodeURIComponent('Quote request — ' + new FormData(form).get('product')) + '&body=' + encodeURIComponent(summary());
    setStatus('Your email app has opened with the enquiry — just press send.', true);
  }

  /* ---------- submit */
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!validate()) return;
    var btn = form.querySelector('[type="submit"]');
    if (isSet(cfg.formEndpoint)) {
      btn.disabled = true;
      fetch(cfg.formEndpoint, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
        .then(function (r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          setStatus('Thank you — your request is in. Our export desk will reply within 24 hours.', true);
          form.reset();
        })
        .catch(function () { setStatus('Sorry, that didn’t send. Please try WhatsApp or email us directly.', false); })
        .finally(function () { btn.disabled = false; });
    } else if (isSet(cfg.whatsappNumber)) {
      viaWhatsApp();
    } else if (isSet(cfg.email)) {
      viaEmail();
    } else {
      setStatus('Online submissions aren’t connected yet. (Site owner: set formEndpoint, whatsappNumber or email in assets/js/config.js.)', false);
    }
  });

  document.getElementById('send-wa').addEventListener('click', function () {
    if (!validate()) return;
    if (isSet(cfg.whatsappNumber)) viaWhatsApp();
    else setStatus('WhatsApp isn’t connected yet. (Site owner: set whatsappNumber in assets/js/config.js.)', false);
  });
})();
