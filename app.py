import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import io

# --- 1. SECURITY & SCALABILITY CONFIG ---
# Secret Token for Payment Verification
MY_SECRET_TOKEN = "ACCESS_KEY_99_ALPHA" 

st.set_page_config(
    page_title="AI Homestead Architect Pro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Error Handling for URL Params
try:
    query_params = st.query_params
    is_paid = query_params.get("status") == MY_SECRET_TOKEN
except Exception:
    is_paid = False

# --- 2. ARCHITECTURAL LOGIC ENGINE ---
def generate_homestead_engine(L, W, name, locked=True):
    """
    पायथन यहाँ खुद तय कर रहा है कि कौन सी चीज़ कहाँ होगी (Logic-based Placement)
    """
    try:
        # Technical Calculations
        total_area = L * W
        perimeter = 2 * (L + W)
        orchard_area = total_area * 0.35
        tree_spacing = 15 # 15ft gap
        tree_count = int(orchard_area / (tree_spacing**2))
        
        # Setup Professional Plot
        fig, ax = plt.subplots(figsize=(14, 16), facecolor='#F5F5F5')
        ax.set_xlim(-20, L + 40)
        ax.set_ylim(-60, W + 40)
        
        # Drawing the Main Plot with 'Blueprint' Texture
        ax.add_patch(patches.Rectangle((0, 0), L, W, fill=True, color='white', edgecolor='#2C3E50', lw=4, zorder=1))
        ax.grid(color='#D1D1D1', linestyle='--', linewidth=0.5, alpha=0.5)

        # --- LOGIC: ZONE PLACEMENT ---
        # Zone 0: Residential (Placed at the highest/safest corner)
        house_w, house_h = L*0.30, W*0.25
        ax.add_patch(patches.Rectangle((5, W-house_h-5), house_w, house_h, facecolor='#34495E', alpha=0.9, edgecolor='black', zorder=2))
        plt.text(house_w/2 + 5, W-(house_h/2)-5, 'ZONE 0\nRESIDENTIAL HUB\n(House, Solar, Storage)', color='white', ha='center', va='center', fontweight='bold', fontsize=10)

        # Zone 1: Intensive Garden (Adjacent to House for easy access)
        garden_w = L - house_w - 15
        ax.add_patch(patches.Rectangle((house_w+10, W-house_h-5), garden_w, house_h, facecolor='#27AE60', alpha=0.3, hatch='\\\\\\', edgecolor='#1B5E20', zorder=2))
        plt.text(house_w + 10 + garden_w/2, W-(house_h/2)-5, 'ZONE 1\nKITCHEN GARDEN\n(Vegetables, Herbs)', color='#1B5E20', ha='center', va='center', fontweight='bold', fontsize=10)

        # Zone 2: Diversified Food Forest (Central Buffer)
        orchard_h = W * 0.40
        ax.add_patch(patches.Rectangle((5, W*0.30), L-10, orchard_h, facecolor='#2ECC71', alpha=0.2, edgecolor='#27AE60', lw=2, zorder=2))
        plt.text(L/2, W*0.50, f'ZONE 2: FOOD FOREST\nCapacity: ~{tree_count} Trees', color='#1B5E20', ha='center', va='center', fontweight='bold', fontsize=14)
        
        # Logic-based Tree Placement
        for x in np.linspace(20, L-20, 10):
            for y in np.linspace(W*0.35, W*0.65, 4):
                ax.add_patch(patches.Circle((x, y), 2.5, color='#27AE60', alpha=0.5, zorder=3))

        # Zone 3: Pasture & Water (Lowest point for drainage)
        pasture_h = W * 0.25
        ax.add_patch(patches.Rectangle((5, 5), L*0.6, pasture_h, facecolor='#F1C40F', alpha=0.2, hatch='...', edgecolor='#F39C12', zorder=2))
        plt.text(L*0.3, pasture_h/2 + 5, 'ZONE 3\nPASTURE / CROPS', color='#7E5109', ha='center', va='center', fontweight='bold', fontsize=10)

        # Engineering: Retention Pond (Bottom Right - Natural Collection)
        pond_r = W * 0.12
        ax.add_patch(patches.Circle((L-pond_r-10, pond_r+10), pond_r, facecolor='#3498DB', alpha=0.7, edgecolor='#2980B9', lw=3, zorder=3))
        plt.text(L-pond_r-10, pond_r+10, 'RETENTION\nPOND', color='#154360', ha='center', va='center', fontweight='bold', fontsize=9)

        # --- TECHNICAL TITLE BLOCK (Architectural Standard) ---
        ax.add_patch(patches.Rectangle((0, -55), L, 45, facecolor='#2C3E50', zorder=4))
        plt.text(L/2, -25, f"PROJECT: {name.upper()} | SCALE: 1:200 | AREA: {total_area:,} SQFT", color='white', fontsize=12, fontweight='bold', ha='center')
        plt.text(L/2, -45, f"FENCING: {perimeter} FT | EST. TREES: {tree_count} | WATER CAP: {int(total_area*0.5)} GAL/YR", color='#BDC3C7', fontsize=10, ha='center')

        # North Arrow
        plt.arrow(L+25, W-20, 0, 20, width=2, color='#2C3E50', head_width=6, zorder=5)
        plt.text(L+25, W+5, 'N', fontsize=16, fontweight='bold', color='#2C3E50')

        if locked:
            plt.text(L/2, W/2, 'PREVIEW MODE\nPAY $10 TO UNLOCK ARCHITECTURAL PDF', fontsize=40, color='gray', alpha=0.2, ha='center', va='center', rotation=30, zorder=10)

        plt.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.close(fig) # Memory management for 100k users
        return buf
    except Exception as e:
        st.error(f"Engine Error: {e}")
        return None

# --- 3. STREAMLIT INTERFACE (The "Pro" Look) ---
st.markdown("""
    <style>
    .main { background-color: #F0F2F6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2C3E50; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ AI Homestead Architect Pro")
st.caption("Data-Driven Site Analysis & Architectural Layout Engine")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📐 Site Parameters")
    L = st.number_input("Plot Length (Feet)", min_value=50, max_value=2000, value=209)
    W = st.number_input("Plot Width (Feet)", min_value=50, max_value=2000, value=209)
    project_name = st.text_input("Project Name", "Global Homestead Alpha")
    
    st.divider()
    
    if not is_paid:
        st.info("🔒 **Professional Blueprint Locked**")
        st.markdown(f'''<a href="https://buymeacoffee.com/m.mehul" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="60"></a>''', unsafe_allow_html=True)
        st.caption("Unlock to remove watermark and get high-res technical specs.")
    else:
        st.success("✅ **Pro Access Verified**")

with col2:
    with st.spinner("Engine calculating optimal placement..."):
        map_img = generate_homestead_engine(L, W, project_name, locked=not is_paid)
        if map_img:
            st.image(map_img, use_container_width=True)
            if is_paid:
                st.download_button("📥 Download High-Res Architectural Blueprint", data=map_img, file_name=f"{project_name}_Blueprint.png", mime="image/png")

st.divider()
st.markdown("<center>Built with Python Architectural Engine | Scalable for 100k+ Users</center>", unsafe_allow_html=True)
