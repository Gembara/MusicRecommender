import requests
import json

# Тестуємо ML service
base_url = "http://localhost:8000"

def test_health():
    print("🔍 Перевірка стану сервісу...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Сервіс працює: {data.get('message', 'OK')}")
            print(f"Моделі натреновані: {data.get('models_trained', False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Помилка підключення: {e}")
        return False

def test_train():
    print("\n🎯 Тренування моделей...")
    try:
        response = requests.post(f"{base_url}/train")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Тренування: {data.get('message', 'OK')}")
            print(f"Час тренування: {data.get('training_time', 0):.2f}с")
            return True
        else:
            print(f"❌ Помилка тренування: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Помилка тренування: {e}")
        return False

def test_recommendations(user_id=1):
    print(f"\n🎵 Тест рекомендацій для користувача {user_id}...")
    
    # Тестуємо різні типи рекомендацій
    algorithms = [
        ("hybrid", "Гібридні"),
        ("content", "Content-Based"),
        ("collaborative", "Collaborative"),
        ("svd", "SVD")
    ]
    
    for algo_endpoint, algo_name in algorithms:
        print(f"\n--- {algo_name} рекомендації ---")
        try:
            if algo_endpoint == "hybrid":
                url = f"{base_url}/recommend"
            else:
                url = f"{base_url}/recommend/{algo_endpoint}"
            
            payload = {
                "user_id": user_id,
                "limit": 5
            }
            
            response = requests.post(url, json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Алгоритм: {data.get('algorithm_used', algo_name)}")
                print(f"Час обробки: {data.get('processing_time', 0):.3f}с")
                
                recommendations = data.get('recommendations', [])
                print(f"Знайдено {len(recommendations)} рекомендацій:")
                
                for i, rec in enumerate(recommendations, 1):
                    track_id = rec.get('track_id', 'Unknown ID')
                    artist = rec.get('artist', 'Unknown Artist')
                    title = rec.get('features', {}).get('title', 'Unknown Track')
                    rating = rec.get('predicted_rating', 0)
                    reason = rec.get('reason', 'No reason')
                    
                    print(f"  {i}. {artist} - {title}")
                    print(f"     ID: {track_id}")
                    print(f"     Рейтинг: {rating:.2f}")
                    print(f"     Причина: {reason}")
                    print()
                    
            else:
                print(f"❌ Помилка {algo_name}: {response.text}")
                
        except Exception as e:
            print(f"❌ Помилка {algo_name}: {e}")

if __name__ == "__main__":
    print("🚀 Тестування ML системи рекомендацій...")
    
    # Перевірка з'єднання
    if not test_health():
        print("❌ Сервіс недоступний!")
        exit(1)
    
    # Тренування
    if not test_train():
        print("❌ Не вдалося натренувати моделі!")
        exit(1)
    
    # Тестування рекомендацій для користувача 1
    test_recommendations(1)
    
    print("\n✅ Тестування завершено!") 