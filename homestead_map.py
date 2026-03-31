"""
Homestead Map Generator - Core Module
Generates professional site plans and PDF reports with watermarking
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Arrow
import numpy as np
from io import BytesIO
from PIL import Image
import io
import math

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Global currency data for 2026 (approximate rates)
CURRENCY_DATA = {
    "USD": {"symbol": "$", "rate": 1.0, "name": "US Dollar"},
    "EUR": {"symbol": "€", "rate": 0.92, "name": "Euro"},
    "GBP": {"symbol": "£", "rate": 0.79, "name": "British Pound"},
    "INR": {"symbol": "₹", "rate": 83.5, "name": "Indian Rupee"},
    "CAD": {"symbol": "C$", "rate": 1.35, "name": "Canadian Dollar"},
    "AUD": {"symbol": "A$", "rate": 1.52, "name": "Australian Dollar"},
    "JPY": {"symbol": "¥", "rate": 150.2, "name": "Japanese Yen"},
    "CNY": {"symbol": "¥", "rate": 7.19, "name": "Chinese Yuan"},
    "BRL": {"symbol": "R$", "rate": 4.95, "name": "Brazilian Real"},
    "MXN": {"symbol": "$", "rate": 17.1, "name": "Mexican Peso"},
}

# Cost estimates by plot size category (USD base)
COST_ESTIMATES = {
    "small": {
        "setup_cost": {"min": 2500, "max": 8000},
        "annual_income": {"min": 800, "max": 2400},
        "annual_expense": {"min": 400, "max": 1200},
        "roi_years": 3,
        "breakdown": {
            "Seeds & Plants": 300,
            "Basic Tools": 500,
            "Irrigation Setup": 800,
            "Soil & Compost": 600,
            "Small Shed": 1500,
            "Fencing": 1200,
            "Miscellaneous": 600
        }
    },
    "medium": {
        "setup_cost": {"min": 15000, "max": 45000},
        "annual_income": {"min": 5000, "max": 15000},
        "annual_expense": {"min": 2000, "max": 6000},
        "roi_years": 4,
        "breakdown": {
            "Seeds & Plants": 2000,
            "Tools & Equipment": 3500,
            "Irrigation System": 5500,
            "Soil & Amendments": 3000,
            "Greenhouse": 8000,
            "Fencing": 6500,
            "Livestock Setup": 5000,
            "Storage Shed": 6000,
            "Solar Setup": 8000,
            "Miscellaneous": 3500
        }
    },
    "large": {
        "setup_cost": {"min": 75000, "max": 200000},
        "annual_income": {"min": 25000, "max": 80000},
        "annual_expense": {"min": 10000, "max": 30000},
        "roi_years": 5,
        "breakdown": {
            "Seeds & Plants": 8000,
            "Heavy Equipment": 25000,
            "Irrigation System": 22000,
            "Soil & Amendments": 12000,
            "Large Greenhouse": 25000,
            "Perimeter Fencing": 18000,
            "Livestock Infrastructure": 15000,
            "Barn & Storage": 35000,
            "Solar System": 35000,
            "Pond Construction": 15000,
            "Access Roads": 12000,
            "Miscellaneous": 15000
        }
    }
}


def get_plot_category(total_sqft):
    """Determine plot category based on size"""
    if total_sqft < 20000:
        return "small"
    elif total_sqft <= 100000:
        return "medium"
    else:
        return "large"


def convert_currency(amount_usd, currency_code):
    """Convert USD amount to selected currency"""
    if currency_code not in CURRENCY_DATA:
        return amount_usd, "$"
    rate = CURRENCY_DATA[currency_code]["rate"]
    symbol = CURRENCY_DATA[currency_code]["symbol"]
    return amount_usd * rate, symbol


def format_currency(amount, symbol):
    """Format amount with currency symbol"""
    if amount >= 1000000:
        return f"{symbol}{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"{symbol}{amount/1000:.1f}K"
    else:
        return f"{symbol}{amount:,.0f}"


def generate_visual(L, W, name, zone_fracs, has_pond, has_solar, has_greenhouse,
                   has_poultry, has_borewell, has_compost, has_swale,
                   slope_dir, borewell_loc, water_src, num_tree_species,
                   house_position, custom_trees, watermark_enabled=True, 
                   watermark_text="chundalgardens.com", dpi=150):
    """
    Generate a professional homestead site plan visualization
    Returns: BytesIO buffer containing PNG image
    """
    
    # Create figure with proper dimensions
    fig, ax = plt.subplots(1, 1, figsize=(16, 16))
    
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
    
    # Calculate zone positions based on house position
    if house_position == "North":
        zones_order = ['z4', 'z3', 'z2', 'z1', 'z0']
    elif house_position == "South":
        zones_order = ['z0', 'z1', 'z2', 'z3', 'z4']
    elif house_position == "East":
        zones_order = ['z2', 'z1', 'z0', 'z3', 'z4']
    elif house_position == "West":
        zones_order = ['z3', 'z2', 'z1', 'z0', 'z4']
    else:  # Center
        zones_order = ['z4', 'z3', 'z0', 'z2', 'z1']
    
    # Draw zones
    current_y = 0
    zone_heights = {
        'z0': W * zone_fracs['z0'],
        'z1': W * zone_fracs['z1'],
        'z2': W * zone_fracs['z2'],
        'z3': W * zone_fracs['z3'],
        'z4': W * zone_fracs['z4']
    }
    
    zone_labels = {
        'z0': ('Residential', zone_fracs['z0']),
        'z1': ('Kitchen Garden', zone_fracs['z1']),
        'z2': ('Food Forest', zone_fracs['z2']),
        'z3': ('Pasture/Crops', zone_fracs['z3']),
        'z4': ('Buffer/Fence', zone_fracs['z4'])
    }
    
    for zone_key in zones_order:
        height = zone_heights[zone_key]
        if height > 0:
            rect = Rectangle((0, current_y), L, height, 
                           facecolor=zone_colors[zone_key],
                           edgecolor='darkgreen', linewidth=2, alpha=0.7)
            ax.add_patch(rect)
            
            label, frac = zone_labels[zone_key]
            area_text = f"{label}\n{int(total_area * frac)} sq.ft."
            ax.text(L/2, current_y + height/2, area_text,
                   ha='center', va='center', fontsize=9, fontweight='bold')
            current_y += height
    
    # Add custom trees
    tree_spacing = min(L, W) / (len(custom_trees) + 1) if custom_trees else L/2
    for i, tree in enumerate(custom_trees):
        if tree.strip():
            tree_x = L * 0.2 + (i % 3) * (L * 0.25)
            tree_y = W * 0.3 + (i // 3) * (W * 0.15)
            tree_circle = Circle((tree_x, tree_y), L*0.03, 
                                facecolor='forestgreen', edgecolor='darkgreen', linewidth=1)
            ax.add_patch(tree_circle)
            ax.text(tree_x, tree_y - L*0.05, tree[:10], ha='center', va='top', 
                   fontsize=7, rotation=0)
    
    # Add features based on selections
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
    
    if has_pond:
        pond_x, pond_y = L * 0.3, W * 0.3
        pond = Circle((pond_x, pond_y), L*0.08, facecolor='lightblue', 
                     edgecolor='blue', linewidth=2, alpha=0.8)
        ax.add_patch(pond)
        ax.text(pond_x, pond_y, 'POND', ha='center', va='center', fontsize=9, color='darkblue')
    
    if has_solar:
        solar_x, solar_y = L * 0.7, W * 0.85
        solar = Rectangle((solar_x, solar_y), L*0.15, L*0.1, 
                         facecolor='orange', edgecolor='darkorange', linewidth=2)
        ax.add_patch(solar)
        ax.text(solar_x + L*0.075, solar_y + L*0.05, 'SOLAR', ha='center', va='center',
                fontsize=8, fontweight='bold')
    
    if has_greenhouse:
        gh_x, gh_y = L * 0.6, W * 0.6
        gh = Rectangle((gh_x, gh_y), L*0.2, L*0.15, facecolor='lightyellow',
                      edgecolor='green', linewidth=2, linestyle='--')
        ax.add_patch(gh)
        ax.text(gh_x + L*0.1, gh_y + L*0.075, 'GREENHOUSE', ha='center', va='center',
                fontsize=8, color='green')
    
    if has_poultry:
        p_x, p_y = L * 0.15, W * 0.75
        poultry = Rectangle((p_x, p_y), L*0.12, L*0.1, facecolor='wheat',
                           edgecolor='brown', linewidth=2)
        ax.add_patch(poultry)
        ax.text(p_x + L*0.06, p_y + L*0.05, 'POULTRY', ha='center', va='center',
                fontsize=8, color='brown')
    
    if has_compost:
        c_x, c_y = L * 0.85, W * 0.65
        compost = Circle((c_x, c_y), L*0.025, facecolor='saddlebrown', 
                        edgecolor='black', linewidth=1)
        ax.add_patch(compost)
        ax.text(c_x, c_y - L*0.04, 'Compost', ha='center', va='top', fontsize=7)
    
    if has_swale:
        for i in range(3):
            swale_y = W * (0.25 + i * 0.2)
            ax.plot([0, L], [swale_y, swale_y], 'b--', linewidth=1.5, alpha=0.6)
            ax.text(L*0.02, swale_y + W*0.01, f'Swale {i+1}', fontsize=7, color='blue')
    
    # Add dimension lines
    ax.annotate('', xy=(0, -W*0.05), xytext=(L, -W*0.05),
                arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
    ax.text(L/2, -W*0.08, f'{int(L)} ft', ha='center', fontsize=10, fontweight='bold')
    
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
    
    # Add title
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
    
    # WATERMARK SYSTEM
    if watermark_enabled:
        # Large semi-transparent watermark across entire image
        ax.text(L/2, W/2, watermark_text, fontsize=35, color='gray',
                ha='center', va='center', alpha=0.25, rotation=30,
                fontweight='bold', zorder=1000)
        
        # Additional diagonal watermarks
        for offset in [-0.3, 0, 0.3]:
            ax.text(L*(0.5 + offset), W*(0.5 + offset), watermark_text, 
                   fontsize=20, color='gray', ha='center', va='center', 
                   alpha=0.15, rotation=45, fontweight='bold', zorder=999)
    else:
        # Small corner watermark (hard to crop out)
        # Multiple small watermarks in corners
        corner_positions = [(L*0.05, W*0.05), (L*0.95, W*0.05), 
                           (L*0.05, W*0.95), (L*0.95, W*0.95), (L*0.5, W*0.02)]
        for cx, cy in corner_positions:
            ax.text(cx, cy, watermark_text, fontsize=6, color='darkgray',
                   ha='center', va='center', alpha=0.6, fontweight='bold', zorder=1000)
        
        # Edge watermark
        ax.text(L/2, W*0.01, watermark_text, fontsize=5, color='darkgray',
               ha='center', va='bottom', alpha=0.5, fontweight='bold', zorder=1000)
    
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
                       house_position, custom_trees, affiliate_products,
                       currency_code="USD", watermark_enabled=True,
                       watermark_text="chundalgardens.com"):
    """
    Generate a comprehensive PDF report with affiliate products and cost analysis
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
    
    warning_style = ParagraphStyle(
        'WarningStyle',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=HexColor('#D32F2F'),
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        borderWidth=1,
        borderColor=HexColor('#D32F2F'),
        borderPadding=10,
        backColor=HexColor('#FFEBEE')
    )
    
    story = []
    
    # Page 1: Title Page with Watermark
    story.append(Paragraph("HOMESTEAD SITE PLAN REPORT", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"<b>Project:</b> {name}", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # DISCLAIMER
    disclaimer_text = (
        "<b>IMPORTANT DISCLAIMER:</b> This report is generated for informational purposes only. "
        "All cost estimates, income projections, and recommendations are approximate and may vary "
        "based on local conditions, market rates, and individual circumstances. Before making any "
        "financial commitments or beginning construction/development on your property, please consult "
        "with qualified agricultural experts, financial advisors, and local authorities. "
        "chundalgardens.com assumes no liability for decisions made based on this report."
    )
    story.append(Paragraph(disclaimer_text, warning_style))
    story.append(Spacer(1, 0.2*inch))
    
    total_area = L * W
    acres = total_area / 43560
    category = get_plot_category(total_area)
    
    # Get cost data
    costs = COST_ESTIMATES[category]
    
    # Convert to selected currency
    def cvt(amount):
        return convert_currency(amount, currency_code)
    
    # Project details table
    data = [
        ['Parameter', 'Value'],
        ['Total Area', f"{int(total_area):,} sq.ft."],
        ['Total Area', f"{acres:.2f} acres"],
        ['Plot Length', f"{int(L)} ft"],
        ['Plot Width', f"{int(W)} ft"],
        ['House Position', house_position],
        ['Slope Direction', slope_dir],
        ['Primary Water Source', water_src],
        ['Borewell Location', borewell_loc],
        ['Custom Trees', str(len([t for t in custom_trees if t.strip()]))],
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
    
    # COST ANALYSIS TABLE
    story.append(Paragraph("Financial Analysis", heading_style))
    
    setup_min, sym = cvt(costs["setup_cost"]["min"])
    setup_max, _ = cvt(costs["setup_cost"]["max"])
    income_min, _ = cvt(costs["annual_income"]["min"])
    income_max, _ = cvt(costs["annual_income"]["max"])
    expense_min, _ = cvt(costs["annual_expense"]["min"])
    expense_max, _ = cvt(costs["annual_expense"]["max"])
    
    cost_data = [
        ['Category', 'Minimum', 'Maximum'],
        ['Initial Setup Cost', format_currency(setup_min, sym), format_currency(setup_max, sym)],
        ['Annual Income Potential', format_currency(income_min, sym), format_currency(income_max, sym)],
        ['Annual Operating Cost', format_currency(expense_min, sym), format_currency(expense_max, sym)],
        ['ROI Timeline', f"{costs['roi_years']} years", f"{costs['roi_years']+2} years"],
    ]
    
    ct = Table(cost_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    ct.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1976D2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#E3F2FD')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.2*inch))
    
    # Setup Cost Breakdown
    story.append(Paragraph("Setup Cost Breakdown", heading_style))
    breakdown_data = [['Item', f'Estimated Cost ({sym})']]
    
    for item, cost_usd in costs["breakdown"].items():
        cost_conv, _ = cvt(cost_usd)
        breakdown_data.append([item, format_currency(cost_conv, sym)])
    
    bt = Table(breakdown_data, colWidths=[4*inch, 2*inch])
    bt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#388E3C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F1F8E9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(bt)
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
    
    # Page 2: Site Features
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
    
    # Custom Trees
    if any(t.strip() for t in custom_trees):
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Custom Tree Species", heading_style))
        for i, tree in enumerate(custom_trees, 1):
            if tree.strip():
                story.append(Paragraph(f"{i}. {tree.strip()}", body_style))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Water Management Strategy", heading_style))
    story.append(Paragraph(f"Primary source: {water_src}. Borewell located at {borewell_loc}. "
                          f"Slope direction {slope_dir} informs water flow patterns.", body_style))
    
    # Page 3-4: Affiliate Products
    story.append(PageBreak())
    story.append(Paragraph("Recommended Products for Your Homestead", title_style))
    story.append(Paragraph("Based on your plot size, we've curated these essential products:", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    for product in affiliate_products:
        story.append(Paragraph(f"<b>{product['name']}</b>", heading_style))
        story.append(Paragraph(product['cta'], body_style))
        story.append(Paragraph(f"<a href='{product['url']}' color='blue'><u>Click here to learn more</u></a>", 
                              body_style))
        story.append(Spacer(1, 0.15*inch))
    
    # Build PDF with watermark on every page
    def add_watermark(canvas, doc):
        canvas.saveState()
        if watermark_enabled:
            # Large diagonal watermark
            canvas.setFont('Helvetica-Bold', 40)
            canvas.setFillColor(HexColor('#CCCCCC'))
            canvas.setStrokeColor(HexColor('#CCCCCC'))
            canvas.translate(A4[0]/2, A4[1]/2)
            canvas.rotate(45)
            canvas.drawCentredString(0, 0, watermark_text)
            canvas.rotate(-45)
            canvas.translate(-A4[0]/2, -A4[1]/2)
            
            # Additional watermarks
            canvas.setFont('Helvetica-Bold', 20)
            canvas.rotate(30)
            canvas.drawCentredString(A4[0]/3, A4[1]/3, watermark_text)
            canvas.rotate(-30)
        else:
            # Small corner watermarks
            canvas.setFont('Helvetica-Bold', 8)
            canvas.setFillColor(HexColor('#999999'))
            positions = [(50, 50), (A4[0]-50, 50), (50, A4[1]-50), (A4[0]-50, A4[1]-50)]
            for x, y in positions:
                canvas.drawCentredString(x, y, watermark_text)
        canvas.restoreState()
    
    doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
    buffer.seek(0)
    return buffer
