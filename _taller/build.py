#!/usr/bin/env python3
# Genera Calendario.html (standalone) y web/index.html (para Netlify).
import json, os, base64, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, '_taller', 'template.html')
PROD_RAW = os.path.join(ROOT, '_taller', 'productos.json')
PRECIOS = os.path.join(ROOT, '_taller', 'precios.json')
PHOTOS_DIR = os.path.join(ROOT, 'fotos')
OUT = os.path.join(ROOT, 'Calendario.html')
WEB = os.path.join(ROOT, 'web', 'index.html')

with open(PROD_RAW) as f:
    raw = json.load(f)
with open(PRECIOS) as f:
    precios = json.load(f)

productos = []
n_with = 0
n_skip_rs = 0
for r in raw:
    marca = (r.get('marca') or '').strip().upper()
    mes = (r.get('MES INGRESO PRODUCCION') or '').strip().upper()
    if marca == 'RS' or mes == 'RS' or mes.startswith('PASA'):
        n_skip_rs += 1
        continue
    cod = (r.get('COD') or '').strip()
    foto = None
    # Sanitize: barras en el COD (ej BM-7266/A) -> guion bajo para nombre de archivo
    cod_fname = cod.replace('/', '_')
    fp = os.path.join(PHOTOS_DIR, cod_fname + '.jpg')
    if os.path.exists(fp):
        with open(fp, 'rb') as ff:
            b = ff.read()
        foto = 'data:image/jpeg;base64,' + base64.b64encode(b).decode('ascii')
        n_with += 1
    p = {
        'mes': r.get('MES INGRESO PRODUCCION'),
        'nombre': r.get('NOMBRE'),
        'cod': cod,
        'cant': r.get('cantidad', 0) or 0,
        'cortado': r.get('cortado', 0) or 0,
        'rubro': r.get('rubro') or '',
        'color': r.get('color') or '',
        'cat': r.get('categoria') or '',
        'marca': r.get('marca') or '',
        'status': r.get('status') or '',
        'origen': r.get('origen') or '',
        'botonera': r.get('botonera') or '',
        'semana': r.get('semana') or '',
        'temporada': r.get('temporada') or '',
        'precio': precios.get(cod) or 0,
        'foto': foto,
        'pdf': None,
        'url_busc': r.get('url_producto') or '',
        'url_google': r.get('url_buscar') or '',
    }
    productos.append(p)

COLOR_HEX = {
    "NEGRO": "#1a1a1a", "BLANCO": "#f5f5f5", "CRUDO": "#efe4d2",
    "GRIS": "#9aa0a6", "MARRON": "#6b3e26", "BEIGE": "#d9c7a3",
    "VERDE": "#3a6b3a", "AZUL": "#2c4a73", "BORDO": "#7a1f2b",
    "LILA": "#b497d6", "ROJO": "#b22222", "ROSA": "#e7a4b6",
    "AMARILLO": "#e8c547", "NARANJA": "#d27b3f", "CELESTE": "#7fb3d5",
    "FUCSIA": "#c2185b", "VIOLETA": "#7c4dff", "TURQUESA": "#26a69a",
    "OLIVA": "#6b7a3a", "MOSTAZA": "#cba135", "CAMEL": "#c19a6b",
    "SUELA": "#a87250", "MILITAR": "#4b5320", "PETROLEO": "#264653",
    "TEJA": "#b85c3c", "KAKI": "#8a7f5a", "PLATA": "#c0c0c0",
    "DORADO": "#d4af37"
}

with open(TPL) as f:
    tpl = f.read()

prod_js = json.dumps(productos, ensure_ascii=False, separators=(',', ':'))
colors_js = json.dumps(COLOR_HEX, ensure_ascii=False, separators=(',', ':'))
html = tpl.replace('__PRODUCTOS__', prod_js).replace('__COLORS__', colors_js)

with open(OUT, 'w') as f:
    f.write(html)
os.makedirs(os.path.dirname(WEB), exist_ok=True)
shutil.copy(OUT, WEB)

sz = os.path.getsize(OUT)
print('OK ' + str(sz) + ' bytes, ' + str(n_with) + ' con foto de ' + str(len(productos)) + ' productos')
print('Done.')
