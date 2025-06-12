#!/usr/bin/env python3
"""
🧪 Тест статусу ML сервісу
"""
import requests
import json

def test_ml_service():
    """Тестуємо статус ML сервісу"""
    base_url = "http://localhost:8000"
    
    print("🔬 Тестування ML Service...")
    print(f"🌐 URL: {base_url}")
    print("=" * 50)
    
    try:
        # Тест 1: Перевірка основного endpoint
        print("📍 Тест 1: Головна сторінка")
        response = requests.get(f"{base_url}/")
        print(f"   📊 Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Сервіс: {data.get('status', 'Unknown')}")
            print(f"   🔢 Версія: {data.get('version', 'Unknown')}")
            print(f"   🤖 Моделі натреновані: {data.get('models_trained', False)}")
            print(f"   📧 Повідомлення: {data.get('message', 'Unknown')}")
        print()
        
        # Тест 2: Перевірка health endpoint
        print("📍 Тест 2: Health Check")
        response = requests.get(f"{base_url}/health")
        print(f"   📊 Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Сервіс: {data.get('status', 'Unknown')}")
            print(f"   📊 БД статистика: {'✅' if data.get('database_stats') else '❌'}")
        print()
        
        # Тест 3: Перевірка status endpoint
        print("📍 Тест 3: Detailed Status")
        response = requests.get(f"{base_url}/status")
        print(f"   📊 Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🌐 Сервіс: {data.get('service_status', 'Unknown')}")
            print(f"   🗄️ БД підключена: {data.get('database_connected', False)}")
            print(f"   📈 Тренувальних даних: {data.get('training_data_count', 0)}")
        print()
        
        # Тест 4: Перевірка інформації про моделі
        print("📍 Тест 4: Models Info")
        response = requests.get(f"{base_url}/models/info")
        print(f"   📊 Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   🤖 Моделі натреновані: {data.get('models_trained', False)}")
            
            # Content-based модель
            content = data.get('content_based', {})
            print(f"   🎵 Content-Based: {'✅' if content.get('available') else '❌'}")
            
            # Collaborative модель
            collaborative = data.get('collaborative', {})
            print(f"   👥 Collaborative: {'✅' if collaborative.get('available') else '❌'}")
            
            # Hybrid модель
            hybrid = data.get('hybrid', {})
            print(f"   🔄 Hybrid: {'✅' if hybrid.get('available') else '❌'}")
        print()
        
        # Тест 5: Статистика даних
        print("📍 Тест 5: Data Statistics")
        response = requests.get(f"{base_url}/data/stats")
        print(f"   📊 Статус: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('stats', {})
                print(f"   📈 Статистика отримана: ✅")
                print(f"   📊 Даних: {json.dumps(stats, indent=6)}")
            else:
                print(f"   ❌ Помилка: {data.get('error', 'Unknown')}")
        print()
        
        print("🎉 Тестування завершено!")
        print("🌐 Документація API: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Не вдалося підключитися до ML сервісу")
        print("💡 Запустіть сервіс командою: py ml_service/main.py")
    except Exception as e:
        print(f"❌ Помилка тестування: {e}")

if __name__ == "__main__":
    test_ml_service() 