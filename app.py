import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import io

# --- 1. SECURITY & 2026 CONFIG ---
MY_SECRET_TOKEN = "ACCESS_KEY_99_ALPHA" 
st.set_page_config(page_title="AI Homestead Architect 2026", layout="wide", page_icon="🏡")

# URL से पेमेंट चेक करना
query_params = st.query_params
is_paid = query_params.get("status") == MY_SECRET_TOKEN

# --- 2. SIDEBAR: USER INTERACTION (यूजर को समझाने के लिए) ---
st.sidebar.header("📖 How to Use This Tool")
st.sidebar.markdown("""
Welcome to the **2026 AI Homestead Planner**. Follow these steps:

1. **📏 Set Dimensions:** Enter your plot's Length & Width in feet.
2. **✍️ Name Your Project:** Give your farm a professional name.
3. **🔍 Preview:** Check the watermarked layout on the right.
4. **🔓 Unlock Pro:** Click the **Buy Me a Coffee** button ($10).
5. **📥 Download:** After payment, you'll be redirected back to unlock the **Full Data Report & High-Res Blueprint**.
""")

st.sidebar.divider()
st.sidebar.info("💡 *A standard 1-acre plot is approx. 209 x 209 feet.*")

# --- 3. DATA ENGINE (Live Calculations) ---
def get_site_data(L, W):
    total_area = L * W
    perimeter = 2 * (L + W)
    
    # Zone Data
    zones = [
        {"Zone": "Zone 0 (Residential)", "Area": total_area * 0.10, "Usage": "House, Solar, Shed"},
        {"Zone": "Zone 1 (Garden)", "Area": total_area * 0.15, "Usage": "Vegetables & Poultry"},
        {"Zone": "Zone 2 (Orchard)", "Area": total_area * 0.30, "Usage": "Fruit Trees & Berries"},
        {"Zone": "Zone 3 (Pasture)", "Area": total_area * 0.35, "Usage": "Main Crops & Livestock"},
        {"Zone": "Zone 4/5 (Buffer)", "Area": total_area * 0.10, "Usage": "Timber & Fencing"}
    ]
    df = pd.DataFrame(zones)
    
    # Financials (2026 Global Estimates)
    setup_cost = (perimeter * 3) + (total_area * 0.20) + 5000 # Fencing + Irrigation + Misc
    est_income = (total_area * 0.30 / 225) * 180 # $180 profit per tree/year
    
    return total_area, perimeter, df, setup_cost, est_income

# --- 4. VISUAL ENGINE ---
def generate_visual(L, W, name, locked=True):
    fig, ax = plt.subplots(figsize=(12, 12), facecolor='#F8F9FA')
    ax.set_xlim(-10, L + 20); ax.set_ylim(-40, W + 20)
    
    # Plot Boundary
    ax.add_patch(patches.Rectangle((0, 0), L, W, fill=True, color='white', edgecolor='#2C3E50', lw=3))
    
    # Zoning Visuals
    ax.add_patch(patches.Rectangle((5, W*0.75), L*0.3, W*0.2, facecolor='#34495E', alpha=0.8)) # Zone 0
    ax.add_patch(patches.Rectangle((L*0.35, W*0.75), L*0.6, W*0.2, facecolor='#27AE60', alpha=0.3, hatch='///')) # Zone 1
    ax.add_patch(patches.Rectangle((5, W*0.35), L*0.95, W*0.35, facecolor='#2ECC71', alpha=0.2)) # Zone 2
    
    # Title Block
    ax.add_patch(patches.Rectangle((0, -35), L, 30, facecolor='#2C3E50'))
    plt.text(L/2, -20, f"PROJECT: {name.upper()} | AREA: {L*W:,} SQFT", color='white', fontweight='bold', ha='center')
    
    if locked:
        plt.text(L/2, W/2, 'PREVIEW MODE\nPAY $10 TO UNLOCK FULL REPORT', fontsize=40, color='gray', alpha=0.2, ha='center', va='center', rotation=30)
    
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)
    plt.close(fig)
    return buf

# --- 5. MAIN INTERFACE ---
st.title("🏗️ AI Homestead Architect Pro (2026 Edition)")
st.markdown("#### *The World's Most Advanced Data-Driven Farm Planner*")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📐 Site Parameters")
    L = st.number_input("Length of Plot (ft)", min_value=50, value=209)
    W = st.number_input("Width of Plot (ft)", min_value=50, value=209)
    farm_name = st.text_input("Homestead Name", "Global Alpha Farm")
    
    area, peri, zone_df, cost, income = get_site_data(L, W)
    
    st.metric("Total Area", f"{area:,} sq.ft")
    st.metric("Perimeter", f"{peri:,} ft")
    
    if not is_paid:
        st.warning("🔒 **Full Report Locked**")
        st.markdown(f'''<a href="https://buymeacoffee.com/m.mehul" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="60"></a>''', unsafe_allow_html=True)
    else:
        st.success("✅ **Pro Access Granted**")

with col2:
    img = generate_visual(L, W, farm_name, locked=not is_paid)
    st.image(img, use_container_width=True)

# --- 6. DATA REPORT (The "Claude-Style" Data) ---
if is_paid:
    st.divider()
    st.header("📊 2026 Site Analysis & Financial Report")
    
    t1, t2, t3 = st.tabs(["📐 Land Allocation", "💰 Financial Projections", "🌱 Technical Specs"])
    
    with t1:
        st.subheader("Zone-wise Area Breakdown")
        st.table(zone_df)
        
    with t2:
        st.subheader("Investment & ROI (USD)")
        c1, c2 = st.columns(2)
        c1.metric("Estimated Setup Cost", f"${cost:,.2f}")
        c2.metric("Projected Annual Income", f"${income:,.2f}")
        st.info("Note: Income projections are based on mature orchard yields (Year 3+).")
        
    with t3:
        st.subheader("Planting & Infrastructure")
        st.write(f"- **Fruit Tree Capacity:** {int(area*0.30/225)} Units (15x15 spacing)")
        st.write(f"- **Water Storage Needed:** {int(area*0.05)} Gallons (Rainwater Harvesting)")
        st.write(f"- **Fencing Material:** {peri + 50} ft (Chain-link recommended)")

    st.download_button("📥 Download Full Architectural Report", data=img, file_name=f"{farm_name}_2026_Report.png")
else:
    with st.expander("❓ What's included in the Pro Report?"):
        st.write("""
        - **Detailed Area Breakdown:** Exact sq.ft for every zone.
        - **Financial Estimates:** Setup costs and annual income projections.
        - **Planting Guide:** Number of trees and water requirements.
        - **High-Res Blueprint:** Clean, watermark-free architectural map.
        """)

st.divider()
st.markdown("<center>© 2026 AI Homestead Engine | Professional Grade Architecture</center>", unsafe_allow_html=True)
