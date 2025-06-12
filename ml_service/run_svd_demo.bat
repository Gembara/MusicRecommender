@echo off
echo.
echo 🎵 SVD Демонстрація для Music Recommender
echo ==========================================
echo.

cd /d "%~dp0"

echo Запуск SVD демонстрації...
python simple_svd_demo.py

echo.
echo Демонстрація завершена!
pause 