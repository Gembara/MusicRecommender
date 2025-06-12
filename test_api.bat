@echo off
echo Testing ML API...

echo.
echo === Health Check ===
curl -X GET "http://localhost:8000/health"

echo.
echo.
echo === Training Models ===
curl -X POST "http://localhost:8000/train" -H "Content-Type: application/json" -d "{}"

echo.
echo.
echo === Test Recommendations ===
curl -X POST "http://localhost:8000/recommend" -H "Content-Type: application/json" -d "{\"user_id\": 1, \"limit\": 3}"

echo.
echo.
echo Done!
pause 