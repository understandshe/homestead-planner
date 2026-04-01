"""
Homestead Map Generator - Advanced Dynamic Module
Generates unique professional site plans based on user data
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Arc, Wedge
from matplotlib.collections import PatchCollection
import numpy as np
from io import BytesIO
from PIL import Image
import io
import math
import random

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


def generate_random_seed(name, L, W):
    """Generate deterministic seed from inputs for consistent randomness"""
    return hash(f"{name}{L}{W}") % (2**32)


def calculate_optimal_layout(L, W, house_position, zone_fracs, features):
    """
    Calculate optimal positioning for all elements based on plot geometry
    Returns dictionary with calculated positions
    """
    layout = {
        'zones': {},
        'house': {},
        'features': {},
        'trees': [],
        'paths': []
    }
    
    total_area = L * W
    
    # Calculate zone boundaries based on house position
    if house_position == "North":
        zone_order = ['z4', 'z3', 'z2', 'z1', 'z0']
        y_start = W
        y_direction = -1
    elif house_position == "South":
        zone_order = ['z0', 'z1', 'z2', 'z3', 'z4']
        y_start = 0
        y_direction = 1
    elif house_position == "East":
        zone_order = ['z2', 'z1', 'z0', 'z3', 'z4']
        y_start = 0
        y_direction = 1
    elif house_position == "West":
        zone_order = ['z3', 'z2', 'z1', 'z0', 'z4']
        y_start = 0
        y_direction = 1
    else:  # Center - radial layout
        zone_order = ['z0', 'z1', 'z2', 'z3', 'z4']
        y_start = W/2
        y_direction = 1
    
    # Calculate zone positions
    current_y = 0 if y_start == 0 else W
    for zone in zone_order:
        height = W * zone_fracs[zone]
        if house_position in ["North", "South"]:
            layout['zones'][zone] = {
                'x': 0, 'y': min(current_y, current_y + y_direction * height),
                'width': L, 'height': height
            }
            current_y += y_direction * height
        else:
            # For East/West/Center, create different layout
            if zone == 'z0':
                layout['zones'][zone] = {
                    'x': L*0.3, 'y': W*0.4,
                    'width': L*0.4, 'height': W*0.2
                }
            elif zone == 'z1':
                layout['zones'][zone] = {
                    'x': L*0.2, 'y': W*0.2,
                    'width': L*0.6, 'height': W*0.2
                }
            elif zone == 'z2':
                layout['zones'][zone] = {
                    'x': L*0.1, 'y': W*0.6,
                    'width': L*0.8, 'height': W*0.3
                }
            elif zone == 'z3':
                layout['zones'][zone] = {
                    'x': 0, 'y': 0,
                    'width': L, 'height': W*0.2
                }
            else:
                layout['zones'][zone] = {
                    'x': 0, 'y': W*0.9,
                    'width': L, 'height': W*0.1
                }
    
    # House position
    if house_position == "North":
        layout['house'] = {'x': L*0.3, 'y': W*0.85, 'width': L*0.4, 'height': W*0.12}
    elif house_position == "South":
        layout['house'] = {'x': L*0.3, 'y': W*0.03, 'width': L*0.4, 'height': W*0.12}
    elif house_position == "East":
        layout['house'] = {'x': L*0.75, 'y': W*0.35, 'width': L*0.2, 'height': W*0.3}
    elif house_position == "West":
        layout['house'] = {'x': L*0.05, 'y': W*0.35, 'width': L*0.2, 'height': W*0.3}
    else:  # Center
        layout['house'] = {'x': L*0.35, 'y': W*0.4, 'width': L*0.3, 'height': W*0.2}
    
    # Feature positions - randomized but logical
    seed = generate_random_seed(str(layout), L, W)
    np.random.seed(seed)
    
    # Borewell - prefer North-East or based on selection
    if features.get('has_borewell'):
        if 'North-East' in features.get('borewell_loc', ''):
            layout['features']['borewell'] = {'x': L*0.9, 'y': W*0.9, 'radius': min(L,W)*0.02}
        elif 'North-West' in features.get('borewell_loc', ''):
            layout['features']['borewell'] = {'x': L*0.1, 'y': W*0.9, 'radius': min(L,W)*0.02}
        elif 'South-East' in features.get('borewell_loc', ''):
            layout['features']['borewell'] = {'x': L*0.9, 'y': W*0.1, 'radius': min(L,W)*0.02}
        else:
            layout['features']['borewell'] = {'x': L*0.1, 'y': W*0.1, 'radius': min(L,W)*0.02}
    
    # Pond - usually in Zone 2 or 3, lower elevation
    if features.get('has_pond'):
        pond_zones = ['z2', 'z3']
        for zone in pond_zones:
            if zone in layout['zones']:
                z = layout['zones'][zone]
                layout['features']['pond'] = {
                    'x': z['x'] + z['width']*0.3 + np.random.random()*z['width']*0.4,
                    'y': z['y'] + z['height']*0.2 + np.random.random()*z['height']*0.3,
                    'radius': min(L, W) * (0.05 + np.random.random() * 0.05),
                    'irregular': True
                }
                break
    
    # Solar - near house, south-facing if possible
    if features.get('has_solar'):
        h = layout['house']
        layout['features']['solar'] = {
            'x': h['x'] + h['width'] + L*0.05,
            'y': h['y'] + h['height']*0.1,
            'width': L*0.15,
            'height': L*0.1,
            'angle': 15 if house_position in ['North', 'South'] else 0
        }
    
    # Greenhouse - Zone 1 or 2
    if features.get('has_greenhouse'):
        for zone in ['z1', 'z2']:
            if zone in layout['zones']:
                z = layout['zones'][zone]
                layout['features']['greenhouse'] = {
                    'x': z['x'] + z['width']*0.1,
                    'y': z['y'] + z['height']*0.3,
                    'width': min(z['width']*0.4, L*0.25),
                    'height': min(z['height']*0.4, W*0.2),
                    'orientation': 'horizontal' if z['width'] > z['height'] else 'vertical'
                }
                break
    
    # Poultry - Zone 3 or 4, away from house
    if features.get('has_poultry'):
        for zone in ['z3', 'z4']:
            if zone in layout['zones']:
                z = layout['zones'][zone]
                layout['features']['poultry'] = {
                    'x': z['x'] + z['width']*0.1 + np.random.random()*z['width']*0.5,
                    'y': z['y'] + z['height']*0.2 + np.random.random()*z['height']*0.5,
                    'width': L*0.08,
                    'height': W*0.06
                }
                break
    
    # Compost - multiple bins in different zones
    if features.get('has_compost'):
        compost_positions = []
        for zone in ['z1', 'z2', 'z3']:
            if zone in layout['zones'] and len(compost_positions) < 3:
                z = layout['zones'][zone]
                compost_positions.append({
                    'x': z['x'] + z['width']*0.8,
                    'y': z['y'] + z['height']*0.1,
                    'size': min(L, W)*0.015
                })
        layout['features']['compost'] = compost_positions
    
    # Swales - contour lines based on slope
    if features.get('has_swale'):
        num_swales = 2 + int(W / 100)  # More swales for larger plots
        swales = []
        for i in range(num_swales):
            y_pos = W * (0.2 + i * (0.6 / num_swales))
            # Create curved swale following contour
            x_points = np.linspace(0, L, 20)
            y_points = y_pos + np.sin(x_points / L * 4 * np.pi) * W * 0.02
            swales.append({'x': x_points, 'y': y_points})
        layout['features']['swales'] = swales
    
    # Trees - distributed in food forest zone
    num_trees = features.get('num_tree_species', 5)
    custom_trees = features.get('custom_trees', [])
    
    if 'z2' in layout['zones']:
        z = layout['zones']['z2']
        for i in range(max(len(custom_trees), num_trees)):
            if i < len(custom_trees) and custom_trees[i].strip():
                tree_name = custom_trees[i]
            else:
                tree_name = f"Tree {i+1}"
            
            # Random position within zone with minimum spacing
            attempts = 0
            while attempts < 10:
                tx = z['x'] + np.random.random() * z['width'] * 0.8 + z['width'] * 0.1
                ty = z['y'] + np.random.random() * z['height'] * 0.8 + z['height'] * 0.1
                
                # Check spacing from other trees
                too_close = False
                for existing in layout['trees']:
                    dist = math.sqrt((tx - existing['x'])**2 + (ty - existing['y'])**2)
                    if dist < min(L, W) * 0.08:
                        too_close = True
                        break
                
                if not too_close:
                    layout['trees'].append({
                        'x': tx, 'y': ty,
                        'radius': min(L, W) * (0.02 + np.random.random() * 0.02),
                        'name': tree_name[:12],
                        'type': 'fruit' if i % 2 == 0 else 'native'
                    })
                    break
                attempts += 1
    
    # Paths connecting zones
    path_points = [(layout['house']['x'] + layout['house']['width']/2, 
                   layout['house']['y'] + layout['house']['height']/2)]
    
    # Add path to main features
    for feature_name in ['pond', 'greenhouse', 'borewell']:
        if feature_name in layout['features']:
            f = layout['features'][feature_name]
            if 'x' in f:
                path_points.append((f['x'], f['y']))
    
    # Create curved paths
    if len(path_points) > 1:
        for i in range(len(path_points)-1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i+1]
            # Bezier curve control points
            mid_x = (x1 + x2) / 2 + np.random.random() * L * 0.1 - L * 0.05
            mid_y = (y1 + y2) / 2 + np.random.random() * W * 0.1 - W * 0.05
            
            t = np.linspace(0, 1, 20)
            x_curve = (1-t)**2 * x1 + 2*(1-t)*t * mid_x + t**2 * x2
            y_curve = (1-t)**2 * y1 + 2*(1-t)*t * mid_y + t**2 * y2
            
            layout['paths'].append({'x': x_curve, 'y': y_curve})
    
    return layout


def generate_visual(L, W, name, zone_fracs, has_pond, has_solar, has_greenhouse,
                   has_poultry, has_borewell, has_compost, has_swale,
                   slope_dir, borewell_loc, water_src, num_tree_species,
                   house_position, custom_trees, watermark_enabled=True, 
                   watermark_text="chundalgardens.com", dpi=150):
    """
    Generate a unique professional homestead site plan visualization
    Each map is architecturally different based on inputs
    Returns: BytesIO buffer containing PNG image
    """
    
    # Calculate intelligent layout
    features = {
        'has_pond': has_pond,
        'has_solar': has_solar,
        'has_greenhouse': has_greenhouse,
        'has_poultry': has_poultry,
        'has_borewell': has_borewell,
        'has_compost': has_compost,
        'has_swale': has_swale,
        'borewell_loc': borewell_loc,
        'num_tree_species': num_tree_species,
        'custom_trees': custom_trees
    }
    
    layout = calculate_optimal_layout(L, W, house_position, zone_fracs, features)
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 16))
    
    total_area = L * W
    category = get_plot_category(total_area)
    
    # Professional color schemes based on category
    color_schemes = {
        'small': {
            'z0': '#FFF8E1',  # Warm residential
            'z1': '#FFECB3',
            'z2': '#FFE082',
            'z3': '#FFD54F',
            'z4': '#FFCA28',
            'house': '#8D6E63',
            'water': '#4FC3F7',
            'accent': '#FF8F00'
        },
        'medium': {
            'z0': '#E8F5E9',  # Natural green
            'z1': '#C8E6C9',
            'z2': '#A5D6A7',
            'z3': '#81C784',
            'z4': '#66BB6A',
            'house': '#5D4037',
            'water': '#29B6F6',
            'accent': '#2E7D32'
        },
        'large': {
            'z0': '#E3F2FD',  # Cool blue
            'z1': '#BBDEFB',
            'z2': '#90CAF9',
            'z3': '#64B5F6',
            'z4': '#42A5F5',
            'house': '#37474F',
            'water': '#0288D1',
            'accent': '#1565C0'
        }
    }
    
    colors = color_schemes[category]
    
    # Draw plot boundary with shadow effect
    shadow = Rectangle((-2, -2), L+4, W+4, linewidth=0, 
                       facecolor='gray', alpha=0.1)
    ax.add_patch(shadow)
    
    boundary = Rectangle((0, 0), L, W, linewidth=4, 
                        edgecolor='#1B5E20', facecolor='#FAFAFA', linestyle='-')
    ax.add_patch(boundary)
    
    # Draw zones with texture effect
    zone_names = {
        'z0': 'Residential',
        'z1': 'Kitchen Garden',
        'z2': 'Food Forest',
        'z3': 'Pasture/Crops',
        'z4': 'Buffer Zone'
    }
    
    for zone_key, zone_data in layout['zones'].items():
        # Main zone
        rect = FancyBboxPatch(
            (zone_data['x'], zone_data['y']),
            zone_data['width'], zone_data['height'],
            boxstyle="round,pad=0.02,rounding_size=0.01",
            facecolor=colors[zone_key],
            edgecolor='#2E7D32',
            linewidth=2,
            alpha=0.8
        )
        ax.add_patch(rect)
        
        # Zone label with background
        label_x = zone_data['x'] + zone_data['width']/2
        label_y = zone_data['y'] + zone_data['height']/2
        
        # Background for text
        text_bg = Circle((label_x, label_y), min(zone_data['width'], zone_data['height'])*0.15,
                        facecolor='white', edgecolor='none', alpha=0.8, zorder=5)
        ax.add_patch(text_bg)
        
        area_text = f"{zone_names[zone_key]}\n{int(total_area * zone_fracs[zone_key]):,} sq.ft."
        ax.text(label_x, label_y, area_text,
               ha='center', va='center', fontsize=10, fontweight='bold',
               color='#1B5E20', zorder=6)
    
    # Draw paths
    for path in layout['paths']:
        ax.plot(path['x'], path['y'], color='#8D6E63', linewidth=3, 
                linestyle='--', alpha=0.8, zorder=1)
        # Path edges
        ax.plot(path['x'], path['y'], color='#5D4037', linewidth=5, 
                alpha=0.4, zorder=0)
    
    # Draw house with architectural detail
    h = layout['house']
    # Main building
    house_rect = FancyBboxPatch(
        (h['x'], h['y']), h['width'], h['height'],
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor=colors['house'],
        edgecolor='#3E2723',
        linewidth=3
    )
    ax.add_patch(house_rect)
    
    # Roof
    roof = Polygon([
        [h['x']-h['width']*0.05, h['y']+h['height']],
        [h['x']+h['width']/2, h['y']+h['height']*1.2],
        [h['x']+h['width']*1.05, h['y']+h['height']]
    ], facecolor='#BF360C', edgecolor='#3E2723', linewidth=2)
    ax.add_patch(roof)
    
    # Door
    door = Rectangle(
        (h['x']+h['width']*0.4, h['y']),
        h['width']*0.2, h['height']*0.3,
        facecolor='#5D4037', edgecolor='#3E2723'
    )
    ax.add_patch(door)
    
    # Windows
    for wx in [h['x']+h['width']*0.15, h['x']+h['width']*0.65]:
        window = Rectangle(
            (wx, h['y']+h['height']*0.5),
            h['width']*0.15, h['height']*0.2,
            facecolor='#B3E5FC', edgecolor='#3E2723', linewidth=1
        )
        ax.add_patch(window)
    
    ax.text(h['x']+h['width']/2, h['y']+h['height']*1.25, 'HOUSE',
           ha='center', va='bottom', fontsize=11, fontweight='bold', color='#BF360C')
    
    # Draw features
    if 'borewell' in layout['features']:
        f = layout['features']['borewell']
        well = Circle((f['x'], f['y']), f['radius'],
                     facecolor=colors['water'], edgecolor='#01579B', linewidth=3)
        ax.add_patch(well)
        # Water ripple effect
        for r in [1.3, 1.6, 1.9]:
            ripple = Circle((f['x'], f['y']), f['radius']*r,
                          facecolor='none', edgecolor=colors['water'], 
                          linewidth=1, alpha=0.5/r, linestyle='--')
            ax.add_patch(ripple)
        ax.text(f['x'], f['y'], 'W', ha='center', va='center',
               fontsize=9, fontweight='bold', color='white')
        ax.text(f['x'], f['y']-f['radius']*1.5, 'Well',
               ha='center', va='top', fontsize=8, color='#01579B')
    
    if 'pond' in layout['features']:
        f = layout['features']['pond']
        if f.get('irregular'):
            # Create irregular pond shape
            theta = np.linspace(0, 2*np.pi, 20)
            r = f['radius'] * (1 + 0.2 * np.sin(4*theta) + 0.1 * np.random.random(20))
            x_pond = f['x'] + r * np.cos(theta)
            y_pond = f['y'] + r * np.sin(theta)
            pond = Polygon(list(zip(x_pond, y_pond)),
                          facecolor='#E1F5FE', edgecolor='#0288D1', 
                          linewidth=2, alpha=0.9)
        else:
            pond = Circle((f['x'], f['y']), f['radius'],
                         facecolor='#E1F5FE', edgecolor='#0288D1', linewidth=2)
        ax.add_patch(pond)
        ax.text(f['x'], f['y'], 'POND', ha='center', va='center',
               fontsize=9, fontweight='bold', color='#01579B')
    
    if 'solar' in layout['features']:
        f = layout['features']['solar']
        # Solar panels with grid
        panel = Rectangle((f['x'], f['y']), f['width'], f['height'],
                         facecolor='#FFF3E0', edgecolor='#E65100', linewidth=2)
        ax.add_patch(panel)
        
        # Grid lines
        for i in range(1, 4):
            ax.plot([f['x'] + f['width']*i/4, f['x'] + f['width']*i/4],
                   [f['y'], f['y']+f['height']], 'orange', linewidth=1)
            ax.plot([f['x'], f['x']+f['width']],
                   [f['y'] + f['height']*i/3, f['y']+f['height']*i/3], 'orange', linewidth=1)
        
        ax.text(f['x']+f['width']/2, f['y']+f['height']/2, '☀',
               ha='center', va='center', fontsize=20, color='#E65100')
        ax.text(f['x']+f['width']/2, f['y']-f['height']*0.1, 'Solar',
               ha='center', va='top', fontsize=8, color='#E65100')
    
    if 'greenhouse' in layout['features']:
        f = layout['features']['greenhouse']
        gh = Rectangle((f['x'], f['y']), f['width'], f['height'],
                      facecolor='#F1F8E9', edgecolor='#33691E', 
                      linewidth=2, linestyle='--', alpha=0.9)
        ax.add_patch(gh)
        # Arched roof
        arc = Arc((f['x']+f['width']/2, f['y']+f['height']), 
                 f['width'], f['height']*0.4,
                 angle=0, theta1=0, theta2=180, color='#33691E', linewidth=2)
        ax.add_patch(arc)
        ax.text(f['x']+f['width']/2, f['y']+f['height']/2, 'GH',
               ha='center', va='center', fontsize=10, color='#33691E')
    
    if 'poultry' in layout['features']:
        f = layout['features']['poultry']
        coop = Rectangle((f['x'], f['y']), f['width'], f['height'],
                        facecolor='#FFF8E1', edgecolor='#F57F17', linewidth=2)
        ax.add_patch(coop)
        # Fence
        for fx in np.linspace(f['x'], f['x']+f['width'], 5):
            ax.plot([fx, fx], [f['y'], f['y']+f['height']], 
                   color='#F57F17', linewidth=1)
        ax.plot([f['x'], f['x']+f['width']], [f['y']+f['height'], f['y']+f['height']],
               color='#F57F17', linewidth=2)
        ax.text(f['x']+f['width']/2, f['y']+f['height']/2, '🐔',
               ha='center', va='center', fontsize=14)
    
    if 'compost' in layout['features']:
        for i, comp in enumerate(layout['features']['compost']):
            c = Circle((comp['x'], comp['y']), comp['size'],
                      facecolor='#3E2723', edgecolor='black', linewidth=1)
            ax.add_patch(c)
            ax.text(comp['x'], comp['y'], 'C'+str(i+1),
                   ha='center', va='center', fontsize=7, color='white')
    
    if 'swales' in layout['features']:
        for i, swale in enumerate(layout['features']['swales']):
            ax.fill_between(swale['x'], swale['y']-W*0.01, swale['y']+W*0.01,
                          color='#81D4FA', alpha=0.6, edgecolor='#0288D1', linewidth=1)
            ax.text(swale['x'][0], swale['y'][0]+W*0.02, f'Swale {i+1}',
                   fontsize=8, color='#01579B', fontweight='bold')
    
    # Draw trees with variety
    for tree in layout['trees']:
        # Tree crown
        crown = Circle((tree['x'], tree['y']), tree['radius'],
                      facecolor='#2E7D32' if tree['type'] == 'native' else '#FF6F00',
                      edgecolor='#1B5E20', linewidth=2, alpha=0.8)
        ax.add_patch(crown)
        
        # Trunk
        trunk = Rectangle((tree['x']-tree['radius']*0.2, tree['y']-tree['radius']*0.5),
                         tree['radius']*0.4, tree['radius']*0.5,
                         facecolor='#5D4037', edgecolor='#3E2723')
        ax.add_patch(trunk)
        
        # Label
        ax.text(tree['x'], tree['y']+tree['radius']*1.3, tree['name'],
               ha='center', va='bottom', fontsize=7, rotation=0,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                        edgecolor='none', alpha=0.8))
    
    # Dimension lines with arrows
    # Horizontal
    ax.annotate('', xy=(0, -W*0.06), xytext=(L, -W*0.06),
                arrowprops=dict(arrowstyle='<->', color='#424242', lw=2))
    ax.text(L/2, -W*0.09, f'{int(L)} ft', ha='center', fontsize=11, 
            fontweight='bold', color='#424242')
    
    # Vertical
    ax.annotate('', xy=(-L*0.06, 0), xytext=(-L*0.06, W),
                arrowprops=dict(arrowstyle='<->', color='#424242', lw=2))
    ax.text(-L*0.09, W/2, f'{int(W)} ft', ha='center', fontsize=11,
            fontweight='bold', color='#424242', rotation=90)
    
    # Compass rose
    compass_x, compass_y = L * 0.92, W * 0.08
    # Outer circle
    compass_circle = Circle((compass_x, compass_y), L*0.04,
                           facecolor='white', edgecolor='#424242', linewidth=2)
    ax.add_patch(compass_circle)
    # North arrow
    ax.annotate('', xy=(compass_x, compass_y + L*0.035),
                xytext=(compass_x, compass_y - L*0.02),
                arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=3))
    ax.text(compass_x, compass_y + L*0.045, 'N', ha='center', 
           fontsize=14, fontweight='bold', color='#D32F2F')
    # Other directions
    for direction, offset in [('E', (0.03, 0)), ('S', (0, -0.03)), ('W', (-0.03, 0))]:
        ax.text(compass_x + offset[0]*L, compass_y + offset[1]*L, direction,
               ha='center', va='center', fontsize=9, color='#616161')
    
    # Title block
    title_text = f'{name}\nSite Plan - {int(total_area):,} sq.ft. ({total_area/43560:.2f} acres)'
    ax.text(L/2, W*1.06, title_text, ha='center', va='bottom',
           fontsize=16, fontweight='bold', color='#1B5E20',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9', 
                    edgecolor='#2E7D32', linewidth=2))
    
    # Info box
    info_text = f'Slope: {slope_dir} | Water: {water_src} | House: {house_position}'
    ax.text(L*0.02, W*0.98, info_text, fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                    edgecolor='#BDBDBD', alpha=0.9))
    
    # Legend
    legend_elements = [
        patches.Patch(facecolor=colors['z0'], edgecolor='black', label='Zone 0: Residential'),
        patches.Patch(facecolor=colors['z1'], edgecolor='black', label='Zone 1: Kitchen Garden'),
        patches.Patch(facecolor=colors['z2'], edgecolor='black', label='Zone 2: Food Forest'),
        patches.Patch(facecolor=colors['z3'], edgecolor='black', label='Zone 3: Pasture/Crops'),
        patches.Patch(facecolor=colors['z4'], edgecolor='black', label='Zone 4/5: Buffer'),
        patches.Patch(facecolor=colors['water'], edgecolor='black', label='Water Features'),
        patches.Patch(facecolor='#2E7D32', edgecolor='black', label='Trees'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 0.95),
             fontsize=9, frameon=True, fancybox=True, shadow=True, ncol=1)
    
    # WATERMARK SYSTEM - Professional
    if watermark_enabled:
        # Large diagonal watermark
        ax.text(L/2, W/2, watermark_text, fontsize=40, color='#9E9E9E',
                ha='center', va='center', alpha=0.2, rotation=35,
                fontweight='bold', zorder=1000)
        
        # Additional watermarks
        for i, offset in enumerate([-0.4, 0, 0.4]):
            alpha = 0.15 - abs(offset)*0.1
            ax.text(L*(0.5 + offset), W*(0.5 + offset), watermark_text, 
                   fontsize=25, color='#9E9E9E', ha='center', va='center', 
                   alpha=alpha, rotation=35, fontweight='bold', zorder=999)
    else:
        # Corner watermarks
        positions = [(L*0.05, W*0.05), (L*0.95, W*0.05), 
                    (L*0.05, W*0.95), (L*0.95, W*0.95)]
        for cx, cy in positions:
            ax.text(cx, cy, watermark_text, fontsize=7, color='#757575',
                   ha='center', va='center', alpha=0.6, fontweight='bold', zorder=1000)
    
    # Set limits and aspect
    margin = max(L, W) * 0.15
    ax.set_xlim(-margin, L + margin + L*0.3)  # Extra space for legend
    ax.set_ylim(-margin, W + margin)
    ax.set_aspect('equal')
    ax.axis('off')
    
    plt.tight_layout()
    
    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', 
                facecolor='white', edgecolor='none', pad_inches=0.2)
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
