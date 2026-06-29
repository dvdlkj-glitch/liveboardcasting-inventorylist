"""
Ulive Smart Fulfillment — Streamlit deployment
================================================
Animated intro tour (top) then a REAL upload-and-match demo:
  • Upload 1 — Customer Orders  (orders_import.xlsx, built from the slist PDFs)
  • Upload 2 — Stock Received   (stock_import.xlsx, built from China Stock Listing)
The engine matches every ordered line to received stock (item code first, then
fuzzy product-name) and produces the confirmed / partial / not-received
breakdown, fill rate and a Fulfill / Hold recommendation.

Assets next to this file:  tour_hero.html, theme_style.html,
                           orders_import.xlsx, stock_import.xlsx (sample)

Run:     pip install -r requirements.txt && streamlit run streamlit_app.py
Deploy:  push this folder to GitHub, point Streamlit Cloud at streamlit_app.py
"""
import os, re
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
def _asset(n):
    try:
        with open(os.path.join(BASE, n), encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""
TOUR_HTML = _asset("tour_hero.html")
THEME     = _asset("theme_style.html")

st.set_page_config(page_title="Ulive Smart Fulfillment", page_icon="📦",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
  .block-container{padding:0.4rem 0.8rem 2rem !important;max-width:1200px}
  header[data-testid="stHeader"]{display:none}
  #MainMenu,footer{visibility:hidden}
  section[data-testid="stSidebar"]{display:none}
  .stApp{background:#0d1117;color:#e6edf3}
  h2,h3,p,label,.stMarkdown{color:#e6edf3 !important}
</style>
""", unsafe_allow_html=True)

# ===================== MATCHING ENGINE (code, then fuzzy name) =====================
BRANDS = ["sukgarden","蔬果园","xfrog","华大","牛蛙","图兰朵","turandot","中国珠宝","brokevin","虾哥"]
COLOR  = re.compile(r"\((?:[^)]*?(?:pink|black|brown|粉|黑|咖|白|蓝|red|blue)[^)]*?)\)", re.I)

def norm_code(c):
    return re.sub(r"[^A-Za-z0-9]", "", str(c or "")).upper()

def norm_name(s):
    s = str(s or "").lower()
    s = COLOR.sub(" ", s)
    for b in BRANDS:
        s = s.replace(b, " ")
    return re.sub(r"[^一-鿿a-z0-9]", "", s)

def cjk_bigrams(s):
    cj = re.findall(r"[一-鿿]", s)
    return set(a + b for a, b in zip(cj, cj[1:]))

def name_score(a, b):
    na, nb = norm_name(a), norm_name(b)
    if not na or not nb:
        return 0.0
    short, lng = (na, nb) if len(na) <= len(nb) else (nb, na)
    contain = 1.0 if short and short in lng else 0.0
    ba, bb = cjk_bigrams(a), cjk_bigrams(b)
    jac = len(ba & bb) / len(ba | bb) if (ba or bb) else 0.0
    ca, cb = set(re.findall(r"[一-鿿]", na)), set(re.findall(r"[一-鿿]", nb))
    charr = len(ca & cb) / len(ca) if ca else 0.0
    return max(contain, jac, 0.6 * charr + 0.4 * jac)

NAME_THRESHOLD = 0.34

def match_orders(orders, stock):
    by_code = {}
    for s in stock:
        c = norm_code(s.get("item_code"))
        if c:
            by_code.setdefault(c, s)
    results = []
    for o in orders:
        ordered = int(o.get("qty_ordered") or 0)
        oc = norm_code(o.get("item_code"))
        matched, how, score = None, "", 0.0
        if oc and oc in by_code:
            matched, how, score = by_code[oc], "code", 1.0
        else:
            best, bestsc = None, 0.0
            for s in stock:
                sc = name_score(o.get("description"), s.get("description"))
                if sc > bestsc:
                    best, bestsc = s, sc
            if best and bestsc >= NAME_THRESHOLD:
                matched, how, score = best, "name", round(bestsc, 2)
        received = int(matched.get("qty_received") or 0) if matched else 0
        avail = min(received, ordered) if matched else 0
        if matched and received >= ordered and received > 0:
            status = "full"
        elif matched and avail > 0:
            status = "partial"
        else:
            status = "pending"
        results.append({**o,
            "matched_code": matched.get("item_code") if matched else "",
            "matched_name": matched.get("description") if matched else "",
            "supplier": matched.get("supplier") if matched else "Unmatched / not in stock",
            "match_type": how, "match_score": score,
            "qty_received": received, "qty_avail": avail, "status": status})
    tot = sum(int(o.get("qty_ordered") or 0) for o in orders)
    got = sum(r["qty_avail"] for r in results)
    summary = {
        "lines": len(results),
        "full": sum(1 for r in results if r["status"] == "full"),
        "partial": sum(1 for r in results if r["status"] == "partial"),
        "pending": sum(1 for r in results if r["status"] == "pending"),
        "units_ordered": tot, "units_avail": got,
        "fill_rate": round(got / tot * 100) if tot else 0,
        "fully_ready": (sum(1 for r in results if r["status"] != "full") == 0 and len(results) > 0)}
    return results, summary

# ===================== READ UPLOADED IMPORT FILES =====================
def _nh(s):
    return re.sub(r"[^一-鿿a-z0-9]", "", str(s).lower())

def _find(cols, *subs):
    for c in cols:
        h = _nh(c)
        for sub in subs:
            if sub in h:
                return c
    return None

def _int(v):
    try:
        return int(float(v))
    except Exception:
        return 0

def _float(v):
    try:
        return float(v)
    except Exception:
        return 0.0

def read_orders(file):
    df = pd.read_excel(file).fillna("")
    cols = list(df.columns)
    cc = _find(cols, "itemcode", "code", "sku", "货号", "货品编码")
    cd = _find(cols, "description", "desc", "name", "品名", "名称", "商品名称")
    cq = _find(cols, "qtyordered", "orderqty", "ordered", "quantity", "qty", "订货数量", "采购", "数量")
    ci = _find(cols, "invoice", "订单")
    cu = _find(cols, "customer", "客户")
    cp = _find(cols, "unitprice", "price", "单价")
    out = []
    for _, r in df.iterrows():
        desc = str(r[cd]).strip() if cd else ""
        code = str(r[cc]).strip() if cc else ""
        if not desc and not code:
            continue
        out.append({"item_code": code, "description": desc,
                    "qty_ordered": _int(r[cq]) if cq else 1,
                    "invoice": str(r[ci]).strip() if ci else "",
                    "customer": str(r[cu]).strip() if cu else "",
                    "unit_price": _float(r[cp]) if cp else 0.0})
    return out

def read_stock(file):
    df = pd.read_excel(file).fillna("")
    cols = list(df.columns)
    cc = _find(cols, "itemcode", "code", "sku", "货号", "货品编码", "序号")
    cd = _find(cols, "description", "desc", "name", "品名", "名称", "商品名称")
    cq = _find(cols, "qtyreceived", "received", "received", "qty", "数量", "采购", "订货数量")
    cs = _find(cols, "supplier", "品牌", "分类")
    out = []
    for _, r in df.iterrows():
        desc = str(r[cd]).strip() if cd else ""
        code = str(r[cc]).strip() if cc else ""
        if not desc and not code:
            continue
        out.append({"item_code": code, "description": desc,
                    "qty_received": _int(r[cq]) if cq else 0,
                    "supplier": str(r[cs]).strip() if cs else "Stock"})
    return out

# ===================== RENDER DARK DASHBOARD =====================
def esc(x):
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

BADGE = {"full": ("b-green", "Confirmed"), "partial": ("b-amber", "Partial"),
         "pending": ("b-slate", "Not received")}

def render_dashboard(results, s, meta):
    ready = s["fully_ready"]
    # supplier receiving cards
    groups = {}
    for r in results:
        g = groups.setdefault(r["supplier"], {"ord": 0, "avail": 0, "lines": 0})
        g["ord"] += int(r["qty_ordered"]); g["avail"] += int(r["qty_avail"]); g["lines"] += 1
    cards = ""
    for sup, g in sorted(groups.items(), key=lambda kv: -kv[1]["ord"]):
        pct = round(g["avail"] / g["ord"] * 100) if g["ord"] else 0
        col = "#22c55e" if pct >= 100 else ("#f59e0b" if pct > 0 else "#64748b")
        st_txt = ("✅ all received" if pct >= 100 else
                  ("⚠ partial — " + str(g["ord"] - g["avail"]) + " short" if pct > 0 else "⏳ not in stock"))
        cards += ('<div class="sup-card"><div class="nm">' + esc(sup) +
                  '<span class="hub" style="margin-left:auto">' + str(g["lines"]) + ' lines</span></div>'
                  '<div class="meta">' + str(g["avail"]) + ' / ' + str(g["ord"]) + ' units in</div>'
                  '<div class="prog"><i style="width:' + str(min(pct,100)) + '%;background:' + col + '"></i></div>'
                  '<div class="st" style="color:' + col + '">' + st_txt + '</div></div>')

    kpis = ('<div class="kpis fadein">'
        '<div class="kpi green"><div class="lab">✅ Confirmed</div><div class="val">' + str(s["full"]) + '</div><div class="sub">lines received in full</div><div class="bar"></div></div>'
        '<div class="kpi amber"><div class="lab">⚠ Partial</div><div class="val">' + str(s["partial"]) + '</div><div class="sub">missing quantity</div><div class="bar"></div></div>'
        '<div class="kpi slate"><div class="lab">⏳ Not received</div><div class="val">' + str(s["pending"]) + '</div><div class="sub">not in stock / pending</div><div class="bar"></div></div>'
        '<div class="kpi brand"><div class="lab">📊 Order fill rate</div><div class="val">' + str(s["fill_rate"]) + '%</div><div class="sub">' + str(s["units_avail"]) + ' / ' + str(s["units_ordered"]) + ' units</div><div class="bar"></div></div>'
        '</div>')

    if ready:
        reco = ('<div class="reco go fadein"><div class="em">🚀</div><div>'
                '<h3>System Recommendation: FULFILL — ship now</h3>'
                '<p>All ' + str(s["lines"]) + ' ordered lines have matching stock received. Dispatch immediately.</p>'
                '</div><div class="act"><button class="act-btn go">Dispatch</button></div></div>')
    else:
        notdone = s["partial"] + s["pending"]
        reco = ('<div class="reco hold fadein"><div class="em">⏸️</div><div>'
                '<h3>System Recommendation: HOLD / QUEUE order</h3>'
                '<p>' + str(notdone) + ' of ' + str(s["lines"]) + ' lines are not yet complete. '
                'Ship-complete policy → hold, notify the customer, and auto-release when the remaining stock arrives.</p>'
                '</div><div class="act"><button class="act-btn" disabled>Awaiting stock</button>'
                '<button class="act-btn">Notify customer</button></div></div>')

    chips = ('<div class="filters fadein">'
        '<div class="chip active" data-f="all">All <b style="margin-left:4px">' + str(s["lines"]) + '</b></div>'
        '<div class="chip" data-f="full"><span class="c" style="background:#22c55e"></span>Confirmed ' + str(s["full"]) + '</div>'
        '<div class="chip" data-f="partial"><span class="c" style="background:#f59e0b"></span>Partial ' + str(s["partial"]) + '</div>'
        '<div class="chip" data-f="pending"><span class="c" style="background:#64748b"></span>Not received ' + str(s["pending"]) + '</div>'
        '</div>')

    rows = ""
    for r in results:
        bcls, blab = BADGE[r["status"]]
        mt = r["match_type"]
        mtag = ('<span class="hub" style="border-color:rgba(59,130,246,.4);color:#7fb4ff">code</span>' if mt == "code"
                else ('<span class="hub" style="border-color:rgba(245,158,11,.4);color:#fcd34d">name ~' + str(r["match_score"]) + '</span>' if mt == "name"
                      else '<span class="hub">—</span>'))
        matched = (esc(r["matched_name"][:46]) if r["matched_name"] else '<span style="color:#5d6b7e">no stock match</span>')
        rows += ('<tr data-status="' + r["status"] + '">'
            '<td><span class="code">' + esc(r["item_code"] or "—") + '</span><div class="sup" style="margin-top:4px">' + esc(r.get("invoice","")) + '</div></td>'
            '<td class="desc"><b>' + esc(r["description"][:52]) + '</b><small>' + esc(r["supplier"]) + ' ' + '</small></td>'
            '<td>' + mtag + '</td>'
            '<td class="desc"><small>' + matched + '</small></td>'
            '<td><span class="qty">' + str(r["qty_avail"]) + '<small> / ' + str(r["qty_ordered"]) + '</small></span></td>'
            '<td><span class="badge ' + bcls + '"><span class="dot"></span>' + blab + '</span></td>'
            '</tr>')

    pills = ('<span class="pill">Invoices: <b>' + str(meta["invoices"]) + '</b></span>'
             '<span class="pill">Customers: <b>' + str(meta["customers"]) + '</b></span>'
             '<span class="pill">Suppliers: <b>' + str(meta["suppliers"]) + '</b></span>'
             '<span class="pill">Mode: <b>AI Automated</b></span>')

    filter_js = ("<script>(function(){var chips=[].slice.call(document.querySelectorAll('.chip'));"
        "chips.forEach(function(c){c.addEventListener('click',function(){"
        "chips.forEach(function(x){x.classList.remove('active')});c.classList.add('active');"
        "var f=c.getAttribute('data-f');"
        "[].slice.call(document.querySelectorAll('#tbody tr')).forEach(function(tr){"
        "tr.style.display=(f==='all'||tr.getAttribute('data-status')===f)?'':'none';});});});})();</script>")

    body = ('<div class="wrap">'
        '<header class="top"><div class="logo">🛒</div>'
        '<div class="htext"><h1>Ulive Smart Fulfillment</h1>'
        '<p>AI Order ↔ Stock Matching Engine · Live result</p></div>'
        '<div class="tag">' + pills + '</div></header>'
        + kpis + reco +
        '<div class="card" style="margin-bottom:18px"><div class="hd"><span class="ic">🏭</span>'
        '<div><h3>Receiving by supplier</h3><small>Units received vs ordered, per matched supplier</small></div></div>'
        '<div class="bd"><div class="scan-grid">' + cards + '</div></div></div>'
        + chips +
        '<div class="card"><div class="hd"><span class="ic">🧮</span>'
        '<div><h3>Matching result — line by line</h3><small>Every ordered line reconciled against received stock</small></div></div>'
        '<div class="bd"><div class="tablewrap" style="max-height:560px">'
        '<table><thead><tr><th>Item / Inv</th><th>Ordered description</th><th>Match</th>'
        '<th>Matched stock</th><th>Recv / Ord</th><th>Status</th></tr></thead>'
        '<tbody id="tbody">' + rows + '</tbody></table></div>'
        '<div class="legend">'
        '<span><span class="dot" style="width:8px;height:8px;background:#22c55e"></span> Confirmed = stock received ≥ ordered</span>'
        '<span><span class="dot" style="width:8px;height:8px;background:#f59e0b"></span> Partial = some units short</span>'
        '<span><span class="dot" style="width:8px;height:8px;background:#64748b"></span> Not received = no stock match</span>'
        '</div></div></div></div>')

    return ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0"/>'
            + THEME + '</head><body>' + body + filter_js + '</body></html>')

# ===================== PAGE =====================
components.html(TOUR_HTML, height=700, scrolling=False)
st.markdown('<div id="demo-anchor"></div>', unsafe_allow_html=True)
st.markdown("## 🛒 Live Demo — AI Order ↔ Stock Matching")
st.caption("Upload the two import files (Customer Orders + Stock Received), or tick the sample box, then run. "
           "The engine matches by item code first, then by fuzzy product name.")

c1, c2 = st.columns(2)
with c1:
    of = st.file_uploader("1 · Customer Orders  (.xlsx)", type=["xlsx"], key="of")
with c2:
    sf = st.file_uploader("2 · Stock Received  (.xlsx)", type=["xlsx"], key="sf")

use_sample = st.checkbox("Use the included sample data (parsed from slist 1–3 PDFs + China Stock Listing)")
run = st.button("▶  Run AI Matching", type="primary", use_container_width=True)

orders = stock = None
err = ""
try:
    if use_sample:
        so, ss = os.path.join(BASE, "orders_import.xlsx"), os.path.join(BASE, "stock_import.xlsx")
        if os.path.exists(so) and os.path.exists(ss):
            orders, stock = read_orders(so), read_stock(ss)
        else:
            err = "Sample files (orders_import.xlsx / stock_import.xlsx) were not found next to the app."
    elif of is not None and sf is not None:
        orders, stock = read_orders(of), read_stock(sf)
except Exception as e:
    err = "Could not read the files: " + str(e)

if err:
    st.error(err)
elif (run or use_sample) and orders and stock:
    results, summary = match_orders(orders, stock)
    meta = {"invoices": len({o["invoice"] for o in orders if o.get("invoice")}),
            "customers": len({o["customer"] for o in orders if o.get("customer")}),
            "suppliers": len({s["supplier"] for s in stock if s.get("supplier")})}
    st.success("Matched %d order lines → %d confirmed · %d partial · %d not received · fill rate %d%%"
               % (summary["lines"], summary["full"], summary["partial"], summary["pending"], summary["fill_rate"]))
    components.html(render_dashboard(results, summary, meta), height=1340, scrolling=True)
elif run:
    st.info("Please upload BOTH files, or tick “Use the included sample data”, then press Run.")
else:
    st.info("⬆️  Upload Customer Orders + Stock Received (.xlsx), or tick the sample box, then press Run AI Matching.")
