@echo off
echo 🚀 Запуск ML сервісу для Music Recommender...
echo.

cd /d "%~dp0\ml_service"

echo 📂 Поточна директорія: %CD%
echo 🔍 Перевірка файлів...
dir main.py

echo.
echo 🌟 Запуск FastAPI сервера на порту 8000...
py -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo ML сервіс зупинено.
pause 