/* ConfirMad cookie consent + gated Google Analytics loader.
   No analytics script runs until the visitor accepts. */
(function () {
  var MEASURE_ID = 'G-0W7FXLY8XQ';
  var STORAGE_KEY = 'cm_consent';

  var STRINGS = {
    en: {
      text: 'We use Google Analytics to see how people use this site — no ads, no selling data. You can accept or decline; the site works the same either way.',
      link: 'Cookie policy',
      accept: 'Accept',
      reject: 'Reject'
    },
    es: {
      text: 'Usamos Google Analytics para ver cómo usa la gente esta web — sin anuncios, sin vender datos. Puedes aceptar o rechazar; la web funciona igual en ambos casos.',
      link: 'Política de cookies',
      accept: 'Aceptar',
      reject: 'Rechazar'
    },
    it: {
      text: 'Usiamo Google Analytics per capire come le persone usano questo sito — niente pubblicità, niente vendita di dati. Puoi accettare o rifiutare; il sito funziona allo stesso modo.',
      link: 'Informativa sui cookie',
      accept: 'Accetta',
      reject: 'Rifiuta'
    },
    fr: {
      text: 'Nous utilisons Google Analytics pour comprendre comment les visiteurs utilisent ce site — pas de publicité, pas de vente de données. Vous pouvez accepter ou refuser ; le site fonctionne pareil dans les deux cas.',
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
      'box-shadow:0 -10px 26px -14px rgba(22,35,59,0.3);padding:16px 20px;' +
      'font-family:var(--font,system-ui,sans-serif);animation:cmSlideUp .3s ease;}' +
      '@keyframes cmSlideUp{from{transform:translateY(100%)}to{transform:translateY(0)}}' +
      '#cm-consent-banner .cm-inner{max-width:1120px;margin:0 auto;display:flex;flex-wrap:wrap;' +
      'gap:14px;align-items:center;justify-content:space-between;}' +
      '#cm-consent-banner p{margin:0;font-size:0.86rem;line-height:1.5;color:var(--ink-soft,#4B5768);' +
      'max-width:620px;flex:1 1 320px;}' +
      '#cm-consent-banner a{color:var(--stamp,#2F5D45);}' +
      '#cm-consent-banner .cm-btns{display:flex;gap:10px;flex:none;}' +
      '#cm-consent-banner button{font-family:inherit;font-weight:700;font-size:0.86rem;' +
      'padding:10px 18px;border-radius:999px;cursor:pointer;border:1.5px solid var(--stamp,#2F5D45);' +
      'background:transparent;color:var(--stamp,#2F5D45);transition:transform .15s ease;white-space:nowrap;}' +
      '#cm-consent-banner button:hover{transform:translateY(-2px);}' +
      '#cm-consent-banner button.cm-accept{background:var(--stamp,#2F5D45);color:#fff;}' +
      '@media (max-width:600px){#cm-consent-banner .cm-inner{flex-direction:column;align-items:stretch;}' +
      '#cm-consent-banner .cm-btns{justify-content:flex-end;}}';
    var style = document.createElement('style');
    style.id = 'cm-consent-style';
    style.textContent = css;
    document.head.appendChild(style);
  }

  function hideBanner() {
    var el = document.getElementById('cm-consent-banner');
    if (el) el.remove();
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
