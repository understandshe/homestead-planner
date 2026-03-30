import streamlit as st
import matplotlib
matplotlib.use('Agg') # सर्वर पर क्रैश रोकने के लिए
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, FancyBboxPatch, Polygon
import numpy as np
import pandas as pd
import io

# --- 1. SECURITY & CONFIG ---
MY_SECRET_TOKEN = "ACCESS_KEY_99_ALPHA" 
st.set_page_config(page_title="AI Homestead Architect Pro", layout="wide", page_icon="🏡")

# URL से पेमेंट चेक करना
query_params = st.query_params
is_paid = query_params.get("status") == MY_SECRET_TOKEN

# --- 2. SIDEBAR: USER GUIDE ---
st.sidebar.header("📖 How to Use This Tool")
st.sidebar.markdown("""
1. **📏 Set Dimensions:** Enter Plot Length & Width in feet.
2. **✍️ Name Your Project:** Give your farm a professional name.
3. **🔍 Preview:** Check the watermarked layout on the right.
4. **🔓 Unlock Pro:** Click **Buy Me a Coffee** ($10).
5. **📥 Download:** Get the **High-Res Blueprint** without watermark.
""")
st.sidebar.divider()
st.sidebar.info("💡 *Standard 1-acre is approx. 209 x 209 ft.*")

# --- 3. DATA ENGINE (For Tables) ---
def get_site_data(L, W):
    total_area = L * W
    perimeter = 2 * (L + W)
    setup_cost = (perimeter * 3) + (total_area * 0.20) + 5000 
    est_income = (total_area * 0.30 / 225) * 180 
    return total_area, perimeter, setup_cost, est_income

# --- 4. YOUR PREMIUM VISUAL ENGINE ---
def generate_visual(L, W, name, locked=True):
    # Colors
    c = {
        'z0': '#E6F1FB', 'z0s': '#185FA5',
        'z1': '#EAF3DE', 'z1s': '#3B6D11',
        'z2': '#EAF3DE', 'z2s': '#639922',
        'z3': '#FAEEDA', 'z3s': '#854F0B',
        'z4': '#F1EFE8', 'z4s': '#5F5E5A',
        'water': '#85B7EB', 'text': '#2C2C2A', 'dim': '#888780'
    }
    
    fig, ax = plt.subplots(figsize=(16, 14), facecolor='#f8f7f2')
    ax.set_facecolor('#f8f7f2')
    ax.set_xlim(-60, L+180) # Space for data table on right
    ax.set_ylim(-80, W+60)
    
    # Plot boundary
    ax.add_patch(patches.Rectangle((0,0), L, W, fill=False, edgecolor=c['text'], lw=1.5))
    
    # Dimension lines
    ax.plot([0,L], [W+15,W+15], '--', color=c['dim'], lw=0.8)
    ax.text(L/2, W+22, f'{L} ft', ha='center', fontsize=9, color=c['dim'])
    ax.plot([L+15,L+15], [0,W], '--', color=c['dim'], lw=0.8)
    ax.text(L+22, W/2, f'{W} ft', rotation=90, va='center', fontsize=9, color=c['dim'])
    
    # Zone 0 - House
    z0w, z0h = L*0.35, W*0.25
    ax.add_patch(patches.Rectangle((0,W-z0h), z0w, z0h, facecolor=c['z0'], edgecolor=c['z0s'], lw=1))
    ax.text(z0w/2, W-z0h/2, 'ZONE 0\nHouse', ha='center', va='center', fontsize=10, weight='bold', color=c['z0s'])
    
    # Zone 1 - Garden
    z1w, z1h = L*0.65, W*0.25
    ax.add_patch(patches.Rectangle((z0w,W-z1h), z1w, z1h, facecolor=c['z1'], edgecolor=c['z1s'], lw=1))
    ax.text(z0w+z1w/2, W-z1h/2, 'ZONE 1\nGarden', ha='center', va='center', fontsize=10, weight='bold', color=c['z1s'])
    
    # Zone 2 - Food Forest
    z2h = W*0.35
    z2y = W-z0h-z2h
    ax.add_patch(patches.Rectangle((0,z2y), L, z2h, facecolor=c['z2'], edgecolor=c['z2s'], lw=1))
    # Simple Tree Markers
    for tx in np.linspace(40, L-40, 6):
        ax.add_patch(Circle((tx, z2y+z2h/2), 12, facecolor='#97C459', edgecolor=c['z2s'], lw=0.5))
    ax.text(L/2, z2y+z2h/2, 'ZONE 2 - Food Forest', ha='center', va='center', fontsize=12, weight='bold', color=c['z2s'])
    
    # Zone 3 - Crops
    z3w, z3h = L*0.70, W*0.30
    z3y = z2y-z3h
    ax.add_patch(patches.Rectangle((0,z3y), z3w, z3h, facecolor=c['z3'], edgecolor=c['z3s'], lw=1))
    ax.text(z3w/2, z3y+z3h/2, 'ZONE 3 - Crops', ha='center', va='center', fontsize=11, weight='bold', color=c['z3s'])
    
    # Pond
    pond_r = W*0.12
    ax.add_patch(Circle((L-pond_r-15, pond_r+15), pond_r, facecolor=c['water'], edgecolor='#2980B9', lw=2))
    ax.text(L-pond_r-15, pond_r+15, 'POND', ha='center', va='center', fontsize=10, weight='bold', color='#154360')
    
    # Zone 4 - Buffer
    z4h = W*0.10
    ax.add_patch(patches.Rectangle((0,0), L, z4h, facecolor=c['z4'], edgecolor=c['z4s'], lw=1))
    
    # Compass
    cx, cy = L+50, W-50
    ax.add_patch(Circle((cx,cy), 18, fill=False, edgecolor=c['dim'], lw=0.5))
    ax.text(cx, cy-25, 'N', ha='center', fontsize=10, weight='bold')
    
    # Title block
    ax.add_patch(patches.Rectangle((-60,-75), L+240, 50, facecolor='#2C3E50', lw=0))
    ax.text(L/2, -55, f'PROJECT: {name.upper()} | AREA: {L*W:,} SQ.FT.', ha='center', fontsize=12, weight='bold', color='white')
    
    # Watermark
    if locked:
        ax.text(L/2, W/2, 'PREVIEW MODE\nPAY $10 TO UNLOCK', ha='center', va='center', fontsize=35, color='gray', alpha=0.2, weight='bold')
    
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=200, facecolor='#f8f7f2')
    plt.close(fig)
    return buf

# --- 5. MAIN INTERFACE ---
st.title("🏗️ AI Homestead Architect Pro (2026)")
st.markdown("#### *Professional Data-Driven Farm Planner*")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📐 Site Parameters")
    L = st.number_input("Length (ft)", min_value=50, value=209)
    W = st.number_input("Width (ft)", min_value=50, value=209)
    farm_name = st.text_input("Farm Name", "Alpha Farm")
    
    area, peri, cost, income = get_site_data(L, W)
    
    if not is_paid:
        st.warning("🔒 **Full Report Locked**")
        st.markdown(f'''<a href="https://buymeacoffee.com/m.mehul" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="60"></a>''', unsafe_allow_html=True)
    else:
        st.success("✅ **Pro Access Granted**")

with col2:
    img = generate_visual(L, W, farm_name, locked=not is_paid)
    st.image(img, use_container_width=True)

if is_paid:
    st.divider()
    st.header("📊 Site Analysis & Financial Report")
    c1, c2 = st.columns(2)
    c1.metric("Estimated Setup Cost", f"${cost:,.2f}")
    c2.metric("Projected Annual Income", f"${income:,.2f}")
    st.download_button("📥 Download High-Res Blueprint", data=img, file_name=f"{farm_name}_Blueprint.png")

st.divider()
st.markdown("<center>© 2026 AI Homestead Engine | Professional Grade Architecture</center>", unsafe_allow_html=True)
