#!/usr/bin/env python3
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:5001"

def test_ml_recommendations():
    """Тестуємо ML рекомендації з існуючими даними"""
    print("🎵 Швидкий тест ML рекомендацій")
    print("=" * 40)
    
    # 1. Перевіряємо ML сервіс
    try:
        response = requests.get(f"{BASE_URL}/ML/CheckMLServiceStatus", verify=False)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ML сервіс: {result.get('status', 'unknown')}")
        else:
            print("❌ ML сервіс недоступний")
            return
    except Exception as e:
        print(f"❌ Помилка підключення: {e}")
        return
    
    # 2. Тренуємо моделі
    print("\n🔄 Тренування моделей...")
    try:
        response = requests.post(f"{BASE_URL}/ML/TrainModels", verify=False)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Тренування: {result.get('message', 'OK')}")
        else:
            print("❌ Помилка тренування")
    except Exception as e:
        print(f"❌ Помилка тренування: {e}")
    
    # 3. Тестуємо всі алгоритми
    algorithms = ['content_based', 'collaborative', 'hybrid']
    
    for algorithm in algorithms:
        print(f"\n🎯 Тестування {algorithm}...")
        try:
            data = {
                "Algorithm": algorithm,
                "NumberOfRecommendations": 5
            }
            
            response = requests.post(
                f"{BASE_URL}/ML/GetMLRecommendations",
                json=data,
                verify=False,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data'):
                    recommendations = result['data']['recommendations']
                    print(f"✅ {algorithm}: {len(recommendations)} рекомендацій")
                    
                    # Показуємо рекомендації
                    for i, rec in enumerate(recommendations[:3], 1):
                        title = rec.get('title', 'Unknown')
                        artist = rec.get('artist', 'Unknown')
                        confidence = rec.get('confidence_score', 0) * 100
                        print(f"   {i}. {title} - {artist} ({confidence:.1f}%)")
                else:
                    print(f"❌ {algorithm}: {result.get('message', 'Немає рекомендацій')}")
            else:
                print(f"❌ {algorithm}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {algorithm}: Помилка - {e}")

if __name__ == "__main__":
    test_ml_recommendations() 