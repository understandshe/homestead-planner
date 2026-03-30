import streamlit as st
import matplotlib
matplotlib.use('Agg') # सर्वर पर क्रैश रोकने के लिए जरूरी है
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import numpy as np
import io

# --- 1. SECURITY & CONFIG ---
MY_SECRET_TOKEN = "ACCESS_KEY_99_ALPHA" 
st.set_page_config(page_title="AI Homestead Architect 2026", layout="wide")

# URL से पेमेंट चेक करना (Error Handling के साथ)
try:
    is_paid = st.query_params.get("status") == MY_SECRET_TOKEN
except:
    is_paid = False

# --- 2. SIDEBAR: USER GUIDE (No Emojis) ---
st.sidebar.header("How to Use This Tool")
st.sidebar.markdown("""
1. Enter Plot Length & Width in feet.
2. Give your homestead a professional name.
3. Check the watermarked layout on the right.
4. Click 'Buy Me a Coffee' to pay $10.
5. After payment, you will be redirected to unlock the Full Report.
""")

st.sidebar.divider()
st.sidebar.info("Note: Standard 1-acre is approx. 209 x 209 ft.")

# --- 3. DATA ENGINE ---
def get_site_data(L, W):
    total_area = L * W
    perimeter = 2 * (L + W)
    zones = [
        {"Zone": "Zone 0 (Residential)", "Area": total_area * 0.10, "Usage": "House, Solar, Shed"},
        {"Zone": "Zone 1 (Garden)", "Area": total_area * 0.15, "Usage": "Vegetables & Poultry"},
        {"Zone": "Zone 2 (Orchard)", "Area": total_area * 0.30, "Usage": "Fruit Trees & Berries"},
        {"Zone": "Zone 3 (Pasture)", "Area": total_area * 0.35, "Usage": "Main Crops & Livestock"},
        {"Zone": "Zone 4/5 (Buffer)", "Area": total_area * 0.10, "Usage": "Timber & Fencing"}
    ]
    df = pd.DataFrame(zones)
    setup_cost = (perimeter * 3) + (total_area * 0.20) + 5000 
    est_income = (total_area * 0.30 / 225) * 180 
    return total_area, perimeter, df, setup_cost, est_income

# --- 4. VISUAL ENGINE (Clean Blueprint) ---
def generate_visual(L, W, name, locked=True):
    colors = {'z0': '#2C3E50', 'z1': '#27AE60', 'z2': '#2ECC71', 'z3': '#F1C40F', 'pond': '#3498DB'}
    
    fig, ax = plt.subplots(figsize=(12, 14), facecolor='white')
    ax.set_xlim(-10, L + 30); ax.set_ylim(-50, W + 20)
    
    # Plot Boundary
    ax.add_patch(patches.Rectangle((0, 0), L, W, fill=True, color='#F8F9FA', edgecolor='#2C3E50', lw=3))
    
    # Zone 0
    ax.add_patch(patches.Rectangle((5, W*0.75), L*0.3, W*0.2, facecolor=colors['z0'], alpha=0.8))
    plt.text(L*0.15, W*0.85, 'ZONE 0\nRESIDENTIAL', color='white', ha='center', va='center', fontweight='bold')

    # Zone 1
    ax.add_patch(patches.Rectangle((L*0.35, W*0.75), L*0.6, W*0.2, facecolor=colors['z1'], alpha=0.3, hatch='///'))
    plt.text(L*0.65, W*0.85, 'ZONE 1\nGARDEN', color='#1B5E20', ha='center', va='center', fontweight='bold')

    # Zone 2
    ax.add_patch(patches.Rectangle((5, W*0.35), L*0.95, W*0.35, facecolor=colors['z2'], alpha=0.2))
    plt.text(L/2, W*0.52, 'ZONE 2: FOOD FOREST', color='#1B5E20', ha='center', va='center', fontweight='bold')
    
    # Zone 3 & Pond
    ax.add_patch(patches.Rectangle((5, 5), L*0.6, W*0.25, facecolor=colors['z3'], alpha=0.2))
    pond_r = W * 0.12
    ax.add_patch(patches.Circle((L-pond_r-10, pond_r+10), pond_r, facecolor=colors['pond'], alpha=0.7))
    plt.text(L-pond_r-10, pond_r+10, 'POND', color='#154360', ha='center', va='center', fontweight='bold')
    
    # Title Block
    ax.add_patch(patches.Rectangle((0, -45), L, 35, facecolor='#2C3E50'))
    plt.text(L/2, -28, f"PROJECT: {name.upper()} | AREA: {L*W:,} SQFT", color='white', fontweight='bold', ha='center')

    # North Arrow
    plt.arrow(L+15, W-20, 0, 15, width=2, color='black', head_width=5)
    plt.text(L+15, W+2, 'N', fontsize=12, fontweight='bold')

    if locked:
        plt.text(L/2, W/2, 'PREVIEW MODE\nPAY $10 TO UNLOCK', fontsize=40, color='gray', alpha=0.2, ha='center', va='center', rotation=30)
    
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)
    plt.close(fig)
    return buf

# --- 5. MAIN INTERFACE ---
st.title("AI Homestead Architect 2026")
st.markdown("Professional Data-Driven Farm Planner")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Site Parameters")
    L = st.number_input("Length (ft)", min_value=50, value=209)
    W = st.number_input("Width (ft)", min_value=50, value=209)
    farm_name = st.text_input("Farm Name", "Alpha Farm")
    
    area, peri, zone_df, cost, income = get_site_data(L, W)
    
    if not is_paid:
        st.warning("Locked: Pay $10 to unlock Full Report")
        st.markdown(f'''<a href="https://buymeacoffee.com/m.mehul" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="60"></a>''', unsafe_allow_html=True)
    else:
        st.success("Pro Access Granted")

with col2:
    img = generate_visual(L, W, farm_name, locked=not is_paid)
    st.image(img, use_container_width=True)

if is_paid:
    st.divider()
    st.header("Site Analysis & Financial Report")
    t1, t2 = st.tabs(["Land Allocation", "Financials"])
    with t1:
        st.table(zone_df)
    with t2:
        st.write(f"Estimated Setup Cost: ${cost:,.2f}")
        st.write(f"Projected Annual Income: ${income:,.2f}")
    st.download_button("Download Blueprint", data=img, file_name="blueprint.png")

st.divider()
st.markdown("<center>© 2026 AI Homestead Engine</center>", unsafe_allow_html=True)
