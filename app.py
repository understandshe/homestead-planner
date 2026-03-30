import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

# --- 1. SECURITY & CONFIG ---
# ये तेरा सीक्रेट टोकन है, इसे BMC के 'Redirect URL' में डालना
MY_SECRET_TOKEN = "ACCESS_KEY_99_ALPHA" 

st.set_page_config(page_title="AI Homestead Planner | Professional Layouts", layout="wide")

# URL से चेक करना कि पेमेंट हुई या नहीं
query_params = st.query_params
is_paid = query_params.get("status") == MY_SECRET_TOKEN

# --- 2. SIDEBAR: USER GUIDE (सबकी समझ के लिए) ---
st.sidebar.header("📖 How to Use This Tool")
st.sidebar.markdown(f"""
Welcome! Follow these simple steps to design your dream 1-acre homestead:

1. **📏 Set Dimensions:** Enter the Length and Width of your plot in feet.
2. **✍️ Name Your Farm:** Give your homestead a unique name.
3. **🔍 Preview:** Look at the watermarked layout on the right.
4. **🔓 Unlock Pro:** Click the **Buy Me a Coffee** button to pay $10.
5. **📥 Download:** After payment, you'll be redirected back here to download your **High-Res Technical Blueprint** without any watermark!
""")

st.sidebar.divider()
st.sidebar.info("💡 *Note: A standard 1-acre plot is roughly 209 x 209 feet.*")

# --- 3. MAIN UI & INPUTS ---
st.title("🏡 Professional 1-Acre Homestead Planner")
st.markdown("#### *Tailored to your desires. Designed for your future.*")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 🛠️ Customize Your Layout")
    length = st.number_input("Length of Plot (ft)", min_value=50, max_value=1000, value=209)
    width = st.number_input("Width of Plot (ft)", min_value=50, max_value=1000, value=209)
    farm_name = st.text_input("Homestead Name", "My Dream Farm")
    
    st.divider()
    
    if not is_paid:
        st.warning("🔒 **Pro Features Locked**")
        st.write("Pay $10 to remove the watermark and download your custom high-resolution blueprint.")
        
        # --- UPDATED PAYMENT LINK ---
        # झोल: BMC में Redirect URL ये डालना: https://your-app.streamlit.app/?status=ACCESS_KEY_99_ALPHA
        bmc_link = "https://buymeacoffee.com/m.mehul" 
        
        st.markdown(f'''
            <a href="{bmc_link}" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >
            </a>
        ''', unsafe_allow_stdio=True)
        st.caption("Secure Payment via Stripe / PayPal")
    else:
        st.success("✅ **Payment Verified!**")
        st.balloons()

# --- 4. THE MASTERPLAN GENERATOR (Python Logic) ---
def generate_pro_map(l, w, name, locked=True):
    # Professional Colors for different desires
    colors = {'house': '#2C3E50', 'garden': '#27AE60', 'orchard': '#2ECC71', 'pasture': '#F1C40F', 'pond': '#3498DB'}
    
    fig, ax = plt.subplots(figsize=(12, 12), facecolor='white')
    ax.set_xlim(0, l + 20)
    ax.set_ylim(0, w + 20)
    
    # 1. Plot Boundary
    ax.add_patch(patches.Rectangle((5, 5), l, w, fill=False, edgecolor='#333', lw=4))
    
    # 2. Zone 0: Residential (For your comfort)
    ax.add_patch(patches.Rectangle((10, w-55), l*0.3, 50, facecolor=colors['house'], alpha=0.8))
    plt.text(l*0.15 + 5, w-30, 'ZONE 0\nResidential Area', color='white', ha='center', fontweight='bold')
    
    # 3. Zone 1: Intensive Garden (For fresh veggies)
    ax.add_patch(patches.Rectangle((l*0.35 + 5, w-55), l*0.6, 50, facecolor=colors['garden'], alpha=0.3, hatch='///'))
    plt.text(l*0.65, w-30, 'ZONE 1\nKitchen Garden', color='#1B5E20', ha='center', fontweight='bold')
    
    # 4. Zone 2: Food Forest (For your fruits)
    ax.add_patch(patches.Rectangle((10, w*0.35), l*0.95, w*0.35, facecolor=colors['orchard'], alpha=0.2, edgecolor=colors['orchard']))
    plt.text(l/2, w*0.52, 'ZONE 2: DIVERSIFIED FOOD FOREST', color='#1B5E20', ha='center', fontweight='bold', fontsize=14)
    
    # 5. Zone 3: Pasture & Pond (For livestock & water)
    ax.add_patch(patches.Rectangle((10, 10), l*0.6, w*0.25, facecolor=colors['pasture'], alpha=0.2, hatch='..'))
    ax.add_patch(patches.Circle((l*0.85, w*0.2), w*0.15, facecolor=colors['pond'], alpha=0.6, edgecolor='#185FA5'))
    plt.text(l*0.85, w*0.2, 'POND', color='#0C447C', ha='center', fontweight='bold')
    
    # Watermark Logic
    if locked:
        plt.text(l/2, w/2, 'PREVIEW ONLY\nPAY $10 TO DOWNLOAD', fontsize=50, color='gray', alpha=0.2, ha='center', va='center', rotation=30)
    
    plt.title(f"MASTERPLAN: {name.upper()}\nTechnical Site Analysis", fontsize=18, fontweight='bold', pad=20)
    plt.axis('off')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    return buf

# --- 5. DISPLAY & DOWNLOAD ---
with col2:
    map_buffer = generate_pro_map(length, width, farm_name, locked=not is_paid)
    st.image(map_buffer, caption=f"Technical Layout for {farm_name}", use_container_width=True)
    
    if is_paid:
        st.download_button(
            label="📥 Download High-Resolution Blueprint (PNG)",
            data=map_buffer,
            file_name=f"{farm_name}_layout.png",
            mime="image/png"
        )
        if st.button("Start New Project"):
            st.query_params.clear()
            st.rerun()

# --- 6. WHY THIS LAYOUT? (Satisfying Desires) ---
st.divider()
st.markdown("""
### 🌟 Why this layout works for you:
- **Optimized Zoning:** We place your house (Zone 0) near the garden (Zone 1) for easy access.
- **Sustainable Water:** The pond is placed at the lowest point for natural rainwater harvesting.
- **High Yield:** Zone 2 is designed for a high-density food forest to maximize your fruit production.
""")
