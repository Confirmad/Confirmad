/* ConfirMad cookie consent + gated Google Analytics loader.
   No analytics script runs until the visitor accepts. */
(function () {
  var MEASURE_ID = 'G-0W7FXLY8XQ';
  var STORAGE_KEY = 'cm_consent';

  var STRINGS = {
    en: {
      text: 'We use cookies to understand how you use ConfirMad.',
      link: 'Cookie policy',
      accept: 'Accept',
      reject: 'Reject'
    },
    es: {
      text: 'Usamos cookies para entender cómo usas ConfirMad.',
      link: 'Política de cookies',
      accept: 'Aceptar',
      reject: 'Rechazar'
    },
    it: {
      text: 'Usiamo i cookie per capire come usi ConfirMad.',
      link: 'Informativa sui cookie',
      accept: 'Accetta',
      reject: 'Rifiuta'
    },
    fr: {
      text: 'Nous utilisons des cookies pour comprendre votre usage de ConfirMad.',
      link: 'Politique de cookies',
      accept: 'Accepter',
      reject: 'Refuser'
    }
  };

  function currentLang() {
    var l = (document.documentElement.getAttribute('lang') || 'en').slice(0, 2).toLowerCase();
    return STRINGS[l] ? l : 'en';
  }

  function loadGA() {
    if (window.__cmGaLoaded) return;
    window.__cmGaLoaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + MEASURE_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', MEASURE_ID);
  }

  function injectStyle() {
    if (document.getElementById('cm-consent-style')) return;
    var css =
      '#cm-consent-banner{position:fixed;left:0;right:0;bottom:0;z-index:999;' +
      'background:var(--card,#fff);border-top:1px solid var(--line,#D7DCD8);' +
      'box-shadow:0 -10px 26px -14px rgba(22,35,59,0.3);padding:10px 16px;' +
      'font-family:var(--font,system-ui,sans-serif);animation:cmSlideUp .3s ease;}' +
      '@keyframes cmSlideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}' +
      '#cm-consent-banner .cm-inner{max-width:1120px;margin:0 auto;display:flex;flex-wrap:wrap;' +
      'gap:8px 14px;align-items:center;justify-content:space-between;}' +
      '#cm-consent-banner p{margin:0;font-size:0.82rem;line-height:1.4;color:var(--ink-soft,#4B5768);' +
      'flex:1 1 auto;min-width:0;}' +
      '#cm-consent-banner a{color:var(--stamp,#2F5D45); white-space:nowrap;}' +
      '#cm-consent-banner .cm-btns{display:flex;gap:8px;flex:none;}' +
      '#cm-consent-banner button{font-family:inherit;font-weight:700;font-size:0.82rem;' +
      'padding:8px 16px;border-radius:999px;cursor:pointer;border:1.5px solid var(--stamp,#2F5D45);' +
      'background:transparent;color:var(--stamp,#2F5D45);transition:transform .15s ease;white-space:nowrap;}' +
      '#cm-consent-banner button:hover{transform:translateY(-2px);}' +
      '#cm-consent-banner button.cm-reject{border-color:var(--ink-faint,#636C79);color:var(--ink-faint,#636C79);}' +
      '@media (max-width:600px){' +
      '#cm-consent-banner{padding:10px 14px;}' +
      '#cm-consent-banner .cm-inner{flex-direction:column;align-items:stretch;justify-content:flex-start;gap:8px;}' +
      '#cm-consent-banner p{font-size:0.78rem;}' +
      '#cm-consent-banner .cm-btns{display:grid;grid-template-columns:1fr 1fr;gap:8px;}' +
      '#cm-consent-banner button{padding:9px 10px;font-size:0.8rem;}}';
    var style = document.createElement('style');
    style.id = 'cm-consent-style';
    style.textContent = css;
    document.head.appendChild(style);
  }

  function applyBodyPadding() {
    var el = document.getElementById('cm-consent-banner');
    if (!el) return;
    try {
      document.body.style.paddingBottom = el.getBoundingClientRect().height + 'px';
    } catch (e) {}
  }

  function clearBodyPadding() {
    document.body.style.paddingBottom = '';
  }

  function hideBanner() {
    var el = document.getElementById('cm-consent-banner');
    if (el) el.remove();
    clearBodyPadding();
    window.removeEventListener('resize', applyBodyPadding);
  }

  function showBanner() {
    if (document.getElementById('cm-consent-banner')) return;
    injectStyle();
    var t = STRINGS[currentLang()];
    var el = document.createElement('div');
    el.id = 'cm-consent-banner';
    el.setAttribute('role', 'region');
    el.setAttribute('aria-label', 'Cookie consent');
    el.innerHTML =
      '<div class="cm-inner">' +
      '<p>' + t.text + ' <a href="/cookies.html">' + t.link + '</a></p>' +
      '<div class="cm-btns">' +
      '<button type="button" class="cm-reject">' + t.reject + '</button>' +
      '<button type="button" class="cm-accept">' + t.accept + '</button>' +
      '</div></div>';
    document.body.appendChild(el);
    applyBodyPadding();
    window.addEventListener('resize', applyBodyPadding);
    el.querySelector('.cm-accept').addEventListener('click', function () {
      try { localStorage.setItem(STORAGE_KEY, 'granted'); } catch (e) {}
      loadGA();
      hideBanner();
    });
    el.querySelector('.cm-reject').addEventListener('click', function () {
      try { localStorage.setItem(STORAGE_KEY, 'denied'); } catch (e) {}
      hideBanner();
    });
  }

  function init() {
    var consent;
    try { consent = localStorage.getItem(STORAGE_KEY); } catch (e) { consent = null; }
    if (consent === 'granted') {
      loadGA();
    } else if (consent !== 'denied') {
      showBanner();
    }
  }

  window.ConfirmadConsent = {
    show: showBanner,
    accept: function () {
      try { localStorage.setItem(STORAGE_KEY, 'granted'); } catch (e) {}
      loadGA();
      hideBanner();
    },
    reject: function () {
      try { localStorage.setItem(STORAGE_KEY, 'denied'); } catch (e) {}
      hideBanner();
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
