"""
Homestead Site Plan Generator — Production Build
All fixes: PDF quality, session state, global currency,
custom trees, animated counter, house position, no overlaps.
"""

import streamlit as st
import io, math, time, random
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

from homestead_map import generate_visual

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Homestead Site Plan Generator",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
BMC_10_URL = "https://buymeacoffee.com/YOUR_USERNAME/e/YOUR_10_PRODUCT"
BMC_20_URL = "https://buymeacoffee.com/YOUR_USERNAME/e/YOUR_20_PRODUCT"

VALID_KEYS_BASIC = {"ACCESS_KEY_99_ALPHA", "ACCESS_KEY_PRO_2026", "UNLOCK_FULL_MAP_X1"}
VALID_KEYS_PRO   = {"FULL_REPORT_KEY_2026", "PRO_FULL_ACCESS_X2"}
ALL_KEYS         = VALID_KEYS_BASIC | VALID_KEYS_PRO

CURRENCY_SYMBOLS = {"USD $": "$", "EUR €": "€", "GBP £": "£",
                    "AUD A$": "A$", "CAD C$": "C$", "INR ₹": "₹"}

# Base costs in USD (1 acre reference)
BASE_COSTS_USD = [
    ("Perimeter fencing (chain-link)",   1_840, "Full boundary"),
    ("Drip irrigation system",           1_035, "Zones 1–3 full coverage"),
    ("Fruit tree saplings",                460, "Mixed species"),
    ("Borewell + solar pump",            1_380, "100 ft depth, 0.5 HP"),
    ("Overhead water tank (10,000 L)",     450, "PVC with stand"),
    ("Raised beds × 6",                    575, "Soil + growing mix"),
    ("Greenhouse / polytunnel",          1_265, "1,200 sq.ft., UV film"),
    ("Solar system (1 kW)",              1_610, "Panels + battery + pump"),
    ("Poultry pen + 30 birds",             505, "Pen + initial flock"),
    ("Compost units (3-bay)",              275, "Hot + vermi + biochar"),
    ("Swale & earthworks",                 690, "Contour trenching, JCB"),
    ("Bio-filter & plumbing",              450, "Greywater system"),
]

# Exchange rates (approx)
FX = {"USD $": 1.0, "EUR €": 0.92, "GBP £": 0.79,
      "AUD A$": 1.53, "CAD C$": 1.36, "INR ₹": 83.5}

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
for key in ("map_buf_bytes", "pdf_buf_bytes", "map_generated",
            "custom_trees", "counter_base"):
    if key not in st.session_state:
        st.session_state[key] = None if key != "custom_trees" else []
        if key == "map_generated":
            st.session_state[key] = False
        if key == "counter_base":
            st.session_state[key] = random.randint(487, 612)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def get_access(key: str) -> str:
    k = key.strip()
    if k in VALID_KEYS_PRO:   return "pro"
    if k in VALID_KEYS_BASIC: return "basic"
    return "free"

def fmt_cost(amount_usd: float, acres: float, sym: str, fx: float) -> str:
    v = amount_usd * acres * fx
    return f"{sym}{v:,.0f}"

def make_planting_df(total_sqft, z2_pct, default_trees, custom_trees, sym, fx):
    z2 = total_sqft * z2_pct / 100
    base = [
        ("Mango (Alphonso)",    "Large",  15, 80,  120, 0.65),
        ("Guava (Allahabad)",   "Large",  12, 40,  60,  0.30),
        ("Lemon / Sweet Lime",  "Medium", 10, 30,  50,  0.25),
        ("Papaya",              "Medium",  8, 25,  40,  0.15),
        ("Pomegranate",         "Medium", 12, 20,  35,  0.35),
        ("Banana (windbreak)",  "Small",   6, 15,  25,  0.20),
    ][:default_trees]

    for ct in custom_trees:
        base.append((ct["name"], ct["size"], ct["spacing"],
                     ct["yield_lo"], ct["yield_hi"], ct["price_usd"]))

    rows = []
    for name, size, spacing, ylo, yhi, price_usd in base:
        qty  = max(1, int(z2 / (spacing * spacing)))
        inc_lo = qty * ylo * price_usd * fx
        inc_hi = qty * yhi * price_usd * fx
        rows.append({
            "Species": name, "Size": size,
            "Spacing (ft)": spacing, "Qty": qty,
            "Yr 5 Yield": f"{ylo}–{yhi} kg/tree",
            "Est. Annual Income": f"{sym}{inc_lo:,.0f}–{sym}{inc_hi:,.0f}",
        })
    return pd.DataFrame(rows)

def make_cost_df(total_sqft, sym, fx):
    acres = total_sqft / 43560
    rows = []
    for item, usd, note in BASE_COSTS_USD:
        v = usd * acres * fx
        rows.append({"Item": item, f"Cost ({sym})": f"{sym}{v:,.0f}", "Notes": note})
    return pd.DataFrame(rows)

def make_water_fig():
    fig, ax = plt.subplots(figsize=(11, 6), facecolor='white')
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis('off')
    ax.set_title("Water Flow & Drainage System",
                 fontsize=13, fontweight='bold', pad=14, color='#0f2417')

    nodes = [
        (1.2, 4.2, "BOREWELL\n(N-E corner)",  "#AED6F1", "#1A5276"),
        (3.8, 5.0, "WATER TANK\n10,000 L",    "#378ADD", "#042C53"),
        (1.8, 2.0, "BIO-FILTER\n(reed bed)",  "#F0997B", "#712B13"),
        (5.5, 5.0, "ZONE 1\nKitchen Garden",  "#A9DFBF", "#0E6655"),
        (5.5, 3.2, "ZONE 2\nFood Forest",     "#97C459", "#27500A"),
        (5.5, 1.4, "ZONE 3\nPasture/Crops",   "#FAC775", "#633806"),
        (8.2, 2.2, "SWALE\n(recharge GW)",    "#B5D4F4", "#185FA5"),
        (3.8, 3.2, "HOUSE\n(greywater out)",  "#D6E4F0", "#1A5276"),
    ]
    for nx, ny, lbl, fc, ec in nodes:
        ax.add_patch(patches.FancyBboxPatch(
            (nx-0.85, ny-0.48), 1.7, 0.96,
            boxstyle="round,pad=0.12",
            facecolor=fc, edgecolor=ec, lw=1.5, zorder=3))
        ax.text(nx, ny+0.04, lbl, ha='center', va='center',
                fontsize=7.5, color=ec, fontweight='bold',
                fontfamily='monospace', zorder=4)

    arrs = [
        (2.05, 4.2,  2.95, 4.8,  "pump line",  "#1A5276"),
        (4.65, 5.0,  4.65, 5.0,  "",           "#1A5276"),
        (4.65, 5.0,  4.65, 3.44, "gravity",    "#1A5276"),
        (4.65, 3.2,  4.65, 1.88, "drip",       "#27AE60"),
        (4.65, 5.0,  4.65, 5.0,  "",           "#1A5276"),
        (2.65, 4.0,  3.1,  3.5,  "greywater",  "#E24B4A"),
        (2.65, 2.0,  4.65, 2.0,  "filtered",   "#27AE60"),
        (6.35, 1.5,  7.35, 1.9,  "overflow",   "#1A5276"),
    ]
    for x1,y1,x2,y2,lbl,col in arrs:
        if x1==x2 and y1==y2: continue
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='->', color=col, lw=1.4), zorder=5)
        if lbl:
            ax.text((x1+x2)/2+0.05, (y1+y2)/2+0.13, lbl,
                    fontsize=6.5, color='#5F5E5A',
                    ha='center', fontfamily='monospace')

    plt.tight_layout(pad=1.5)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200, bbox_inches='tight',
                facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf

# ─────────────────────────────────────────────
#  PDF GENERATOR  (fixed — no overlapping)
# ─────────────────────────────────────────────
def _pdf_table(ax, data, col_labels, bbox, hdr_color="#0f2417",
               alt_color="#f0fdf4", fs=8.5):
    """Draw a clean table with no overlap."""
    tbl = ax.table(cellText=data, colLabels=col_labels,
                   loc='upper left', bbox=bbox)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(fs)
    ncols = len(col_labels)
    nrows = len(data)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor('#dee2e6')
        cell.set_linewidth(0.5)
        cell.PAD = 0.06
        if r == 0:
            cell.set_facecolor(hdr_color)
            cell.get_text().set_color('white')
            cell.get_text().set_fontweight('bold')
        elif r % 2 == 0:
            cell.set_facecolor(alt_color)
        else:
            cell.set_facecolor('white')
        if r == nrows and c >= 0:
            cell.set_facecolor('#dcfce7')
            cell.get_text().set_fontweight('bold')
    return tbl


def generate_pdf(map_buf_bytes, project_name, total_sqft,
                 z0, z1, z2, z3, z4,
                 planting_df, cost_df, sym, fx):

    out = io.BytesIO()
    with PdfPages(out) as pdf:

        # ── PAGE 1: Cover ────────────────────
        fig = plt.figure(figsize=(8.27, 11.69), facecolor='#0f2417')
        ax  = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
        ax.add_patch(patches.Rectangle((0,0),1,1,
                     facecolor='#0f2417', transform=ax.transAxes))
        # green accent bar
        ax.add_patch(patches.Rectangle((0.12,0.42),0.76,0.003,
                     facecolor='#22c55e', transform=ax.transAxes))
        ax.text(0.5, 0.80, '🌿', fontsize=52, ha='center',
                va='center', transform=ax.transAxes, color='#22c55e')
        ax.text(0.5, 0.72, project_name.upper(),
                fontsize=20, ha='center', va='center',
                transform=ax.transAxes, color='#e8f5e9',
                fontweight='bold', fontfamily='monospace')
        ax.text(0.5, 0.65, 'HOMESTEAD SITE PLAN REPORT',
                fontsize=11, ha='center', va='center',
                transform=ax.transAxes, color='#81c784',
                fontfamily='monospace')
        ax.text(0.5, 0.58,
                f'Total Area: {total_sqft:,} sq.ft. = {total_sqft/43560:.2f} acres',
                fontsize=9.5, ha='center', va='center',
                transform=ax.transAxes, color='#4ade80',
                fontfamily='monospace')
        for i, (label, val) in enumerate([
            ('ZONES', '5 permaculture zones'),
            ('SCALE', '1:200 orthographic'),
            ('YEAR', '2026'),
        ]):
            ax.text(0.22 + i*0.28, 0.34, label, fontsize=7,
                    ha='center', va='center',
                    transform=ax.transAxes, color='#4b7a5c',
                    fontfamily='monospace')
            ax.text(0.22 + i*0.28, 0.29, val, fontsize=8.5,
                    ha='center', va='center',
                    transform=ax.transAxes, color='#81c784',
                    fontweight='bold', fontfamily='monospace')
        ax.text(0.5, 0.08,
                'Generated by Homestead Site Plan Generator  |  AI SITE ARCHITECT 2026',
                fontsize=7, ha='center', va='center',
                transform=ax.transAxes, color='#2d5a3d',
                fontfamily='monospace')
        pdf.savefig(fig, bbox_inches='tight', dpi=250)
        plt.close(fig)

        # ── PAGE 2: Site Map (landscape) ─────
        map_img = Image.open(io.BytesIO(map_buf_bytes))
        fig = plt.figure(figsize=(11.69, 8.27), facecolor='white')
        ax  = fig.add_axes([0.02, 0.06, 0.96, 0.86])
        ax.axis('off')
        ax.imshow(map_img, aspect='auto')
        fig.text(0.5, 0.96, f'{project_name} — Site Plan',
                 ha='center', fontsize=12, fontweight='bold',
                 color='#0f2417', fontfamily='monospace')
        fig.text(0.5, 0.02,
                 f'{total_sqft:,} sq.ft. = {total_sqft/43560:.2f} acres  |  Scale 1:200',
                 ha='center', fontsize=8, color='#6b7280',
                 fontfamily='monospace')
        pdf.savefig(fig, bbox_inches='tight', dpi=250)
        plt.close(fig)

        # ── PAGE 3a: Zone Calculations ───────
        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor='white')
        ax.axis('off')
        fig.text(0.5, 0.96, 'ZONE AREA CALCULATIONS',
                 ha='center', fontsize=14, fontweight='bold',
                 color='#0f2417', fontfamily='monospace')
        zones_data = [
            ['Zone 0', 'Residential',    f'{total_sqft*z0/100:,.0f}', f'{z0}%'],
            ['Zone 1', 'Kitchen Garden', f'{total_sqft*z1/100:,.0f}', f'{z1}%'],
            ['Zone 2', 'Food Forest',    f'{total_sqft*z2/100:,.0f}', f'{z2}%'],
            ['Zone 3', 'Pasture/Crops',  f'{total_sqft*z3/100:,.0f}', f'{z3}%'],
            ['Zone 4/5','Buffer/Fence',  f'{total_sqft*z4/100:,.0f}', f'{z4}%'],
            ['TOTAL',  '',               f'{total_sqft:,.0f}',         '100%'],
        ]
        _pdf_table(ax, zones_data, ['Zone','Description','Area (sq.ft.)','%'],
                   bbox=[0.05, 0.74, 0.90, 0.18])
        pdf.savefig(fig, bbox_inches='tight', dpi=250)
        plt.close(fig)

        # ── PAGE 3b: Planting Schedule ───────
        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor='white')
        ax.axis('off')
        fig.text(0.5, 0.96, 'PLANTING SCHEDULE — ZONE 2 FOOD FOREST',
                 ha='center', fontsize=13, fontweight='bold',
                 color='#0f2417', fontfamily='monospace')
        p_data = planting_df.values.tolist()
        p_cols = list(planting_df.columns)
        row_h  = 0.06
        tbl_h  = min(0.82, len(p_data) * row_h + 0.07)
        _pdf_table(ax, p_data, p_cols,
                   bbox=[0.02, 0.93 - tbl_h, 0.96, tbl_h],
                   hdr_color='#166534', alt_color='#f0fdf4', fs=8)
        pdf.savefig(fig, bbox_inches='tight', dpi=250)
        plt.close(fig)

        # ── PAGE 4: Cost Estimate ────────────
        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor='white')
        ax.axis('off')
        fig.text(0.5, 0.96, 'SETUP COST ESTIMATE',
                 ha='center', fontsize=14, fontweight='bold',
                 color='#0f2417', fontfamily='monospace')
        c_data = cost_df.values.tolist()
        c_cols = list(cost_df.columns)
        c_row_h = 0.055
        c_tbl_h = min(0.55, len(c_data) * c_row_h + 0.06)
        _pdf_table(ax, c_data, c_cols,
                   bbox=[0.02, 0.93 - c_tbl_h, 0.96, c_tbl_h],
                   hdr_color='#0f2417', alt_color='#fefce8', fs=8.5)

        # total
        acres = total_sqft / 43560
        total_cost = sum(v * acres * fx for _, v, _ in BASE_COSTS_USD)
        fig.text(0.5, 0.93 - c_tbl_h - 0.04,
                 f'Estimated Total: {sym}{total_cost:,.0f}  (adjust for your region)',
                 ha='center', fontsize=10, color='#166534',
                 fontweight='bold', fontfamily='monospace')

        # income table
        fig.text(0.5, 0.93 - c_tbl_h - 0.10,
                 'PROJECTED ANNUAL INCOME (Year 3+)',
                 ha='center', fontsize=12, fontweight='bold',
                 color='#0f2417', fontfamily='monospace')
        inc_data = [
            ['Fruit trees (mango + guava)', '600–900 kg',
             f'{sym}{600*fx:,.0f}–{sym}{900*fx:,.0f}'],
            ['Vegetables (zone 1)', 'Year-round',
             f'{sym}{400*fx:,.0f}–{sym}{600*fx:,.0f}'],
            ['Poultry (eggs + meat)', '8,000+ eggs/yr',
             f'{sym}{350*fx:,.0f}–{sym}{500*fx:,.0f}'],
            ['Fodder / crop sale', 'Seasonal',
             f'{sym}{250*fx:,.0f}–{sym}{400*fx:,.0f}'],
            ['TOTAL ESTIMATE', '',
             f'{sym}{1600*fx:,.0f}–{sym}{2400*fx:,.0f}/yr'],
        ]
        i_tbl_h = 0.28
        i_top   = 0.93 - c_tbl_h - 0.15
        _pdf_table(ax, inc_data, ['Source', 'Yield', 'Est. Annual Income'],
                   bbox=[0.02, i_top - i_tbl_h, 0.96, i_tbl_h],
                   hdr_color='#166534', alt_color='#f0fdf4', fs=9)
        pdf.savefig(fig, bbox_inches='tight', dpi=250)
        plt.close(fig)

        # ── PAGE 5: Water Flow (landscape) ───
        wf_buf = make_water_fig()
        wf_img = Image.open(wf_buf)
        fig = plt.figure(figsize=(11.69, 8.27), facecolor='white')
        ax  = fig.add_axes([0.02, 0.05, 0.96, 0.88])
        ax.axis('off')
        ax.imshow(wf_img, aspect='auto')
        pdf.savefig(fig, bbox_inches='tight', dpi=250)
        plt.close(fig)

    out.seek(0)
    return out.read()


# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; }

.hero {
    background: linear-gradient(135deg,#0f2417 0%,#1a3a24 60%,#0d3320 100%);
    border-radius:14px; padding:1.8rem 2.2rem; margin-bottom:1.2rem;
    border:1px solid #2d5a3d;
}
.hero h1 { color:#e8f5e9 !important; font-size:1.75rem !important;
            font-weight:600 !important; margin:0 0 0.3rem !important; }
.hero p  { color:#81c784; font-size:0.95rem; margin:0; }

.counter-badge {
    display:inline-flex; align-items:center; gap:8px;
    background:#ecfdf5; border:1.5px solid #86efac;
    border-radius:20px; padding:4px 14px; font-size:0.85rem;
    color:#166534; font-weight:600;
}
.counter-dot { width:8px; height:8px; border-radius:50%;
               background:#22c55e; display:inline-block;
               animation: pulse 1.5s infinite; }
@keyframes pulse {
    0%,100%{opacity:1;transform:scale(1)}
    50%{opacity:.4;transform:scale(1.4)}
}

.pricing-row { display:grid; grid-template-columns:1fr 1fr 1fr;
               gap:12px; margin:1rem 0; }
.price-card { border-radius:12px; padding:1.1rem; border:1.5px solid; }
.price-free  { background:#f9fafb; border-color:#e5e7eb; }
.price-basic { background:#f0fdf4; border-color:#86efac; }
.price-pro   { background:#ecfdf5; border-color:#34d399; }
.price-card h3 { margin:0 0 0.25rem; font-size:0.95rem; font-weight:600; }
.price-card .amount { font-size:1.7rem; font-weight:700; margin:0.25rem 0; }
.price-card ul { text-align:left; font-size:0.8rem; padding-left:1rem;
                 margin:0.5rem 0 0; color:#374151; }
.price-free h3   { color:#6b7280; }
.price-free .amount { color:#6b7280; }
.price-basic h3  { color:#166534; }
.price-basic .amount { color:#15803d; }
.price-pro h3    { color:#064e3b; }
.price-pro .amount   { color:#065f46; }

.cta-btn {
    display:inline-block; background:#16a34a; color:white !important;
    padding:0.6rem 1.4rem; border-radius:8px; font-weight:600;
    font-size:0.9rem; text-decoration:none !important; margin:0.25rem 0;
}
.cta-btn.secondary { background:#065f46; font-size:0.85rem; }
.cta-btn:hover { opacity:0.9; }

.testimonial { background:#f0fdf4; border-left:4px solid #22c55e;
               border-radius:0 10px 10px 0; padding:0.8rem 1rem;
               margin:0.4rem 0; font-size:0.85rem; color:#374151; }
.testimonial strong { color:#166534; display:block; margin-top:0.3rem;
                      font-size:0.8rem; }

.step { display:flex; gap:10px; align-items:flex-start;
        margin-bottom:0.6rem; font-size:0.88rem; }
.step-num { background:#166534; color:white; width:22px; height:22px;
            border-radius:50%; display:flex; align-items:center;
            justify-content:center; font-size:0.75rem; font-weight:600;
            flex-shrink:0; margin-top:2px; }

.stDownloadButton > button {
    background:#16a34a !important; color:white !important;
    border:none !important; font-weight:600 !important;
    border-radius:8px !important; width:100%;
}
.stDownloadButton > button:hover { background:#15803d !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LICENSE CHECK (URL param)
# ─────────────────────────────────────────────
params  = st.query_params
url_key = params.get("status", "").strip()
access  = get_access(url_key)

# ─────────────────────────────────────────────
#  HERO + ANIMATED COUNTER
# ─────────────────────────────────────────────
col_hero, col_counter = st.columns([3, 1])
with col_hero:
    st.markdown("""
    <div class="hero">
        <h1>🌿 Homestead Site Plan Generator</h1>
        <p>Professional permaculture blueprints in seconds — trusted by homesteaders worldwide</p>
    </div>""", unsafe_allow_html=True)
with col_counter:
    st.markdown(f"""
    <div style="height:100%;display:flex;align-items:center;justify-content:center">
    <div style="text-align:center;padding:1rem">
        <div style="font-size:0.75rem;color:#6b7280;margin-bottom:4px">LIVE USERS</div>
        <div id="counter" style="font-size:2.2rem;font-weight:700;color:#166534;
             font-family:'DM Mono',monospace">{st.session_state.counter_base}</div>
        <div class="counter-badge" style="margin-top:6px">
            <span class="counter-dot"></span> plans generated
        </div>
    </div></div>
    <script>
    (function(){{
        var el=document.getElementById('counter');
        if(!el)return;
        var base={st.session_state.counter_base};
        function tick(){{
            if(Math.random()<0.3){{
                base+=Math.floor(Math.random()*3)+1;
                el.textContent=base.toLocaleString();
            }}
            setTimeout(tick, 1800+Math.random()*2400);
        }}
        tick();
    }})();
    </script>""", unsafe_allow_html=True)
    st.session_state.counter_base += random.randint(0, 2)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:

    # access badge
    if access == "pro":
        st.success("🏆 Pro Access — Full report unlocked")
    elif access == "basic":
        st.success("✅ Basic Access — HD map unlocked")
    else:
        st.markdown("""<div style='background:#fff7ed;border:1.5px solid #fb923c;
            border-radius:10px;padding:0.8rem;font-size:0.85rem;'>
            🔒 <b>Free Preview</b> — Watermarked<br>
            <span style='color:#9a3412'>Unlock for HD + PDF</span>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Currency ──────────────────────────
    cur_label = st.selectbox("💱 Currency", list(CURRENCY_SYMBOLS.keys()), index=0)
    CUR_SYM = CURRENCY_SYMBOLS[cur_label]
    CUR_FX  = FX[cur_label]

    st.divider()

    # ── 1. Basic Info ─────────────────────
    st.subheader("1. Basic Info")
    project_name = st.text_input("Project Name", value="Green Valley Homestead")

    # Plot shape
    plot_shape = st.selectbox("Plot Shape", [
        "Rectangle", "L-Shape (missing NE corner)",
        "L-Shape (missing SW corner)", "Irregular (approx rectangle)"])

    col1, col2 = st.columns(2)
    with col1:
        length = st.number_input("Length (ft)", 50, 2000, 400, 10)
    with col2:
        width  = st.number_input("Width  (ft)", 50, 2000, 400, 10)

    if "L-Shape" in plot_shape:
        cut_pct = st.slider("Corner cut size (%)", 10, 40, 25, step=5)
        total_sqft = int(length * width * (1 - cut_pct/100))
    else:
        total_sqft = length * width
    total_acres = total_sqft / 43560
    st.info(f"📐 **{total_sqft:,} sq.ft** ≈ **{total_acres:.2f} acres**")

    # ── 2. Zone Sizes ─────────────────────
    st.subheader("2. Zone Sizes (%)")
    z0 = st.slider("Zone 0 — Residential",    5, 30, 10, 5)
    z1 = st.slider("Zone 1 — Kitchen Garden", 5, 30, 15, 5)
    z2 = st.slider("Zone 2 — Food Forest",   10, 50, 30, 5)
    z3 = st.slider("Zone 3 — Pasture/Crops", 10, 50, 35, 5)
    z4 = 100 - z0 - z1 - z2 - z3
    if z4 < 0:
        st.error(f"Total {z0+z1+z2+z3}% — reduce a slider.")
        z4 = 0
    else:
        st.success(f"Zone 4/5 Buffer: {z4}%")

    # ── 3. House Position ─────────────────
    st.subheader("3. House Position")
    house_pos = st.selectbox("Place house at", [
        "Top-Left (NW)", "Top-Right (NE)",
        "Bottom-Left (SW)", "Bottom-Right (SE)", "Top-Center"])
    st.caption("This changes where Zone 0 is drawn on the map.")

    # ── 4. Features ───────────────────────
    st.subheader("4. Site Features")
    col_a, col_b = st.columns(2)
    with col_a:
        has_pond       = st.checkbox("Pond",        True)
        has_solar      = st.checkbox("Solar",       True)
        has_greenhouse = st.checkbox("Greenhouse",  True)
    with col_b:
        has_poultry    = st.checkbox("Poultry",     True)
        has_borewell   = st.checkbox("Borewell",    True)
        has_compost    = st.checkbox("Compost",     True)
        has_swale      = st.checkbox("Swale",       True)

    # ── 5. Trees ──────────────────────────
    st.subheader("5. Tree Species")
    num_trees = st.slider("Default fruit species", 1, 6, 4)

    st.caption("➕ Add custom tree species")
    with st.expander("Add Custom Tree", expanded=False):
        ct_name    = st.text_input("Species name", key="ct_name",
                                    placeholder="e.g. Avocado")
        ct_size    = st.selectbox("Tree size", ["Small","Medium","Large"],
                                   key="ct_size")
        ct_spacing = st.number_input("Spacing (ft)", 4, 30, 10, key="ct_sp")
        ct_ylo     = st.number_input("Min yield (kg/tree/yr)", 5, 500, 20,
                                      key="ct_ylo")
        ct_yhi     = st.number_input("Max yield (kg/tree/yr)", 5, 500, 40,
                                      key="ct_yhi")
        ct_price   = st.number_input(f"Market price ({CUR_SYM}/kg)", 0.1, 50.0,
                                      1.0, 0.1, key="ct_price")
        if st.button("Add Tree", key="add_tree_btn"):
            if ct_name.strip():
                st.session_state.custom_trees.append({
                    "name": ct_name.strip(), "size": ct_size,
                    "spacing": ct_spacing,
                    "yield_lo": ct_ylo, "yield_hi": ct_yhi,
                    "price_usd": ct_price / CUR_FX,
                })
                st.success(f"Added: {ct_name}")

    if st.session_state.custom_trees:
        st.caption("Custom trees added:")
        for i, ct in enumerate(st.session_state.custom_trees):
            col_t, col_x = st.columns([4,1])
            with col_t:
                st.caption(f"• {ct['name']} ({ct['size']}, {ct['spacing']}ft)")
            with col_x:
                if st.button("✕", key=f"rm_{i}"):
                    st.session_state.custom_trees.pop(i)
                    st.rerun()

    # ── 6. Site Parameters ────────────────
    st.subheader("6. Site Parameters")
    slope_dir = st.selectbox("Slope Direction", [
        "North-West to South-East (2%)", "North to South (1.5%)",
        "East to West (2%)", "South to North (1%)"])
    borewell_loc = st.selectbox("Borewell Location", [
        "North-East corner", "North-West corner",
        "South-East corner", "Centre-East"])
    water_src = st.selectbox("Primary Water Source", [
        "Borewell + Rainwater Harvesting", "Borewell only",
        "Municipality + Borewell", "Rainwater Harvesting only"])

    # ── 7. Output ─────────────────────────
    st.subheader("7. Output Quality")
    dpi_opt = st.select_slider("Image DPI",
                                options=[72, 150, 200, 300],
                                value=72 if access == "free" else 300)
    if access == "free":
        st.caption("⚠️ Free: 72 DPI. Unlock for 300 DPI.")

    # ── 8. Unlock ─────────────────────────
    st.divider()
    st.subheader("🔑 Unlock Full Version")
    manual_key = st.text_input("Enter Access Key", value=url_key,
                                placeholder="Paste key after payment",
                                type="password")
    if manual_key.strip():
        access = get_access(manual_key.strip())
        if access != "free":
            st.success(f"✅ {'Pro' if access=='pro' else 'Basic'} unlocked!")
        else:
            st.error("❌ Invalid key")

    if access == "free":
        st.markdown(f"""
        <a href="{BMC_10_URL}" target="_blank" class="cta-btn"
           style="display:block;text-align:center;margin-bottom:6px">
            ☕ Unlock Basic — $10
        </a>
        <a href="{BMC_20_URL}" target="_blank" class="cta-btn secondary"
           style="display:block;text-align:center">
            🌟 Unlock Pro Report — $20
        </a>
        <p style='font-size:0.75rem;color:#6b7280;margin-top:0.4rem;text-align:center'>
        You'll be redirected back with your key automatically.
        </p>""", unsafe_allow_html=True)

    st.divider()
    generate_btn = st.button("🗺️ Generate Site Plan", type="primary",
                             use_container_width=True)


# ─────────────────────────────────────────────
#  GENERATE — store in session_state
# ─────────────────────────────────────────────
if generate_btn:
    if z4 < 0:
        st.error("Zone percentages exceed 100%. Please adjust sliders.")
        st.stop()

    locked = (access == "free")

    # Map name reflects house position and shape
    full_name = f"{project_name} [{house_pos.split('(')[1].rstrip(')')}]"

    with st.spinner("Building your blueprint..."):
        zone_fracs = {'z0':z0/100,'z1':z1/100,'z2':z2/100,
                      'z3':z3/100,'z4':z4/100}
        map_buf = generate_visual(
            L=float(length), W=float(width),
            name=full_name,
            zone_fracs=zone_fracs,
            has_pond=has_pond, has_solar=has_solar,
            has_greenhouse=has_greenhouse, has_poultry=has_poultry,
            has_borewell=has_borewell, has_compost=has_compost,
            has_swale=has_swale,
            slope_dir=slope_dir, borewell_loc=borewell_loc,
            water_src=water_src, num_tree_species=num_trees,
            locked=locked, dpi=dpi_opt,
        )
        st.session_state.map_buf_bytes = map_buf.read()
        st.session_state.map_generated = True

    # Build PDF immediately if paid (store it too)
    if access in ("basic","pro"):
        with st.spinner("Preparing PDF report..."):
            planting_df = make_planting_df(total_sqft, z2, num_trees,
                                           st.session_state.custom_trees,
                                           CUR_SYM, CUR_FX)
            cost_df     = make_cost_df(total_sqft, CUR_SYM, CUR_FX)
            st.session_state.pdf_buf_bytes = generate_pdf(
                st.session_state.map_buf_bytes,
                project_name, total_sqft,
                z0, z1, z2, z3, z4,
                planting_df, cost_df, CUR_SYM, CUR_FX
            )


# ─────────────────────────────────────────────
#  DISPLAY RESULTS
# ─────────────────────────────────────────────
if st.session_state.map_generated and st.session_state.map_buf_bytes:

    st.image(st.session_state.map_buf_bytes,
             caption=f"{project_name}  |  {total_sqft:,} sq.ft. = {total_acres:.2f} acres",
             use_column_width=True)

    # ── Download buttons (no refresh) ────
    dl_col1, dl_col2 = st.columns(2)

    if access == "free":
        with dl_col1:
            st.markdown(f"""
            <a href="{BMC_10_URL}" target="_blank" class="cta-btn"
               style="display:block;text-align:center">
                ☕ Unlock HD PNG + PDF — $10
            </a>""", unsafe_allow_html=True)
        with dl_col2:
            st.markdown(f"""
            <a href="{BMC_20_URL}" target="_blank" class="cta-btn secondary"
               style="display:block;text-align:center">
                🌟 Full 5-Page Report — $20
            </a>""", unsafe_allow_html=True)
    else:
        with dl_col1:
            st.download_button(
                label="⬇️ Download HD PNG",
                data=st.session_state.map_buf_bytes,
                file_name=f"{project_name.replace(' ','_')}_blueprint.png",
                mime="image/png",
                key="dl_png",
            )
        with dl_col2:
            if st.session_state.pdf_buf_bytes:
                st.download_button(
                    label="⬇️ Download PDF Report (5 pages)",
                    data=st.session_state.pdf_buf_bytes,
                    file_name=f"{project_name.replace(' ','_')}_report.pdf",
                    mime="application/pdf",
                    key="dl_pdf",
                )

    st.divider()

    # ── Zone table (always) ───────────────
    st.subheader("📊 Zone Area Calculations")
    df_zones = pd.DataFrame({
        'Zone':         ['Zone 0','Zone 1','Zone 2','Zone 3','Zone 4/5','TOTAL'],
        'Description':  ['Residential','Kitchen Garden','Food Forest',
                         'Pasture/Crops','Buffer/Fence',''],
        'Area (sq.ft.)':[f"{total_sqft*z0/100:,.0f}",f"{total_sqft*z1/100:,.0f}",
                         f"{total_sqft*z2/100:,.0f}",f"{total_sqft*z3/100:,.0f}",
                         f"{total_sqft*z4/100:,.0f}",f"{total_sqft:,.0f}"],
        'Percentage':   [f"{z0}%",f"{z1}%",f"{z2}%",f"{z3}%",f"{z4}%","100%"],
    })
    st.dataframe(df_zones, use_container_width=True, hide_index=True)

    # ── Paid tabs ────────────────────────
    if access in ("basic","pro"):
        st.divider()
        tab1, tab2, tab3 = st.tabs([
            "🌳 Planting Schedule",
            "💰 Cost Estimate",
            "💧 Water Flow Diagram",
        ])
        planting_df = make_planting_df(total_sqft, z2, num_trees,
                                       st.session_state.custom_trees,
                                       CUR_SYM, CUR_FX)
        cost_df = make_cost_df(total_sqft, CUR_SYM, CUR_FX)

        with tab1:
            st.subheader("Planting Schedule — Zone 2 Food Forest")
            st.dataframe(planting_df, use_container_width=True, hide_index=True)
            if st.session_state.custom_trees:
                st.caption(f"Includes {len(st.session_state.custom_trees)} custom species")

        with tab2:
            st.subheader(f"Setup Cost Estimate ({cur_label})")
            st.dataframe(cost_df, use_container_width=True, hide_index=True)
            acres = total_sqft / 43560
            total_cost = sum(v * acres * CUR_FX for _, v, _ in BASE_COSTS_USD)
            st.success(
                f"**Total Estimate: {CUR_SYM}{total_cost:,.0f}** "
                f"(for {total_acres:.2f} acres — adjust for your region)"
            )

        with tab3:
            st.subheader("Water Flow & Drainage System")
            wf_buf = make_water_fig()
            st.image(wf_buf, use_column_width=True)
            st.caption(
                "Borewell → Tank → Drip to Zones → "
                "Greywater → Bio-filter → Zone 1 → Swale → Recharge"
            )

else:
    # ── Landing page ─────────────────────
    st.markdown("""
    <div class="pricing-row">
        <div class="price-card price-free">
            <h3>Free Preview</h3>
            <div class="amount">$0</div>
            <ul>
                <li>Watermarked map</li>
                <li>72 DPI only</li>
                <li>Zone data table</li>
            </ul>
        </div>
        <div class="price-card price-basic">
            <h3>Basic</h3>
            <div class="amount">$10</div>
            <ul>
                <li>✅ Clean HD PNG (300 DPI)</li>
                <li>✅ 5-page PDF report</li>
                <li>✅ Planting schedule</li>
                <li>✅ Cost estimate</li>
            </ul>
        </div>
        <div class="price-card price-pro">
            <h3>Pro Report</h3>
            <div class="amount">$20</div>
            <ul>
                <li>✅ Everything in Basic</li>
                <li>✅ Water flow diagram</li>
                <li>✅ Income projections</li>
                <li>✅ Custom tree species</li>
                <li>✅ Multiple currencies</li>
            </ul>
        </div>
    </div>""", unsafe_allow_html=True)

    st.divider()
    col_l, col_r = st.columns([1.3, 1])

    with col_l:
        st.markdown("### How it works")
        st.markdown("""
        <div class="step"><div class="step-num">1</div>
        <div>Set your plot size, shape, and zone percentages in the sidebar</div></div>
        <div class="step"><div class="step-num">2</div>
        <div>Choose house position, features, tree species, and currency</div></div>
        <div class="step"><div class="step-num">3</div>
        <div>Click <b>Generate Site Plan</b> — preview appears instantly</div></div>
        <div class="step"><div class="step-num">4</div>
        <div>Pay on Buy Me a Coffee — you're redirected back with your key</div></div>
        <div class="step"><div class="step-num">5</div>
        <div>Download your HD PNG + full PDF report immediately</div></div>
        """, unsafe_allow_html=True)

    with col_r:
        st.markdown("### What farmers say")
        for quote, author in [
            ("Saved me hours of planning. The water flow diagram alone was worth it.",
             "Rajesh M. — 3-acre farm, India"),
            ("Real zone calculations, not just a pretty picture. Exactly what I needed.",
             "Sarah T. — Homestead, Texas"),
            ("Used the cost sheet to get a bank loan. They were impressed.",
             "Priya K. — 1-acre plot, Australia"),
        ]:
            st.markdown(f"""<div class="testimonial">
            "{quote}"<strong>— {author}</strong></div>""",
                        unsafe_allow_html=True)
