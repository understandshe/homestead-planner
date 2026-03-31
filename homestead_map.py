"""
Homestead Map Generator — Core Module
Generates professional site plans and PDF reports
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Arrow
import numpy as np
from io import BytesIO
from PIL import Image
import io

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

def generate_visual(L, W, name, zone_fracs, has_pond, has_solar, has_greenhouse,
                   has_poultry, has_borewell, has_compost, has_swale,
                   slope_dir, borewell_loc, water_src, num_tree_species,
                   locked=False, dpi=150):
    """
    Generate a professional homestead site plan visualization
    Returns: BytesIO buffer containing PNG image
    """
    
    # Create figure with proper dimensions
    fig, ax = plt.subplots(1, 1, figsize=(14, 14))
    
    # Calculate zones based on percentages
    total_area = L * W
    
    # Zone colors (professional blueprint style)
    zone_colors = {
        'z0': '#E8F5E9',  # Residential - light green
        'z1': '#C8E6C9',  # Kitchen garden
        'z2': '#A5D6A7',  # Food forest
        'z3': '#81C784',  # Pasture/Crops
        'z4': '#66BB6A',  # Buffer
    }
    
    # Draw plot boundary
    plot_rect = Rectangle((0, 0), L, W, linewidth=3, edgecolor='black', facecolor='none')
    ax.add_patch(plot_rect)
    
    # Calculate zone positions (concentric/sectioned layout)
    # Zone 0 - Residential (center or corner based on vastu)
    z0_area = total_area * zone_fracs['z0']
    z0_side = np.sqrt(z0_area)
    
    # Position zones
    current_y = 0
    
    # Zone 4/5 - Buffer (outer edges)
    z4_height = W * 0.1
    z4_rect = Rectangle((0, 0), L, z4_height, facecolor=zone_colors['z4'], 
                        edgecolor='darkgreen', linewidth=2, alpha=0.7)
    ax.add_patch(z4_rect)
    ax.text(L/2, z4_height/2, 'Zone 4/5: Buffer/Fence', ha='center', va='center',
            fontsize=10, fontweight='bold', color='darkgreen')
    current_y += z4_height
    
    # Zone 3 - Pasture/Crops
    z3_height = W * zone_fracs['z3']
    z3_rect = Rectangle((0, current_y), L, z3_height, facecolor=zone_colors['z3'],
                        edgecolor='darkgreen', linewidth=2, alpha=0.7)
    ax.add_patch(z3_rect)
    ax.text(L/2, current_y + z3_height/2, f"Zone 3: Pasture/Crops\n{int(total_area*zone_fracs['z3'])} sq.ft.",
            ha='center', va='center', fontsize=10, fontweight='bold')
    current_y += z3_height
    
    # Zone 2 - Food Forest
    z2_height = W * zone_fracs['z2']
    z2_rect = Rectangle((0, current_y), L, z2_height, facecolor=zone_colors['z2'],
                        edgecolor='darkgreen', linewidth=2, alpha=0.7)
    ax.add_patch(z2_rect)
    ax.text(L/2, current_y + z2_height/2, f"Zone 2: Food Forest\n{int(total_area*zone_fracs['z2'])} sq.ft.",
            ha='center', va='center', fontsize=10, fontweight='bold')
    current_y += z2_height
    
    # Zone 1 - Kitchen Garden
    z1_height = W * zone_fracs['z1']
    z1_rect = Rectangle((0, current_y), L, z1_height, facecolor=zone_colors['z1'],
                        edgecolor='darkgreen', linewidth=2, alpha=0.7)
    ax.add_patch(z1_rect)
    ax.text(L/2, current_y + z1_height/2, f"Zone 1: Kitchen Garden\n{int(total_area*zone_fracs['z1'])} sq.ft.",
            ha='center', va='center', fontsize=10, fontweight='bold')
    current_y += z1_height
    
    # Zone 0 - Residential (top portion)
    z0_height = W - current_y
    z0_rect = Rectangle((0, current_y), L, z0_height, facecolor=zone_colors['z0'],
                        edgecolor='darkgreen', linewidth=2, alpha=0.7)
    ax.add_patch(z0_rect)
    ax.text(L/2, current_y + z0_height/2, f"Zone 0: Residential\n{int(total_area*zone_fracs['z0'])} sq.ft.",
            ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Add features based on selections
    
    # Borewell
    if has_borewell:
        if 'North-East' in borewell_loc:
            bx, by = L * 0.9, W * 0.9
        elif 'North-West' in borewell_loc:
            bx, by = L * 0.1, W * 0.9
        elif 'South-East' in borewell_loc:
            bx, by = L * 0.9, W * 0.1
        else:
            bx, by = L * 0.9, W * 0.5
        
        well = Circle((bx, by), L*0.02, facecolor='blue', edgecolor='darkblue', linewidth=2)
        ax.add_patch(well)
        ax.text(bx, by, 'W', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    
    # Pond
    if has_pond:
        pond_x, pond_y = L * 0.3, W * 0.3
        pond = Circle((pond_x, pond_y), L*0.08, facecolor='lightblue', 
                     edgecolor='blue', linewidth=2, alpha=0.8)
        ax.add_patch(pond)
        ax.text(pond_x, pond_y, 'POND', ha='center', va='center', fontsize=9, color='darkblue')
    
    # Solar
    if has_solar:
        solar_x, solar_y = L * 0.7, W * 0.85
        solar = Rectangle((solar_x, solar_y), L*0.15, L*0.1, 
                         facecolor='orange', edgecolor='darkorange', linewidth=2)
        ax.add_patch(solar)
        ax.text(solar_x + L*0.075, solar_y + L*0.05, 'SOLAR', ha='center', va='center',
                fontsize=8, fontweight='bold')
    
    # Greenhouse
    if has_greenhouse:
        gh_x, gh_y = L * 0.6, W * 0.6
        gh = Rectangle((gh_x, gh_y), L*0.2, L*0.15, facecolor='lightyellow',
                      edgecolor='green', linewidth=2, linestyle='--')
        ax.add_patch(gh)
        ax.text(gh_x + L*0.1, gh_y + L*0.075, 'GREENHOUSE', ha='center', va='center',
                fontsize=8, color='green')
    
    # Poultry
    if has_poultry:
        p_x, p_y = L * 0.15, W * 0.75
        poultry = Rectangle((p_x, p_y), L*0.12, L*0.1, facecolor='wheat',
                           edgecolor='brown', linewidth=2)
        ax.add_patch(poultry)
        ax.text(p_x + L*0.06, p_y + L*0.05, 'POULTRY', ha='center', va='center',
                fontsize=8, color='brown')
    
    # Compost
    if has_compost:
        c_x, c_y = L * 0.85, W * 0.65
        compost = Circle((c_x, c_y), L*0.025, facecolor='saddlebrown', 
                        edgecolor='black', linewidth=1)
        ax.add_patch(compost)
        ax.text(c_x, c_y - L*0.04, 'Compost', ha='center', va='top', fontsize=7)
    
    # Swale (water management)
    if has_swale:
        for i in range(3):
            swale_y = W * (0.25 + i * 0.2)
            ax.plot([0, L], [swale_y, swale_y], 'b--', linewidth=1.5, alpha=0.6)
            ax.text(L*0.02, swale_y + W*0.01, f'Swale {i+1}', fontsize=7, color='blue')
    
    # Add dimension lines
    # Length dimension
    ax.annotate('', xy=(0, -W*0.05), xytext=(L, -W*0.05),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(L/2, -W*0.08, f'{int(L)} ft', ha='center', fontsize=10, fontweight='bold')
    
    # Width dimension
    ax.annotate('', xy=(-L*0.05, 0), xytext=(-L*0.05, W),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(-L*0.1, W/2, f'{int(W)} ft', ha='center', fontsize=10, fontweight='bold',
            rotation=90)
    
    # Add compass
    compass_x, compass_y = L * 0.92, W * 0.08
    ax.annotate('N', xy=(compass_x, compass_y + L*0.05), fontsize=14, 
                ha='center', fontweight='bold', color='red')
    ax.annotate('', xy=(compass_x, compass_y + L*0.04), 
                xytext=(compass_x, compass_y),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    
    # Add title and info
    ax.set_title(f'{name}\nSite Plan - {int(total_area):,} sq.ft. ({total_area/43560:.2f} acres)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add legend
    legend_elements = [
        patches.Patch(facecolor=zone_colors['z0'], edgecolor='black', label='Zone 0: Residential'),
        patches.Patch(facecolor=zone_colors['z1'], edgecolor='black', label='Zone 1: Kitchen Garden'),
        patches.Patch(facecolor=zone_colors['z2'], edgecolor='black', label='Zone 2: Food Forest'),
        patches.Patch(facecolor=zone_colors['z3'], edgecolor='black', label='Zone 3: Pasture/Crops'),
        patches.Patch(facecolor=zone_colors['z4'], edgecolor='black', label='Zone 4/5: Buffer'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1),
             fontsize=9, frameon=True, fancybox=True, shadow=True)
    
    # Add slope indicator
    ax.text(L*0.02, W*0.98, f'Slope: {slope_dir}', fontsize=9, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Add water source info
    ax.text(L*0.02, W*0.94, f'Water: {water_src}', fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    # Watermark if locked/preview mode
    if locked:
        ax.text(L/2, W/2, 'PREVIEW\nWATERMARK', fontsize=40, color='gray',
                ha='center', va='center', alpha=0.3, rotation=30,
                fontweight='bold')
    
    # Set limits and aspect
    ax.set_xlim(-L*0.15, L*1.35)
    ax.set_ylim(-W*0.15, W*1.05)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    
    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buf.seek(0)
    plt.close(fig)
    
    return buf


def generate_pdf_report(L, W, name, zone_fracs, has_pond, has_solar, has_greenhouse,
                       has_poultry, has_borewell, has_compost, has_swale,
                       slope_dir, borewell_loc, water_src, num_tree_species,
                       affiliate_products):
    """
    Generate a comprehensive PDF report with affiliate products
    Returns: BytesIO buffer containing PDF
    """
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#2E7D32'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#388E3C'),
        spaceAfter=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    story = []
    
    # Page 1: Title Page
    story.append(Paragraph("HOMESTEAD SITE PLAN REPORT", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"<b>Project:</b> {name}", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    total_area = L * W
    acres = total_area / 43560
    
    # Project details table
    data = [
        ['Parameter', 'Value'],
        ['Total Area', f"{int(total_area):,} sq.ft."],
        ['Total Area', f"{acres:.2f} acres"],
        ['Plot Length', f"{int(L)} ft"],
        ['Plot Width', f"{int(W)} ft"],
        ['Slope Direction', slope_dir],
        ['Primary Water Source', water_src],
        ['Borewell Location', borewell_loc],
    ]
    
    t = Table(data, colWidths=[3*inch, 3*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#E8F5E9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.3*inch))
    
    # Zone breakdown
    story.append(Paragraph("Zone Breakdown", heading_style))
    
    zone_data = [
        ['Zone', 'Description', 'Area (sq.ft.)', 'Percentage'],
        ['Zone 0', 'Residential', f"{int(total_area * zone_fracs['z0']):,}", f"{zone_fracs['z0']*100:.0f}%"],
        ['Zone 1', 'Kitchen Garden', f"{int(total_area * zone_fracs['z1']):,}", f"{zone_fracs['z1']*100:.0f}%"],
        ['Zone 2', 'Food Forest', f"{int(total_area * zone_fracs['z2']):,}", f"{zone_fracs['z2']*100:.0f}%"],
        ['Zone 3', 'Pasture/Crops', f"{int(total_area * zone_fracs['z3']):,}", f"{zone_fracs['z3']*100:.0f}%"],
        ['Zone 4/5', 'Buffer/Fence', f"{int(total_area * zone_fracs['z4']):,}", f"{zone_fracs['z4']*100:.0f}%"],
        ['TOTAL', '', f"{int(total_area):,}", '100%'],
    ]
    
    zt = Table(zone_data, colWidths=[1.2*inch, 1.8*inch, 1.5*inch, 1.5*inch])
    zt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E7D32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -2), HexColor('#C8E6C9')),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#81C784')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(zt)
    
    # Page 2-5: Feature details, instructions, etc.
    story.append(PageBreak())
    story.append(Paragraph("Site Features", heading_style))
    
    features = []
    if has_pond:
        features.append("<b>Pond:</b> Water storage and aquaculture")
    if has_solar:
        features.append("<b>Solar Power:</b> Renewable energy system")
    if has_greenhouse:
        features.append("<b>Greenhouse:</b> Extended growing season")
    if has_poultry:
        features.append("<b>Poultry:</b> Egg and meat production")
    if has_borewell:
        features.append("<b>Borewell:</b> Primary water source")
    if has_compost:
        features.append("<b>Compost:</b> Organic waste management")
    if has_swale:
        features.append("<b>Swales:</b> Water harvesting earthworks")
    
    for feature in features:
        story.append(Paragraph(feature, body_style))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Water Management Strategy", heading_style))
    story.append(Paragraph(f"Primary source: {water_src}. Borewell located at {borewell_loc}. "
                          f"Slope direction {slope_dir} informs water flow patterns.", body_style))
    
    # Page 6-7: Affiliate Products
    story.append(PageBreak())
    story.append(Paragraph("Recommended Products for Your Homestead", title_style))
    story.append(Paragraph("Based on your plot size, we've curated these essential products:", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    for product in affiliate_products:
        story.append(Paragraph(f"<b>{product['name']}</b>", heading_style))
        story.append(Paragraph(product['cta'], body_style))
        story.append(Paragraph(f"<a href='{product['url']}' color='blue'><u>Click here to learn more →</u></a>", 
                              body_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
