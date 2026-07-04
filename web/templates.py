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
:root{
--bg:#050510;
--glass:rgba(12,15,40,.55);
--glass-h:rgba(18,22,50,.7);
--glass-b:rgba(255,255,255,.06);
--glass-bh:rgba(255,255,255,.12);
--blur:blur(20px) saturate(1.4);
--cyan:#00e5ff;--purple:#a855f7;--pink:#f43f5e;
--blue:#3b82f6;--green:#10b981;--amber:#f59e0b;--red:#ef4444;
--txt:#e2e8f0;--txt-b:#f8fafc;--txt-m:#94a3b8;--txt-d:#64748b;
--sidebar-bg:rgba(8,10,28,.95);
--sidebar-w:260px;
--r-sm:6px;--r:10px;--r-lg:14px;
--glow-c:0 0 15px rgba(0,229,255,.15),0 0 40px rgba(0,229,255,.05);
--glow-p:0 0 15px rgba(168,85,247,.15),0 0 40px rgba(168,85,247,.05);
--shadow:0 8px 32px rgba(0,0,0,.3);
--shadow-h:0 12px 48px rgba(0,0,0,.4);
--focus:0 0 0 3px rgba(0,229,255,.25);
--fd:'Orbitron',sans-serif;--fb:'Outfit',sans-serif;--fm:'JetBrains Mono',monospace;
--tf:150ms cubic-bezier(.4,0,.2,1);--tn:250ms cubic-bezier(.4,0,.2,1);--ts:400ms cubic-bezier(.16,1,.3,1)
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
[hidden]{display:none!important}
html{overflow-x:hidden;scroll-behavior:smooth}
body{min-height:100vh;background:radial-gradient(ellipse at 18% 0%,rgba(88,28,135,.15) 0%,transparent 50%),radial-gradient(ellipse at 82% 100%,rgba(0,100,150,.12) 0%,transparent 50%),var(--bg);background-attachment:fixed;color:var(--txt);font:14px/1.5 var(--fb),sans-serif;font-variant-numeric:tabular-nums;-webkit-font-smoothing:antialiased}
body::before{content:'';position:fixed;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");pointer-events:none;z-index:9999}
button,input,select,textarea{font:inherit}
.app{display:grid;grid-template-columns:var(--sidebar-w) minmax(0,1fr);min-height:100vh}

/* === SIDEBAR === */
.sidebar{position:sticky;top:0;display:flex;flex-direction:column;height:100vh;padding:20px 14px 16px;background:var(--sidebar-bg);backdrop-filter:blur(30px);border-right:1px solid rgba(0,229,255,.06);color:var(--txt);overflow-y:auto;overflow-x:hidden}
.sidebar::after{content:'';position:absolute;top:0;right:0;width:1px;height:100%;background:linear-gradient(180deg,transparent,var(--cyan) 20%,var(--purple) 50%,var(--cyan) 80%,transparent);opacity:.3;pointer-events:none}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:18px;padding:0 6px 14px;border-bottom:1px solid rgba(255,255,255,.05)}
.brand-mark{display:grid;place-items:center;flex:0 0 38px;width:38px;height:38px;border-radius:var(--r);background:linear-gradient(135deg,rgba(0,229,255,.15),rgba(168,85,247,.15));border:1px solid rgba(0,229,255,.25);color:var(--cyan);font-family:var(--fd);font-size:11px;font-weight:900;box-shadow:var(--glow-c);animation:brandPulse 3s ease-in-out infinite}
@keyframes brandPulse{0%,100%{box-shadow:0 0 10px rgba(0,229,255,.15)}50%{box-shadow:0 0 20px rgba(0,229,255,.3),0 0 40px rgba(0,229,255,.1)}}
.brand-copy{display:grid;gap:2px;min-width:0}
.brand h1{color:var(--txt-b);font-family:var(--fd);font-size:15px;font-weight:700;letter-spacing:.05em}
.brand-copy>span{color:var(--txt-d);font-size:11px}
.brand .pill{margin-inline-start:auto;padding:3px 9px;border-radius:999px;background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.2);color:var(--cyan);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em}

/* lang switcher */
.lang-switch{display:flex;gap:4px;margin-bottom:16px;padding:0 6px}
.lang-btn{flex:1;padding:6px 0;border:1px solid rgba(255,255,255,.06);border-radius:var(--r-sm);background:transparent;color:var(--txt-d);font-size:11px;font-weight:600;cursor:pointer;transition:all var(--tf);text-transform:uppercase;letter-spacing:.06em}
.lang-btn:hover{background:rgba(255,255,255,.05);color:var(--txt);border-color:rgba(255,255,255,.1)}
.lang-btn.is-active{background:rgba(0,229,255,.1);border-color:rgba(0,229,255,.3);color:var(--cyan);box-shadow:0 0 10px rgba(0,229,255,.1)}

/* nav */
.nav{display:grid;gap:3px}
.nav button{position:relative;display:flex;align-items:center;gap:10px;width:100%;min-height:40px;padding:9px 12px;border:1px solid transparent;border-radius:var(--r);background:transparent;color:var(--txt-m);text-align:start;cursor:pointer;font-size:13px;font-weight:500;transition:all var(--tn)}
.nav button::before{content:attr(data-icon);display:grid;place-items:center;flex:0 0 24px;width:24px;height:24px;border:1px solid rgba(255,255,255,.06);border-radius:var(--r-sm);background:rgba(255,255,255,.03);color:currentColor;font-family:var(--fd);font-size:10px;font-weight:700;transition:all var(--tn)}
.nav button:hover{background:rgba(255,255,255,.04);color:var(--txt);border-color:rgba(255,255,255,.06);transform:translateX(2px)}
[dir="rtl"] .nav button:hover{transform:translateX(-2px)}
.nav button.is-active{background:rgba(0,229,255,.06);color:var(--txt-b);border-color:rgba(0,229,255,.15)}
.nav button.is-active::before{border-color:rgba(0,229,255,.3);background:rgba(0,229,255,.12);color:var(--cyan);box-shadow:0 0 8px rgba(0,229,255,.2)}
.nav button.is-active::after{content:'';position:absolute;top:50%;inset-inline-start:0;transform:translateY(-50%);width:3px;height:60%;border-radius:0 3px 3px 0;background:var(--cyan);box-shadow:0 0 8px var(--cyan)}

/* donation */
.donation-cta{position:relative;display:grid;align-items:center;min-height:80px;margin-top:auto;padding:14px 14px 14px 48px;border:1px solid rgba(168,85,247,.15);border-radius:var(--r);background:linear-gradient(135deg,rgba(168,85,247,.08),rgba(0,229,255,.04));color:var(--txt);text-decoration:none;overflow:hidden;transition:all var(--tn)}
.donation-cta::before{content:'\2665';position:absolute;top:50%;inset-inline-start:14px;transform:translateY(-50%);display:grid;place-items:center;width:28px;height:28px;border:1px solid rgba(244,63,94,.3);border-radius:var(--r-sm);background:rgba(244,63,94,.1);color:var(--pink);font-size:14px;transition:all var(--tn)}
.donation-cta:hover{border-color:rgba(168,85,247,.3);background:linear-gradient(135deg,rgba(168,85,247,.12),rgba(0,229,255,.06));transform:translateY(-1px);box-shadow:0 4px 20px rgba(168,85,247,.1)}
.donation-cta__copy{display:grid;gap:3px;min-width:0}
.donation-cta__label{color:var(--purple);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.donation-cta__title{color:var(--txt);font-size:13px;font-weight:600;line-height:1.3}
.donation-cta__hint{color:var(--txt-d);font-size:11px}

/* === MAIN === */
main{min-width:0;padding:28px 30px 40px}
.section{display:none;width:100%;max-width:1300px;animation:secIn .3s ease-out}
.section.is-active{display:block}
@keyframes secIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.section-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:20px}
.section-title{margin:0;font-family:var(--fd);font-size:24px;font-weight:700;color:var(--txt-b);letter-spacing:.03em}
.section-meta{margin-top:5px;color:var(--txt-m);font-size:13px;line-height:1.5}

/* === GLASS PANELS === */
.card,.panel,.toolbar,.table-wrap{border:1px solid var(--glass-b);border-radius:var(--r);background:var(--glass);backdrop-filter:var(--blur);box-shadow:var(--shadow);transition:border-color var(--tn),box-shadow var(--tn)}
.card:hover,.panel:hover{border-color:var(--glass-bh)}

/* stats */
.stats-grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));margin-bottom:20px}
.stat-card{position:relative;min-height:100px;padding:16px 16px 14px 20px;overflow:hidden;background:var(--glass);backdrop-filter:var(--blur);animation:cardUp .5s ease-out backwards}
.stat-card:nth-child(1){animation-delay:0s}.stat-card:nth-child(2){animation-delay:.05s}.stat-card:nth-child(3){animation-delay:.1s}.stat-card:nth-child(4){animation-delay:.15s}.stat-card:nth-child(5){animation-delay:.2s}.stat-card:nth-child(6){animation-delay:.25s}.stat-card:nth-child(7){animation-delay:.3s}.stat-card:nth-child(8){animation-delay:.35s}.stat-card:nth-child(9){animation-delay:.4s}.stat-card:nth-child(10){animation-delay:.45s}.stat-card:nth-child(11){animation-delay:.5s}.stat-card:nth-child(12){animation-delay:.55s}
@keyframes cardUp{from{opacity:0;transform:translateY(16px) scale(.97)}to{opacity:1;transform:translateY(0) scale(1)}}
.stat-card::before{content:'';position:absolute;inset:0 auto 0 0;width:3px;border-radius:0 3px 3px 0;background:var(--sc,var(--cyan));box-shadow:0 0 10px var(--sc,var(--cyan));transition:box-shadow var(--tn)}
.stat-card:hover::before{box-shadow:0 0 18px var(--sc,var(--cyan))}
[data-stat="total_checked"],[data-stat="last_batch_checked"]{--sc:var(--blue)}
[data-stat="total_available"],[data-stat="last_batch_available"]{--sc:var(--green)}
[data-stat="total_taken_invalid"]{--sc:var(--red)}
[data-stat="total_unchecked"]{--sc:var(--amber)}
[data-stat="total_used"]{--sc:var(--purple)}
[data-stat="total_evaluated"]{--sc:var(--cyan)}
[data-stat="avg_score"],[data-stat="best_score"]{--sc:var(--pink)}
[data-stat="last_batch_num"],[data-stat="last_batch_count"]{--sc:var(--blue)}
.stat-label{color:var(--txt-m);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em}
.stat-value{margin-top:8px;font-family:var(--fd);font-size:26px;font-weight:700;color:var(--txt-b);white-space:nowrap}

/* panel headings */
.panel-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:10px}
.panel-title{margin:0;color:var(--txt-b);font-size:16px;font-weight:600}
.panel-caption{color:var(--txt-d);font-size:12px;white-space:nowrap}

/* toolbar */
.toolbar{display:flex;flex-wrap:wrap;align-items:flex-end;gap:10px;margin-bottom:14px;padding:14px}
label{display:grid;gap:5px;min-width:120px;color:var(--txt-m);font-size:12px;font-weight:500}
input,select{width:100%;min-height:38px;padding:8px 12px;border:1px solid rgba(255,255,255,.08);border-radius:var(--r-sm);background:rgba(0,0,0,.2);color:var(--txt);transition:all var(--tf)}
input::placeholder{color:var(--txt-d)}
input:hover,select:hover{border-color:rgba(255,255,255,.15)}
input:focus,select:focus{outline:0;border-color:var(--cyan);box-shadow:var(--focus),0 0 20px rgba(0,229,255,.08)}
input[type="checkbox"]{min-height:auto;width:16px;height:16px;padding:0;accent-color:var(--cyan)}
.check-label{display:inline-flex;grid-template-columns:none;align-items:center;min-width:auto;min-height:38px;gap:8px;color:var(--txt);font-size:13px;font-weight:500}

/* buttons */
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

/* tables */
.table-wrap{width:100%;overflow:auto}
.table-wrap .btn{min-height:32px;padding:5px 10px;font-size:12px}
table{width:100%;border-collapse:collapse;min-width:760px;font-size:13px}
th,td{padding:11px 12px;border-bottom:1px solid rgba(255,255,255,.04);text-align:start;vertical-align:middle;white-space:nowrap}
th{background:rgba(0,0,0,.2);color:var(--txt-m);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;position:sticky;top:0;z-index:1}
tbody tr{transition:background var(--tf)}
tbody tr:hover{background:rgba(0,229,255,.03)}
td.notes{max-width:300px;overflow:hidden;text-overflow:ellipsis}
.mono{font-family:var(--fm);font-size:12px;font-weight:600;color:var(--cyan)}

/* badges */
.badge{display:inline-flex;align-items:center;gap:5px;min-height:24px;padding:2px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.04);color:var(--txt-m);font-size:11px;font-weight:600;white-space:nowrap}
.badge::before{content:'';display:inline-block;width:5px;height:5px;border-radius:999px;background:currentColor}
.badge.available,.badge.active{border-color:rgba(16,185,129,.3);background:rgba(16,185,129,.08);color:var(--green);box-shadow:0 0 8px rgba(16,185,129,.1)}
.badge.cooldown,.badge.warn{border-color:rgba(245,158,11,.3);background:rgba(245,158,11,.08);color:var(--amber)}
.badge.dead,.badge.invalid,.badge.checked_taken,.badge.error{border-color:rgba(239,68,68,.3);background:rgba(239,68,68,.08);color:var(--red)}
.badge.unchecked{border-color:rgba(59,130,246,.3);background:rgba(59,130,246,.08);color:var(--blue)}
.badge.used{border-color:rgba(168,85,247,.3);background:rgba(168,85,247,.08);color:var(--purple)}

/* progress */
.progress{height:6px;overflow:hidden;border-radius:999px;background:rgba(255,255,255,.04)}
.progress>div{width:0%;height:100%;background:linear-gradient(90deg,var(--cyan),var(--purple),var(--pink));background-size:200% 100%;animation:progShim 2s linear infinite;transition:width 300ms ease;border-radius:999px;box-shadow:0 0 10px rgba(0,229,255,.3)}
@keyframes progShim{0%{background-position:200% 0}100%{background-position:-200% 0}}
.status-line{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:10px 0;color:var(--txt-m);font-size:13px}
.empty{padding:20px;color:var(--txt-m);text-align:center}
.empty-state{display:grid;gap:4px;justify-items:center;padding:6px 0;color:var(--txt-m);white-space:normal}
.empty-state strong{color:var(--txt);font-size:13px;font-weight:600}
.empty-state span{max-width:400px;font-size:12px;line-height:1.4}

/* log box */
.log-box{min-height:400px;max-height:70vh;margin:0;overflow:auto;padding:16px;border:1px solid rgba(0,229,255,.08);border-radius:var(--r);background:rgba(0,0,0,.5);backdrop-filter:blur(10px);color:#a5f3fc;white-space:pre-wrap;word-break:break-word;font-family:var(--fm);font-size:12px;line-height:1.6;box-shadow:inset 0 0 40px rgba(0,0,0,.3)}

/* scrollbar */
*::-webkit-scrollbar{width:6px;height:6px}
*::-webkit-scrollbar-track{background:transparent}
*::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:3px}
*::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.2)}

/* mode strip */
.mode-strip{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:14px}
.mode-cell{display:grid;gap:4px;min-height:70px;padding:14px;border:1px solid var(--glass-b);border-radius:var(--r);background:var(--glass);backdrop-filter:var(--blur);transition:all var(--tn)}
.mode-cell:hover{border-color:var(--glass-bh);box-shadow:var(--glow-c)}
.mode-cell span{color:var(--txt-m);font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.04em}
.mode-cell strong{color:var(--txt-b);font-size:14px;font-weight:600}
.mode-cell.is-warn{border-color:rgba(245,158,11,.2);background:rgba(245,158,11,.04)}
.selected-box{display:grid;gap:10px}
.selected-name{font-family:var(--fd);font-size:20px;font-weight:700;color:var(--cyan);text-shadow:0 0 20px rgba(0,229,255,.3)}

/* auth panels */
.auth-panel{display:grid;grid-template-columns:minmax(220px,.85fr) minmax(280px,1.2fr) minmax(320px,1.4fr);gap:14px;align-items:start;margin-bottom:14px}
.auth-summary{display:grid;gap:8px;align-content:start}
.auth-actions{display:grid;grid-template-columns:repeat(2,minmax(140px,1fr));gap:10px;align-items:end}
.auth-panel input,.auth-panel select{width:100%;min-width:0}
.auth-panel .btn{min-width:0;white-space:normal;line-height:1.2}
.config-actions{grid-template-columns:repeat(2,minmax(140px,1fr));margin-top:10px}
.accounts-auth{grid-template-columns:minmax(360px,1fr) minmax(360px,1fr)}
.accounts-auth .auth-actions{grid-template-columns:repeat(2,minmax(0,1fr))}

/* ambient orbs */
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
<!-- DASHBOARD -->
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

<!-- GENERATION -->
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
<label data-i18n="gen.batchSize">Batch Size<input id="batchSize" type="number" min="1" max="500" value="100"></label>
<label data-i18n="gen.minLength">Min Length<input id="generationMinLength" type="number" min="4" max="10" value="5"></label>
<label data-i18n="gen.maxLength">Max Length<input id="generationMaxLength" type="number" min="4" max="10" value="6"></label>
<label class="check-label"><input id="generationAllowDigits" type="checkbox"> <span data-i18n="gen.digits">digits</span></label>
<button class="btn primary" id="generateBtn" data-i18n="gen.generateBtn">Generate &amp; Evaluate</button>
</div>
<div class="panel"><div class="status-line"><span id="generationStatus" data-i18n="gen.ready">Ready to start</span><span id="generationTaskId"></span></div>
<div class="progress"><div id="generationProgress"></div></div></div>
<div class="table-wrap" style="margin-top:14px"><table><thead><tr><th>username</th><th>score</th><th data-i18n="th.status">status</th><th>generation_type</th><th>batch</th></tr></thead><tbody id="generationRows"></tbody></table></div>
</section>

<!-- DATABASE -->
<section id="database" class="section">
<div class="section-head"><div>
<h2 class="section-title" data-i18n="db.title">Username Database</h2>
<div class="section-meta" id="databaseMeta" data-i18n="db.limitOn">Output limit enabled</div>
</div></div>
<div class="toolbar">
<label data-i18n="common.status">Status<select id="dbStatus"><option value="all" data-i18n="db.all">All</option><option value="available">available</option><option value="unchecked">unchecked</option><option value="used">used</option><option value="taken_invalid">checked_taken/invalid</option><option value="checked">checked</option></select></label>
<label data-i18n="common.search">Search<input id="dbSearch" data-i18n-placeholder="db.searchPH" placeholder="username"></label>
<label>Min score<input id="dbMinScore" type="number" step="0.1" min="0" max="10"></label>
<label>Top N<input id="dbLimit" type="number" min="1" max="200" value="50"></label>
<label class="check-label"><input id="dbLastBatch" type="checkbox"> last batch</label>
<button class="btn primary" id="loadDatabase" data-i18n="common.show">Show</button>
</div>
<div class="table-wrap"><table><thead><tr><th>username</th><th>score</th><th data-i18n="th.status">status</th><th>generation_type</th><th>batch</th><th>checked_at</th><th>notes</th></tr></thead><tbody id="databaseRows"></tbody></table></div>
</section>

<!-- TELEGRAM -->
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
<label>API HASH<input id="tgApiHash" type="password" autocomplete="off" data-i18n-placeholder="tg.apiHashPH" placeholder="leave empty if already saved"></label>
<label data-i18n="common.phone">Phone<input id="tgConfigPhone" autocomplete="tel" placeholder="+79990000000"></label>
<button class="btn primary" id="tgSaveConfig" data-i18n="tg.saveApi">Save API</button>
</div>
<div class="section-meta" id="tgConfigMessage" style="margin-top:10px" data-i18n="tg.apiNote">This account is only for channel creation, not for live checks.</div>
</div>
<div class="panel">
<div class="status-line" style="margin:0 0 10px"><span data-i18n="tg.loginMain">Login to main account</span></div>
<div class="auth-actions">
<label data-i18n="common.phone">Phone<input id="tgPhone" data-i18n-placeholder="tg.phonePH" placeholder="+79990000000 or from .env"></label>
<button class="btn" id="tgSendCode" data-i18n="common.sendCode">Send Code</button>
<label data-i18n="common.code">Code<input id="tgCode" inputmode="numeric" autocomplete="one-time-code" placeholder="12345"></label>
<button class="btn primary" id="tgConfirmCode" data-i18n="common.login">Login</button>
<label data-i18n="common.2fa">2FA Password<input id="tgPassword" type="password" autocomplete="current-password" data-i18n-placeholder="common.ifEnabled" placeholder="if enabled"></label>
<button class="btn" id="tgConfirmPassword" data-i18n="tg.confirm2fa">Confirm 2FA</button>
<button class="btn" id="tgCancelAuth" data-i18n="tg.resetLogin">Reset Login</button>
<button class="btn danger" id="tgResetSession" data-i18n="tg.resetSession">Reset Session</button>
</div>
<div class="section-meta" id="tgAuthMessage" style="margin-top:10px" data-i18n="tg.codeNote">Code and password are not saved in the browser.</div>
</div>
</div>
<div class="toolbar">
<label data-i18n="tg.manualUsername">Manual username<input id="tgManualUsername" placeholder="@username"></label>
<label data-i18n="tg.checkLimit">Check limit<input id="tgLimit" type="number" min="1" max="30" value="10"></label>
<label>Min score<input id="tgMinScore" type="number" step="0.1" min="0" max="10" value="6"></label>
<label class="check-label"><input id="tgDryRun" type="checkbox" checked> dry-run</label>
<label data-i18n="tg.liveConfirm">Live confirm<input id="tgConfirm" data-i18n-placeholder="tg.confirmPH" placeholder="CHECK"></label>
<button class="btn" id="tgPreviewBtn" data-i18n="tg.preview">Preview</button>
<button class="btn primary" id="tgCheckBtn" data-i18n="tg.previewSel">Preview Selected</button>
</div>
<div class="panel"><div class="status-line"><span id="telegramStatus" data-i18n="tg.candidatesNotLoaded">Candidates not loaded</span><span id="telegramTaskId"></span></div>
<div class="progress"><div id="telegramProgress"></div></div></div>
<div class="split" style="margin-top:14px">
<div class="table-wrap"><table><thead><tr><th></th><th>username</th><th>score</th><th data-i18n="th.status">status</th><th>type</th><th>batch</th></tr></thead><tbody id="telegramRows"></tbody></table></div>
<div class="table-wrap"><table style="min-width:420px"><thead><tr><th>skip</th><th>reason</th></tr></thead><tbody id="telegramSkippedRows"></tbody></table></div>
</div></section>

<!-- ACCOUNTS -->
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
<label data-i18n="common.phone">Phone<input id="accountPhone" autocomplete="tel" placeholder="+79990000000"></label>
<button class="btn primary" id="accountSendCode" data-i18n="common.sendCode">Send Code</button>
</div>
<div class="section-meta" id="accountAuthMessage" style="margin-top:10px" data-i18n="acc.apiNote">API ID, API Hash and phone are saved locally after successful login.</div>
</div>
<div class="panel">
<div class="status-line" style="margin:0 0 10px"><span data-i18n="acc.loginConfirm">Login Confirmation</span></div>
<div class="auth-actions">
<label data-i18n="acc.tgCode">Telegram Code<input id="accountCode" inputmode="numeric" autocomplete="one-time-code" placeholder="12345"></label>
<button class="btn primary" id="accountConfirmCode" data-i18n="common.login">Login</button>
<label id="accountPasswordLabel" hidden data-i18n="common.2fa">2FA Password<input id="accountPassword" type="password" autocomplete="current-password" data-i18n-placeholder="common.ifEnabled" placeholder="if enabled"></label>
<button class="btn" id="accountConfirmPassword" hidden data-i18n="tg.confirm2fa">Confirm 2FA</button>
<button class="btn" id="accountCancelAuth" data-i18n="tg.resetLogin">Reset Login</button>
</div></div>
</div>
<div class="table-wrap"><table><thead><tr><th data-i18n="th.phone">phone</th><th data-i18n="th.status">status</th><th>cooldown</th><th>user</th><th data-i18n="th.lastError">last error</th><th></th></tr></thead><tbody id="accountsRows"></tbody></table></div>
</section>

<!-- CHANNELS -->
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
<label data-i18n="ch.channelName">Channel Name<input id="channelTitle" data-i18n-placeholder="common.optional" placeholder="optional"></label>
<label class="check-label"><input id="channelDryRun" type="checkbox" checked> dry-run</label>
<label id="channelConfirmLabel" data-i18n="ch.useUsername">Use username? (y/n)<input id="channelConfirm" data-i18n-placeholder="common.yes" placeholder="y"></label>
<button class="btn primary" id="createChannelBtn" data-i18n="ch.create">Create</button>
<div class="status-line"><span id="channelStatus" data-i18n="ch.notSelected">Username not selected</span><span id="channelTaskId"></span></div>
<div class="progress"><div id="channelProgress"></div></div>
</div></div></section>

<!-- LOGS -->
<section id="logs" class="section">
<div class="section-head"><div>
<h2 class="section-title" data-i18n="logs.title">Logs</h2>
<div class="section-meta" id="logsMeta">logs/logs.txt</div>
</div></div>
<div class="toolbar">
<label data-i18n="logs.lines">Lines<input id="logLines" type="number" min="20" max="1000" value="160"></label>
<button class="btn primary" id="refreshLogs" data-i18n="common.refresh">Refresh</button>
</div>
<pre class="log-box" id="logsBox"></pre>
</section>
</main>
</div>

<script>
/* ===== I18N ===== */
const L={
en:{
brand:{subtitle:"Telegram Username Tool"},
nav:{dashboard:"Dashboard",generation:"Generation",database:"Database",telegram:"Telegram",accounts:"Accounts",channels:"Channels",logs:"Logs"},
donation:{title:"Support Username Studio",hint:"A calm contribution to development"},
common:{refresh:"Refresh",save:"Save",show:"Show",delete:"Delete",loading:"loading",error:"error",status:"Status",search:"Search",phone:"Phone",code:"Code",login:"Login",sendCode:"Send Code","2fa":"2FA Password",ifEnabled:"if enabled",optional:"optional",yes:"y",updated:"Updated"},
dashboard:{title:"Dashboard",lastBatch:"Last Batch",last10:"last 10",availTop:"Available Top",scoreDesc:"score desc"},
gen:{title:"Generation",subtitle:"LM Studio + local evaluation, no Telegram actions",rotationAccount:"Active rotation account",required:"required",waiting:"waiting",checkingAccounts:"Checking account list...",batchSize:"Batch Size",minLength:"Min Length",maxLength:"Max Length",digits:"digits",generateBtn:"Generate & Evaluate",ready:"Ready to start",launching:"Launching..."},
db:{title:"Username Database",limitOn:"Output limit enabled",all:"All",searchPH:"username",shown:"Shown {n}",shownMore:"Shown {n}, more available"},
tg:{title:"Telegram Check",subtitle:"Checks only through accounts from the Accounts tab",mainAccount:"Main Account",channelCreation:"channel creation",liveCheck:"Live Check",sessionsOnly:"sessions/ only",mode:"Mode",checkForLive:"CHECK for live",mainCreation:"Main creation account",checking:"checking",checkingSession:"Checking session...",refreshStatus:"Refresh Status",apiMain:"Telegram API main account",apiHashPH:"leave empty if already saved",saveApi:"Save API",apiNote:"This account is only for channel creation, not for live checks.",loginMain:"Login to main account",phonePH:"+79990000000 or from .env",confirm2fa:"Confirm 2FA",resetLogin:"Reset Login",resetSession:"Reset Session",codeNote:"Code and password are not saved in the browser. Username check is not performed with this account.",manualUsername:"Manual username",checkLimit:"Check limit",liveConfirm:"Live confirm",confirmPH:"CHECK",preview:"Preview",previewSel:"Preview Selected",checkSelLive:"Check Selected Live",candidatesNotLoaded:"Candidates not loaded",noCandidates:"No candidates",noCandidatesHint:"Try lowering min score or specify a username manually.",noSkips:"No skips",noSkipsHint:"All candidates passed the preliminary filter.",enterCheck:"For live check, enter CHECK"},
acc:{title:"Accounts",subtitle:"Accounts for live-check rotation only",add:"+ Add",newAccount:"New Account",notStarted:"not started",apiNote:"API ID, API Hash and phone are saved locally in sessions after successful login.",loginConfirm:"Login Confirmation",tgCode:"Telegram Code"},
ch:{title:"Channel Creation",subtitle:"Creation via main account; checking is separate",channelName:"Channel Name",useUsername:"Use username? (y/n)",notSelected:"Username not selected",select:"Select",create:"Create"},
logs:{title:"Logs",lines:"Lines"},
stats:{totalEvaluated:"Total Evaluated",totalChecked:"Telegram Checked",totalAvailable:"Available",totalTaken:"Taken/Invalid",totalUsed:"Used",totalUnchecked:"Unchecked",avgScore:"Avg Score",bestScore:"Best Score",lastBatchNum:"Last Batch",lastBatchCount:"Batch Usernames",lastBatchChecked:"Batch Checked",lastBatchAvail:"Batch Available"},
th:{status:"status",phone:"phone",lastError:"last error"},
status:{available:"available",active:"active",cooldown:"cooldown",dead:"dead",unchecked:"unchecked",used:"used",invalid:"invalid",error:"error",warn:"warn",noUsername:"no username",authorized:"authorized",loginReq:"login required",notConfigured:"not configured",wrongAccount:"wrong account",configured:"configured",notReady:"not ready",sending:"sending",codeSent:"code sent",notStarted:"not started",checking:"checking"},
time:{m:"m",s:"s"},
msg:{noBatchData:"No batch data",noBatchDataHint:"A new batch will appear after generation.",noAvail:"No available usernames",noAvailHint:"After live check, available usernames will appear here.",nothingFound:"Nothing found",nothingFoundHint:"Change filters or run generation.",genNoResults:"No results",genNoResultsHint:"Generation completed without new usernames.",genError:"Generation error",noAcc:"No accounts for live check",noAccHint:"Add account here; main creation account does not participate in live-check.",accLoaded:"Accounts loaded: {n}",multiNotAdded:"Multi-accounts not added",addAccHint:"Add an account in the Accounts tab. The main .env account does not participate in live checks.",accLoadedHint:"Accounts loaded, active will appear after live check starts.",noChAvail:"No available usernames",noChAvailHint:"Channel creation only for verified available usernames.",readyPreview:"Ready to preview",created:"Channel created ID {n}",delConfirm:"Delete account and its local session?",resetConfirm:"Reset local Telegram session and login again?",sessionReset:"Session reset. Send code for new login.",codeSentPhone:"Code sent to {n}. Enter code on the right.",accAuth:"Account authorized and ready for rotation.",accAdded:"Account added.",sendFirst:"Send code first.",noActive:"No active login.",loginReset:"Login reset.",alreadyAuth:"Account already authorized",loginOk:"Login successful",enter2fa:"Enter 2FA password",savingApi:"Saving Telegram API...",sendingCode:"Sending code...",checkingCode:"Checking code...",checking2fa:"Checking 2FA...",resettingSession:"Resetting Telegram session...",mainSession:"Main creation account. Session: {n}",fillApi:"Fill in TELEGRAM_API_ID and TELEGRAM_API_HASH for channel creation",wrongDetail:"Current session @{u} does not match phone from .env",authDetail:"{name} · @{u} · id {id} · channel creation only",loginReqDetail:"Main creation account {n} is not authorized",hashChanged:"Main account API saved. If new account, reset session and login again.",noHashChange:"Main account API ID/phone saved. API HASH was not changed.",previewReady:"Preview ready",checkDone:"Check completed: {checked} checked, {available} available",candidates:"{source}: {count} candidates, {skipped} skipped",enterCodeFirst:"Enter code first.",notResetSession:"No active login.",resetAuth:"Login reset."}
},
fa:{
brand:{subtitle:"ابزار یوزرنیم تلگرام"},
nav:{dashboard:"داشبورد",generation:"تولید",database:"پایگاه داده",telegram:"تلگرام",accounts:"حساب\u200cها",channels:"کانال\u200cها",logs:"لاگ\u200cها"},
donation:{title:"پشتیبانی از Username Studio",hint:"کمک به توسعه پروژه"},
common:{refresh:"بروزرسانی",save:"ذخیره",show:"نمایش",delete:"حذف",loading:"بارگذاری",error:"خطا",status:"وضعیت",search:"جستجو",phone:"تلفن",code:"کد",login:"ورود",sendCode:"ارسال کد","2fa":"رمز 2FA",ifEnabled:"در صورت فعال بودن",optional:"اختیاری",yes:"بله",updated:"بروز شده"},
dashboard:{title:"داشبورد",lastBatch:"آخرین بچ",last10:"10 تای آخر",availTop:"برترین\u200cهای موجود",scoreDesc:"مرتب بر اساس امتیاز"},
gen:{title:"تولید",subtitle:"LM Studio + ارزیابی محلی، بدون عملیات تلگرام",rotationAccount:"حساب فعال چرخشی",required:"الزامی",waiting:"در انتظار",checkingAccounts:"بررسی لیست حساب\u200cها...",batchSize:"اندازه بچ",minLength:"حداقل طول",maxLength:"حداکثر طول",digits:"اعداد",generateBtn:"تولید و ارزیابی",ready:"آماده شروع",launching:"در حال اجرا..."},
db:{title:"پایگاه داده یوزرنیم",limitOn:"محدودیت نمایش فعال",all:"همه",searchPH:"یوزرنیم",shown:"نمایش {n}",shownMore:"نمایش {n}، بیشتر موجود است"},
tg:{title:"بررسی تلگرام",subtitle:"بررسی فقط از طریق حساب\u200cهای تب حساب\u200cها انجام می\u200cشود",mainAccount:"حساب اصلی",channelCreation:"ایجاد کانال",liveCheck:"بررسی زنده",sessionsOnly:"فقط sessions/",mode:"حالت",checkForLive:"CHECK برای بررسی زنده",mainCreation:"حساب اصلی ایجاد",checking:"در حال بررسی",checkingSession:"بررسی نشست...",refreshStatus:"بروزرسانی وضعیت",apiMain:"API تلگرام حساب اصلی",apiHashPH:"خالی بگذارید اگر قبلا ذخیره شده",saveApi:"ذخیره API",apiNote:"این حساب فقط برای ایجاد کانال است، نه بررسی زنده.",loginMain:"ورود به حساب اصلی",phonePH:"+79990000000 یا از .env",confirm2fa:"تایید 2FA",resetLogin:"بازنشانی ورود",resetSession:"بازنشانی نشست",codeNote:"کد و رمز در مرورگر ذخیره نمی\u200cشوند. بررسی یوزرنیم با این حساب انجام نمی\u200cشود.",manualUsername:"یوزرنیم دستی",checkLimit:"محدودیت بررسی",liveConfirm:"تایید زنده",confirmPH:"CHECK",preview:"پیش\u200cنمایش",previewSel:"پیش\u200cنمایش انتخاب\u200cشده",checkSelLive:"بررسی زنده انتخاب\u200cشده",candidatesNotLoaded:"نامزدها بارگذاری نشدند",noCandidates:"نامزدی وجود ندارد",noCandidatesHint:"حداقل امتیاز را کاهش دهید یا یوزرنیم وارد کنید.",noSkips:"بدون پرش",noSkipsHint:"همه نامزدها از فیلتر اولیه عبور کردند.",enterCheck:"برای بررسی زنده، CHECK وارد کنید"},
acc:{title:"حساب\u200cها",subtitle:"حساب\u200cها فقط برای چرخش بررسی زنده",add:"+ افزودن",newAccount:"حساب جدید",notStarted:"شروع نشده",apiNote:"API ID، API Hash و تلفن پس از ورود موفق در sessions ذخیره می\u200cشوند.",loginConfirm:"تایید ورود",tgCode:"کد تلگرام"},
ch:{title:"ایجاد کانال",subtitle:"ایجاد از طریق حساب اصلی؛ بررسی جداگانه",channelName:"نام کانال",useUsername:"از یوزرنیم استفاده شود؟ (y/n)",notSelected:"یوزرنیم انتخاب نشده",select:"انتخاب",create:"ایجاد"},
logs:{title:"لاگ\u200cها",lines:"تعداد خطوط"},
stats:{totalEvaluated:"کل ارزیابی\u200cشده",totalChecked:"بررسی\u200cشده تلگرام",totalAvailable:"موجود",totalTaken:"اشغال\u200cشده/نامعتبر",totalUsed:"استفاده\u200cشده",totalUnchecked:"بررسی\u200cنشده",avgScore:"میانگین امتیاز",bestScore:"بهترین امتیاز",lastBatchNum:"آخرین بچ",lastBatchCount:"یوزرنیم\u200cهای بچ",lastBatchChecked:"بچ بررسی\u200cشده",lastBatchAvail:"بچ موجود"},
th:{status:"وضعیت",phone:"تلفن",lastError:"آخرین خطا"},
status:{available:"موجود",active:"فعال",cooldown:"زمان انتظار",dead:"غیرفعال",unchecked:"بررسی\u200cنشده",used:"استفاده\u200cشده",invalid:"نامعتبر",error:"خطا",warn:"هشدار",noUsername:"بدون یوزرنیم",authorized:"مجاز",loginReq:"نیاز به ورود",notConfigured:"پیکربندی نشده",wrongAccount:"حساب اشتباه",configured:"پیکربندی شده",notReady:"آماده نیست",sending:"ارسال",codeSent:"کد ارسال شد",notStarted:"شروع نشده",checking:"در حال بررسی"},
time:{m:"د",s:"ث"},
msg:{noBatchData:"داده\u200cای موجود نیست",noBatchDataHint:"بچ جدید بعد از تولید ظاهر می\u200cشود.",noAvail:"یوزرنیم موجودی نیست",noAvailHint:"بعد از بررسی زنده، یوزرنیم\u200cهای موجود اینجا نمایش داده می\u200cشوند.",nothingFound:"چیزی پیدا نشد",nothingFoundHint:"فیلترها را تغییر دهید یا تولید انجام دهید.",genNoResults:"نتیجه\u200cای ندارد",genNoResultsHint:"تولید بدون یوزرنیم جدید تکمیل شد.",genError:"خطای تولید",noAcc:"حسابی برای بررسی زنده نیست",noAccHint:"حساب اضافه کنید؛ حساب اصلی ایجاد در بررسی زنده شرکت نمی\u200cکند.",accLoaded:"تعداد حساب\u200cها: {n}",multiNotAdded:"حساب\u200cهای چندگانه اضافه نشده",addAccHint:"در تب حساب\u200cها یک حساب اضافه کنید. حساب اصلی .env در بررسی زنده شرکت نمی\u200cکند.",accLoadedHint:"حساب\u200cها بارگذاری شد، حساب فعال بعد از شروع بررسی زنده نمایش داده می\u200cشود.",noChAvail:"یوزرنیم موجودی نیست",noChAvailHint:"ایجاد کانال فقط برای یوزرنیم\u200cهای موجود تایید شده.",readyPreview:"آماده پیش\u200cنمایش",created:"کانال ایجاد شد ID {n}",delConfirm:"حذف حساب و نشست محلی آن؟",resetConfirm:"بازنشانی نشست تلگرام و ورود مجدد؟",sessionReset:"نشست بازنشانی شد. کد جدید ارسال کنید.",codeSentPhone:"کد به {n} ارسال شد. کد را در سمت راست وارد کنید.",accAuth:"حساب مجاز و آماده چرخش.",accAdded:"حساب اضافه شد.",sendFirst:"ابتدا کد ارسال کنید.",noActive:"ورود فعالی نیست.",loginReset:"ورود بازنشانی شد.",alreadyAuth:"حساب قبلا مجاز است",loginOk:"ورود موفق",enter2fa:"رمز 2FA را وارد کنید",savingApi:"ذخیره API تلگرام...",sendingCode:"ارسال کد...",checkingCode:"بررسی کد...",checking2fa:"بررسی 2FA...",resettingSession:"بازنشانی نشست تلگرام...",mainSession:"حساب اصلی ایجاد. نشست: {n}",fillApi:"API ID و API HASH حساب اصلی را برای ایجاد کانال وارد کنید",wrongDetail:"نشست فعلی @{u} با تلفن .env مطابقت ندارد",authDetail:"{name} · @{u} · id {id} · فقط ایجاد کانال",loginReqDetail:"حساب اصلی ایجاد {n} مجاز نیست",hashChanged:"API حساب اصلی ذخیره شد. اگر حساب جدید است، نشست را بازنشانی و ورود مجدد کنید.",noHashChange:"API ID/تلفن حساب اصلی ذخیره شد. API HASH تغییر نکرد.",previewReady:"پیش\u200cنمایش آماده",checkDone:"بررسی تکمیل: {checked} بررسی\u200cشده، {available} موجود",candidates:"{source}: {count} نامزد، {skipped} پرش",enterCodeFirst:"ابتدا کد را وارد کنید.",notResetSession:"ورود فعالی نیست.",resetAuth:"ورود بازنشانی شد."}
},
ru:{
brand:{subtitle:"Инструмент Telegram username"},
nav:{dashboard:"Dashboard",generation:"Генерация",database:"База",telegram:"Telegram",accounts:"Аккаунты",channels:"Канал",logs:"Логи"},
donation:{title:"Поддержать Username Studio",hint:"спокойный вклад в развитие"},
common:{refresh:"Обновить",save:"Сохранить",show:"Показать",delete:"Удалить",loading:"загрузка",error:"ошибка",status:"Статус",search:"Поиск",phone:"Телефон",code:"Код",login:"Войти",sendCode:"Отправить код","2fa":"2FA пароль",ifEnabled:"если включен",optional:"необязательно",yes:"y",updated:"Обновлено"},
dashboard:{title:"Dashboard",lastBatch:"Последний batch",last10:"последние 10",availTop:"Available top",scoreDesc:"score desc"},
gen:{title:"Генерация",subtitle:"LM Studio + локальная оценка, без Telegram-действий",rotationAccount:"Активный аккаунт ротации",required:"required",waiting:"waiting",checkingAccounts:"Проверка списка аккаунтов...",batchSize:"Размер batch",minLength:"Мин. длина",maxLength:"Макс. длина",digits:"цифры",generateBtn:"Сгенерировать и оценить",ready:"Готово к запуску",launching:"Запуск..."},
db:{title:"База username",limitOn:"Лимит вывода включен",all:"Все",searchPH:"username",shown:"Показано {n}",shownMore:"Показано {n}, есть еще"},
tg:{title:"Telegram-проверка",subtitle:"Проверка идет только через аккаунты из вкладки Аккаунты",mainAccount:"Основной аккаунт",channelCreation:"создание каналов",liveCheck:"Live-проверка",sessionsOnly:"только sessions/",mode:"Режим",checkForLive:"CHECK для live",mainCreation:"Основной аккаунт создания",checking:"checking",checkingSession:"Проверка сессии...",refreshStatus:"Обновить статус",apiMain:"Telegram API основного аккаунта",apiHashPH:"оставьте пустым, если уже сохранен",saveApi:"Сохранить API",apiNote:"Этот аккаунт используется только для создания каналов, не для live-проверок.",loginMain:"Вход в основной аккаунт",phonePH:"+79990000000 или из .env",confirm2fa:"Подтвердить 2FA",resetLogin:"Сбросить вход",resetSession:"Сбросить сессию",codeNote:"Код и пароль не сохраняются в браузере. Проверка username этим аккаунтом не выполняется.",manualUsername:"Manual username",checkLimit:"Лимит проверки",liveConfirm:"Live confirm",confirmPH:"CHECK",preview:"Preview",previewSel:"Preview выбранных",checkSelLive:"Проверить выбранные live",candidatesNotLoaded:"Кандидаты не загружены",noCandidates:"Нет кандидатов",noCandidatesHint:"Попробуйте снизить min score или указать username вручную.",noSkips:"Нет пропусков",noSkipsHint:"Все кандидаты прошли предварительный фильтр.",enterCheck:"Для live-проверки введите CHECK"},
acc:{title:"Аккаунты",subtitle:"Аккаунты только для ротации live-проверок",add:"+ Добавить",newAccount:"Новый аккаунт",notStarted:"not started",apiNote:"API ID, API Hash и телефон сохраняются локально в sessions после успешного входа.",loginConfirm:"Подтверждение входа",tgCode:"Код Telegram"},
ch:{title:"Создание канала",subtitle:"Создание через основной аккаунт; проверка выполняется отдельно",channelName:"Название канала",useUsername:"Использовать username? (y/n)",notSelected:"Username не выбран",select:"Выбрать",create:"Создать"},
logs:{title:"Логи",lines:"Строк"},
stats:{totalEvaluated:"Всего оценено",totalChecked:"Проверено в Telegram",totalAvailable:"Доступных",totalTaken:"Занятых/невалидных",totalUsed:"Использованных",totalUnchecked:"Непроверенных",avgScore:"Средний score",bestScore:"Лучший score",lastBatchNum:"Последний batch",lastBatchCount:"Username в batch",lastBatchChecked:"Batch checked",lastBatchAvail:"Batch available"},
th:{status:"status",phone:"телефон",lastError:"last error"},
status:{available:"available",active:"active",cooldown:"cooldown",dead:"dead",unchecked:"unchecked",used:"used",invalid:"invalid",error:"error",warn:"warn",noUsername:"без username",authorized:"authorized",loginReq:"login required",notConfigured:"not configured",wrongAccount:"wrong account",configured:"configured",notReady:"not ready",sending:"sending",codeSent:"code sent",notStarted:"not started",checking:"checking"},
time:{m:"m",s:"s"},
msg:{noBatchData:"Нет данных batch",noBatchDataHint:"Новый batch появится после генерации.",noAvail:"Нет available username",noAvailHint:"После live-проверки доступные username появятся здесь.",nothingFound:"Ничего не найдено",nothingFoundHint:"Измените фильтры или выполните генерацию.",genNoResults:"Нет результатов",genNoResultsHint:"Генерация завершилась без новых username.",genError:"Ошибка генерации",noAcc:"Нет аккаунтов для live-проверки",noAccHint:"Добавьте аккаунт здесь; основной аккаунт создания в live-check не участвует.",accLoaded:"Загружено аккаунтов: {n}",multiNotAdded:"Мульти-аккаунты не добавлены",addAccHint:"Добавьте аккаунт во вкладке Аккаунты. Основной аккаунт из .env не участвует в live-проверках.",accLoadedHint:"Аккаунты загружены, активный появится после старта live-проверки.",noChAvail:"Нет available username",noChAvailHint:"Создание канала доступно только для проверенных available username.",readyPreview:"Готово к preview",created:"Создан канал ID {n}",delConfirm:"Удалить аккаунт и его локальную сессию?",resetConfirm:"Сбросить локальную Telegram-сессию и войти заново?",sessionReset:"Сессия сброшена. Отправьте код для нового входа.",codeSentPhone:"Код отправлен на {n}. Введите код справа.",accAuth:"Аккаунт авторизован и готов к ротации.",accAdded:"Аккаунт добавлен.",sendFirst:"Сначала отправьте код.",noActive:"Нет активного входа.",loginReset:"Вход сброшен.",alreadyAuth:"Аккаунт уже авторизован",loginOk:"Вход выполнен",enter2fa:"Введите 2FA-пароль",savingApi:"Сохранение Telegram API...",sendingCode:"Отправка кода...",checkingCode:"Проверка кода...",checking2fa:"Проверка 2FA...",resettingSession:"Сброс Telegram-сессии...",mainSession:"Основной аккаунт создания. Сессия: {n}",fillApi:"Заполните TELEGRAM_API_ID и TELEGRAM_API_HASH основного аккаунта для создания каналов",wrongDetail:"Текущая сессия @{u} не совпадает с телефоном из .env",authDetail:"{name} · @{u} · id {id} · только создание каналов",loginReqDetail:"Основной аккаунт создания {n} не авторизован",hashChanged:"API основного аккаунта сохранены. Если новый аккаунт, сбросьте сессию и войдите заново.",noHashChange:"API ID/телефон основного аккаунта сохранены. API HASH не менялся.",previewReady:"Preview готов",checkDone:"Проверка завершена: {checked} проверено, {available} доступны",candidates:"{source}: {count} candidates, {skipped} skipped",enterCodeFirst:"Сначала отправьте код.",notResetSession:"Нет активного входа.",resetAuth:"Вход сброшен."}
}
};

let curLang=localStorage.getItem('us_lang')||'en';
const LOCALE={en:'en-US',fa:'en-US',ru:'ru-RU'};

function t(k,p){
const ks=k.split('.');let v=L[curLang];
for(const x of ks)v=v?.[x];
if(v==null){v=L.en;for(const x of ks)v=v?.[x];}
if(v==null)return k;
if(p)for(const[a,b]of Object.entries(p))v=v.replace('{'+a+'}',b);
return v;
}

function applyI18n(){
document.documentElement.lang=curLang;
document.documentElement.dir=curLang==='fa'?'rtl':'ltr';
document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.dataset.i18n)});
document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{el.placeholder=t(el.dataset.i18nPlaceholder)});
document.querySelectorAll('.lang-btn').forEach(b=>{b.classList.toggle('is-active',b.dataset.lang===curLang)});
}

function setLang(l){curLang=l;localStorage.setItem('us_lang',l);applyI18n();loadDashboard().catch(()=>{});syncTelegramMode();}

/* ===== APP ===== */
const $=s=>document.querySelector(s);
const $$=s=>Array.from(document.querySelectorAll(s));
function makeClientId(){if(globalThis.crypto?.randomUUID)return globalThis.crypto.randomUUID();return `{Date.now()}-${Math.random().toString(16).slice(2)}`;}

const app={config:{},selectedChannel:null,telegramPreview:null,authFlowId:null,accountAuthFlowId:null,clientId:makeClientId(),serverToken:"__SERVER_RUN_TOKEN__",heartbeatTimer:null,closeSent:false};

async function api(path,options={}){const r=await fetch(path,{headers:{"Content-Type":"application/json"},...options});const d=await r.json();if(!r.ok){const e=new Error(d.error||r.statusText);e.data=d;throw e;}return d;}

function clientBody(){return JSON.stringify({client_id:app.clientId,server_token:app.serverToken});}
async function postClientEvent(a,keepalive=false){return fetch(`/api/client/${a}`,{method:"POST",headers:{"Content-Type":"application/json"},body:clientBody(),keepalive}).catch(()=>null);}
async function registerBrowserClient(){await postClientEvent("open");if(app.heartbeatTimer)clearInterval(app.heartbeatTimer);app.heartbeatTimer=setInterval(()=>{postClientEvent("ping",true);},3000);}
function notifyBrowserClosed(){if(app.closeSent)return;app.closeSent=true;if(app.heartbeatTimer)clearInterval(app.heartbeatTimer);const b=clientBody();if(navigator.sendBeacon){const bl=new Blob([b],{type:"application/json"});navigator.sendBeacon("/api/client/close",bl);return;}fetch("/api/client/close",{method:"POST",headers:{"Content-Type":"application/json"},body:b,keepalive:true}).catch(()=>{});}
window.addEventListener("pagehide",notifyBrowserClosed);
window.addEventListener("beforeunload",notifyBrowserClosed);

function fmtNumber(v){if(v===null||v===undefined||v==="")return"0";return Number(v).toLocaleString(LOCALE[curLang],{maximumFractionDigits:2});}
function fmtScore(v){if(v===null||v===undefined||v==="")return"-";return Number(v).toFixed(2);}
function badge(s){const v=s||"unchecked";return `<span class="badge ${esc(v)}">${esc(v)}</span>`;}
function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));}
function rowHtml(r,e=""){return `<tr>${e}<td class="mono">@${esc(r.username)}</td><td>${fmtScore(r.score)}</td><td>${badge(r.status)}</td><td>${esc(r.generation_type||"-")}</td><td>${esc(r.batch_num||"-")}</td></tr>`;}
function setProgress(id,v){$(id).style.width=`${Math.max(0,Math.min(100,Number(v)||0))}%`;}
function fmtCooldown(v){const s=Number(v||0);if(s<=0)return"-";const m=Math.floor(s/60),r=s%60;return m?`${m}${t('time.m')} ${r}${t('time.s')}`:`${r}${t('time.s')}`;}
function accUserText(a){const u=a?.user||{};const un=u.username?`@${u.username}`:t('status.noUsername');const nm=`${u.first_name||""} ${u.last_name||""}`.trim();return nm?`${nm} · ${un}`:un;}

function renderRotAcc(data){const active=data.active_account;const b=$("#rotationAccountBadge");b.className="badge";if(!data.has_accounts){b.classList.add("warn");b.textContent=t('gen.required');$("#rotationAccountDetails").textContent=t('msg.addAccHint');return;}if(!active){b.classList.add("warn");b.textContent=t('gen.waiting');$("#rotationAccountDetails").textContent=t('msg.accLoadedHint');return;}b.classList.add(active.status||"active");b.textContent=active.status||"active";const cd=active.cooldown_remaining?` · cooldown ${fmtCooldown(active.cooldown_remaining)}`:"";$("#rotationAccountDetails").textContent=`${active.phone||"-"} · ${accUserText(active)}${cd}`;}

function renderAccounts(data){const accs=data.accounts||[];$("#accountsMeta").textContent=accs.length?t('msg.accLoaded',{n:accs.length}):t('msg.multiNotAdded');renderRotAcc(data);$("#accountsRows").innerHTML=accs.length?accs.map(a=>`<tr><td class="mono">${esc(a.phone||"-")}</td><td>${badge(a.status||"active")}</td><td>${esc(fmtCooldown(a.cooldown_remaining))}</td><td>${esc(accUserText(a))}</td><td class="notes">${esc(a.last_error||"")}</td><td><button class="btn danger" data-del-acc="${esc(a.account_id)}">${t('common.delete')}</button></td></tr>`).join(""):`<tr><td colspan="6" class="empty"><div class="empty-state"><strong>${t('msg.noAcc')}</strong><span>${t('msg.noAccHint')}</span></div></td></tr>`;$$$$("[data-del-acc]").forEach(b=>b.addEventListener("click",()=>delAccount(b.dataset.delAcc)));}

async function loadAccounts(){const d=await api("/api/accounts");renderAccounts(d);return d;}

function resetAccAuthForm(clear=false){app.accountAuthFlowId=null;$("#accountCode").value="";$("#accountPassword").value="";$("#accountPasswordLabel").hidden=true;$("#accountConfirmPassword").hidden=true;if(clear){$("#accountApiId").value="";$("#accountApiHash").value="";$("#accountPhone").value="";}}
function setAccBadge(s){const b=$("#accountAuthBadge");b.className="badge";b.classList.add(s==="authorized"?"active":"warn");b.textContent=s;}

async function startAccAuth(){setAccBadge(t('status.sending'));$("#accountAuthMessage").textContent=t('msg.sendingCode');try{const d=await api("/api/accounts/auth",{method:"POST",body:JSON.stringify({action:"start",api_id:$("#accountApiId").value.trim(),api_hash:$("#accountApiHash").value.trim(),phone:$("#accountPhone").value.trim()})});const a=d.auth||{};if(a.authorized||a.already_authorized){resetAccAuthForm(true);setAccBadge(t('status.authorized'));$("#accountAuthMessage").textContent=t('msg.accAuth');}else{app.accountAuthFlowId=a.flow_id;setAccBadge(t('status.codeSent'));$("#accountAuthMessage").textContent=t('msg.codeSentPhone',{n:a.phone||"phone"});}renderAccounts(d);}catch(e){setAccBadge(t('status.error'));$("#accountAuthMessage").textContent=e.data?.message||e.data?.error||e.message;}}

async function confirmAccCode(){if(!app.accountAuthFlowId){$("#accountAuthMessage").textContent=t('msg.sendFirst');return;}setAccBadge(t('status.checking'));try{const d=await api("/api/accounts/auth",{method:"POST",body:JSON.stringify({action:"code",flow_id:app.accountAuthFlowId,code:$("#accountCode").value.trim()})});const a=d.auth||{};$("#accountCode").value="";if(a.password_required){$("#accountPasswordLabel").hidden=false;$("#accountConfirmPassword").hidden=false;setAccBadge("2FA");$("#accountAuthMessage").textContent=t('msg.enter2fa');return;}resetAccAuthForm(true);setAccBadge(t('status.authorized'));$("#accountAuthMessage").textContent=t('msg.accAdded');renderAccounts(d);}catch(e){setAccBadge(t('status.error'));$("#accountAuthMessage").textContent=e.data?.message||e.data?.error||e.message;}}

async function confirmAccPwd(){if(!app.accountAuthFlowId){$("#accountAuthMessage").textContent=t('msg.noActive');return;}setAccBadge(t('status.checking'));try{const d=await api("/api/accounts/auth",{method:"POST",body:JSON.stringify({action:"password",flow_id:app.accountAuthFlowId,password:$("#accountPassword").value})});resetAccAuthForm(true);setAccBadge(t('status.authorized'));$("#accountAuthMessage").textContent=t('msg.accAdded');renderAccounts(d);}catch(e){$("#accountPassword").value="";setAccBadge(t('status.error'));$("#accountAuthMessage").textContent=e.data?.message||e.data?.error||e.message;}}

async function cancelAccAuth(){if(app.accountAuthFlowId){await api("/api/accounts/auth",{method:"POST",body:JSON.stringify({action:"cancel",flow_id:app.accountAuthFlowId})}).catch(()=>{});}resetAccAuthForm(false);setAccBadge(t('status.notStarted'));$("#accountAuthMessage").textContent=t('msg.loginReset');}

async function delAccount(id){if(!confirm(t('msg.delConfirm')))return;try{const d=await api("/api/accounts/delete",{method:"POST",body:JSON.stringify({account_id:id})});renderAccounts(d);}catch(e){$("#accountsMeta").textContent=e.data?.message||e.data?.error||e.message;}}

async function loadConfig(){const d=await api("/api/config");app.config=d;$("#batchSize").value=d.batch_size;$("#generationMinLength").value=d.generation_min_length||d.username_min_length||5;$("#generationMaxLength").value=d.generation_max_length||d.username_max_length||6;$("#generationAllowDigits").checked=Boolean(d.generation_allow_digits);$("#tgMinScore").value=d.score_threshold;$("#tgLimit").max=d.max_telegram_checks;}

async function loadDashboard(){const d=await api("/api/stats");const s=d.stats||{};const items=[["total_evaluated","stats.totalEvaluated"],["total_checked","stats.totalChecked"],["total_available","stats.totalAvailable"],["total_taken_invalid","stats.totalTaken"],["total_used","stats.totalUsed"],["total_unchecked","stats.totalUnchecked"],["avg_score","stats.avgScore"],["best_score","stats.bestScore"],["last_batch_num","stats.lastBatchNum"],["last_batch_count","stats.lastBatchCount"],["last_batch_checked","stats.lastBatchChecked"],["last_batch_available","stats.lastBatchAvail"]];$("#statsGrid").innerHTML=items.map(([k,l])=>`<article class="card stat-card" data-stat="${k}"><div class="stat-label">${t(l)}</div><div class="stat-value">${fmtNumber(s[k])}</div></article>`).join("");$("#dashMeta").textContent=`${t('common.updated')}: ${new Date().toLocaleTimeString(LOCALE[curLang])}`;await loadMiniTables();}

async function loadMiniTables(){const last=await api("/api/usernames?last_batch=1&limit=10");$("#lastBatchRows").innerHTML=last.rows.length?last.rows.map(r=>rowHtml(r)).join(""):`<tr><td colspan="5" class="empty"><div class="empty-state"><strong>${t('msg.noBatchData')}</strong><span>${t('msg.noBatchDataHint')}</span></div></td></tr>`;const av=await api("/api/usernames?status=available&valid_only=1&limit=10");$("#availableTopRows").innerHTML=av.rows.length?av.rows.map(r=>`<tr><td class="mono">@${esc(r.username)}</td><td>${fmtScore(r.score)}</td><td>${esc(r.generation_type||"-")}</td></tr>`).join(""):`<tr><td colspan="3" class="empty"><div class="empty-state"><strong>${t('msg.noAvail')}</strong><span>${t('msg.noAvailHint')}</span></div></td></tr>`;}

async function loadDatabase(){const p=new URLSearchParams();p.set("status",$("#dbStatus").value);p.set("limit",$("#dbLimit").value||"50");if($("#dbSearch").value.trim())p.set("search",$("#dbSearch").value.trim());if($("#dbMinScore").value)p.set("min_score",$("#dbMinScore").value);if($("#dbLastBatch").checked)p.set("last_batch","1");const d=await api(`/api/usernames?${p.toString()}`);$("#databaseMeta").textContent=d.has_more?t('db.shownMore',{n:d.total_visible}):t('db.shown',{n:d.total_visible});$("#databaseRows").innerHTML=d.rows.length?d.rows.map(r=>`<tr><td class="mono">@${esc(r.username)}</td><td>${fmtScore(r.score)}</td><td>${badge(r.status)}</td><td>${esc(r.generation_type||"-")}</td><td>${esc(r.batch_num||"-")}</td><td>${esc(r.checked_at||"-")}</td><td class="notes">${esc(r.notes||"")}</td></tr>`).join(""):`<tr><td colspan="7" class="empty"><div class="empty-state"><strong>${t('msg.nothingFound')}</strong><span>${t('msg.nothingFoundHint')}</span></div></td></tr>`;}

async function startGeneration(){$("#generateBtn").disabled=true;$("#generationStatus").textContent=t('gen.launching');setProgress("#generationProgress",1);try{const d=await api("/api/generate",{method:"POST",body:JSON.stringify({batch_size:Number($("#batchSize").value||app.config.batch_size||100),min_length:Number($("#generationMinLength").value||5),max_length:Number($("#generationMaxLength").value||6),allow_digits:$("#generationAllowDigits").checked})});$("#generationTaskId").textContent=d.task.id;await pollTask(d.task.id,renderGenTask);}catch(e){$("#generationStatus").textContent=e.message;}finally{$("#generateBtn").disabled=false;await loadDashboard();}}

function renderGenTask(tk){$("#generationStatus").textContent=tk.message||tk.status;setProgress("#generationProgress",tk.progress||0);if(tk.status==="completed"&&tk.result){const rows=tk.result.rows||[];$("#generationRows").innerHTML=rows.length?rows.map(r=>rowHtml(r)).join(""):`<tr><td colspan="5" class="empty"><div class="empty-state"><strong>${t('msg.genNoResults')}</strong><span>${t('msg.genNoResultsHint')}</span></div></td></tr>`;}if(tk.status==="failed"){$("#generationRows").innerHTML=`<tr><td colspan="5" class="empty"><div class="empty-state"><strong>${t('msg.genError')}</strong><span>${esc(tk.error||"Error")}</span></div></td></tr>`;}}

async function loadTgAuthStatus(){const d=await api("/api/telegram/auth/status");renderTgAuth(d.auth||{});return d.auth||{};}
async function loadTgConfig(){const d=await api("/api/telegram/config");renderTgConfig(d.telegram_config||{});return d.telegram_config||{};}

function renderTgConfig(c){const b=$("#tgConfigBadge");b.className="badge";const ok=Boolean(c.api_id&&c.api_hash_set);b.classList.add(ok?"available":"warn");b.textContent=ok?t('status.configured'):t('status.notReady');$("#tgApiId").value=c.api_id||"";$("#tgConfigPhone").value=c.phone||"";$("#tgApiHash").value="";$("#tgApiHash").placeholder=t('tg.apiHashPH');if(!$("#tgPhone").value.trim()&&c.phone)$("#tgPhone").value=c.phone;$("#tgConfigMessage").textContent=ok?t('msg.mainSession',{n:c.session_name||"telegram_session"}):t('msg.fillApi');}

async function saveTgConfig(){$("#tgConfigMessage").textContent=t('msg.savingApi');try{const d=await api("/api/telegram/config",{method:"POST",body:JSON.stringify({api_id:$("#tgApiId").value.trim(),api_hash:$("#tgApiHash").value.trim(),phone:$("#tgConfigPhone").value.trim()})});const c=d.telegram_config||{};renderTgConfig(c);$("#tgPhone").value=c.phone||"";$("#tgConfigMessage").textContent=c.api_hash_changed?t('msg.hashChanged'):t('msg.noHashChange');await loadTgAuthStatus();}catch(e){$("#tgConfigMessage").textContent=e.data?.message||e.message;}}

function renderTgAuth(a){const b=$("#tgAuthBadge");b.className="badge";if(!a.configured){b.classList.add("invalid");b.textContent=t('status.notConfigured');$("#tgAuthDetails").textContent=a.error||t('msg.fillApi');return;}if(a.authorized&&a.session_matches_config===false){const u=a.user||{};b.classList.add("invalid");b.textContent=t('status.wrongAccount');const un=u.username?`@${u.username}`:t('status.noUsername');$("#tgAuthDetails").textContent=a.error||t('msg.wrongDetail',{u:un});}else if(a.authorized){const u=a.user||{};b.classList.add("available");b.textContent=t('status.authorized');const un=u.username?`@${u.username}`:t('status.noUsername');const nm=`${u.first_name||""} ${u.last_name||""}`.trim();$("#tgAuthDetails").textContent=t('msg.authDetail',{name:nm||un,u:un,id:u.id||"-"});}else{b.classList.add("warn");b.textContent=t('status.loginReq');$("#tgAuthDetails").textContent=a.error||t('msg.loginReqDetail',{n:a.session_name||"telegram_session"});}}

async function sendTgCode(){$("#tgAuthMessage").textContent=t('msg.sendingCode');try{const d=await api("/api/telegram/auth/start",{method:"POST",body:JSON.stringify({phone:$("#tgPhone").value.trim()})});const a=d.auth||{};if(a.already_authorized||a.authorized){renderTgAuth(a);$("#tgAuthMessage").textContent=t('msg.alreadyAuth');return;}app.authFlowId=a.flow_id;$("#tgAuthMessage").textContent=t('msg.codeSentPhone',{n:a.phone||"phone"});}catch(e){$("#tgAuthMessage").textContent=e.message;}}

async function confirmTgCode(){if(!app.authFlowId){$("#tgAuthMessage").textContent=t('msg.sendFirst');return;}$("#tgAuthMessage").textContent=t('msg.checkingCode');try{const d=await api("/api/telegram/auth/confirm",{method:"POST",body:JSON.stringify({flow_id:app.authFlowId,code:$("#tgCode").value.trim()})});const a=d.auth||{};$("#tgCode").value="";if(a.password_required){$("#tgAuthMessage").textContent=t('msg.enter2fa');return;}app.authFlowId=null;renderTgAuth(a);$("#tgAuthMessage").textContent=t('msg.loginOk');}catch(e){$("#tgAuthMessage").textContent=e.message;}}

async function confirmTgPwd(){if(!app.authFlowId){$("#tgAuthMessage").textContent=t('msg.noActive');return;}$("#tgAuthMessage").textContent=t('msg.checking2fa');try{const d=await api("/api/telegram/auth/password",{method:"POST",body:JSON.stringify({flow_id:app.authFlowId,password:$("#tgPassword").value})});$("#tgPassword").value="";app.authFlowId=null;renderTgAuth(d.auth||{});$("#tgAuthMessage").textContent=t('msg.loginOk');}catch(e){$("#tgPassword").value="";$("#tgAuthMessage").textContent=e.message;}}

async function cancelTgAuth(){if(app.authFlowId){await api("/api/telegram/auth/cancel",{method:"POST",body:JSON.stringify({flow_id:app.authFlowId})}).catch(()=>{});}app.authFlowId=null;$("#tgCode").value="";$("#tgPassword").value="";$("#tgAuthMessage").textContent=t('msg.loginReset');await loadTgAuthStatus();}

async function resetTgSession(){if(!confirm(t('msg.resetConfirm')))return;$("#tgAuthMessage").textContent=t('msg.resettingSession');try{await api("/api/telegram/auth/reset-session",{method:"POST",body:JSON.stringify({})});app.authFlowId=null;$("#tgCode").value="";$("#tgPassword").value="";$("#tgAuthMessage").textContent=t('msg.sessionReset');await loadTgAuthStatus();}catch(e){$("#tgAuthMessage").textContent=e.message;}}

async function loadTgPreview(){const p=new URLSearchParams();p.set("limit",$("#tgLimit").value||"10");p.set("min_score",$("#tgMinScore").value||app.config.score_threshold||"6");const mu=$("#tgManualUsername").value.trim();if(mu)p.set("username",mu);const d=await api(`/api/telegram/preview?${p.toString()}`);app.telegramPreview=d;$("#telegramMeta").textContent=t('msg.candidates',{source:d.source,count:d.candidate_count,skipped:d.skipped_count});$("#telegramStatus").textContent=t('msg.previewReady');$("#telegramRows").innerHTML=d.candidates.length?d.candidates.map(r=>`<tr><td><input type="checkbox" class="tgPick" value="${esc(r.username)}" checked></td><td class="mono">@${esc(r.username)}</td><td>${fmtScore(r.score)}</td><td>${badge(r.status)}</td><td>${esc(r.generation_type||"-")}</td><td>${esc(r.batch_num||"-")}</td></tr>`).join(""):`<tr><td colspan="6" class="empty"><div class="empty-state"><strong>${t('tg.noCandidates')}</strong><span>${t('tg.noCandidatesHint')}</span></div></td></tr>`;$("#telegramSkippedRows").innerHTML=d.skipped.length?d.skipped.map(i=>`<tr><td class="mono">@${esc(i.username)}</td><td>${esc(i.reason)}</td></tr>`).join(""):`<tr><td colspan="2" class="empty"><div class="empty-state"><strong>${t('tg.noSkips')}</strong><span>${t('tg.noSkipsHint')}</span></div></td></tr>`;}

async function checkTgSelected(){const usernames=$$(".tgPick:checked").map(i=>i.value);const mu=("#tgManualUsername").value.trim().replace(/^@/,"").toLowerCase();if(mu&&!usernames.includes(mu))usernames.unshift(mu);$("#telegramStatus").textContent=t('common.loading');setProgress("#telegramProgress",1);const dry=$("#tgDryRun").checked;if(!dry&&$("#tgConfirm").value.trim()!=="CHECK"){$("#telegramStatus").textContent=t('tg.enterCheck');return;}try{const d=await api("/api/telegram/check",{method:"POST",body:JSON.stringify({usernames,limit:Number($("#tgLimit").value||10),min_score:Number($("#tgMinScore").value||app.config.score_threshold||6),dry_run:dry,confirm:$("#tgConfirm").value.trim()})});if(d.dry_run){$("#telegramStatus").textContent=d.message;app.telegramPreview=d.preview;return;}$("#telegramTaskId").textContent=d.task.id;const ft=await pollTask(d.task.id,renderTgTask);await loadDashboard();if(ft.status==="completed"&&ft.result){const ck=ft.result.checked_count||0,av=ft.result.available_count||0;$("#telegramStatus").textContent=t('msg.checkDone',{checked:ck,available:av});$("#telegramMeta").textContent=t('msg.checkDone',{checked:ck,available:av});}}catch(e){$("#telegramStatus").textContent=e.data?.message||e.message;}}

function syncTelegramMode(){const dry=$("#tgDryRun").checked;$("#tgCheckBtn").textContent=dry?t('tg.previewSel'):t('tg.checkSelLive');$("#telegramMeta").textContent=dry?t('tg.subtitle'):t('tg.enterCheck');$("#tgModeLabel").textContent=dry?"dry-run":"live check";$("#tgConfirmState").textContent=dry?t('status.notStarted'):"CHECK";$("#tgConfirm").disabled=dry;}

function renderTgTask(tk){$("#telegramStatus").textContent=tk.message||tk.status;setProgress("#telegramProgress",tk.progress||0);loadAccounts().catch(()=>{});if(tk.status==="completed"&&tk.result){$("#telegramRows").innerHTML=(tk.result.rows||[]).map(r=>`<tr><td></td><td class="mono">@${esc(r.username)}</td><td>${fmtScore(r.score)}</td><td>${badge(r.status)}</td><td>${esc(r.generation_type||"-")}</td><td>${esc(r.batch_num||"-")}</td></tr>`).join("");}}

async function loadChannels(){const p=new URLSearchParams();p.set("limit",$("#channelLimit").value||"20");if($("#channelMinScore").value)p.set("min_score",$("#channelMinScore").value);const d=await api(`/api/channels/available?${p.toString()}`);$("#channelRows").innerHTML=d.rows.length?d.rows.map(r=>`<tr><td class="mono">@${esc(r.username)}</td><td>${fmtScore(r.score)}</td><td>${badge(r.status)}</td><td>${esc(r.generation_type||"-")}</td><td><button class="btn" data-ch="${esc(r.username)}" data-sc="${esc(r.score)}">${t('ch.select')}</button></td></tr>`).join(""):`<tr><td colspan="5" class="empty"><div class="empty-state"><strong>${t('msg.noChAvail')}</strong><span>${t('msg.noChAvailHint')}</span></div></td></tr>`;$$$$("[data-ch]").forEach(b=>b.addEventListener("click",()=>selectCh(b.dataset.ch,b.dataset.sc)));}

function selectCh(u,s){app.selectedChannel={username:u,score:s};$("#selectedChannelName").textContent=`@${u}`;$("#selectedChannelScore").textContent=`score: ${fmtScore(s)}`;$("#channelTitle").value=u;$("#channelConfirmLabel").firstChild.textContent=t('ch.useUsername');$("#channelStatus").textContent=t('msg.readyPreview');}

async function createChannel(){if(!app.selectedChannel){$("#channelStatus").textContent=t('ch.notSelected');return;}$("#channelStatus").textContent=t('common.loading');setProgress("#channelProgress",1);try{const d=await api("/api/channels/create",{method:"POST",body:JSON.stringify({username:app.selectedChannel.username,title:$("#channelTitle").value.trim(),dry_run:$("#channelDryRun").checked,confirm:$("#channelConfirm").value.trim()})});if(d.dry_run){$("#channelStatus").textContent=d.message;return;}$("#channelTaskId").textContent=d.task.id;await pollTask(d.task.id,renderChTask);await loadDashboard();await loadChannels();}catch(e){$("#channelStatus").textContent=e.data?.message||e.data?.reason||e.message;}}

function renderChTask(tk){$("#channelStatus").textContent=tk.message||tk.status;setProgress("#channelProgress",tk.progress||0);if(tk.status==="completed"&&tk.result)$("#channelStatus").textContent=t('msg.created',{n:tk.result.channel_id});}

async function pollTask(id,render){for(;;){const d=await api(`/api/tasks/${id}`);const tk=d.task;render(tk);if(tk.status!=="running")return tk;await new Promise(r=>setTimeout(r,1200));}}

async function loadLogs(){const l=$("#logLines").value||"160";const d=await api(`/api/logs?lines=${encodeURIComponent(l)}`);$("#logsMeta").textContent=d.path;$("#logsBox").textContent=d.text||"";$("#logsBox").scrollTop=$("#logsBox").scrollHeight;}

function bindEvents(){
$$(".nav button").forEach(b=>{b.addEventListener("click",()=>{$$(".nav button").forEach(i=>i.classList.remove("is-active"));$$(".section").forEach(i=>i.classList.remove("is-active"));b.classList.add("is-active");(`#${b.dataset.tab}`).classList.add("is-active");});});
$$$$(".lang-switch .lang-btn").forEach(b=>{b.addEventListener("click",()=>setLang(b.dataset.lang));});
$("#refreshDashboard").addEventListener("click",loadDashboard);
$("#loadDatabase").addEventListener("click",loadDatabase);
$("#dbSearch").addEventListener("keydown",e=>{if(e.key==="Enter")loadDatabase();});
$("#generateBtn").addEventListener("click",startGeneration);
$("#tgSaveConfig").addEventListener("click",saveTgConfig);
$("#tgAuthRefresh").addEventListener("click",loadTgAuthStatus);
$("#tgSendCode").addEventListener("click",sendTgCode);
$("#tgConfirmCode").addEventListener("click",confirmTgCode);
$("#tgConfirmPassword").addEventListener("click",confirmTgPwd);
$("#tgCancelAuth").addEventListener("click",cancelTgAuth);
$("#tgResetSession").addEventListener("click",resetTgSession);
$("#tgCode").addEventListener("keydown",e=>{if(e.key==="Enter")confirmTgCode();});
$("#tgPassword").addEventListener("keydown",e=>{if(e.key==="Enter")confirmTgPwd();});
$("#tgPreviewBtn").addEventListener("click",loadTgPreview);
$("#tgCheckBtn").addEventListener("click",checkTgSelected);
$("#tgDryRun").addEventListener("change",syncTelegramMode);
$("#accountAddBtn").addEventListener("click",()=>{resetAccAuthForm(true);setAccBadge(t('status.notStarted'));$("#accountAuthMessage").textContent=t('acc.apiNote');$("#accountApiId").focus();});
$("#accountSendCode").addEventListener("click",startAccAuth);
$("#accountConfirmCode").addEventListener("click",confirmAccCode);
$("#accountConfirmPassword").addEventListener("click",confirmAccPwd);
$("#accountCancelAuth").addEventListener("click",cancelAccAuth);
$("#accountCode").addEventListener("keydown",e=>{if(e.key==="Enter")confirmAccCode();});
$("#accountPassword").addEventListener("keydown",e=>{if(e.key==="Enter")confirmAccPwd();});
$("#loadChannels").addEventListener("click",loadChannels);
$("#createChannelBtn").addEventListener("click",createChannel);
$("#refreshLogs").addEventListener("click",loadLogs);
}

async function init(){await registerBrowserClient();bindEvents();applyI18n();syncTelegramMode();await loadConfig();await Promise.all([loadDashboard(),loadDatabase(),loadTgConfig(),loadTgAuthStatus(),loadAccounts(),loadTgPreview(),loadChannels(),loadLogs()]);}

init().catch(e=>{console.error(e);$("#dashMeta").textContent=e.message;});
</script>
</body>
</html>
"""
