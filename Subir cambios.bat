@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === Subiendo cambios a GitHub ===
echo.
echo Limpiando archivos de bloqueo previos...
if exist ".git\index.lock" del ".git\index.lock"
if exist ".git\HEAD.lock" del ".git\HEAD.lock"
if exist ".git\MERGE_HEAD" del ".git\MERGE_HEAD"
if exist ".git\MERGE_MSG" del ".git\MERGE_MSG"
echo.
echo Configurando git...
git config user.email "nadiabeluzo@gmail.com"
git config user.name "nadiabeluzo-prog"
echo.
echo Commiteando cambios locales...
git add -A
git commit -m "fix: Facturacion esperada con precio promedio y mes A definir"
echo.
echo Sincronizando con GitHub (resolviendo conflictos a favor del local)...
git pull -X ours --no-edit origin main
echo.
echo Push final...
git push origin main
echo.
echo === Listo ===
echo Si arriba se ve algo como 'main -^> main' o 'Everything up-to-date', estamos bien.
echo Si dice 'rejected' o 'error', copiame este texto y lo arreglo.
echo.
pause
