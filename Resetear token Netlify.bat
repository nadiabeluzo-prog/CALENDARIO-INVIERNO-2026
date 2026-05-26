@echo off
chcp 65001 >nul
title Resetear token Netlify

set "TOKEN_FILE=%USERPROFILE%\.calendario-batuk-token"

if exist "%TOKEN_FILE%" (
    del "%TOKEN_FILE%"
    echo Token borrado: %TOKEN_FILE%
) else (
    echo No habia token guardado en %TOKEN_FILE%
)

echo.
echo Listo. Ahora corre "Deploy a Netlify.bat" y va a pedirte el token de nuevo.
echo.
pause
