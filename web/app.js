/* 珞珈机试 OJ —— 前端应用 */
(() => {
  "use strict";

  const $ = (sel, el = document) => el.querySelector(sel);
  const $$ = (sel, el = document) => Array.from(el.querySelectorAll(sel));
  const MAIN = $("#main");
  const NAV = $("#problemNav");

  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  };

  const state = {
    meta: null,
    index: null,
    problems: [],
    byId: new Map(),
    years: [],
    progress: {},
    langs: {},
    stats: {},
    current: null,
    problem: null,
    tab: "statement",
    lang: "python",
    search: "",
    collapsed: new Set(store.get("whuoj:collapsed", [])),
    result: null,
    busy: false,
    submissions: [],
  };

  const DIFF = ["", "⭐", "⭐⭐", "⭐⭐⭐"];
  const STATUS_TEXT = { AC: "通过", WA: "答案错误", TLE: "运行超时", RE: "运行错误", CE: "编译错误", OLE: "输出超限" };
  const STATUS_CLASS = { AC: "AC", WA: "WA", TLE: "TLE", RE: "RE", CE: "CE", OLE: "OLE" };

  /* ---------------- boot ---------------- */
  async function boot() {
    bindChrome();
    try {
      const res = await fetch("/api/meta");
      if (!res.ok) throw new Error("无法连接评测服务");
      const data = await res.json();
      state.meta = data;
      state.index = data.index;
      state.problems = data.index.problems;
      state.years = data.index.years;
      state.progress = data.progress || {};
      state.langs = data.languages || {};
      state.stats = data.stats || {};
      state.byId = new Map(state.problems.map((p) => [p.id, p]));
      const defLang = state.langs.cpp?.available ? "cpp" : "python";
      state.lang = store.get("whuoj:lang", defLang);
      if (!state.langs[state.lang] || !state.langs[state.lang].available) state.lang = "python";
      renderUser();
      renderTopStat();
      renderNav();
      route();
    } catch (e) {
      MAIN.innerHTML = `<div class="panel" style="max-width:560px;margin:80px auto;text-align:center;padding:40px">
        <h2 style="font-family:var(--serif);margin-top:0">评测服务未启动</h2>
        <p style="color:var(--muted);font-size:13px;line-height:1.9">请先在项目目录运行 <code>run.bat</code> 或 <code>python server.py</code>，然后刷新页面。</p>
        <p style="color:#b3382e;font-size:12px">${esc(e.message)}</p></div>`;
    }
  }

  function bindChrome() {
    $("#menuBtn").addEventListener("click", () => document.body.classList.toggle("nav-open"));
    $("#sidebarMask").addEventListener("click", () => document.body.classList.remove("nav-open"));
    $("#userBtn").addEventListener("click", () => {
      const cur = store.get("whuoj:nickname", "游客");
      const name = prompt("输入一个昵称（仅保存在本机，用于提交记录）", cur);
      if (name === null) return;
      const v = name.trim().slice(0, 24) || "游客";
      store.set("whuoj:nickname", v);
      renderUser();
      toast("昵称已保存");
    });
    const input = $("#searchInput");
    input.addEventListener("input", () => {
      state.search = input.value.trim();
      renderNav();
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { input.value = ""; state.search = ""; renderNav(); }
    });
    window.addEventListener("hashchange", route);
  }

  function renderUser() {
    $("#userName").textContent = store.get("whuoj:nickname", "游客");
  }

  function renderTopStat() {
    const total = state.problems.filter((p) => p.type === "program").length;
    const solved = Object.values(state.progress).filter((v) => v === "AC").length;
    $("#topStat").innerHTML = `已通过 <b>${solved}</b> / ${total} · 提交 <b>${state.stats.submissions || 0}</b> 次`;
  }

  /* ---------------- routing ---------------- */
  function route() {
    const h = location.hash.replace(/^#/, "") || "/";
    document.body.classList.remove("nav-open");
    if (h === "/" || h === "") return renderDashboard();
    if (h === "/about") return renderAbout();
    const m = h.match(/^\/p\/([a-z0-9-]+)$/);
    if (m) return openProblem(m[1]);
    renderDashboard();
  }

  function go(hash) { location.hash = hash; }

  async function openProblem(pid) {
    const meta = state.byId.get(pid);
    if (!meta) { renderDashboard(); return; }
    state.current = pid;
    state.tab = "statement";
    state.result = null;
    state.busy = false;
    store.set("whuoj:last", pid);
    MAIN.scrollTop = 0;
    document.title = `${meta.id.toUpperCase()} ${meta.title} · 珞珈机试 OJ`;
    renderNav();
    MAIN.innerHTML = `<div class="panel" style="padding:60px;text-align:center;color:var(--muted);font-size:13px">正在载入题目…</div>`;
    try {
      const res = await fetch(`/api/problem/${pid}`);
      if (!res.ok) throw new Error("题目载入失败");
      const prob = await res.json();
      if (state.current !== pid) return;
      state.problem = prob;
      renderProblem(prob);
    } catch (e) {
      MAIN.innerHTML = `<div class="panel" style="padding:40px;color:#b3382e">${esc(e.message)}</div>`;
    }
  }

  /* ---------------- sidebar ---------------- */
  function renderNav() {
    const q = state.search.toLowerCase();
    if (q) {
      const hits = state.problems.filter((p) =>
        p.id.includes(q) || p.title.toLowerCase().includes(q) || p.tags.join(" ").toLowerCase().includes(q));
      NAV.innerHTML = `<div class="year-group"><div class="year-head" style="cursor:default">搜索结果<span class="year-count">${hits.length}</span></div>
        <div class="year-list">${hits.map(probLink).join("") || `<div class="empty-mini">没有匹配的题目</div>`}</div></div>`;
      return;
    }
    NAV.innerHTML = state.years.map((y) => {
      const list = y.problems.map((id) => state.byId.get(id)).filter(Boolean);
      const solved = list.filter((p) => state.progress[p.id] === "AC").length;
      const pct = list.length ? Math.round((solved / list.length) * 100) : 0;
      const collapsed = state.collapsed.has(String(y.year));
      return `<div class="year-group ${collapsed ? "collapsed" : ""}" data-year="${y.year}">
        <button class="year-head" data-toggle="${y.year}">
          <svg class="chev" width="12" height="12" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          <span>${y.year} 年</span>
          <span class="year-progress" title="${solved}/${list.length}"><i style="width:${pct}%"></i></span>
          <span class="year-count">${solved}/${list.length}</span>
        </button>
        <div class="year-list">${list.map(probLink).join("")}</div>
      </div>`;
    }).join("");

    $$("[data-toggle]", NAV).forEach((btn) => btn.addEventListener("click", () => {
      const y = btn.dataset.toggle;
      if (state.collapsed.has(y)) state.collapsed.delete(y); else state.collapsed.add(y);
      store.set("whuoj:collapsed", [...state.collapsed]);
      renderNav();
    }));
  }

  function probLink(p) {
    const st = state.progress[p.id];
    const cls = st === "AC" ? "ac" : st === "TRIED" ? "tried" : "";
    return `<a class="prob-link ${state.current === p.id ? "active" : ""}" href="#/p/${p.id}" data-pid="${p.id}">
      <span class="pid">${p.id.toUpperCase()}</span>
      <span class="ptitle">${esc(p.title)}</span>
      <span class="pstat ${cls}"></span></a>`;
  }

  /* ---------------- dashboard ---------------- */
  function renderDashboard() {
    state.current = null;
    state.problem = null;
    document.title = "珞珈机试 OJ · WHU CS 考研机试";
    renderNav();
    const total = state.problems.filter((p) => p.type === "program").length;
    const solved = Object.values(state.progress).filter((v) => v === "AC").length;
    const pct = total ? Math.round((solved / total) * 100) : 0;
    const last = store.get("whuoj:last", "");
    const years = state.years.map((y) => {
      const list = y.problems.map((id) => state.byId.get(id)).filter(Boolean);
      const prog = list.filter((p) => p.type === "program");
      const done = prog.filter((p) => state.progress[p.id] === "AC").length;
      return { year: y.year, total: list.length, progTotal: prog.length, done, pct: prog.length ? Math.round(done / prog.length * 100) : 0 };
    });

    MAIN.innerHTML = `
      <section class="hero">
        <div class="hero-eyebrow">Wuhan University · Computer Science</div>
        <h1>把历年真题，刷成自己的底气。</h1>
        <p>2014–2025 年武汉大学计算机学院考研复试机试真题，按年份整理为可在线评测的题目。每道题的样例与测试数据均由本 OJ 重新生成，覆盖边界与易错情形。</p>
        <div class="hero-stats">
          <div class="hero-stat"><b>${total}</b><span>编程题</span></div>
          <div class="hero-stat"><b>${solved}</b><span>已通过</span></div>
          <div class="hero-stat"><b>${pct}%</b><span>完成度</span></div>
        </div>
        <div class="hero-actions">
          ${last ? `<button class="btn btn-light" data-continue>继续上次</button>` : ""}
          <button class="btn btn-primary" data-random>随机一题</button>
        </div>
      </section>

      <div class="section-head"><h2>按年份</h2><span>点击年份卡片，从该年第一道未通过的题开始</span></div>
      <div class="year-grid">
        ${years.map((y) => `<a class="year-card" href="#/year/${y.year}" data-year-card="${y.year}">
          <div class="year-card-top"><b>${y.year}</b><span>${y.total} 题</span></div>
          <div class="year-bar"><i style="width:${y.pct}%"></i></div>
          <div class="year-card-foot"><span>${y.done} / ${y.progTotal} 编程题通过</span><span class="ok">${y.pct}%</span></div>
        </a>`).join("")}
      </div>

      <div class="dash-cols">
        <div class="panel">
          <h3>最近提交</h3>
          <div class="sub">你的每一次评测都会记录在本机</div>
          ${recentHTML()}
        </div>
        <div class="panel">
          <h3>使用提示</h3>
          <div class="sub">关于这套 OJ</div>
          <ul class="tips-list">
            <li>题面来自开源真题仓库，样例与隐藏测试由参考解生成并交叉校验。</li>
            <li>C / C++ 需本机安装 <b>g++</b> 才会启用；Python 3 开箱即用。</li>
            <li>提交后按测试点计分；样例也计入测试点，避免“样例过、隐藏点全错”。</li>
            <li>代码与昵称只保存在本机浏览器和 <code>data/</code> 目录，不会上传。</li>
          </ul>
        </div>
      </div>`;

    $$("[data-random]").forEach((b) => b.addEventListener("click", () => {
      const pool = state.problems.filter((p) => p.type === "program" && state.progress[p.id] !== "AC");
      const arr = pool.length ? pool : state.problems.filter((p) => p.type === "program");
      const pick = arr[Math.floor(Math.random() * arr.length)];
      if (pick) go(`#/p/${pick.id}`);
    }));
    $$("[data-continue]").forEach((b) => b.addEventListener("click", () => go(`#/p/${last}`)));
    $$("[data-year-card]").forEach((a) => a.addEventListener("click", (e) => {
      e.preventDefault();
      const y = a.dataset.yearCard;
      const list = state.years.find((x) => String(x.year) === y);
      if (!list) return;
      const probs = list.problems.map((id) => state.byId.get(id)).filter((p) => p.type === "program");
      const next = probs.find((p) => state.progress[p.id] !== "AC") || probs[0];
      if (next) go(`#/p/${next.id}`);
    }));
    $$("[data-open-sub]", MAIN).forEach((el) => el.addEventListener("click", () => go(`#/p/${el.dataset.openSub}`)));
  }

  function recentHTML() {
    const rows = state.stats.recent || [];
    if (!rows.length) return `<div class="empty-mini">还没有提交记录，选一道题开始吧。</div>`;
    return rows.map((r) => {
      const p = state.byId.get(r.problemId);
      return `<div class="recent-row" data-open-sub="${r.problemId}" style="cursor:pointer">
        <span class="sub-status ${STATUS_CLASS[r.status] || ""}">${STATUS_TEXT[r.status] || r.status}</span>
        <span class="rid">${(r.problemId || "").toUpperCase()}</span>
        <span class="rname">${esc(p ? p.title : r.problemId)}</span>
        <span class="rtime">${timeAgo(r.ts)}</span>
      </div>`;
    }).join("");
  }

  /* ---------------- problem page ---------------- */
  function renderProblem(prob) {
    const isEssay = prob.type === "essay";
    const st = state.progress[prob.id];
    const statusChip = isEssay ? `<span class="status-chip none">主观题</span>` :
      st === "AC" ? `<span class="status-chip ac">已通过</span>` :
      st === "TRIED" ? `<span class="status-chip tried">尝试过</span>` :
      `<span class="status-chip none">未尝试</span>`;
    const tags = prob.tags.map((t, i) => `<span class="tag ${i === 0 ? "jade" : ""}">${esc(t)}</span>`).join("");
    const stars = Array.from({ length: 3 }, (_, i) => i < prob.difficulty ? "★" : `<span class="off">★</span>`).join("");

    MAIN.innerHTML = `
      <div class="prob-head">
        <span class="prob-id">${prob.id.toUpperCase()}</span>
        <h1 class="prob-title">${esc(prob.title)}</h1>
        <div class="prob-meta">
          ${tags}<span class="stars">${stars}</span>${statusChip}
          <span class="tag">${isEssay ? "不参与评测" : "时间 " + fmtLimit(prob.timeLimit)}</span>
        </div>
      </div>
      <div class="problem-layout ${isEssay ? "single" : ""}">
        <section class="statement-card">
          <div class="prob-tabs">
            <button class="tab-btn ${state.tab === "statement" ? "active" : ""}" data-tab="statement">题目</button>
            ${isEssay ? "" : `<button class="tab-btn ${state.tab === "subs" ? "active" : ""}" data-tab="subs">提交记录</button>`}
          </div>
          <div id="tabContent"></div>
        </section>
        ${isEssay ? "" : workbenchHTML(prob)}
      </div>
      ${isEssay ? "" : `<button class="mobile-jump" id="jumpBtn">写代码 ↓</button>`}`;

    $("#jumpBtn")?.addEventListener("click", () => {
      $(".workbench")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    $$("[data-tab]", MAIN).forEach((b) => b.addEventListener("click", () => {
      state.tab = b.dataset.tab;
      $$("[data-tab]", MAIN).forEach((x) => x.classList.toggle("active", x === b));
      renderTab();
    }));

    if (!isEssay) initWorkbench(prob);
    renderTab();
  }

  function fmtLimit(t) { return t >= 10 ? "10 s" : `${Math.round(t)} s`; }

  function renderTab() {
    const box = $("#tabContent");
    if (!box || !state.problem) return;
    if (state.tab === "subs") {
      renderSubmissions(box);
      return;
    }
    box.innerHTML = `<div class="md">${renderMarkdown(state.problem.statement)}</div>` +
      (state.problem.samples.length ? samplesHTML(state.problem.samples) : "");
    bindSamples();
  }

  function samplesHTML(samples) {
    return `<div class="samples">
      <div class="samples-head"><h2>样例</h2><span>由本 OJ 生成 · 已用参考解校验</span></div>
      ${samples.map((s, i) => `<div class="sample">
        <div class="sample-head"><b>样例 ${i + 1}</b><span class="spacer"></span>
          <button class="btn btn-ghost btn-sm" data-copy-sample="${i}">复制输入</button>
          <button class="btn btn-ghost btn-sm" data-load-sample="${i}">载入自测</button>
        </div>
        <div class="sample-body">
          <div class="sample-col"><div class="lbl">输入</div><pre class="${s.input.trim() ? "" : "empty"}">${s.input.trim() ? esc(s.input.replace(/\n$/, "")) : "（无输入）"}</pre></div>
          <div class="sample-col"><div class="lbl">输出</div><pre class="${s.output.trim() ? "" : "empty"}">${s.output.trim() ? esc(s.output.replace(/\n$/, "")) : "（无输出）"}</pre></div>
        </div>
      </div>`).join("")}
    </div>`;
  }

  function bindSamples() {
    $$("[data-copy-sample]", MAIN).forEach((b) => b.addEventListener("click", async () => {
      const s = state.problem.samples[+b.dataset.copySample];
      try { await navigator.clipboard.writeText(s.input); toast("输入已复制"); }
      catch { toast("复制失败，请手动选择"); }
    }));
    $$("[data-load-sample]", MAIN).forEach((b) => b.addEventListener("click", () => {
      const s = state.problem.samples[+b.dataset.loadSample];
      const box = $("#customInput");
      if (box) {
        box.value = s.input;
        const det = $("#customBox");
        if (det) det.open = true;
        toast("已载入自测输入");
      }
    }));
  }

  /* ---------------- workbench ---------------- */
  function workbenchHTML(prob) {
    const opts = Object.entries(state.langs).map(([k, v]) =>
      `<option value="${k}" ${v.available ? "" : "disabled"} ${k === state.lang ? "selected" : ""}>${esc(v.label)}${v.available ? "" : "（未检测到）"}</option>`).join("");
    return `<section class="workbench">
      <div class="wb-head">
        <div class="dots"><i></i><i></i><i></i></div>
        <span class="wb-title">CODE</span>
        <span class="spacer"></span>
        <select class="lang-select" id="langSel" title="语言">${opts}</select>
        <button class="wb-icon" id="resetBtn" title="重置为模板">
          <svg width="15" height="15" viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 3-6.7M3 4v5h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </div>
      <div class="editor-shell">
        <div class="gutter" id="gutter"></div>
        <div class="code-area">
          <pre id="highlight" aria-hidden="true"></pre>
          <textarea id="code" spellcheck="false" autocomplete="off" autocapitalize="off" autocorrect="off"></textarea>
        </div>
      </div>
      <details class="custom-input" id="customBox">
        <summary>自测输入（运行按钮使用这里的输入）</summary>
        <textarea id="customInput" placeholder="在这里粘贴自定义输入…"></textarea>
      </details>
      <div class="wb-foot">
        <span class="hint" title="Tab 缩进 / Shift+Tab 反缩进 · 自动补全括号与引号 · Ctrl+/ 注释 · Ctrl+Enter 提交">Tab 缩进 · 自动补全 · Ctrl+Enter 提交</span>
        <span class="spacer"></span>
        <button class="btn btn-run" id="runBtn">运行</button>
        <button class="btn btn-submit" id="submitBtn">提交评测</button>
      </div>
      <div class="result-panel" id="resultPanel">
        <div class="result-empty">运行或提交后，结果会显示在这里。</div>
      </div>
    </section>`;
  }

  const OPEN_TO_CLOSE = { "(": ")", "[": "]", "{": "}", '"': '"', "'": "'", "`": "`" };
  const CLOSE_TO_OPEN = { ")": "(", "]": "[", "}": "{", '"': '"', "'": "'", "`": "`" };

  function isWordChar(ch) {
    return !!ch && /[A-Za-z0-9_$]/.test(ch);
  }

  function insertEditorText(ta, text, selStart, selEnd) {
    ta.focus();
    const start = ta.selectionStart, end = ta.selectionEnd;
    let ok = false;
    try { ok = document.execCommand("insertText", false, text); } catch { ok = false; }
    if (!ok) ta.setRangeText(text, start, end, "end");
    if (typeof selStart === "number") ta.setSelectionRange(selStart, selEnd == null ? selStart : selEnd);
  }

  function deleteEditorRange(ta, start, end) {
    ta.setSelectionRange(start, end);
    let ok = false;
    try { ok = document.execCommand("delete"); } catch { ok = false; }
    if (!ok) ta.setRangeText("", start, end, "end");
  }

  function canAutoCloseAfter(ch) {
    return !ch || /[\s)\]},;:]/.test(ch);
  }

  function handleOpenChar(ta, key) {
    const v = ta.value;
    const s = ta.selectionStart, e = ta.selectionEnd;
    const next = v[s] || "", prev = v[s - 1] || "";
    const close = OPEN_TO_CLOSE[key];

    if (s !== e) {
      const selected = v.slice(s, e);
      insertEditorText(ta, key + selected + close, s + 1, s + 1 + selected.length);
      return true;
    }
    if (key === '"' || key === "'" || key === "`") {
      if (next === key) {
        ta.setSelectionRange(s + 1, s + 1);
        return true;
      }
      if (key !== "`" && isWordChar(prev)) return false;
    }
    if (next === close) {
      insertEditorText(ta, key, s + 1, s + 1);
      return true;
    }
    if (!canAutoCloseAfter(next)) return false;
    insertEditorText(ta, key + close, s + 1, s + 1);
    return true;
  }

  function handleEnter(ta) {
    const v = ta.value;
    const s = ta.selectionStart, e = ta.selectionEnd;
    if (s !== e) return false;

    const lineStart = v.lastIndexOf("\n", s - 1) + 1;
    const line = v.slice(lineStart, s);
    const indent = (line.match(/^[ \t]*/) || [""])[0];
    const prev = v[s - 1] || "", next = v[s] || "";
    const close = OPEN_TO_CLOSE[prev];

    if (close && next === close) {
      const text = "\n" + indent + "    \n" + indent;
      insertEditorText(ta, text, s + 1 + indent.length + 4, s + 1 + indent.length + 4);
      return true;
    }
    const trimmed = line.replace(/[ \t]+$/, "");
    if (/[{\[(]$/.test(trimmed) || trimmed.endsWith(":")) {
      insertEditorText(ta, "\n" + indent + "    ");
      return true;
    }
    if (indent) {
      insertEditorText(ta, "\n" + indent);
      return true;
    }
    return false;
  }

  function handleBackspace(ta) {
    const v = ta.value;
    const s = ta.selectionStart, e = ta.selectionEnd;
    if (s !== e || s === 0) return false;
    if (OPEN_TO_CLOSE[v[s - 1]] === v[s]) {
      deleteEditorRange(ta, s - 1, s + 1);
      return true;
    }
    return false;
  }

  function applyTab(ta, shift) {
    const v = ta.value;
    const s = ta.selectionStart, e = ta.selectionEnd;

    if (s === e) {
      if (!shift) {
        const lineStart = v.lastIndexOf("\n", s - 1) + 1;
        const n = 4 - ((s - lineStart) % 4);
        insertEditorText(ta, " ".repeat(n));
        return true;
      }
      const lineStart = v.lastIndexOf("\n", s - 1) + 1;
      const before = v.slice(lineStart, s);
      const m = before.match(/ {1,4}$/);
      if (!m) return false;
      deleteEditorRange(ta, s - m[0].length, s);
      return true;
    }

    const blockStart = v.lastIndexOf("\n", s - 1) + 1;
    let blockEnd = e;
    if (blockEnd > blockStart && v[blockEnd - 1] === "\n") blockEnd--;
    const block = v.slice(blockStart, blockEnd);
    if (!block) return false;

    const lines = block.split("\n");
    const newLines = shift
      ? lines.map((l) => l.replace(/^ {1,4}/, ""))
      : lines.map((l) => "    " + l);
    const newBlock = newLines.join("\n");
    if (newBlock === block) return false;
    ta.focus();
    ta.setSelectionRange(blockStart, blockEnd);
    insertEditorText(ta, newBlock, blockStart, blockStart + newBlock.length);
    return true;
  }

  function toggleLineComment(ta, lang) {
    const v = ta.value;
    const s = ta.selectionStart, e = ta.selectionEnd;
    const start = v.lastIndexOf("\n", s - 1) + 1;
    let end = v.indexOf("\n", e);
    if (end < 0) end = v.length;
    const block = v.slice(start, end);
    const lines = block.split("\n");
    if (!lines.some((l) => l.trim())) return false;

    const marker = lang === "python" ? "#" : "//";
    const re = new RegExp("^" + marker.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + " ?");
    const nonEmpty = lines.filter((l) => l.trim());
    const all = nonEmpty.every((l) => re.test(l.trimStart()));
    const out = lines.map((l) => {
      if (!l.trim()) return l;
      const indent = (l.match(/^[ \t]*/) || [""])[0];
      const rest = l.slice(indent.length);
      if (all) return indent + rest.replace(re, "");
      return indent + marker + " " + rest;
    });
    const newBlock = out.join("\n");
    if (newBlock === block) return false;
    ta.focus();
    ta.setSelectionRange(start, end);
    insertEditorText(ta, newBlock, start, start + newBlock.length);
    return true;
  }

  function handleEditorKey(e, ta, lang, afterEdit) {
    if (e.isComposing || e.keyCode === 229) return false;
    const mod = e.ctrlKey || e.metaKey;

    if (mod && e.key === "Enter") {
      e.preventDefault();
      submit();
      return true;
    }
    if (mod && e.key === "/") {
      e.preventDefault();
      if (toggleLineComment(ta, lang)) afterEdit();
      return true;
    }
    if (mod || e.altKey) return false;

    if (e.key === "Tab") {
      e.preventDefault();
      if (applyTab(ta, e.shiftKey)) afterEdit();
      return true;
    }
    if (e.key === "Enter") {
      if (handleEnter(ta)) {
        e.preventDefault();
        afterEdit();
      }
      return false;
    }
    if (e.key === "Backspace") {
      if (handleBackspace(ta)) {
        e.preventDefault();
        afterEdit();
      }
      return false;
    }
    if (e.key.length !== 1) return false;

    const key = e.key;
    if (OPEN_TO_CLOSE[key]) {
      if (handleOpenChar(ta, key)) {
        e.preventDefault();
        afterEdit();
      }
      return false;
    }
    if (CLOSE_TO_OPEN[key]) {
      const s = ta.selectionStart, en = ta.selectionEnd;
      if (s === en && ta.value[s] === key) {
        e.preventDefault();
        ta.setSelectionRange(s + 1, s + 1);
      }
    }
    return false;
  }

  function initWorkbench(prob) {
    const ta = $("#code");
    const pre = $("#highlight");
    const gutter = $("#gutter");
    const langSel = $("#langSel");

    if (!state.langs[state.lang]?.available) state.lang = "python";
    const savedLang = store.get("whuoj:lang", state.lang);
    if (state.langs[savedLang]?.available) state.lang = savedLang;
    langSel.value = state.lang;

    const key = (lang) => `whuoj:code:${prob.id}:${lang}`;
    const template = (lang) => state.langs[lang]?.template || "";

    function paint() {
      const code = ta.value;
      pre.innerHTML = highlight(code, state.lang) + (code.endsWith("\n") ? " " : "");
      const n = code.split("\n").length;
      gutter.innerHTML = Array.from({ length: n }, (_, i) => `<div>${i + 1}</div>`).join("");
      pre.scrollTop = ta.scrollTop;
      pre.scrollLeft = ta.scrollLeft;
    }

    function setCode(text) {
      ta.value = text;
      paint();
      store.set(key(state.lang), text);
    }

    setCode(store.get(key(state.lang), template(state.lang)));

    const afterEdit = () => {
      paint();
      store.set(key(state.lang), ta.value);
    };
    ta.addEventListener("input", afterEdit);
    ta.addEventListener("scroll", () => {
      pre.scrollTop = ta.scrollTop;
      pre.scrollLeft = ta.scrollLeft;
      gutter.scrollTop = ta.scrollTop;
    });
    ta.addEventListener("keydown", (e) => handleEditorKey(e, ta, state.lang, afterEdit));
    langSel.addEventListener("change", () => {
      store.set(key(state.lang), ta.value);
      state.lang = langSel.value;
      store.set("whuoj:lang", state.lang);
      setCode(store.get(key(state.lang), template(state.lang)));
    });
    $("#resetBtn").addEventListener("click", () => {
      if (!confirm("重置为当前语言的模板？当前代码会丢失。")) return;
      setCode(template(state.lang));
      toast("已重置");
    });
    $("#runBtn").addEventListener("click", run);
    $("#submitBtn").addEventListener("click", submit);

    state.result = null;
    $("#resultPanel").innerHTML = `<div class="result-empty">运行或提交后，结果会显示在这里。</div>`;
  }

  async function run() {
    if (state.busy || !state.problem) return;
    const code = $("#code").value;
    if (!code.trim()) { toast("代码为空"); return; }
    let input = $("#customInput").value;
    if (!input && state.problem.samples.length) input = state.problem.samples[0].input;
    state.busy = true;
    const btn = $("#runBtn");
    btn.disabled = true; btn.innerHTML = `<span class="spinner"></span> 运行中`;
    try {
      const res = await fetch("/api/run", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language: state.lang, code, input }),
      }).then((r) => r.json());
      renderRunResult(res, input);
    } catch (e) {
      renderRunResult({ status: "RE", stdout: "", stderr: String(e) }, input);
    } finally {
      state.busy = false;
      btn.disabled = false; btn.textContent = "运行";
    }
  }

  async function submit() {
    if (state.busy || !state.problem || state.problem.type === "essay") return;
    const code = $("#code").value;
    if (!code.trim()) { toast("代码为空"); return; }
    state.busy = true;
    const btn = $("#submitBtn");
    btn.disabled = true; btn.innerHTML = `<span class="spinner"></span> 评测中`;
    const pid = state.problem.id;
    try {
      const res = await fetch("/api/submit", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ problemId: pid, language: state.lang, code, nickname: store.get("whuoj:nickname", "") }),
      }).then((r) => r.json());
      if (state.current !== pid) return;
      state.result = res;
      renderJudgeResult(res);
      if (res.status === "AC") {
        state.progress[pid] = "AC";
      } else if (state.progress[pid] !== "AC") {
        state.progress[pid] = "TRIED";
      }
      renderNav();
      renderTopStat();
      refreshMeta();
      if (state.tab === "subs") renderTab();
      toast(res.status === "AC" ? "恭喜，通过！" : (STATUS_TEXT[res.status] || "评测完成"));
    } catch (e) {
      state.result = { status: "RE", message: String(e) };
      renderJudgeResult(state.result);
    } finally {
      state.busy = false;
      btn.disabled = false; btn.textContent = "提交评测";
    }
  }

  async function refreshMeta() {
    try {
      const data = await fetch("/api/meta").then((r) => r.json());
      state.progress = data.progress || state.progress;
      state.stats = data.stats || state.stats;
      renderTopStat();
      renderNav();
    } catch {}
  }

  function renderJudgeResult(res) {
    const panel = $("#resultPanel");
    if (!panel) return;
    const st = res.status || "RE";
    const cls = STATUS_CLASS[st] || "";
    const dots = Array.from({ length: res.total || 0 }, (_, i) => {
      const t = (res.tests || []).find((x) => x.i === i + 1);
      return `<span class="test-dot ${t ? t.status : ""}" title="测试点 ${i + 1}${t ? " · " + (STATUS_TEXT[t.status] || t.status) : " · 未运行"}">${i + 1}</span>`;
    }).join("");
    const detail = res.message ? `<div class="result-msg">${esc(res.message)}</div>` : "";
    let extra = "";
    if (st === "CE") {
      extra = `<pre class="result-pre">${esc(res.message || "编译失败")}</pre>`;
    } else if (st === "WA") {
      const fail = (res.tests || []).find((t) => t.status === "WA");
      if (fail?.stdout) extra = `<div class="result-msg">你的输出（首个错误点）：</div><pre class="result-pre ok">${esc(fail.stdout)}</pre>`;
    } else if (st === "RE") {
      const fail = (res.tests || []).find((t) => t.status === "RE");
      if (fail?.stderr) extra = `<pre class="result-pre">${esc(fail.stderr)}</pre>`;
    }
    panel.innerHTML = `
      <div class="result-head">
        <span class="result-badge ${cls}">${st}</span>
        <span class="result-meta">${res.passed || 0} / ${res.total || 0} 测试点 · 用时 <b>${(res.time || 0).toFixed(2)} s</b></span>
      </div>
      ${dots ? `<div class="test-dots">${dots}</div>` : ""}
      ${detail}${extra}`;
  }

  function renderRunResult(res, input) {
    const panel = $("#resultPanel");
    if (!panel) return;
    const ok = res.status === "OK";
    const st = ok ? "RUN" : res.status;
    const badge = ok ? `<span class="result-badge AC">运行完成</span>` :
      `<span class="result-badge ${STATUS_CLASS[st] || "RE"}">${STATUS_TEXT[st] || st}</span>`;
    panel.innerHTML = `
      <div class="result-head">${badge}<span class="result-meta">用时 <b>${(res.time || 0).toFixed(2)} s</b>${input ? "" : " · 无输入"}</span></div>
      <div class="result-msg">标准输出</div>
      <pre class="result-pre ok">${esc(res.stdout || "（空）")}</pre>
      ${res.stderr ? `<div class="result-msg">标准错误</div><pre class="result-pre">${esc(res.stderr)}</pre>` : ""}`;
  }

  /* ---------------- submissions tab ---------------- */
  async function renderSubmissions(box) {
    box.innerHTML = `<div class="sub-empty">正在载入提交记录…</div>`;
    try {
      const data = await fetch(`/api/submissions?problemId=${state.problem.id}&limit=30`).then((r) => r.json());
      state.submissions = data.submissions || [];
    } catch { state.submissions = []; }
    if (!state.submissions.length) {
      box.innerHTML = `<div class="sub-empty">这道题还没有提交记录。</div>`;
      return;
    }
    box.innerHTML = `<div class="sub-list">${state.submissions.map((s) => `
      <div class="sub-row" data-sid="${s.id}">
        <span class="sub-status ${STATUS_CLASS[s.status] || ""}">${STATUS_TEXT[s.status] || s.status}</span>
        <span class="sub-score">${s.passed}/${s.total}</span>
        <span class="sub-lang">${esc((state.langs[s.language] || {}).label || s.language)}</span>
        <span class="sub-time">${timeAgo(s.ts)} · ${(s.runtime || 0).toFixed(2)}s</span>
      </div>`).join("")}</div>
      <div style="font-size:11.5px;color:var(--muted);margin-top:10px">点击一条记录，可把当时的代码载入编辑器。</div>`;
    $$("[data-sid]", box).forEach((row) => row.addEventListener("click", async () => {
      try {
        const rec = await fetch(`/api/submission/${row.dataset.sid}`).then((r) => r.json());
        if (!rec.code) return;
        const ta = $("#code");
        if (!ta) return;
        state.lang = rec.language;
        const sel = $("#langSel");
        if (sel) sel.value = rec.language;
        ta.value = rec.code;
        ta.dispatchEvent(new Event("input"));
        state.tab = "statement";
        $$("[data-tab]", MAIN).forEach((x) => x.classList.toggle("active", x.dataset.tab === "statement"));
        renderTab();
        toast("已载入该次提交的代码");
      } catch { toast("载入失败"); }
    }));
  }

  /* ---------------- markdown ---------------- */
  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function inlineMd(s) {
    let out = esc(s);
    out = out.replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`);
    out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    out = out.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer">$1</a>');
    return out;
  }

  function joinSmart(lines) {
    let s = "";
    for (const l of lines) {
      if (s) {
        const a = s[s.length - 1], b = l[0] || "";
        if (/[A-Za-z0-9)\].,;:!?]/.test(a) && /[A-Za-z0-9([]/.test(b)) s += " ";
      }
      s += l;
    }
    return s;
  }

  function renderMarkdown(src) {
    const lines = String(src || "").replace(/\r\n/g, "\n").split("\n");
    const out = [];
    let i = 0;
    const isBlockStart = (l) => /^(#{1,6}\s|```|>\s?|\s*[-*]\s+|\s*\d+\.\s+|---+\s*$)/.test(l);
    while (i < lines.length) {
      const line = lines[i];
      if (!line.trim()) { i++; continue; }
      if (/^```/.test(line)) {
        const buf = [];
        i++;
        while (i < lines.length && !/^```/.test(lines[i])) { buf.push(lines[i]); i++; }
        i++;
        out.push(`<pre><code>${esc(buf.join("\n"))}</code></pre>`);
        continue;
      }
      let m = line.match(/^(#{1,6})\s+(.*)$/);
      if (m) {
        const lvl = Math.min(6, m[1].length + 1);
        out.push(`<h${lvl}>${inlineMd(m[2])}</h${lvl}>`);
        i++;
        continue;
      }
      if (/^\s*---+\s*$/.test(line)) { out.push("<hr>"); i++; continue; }
      if (/^>\s?/.test(line)) {
        const buf = [];
        while (i < lines.length && /^>\s?/.test(lines[i])) { buf.push(lines[i].replace(/^>\s?/, "")); i++; }
        out.push(`<blockquote>${inlineMd(joinSmart(buf))}</blockquote>`);
        continue;
      }
      if (/^\s*[-*]\s+/.test(line) || /^\s*\d+\.\s+/.test(line)) {
        const ordered = /^\s*\d+\.\s+/.test(line);
        const itemRe = ordered ? /^\s*\d+\.\s+/ : /^\s*[-*]\s+/;
        const items = [];
        while (i < lines.length && itemRe.test(lines[i])) {
          let text = lines[i].replace(itemRe, "");
          i++;
          const subs = [];
          while (i < lines.length) {
            if (/^\s{2,}[-*]\s+/.test(lines[i])) {
              subs.push(lines[i].replace(/^\s*[-*]\s+/, ""));
              i++;
            } else if (/^\s{2,}\S/.test(lines[i]) && !/^\s*\d+\.\s+/.test(lines[i])) {
              text += " " + lines[i].trim();
              i++;
            } else break;
          }
          items.push({ text, subs });
        }
        const tag = ordered ? "ol" : "ul";
        out.push(`<${tag}>${items.map((it) =>
          `<li>${inlineMd(it.text)}${it.subs.length ? "<br>" + it.subs.map((s) => `<span class="li-sub">• ${inlineMd(s)}</span>`).join("<br>") : ""}</li>`
        ).join("")}</${tag}>`);
        continue;
      }
      if (/^\*\*[^*]+\*\*[:：]?\s*$/.test(line.trim())) {
        out.push(`<div class="md-sec">${inlineMd(line.trim())}</div>`);
        i++;
        continue;
      }
      const buf = [line];
      i++;
      while (i < lines.length && lines[i].trim() && !isBlockStart(lines[i])) {
        if (/^\*\*[^*]+\*\*[:：]?\s*$/.test(lines[i].trim())) break;
        buf.push(lines[i]);
        i++;
      }
      out.push(`<p>${inlineMd(joinSmart(buf))}</p>`);
    }
    return out.join("\n");
  }

  /* ---------------- syntax highlight ---------------- */
  const KW = {
    python: new Set("False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield".split(" ")),
    cpp: new Set("alignas alignof and and_eq asm auto bitand bitor bool break case catch char char16_t char32_t class compl const constexpr const_cast continue decltype default delete do double dynamic_cast else enum explicit export extern false float for friend goto if inline int long mutable namespace new noexcept not nullptr operator or private protected public register reinterpret_cast return short signed sizeof static static_assert static_cast struct switch template this throw true try typedef typeid typename union unsigned using virtual void volatile wchar_t while xor".split(" ")),
    c: new Set("auto break case char const continue default do double else enum extern float for goto if inline int long register restrict return short signed sizeof static struct switch typedef union unsigned void volatile while".split(" ")),
    javascript: new Set("await break case catch class const continue debugger default delete do else export extends finally for function if import in instanceof let new return static super switch this throw try typeof var void while with yield true false null undefined".split(" ")),
  };

  function highlight(code, lang) {
    const py = lang === "python";
    const re = new RegExp(
      (py ? "#[^\\n]*" : "\\/\\/[^\\n]*|\\/\\*[\\s\\S]*?\\*\\/") +
      "|(\"(?:\\\\.|[^\"\\\\])*\"|'(?:\\\\.|[^'\\\\])*')" +
      "|(\\b\\d+(?:\\.\\d+)?\\b)" +
      "|([A-Za-z_]\\w*)", "g");
    let out = "", last = 0, m;
    while ((m = re.exec(code))) {
      out += esc(code.slice(last, m.index));
      const tok = m[0];
      if ((py && tok.startsWith("#")) || (!py && (tok.startsWith("//") || tok.startsWith("/*")))) {
        out += `<span class="tok-com">${esc(tok)}</span>`;
      } else if (m[1] !== undefined) {
        out += `<span class="tok-str">${esc(tok)}</span>`;
      } else if (m[2] !== undefined) {
        out += `<span class="tok-num">${esc(tok)}</span>`;
      } else {
        const after = code.slice(re.lastIndex).match(/^\s*\(/);
        if (KW[lang]?.has(tok)) out += `<span class="tok-kw">${esc(tok)}</span>`;
        else if (after) out += `<span class="tok-fn">${esc(tok)}</span>`;
        else out += esc(tok);
      }
      last = re.lastIndex;
    }
    out += esc(code.slice(last));
    return out;
  }

  /* ---------------- about ---------------- */
  function renderAbout() {
    state.current = null;
    document.title = "关于 · 珞珈机试 OJ";
    renderNav();
    MAIN.innerHTML = `<div class="panel about-card">
      <h1>关于珞珈机试 OJ</h1>
      <p>这是一套为武汉大学计算机学院考研复试机试准备的本地在线评测系统。题目来自开源仓库
      <a href="https://github.com/XUAHW/WHU-CS-KaoYan-Machine-Test" target="_blank" rel="noreferrer">WHU-CS-KaoYan-Machine-Test</a>，
      覆盖 2014–2025 年，按年份整理；题面在原仓库基础上做了少量修订。</p>
      <h3 style="font-family:var(--serif)">数据与评测</h3>
      <ul>
        <li>每道编程题都配有参考解；样例与隐藏测试由参考解生成，并在构建时校验。</li>
        <li>默认使用“忽略行末空白、按空白分词”的比对方式；浮点题按误差比较，部分题使用特殊评测。</li>
        <li>主观题（简答 / 设计）保留题面，不参与评测。</li>
      </ul>
      <h3 style="font-family:var(--serif)">支持的语言</h3>
      <ul>
        <li>Python 3：内置运行时，开箱即用。</li>
        <li>C / C++：检测到本机 <code>g++</code> / <code>gcc</code> 时自动启用（可设置环境变量 <code>WHUOJ_GXX</code> / <code>WHUOJ_GCC</code> 指定路径）。</li>
        <li>JavaScript：检测到 Node.js 时启用。</li>
      </ul>
      <h3 style="font-family:var(--serif)">本地运行</h3>
      <p>双击 <code>run.bat</code>，或执行 <code>python server.py</code>，然后访问 <code>http://127.0.0.1:8765</code>。
      提交记录保存在 <code>data/submissions.jsonl</code>，代码只在本机。</p>
      <p style="color:var(--muted);font-size:12px">题面版权归原作者；本项目的样例、测试数据与评测系统仅用于学习交流。</p>
    </div>`;
  }

  /* ---------------- misc ---------------- */
  function timeAgo(ts) {
    if (!ts) return "";
    const t = new Date(ts).getTime();
    if (Number.isNaN(t)) return ts;
    const d = Math.max(0, Date.now() - t);
    if (d < 60e3) return "刚刚";
    if (d < 3600e3) return `${Math.floor(d / 60e3)} 分钟前`;
    if (d < 86400e3) return `${Math.floor(d / 3600e3)} 小时前`;
    if (d < 30 * 86400e3) return `${Math.floor(d / 86400e3)} 天前`;
    return new Date(ts).toLocaleDateString("zh-CN");
  }

  let toastTimer = null;
  function toast(msg) {
    const el = $("#toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), 2200);
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") document.body.classList.remove("nav-open");
  });

  boot();
})();
