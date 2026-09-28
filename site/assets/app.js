// Shared helpers for every calculator page.
(function () {
  const CURRENCIES = { GBP: "en-GB", USD: "en-US", EUR: "de-DE", CAD: "en-CA", AUD: "en-AU", INR: "en-IN" };

  function store(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (e) { return null; }
  }

  function guessCurrency() {
    const lang = (navigator.language || "en-US").toUpperCase();
    if (lang.endsWith("-GB")) return "GBP";
    if (lang.endsWith("-CA")) return "CAD";
    if (lang.endsWith("-AU")) return "AUD";
    if (lang.endsWith("-IN")) return "INR";
    if (/-(DE|FR|ES|IT|NL|IE|PT|AT|BE|FI)$/.test(lang)) return "EUR";
    return "USD";
  }

  let currency = store("currency") || guessCurrency();
  if (!CURRENCIES[currency]) currency = "USD";

  const App = {
    listeners: [],
    money(n, digits = 0) {
      if (!isFinite(n)) return "—";
      return new Intl.NumberFormat(CURRENCIES[currency], {
        style: "currency", currency, maximumFractionDigits: digits, minimumFractionDigits: digits,
      }).format(n);
    },
    num(n, digits = 2) {
      if (!isFinite(n)) return "—";
      return new Intl.NumberFormat(undefined, { maximumFractionDigits: digits }).format(n);
    },
    val(id) {
      const v = parseFloat(document.getElementById(id).value);
      return isFinite(v) ? v : 0;
    },
    set(id, text) {
      const el = document.getElementById(id);
      if (el) el.textContent = text;
    },
    // Re-run `fn` whenever any input on the page changes (and once on load).
    bind(fn) {
      App.listeners.push(fn);
      document.querySelectorAll("input, select.field").forEach((el) => el.addEventListener("input", fn));
      fn();
    },
    // Simple stacked bar chart. series = [{label, color, values: []}], labels = [] (x-axis)
    chart(el, labels, series) {
      const W = 640, H = 260, P = { l: 64, r: 10, t: 10, b: 28 };
      const n = labels.length;
      if (!n) { el.innerHTML = ""; return; }
      const totals = labels.map((_, i) => series.reduce((s, x) => s + Math.max(0, x.values[i]), 0));
      const max = Math.max(...totals, 1);
      const bw = (W - P.l - P.r) / n;
      const y = (v) => H - P.b - (v / max) * (H - P.t - P.b);
      let svg = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Chart">`;
      for (let g = 0; g <= 4; g++) {
        const v = (max * g) / 4, yy = y(v);
        svg += `<line x1="${P.l}" x2="${W - P.r}" y1="${yy}" y2="${yy}" stroke="currentColor" stroke-opacity=".12"/>`;
        svg += `<text x="${P.l - 6}" y="${yy + 4}" font-size="11" text-anchor="end" fill="currentColor" opacity=".6">${App.money(v).replace(/\.00$/, "")}</text>`;
      }
      const step = Math.ceil(n / 12);
      labels.forEach((lab, i) => {
        let base = 0;
        series.forEach((s) => {
          const v = Math.max(0, s.values[i]);
          const y0 = y(base), y1 = y(base + v);
          svg += `<rect x="${P.l + i * bw + bw * 0.12}" y="${y1}" width="${bw * 0.76}" height="${Math.max(0, y0 - y1)}" style="fill:${s.color}"><title>${lab}: ${s.label} ${App.money(v)}</title></rect>`;
          base += v;
        });
        if (i % step === 0 || i === n - 1)
          svg += `<text x="${P.l + i * bw + bw / 2}" y="${H - 8}" font-size="11" text-anchor="middle" fill="currentColor" opacity=".6">${lab}</text>`;
      });
      svg += "</svg>";
      svg += `<div class="legend">${series.map((s) => `<span><i style="background:${s.color}"></i>${s.label}</span>`).join("")}</div>`;
      el.innerHTML = svg;
    },
  };
  window.App = App;

  document.addEventListener("DOMContentLoaded", () => {
    // Currency picker
    const picker = document.getElementById("currency");
    if (picker) {
      picker.innerHTML = Object.keys(CURRENCIES).map((c) => `<option ${c === currency ? "selected" : ""}>${c}</option>`).join("");
      picker.addEventListener("change", () => {
        currency = picker.value;
        store("currency", currency);
        App.listeners.forEach((fn) => fn());
      });
    }

    // Monetisation — each piece only appears once configured in config.js
    const cfg = window.SITE_CONFIG || {};
    if (cfg.adsenseClient) {
      const s = document.createElement("script");
      s.async = true;
      s.crossOrigin = "anonymous";
      s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + encodeURIComponent(cfg.adsenseClient);
      document.head.appendChild(s);
      document.querySelectorAll(".ad-slot").forEach((slot) => {
        slot.innerHTML = `<ins class="adsbygoogle" style="display:block" data-ad-client="${cfg.adsenseClient}" data-ad-format="auto" data-full-width-responsive="true"></ins>`;
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      });
    }
    const promo = document.getElementById("promo");
    if (promo && (cfg.tipUrl || (cfg.affiliates && cfg.affiliates.length))) {
      let html = "";
      if (cfg.affiliates && cfg.affiliates.length) {
        html += `<h2 style="margin-top:0">Recommended</h2><div class="aff">` +
          cfg.affiliates.map((a) => `<a href="${a.url}" rel="sponsored noopener" target="_blank"><strong>${a.title}</strong><br><span class="note">${a.text || ""}</span></a>`).join("") +
          `</div>`;
      }
      if (cfg.tipUrl) {
        html += `<p style="margin-bottom:0">Found this calculator useful? It's free and ad-light thanks to supporters. <a class="btn" href="${cfg.tipUrl}" target="_blank" rel="noopener">☕ Buy me a coffee</a></p>`;
      }
      promo.innerHTML = html;
      promo.hidden = false;
    }
  });
})();
