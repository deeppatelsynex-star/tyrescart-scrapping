import os

brands_svg = {
    'michelin.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 36" fill="none">
  <path d="M18 6c-3.3 0-6 2.7-6 6 0 1.8.8 3.4 2.1 4.5L12 28h5l1.5-6h4l1.5 6h5L27 16.5c1.3-1.1 2.1-2.7 2.1-4.5 0-3.3-2.7-6-6-6h-5.1z" fill="#27348B"/>
  <circle cx="20" cy="12" r="2.5" fill="#FEE100"/>
  <text x="36" y="24" font-family="'Arial Black', 'Helvetica Neue', sans-serif" font-size="18" font-weight="900" font-style="italic" fill="#27348B" letter-spacing="-0.5">MICHELIN</text>
</svg>''',
    'bridgestone.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 170 36" fill="none">
  <polygon points="10,6 10,30 16,30 22,25 22,19 16,16 21,12 21,8 16,6" fill="#ED1C24"/>
  <text x="30" y="24" font-family="'Arial Black', Impact, sans-serif" font-size="16" font-weight="900" fill="#111111" letter-spacing="0.2">BRIDGESTONE</text>
</svg>''',
    'continental.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 170 36" fill="none">
  <path d="M6 26c0-8 6-15 15-15 4 0 7 1.5 9 4l-4 3c-1.2-1.5-3-2.5-5-2.5-5.5 0-9.5 4.5-9.5 10.5S16 36.5 21.5 36.5c2.5 0 4.5-1 6-2.5l3.5 3.5c-2.5 2.5-5.5 4-9.5 4-9 0-15.5-7-15.5-15.5z" fill="#FFA000" transform="translate(0,-6)"/>
  <text x="36" y="23" font-family="'Helvetica Neue', Arial, sans-serif" font-size="17" font-weight="900" fill="#FFA000" letter-spacing="-0.3">Continental</text>
</svg>''',
    'goodyear.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 36" fill="none">
  <path d="M4 18c2-2 6-4 10-3l-2 3c-3 0-5 1-6 2l-2-2z" fill="#FFDD00"/>
  <text x="30" y="24" font-family="'Arial Black', Impact, sans-serif" font-size="17" font-weight="900" font-style="italic" fill="#002B66" letter-spacing="0.5">GOOD<tspan fill="#FFDD00">YEAR</tspan></text>
</svg>''',
    'pirelli.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 36" fill="none">
  <path d="M8 26V7h12c7 0 11 3.5 11 9.5 0 5.5-3.8 9.5-10.5 9.5H8zm6-6h5.5c3.5 0 5.5-1.8 5.5-4.5s-2-4.5-5.5-4.5H14v9z" fill="#ED1C24"/>
  <path d="M8 7h95v3H20v16H8V7z" fill="#ED1C24"/>
  <text x="28" y="24" font-family="'Arial Black', Impact, sans-serif" font-size="19" font-weight="900" fill="#ED1C24" letter-spacing="0.8">IRELLI</text>
</svg>''',
    'yokohama.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 36" fill="none">
  <path d="M6 18l7-11 7 11-7 11-7-11zm5 0l2-3 2 3-2 3-2-3z" fill="#ED1C24"/>
  <text x="28" y="23" font-family="'Arial Black', sans-serif" font-size="15" font-weight="900" fill="#ED1C24" letter-spacing="0.2">YOKOHAMA</text>
</svg>''',
    'hankook.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 36" fill="none">
  <path d="M6 18c0-5 3-9 8-11l3 4c-3 1-5 4-5 7s2 6 5 7l-3 4c-5-2-8-6-8-11z" fill="#FF6600"/>
  <text x="24" y="24" font-family="'Arial Black', sans-serif" font-size="17" font-weight="900" font-style="italic" fill="#111111" letter-spacing="-0.5">Hankook</text>
</svg>''',
    'toyo.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 36" fill="none">
  <text x="6" y="24" font-family="'Arial Black', sans-serif" font-size="18" font-weight="900" fill="#005BAC" letter-spacing="0.5">TOYO TIRES</text>
</svg>''',
    'falken.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 36" fill="none">
  <text x="6" y="24" font-family="'Arial Black', sans-serif" font-size="19" font-weight="900" font-style="italic" fill="#005BAC" letter-spacing="0.5">FALKEN</text>
</svg>''',
    'dunlop.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 36" fill="none">
  <path d="M6 8l10 10-10 10V8z" fill="#ED1C24"/>
  <text x="22" y="24" font-family="'Arial Black', sans-serif" font-size="18" font-weight="900" font-style="italic" fill="#111111" letter-spacing="0.2">DUNLOP</text>
</svg>''',
    'kumho.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 36" fill="none">
  <path d="M6 10l8 8-8 8V10z" fill="#ED1C24"/>
  <text x="20" y="22" font-family="'Arial Black', sans-serif" font-size="14" font-weight="900" fill="#111111">KUMHO TIRE</text>
</svg>''',
    'nexen.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 36" fill="none">
  <text x="6" y="24" font-family="'Arial Black', sans-serif" font-size="18" font-weight="900" fill="#7A2582" letter-spacing="1">NEXEN</text>
</svg>''',
    'apollo.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 150 36" fill="none">
  <circle cx="14" cy="18" r="7" fill="#682079"/>
  <circle cx="14" cy="18" r="4" fill="#ffffff"/>
  <text x="26" y="24" font-family="'Helvetica Neue', Arial, sans-serif" font-size="18" font-weight="800" fill="#682079" letter-spacing="-0.5">apollo</text>
</svg>''',
    'ceat.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 140 36" fill="none">
  <text x="6" y="25" font-family="'Arial Black', sans-serif" font-size="22" font-weight="900" fill="#004B87" letter-spacing="1">CE<tspan fill="#F37021">A</tspan>T</text>
</svg>'''
}

out_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'assets', 'images', 'brands')
os.makedirs(out_dir, exist_ok=True)
for fname, content in brands_svg.items():
    with open(os.path.join(out_dir, fname), 'w', encoding='utf-8') as f:
        f.write(content)
print(f'Wrote {len(brands_svg)} brand SVGs successfully!')
