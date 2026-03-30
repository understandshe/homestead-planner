import io
import base64
from datetime import datetime

def generate_premium_homestead_map(L, W, project_name, zones_data=None, locked=False):
    """
    Premium Homestead Map Generator - Professional SVG-based output
    Creates publication-quality site plans similar to the reference HTML file
    """
    
    # Default zones if not provided
    if zones_data is None:
        zones_data = {
            'zone0': {'name': 'House + Infrastructure', 'pct': 10, 'color': '#E6F1FB', 'stroke': '#185FA5'},
            'zone1': {'name': 'Intensive Garden', 'pct': 15, 'color': '#EAF3DE', 'stroke': '#3B6D11'},
            'zone2': {'name': 'Food Forest', 'pct': 30, 'color': '#EAF3DE', 'stroke': '#639922'},
            'zone3': {'name': 'Main Crops/Pasture', 'pct': 35, 'color': '#FAEEDA', 'stroke': '#854F0B'},
            'zone4': {'name': 'Perimeter Buffer', 'pct': 10, 'color': '#F1EFE8', 'stroke': '#5F5E5A'}
        }
    
    # Calculate areas
    total_area = L * W
    scale_factor = min(640/L, 480/W)  # Fit in viewBox
    
    # SVG Dimensions
    svg_width = 800
    svg_height = 600
    map_x, map_y = 60, 40
    map_w = L * scale_factor
    map_h = W * scale_factor
    
    # Zone positioning (responsive)
    zones_layout = {
        'zone0': {'x': map_x, 'y': map_y, 'w': map_w*0.35, 'h': map_h*0.25},
        'zone1': {'x': map_x + map_w*0.35, 'y': map_y, 'w': map_w*0.65, 'h': map_h*0.25},
        'zone2': {'x': map_x, 'y': map_y + map_h*0.25, 'w': map_w, 'h': map_h*0.35},
        'zone3': {'x': map_x, 'y': map_y + map_h*0.60, 'w': map_w*0.70, 'h': map_h*0.30},
        'zone4': {'x': map_x, 'y': map_y + map_h*0.90, 'w': map_w, 'h': map_h*0.10}
    }
    
    # Generate SVG content
    svg_parts = []
    
    # SVG Header with professional styling
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" style="background:#f8f7f2;font-family:system-ui,-apple-system,sans-serif;">
    <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M2,1 L8,5 L2,9" fill="none" stroke="#378ADD" stroke-width="1.5" stroke-linecap="round"/>
        </marker>
        <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="8" stroke="#3B6D11" stroke-width="0.5" opacity="0.3"/>
        </pattern>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="1" dy="1" stdDeviation="1" flood-opacity="0.1"/>
        </filter>
    </defs>''')
    
    # Title Block
    svg_parts.append(f'''
    <rect x="20" y="10" width="{svg_width-40}" height="24" fill="#2C3E50" rx="4"/>
    <text x="{svg_width/2}" y="26" text-anchor="middle" fill="white" font-size="12" font-weight="600">{project_name.upper()} | 1-ACRE HOMESTEAD MASTERPLAN</text>
    ''')
    
    # Main Map Container
    svg_parts.append(f'<g transform="translate(0, 40)">')
    
    # Plot Boundary with dimension lines
    svg_parts.append(f'''
    <!-- Plot Boundary -->
    <rect x="{map_x}" y="{map_y}" width="{map_w}" height="{map_h}" fill="none" stroke="#444441" stroke-width="1.5"/>
    
    <!-- Dimension Lines - Top -->
    <line x1="{map_x}" y1="{map_y-12}" x2="{map_x+map_w}" y2="{map_y-12}" stroke="#888780" stroke-width="0.5" stroke-dasharray="4,2"/>
    <line x1="{map_x}" y1="{map_y-16}" x2="{map_x}" y2="{map_y-8}" stroke="#888780" stroke-width="0.8"/>
    <line x1="{map_x+map_w}" y1="{map_y-16}" x2="{map_x+map_w}" y2="{map_y-8}" stroke="#888780" stroke-width="0.8"/>
    <text x="{map_x+map_w/2}" y="{map_y-18}" text-anchor="middle" fill="#888780" font-size="9">{L} ft ({L*0.3048:.1f} m)</text>
    
    <!-- Dimension Lines - Right -->
    <line x1="{map_x+map_w+8}" y1="{map_y}" x2="{map_x+map_w+8}" y2="{map_y+map_h}" stroke="#888780" stroke-width="0.5" stroke-dasharray="4,2"/>
    <text x="{map_x+map_w+20}" y="{map_y+map_h/2}" text-anchor="middle" fill="#888780" font-size="9" transform="rotate(90,{map_x+map_w+20},{map_y+map_h/2})">{W} ft ({W*0.3048:.1f} m)</text>
    ''')
    
    # Draw Zones with professional styling
    for zone_id, zone_info in zones_data.items():
        layout = zones_layout[zone_id]
        
        # Zone background
        svg_parts.append(f'''
        <rect x="{layout['x']}" y="{layout['y']}" width="{layout['w']}" height="{layout['h']}" 
              fill="{zone_info['color']}" stroke="{zone_info['stroke']}" stroke-width="0.8" opacity="0.9"/>
        <text x="{layout['x']+layout['w']/2}" y="{layout['y']+layout['h']/2-5}" text-anchor="middle" 
              fill="{zone_info['stroke']}" font-size="11" font-weight="600">{zone_id.upper()}</text>
        <text x="{layout['x']+layout['w']/2}" y="{layout['y']+layout['h']/2+8}" text-anchor="middle" 
              fill="{zone_info['stroke']}" font-size="9" opacity="0.8">{zone_info['name']}</text>
        ''')
        
        # Add zone-specific details
        if zone_id == 'zone0':
            # House icon
            house_x = layout['x'] + 20
            house_y = layout['y'] + 15
            svg_parts.append(f'''
            <rect x="{house_x}" y="{house_y}" width="30" height="20" rx="2" fill="#B5D4F4" stroke="#185FA5" stroke-width="0.5"/>
            <polygon points="{house_x+15},{house_y-8} {house_x-5},{house_y+5} {house_x+35},{house_y+5}" fill="#85B7EB" stroke="#185FA5" stroke-width="0.5"/>
            ''')
        elif zone_id == 'zone1':
            # Raised beds
            for i, bx in enumerate([layout['x']+20, layout['x']+85, layout['x']+150]):
                svg_parts.append(f'''
                <rect x="{bx}" y="{layout['y']+10}" width="50" height="20" rx="2" fill="url(#hatch)" stroke="#3B6D11" stroke-width="0.5"/>
                <text x="{bx+25}" y="{layout['y']+24}" text-anchor="middle" fill="#3B6D11" font-size="7">Bed {chr(65+i)}</text>
                ''')
        elif zone_id == 'zone2':
            # Fruit trees as circles with labels
            trees = [
                (layout['x']+40, layout['y']+30, 'Mango'),
                (layout['x']+100, layout['y']+50, 'Guava'),
                (layout['x']+160, layout['y']+35, 'Mango'),
                (layout['x']+220, layout['y']+55, 'Lemon'),
                (layout['x']+layout['w']-50, layout['y']+40, 'Guava')
            ]
            for tx, ty, label in trees:
                svg_parts.append(f'''
                <circle cx="{tx}" cy="{ty}" r="12" fill="#97C459" stroke="#3B6D11" stroke-width="0.5" opacity="0.85"/>
                <text x="{tx}" y="{ty+3}" text-anchor="middle" fill="#173404" font-size="7">{label}</text>
                ''')
    
    # Water Features
    svg_parts.append(f'''
    <!-- Water Tank -->
    <circle cx="{map_x+map_w-40}" cy="{map_y+map_h*0.45}" r="15" fill="#85B7EB" stroke="#185FA5" stroke-width="0.8"/>
    <text x="{map_x+map_w-40}" y="{map_y+map_h*0.45+3}" text-anchor="middle" fill="#042C53" font-size="7">Tank</text>
    
    <!-- Swale -->
    <path d="M{map_x+map_w*0.6},{map_y+map_h*0.75} Q{map_x+map_w*0.8},{map_y+map_h*0.78} {map_x+map_w},{map_y+map_h*0.75}" 
          fill="none" stroke="#378ADD" stroke-width="2" stroke-linecap="round"/>
    <text x="{map_x+map_w*0.8}" y="{map_y+map_h*0.82}" text-anchor="middle" fill="#0C447C" font-size="8">Swale</text>
    
    <!-- Water Flow Arrow -->
    <path d="M{map_x+50},{map_y+50} Q{map_x+150},{map_y+150} {map_x+300},{map_y+250}" 
          fill="none" stroke="#378ADD" stroke-width="1" stroke-dasharray="5,3" marker-end="url(#arrow)"/>
    ''')
    
    # Compass Rose
    compass_x = map_x + map_w + 35
    compass_y = map_y + 30
    svg_parts.append(f'''
    <g transform="translate({compass_x},{compass_y})">
        <circle cx="0" cy="0" r="18" fill="#F1EFE8" stroke="#888780" stroke-width="0.5"/>
        <polygon points="0,-14 4,-4 0,-8 -4,-4" fill="#E24B4A"/>
        <polygon points="0,14 4,4 0,8 -4,4" fill="#444441"/>
        <text x="0" y="-16" text-anchor="middle" fill="#444441" font-size="9" font-weight="500">N</text>
        <text x="0" y="24" text-anchor="middle" fill="#444441" font-size="9">S</text>
        <text x="22" y="4" text-anchor="middle" fill="#444441" font-size="9">E</text>
        <text x="-22" y="4" text-anchor="middle" fill="#444441" font-size="9">W</text>
    </g>
    ''')
    
    # Scale Bar
    scale_len = 50  # pixels representing 50ft
    svg_parts.append(f'''
    <line x1="{map_x}" y1="{map_y+map_h+25}" x2="{map_x+scale_len}" y2="{map_y+map_h+25}" stroke="#444441" stroke-width="1.5"/>
    <line x1="{map_x}" y1="{map_y+map_h+21}" x2="{map_x}" y2="{map_y+map_h+29}" stroke="#444441" stroke-width="1.5"/>
    <line x1="{map_x+scale_len}" y1="{map_y+map_h+21}" x2="{map_x+scale_len}" y2="{map_y+map_h+29}" stroke="#444441" stroke-width="1.5"/>
    <text x="{map_x+scale_len/2}" y="{map_y+map_h+38}" text-anchor="middle" fill="#888780" font-size="8">0 ————— 50 ft</text>
    ''')
    
    svg_parts.append('</g>')  # Close map group
    
    # Data Table (Zone Breakdown)
    table_y = 520
    svg_parts.append(f'''
    <rect x="20" y="{table_y}" width="{svg_width-40}" height="70" fill="white" stroke="#D3D1C7" stroke-width="0.5" rx="6"/>
    <text x="30" y="{table_y+15}" fill="#444441" font-size="10" font-weight="600">Zone-wise Area Breakdown — {total_area:,} sq.ft.</text>
    ''')
    
    # Table headers
    headers = ['Zone', 'Description', 'Area (sq.ft.)', '%']
    col_x = [30, 80, 200, 280]
    for hx, htext in zip(col_x, headers):
        svg_parts.append(f'<text x="{hx}" y="{table_y+32}" fill="#5F5E5A" font-size="8" font-weight="500">{htext}</text>')
    
    # Table rows
    row_y = table_y + 48
    for zone_id, zone_info in zones_data.items():
        area = total_area * zone_info['pct'] / 100
        svg_parts.append(f'''
        <circle cx="{col_x[0]}" cy="{row_y-2}" r="4" fill="{zone_info['stroke']}"/>
        <text x="{col_x[0]+10}" y="{row_y}" fill="#2C2C2A" font-size="8">{zone_id.upper()}</text>
        <text x="{col_x[1]}" y="{row_y}" fill="#5F5E5A" font-size="8">{zone_info['name']}</text>
        <text x="{col_x[2]}" y="{row_y}" fill="#2C2C2A" font-size="8">{area:,.0f}</text>
        <text x="{col_x[3]}" y="{row_y}" fill="#2C2C2A" font-size="8">{zone_info['pct']}%</text>
        <rect x="{col_x[3]+25}" y="{row_y-4}" width="{zone_info['pct']*0.8}" height="4" fill="{zone_info['stroke']}" rx="2" opacity="0.6"/>
        ''')
        row_y += 14
    
    # Watermark for locked mode
    if locked:
        svg_parts.append(f'''
        <rect x="0" y="0" width="{svg_width}" height="{svg_height}" fill="white" opacity="0.85"/>
        <text x="{svg_width/2}" y="{svg_height/2-20}" text-anchor="middle" fill="#E74C3C" font-size="24" font-weight="bold">🔒 PREVIEW MODE</text>
        <text x="{svg_width/2}" y="{svg_height/2+10}" text-anchor="middle" fill="#2C3E50" font-size="14">Upgrade to Premium for High-Resolution Download</text>
        <text x="{svg_width/2}" y="{svg_height/2+35}" text-anchor="middle" fill="#27AE60" font-size="12" font-weight="600">Includes: Zone Tables • Water Flow • Cost Sheet • Planting Schedule</text>
        ''')
    
    svg_parts.append('</svg>')
    
    # Combine and return
    svg_content = '\n'.join(svg_parts)
    
    # Convert to PNG using matplotlib for compatibility, or return SVG
    return {
        'svg': svg_content,
        'html': f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{project_name} - Homestead Masterplan</title>
            <style>
                body {{ margin:0; padding:20px; background:#f5f5f5; font-family:system-ui; }}
                .container {{ max-width:900px; margin:0 auto; background:white; padding:30px; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.1); }}
                h1 {{ color:#2C3E50; font-size:24px; margin-bottom:5px; }}
                .subtitle {{ color:#7f8c8d; font-size:14px; margin-bottom:20px; }}
                .map-container {{ border:1px solid #e0e0e0; border-radius:8px; overflow:hidden; }}
                .data-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:15px; margin-top:20px; }}
                .data-card {{ background:#f8f9fa; padding:15px; border-radius:8px; border-left:4px solid #27AE60; }}
                .data-card h3 {{ margin:0 0 8px 0; font-size:14px; color:#2C3E50; }}
                .data-card p {{ margin:0; font-size:12px; color:#5F5E5A; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏡 {project_name}</h1>
                <p class="subtitle">Professional Homestead Masterplan • Generated {datetime.now().strftime('%B %d, %Y')}</p>
                <div class="map-container">
                    {svg_content}
                </div>
                <div class="data-grid">
                    <div class="data-card">
                        <h3>📊 Zone Distribution</h3>
                        <p>5-zone permaculture layout optimized for 1-acre productivity. Zone 0 (Residential) through Zone 4 (Wild Buffer).</p>
                    </div>
                    <div class="data-card">
                        <h3>💧 Water Management</h3>
                        <p>Integrated swale system, borewell positioning, and gravity-fed irrigation from overhead tank.</p>
                    </div>
                    <div class="data-card">
                        <h3>🌳 Planting Schedule</h3>
                        <p>65 mixed fruit trees: Mango (15ft), Guava (12ft), Lemon (10ft), with understory crops.</p>
                    </div>
                    <div class="data-card">
                        <h3>💰 Investment</h3>
                        <p>Estimated setup: ₹4.55L | Projected annual income (Yr 3+): ₹1.6L–2.4L</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
    }

# Usage Example
result = generate_premium_homestead_map(
    L=209,  # feet
    W=209,  # feet (1 acre approx)
    project_name="Sharma Farm",
    locked=False
)

# Save files
with open('/mnt/kimi/output/premium_map.svg', 'w') as f:
    f.write(result['svg'])

with open('/mnt/kimi/output/premium_map.html', 'w') as f:
    f.write(result['html'])

print("✅ Premium map generated!")
print(f"📁 SVG saved: /mnt/kimi/output/premium_map.svg")
print(f"📁 HTML saved: /mnt/kimi/output/premium_map.html")
