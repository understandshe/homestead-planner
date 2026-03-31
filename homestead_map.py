import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, Arc
from matplotlib.lines import Line2D
import matplotlib.gridspec as gridspec
import numpy as np
import io

# ─────────────────────────────────────────────
#  COLOUR SYSTEM  (blueprint palette)
# ─────────────────────────────────────────────
C = {
    'bg':       '#FAFAF7',
    'border':   '#1A1A2E',
    'grid':     '#D8D8D0',

    'zone0_f':  '#D6E4F0',   # house / residential
    'zone0_e':  '#1A5276',

    'zone1_f':  '#D5F5E3',   # kitchen garden
    'zone1_e':  '#1E8449',

    'zone2_f':  '#EAFAF1',   # food forest
    'zone2_e':  '#27AE60',

    'zone3_f':  '#FEF9E7',   # pasture / crops
    'zone3_e':  '#B7950B',

    'zone4_f':  '#F2F3F4',   # buffer / fence
    'zone4_e':  '#717D7E',

    'water_f':  '#AED6F1',
    'water_e':  '#1A5276',

    'solar_f':  '#FAD7A0',
    'solar_e':  '#935116',

    'path_c':   '#BFC9CA',

    'title_bg': '#1A1A2E',
    'title_fg': '#FFFFFF',
    'sub_fg':   '#AEB6BF',

    'dim':      '#7F8C8D',
    'water_arr':'#1A5276',
    'contour':  '#AED6F1',
}

FONT_MONO   = {'family': 'monospace'}
FONT_SANS   = {'family': 'DejaVu Sans'}


# ─────────────────────────────────────────────
#  HELPER: draw a zone rectangle
# ─────────────────────────────────────────────
def _zone_rect(ax, x, y, w, h, fc, ec, lw=1.2, alpha=1.0, hatch=None, zorder=2):
    rect = patches.Rectangle(
        (x, y), w, h,
        facecolor=fc, edgecolor=ec,
        linewidth=lw, alpha=alpha,
        hatch=hatch, zorder=zorder
    )
    ax.add_patch(rect)
    return rect


def _zone_label(ax, cx, cy, title, subtitle=None,
                fc='#1A1A2E', sc='#4A4A6A', fs=9, zorder=5):
    ax.text(cx, cy + (4 if subtitle else 0), title,
            ha='center', va='center', fontsize=fs,
            fontweight='bold', color=fc, zorder=zorder,
            **FONT_SANS)
    if subtitle:
        ax.text(cx, cy - 4, subtitle,
                ha='center', va='center', fontsize=fs - 1.5,
                color=sc, zorder=zorder, **FONT_SANS)


# ─────────────────────────────────────────────
#  HELPER: dimension line
# ─────────────────────────────────────────────
def _dim_line(ax, x1, y1, x2, y2, label, offset=6, horiz=True, zorder=6):
    lw, c = 0.6, C['dim']
    if horiz:
        mid_x = (x1 + x2) / 2
        ax.annotate('', xy=(x2, y1 - offset), xytext=(x1, y1 - offset),
                    arrowprops=dict(arrowstyle='<->', color=c, lw=lw), zorder=zorder)
        ax.plot([x1, x1], [y1, y1 - offset], color=c, lw=lw * 0.7, zorder=zorder)
        ax.plot([x2, x2], [y1, y1 - offset], color=c, lw=lw * 0.7, zorder=zorder)
        ax.text(mid_x, y1 - offset - 3, label, ha='center', va='top',
                fontsize=7, color=c, **FONT_MONO, zorder=zorder)
    else:
        mid_y = (y1 + y2) / 2
        ax.annotate('', xy=(x1 + offset, y2), xytext=(x1 + offset, y1),
                    arrowprops=dict(arrowstyle='<->', color=c, lw=lw), zorder=zorder)
        ax.plot([x1, x1 + offset], [y1, y1], color=c, lw=lw * 0.7, zorder=zorder)
        ax.plot([x1, x1 + offset], [y2, y2], color=c, lw=lw * 0.7, zorder=zorder)
        ax.text(x1 + offset + 2, mid_y, label, ha='left', va='center',
                fontsize=7, color=c, rotation=90, **FONT_MONO, zorder=zorder)


# ─────────────────────────────────────────────
#  HELPER: north arrow
# ─────────────────────────────────────────────
def _north_arrow(ax, cx, cy, r=8):
    ax.annotate('', xy=(cx, cy + r), xytext=(cx, cy),
                arrowprops=dict(arrowstyle='->', color=C['border'], lw=1.5))
    circle = plt.Circle((cx, cy), r * 1.5, fill=False,
                         edgecolor=C['border'], lw=0.8)
    ax.add_patch(circle)
    ax.text(cx, cy + r * 2, 'N', ha='center', va='bottom',
            fontsize=9, fontweight='bold', color=C['border'], **FONT_SANS)


# ─────────────────────────────────────────────
#  HELPER: scale bar
# ─────────────────────────────────────────────
def _scale_bar(ax, x, y, bar_ft=50, px_per_ft=1.0):
    bar_px = bar_ft * px_per_ft
    half = bar_px / 2
    # alternating black-white segments
    for i in range(4):
        fc = 'black' if i % 2 == 0 else 'white'
        rect = patches.Rectangle((x + i * half / 2, y), half / 2, 2.5,
                                  facecolor=fc, edgecolor='black', lw=0.5)
        ax.add_patch(rect)
    ax.text(x, y - 3, '0', ha='center', fontsize=6.5,
            color=C['dim'], **FONT_MONO)
    ax.text(x + bar_px / 2, y - 3, f'{bar_ft//2} ft', ha='center',
            fontsize=6.5, color=C['dim'], **FONT_MONO)
    ax.text(x + bar_px, y - 3, f'{bar_ft} ft', ha='center',
            fontsize=6.5, color=C['dim'], **FONT_MONO)
    ax.text(x + bar_px / 2, y + 5.5, 'SCALE BAR',
            ha='center', fontsize=6, color=C['dim'], **FONT_MONO)


# ─────────────────────────────────────────────
#  HELPER: tree dot cluster
# ─────────────────────────────────────────────
def _tree_dots(ax, x0, x1, y0, y1, nx=6, ny=3, r=2.5, color='#27AE60', zorder=4):
    for x in np.linspace(x0, x1, nx):
        for y in np.linspace(y0, y1, ny):
            jx = np.random.uniform(-2, 2)
            jy = np.random.uniform(-2, 2)
            c = plt.Circle((x + jx, y + jy), r,
                            color=color, alpha=0.65, zorder=zorder)
            ax.add_patch(c)


# ─────────────────────────────────────────────
#  HELPER: crop row hatching
# ─────────────────────────────────────────────
def _crop_rows(ax, x0, x1, y0, y1, spacing=8, color='#B7950B', zorder=3):
    y = y0 + spacing
    while y < y1:
        ax.plot([x0 + 4, x1 - 4], [y, y],
                color=color, lw=0.6, alpha=0.5, linestyle='--', zorder=zorder)
        y += spacing


# ─────────────────────────────────────────────
#  HELPER: water flow arrow
# ─────────────────────────────────────────────
def _water_arrow(ax, x1, y1, x2, y2, zorder=7):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle='->', color=C['water_arr'],
                    lw=1.0, connectionstyle='arc3,rad=0.2'
                ), zorder=zorder)


# ─────────────────────────────────────────────
#  HELPER: info bubble (callout box)
# ─────────────────────────────────────────────
def _callout(ax, x, y, lines, bg='white', border='#1A1A2E',
             fs=7.0, pad=3, zorder=8):
    t = ax.text(x, y, '\n'.join(lines),
                ha='left', va='top', fontsize=fs,
                color=C['border'], **FONT_SANS, zorder=zorder,
                linespacing=1.5,
                bbox=dict(boxstyle=f'round,pad={pad/10}',
                          facecolor=bg, edgecolor=border,
                          linewidth=0.6, alpha=0.93))
    return t


# ─────────────────────────────────────────────
#  HELPER: legend box (bottom-right of map)
# ─────────────────────────────────────────────
def _draw_legend(ax, x, y):
    items = [
        (C['zone0_f'], C['zone0_e'], 'Zone 0 — Residential'),
        (C['zone1_f'], C['zone1_e'], 'Zone 1 — Kitchen Garden'),
        (C['zone2_f'], C['zone2_e'], 'Zone 2 — Food Forest'),
        (C['zone3_f'], C['zone3_e'], 'Zone 3 — Pasture / Crops'),
        (C['zone4_f'], C['zone4_e'], 'Zone 4/5 — Buffer / Fence'),
        (C['water_f'], C['water_e'], 'Water — Tank / Pond / Swale'),
        (C['solar_f'], C['solar_e'], 'Solar panels'),
    ]
    bw, bh, gap = 8, 5, 2
    legend_h = len(items) * (bh + gap) + 14
    legend_w = 80

    bg = patches.FancyBboxPatch(
        (x, y - legend_h), legend_w, legend_h,
        boxstyle='round,pad=2',
        facecolor='white', edgecolor=C['border'], lw=0.6, zorder=9
    )
    ax.add_patch(bg)
    ax.text(x + legend_w / 2, y - 5, 'LEGEND',
            ha='center', va='center', fontsize=7,
            fontweight='bold', color=C['border'], **FONT_SANS, zorder=10)

    for i, (fc, ec, label) in enumerate(items):
        iy = y - 14 - i * (bh + gap)
        rect = patches.Rectangle((x + 4, iy - bh / 2), bw, bh,
                                  facecolor=fc, edgecolor=ec,
                                  lw=0.7, zorder=10)
        ax.add_patch(rect)
        ax.text(x + 4 + bw + 3, iy, label,
                ha='left', va='center', fontsize=6.5,
                color=C['border'], **FONT_SANS, zorder=10)


# ─────────────────────────────────────────────
#  HELPER: title block panel
# ─────────────────────────────────────────────
def _title_block(ax, L, W, name, sqft, slope_dir,
                 borewell_loc, water_src, locked, zorder=8):
    tb_h = 34
    tb_y = -tb_h - 6

    # dark background
    ax.add_patch(patches.Rectangle(
        (0, tb_y), L, tb_h,
        facecolor=C['title_bg'], zorder=zorder
    ))
    # left stripe
    ax.add_patch(patches.Rectangle(
        (0, tb_y), 4, tb_h,
        facecolor='#2471A3', zorder=zorder + 1
    ))

    ax.text(7, tb_y + tb_h * 0.72,
            f'PROJECT:  {name.upper()}',
            color=C['title_fg'], fontsize=9, fontweight='bold',
            **FONT_MONO, zorder=zorder + 2)
    ax.text(7, tb_y + tb_h * 0.48,
            f'TOTAL AREA: {sqft:,.0f} sq.ft.  |  SCALE: 1:200  |  SLOPE: {slope_dir}',
            color=C['sub_fg'], fontsize=7.5,
            **FONT_MONO, zorder=zorder + 2)
    ax.text(7, tb_y + tb_h * 0.24,
            f'WATER SOURCE: {water_src.upper()}  |  BOREWELL: {borewell_loc.upper()}',
            color=C['sub_fg'], fontsize=7.5,
            **FONT_MONO, zorder=zorder + 2)

    ax.text(L - 5, tb_y + tb_h * 0.72,
            'AI SITE ARCHITECT  2026',
            color='#AED6F1', fontsize=7, ha='right',
            **FONT_MONO, zorder=zorder + 2)
    ax.text(L - 5, tb_y + tb_h * 0.48,
            'PERMACULTURE MASTERPLAN',
            color=C['sub_fg'], fontsize=7, ha='right',
            **FONT_MONO, zorder=zorder + 2)
    ax.text(L - 5, tb_y + tb_h * 0.24,
            'ORTHOGRAPHIC TOP-DOWN VIEW',
            color=C['sub_fg'], fontsize=7, ha='right',
            **FONT_MONO, zorder=zorder + 2)

    if locked:
        ax.text(L / 2, W / 2,
                'PREVIEW MODE\nUNLOCK HIGH-RES',
                fontsize=36, color='gray', alpha=0.12,
                ha='center', va='center', rotation=28,
                fontweight='bold', zorder=20)


# ─────────────────────────────────────────────
#  MAIN GENERATOR
# ─────────────────────────────────────────────
def generate_visual(
    L: float,
    W: float,
    name: str,

    # Zone custom sizes (fraction of total; None = auto-distribute)
    zone_fracs: dict = None,

    # Feature toggles
    has_pond: bool = True,
    has_solar: bool = True,
    has_greenhouse: bool = True,
    has_poultry: bool = True,
    has_borewell: bool = True,
    has_compost: bool = True,
    has_swale: bool = True,

    # Site parameters
    slope_dir: str = 'North-West to South-East (2%)',
    borewell_loc: str = 'North-East corner',
    water_src: str = 'Borewell + Rainwater',
    num_tree_species: int = 4,

    # House / Zone 0 position: 'NW' | 'NE' | 'SW' | 'SE'
    house_pos: str = 'NW',

    # Output
    locked: bool = True,
    dpi: int = 300,
) -> io.BytesIO:

    np.random.seed(42)

    # ── zone fractions ──────────────────────────
    default_fracs = {
        'z0': 0.10, 'z1': 0.15, 'z2': 0.30,
        'z3': 0.35, 'z4': 0.10
    }
    zf = {**default_fracs, **(zone_fracs or {})}

    total_sqft = L * W
    z0_sqft = total_sqft * zf['z0']
    z1_sqft = total_sqft * zf['z1']
    z2_sqft = total_sqft * zf['z2']
    z3_sqft = total_sqft * zf['z3']
    z4_sqft = total_sqft * zf['z4']

    # ── layout geometry ─────────────────────────
    z3_h = W * (zf['z3'] + zf['z4'] * 0.5)
    z2_h = W * zf['z2']
    z1_h = W * zf['z1']
    z0_h = W * (zf['z0'] + zf['z4'] * 0.5)

    # house_pos controls which corner Zone 0 occupies
    hp        = (house_pos or 'NW').upper()[:2]
    z0_on_top = hp in ('NW', 'NE')
    z0_on_lft = hp in ('NW', 'SW')

    if z0_on_top:
        # Z3 bottom → Z2 → Z1 → Z0 top  (default)
        z3_y = 0
        z2_y = z3_h
        z1_y = z3_h + z2_h
        z0_y = z3_h + z2_h + z1_h
    else:
        # Z0 bottom → Z1 → Z2 → Z3 top
        z0_y = 0
        z1_y = z0_h
        z2_y = z0_h + z1_h
        z3_y = z0_h + z1_h + z2_h

    # horizontal split between Zone 0 and Zone 1
    z0_section_w = L * 0.35
    if z0_on_lft:
        z0_x_off = 2                        # Zone 0 starts at left
        z1_x_off = z0_section_w             # Zone 1 starts after Zone 0
    else:
        z1_x_off = 2                        # Zone 1 starts at left
        z0_x_off = L - z0_section_w + 2    # Zone 0 starts at right

    # ── figure setup ────────────────────────────
    fig_w = 14
    fig_h = fig_w * (W / L) * 1.35 + 3
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), facecolor='white')

    margin_left  = -18
    margin_right = L + 90
    margin_bot   = -60
    margin_top   = W + 30

    ax.set_xlim(margin_left, margin_right)
    ax.set_ylim(margin_bot, margin_top)
    ax.set_aspect('equal')
    ax.axis('off')

    # ── background + grid ───────────────────────
    ax.set_facecolor(C['bg'])
    ax.grid(color=C['grid'], linestyle='--', linewidth=0.35, alpha=0.6, zorder=0)

    # outer border (double rule)
    for lw_, al in [(3, 1.0), (5, 0.25)]:
        ax.add_patch(patches.Rectangle(
            (0, 0), L, W,
            fill=False, edgecolor=C['border'],
            linewidth=lw_, zorder=1, alpha=al
        ))

    # ── ZONE 0 — Residential ────────────────────
    z0_w = z0_section_w
    _zone_rect(ax, z0_x_off, z0_y + 2, z0_w - 4, z0_h - 4,
               C['zone0_f'], C['zone0_e'], lw=1.2, zorder=2)

    # house footprint
    house_w, house_h = z0_w * 0.45, z0_h * 0.50
    house_x = z0_x_off + (z0_w - house_w) / 2 - 4
    house_y = z0_y + z0_h * 0.25
    _zone_rect(ax, house_x, house_y, house_w, house_h,
               '#B3D3ED', C['zone0_e'], lw=0.8, zorder=3)
    # simple roof triangle
    roof_pts = np.array([
        [house_x - 2, house_y + house_h],
        [house_x + house_w / 2, house_y + house_h + house_h * 0.4],
        [house_x + house_w + 2, house_y + house_h]
    ])
    roof = plt.Polygon(roof_pts, closed=True,
                       facecolor='#1A5276', edgecolor=C['zone0_e'],
                       lw=0.7, zorder=4)
    ax.add_patch(roof)
    # door
    door_w = house_w * 0.18
    ax.add_patch(patches.Rectangle(
        (house_x + house_w / 2 - door_w / 2, house_y),
        door_w, house_h * 0.38,
        facecolor='#1A5276', edgecolor=C['zone0_e'], lw=0.5, zorder=5
    ))
    # parking strip
    _zone_rect(ax, z0_x_off, z0_y + 2, z0_w * 0.25, z0_h * 0.2,
               C['path_c'], C['zone4_e'], lw=0.5, zorder=3)
    ax.text(z0_x_off + z0_w * 0.125, z0_y + z0_h * 0.11, 'PARKING',
            ha='center', va='center', fontsize=5.5,
            color='#444', **FONT_MONO, zorder=5)
    # shed
    shed_x = house_x + house_w + 4
    _zone_rect(ax, shed_x, house_y + house_h * 0.3,
               z0_w * 0.18, house_h * 0.45,
               '#AED6F1', C['zone0_e'], lw=0.6, zorder=3)
    ax.text(shed_x + z0_w * 0.09, house_y + house_h * 0.52,
            'SHED', ha='center', fontsize=5.5,
            color=C['zone0_e'], **FONT_MONO, zorder=5)

    _zone_label(ax, z0_x_off + z0_w * 0.5, z0_y + z0_h * 0.08,
                'ZONE 0 — RESIDENTIAL',
                f'{z0_sqft:,.0f} sq.ft. | {zf["z0"]*100:.0f}%',
                fc=C['zone0_e'], sc='#2471A3', fs=8)

    # ── ZONE 1 — Kitchen Garden ──────────────────
    z1_x = z1_x_off
    z1_w = L - z0_section_w
    _zone_rect(ax, z1_x, z1_y + 2, z1_w - 2, z1_h - 4,
               C['zone1_f'], C['zone1_e'], lw=1.2, hatch='///', zorder=2)

    # raised beds
    bed_w, bed_h = z1_w * 0.15, z1_h * 0.55
    for i in range(4):
        bx = z1_x + 4 + i * (bed_w + 6)
        _zone_rect(ax, bx, z1_y + z1_h * 0.25,
                   bed_w, bed_h,
                   '#A9DFBF', C['zone1_e'], lw=0.8, zorder=3)
        ax.text(bx + bed_w / 2, z1_y + z1_h * 0.52,
                f'BED\n{chr(65+i)}', ha='center', va='center',
                fontsize=5.5, color=C['zone1_e'], **FONT_MONO, zorder=5)

    if has_greenhouse:
        gh_x = z1_x + 4 + 4 * (bed_w + 6)
        gh_w = min(z1_w - (gh_x - z1_x) - 4, z1_w * 0.28)
        _zone_rect(ax, gh_x, z1_y + 4,
                   gh_w, z1_h - 8,
                   '#D1F2EB', '#0E6655', lw=0.9, zorder=3)
        ax.text(gh_x + gh_w / 2, z1_y + z1_h / 2,
                'GREENHOUSE', ha='center', fontsize=6,
                color='#0E6655', fontweight='bold', **FONT_MONO, zorder=5)

    if has_poultry:
        po_x = z1_x + z1_w * 0.72
        po_w = z1_w * 0.22
        _zone_rect(ax, po_x, z1_y + z1_h * 0.3,
                   po_w, z1_h * 0.55,
                   '#FDFEFE', C['zone1_e'], lw=0.7, zorder=3)
        ax.text(po_x + po_w / 2, z1_y + z1_h * 0.58,
                'POULTRY', ha='center', fontsize=6,
                color=C['zone1_e'], **FONT_MONO, zorder=5)

    if has_compost:
        _zone_rect(ax, z1_x + 4, z1_y + 2,
                   z1_w * 0.10, z1_h * 0.20,
                   '#D5D8DC', '#7D6608', lw=0.7, zorder=3)
        ax.text(z1_x + z1_w * 0.07, z1_y + z1_h * 0.10,
                'COMPOST', ha='center', fontsize=5.5,
                color='#7D6608', **FONT_MONO, zorder=5)

    _zone_label(ax, z1_x + z1_w / 2, z1_y + z1_h * 0.08,
                'ZONE 1 — KITCHEN GARDEN',
                f'{z1_sqft:,.0f} sq.ft. | {zf["z1"]*100:.0f}%',
                fc=C['zone1_e'], sc='#1E8449', fs=8)

    # ── ZONE 2 — Food Forest ─────────────────────
    _zone_rect(ax, 2, z2_y + 1, L - 4, z2_h - 2,
               C['zone2_f'], C['zone2_e'], lw=1.2, zorder=2)

    # contour lines (slope indicator)
    for i, y_off in enumerate(np.linspace(z2_h * 0.2, z2_h * 0.8, 4)):
        xs = np.linspace(5, L - 5, 50)
        ys = z2_y + y_off + np.sin(xs / L * np.pi) * (z2_h * 0.04)
        ax.plot(xs, ys, color=C['contour'], lw=0.5,
                linestyle='--', alpha=0.5, zorder=3)

    # water flow arrow (contour direction)
    _water_arrow(ax, L * 0.2, z2_y + z2_h * 0.7,
                 L * 0.75, z2_y + z2_h * 0.3)
    ax.text(L * 0.47, z2_y + z2_h * 0.55,
            f'WATER FLOW\n({slope_dir})',
            ha='center', va='center', fontsize=5.5,
            color=C['water_arr'], style='italic', **FONT_SANS, zorder=7)

    # tree dots for each species
    tree_colors = ['#27AE60', '#1E8449', '#2ECC71', '#0E6655',
                   '#117A65', '#145A32']
    species_names = ['Mango', 'Guava', 'Lemon', 'Papaya',
                     'Pomegranate', 'Banana']
    n_sp = min(num_tree_species, 6)
    strip_w = (L - 10) / n_sp
    for i in range(n_sp):
        x0 = 5 + i * strip_w
        _tree_dots(ax, x0, x0 + strip_w - 4,
                   z2_y + z2_h * 0.25, z2_y + z2_h * 0.75,
                   nx=5, ny=3, r=3.0,
                   color=tree_colors[i], zorder=4)
        ax.text(x0 + strip_w * 0.42,
                z2_y + z2_h * 0.12,
                species_names[i],
                ha='center', fontsize=5.8,
                color=tree_colors[i], **FONT_SANS, zorder=5)

    # water tank (highest point → NE of zone2)
    tank_r = min(W, L) * 0.04
    tank_x, tank_y = L * 0.88, z2_y + z2_h * 0.75
    tank = plt.Circle((tank_x, tank_y), tank_r,
                      facecolor=C['water_f'], edgecolor=C['water_e'],
                      lw=1.2, zorder=5)
    ax.add_patch(tank)
    ax.text(tank_x, tank_y, '10K L\nTANK',
            ha='center', va='center', fontsize=5,
            color=C['zone0_e'], fontweight='bold', **FONT_MONO, zorder=6)

    # solar panels
    if has_solar:
        sol_x, sol_y = L * 0.06, z2_y + z2_h * 0.72
        sol_w, sol_h = L * 0.12, z2_h * 0.14
        _zone_rect(ax, sol_x, sol_y, sol_w, sol_h,
                   C['solar_f'], C['solar_e'], lw=0.8, zorder=5)
        # panel grid lines
        for xi in np.linspace(sol_x, sol_x + sol_w, 5):
            ax.plot([xi, xi], [sol_y, sol_y + sol_h],
                    color=C['solar_e'], lw=0.4, zorder=6)
        ax.plot([sol_x, sol_x + sol_w],
                [sol_y + sol_h / 2, sol_y + sol_h / 2],
                color=C['solar_e'], lw=0.4, zorder=6)
        ax.text(sol_x + sol_w / 2, sol_y - 3, 'SOLAR',
                ha='center', fontsize=5.5, color=C['solar_e'],
                **FONT_MONO, zorder=6)

    _zone_label(ax, L / 2, z2_y + z2_h - 6,
                'ZONE 2 — FOOD FOREST',
                f'{z2_sqft:,.0f} sq.ft. | {zf["z2"]*100:.0f}%',
                fc=C['zone2_e'], sc='#1E8449', fs=8.5)

    # ── ZONE 3 — Pasture / Crops ─────────────────
    _zone_rect(ax, 2, z3_y + 1, L - 4, z3_h - 2,
               C['zone3_f'], C['zone3_e'], lw=1.2, zorder=2)
    _crop_rows(ax, 2, L * 0.65, z3_y + 4, z3_y + z3_h - 4,
               spacing=9, color=C['zone3_e'])

    # borewell
    if has_borewell:
        bw_x = L * 0.88
        bw_y = z3_y + z3_h * 0.65
        bw = plt.Circle((bw_x, bw_y), min(W, L) * 0.028,
                         facecolor='#AED6F1', edgecolor='#1A5276',
                         lw=1.2, zorder=5)
        ax.add_patch(bw)
        ax.text(bw_x, bw_y, 'BW',
                ha='center', va='center', fontsize=6,
                color='#1A5276', fontweight='bold', zorder=6)
        ax.text(bw_x, bw_y - min(W, L) * 0.048, 'BOREWELL',
                ha='center', fontsize=5.5, color='#1A5276',
                **FONT_MONO, zorder=6)
        # pump line to tank
        _water_arrow(ax, bw_x, bw_y + min(W, L) * 0.03,
                     tank_x, tank_y - tank_r)

    # pond
    if has_pond:
        pond_r = min(W * 0.10, L * 0.07)
        pond_x = L * 0.52
        pond_y = z3_y + z3_h * 0.42
        pond = patches.Ellipse((pond_x, pond_y),
                                pond_r * 2.4, pond_r * 1.6,
                                facecolor=C['water_f'],
                                edgecolor=C['water_e'],
                                lw=1.2, zorder=4, alpha=0.9)
        ax.add_patch(pond)
        ax.text(pond_x, pond_y, 'POND',
                ha='center', va='center', fontsize=6,
                color='#1A5276', fontweight='bold', **FONT_MONO, zorder=5)

    # swale
    if has_swale:
        swale_y = z3_y + z3_h * 0.82
        xs = np.linspace(5, L - 5, 60)
        ys = swale_y + np.sin((xs - 5) / (L - 10) * 2 * np.pi) * (z3_h * 0.04)
        ax.fill_between(xs, ys - 1.5, ys + 1.5,
                        color=C['water_f'], alpha=0.6, zorder=4)
        ax.plot(xs, ys, color=C['water_e'], lw=0.8, zorder=5)
        ax.text(L / 2, swale_y + z3_h * 0.07,
                'SWALE — CONTOUR TRENCH (GROUNDWATER RECHARGE)',
                ha='center', fontsize=5.5, color=C['water_e'],
                **FONT_MONO, zorder=6)

    _zone_label(ax, L * 0.30, z3_y + z3_h * 0.10,
                'ZONE 3 — PASTURE / CROPS',
                f'{z3_sqft:,.0f} sq.ft. | {zf["z3"]*100:.0f}%',
                fc=C['zone3_e'], sc='#9A7D0A', fs=8.5)

    # ── DIMENSION LINES ──────────────────────────
    _dim_line(ax, 0, W, L, W, f'{L:.0f} ft  ({L*0.3048:.1f} m)',
              offset=11, horiz=True)
    _dim_line(ax, -10, 0, -10, W, f'{W:.0f} ft\n({W*0.3048:.1f} m)',
              offset=12, horiz=False)

    # zone height dims (right side)
    for (ya, yb, lbl) in [
        (z3_y, z3_y + z3_h, f'{z3_h:.0f} ft'),
        (z2_y, z2_y + z2_h, f'{z2_h:.0f} ft'),
        (z1_y, z1_y + z1_h, f'{z1_h:.0f} ft'),
        (z0_y, z0_y + z0_h, f'{z0_h:.0f} ft'),
    ]:
        ax.plot([L + 2, L + 8], [ya, ya], color=C['dim'], lw=0.5)
        ax.plot([L + 2, L + 8], [yb, yb], color=C['dim'], lw=0.5)
        ax.annotate('', xy=(L + 5, yb), xytext=(L + 5, ya),
                    arrowprops=dict(arrowstyle='<->', color=C['dim'], lw=0.5))
        ax.text(L + 9, (ya + yb) / 2, lbl,
                ha='left', va='center', fontsize=5.5,
                color=C['dim'], **FONT_MONO)

    # ── CALLOUT BOXES (right margin) ─────────────
    cbx = L + 18
    callouts = [
        (cbx, W * 0.93, [
            'WATER TANK',
            f'10,000 L capacity',
            'Highest elevation pt.',
            'Gravity-fed to zones 1-3',
        ]),
        (cbx, W * 0.68, [
            'SOLAR ARRAY',
            '1 kW system',
            'North-facing, 10° tilt',
            'Powers pump + lighting',
        ]),
        (cbx, W * 0.44, [
            'BOREWELL',
            f'{borewell_loc}',
            '100 ft depth (typical)',
            'Solar pump, 0.5 HP',
        ]),
        (cbx, W * 0.20, [
            'SWALE SYSTEM',
            'Contour trench @ 2% slope',
            'Recharges groundwater',
            'Prevents runoff erosion',
        ]),
    ]
    for cx, cy, lines in callouts:
        _callout(ax, cx, cy, lines, fs=6.5, zorder=9)
        # leader line to nearest feature
        ax.plot([cx - 1, cx - 7], [cy - 1, cy - 1],
                color=C['dim'], lw=0.4, linestyle=':', zorder=8)

    # ── LEGEND ───────────────────────────────────
    _draw_legend(ax, cbx, W * 0.10 + 55)

    # ── NORTH ARROW ──────────────────────────────
    _north_arrow(ax, cbx + 55, W + 16, r=7)

    # ── SCALE BAR ────────────────────────────────
    _scale_bar(ax, 5, W + 10, bar_ft=50, px_per_ft=1.0)

    # ── TITLE BLOCK ──────────────────────────────
    _title_block(ax, L, W, name, total_sqft, slope_dir,
                 borewell_loc, water_src, locked)

    # ── ZONE CALCULATION TABLE (below title) ─────
    tbl_y = -46
    cols = ['ZONE', 'DESCRIPTION', 'AREA (sq.ft.)', '%', 'KEY FEATURES']
    rows = [
        ['Z0', 'Residential', f'{z0_sqft:,.0f}', f'{zf["z0"]*100:.0f}%',
         'House, Shed, Parking, Paths'],
        ['Z1', 'Kitchen Garden', f'{z1_sqft:,.0f}', f'{zf["z1"]*100:.0f}%',
         'Beds, Greenhouse, Poultry, Compost'],
        ['Z2', 'Food Forest', f'{z2_sqft:,.0f}', f'{zf["z2"]*100:.0f}%',
         f'{n_sp} fruit species, Solar, Water tank'],
        ['Z3', 'Pasture/Crops', f'{z3_sqft:,.0f}', f'{zf["z3"]*100:.0f}%',
         'Fodder rows, Borewell, Swale, Pond'],
        ['Z4/5', 'Buffer/Fence', f'{z4_sqft:,.0f}', f'{zf["z4"]*100:.0f}%',
         'Perimeter fencing, Wild buffer'],
        ['TOTAL', '', f'{total_sqft:,.0f}', '100%', ''],
    ]

    col_xs = [0, L * 0.09, L * 0.30, L * 0.50, L * 0.60]
    ax.text(L / 2, tbl_y + 2,
            'ZONE AREA CALCULATIONS', ha='center', va='top',
            fontsize=7, fontweight='bold', color='white',
            **FONT_MONO, zorder=9)

    for ci, (ch, cx) in enumerate(zip(cols, col_xs)):
        ax.text(cx + 2, tbl_y - 5, ch,
                ha='left', va='top', fontsize=5.8,
                color='#AED6F1', fontweight='bold',
                **FONT_MONO, zorder=9)

    row_colors = ['#2C3E50', '#253545']
    for ri, row in enumerate(rows):
        ry = tbl_y - 10 - ri * 6
        ax.add_patch(patches.Rectangle(
            (0, ry - 1), L, 6.5,
            facecolor=row_colors[ri % 2], zorder=8, alpha=0.6
        ))
        for ci, (cell, cx) in enumerate(zip(row, col_xs)):
            ax.text(cx + 2, ry + 2, cell,
                    ha='left', va='center', fontsize=5.5,
                    color='#ECF0F1', **FONT_MONO, zorder=9)

    # ── OUTPUT ───────────────────────────────────
    plt.tight_layout(pad=0.3)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=dpi,
                bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────
#  QUICK TEST
# ─────────────────────────────────────────────
if __name__ == '__main__':
    buf = generate_visual(
        L=209, W=209,
        name='Green Valley Homestead',
        zone_fracs={'z0': 0.10, 'z1': 0.15, 'z2': 0.30, 'z3': 0.35, 'z4': 0.10},
        has_pond=True,
        has_solar=True,
        has_greenhouse=True,
        has_poultry=True,
        has_borewell=True,
        has_compost=True,
        has_swale=True,
        slope_dir='North-West to South-East (2%)',
        borewell_loc='North-East corner',
        water_src='Borewell + Rainwater Harvesting',
        num_tree_species=5,
        locked=False,
        dpi=200,
    )
    with open('/mnt/user-data/outputs/homestead_map_sample.png', 'wb') as f:
        f.write(buf.read())
    print('Map saved.')
