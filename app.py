"""
Homestead Map Generator - Streamlit Web App
Run: streamlit run app.py
"""

import streamlit as st
import io
from homestead_map import generate_visual, generate_pdf_report, get_plot_category, CURRENCY_DATA
import streamlit as st
# AFFILIATE PRODUCT DATABASE WITH DYNAMIC CTA LOGIC
AFFILIATE_PRODUCTS = {
    1: {
        "name": "Self Sufficient Backyard (ClickBank)",
        "url": "https://74c1ailom3rncwaldylac5xc0m.hop.clickbank.net",
        "ctas": {
            "small": "Grow fresh food from your small rooftop or balcony and save up to $1,600!",
            "medium": "Transform your kitchen garden into a goldmine and start self-sufficient farming today!",
            "large": "Discover how to 10x your annual $2,400 income from your vast land! Click to learn the secret!"
        }
    },
    2: {
        "name": "Energy Revolution System (ClickBank)",
        "url": "https://d92ebgtuifnm3o39udsrbrdn9y.hop.clickbank.net",
        "ctas": {
            "small": "Cut your electricity bill to ZERO for small homes! Generate power without heavy solar panels.",
            "medium": "Power your entire farm and pumps with FREE electricity. Say goodbye to heavy bills forever!",
            "large": "Save the $3,105 solar cost mentioned in reports! Go off-grid for your entire land for just $100!"
        }
    },
    3: {
        "name": "My Shed Plans (ClickBank)",
        "url": "https://3a412hnji5uyct5hi-ghpwvre4.hop.clickbank.net",
        "ctas": {
            "small": "Download perfect shed and storage designs for your small yard here.",
            "medium": "Get 16,000+ professional shed and workshop designs for your property!",
            "large": "World's most accurate architecture plans for building homes and large warehouses in Zone 0!"
        }
    },
    4: {
        "name": "Heavy Duty Fencing Mesh (Amazon)",
        "url": "https://amzn.to/3PEkBMV",
        "ctas": {
            "small": "Secure your boundary at low cost. Easy to install and durable fencing!",
            "medium": "Reduce the $3,548 fencing cost! This heavy-duty mesh secures your entire property.",
            "large": "Best privacy and security solution for large farmland. Order your fencing kit now!"
        }
    },
    5: {
        "name": "240FT Drip Irrigation Kit (Amazon)",
        "url": "https://amzn.to/4dgxFBX",
        "ctas": {
            "small": "Automatic watering for small kitchen gardens. Stop worrying about watering plants!",
            "medium": "Automate irrigation for your entire land. Save water and boost yields!",
            "large": "Manage the $1,996 drip system budget. Professional irrigation kit for large farms here!"
        }
    },
    6: {
        "name": "VIVOSUN Submersible Pump (Amazon)",
        "url": "https://amzn.to/3NWPEmC",
        "ctas": {
            "small": "The quietest and most powerful pump for your small fish tank or aquarium.",
            "medium": "Ultra-quiet submersible pump for garden ponds and fountains. Easy setup!",
            "large": "Perfect 800GPH pump for drainage and water flow systems. Buy now!"
        }
    }
}

BMC_URL = "https://buymeacoffee.com/m.mehul"
WATERMARK_TEXT = "chundalgardens.com"


def get_cta_size(total_sqft):
    """Determine CTA size based on total area"""
    if total_sqft < 20000:
        return "small"
    elif total_sqft <= 100000:
        return "medium"
    else:
        return "large"


def get_affiliate_products(total_sqft):
    """Get all affiliate products with appropriate CTAs for the area size"""
    cta_size = get_cta_size(total_sqft)
    products = []
    for pid, product in AFFILIATE_PRODUCTS.items():
        products.append({
            "name": product["name"],
            "url": product["url"],
            "cta": product["ctas"][cta_size]
        })
    return products


# STREAMLIT PAGE CONFIGURATION
st.set_page_config(
    page_title="Homestead Map Generator",
    page_icon="",
    layout="wide",
)

# Custom CSS - NO EMOJIS, fixed button text color
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    h1 { font-size: 1.6rem; }
    
    .affiliate-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .affiliate-card h4 {
        color: #2E7D32;
        margin-bottom: 10px;
    }
    
    .affiliate-cta {
        font-style: italic;
        color: #333333;
        margin: 10px 0;
    }
    
    .affiliate-link {
        background-color: #FF6B35;
        color: #FFFFFF !important;
        padding: 10px 20px;
        border-radius: 25px;
        text-decoration: none;
        display: inline-block;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .affiliate-link:hover {
        background-color: #E55100;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255,107,53,0.4);
    }
    
    .bmc-support-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        color: white;
    }
    
    .stButton>button {
        color: #FFFFFF !important;
        font-weight: bold;
    }
    
    .stDownloadButton>button {
        color: #FFFFFF !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# SESSION STATE INITIALIZATION
if 'show_bmc' not in st.session_state:
    st.session_state.show_bmc = False
if 'download_pending' not in st.session_state:
    st.session_state.download_pending = None
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'map_buffer' not in st.session_state:
    st.session_state.map_buffer = None
if 'pdf_buffer' not in st.session_state:
    st.session_state.pdf_buffer = None

# HEADER
st.title("Homestead Site Plan Generator")
st.caption("Enter your site details to generate professional blueprint instantly")

# SIDEBAR - USER FORM
with st.sidebar:
    st.header("Site Details")
    
    # Basic Info
    st.subheader("1. Basic Information")
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
    st.info(f"Total: {total_sqft:,} sq.ft = {total_acres:.2f} acres")
    
    # Currency Selection
    st.subheader("2. Currency Selection")
    currency_options = [f"{code} - {data['name']}" for code, data in CURRENCY_DATA.items()]
    selected_currency = st.selectbox("Select Currency", currency_options)
    currency_code = selected_currency.split(" - ")[0]
    
    # Determine category
    cta_category = get_cta_size(total_sqft)
    category = get_plot_category(total_sqft)
    if category == "small":
        st.success("Small Plot Category - Optimized for urban/suburban homesteads")
    elif category == "medium":
        st.success("Medium Plot Category - Perfect for rural homesteads")
    else:
        st.success("Large Plot Category - Ideal for farm-scale operations")
    
    # Zone Sizes
    st.subheader("3. Zone Sizes (%)")
    st.caption("Must total 100%")
    
    z0 = st.slider("Zone 0 - Residential", 5, 30, 10, step=5)
    z1 = st.slider("Zone 1 - Kitchen Garden", 5, 30, 15, step=5)
    z2 = st.slider("Zone 2 - Food Forest", 10, 50, 30, step=5)
    z3 = st.slider("Zone 3 - Pasture/Crops", 10, 50, 35, step=5)
    z4 = 100 - z0 - z1 - z2 - z3
    
    if z4 < 0:
        st.error(f"Total {z0+z1+z2+z3}% exceeds 100%! Adjust sliders.")
        z4 = 0
    else:
        st.success(f"Zone 4/5 (Buffer): {z4}%")
    
    # House Position
    st.subheader("4. House Position")
    house_position = st.selectbox(
        "Where is your house located?",
        ["North", "South", "East", "West", "Center"]
    )
    
    # Custom Trees
    st.subheader("5. Custom Tree Species")
    st.caption("Enter tree names (one per line, max 12)")
    trees_input = st.text_area("Tree Species", 
                              value="Apple\nOrange\nMango\nLemon",
                              height=100)
    custom_trees = [t.strip() for t in trees_input.split('\n') if t.strip()][:12]
    
    # Features
    st.subheader("6. Site Features")
    col_a, col_b = st.columns(2)
    with col_a:
        has_pond = st.checkbox("Pond", value=True)
        has_solar = st.checkbox("Solar", value=True)
        has_greenhouse = st.checkbox("Greenhouse", value=True)
    with col_b:
        has_poultry = st.checkbox("Poultry", value=True)
        has_borewell = st.checkbox("Borewell", value=True)
        has_compost = st.checkbox("Compost", value=True)
        has_swale = st.checkbox("Swale", value=True)
    
    # Site Parameters
    st.subheader("7. Site Parameters")
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
    
    # Output Options
    st.subheader("8. Output Options")
    watermark_enabled = st.checkbox("Enable Watermark (Recommended)", value=True)
    dpi_opt = st.select_slider("Resolution (DPI)",
                                options=[72, 150, 200, 300], value=150)
    
    generate_btn = st.button("Generate Map", type="primary",
                             use_container_width=True)

# MAIN AREA - GENERATION LOGIC
if generate_btn:
    if z4 < 0:
        st.error("Zone percentages exceed 100%. Please adjust in sidebar.")
        st.stop()
    
    with st.spinner("Creating your blueprint..."):
        zone_fracs = {
            'z0': z0 / 100,
            'z1': z1 / 100,
            'z2': z2 / 100,
            'z3': z3 / 100,
            'z4': z4 / 100,
        }
        
        # Generate map image
        map_buf = generate_visual(
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
            num_tree_species=len(custom_trees),
            house_position=house_position,
            custom_trees=custom_trees,
            watermark_enabled=watermark_enabled,
            watermark_text=WATERMARK_TEXT,
            dpi=dpi_opt,
        )
        
        # Get affiliate products based on area
        affiliate_products = get_affiliate_products(total_sqft)
        
        # Generate PDF report
        pdf_buf = generate_pdf_report(
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
            num_tree_species=len(custom_trees),
            house_position=house_position,
            custom_trees=custom_trees,
            affiliate_products=affiliate_products,
            currency_code=currency_code,
            watermark_enabled=watermark_enabled,
            watermark_text=WATERMARK_TEXT
        )
        
        # Store in session state
        st.session_state.map_buffer = map_buf
        st.session_state.pdf_buffer = pdf_buf
        st.session_state.generated = True
        st.session_state.affiliate_products = affiliate_products
        st.session_state.project_name = project_name
        st.session_state.total_sqft = total_sqft
        st.session_state.currency_code = currency_code
        st.session_state.z0 = z0
        st.session_state.z1 = z1
        st.session_state.z2 = z2
        st.session_state.z3 = z3
        st.session_state.z4 = z4

# Display results if generated
if st.session_state.generated and st.session_state.map_buffer:
    
    # Show Map
    st.image(st.session_state.map_buffer, 
             caption=f"{st.session_state.project_name} - {st.session_state.total_sqft:,} sq.ft.", 
             use_container_width=True)
    
    # COST ANALYSIS SECTION
    st.divider()
    st.subheader("Financial Analysis")
    
    from homestead_map import COST_ESTIMATES, convert_currency, format_currency
    
    category = get_plot_category(st.session_state.total_sqft)
    costs = COST_ESTIMATES[category]
    currency_code = st.session_state.get('currency_code', 'USD')
    
    def cvt(amount):
        return convert_currency(amount, currency_code)
    
    setup_min, sym = cvt(costs["setup_cost"]["min"])
    setup_max, _ = cvt(costs["setup_cost"]["max"])
    income_min, _ = cvt(costs["annual_income"]["min"])
    income_max, _ = cvt(costs["annual_income"]["max"])
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.metric("Setup Cost Range", f"{format_currency(setup_min, sym)} - {format_currency(setup_max, sym)}")
    with col_c2:
        st.metric("Annual Income Potential", f"{format_currency(income_min, sym)} - {format_currency(income_max, sym)}")
    with col_c3:
        st.metric("ROI Timeline", f"{costs['roi_years']}-{costs['roi_years']+2} years")
    
    # Setup Cost Breakdown
    with st.expander("View Detailed Cost Breakdown"):
        breakdown_data = []
        for item, cost_usd in costs["breakdown"].items():
            cost_conv, _ = cvt(cost_usd)
            breakdown_data.append({"Item": item, "Estimated Cost": format_currency(cost_conv, sym)})
        
        import pandas as pd
        st.dataframe(breakdown_data, use_container_width=True, hide_index=True)
    
    # AFFILIATE RECOMMENDATIONS SECTION
    st.divider()
    st.subheader("Recommended Products for Your Homestead")
    st.caption(f"Personalized recommendations based on your plot size ({st.session_state.total_sqft:,} sq.ft.)")
    
    affiliate_products = st.session_state.get('affiliate_products', [])
    
    cols = st.columns(2)
    for idx, product in enumerate(affiliate_products):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="affiliate-card">
                <h4>{product['name']}</h4>
                <p class="affiliate-cta">"{product['cta']}"</p>
            </div>
            """, unsafe_allow_html=True)
            
            btn_col1, btn_col2 = st.columns([3, 1])
            with btn_col1:
                st.markdown(f"""
                <a href="{product['url']}" target="_blank" class="affiliate-link">
                    Learn More
                </a>
                """, unsafe_allow_html=True)
            with btn_col2:
                st.empty()
    
    # DOWNLOAD SECTION WITH BMC MODAL
    st.divider()
    st.subheader("Download Your Plans")
    
    if st.session_state.show_bmc:
        st.markdown(f"""
        <div class="bmc-support-box">
            <h3>Support This Free Tool</h3>
            <p>This tool is <b>100% FREE</b>! If you found it helpful, please consider supporting its development.</p>
            <a href="{BMC_URL}" target="_blank" 
               style="background-color: #FFDD00; color: #000; padding: 15px 30px; 
                      border-radius: 30px; text-decoration: none; font-weight: bold;
                      display: inline-block; margin: 10px; font-size: 16px;">
                Buy Me a Coffee
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        col_close, _ = st.columns([1, 3])
        with col_close:
            if st.button("Continue to Download", type="primary"):
                st.session_state.show_bmc = False
                st.rerun()
    else:
        col_dl1, col_dl2 = st.columns(2)
        
        with col_dl1:
            if st.button("Download PNG Map", use_container_width=True):
                st.session_state.show_bmc = True
                st.session_state.download_pending = "png"
                st.rerun()
        
        with col_dl2:
            if st.button("Download PDF Report", use_container_width=True):
                st.session_state.show_bmc = True
                st.session_state.download_pending = "pdf"
                st.rerun()
    
    # Show download buttons if BMC was shown and closed
    if not st.session_state.show_bmc and st.session_state.download_pending:
        st.success("Thank you! Your download is ready:")
        
        dl_col1, dl_col2 = st.columns(2)
        
        with dl_col1:
            st.session_state.map_buffer.seek(0)
            st.download_button(
                label="Download PNG Map",
                data=st.session_state.map_buffer,
                file_name=f"{st.session_state.project_name.replace(' ','_')}_blueprint.png",
                mime="image/png",
                use_container_width=True
            )
        
        with dl_col2:
            st.session_state.pdf_buffer.seek(0)
            st.download_button(
                label="Download PDF Report",
                data=st.session_state.pdf_buffer,
                file_name=f"{st.session_state.project_name.replace(' ','_')}_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        st.session_state.download_pending = None
    
    # ZONE DATA TABLE - FIXED
    st.divider()
    st.subheader("Zone Calculations")
    
    import pandas as pd
    
    # Get zone values from session state
    sz0 = st.session_state.get('z0', z0)
    sz1 = st.session_state.get('z1', z1)
    sz2 = st.session_state.get('z2', z2)
    sz3 = st.session_state.get('z3', z3)
    sz4 = st.session_state.get('z4', z4)
    total = st.session_state.total_sqft
    
    df = pd.DataFrame({
        'Zone': ['Zone 0', 'Zone 1', 'Zone 2', 'Zone 3', 'Zone 4/5', 'TOTAL'],
        'Description': ['Residential', 'Kitchen Garden', 'Food Forest',
                        'Pasture/Crops', 'Buffer/Fence', ''],
        'Area (sq.ft.)': [
            f"{int(total * sz0 / 100):,}",
            f"{int(total * sz1 / 100):,}",
            f"{int(total * sz2 / 100):,}",
            f"{int(total * sz3 / 100):,}",
            f"{int(total * sz4 / 100):,}",
            f"{int(total):,}"
        ],
        'Percentage': [f"{sz0}%", f"{sz1}%", f"{sz2}%", f"{sz3}%", f"{sz4}%", "100%"],
    })
    
    # FIXED: use_container_width instead of use_column_width
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    # Default placeholder
    st.info("Fill in your site details in the left sidebar and click Generate Map to get started.")
    
    st.markdown("""
    ### What You Will Get:
    | Feature | Details |
    |---------|---------|
    | Professional Blueprint | AutoCAD-style top-down site plan |
    | Zone Calculations | Exact sq.ft. and percentage for each zone |
    | Cost Analysis | Setup costs and income potential in your currency |
    | Custom Trees | Add your own tree species to the plan |
    | House Position | Choose where your house is located |
    | Water Flow | Borewell to Tank to Zones routing |
    | Dimension Lines | All plot measurements |
    | Legend + Compass | Professional map elements |
    | PDF Report | Multi-page comprehensive report with financial analysis |
    | Product Recommendations | Curated affiliate products based on your plot size |
    
    ### Plot Size Categories:
    - **Small (< 20,000 sq.ft.)**: Urban/suburban homesteads
    - **Medium (20,000 - 100,000 sq.ft.)**: Rural homesteads
    - **Large (> 100,000 sq.ft.)**: Farm-scale operations
    """)
