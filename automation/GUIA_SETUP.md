# Setup auto-sync cada 2 horas

Tiempo total: 30-40 minutos. Se hace una sola vez.

Después, el calendario se actualiza solo cada 2 horas (lunes a viernes, 9 a 21 hora Argentina) sin que tengas que tocar nada.

---

## Paso 1 · Crear cuenta de GitHub (5 min)

1. Andá a https://github.com/signup
2. Mail, password, username (ej: `nadiabeluzo`)
3. Verificá el mail.

---

## Paso 2 · Crear el repo y subir el código (10 min)

1. En GitHub, click en el `+` arriba a la derecha → **New repository**.
2. Repository name: `calendario-batuk` (o como quieras)
3. **PRIVATE** (importantísimo — tiene tus fotos y datos)
4. NO marques "Add a README" — el repo arranca vacío.
5. **Create repository**.
6. GitHub te muestra una pantalla con comandos. Vamos a usar GitHub Desktop (más fácil):
   - Descargá GitHub Desktop: https://desktop.github.com/
   - Instalalo, abrilo, login con tu cuenta.
   - **File → Add Local Repository** → seleccioná la carpeta `C:\Users\user\Desktop\CALENDARIO INVIERNO 2026`
   - Si te dice que no es un repo, click en "create a repository" → confirmá.
   - **Publish repository** → desmarcá "Keep this code private" si está marcado al revés (debe quedar PRIVADO) → Publish.

Tu código ya está en GitHub.

---

## Paso 3 · Service Account de Google Drive (10 min)

Esto es para que GitHub pueda leer tu Drive sin tu password.

1. Andá a https://console.cloud.google.com/ (login con tu cuenta de Google).
2. Arriba a la izquierda, dropdown de proyectos → **New Project**.
   - Project name: `calendario-batuk-sync` → Create.
3. Esperá ~10 segundos a que cree el proyecto y seleccionalo en el dropdown.
4. En el buscador de arriba escribí "Google Drive API" → click en el resultado → **Enable**.
5. Buscá "Service Accounts" → **Service Accounts** → **+ Create Service Account**.
   - Name: `sync-calendario`
   - Click Create and Continue → Continue → Done.
6. En la lista de service accounts, click en `sync-calendario@...` que recién creaste.
7. Pestaña **Keys** → **Add Key → Create new key → JSON → Create**.
8. Se descarga un archivo `.json`. **Guardalo en un lugar seguro, no lo subas a ningún lado.**
9. Anotá el mail del service account (algo como `sync-calendario@calendario-batuk-sync.iam.gserviceaccount.com`).

---

## Paso 4 · Compartir las carpetas de Drive con el service account (3 min)

El service account es como un usuario más. Tiene que tener permiso de "Lector" en:

1. **Archivo del maestro** (el xlsx)
   - Click derecho en Drive → Compartir
   - Pegá el mail del service account → seleccioná "Lector" → Enviar (sin notificar)

2. **Carpeta de fotos** — la `FOTOS ECOMMERCE` (la que contiene 2026 con todas las subcarpetas)
   - Click derecho → Compartir → mismo mail → Lector → Enviar

Con solo compartir la carpeta padre `FOTOS ECOMMERCE`, ya tiene acceso a todas las subcarpetas.

---

## Paso 5 · Token de Netlify (3 min)

1. https://app.netlify.com/user/applications#personal-access-tokens
2. **New access token** → descripción: `github-sync` → expira en 365 días → Generate.
3. Copiá el token (empieza con `nfp_...`). No vas a poder verlo de nuevo.

---

## Paso 6 · Cargar los secrets en GitHub (3 min)

En tu repo de GitHub:

1. **Settings** (pestaña arriba) → **Secrets and variables → Actions** → **New repository secret**.
2. Crear estos 3 secrets, uno por uno:

| Name | Value |
|---|---|
| `GDRIVE_SA_JSON` | Abrí el archivo .json del paso 3 con Notepad, copiá TODO el contenido, pegalo acá |
| `NETLIFY_TOKEN` | El token `nfp_...` del paso 5 |
| `NETLIFY_SITE_ID` | `e76473c5-431e-4949-9c83-d59143300dbd` |

---

## Paso 7 · Probar manualmente (2 min)

1. En tu repo → pestaña **Actions** (arriba).
2. Si te aparece un cartel "Workflows aren't being run...", click en "I understand my workflows, go ahead and enable them".
3. En la barra izquierda, click en **Auto-sync calendario**.
4. Botón **Run workflow** (derecha) → Run workflow.
5. A los ~10 seg empieza a correr. Click en la línea que aparece para ver el log en vivo.
6. Si todo va bien, en ~2 min termina con tildes verdes y tu sitio está actualizado.

---

## Listo

Desde ahora se actualiza solo cada 2 hs en horario laboral. Si querés forzar una actualización en cualquier momento, vas a **Actions → Auto-sync calendario → Run workflow**.

Si algo falla, vas a **Actions** y click en la corrida fallida — el log te dice el error exacto.

## Cambiar el horario

Si querés cambiar la frecuencia, editás `.github/workflows/sync.yml` la línea del cron:

- `'0 */2 * * *'` → cada 2 hs todos los días, 24 hs
- `'0 12-23/2 * * 1-5'` → cada 2 hs entre 9 y 20 hora Argentina, lunes a viernes (actual)
- `'0 12 * * 1-5'` → una vez por día a las 9 hora Argentina, lunes a viernes

Hacés el cambio en GitHub web (botón lapicito) → Commit changes.
