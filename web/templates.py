"""HTML template for the web dashboard — i18n + Neon Glass UI."""
from __future__ import annotations


INDEX_HTML = r"""<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Username Studio</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#050510;--glass:rgba(12,15,40,.55);--glass-h:rgba(18,22,50,.7);--glass-b:rgba(255,255,255,.06);--glass-bh:rgba(255,255,255,.12);--blur:blur(20px) saturate(1.4);--cyan:#00e5ff;--purple:#a855f7;--pink:#f43f5e;--blue:#3b82f6;--green:#10b981;--amber:#f59e0b;--red:#ef4444;--txt:#e2e8f0;--txt-b:#f8fafc;--txt-m:#94a3b8;--txt-d:#64748b;--sidebar-bg:rgba(8,10,28,.95);--sidebar-w:260px;--r-sm:6px;--r:10px;--r-lg:14px;--glow-c:0 0 15px rgba(0,229,255,.15),0 0 40px rgba(0,229,255,.05);--glow-p:0 0 15px rgba(168,85,247,.15),0 0 40px rgba(168,85,247,.05);--shadow:0 8px 32px rgba(0,0,0,.3);--focus:0 0 0 3px rgba(0,229,255,.25);--fd:'Orbitron',sans-serif;--fb:'Outfit',sans-serif;--fm:'JetBrains Mono',monospace;--tf:150ms cubic-bezier(.4,0,.2,1);--tn:250ms cubic-bezier(.4,0,.2,1);--ts:400ms cubic-bezier(.16,1,.3,1)}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
[hidden]{display:none!important}
html{overflow-x:hidden;scroll-behavior:smooth}
body{min-height:100vh;background:radial-gradient(ellipse at 18% 0%,rgba(88,28,135,.15) 0%,transparent 50%),radial-gradient(ellipse at 82% 100%,rgba(0,100,150,.12) 0%,transparent 50%),var(--bg);background-attachment:fixed;color:var(--txt);font:14px/1.5 var(--fb),sans-serif;font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}
body::before{content:'';position:fixed;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");pointer-events:none;z-index:9999}
button,input,select,textarea{font:inherit}
.app{display:grid;grid-template-columns:var(--sidebar-w) minmax(0,1fr);min-height:100vh}
.sidebar{position:sticky;top:0;display:flex;flex-direction:column;height:100vh;padding:20px 14px 16px;background:var(--sidebar-bg);backdrop-filter:blur(30px);border-right:1px solid rgba(0,229,255,.06);color:var(--txt);overflow-y:auto;overflow-x:hidden}
.sidebar::after{content:'';position:absolute;top:0;right:0;width:1px;height:100%;background:linear-gradient(180deg,transparent,var(--cyan) 20%,var(--purple) 50%,var(--cyan) 80%,transparent);opacity:.3;pointer-events:none}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:18px;padding:0 6px 14px;border-bottom:1px solid rgba(255,255,255,.05)}
.brand-mark{display:grid;place-items:center;flex:0 0 38px;width:38px;height:38px;border-radius:var(--r);background:linear-gradient(135deg,rgba(0,229,255,.15),rgba(168,85,247,.15));border:1px solid rgba(0,229,255,.25);color:var(--cyan);font-family:var(--fd);font-size:11px;font-weight:900;box-shadow:var(--glow-c);animation:brandPulse 3s ease-in-out infinite}
@keyframes brandPulse{0%,100%{box-shadow:0 0 10px rgba(0,229,255,.15)}50%{box-shadow:0 0 20px rgba(0,229,255,.3),0 0 40px rgba(0,229,255,.1)}}
.brand-copy{display:grid;gap:2px;min-width:0}
.brand h1{color:var(--txt-b);font-family:var(--fd);font-size:15px;font-weight:700;letter-spacing:.05em}
.brand-copy>span{color:var(--txt-d);font-size:11px}
.brand .pill{margin-inline-start:auto;padding:3px 9px;border-radius:999px;background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.2);color:var(--cyan);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.lang-switch{display:flex;gap:4px;margin-bottom:16px;padding:0 6px}
.lang-btn{flex:1;padding:6px 0;border:1px solid rgba(255,255,255,.06);border-radius:var(--r-sm);background:transparent;color:var(--txt-d);font-size:11px;font-weight:600;cursor:pointer;transition:all var(--tf);text-transform:uppercase;letter-spacing:.06em}
.lang-btn:hover{background:rgba(255,255,255,.05);color:var(--txt);border-color:rgba(255,255,255,.1)}
.lang-btn.is-active{background:rgba(0,229,255,.1);border-color:rgba(0,229,255,.3);color:var(--cyan);box-shadow:0 0 10px rgba(0,229,255,.1)}
.nav{display:grid;gap:3px}
.nav button{position:relative;display:flex;align-items:center;gap:10px;width:100%;min-height:40px;padding:9px 12px;border:1px solid transparent;border-radius:var(--r);background:transparent;color:var(--txt-m);text-align:start;cursor:pointer;font-size:13px;font-weight:500;transition:all var(--tn)}
.nav button::before{content:attr(data-icon);display:grid;place-items:center;flex:0 0 24px;width:24px;height:24px;border:1px solid rgba(255,255,255,.06);border-radius:var(--r-sm);background:rgba(255,255,255,.03);color:currentColor;font-family:var(--fd);font-size:10px;font-weight:700;transition:all var(--tn)}
.nav button:hover{background:rgba(255,255,255,.04);color:var(--txt);border-color:rgba(255,255,255,.06);transform:translateX(2px)}
[dir="rtl"] .nav button:hover{transform:translateX(-2px)}
.nav button.is-active{background:rgba(0,229,255,.06);color:var(--txt-b);border-color:rgba(0,229,255,.15)}
.nav button.is-active::before{border-color:rgba(0,229,255,.3);background:rgba(0,229,255,.12);color:var(--cyan);box-shadow:0 0 8px rgba(0,229,255,.2)}
.nav button.is-active::after{content:'';position:absolute;top:50%;inset-inline-start:0;transform:translateY(-50%);width:3px;height:60%;border-radius:0 3px 3px 0;background:var(--cyan);box-shadow:0 0 8px var(--cyan)}
.donation-cta{position:relative;display:grid;align-items:center;min-height:80px;margin-top:auto;padding:14px 14px 14px 48px;border:1px solid rgba(168,85,247,.15);border-radius:var(--r);background:linear-gradient(135deg,rgba(168,85,247,.08),rgba(0,229,255,.04));color:var(--txt);text-decoration:none;overflow:hidden;transition:all var(--tn)}
.donation-cta::before{content:'\2665';position:absolute;top:50%;inset-inline-start:14px;transform:translateY(-50%);display:grid;place-items:center;width:28px;height:28px;border:1px solid rgba(244,63,94,.3);border-radius:var(--r-sm);background:rgba(244,63,94,.1);color:var(--pink);font-size:14px;transition:all var(--tn)}
.donation-cta:hover{border-color:rgba(168,85,247,.3);background:linear-gradient(135deg,rgba(168,85,247,.12),rgba(0,229,255,.06));transform:translateY(-1px);box-shadow:0 4px 20px rgba(168,85,247,.1)}
.donation-cta__copy{display:grid;gap:3px;min-width:0}
.donation-cta__label{color:var(--purple);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.donation-cta__title{color:var(--txt);font-size:13px;font-weight:600;line-height:1.3}
.donation-cta__hint{color:var(--txt-d);font-size:11px}
main{min-width:0;padding:28px 30px 40px}
.section{display:none;width:100%;max-width:1300px;animation:secIn .3s ease-out}
.section.is-active{display:block}
@keyframes secIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:20px}
.section-title{margin:0;font-family:var(--fd);font-size:24px;font-weight:700;color:var(--txt-b);letter-spacing:.03em}
.section-meta{margin-top:5px;color:var(--txt-m);font-size:13px;line-height:1.5}
.card,.panel,.toolbar,.table-wrap{border:1px solid var(--glass-b);border-radius:var(--r);background:var(--glass);backdrop-filter:var(--blur);box-shadow:var(--shadow);transition:border-color var(--tn),box-shadow var(--tn)}
.card:hover,.panel:hover{border-color:var(--glass-bh)}
.stats-grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));margin-bottom:20px}
.stat-card{position:relative;min-height:100px;padding:16px 16px 14px 20px;overflow:hidden;background:var(--glass);backdrop-filter:var(--blur);animation:cardUp .5s ease-out backwards}
.stat-card:nth-child(1){animation-delay:0s}.stat-card:nth-child(2){animation-delay:.05s}.stat-card:nth-child(3){animation-delay:.1s}.stat-card:nth-child(4){animation-delay:.15s}.stat-card:nth-child(5){animation-delay:.2s}.stat-card:nth-child(6){animation-delay:.25s}.stat-card:nth-child(7){animation-delay:.3s}.stat-card:nth-child(8){animation-delay:.35s}.stat-card:nth-child(9){animation-delay:.4s}.stat-card:nth-child(10){animation-delay:.45s}.stat-card:nth-child(11){animation-delay:.5s}.stat-card:nth-child(12){animation-delay:.55s}
@keyframes cardUp{from{opacity:0;transform:translateY(16px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}
.stat-card::before{content:'';position:absolute;inset:0 auto 0 0;width:3px;border-radius:0 3px 3px 0;background:var(--sc,var(--cyan));box-shadow:0 0 10px var(--sc,var(--cyan));transition:box-shadow var(--tn)}
.stat-card:hover::before{box-shadow:0 0 18px var(--sc,var(--cyan))}
[data-stat="total_checked"],[data-stat="last_batch_checked"]{--sc:var(--blue)}[data-stat="total_available"],[data-stat="last_batch_available"]{--sc:var(--green)}[data-stat="total_taken_invalid"]{--sc:var(--red)}[data-stat="total_unchecked"]{--sc:var(--amber)}[data-stat="total_used"]{--sc:var(--purple)}[data-stat="total_evaluated"]{--sc:var(--cyan)}[data-stat="avg_score"],[data-stat="best_score"]{--sc:var(--pink)}[data-stat="last_batch_num"],[data-stat="last_batch_count"]{--sc:var(--blue)}
.stat-label{color:var(--txt-m);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em}
.stat-value{margin-top:8px;font-family:var(--fd);font-size:26px;font-weight:700;color:var(--txt-b);white-space:nowrap}
.panel-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:10px}
.panel-title{margin:0;color:var(--txt-b);font-size:16px;font-weight:600}
.panel-caption{color:var(--txt-d);font-size:12px;white-space:nowrap}
.toolbar{display:flex;flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:14px;padding:14px}
label{display:grid;gap:5px;min-width:120px;color:var(--txt-m);font-size:12px;font-weight:500}
input,select{width:100%;min-height:38px;padding:8px 12px;border:1px solid rgba(255,255,255,.08);border-radius:var(--r-sm);background:rgba(0,0,0,.2);color:var(--txt);transition:all var(--tf)}
input::placeholder{color:var(--txt-d)}
input:hover,select:hover{border-color:rgba(255,255,255,.15)}
input:focus,select:focus{outline:0;border-color:var(--cyan);box-shadow:var(--focus),0 0 20px rgba(0,229,255,.08)}
input[type="checkbox"]{min-height:auto;width:16px;height:16px;padding:0;accent-color:var(--cyan)}
.check-label{display:inline-flex;grid-template-columns:none;align-items:center;min-width:auto;min-height:38px;gap:8px;color:var(--txt);font-size:13px;font-weight:500}
.btn{position:relative;min-height:38px;padding:8px 16px;border:1px solid rgba(255,255,255,.1);border-radius:var(--r-sm);background:rgba(255,255,255,.04);color:var(--txt);cursor:pointer;font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;transition:all var(--tn)}
.btn::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.1),transparent);opacity:0;transition:opacity var(--tf)}
.btn:hover{border-color:rgba(255,255,255,.2);background:rgba(255,255,255,.08);transform:translateY(-1px);box-shadow:0 4px 16px rgba(0,0,0,.2)}
.btn:hover::before{opacity:1}
.btn.primary{border-color:rgba(0,229,255,.4);background:linear-gradient(135deg,rgba(0,229,255,.15),rgba(0,229,255,.08));color:var(--cyan)}
.btn.primary:hover{background:linear-gradient(135deg,rgba(0,229,255,.25),rgba(0,229,255,.12));border-color:rgba(0,229,255,.6);box-shadow:var(--glow-c)}
.btn.danger{border-color:rgba(239,68,68,.3);background:rgba(239,68,68,.06);color:var(--red)}
.btn.danger:hover{background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.5);box-shadow:0 0 15px rgba(239,68,68,.15)}
.btn:disabled,.btn:disabled:hover{opacity:.4;cursor:not-allowed;transform:none;box-shadow:none}
.panel{padding:16px}
.split{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(320px,.75fr);gap:16px;align-items:start}
.table-wrap{width:100%;overflow:auto}
.table-wrap .btn{min-height:32px;padding:5px 10px;font-size:12px}
table{width:100%;border-collapse:collapse;min-width:760px;font-size:13px}
th,td{padding:11px 12px;border-bottom:1px solid rgba(255,255,255,.04);text-align:start;vertical-align:middle;white-space:nowrap}
th{background:rgba(0,0,0,.2);color:var(--txt-m);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;position:sticky;top:0;z-index:1}
tbody tr{transition:background var(--tf)}
tbody tr:hover{background:rgba(0,229,255,.03)}
td.notes{max-width:300px;overflow:hidden;text-overflow:ellipsis}
.mono{font-family:var(--fm);font-size:12px;font-weight:600;color:var(--cyan)}
.badge{display:inline-flex;align-items:center;gap:5px;min-height:24px;padding:2px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.04);color:var(--txt-m);font-size:11px;font-weight:600;white-space:nowrap}
.badge::before{content:'';display:inline-block;width:5px;height:5px;border-radius:999px;background:currentColor}
.badge.available,.badge.active{border-color:rgba(16,185,129,.3);background:rgba(16,185,129,.08);color:var(--green);box-shadow:0 0 8px rgba(16,185,129,.1)}
.badge.cooldown,.badge.warn{border-color:rgba(245,158,11,.3);background:rgba(245,158,11,.08);color:var(--amber)}
.badge.dead,.badge.invalid,.badge.checked_taken,.badge.error{border-color:rgba(239,68,68,.3);background:rgba(239,68,68,.08);color:var(--red)}
.badge.unchecked{border-color:rgba(59,130,246,.3);background:rgba(59,130,246,.08);color:var(--blue)}
.badge.used{border-color:rgba(168,85,247,.3);background:rgba(168,85,247,.08);color:var(--purple)}
.progress{height:6px;overflow:hidden;border-radius:999px;background:rgba(255,255,255,.04)}
.progress>div{width:0%;height:100%;background:linear-gradient(90deg,var(--cyan),var(--purple),var(--pink));background-size:200% 100%;animation:progShim 2s linear infinite;transition:width 300ms ease;border-radius:999px;box-shadow:0 0 10px rgba(0,229,255,.3)}
@keyframes progShim{0%{background-position:200% 0}100%{background-position:-200% 0}}
.status-line{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:10px 0;color:var(--txt-m);font-size:13px}
.empty{padding:20px;color:var(--txt-m);text-align:center}
.empty-state{display:grid;gap:4px;justify-items:center;padding:6px 0;color:var(--txt-m);white-space:normal}
.empty-state strong{color:var(--txt);font-size:13px;font-weight:600}
.empty-state span{max-width:400px;font-size:12px;line-height:1.4}
.log-box{min-height:400px;max-height:70vh;margin:0;overflow:auto;padding:16px;border:1px solid rgba(0,229,255,.08);border-radius:var(--r);background:rgba(0,0,0,.5);backdrop-filter:blur(10px);color:#a5f3fc;white-space:pre-wrap;word-break:break-word;font-family:var(--fm);font-size:12px;line-height:1.6;box-shadow:inset 0 0 40px rgba(0,0,0,.3)}
*::-webkit-scrollbar{width:6px;height:6px}*::-webkit-scrollbar-track{background:transparent}*::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:3px}*::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.2)}
.mode-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:14px}
.mode-cell{display:grid;gap:4px;min-height:70px;padding:14px;border:1px solid var(--glass-b);border-radius:var(--r);background:var(--glass);backdrop-filter:var(--blur);transition:all var(--tn)}
.mode-cell:hover{border-color:var(--glass-bh);box-shadow:var(--glow-c)}
.mode-cell span{color:var(--txt-m);font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.04em}
.mode-cell strong{color:var(--txt-b);font-size:14px;font-weight:600}
.mode-cell.is-warn{border-color:rgba(245,158,11,.2);background:rgba(245,158,11,.04)}
.selected-box{display:grid;gap:10px}
.selected-name{font-family:var(--fd);font-size:20px;font-weight:700;color:var(--cyan);text-shadow:0 0 20px rgba(0,229,255,.3)}
.auth-panel{display:grid;grid-template-columns:minmax(220px,.85fr) minmax(280px,1.2fr) minmax(320px,1.4fr);gap:14px;align-items:start;margin-bottom:14px}
.auth-summary{display:grid;gap:8px;align-content:start}
.auth-actions{display:grid;grid-template-columns:repeat(2,minmax(140px,1fr));gap:10px;align-items:end}
.auth-panel input,.auth-panel select{width:100%;min-width:0}
.auth-panel .btn{min-width:0;white-space:normal;line-height:1.2}
.config-actions{grid-template-columns:repeat(2,minmax(140px,1fr));margin-top:10px}
.accounts-auth{grid-template-columns:minmax(360px,1fr) minmax(360px,1fr)}
.accounts-auth .auth-actions{grid-template-columns:repeat(2,minmax(0,1fr))}
.orb{position:fixed;border-radius:50%;pointer-events:none;filter:blur(80px);z-index:-1;animation:orbF 20s ease-in-out infinite}
.orb--c{width:300px;height:300px;background:rgba(0,229,255,.06);top:10%;left:5%}
.orb--p{width:250px;height:250px;background:rgba(168,85,247,.05);bottom:20%;right:10%;animation-delay:-7s}
.orb--k{width:200px;height:200px;background:rgba(244,63,94,.04);top:60%;left:50%;animation-delay:-14s}
@keyframes orbF{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(30px,-20px) scale(1.1)}66%{transform:translate(-20px,30px) scale(.95)}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important}}
@media(max-width:1040px){.split{grid-template-columns:1fr}.mode-strip{grid-template-columns:repeat(2,minmax(0,1fr))}.auth-panel{grid-template-columns:1fr}}
@media(max-width:760px){.app{grid-template-columns:1fr}.sidebar{position:static;height:auto;border-right:0;border-bottom:1px solid rgba(0,229,255,.06)}.sidebar::after{display:none}.nav{grid-template-columns:repeat(2,minmax(0,1fr))}.donation-cta{margin-top:14px}main{padding:16px 14px 28px}.section-head{display:grid;gap:12px}.section-head .btn{width:100%}.toolbar{display:grid;grid-template-columns:1fr}.mode-strip{grid-template-columns:1fr}.stats-grid{grid-template-columns:1fr}.auth-actions{grid-template-columns:1fr}table{min-width:660px}}
@media(max-width:520px){.brand .pill{display:none}.nav{grid-template-columns:1fr}.section-title{font-size:20px}.stat-value{font-size:22px}}
</style>
</head>
<body>
<div class="orb orb--c"></div><div class="orb orb--p"></div><div class="orb orb--k"></div>
<div class="app">
<aside class="sidebar">
<div class="brand">
<div class="brand-mark">US</div>
<div class="brand-copy"><h1>Username Studio</h1><span data-i18n="brand.subtitle">Telegram Username Tool</span></div>
<span class="pill">local</span>
</div>
<div class="lang-switch">
<button class="lang-btn is-active" data-lang="en">EN</button>
<button class="lang-btn" data-lang="fa">FA</button>
<button class="lang-btn" data-lang="ru">RU</button>
</div>
<nav class="nav">
<button class="is-active" data-tab="dashboard" data-icon="D" data-i18n="nav.dashboard">Dashboard</button>
<button data-tab="generation" data-icon="G" data-i18n="nav.generation">Generation</button>
<button data-tab="database" data-icon="B" data-i18n="nav.database">Database</button>
<button data-tab="telegram" data-icon="T" data-i18n="nav.telegram">Telegram</button>
<button data-tab="accounts" data-icon="A" data-i18n="nav.accounts">Accounts</button>
<button data-tab="channels" data-icon="C" data-i18n="nav.channels">Channels</button>
<button data-tab="logs" data-icon="L" data-i18n="nav.logs">Logs</button>
</nav>
<a class="donation-cta" href="https://www.donationalerts.com/r/sattop02" target="_blank" rel="noopener noreferrer">
<span class="donation-cta__copy">
<span class="donation-cta__label">DonationAlerts</span>
<span class="donation-cta__title" data-i18n="donation.title">Support Username Studio</span>
<span class="donation-cta__hint" data-i18n="donation.hint">A calm contribution to development</span>
</span></a>
</aside>

<main>
<section id="dashboard" class="section is-active">
<div class="section-head"><div>
<h2 class="section-title" data-i18n="dashboard.title">Dashboard</h2>
<div class="section-meta" id="dashMeta">-</div>
</div><button class="btn" id="refreshDashboard" data-i18n="common.refresh">Refresh</button></div>
<div class="grid stats-grid" id="statsGrid"></div>
<div class="split">
<div><div class="panel-heading"><h3 class="panel-title" data-i18n="dashboard.lastBatch">Last Batch</h3><span class="panel-caption" data-i18n="dashboard.last10">last 10</span></div>
<div class="table-wrap"><table><thead><tr><th>username</th><th>score</th><th data-i18n="th.status">status</th><th>type</th><th>batch</th></tr></thead><tbody id="lastBatchRows"></tbody></table></div></div>
<div><div class="panel-heading"><h3 class="panel-title" data-i18n="dashboard.availTop">Available Top</h3><span class="panel-caption" data-i18n="dashboard.scoreDesc">score desc</span></div>
<div class="table-wrap"><table style="min-width:420px"><thead><tr><th>username</th><th>score</th><th>type</th></tr></thead><tbody id="availableTopRows"></tbody></table></div></div>
</div></section>

<section id="generation" class="section">
<div class="section-head"><div>
<h2 class="section-title" data-i18n="gen.title">Generation</h2>
<div class="section-meta" data-i18n="gen.subtitle">LM Studio + local evaluation, no Telegram actions</div>
</div></div>
<div class="panel" style="margin-bottom:14px">
<div class="status-line" style="margin:0"><span data-i18n="gen.rotationAccount">Active rotation account</span><span id="rotationAccountBadge" class="badge warn" data-i18n="status.loading">loading</span></div>
<div id="rotationAccountDetails" class="section-meta" style="margin-top:8px" data-i18n="gen.checkingAccounts">Checking account list...</div>
</div>
<div class="toolbar">
<label><span data-i18n="gen.batchSize">Batch Size</span><input id="batchSize" type="number" min="1" max="500" value="100"></label>
<label><span data-i18n="gen.minLength">Min Length</span><input id="generationMinLength" type="number" min="4" max="10" value="5"></label>
<label><span data-i18n="gen.maxLength">Max Length</span><input id="generationMaxLength" type="number" min="4" max="10" value="6"></label>
<label class="check-label"><input id="generationAllowDigits" type="checkbox"> <span data-i18n="gen.digits">digits</span></label>
<button class="btn primary" id="generateBtn" data-i18n="gen.generateBtn">Generate &amp; Evaluate</button>
</div>
<div class="panel"><div class="status-line"><span id="generationStatus" data-i18n="gen.ready">Ready to start</span><span id="generationTaskId"></span></div>
<div class="progress"><div id="generationProgress"></div></div></div>
<div class="table-wrap" style="margin-top:14px"><table><thead><tr><th>username</th><th>score</th><th data-i18n="th.status">status</th><th>generation_type</th><th>batch</th></tr></thead><tbody id="generationRows"></tbody></table></div>
</section>

<section id="database" class="section">
<div class="section-head"><div>
<h2 class="section-title" data-i18n="db.title">Username Database</h2>
<div class="section-meta" id="databaseMeta" data-i18n="db.limitOn">Output limit enabled</div>
</div></div>
<div class="toolbar">
<label><span data-i18n="common.status">Status</span>
<select id="dbStatus"><option value="all" data-i18n="db.all">All</option><option value="available">available</option><option value="unchecked">unchecked</option><option value="used">used</option><option value="taken_invalid">checked_taken/invalid</option><option value="checked">checked</option></select></label>
<label><span data-i18n="common.search">Search</span><input id="dbSearch" placeholder="username"></label>
<label>Min score<input id="dbMinScore" type="number" step="0.1" min="0" max="10"></label>
<label>Top N<input id="dbLimit" type="number" min="1" max="200" value="50"></label>
<label class="check-label"><input id="dbLastBatch" type="checkbox"> last batch</label>
<button class="btn primary" id="loadDatabase" data-i18n="common.show">Show</button>
</div>
<div class="table-wrap"><table><thead><tr><th>username</th><th>score</th><th data-i18n="th.status">status</th><th>generation_type</th><th>batch</th><th>checked_at</th><th>notes</th></tr></thead><tbody id="databaseRows"></tbody></table></div>
</section>

<section id="telegram" class="section">
<div class="section-head"><div>
<h2 class="section-title" data-i18n="tg.title">Telegram Check</h2>
<div class="section-meta" id="telegramMeta" data-i18n="tg.subtitle">Checks only through accounts from the Accounts tab</div>
</div></div>
<div class="mode-strip">
<div class="mode-cell"><span data-i18n="tg.mainAccount">Main Account</span><strong data-i18n="tg.channelCreation">channel creation</strong></div>
<div class="mode-cell"><span data-i18n="tg.liveCheck">Live Check</span><strong data-i18n="tg.sessionsOnly">sessions/ only</strong></div>
<div class="mode-cell"><span data-i18n="tg.mode">Mode</span><strong id="tgModeLabel">dry-run</strong></div>
<div class="mode-cell is-warn"><span>Confirm</span><strong id="tgConfirmState" data-i18n="tg.checkForLive">CHECK for live</strong></div>
</div>
<div class="auth-panel">
<div class="panel auth-summary">
<div class="status-line" style="margin:0"><span data-i18n="tg.mainCreation">Main creation account</span><span id="tgAuthBadge" class="badge warn" data-i18n="tg.checking">checking</span></div>
<div id="tgAuthDetails" class="section-meta" data-i18n="tg.checkingSession">Checking session...</div>
<button class="btn" id="tgAuthRefresh" data-i18n="tg.refreshStatus">Refresh Status</button>
</div>
<div class="panel">
<div class="status-line" style="margin:0"><span data-i18n="tg.apiMain">Telegram API main account</span><span id="tgConfigBadge" class="badge warn" data-i18n="status.loading">loading</span></div>
<div class="auth-actions config-actions">
<label>API ID<input id="tgApiId" inputmode="numeric" autocomplete="off" placeholder="1234567"></label>
<label>API HASH<input id="tgApiHash" type="password" autocomplete="off" placeholder="leave empty if already saved"></label>
<label><span data-i18n="common.phone">Phone</span><input id="tgConfigPhone" autocomplete="tel" placeholder="+79990000000"></label>
<button class="btn primary" id="tgSaveConfig" data-i18n="tg.saveApi">Save API</button>
</div>
<div class="section-meta" id="tgConfigMessage" style="margin-top:10px" data-i18n="tg.apiNote">This account is only for channel creation, not for live checks.</div>
</div>
<div class="panel">
<div class="status-line" style="margin:0 0 10px"><span data-i18n="tg.loginMain">Login to main account</span></div>
<div class="auth-actions">
<label><span data-i18n="common.phone">Phone</span><input id="tgPhone" placeholder="+79990000000 or from .env"></label>
<button class="btn" id="tgSendCode" data-i18n="common.sendCode">Send Code</button>
<label><span data-i18n="common.code">Code</span><input id="tgCode" inputmode="numeric" autocomplete="one-time-code" placeholder="12345"></label>
<button class="btn primary" id="tgConfirmCode" data-i18n="common.login">Login</button>
<label><span data-i18n="common.2fa">2FA Password</span><input id="tgPassword" type="password" autocomplete="current-password" placeholder="if enabled"></label>
<button class="btn" id="tgConfirmPassword" data-i18n="tg.confirm2fa">Confirm 2FA</button>
<button class="btn" id="tgCancelAuth" data-i18n="tg.resetLogin">Reset Login</button>
<button class="btn danger" id="tgResetSession" data-i18n="tg.resetSession">Reset Session</button>
</div>
<div class="section-meta" id="tgAuthMessage" style="margin-top:10px" data-i18n="tg.codeNote">Code and password are not saved in the browser.</div>
</div>
</div>
<div class="toolbar">
<label><span data-i18n="tg.manualUsername">Manual username</span><input id="tgManualUsername" placeholder="@username"></label>
<label><span data-i18n="tg.checkLimit">Check limit</span><input id="tgLimit" type="number" min="1" max="30" value="10"></label>
<label>Min score<input id="tgMinScore" type="number" step="0.1" min="0" max="10" value="6"></label>
<label class="check-label"><input id="tgDryRun" type="checkbox" checked> dry-run</label>
<label><span data-i18n="tg.liveConfirm">Live confirm</span><input id="tgConfirm" placeholder="CHECK"></label>
<button class="btn" id="tgPreviewBtn" data-i18n="tg.preview">Preview</button>
<button class="btn primary" id="tgCheckBtn" data-i18n="tg.previewSel">Preview Selected</button>
</div>
<div class="panel"><div class="status-line"><span id="telegramStatus" data-i18n="tg.candidatesNotLoaded">Candidates not loaded</span><span id="telegramTaskId"></span></div>
<div class="progress"><div id="telegramProgress"></div></div></div>
<div class="split" style="margin-top:14px">
<div class="table-wrap"><table><thead><tr><th></th><th>username</th><th>score</th><th data-i18n="th.status">status</th><th>type</th><th>batch</th></tr></thead><tbody id="telegramRows"></tbody></table></div>
<div class="table-wrap"><table style="min-width:420px"><thead><tr><th>skip</th><th>reason</th></tr></thead><tbody id="telegramSkippedRows"></tbody></table></div>
</div></section>

<section id="accounts" class="section">
<div class="section-head"><div>
<h2 class="section-title" data-i18n="acc.title">Accounts</h2>
<div class="section-meta" id="accountsMeta" data-i18n="acc.subtitle">Accounts for live-check rotation only</div>
</div><button class="btn primary" id="accountAddBtn" data-i18n="acc.add">+ Add</button></div>
<div class="auth-panel accounts-auth" id="accountsAuthPanel">
<div class="panel">
<div class="status-line" style="margin:0"><span data-i18n="acc.newAccount">New Account</span><span id="accountAuthBadge" class="badge warn" data-i18n="acc.notStarted">not started</span></div>
<div class="auth-actions config-actions">
<label>API ID<input id="accountApiId" inputmode="numeric" autocomplete="off" placeholder="1234567"></label>
<label>API HASH<input id="accountApiHash" type="password" autocomplete="off" placeholder="api_hash"></label>
<label><span data-i18n="common.phone">Phone</span><input id="accountPhone" autocomplete="tel" placeholder="+79990000000"></label>
<button class="btn primary" id="accountSendCode" data-i18n="common.sendCode">Send Code</button>
</div>
<div class="section-meta" id="accountAuthMessage" style="margin-top:10px" data-i18n="acc.apiNote">API ID, API Hash and phone are saved locally after successful login.</div>
</div>
<div class="panel">
<div class="status-line" style="margin:0 0 10px"><span data-i18n="acc.loginConfirm">Login Confirmation</span></div>
<div class="auth-actions">
<label><span data-i18n="acc.tgCode">Telegram Code</span><input id="accountCode" inputmode="numeric" autocomplete="one-time-code" placeholder="12345"></label>
<button class="btn primary" id="accountConfirmCode" data-i18n="common.login">Login</button>
<label id="accountPasswordLabel" hidden><span data-i18n="common.2fa">2FA Password</span><input id="accountPassword" type="password" autocomplete="current-password" placeholder="if enabled"></label>
<button class="btn" id="accountConfirmPassword" hidden data-i18n="tg.confirm2fa">Confirm 2FA</button>
<button class="btn" id="accountCancelAuth" data-i18n="tg.resetLogin">Reset Login</button>
</div></div>
</div>
<div class="table-wrap"><table><thead><tr><th data-i18n="th.phone">phone</th><th data-i18n="th.status">status</th><th>cooldown</th><th>user</th><th data-i18n="th.lastError">last error</th><th></th></tr></thead><tbody id="accountsRows"></tbody></table></div>
</section>

<section id="channels" class="section">
<div class="section-head"><div>
<h2 class="section-title" data-i18n="ch.title">Channel Creation</h2>
<div class="section-meta" data-i18n="ch.subtitle">Creation via main account; checking is separate</div>
</div></div>
<div class="toolbar">
<label>Min score<input id="channelMinScore" type="number" step="0.1" min="0" max="10"></label>
<label>Top N<input id="channelLimit" type="number" min="1" max="100" value="20"></label>
<button class="btn" id="loadChannels" data-i18n="common.refresh">Refresh</button>
</div>
<div class="split">
<div class="table-wrap"><table><thead><tr><th>username</th><th>score</th><th data-i18n="th.status">status</th><th>type</th><th></th></tr></thead><tbody id="channelRows"></tbody></table></div>
<div class="panel selected-box">
<div class="selected-name" id="selectedChannelName">-</div>
<div class="section-meta" id="selectedChannelScore">score: -</div>
<label><span data-i18n="ch.channelName">Channel Name</span><input id="channelTitle" placeholder="optional"></label>
<label class="check-label"><input id="channelDryRun" type="checkbox" checked> dry-run</label>
<label id="channelConfirmLabel"><span id="chConfirmText" data-i18n="ch.useUsername">Use username? (y/n)</span><input id="channelConfirm" placeholder="y"></label>
<button class="btn primary" id="createChannelBtn" data-i18n="ch.create">Create</button>
<div class="status-line"><span id="channelStatus" data-i18n="ch.notSelected">Username not selected</span><span id="channelTaskId"></span></div>
<div class="progress"><div id="channelProgress"></div></div>
</div></div></section>

<section id="logs" class="section">
<div class="section-head"><div>
<h2 class="section-title" data-i18n="logs.title">Logs</h2>
<div class="section-meta" id="logsMeta">logs/logs.txt</div>
</div></div>
<div class="toolbar">
<label><span data-i18n="logs.lines">Lines</span><input id="logLines" type="number" min="20" max="1000" value="160"></label>
<button class="btn primary" id="refreshLogs" data-i18n="common.refresh">Refresh</button>
</div>
<pre class="log-box" id="logsBox"></pre>
</section>
</main>
</div>

<script>
/* ===== I18N ===== */
var L={
en:{
brand:{subtitle:"Telegram Username Tool"},
nav:{dashboard:"Dashboard",generation:"Generation",database:"Database",telegram:"Telegram",accounts:"Accounts",channels:"Channels",logs:"Logs"},
donation:{title:"Support Username Studio",hint:"A calm contribution to development"},
common:{refresh:"Refresh",save:"Save",show:"Show",delete:"Delete",loading:"loading",error:"error",status:"Status",search:"Search",phone:"Phone",code:"Code",login:"Login",sendCode:"Send Code","2fa":"2FA Password",ifEnabled:"if enabled",optional:"optional",yes:"y",updated:"Updated"},
dashboard:{title:"Dashboard",lastBatch:"Last Batch",last10:"last 10",availTop:"Available Top",scoreDesc:"score desc"},
gen:{title:"Generation",subtitle:"LM Studio + local evaluation, no Telegram actions",rotationAccount:"Active rotation account",required:"required",waiting:"waiting",checkingAccounts:"Checking account list...",batchSize:"Batch Size",minLength:"Min Length",maxLength:"Max Length",digits:"digits",generateBtn:"Generate & Evaluate",ready:"Ready to start",launching:"Launching..."},
db:{title:"Username Database",limitOn:"Output limit enabled",all:"All",searchPH:"username",shown:"Shown {n}",shownMore:"Shown {n}, more available"},
tg:{title:"Telegram Check",subtitle:"Checks only through accounts from the Accounts tab",mainAccount:"Main Account",channelCreation:"channel creation",liveCheck:"Live Check",sessionsOnly:"sessions/ only",mode:"Mode",checkForLive:"CHECK for live",mainCreation:"Main creation account",checking:"checking",checkingSession:"Checking session...",refreshStatus:"Refresh Status",apiMain:"Telegram API main account",apiHashPH:"leave empty if already saved",saveApi:"Save API",apiNote:"This account is only for channel creation, not for live checks.",loginMain:"Login to main account",phonePH:"+79990000000 or from .env",confirm2fa:"Confirm 2FA",resetLogin:"Reset Login",resetSession:"Reset Session",codeNote:"Code and password are not saved in the browser.",manualUsername:"Manual username",checkLimit:"Check limit",liveConfirm:"Live confirm",confirmPH:"CHECK",preview:"Preview",previewSel:"Preview Selected",checkSelLive:"Check Selected Live",candidatesNotLoaded:"Candidates not loaded",noCandidates:"No candidates",noCandidatesHint:"Try lowering min score or specify a username manually.",noSkips:"No skips",noSkipsHint:"All candidates passed the preliminary filter.",enterCheck:"For live check, enter CHECK"},
acc:{title:"Accounts",subtitle:"Accounts for live-check rotation only",add:"+ Add",newAccount:"New Account",notStarted:"not started",apiNote:"API ID, API Hash and phone are saved locally after successful login.",loginConfirm:"Login Confirmation",tgCode:"Telegram Code"},
ch:{title:"Channel Creation",subtitle:"Creation via main account; checking is separate",channelName:"Channel Name",useUsername:"Use username? (y/n)",notSelected:"Username not selected",select:"Select",create:"Create"},
logs:{title:"Logs",lines:"Lines"},
stats:{totalEvaluated:"Total Evaluated",totalChecked:"Telegram Checked",totalAvailable:"Available",totalTaken:"Taken/Invalid",totalUsed:"Used",totalUnchecked:"Unchecked",avgScore:"Avg Score",bestScore:"Best Score",lastBatchNum:"Last Batch",lastBatchCount:"Batch Usernames",lastBatchChecked:"Batch Checked",lastBatchAvail:"Batch Available"},
th:{status:"status",phone:"phone",lastError:"last error"},
status:{available:"available",active:"active",cooldown:"cooldown",dead:"dead",unchecked:"unchecked",used:"used",invalid:"invalid",error:"error",warn:"warn",noUsername:"no username",authorized:"authorized",loginReq:"login required",notConfigured:"not configured",wrongAccount:"wrong account",configured:"configured",notReady:"not ready",sending:"sending",codeSent:"code sent",notStarted:"not started",checking:"checking"},
time:{m:"m",s:"s"},
msg:{noBatchData:"No batch data",noBatchDataHint:"A new batch will appear after generation.",noAvail:"No available usernames",noAvailHint:"After live check, available usernames will appear here.",nothingFound:"Nothing found",nothingFoundHint:"Change filters or run generation.",genNoResults:"No results",genNoResultsHint:"Generation completed without new usernames.",genError:"Generation error",noAcc:"No accounts for live check",noAccHint:"Add account here; main creation account does not participate in live-check.",accLoaded:"Accounts loaded: {n}",multiNotAdded:"Multi-accounts not added",addAccHint:"Add an account in the Accounts tab. The main .env account does not participate in live checks.",accLoadedHint:"Accounts loaded, active will appear after live check starts.",noChAvail:"No available usernames",noChAvailHint:"Channel creation only for verified available usernames.",readyPreview:"Ready to preview",created:"Channel created ID {n}",delConfirm:"Delete account and its local session?",resetConfirm:"Reset local Telegram session and login again?",sessionReset:"Session reset. Send code for new login.",codeSentPhone:"Code sent to {n}.",accAuth:"Account authorized and ready for rotation.",accAdded:"Account added.",sendFirst:"Send code first.",noActive:"No active login.",loginReset:"Login reset.",alreadyAuth:"Account already authorized",loginOk:"Login successful",enter2fa:"Enter 2FA password",savingApi:"Saving Telegram API...",sendingCode:"Sending code...",checkingCode:"Checking code...",checking2fa:"Checking 2FA...",resettingSession:"Resetting Telegram session...",mainSession:"Main account. Session: {n}",fillApi:"Fill in TELEGRAM_API_ID and TELEGRAM_API_HASH",wrongDetail:"Session @{u} does not match phone from .env",authDetail:"{name} \u00b7 @{u} \u00b7 id {id} \u00b7 channel creation only",loginReqDetail:"Main account {n} is not authorized",hashChanged:"API saved. If new account, reset session.",noHashChange:"API ID/phone saved. HASH unchanged.",previewReady:"Preview ready",checkDone:"Done: {checked} checked, {available} available",candidates:"{source}: {count} candidates, {skipped} skipped"}
},
fa:{
brand:{subtitle:"\u0627\u0628\u0632\u0627\u0631 \u06cc\u0648\u0632\u0631\u0646\u06cc\u0645 \u062a\u0644\u06af\u0631\u0627\u0645"},
nav:{dashboard:"\u062f\u0627\u0634\u0628\u0648\u0631\u062f",generation:"\u062a\u0648\u0644\u06cc\u062f",database:"\u067e\u0627\u06cc\u06af\u0627\u0647 \u062f\u0627\u062f\u0647",telegram:"\u062a\u0644\u06af\u0631\u0627\u0645",accounts:"\u062d\u0633\u0627\u0628\u200c\u0647\u0627",channels:"\u06a9\u0627\u0646\u0627\u0644\u200c\u0647\u0627",logs:"\u0644\u0627\u06af\u200c\u0647\u0627"},
donation:{title:"\u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc \u0627\u0632 Username Studio",hint:"\u06a9\u0645\u06a9 \u0628\u0647 \u062a\u0648\u0633\u0639\u0647 \u067e\u0631\u0648\u0698\u0647"},
common:{refresh:"\u0628\u0631\u0648\u0632\u0631\u0633\u0627\u0646\u06cc",save:"\u0630\u062e\u06cc\u0631\u0647",show:"\u0646\u0645\u0627\u06cc\u0634",delete:"\u062d\u0630\u0641",loading:"\u0628\u0627\u0631\u06af\u0630\u0627\u0631\u06cc",error:"\u062e\u0637\u0627",status:"\u0648\u0636\u0639\u06cc\u062a",search:"\u062c\u0633\u062a\u062c\u0648",phone:"\u062a\u0644\u0641\u0646",code:"\u06a9\u062f",login:"\u0648\u0631\u0648\u062f",sendCode:"\u0627\u0631\u0633\u0627\u0644 \u06a9\u062f","2fa":"\u0631\u0645\u0632 2FA",ifEnabled:"\u062f\u0631 \u0635\u0648\u0631\u062a \u0641\u0639\u0627\u0644 \u0628\u0648\u062f\u0646",optional:"\u0627\u062e\u062a\u06cc\u0627\u0631\u06cc",yes:"\u0628\u0644\u0647",updated:"\u0628\u0631\u0648\u0632 \u0634\u062f\u0647"},
dashboard:{title:"\u062f\u0627\u0634\u0628\u0648\u0631\u062f",lastBatch:"\u0622\u062e\u0631\u06cc\u0646 \u0628\u0686",last10:"10 \u062a\u0627\u06cc \u0622\u062e\u0631",availTop:"\u0628\u0631\u062a\u0631\u06cc\u0646\u200c\u0647\u0627\u06cc \u0645\u0648\u062c\u0648\u062f",scoreDesc:"\u0645\u0631\u062a\u0628 \u0628\u0631 \u0627\u0633\u0627\u0633 \u0627\u0645\u062a\u06cc\u0627\u0632"},
gen:{title:"\u062a\u0648\u0644\u06cc\u062f",subtitle:"LM Studio + \u0627\u0631\u0632\u06cc\u0627\u0628\u06cc \u0645\u062d\u0644\u06cc\u060c \u0628\u062f\u0648\u0646 \u0639\u0645\u0644\u06cc\u0627\u062a \u062a\u0644\u06af\u0631\u0627\u0645",rotationAccount:"\u062d\u0633\u0627\u0628 \u0641\u0639\u0627\u0644 \u0686\u0631\u0634\u06cc",required:"\u0627\u0644\u0632\u0627\u0645\u06cc",waiting:"\u062f\u0631 \u0627\u0646\u062a\u0638\u0627\u0631",checkingAccounts:"\u0628\u0631\u0631\u0633\u06cc \u0644\u06cc\u0633\u062a \u062d\u0633\u0627\u0628\u200c\u0647\u0627...",batchSize:"\u0627\u0646\u062f\u0627\u0632\u0647 \u0628\u0686",minLength:"\u062d\u062f\u0627\u0642\u0644 \u0637\u0648\u0644",maxLength:"\u062d\u062f\u0627\u06a9\u062b\u0631 \u0637\u0648\u0644",digits:"\u0627\u0639\u062f\u0627\u062f",generateBtn:"\u062a\u0648\u0644\u06cc\u062f \u0648 \u0627\u0631\u0632\u06cc\u0627\u0628\u06cc",ready:"\u0622\u0645\u0627\u062f\u0647 \u0634\u0631\u0648\u0639",launching:"\u062f\u0631 \u062d\u0627\u0644 \u0627\u062c\u0631\u0627..."},
db:{title:"\u067e\u0627\u06cc\u06af\u0627\u0647 \u062f\u0627\u062f\u0647 \u06cc\u0648\u0632\u0631\u0646\u06cc\u0645",limitOn:"\u0645\u062d\u062f\u0648\u062f\u06cc\u062a \u0646\u0645\u0627\u06cc\u0634 \u0641\u0639\u0627\u0644",all:"\u0647\u0645\u0647",searchPH:"\u06cc\u0648\u0632\u0631\u0646\u06cc\u0645",shown:"\u0646\u0645\u0627\u06cc\u0634 {n}",shownMore:"\u0646\u0645\u0627\u06cc\u0634 {n}\u060c \u0628\u06cc\u0634\u062a\u0631 \u0645\u0648\u062c\u0648\u062f \u0627\u0633\u062a"},
tg:{title:"\u0628\u0631\u0631\u0633\u06cc \u062a\u0644\u06af\u0631\u0627\u0645",subtitle:"\u0628\u0631\u0631\u0633\u06cc \u0641\u0642\u0637 \u0627\u0632 \u0637\u0631\u06cc\u0642 \u062d\u0633\u0627\u0628\u200c\u0647\u0627\u06cc \u062a\u0628 \u062d\u0633\u0627\u0628\u200c\u0647\u0627",mainAccount:"\u062d\u0633\u0627\u0628 \u0627\u0635\u0644\u06cc",channelCreation:"\u0627\u06cc\u062c\u0627\u062f \u06a9\u0627\u0646\u0627\u0644",liveCheck:"\u0628\u0631\u0631\u0633\u06cc \u0632\u0646\u062f\u0647",sessionsOnly:"\u0641\u0642\u0637 sessions/",mode:"\u062d\u0627\u0644\u062a",checkForLive:"CHECK \u0628\u0631\u0627\u06cc \u0628\u0631\u0631\u0633\u06cc \u0632\u0646\u062f\u0647",mainCreation:"\u062d\u0633\u0627\u0628 \u0627\u0635\u0644\u06cc \u0627\u06cc\u062c\u0627\u062f",checking:"\u062f\u0631 \u062d\u0627\u0644 \u0628\u0631\u0631\u0633\u06cc",checkingSession:"\u0628\u0631\u0631\u0633\u06cc \u0646\u0634\u0633\u062a...",refreshStatus:"\u0628\u0631\u0648\u0632\u0631\u0633\u0627\u0646\u06cc \u0648\u0636\u0639\u06cc\u062a",apiMain:"API \u062a\u0644\u06af\u0631\u0627\u0645 \u062d\u0633\u0627\u0628 \u0627\u0635\u0644\u06cc",apiHashPH:"\u062e\u0627\u0644\u06cc \u0628\u06af\u0630\u0627\u0631\u06cc\u062f \u0627\u06af\u0631 \u0642\u0628\u0644\u0627 \u0630\u062e\u06cc\u0631\u0647 \u0634\u062f\u0647",saveApi:"\u0630\u062e\u06cc\u0631\u0647 API",apiNote:"\u0627\u06cc\u0646 \u062d\u0633\u0627\u0628 \u0641\u0642\u0637 \u0628\u0631\u0627\u06cc \u0627\u06cc\u062c\u0627\u062f \u06a9\u0627\u0646\u0627\u0644 \u0627\u0633\u062a.",loginMain:"\u0648\u0631\u0648\u062f \u0628\u0647 \u062d\u0633\u0627\u0628 \u0627\u0635\u0644\u06cc",phonePH:"+79990000000 \u06cc\u0627 \u0627\u0632 .env",confirm2fa:"\u062a\u0627\u06cc\u06cc\u062f 2FA",resetLogin:"\u0628\u0627\u0632\u0646\u0634\u0627\u0646\u06cc \u0648\u0631\u0648\u062f",resetSession:"\u0628\u0627\u0632\u0646\u0634\u0627\u0646\u06cc \u0646\u0634\u0633\u062a",codeNote:"\u06a9\u062f \u0648 \u0631\u0645\u0632 \u062f\u0631 \u0645\u0631\u0648\u0631\u06af\u0631 \u0630\u062e\u06cc\u0631\u0647 \u0646\u0645\u06cc\u200c\u0634\u0648\u0646\u062f.",manualUsername:"\u06cc\u0648\u0632\u0631\u0646\u06cc\u0645 \u062f\u0633\u062a\u06cc",checkLimit:"\u0645\u062d\u062f\u0648\u062f\u06cc\u062a \u0628\u0631\u0631\u0633\u06cc",liveConfirm:"\u062a\u0627\u06cc\u06cc\u062f \u0632\u0646\u062f\u0647",confirmPH:"CHECK",preview:"\u067e\u06cc\u0634\u200c\u0646\u0645\u0627\u06cc\u0634",previewSel:"\u067e\u06cc\u0634\u200c\u0646\u0645\u0627\u06cc\u0634 \u0627\u0646\u062a\u062e\u0627\u0628\u200c\u0634\u062f\u0647",checkSelLive:"\u0628\u0631\u0631\u0633\u06cc \u0632\u0646\u062f\u0647 \u0627\u0646\u062a\u062e\u0627\u0628\u200c\u0634\u062f\u0647",candidatesNotLoaded:"\u0646\u0627\u0645\u0632\u062f\u0627 \u0628\u0627\u0631\u06af\u0630\u0627\u0631\u06cc \u0646\u0634\u062f\u0646\u062f",noCandidates:"\u0646\u0627\u0645\u0632\u062f\u06cc \u0648\u062c\u0648\u062f \u0646\u062f\u0627\u0631\u062f",noCandidatesHint:"\u062d\u062f\u0627\u0642\u0644 \u0627\u0645\u062a\u06cc\u0627\u0632 \u0631\u0627 \u06a9\u0627\u0647\u0634 \u062f\u0647\u06cc\u062f \u06cc\u0627 \u06cc\u0648\u0632\u0631\u0646\u06cc\u0645 \u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f.",noSkips:"\u0628\u062f\u0648\u0646 \u067e\u0631\u0634",noSkipsHint:"\u0647\u0645\u0647 \u0646\u0627\u0645\u0632\u062f\u0627 \u0627\u0632 \u0641\u06cc\u0644\u062a\u0631 \u0639\u0628\u0648\u0631 \u06a9\u0631\u062f\u0646\u062f.",enterCheck:"\u0628\u0631\u0627\u06cc \u0628\u0631\u0631\u0633\u06cc \u0632\u0646\u062f\u0647\u060c CHECK \u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f"},
acc:{title:"\u062d\u0633\u0627\u0628\u200c\u0647\u0627",subtitle:"\u062d\u0633\u0627\u0628\u200c\u0647\u0627 \u0641\u0642\u0637 \u0628\u0631\u0627\u06cc \u0686\u0631\u0634\u06cc \u0628\u0631\u0631\u0633\u06cc \u0632\u0646\u062f\u0647",add:"+ \u0627\u0641\u0632\u0648\u062f\u0646",newAccount:"\u062d\u0633\u0627\u0628 \u062c\u062f\u06cc\u062f",notStarted:"\u0634\u0631\u0648\u0639 \u0646\u0634\u062f\u0647",apiNote:"API ID\u060c API Hash \u0648 \u062a\u0644\u0641\u0646 \u067e\u0633 \u0627\u0632 \u0648\u0631\u0648\u062f \u0645\u0648\u0641\u0642 \u062f\u0631 sessions \u0630\u062e\u06cc\u0631\u0647 \u0645\u06cc\u200c\u0634\u0648\u0646\u062f.",loginConfirm:"\u062a\u0627\u06cc\u06cc\u062f \u0648\u0631\u0648\u062f",tgCode:"\u06a9\u062f \u062a\u0644\u06af\u0631\u0627\u0645"},
ch:{title:"\u0627\u06cc\u062c\u0627\u062f \u06a9\u0627\u0646\u0627\u0644",subtitle:"\u0627\u06cc\u062c\u0627\u062f \u0627\u0632 \u0637\u0631\u06cc\u0642 \u062d\u0633\u0627\u0628 \u0627\u0635\u0644\u06cc\u060c \u0628\u0631\u0631\u0633\u06cc \u062c\u062f\u0627\u06af\u0627\u0646\u0647",channelName:"\u0646\u0627\u0645 \u06a9\u0627\u0646\u0627\u0644",useUsername:"\u0627\u0632 \u06cc\u0648\u0632\u0631\u0646\u06cc\u0645 \u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u0634\u0648\u062f\u061f (y/n)",notSelected:"\u06cc\u0648\u0632\u0631\u0646\u06cc\u0645 \u0627\u0646\u062a\u062e\u0627\u0628 \u0646\u0634\u062f\u0647",select:"\u0627\u0646\u062a\u062e\u0627\u0628",create:"\u0627\u06cc\u062c\u0627\u062f"},
logs:{title:"\u0644\u0627\u06af\u200c\u0647\u0627",lines:"\u062a\u0639\u062f\u0627\u062f \u062e\u0637\u0648\u0637"},
stats:{totalEvaluated:"\u06a9\u0644 \u0627\u0631\u0632\u06cc\u0627\u0628\u06cc\u200c\u0634\u062f\u0647",totalChecked:"\u0628\u0631\u0631\u0633\u06cc\u200c\u0634\u062f\u0647 \u062a\u0644\u06af\u0631\u0627\u0645",totalAvailable:"\u0645\u0648\u062c\u0648\u062f",totalTaken:"\u0627\u0634\u063a\u0627\u0644\u200c\u0634\u062f\u0647/\u0646\u0627\u0645\u0639\u062a\u0628\u0631",totalUsed:"\u0627\u0633\u062a\u0641\u0627\u062f\u0647\u200c\u0634\u062f\u0647",totalUnchecked:"\u0628\u0631\u0631\u0633\u06cc\u200c\u0646\u0634\u062f\u0647",avgScore:"\u0645\u06cc\u0627\u0646\u06af\u06cc\u0646 \u0627\u0645\u062a\u06cc\u0627\u0632",bestScore:"\u0628\u0647\u062a\u0631\u06cc\u0646 \u0627\u0645\u062a\u06cc\u0627\u0632",lastBatchNum:"\u0622\u062e\u0631\u06cc\u0646 \u0628\u0686",lastBatchCount:"\u06cc\u0648\u0632\u0631\u0646\u06cc\u0645\u200c\u0647\u0627\u06cc \u0628\u0686",lastBatchChecked:"\u0628\u0686 \u0628\u0631\u0631\u0633\u06cc\u200c\u0634\u062f\u0647",lastBatchAvail:"\u0628\u0686 \u0645\u0648\u062c\u0648\u062f"},
th:{status:"\u0648\u0636\u0639\u06cc\u062a",phone:"\u062a\u0644\u0641\u0646",lastError:"\u0622\u062e\u0631\u06cc\u0646 \u062e\u0637\u0627"},
status:{available:"\u0645\u0648\u062c\u0648\u062f",active:"\u0641\u0639\u0627\u0644",cooldown:"\u0632\u0645\u0627\u0646 \u0627\u0646\u062a\u0638\u0627\u0631",dead:"\u063a\u06cc\u0631\u0641\u0639\u0627\u0644",unchecked:"\u0628\u0631\u0631\u0633\u06cc\u200c\u0646\u0634\u062f\u0647",used:"\u0627\u0633\u062a\u0641\u0627\u062f\u0647\u200c\u0634\u062f\u0647",invalid:"\u0646\u0627\u0645\u0639\u062a\u0628\u0631",error:"\u062e\u0637\u0627",warn:"\u0647\u0634\u062f\u0627\u0631",noUsername:"\u0628\u062f\u0648\u0646 \u06cc\u0648\u0632\u0631\u0646\u06cc\u0645",authorized:"\u0645\u062c\u0627\u0632",loginReq:"\u0646\u06cc\u0627\u0632 \u0628\u0647 \u0648\u0631\u0648\u062f",notConfigured:"\u067e\u06cc\u06a9\u0631\u0628\u0646\u062f\u06cc \u0646\u0634\u062f\u0647",wrongAccount:"\u062d\u0633\u0627\u0628 \u0627\u0634\u062a\u0628\u0627\u0647",configured:"\u067e\u06cc\u06a9\u0631\u0628\u0646\u062f\u06cc \u0634\u062f\u0647",notReady:"\u0622\u0645\u0627\u062f\u0647 \u0646\u06cc\u0633\u062a",sending:"\u0627\u0631\u0633\u0627\u0644",codeSent:"\u06a9\u062f \u0627\u0631\u0633\u0627\u0644 \u0634\u062f",notStarted:"\u0634\u0631\u0648\u0639 \u0646\u0634\u062f\u0647",checking:"\u062f\u0631 \u062d\u0627\u0644 \u0628\u0631\u0631\u0633\u06cc"},
time:{m:"\u062f",s:"\u062b"},
msg:{noBatchData:"\u062f\u0627\u062f\u0647\u200c\u0627\u06cc \u0645\u0648\u062c\u0648\u062f \u0646\u06cc\u0633\u062a",noBatchDataHint:"\u0628\u0686 \u062c\u062f\u06cc\u062f \u0628\u0639\u062f \u0627\u0632 \u062a\u0648\u0644\u06cc\u062f \u0638\u0627\u0647\u0631 \u0645\u06cc\u200c\u0634\u0648\u062f.",noAvail:"\u06cc\u0648\u0632\u0631\u0646\u06cc\u0645 \u0645\u0648\u062c\u0648\u062f\u06cc \u0646\u06cc\u0633\u062a",noAvailHint:"\u0628\u0639\u062f \u0627\u0632 \u0628\u0631\u0631\u0633\u06cc \u0632\u0646\u062f\u0647\u060c \u06cc\u0648\u0632\u0631\u0646\u06cc\u0645\u200c\u0647\u0627\u06cc \u0645\u0648\u062c\u0648\u062f \u0627\u06cc\u0646\u062c\u0627 \u0646\u0645\u0627\u06cc\u0634 \u062f\u0627\u062f\u0647 \u0645\u06cc\u200c\u0634\u0648\u0646\u062f.",nothingFound:"\u0686\u06cc\u0632\u06cc \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f",nothingFoundHint:"\u0641\u06cc\u0644\u062a\u0631\u0647\u0627 \u0631\u0627 \u062a\u063a\u06cc\u06cc\u0631 \u062f\u0647\u06cc\u062f.",genNoResults:"\u0646\u062a\u06cc\u062c\u0647\u200c\u0627\u06cc \u0646\u062f\u0627\u0631\u062f",genNoResultsHint:"\u062a\u0648\u0644\u06cc\u062f \u0628\u062f\u0648\u0646 \u06cc\u0648\u0632\u0631\u0646\u06cc\u0645 \u062c\u062f\u06cc\u062f \u062a\u06a9\u0645\u06cc\u0644 \u0634\u062f.",genError:"\u062e\u0637\u0627\u06cc \u062a\u0648\u0644\u06cc\u062f",noAcc:"\u062d\u0633\u0627\u0628\u06cc \u0628\u0631\u0627\u06cc \u0628\u0631\u0631\u0633\u06cc \u0632\u0646\u062f\u0647 \u0646\u06cc\u0633\u062a",noAccHint:"\u062d\u0633\u0627\u0628 \u0627\u0636\u0627\u0641\u0647 \u06a9\u0646\u06cc\u062f.",accLoaded:"\u062a\u0639\u062f\u0627\u062f \u062d\u0633\u0627\u0628\u200c\u0647\u0627: {n}",multiNotAdded:"\u062d\u0633\u0627\u0628\u200c\u0647\u0627\u06cc \u0686\u0646\u062f\u06af\u0627\u0646\u0647 \u0627\u0636\u0627\u0641\u0647 \u0646\u0634\u062f\u0647",addAccHint:"\u062f\u0631 \u062a\u0628 \u062d\u0633\u0627\u0628\u200c\u0647\u0627 \u06cc\u06a9 \u062d\u0633\u0627\u0628 \u0627\u0636\u0627\u0641\u0647 \u06a9\u0646\u06cc\u062f.",accLoadedHint:"\u062d\u0633\u0627\u0628\u200c\u0647\u0627 \u0628\u0627\u0631\u06af\u0630\u0627\u0631\u06cc \u0634\u062f.",noChAvail:"\u06cc\u0648\u0632\u0631\u0646\u06cc\u0645 \u0645\u0648\u062c\u0648\u062f\u06cc \u0646\u06cc\u0633\u062a",noChAvailHint:"\u0627\u06cc\u062c\u0627\u062f \u06a9\u0627\u0646\u0627\u0644 \u0641\u0642\u0637 \u0628\u0631\u0627\u06cc \u06cc\u0648\u0632\u0631\u0646\u06cc\u0645\u200c\u0647\u0627\u06cc \u062a\u0627\u06cc\u06cc\u062f \u0634\u062f\u0647.",readyPreview:"\u0622\u0645\u0627\u062f\u0647 \u067e\u06cc\u0634\u200c\u0646\u0645\u0627\u06cc\u0634",created:"\u06a9\u0627\u0646\u0627\u0644 \u0627\u06cc\u062c\u0627\u062f \u0634\u062f ID {n}",delConfirm:"\u062d\u0630\u0641 \u062d\u0633\u0627\u0628 \u0648 \u0646\u0634\u0633\u062a \u0645\u062d\u0644\u06cc\u061f",resetConfirm:"\u0628\u0627\u0632\u0646\u0634\u0627\u0646\u06cc \u0646\u0634\u0633\u062a \u062a\u0644\u06af\u0631\u0627\u0645 \u0648 \u0648\u0631\u0648\u062f \u0645\u062c\u062f\u062f\u061f",sessionReset:"\u0646\u0634\u0633\u062a \u0628\u0627\u0632\u0646\u0634\u0627\u0646\u06cc \u0634\u062f. \u06a9\u062f \u062c\u062f\u06cc\u062f \u0627\u0631\u0633\u0627\u0644 \u06a9\u0646\u06cc\u062f.",codeSentPhone:"\u06a9\u062f \u0628\u0647 {n} \u0627\u0631\u0633\u0627\u0644 \u0634\u062f.",accAuth:"\u062d\u0633\u0627\u0628 \u0645\u062c\u0627\u0632 \u0648 \u0622\u0645\u0627\u062f\u0647 \u0686\u0631\u0634\u06cc.",accAdded:"\u062d\u0633\u0627\u0628 \u0627\u0636\u0627\u0641\u0647 \u0634\u062f.",sendFirst:"\u0627\u0628\u062a\u062f\u0627 \u06a9\u062f \u0627\u0631\u0633\u0627\u0644 \u06a9\u0646\u06cc\u062f.",noActive:"\u0648\u0631\u0648\u062f \u0641\u0639\u0627\u0644\u06cc \u0646\u06cc\u0633\u062a.",loginReset:"\u0648\u0631\u0648\u062f \u0628\u0627\u0632\u0646\u0634\u0627\u0646\u06cc \u0634\u062f.",alreadyAuth:"\u062d\u0633\u0627\u0628 \u0642\u0628\u0644\u0627 \u0645\u062c\u0627\u0632 \u0627\u0633\u062a",loginOk:"\u0648\u0631\u0648\u062f \u0645\u0648\u0641\u0642",enter2fa:"\u0631\u0645\u0632 2FA \u0631\u0627 \u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f",savingApi:"\u0630\u062e\u06cc\u0631\u0647 API \u062a\u0644\u06af\u0631\u0627\u0645...",sendingCode:"\u0627\u0631\u0633\u0627\u0644 \u06a9\u062f...",checkingCode:"\u0628\u0631\u0631\u0633\u06cc \u06a9\u062f...",checking2fa:"\u0628\u0631\u0631\u0633\u06cc 2FA...",resettingSession:"\u0628\u0627\u0632\u0646\u0634\u0627\u0646\u06cc \u0646\u0634\u0633\u062a...",mainSession:"\u062d\u0633\u0627\u0628 \u0627\u0635\u0644\u06cc. \u0646\u0634\u0633\u062a: {n}",fillApi:"API ID \u0648 API HASH \u0631\u0627 \u0648\u0627\u0631\u062f \u06a9\u0646\u06cc\u062f",wrongDetail:"\u0646\u0634\u0633\u062a \u0641\u0639\u0644\u06cc @{u} \u0645\u0637\u0627\u0628\u0642\u062a \u0646\u062f\u0627\u0631\u062f",authDetail:"{name} \u00b7 @{u} \u00b7 id {id} \u00b7 \u0641\u0642\u0637 \u0627\u06cc\u062c\u0627\u062f \u06a9\u0627\u0646\u0627\u0644",loginReqDetail:"\u062d\u0633\u0627\u0628 \u0627\u0635\u0644\u06cc {n} \u0645\u062c\u0627\u0632 \u0646\u06cc\u0633\u062a",hashChanged:"API \u0630\u062e\u06cc\u0631\u0647 \u0634\u062f. \u0627\u06af\u0631 \u062d\u0633\u0627\u0628 \u062c\u062f\u06cc\u062f\u060c \u0646\u0634\u0633\u062a \u0631\u0627 \u0628\u0627\u0632\u0646\u0634\u0627\u0646\u06cc \u06a9\u0646\u06cc\u062f.",noHashChange:"API ID/\u062a\u0644\u0641\u0646 \u0630\u062e\u06cc\u0631\u0647 \u0634\u062f. HASH \u062a\u063a\u06cc\u06cc\u0631 \u0646\u06a9\u0631\u062f.",previewReady:"\u067e\u06cc\u0634\u200c\u0646\u0645\u0627\u06cc\u0634 \u0622\u0645\u0627\u062f\u0647",checkDone:"\u062a\u06a9\u0645\u06cc\u0644: {checked} \u0628\u0631\u0631\u0633\u06cc\u200c\u0634\u062f\u0647\u060c {available} \u0645\u0648\u062c\u0648\u062f",candidates:"{source}: {count} \u0646\u0627\u0645\u0632\u062f\u060c {skipped} \u067e\u0631\u0634"}
},
ru:{
brand:{subtitle:"\u0418\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442 Telegram username"},
nav:{dashboard:"Dashboard",generation:"\u0413\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u044f",database:"\u0411\u0430\u0437\u0430",telegram:"Telegram",accounts:"\u0410\u043a\u043a\u0430\u0443\u043d\u0442\u044b",channels:"\u041a\u0430\u043d\u0430\u043b",logs:"\u041b\u043e\u0433\u0438"},
donation:{title:"\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u0430\u0442\u044c Username Studio",hint:"\u0441\u043f\u043e\u043a\u043e\u0439\u043d\u044b\u0439 \u0432\u043a\u043b\u0430\u0434 \u0432 \u0440\u0430\u0437\u0432\u0438\u0442\u0438\u0435"},
common:{refresh:"\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c",save:"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c",show:"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c",delete:"\u0423\u0434\u0430\u043b\u0438\u0442\u044c",loading:"\u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0430",error:"\u043e\u0448\u0438\u0431\u043a\u0430",status:"\u0421\u0442\u0430\u0442\u0443\u0441",search:"\u041f\u043e\u0438\u0441\u043a",phone:"\u0422\u0435\u043b\u0435\u0444\u043e\u043d",code:"\u041a\u043e\u0434",login:"\u0412\u043e\u0439\u0442\u0438",sendCode:"\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u044c \u043a\u043e\u0434","2fa":"2FA \u043f\u0430\u0440\u043e\u043b\u044c",ifEnabled:"\u0435\u0441\u043b\u0438 \u0432\u043a\u043b\u044e\u0447\u0435\u043d",optional:"\u043d\u0435\u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u043e",yes:"y",updated:"\u041e\u0431\u043d\u043e\u0432\u043b\u0435\u043d\u043e"},
dashboard:{title:"Dashboard",lastBatch:"\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 batch",last10:"\u043f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 10",availTop:"Available top",scoreDesc:"score desc"},
gen:{title:"\u0413\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u044f",subtitle:"LM Studio + \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u0430\u044f \u043e\u0446\u0435\u043d\u043a\u0430",rotationAccount:"\u0410\u043a\u0442\u0438\u0432\u043d\u044b\u0439 \u0430\u043a\u043a\u0430\u0443\u043d\u0442 \u0440\u043e\u0442\u0430\u0446\u0438\u0438",required:"required",waiting:"waiting",checkingAccounts:"\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0441\u043f\u0438\u0441\u043a\u0430...",batchSize:"\u0420\u0430\u0437\u043c\u0435\u0440 batch",minLength:"\u041c\u0438\u043d. \u0434\u043b\u0438\u043d\u0430",maxLength:"\u041c\u0430\u043a\u0441. \u0434\u043b\u0438\u043d\u0430",digits:"\u0446\u0438\u0444\u0440\u044b",generateBtn:"\u0421\u0433\u0435\u043d\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c",ready:"\u0413\u043e\u0442\u043e\u0432\u043e",launching:"\u0417\u0430\u043f\u0443\u0441\u043a..."},
db:{title:"\u0411\u0430\u0437\u0430 username",limitOn:"\u041b\u0438\u043c\u0438\u0442 \u0432\u044b\u0432\u043e\u0434\u0430 \u0432\u043a\u043b\u044e\u0447\u0435\u043d",all:"\u0412\u0441\u0435",searchPH:"username",shown:"\u041f\u043e\u043a\u0430\u0437\u0430\u043d\u043e {n}",shownMore:"\u041f\u043e\u043a\u0430\u0437\u0430\u043d\u043e {n}, \u0435\u0441\u0442\u044c \u0435\u0449\u0435"},
tg:{title:"Telegram-\u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430",subtitle:"\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0442\u043e\u043b\u044c\u043a\u043e \u0447\u0435\u0440\u0435\u0437 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u044b",mainAccount:"\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0430\u043a\u043a\u0430\u0443\u043d\u0442",channelCreation:"\u0441\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043a\u0430\u043d\u0430\u043b\u043e\u0432",liveCheck:"Live-\u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430",sessionsOnly:"\u0442\u043e\u043b\u044c\u043a\u043e sessions/",mode:"\u0420\u0435\u0436\u0438\u043c",checkForLive:"CHECK \u0434\u043b\u044f live",mainCreation:"\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0430\u043a\u043a\u0430\u0443\u043d\u0442 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f",checking:"checking",checkingSession:"\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0441\u0435\u0441\u0441\u0438\u0438...",refreshStatus:"\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c \u0441\u0442\u0430\u0442\u0443\u0441",apiMain:"Telegram API \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0433\u043e",apiHashPH:"\u043e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c",saveApi:"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c API",apiNote:"\u0422\u043e\u043b\u044c\u043a\u043e \u0434\u043b\u044f \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f \u043a\u0430\u043d\u0430\u043b\u043e\u0432.",loginMain:"\u0412\u0445\u043e\u0434 \u0432 \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439",phonePH:"+79990000000 \u0438\u043b\u0438 \u0438\u0437 .env",confirm2fa:"\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0434\u0438\u0442\u044c 2FA",resetLogin:"\u0421\u0431\u0440\u043e\u0441\u0438\u0442\u044c \u0432\u0445\u043e\u0434",resetSession:"\u0421\u0431\u0440\u043e\u0441\u0438\u0442\u044c \u0441\u0435\u0441\u0441\u0438\u044e",codeNote:"\u041a\u043e\u0434 \u0438 \u043f\u0430\u0440\u043e\u043b\u044c \u043d\u0435 \u0441\u043e\u0445\u0440\u0430\u043d\u044f\u044e\u0442\u0441\u044f.",manualUsername:"Manual username",checkLimit:"\u041b\u0438\u043c\u0438\u0442 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438",liveConfirm:"Live confirm",confirmPH:"CHECK",preview:"Preview",previewSel:"Preview \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u044b\u0445",checkSelLive:"\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c live",candidatesNotLoaded:"\u041a\u0430\u043d\u0434\u0438\u0434\u0430\u0442\u044b \u043d\u0435 \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043d\u044b",noCandidates:"\u041d\u0435\u0442 \u043a\u0430\u043d\u0434\u0438\u0434\u0430\u0442\u043e\u0432",noCandidatesHint:"\u0421\u043d\u0438\u0437\u044c\u0442\u0435 min score.",noSkips:"\u041d\u0435\u0442 \u043f\u0440\u043e\u043f\u0443\u0441\u043a\u043e\u0432",noSkipsHint:"\u0412\u0441\u0435 \u043f\u0440\u043e\u0448\u043b\u0438 \u0444\u0438\u043b\u044c\u0442\u0440.",enterCheck:"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 CHECK"},
acc:{title:"\u0410\u043a\u043a\u0430\u0443\u043d\u0442\u044b",subtitle:"\u0422\u043e\u043b\u044c\u043a\u043e \u0434\u043b\u044f \u0440\u043e\u0442\u0430\u0446\u0438\u0438 live-\u043f\u0440\u043e\u0432\u0435\u0440\u043e\u043a",add:"+ \u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c",newAccount:"\u041d\u043e\u0432\u044b\u0439 \u0430\u043a\u043a\u0430\u0443\u043d\u0442",notStarted:"not started",apiNote:"API ID, Hash \u0438 \u0442\u0435\u043b\u0435\u0444\u043e\u043d \u0441\u043e\u0445\u0440\u0430\u043d\u044f\u044e\u0442\u0441\u044f \u043b\u043e\u043a\u0430\u043b\u044c\u043d\u043e.",loginConfirm:"\u041f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u0435 \u0432\u0445\u043e\u0434\u0430",tgCode:"\u041a\u043e\u0434 Telegram"},
ch:{title:"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u043a\u0430\u043d\u0430\u043b\u0430",subtitle:"\u0427\u0435\u0440\u0435\u0437 \u043e\u0441\u043d\u043e\u0432\u043d\u043e\u0439 \u0430\u043a\u043a\u0430\u0443\u043d\u0442",channelName:"\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u0430\u043d\u0430\u043b\u0430",useUsername:"\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c? (y/n)",notSelected:"\u041d\u0435 \u0432\u044b\u0431\u0440\u0430\u043d\u043e",select:"\u0412\u044b\u0431\u0440\u0430\u0442\u044c",create:"\u0421\u043e\u0437\u0434\u0430\u0442\u044c"},
logs:{title:"\u041b\u043e\u0433\u0438",lines:"\u0421\u0442\u0440\u043e\u043a"},
stats:{totalEvaluated:"\u0412\u0441\u0435\u0433\u043e \u043e\u0446\u0435\u043d\u0435\u043d\u043e",totalChecked:"\u041f\u0440\u043e\u0432\u0435\u0440\u0435\u043d\u043e \u0432 Telegram",totalAvailable:"\u0414\u043e\u0441\u0442\u0443\u043f\u043d\u044b\u0445",totalTaken:"\u0417\u0430\u043d\u044f\u0442\u044b\u0445/\u043d\u0435\u0432\u0430\u043b\u0438\u0434\u043d\u044b\u0445",totalUsed:"\u0418\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u043d\u044b\u0445",totalUnchecked:"\u041d\u0435\u043f\u0440\u043e\u0432\u0435\u0440\u0435\u043d\u043d\u044b\u0445",avgScore:"\u0421\u0440\u0435\u0434\u043d\u0438\u0439 score",bestScore:"\u041b\u0443\u0447\u0448\u0438\u0439 score",lastBatchNum:"\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0439 batch",lastBatchCount:"Username \u0432 batch",lastBatchChecked:"Batch checked",lastBatchAvail:"Batch available"},
th:{status:"status",phone:"\u0442\u0435\u043b\u0435\u0444\u043e\u043d",lastError:"last error"},
status:{available:"available",active:"active",cooldown:"cooldown",dead:"dead",unchecked:"unchecked",used:"used",invalid:"invalid",error:"error",warn:"warn",noUsername:"\u0431\u0435\u0437 username",authorized:"authorized",loginReq:"login required",notConfigured:"not configured",wrongAccount:"wrong account",configured:"configured",notReady:"not ready",sending:"sending",codeSent:"code sent",notStarted:"not started",checking:"checking"},
time:{m:"m",s:"s"},
msg:{noBatchData:"\u041d\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0445 batch",noBatchDataHint:"\u041d\u043e\u0432\u044b\u0439 batch \u043f\u043e\u044f\u0432\u0438\u0442\u0441\u044f \u043f\u043e\u0441\u043b\u0435 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u0438.",noAvail:"\u041d\u0435\u0442 available username",noAvailHint:"\u041f\u043e\u0441\u043b\u0435 live-\u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438 \u043f\u043e\u044f\u0432\u044f\u0442\u0441\u044f \u0437\u0434\u0435\u0441\u044c.",nothingFound:"\u041d\u0438\u0447\u0435\u0433\u043e \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e",nothingFoundHint:"\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u0435 \u0444\u0438\u043b\u044c\u0442\u0440\u044b.",genNoResults:"\u041d\u0435\u0442 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u043e\u0432",genNoResultsHint:"\u0413\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u044f \u0431\u0435\u0437 \u043d\u043e\u0432\u044b\u0445.",genError:"\u041e\u0448\u0438\u0431\u043a\u0430 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u0438",noAcc:"\u041d\u0435\u0442 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u043e\u0432",noAccHint:"\u0414\u043e\u0431\u0430\u0432\u044c\u0442\u0435 \u0430\u043a\u043a\u0430\u0443\u043d\u0442.",accLoaded:"\u0417\u0430\u0433\u0440\u0443\u0436\u0435\u043d\u043e: {n}",multiNotAdded:"\u041c\u0443\u043b\u044c\u0442\u0438-\u0430\u043a\u043a\u0430\u0443\u043d\u0442\u044b \u043d\u0435 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u044b",addAccHint:"\u0414\u043e\u0431\u0430\u0432\u044c\u0442\u0435 \u0430\u043a\u043a\u0430\u0443\u043d\u0442.",accLoadedHint:"\u0410\u043a\u043a\u0430\u0443\u043d\u0442\u044b \u0437\u0430\u0433\u0440\u0443\u0436\u0435\u043d\u044b.",noChAvail:"\u041d\u0435\u0442 available username",noChAvailHint:"\u0421\u043e\u0437\u0434\u0430\u043d\u0438\u0435 \u0442\u043e\u043b\u044c\u043a\u043e \u0434\u043b\u044f \u043f\u0440\u043e\u0432\u0435\u0440\u0435\u043d\u043d\u044b\u0445.",readyPreview:"\u0413\u043e\u0442\u043e\u0432\u043e",created:"\u041a\u0430\u043d\u0430\u043b ID {n}",delConfirm:"\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0430\u043a\u043a\u0430\u0443\u043d\u0442?",resetConfirm:"\u0421\u0431\u0440\u043e\u0441\u0438\u0442\u044c \u0441\u0435\u0441\u0441\u0438\u044e?",sessionReset:"\u0421\u0435\u0441\u0441\u0438\u044f \u0441\u0431\u0440\u043e\u0448\u0435\u043d\u0430.",codeSentPhone:"\u041a\u043e\u0434 \u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d \u043d\u0430 {n}.",accAuth:"\u0410\u043a\u043a\u0430\u0443\u043d\u0442 \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u043e\u0432\u0430\u043d.",accAdded:"\u0410\u043a\u043a\u0430\u0443\u043d\u0442 \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d.",sendFirst:"\u0421\u043d\u0430\u0447\u0430\u043b\u0430 \u043e\u0442\u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u043a\u043e\u0434.",noActive:"\u041d\u0435\u0442 \u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0433\u043e \u0432\u0445\u043e\u0434\u0430.",loginReset:"\u0412\u0445\u043e\u0434 \u0441\u0431\u0440\u043e\u0448\u0435\u043d.",alreadyAuth:"\u0423\u0436\u0435 \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u043e\u0432\u0430\u043d",loginOk:"\u0412\u0445\u043e\u0434 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d",enter2fa:"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 2FA",savingApi:"\u0421\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u0435...",sendingCode:"\u041e\u0442\u043f\u0440\u0430\u0432\u043a\u0430...",checkingCode:"\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430...",checking2fa:"\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 2FA...",resettingSession:"\u0421\u0431\u0440\u043e\u0441...",mainSession:"\u0421\u0435\u0441\u0441\u0438\u044f: {n}",fillApi:"\u0417\u0430\u043f\u043e\u043b\u043d\u0438\u0442\u0435 API",wrongDetail:"\u0421\u0435\u0441\u0441\u0438\u044f @{u} \u043d\u0435 \u0441\u043e\u0432\u043f\u0430\u0434\u0430\u0435\u0442",authDetail:"{name} \u00b7 @{u} \u00b7 id {id}",loginReqDetail:"{n} \u043d\u0435 \u0430\u0432\u0442\u043e\u0440\u0438\u0437\u043e\u0432\u0430\u043d",hashChanged:"API \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u044b.",noHashChange:"API ID/\u0442\u0435\u043b\u0435\u0444\u043e\u043d \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u044b. HASH \u043d\u0435 \u043c\u0435\u043d\u044f\u043b\u0441\u044f.",previewReady:"Preview \u0433\u043e\u0442\u043e\u0432",checkDone:"\u0417\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u043e: {checked} \u043f\u0440\u043e\u0432\u0435\u0440\u0435\u043d\u043e, {available} \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u044b",candidates:"{source}: {count} \u043a\u0430\u043d\u0434\u0438\u0434\u0430\u0442\u043e\u0432, {skipped} \u043f\u0440\u043e\u043f\u0443\u0449\u0435\u043d\u043e"}
}
};

var curLang=localStorage.getItem('us_lang')||'en';
var LOCALE_MAP={en:'en-US',fa:'en-US',ru:'ru-RU'};

function t(k,p){try{var ks=k.split('.'),v=L[curLang];for(var i=0;i<ks.length;i++){if(v)break;return k;}for(var i=0;i<ks.length;i++){v=v?v[ks[i]]:null;}if(v==null){v=L.en;for(var i=0;i<ks.length;i++){v=v?v[ks[i]]:null;}}if(v==null)return k;if(p)for(var a in p)v=v.replace('{'+a+'}',p[a]);return v;}catch(e){return k;}}

function applyI18n(){
try{
document.documentElement.lang=curLang;
document.documentElement.dir=curLang==='fa'?'rtl':'ltr';
var els=document.querySelectorAll('[data-i18n]');
for(var i=0;i<els.length;i++){
var el=els[i];var key=el.getAttribute('data-i18n');if(!key)continue;
var translation=t(key);if(!translation)continue;
if(el.children.length>0){
var textSpan=el.querySelector(':scope > .i18n-t');
if(textSpan){textSpan.textContent=translation;}
else if(el.childNodes.length>0&&el.childNodes[0].nodeType===3){el.childNodes[0].textContent=translation;}
}else{el.textContent=translation;}
}
var phEls=document.querySelectorAll('[data-i18n-placeholder]');
for(var i=0;i<phEls.length;i++){
var el=phEls[i];var key=el.getAttribute('data-i18n-placeholder');if(!key)continue;
if(typeof el.placeholder!=='undefined'){el.placeholder=t(key);}
}
var langBtns=document.querySelectorAll('.lang-btn');
for(var i=0;i<langBtns.length;i++){langBtns[i].classList.toggle('is-active',langBtns[i].getAttribute('data-lang')===curLang);}
}catch(e){console.error('applyI18n error:',e);}
}

function setLang(l){curLang=l;localStorage.setItem('us_lang',l);applyI18n();try{loadDashboard();}catch(e){}syncTelegramMode();}

/* ===== APP ===== */
var $=function(s){return document.querySelector(s);};
var $$$$=function(s){return Array.from(document.querySelectorAll(s));};
function makeClientId(){try{if(globalThis.crypto&&globalThis.crypto.randomUUID)return globalThis.crypto.randomUUID();}catch(e){}return ''+Date.now()+'-'+Math.random().toString(16).slice(2);}

var app={config:{},selectedChannel:null,telegramPreview:null,authFlowId:null,accountAuthFlowId:null,clientId:makeClientId(),serverToken:"__SERVER_RUN_TOKEN__",heartbeatTimer:null,closeSent:false};

function api(path,options){
options=options||{};
return fetch(path,Object.assign({headers:{"Content-Type":"application/json"}},options)).then(function(r){
return r.json().then(function(d){
if(!r.ok){var e=new Error(d.error||r.statusText);e.data=d;throw e;}
return d;
});
});
}

function clientBody(){return JSON.stringify({client_id:app.clientId,server_token:app.serverToken});}
function postClientEvent(a,keepalive){return fetch('/api/client/'+a,{method:"POST",headers:{"Content-Type":"application/json"},body:clientBody(),keepalive:!!keepalive}).catch(function(){return null;});}
function registerBrowserClient(){return postClientEvent("open").then(function(){if(app.heartbeatTimer)clearInterval(app.heartbeatTimer);app.heartbeatTimer=setInterval(function(){postClientEvent("ping",true);},3000);});}
function notifyBrowserClosed(){if(app.closeSent)return;app.closeSent=true;if(app.heartbeatTimer)clearInterval(app.heartbeatTimer);var b=clientBody();if(navigator.sendBeacon){navigator.sendBeacon("/api/client/close",new Blob([b],{type:"application/json"}));return;}fetch("/api/client/close",{method:"POST",headers:{"Content-Type":"application/json"},body:b,keepalive:true}).catch(function(){});}
window.addEventListener("pagehide",notifyBrowserClosed);
window.addEventListener("beforeunload",notifyBrowserClosed);

function fmtNumber(v){if(v===null||v===undefined||v==="")return"0";try{return Number(v).toLocaleString(LOCALE_MAP[curLang]||'en-US',{maximumFractionDigits:2});}catch(e){return String(v);}}
function fmtScore(v){if(v===null||v===undefined||v==="")return"-";return Number(v).toFixed(2);}
function badge(s){var v=s||"unchecked";return '<span class="badge '+esc(v)+'">'+esc(v)+'</span>';}
function esc(v){return String(v==null?"":v).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c];});}
function rowHtml(r,e){e=e||"";return '<tr>'+e+'<td class="mono">@'+esc(r.username)+'</td><td>'+fmtScore(r.score)+'</td><td>'+badge(r.status)+'</td><td>'+esc(r.generation_type||"-")+'</td><td>'+esc(r.batch_num||"-")+'</td></tr>';}
function setProgress(id,v){var el=$(id);if(el)el.style.width=Math.max(0,Math.min(100,Number(v)||0))+'%';}
function fmtCooldown(v){var s=Number(v||0);if(s<=0)return"-";var m=Math.floor(s/60),r=s%60;return m?m+t('time.m')+' '+r+t('time.s'):r+t('time.s');}
function accUserText(a){var u=a&&a.user?a.user:{};var un=u.username?'@'+u.username:t('status.noUsername');var nm=((u.first_name||'')+' '+(u.last_name||'')).trim();return nm?nm+' \u00b7 '+un:un;}

function renderRotAcc(data){var active=data.active_account;var b=$("#rotationAccountBadge");if(!b)return;b.className="badge";if(!data.has_accounts){b.classList.add("warn");b.textContent=t('gen.required');$("#rotationAccountDetails").textContent=t('msg.addAccHint');return;}if(!active){b.classList.add("warn");b.textContent=t('gen.waiting');$("#rotationAccountDetails").textContent=t('msg.accLoadedHint');return;}b.classList.add(active.status||"active");b.textContent=active.status||"active";var cd=active.cooldown_remaining?' \u00b7 cooldown '+fmtCooldown(active.cooldown_remaining):"";$("#rotationAccountDetails").textContent=(active.phone||"-")+' \u00b7 '+accUserText(active)+cd;}

function renderAccounts(data){var accs=data.accounts||[];var meta=$("#accountsMeta");if(meta)meta.textContent=accs.length?t('msg.accLoaded',{n:accs.length}):t('msg.multiNotAdded');renderRotAcc(data);var rows=$("#accountsRows");if(!rows)return;rows.innerHTML=accs.length?accs.map(function(a){return '<tr><td class="mono">'+esc(a.phone||"-")+'</td><td>'+badge(a.status||"active")+'</td><td>'+esc(fmtCooldown(a.cooldown_remaining))+'</td><td>'+esc(accUserText(a))+'</td><td class="notes">'+esc(a.last_error||"")+'</td><td><button class="btn danger" data-del-acc="'+esc(a.account_id)+'">'+t('common.delete')+'</button></td></tr>';}).join(""):'<tr><td colspan="6" class="empty"><div class="empty-state"><strong>'+t('msg.noAcc')+'</strong><span>'+t('msg.noAccHint')+'</span></div></td></tr>';
$$("[data-del-acc]").forEach(function(b){b.addEventListener("click",function(){delAccount(b.getAttribute("data-del-acc"));});});}

function loadAccounts(){return api("/api/accounts").then(function(d){renderAccounts(d);return d;});}

function resetAccAuthForm(clear){app.accountAuthFlowId=null;("#accountCode").value="";$("#accountPassword").value="";$("#accountPasswordLabel").hidden=true;$("#accountConfirmPassword").hidden=true;if(clear){$("#accountApiId").value="";$("#accountApiHash").value="";$("#accountPhone").value="";}}
function setAccBadge(s){var b=$("#accountAuthBadge");if(!b)return;b.className="badge";b.classList.add(s==="authorized"?"active":"warn");b.textContent=s;}

function startAccAuth(){setAccBadge(t('status.sending'));$("#accountAuthMessage").textContent=t('msg.sendingCode');api("/api/accounts/auth",{method:"POST",body:JSON.stringify({action:"start",api_id:$("#accountApiId").value.trim(),api_hash:$("#accountApiHash").value.trim(),phone:$("#accountPhone").value.trim()})}).then(function(d){var a=d.auth||{};if(a.authorized||a.already_authorized){resetAccAuthForm(true);setAccBadge(t('status.authorized'));$("#accountAuthMessage").textContent=t('msg.accAuth');}else{app.accountAuthFlowId=a.flow_id;setAccBadge(t('status.codeSent'));$("#accountAuthMessage").textContent=t('msg.codeSentPhone',{n:a.phone||"phone"});}renderAccounts(d);}).catch(function(e){setAccBadge(t('status.error'));$("#accountAuthMessage").textContent=(e.data&&e.data.message)||(e.data&&e.data.error)||e.message;});}

function confirmAccCode(){if(!app.accountAuthFlowId){$("#accountAuthMessage").textContent=t('msg.sendFirst');return;}setAccBadge(t('status.checking'));api("/api/accounts/auth",{method:"POST",body:JSON.stringify({action:"code",flow_id:app.accountAuthFlowId,code:$("#accountCode").value.trim()})}).then(function(d){var a=d.auth||{};$("#accountCode").value="";if(a.password_required){$("#accountPasswordLabel").hidden=false;$("#accountConfirmPassword").hidden=false;setAccBadge("2FA");$("#accountAuthMessage").textContent=t('msg.enter2fa');return;}resetAccAuthForm(true);setAccBadge(t('status.authorized'));$("#accountAuthMessage").textContent=t('msg.accAdded');renderAccounts(d);}).catch(function(e){setAccBadge(t('status.error'));$("#accountAuthMessage").textContent=(e.data&&e.data.message)||(e.data&&e.data.error)||e.message;});}

function confirmAccPwd(){if(!app.accountAuthFlowId){$("#accountAuthMessage").textContent=t('msg.noActive');return;}setAccBadge(t('status.checking'));api("/api/accounts/auth",{method:"POST",body:JSON.stringify({action:"password",flow_id:app.accountAuthFlowId,password:$("#accountPassword").value})}).then(function(d){resetAccAuthForm(true);setAccBadge(t('status.authorized'));$("#accountAuthMessage").textContent=t('msg.accAdded');renderAccounts(d);}).catch(function(e){$("#accountPassword").value="";setAccBadge(t('status.error'));$("#accountAuthMessage").textContent=(e.data&&e.data.message)||(e.data&&e.data.error)||e.message;});}

function cancelAccAuth(){if(app.accountAuthFlowId){api("/api/accounts/auth",{method:"POST",body:JSON.stringify({action:"cancel",flow_id:app.accountAuthFlowId})}).catch(function(){});}resetAccAuthForm(false);setAccBadge(t('status.notStarted'));$("#accountAuthMessage").textContent=t('msg.loginReset');}

function delAccount(id){if(!confirm(t('msg.delConfirm')))return;api("/api/accounts/delete",{method:"POST",body:JSON.stringify({account_id:id})}).then(function(d){renderAccounts(d);}).catch(function(e){var m=$("#accountsMeta");if(m)m.textContent=(e.data&&e.data.message)||(e.data&&e.data.error)||e.message;});}

function loadConfig(){return api("/api/config").then(function(d){app.config=d;$("#batchSize").value=d.batch_size;$("#generationMinLength").value=d.generation_min_length||d.username_min_length||5;$("#generationMaxLength").value=d.generation_max_length||d.username_max_length||6;$("#generationAllowDigits").checked=!!d.generation_allow_digits;$("#tgMinScore").value=d.score_threshold;$("#tgLimit").max=d.max_telegram_checks;});}

function loadDashboard(){return api("/api/stats").then(function(d){var s=d.stats||{};var items=[["total_evaluated","stats.totalEvaluated"],["total_checked","stats.totalChecked"],["total_available","stats.totalAvailable"],["total_taken_invalid","stats.totalTaken"],["total_used","stats.totalUsed"],["total_unchecked","stats.totalUnchecked"],["avg_score","stats.avgScore"],["best_score","stats.bestScore"],["last_batch_num","stats.lastBatchNum"],["last_batch_count","stats.lastBatchCount"],["last_batch_checked","stats.lastBatchChecked"],["last_batch_available","stats.lastBatchAvail"]];$("#statsGrid").innerHTML=items.map(function(it){return '<article class="card stat-card" data-stat="'+it[0]+'"><div class="stat-label">'+t(it[1])+'</div><div class="stat-value">'+fmtNumber(s[it[0]])+'</div></article>';}).join("");$("#dashMeta").textContent=t('common.updated')+': '+new Date().toLocaleTimeString(LOCALE_MAP[curLang]||'en-US');return loadMiniTables();});}

function loadMiniTables(){return Promise.all([api("/api/usernames?last_batch=1&limit=10").then(function(last){$("#lastBatchRows").innerHTML=last.rows.length?last.rows.map(function(r){return rowHtml(r);}).join(""):'<tr><td colspan="5" class="empty"><div class="empty-state"><strong>'+t('msg.noBatchData')+'</strong><span>'+t('msg.noBatchDataHint')+'</span></div></td></tr>';}),api("/api/usernames?status=available&valid_only=1&limit=10").then(function(av){$("#availableTopRows").innerHTML=av.rows.length?av.rows.map(function(r){return '<tr><td class="mono">@'+esc(r.username)+'</td><td>'+fmtScore(r.score)+'</td><td>'+esc(r.generation_type||"-")+'</td></tr>';}).join(""):'<tr><td colspan="3" class="empty"><div class="empty-state"><strong>'+t('msg.noAvail')+'</strong><span>'+t('msg.noAvailHint')+'</span></div></td></tr>';})]);}

function loadDatabase(){var p=new URLSearchParams();p.set("status",$("#dbStatus").value);p.set("limit",$("#dbLimit").value||"50");if($("#dbSearch").value.trim())p.set("search",$("#dbSearch").value.trim());if($("#dbMinScore").value)p.set("min_score",$("#dbMinScore").value);if($("#dbLastBatch").checked)p.set("last_batch","1");return api('/api/usernames?'+p.toString()).then(function(d){$("#databaseMeta").textContent=d.has_more?t('db.shownMore',{n:d.total_visible}):t('db.shown',{n:d.total_visible});$("#databaseRows").innerHTML=d.rows.length?d.rows.map(function(r){return '<tr><td class="mono">@'+esc(r.username)+'</td><td>'+fmtScore(r.score)+'</td><td>'+badge(r.status)+'</td><td>'+esc(r.generation_type||"-")+'</td><td>'+esc(r.batch_num||"-")+'</td><td>'+esc(r.checked_at||"-")+'</td><td class="notes">'+esc(r.notes||"")+'</td></tr>';}).join(""):'<tr><td colspan="7" class="empty"><div class="empty-state"><strong>'+t('msg.nothingFound')+'</strong><span>'+t('msg.nothingFoundHint')+'</span></div></td></tr>';});}

function startGeneration(){$("#generateBtn").disabled=true;$("#generationStatus").textContent=t('gen.launching');setProgress("#generationProgress",1);api("/api/generate",{method:"POST",body:JSON.stringify({batch_size:Number($("#batchSize").value||app.config.batch_size||100),min_length:Number($("#generationMinLength").value||5),max_length:Number($("#generationMaxLength").value||6),allow_digits:$("#generationAllowDigits").checked})}).then(function(d){$("#generationTaskId").textContent=d.task.id;return pollTask(d.task.id,renderGenTask);}).catch(function(e){$("#generationStatus").textContent=e.message;}).then(function(){$("#generateBtn").disabled=false;return loadDashboard();});}

function renderGenTask(tk){$("#generationStatus").textContent=tk.message||tk.status;setProgress("#generationProgress",tk.progress||0);if(tk.status==="completed"&&tk.result){var rows=tk.result.rows||[];$("#generationRows").innerHTML=rows.length?rows.map(function(r){return rowHtml(r);}).join(""):'<tr><td colspan="5" class="empty"><div class="empty-state"><strong>'+t('msg.genNoResults')+'</strong><span>'+t('msg.genNoResultsHint')+'</span></div></td></tr>';}if(tk.status==="failed"){$("#generationRows").innerHTML='<tr><td colspan="5" class="empty"><div class="empty-state"><strong>'+t('msg.genError')+'</strong><span>'+esc(tk.error||"Error")+'</span></div></td></tr>';}}

function loadTgAuthStatus(){return api("/api/telegram/auth/status").then(function(d){renderTgAuth(d.auth||{});return d.auth||{};});}
function loadTgConfig(){return api("/api/telegram/config").then(function(d){renderTgConfig(d.telegram_config||{});return d.telegram_config||{};});}

function renderTgConfig(c){var b=$("#tgConfigBadge");if(!b)return;b.className="badge";var ok=!!(c.api_id&&c.api_hash_set);b.classList.add(ok?"available":"warn");b.textContent=ok?t('status.configured'):t('status.notReady');$("#tgApiId").value=c.api_id||"";$("#tgConfigPhone").value=c.phone||"";$("#tgApiHash").value="";$("#tgApiHash").placeholder=t('tg.apiHashPH');if(!$("#tgPhone").value.trim()&&c.phone)$("#tgPhone").value=c.phone;$("#tgConfigMessage").textContent=ok?t('msg.mainSession',{n:c.session_name||"telegram_session"}):t('msg.fillApi');}

function saveTgConfig(){$("#tgConfigMessage").textContent=t('msg.savingApi');api("/api/telegram/config",{method:"POST",body:JSON.stringify({api_id:$("#tgApiId").value.trim(),api_hash:$("#tgApiHash").value.trim(),phone:$("#tgConfigPhone").value.trim()})}).then(function(d){var c=d.telegram_config||{};renderTgConfig(c);$("#tgPhone").value=c.phone||"";$("#tgConfigMessage").textContent=c.api_hash_changed?t('msg.hashChanged'):t('msg.noHashChange');return loadTgAuthStatus();}).catch(function(e){$("#tgConfigMessage").textContent=(e.data&&e.data.message)||e.message;});}

function renderTgAuth(a){var b=$("#tgAuthBadge");if(!b)return;b.className="badge";if(!a.configured){b.classList.add("invalid");b.textContent=t('status.notConfigured');$("#tgAuthDetails").textContent=a.error||t('msg.fillApi');return;}if(a.authorized&&a.session_matches_config===false){var u=a.user||{};b.classList.add("invalid");b.textContent=t('status.wrongAccount');var un=u.username?'@'+u.username:t('status.noUsername');$("#tgAuthDetails").textContent=a.error||t('msg.wrongDetail',{u:un});}else if(a.authorized){var u=a.user||{};b.classList.add("available");b.textContent=t('status.authorized');var un=u.username?'@'+u.username:t('status.noUsername');var nm=((u.first_name||'')+' '+(u.last_name||'')).trim();$("#tgAuthDetails").textContent=t('msg.authDetail',{name:nm||un,u:un,id:u.id||"-"});}else{b.classList.add("warn");b.textContent=t('status.loginReq');$("#tgAuthDetails").textContent=a.error||t('msg.loginReqDetail',{n:a.session_name||"telegram_session"});}}

function sendTgCode(){$("#tgAuthMessage").textContent=t('msg.sendingCode');api("/api/telegram/auth/start",{method:"POST",body:JSON.stringify({phone:$("#tgPhone").value.trim()})}).then(function(d){var a=d.auth||{};if(a.already_authorized||a.authorized){renderTgAuth(a);$("#tgAuthMessage").textContent=t('msg.alreadyAuth');return;}app.authFlowId=a.flow_id;$("#tgAuthMessage").textContent=t('msg.codeSentPhone',{n:a.phone||"phone"});}).catch(function(e){$("#tgAuthMessage").textContent=e.message;});}

function confirmTgCode(){if(!app.authFlowId){$("#tgAuthMessage").textContent=t('msg.sendFirst');return;}$("#tgAuthMessage").textContent=t('msg.checkingCode');api("/api/telegram/auth/confirm",{method:"POST",body:JSON.stringify({flow_id:app.authFlowId,code:$("#tgCode").value.trim()})}).then(function(d){var a=d.auth||{};$("#tgCode").value="";if(a.password_required){$("#tgAuthMessage").textContent=t('msg.enter2fa');return;}app.authFlowId=null;renderTgAuth(a);$("#tgAuthMessage").textContent=t('msg.loginOk');}).catch(function(e){$("#tgAuthMessage").textContent=e.message;});}

function confirmTgPwd(){if(!app.authFlowId){$("#tgAuthMessage").textContent=t('msg.noActive');return;}$("#tgAuthMessage").textContent=t('msg.checking2fa');api("/api/telegram/auth/password",{method:"POST",body:JSON.stringify({flow_id:app.authFlowId,password:$("#tgPassword").value})}).then(function(d){$("#tgPassword").value="";app.authFlowId=null;renderTgAuth(d.auth||{});$("#tgAuthMessage").textContent=t('msg.loginOk');}).catch(function(e){$("#tgPassword").value="";$("#tgAuthMessage").textContent=e.message;});}

function cancelTgAuth(){if(app.authFlowId){api("/api/telegram/auth/cancel",{method:"POST",body:JSON.stringify({flow_id:app.authFlowId})}).catch(function(){});}app.authFlowId=null;$("#tgCode").value="";$("#tgPassword").value="";$("#tgAuthMessage").textContent=t('msg.loginReset');loadTgAuthStatus();}

function resetTgSession(){if(!confirm(t('msg.resetConfirm')))return;$("#tgAuthMessage").textContent=t('msg.resettingSession');api("/api/telegram/auth/reset-session",{method:"POST",body:JSON.stringify({})}).then(function(){app.authFlowId=null;$("#tgCode").value="";$("#tgPassword").value="";$("#tgAuthMessage").textContent=t('msg.sessionReset');return loadTgAuthStatus();}).catch(function(e){$("#tgAuthMessage").textContent=e.message;});}

function loadTgPreview(){var p=new URLSearchParams();p.set("limit",$("#tgLimit").value||"10");p.set("min_score",$("#tgMinScore").value||app.config.score_threshold||"6");var mu=$("#tgManualUsername").value.trim();if(mu)p.set("username",mu);api('/api/telegram/preview?'+p.toString()).then(function(d){app.telegramPreview=d;$("#telegramMeta").textContent=t('msg.candidates',{source:d.source,count:d.candidate_count,skipped:d.skipped_count});$("#telegramStatus").textContent=t('msg.previewReady');$("#telegramRows").innerHTML=d.candidates.length?d.candidates.map(function(r){return '<tr><td><input type="checkbox" class="tgPick" value="'+esc(r.username)+'" checked></td><td class="mono">@'+esc(r.username)+'</td><td>'+fmtScore(r.score)+'</td><td>'+badge(r.status)+'</td><td>'+esc(r.generation_type||"-")+'</td><td>'+esc(r.batch_num||"-")+'</td></tr>';}).join(""):'<tr><td colspan="6" class="empty"><div class="empty-state"><strong>'+t('tg.noCandidates')+'</strong><span>'+t('tg.noCandidatesHint')+'</span></div></td></tr>';$("#telegramSkippedRows").innerHTML=d.skipped.length?d.skipped.map(function(i){return '<tr><td class="mono">@'+esc(i.username)+'</td><td>'+esc(i.reason)+'</td></tr>';}).join(""):'<tr><td colspan="2" class="empty"><div class="empty-state"><strong>'+t('tg.noSkips')+'</strong><span>'+t('tg.noSkipsHint')+'</span></div></td></tr>';});}

function checkTgSelected(){var usernames=$$$$(".tgPick:checked").map(function(i){return i.value;});var mu=$("#tgManualUsername").value.trim().replace(/^@/,"").toLowerCase();if(mu&&usernames.indexOf(mu)===-1)usernames.unshift(mu);$("#telegramStatus").textContent=t('common.loading');setProgress("#telegramProgress",1);var dry=$("#tgDryRun").checked;if(!dry&&$("#tgConfirm").value.trim()!=="CHECK"){$("#telegramStatus").textContent=t('tg.enterCheck');return;}api("/api/telegram/check",{method:"POST",body:JSON.stringify({usernames:usernames,limit:Number($("#tgLimit").value||10),min_score:Number($("#tgMinScore").value||app.config.score_threshold||6),dry_run:dry,confirm:$("#tgConfirm").value.trim()})}).then(function(d){if(d.dry_run){$("#telegramStatus").textContent=d.message;app.telegramPreview=d.preview;return;}$("#telegramTaskId").textContent=d.task.id;return pollTask(d.task.id,renderTgTask).then(function(ft){return loadDashboard().then(function(){if(ft.status==="completed"&&ft.result){var ck=ft.result.checked_count||0,av=ft.result.available_count||0;$("#telegramStatus").textContent=t('msg.checkDone',{checked:ck,available:av});}});});}).catch(function(e){$("#telegramStatus").textContent=(e.data&&e.data.message)||e.message;});}

function syncTelegramMode(){var dry=$("#tgDryRun").checked;$("#tgCheckBtn").textContent=dry?t('tg.previewSel'):t('tg.checkSelLive');$("#telegramMeta").textContent=dry?t('tg.subtitle'):t('tg.enterCheck');$("#tgModeLabel").textContent=dry?"dry-run":"live check";$("#tgConfirmState").textContent=dry?"-":"CHECK";$("#tgConfirm").disabled=dry;}

function renderTgTask(tk){$("#telegramStatus").textContent=tk.message||tk.status;setProgress("#telegramProgress",tk.progress||0);loadAccounts().catch(function(){});if(tk.status==="completed"&&tk.result){$("#telegramRows").innerHTML=(tk.result.rows||[]).map(function(r){return '<tr><td></td><td class="mono">@'+esc(r.username)+'</td><td>'+fmtScore(r.score)+'</td><td>'+badge(r.status)+'</td><td>'+esc(r.generation_type||"-")+'</td><td>'+esc(r.batch_num||"-")+'</td></tr>';}).join("");}}

function loadChannels(){var p=new URLSearchParams();p.set("limit",$("#channelLimit").value||"20");if($("#channelMinScore").value)p.set("min_score",$("#channelMinScore").value);api('/api/channels/available?'+p.toString()).then(function(d){$("#channelRows").innerHTML=d.rows.length?d.rows.map(function(r){return '<tr><td class="mono">@'+esc(r.username)+'</td><td>'+fmtScore(r.score)+'</td><td>'+badge(r.status)+'</td><td>'+esc(r.generation_type||"-")+'</td><td><button class="btn" data-ch="'+esc(r.username)+'" data-sc="'+esc(r.score)+'">'+t('ch.select')+'</button></td></tr>';}).join(""):'<tr><td colspan="5" class="empty"><div class="empty-state"><strong>'+t('msg.noChAvail')+'</strong><span>'+t('msg.noChAvailHint')+'</span></div></td></tr>';$$("[data-ch]").forEach(function(b){b.addEventListener("click",function(){selectCh(b.getAttribute("data-ch"),b.getAttribute("data-sc"));});});});}

function selectCh(u,s){app.selectedChannel={username:u,score:s};("#selectedChannelName").textContent='@'+u;$("#selectedChannelScore").textContent='score: '+fmtScore(s);$("#channelTitle").value=u;var ct=$("#chConfirmText");if(ct)ct.textContent=u+' (score: '+fmtScore(s)+')? (y/n)';$("#channelStatus").textContent=t('msg.readyPreview');}

function createChannel(){if(!app.selectedChannel){$("#channelStatus").textContent=t('ch.notSelected');return;}$("#channelStatus").textContent=t('common.loading');setProgress("#channelProgress",1);api("/api/channels/create",{method:"POST",body:JSON.stringify({username:app.selectedChannel.username,title:$("#channelTitle").value.trim(),dry_run:$("#channelDryRun").checked,confirm:$("#channelConfirm").value.trim()})}).then(function(d){if(d.dry_run){$("#channelStatus").textContent=d.message;return;}$("#channelTaskId").textContent=d.task.id;return pollTask(d.task.id,renderChTask).then(function(){return Promise.all([loadDashboard(),loadChannels()]);});}).catch(function(e){$("#channelStatus").textContent=(e.data&&e.data.message)||(e.data&&e.data.reason)||e.message;});}

function renderChTask(tk){$("#channelStatus").textContent=tk.message||tk.status;setProgress("#channelProgress",tk.progress||0);if(tk.status==="completed"&&tk.result)$("#channelStatus").textContent=t('msg.created',{n:tk.result.channel_id});}

function pollTask(id,render){function loop(){return api('/api/tasks/'+id).then(function(d){var tk=d.task;render(tk);if(tk.status!=="running")return tk;return new Promise(function(r){setTimeout(r,1200);}).then(loop);});}return loop();}

function loadLogs(){var l=$("#logLines").value||"160";api('/api/logs?lines='+encodeURIComponent(l)).then(function(d){$("#logsMeta").textContent=d.path;$("#logsBox").textContent=d.text||"";$("#logsBox").scrollTop=$("#logsBox").scrollHeight;});}

function bindEvents(){
$$$$(".nav button").forEach(function(b){b.addEventListener("click",function(){$$(".nav button").forEach(function(i){i.classList.remove("is-active");});$$(".section").forEach(function(i){i.classList.remove("is-active");});b.classList.add("is-active");var target=document.getElementById(b.getAttribute("data-tab"));if(target)target.classList.add("is-active");});});
$$(".lang-btn").forEach(function(b){b.addEventListener("click",function(){setLang(b.getAttribute("data-lang"));});});
$("#refreshDashboard").addEventListener("click",loadDashboard);
$("#loadDatabase").addEventListener("click",loadDatabase);
$("#dbSearch").addEventListener("keydown",function(e){if(e.key==="Enter")loadDatabase();});
$("#generateBtn").addEventListener("click",startGeneration);
$("#tgSaveConfig").addEventListener("click",saveTgConfig);
$("#tgAuthRefresh").addEventListener("click",loadTgAuthStatus);
$("#tgSendCode").addEventListener("click",sendTgCode);
$("#tgConfirmCode").addEventListener("click",confirmTgCode);
$("#tgConfirmPassword").addEventListener("click",confirmTgPwd);
$("#tgCancelAuth").addEventListener("click",cancelTgAuth);
$("#tgResetSession").addEventListener("click",resetTgSession);
$("#tgCode").addEventListener("keydown",function(e){if(e.key==="Enter")confirmTgCode();});
$("#tgPassword").addEventListener("keydown",function(e){if(e.key==="Enter")confirmTgPwd();});
$("#tgPreviewBtn").addEventListener("click",loadTgPreview);
$("#tgCheckBtn").addEventListener("click",checkTgSelected);
$("#tgDryRun").addEventListener("change",syncTelegramMode);
$("#accountAddBtn").addEventListener("click",function(){resetAccAuthForm(true);setAccBadge(t('status.notStarted'));$("#accountAuthMessage").textContent=t('acc.apiNote');$("#accountApiId").focus();});
$("#accountSendCode").addEventListener("click",startAccAuth);
$("#accountConfirmCode").addEventListener("click",confirmAccCode);
$("#accountConfirmPassword").addEventListener("click",confirmAccPwd);
$("#accountCancelAuth").addEventListener("click",cancelAccAuth);
$("#accountCode").addEventListener("keydown",function(e){if(e.key==="Enter")confirmAccCode();});
$("#accountPassword").addEventListener("keydown",function(e){if(e.key==="Enter")confirmAccPwd();});
$("#loadChannels").addEventListener("click",loadChannels);
$("#createChannelBtn").addEventListener("click",createChannel);
$("#refreshLogs").addEventListener("click",loadLogs);
}

function init(){
registerBrowserClient().then(function(){
bindEvents();
applyI18n();
syncTelegramMode();
return loadConfig();
}).then(function(){
return Promise.all([
loadDashboard().catch(function(){}),
loadDatabase().catch(function(){}),
loadTgConfig().catch(function(){}),
loadTgAuthStatus().catch(function(){}),
loadAccounts().catch(function(){}),
loadTgPreview().catch(function(){}),
loadChannels().catch(function(){}),
loadLogs().catch(function(){})
]);
}).catch(function(e){console.error(e);var dm=$("#dashMeta");if(dm)dm.textContent=e.message;});
}

init();
</script>
</body>
</html>
"""
