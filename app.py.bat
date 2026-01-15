@echo off
chcp 65001 >nul
title Akademik Dergi Yonetim Sistemi
color 0A
cls
echo.
echo ========================================
echo  AKADEMIK DERGI YONETIM SISTEMI
echo ========================================
echo.
echo Uygulama baslatiliyor...
echo Tarayici otomatik olarak acilacak...
echo.
echo Uygulamayi durdurmak icin Ctrl+C tuslarina basin
echo.
echo ========================================
echo.

cd /d "%~dp0"
python app.py

echo.
echo.
echo Uygulama kapatildi.
pause
