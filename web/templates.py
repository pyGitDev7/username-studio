"""HTML template for the web dashboard."""
from __future__ import annotations


INDEX_HTML = r"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Telegram Username Dashboard</title>
  <style>
    :root {
      --bg: #f2f5f7;
      --panel: #ffffff;
      --panel-soft: #eef4f7;
      --text: #101720;
      --muted: #66758a;
      --line: #d6dee8;
      --line-strong: #c7d1df;
      --accent: #0d9488;
      --accent-strong: #0f766e;
      --accent-soft: #dff7f2;
      --blue: #2563eb;
      --green: #16814d;
      --red: #b42318;
      --amber: #a15c07;
      --violet: #6d28d9;
      --sidebar: #111820;
      --sidebar-soft: #1b2632;
      --sidebar-text: #eef4f7;
      --sidebar-muted: #aeb9c8;
      --shadow: 0 16px 40px rgba(16, 23, 32, 0.08);
      --shadow-soft: 0 8px 22px rgba(16, 23, 32, 0.06);
      --focus: 0 0 0 3px rgba(13, 148, 136, 0.18);
    }

    * { box-sizing: border-box; }
    [hidden] { display: none !important; }
    html { overflow-x: hidden; }
    body {
      margin: 0;
      min-height: 100vh;
      background: linear-gradient(180deg, #f7f9fb 0%, var(--bg) 54%, #edf3f4 100%);
      color: var(--text);
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
      font-variant-numeric: tabular-nums;
    }

    button, input, select, textarea {
      font: inherit;
      letter-spacing: 0;
    }

    .app {
      display: grid;
      grid-template-columns: 248px minmax(0, 1fr);
      min-height: 100vh;
    }

    .sidebar {
      position: sticky;
      top: 0;
      display: flex;
      flex-direction: column;
      height: 100vh;
      padding: 22px 14px;
      border-right: 1px solid rgba(255, 255, 255, 0.08);
      background: var(--sidebar);
      color: var(--sidebar-text);
    }

    .brand {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 18px;
      padding: 0 6px;
    }

    .brand h1 {
      margin: 0;
      color: var(--sidebar-text);
      font-size: 18px;
      line-height: 1.2;
      font-weight: 780;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid rgba(125, 211, 190, 0.34);
      background: rgba(13, 148, 136, 0.16);
      color: #b9f4e7;
      font-size: 12px;
      font-weight: 650;
      white-space: nowrap;
    }

    .nav {
      display: grid;
      gap: 5px;
    }

    .nav button {
      width: 100%;
      min-height: 40px;
      padding: 9px 10px;
      border: 0;
      border-radius: 8px;
      background: transparent;
      color: var(--sidebar-muted);
      text-align: left;
      cursor: pointer;
      font-size: 13px;
      font-weight: 650;
      transition: background 150ms ease, color 150ms ease, transform 150ms ease;
    }

    .nav button::before {
      content: "";
      display: inline-block;
      width: 7px;
      height: 7px;
      margin-right: 10px;
      border-radius: 999px;
      background: currentColor;
      opacity: 0.42;
      vertical-align: 1px;
    }

    .nav button:hover { background: var(--sidebar-soft); color: var(--sidebar-text); }
    .nav button.is-active {
      background: #ffffff;
      color: var(--text);
      box-shadow: 0 10px 26px rgba(0, 0, 0, 0.16);
    }
    .nav button.is-active::before { opacity: 1; color: var(--accent); }

    .donation-cta {
      position: relative;
      display: grid;
      grid-template-columns: 1fr;
      align-items: center;
      min-height: 76px;
      margin-top: auto;
      padding: 13px 14px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.24);
      border-radius: 8px;
      background:
        linear-gradient(135deg, rgba(255, 255, 255, 0.23), rgba(255, 255, 255, 0.02) 38%),
        linear-gradient(135deg, #ff4d7d 0%, #ff8a3d 46%, #ffd166 100%);
      color: #190a12;
      text-decoration: none;
      box-shadow: 0 18px 34px rgba(255, 77, 125, 0.3);
      isolation: isolate;
      transform: translateZ(0);
      transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
    }

    .donation-cta::before {
      content: "";
      position: absolute;
      inset: -2px;
      z-index: 0;
      background: linear-gradient(115deg, transparent 0%, rgba(255, 255, 255, 0.72) 42%, transparent 58%);
      transform: translateX(-135%) skewX(-18deg);
      animation: donationShine 3.2s ease-in-out infinite;
      pointer-events: none;
    }

    .donation-cta::after {
      content: "";
      position: absolute;
      inset: 5px;
      border: 1px solid rgba(255, 255, 255, 0.42);
      border-radius: 6px;
      pointer-events: none;
    }

    .donation-cta:hover {
      filter: saturate(1.06);
      transform: translateY(-2px);
      box-shadow: 0 22px 42px rgba(255, 77, 125, 0.42);
    }

    .donation-cta:focus-visible {
      outline: 0;
      box-shadow: var(--focus), 0 22px 42px rgba(255, 77, 125, 0.42);
    }

    .donation-cta__copy {
      position: relative;
      z-index: 1;
      display: grid;
      gap: 2px;
      min-width: 0;
    }

    .donation-cta__label {
      color: rgba(25, 10, 18, 0.78);
      font-size: 10px;
      font-weight: 850;
      letter-spacing: 0.08em;
      line-height: 1;
      text-transform: uppercase;
    }

    .donation-cta__title {
      color: #190a12;
      font-size: 14px;
      font-weight: 880;
      line-height: 1.18;
    }

    .donation-cta__hint {
      color: rgba(25, 10, 18, 0.74);
      font-size: 11px;
      font-weight: 700;
      line-height: 1.2;
    }

    @keyframes donationShine {
      0%, 58% { transform: translateX(-135%) skewX(-18deg); }
      78%, 100% { transform: translateX(135%) skewX(-18deg); }
    }

    @media (prefers-reduced-motion: reduce) {
      .donation-cta::before { animation: none; }
      .donation-cta,
      .donation-cta:hover {
        transition: none;
        transform: none;
      }
    }

    main {
      min-width: 0;
      padding: 30px;
    }

    .section {
      display: none;
      width: 100%;
      max-width: 1260px;
      margin: 0;
    }
    .section.is-active { display: block; }

    .section-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 20px;
    }

    .section-title {
      margin: 0;
      font-size: 26px;
      line-height: 1.2;
      font-weight: 760;
    }

    .section-meta {
      margin-top: 5px;
      color: var(--muted);
      font-size: 13px;
      max-width: 820px;
    }

    .grid {
      display: grid;
      gap: 14px;
    }

    .stats-grid {
      grid-template-columns: repeat(auto-fit, minmax(188px, 1fr));
      margin-bottom: 22px;
    }

    .card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow-soft);
    }

    .stat-card {
      position: relative;
      min-height: 96px;
      overflow: hidden;
      padding: 15px 16px 14px 18px;
      background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%);
      box-shadow: var(--shadow-soft);
    }

    .stat-card::before {
      content: "";
      position: absolute;
      inset: 0 auto 0 0;
      width: 4px;
      background: var(--stat-accent, var(--accent));
    }

    .stat-card[data-stat="total_checked"],
    .stat-card[data-stat="last_batch_checked"] { --stat-accent: var(--blue); }
    .stat-card[data-stat="total_available"],
    .stat-card[data-stat="last_batch_available"] { --stat-accent: var(--green); }
    .stat-card[data-stat="total_taken_invalid"] { --stat-accent: var(--red); }
    .stat-card[data-stat="total_unchecked"] { --stat-accent: var(--amber); }
    .stat-card[data-stat="total_used"] { --stat-accent: var(--violet); }

    .stat-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 720;
      line-height: 1.25;
      text-transform: uppercase;
    }

    .stat-value {
      margin-top: 9px;
      font-size: 27px;
      line-height: 1;
      font-weight: 780;
      white-space: nowrap;
    }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      align-items: end;
      gap: 12px;
      margin-bottom: 16px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow-soft);
    }

    label {
      display: grid;
      gap: 5px;
      min-width: 130px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }

    input, select {
      min-height: 38px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #ffffff;
      color: var(--text);
      box-shadow: inset 0 1px 0 rgba(16, 23, 32, 0.03);
      transition: border-color 150ms ease, box-shadow 150ms ease;
    }

    input:hover, select:hover { border-color: var(--line-strong); }
    input:focus, select:focus, button:focus-visible {
      outline: 0;
      border-color: var(--accent);
      box-shadow: var(--focus);
    }

    input[type="checkbox"] {
      min-height: auto;
      width: 16px;
      height: 16px;
      padding: 0;
    }

    .check-label {
      display: inline-flex;
      grid-template-columns: none;
      align-items: center;
      min-width: auto;
      min-height: 38px;
      gap: 8px;
      color: var(--text);
      font-size: 13px;
    }

    .btn {
      min-height: 38px;
      padding: 8px 13px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #fff;
      color: var(--text);
      cursor: pointer;
      font-weight: 720;
      white-space: nowrap;
      box-shadow: 0 1px 0 rgba(16, 23, 32, 0.05);
      transition: background 150ms ease, border-color 150ms ease, box-shadow 150ms ease, transform 150ms ease;
    }

    .btn:hover { border-color: var(--line-strong); box-shadow: var(--shadow-soft); transform: translateY(-1px); }
    .btn.primary { border-color: var(--accent); background: var(--accent); color: #fff; }
    .btn.primary:hover { background: var(--accent-strong); }
    .btn.danger { border-color: #f5b5af; background: #fff7f5; color: var(--red); }
    .btn:disabled { opacity: 0.55; cursor: not-allowed; }

    .panel {
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow-soft);
    }

    .split {
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.75fr);
      gap: 16px;
      align-items: start;
    }

    .table-wrap {
      width: 100%;
      max-width: 100%;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow-soft);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 780px;
      font-size: 13px;
    }

    th, td {
      padding: 11px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: middle;
      white-space: nowrap;
    }

    th {
      background: #f5f8fb;
      color: var(--muted);
      font-size: 12px;
      font-weight: 760;
      position: sticky;
      top: 0;
      z-index: 1;
    }

    tbody tr:hover { background: #f8fbfb; }
    tr:last-child td { border-bottom: 0; }
    td.notes {
      max-width: 320px;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .mono {
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 8px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #f8fafc;
      color: var(--muted);
      font-size: 12px;
      font-weight: 720;
      white-space: nowrap;
    }

    .badge.available { border-color: #bbf7d0; background: #ecfdf3; color: var(--green); }
    .badge.active { border-color: #bbf7d0; background: #ecfdf3; color: var(--green); }
    .badge.cooldown { border-color: #fed7aa; background: #fff7ed; color: var(--amber); }
    .badge.dead { border-color: #fecaca; background: #fef2f2; color: var(--red); }
    .badge.unchecked { border-color: #bfdbfe; background: #eff6ff; color: var(--blue); }
    .badge.used { border-color: #ddd6fe; background: #f5f3ff; color: var(--violet); }
    .badge.invalid, .badge.checked_taken, .badge.error { border-color: #fecaca; background: #fef2f2; color: var(--red); }
    .badge.warn { border-color: #fed7aa; background: #fff7ed; color: var(--amber); }

    .progress {
      height: 9px;
      overflow: hidden;
      border-radius: 999px;
      background: #e6edf2;
    }

    .progress > div {
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, var(--accent) 0%, #22c55e 100%);
      transition: width 180ms ease;
    }

    .status-line {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 10px 0;
      color: var(--muted);
      font-size: 13px;
    }

    .empty {
      padding: 18px;
      color: var(--muted);
      text-align: center;
    }

    .log-box {
      min-height: 420px;
      max-height: 70vh;
      margin: 0;
      overflow: auto;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #111820;
      color: #e5e7eb;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 12px;
      box-shadow: var(--shadow-soft);
    }

    .selected-box {
      display: grid;
      gap: 10px;
    }

    .selected-name {
      font-size: 20px;
      font-weight: 760;
    }

    .auth-panel {
      display: grid;
      grid-template-columns: minmax(220px, 0.85fr) minmax(280px, 1.2fr) minmax(320px, 1.4fr);
      gap: 12px;
      align-items: start;
      margin-bottom: 14px;
    }

    .auth-summary {
      display: grid;
      gap: 8px;
      align-content: start;
    }

    .auth-actions {
      display: grid;
      grid-template-columns: repeat(2, minmax(150px, 1fr));
      gap: 10px;
      align-items: end;
    }

    .auth-panel input,
    .auth-panel select {
      width: 100%;
      min-width: 0;
    }

    .auth-panel .btn {
      min-width: 0;
      white-space: normal;
      line-height: 1.2;
    }

    .config-actions {
      grid-template-columns: repeat(2, minmax(150px, 1fr));
      margin-top: 10px;
    }

    .accounts-auth {
      grid-template-columns: minmax(360px, 1fr) minmax(360px, 1fr);
    }

    .accounts-auth .auth-actions {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    @media (max-width: 1040px) {
      .split { grid-template-columns: 1fr; }
      .auth-panel { grid-template-columns: 1fr; }
      .auth-actions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .config-actions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 760px) {
      .app { grid-template-columns: 1fr; }
      .sidebar {
        position: static;
        height: auto;
        border-right: 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      }
      .nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .donation-cta {
        grid-column: 1 / -1;
        margin-top: 14px;
      }
      main { padding: 16px; }
      .section-head { display: block; }
      .stats-grid { grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
      label { min-width: 100%; }
      .btn { width: 100%; }
      .auth-actions { grid-template-columns: 1fr; }
    }

    @media (max-width: 520px) {
      .stats-grid { grid-template-columns: 1fr; }
      .section-title { font-size: 24px; }
    }

    /* SaaS polish pass: shared tokens and component refinements. */
    :root {
      --background: #f5f7fa;
      --surface: #ffffff;
      --surface-raised: #ffffff;
      --surface-subtle: #f8fafc;
      --surface-muted: #eef2f6;
      --text: #17202e;
      --text-strong: #0f1724;
      --muted: #667085;
      --muted-strong: #475467;
      --border: #d8e0ea;
      --border-strong: #c4cedb;
      --accent: #0f766e;
      --accent-strong: #0b5f59;
      --accent-soft: #e7f6f3;
      --accent-line: #8fd6c8;
      --success: #16784c;
      --success-soft: #ecfdf3;
      --warn: #a05a08;
      --warn-soft: #fff7ed;
      --danger: #b42318;
      --danger-soft: #fff1f0;
      --info: #2563eb;
      --info-soft: #eff6ff;
      --purple: #6d28d9;
      --purple-soft: #f4f0ff;
      --sidebar: #0e1621;
      --sidebar-soft: #151f2b;
      --sidebar-raised: #1b2634;
      --sidebar-text: #f5f8fb;
      --sidebar-muted: #a7b4c5;
      --shadow: 0 18px 44px rgba(16, 24, 40, 0.08);
      --shadow-soft: 0 8px 20px rgba(16, 24, 40, 0.06);
      --focus: 0 0 0 3px rgba(15, 118, 110, 0.18);
      --radius-sm: 6px;
      --radius: 8px;
      --radius-lg: 10px;
      --space-1: 4px;
      --space-2: 8px;
      --space-3: 12px;
      --space-4: 16px;
      --space-5: 20px;
      --space-6: 24px;
      --bg: var(--background);
      --panel: var(--surface);
      --panel-soft: var(--surface-subtle);
      --line: var(--border);
      --line-strong: var(--border-strong);
      --blue: var(--info);
      --green: var(--success);
      --red: var(--danger);
      --amber: var(--warn);
      --violet: var(--purple);
    }

    body {
      background: var(--background);
      color: var(--text);
      -webkit-font-smoothing: antialiased;
      text-rendering: optimizeLegibility;
    }

    a:focus-visible,
    button:focus-visible,
    input:focus-visible,
    select:focus-visible {
      outline: 0;
      box-shadow: var(--focus);
    }

    .app {
      grid-template-columns: 264px minmax(0, 1fr);
      background: var(--background);
    }

    .sidebar {
      padding: 20px 14px 16px;
      border-right: 1px solid rgba(255, 255, 255, 0.08);
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.035), rgba(255, 255, 255, 0) 34%),
        var(--sidebar);
    }

    .brand {
      justify-content: flex-start;
      margin-bottom: 18px;
      padding: 4px 6px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .brand-mark {
      display: grid;
      place-items: center;
      flex: 0 0 36px;
      width: 36px;
      height: 36px;
      border: 1px solid rgba(143, 214, 200, 0.34);
      border-radius: var(--radius);
      background: rgba(15, 118, 110, 0.18);
      color: #d9fff7;
      font-size: 12px;
      font-weight: 820;
    }

    .brand-copy {
      display: grid;
      gap: 2px;
      min-width: 0;
    }

    .brand h1 {
      color: var(--sidebar-text);
      font-size: 17px;
      font-weight: 760;
    }

    .brand-copy span {
      color: var(--sidebar-muted);
      font-size: 12px;
      line-height: 1.25;
    }

    .brand .pill {
      margin-left: auto;
      border-color: rgba(143, 214, 200, 0.28);
      background: rgba(15, 118, 110, 0.16);
      color: #c8fff2;
      font-size: 11px;
      font-weight: 720;
    }

    .nav {
      gap: 4px;
    }

    .nav button {
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 38px;
      padding: 9px 10px;
      border: 1px solid transparent;
      border-radius: var(--radius);
      color: var(--sidebar-muted);
      font-size: 13px;
      font-weight: 680;
      transition: background 140ms ease, border-color 140ms ease, color 140ms ease, transform 140ms ease;
    }

    .nav button::before {
      content: attr(data-icon);
      display: grid;
      place-items: center;
      flex: 0 0 22px;
      width: 22px;
      height: 22px;
      margin: 0;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: var(--radius-sm);
      background: rgba(255, 255, 255, 0.05);
      color: currentColor;
      font-size: 11px;
      font-weight: 760;
      opacity: 1;
      vertical-align: 0;
    }

    .nav button:hover {
      background: rgba(255, 255, 255, 0.06);
      color: var(--sidebar-text);
      transform: translateX(1px);
    }

    .nav button.is-active {
      border-color: rgba(143, 214, 200, 0.22);
      background: rgba(255, 255, 255, 0.1);
      color: var(--sidebar-text);
      box-shadow: inset 3px 0 0 var(--accent-line);
    }

    .nav button.is-active::before {
      border-color: rgba(143, 214, 200, 0.38);
      background: rgba(15, 118, 110, 0.28);
      color: #d8fff6;
    }

    .donation-cta {
      min-height: 92px;
      margin: auto 2px 0;
      padding: 14px 14px 14px 54px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius);
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.035)),
        var(--sidebar-raised);
      color: var(--sidebar-text);
      box-shadow: none;
      transition: background 140ms ease, border-color 140ms ease, transform 140ms ease;
    }

    .donation-cta::before {
      display: none;
      animation: none;
    }

    .donation-cta::after {
      content: "DA";
      position: absolute;
      inset: 16px auto auto 14px;
      display: grid;
      place-items: center;
      width: 28px;
      height: 28px;
      border: 1px solid rgba(251, 191, 36, 0.38);
      border-radius: var(--radius-sm);
      background: rgba(251, 191, 36, 0.12);
      color: #ffe3a3;
      font-size: 11px;
      font-weight: 820;
    }

    .donation-cta:hover {
      border-color: rgba(251, 191, 36, 0.32);
      background:
        linear-gradient(180deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.045)),
        var(--sidebar-raised);
      box-shadow: none;
      filter: none;
      transform: translateY(-1px);
    }

    .donation-cta:focus-visible {
      box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.2);
    }

    .donation-cta__label {
      color: #f7c96d;
      font-size: 11px;
      font-weight: 760;
      letter-spacing: 0;
      text-transform: none;
    }

    .donation-cta__title {
      color: var(--sidebar-text);
      font-size: 14px;
      font-weight: 760;
    }

    .donation-cta__hint {
      color: var(--sidebar-muted);
      font-size: 12px;
      font-weight: 560;
    }

    main {
      padding: 28px 30px 40px;
    }

    .section {
      max-width: 1280px;
    }

    .section-head {
      align-items: center;
      margin-bottom: 18px;
    }

    .section-title {
      color: var(--text-strong);
      font-size: 25px;
      font-weight: 740;
    }

    .section-meta {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }

    .panel-heading {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: var(--space-3);
      margin: 0 0 10px;
    }

    .panel-title {
      margin: 0;
      color: var(--text-strong);
      font-size: 17px;
      line-height: 1.25;
      font-weight: 730;
    }

    .panel-caption {
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }

    .card,
    .panel,
    .toolbar,
    .table-wrap {
      border-color: var(--border);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: var(--shadow-soft);
    }

    .stats-grid {
      gap: 12px;
      grid-template-columns: repeat(auto-fit, minmax(182px, 1fr));
    }

    .stat-card {
      min-height: 104px;
      padding: 16px 16px 15px 18px;
      background: var(--surface-raised);
    }

    .stat-card::before {
      width: 3px;
      opacity: 0.92;
    }

    .stat-label {
      color: var(--muted-strong);
      font-size: 11px;
      font-weight: 720;
      line-height: 1.3;
    }

    .stat-value {
      color: var(--text-strong);
      font-size: 28px;
      font-weight: 760;
    }

    .toolbar {
      align-items: end;
      gap: 10px;
      padding: 12px;
    }

    label {
      color: var(--muted-strong);
      font-size: 12px;
      font-weight: 650;
    }

    input,
    select {
      width: 100%;
      min-height: 38px;
      border-color: var(--border);
      border-radius: var(--radius-sm);
      background: var(--surface);
      color: var(--text);
    }

    input::placeholder {
      color: #98a2b3;
    }

    input:hover,
    select:hover {
      border-color: var(--border-strong);
    }

    input:focus,
    select:focus {
      border-color: var(--accent);
      box-shadow: var(--focus);
    }

    .check-label {
      color: var(--text);
      font-weight: 650;
    }

    input[type="checkbox"] {
      width: 16px;
      min-width: 16px;
      accent-color: var(--accent);
    }

    .btn {
      min-height: 38px;
      border-color: var(--border);
      border-radius: var(--radius-sm);
      background: var(--surface);
      color: var(--text);
      font-size: 13px;
      font-weight: 700;
      box-shadow: 0 1px 1px rgba(16, 24, 40, 0.04);
    }

    .btn:hover {
      border-color: var(--border-strong);
      background: var(--surface-subtle);
      box-shadow: 0 6px 14px rgba(16, 24, 40, 0.06);
    }

    .btn.primary {
      border-color: var(--accent);
      background: var(--accent);
      color: #ffffff;
    }

    .btn.primary:hover {
      background: var(--accent-strong);
    }

    .btn.danger {
      border-color: #f2b6ae;
      background: var(--danger-soft);
      color: var(--danger);
    }

    .btn:disabled,
    .btn:disabled:hover {
      transform: none;
      box-shadow: none;
      opacity: 0.58;
    }

    .table-wrap .btn {
      min-height: 32px;
      padding: 6px 10px;
    }

    .split {
      grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.75fr);
      gap: 16px;
    }

    .table-wrap {
      overflow: auto;
    }

    table {
      min-width: 760px;
      color: var(--text);
      font-size: 13px;
    }

    th,
    td {
      padding: 11px 12px;
      border-bottom-color: var(--border);
    }

    th {
      background: var(--surface-subtle);
      color: var(--muted-strong);
      font-size: 11px;
      font-weight: 760;
      text-transform: uppercase;
    }

    tbody tr {
      transition: background 120ms ease;
    }

    tbody tr:hover {
      background: #f9fbfd;
    }

    .mono {
      color: var(--text-strong);
      font-size: 12.5px;
      font-weight: 650;
    }

    .badge {
      gap: 6px;
      min-height: 24px;
      padding: 2px 8px;
      border-color: var(--border);
      background: var(--surface-subtle);
      color: var(--muted-strong);
      font-size: 12px;
      font-weight: 700;
    }

    .badge::before {
      content: "";
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 999px;
      background: currentColor;
      opacity: 0.76;
    }

    .badge.available,
    .badge.active {
      border-color: #b7e7ca;
      background: var(--success-soft);
      color: var(--success);
    }

    .badge.cooldown,
    .badge.warn {
      border-color: #fed7aa;
      background: var(--warn-soft);
      color: var(--warn);
    }

    .badge.dead,
    .badge.invalid,
    .badge.checked_taken,
    .badge.error {
      border-color: #fecaca;
      background: var(--danger-soft);
      color: var(--danger);
    }

    .badge.unchecked {
      border-color: #bfd7ff;
      background: var(--info-soft);
      color: var(--info);
    }

    .badge.used {
      border-color: #ddd6fe;
      background: var(--purple-soft);
      color: var(--purple);
    }

    .status-line {
      color: var(--muted);
      line-height: 1.4;
    }

    .progress {
      height: 8px;
      background: var(--surface-muted);
    }

    .progress > div {
      background: linear-gradient(90deg, var(--accent), #16a34a);
    }

    .empty {
      color: var(--muted);
      text-align: center;
    }

    .empty-state {
      display: grid;
      gap: 4px;
      justify-items: center;
      padding: 6px 0;
      color: var(--muted);
      white-space: normal;
    }

    .empty-state strong {
      color: var(--text);
      font-size: 13px;
      font-weight: 730;
    }

    .empty-state span {
      max-width: 420px;
      font-size: 12px;
      line-height: 1.4;
    }

    .mode-strip {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }

    .mode-cell {
      display: grid;
      gap: 4px;
      min-height: 74px;
      padding: 13px 14px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: var(--surface);
      box-shadow: var(--shadow-soft);
    }

    .mode-cell span {
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }

    .mode-cell strong {
      color: var(--text-strong);
      font-size: 14px;
      font-weight: 740;
      line-height: 1.25;
    }

    .mode-cell.is-warn {
      border-color: #fed7aa;
      background: #fffbf5;
    }

    .auth-panel {
      gap: 14px;
    }

    .auth-summary .btn {
      width: max-content;
    }

    .log-box {
      border-color: #1f2937;
      background: #0d1420;
      color: #dbe4ef;
      font-size: 12.5px;
      line-height: 1.55;
      box-shadow: var(--shadow-soft);
    }

    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
      }
    }

    @media (max-width: 1040px) {
      .split {
        grid-template-columns: 1fr;
      }

      .mode-strip {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 760px) {
      .app {
        grid-template-columns: 1fr;
      }

      .sidebar {
        padding: 14px;
      }

      .brand {
        padding-bottom: 12px;
      }

      .nav {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .nav button {
        min-height: 40px;
      }

      .donation-cta {
        margin-top: 12px;
      }

      main {
        padding: 18px 14px 28px;
      }

      .section-head {
        display: grid;
        gap: 12px;
      }

      .section-head .btn {
        width: 100%;
      }

      .toolbar {
        display: grid;
        grid-template-columns: 1fr;
      }

      label,
      .btn {
        min-width: 0;
      }

      .mode-strip {
        grid-template-columns: 1fr;
      }

      .stats-grid {
        grid-template-columns: 1fr;
      }

      .auth-summary .btn {
        width: 100%;
      }

      table {
        min-width: 680px;
      }
    }

    @media (max-width: 430px) {
      .brand {
        align-items: flex-start;
      }

      .brand .pill {
        display: none;
      }

      .nav {
        grid-template-columns: 1fr;
      }

      .stats-grid {
        grid-template-columns: 1fr;
      }

      .nav {
        grid-template-columns: 1fr;
      }

      .section-title {
        font-size: 23px;
      }

      .stat-card {
        min-height: 92px;
      }

      .donation-cta {
        min-height: 84px;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">US</div>
        <div class="brand-copy">
          <h1>Username Studio</h1>
          <span>Telegram username tool</span>
        </div>
        <span class="pill">local</span>
      </div>
      <nav class="nav" aria-label="Навигация">
        <button class="is-active" data-tab="dashboard" data-icon="D">Dashboard</button>
        <button data-tab="generation" data-icon="G">Генерация</button>
        <button data-tab="database" data-icon="B">База</button>
        <button data-tab="telegram" data-icon="T">Telegram</button>
        <button data-tab="accounts" data-icon="A">Аккаунты</button>
        <button data-tab="channels" data-icon="C">Канал</button>
        <button data-tab="logs" data-icon="L">Логи</button>
      </nav>
      <a class="donation-cta" href="https://www.donationalerts.com/r/sattop02" target="_blank" rel="noopener noreferrer" aria-label="Поддержать проект через DonationAlerts">
        <span class="donation-cta__copy">
          <span class="donation-cta__label">DonationAlerts</span>
          <span class="donation-cta__title">Поддержать Username Studio</span>
          <span class="donation-cta__hint">спокойный вклад в развитие</span>
        </span>
      </a>
    </aside>

    <main>
      <section id="dashboard" class="section is-active">
        <div class="section-head">
          <div>
            <h2 class="section-title">Dashboard</h2>
            <div class="section-meta" id="dashMeta">-</div>
          </div>
          <button class="btn" id="refreshDashboard">Обновить</button>
        </div>
        <div class="grid stats-grid" id="statsGrid"></div>
        <div class="split">
          <div>
            <div class="panel-heading">
              <h3 class="panel-title">Последний batch</h3>
              <span class="panel-caption">последние 10</span>
            </div>
            <div class="table-wrap">
              <table>
                <thead><tr><th>username</th><th>score</th><th>status</th><th>type</th><th>batch</th></tr></thead>
                <tbody id="lastBatchRows"></tbody>
              </table>
            </div>
          </div>
          <div>
            <div class="panel-heading">
              <h3 class="panel-title">Available top</h3>
              <span class="panel-caption">score desc</span>
            </div>
            <div class="table-wrap">
              <table style="min-width:420px">
                <thead><tr><th>username</th><th>score</th><th>type</th></tr></thead>
                <tbody id="availableTopRows"></tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <section id="generation" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Генерация</h2>
            <div class="section-meta">LM Studio + локальная оценка, без Telegram-действий</div>
          </div>
        </div>
        <div class="panel" style="margin-bottom:14px">
          <div class="status-line" style="margin:0">
            <span>Активный аккаунт ротации</span>
            <span id="rotationAccountBadge" class="badge warn">loading</span>
          </div>
          <div id="rotationAccountDetails" class="section-meta" style="margin-top:8px">Проверка списка аккаунтов...</div>
        </div>
        <div class="toolbar">
          <label>Размер batch
            <input id="batchSize" type="number" min="1" max="500" value="100">
          </label>
          <label>Мин. длина
            <input id="generationMinLength" type="number" min="4" max="10" value="5">
          </label>
          <label>Макс. длина
            <input id="generationMaxLength" type="number" min="4" max="10" value="6">
          </label>
          <label class="check-label"><input id="generationAllowDigits" type="checkbox"> цифры</label>
          <button class="btn primary" id="generateBtn">Сгенерировать и оценить</button>
        </div>
        <div class="panel">
          <div class="status-line"><span id="generationStatus">Готово к запуску</span><span id="generationTaskId"></span></div>
          <div class="progress"><div id="generationProgress"></div></div>
        </div>
        <div class="table-wrap" style="margin-top:14px">
          <table>
            <thead><tr><th>username</th><th>score</th><th>status</th><th>generation_type</th><th>batch</th></tr></thead>
            <tbody id="generationRows"></tbody>
          </table>
        </div>
      </section>

      <section id="database" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">База username</h2>
            <div class="section-meta" id="databaseMeta">Лимит вывода включен</div>
          </div>
        </div>
        <div class="toolbar">
          <label>Статус
            <select id="dbStatus">
              <option value="all">Все</option>
              <option value="available">available</option>
              <option value="unchecked">unchecked</option>
              <option value="used">used</option>
              <option value="taken_invalid">checked_taken/invalid</option>
              <option value="checked">checked</option>
            </select>
          </label>
          <label>Поиск
            <input id="dbSearch" placeholder="username">
          </label>
          <label>Min score
            <input id="dbMinScore" type="number" step="0.1" min="0" max="10">
          </label>
          <label>Top N
            <input id="dbLimit" type="number" min="1" max="200" value="50">
          </label>
          <label class="check-label"><input id="dbLastBatch" type="checkbox"> last batch</label>
          <button class="btn primary" id="loadDatabase">Показать</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>username</th><th>score</th><th>status</th><th>generation_type</th><th>batch</th><th>checked_at</th><th>notes</th></tr></thead>
            <tbody id="databaseRows"></tbody>
          </table>
        </div>
      </section>

      <section id="telegram" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Telegram-проверка</h2>
            <div class="section-meta" id="telegramMeta">Проверка идет только через аккаунты из вкладки Аккаунты</div>
          </div>
        </div>
        <div class="mode-strip" aria-label="Telegram режимы">
          <div class="mode-cell">
            <span>Основной аккаунт</span>
            <strong>создание каналов</strong>
          </div>
          <div class="mode-cell">
            <span>Live-проверка</span>
            <strong>только sessions/</strong>
          </div>
          <div class="mode-cell">
            <span>Режим</span>
            <strong id="tgModeLabel">dry-run</strong>
          </div>
          <div class="mode-cell is-warn">
            <span>Confirm</span>
            <strong id="tgConfirmState">CHECK для live</strong>
          </div>
        </div>
        <div class="auth-panel">
          <div class="panel auth-summary">
            <div class="status-line" style="margin:0">
              <span>Основной аккаунт создания</span>
              <span id="tgAuthBadge" class="badge warn">checking</span>
            </div>
            <div id="tgAuthDetails" class="section-meta">Проверка сессии...</div>
            <button class="btn" id="tgAuthRefresh">Обновить статус</button>
          </div>
          <div class="panel">
            <div class="status-line" style="margin:0">
              <span>Telegram API основного аккаунта</span>
              <span id="tgConfigBadge" class="badge warn">loading</span>
            </div>
            <div class="auth-actions config-actions">
              <label>API ID
                <input id="tgApiId" inputmode="numeric" autocomplete="off" placeholder="1234567">
              </label>
              <label>API HASH
                <input id="tgApiHash" type="password" autocomplete="off" placeholder="оставьте пустым, если уже сохранен">
              </label>
              <label>Телефон
                <input id="tgConfigPhone" autocomplete="tel" placeholder="+79990000000">
              </label>
              <button class="btn primary" id="tgSaveConfig">Сохранить API</button>
            </div>
            <div class="section-meta" id="tgConfigMessage" style="margin-top:10px">Этот аккаунт используется только для создания каналов, не для live-проверок.</div>
          </div>
          <div class="panel">
            <div class="status-line" style="margin:0 0 10px">
              <span>Вход в основной аккаунт</span>
            </div>
            <div class="auth-actions">
              <label>Телефон
                <input id="tgPhone" placeholder="+79990000000 или из .env">
              </label>
              <button class="btn" id="tgSendCode">Отправить код</button>
              <label>Код
                <input id="tgCode" inputmode="numeric" autocomplete="one-time-code" placeholder="12345">
              </label>
              <button class="btn primary" id="tgConfirmCode">Войти</button>
              <label>2FA пароль
                <input id="tgPassword" type="password" autocomplete="current-password" placeholder="если включен">
              </label>
              <button class="btn" id="tgConfirmPassword">Подтвердить 2FA</button>
              <button class="btn" id="tgCancelAuth">Сбросить вход</button>
              <button class="btn danger" id="tgResetSession">Сбросить сессию</button>
            </div>
            <div class="section-meta" id="tgAuthMessage" style="margin-top:10px">Код и пароль не сохраняются в браузере. Проверка username этим аккаунтом не выполняется.</div>
          </div>
        </div>
        <div class="toolbar">
          <label>Manual username
            <input id="tgManualUsername" placeholder="@username">
          </label>
          <label>Лимит проверки
            <input id="tgLimit" type="number" min="1" max="30" value="10">
          </label>
          <label>Min score
            <input id="tgMinScore" type="number" step="0.1" min="0" max="10" value="6">
          </label>
          <label class="check-label"><input id="tgDryRun" type="checkbox" checked> dry-run</label>
          <label>Live confirm
            <input id="tgConfirm" placeholder="CHECK">
          </label>
          <button class="btn" id="tgPreviewBtn">Preview</button>
          <button class="btn primary" id="tgCheckBtn">Preview выбранных</button>
        </div>
        <div class="panel">
          <div class="status-line"><span id="telegramStatus">Кандидаты не загружены</span><span id="telegramTaskId"></span></div>
          <div class="progress"><div id="telegramProgress"></div></div>
        </div>
        <div class="split" style="margin-top:14px">
          <div class="table-wrap">
            <table>
              <thead><tr><th></th><th>username</th><th>score</th><th>status</th><th>type</th><th>batch</th></tr></thead>
              <tbody id="telegramRows"></tbody>
            </table>
          </div>
          <div class="table-wrap">
            <table style="min-width:420px">
              <thead><tr><th>skip</th><th>reason</th></tr></thead>
              <tbody id="telegramSkippedRows"></tbody>
            </table>
          </div>
        </div>
      </section>

      <section id="accounts" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Аккаунты</h2>
            <div class="section-meta" id="accountsMeta">Аккаунты только для ротации live-проверок</div>
          </div>
          <button class="btn primary" id="accountAddBtn">+ Добавить</button>
        </div>
        <div class="auth-panel accounts-auth" id="accountsAuthPanel">
          <div class="panel">
            <div class="status-line" style="margin:0">
              <span>Новый аккаунт</span>
              <span id="accountAuthBadge" class="badge warn">not started</span>
            </div>
            <div class="auth-actions config-actions">
              <label>API ID
                <input id="accountApiId" inputmode="numeric" autocomplete="off" placeholder="1234567">
              </label>
              <label>API HASH
                <input id="accountApiHash" type="password" autocomplete="off" placeholder="api_hash">
              </label>
              <label>Телефон
                <input id="accountPhone" autocomplete="tel" placeholder="+79990000000">
              </label>
              <button class="btn primary" id="accountSendCode">Отправить код</button>
            </div>
            <div class="section-meta" id="accountAuthMessage" style="margin-top:10px">API ID, API Hash и телефон сохраняются локально в sessions после успешного входа.</div>
          </div>
          <div class="panel">
            <div class="status-line" style="margin:0 0 10px">
              <span>Подтверждение входа</span>
            </div>
            <div class="auth-actions">
              <label>Код Telegram
                <input id="accountCode" inputmode="numeric" autocomplete="one-time-code" placeholder="12345">
              </label>
              <button class="btn primary" id="accountConfirmCode">Войти</button>
              <label id="accountPasswordLabel" hidden>2FA пароль
                <input id="accountPassword" type="password" autocomplete="current-password" placeholder="если включен">
              </label>
              <button class="btn" id="accountConfirmPassword" hidden>Подтвердить 2FA</button>
              <button class="btn" id="accountCancelAuth">Сбросить вход</button>
            </div>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>телефон</th><th>status</th><th>cooldown</th><th>user</th><th>last error</th><th></th></tr></thead>
            <tbody id="accountsRows"></tbody>
          </table>
        </div>
      </section>

      <section id="channels" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Создание канала</h2>
            <div class="section-meta">Создание через основной аккаунт; проверка выполняется отдельно</div>
          </div>
        </div>
        <div class="toolbar">
          <label>Min score
            <input id="channelMinScore" type="number" step="0.1" min="0" max="10">
          </label>
          <label>Top N
            <input id="channelLimit" type="number" min="1" max="100" value="20">
          </label>
          <button class="btn" id="loadChannels">Обновить</button>
        </div>
        <div class="split">
          <div class="table-wrap">
            <table>
              <thead><tr><th>username</th><th>score</th><th>status</th><th>type</th><th></th></tr></thead>
              <tbody id="channelRows"></tbody>
            </table>
          </div>
          <div class="panel selected-box">
            <div class="selected-name" id="selectedChannelName">-</div>
            <div class="section-meta" id="selectedChannelScore">score: -</div>
            <label>Название канала
              <input id="channelTitle" placeholder="optional">
            </label>
            <label class="check-label"><input id="channelDryRun" type="checkbox" checked> dry-run</label>
            <label id="channelConfirmLabel">Использовать username? (y/n)
              <input id="channelConfirm" placeholder="y">
            </label>
            <button class="btn primary" id="createChannelBtn">Создать</button>
            <div class="status-line"><span id="channelStatus">Username не выбран</span><span id="channelTaskId"></span></div>
            <div class="progress"><div id="channelProgress"></div></div>
          </div>
        </div>
      </section>

      <section id="logs" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Логи</h2>
            <div class="section-meta" id="logsMeta">logs/logs.txt</div>
          </div>
        </div>
        <div class="toolbar">
          <label>Строк
            <input id="logLines" type="number" min="20" max="1000" value="160">
          </label>
          <button class="btn primary" id="refreshLogs">Обновить</button>
        </div>
        <pre class="log-box" id="logsBox"></pre>
      </section>
    </main>
  </div>

  <script>
    const $ = (selector) => document.querySelector(selector);
    const $$ = (selector) => Array.from(document.querySelectorAll(selector));
    function makeClientId() {
      if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
      return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    }

    const app = {
      config: {},
      selectedChannel: null,
      telegramPreview: null,
      authFlowId: null,
      accountAuthFlowId: null,
      clientId: makeClientId(),
      serverToken: "__SERVER_RUN_TOKEN__",
      heartbeatTimer: null,
      closeSent: false
    };

    async function api(path, options = {}) {
      const response = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options
      });
      const data = await response.json();
      if (!response.ok) {
        const message = data.error || response.statusText;
        const error = new Error(message);
        error.data = data;
        throw error;
      }
      return data;
    }

    function clientBody() {
      return JSON.stringify({ client_id: app.clientId, server_token: app.serverToken });
    }

    async function postClientEvent(action, keepalive = false) {
      return fetch(`/api/client/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: clientBody(),
        keepalive
      }).catch(() => null);
    }

    async function registerBrowserClient() {
      await postClientEvent("open");
      if (app.heartbeatTimer) clearInterval(app.heartbeatTimer);
      app.heartbeatTimer = setInterval(() => {
        postClientEvent("ping", true);
      }, 3000);
    }

    function notifyBrowserClosed() {
      if (app.closeSent) return;
      app.closeSent = true;
      if (app.heartbeatTimer) clearInterval(app.heartbeatTimer);

      const body = clientBody();
      if (navigator.sendBeacon) {
        const blob = new Blob([body], { type: "application/json" });
        navigator.sendBeacon("/api/client/close", blob);
        return;
      }

      fetch("/api/client/close", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body,
        keepalive: true
      }).catch(() => {});
    }

    window.addEventListener("pagehide", notifyBrowserClosed);
    window.addEventListener("beforeunload", notifyBrowserClosed);

    function fmtNumber(value) {
      if (value === null || value === undefined || value === "") return "0";
      return Number(value).toLocaleString("ru-RU", { maximumFractionDigits: 2 });
    }

    function fmtScore(value) {
      if (value === null || value === undefined || value === "") return "-";
      return Number(value).toFixed(2);
    }

    function badge(status) {
      const value = status || "unchecked";
      return `<span class="badge ${escapeHtml(value)}">${escapeHtml(value)}</span>`;
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }[char]));
    }

    function rowHtml(row, extra = "") {
      return `<tr>${extra}<td class="mono">@${escapeHtml(row.username)}</td><td>${fmtScore(row.score)}</td><td>${badge(row.status)}</td><td>${escapeHtml(row.generation_type || "-")}</td><td>${escapeHtml(row.batch_num || "-")}</td></tr>`;
    }

    function setProgress(id, value) {
      $(id).style.width = `${Math.max(0, Math.min(100, Number(value) || 0))}%`;
    }

    function fmtCooldown(value) {
      const seconds = Number(value || 0);
      if (seconds <= 0) return "-";
      const minutes = Math.floor(seconds / 60);
      const rest = seconds % 60;
      return minutes ? `${minutes}m ${rest}s` : `${rest}s`;
    }

    function accountUserText(account) {
      const user = account?.user || {};
      const username = user.username ? `@${user.username}` : "без username";
      const name = `${user.first_name || ""} ${user.last_name || ""}`.trim();
      return name ? `${name} · ${username}` : username;
    }

    function renderRotationAccount(data) {
      const active = data.active_account;
      const badgeEl = $("#rotationAccountBadge");
      badgeEl.className = "badge";
      if (!data.has_accounts) {
        badgeEl.classList.add("warn");
        badgeEl.textContent = "required";
        $("#rotationAccountDetails").textContent = "Добавьте аккаунт во вкладке Аккаунты. Основной аккаунт из .env не участвует в live-проверках.";
        return;
      }
      if (!active) {
        badgeEl.classList.add("warn");
        badgeEl.textContent = "waiting";
        $("#rotationAccountDetails").textContent = "Аккаунты загружены, активный появится после старта live-проверки.";
        return;
      }
      badgeEl.classList.add(active.status || "active");
      badgeEl.textContent = active.status || "active";
      const cooldown = active.cooldown_remaining ? ` · cooldown ${fmtCooldown(active.cooldown_remaining)}` : "";
      $("#rotationAccountDetails").textContent = `${active.phone || "-"} · ${accountUserText(active)}${cooldown}`;
    }

    function renderAccounts(data) {
      const accounts = data.accounts || [];
      $("#accountsMeta").textContent = accounts.length
        ? `Загружено аккаунтов: ${accounts.length}`
        : "Мульти-аккаунты не добавлены";
      renderRotationAccount(data);
      $("#accountsRows").innerHTML = accounts.length ? accounts.map((account) => `
        <tr>
          <td class="mono">${escapeHtml(account.phone || "-")}</td>
          <td>${badge(account.status || "active")}</td>
          <td>${escapeHtml(fmtCooldown(account.cooldown_remaining))}</td>
          <td>${escapeHtml(accountUserText(account))}</td>
          <td class="notes">${escapeHtml(account.last_error || "")}</td>
          <td><button class="btn danger" data-delete-account="${escapeHtml(account.account_id)}">Удалить</button></td>
        </tr>
      `).join("") : `<tr><td colspan="6" class="empty"><div class="empty-state"><strong>Нет аккаунтов для live-проверки</strong><span>Добавьте аккаунт здесь; основной аккаунт создания в live-check не участвует.</span></div></td></tr>`;
      $$("[data-delete-account]").forEach((button) => button.addEventListener("click", () => deleteAccount(button.dataset.deleteAccount)));
    }

    async function loadAccounts() {
      const data = await api("/api/accounts");
      renderAccounts(data);
      return data;
    }

    function resetAccountAuthForm(clearCredentials = false) {
      app.accountAuthFlowId = null;
      $("#accountCode").value = "";
      $("#accountPassword").value = "";
      $("#accountPasswordLabel").hidden = true;
      $("#accountConfirmPassword").hidden = true;
      if (clearCredentials) {
        $("#accountApiId").value = "";
        $("#accountApiHash").value = "";
        $("#accountPhone").value = "";
      }
    }

    function setAccountAuthBadge(status) {
      const badgeEl = $("#accountAuthBadge");
      badgeEl.className = "badge";
      badgeEl.classList.add(status === "authorized" ? "active" : "warn");
      badgeEl.textContent = status;
    }

    async function startAccountAuth() {
      setAccountAuthBadge("sending");
      $("#accountAuthMessage").textContent = "Отправка кода Telegram...";
      try {
        const data = await api("/api/accounts/auth", {
          method: "POST",
          body: JSON.stringify({
            action: "start",
            api_id: $("#accountApiId").value.trim(),
            api_hash: $("#accountApiHash").value.trim(),
            phone: $("#accountPhone").value.trim()
          })
        });
        const auth = data.auth || {};
        if (auth.authorized || auth.already_authorized) {
          resetAccountAuthForm(true);
          setAccountAuthBadge("authorized");
          $("#accountAuthMessage").textContent = "Аккаунт авторизован и готов к ротации.";
        } else {
          app.accountAuthFlowId = auth.flow_id;
          setAccountAuthBadge("code sent");
          $("#accountAuthMessage").textContent = `Код отправлен на ${auth.phone || "телефон"}. Введите код справа.`;
        }
        renderAccounts(data);
      } catch (error) {
        setAccountAuthBadge("error");
        $("#accountAuthMessage").textContent = error.data?.message || error.data?.error || error.message;
      }
    }

    async function confirmAccountCode() {
      if (!app.accountAuthFlowId) {
        $("#accountAuthMessage").textContent = "Сначала отправьте код.";
        return;
      }
      setAccountAuthBadge("checking");
      try {
        const data = await api("/api/accounts/auth", {
          method: "POST",
          body: JSON.stringify({
            action: "code",
            flow_id: app.accountAuthFlowId,
            code: $("#accountCode").value.trim()
          })
        });
        const auth = data.auth || {};
        $("#accountCode").value = "";
        if (auth.password_required) {
          $("#accountPasswordLabel").hidden = false;
          $("#accountConfirmPassword").hidden = false;
          setAccountAuthBadge("2FA");
          $("#accountAuthMessage").textContent = auth.message || "Введите 2FA-пароль.";
          return;
        }
        resetAccountAuthForm(true);
        setAccountAuthBadge("authorized");
        $("#accountAuthMessage").textContent = "Аккаунт добавлен.";
        renderAccounts(data);
      } catch (error) {
        setAccountAuthBadge("error");
        $("#accountAuthMessage").textContent = error.data?.message || error.data?.error || error.message;
      }
    }

    async function confirmAccountPassword() {
      if (!app.accountAuthFlowId) {
        $("#accountAuthMessage").textContent = "Нет активного входа.";
        return;
      }
      setAccountAuthBadge("checking");
      try {
        const data = await api("/api/accounts/auth", {
          method: "POST",
          body: JSON.stringify({
            action: "password",
            flow_id: app.accountAuthFlowId,
            password: $("#accountPassword").value
          })
        });
        resetAccountAuthForm(true);
        setAccountAuthBadge("authorized");
        $("#accountAuthMessage").textContent = "Аккаунт добавлен.";
        renderAccounts(data);
      } catch (error) {
        $("#accountPassword").value = "";
        setAccountAuthBadge("error");
        $("#accountAuthMessage").textContent = error.data?.message || error.data?.error || error.message;
      }
    }

    async function cancelAccountAuth() {
      if (app.accountAuthFlowId) {
        await api("/api/accounts/auth", {
          method: "POST",
          body: JSON.stringify({ action: "cancel", flow_id: app.accountAuthFlowId })
        }).catch(() => {});
      }
      resetAccountAuthForm(false);
      setAccountAuthBadge("not started");
      $("#accountAuthMessage").textContent = "Вход сброшен.";
    }

    async function deleteAccount(accountId) {
      if (!confirm("Удалить аккаунт и его локальную сессию?")) return;
      try {
        const data = await api("/api/accounts/delete", {
          method: "POST",
          body: JSON.stringify({ account_id: accountId })
        });
        renderAccounts(data);
      } catch (error) {
        $("#accountsMeta").textContent = error.data?.message || error.data?.error || error.message;
      }
    }

    async function loadConfig() {
      const data = await api("/api/config");
      app.config = data;
      $("#batchSize").value = data.batch_size;
      $("#generationMinLength").value = data.generation_min_length || data.username_min_length || 5;
      $("#generationMaxLength").value = data.generation_max_length || data.username_max_length || 6;
      $("#generationAllowDigits").checked = Boolean(data.generation_allow_digits);
      $("#tgMinScore").value = data.score_threshold;
      $("#tgLimit").max = data.max_telegram_checks;
    }

    async function loadDashboard() {
      const data = await api("/api/stats");
      const stats = data.stats || {};
      const items = [
        ["total_evaluated", "Всего оценено"],
        ["total_checked", "Проверено в Telegram"],
        ["total_available", "Доступных"],
        ["total_taken_invalid", "Занятых/невалидных"],
        ["total_used", "Использованных"],
        ["total_unchecked", "Непроверенных"],
        ["avg_score", "Средний score"],
        ["best_score", "Лучший score"],
        ["last_batch_num", "Последний batch"],
        ["last_batch_count", "Username в batch"],
        ["last_batch_checked", "Batch checked"],
        ["last_batch_available", "Batch available"]
      ];
      $("#statsGrid").innerHTML = items.map(([key, label]) => `
        <article class="card stat-card" data-stat="${key}">
          <div class="stat-label">${label}</div>
          <div class="stat-value">${fmtNumber(stats[key])}</div>
        </article>
      `).join("");
      $("#dashMeta").textContent = `Обновлено: ${new Date().toLocaleTimeString("ru-RU")}`;
      await loadMiniTables();
    }

    async function loadMiniTables() {
      const last = await api("/api/usernames?last_batch=1&limit=10");
      $("#lastBatchRows").innerHTML = last.rows.length
        ? last.rows.map((row) => rowHtml(row)).join("")
        : `<tr><td colspan="5" class="empty"><div class="empty-state"><strong>Нет данных batch</strong><span>Новый batch появится после генерации.</span></div></td></tr>`;

      const available = await api("/api/usernames?status=available&valid_only=1&limit=10");
      $("#availableTopRows").innerHTML = available.rows.length
        ? available.rows.map((row) => `<tr><td class="mono">@${escapeHtml(row.username)}</td><td>${fmtScore(row.score)}</td><td>${escapeHtml(row.generation_type || "-")}</td></tr>`).join("")
        : `<tr><td colspan="3" class="empty"><div class="empty-state"><strong>Нет available username</strong><span>После live-проверки доступные username появятся здесь.</span></div></td></tr>`;
    }

    async function loadDatabase() {
      const params = new URLSearchParams();
      params.set("status", $("#dbStatus").value);
      params.set("limit", $("#dbLimit").value || "50");
      if ($("#dbSearch").value.trim()) params.set("search", $("#dbSearch").value.trim());
      if ($("#dbMinScore").value) params.set("min_score", $("#dbMinScore").value);
      if ($("#dbLastBatch").checked) params.set("last_batch", "1");
      const data = await api(`/api/usernames?${params.toString()}`);
      $("#databaseMeta").textContent = data.has_more ? `Показано ${data.total_visible}, есть еще` : `Показано ${data.total_visible}`;
      $("#databaseRows").innerHTML = data.rows.length ? data.rows.map((row) => `
        <tr>
          <td class="mono">@${escapeHtml(row.username)}</td>
          <td>${fmtScore(row.score)}</td>
          <td>${badge(row.status)}</td>
          <td>${escapeHtml(row.generation_type || "-")}</td>
          <td>${escapeHtml(row.batch_num || "-")}</td>
          <td>${escapeHtml(row.checked_at || "-")}</td>
          <td class="notes">${escapeHtml(row.notes || "")}</td>
        </tr>
      `).join("") : `<tr><td colspan="7" class="empty"><div class="empty-state"><strong>Ничего не найдено</strong><span>Измените фильтры или выполните генерацию.</span></div></td></tr>`;
    }

    async function startGeneration() {
      $("#generateBtn").disabled = true;
      $("#generationStatus").textContent = "Запуск...";
      setProgress("#generationProgress", 1);
      try {
        const data = await api("/api/generate", {
          method: "POST",
          body: JSON.stringify({
            batch_size: Number($("#batchSize").value || app.config.batch_size || 100),
            min_length: Number($("#generationMinLength").value || 5),
            max_length: Number($("#generationMaxLength").value || 6),
            allow_digits: $("#generationAllowDigits").checked
          })
        });
        $("#generationTaskId").textContent = data.task.id;
        await pollTask(data.task.id, renderGenerationTask);
      } catch (error) {
        $("#generationStatus").textContent = error.message;
      } finally {
        $("#generateBtn").disabled = false;
        await loadDashboard();
      }
    }

    function renderGenerationTask(task) {
      $("#generationStatus").textContent = task.message || task.status;
      setProgress("#generationProgress", task.progress || 0);
      if (task.status === "completed" && task.result) {
        const rows = task.result.rows || [];
        $("#generationRows").innerHTML = rows.length
          ? rows.map((row) => rowHtml(row)).join("")
          : `<tr><td colspan="5" class="empty"><div class="empty-state"><strong>Нет результатов</strong><span>Генерация завершилась без новых username.</span></div></td></tr>`;
      }
      if (task.status === "failed") {
        $("#generationRows").innerHTML = `<tr><td colspan="5" class="empty"><div class="empty-state"><strong>Ошибка генерации</strong><span>${escapeHtml(task.error || "Ошибка")}</span></div></td></tr>`;
      }
    }

    async function loadTelegramAuthStatus() {
      const data = await api("/api/telegram/auth/status");
      renderTelegramAuth(data.auth || {});
      return data.auth || {};
    }

    async function loadTelegramConfig() {
      const data = await api("/api/telegram/config");
      renderTelegramConfig(data.telegram_config || {});
      return data.telegram_config || {};
    }

    function renderTelegramConfig(configData) {
      const badge = $("#tgConfigBadge");
      badge.className = "badge";
      const configured = Boolean(configData.api_id && configData.api_hash_set);
      badge.classList.add(configured ? "available" : "warn");
      badge.textContent = configured ? "configured" : "not ready";
      $("#tgApiId").value = configData.api_id || "";
      $("#tgConfigPhone").value = configData.phone || "";
      $("#tgApiHash").value = "";
      $("#tgApiHash").placeholder = configData.api_hash_set
        ? "сохранен, оставьте пустым чтобы не менять"
        : "вставьте TELEGRAM_API_HASH";
      if (!$("#tgPhone").value.trim() && configData.phone) {
        $("#tgPhone").value = configData.phone;
      }
      $("#tgConfigMessage").textContent = configured
        ? `Основной аккаунт создания. Сессия: ${configData.session_name || "telegram_session"}`
        : "Заполните API ID и API HASH основного аккаунта для создания каналов.";
    }

    async function saveTelegramConfig() {
      $("#tgConfigMessage").textContent = "Сохранение Telegram API...";
      try {
        const data = await api("/api/telegram/config", {
          method: "POST",
          body: JSON.stringify({
            api_id: $("#tgApiId").value.trim(),
            api_hash: $("#tgApiHash").value.trim(),
            phone: $("#tgConfigPhone").value.trim()
          })
        });
        const cfg = data.telegram_config || {};
        renderTelegramConfig(cfg);
        $("#tgPhone").value = cfg.phone || "";
        $("#tgConfigMessage").textContent = cfg.api_hash_changed
          ? "API основного аккаунта сохранены. Если это новый аккаунт, сбросьте сессию и войдите заново."
          : "API ID/телефон основного аккаунта сохранены. API HASH не менялся.";
        await loadTelegramAuthStatus();
      } catch (error) {
        $("#tgConfigMessage").textContent = error.data?.message || error.message;
      }
    }

    function renderTelegramAuth(auth) {
      const badge = $("#tgAuthBadge");
      badge.className = "badge";
      if (!auth.configured) {
        badge.classList.add("invalid");
        badge.textContent = "not configured";
        $("#tgAuthDetails").textContent = auth.error || "Заполните TELEGRAM_API_ID и TELEGRAM_API_HASH основного аккаунта для создания каналов";
        return;
      }

      if (auth.authorized && auth.session_matches_config === false) {
        const user = auth.user || {};
        badge.classList.add("invalid");
        badge.textContent = "wrong account";
        const username = user.username ? `@${user.username}` : "без username";
        $("#tgAuthDetails").textContent = auth.error || `Текущая сессия ${username} не совпадает с телефоном из .env`;
      } else if (auth.authorized) {
        const user = auth.user || {};
        badge.classList.add("available");
        badge.textContent = "authorized";
        const username = user.username ? `@${user.username}` : "без username";
        const name = `${user.first_name || ""} ${user.last_name || ""}`.trim();
        $("#tgAuthDetails").textContent = `${name || username} · ${username} · id ${user.id || "-"} · только создание каналов`;
      } else {
        badge.classList.add("warn");
        badge.textContent = "login required";
        $("#tgAuthDetails").textContent = auth.error || `Основной аккаунт создания ${auth.session_name || "telegram_session"} не авторизован`;
      }
    }

    async function sendTelegramCode() {
      $("#tgAuthMessage").textContent = "Отправка кода...";
      try {
        const data = await api("/api/telegram/auth/start", {
          method: "POST",
          body: JSON.stringify({ phone: $("#tgPhone").value.trim() })
        });
        const auth = data.auth || {};
        if (auth.already_authorized || auth.authorized) {
          renderTelegramAuth(auth);
          $("#tgAuthMessage").textContent = "Аккаунт уже авторизован";
          return;
        }
        app.authFlowId = auth.flow_id;
        $("#tgAuthMessage").textContent = `Код отправлен на ${auth.phone || "телефон"}. Введите код и нажмите "Войти".`;
      } catch (error) {
        $("#tgAuthMessage").textContent = error.message;
      }
    }

    async function confirmTelegramCode() {
      if (!app.authFlowId) {
        $("#tgAuthMessage").textContent = "Сначала отправьте код";
        return;
      }
      $("#tgAuthMessage").textContent = "Проверка кода...";
      try {
        const data = await api("/api/telegram/auth/confirm", {
          method: "POST",
          body: JSON.stringify({ flow_id: app.authFlowId, code: $("#tgCode").value.trim() })
        });
        const auth = data.auth || {};
        $("#tgCode").value = "";
        if (auth.password_required) {
          $("#tgAuthMessage").textContent = auth.message || "Введите 2FA-пароль";
          return;
        }
        app.authFlowId = null;
        renderTelegramAuth(auth);
        $("#tgAuthMessage").textContent = "Вход выполнен";
      } catch (error) {
        $("#tgAuthMessage").textContent = error.message;
      }
    }

    async function confirmTelegramPassword() {
      if (!app.authFlowId) {
        $("#tgAuthMessage").textContent = "Нет активного входа";
        return;
      }
      $("#tgAuthMessage").textContent = "Проверка 2FA...";
      try {
        const data = await api("/api/telegram/auth/password", {
          method: "POST",
          body: JSON.stringify({ flow_id: app.authFlowId, password: $("#tgPassword").value })
        });
        $("#tgPassword").value = "";
        app.authFlowId = null;
        renderTelegramAuth(data.auth || {});
        $("#tgAuthMessage").textContent = "Вход выполнен";
      } catch (error) {
        $("#tgPassword").value = "";
        $("#tgAuthMessage").textContent = error.message;
      }
    }

    async function cancelTelegramAuth() {
      if (app.authFlowId) {
        await api("/api/telegram/auth/cancel", {
          method: "POST",
          body: JSON.stringify({ flow_id: app.authFlowId })
        }).catch(() => {});
      }
      app.authFlowId = null;
      $("#tgCode").value = "";
      $("#tgPassword").value = "";
      $("#tgAuthMessage").textContent = "Вход сброшен";
      await loadTelegramAuthStatus();
    }

    async function resetTelegramSession() {
      if (!confirm("Сбросить локальную Telegram-сессию и войти заново?")) return;
      $("#tgAuthMessage").textContent = "Сброс Telegram-сессии...";
      try {
        await api("/api/telegram/auth/reset-session", {
          method: "POST",
          body: JSON.stringify({})
        });
        app.authFlowId = null;
        $("#tgCode").value = "";
        $("#tgPassword").value = "";
        $("#tgAuthMessage").textContent = "Сессия сброшена. Отправьте код для нового входа.";
        await loadTelegramAuthStatus();
      } catch (error) {
        $("#tgAuthMessage").textContent = error.message;
      }
    }

    async function loadTelegramPreview() {
      const params = new URLSearchParams();
      params.set("limit", $("#tgLimit").value || "10");
      params.set("min_score", $("#tgMinScore").value || app.config.score_threshold || "6");
      const manualUsername = $("#tgManualUsername").value.trim();
      if (manualUsername) params.set("username", manualUsername);
      const data = await api(`/api/telegram/preview?${params.toString()}`);
      app.telegramPreview = data;
      $("#telegramMeta").textContent = `${data.source}: ${data.candidate_count} candidates, ${data.skipped_count} skipped`;
      $("#telegramStatus").textContent = "Preview готов";
      $("#telegramRows").innerHTML = data.candidates.length ? data.candidates.map((row) => `
        <tr>
          <td><input type="checkbox" class="tgPick" value="${escapeHtml(row.username)}" checked></td>
          <td class="mono">@${escapeHtml(row.username)}</td>
          <td>${fmtScore(row.score)}</td>
          <td>${badge(row.status)}</td>
          <td>${escapeHtml(row.generation_type || "-")}</td>
          <td>${escapeHtml(row.batch_num || "-")}</td>
        </tr>
      `).join("") : `<tr><td colspan="6" class="empty"><div class="empty-state"><strong>Нет кандидатов</strong><span>Попробуйте снизить min score или указать username вручную.</span></div></td></tr>`;
      $("#telegramSkippedRows").innerHTML = data.skipped.length ? data.skipped.map((item) => `
        <tr><td class="mono">@${escapeHtml(item.username)}</td><td>${escapeHtml(item.reason)}</td></tr>
      `).join("") : `<tr><td colspan="2" class="empty"><div class="empty-state"><strong>Нет пропусков</strong><span>Все кандидаты прошли предварительный фильтр.</span></div></td></tr>`;
    }

    async function checkTelegramSelected() {
      const usernames = $$(".tgPick:checked").map((input) => input.value);
      const manualUsername = $("#tgManualUsername").value.trim().replace(/^@/, "").toLowerCase();
      if (manualUsername && !usernames.includes(manualUsername)) usernames.unshift(manualUsername);
      $("#telegramStatus").textContent = "Подготовка...";
      setProgress("#telegramProgress", 1);
      const dryRun = $("#tgDryRun").checked;
      if (!dryRun && $("#tgConfirm").value.trim() !== "CHECK") {
        $("#telegramStatus").textContent = "Для live-проверки введите CHECK";
        return;
      }
      try {
        const data = await api("/api/telegram/check", {
          method: "POST",
          body: JSON.stringify({
            usernames,
            limit: Number($("#tgLimit").value || 10),
            min_score: Number($("#tgMinScore").value || app.config.score_threshold || 6),
            dry_run: dryRun,
            confirm: $("#tgConfirm").value.trim()
          })
        });
        if (data.dry_run) {
          $("#telegramStatus").textContent = data.message;
          app.telegramPreview = data.preview;
          return;
        }
        $("#telegramTaskId").textContent = data.task.id;
        const finishedTask = await pollTask(data.task.id, renderTelegramTask);
        await loadDashboard();
        if (finishedTask.status === "completed" && finishedTask.result) {
          const checked = finishedTask.result.checked_count || 0;
          const available = finishedTask.result.available_count || 0;
          $("#telegramStatus").textContent = `Проверка завершена: ${checked} проверено, ${available} доступны`;
          $("#telegramMeta").textContent = "Показаны результаты live-проверки. Для следующих unchecked нажмите Preview.";
        }
      } catch (error) {
        $("#telegramStatus").textContent = error.data?.message || error.message;
      }
    }

    function syncTelegramMode() {
      const dryRun = $("#tgDryRun").checked;
      $("#tgCheckBtn").textContent = dryRun ? "Preview выбранных" : "Проверить выбранные live";
      $("#telegramMeta").textContent = dryRun
        ? "Preview включен; live-проверка использует только вкладку Аккаунты"
        : "Live режим: введите CHECK; основной аккаунт не используется для проверки";
      $("#tgModeLabel").textContent = dryRun ? "dry-run preview" : "live check";
      $("#tgConfirmState").textContent = dryRun ? "не требуется" : "требуется CHECK";
      $("#tgConfirm").disabled = dryRun;
    }

    function renderTelegramTask(task) {
      $("#telegramStatus").textContent = task.message || task.status;
      setProgress("#telegramProgress", task.progress || 0);
      loadAccounts().catch(() => {});
      if (task.status === "completed" && task.result) {
        $("#telegramRows").innerHTML = (task.result.rows || []).map((row) => `
          <tr>
            <td></td>
            <td class="mono">@${escapeHtml(row.username)}</td>
            <td>${fmtScore(row.score)}</td>
            <td>${badge(row.status)}</td>
            <td>${escapeHtml(row.generation_type || "-")}</td>
            <td>${escapeHtml(row.batch_num || "-")}</td>
          </tr>
        `).join("");
      }
    }

    async function loadChannels() {
      const params = new URLSearchParams();
      params.set("limit", $("#channelLimit").value || "20");
      if ($("#channelMinScore").value) params.set("min_score", $("#channelMinScore").value);
      const data = await api(`/api/channels/available?${params.toString()}`);
      $("#channelRows").innerHTML = data.rows.length ? data.rows.map((row) => `
        <tr>
          <td class="mono">@${escapeHtml(row.username)}</td>
          <td>${fmtScore(row.score)}</td>
          <td>${badge(row.status)}</td>
          <td>${escapeHtml(row.generation_type || "-")}</td>
          <td><button class="btn" data-channel="${escapeHtml(row.username)}" data-score="${escapeHtml(row.score)}">Выбрать</button></td>
        </tr>
      `).join("") : `<tr><td colspan="5" class="empty"><div class="empty-state"><strong>Нет available username</strong><span>Создание канала доступно только для проверенных available username.</span></div></td></tr>`;
      $$("[data-channel]").forEach((button) => button.addEventListener("click", () => selectChannel(button.dataset.channel, button.dataset.score)));
    }

    function selectChannel(username, score) {
      app.selectedChannel = { username, score };
      $("#selectedChannelName").textContent = `@${username}`;
      $("#selectedChannelScore").textContent = `score: ${fmtScore(score)}`;
      $("#channelTitle").value = username;
      $("#channelConfirmLabel").firstChild.textContent = `Использовать ${username} (score: ${fmtScore(score)})? (y/n)`;
      $("#channelStatus").textContent = "Готово к preview";
    }

    async function createChannel() {
      if (!app.selectedChannel) {
        $("#channelStatus").textContent = "Username не выбран";
        return;
      }
      $("#channelStatus").textContent = "Подготовка...";
      setProgress("#channelProgress", 1);
      try {
        const data = await api("/api/channels/create", {
          method: "POST",
          body: JSON.stringify({
            username: app.selectedChannel.username,
            title: $("#channelTitle").value.trim(),
            dry_run: $("#channelDryRun").checked,
            confirm: $("#channelConfirm").value.trim()
          })
        });
        if (data.dry_run) {
          $("#channelStatus").textContent = data.message;
          return;
        }
        $("#channelTaskId").textContent = data.task.id;
        await pollTask(data.task.id, renderChannelTask);
        await loadDashboard();
        await loadChannels();
      } catch (error) {
        $("#channelStatus").textContent = error.data?.message || error.data?.reason || error.message;
      }
    }

    function renderChannelTask(task) {
      $("#channelStatus").textContent = task.message || task.status;
      setProgress("#channelProgress", task.progress || 0);
      if (task.status === "completed" && task.result) {
        $("#channelStatus").textContent = `Создан канал ID ${task.result.channel_id}`;
      }
    }

    async function pollTask(taskId, render) {
      for (;;) {
        const data = await api(`/api/tasks/${taskId}`);
        const task = data.task;
        render(task);
        if (task.status !== "running") return task;
        await new Promise((resolve) => setTimeout(resolve, 1200));
      }
    }

    async function loadLogs() {
      const lines = $("#logLines").value || "160";
      const data = await api(`/api/logs?lines=${encodeURIComponent(lines)}`);
      $("#logsMeta").textContent = data.path;
      $("#logsBox").textContent = data.text || "";
      $("#logsBox").scrollTop = $("#logsBox").scrollHeight;
    }

    function bindEvents() {
      $$(".nav button").forEach((button) => {
        button.addEventListener("click", () => {
          $$(".nav button").forEach((item) => item.classList.remove("is-active"));
          $$(".section").forEach((item) => item.classList.remove("is-active"));
          button.classList.add("is-active");
          $(`#${button.dataset.tab}`).classList.add("is-active");
        });
      });
      $("#refreshDashboard").addEventListener("click", loadDashboard);
      $("#loadDatabase").addEventListener("click", loadDatabase);
      $("#dbSearch").addEventListener("keydown", (event) => { if (event.key === "Enter") loadDatabase(); });
      $("#generateBtn").addEventListener("click", startGeneration);
      $("#tgSaveConfig").addEventListener("click", saveTelegramConfig);
      $("#tgAuthRefresh").addEventListener("click", loadTelegramAuthStatus);
      $("#tgSendCode").addEventListener("click", sendTelegramCode);
      $("#tgConfirmCode").addEventListener("click", confirmTelegramCode);
      $("#tgConfirmPassword").addEventListener("click", confirmTelegramPassword);
      $("#tgCancelAuth").addEventListener("click", cancelTelegramAuth);
      $("#tgResetSession").addEventListener("click", resetTelegramSession);
      $("#tgCode").addEventListener("keydown", (event) => { if (event.key === "Enter") confirmTelegramCode(); });
      $("#tgPassword").addEventListener("keydown", (event) => { if (event.key === "Enter") confirmTelegramPassword(); });
      $("#tgPreviewBtn").addEventListener("click", loadTelegramPreview);
      $("#tgCheckBtn").addEventListener("click", checkTelegramSelected);
      $("#tgDryRun").addEventListener("change", syncTelegramMode);
      $("#accountAddBtn").addEventListener("click", () => {
        resetAccountAuthForm(true);
        setAccountAuthBadge("not started");
        $("#accountAuthMessage").textContent = "Введите API ID, API Hash и телефон.";
        $("#accountApiId").focus();
      });
      $("#accountSendCode").addEventListener("click", startAccountAuth);
      $("#accountConfirmCode").addEventListener("click", confirmAccountCode);
      $("#accountConfirmPassword").addEventListener("click", confirmAccountPassword);
      $("#accountCancelAuth").addEventListener("click", cancelAccountAuth);
      $("#accountCode").addEventListener("keydown", (event) => { if (event.key === "Enter") confirmAccountCode(); });
      $("#accountPassword").addEventListener("keydown", (event) => { if (event.key === "Enter") confirmAccountPassword(); });
      $("#loadChannels").addEventListener("click", loadChannels);
      $("#createChannelBtn").addEventListener("click", createChannel);
      $("#refreshLogs").addEventListener("click", loadLogs);
    }

    async function init() {
      await registerBrowserClient();
      bindEvents();
      syncTelegramMode();
      await loadConfig();
      await Promise.all([loadDashboard(), loadDatabase(), loadTelegramConfig(), loadTelegramAuthStatus(), loadAccounts(), loadTelegramPreview(), loadChannels(), loadLogs()]);
    }

    init().catch((error) => {
      console.error(error);
      $("#dashMeta").textContent = error.message;
    });
  </script>
</body>
</html>
"""
