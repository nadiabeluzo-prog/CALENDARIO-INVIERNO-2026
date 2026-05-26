#!/usr/bin/env python3
"""
Re-extrae productos.json y precios.json desde un xlsx del maestro
(de Drive o local) y dispara build.py para regenerar el calendario.

Uso:
  python3 sync.py /ruta/al/maestro.xlsx
"""
import json, os, sys, subprocess, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TALLER = os.path.join(ROOT, '_taller')
PROD_OUT = os.path.join(TALLER, 'productos.json')
PRECIOS_OUT = os.path.join(TALLER, 'precios.json')
BUILD = os.path.join(TALLER, 'build.py')

# rubro -> prefix usado en las URLs de batuk.com.ar
RUBRO_PREFIX = {
    'BABUCHA': 'Pantalon', 'BLUSA': 'Producto', 'BODY': 'Body',
    'BUZO': 'Buzo', 'BUZO C/CAPUCHA': 'Buzo', 'BUZO MEDIO CIERRE': 'Buzo',
    'BUZO S/CAPUCHA': 'Buzo', 'CAMISA': 'Producto', 'CAMPERA': 'Campera',
    'CAMPERA DENIM': 'Jean', 'CARGO': 'Pantalon', 'CHINO': 'Producto',
    'CHOMBA': 'Producto', 'CREW': 'Buzo', 'DENIM': 'Jean',
    'FALDA': 'Falda', 'HOOD': 'Buzo', 'HOODIE': 'Buzo',
    'LEGGING': 'Producto', 'MUSCULOSA': 'Producto', 'PANTALON': 'Pantalon',
    'REMERA': 'Remera', 'REMERA ML': 'Remera', 'REMERA SIN MANGAS': 'Remera',
    'SHORT': 'Short', 'VESTIDO': 'Vestido', 'ZIPHOOD': 'Buzo',
}


def parse_money(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s == '-':
        return None
    s = s.replace('$', '').replace(' ', '').replace('\xa0', '')
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return None


def title_es(s):
    s = (s or '').strip().lower()
    return '-'.join(w.capitalize() for w in re.split(r'\s+', s) if w)


def main(xlsx_path):
    import openpyxl
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb['01-MAESTRO MATERIALES INV']

    # column indices (0-based) — actualizado 2026-04-28 con columna ORIGEN nueva
    C_ORIGEN = 1
    C_MARCA = 2
    C_COD = 4
    C_CAT = 6
    C_RUBRO = 7
    C_BOTONERA = 8
    C_DESC = 9
    C_MES_ING = 10
    C_MES = 11
    C_SEMANA = 16
    C_STATUS = 17
    C_NOMBRE = 23
    C_COLOR_BAS = 25
    C_UNID = 28
    C_CORTADO = 34
    C_COSTO_OB = 45

    by_cod = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        cod = r[C_COD]
        if not cod:
            continue
        cod = str(cod).strip()
        if not cod:
            continue
        marca = (r[C_MARCA] or '').strip() if r[C_MARCA] else ''
        if marca.upper() == 'RS':
            continue
        def _s(v):
            if v is None: return ''
            return str(v).strip()
        if cod not in by_cod:
            by_cod[cod] = {
                'COD': cod,
                'NOMBRE': _s(r[C_NOMBRE]),
                'MES INGRESO PRODUCCION': _s(r[C_MES]),
                'cantidad': 0,
                'cortado': 0,
                'rubro': _s(r[C_RUBRO]),
                '_colors': set(),
                'categoria': _s(r[C_CAT]),
                'marca': marca,
                'status': _s(r[C_STATUS]),
                'origen': _s(r[C_ORIGEN]),
                'botonera': _s(r[C_BOTONERA]),
                'semana': _s(r[C_SEMANA]),
                '_costo': None,
            }
        c = r[C_CORTADO]
        if isinstance(c, (int, float)):
            by_cod[cod]['cortado'] += int(c)
        u = r[C_UNID]
        if isinstance(u, (int, float)):
            by_cod[cod]['cantidad'] += int(u)
        col = (r[C_COLOR_BAS] or '').strip() if r[C_COLOR_BAS] else ''
        if col:
            by_cod[cod]['_colors'].add(col.upper())
        if by_cod[cod]['_costo'] is None:
            cnum = parse_money(r[C_COSTO_OB])
            if cnum is not None:
                by_cod[cod]['_costo'] = cnum

    productos = []
    precios = {}
    for cod, p in by_cod.items():
        rubro_u = p['rubro'].strip().upper()
        prefix = RUBRO_PREFIX.get(rubro_u, 'Producto')
        slug = f"{prefix}-{title_es(p['NOMBRE'])}"
        url_prod = f"https://www.batuk.com.ar/productos/{slug}/"
        url_busc = (
            f"https://www.google.com/search?tbm=isch&q="
            f"batuk+{p['NOMBRE'].lower().replace(' ', '+')}+site%3Abatuk.com.ar"
        )
        productos.append({
            'MES INGRESO PRODUCCION': p['MES INGRESO PRODUCCION'],
            'NOMBRE': p['NOMBRE'],
            'COD': cod,
            'cantidad': p['cantidad'],
            'cortado': p['cortado'],
            'rubro': p['rubro'],
            'color': ', '.join(sorted(p['_colors'])),
            'categoria': p['categoria'],
            'marca': p['marca'],
            'status': p['status'],
            'origen': p['origen'],
            'botonera': p['botonera'],
            'semana': p['semana'],
            'web_prefix': prefix,
            'slug': slug,
            'url_producto': url_prod,
            'url_buscar': url_busc,
        })
        if p['_costo'] is not None:
            costo = p['_costo']
            # Importados: el costo en el maestro suele venir tipeado como "41.828"
            # interpretando el punto como separador de miles (formato AR), pero
            # openpyxl lo lee como decimal (41,828). Si origen=IMPORTADO y el
            # costo es absurdamente chico para una prenda, multiplico x1000.
            if (p['origen'] or '').strip().upper() == 'IMPORTADO' and costo < 1000:
                costo = costo * 1000
            precios[cod] = round(costo * 2.16)

    with open(PROD_OUT, 'w', encoding='utf-8') as f:
        json.dump(productos, f, ensure_ascii=False, indent=1)
    with open(PRECIOS_OUT, 'w', encoding='utf-8') as f:
        json.dump(precios, f, ensure_ascii=False)

    print('productos.json:', len(productos), 'filas')
    print('precios.json:  ', len(precios), 'CODs con precio')
    print('--- build ---')
    subprocess.run(['python3', BUILD], check=True)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Uso: python3 sync.py /ruta/al/maestro.xlsx', file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
