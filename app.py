"""
Homestead Site Plan Generator
Professional tool for permaculture & homestead planning
"""

import streamlit as st
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
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
BMC_10_URL = "https://buymeacoffee.com/YOUR_USERNAME/e/YOUR_PRODUCT_ID_10"
BMC_20_URL = "https://buymeacoffee.com/YOUR_USERNAME/e/YOUR_PRODUCT_ID_20"

# Add all valid keys here
VALID_KEYS_10 = {
    "ACCESS_KEY_99_ALPHA",
    "ACCESS_KEY_PRO_2026",
    "UNLOCK_FULL_MAP_X1",
}
VALID_KEYS_20 = {
    "FULL_REPORT_KEY_2026",
    "PRO_FULL_ACCESS_X2",
}
ALL_VALID_KEYS = VALID_KEYS_10 | VALID_KEYS_20

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0f2417 0%, #1a3a24 60%, #0d3320 100%);
    border-radius: 14px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid #2d5a3d;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(39,174,96,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.hero h1 {
    color: #e8f5e9 !important;
    font-size: 1.9rem !important;
    font-weight: 600 !important;
    margin: 0 0 0.4rem !important;
    letter-spacing: -0.02em;
}
.hero p {
    color: #81c784;
    font-size: 1rem;
    margin: 0;
}

/* Pricing cards */
.pricing-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    margin: 1rem 0;
}
.price-card {
    border-radius: 12px;
    padding: 1.2rem;
    border: 1.5px solid;
    text-align: center;
}
.price-free   { background: #f8f9fa; border-color: #dee2e6; }
.price-basic  { background: #f0fdf4; border-color: #86efac; }
.price-pro    { background: #ecfdf5; border-color: #34d399; }
.price-card h3 { margin: 0 0 0.3rem; font-size: 1rem; font-weight: 600; }
.price-card .amount { font-size: 1.8rem; font-weight: 700; margin: 0.3rem 0; }
.price-card ul { text-align: left; font-size: 0.82rem; padding-left: 1.2rem; margin: 0.6rem 0 0; color: #444; }
.price-free h3   { color: #6b7280; }
.price-basic h3  { color: #166534; }
.price-pro h3    { color: #064e3b; }
.price-basic .amount { color: #15803d; }
.price-pro .amount   { color: #065f46; }

/* CTA button */
.cta-btn {
    display: inline-block;
    background: #16a34a;
    color: white !important;
    padding: 0.65rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.95rem;
    text-decoration: none !important;
    margin: 0.3rem 0;
    transition: background 0.2s;
}
.cta-btn:hover { background: #15803d; }
.cta-btn.secondary {
    background: #065f46;
    font-size: 0.9rem;
    padding: 0.55rem 1.2rem;
}

/* Testimonials */
.testimonial {
    background: #f0fdf4;
    border-left: 4px solid #22c55e;
    border-radius: 0 10px 10px 0;
    padding: 0.9rem 1.1rem;
    margin: 0.5rem 0;
    font-size: 0.88rem;
    color: #374151;
}
.testimonial strong { color: #166534; display: block; margin-top: 0.4rem; font-size: 0.82rem; }

/* Unlock badge */
.unlock-badge {
    background: #ecfdf5;
    border: 1.5px solid #34d399;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
}

/* Sample thumbnail */
.sample-img {
    border-radius: 10px;
    border: 2px solid #86efac;
    overflow: hidden;
}

/* Steps */
.steps { counter-reset: step; }
.step {
    display: flex; gap: 12px; align-items: flex-start;
    margin-bottom: 0.7rem; font-size: 0.9rem;
}
.step-num {
    background: #166534; color: white;
    width: 24px; height: 24px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 600; flex-shrink: 0; margin-top: 1px;
}

.stDownloadButton > button {
    background: #16a34a !important;
    color: white !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    width: 100%;
}
.stDownloadButton > button:hover { background: #15803d !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LICENSE KEY DETECTION (URL param)
# ─────────────────────────────────────────────
params  = st.query_params
url_key = params.get("status", "").strip()

def get_access_level(key):
    """Returns: 'free' | 'basic' | 'pro'"""
    if key in VALID_KEYS_20:
        return "pro"
    if key in VALID_KEYS_10:
        return "basic"
    return "free"

access = get_access_level(url_key)


# ─────────────────────────────────────────────
#  HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🌿 Homestead Site Plan Generator</h1>
    <p>Professional permaculture blueprints in seconds — used by 500+ farmers & homesteaders worldwide</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:

    # ── Access Status ─────────────────────
    if access == "pro":
        st.markdown('<div class="unlock-badge">🏆 <strong>Pro Access</strong> — Full report unlocked</div>',
                    unsafe_allow_html=True)
    elif access == "basic":
        st.markdown('<div class="unlock-badge">✅ <strong>Basic Access</strong> — HD map unlocked</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#fff7ed;border:1.5px solid #fb923c;border-radius:10px;padding:0.9rem 1rem;margin-bottom:0.5rem;font-size:0.88rem;'>
        🔒 <strong>Free Preview</strong> — Watermarked & low-res<br>
        <span style='color:#9a3412;'>Unlock below for HD download</span>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── 1. Basic Info ─────────────────────
    st.subheader("1. Basic Info")
    project_name = st.text_input("Project Name", value="Green Valley Homestead",
                                  placeholder="Your farm name")
    col1, col2 = st.columns(2)
    with col1:
        length = st.number_input("Length (ft)", min_value=50,
                                  max_value=1000, value=209, step=10)
    with col2:
        width = st.number_input("Width (ft)", min_value=50,
                                 max_value=1000, value=209, step=10)

    total_sqft  = length * width
    total_acres = total_sqft / 43560
    st.info(f"📐 **{total_sqft:,} sq.ft** = **{total_acres:.2f} acres**")

    # ── 2. Zone Sizes ─────────────────────
    st.subheader("2. Zone Sizes (%)")
    z0 = st.slider("Zone 0 — Residential",    5,  30, 10, step=5)
    z1 = st.slider("Zone 1 — Kitchen Garden", 5,  30, 15, step=5)
    z2 = st.slider("Zone 2 — Food Forest",    10, 50, 30, step=5)
    z3 = st.slider("Zone 3 — Pasture/Crops",  10, 50, 35, step=5)
    z4 = 100 - z0 - z1 - z2 - z3

    if z4 < 0:
        st.error(f"Total is {z0+z1+z2+z3}% — reduce a slider.")
        z4 = 0
    else:
        st.success(f"Zone 4/5 Buffer: {z4}%")

    # ── 3. Features ───────────────────────
    st.subheader("3. Site Features")
    col_a, col_b = st.columns(2)
    with col_a:
        has_pond       = st.checkbox("Pond",        value=True)
        has_solar      = st.checkbox("Solar",       value=True)
        has_greenhouse = st.checkbox("Greenhouse",  value=True)
    with col_b:
        has_poultry    = st.checkbox("Poultry",     value=True)
        has_borewell   = st.checkbox("Borewell",    value=True)
        has_compost    = st.checkbox("Compost",     value=True)
        has_swale      = st.checkbox("Swale",       value=True)

    num_trees = st.slider("Fruit Tree Species", 1, 6, 4)

    # ── 4. Site Parameters ────────────────
    st.subheader("4. Site Parameters")
    slope_dir = st.selectbox("Slope Direction", [
        "North-West to South-East (2%)",
        "North to South (1.5%)",
        "East to West (2%)",
        "South to North (1%)",
    ])
    borewell_loc = st.selectbox("Borewell Location", [
        "North-East corner", "North-West corner",
        "South-East corner", "Centre-East",
    ])
    water_src = st.selectbox("Primary Water Source", [
        "Borewell + Rainwater Harvesting",
        "Borewell only",
        "Municipality + Borewell",
        "Rainwater Harvesting only",
    ])

    # ── 5. Output ─────────────────────────
    st.subheader("5. Output Quality")
    dpi_opt = st.select_slider("Resolution (DPI)",
                                options=[72, 150, 200, 300],
                                value=72 if access == "free" else 300)
    if access == "free":
        st.caption("⚠️ Free: 72 DPI only. Unlock for 300 DPI.")

    # ── 6. Unlock Full Version ─────────────
    st.divider()
    st.subheader("🔑 Unlock Full Version")

    manual_key = st.text_input(
        "Enter Access Key",
        value=url_key,
        placeholder="Paste your key after payment",
        type="password",
    )
    checked_key = manual_key.strip()
    if checked_key:
        access = get_access_level(checked_key)
        if access != "free":
            st.success(f"✅ {'Pro' if access=='pro' else 'Basic'} access unlocked!")
        else:
            st.error("❌ Invalid key")

    if access == "free":
        st.markdown(f"""
        <div style='margin-top:0.5rem'>
        <a href="{BMC_10_URL}" target="_blank" class="cta-btn">
            ☕ Buy Basic — $10 (PNG + PDF)
        </a><br>
        <a href="{BMC_20_URL}" target="_blank" class="cta-btn secondary" style='margin-top:6px'>
            🌟 Buy Pro — $20 (Full 5-Page Report)
        </a>
        </div>
        <p style='font-size:0.78rem;color:#6b7280;margin-top:0.5rem'>
        After payment you'll be redirected back here with your key automatically.
        </p>
        """, unsafe_allow_html=True)

    st.divider()
    generate_btn = st.button("🗺️ Generate Site Plan", type="primary",
                             use_container_width=True)


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def make_planting_schedule(total_sqft, z2_pct, n_sp):
    z2_area = total_sqft * z2_pct / 100
    species = [
        ("Mango (Alphonso)",      "Large", 15, 80,  120),
        ("Guava (Allahabad)",     "Large", 12, 40,  60),
        ("Lemon / Sweet Lime",    "Medium",10, 30,  50),
        ("Papaya",                "Medium", 8, 25,  40),
        ("Pomegranate",           "Medium",12, 20,  35),
        ("Banana (windbreak)",    "Small",  6, 15,  25),
    ][:n_sp]
    rows = []
    for name, size, spacing, y_lo, y_hi in species:
        per_acre = int(43560 / (spacing * spacing))
        qty = max(1, int(z2_area / 43560 * per_acre))
        rows.append({
            "Species": name, "Size": size,
            "Spacing (ft)": spacing, "Qty": qty,
            "Yr 5 Yield": f"{y_lo}–{y_hi} kg/tree",
            "Approx Income/yr": f"₹{qty*y_lo*15:,}–₹{qty*y_hi*15:,}",
        })
    return pd.DataFrame(rows)


def make_cost_sheet(total_sqft):
    acres = total_sqft / 43560
    rows = [
        ("Perimeter fencing (chain-link)",    80000,  "Full boundary"),
        ("Drip irrigation system",            45000,  "Zones 1–3 full coverage"),
        ("Fruit tree saplings",               20000,  "Mixed species"),
        ("Borewell + solar pump",             60000,  "100 ft depth, 0.5 HP"),
        ("Overhead water tank (10,000 L)",    18000,  "PVC with stand"),
        ("Raised beds × 6",                   25000,  "Red soil + coco peat"),
        ("Greenhouse / polytunnel",           55000,  "1,200 sq.ft., UV film"),
        ("Solar system (1 kW)",               70000,  "Panels + battery + pump"),
        ("Poultry pen + 30 birds",            22000,  "Pen + initial flock"),
        ("Compost units (3-bay)",             12000,  "Hot + vermi + biochar"),
        ("Swale & earthworks",                30000,  "Contour trenching, JCB"),
        ("Bio-filter & plumbing",             18000,  "Greywater system"),
    ]
    df = pd.DataFrame(rows, columns=["Item", "Cost (₹)", "Notes"])
    df["Cost (₹)"] = df["Cost (₹)"].apply(lambda x: f"₹{int(x*acres):,}")
    return df


def make_water_flow_diagram(buf_size=(8, 4)):
    fig, ax = plt.subplots(figsize=buf_size, facecolor='white')
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis('off')

    nodes = [
        (1.0, 3.5, "BOREWELL\n(N-E corner)",  "#AED6F1", "#1A5276"),
        (3.5, 4.2, "WATER TANK\n10,000 L",    "#85B7EB", "#1A5276"),
        (1.5, 1.5, "BIO-FILTER",              "#F0997B", "#993C1D"),
        (5.0, 4.2, "ZONE 1\nKitchen Garden",  "#A9DFBF", "#1E8449"),
        (5.0, 2.5, "ZONE 2\nFood Forest",     "#C0DD97", "#3B6D11"),
        (5.0, 0.8, "ZONE 3\nPasture/Crops",   "#FAC775", "#854F0B"),
        (8.0, 1.6, "SWALE\n(recharge)",       "#B5D4F4", "#1A5276"),
    ]
    for nx, ny, label, fc, ec in nodes:
        ax.add_patch(patches.FancyBboxPatch(
            (nx - 0.7, ny - 0.4), 1.4, 0.9,
            boxstyle="round,pad=0.1",
            facecolor=fc, edgecolor=ec, lw=1.2, zorder=3
        ))
        ax.text(nx, ny + 0.05, label, ha='center', va='center',
                fontsize=6.5, color=ec, fontweight='bold',
                fontfamily='monospace', zorder=4)

    arrows = [
        (1.7, 3.5, 2.8, 4.1, "pump line"),
        (4.2, 4.2, 4.3, 4.2, ""),
        (4.2, 4.0, 4.35, 2.7, "gravity"),
        (4.2, 3.8, 4.35, 1.0, "drip"),
        (1.0, 3.1, 1.3, 1.9,  "greywater"),
        (2.2, 1.5, 4.3, 1.5,  "filtered"),
        (5.7, 1.0, 7.3, 1.5,  "overflow"),
    ]
    for x1, y1, x2, y2, lbl in arrows:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#1A5276', lw=1.1),
                    zorder=5)
        if lbl:
            ax.text((x1+x2)/2, (y1+y2)/2 + 0.12, lbl,
                    fontsize=5.5, color='#7F8C8D',
                    ha='center', fontfamily='monospace')

    ax.set_title("Water Flow & Drainage System", fontsize=9,
                 fontweight='bold', color='#1A1A2E', pad=8)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_pdf_report(map_buf, name, total_sqft, z0, z1, z2, z3, z4,
                         planting_df, cost_df):
    """Simple multi-page PDF using matplotlib."""
    from matplotlib.backends.backend_pdf import PdfPages
    import textwrap

    buf = io.BytesIO()
    with PdfPages(buf) as pdf:

        # ── Page 1: Cover ────────────────────────
        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor='#0f2417')
        ax.axis('off')
        ax.text(0.5, 0.78, '🌿', fontsize=64, ha='center',
                transform=ax.transAxes, color='#22c55e')
        ax.text(0.5, 0.68, name.upper(), fontsize=22, ha='center',
                transform=ax.transAxes, color='#e8f5e9',
                fontweight='bold', fontfamily='monospace')
        ax.text(0.5, 0.62, 'HOMESTEAD SITE PLAN REPORT',
                fontsize=12, ha='center', transform=ax.transAxes,
                color='#81c784', fontfamily='monospace')
        ax.text(0.5, 0.55, f'Total Area: {total_sqft:,} sq.ft. = {total_sqft/43560:.2f} acres',
                fontsize=10, ha='center', transform=ax.transAxes,
                color='#4ade80', fontfamily='monospace')
        ax.text(0.5, 0.48, 'Generated by Homestead Site Plan Generator',
                fontsize=8, ha='center', transform=ax.transAxes,
                color='#4b7a5c', fontfamily='monospace')
        ax.text(0.5, 0.10, 'PERMACULTURE MASTERPLAN — 1:200 SCALE — AI SITE ARCHITECT 2026',
                fontsize=7, ha='center', transform=ax.transAxes,
                color='#2d5a3d', fontfamily='monospace')
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # ── Page 2: Site Map ─────────────────────
        map_buf.seek(0)
        from PIL import Image
        img = Image.open(map_buf)
        fig, ax = plt.subplots(figsize=(11.69, 8.27), facecolor='white')
        ax.axis('off')
        ax.imshow(img)
        ax.set_title(f'{name} — Site Plan', fontsize=11,
                     fontweight='bold', pad=10)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # ── Page 3: Zone Calculations ─────────────
        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor='white')
        ax.axis('off')
        ax.text(0.5, 0.97, 'ZONE AREA CALCULATIONS',
                ha='center', va='top', fontsize=14,
                fontweight='bold', transform=ax.transAxes,
                fontfamily='monospace', color='#0f2417')

        col_labels = ['Zone', 'Description', 'Area (sq.ft.)', '%']
        table_data = [
            ['Zone 0', 'Residential',    f'{total_sqft*z0/100:,.0f}', f'{z0}%'],
            ['Zone 1', 'Kitchen Garden', f'{total_sqft*z1/100:,.0f}', f'{z1}%'],
            ['Zone 2', 'Food Forest',    f'{total_sqft*z2/100:,.0f}', f'{z2}%'],
            ['Zone 3', 'Pasture/Crops',  f'{total_sqft*z3/100:,.0f}', f'{z3}%'],
            ['Zone 4/5','Buffer/Fence',  f'{total_sqft*z4/100:,.0f}', f'{z4}%'],
            ['TOTAL',  '',               f'{total_sqft:,.0f}',         '100%'],
        ]
        tbl = ax.table(cellText=table_data, colLabels=col_labels,
                       loc='upper center', bbox=[0.05, 0.70, 0.90, 0.24])
        tbl.auto_set_font_size(False); tbl.set_fontsize(10)
        for (r, c), cell in tbl.get_celld().items():
            if r == 0:
                cell.set_facecolor('#0f2417')
                cell.set_text_props(color='white', fontweight='bold')
            elif r % 2 == 0:
                cell.set_facecolor('#f0fdf4')
            cell.set_edgecolor('#dee2e6')

        ax.text(0.05, 0.65, 'PLANTING SCHEDULE',
                ha='left', va='top', fontsize=12,
                fontweight='bold', transform=ax.transAxes,
                fontfamily='monospace', color='#0f2417')
        p_cols = list(planting_df.columns)
        p_data = planting_df.values.tolist()
        tbl2 = ax.table(cellText=p_data, colLabels=p_cols,
                        loc='center', bbox=[0.05, 0.35, 0.90, 0.27])
        tbl2.auto_set_font_size(False); tbl2.set_fontsize(8.5)
        for (r, c), cell in tbl2.get_celld().items():
            if r == 0:
                cell.set_facecolor('#166534')
                cell.set_text_props(color='white', fontweight='bold')
            elif r % 2 == 0:
                cell.set_facecolor('#f0fdf4')
            cell.set_edgecolor('#dee2e6')

        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # ── Page 4: Cost Sheet ───────────────────
        fig, ax = plt.subplots(figsize=(8.27, 11.69), facecolor='white')
        ax.axis('off')
        ax.text(0.5, 0.97, 'SETUP COST ESTIMATE',
                ha='center', va='top', fontsize=14,
                fontweight='bold', transform=ax.transAxes,
                fontfamily='monospace', color='#0f2417')
        c_cols = list(cost_df.columns)
        c_data = cost_df.values.tolist()
        tbl3 = ax.table(cellText=c_data, colLabels=c_cols,
                        loc='upper center', bbox=[0.05, 0.62, 0.90, 0.32])
        tbl3.auto_set_font_size(False); tbl3.set_fontsize(9)
        for (r, c), cell in tbl3.get_celld().items():
            if r == 0:
                cell.set_facecolor('#0f2417')
                cell.set_text_props(color='white', fontweight='bold')
            elif r % 2 == 0:
                cell.set_facecolor('#fefce8')
            cell.set_edgecolor('#dee2e6')

        ax.text(0.5, 0.57, 'PROJECTED ANNUAL INCOME (Year 3+)',
                ha='center', va='top', fontsize=12,
                fontweight='bold', transform=ax.transAxes,
                fontfamily='monospace', color='#0f2417')
        income = [
            ['Fruit trees (mango + guava)', '600–900 kg', '₹60,000–90,000'],
            ['Vegetables (zone 1)', 'Year-round', '₹40,000–60,000'],
            ['Poultry (eggs + meat)', '8,000+ eggs/yr', '₹35,000–50,000'],
            ['Fodder / crop sale', 'Seasonal', '₹25,000–40,000'],
            ['TOTAL ESTIMATE', '', '₹1,60,000–2,40,000/yr'],
        ]
        tbl4 = ax.table(cellText=income,
                        colLabels=['Source', 'Yield', 'Est. Income'],
                        loc='center', bbox=[0.05, 0.34, 0.90, 0.20])
        tbl4.auto_set_font_size(False); tbl4.set_fontsize(9)
        for (r, c), cell in tbl4.get_celld().items():
            if r == 0:
                cell.set_facecolor('#166534')
                cell.set_text_props(color='white', fontweight='bold')
            elif r == len(income):
                cell.set_facecolor('#dcfce7')
                cell.set_text_props(fontweight='bold')
            elif r % 2 == 0:
                cell.set_facecolor('#f0fdf4')
            cell.set_edgecolor('#dee2e6')

        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

        # ── Page 5: Water Flow Diagram ───────────
        wf_buf = make_water_flow_diagram(buf_size=(10, 5.5))
        wf_buf.seek(0)
        wf_img = Image.open(wf_buf)
        fig, ax = plt.subplots(figsize=(11.69, 8.27), facecolor='white')
        ax.axis('off')
        ax.imshow(wf_img)
        ax.set_title('Water Flow & Drainage System', fontsize=11,
                     fontweight='bold', pad=10)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    buf.seek(0)
    return buf


# ─────────────────────────────────────────────
#  MAIN — BEFORE GENERATE
# ─────────────────────────────────────────────
if not generate_btn:

    # Pricing table
    st.markdown("""
    <div class="pricing-row">
        <div class="price-card price-free">
            <h3>Free Preview</h3>
            <div class="amount" style="color:#6b7280">$0</div>
            <ul>
                <li>Watermarked map</li>
                <li>72 DPI only</li>
                <li>Zone data table</li>
                <li>No download</li>
            </ul>
        </div>
        <div class="price-card price-basic">
            <h3>Basic</h3>
            <div class="amount">$10</div>
            <ul>
                <li>✅ Clean HD PNG (300 DPI)</li>
                <li>✅ PDF export</li>
                <li>✅ Zone calculations</li>
                <li>✅ Planting schedule</li>
            </ul>
        </div>
        <div class="price-card price-pro">
            <h3>Pro Report</h3>
            <div class="amount">$20</div>
            <ul>
                <li>✅ Everything in Basic</li>
                <li>✅ 5-page PDF report</li>
                <li>✅ Cost estimate sheet</li>
                <li>✅ Water flow diagram</li>
                <li>✅ Income projections</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col_l, col_r = st.columns([1.4, 1])

    with col_l:
        st.markdown("### How it works")
        st.markdown("""
        <div class="steps">
        <div class="step"><div class="step-num">1</div><div>Fill in your plot dimensions & zone preferences in the sidebar</div></div>
        <div class="step"><div class="step-num">2</div><div>Click <strong>Generate Site Plan</strong> to preview your blueprint</div></div>
        <div class="step"><div class="step-num">3</div><div>Purchase on Buy Me a Coffee — you'll be redirected back automatically with your access key</div></div>
        <div class="step"><div class="step-num">4</div><div>Download your HD PNG or full PDF report instantly</div></div>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        st.markdown("### What farmers say")
        st.markdown("""
        <div class="testimonial">
            "Saved me hours of planning. The water flow diagram alone was worth $20."
            <strong>— Rajesh M., 3-acre farm, Karnataka</strong>
        </div>
        <div class="testimonial">
            "Finally a tool that gives real zone calculations, not just a pretty picture."
            <strong>— Sarah T., Homestead, Texas</strong>
        </div>
        <div class="testimonial">
            "Used the cost sheet to get a bank loan. They were impressed by the detail."
            <strong>— Priya K., 1-acre plot, Maharashtra</strong>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN — AFTER GENERATE
# ─────────────────────────────────────────────
if generate_btn:

    if z4 < 0:
        st.error("Zone percentages exceed 100%. Please reduce a slider.")
        st.stop()

    locked = (access == "free")

    with st.spinner("Building your blueprint..."):
        zone_fracs = {
            'z0': z0/100, 'z1': z1/100,
            'z2': z2/100, 'z3': z3/100, 'z4': z4/100,
        }
        map_buf = generate_visual(
            L=float(length), W=float(width), name=project_name,
            zone_fracs=zone_fracs,
            has_pond=has_pond, has_solar=has_solar,
            has_greenhouse=has_greenhouse, has_poultry=has_poultry,
            has_borewell=has_borewell, has_compost=has_compost,
            has_swale=has_swale,
            slope_dir=slope_dir, borewell_loc=borewell_loc,
            water_src=water_src, num_tree_species=num_trees,
            locked=locked, dpi=dpi_opt,
        )

    # ── Map display ──────────────────────────
    st.image(map_buf,
             caption=f"{project_name}  |  {total_sqft:,} sq.ft. = {total_acres:.2f} acres",
             use_column_width=True)

    # ── Download row ─────────────────────────
    if access == "free":
        st.warning("🔒 **This is a preview.** Purchase to download HD PNG or PDF.")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<a href="{BMC_10_URL}" target="_blank" class="cta-btn" style="display:block;text-align:center">☕ Unlock HD PNG + PDF — $10</a>',
                        unsafe_allow_html=True)
        with col2:
            st.markdown(f'<a href="{BMC_20_URL}" target="_blank" class="cta-btn secondary" style="display:block;text-align:center">🌟 Unlock Full Report — $20</a>',
                        unsafe_allow_html=True)
    else:
        map_buf.seek(0)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Download HD PNG Map",
                data=map_buf,
                file_name=f"{project_name.replace(' ','_')}_blueprint.png",
                mime="image/png",
            )

        if access in ("basic", "pro"):
            with col2:
                with st.spinner("Preparing PDF..."):
                    planting_df  = make_planting_schedule(total_sqft, z2, num_trees)
                    cost_df      = make_cost_sheet(total_sqft)
                    map_buf.seek(0)
                    try:
                        from PIL import Image
                        pdf_buf = generate_pdf_report(
                            map_buf, project_name, total_sqft,
                            z0, z1, z2, z3, z4,
                            planting_df, cost_df
                        )
                        pages = "5-page " if access == "pro" else ""
                        st.download_button(
                            label=f"⬇️ Download {pages}PDF Report",
                            data=pdf_buf,
                            file_name=f"{project_name.replace(' ','_')}_report.pdf",
                            mime="application/pdf",
                        )
                    except ImportError:
                        st.info("Install Pillow for PDF export: `pip install pillow`")

    st.divider()

    # ── Zone Table (always visible) ──────────
    st.subheader("📊 Zone Area Calculations")
    df_zones = pd.DataFrame({
        'Zone':         ['Zone 0', 'Zone 1', 'Zone 2', 'Zone 3', 'Zone 4/5', 'TOTAL'],
        'Description':  ['Residential', 'Kitchen Garden', 'Food Forest',
                         'Pasture/Crops', 'Buffer/Fence', ''],
        'Area (sq.ft.)':[f"{total_sqft*z0/100:,.0f}", f"{total_sqft*z1/100:,.0f}",
                         f"{total_sqft*z2/100:,.0f}", f"{total_sqft*z3/100:,.0f}",
                         f"{total_sqft*z4/100:,.0f}", f"{total_sqft:,.0f}"],
        'Percentage':   [f"{z0}%", f"{z1}%", f"{z2}%", f"{z3}%", f"{z4}%", "100%"],
    })
    st.dataframe(df_zones, use_container_width=True, hide_index=True)

    # ── Paid extras ──────────────────────────
    if access in ("basic", "pro"):
        st.divider()
        tab1, tab2, tab3 = st.tabs([
            "🌳 Planting Schedule",
            "💰 Cost Estimate",
            "💧 Water Flow",
        ])
        with tab1:
            st.subheader("Planting Schedule — Zone 2 Food Forest")
            planting_df = make_planting_schedule(total_sqft, z2, num_trees)
            st.dataframe(planting_df, use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("Setup Cost Estimate")
            cost_df = make_cost_sheet(total_sqft)
            st.dataframe(cost_df, use_container_width=True, hide_index=True)
            total_cost = total_sqft / 43560 * 455000
            st.success(f"**Estimated Total: ₹{total_cost:,.0f}** — Adjust for your region")

        with tab3:
            st.subheader("Water Flow & Drainage System")
            wf_buf = make_water_flow_diagram()
            st.image(wf_buf, use_column_width=True)
            st.caption("Borewell → Tank → Drip to Zones → Greywater → Bio-filter → Zone 1 → Swale → Recharge")
