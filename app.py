"""
Homestead Map Generator — Streamlit Web App
Run: streamlit run app.py
"""

import streamlit as st
import io
from homestead_map import generate_visual   # <-- तेरी file

# ─── Page config ─────────────────────────────
st.set_page_config(
    page_title="Homestead Map Generator",
    page_icon="🌿",
    layout="wide",
)

# ─── CSS tweak ───────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 1.6rem; }
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────
st.title("🌿 Homestead Site Plan Generator")
st.caption("User अपना data भरे → Professional blueprint तुरंत बनेगा")

# ═════════════════════════════════════════════
#  SIDEBAR = USER FORM
# ═════════════════════════════════════════════
with st.sidebar:
    st.header("📋 Site Details")

    # ── Basic Info ───────────────────────────
    st.subheader("1. Basic Info")
    project_name = st.text_input("Project Name", value="Green Valley Homestead")
    col1, col2 = st.columns(2)
    with col1:
        length = st.number_input("Plot Length (ft)", min_value=50, max_value=1000,
                                  value=209, step=10)
    with col2:
        width = st.number_input("Plot Width (ft)", min_value=50, max_value=1000,
                                 value=209, step=10)

    total_sqft = length * width
    total_acres = total_sqft / 43560
    st.info(f"📐 Total: **{total_sqft:,} sq.ft** = **{total_acres:.2f} acres**")

    # ── Zone Sizes ───────────────────────────
    st.subheader("2. Zone Sizes (%)")
    st.caption("कुल 100% होना चाहिए")

    z0 = st.slider("Zone 0 — Residential", 5, 30, 10, step=5)
    z1 = st.slider("Zone 1 — Kitchen Garden", 5, 30, 15, step=5)
    z2 = st.slider("Zone 2 — Food Forest", 10, 50, 30, step=5)
    z3 = st.slider("Zone 3 — Pasture/Crops", 10, 50, 35, step=5)
    z4 = 100 - z0 - z1 - z2 - z3

    if z4 < 0:
        st.error(f"❌ Total {z0+z1+z2+z3}% है — 100% से ज़्यादा! Sliders घटाओ।")
        z4 = 0
    else:
        st.success(f"✅ Zone 4/5 (Buffer): {z4}%")

    # ── Features ─────────────────────────────
    st.subheader("3. Features")
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

    # ── Site Parameters ──────────────────────
    st.subheader("4. Site Parameters")
    slope_dir = st.selectbox(
        "Slope Direction",
        ["North-West to South-East (2%)",
         "North to South (1.5%)",
         "East to West (2%)",
         "South to North (1%)"],
    )
    borewell_loc = st.selectbox(
        "Borewell Location",
        ["North-East corner", "North-West corner",
         "South-East corner", "Centre-East"],
    )
    water_src = st.selectbox(
        "Primary Water Source",
        ["Borewell + Rainwater Harvesting",
         "Borewell only",
         "Municipality + Borewell",
         "Rainwater Harvesting only"],
    )

    # ── Output Options ────────────────────────
    st.subheader("5. Output")
    dpi_opt = st.select_slider("Resolution (DPI)",
                                options=[72, 150, 200, 300], value=150)

    # ════════════════════════════════════════
    #  🔑 LICENSE KEY — यहाँ जोड़ा
    # ════════════════════════════════════════
    st.divider()
    st.subheader("🔑 Access Key")

    # URL से key automatically पकड़ो
    # जैसे: ?status=ACCESS_KEY_99_ALPHA
    params  = st.query_params
    url_key = params.get("status", "")

    # Manual input box — URL key pre-fill होगी
    manual_key = st.text_input(
        "Enter Access Key",
        value=url_key,
        placeholder="Paste your key here...",
        help="Key URL में ?status= के बाद आती है"
    )

    # ── Valid Keys की list — यहाँ अपनी keys डाल ──
    VALID_KEYS = {
        "ACCESS_KEY_99_ALPHA",   # तेरी existing key
        "ACCESS_KEY_PRO_2026",   # नई key बना सकता है
        "UNLOCK_FULL_MAP_X1",    # और एक
    }

    # locked/unlocked decide करो
    key_entered = manual_key.strip()
    if key_entered in VALID_KEYS:
        locked = False
        st.success("✅ Full access unlocked!")
    elif key_entered == "":
        locked = True
        st.warning("🔒 Preview mode — Key डालो full map के लिए")
    else:
        locked = True
        st.error("❌ Invalid key — Watermark रहेगा")
    # ════════════════════════════════════════

    generate_btn = st.button("🗺️ Generate Map", type="primary",
                             use_container_width=True)


# ═════════════════════════════════════════════
#  MAIN AREA
# ═════════════════════════════════════════════

if generate_btn:

    # validation
    if z4 < 0:
        st.error("Zone percentages 100% से ज़्यादा हैं। Sidebar में fix करो।")
        st.stop()

    with st.spinner("🛠️ Blueprint बन रहा है..."):

        zone_fracs = {
            'z0': z0 / 100,
            'z1': z1 / 100,
            'z2': z2 / 100,
            'z3': z3 / 100,
            'z4': z4 / 100,
        }

        # ── Call your function ────────────────
        buf = generate_visual(
            L=float(length),
            W=float(width),
            name=project_name,
            zone_fracs=zone_fracs,
            has_pond=has_pond,
            has_solar=has_solar,
            has_greenhouse=has_greenhouse,
            has_poultry=has_poultry,
            has_borewell=has_borewell,
            has_compost=has_compost,
            has_swale=has_swale,
            slope_dir=slope_dir,
            borewell_loc=borewell_loc,
            water_src=water_src,
            num_tree_species=num_trees,
            locked=locked,        # ← यह अब key से control होता है
            dpi=dpi_opt,
        )

    # ── Show Map ─────────────────────────────
    st.image(buf, caption=f"{project_name} — {total_sqft:,} sq.ft.", use_column_width=True)

    # ── Download Button ───────────────────────
    buf.seek(0)
    st.download_button(
        label="⬇️ Download PNG Map",
        data=buf,
        file_name=f"{project_name.replace(' ','_')}_blueprint.png",
        mime="image/png",
    )

    # ── Zone Data Table ───────────────────────
    st.divider()
    st.subheader("📊 Zone Calculations")

    import pandas as pd
    df = pd.DataFrame({
        'Zone':        ['Zone 0', 'Zone 1', 'Zone 2', 'Zone 3', 'Zone 4/5', 'TOTAL'],
        'Description': ['Residential', 'Kitchen Garden', 'Food Forest',
                        'Pasture/Crops', 'Buffer/Fence', ''],
        'Area (sq.ft.)':[f"{total_sqft*z0/100:,.0f}",
                         f"{total_sqft*z1/100:,.0f}",
                         f"{total_sqft*z2/100:,.0f}",
                         f"{total_sqft*z3/100:,.0f}",
                         f"{total_sqft*z4/100:,.0f}",
                         f"{total_sqft:,.0f}"],
        'Percentage':  [f"{z0}%", f"{z1}%", f"{z2}%",
                        f"{z3}%", f"{z4}%", "100%"],
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    # Default placeholder
    st.info("👈 Left sidebar में अपना data भरो और **Generate Map** दबाओ।")

    st.markdown("""
    ### इस Tool से क्या मिलेगा?
    | Feature | Details |
    |---------|---------|
    | Professional Blueprint | AutoCAD जैसा top-down site plan |
    | Zone Calculations | हर zone की exact sq.ft. और % |
    | Water Flow | Borewell → Tank → Zones routing |
    | Dimension Lines | Plot के सभी measurements |
    | Legend + Compass | Professional map elements |
    | Download | High-res PNG (300 DPI तक) |
    | Watermark | Preview free, Unlock paid |
    """)
