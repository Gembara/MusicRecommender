@echo off
echo 🔄 Запуск ML сервісу...
cd /d "ml_service"

echo 📦 Встановлення залежностей...
pip install fastapi uvicorn pandas numpy scikit-learn joblib

echo 🚀 Запуск сервера...
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause 