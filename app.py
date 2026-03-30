import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors as pdf_colors

# --- 1. CONFIG & SECURITY ---
MY_SECRET_TOKEN = "ACCESS_KEY_99_ALPHA"
st.set_page_config(page_title="AI Homestead Architect Pro", layout="wide")
is_paid = st.query_params.get("status") == MY_SECRET_TOKEN

# --- 2. PROFESSIONAL PALETTE ---
PALETTE = {
    'bg': (248, 247, 242), 'text': (44, 44, 42), 'dim': (136, 135, 128),
    'z0': (230, 241, 251), 'z0_stroke': (24, 95, 165),
    'z1': (234, 243, 222), 'z1_stroke': (59, 109, 17),
    'z2': (234, 243, 222), 'z2_stroke': (99, 153, 34),
    'z3': (250, 238, 218), 'z3_stroke': (133, 79, 11),
    'pond': (133, 183, 235), 'title_bg': (44, 62, 80)
}

# --- 3. DRAWING ENGINE (Pillow) ---
def generate_cad_image(L, W, name, locked=True):
    # Scale: 10 pixels = 1 foot
    scale = 10
    margin = 200
    img_w, img_h = int(L * scale) + margin * 2, int(W * scale) + margin * 2
    img = Image.new('RGB', (img_w, img_h), color=PALETTE['bg'])
    draw = ImageDraw.Draw(img)
    
    # Offset for plot
    off_x, off_y = margin, margin
    plot_w, plot_h = L * scale, W * scale

    # 1. DIMENSION LINES (Top & Right)
    # Top Dim
    draw.line([(off_x, off_y-50), (off_x+plot_w, off_y-50)], fill=PALETTE['dim'], width=2)
    draw.text((off_x + plot_w/2 - 50, off_y-80), f"{L} ft ({L*0.3048:.1f} m)", fill=PALETTE['dim'])
    
    # 2. ZONE 0: HOUSE (Rectangle + Triangle Roof + Shed)
    z0_w, z0_h = int(plot_w * 0.35), int(plot_h * 0.25)
    draw.rectangle([off_x, off_y, off_x+z0_w, off_y+z0_h], fill=PALETTE['z0'], outline=PALETTE['z0_stroke'])
    # Roof
    draw.polygon([(off_x, off_y), (off_x+z0_w/2, off_y-40), (off_x+z0_w, off_y)], fill=PALETTE['z0_stroke'])
    draw.text((off_x+20, off_y+20), "ZONE 0: HOUSE", fill=PALETTE['z0_stroke'])

    # 3. ZONE 1: RAISED BEDS (Rounded Rects)
    for i in range(3):
        bx = off_x + z0_w + 50 + (i * 150)
        draw.rounded_rectangle([bx, off_y+20, bx+120, off_y+80], radius=10, fill=PALETTE['z1'], outline=PALETTE['z1_stroke'])
        draw.text((bx+30, off_y+40), f"Bed {chr(65+i)}", fill=PALETTE['z1_stroke'])

    # 4. ZONE 2: TREES (Circles with Trunks)
    for i in range(5):
        tx, ty = off_x + 100 + (i * 300), off_y + z0_h + 150
        draw.ellipse([tx-40, ty-40, tx+40, ty+40], fill=(151, 196, 89), outline=PALETTE['z2_stroke'])
        draw.line([(tx, ty+40), (tx, ty+60)], fill=PALETTE['z2_stroke'], width=3) # Trunk
        draw.text((tx-20, ty-10), "Mango", fill=(23, 52, 4))

    # 5. POND (Blue Circle)
    px, py = off_x + plot_w - 200, off_y + plot_h - 200
    draw.ellipse([px-100, py-100, px+100, py+100], fill=PALETTE['pond'], outline=(21, 67, 96), width=3)
    draw.text((px-25, py-10), "POND", fill=(21, 67, 96))

    # 6. COMPASS ROSE
    cx, cy = img_w - 100, 100
    draw.ellipse([cx-40, cy-40, cx+40, cy+40], outline=PALETTE['text'])
    draw.polygon([(cx, cy-35), (cx-10, cy-10), (cx+10, cy-10)], fill=(226, 75, 74)) # North
    draw.text((cx-5, cy-55), "N", fill=PALETTE['text'])

    # 7. TITLE BLOCK (Dark Blue Bar)
    draw.rectangle([0, img_h-100, img_w, img_h], fill=PALETTE['title_bg'])
    title_text = f"PROJECT: {name.upper()} | SCALE: 1:200 | AREA: {L*W:,} SQ.FT."
    draw.text((img_w/2 - 200, img_h-60), title_text, fill="white")

    # 8. WATERMARK
    if locked:
        draw.text((img_w/2 - 400, img_h/2), "PREVIEW MODE - $10 FOR FULL VERSION", fill=(200, 200, 200), font_size=80)

    return img

# --- 4. PDF GENERATOR (ReportLab) ---
def generate_pdf_report(L, W, name, img_buf):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # Page 1: The Plan
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"Homestead Masterplan: {name}")
    # Insert Image (Simplified for demo)
    # c.drawImage(img_buf, 50, 400, width=500, height=350)
    
    # Page 2: Tables
    c.showPage()
    c.drawString(50, 800, "Tree Planting & Financial Report")
    
    data = [
        ["Species", "Qty", "Spacing", "Est. Income"],
        ["Mango", "12", "15 ft", "$1,200"],
        ["Guava", "10", "12 ft", "$800"],
        ["Lemon", "8", "10 ft", "$400"]
    ]
    t = Table(data, colWidths=[100, 50, 80, 100])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), pdf_colors.darkblue),
                           ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.whitesmoke),
                           ('GRID', (0,0), (-1,-1), 0.5, pdf_colors.grey)]))
    t.wrapOn(c, 50, 600)
    t.drawOn(c, 50, 650)
    
    c.save()
    buffer.seek(0)
    return buffer

# --- 5. STREAMLIT UI ---
st.title("🏗️ Professional AI Homestead Architect")
st.sidebar.header("Project Settings")
L = st.sidebar.number_input("Length (ft)", value=209)
W = st.sidebar.number_input("Width (ft)", value=209)
name = st.sidebar.text_input("Project Name", "Alpha Estate")

col1, col2 = st.columns([1, 2])

with col1:
    if not is_paid:
        st.warning("🔒 Pro Version Locked ($10)")
        st.markdown(f'''<a href="https://buymeacoffee.com/m.mehul" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" height="60"></a>''', unsafe_allow_html=True)
    else:
        st.success("✅ Pro Access Granted")

with col2:
    img = generate_cad_image(L, W, name, locked=not is_paid)
    st.image(img, use_container_width=True)
    
    if is_paid:
        # PDF Generation
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        pdf_buf = generate_pdf_report(L, W, name, img_byte_arr)
        st.download_button("📥 Download Professional PDF Report", data=pdf_buf, file_name="Homestead_Report.pdf")
