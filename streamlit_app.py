"""
Ulive Smart Fulfillment — Streamlit deployment
================================================
A single, self-contained Streamlit app. The animated intro "tour" plays first;
when it finishes the user clicks **Enter the Demo** (or **Skip intro** at any time)
to flow straight into the interactive "AI Order Matching" demo — exactly like the
original design. Both screens live in ONE embedded page, so navigation happens
client-side with no sidebar.

Run locally:
    pip install -r requirements.txt
    streamlit run streamlit_app.py

Deploy on Streamlit Community Cloud:
    Push this file + requirements.txt to a GitHub repo, then create a new app
    pointing at streamlit_app.py.
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Ulive Smart Fulfillment",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Strip Streamlit chrome so the embedded dark UI fills the page.
st.markdown(
    """
    <style>
      .block-container {padding: 0 !important; max-width: 100%;}
      header[data-testid="stHeader"] {display: none;}
      #MainMenu, footer {visibility: hidden;}
      section[data-testid="stSidebar"] {display: none;}
      .stApp {background: #0d1117;}
      div[data-testid="stDecoration"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# Combined single-page app:  TOUR  →  (Enter Demo / Skip intro)  →  DEMO
# The intro tour is a vanilla-JS rebuild of "Ulive Tour Cover.dc.html"
# (the original needed a proprietary DCLogic runtime). The demo below is the
# "Ulive_Smart_Fulfillment_Demo.html" embedded verbatim.
# ============================================================================
PAGE_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  /* ---------- shared / demo styles ---------- */
  :root{
    --bg:#0d1117; --panel:#161b22; --panel2:#1c2330; --line:#283042;
    --ink:#e6edf3; --muted:#8b97a8; --muted2:#5d6b7e;
    --brand:#3b82f6; --brand2:#6366f1;
    --green:#22c55e; --green-bg:rgba(34,197,94,.12);
    --amber:#f59e0b; --amber-bg:rgba(245,158,11,.12);
    --slate:#64748b; --slate-bg:rgba(100,116,139,.14);
    --red:#ef4444;
    --shadow:0 10px 30px rgba(0,0,0,.35);
    --radius:16px;
    font-synthesis:none;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{background:var(--bg);color:var(--ink);
    font-family:'Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,'PingFang SC','Microsoft YaHei',sans-serif;
    -webkit-font-smoothing:antialiased;line-height:1.5}
  a{color:var(--brand)}
  .wrap{max-width:1180px;margin:0 auto;padding:28px 20px 80px}

  /* ---------- tour-only animations ---------- */
  @keyframes tourRise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
  @keyframes glowPulse{0%,100%{opacity:.4;transform:scale(1)}50%{opacity:.85;transform:scale(1.12)}}
  @keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}
  .stage-anim{animation:tourRise .5s ease both}

  header.top{
    display:flex;align-items:center;gap:16px;flex-wrap:wrap;
    background:linear-gradient(120deg,#11203b 0%,#161b22 60%);
    border:1px solid var(--line);border-radius:var(--radius);
    padding:20px 24px;box-shadow:var(--shadow);margin-bottom:22px;position:relative;overflow:hidden}
  header.top::after{content:"";position:absolute;right:-60px;top:-60px;width:240px;height:240px;
    background:radial-gradient(circle,rgba(99,102,241,.35),transparent 70%);filter:blur(10px)}
  .logo{width:52px;height:52px;border-radius:14px;flex:0 0 auto;
    background:linear-gradient(135deg,var(--brand),var(--brand2));
    display:grid;place-items:center;font-size:26px;box-shadow:0 6px 18px rgba(59,130,246,.45)}
  .htext h1{font-size:21px;letter-spacing:.2px}
  .htext p{color:var(--muted);font-size:13px;margin-top:2px}
  .tag{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap;z-index:1;align-items:center}
  .pill{font-size:11.5px;padding:5px 11px;border-radius:999px;border:1px solid var(--line);
    background:rgba(255,255,255,.03);color:var(--muted)}
  .pill b{color:var(--ink)}
  .pill.link{cursor:pointer;transition:.15s}
  .pill.link:hover{border-color:var(--brand);color:var(--ink)}

  .stepper{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:22px}
  .step{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 14px;position:relative;
    transition:.4s;opacity:.55}
  .step .num{width:28px;height:28px;border-radius:8px;background:var(--panel2);border:1px solid var(--line);
    display:grid;place-items:center;font-weight:700;font-size:13px;color:var(--muted);transition:.4s}
  .step h4{font-size:13.5px;margin:10px 0 3px}
  .step p{font-size:11.5px;color:var(--muted)}
  .step.active{opacity:1;border-color:var(--brand);box-shadow:0 0 0 1px var(--brand),0 8px 22px rgba(59,130,246,.18)}
  .step.active .num{background:linear-gradient(135deg,var(--brand),var(--brand2));color:#fff;border-color:transparent}
  .step.done{opacity:1;border-color:rgba(34,197,94,.5)}
  .step.done .num{background:var(--green);color:#04210f;border-color:transparent}
  .step.done .num::after{content:"✓"}
  .step.done .num span{display:none}

  .grid{display:grid;grid-template-columns:340px 1fr;gap:20px;align-items:start}
  @media(max-width:900px){.grid{grid-template-columns:1fr}.stepper{grid-template-columns:1fr 1fr}}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}
  .card .hd{padding:16px 18px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:10px}
  .card .hd .ic{font-size:18px}
  .card .hd h3{font-size:15px}
  .card .hd small{color:var(--muted);font-weight:400;font-size:12px;display:block}
  .card .bd{padding:18px}

  .cust{font-size:13px}
  .cust .row{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px dashed var(--line)}
  .cust .row:last-child{border:0}
  .cust .row span:first-child{color:var(--muted)}
  .cust .row b{font-weight:600}
  .src-note{margin-top:14px;font-size:11.5px;color:var(--muted);background:var(--panel2);
    border:1px solid var(--line);border-radius:10px;padding:10px 12px;line-height:1.6}

  .btn{appearance:none;border:0;cursor:pointer;font-weight:700;font-size:14px;color:#fff;
    background:linear-gradient(135deg,var(--brand),var(--brand2));padding:13px 16px;border-radius:12px;width:100%;
    box-shadow:0 8px 20px rgba(59,130,246,.35);transition:.18s;display:flex;align-items:center;justify-content:center;gap:9px}
  .btn:hover{transform:translateY(-1px);filter:brightness(1.07)}
  .btn:disabled{opacity:.45;cursor:not-allowed;transform:none;filter:none}
  .btn.ghost{background:transparent;border:1px solid var(--line);color:var(--ink);box-shadow:none}
  .btn.sm{width:auto;padding:9px 14px;font-size:13px}
  .btnrow{display:flex;gap:10px;margin-top:16px}

  .empty{padding:60px 24px;text-align:center;color:var(--muted)}
  .empty .big{font-size:46px;margin-bottom:10px;opacity:.8}
  .empty h3{color:var(--ink);font-size:17px;margin-bottom:6px}
  .empty p{font-size:13px;max-width:440px;margin:0 auto}

  .console{font-family:'Consolas','SF Mono',ui-monospace,monospace;font-size:12px;background:#0a0e14;
    border:1px solid var(--line);border-radius:12px;padding:14px;height:0;overflow:hidden;transition:height .35s ease;color:#9fb3c8}
  .console.show{height:150px;overflow:auto;margin-bottom:18px}
  .console .ln{padding:2px 0;opacity:0;animation:fade .3s forwards}
  .console .ln .t{color:var(--muted2)}
  .console .ln.ok{color:#7ee2a8}
  .console .ln.warn{color:#f3c267}
  .console .ln.info{color:#7fb4ff}
  @keyframes fade{to{opacity:1}}

  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:18px}
  @media(max-width:680px){.kpis{grid-template-columns:1fr 1fr}}
  .kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:15px 16px;position:relative;overflow:hidden}
  .kpi .lab{font-size:11.5px;color:var(--muted);display:flex;align-items:center;gap:6px}
  .kpi .val{font-size:30px;font-weight:800;margin-top:6px;line-height:1}
  .kpi .sub{font-size:11px;color:var(--muted);margin-top:4px}
  .kpi .bar{position:absolute;left:0;bottom:0;height:4px;width:100%}
  .kpi.green .val{color:var(--green)} .kpi.green .bar{background:var(--green)}
  .kpi.amber .val{color:var(--amber)} .kpi.amber .bar{background:var(--amber)}
  .kpi.slate .val{color:#93a3b8} .kpi.slate .bar{background:var(--slate)}
  .kpi.brand .val{color:#7fb4ff} .kpi.brand .bar{background:var(--brand)}

  .reco{display:flex;gap:14px;align-items:center;border-radius:14px;padding:16px 18px;margin-bottom:18px;
    border:1px solid var(--line)}
  .reco .em{font-size:30px}
  .reco h3{font-size:16px;margin-bottom:3px}
  .reco p{font-size:12.5px;color:var(--muted)}
  .reco.hold{background:linear-gradient(120deg,rgba(245,158,11,.14),transparent);border-color:rgba(245,158,11,.45)}
  .reco.go{background:linear-gradient(120deg,rgba(34,197,94,.14),transparent);border-color:rgba(34,197,94,.45)}
  .reco .act{margin-left:auto;display:flex;gap:8px}

  .tablewrap{overflow:auto;border-radius:12px;border:1px solid var(--line)}
  table{width:100%;border-collapse:collapse;font-size:12.5px;min-width:760px}
  thead th{position:sticky;top:0;background:var(--panel2);color:var(--muted);text-align:left;
    padding:11px 12px;font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid var(--line);white-space:nowrap}
  tbody td{padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:middle}
  tbody tr:hover{background:rgba(255,255,255,.02)}
  tbody tr:last-child td{border-bottom:0}
  .code{font-family:'Consolas',monospace;font-size:11.5px;color:#9fb4cf;background:var(--panel2);
    padding:2px 7px;border-radius:6px;white-space:nowrap}
  .desc b{font-weight:600;display:block;font-size:12.5px}
  .desc small{color:var(--muted);font-size:11px}
  .sup{font-size:11px;color:var(--muted);white-space:nowrap}
  .hub{font-size:10.5px;padding:2px 7px;border-radius:6px;background:var(--panel2);border:1px solid var(--line);color:var(--muted)}
  .qty{font-variant-numeric:tabular-nums;white-space:nowrap;font-weight:600}
  .qty small{color:var(--muted);font-weight:400}

  .badge{display:inline-flex;align-items:center;gap:6px;font-size:11px;font-weight:700;
    padding:4px 10px;border-radius:999px;white-space:nowrap}
  .b-green{color:#86efac;background:var(--green-bg);border:1px solid rgba(34,197,94,.4)}
  .b-amber{color:#fcd34d;background:var(--amber-bg);border:1px solid rgba(245,158,11,.4)}
  .b-slate{color:#cbd5e1;background:var(--slate-bg);border:1px solid rgba(100,116,139,.4)}
  .dot{width:7px;height:7px;border-radius:50%}
  .b-green .dot{background:var(--green)} .b-amber .dot{background:var(--amber)} .b-slate .dot{background:var(--slate)}

  .act-btn{font-size:11px;font-weight:700;padding:6px 11px;border-radius:8px;border:1px solid var(--line);
    cursor:pointer;background:var(--panel2);color:var(--ink);transition:.15s;white-space:nowrap}
  .act-btn.go{background:var(--green);color:#04210f;border-color:transparent}
  .act-btn.go:hover{filter:brightness(1.1)}
  .act-btn.wait{color:var(--muted)}
  .act-btn:disabled{opacity:.5;cursor:default}

  .filters{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}
  .chip{font-size:12px;padding:7px 13px;border-radius:999px;border:1px solid var(--line);background:var(--panel);
    color:var(--muted);cursor:pointer;transition:.15s;display:flex;align-items:center;gap:7px}
  .chip.active{color:var(--ink);border-color:var(--brand);background:rgba(59,130,246,.12)}
  .chip .c{width:8px;height:8px;border-radius:50%}

  .legend{display:flex;gap:18px;flex-wrap:wrap;margin-top:14px;font-size:11.5px;color:var(--muted)}
  .legend span{display:flex;align-items:center;gap:7px}

  footer{margin-top:30px;color:var(--muted2);font-size:11.5px;text-align:center;line-height:1.8}
  .hide{display:none!important}
  .fadein{animation:rise .5s ease both}
  @keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}

  .scan-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:4px}
  @media(max-width:680px){.scan-grid{grid-template-columns:1fr}}
  .sup-card{background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:12px}
  .sup-card .nm{font-size:12.5px;font-weight:700;display:flex;align-items:center;gap:8px}
  .sup-card .meta{font-size:11px;color:var(--muted);margin-top:3px}
  .sup-card .prog{height:6px;border-radius:6px;background:var(--line);margin-top:10px;overflow:hidden}
  .sup-card .prog i{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--brand),var(--green));transition:width .8s ease}
  .sup-card .st{font-size:10.5px;color:var(--muted);margin-top:6px;font-variant-numeric:tabular-nums}

  /* ---------- tour text (class-based so it can scale responsively) ---------- */
  .tk-kicker{font-size:11px;letter-spacing:2.5px;color:#7fb4ff;font-weight:700;margin-bottom:12px}
  .tk-title{font-size:33px;font-weight:800;letter-spacing:-.4px;line-height:1.12;margin-bottom:26px;max-width:760px}
  .tk-stagebox{min-height:236px;display:grid;place-items:center;width:100%}
  .tk-caption{font-size:15.5px;color:#aeb9c8;margin-top:26px;max-width:620px;line-height:1.6}
  .tk-outro-h{font-size:38px;font-weight:800;letter-spacing:-.5px;line-height:1.1}
  .tk-outro-p{font-size:15px;color:#8b97a8;margin-top:12px;max-width:480px;margin-left:auto;margin-right:auto}
  .tk-actions{display:flex;gap:12px;align-items:center;justify-content:center;margin-top:6px;flex-wrap:wrap}

  /* ---------- tablet (<= 820px) ---------- */
  @media(max-width:820px){
    .tourcard{height:auto !important;min-height:520px}
    .tk-title{font-size:27px;margin-bottom:18px}
    .tk-outro-h{font-size:30px}
    .grid{grid-template-columns:1fr}
  }
  /* ---------- phone (<= 560px) ---------- */
  @media(max-width:560px){
    #tourView{padding:10px !important}
    .tourcard{height:auto !important;min-height:0;box-shadow:0 10px 30px rgba(0,0,0,.4)}
    .tourtop{padding:14px 16px !important;gap:9px !important}
    .tourstage{padding:6px 14px !important}
    .tourctrls{padding:12px 12px 16px !important;gap:10px !important}
    .tk-kicker{font-size:10px;letter-spacing:2px;margin-bottom:8px}
    .tk-title{font-size:20px;margin-bottom:14px;line-height:1.18}
    .tk-stagebox{min-height:150px}
    .tk-caption{font-size:12.5px;margin-top:16px;line-height:1.5}
    .tk-outro-h{font-size:22px}
    .tk-outro-p{font-size:12.5px;margin-top:8px}
    #ph-counter{display:none}
    .wrap{padding:16px 12px 60px}
    header.top{padding:16px 16px}
    .htext h1{font-size:18px}
    .stepper{grid-template-columns:1fr 1fr;gap:8px}
    .reco{flex-wrap:wrap}
    .reco .act{margin-left:0;width:100%}
    .reco .act .act-btn{flex:1}
    .kpi .val{font-size:24px}
    .btnrow{flex-wrap:wrap}
  }
</style>
</head>
<body>

<!-- ============================== TOUR VIEW ============================== -->
<div id="tourView" style="display:flex;align-items:center;justify-content:center;padding:22px;background:#0d1117">
  <div class="tourcard" style="position:relative;width:100%;max-width:1100px;height:620px;overflow:hidden;border-radius:16px;border:1px solid #283042;background:radial-gradient(1100px 700px at 78% -10%,#15233f 0%,#0d1117 55%);color:#e6edf3;display:flex;flex-direction:column;box-shadow:0 18px 50px rgba(0,0,0,.45)">

    <div style="position:absolute;right:-120px;top:-120px;width:420px;height:420px;border-radius:50%;background:radial-gradient(circle,rgba(99,102,241,.28),transparent 70%);filter:blur(14px);pointer-events:none"></div>
    <div style="position:absolute;left:-100px;bottom:-140px;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,rgba(59,130,246,.18),transparent 70%);filter:blur(12px);pointer-events:none"></div>

    <!-- top bar -->
    <div class="tourtop" style="display:flex;align-items:center;gap:13px;padding:20px 28px;z-index:2;flex-wrap:wrap">
      <div style="width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#3b82f6,#6366f1);display:grid;place-items:center;font-size:18px;box-shadow:0 6px 16px rgba(59,130,246,.45)">📦</div>
      <div style="line-height:1.25">
        <div style="font-size:14px;font-weight:700;letter-spacing:.2px">David Lau Logistic Matching System</div>
        <div style="font-size:11px;color:#8b97a8">Guided tour · AI order-to-fulfillment</div>
      </div>
      <span style="margin-left:10px;font-size:10px;letter-spacing:1.5px;color:#8b97a8;border:1px solid #283042;padding:4px 9px;border-radius:999px">INTRO</span>
      <button onclick="showDemo()" style="margin-left:auto;border:1px solid #283042;background:rgba(255,255,255,.03);color:#e6edf3;font-size:12.5px;font-weight:600;padding:8px 15px;border-radius:999px;cursor:pointer">Skip intro →</button>
    </div>

    <!-- stage -->
    <div class="tourstage" style="flex:1;display:grid;place-items:center;padding:8px 28px;z-index:1;min-height:0">
      <div id="t-stage" style="width:100%;max-width:940px;text-align:center"></div>
    </div>

    <!-- bottom controls -->
    <div class="tourctrls" style="display:flex;align-items:center;gap:18px;padding:18px 28px 24px;z-index:2">
      <div id="ph-counter" style="font-size:12px;color:#8b97a8;font-variant-numeric:tabular-nums;min-width:84px">01 / 06</div>
      <div style="flex:1;display:flex;gap:7px;max-width:560px;margin:0 auto">
        <div data-seek="0" style="flex:1;height:4px;border-radius:3px;background:#283042;overflow:hidden;cursor:pointer"><div id="ph-fill-0" style="height:100%;width:0%;background:linear-gradient(90deg,#3b82f6,#6366f1);border-radius:3px;transition:width .12s linear"></div></div>
        <div data-seek="1" style="flex:1;height:4px;border-radius:3px;background:#283042;overflow:hidden;cursor:pointer"><div id="ph-fill-1" style="height:100%;width:0%;background:linear-gradient(90deg,#3b82f6,#6366f1);border-radius:3px;transition:width .12s linear"></div></div>
        <div data-seek="2" style="flex:1;height:4px;border-radius:3px;background:#283042;overflow:hidden;cursor:pointer"><div id="ph-fill-2" style="height:100%;width:0%;background:linear-gradient(90deg,#3b82f6,#6366f1);border-radius:3px;transition:width .12s linear"></div></div>
        <div data-seek="3" style="flex:1;height:4px;border-radius:3px;background:#283042;overflow:hidden;cursor:pointer"><div id="ph-fill-3" style="height:100%;width:0%;background:linear-gradient(90deg,#3b82f6,#6366f1);border-radius:3px;transition:width .12s linear"></div></div>
        <div data-seek="4" style="flex:1;height:4px;border-radius:3px;background:#283042;overflow:hidden;cursor:pointer"><div id="ph-fill-4" style="height:100%;width:0%;background:linear-gradient(90deg,#3b82f6,#6366f1);border-radius:3px;transition:width .12s linear"></div></div>
        <div data-seek="5" style="flex:1;height:4px;border-radius:3px;background:#283042;overflow:hidden;cursor:pointer"><div id="ph-fill-5" style="height:100%;width:0%;background:linear-gradient(90deg,#3b82f6,#6366f1);border-radius:3px;transition:width .12s linear"></div></div>
      </div>
      <div style="display:flex;gap:9px;min-width:84px;justify-content:flex-end">
        <button id="ph-play" style="width:36px;height:36px;border-radius:10px;border:1px solid #283042;background:rgba(255,255,255,.03);color:#e6edf3;font-size:13px;cursor:pointer">&#10074;&#10074;</button>
        <button id="ph-replay" style="width:36px;height:36px;border-radius:10px;border:1px solid #283042;background:rgba(255,255,255,.03);color:#e6edf3;font-size:14px;cursor:pointer">&#8634;</button>
      </div>
    </div>
  </div>
</div>

<!-- ============================== DEMO VIEW ============================== -->
<div id="demoView" style="display:none">
  <div class="wrap">

    <header class="top">
      <div class="logo">🛒</div>
      <div class="htext">
        <h1>Ulive Smart Fulfillment</h1>
        <p>AI Order-to-Receiving Matching Engine · Live Demo</p>
      </div>
      <div class="tag">
        <span class="pill">Hubs: <b>K.K.</b> · <b>K.L.</b></span>
        <span class="pill">Suppliers: <b>A · B · C</b></span>
        <span class="pill">Mode: <b>AI Automated</b></span>
        <span class="pill link" onclick="showTour()">↺ <b>Replay intro</b></span>
      </div>
    </header>

    <div class="stepper" id="stepper">
      <div class="step" data-step="1">
        <div class="num"><span>1</span></div>
        <h4>Order Intake & Extraction</h4>
        <p>Customer order from Messenger → structured line items</p>
      </div>
      <div class="step" data-step="2">
        <div class="num"><span>2</span></div>
        <h4>Inbound Receiving & Scan</h4>
        <p>Suppliers ship to hubs · barcode scan vs digital records</p>
      </div>
      <div class="step" data-step="3">
        <div class="num"><span>3</span></div>
        <h4>Smart Inventory Matching</h4>
        <p>Match received goods to each ordered line</p>
      </div>
      <div class="step" data-step="4">
        <div class="num"><span>4</span></div>
        <h4>Optimized Output</h4>
        <p>Fulfillment status + Fulfill / Hold recommendation</p>
      </div>
    </div>

    <div class="grid">
      <div>
        <div class="card">
          <div class="hd"><span class="ic">📄</span>
            <div><h3>Customer Order Source</h3><small>Uploaded Excel — Amy Yee</small></div>
          </div>
          <div class="bd">
            <div class="cust">
              <div class="row"><span>Customer</span><b>AMY YEE</b></div>
              <div class="row"><span>FB / Channel</span><b>Messenger</b></div>
              <div class="row"><span>Phone</span><b>+60 98808133</b></div>
              <div class="row"><span>Country</span><b>🇲🇾 Malaysia</b></div>
              <div class="row"><span>Invoices</span><b>2 (19023 · 19697)</b></div>
              <div class="row"><span>Order lines</span><b id="lineCount">—</b></div>
              <div class="row"><span>Order value</span><b id="orderValue">—</b></div>
            </div>
            <div class="src-note">
              📌 <b>How the demo maps to the real flow:</b> Amy's two invoice screenshots are
              OCR-extracted into structured lines. Each line is auto-assigned to its supplier &amp;
              receiving hub, then matched against what has physically arrived &amp; been scanned.
            </div>
            <div class="btnrow">
              <button class="btn" id="uploadBtn">📥 Simulate Excel Upload</button>
            </div>
            <div class="btnrow">
              <button class="btn ghost sm" id="runBtn" disabled style="flex:1">▶ Run AI Matching</button>
              <button class="btn ghost sm" id="resetBtn" style="width:auto">↺ Reset</button>
            </div>
          </div>
        </div>

        <div class="card" style="margin-top:18px">
          <div class="hd"><span class="ic">🏭</span>
            <div><h3>Inbound Receiving</h3><small>Live scan progress by supplier</small></div>
          </div>
          <div class="bd">
            <div class="scan-grid" id="scanGrid">
              <div class="empty" style="padding:24px;grid-column:1/-1">
                <div class="big">📦</div>
                <p style="font-size:12px">Run matching to see supplier receiving progress.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div class="console" id="console"></div>

        <div id="resultArea">
          <div class="card">
            <div class="empty">
              <div class="big">🤖</div>
              <h3>Awaiting order &amp; matching run</h3>
              <p>Click <b>Simulate Excel Upload</b> to load Amy Yee's order, then
                 <b>Run AI Matching</b> to watch the engine reconcile every line against
                 received supplier stock and decide what can ship.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <footer>
      <div>Ulive Purchase-Order → Automation · Demo build · single-file HTML (no server, no dependencies — upload anywhere)</div>
      <div>Replaces the manual bottleneck: 50+ printed lists &amp; hand-checking at K.K./K.L. → real-time AI matching.</div>
    </footer>
  </div>
</div>

<!-- ============================== DEMO SCRIPT ============================== -->
<script>
const SUPPLIERS = {
  A: {name:"Supplier A · Electronics", hub:"K.K.", emoji:"🔌"},
  B: {name:"Supplier B · 虾哥 Herbal & Soup", hub:"K.L.", emoji:"🍲"},
  C: {name:"Supplier C · SukGarden Care", hub:"K.K.", emoji:"🧴"}
};

const ORDER = [
  {inv:"19023", code:"E10C", en:"10W Spray Handheld Fan (White)", cn:"喷雾制冷手持电风扇", sup:"A", price:69.90, ordered:1, received:1},
  {inv:"19023", code:"E41",  en:"Fast Charger YSY-6099 65W",     cn:"快充插头",           sup:"A", price:39.90, ordered:1, received:1},
  {inv:"19023", code:"E45",  en:"Multi-function Electric Cooker 110V", cn:"多功能电煮锅", sup:"A", price:118.00, ordered:1, received:0},
  {inv:"19023", code:"H16",  en:"Lingzhi Chicken-Bone-Grass Soup Pack", cn:"灵芝鸡骨草汤包", sup:"B", price:9.90, ordered:1, received:1},
  {inv:"19023", code:"H20",  en:"Five-Finger Peach Soup Pack",   cn:"老火靓汤五指毛桃汤包", sup:"B", price:9.90, ordered:2, received:1},
  {inv:"19023", code:"H21",  en:"Agaricus Blazei 250g",          cn:"姬松茸",             sup:"B", price:39.90, ordered:1, received:1},
  {inv:"19023", code:"H26",  en:"Five-Finger Peach Root 200g",   cn:"五指毛桃",           sup:"B", price:18.90, ordered:1, received:1},
  {inv:"19023", code:"H27",  en:"Dried Lily 300g",               cn:"百合",               sup:"B", price:33.90, ordered:1, received:0},
  {inv:"19023", code:"H30",  en:"Lotus Seeds 450g",              cn:"莲子",               sup:"B", price:29.90, ordered:1, received:1},
  {inv:"19023", code:"H36",  en:"Gui Fei Fungus 250g",           cn:"贵妃耳",             sup:"B", price:33.90, ordered:1, received:1},
  {inv:"19023", code:"H37",  en:"White Jade Fungus 250g",        cn:"白玉耳",             sup:"B", price:32.90, ordered:1, received:1},
  {inv:"19697", code:"?",    en:"Unreadable item (OCR low-confidence)", cn:"票面截断 — 需人工核对", sup:"C", price:9.90, ordered:2, received:0, verify:true},
  {inv:"19697", code:"R35",  en:"SukGarden Fabric Softener Sachet 36g (+5 free)", cn:"蔬果园香氛柔顺剂", sup:"C", price:1.50, ordered:5, received:5},
  {inv:"19697", code:"R40",  en:"SukGarden Bluebell Shower Gel 800g", cn:"蓝风铃精油沐浴乳", sup:"C", price:65.80, ordered:1, received:1, note:'flagged "Owe"'},
  {inv:"19697", code:"R42",  en:"SukGarden Sandalwood-Camellia Shower Gel 800g", cn:"白檀山茶精油沐浴乳", sup:"C", price:65.80, ordered:1, received:0}
];

function statusOf(it){
  if(it.received >= it.ordered && it.received>0) return "full";
  if(it.received > 0 && it.received < it.ordered) return "partial";
  return "pending";
}
const STATUS = {
  full:   {label:"Confirmed",      badge:"b-green", chip:"#22c55e", verb:"Received in full"},
  partial:{label:"Partial",        badge:"b-amber", chip:"#f59e0b", verb:"Missing quantity"},
  pending:{label:"To Be Confirmed",badge:"b-slate", chip:"#64748b", verb:"Not yet received"}
};
const RM = n => "RM "+n.toFixed(2);

const $ = s => document.querySelector(s);
const steps = [...document.querySelectorAll('.step')];
const consoleEl = $('#console');
let loaded=false, activeFilter="all";

function setStep(n, mode){
  steps.forEach(s=>{
    const k = +s.dataset.step;
    s.classList.remove('active','done');
    if(k<n) s.classList.add('done');
    else if(k===n) s.classList.add(mode==='done'?'done':'active');
  });
}
function allDone(){ steps.forEach(s=>{s.classList.remove('active');s.classList.add('done')}); }

function log(msg, cls=""){
  consoleEl.classList.add('show');
  const d=document.createElement('div');
  d.className='ln '+cls;
  const t=new Intl.DateTimeFormat('en-GB',{hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(new Date());
  d.innerHTML=`<span class="t">[${t}]</span> ${msg}`;
  consoleEl.appendChild(d);
  consoleEl.scrollTop=consoleEl.scrollHeight;
}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

$('#uploadBtn').addEventListener('click', ()=>{
  loaded=true;
  const lines=ORDER.length;
  const val=ORDER.reduce((s,i)=>s+i.price*i.ordered,0);
  $('#lineCount').textContent=lines+" lines";
  $('#orderValue').textContent=RM(val);
  setStep(1,'done');
  log('📄 Excel parsed — <b>Ulive_Invoices.xlsx</b>','info');
  log(`✓ Extracted <b>${lines}</b> order lines across 2 invoices for AMY YEE`,'ok');
  $('#runBtn').disabled=false;
  $('#uploadBtn').disabled=true;
  $('#uploadBtn').textContent="✓ Order Loaded";
  renderResults(false);
});

$('#resetBtn').addEventListener('click', ()=>{
  loaded=false; activeFilter="all";
  steps.forEach(s=>s.classList.remove('active','done'));
  consoleEl.classList.remove('show'); consoleEl.innerHTML="";
  $('#lineCount').textContent="—"; $('#orderValue').textContent="—";
  $('#runBtn').disabled=true; $('#runBtn').textContent="▶ Run AI Matching";
  $('#uploadBtn').disabled=false; $('#uploadBtn').textContent="📥 Simulate Excel Upload";
  $('#scanGrid').innerHTML='<div class="empty" style="padding:24px;grid-column:1/-1"><div class="big">📦</div><p style="font-size:12px">Run matching to see supplier receiving progress.</p></div>';
  $('#resultArea').innerHTML='<div class="card"><div class="empty"><div class="big">🤖</div><h3>Awaiting order &amp; matching run</h3><p>Click <b>Simulate Excel Upload</b> to load Amy Yee\'s order, then <b>Run AI Matching</b> to watch the engine reconcile every line against received supplier stock and decide what can ship.</p></div></div>';
});

$('#runBtn').addEventListener('click', run);
async function run(){
  $('#runBtn').disabled=true; $('#runBtn').textContent="⏳ Matching…";

  setStep(2,'active');
  log('🏭 Connecting to receiving hubs K.K. &amp; K.L. …','info');
  buildScanCards();
  await sleep(500);
  for(const key of Object.keys(SUPPLIERS)){
    await scanSupplier(key);
  }
  setStep(2,'done');

  setStep(3,'active');
  log('🤖 Smart Inventory Matching — reconciling received stock to ordered lines…','info');
  await sleep(700);
  const f=ORDER.filter(i=>statusOf(i)==='full').length;
  const p=ORDER.filter(i=>statusOf(i)==='partial').length;
  const g=ORDER.filter(i=>statusOf(i)==='pending').length;
  log(`✓ ${f} confirmed · ⚠ ${p} partial · ⏳ ${g} pending`, 'ok');
  await sleep(500);
  setStep(3,'done');

  setStep(4,'active');
  log('📦 Calculating order-level fulfillment recommendation…','info');
  await sleep(600);
  renderResults(true);
  allDone();
  log('✅ Done. See dashboard for fulfill / hold decision.','ok');
  $('#runBtn').textContent="✓ Matching Complete";
}

function buildScanCards(){
  const grid=$('#scanGrid'); grid.innerHTML="";
  for(const [key,s] of Object.entries(SUPPLIERS)){
    const items=ORDER.filter(i=>i.sup===key);
    const ord=items.reduce((a,i)=>a+i.ordered,0);
    const el=document.createElement('div');
    el.className='sup-card'; el.id='sup-'+key;
    el.innerHTML=`
      <div class="nm">${s.emoji} ${s.name.split('·')[0].trim()} <span class="hub" style="margin-left:auto">${s.hub}</span></div>
      <div class="meta">${s.name.split('·')[1].trim()} — ${items.length} SKUs / ${ord} units</div>
      <div class="prog"><i></i></div>
      <div class="st">scanning… 0 / ${ord} units</div>`;
    grid.appendChild(el);
  }
}
async function scanSupplier(key){
  const s=SUPPLIERS[key];
  const items=ORDER.filter(i=>i.sup===key);
  const ord=items.reduce((a,i)=>a+i.ordered,0);
  const rec=items.reduce((a,i)=>a+i.received,0);
  const card=$('#sup-'+key);
  const bar=card.querySelector('.prog i');
  const st=card.querySelector('.st');
  log(`📡 ${s.hub} — scanning inbound from ${s.name.split('·')[0].trim()}…`);
  await sleep(450);
  bar.style.width=(rec/ord*100)+"%";
  st.textContent=`scanned ${rec} / ${ord} units`;
  if(rec===ord){ st.innerHTML=`✅ <span style="color:#86efac">all ${ord} units received</span>`; bar.style.background="var(--green)"; log(`✓ ${s.name.split('·')[0].trim()} complete (${rec}/${ord})`,'ok'); }
  else { st.innerHTML=`⚠ <span style="color:#fcd34d">${rec} / ${ord} units — ${ord-rec} short / pending</span>`; bar.style.background="var(--amber)"; log(`⚠ ${s.name.split('·')[0].trim()} short: ${rec}/${ord} received`,'warn'); }
  await sleep(400);
}

function renderResults(matched){
  const area=$('#resultArea');
  const f=ORDER.filter(i=>statusOf(i)==='full');
  const p=ORDER.filter(i=>statusOf(i)==='partial');
  const g=ORDER.filter(i=>statusOf(i)==='pending');
  const totalUnits=ORDER.reduce((a,i)=>a+i.ordered,0);
  const recvUnits =ORDER.reduce((a,i)=>a+Math.min(i.received,i.ordered),0);
  const pct=Math.round(recvUnits/totalUnits*100);

  const fullyReady = (p.length===0 && g.length===0);

  let dash="";
  if(matched){
    dash=`
    <div class="kpis fadein">
      <div class="kpi green"><div class="lab">✅ Fulfillable now</div><div class="val">${f.length}</div><div class="sub">lines received in full</div><div class="bar"></div></div>
      <div class="kpi amber"><div class="lab">⚠ Partial</div><div class="val">${p.length}</div><div class="sub">missing quantity</div><div class="bar"></div></div>
      <div class="kpi slate"><div class="lab">⏳ Not received</div><div class="val">${g.length}</div><div class="sub">pending arrival / verify</div><div class="bar"></div></div>
      <div class="kpi brand"><div class="lab">📊 Order fill rate</div><div class="val">${pct}%</div><div class="sub">${recvUnits} / ${totalUnits} units in</div><div class="bar"></div></div>
    </div>

    <div class="reco ${fullyReady?'go':'hold'} fadein">
      <div class="em">${fullyReady?'🚀':'⏸️'}</div>
      <div>
        <h3>System Recommendation: ${fullyReady?'FULFILL — ship now':'HOLD / QUEUE order'}</h3>
        <p>${fullyReady
            ? 'All items for this order have been received. Dispatch immediately.'
            : `${p.length+g.length} of ${ORDER.length} lines are not yet complete. Ship-complete policy → hold the order, notify Amy, and auto-release when the remaining items arrive.`}</p>
      </div>
      <div class="act">
        <button class="act-btn ${fullyReady?'go':''}" ${fullyReady?'':'disabled'}>${fullyReady?'Dispatch':'Awaiting stock'}</button>
        ${fullyReady?'':'<button class="act-btn">Notify customer</button>'}
      </div>
    </div>

    <div class="filters fadein" id="filters">
      <div class="chip active" data-f="all">All <b style="margin-left:4px">${ORDER.length}</b></div>
      <div class="chip" data-f="full"><span class="c" style="background:#22c55e"></span>Confirmed ${f.length}</div>
      <div class="chip" data-f="partial"><span class="c" style="background:#f59e0b"></span>Partial ${p.length}</div>
      <div class="chip" data-f="pending"><span class="c" style="background:#64748b"></span>Not received ${g.length}</div>
    </div>`;
  }

  const head = matched ? 'Matching Result — line by line' : 'Order Lines (loaded — not yet matched)';
  const sub  = matched ? 'Received stock reconciled against each ordered item' : 'Click “Run AI Matching” to reconcile against received stock';

  let rows = ORDER.map((it,idx)=>{
    const stt = statusOf(it);
    const meta = STATUS[stt];
    const sup = SUPPLIERS[it.sup];
    const badge = matched
      ? `<span class="badge ${meta.badge}"><span class="dot"></span>${meta.label}</span>`
      : `<span class="badge b-slate"><span class="dot"></span>Queued</span>`;
    const qty = matched
      ? `<span class="qty">${Math.min(it.received,it.ordered)}<small> / ${it.ordered}</small></span>${it.received>it.ordered?' <small style="color:#86efac">(+'+(it.received-it.ordered)+')</small>':''}`
      : `<span class="qty">${it.ordered}</span>`;
    let action='';
    if(matched){
      if(stt==='full') action=`<button class="act-btn go">Fulfill</button>`;
      else if(stt==='partial') action=`<button class="act-btn wait">Ship partial?</button>`;
      else action=`<button class="act-btn wait" disabled>Hold</button>`;
    } else action='—';
    const flags=[];
    if(it.verify) flags.push('🔎 verify');
    if(it.note) flags.push('📝 '+it.note);
    const flagHtml = flags.length?`<small style="color:#f3c267"> · ${flags.join(' · ')}</small>`:'';
    return `<tr data-status="${stt}">
      <td><span class="code">${it.code}</span><div class="sup" style="margin-top:4px">Inv ${it.inv}</div></td>
      <td class="desc"><b>${it.en}</b><small>${it.cn}${flagHtml}</small></td>
      <td><div class="sup">${sup.emoji} ${sup.name.split('·')[0].trim()}</div><span class="hub">${sup.hub}</span></td>
      <td>${qty}</td>
      <td>${RM(it.price*it.ordered)}</td>
      <td>${badge}</td>
      <td>${action}</td>
    </tr>`;
  }).join('');

  area.innerHTML = `
    ${dash}
    <div class="card fadein">
      <div class="hd"><span class="ic">${matched?'🧮':'📋'}</span>
        <div><h3>${head}</h3><small>${sub}</small></div>
      </div>
      <div class="bd">
        <div class="tablewrap">
          <table>
            <thead><tr>
              <th>Item</th><th>Description</th><th>Supplier / Hub</th>
              <th>Recv / Ord</th><th>Line value</th><th>Status</th><th>Action</th>
            </tr></thead>
            <tbody id="tbody">${rows}</tbody>
          </table>
        </div>
        ${matched?`<div class="legend">
          <span><span class="dot" style="width:8px;height:8px;background:#22c55e"></span> Confirmed = received in full → ready to ship</span>
          <span><span class="dot" style="width:8px;height:8px;background:#f59e0b"></span> Partial = some units missing</span>
          <span><span class="dot" style="width:8px;height:8px;background:#64748b"></span> Not received = pending arrival / needs verify</span>
        </div>`:''}
      </div>
    </div>`;

  if(matched) wireFilters();
}

function wireFilters(){
  const chips=[...document.querySelectorAll('#filters .chip')];
  chips.forEach(c=>c.addEventListener('click',()=>{
    chips.forEach(x=>x.classList.remove('active'));
    c.classList.add('active');
    const f=c.dataset.f;
    [...document.querySelectorAll('#tbody tr')].forEach(tr=>{
      tr.style.display = (f==='all'||tr.dataset.status===f)?'':'none';
    });
  }));
  document.querySelectorAll('.act-btn.go').forEach(b=>{
    if(b.textContent==='Fulfill') b.addEventListener('click',()=>{b.textContent='✓ Queued';b.disabled=true;});
  });
}
</script>

<!-- ============================== TOUR SCRIPT ============================== -->
<script>
(function(){
  var timed = [5000, 6000, 6800, 7000, 6000, 6500];
  var starts = []; var c = 0;
  for (var i=0;i<timed.length;i++){ starts.push(c); c += timed[i]; }
  var total = c;
  var outroHold = 800;

  var meta = [
    { kicker:"DAVID LAU · LOGISTIC MATCHING SYSTEM", title:"Smart fulfillment, fully automated",
      caption:"An AI engine that turns raw customer orders into ship-ready decisions — from intake all the way to dispatch." },
    { kicker:"THE PROBLEM", title:"The manual bottleneck",
      caption:"Orders were reconciled by hand against 50+ printed lists at the K.K. and K.L. hubs — slow, error-prone, and blind to what could actually ship." },
    { kicker:"STEP 1 · INTAKE & EXTRACTION", title:"From a Messenger chat to clean data",
      caption:"Customer order screenshots are OCR-extracted into structured line items, with each line auto-assigned to its supplier and receiving hub." },
    { kicker:"STEP 2 · INBOUND RECEIVING", title:"Scanned in as it arrives",
      caption:"Suppliers ship to the hubs and every box is barcode-scanned, reconciling physical stock against the digital order in real time." },
    { kicker:"STEP 3 · SMART MATCHING", title:"Received stock, meet ordered lines",
      caption:"The engine matches what physically arrived against every ordered line — flagging each as confirmed, partial, or still pending." },
    { kicker:"STEP 4 · OPTIMIZED OUTPUT", title:"Fulfill or hold — decided instantly",
      caption:"A live fill-rate dashboard plus a clear Fulfill / Hold recommendation for the whole order, with one click to dispatch or notify." }
  ];

  var stages = [
    '<div style="position:relative;width:200px;height:200px;display:grid;place-items:center;margin:0 auto">'
    + '<div style="position:absolute;inset:0;border-radius:50%;border:1px solid rgba(99,102,241,.4);animation:glowPulse 2.6s ease-in-out infinite"></div>'
    + '<div style="position:absolute;inset:30px;border-radius:50%;border:1px solid rgba(59,130,246,.45);animation:glowPulse 2.6s .5s ease-in-out infinite"></div>'
    + '<div style="width:108px;height:108px;border-radius:30px;background:linear-gradient(135deg,#3b82f6,#6366f1);display:grid;place-items:center;font-size:56px;box-shadow:0 16px 40px rgba(59,130,246,.5);animation:floaty 3.4s ease-in-out infinite">📦</div>'
    + '</div>',
    '<div style="display:flex;flex-direction:column;align-items:center;gap:18px">'
    + '<div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center">'
    + '<div style="background:#1c2330;border:1px solid #283042;border-radius:13px;padding:14px 18px;font-size:14px;font-weight:600;display:flex;align-items:center;gap:9px">📋 50+ printed lists</div>'
    + '<div style="background:#1c2330;border:1px solid #283042;border-radius:13px;padding:14px 18px;font-size:14px;font-weight:600;display:flex;align-items:center;gap:9px">✍️ Hand-checked at the hub</div>'
    + '<div style="background:#1c2330;border:1px solid #283042;border-radius:13px;padding:14px 18px;font-size:14px;font-weight:600;display:flex;align-items:center;gap:9px">⏱️ Hours of delay</div>'
    + '</div>'
    + '<div style="display:flex;align-items:center;gap:11px;background:linear-gradient(120deg,rgba(239,68,68,.14),transparent);border:1px solid rgba(239,68,68,.42);border-radius:13px;padding:14px 20px">'
    + '<span style="font-size:22px">⚠️</span><span style="font-size:14px;font-weight:600;color:#fca5a5">No real-time view of what can actually ship</span>'
    + '</div></div>',
    '<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;justify-content:center">'
    + '<div style="background:linear-gradient(135deg,#3b82f6,#6366f1);color:#fff;border-radius:16px 16px 16px 4px;padding:14px 17px;font-size:13px;font-weight:600;text-align:left;max-width:170px;box-shadow:0 8px 20px rgba(59,130,246,.3)">Amy · Messenger<div style="font-size:11px;opacity:.85;margin-top:4px;font-weight:500">📷 2 invoice screenshots</div></div>'
    + '<span style="font-size:20px;color:#5d6b7e">&#10141;</span>'
    + '<div style="background:#1c2330;border:1px solid #283042;border-radius:13px;padding:14px 16px;font-size:13px"><div style="font-size:22px;margin-bottom:5px">📄</div><b>OCR Extract</b><div style="font-size:11px;color:#8b97a8;margin-top:3px">Inv 19023 · 19697</div></div>'
    + '<span style="font-size:20px;color:#5d6b7e">&#10141;</span>'
    + '<div style="display:flex;flex-direction:column;gap:7px;text-align:left">'
    + '<div style="display:flex;align-items:center;gap:8px;background:#161b22;border:1px solid #283042;border-radius:9px;padding:8px 11px;font-size:11.5px"><span style="font-family:Consolas,monospace;color:#9fb4cf;background:#1c2330;padding:1px 6px;border-radius:5px">E10C</span> Handheld Fan</div>'
    + '<div style="display:flex;align-items:center;gap:8px;background:#161b22;border:1px solid #283042;border-radius:9px;padding:8px 11px;font-size:11.5px"><span style="font-family:Consolas,monospace;color:#9fb4cf;background:#1c2330;padding:1px 6px;border-radius:5px">H16</span> Lingzhi Soup Pack</div>'
    + '<div style="display:flex;align-items:center;gap:8px;background:#161b22;border:1px solid #283042;border-radius:9px;padding:8px 11px;font-size:11.5px"><span style="font-family:Consolas,monospace;color:#9fb4cf;background:#1c2330;padding:1px 6px;border-radius:5px">R40</span> Shower Gel 800g</div>'
    + '</div></div>',
    '<div style="display:flex;gap:14px;flex-wrap:wrap;justify-content:center">'
    + '<div style="width:200px;background:#1c2330;border:1px solid #283042;border-radius:14px;padding:14px;text-align:left"><div style="font-size:13px;font-weight:700;display:flex;align-items:center;gap:7px">🔌 Supplier A <span style="margin-left:auto;font-size:10px;color:#8b97a8;background:#161b22;border:1px solid #283042;padding:2px 7px;border-radius:6px">K.K.</span></div><div style="height:7px;border-radius:6px;background:#283042;margin-top:12px;overflow:hidden"><div style="height:100%;width:100%;background:#22c55e"></div></div><div style="font-size:10.5px;color:#86efac;margin-top:7px">✅ all units received</div></div>'
    + '<div style="width:200px;background:#1c2330;border:1px solid #283042;border-radius:14px;padding:14px;text-align:left"><div style="font-size:13px;font-weight:700;display:flex;align-items:center;gap:7px">🍲 Supplier B <span style="margin-left:auto;font-size:10px;color:#8b97a8;background:#161b22;border:1px solid #283042;padding:2px 7px;border-radius:6px">K.L.</span></div><div style="height:7px;border-radius:6px;background:#283042;margin-top:12px;overflow:hidden"><div style="height:100%;width:55%;background:#f59e0b"></div></div><div style="font-size:10.5px;color:#fcd34d;margin-top:7px">⚠ partial — units short</div></div>'
    + '<div style="width:200px;background:#1c2330;border:1px solid #283042;border-radius:14px;padding:14px;text-align:left"><div style="font-size:13px;font-weight:700;display:flex;align-items:center;gap:7px">🧴 Supplier C <span style="margin-left:auto;font-size:10px;color:#8b97a8;background:#161b22;border:1px solid #283042;padding:2px 7px;border-radius:6px">K.K.</span></div><div style="height:7px;border-radius:6px;background:#283042;margin-top:12px;overflow:hidden"><div style="height:100%;width:30%;background:#64748b"></div></div><div style="font-size:10.5px;color:#8b97a8;margin-top:7px">⏳ awaiting arrival</div></div>'
    + '</div>',
    '<div style="display:flex;flex-direction:column;gap:8px;width:100%;max-width:520px;margin:0 auto">'
    + '<div style="display:flex;align-items:center;gap:12px;background:#161b22;border:1px solid #283042;border-radius:11px;padding:11px 15px"><span style="font-family:Consolas,monospace;font-size:11.5px;color:#9fb4cf;background:#1c2330;padding:2px 8px;border-radius:6px">E10C</span><span style="font-size:13px;flex:1;text-align:left">Handheld Fan</span><span style="font-size:11px;font-weight:700;color:#86efac;background:rgba(34,197,94,.12);border:1px solid rgba(34,197,94,.4);padding:4px 11px;border-radius:999px">● Confirmed</span></div>'
    + '<div style="display:flex;align-items:center;gap:12px;background:#161b22;border:1px solid #283042;border-radius:11px;padding:11px 15px"><span style="font-family:Consolas,monospace;font-size:11.5px;color:#9fb4cf;background:#1c2330;padding:2px 8px;border-radius:6px">H20</span><span style="font-size:13px;flex:1;text-align:left">Five-Finger Peach Soup</span><span style="font-size:11px;font-weight:700;color:#fcd34d;background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.4);padding:4px 11px;border-radius:999px">● Partial</span></div>'
    + '<div style="display:flex;align-items:center;gap:12px;background:#161b22;border:1px solid #283042;border-radius:11px;padding:11px 15px"><span style="font-family:Consolas,monospace;font-size:11.5px;color:#9fb4cf;background:#1c2330;padding:2px 8px;border-radius:6px">R35</span><span style="font-size:13px;flex:1;text-align:left">Fabric Softener ×5</span><span style="font-size:11px;font-weight:700;color:#86efac;background:rgba(34,197,94,.12);border:1px solid rgba(34,197,94,.4);padding:4px 11px;border-radius:999px">● Confirmed</span></div>'
    + '<div style="display:flex;align-items:center;gap:12px;background:#161b22;border:1px solid #283042;border-radius:11px;padding:11px 15px"><span style="font-family:Consolas,monospace;font-size:11.5px;color:#9fb4cf;background:#1c2330;padding:2px 8px;border-radius:6px">R42</span><span style="font-size:13px;flex:1;text-align:left">Sandalwood Shower Gel</span><span style="font-size:11px;font-weight:700;color:#cbd5e1;background:rgba(100,116,139,.14);border:1px solid rgba(100,116,139,.4);padding:4px 11px;border-radius:999px">● To confirm</span></div>'
    + '</div>',
    '<div style="display:flex;flex-direction:column;gap:14px;width:100%;max-width:640px;margin:0 auto">'
    + '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:11px">'
    + '<div style="background:#161b22;border:1px solid #283042;border-radius:13px;padding:13px;text-align:left;position:relative;overflow:hidden"><div style="font-size:10.5px;color:#8b97a8">✅ Fulfillable</div><div style="font-size:27px;font-weight:800;color:#22c55e;margin-top:5px">10</div><div style="position:absolute;left:0;bottom:0;height:3px;width:100%;background:#22c55e"></div></div>'
    + '<div style="background:#161b22;border:1px solid #283042;border-radius:13px;padding:13px;text-align:left;position:relative;overflow:hidden"><div style="font-size:10.5px;color:#8b97a8">⚠ Partial</div><div style="font-size:27px;font-weight:800;color:#f59e0b;margin-top:5px">1</div><div style="position:absolute;left:0;bottom:0;height:3px;width:100%;background:#f59e0b"></div></div>'
    + '<div style="background:#161b22;border:1px solid #283042;border-radius:13px;padding:13px;text-align:left;position:relative;overflow:hidden"><div style="font-size:10.5px;color:#8b97a8">⏳ Not in</div><div style="font-size:27px;font-weight:800;color:#93a3b8;margin-top:5px">4</div><div style="position:absolute;left:0;bottom:0;height:3px;width:100%;background:#64748b"></div></div>'
    + '<div style="background:#161b22;border:1px solid #283042;border-radius:13px;padding:13px;text-align:left;position:relative;overflow:hidden"><div style="font-size:10.5px;color:#8b97a8">📊 Fill rate</div><div style="font-size:27px;font-weight:800;color:#7fb4ff;margin-top:5px">67%</div><div style="position:absolute;left:0;bottom:0;height:3px;width:100%;background:#3b82f6"></div></div>'
    + '</div>'
    + '<div style="display:flex;align-items:center;gap:14px;background:linear-gradient(120deg,rgba(245,158,11,.14),transparent);border:1px solid rgba(245,158,11,.45);border-radius:14px;padding:15px 18px;text-align:left"><span style="font-size:28px">⏸️</span><div><div style="font-size:15px;font-weight:700">Recommendation: HOLD / QUEUE</div><div style="font-size:12px;color:#8b97a8;margin-top:2px">Ship-complete policy → hold, notify customer, auto-release when stock arrives.</div></div></div>'
    + '</div>'
  ];

  var outroHTML =
    '<div style="display:flex;flex-direction:column;align-items:center;gap:22px">'
    + '<div style="width:84px;height:84px;border-radius:22px;background:linear-gradient(135deg,#3b82f6,#6366f1);display:grid;place-items:center;font-size:42px;box-shadow:0 12px 34px rgba(59,130,246,.5)">🛒</div>'
    + '<div><div class="tk-kicker" style="margin-bottom:10px">YOU\'RE READY</div>'
    + '<h2 class="tk-outro-h">See it work, live.</h2>'
    + '<p class="tk-outro-p">Run the full order-to-fulfillment flow yourself — upload the order, then watch the engine match and decide.</p></div>'
    + '<div class="tk-actions">'
    + '<button onclick="showDemo()" style="border:0;cursor:pointer;font-weight:800;font-size:15.5px;color:#fff;background:linear-gradient(135deg,#3b82f6,#6366f1);padding:15px 30px;border-radius:14px;box-shadow:0 10px 26px rgba(59,130,246,.45);display:flex;align-items:center;gap:10px">Enter the Demo <span style="font-size:17px">→</span></button>'
    + '<button id="t-replay2" style="appearance:none;border:1px solid #283042;background:transparent;color:#e6edf3;font-weight:700;font-size:14px;padding:15px 20px;border-radius:14px;cursor:pointer">&#8634; Replay tour</button>'
    + '</div></div>';

  var stageEl = document.getElementById('t-stage');
  var counterEl = document.getElementById('ph-counter');
  var playBtn = document.getElementById('ph-play');

  var base = 0, anchor = performance.now(), playing = true, cur = 0, rendered = -1;
  var speed = 1, loop = false;

  function rawElapsed(){ return playing ? base + (performance.now()-anchor)*speed : base; }
  function elapsedNow(){ var e = rawElapsed(); if(e<0)e=0; if(e>total+outroHold)e=total+outroHold; return e; }
  function calcCur(){
    var e = elapsedNow();
    if(e>=total) return timed.length;
    for(var i=0;i<timed.length;i++){ if(e<starts[i]+timed[i]) return i; }
    return timed.length;
  }
  function renderStage(idx){
    if(idx===rendered) return;
    rendered = idx;
    if(idx===timed.length){
      stageEl.innerHTML = '<div class="stage-anim">'+outroHTML+'</div>';
      var r2 = document.getElementById('t-replay2');
      if(r2) r2.onclick = replay;
      return;
    }
    var m = meta[idx];
    stageEl.innerHTML = '<div class="stage-anim" style="display:flex;flex-direction:column;align-items:center">'
      + '<div class="tk-kicker">'+m.kicker+'</div>'
      + '<h2 class="tk-title">'+m.title+'</h2>'
      + '<div class="tk-stagebox">'+stages[idx]+'</div>'
      + '<p class="tk-caption">'+m.caption+'</p>'
      + '</div>';
  }
  function updateChrome(){
    var e = elapsedNow();
    for(var i=0;i<timed.length;i++){
      var f = document.getElementById('ph-fill-'+i);
      if(f){ var frac = Math.max(0,Math.min(1,(e-starts[i])/timed[i])); f.style.width = (frac*100)+'%'; }
    }
    var k = calcCur();
    counterEl.textContent = e>=total ? 'Tour complete' : ('0'+(k+1)+' / 06');
    playBtn.innerHTML = playing ? '&#10074;&#10074;' : '&#9654;';
  }
  function tick(){
    var e = rawElapsed();
    if(loop && e>=total){ base=0; anchor=performance.now(); }
    else if(e>=total+outroHold){ base=total+outroHold; playing=false; }
    updateChrome();
    var k = calcCur();
    if(k!==cur){ cur=k; renderStage(k); }
  }
  function seekTo(i){ base = starts[i]+1; anchor=performance.now(); playing=true; cur=i; renderStage(i); updateChrome(); }
  function togglePlay(){
    if(playing){ base=elapsedNow(); playing=false; }
    else { anchor=performance.now(); playing=true; }
    updateChrome();
  }
  function replay(){ base=0; anchor=performance.now(); playing=true; cur=0; renderStage(0); updateChrome(); }
  window.replayTour = replay;

  playBtn.onclick = togglePlay;
  document.getElementById('ph-replay').onclick = replay;
  var seekEls = document.querySelectorAll('[data-seek]');
  for(var s=0;s<seekEls.length;s++){
    (function(el){ el.onclick = function(){ seekTo(parseInt(el.getAttribute('data-seek'),10)); }; })(seekEls[s]);
  }

  renderStage(0);
  updateChrome();
  setInterval(tick, 50);
})();
</script>

<!-- ============================== NAVIGATION ============================== -->
<script>
  // Resize the embedding iframe to fit the currently visible view so the page
  // is never clipped and has no dead space — works on phone, tablet & desktop.
  function fitFrame(){
    try{
      if(!window.frameElement) return;
      var tour=document.getElementById('tourView');
      var demo=document.getElementById('demoView');
      var active=(tour.style.display==='none')?demo:tour;
      var h=Math.max(active.scrollHeight, active.offsetHeight,
                     document.body.scrollHeight);
      window.frameElement.style.height=(h+6)+'px';
    }catch(e){}
  }
  function showDemo(){
    document.getElementById('tourView').style.display='none';
    document.getElementById('demoView').style.display='block';
    fitFrame();
    try{ window.scrollTo(0,0); }catch(e){}
  }
  function showTour(){
    document.getElementById('demoView').style.display='none';
    document.getElementById('tourView').style.display='flex';
    if(window.replayTour) window.replayTour();
    fitFrame();
    try{ window.scrollTo(0,0); }catch(e){}
  }
  window.addEventListener('resize', fitFrame);
  setInterval(fitFrame, 400);
  setTimeout(fitFrame, 120);
</script>

</body>
</html>
"""

# A tall frame so the demo (after matching) renders fully; the tour centres
# itself within the viewport, and scrolling=True covers any overflow.
components.html(PAGE_HTML, height=760, scrolling=True)
