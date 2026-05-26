// ============================================================
//  CALENDARIO PRODUCCIÓN — Batuk / Huoky
//  Google Apps Script  ·  Web App (doGet)
//
//  DEPLOY:
//  1. Abrir la planilla → Extensiones → Apps Script
//  2. Pegar este código completo (reemplazar lo que haya)
//  3. Guardar  →  Implementar → Nueva implementación
//     Tipo: Aplicación web
//     Ejecutar como: Yo (tu cuenta)
//     Acceso: Cualquier usuario (Anyone)
//  4. Copiar la URL que te da y pegarla en index_dinamico.html
//     donde dice  API_URL = '...'
// ============================================================

const SHEET_ID   = '1stw7L-HT4letxcgxNrhjjKzGt1-oDxQu';
const SHEET_NAME = '01-MAESTRO MATERIALES INV';

// Índices de columna (fila de encabezados, base 0)
// Si el orden del sheet cambia, actualizar acá
const COL = {
  FECHA_DISENO  : 0,
  MARCA         : 1,
  TEMPORADA     : 2,
  COD           : 3,
  CODIGO_BAS    : 4,
  CAT_PLAN      : 5,
  RUBRO         : 6,
  BOTONERA      : 7,
  MES_INGRESO   : 8,
  MES_PROD      : 9,   // ← columna que dispara el calendario
  DESC_PROD     : 10,
  DISTRIBUCION  : 11,
  TIEMPOS_PROD  : 12,
  DIAS_REAL     : 13,
  FECHA_ENTREGA : 14,
  STATUS        : 15,
  ENTREGADO     : 16,
  MUESTRARIO    : 17,
  FECHA_MOD     : 18,
  FOTO          : 19,
  TALLE         : 20,
  NOMBRE        : 21,
  VARIANTE      : 22,
  COLOR_BAS     : 23,
  MUESTRA       : 24,
  PRODUCTO      : 25,
  UNID_PEDIDAS  : 26,
  CURVA         : 27,
  CALCE         : 28,
  TIRO          : 29,
  MOLDERIA      : 30,
  CORTADO       : 31,
  XS            : 32,
  S             : 33,
  M             : 34,
  L             : 35,
  XL            : 36,
  XXL           : 37,
  DISENADOR     : 38,
  TIPO_TEJIDO   : 39,
  TELA          : 40,
  PROVEEDOR     : 41,
  COSTO_OB      : 42,
};

function doGet(e) {
  try {
    const ss    = SpreadsheetApp.openById(SHEET_ID);
    const sheet = ss.getSheetByName(SHEET_NAME);

    if (!sheet) {
      return jsonResp({ error: 'Hoja "' + SHEET_NAME + '" no encontrada.' });
    }

    // Leer todos los datos de una sola vez (más rápido)
    const values = sheet.getDataRange().getValues();

    // Buscar la fila de encabezados (la que tiene "MARCA" en col 1)
    let startRow = -1;
    for (let i = 0; i < values.length; i++) {
      if (String(values[i][COL.MARCA]).trim() === 'MARCA' &&
          String(values[i][COL.COD]).trim()   === 'COD') {
        startRow = i + 1; // datos empiezan en la siguiente
        break;
      }
    }

    if (startRow === -1) {
      return jsonResp({ error: 'No se encontró la fila de encabezados.' });
    }

    const productos = [];

    for (let i = startRow; i < values.length; i++) {
      const row = values[i];

      const cod  = String(row[COL.COD]  || '').trim();
      const mes  = String(row[COL.MES_PROD] || '').trim().toUpperCase();
      const nombre = String(row[COL.NOMBRE] || '').trim();

      // Saltar filas sin código o sin mes de producción asignado
      if (!cod || !mes || !nombre) continue;

      // Formatear fecha de entrega si existe
      let fechaEntrega = '';
      const fe = row[COL.FECHA_ENTREGA];
      if (fe instanceof Date && !isNaN(fe)) {
        fechaEntrega = Utilities.formatDate(
          fe, 'America/Argentina/Buenos_Aires', 'dd/MM/yyyy'
        );
      } else if (fe) {
        fechaEntrega = String(fe).trim();
      }

      productos.push({
        mes          : mes,
        nombre       : nombre,
        cod          : cod,
        cant         : parseInt(row[COL.UNID_PEDIDAS]) || 0,
        rubro        : String(row[COL.RUBRO]    || '').trim(),
        color        : String(row[COL.COLOR_BAS]|| '').trim(),
        cat          : String(row[COL.CAT_PLAN] || '').trim(),
        marca        : String(row[COL.MARCA]    || '').trim(),
        status       : String(row[COL.STATUS]   || '').trim(),
        foto_status  : String(row[COL.FOTO]     || '').trim(),
        calce        : String(row[COL.CALCE]    || '').trim(),
        tiro         : String(row[COL.TIRO]     || '').trim(),
        proveedor    : String(row[COL.PROVEEDOR]|| '').trim(),
        tela         : String(row[COL.TELA]     || '').trim(),
        disenador    : String(row[COL.DISENADOR]|| '').trim(),
        fecha_entrega: fechaEntrega,
        mes_ingreso  : String(row[COL.MES_INGRESO] || '').trim().toUpperCase(),
      });
    }

    return jsonResp({
      productos : productos,
      total     : productos.length,
      ts        : new Date().toISOString(),
    });

  } catch (err) {
    return jsonResp({ error: err.toString() });
  }
}

function jsonResp(data) {
  const out = ContentService.createTextOutput(JSON.stringify(data));
  out.setMimeType(ContentService.MimeType.JSON);
  return out;
}
