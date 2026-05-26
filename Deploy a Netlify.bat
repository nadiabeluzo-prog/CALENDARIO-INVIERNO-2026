@echo off
chcp 65001 >nul
title Deploy Calendario Batuk a Netlify
setlocal

set "TOKEN_FILE=%USERPROFILE%\.calendario-batuk-token"
set "SITE_ID=e76473c5-431e-4949-9c83-d59143300dbd"
set "WEB_DIR=%~dp0web"
set "ZIP_FILE=%TEMP%\calendario_batuk_deploy.zip"
set "RESP_FILE=%TEMP%\netlify_resp.json"
set "LOG_FILE=%~dp0deploy_log.txt"

echo === Deploy Calendario Batuk === > "%LOG_FILE%"
echo Fecha: %date% %time% >> "%LOG_FILE%"
echo Carpeta web: %WEB_DIR% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

if not exist "%WEB_DIR%" goto NOWEB
if not exist "%TOKEN_FILE%" goto ASKTOKEN
goto READTOKEN

:NOWEB
echo ERROR: No encuentro la carpeta web\
echo ERROR: web/ no existe >> "%LOG_FILE%"
pause
exit /b 1

:ASKTOKEN
echo ============================================================
echo  PRIMERA VEZ: necesito tu token de Netlify
echo ============================================================
echo.
echo  1) Abri en el navegador:
echo     https://app.netlify.com/user/applications#personal-access-tokens
echo.
echo  2) Generate token, copialo y pegalo aca:
echo.
set /p NETLIFY_TOKEN="Token: "
if "%NETLIFY_TOKEN%"=="" (
    echo Token vacio. Cancelado.
    echo Token vacio >> "%LOG_FILE%"
    pause
    exit /b 1
)
> "%TOKEN_FILE%" echo %NETLIFY_TOKEN%
echo Token guardado.
echo.
goto READTOKEN

:READTOKEN
set /p NETLIFY_TOKEN=<"%TOKEN_FILE%"
if "%NETLIFY_TOKEN%"=="" (
    echo ERROR: token vacio en archivo. Borra %TOKEN_FILE% y volve a correr.
    echo Token archivo vacio >> "%LOG_FILE%"
    pause
    exit /b 1
)
echo Token leido del archivo. >> "%LOG_FILE%"

echo Empaquetando carpeta web\...
if exist "%ZIP_FILE%" del "%ZIP_FILE%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Compress-Archive -Path '%WEB_DIR%\*' -DestinationPath '%ZIP_FILE%' -Force -ErrorAction Stop; Write-Host 'ZIP_OK' } catch { Write-Host ('ZIP_ERR: ' + $_.Exception.Message); exit 1 }" >> "%LOG_FILE%" 2>&1

if not exist "%ZIP_FILE%" (
    echo ERROR al empaquetar. Mira deploy_log.txt
    pause
    exit /b 1
)

for %%I in ("%ZIP_FILE%") do echo ZIP creado: %%~zI bytes >> "%LOG_FILE%"
echo Empaquetado OK. Subiendo a Netlify...

curl.exe -sS -w "HTTP_STATUS:%%{http_code}\n" -X POST ^
  -H "Authorization: Bearer %NETLIFY_TOKEN%" ^
  -H "Content-Type: application/zip" ^
  --data-binary "@%ZIP_FILE%" ^
  "https://api.netlify.com/api/v1/sites/%SITE_ID%/deploys" -o "%RESP_FILE%" >> "%LOG_FILE%" 2>&1

echo. >> "%LOG_FILE%"
echo --- Respuesta Netlify --- >> "%LOG_FILE%"
type "%RESP_FILE%" >> "%LOG_FILE%" 2>&1
echo. >> "%LOG_FILE%"

echo.
echo ============================================================
findstr /C:"deploy_ssl_url" "%RESP_FILE%" >nul 2>&1
if errorlevel 1 goto FAIL
echo  LISTO. Calendario actualizado.
echo  Link: https://calendario-batuk.netlify.app
echo  (puede tardar 30-60 segundos en propagarse)
goto END

:FAIL
echo  ALGO SALIO MAL.
echo.
echo  Respuesta de Netlify:
type "%RESP_FILE%"
echo.
echo  Detalle completo en: deploy_log.txt

:END
echo ============================================================
echo.
del "%ZIP_FILE%" 2>nul
echo.
echo Presiona una tecla para cerrar...
pause >nul
