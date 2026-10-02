@echo off
title Suez Canal Tonnage Calculator Software
cd /d "%~dp0"

echo ================================================================
echo   SUEZ CANAL TONNAGE CALCULATOR SOFTWARE
echo   Naval Architecture Offset & Moorsom Tonnage Tool
echo ================================================================
echo.
echo Starting application server at http://localhost:5000 ...
echo Opening your browser automatically...
echo.

start "" "http://localhost:5000"
python app.py

pause
