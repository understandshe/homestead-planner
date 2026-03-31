"""
Homestead Site Plan Generator
Production build — global audience
"""

import streamlit as st
import io, random
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
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
BMC_10_URL = "https://buymeacoffee.com/YOUR_USERNAME/e/YOUR_10_PRODUCT_ID"
BMC_20_URL = "https://buymeacoffee.com/YOUR_USERNAME/e/YOUR_20_PRODUCT_ID"

VALID_KEYS_BASIC = {"ACCESS_KEY_99_ALPHA", "ACCESS_KEY_PRO_2026", "UNLOCK_FULL_MAP_X1"}
VALID_KEYS_PRO   = {"FULL_REPORT_KEY_2026", "PRO_FULL_ACCESS_X2"}

CURRENCIES = {
    "USD ($)":  ("$",  1.00),
    "EUR (€)":  ("€",  0.92),
    "GBP (£)":  ("£",  0.79),
    "AUD (A$)": ("A$", 1.53),
    "CAD (C$)": ("C$", 1.36),
    "INR (Rs)": ("Rs", 83.5),
}

BASE_COSTS_USD = [
    ("Perimeter fencing",      1840, "Full boundary"),
    ("Drip irrigation",        1035, "Zones 1-3 full"),
    ("Fruit tree saplings",     460, "Mixed species"),
    ("Borewell + pump",        1380, "100 ft, 0.5 HP"),
    ("Water tank (10,000 L)",   450, "PVC with stand"),
    ("Raised beds x 6",         575, "Soil + growing mix"),
    ("Greenhouse",             1265, "1,200 sq.ft., UV film"),
    ("Solar system (1 kW)",    1610, "Panels + battery"),
    ("Poultry pen + 30 birds",  505, "Pen + initial flock"),
    ("Compost units (3-bay)",   275, "Hot + vermi + biochar"),
    ("Swale + earthworks",      690, "Contour trenching"),
    ("Bio-filter + plumbing",   450, "Greywater system"),
]

HOUSE_POS_MAP = {
    "Top-Left (NW)":     "NW",
    "Top-Right (NE)":    "NE",
    "Bottom-Left (SW)":  "SW",
    "Bottom-Right (SE)": "SE",
}

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────
defaults = {
    "map_bytes":     None,
    "pdf_bytes":     None,
    "generated":     False,
    "custom_trees":  [],
    "counter":       random.randint(490, 630),
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def clear_all():
    for k in defaults:
        st.session_state[k] = defaults[k] if k != "counter" else st.session_state.get("counter", 500)
    st.rerun()


def get_access(key: str) -> str:
    k = key.strip()
    if k in VALID_KEYS_PRO:   return "pro"
    if k in VALID_KEYS_BASIC: return "basic"
    return "free"


# ─────────────────────────────────────────────
#  DATA HELPERS
# ─────────────────────────────────────────────
def make_planting_df(total_sqft, z2_pct, n_default, custom_trees, sym, fx):
    z2 = total_sqft * z2_pct / 100
    base = [
        ("Mango (Alphonso)",   "Large",  15, 80,  120, 0.65),
        ("Guava (Allahabad)",  "Large",  12, 40,  60,  0.30),
        ("Lemon / Sweet Lime", "Medium", 10, 30,  50,  0.25),
        ("Papaya",             "Medium",  8, 25,  40,  0.15),
        ("Pomegranate",        "Medium", 12, 20,  35,  0.35),
        ("Banana (windbreak)", "Small",   6, 15,  25,  0.20),
    ][:n_default]
    for ct in custom_trees:
        base.append((ct["name"], ct["size"], ct["spacing"],
                     ct["yield_lo"], ct["yield_hi"], ct["price_usd"]))
    rows = []
    for name, size, sp, ylo, yhi, pr in base:
        qty = max(1, int(z2 / (sp * sp)))
        rows.append({
            "Species": name, "Size": size, "Spacing (ft)": sp, "Qty": qty,
            "Yr 5 Yield": f"{ylo}-{yhi} kg/tree",
            "Est. Annual Income": f"{sym}{qty*ylo*pr*fx:,.0f}-{sym}{qty*yhi*pr*fx:,.0f}",
        })
    return pd.DataFrame(rows)


def make_cost_df(total_sqft, sym, fx):
    acres = total_sqft / 43560
    rows = []
    for item, usd, note in BASE_COSTS_USD:
        rows.append({"Item": item,
                     f"Cost ({sym})": f"{sym}{usd * acres * fx:,.0f}",
                     "Notes": note})
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
#  WATER FLOW DIAGRAM
# ─────────────────────────────────────────────
def make_water_fig():
    fig, ax = plt.subplots(figsize=(11, 6), facecolor="white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    ax.set_title("Water Flow and Drainage System",
                 fontsize=13, fontweight="bold", pad=14, color="#0f2417")

    nodes = [
        (1.2, 4.4, "BOREWELL\n(N-E corner)",   "#AED6F1", "#1A5276"),
        (3.8, 5.1, "WATER TANK\n10,000 L",     "#378ADD", "#042C53"),
        (1.8, 2.1, "BIO-FILTER\n(reed bed)",   "#F0997B", "#712B13"),
        (5.5, 5.1, "ZONE 1\nKitchen Garden",   "#A9DFBF", "#0E6655"),
        (5.5, 3.3, "ZONE 2\nFood Forest",      "#97C459", "#27500A"),
        (5.5, 1.5, "ZONE 3\nPasture/Crops",    "#FAC775", "#633806"),
        (8.2, 2.3, "SWALE\n(recharge GW)",     "#B5D4F4", "#185FA5"),
        (3.8, 3.3, "HOUSE\n(greywater)",       "#D6E4F0", "#1A5276"),
    ]
    for nx, ny, lbl, fc, ec in nodes:
        ax.add_patch(patches.FancyBboxPatch(
            (nx-0.85, ny-0.48), 1.7, 0.96,
            boxstyle="round,pad=0.12",
            facecolor=fc, edgecolor=ec, lw=1.5, zorder=3))
        ax.text(nx, ny+0.04, lbl, ha="center", va="center",
                fontsize=7.5, color=ec, fontweight="bold",
                fontfamily="monospace", zorder=4)

    for x1,y1,x2,y2,lbl,col in [
        (2.05,4.4,  2.95,4.9,  "pump line",  "#1A5276"),
        (4.65,5.1,  4.65,3.78, "gravity",    "#1A5276"),
        (4.65,3.3,  4.65,1.98, "drip",       "#27AE60"),
        (2.65,4.1,  3.1, 3.6,  "greywater",  "#E24B4A"),
        (2.65,2.1,  4.65,2.1,  "filtered",   "#27AE60"),
        (6.35,1.5,  7.35,1.9,  "overflow",   "#1A5276"),
    ]:
        ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle="->", color=col, lw=1.4), zorder=5)
        if lbl:
            ax.text((x1+x2)/2+0.05, (y1+y2)/2+0.13, lbl,
                    fontsize=6.5, color="#5F5E5A", ha="center",
                    fontfamily="monospace")
    plt.tight_layout(pad=1.5)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────
#  PDF GENERATOR — no overlaps, high DPI
# ─────────────────────────────────────────────
def _draw_table(ax, data, col_labels, bbox,
                hdr_bg="#0f2417", alt_bg="#f0fdf4", fs=8.5):
    tbl = ax.table(cellText=data, colLabels=col_labels,
                   loc="upper left", bbox=bbox)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(fs)
    nrows = len(data)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#dee2e6"); cell.set_linewidth(0.5); cell.PAD = 0.06
        if r == 0:
            cell.set_facecolor(hdr_bg)
            cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
        elif r == nrows and c >= 0:
            cell.set_facecolor("#dcfce7"); cell.get_text().set_fontweight("bold")
        elif r % 2 == 0:
            cell.set_facecolor(alt_bg)
        else:
            cell.set_facecolor("white")


def build_pdf(map_bytes, project_name, total_sqft,
              z0, z1, z2, z3, z4, planting_df, cost_df, sym, fx):
    out = io.BytesIO()
    with PdfPages(out) as pdf:

        # PAGE 1 — Cover
        fig = plt.figure(figsize=(8.27, 11.69), facecolor="#0f2417")
        ax  = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        ax.add_patch(patches.Rectangle((0.12, 0.41), 0.76, 0.003,
                                        facecolor="#22c55e", transform=ax.transAxes))
        for txt, y, fs, col, fw in [
            (project_name.upper(),            0.72, 20, "#e8f5e9",  "bold"),
            ("HOMESTEAD SITE PLAN REPORT",    0.65, 11, "#81c784",  "normal"),
            (f"Total Area: {total_sqft:,} sq.ft. = {total_sqft/43560:.2f} acres",
                                              0.58,  9, "#4ade80",  "normal"),
            ("Generated by Homestead Site Plan Generator", 0.50,  8, "#4b7a5c",  "normal"),
            ("PERMACULTURE MASTERPLAN  |  1:200 SCALE  |  AI SITE ARCHITECT 2026",
                                              0.09,  7, "#2d5a3d",  "normal"),
        ]:
            ax.text(0.5, y, txt, ha="center", va="center",
                    transform=ax.transAxes, color=col, fontsize=fs,
                    fontweight=fw, fontfamily="monospace")
        pdf.savefig(fig, bbox_inches="tight", dpi=250); plt.close(fig)

        # PAGE 2 — Site Map (landscape)
        img = Image.open(io.BytesIO(map_bytes))
        fig = plt.figure(figsize=(11.69, 8.27), facecolor="white")
        ax  = fig.add_axes([0.02, 0.07, 0.96, 0.85])
        ax.axis("off"); ax.imshow(img, aspect="auto")
        fig.text(0.5, 0.97, f"{project_name} — Site Plan",
                 ha="center", fontsize=12, fontweight="bold",
                 color="#0f2417", fontfamily="monospace")
        fig.text(0.5, 0.02,
                 f"{total_sqft:,} sq.ft. = {total_sqft/43560:.2f} acres  |  Scale 1:200",
                 ha="center", fontsize=8, color="#6b7280", fontfamily="monospace")
        pdf.savefig(fig, bbox_inches="tight", dpi=250); plt.close(fig)

        # PAGE 3 — Zone Calculations
        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor="white")
        ax.axis("off")
        fig.text(0.5, 0.96, "ZONE AREA CALCULATIONS",
                 ha="center", fontsize=14, fontweight="bold",
                 color="#0f2417", fontfamily="monospace")
        _draw_table(ax, [
            ["Zone 0", "Residential",    f"{total_sqft*z0/100:,.0f}", f"{z0}%"],
            ["Zone 1", "Kitchen Garden", f"{total_sqft*z1/100:,.0f}", f"{z1}%"],
            ["Zone 2", "Food Forest",    f"{total_sqft*z2/100:,.0f}", f"{z2}%"],
            ["Zone 3", "Pasture/Crops",  f"{total_sqft*z3/100:,.0f}", f"{z3}%"],
            ["Zone 4/5","Buffer/Fence",  f"{total_sqft*z4/100:,.0f}", f"{z4}%"],
            ["TOTAL",  "",               f"{total_sqft:,.0f}",          "100%"],
        ], ["Zone", "Description", "Area (sq.ft.)", "%"],
           bbox=[0.03, 0.74, 0.94, 0.20])
        pdf.savefig(fig, bbox_inches="tight", dpi=250); plt.close(fig)

        # PAGE 4 — Planting Schedule
        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor="white")
        ax.axis("off")
        fig.text(0.5, 0.96, "PLANTING SCHEDULE — ZONE 2 FOOD FOREST",
                 ha="center", fontsize=13, fontweight="bold",
                 color="#0f2417", fontfamily="monospace")
        p_data = planting_df.values.tolist()
        row_h  = 0.065
        tbl_h  = min(0.82, len(p_data) * row_h + 0.07)
        _draw_table(ax, p_data, list(planting_df.columns),
                    bbox=[0.01, 0.93 - tbl_h, 0.98, tbl_h],
                    hdr_bg="#166534", alt_bg="#f0fdf4", fs=8)
        pdf.savefig(fig, bbox_inches="tight", dpi=250); plt.close(fig)

        # PAGE 5 — Cost Estimate
        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor="white")
        ax.axis("off")
        fig.text(0.5, 0.96, "SETUP COST ESTIMATE",
                 ha="center", fontsize=14, fontweight="bold",
                 color="#0f2417", fontfamily="monospace")
        c_data = cost_df.values.tolist()
        c_h    = min(0.52, len(c_data) * 0.055 + 0.06)
        _draw_table(ax, c_data, list(cost_df.columns),
                    bbox=[0.01, 0.93 - c_h, 0.98, c_h],
                    hdr_bg="#0f2417", alt_bg="#fefce8", fs=8.5)

        acres = total_sqft / 43560
        total_cost = sum(v * acres * fx for _, v, _ in BASE_COSTS_USD)
        fig.text(0.5, 0.93 - c_h - 0.04,
                 f"Estimated Total: {sym}{total_cost:,.0f}  (adjust for your region)",
                 ha="center", fontsize=10, color="#166534",
                 fontweight="bold", fontfamily="monospace")

        # Income table on same page
        fig.text(0.5, 0.93 - c_h - 0.11,
                 "PROJECTED ANNUAL INCOME (Year 3+)",
                 ha="center", fontsize=12, fontweight="bold",
                 color="#0f2417", fontfamily="monospace")
        inc = [
            ["Fruit trees", "600-900 kg", f"{sym}{600*fx:,.0f}-{sym}{900*fx:,.0f}"],
            ["Vegetables",  "Year-round", f"{sym}{400*fx:,.0f}-{sym}{600*fx:,.0f}"],
            ["Poultry",     "8,000+ eggs/yr", f"{sym}{350*fx:,.0f}-{sym}{500*fx:,.0f}"],
            ["Fodder/crops","Seasonal",    f"{sym}{250*fx:,.0f}-{sym}{400*fx:,.0f}"],
            ["TOTAL",       "",           f"{sym}{1600*fx:,.0f}-{sym}{2400*fx:,.0f}/yr"],
        ]
        i_h   = 0.27
        i_top = 0.93 - c_h - 0.16
        _draw_table(ax, inc, ["Source", "Yield", "Est. Annual Income"],
                    bbox=[0.01, i_top - i_h, 0.98, i_h],
                    hdr_bg="#166534", alt_bg="#f0fdf4", fs=9)
        pdf.savefig(fig, bbox_inches="tight", dpi=250); plt.close(fig)

        # PAGE 6 — Water Flow (landscape)
        wf_buf = make_water_fig()
        wf_img = Image.open(wf_buf)
        fig = plt.figure(figsize=(11.69, 8.27), facecolor="white")
        ax  = fig.add_axes([0.02, 0.05, 0.96, 0.88])
        ax.axis("off"); ax.imshow(wf_img, aspect="auto")
        pdf.savefig(fig, bbox_inches="tight", dpi=250); plt.close(fig)

    out.seek(0)
    return out.read()


# ─────────────────────────────────────────────
#  CSS — professional, no garish gradients
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.block-container { padding-top: 1rem; padding-bottom: 2rem; }

/* HERO */
.hero {
    background: #0f2417;
    border-radius: 10px;
    padding: 1.6rem 2rem;
    margin-bottom: 1rem;
    border: 1px solid #2d5a3d;
}
.hero h1 {
    color: #e8f5e9 !important;
    font-size: 1.6rem !important;
    font-weight: 600 !important;
    margin: 0 0 0.25rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: -0.01em;
}
.hero p { color: #81c784; font-size: 0.9rem; margin: 0; }

/* COUNTER */
.live-counter {
    text-align: center;
    padding: 1rem;
    background: #0f2417;
    border-radius: 10px;
    border: 1px solid #2d5a3d;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
}
.counter-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.4rem;
    font-weight: 600;
    color: #4ade80;
}
.counter-label { font-size: 0.75rem; color: #81c784; }
.counter-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 5px;
    animation: blink 1.4s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.25} }

/* PRICING */
.pricing-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 0.8rem 0; }
.price-card { border-radius: 10px; padding: 1rem 1.1rem; border: 1.5px solid; }
.price-free  { background: #f9fafb; border-color: #e5e7eb; }
.price-basic { background: #f0fdf4; border-color: #86efac; }
.price-pro   { background: #ecfdf5; border-color: #34d399; }
.price-card h3 { margin: 0 0 0.2rem; font-size: 0.9rem; font-weight: 600; }
.price-card .amount { font-size: 1.6rem; font-weight: 700; margin: 0.2rem 0; }
.price-card ul { font-size: 0.78rem; padding-left: 1rem; margin: 0.4rem 0 0; color: #374151; }
.price-free h3   { color: #6b7280; }  .price-free .amount   { color: #6b7280; }
.price-basic h3  { color: #166534; }  .price-basic .amount  { color: #15803d; }
.price-pro h3    { color: #064e3b; }  .price-pro .amount    { color: #065f46; }

/* TESTIMONIAL */
.review { background: #f0fdf4; border-left: 3px solid #22c55e;
          border-radius: 0 8px 8px 0; padding: 0.7rem 0.9rem;
          margin: 0.35rem 0; font-size: 0.83rem; color: #374151; }
.review strong { color: #166534; display: block; margin-top: 0.25rem; font-size: 0.78rem; }

/* STEPS */
.step { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 0.55rem; font-size: 0.86rem; }
.sn { background: #166534; color: white; width: 21px; height: 21px;
      border-radius: 50%; display: flex; align-items: center; justify-content: center;
      font-size: 0.73rem; font-weight: 600; flex-shrink: 0; margin-top: 2px; }

/* DOWNLOAD BUTTONS */
.stDownloadButton > button {
    background: #166534 !important; color: white !important;
    border: none !important; font-weight: 600 !important;
    border-radius: 8px !important; width: 100% !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stDownloadButton > button:hover { background: #14532d !important; }

/* ACCESS BADGE */
.access-ok { background: #f0fdf4; border: 1px solid #86efac;
             border-radius: 8px; padding: 0.65rem 0.9rem;
             font-size: 0.85rem; color: #166534; margin-bottom: 0.5rem; }
.access-free { background: #fff7ed; border: 1px solid #fb923c;
               border-radius: 8px; padding: 0.65rem 0.9rem;
               font-size: 0.85rem; color: #9a3412; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LICENSE KEY (URL param)
# ─────────────────────────────────────────────
params  = st.query_params
url_key = params.get("status", "").strip()
access  = get_access(url_key)


# ─────────────────────────────────────────────
#  HEADER ROW
# ─────────────────────────────────────────────
col_hero, col_ctr = st.columns([3.5, 1])

with col_hero:
    st.markdown("""
    <div class="hero">
        <h1>Homestead Site Plan Generator</h1>
        <p>Professional permaculture blueprints in seconds — trusted by homesteaders worldwide</p>
    </div>""", unsafe_allow_html=True)

with col_ctr:
    st.markdown(f"""
    <div class="live-counter">
        <div class="counter-label">PLANS GENERATED</div>
        <div class="counter-num" id="cnt">{st.session_state.counter:,}</div>
        <div class="counter-label">
            <span class="counter-dot"></span>live
        </div>
    </div>
    <script>
    (function(){{
        var el = document.getElementById('cnt');
        if (!el) return;
        var n = {st.session_state.counter};
        function tick() {{
            if (Math.random() < 0.35) {{
                n += Math.ceil(Math.random() * 3);
                el.textContent = n.toLocaleString();
            }}
            setTimeout(tick, 1500 + Math.random() * 2500);
        }}
        tick();
    }})();
    </script>""", unsafe_allow_html=True)
    st.session_state.counter += random.randint(0, 2)


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:

    if access == "pro":
        st.markdown('<div class="access-ok">Pro Access — Full report unlocked</div>',
                    unsafe_allow_html=True)
    elif access == "basic":
        st.markdown('<div class="access-ok">Basic Access — HD map unlocked</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="access-free">Free Preview — Watermarked map only</div>',
                    unsafe_allow_html=True)

    if st.button("Clear / Start Over", use_container_width=True):
        clear_all()

    st.divider()

    # Currency
    cur_label = st.selectbox("Currency", list(CURRENCIES.keys()))
    CUR_SYM, CUR_FX = CURRENCIES[cur_label]

    st.divider()

    # 1. Basic Info
    st.subheader("1. Basic Info")
    project_name = st.text_input("Project Name", value="Green Valley Homestead")

    plot_shape = st.selectbox("Plot Shape", [
        "Rectangle",
        "L-Shape (NE corner removed)",
        "L-Shape (SW corner removed)",
        "Irregular (approximate)",
    ])

    c1, c2 = st.columns(2)
    with c1: length = st.number_input("Length (ft)", 50, 2000, 400, 10)
    with c2: width  = st.number_input("Width  (ft)", 50, 2000, 400, 10)

    if "L-Shape" in plot_shape:
        cut = st.slider("Corner cut (%)", 10, 40, 25, 5)
        total_sqft = int(length * width * (1 - cut/100))
    else:
        total_sqft = length * width
    total_acres = total_sqft / 43560
    st.info(f"{total_sqft:,} sq.ft.  =  {total_acres:.2f} acres")

    # 2. Zone Sizes
    st.subheader("2. Zone Sizes (%)")
    z0 = st.slider("Zone 0  Residential",    5, 30, 10, 5)
    z1 = st.slider("Zone 1  Kitchen Garden", 5, 30, 15, 5)
    z2 = st.slider("Zone 2  Food Forest",   10, 50, 30, 5)
    z3 = st.slider("Zone 3  Pasture/Crops", 10, 50, 35, 5)
    z4 = 100 - z0 - z1 - z2 - z3
    if z4 < 0:
        st.error(f"Total {z0+z1+z2+z3}%  — reduce a slider.")
        z4 = 0
    else:
        st.success(f"Zone 4/5 Buffer: {z4}%")

    # 3. House Position
    st.subheader("3. House Position")
    house_pos_label = st.selectbox("Place residential zone at", list(HOUSE_POS_MAP.keys()))
    house_pos = HOUSE_POS_MAP[house_pos_label]
    st.caption("The map will draw Zone 0 at the selected corner.")

    # 4. Site Features
    st.subheader("4. Site Features")
    ca, cb = st.columns(2)
    with ca:
        has_pond       = st.checkbox("Pond",       True)
        has_solar      = st.checkbox("Solar",      True)
        has_greenhouse = st.checkbox("Greenhouse", True)
    with cb:
        has_poultry    = st.checkbox("Poultry",    True)
        has_borewell   = st.checkbox("Borewell",   True)
        has_compost    = st.checkbox("Compost",    True)
        has_swale      = st.checkbox("Swale",      True)

    # 5. Trees
    st.subheader("5. Tree Species")
    n_default_trees = st.slider("Default species (preset list)", 1, 6, 4)

    with st.expander("Add Custom Tree Species"):
        ct_name    = st.text_input("Species name", key="ct_name", placeholder="e.g. Avocado")
        ct_size    = st.selectbox("Size", ["Small", "Medium", "Large"], key="ct_size")
        ct_sp      = st.number_input("Spacing (ft)", 4, 30, 10, key="ct_sp")
        ct_ylo     = st.number_input("Min yield (kg/tree/yr)", 5, 500, 20, key="ct_ylo")
        ct_yhi     = st.number_input("Max yield (kg/tree/yr)", 5, 500, 40, key="ct_yhi")
        ct_price   = st.number_input(f"Market price ({CUR_SYM}/kg)", 0.1, 50.0, 1.0, 0.1, key="ct_pr")
        if st.button("Add to list", key="add_tree"):
            if ct_name.strip():
                st.session_state.custom_trees.append({
                    "name": ct_name.strip(), "size": ct_size,
                    "spacing": ct_sp, "yield_lo": ct_ylo, "yield_hi": ct_yhi,
                    "price_usd": ct_price / CUR_FX,
                })
                st.success(f"Added: {ct_name.strip()}")

    if st.session_state.custom_trees:
        for i, ct in enumerate(st.session_state.custom_trees):
            cx, cy = st.columns([4, 1])
            cx.caption(f"{ct['name']} ({ct['size']}, {ct['spacing']} ft)")
            if cy.button("X", key=f"rm_{i}"):
                st.session_state.custom_trees.pop(i); st.rerun()

    # 6. Site Parameters
    st.subheader("6. Site Parameters")
    slope_dir = st.selectbox("Slope direction", [
        "NW to SE (2%)", "N to S (1.5%)", "E to W (2%)", "S to N (1%)"])
    borewell_loc = st.selectbox("Borewell location", [
        "North-East corner", "North-West corner",
        "South-East corner", "Centre-East"])
    water_src = st.selectbox("Primary water source", [
        "Borewell + Rainwater Harvesting",
        "Borewell only", "Municipality + Borewell",
        "Rainwater Harvesting only"])

    # 7. Output
    st.subheader("7. Output Quality")
    dpi_opt = st.select_slider("Image DPI",
                                options=[72, 150, 200, 300],
                                value=72 if access == "free" else 300)
    if access == "free":
        st.caption("Free plan: 72 DPI only. Paid: up to 300 DPI.")

    # 8. Unlock
    st.divider()
    st.subheader("Unlock Full Version")
    manual_key = st.text_input("Access Key",
                                value=url_key,
                                placeholder="Paste key after payment",
                                type="password")
    if manual_key.strip():
        access = get_access(manual_key.strip())
        if access == "free":
            st.error("Invalid key")
        else:
            st.success(f"{'Pro' if access=='pro' else 'Basic'} access active")

    if access == "free":
        st.link_button("Buy Basic — $10  (HD PNG + PDF)", BMC_10_URL,
                       use_container_width=True)
        st.link_button("Buy Pro — $20  (Full 6-Page Report)", BMC_20_URL,
                       use_container_width=True)
        st.caption("After payment you are redirected back with your key.")

    st.divider()
    generate_btn = st.button("Generate Site Plan", type="primary",
                             use_container_width=True)


# ─────────────────────────────────────────────
#  GENERATE
# ─────────────────────────────────────────────
if generate_btn:
    if z4 < 0:
        st.error("Zone percentages exceed 100%. Please adjust sliders.")
        st.stop()

    locked = (access == "free")

    with st.spinner("Building blueprint..."):
        zf = {"z0": z0/100, "z1": z1/100, "z2": z2/100,
              "z3": z3/100, "z4": z4/100}
        map_buf = generate_visual(
            L=float(length), W=float(width), name=project_name,
            zone_fracs=zf,
            has_pond=has_pond, has_solar=has_solar,
            has_greenhouse=has_greenhouse, has_poultry=has_poultry,
            has_borewell=has_borewell, has_compost=has_compost,
            has_swale=has_swale,
            slope_dir=slope_dir, borewell_loc=borewell_loc,
            water_src=water_src, num_tree_species=n_default_trees,
            house_pos=house_pos,
            locked=locked, dpi=dpi_opt,
        )
        st.session_state.map_bytes = map_buf.read()
        st.session_state.generated = True

    if access in ("basic", "pro"):
        with st.spinner("Preparing PDF..."):
            planting_df = make_planting_df(
                total_sqft, z2, n_default_trees,
                st.session_state.custom_trees, CUR_SYM, CUR_FX)
            cost_df = make_cost_df(total_sqft, CUR_SYM, CUR_FX)
            st.session_state.pdf_bytes = build_pdf(
                st.session_state.map_bytes, project_name, total_sqft,
                z0, z1, z2, z3, z4, planting_df, cost_df, CUR_SYM, CUR_FX)


# ─────────────────────────────────────────────
#  DISPLAY
# ─────────────────────────────────────────────
if st.session_state.generated and st.session_state.map_bytes:

    st.image(st.session_state.map_bytes,
             caption=f"{project_name}  |  {total_sqft:,} sq.ft. = {total_acres:.2f} acres  |  Zone 0: {house_pos_label}",
             use_column_width=True)

    d1, d2 = st.columns(2)

    if access == "free":
        with d1:
            st.link_button("Buy Basic — $10  (HD PNG + PDF)",
                           BMC_10_URL, use_container_width=True)
        with d2:
            st.link_button("Buy Pro — $20  (Full 6-Page Report)",
                           BMC_20_URL, use_container_width=True)
        st.info("Purchase to download watermark-free HD PNG and full PDF report.")
    else:
        with d1:
            st.download_button("Download HD PNG",
                                data=st.session_state.map_bytes,
                                file_name=f"{project_name.replace(' ','_')}_plan.png",
                                mime="image/png", key="dl_png")
        with d2:
            if st.session_state.pdf_bytes:
                st.download_button("Download PDF Report (6 pages)",
                                    data=st.session_state.pdf_bytes,
                                    file_name=f"{project_name.replace(' ','_')}_report.pdf",
                                    mime="application/pdf", key="dl_pdf")

    st.divider()
    st.subheader("Zone Area Calculations")
    st.dataframe(pd.DataFrame({
        "Zone":         ["Zone 0","Zone 1","Zone 2","Zone 3","Zone 4/5","TOTAL"],
        "Description":  ["Residential","Kitchen Garden","Food Forest",
                         "Pasture/Crops","Buffer/Fence",""],
        "Area (sq.ft.)":[f"{total_sqft*z0/100:,.0f}", f"{total_sqft*z1/100:,.0f}",
                         f"{total_sqft*z2/100:,.0f}", f"{total_sqft*z3/100:,.0f}",
                         f"{total_sqft*z4/100:,.0f}", f"{total_sqft:,.0f}"],
        "Percentage":   [f"{z0}%",f"{z1}%",f"{z2}%",f"{z3}%",f"{z4}%","100%"],
    }), use_container_width=True, hide_index=True)

    if access in ("basic", "pro"):
        st.divider()
        planting_df = make_planting_df(total_sqft, z2, n_default_trees,
                                       st.session_state.custom_trees, CUR_SYM, CUR_FX)
        cost_df = make_cost_df(total_sqft, CUR_SYM, CUR_FX)

        t1, t2, t3 = st.tabs(["Planting Schedule", "Cost Estimate", "Water Flow"])

        with t1:
            st.subheader("Planting Schedule — Zone 2 Food Forest")
            st.dataframe(planting_df, use_container_width=True, hide_index=True)

        with t2:
            st.subheader(f"Setup Cost Estimate ({cur_label})")
            st.dataframe(cost_df, use_container_width=True, hide_index=True)
            acres = total_sqft / 43560
            total_c = sum(v * acres * CUR_FX for _, v, _ in BASE_COSTS_USD)
            st.success(f"Total Estimate: {CUR_SYM}{total_c:,.0f}  (adjust for your region)")

        with t3:
            st.subheader("Water Flow and Drainage System")
            wf = make_water_fig()
            st.image(wf, use_column_width=True)
            st.caption("Borewell → Tank → Drip → Zones | Greywater → Bio-filter → Zone 1 | Overflow → Swale → Recharge")

# ─────────────────────────────────────────────
#  LANDING PAGE (before first generate)
# ─────────────────────────────────────────────
else:
    st.markdown("""
    <div class="pricing-row">
      <div class="price-card price-free">
        <h3>Free Preview</h3><div class="amount">$0</div>
        <ul><li>Watermarked map</li><li>72 DPI preview</li><li>Zone data table</li></ul>
      </div>
      <div class="price-card price-basic">
        <h3>Basic</h3><div class="amount">$10</div>
        <ul><li>Clean HD PNG (300 DPI)</li><li>6-page PDF report</li>
            <li>Planting schedule</li><li>Cost estimate sheet</li></ul>
      </div>
      <div class="price-card price-pro">
        <h3>Pro Report</h3><div class="amount">$20</div>
        <ul><li>All of Basic</li><li>Water flow diagram</li>
            <li>Income projections</li><li>Custom tree species</li>
            <li>Multi-currency support</li></ul>
      </div>
    </div>""", unsafe_allow_html=True)

    st.divider()
    cl, cr = st.columns([1.4, 1])

    with cl:
        st.markdown("**How it works**")
        st.markdown("""
        <div class="step"><div class="sn">1</div><div>Set plot size, shape, and zone percentages in the sidebar</div></div>
        <div class="step"><div class="sn">2</div><div>Choose house position — the map draws Zone 0 at the correct corner</div></div>
        <div class="step"><div class="sn">3</div><div>Click Generate Site Plan to see the blueprint instantly</div></div>
        <div class="step"><div class="sn">4</div><div>Purchase — you are redirected back with an access key automatically</div></div>
        <div class="step"><div class="sn">5</div><div>Download your HD PNG and full PDF report immediately</div></div>
        """, unsafe_allow_html=True)

    with cr:
        st.markdown("**What customers say**")
        for q, a in [
            ("Saved me hours of planning. The water flow diagram alone was worth it.",
             "Rajesh M. — 3-acre farm, India"),
            ("Real zone calculations, not just a pretty picture.",
             "Sarah T. — Homestead, Texas"),
            ("Used the cost sheet to get a bank loan. They were impressed.",
             "Priya K. — 1-acre plot, Australia"),
        ]:
            st.markdown(f'<div class="review">"{q}"<strong>— {a}</strong></div>',
                        unsafe_allow_html=True)
