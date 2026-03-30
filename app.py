def generate_visual(L, W, name, locked=True):
    """
    Professional Homestead Site Plan Generator
    Upgraded version with CAD-style technical drawing aesthetics
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np
    from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Wedge
    import io
    
    # Professional Color Palette (from your HTML reference)
    colors = {
        'zone0': '#E6F1FB',      # Light blue - House
        'zone0_stroke': '#185FA5', # Dark blue
        'zone1': '#EAF3DE',      # Light green - Garden
        'zone1_stroke': '#3B6D11', # Dark green
        'zone2': '#EAF3DE',      # Food forest
        'zone2_stroke': '#639922', # Medium green
        'zone3': '#FAEEDA',      # Pasture
        'zone3_stroke': '#854F0B', # Brown
        'zone4': '#F1EFE8',      # Buffer
        'zone4_stroke': '#5F5E5A', # Gray
        'water': '#85B7EB',      # Water tank
        'text': '#2C2C2A',       # Almost black
        'dim': '#888780',        # Dimension gray
        'bg': '#f8f7f2'          # Warm white background
    }
    
    # Create figure with proper aspect ratio
    fig, ax = plt.subplots(figsize=(16, 14), facecolor=colors['bg'])
    ax.set_facecolor(colors['bg'])
    
    # Calculate scaling
    margin = 80
    total_w = L + 2 * margin
    total_h = W + 2 * margin + 100  # Extra for title block
    
    ax.set_xlim(-margin, L + margin)
    ax.set_ylim(-100, W + margin)
    
    # ============================================
    # 1. PLOT BOUNDARY WITH DIMENSION LINES
    # ============================================
    
    # Main boundary
    boundary = patches.Rectangle((0, 0), L, W, fill=False, 
                                  edgecolor=colors['text'], 
                                  linewidth=1.5, zorder=10)
    ax.add_patch(boundary)
    
    # Top dimension line
    ax.plot([0, L], [W + 15, W + 15], color=colors['dim'], 
            linewidth=0.8, linestyle='--', zorder=5)
    ax.plot([0, 0], [W + 12, W + 18], color=colors['dim'], linewidth=0.8)
    ax.plot([L, L], [W + 12, W + 18], color=colors['dim'], linewidth=0.8)
    ax.text(L/2, W + 22, f'{L} ft ({L*0.3048:.1f} m)', 
            ha='center', va='bottom', fontsize=9, color=colors['dim'])
    
    # Right dimension line
    ax.plot([L + 15, L + 15], [0, W], color=colors['dim'], 
            linewidth=0.8, linestyle='--', zorder=5)
    ax.plot([L + 12, L + 18], [0, 0], color=colors['dim'], linewidth=0.8)
    ax.plot([L + 12, L + 18], [W, W], color=colors['dim'], linewidth=0.8)
    ax.text(L + 25, W/2, f'{W} ft ({W*0.3048:.1f} m)', 
            ha='left', va='center', fontsize=9, color=colors['dim'], rotation=90)
    
    # ============================================
    # 2. ZONE 0 - HOUSE (Top Left)
    # ============================================
    z0_w, z0_h = L * 0.35, W * 0.25
    z0_x, z0_y = 0, W - z0_h
    
    # Zone background
    ax.add_patch(patches.Rectangle((z0_x, z0_y), z0_w, z0_h,
                                   facecolor=colors['zone0'],
                                   edgecolor=colors['zone0_stroke'],
                                   linewidth=1, alpha=0.9, zorder=2))
    
    # House icon - professional style (no emoji)
    house_x, house_y = z0_x + 20, z0_y + z0_h - 50
    # House body
    ax.add_patch(patches.Rectangle((house_x, house_y), 30, 20, 
                                   facecolor='#B5D4F4',
                                   edgecolor=colors['zone0_stroke'],
                                   linewidth=0.8, zorder=3))
    # Roof triangle
    roof = Polygon([(house_x-5, house_y+20), 
                    (house_x+15, house_y+35), 
                    (house_x+35, house_y+20)],
                   facecolor='#85B7EB', edgecolor=colors['zone0_stroke'], 
                   linewidth=0.8, zorder=3)
    ax.add_patch(roof)
    
    # Shed
    ax.add_patch(patches.Rectangle((house_x+35, house_y-5), 20, 15,
                                   facecolor='#B5D4F4',
                                   edgecolor=colors['zone0_stroke'],
                                   linewidth=0.8, zorder=3))
    
    # Zone label
    ax.text(z0_x + z0_w/2, z0_y + z0_h/2 + 10, 'ZONE 0', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            color=colors['zone0_stroke'])
    ax.text(z0_x + z0_w/2, z0_y + z0_h/2 - 5, 'House + Infrastructure', 
            ha='center', va='center', fontsize=8, color=colors['zone0_stroke'])
    
    # ============================================
    # 3. ZONE 1 - INTENSIVE GARDEN (Top Right)
    # ============================================
    z1_w, z1_h = L * 0.65, W * 0.25
    z1_x, z1_y = z0_w, W - z1_h
    
    ax.add_patch(patches.Rectangle((z1_x, z1_y), z1_w, z1_h,
                                   facecolor=colors['zone1'],
                                   edgecolor=colors['zone1_stroke'],
                                   linewidth=1, alpha=0.9, zorder=2))
    
    # Raised beds (3 boxes)
    bed_colors = ['#C0DD97', '#C0DD97', '#C0DD97']
    for i, bx in enumerate([z1_x + 15, z1_x + 80, z1_x + 145]):
        ax.add_patch(FancyBboxPatch((bx, z1_y + z1_h - 35), 50, 20,
                                    boxstyle="round,pad=0.02,rounding_size=2",
                                    facecolor=bed_colors[i],
                                    edgecolor=colors['zone1_stroke'],
                                    linewidth=0.6, zorder=3))
        ax.text(bx + 25, z1_y + z1_h - 25, f'Bed {chr(65+i)}', 
                ha='center', va='center', fontsize=7, color=colors['zone1_stroke'])
    
    # Greenhouse
    gh_x, gh_y = z1_x + z1_w - 100, z1_y + 10
    ax.add_patch(FancyBboxPatch((gh_x, gh_y), 85, 35,
                                boxstyle="round,pad=0.02,rounding_size=3",
                                facecolor='#9FE1CB',
                                edgecolor='#0F6E56',
                                linewidth=0.8, zorder=3))
    ax.text(gh_x + 42.5, gh_y + 17.5, 'Greenhouse', 
            ha='center', va='center', fontsize=8, color='#085041')
    
    # Zone label
    ax.text(z1_x + z1_w/2, z1_y + z1_h/2 + 10, 'ZONE 1', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            color=colors['zone1_stroke'])
    ax.text(z1_x + z1_w/2, z1_y + z1_h/2 - 5, 'Intensive Garden (15%)', 
            ha='center', va='center', fontsize=8, color=colors['zone1_stroke'])
    
    # ============================================
    # 4. ZONE 2 - FOOD FOREST (Middle)
    # ============================================
    z2_h = W * 0.35
    z2_y = W - z0_h - z2_h
    
    ax.add_patch(patches.Rectangle((0, z2_y), L, z2_h,
                                   facecolor=colors['zone2'],
                                   edgecolor=colors['zone2_stroke'],
                                   linewidth=1, alpha=0.85, zorder=2))
    
    # Fruit trees as professional circles with labels
    trees = [
        (60, z2_y + z2_h/2, 18, 'Mango', '#97C459'),
        (140, z2_y + z2_h/2 + 20, 16, 'Guava', '#97C459'),
        (220, z2_y + z2_h/2, 18, 'Mango', '#97C459'),
        (300, z2_y + z2_h/2 - 15, 14, 'Lemon', '#C0DD97'),
        (380, z2_y + z2_h/2 + 10, 16, 'Guava', '#97C459'),
        (L-60, z2_y + z2_h/2, 18, 'Mango', '#97C459')
    ]
    
    for tx, ty, tr, label, tcolor in trees:
        circle = Circle((tx, ty), tr, facecolor=tcolor,
                       edgecolor=colors['zone2_stroke'],
                       linewidth=0.6, alpha=0.85, zorder=4)
        ax.add_patch(circle)
        ax.text(tx, ty, label, ha='center', va='center', 
                fontsize=7, color='#173404', fontweight='medium')
    
    # Solar panels
    solar_x, solar_y = 40, z2_y + 20
    ax.add_patch(patches.Rectangle((solar_x, solar_y), 35, 20,
                                   facecolor='#FAC775',
                                   edgecolor='#854F0B',
                                   linewidth=0.6, zorder=3))
    ax.text(solar_x + 17.5, solar_y + 10, 'Solar', 
            ha='center', va='center', fontsize=7, color='#633806')
    
    # Water tank
    tank_x, tank_y = L - 50, z2_y + 30
    tank = Circle((tank_x, tank_y), 15, facecolor=colors['water'],
                 edgecolor=colors['zone0_stroke'], linewidth=0.8, zorder=4)
    ax.add_patch(tank)
    ax.text(tank_x, tank_y, 'Tank', ha='center', va='center', 
            fontsize=7, color='#042C53')
    
    # Zone label
    ax.text(L/2, z2_y + z2_h/2 + 50, 'ZONE 2 — Food Forest (30%)', 
            ha='center', va='center', fontsize=12, fontweight='bold',
            color=colors['zone2_stroke'])
    
    # ============================================
    # 5. ZONE 3 - MAIN CROPS (Bottom Left)
    # ============================================
    z3_w, z3_h = L * 0.70, W * 0.30
    z3_y = z2_y - z3_h
    
    ax.add_patch(patches.Rectangle((0, z3_y), z3_w, z3_h,
                                   facecolor=colors['zone3'],
                                   edgecolor=colors['zone3_stroke'],
                                   linewidth=1, alpha=0.85, zorder=2))
    
    # Crop rows (dashed lines)
    for i, cy in enumerate(np.linspace(z3_y + 20, z3_y + z3_h - 20, 5)):
        ax.plot([15, z3_w - 15], [cy, cy], color='#EF9F27', 
                linewidth=1, linestyle='--', alpha=0.6, zorder=3)
    
    ax.text(z3_w/2, z3_y + z3_h - 10, 'Fodder / Pasture / Crop Rows', 
            ha='center', va='top', fontsize=9, color=colors['zone3_stroke'])
    
    # Zone label
    ax.text(z3_w/2, z3_y + z3_h/2, 'ZONE 3 — Main Crops (35%)', 
            ha='center', va='center', fontsize=11, fontweight='bold',
            color=colors['zone3_stroke'])
    
    # Borewell
    bw_x, bw_y = L - 30, z3_y + z3_h/2
    ax.add_patch(Circle((bw_x, bw_y), 10, facecolor='#B5D4F4',
                       edgecolor=colors['zone0_stroke'], linewidth=1, zorder=4))
    ax.text(bw_x, bw_y, 'BW', ha='center', va='center', 
            fontsize=7, color=colors['zone0_stroke'])
    
    # Swale (curved water catchment)
    swale_x = np.linspace(z3_w, L, 50)
    swale_y = z3_y + 30 + 10 * np.sin((swale_x - z3_w) / 30)
    ax.plot(swale_x, swale_y, color='#378ADD', linewidth=2.5, zorder=3)
    ax.text((z3_w + L)/2, z3_y + 15, 'Swale', 
            ha='center', va='center', fontsize=8, color='#0C447C')
    
    # ============================================
    # 6. ZONE 4 - BUFFER (Bottom Strip)
    # ============================================
    z4_h = W * 0.10
    z4_y = 0
    
    ax.add_patch(patches.Rectangle((0, z4_y), L, z4_h,
                                   facecolor=colors['zone4'],
                                   edgecolor=colors['zone4_stroke'],
                                   linewidth=1, alpha=0.8, zorder=2))
    
    # Fence line
    ax.plot([0, L], [z4_h, z4_h], color=colors['zone4_stroke'], 
            linewidth=1.5, linestyle='--', zorder=5)
    
    ax.text(L/2, z4_y + z4_h/2, 'ZONE 4/5 — Perimeter Buffer (10%)', 
            ha='center', va='center', fontsize=10, fontweight='bold',
            color=colors['zone4_stroke'])
    
    # ============================================
    # 7. COMPASS ROSE
    # ============================================
    cx, cy = L + 50, W - 60
    # Outer circle
    compass_bg = Circle((cx, cy), 20, facecolor='#F1EFE8',
                       edgecolor=colors['dim'], linewidth=0.5, zorder=6)
    ax.add_patch(compass_bg)
    
    # North arrow (red triangle)
    north_arrow = Polygon([(cx, cy+16), (cx-4, cy+4), (cx+4, cy+4)],
                         facecolor='#E24B4A', zorder=7)
    ax.add_patch(north_arrow)
    # South (black)
    south_arrow = Polygon([(cx, cy-16), (cx-4, cy-4), (cx+4, cy-4)],
                         facecolor=colors['text'], zorder=7)
    ax.add_patch(south_arrow)
    
    # Labels
    ax.text(cx, cy + 24, 'N', ha='center', va='bottom', 
            fontsize=10, fontweight='bold', color=colors['text'])
    ax.text(cx, cy - 24, 'S', ha='center', va='top', 
            fontsize=9, color=colors['dim'])
    ax.text(cx + 24, cy, 'E', ha='left', va='center', 
            fontsize=9, color=colors['dim'])
    ax.text(cx - 24, cy, 'W', ha='right', va='center', 
            fontsize=9, color=colors['dim'])
    
    # ============================================
    # 8. SCALE BAR
    # ============================================
    sb_x, sb_y = 20, -35
    sb_len = 50  # Represents 50ft
    
    ax.plot([sb_x, sb_x + sb_len], [sb_y, sb_y], 
            color=colors['text'], linewidth=2, zorder=6)
    ax.plot([sb_x, sb_x], [sb_y-3, sb_y+3], color=colors['text'], linewidth=1.5)
    ax.plot([sb_x + sb_len, sb_x + sb_len], [sb_y-3, sb_y+3], 
            color=colors['text'], linewidth=1.5)
    ax.plot([sb_x + sb_len/2, sb_x + sb_len/2], [sb_y-2, sb_y+2], 
            color=colors['text'], linewidth=1)
    
    ax.text(sb_x + sb_len/2, sb_y - 10, '0 ——————— 50 ft', 
            ha='center', va='top', fontsize=8, color=colors['dim'])
    
    # ============================================
    # 9. TITLE BLOCK
    # ============================================
    # Bottom professional title bar
    ax.add_patch(patches.Rectangle((-margin, -90), L + 2*margin, 50,
                                   facecolor='#2C3E50', zorder=8))
    
    # Project info
    ax.text(L/2, -65, f'PROJECT: {name.upper()}', 
            ha='center', va='center', fontsize=13, fontweight='bold',
            color='white')
    ax.text(L/2, -80, f'SCALE: 1:200 | TOTAL AREA: {L*W:,} SQ.FT. | 1-ACRE HOMESTEAD MASTERPLAN', 
            ha='center', va='center', fontsize=9, color='#BDC3C7')
    
    # ============================================
    # 10. WATERMARK (If locked)
    # ============================================
    if locked:
        ax.text(L/2, W/2, 'PREVIEW MODE\nUNLOCK FULL VERSION', 
                ha='center', va='center', fontsize=32, color='gray',
                alpha=0.15, rotation=25, zorder=20,
                fontweight='bold')
    
    # ============================================
    # FINALIZE
    # ============================================
    plt.axis('off')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', 
                dpi=300, facecolor=colors['bg'])
    buf.seek(0)
    plt.close(fig)
    
    return buf
