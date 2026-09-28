// Daily Target — combine six numbers with + − × ÷ to hit the day's target.
(function () {
  const EPOCH = Date.UTC(2026, 8, 28); // puzzle #1
  const today = new Date();
  const dayNo = Math.floor((Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()) - EPOCH) / 864e5) + 1;
  const params = new URLSearchParams(location.search);
  const num = Math.max(1, parseInt(params.get("n"), 10) || dayNo); // ?n=12 replays an old puzzle

  function rng(seed) { // mulberry32
    return () => {
      seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  const OPS = {
    "+": (a, b) => a + b,
    "−": (a, b) => (a > b ? a - b : null),
    "×": (a, b) => (a > 1 && b > 1 ? a * b : null),
    "÷": (a, b) => (b > 1 && a % b === 0 ? a / b : null),
  };

  // Build the puzzle: pick numbers, then make a target from a random valid calculation so it's always solvable.
  function makePuzzle(n) {
    const r = rng(n * 7919 + 17);
    const pick = (arr) => arr.splice(Math.floor(r() * arr.length), 1)[0];
    const large = [25, 50, 75, 100], small = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10];
    const bigCount = 1 + Math.floor(r() * 2);
    const nums = [];
    for (let i = 0; i < bigCount; i++) nums.push(pick(large));
    while (nums.length < 6) nums.push(pick(small));
    for (let tries = 0; tries < 5000; tries++) {
      const pool = nums.slice();
      let steps = 0, best = null;
      while (pool.length > 1 && steps < 5) {
        const a = pick(pool), b = pick(pool);
        const opKeys = Object.keys(OPS), op = opKeys[Math.floor(r() * 4)];
        const v = OPS[op](Math.max(a, b), Math.min(a, b));
        if (v === null) { pool.push(a, b); steps++; continue; }
        pool.push(v); steps++;
        if (v >= 101 && v <= 999 && pool.length <= 3) best = v;
      }
      if (best) return { nums: nums.sort((a, b) => b - a), target: best };
    }
    return { nums, target: 100 + (n % 800) };
  }

  const { nums, target } = makePuzzle(num);
  const KEY = "daily-target-" + num;
  const $ = (id) => document.getElementById(id);
  let tiles, history, sel, op, done;

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; }
  }
  function save(result) {
    try {
      localStorage.setItem(KEY, JSON.stringify(result));
      if (result.diff === 0 && num === dayNo) {
        const s = JSON.parse(localStorage.getItem("daily-target-streak") || '{"last":0,"count":0}');
        s.count = s.last === num - 1 ? s.count + 1 : s.last === num ? s.count : 1;
        s.last = num;
        localStorage.setItem("daily-target-streak", JSON.stringify(s));
      }
    } catch (e) { /* storage unavailable — game still works */ }
  }
  function streak() {
    try {
      const s = JSON.parse(localStorage.getItem("daily-target-streak") || "null");
      return s && s.last >= dayNo - 1 ? s.count : 0;
    } catch (e) { return 0; }
  }

  function reset() {
    tiles = nums.map((v, i) => ({ v, id: i, used: false }));
    history = []; sel = null; op = null; done = false;
    render();
  }

  function closest() {
    return tiles.filter((t) => !t.used).reduce((b, t) => (Math.abs(t.v - target) < Math.abs(b - target) ? t.v : b), Infinity);
  }

  function stars(diff) { return diff === 0 ? 3 : diff <= 5 ? 2 : diff <= 10 ? 1 : 0; }

  function finish(value) {
    done = true;
    const diff = Math.abs(value - target);
    const result = { value, diff, steps: history.length, lines: history.map((h) => h.text) };
    save(result);
    showResult(result);
    render();
  }

  function showResult(res) {
    const s = stars(res.diff);
    $("result").hidden = false;
    $("verdict").textContent = res.diff === 0 ? `🎯 Exactly ${target} in ${res.steps} step${res.steps === 1 ? "" : "s"}!` :
      `You reached ${res.value} — ${res.diff} away.`;
    $("stars").textContent = "⭐".repeat(s) + "☆".repeat(3 - s);
    $("working").textContent = res.lines.join("\n");
    const st = streak();
    $("streak").textContent = st > 1 ? `🔥 ${st}-day streak` : "";
  }

  function shareText() {
    const res = load();
    if (!res) return "";
    const s = stars(res.diff);
    return `Daily Target #${num} ${"⭐".repeat(s)}${"☆".repeat(3 - s)}\n` +
      (res.diff === 0 ? `🎯 Hit ${target} in ${res.steps} steps` : `Got within ${res.diff} of ${target}`) +
      `\n${"🟩".repeat(res.steps)}${res.diff === 0 ? "🎯" : "⬜"}\n${location.origin}${location.pathname}`;
  }

  function render() {
    document.querySelector(".game").classList.toggle("done", done);
    $("target").textContent = target;
    $("num").textContent = `#${num}`;
    $("tiles").innerHTML = tiles.map((t) =>
      `<button class="tile${t.used ? " used" : ""}${sel === t.id ? " sel" : ""}" data-id="${t.id}" ${t.used || done ? "disabled" : ""}>${t.v}</button>`).join("");
    document.querySelectorAll(".op").forEach((b) => { b.classList.toggle("sel", b.dataset.op === op); b.disabled = done; });
    $("log").textContent = history.map((h) => h.text).join("\n") || "Pick a number, an operation, then another number.";
    $("undo").disabled = done || !history.length;
    $("submit").disabled = done;
    const c = closest();
    $("submit").textContent = isFinite(c) ? `I'm done — submit ${c}` : "Submit";
  }

  function clickTile(id) {
    if (done) return;
    const t = tiles.find((x) => x.id === id);
    if (sel === null || op === null) { sel = sel === id ? null : id; render(); return; }
    if (id === sel) { sel = null; op = null; render(); return; }
    const a = tiles.find((x) => x.id === sel);
    const hi = Math.max(a.v, t.v), lo = Math.min(a.v, t.v);
    // Keep the order the player chose, but allow − and ÷ in whichever order is valid
    let v = OPS[op](a.v, t.v), text = `${a.v} ${op} ${t.v} = ${v}`;
    if (v === null && (op === "−" || op === "÷")) { v = OPS[op](hi, lo); text = `${hi} ${op} ${lo} = ${v}`; }
    if (v === null || v === undefined) {
      $("log").textContent = op === "÷" ? "Division must give a whole number." : op === "×" ? "Multiplying by 1 wastes a number!" : "Results must be positive.";
      sel = null; op = null; setTimeout(render, 1400); return;
    }
    a.used = true; t.used = true;
    const nt = { v, id: tiles.length, used: false };
    tiles.push(nt);
    history.push({ text, consumed: [a.id, t.id], made: nt.id });
    sel = null; op = null;
    if (v === target) finish(v); else render();
  }

  function undo() {
    const h = history.pop();
    if (!h) return;
    tiles = tiles.filter((t) => t.id !== h.made);
    h.consumed.forEach((id) => { tiles.find((t) => t.id === id).used = false; });
    render();
  }

  function countdown() {
    const now = new Date(), next = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
    const s = Math.floor((next - now) / 1000);
    $("next").textContent = `Next puzzle in ${String(Math.floor(s / 3600)).padStart(2, "0")}:${String(Math.floor(s / 60) % 60).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  }

  document.addEventListener("DOMContentLoaded", () => {
    reset();
    $("tiles").addEventListener("click", (e) => { const b = e.target.closest(".tile"); if (b) clickTile(+b.dataset.id); });
    document.querySelectorAll(".op").forEach((b) => b.addEventListener("click", () => {
      if (sel === null || done) return; op = op === b.dataset.op ? null : b.dataset.op; render();
    }));
    $("undo").addEventListener("click", undo);
    $("reset").addEventListener("click", () => { if (!done) reset(); });
    $("submit").addEventListener("click", () => { const c = closest(); if (isFinite(c)) finish(c); });
    $("share").addEventListener("click", async () => {
      const text = shareText();
      try {
        if (navigator.share) await navigator.share({ text });
        else { await navigator.clipboard.writeText(text); $("share").textContent = "Copied! Paste it anywhere"; }
      } catch (e) { /* user cancelled */ }
    });
    const prev = load();
    if (prev) { done = true; showResult(prev); render(); }
    if (num > 1) $("archive").innerHTML = `<a href="?n=${num - 1}">← Yesterday's puzzle</a>`;
    countdown(); setInterval(countdown, 1000);
  });
})();
