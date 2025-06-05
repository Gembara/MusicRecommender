#!/usr/bin/env python3
import requests
import json

def debug_ml_service():
    """Детальний дебаг ML сервісу"""
    print("🔍 Дебаг ML сервісу")
    
    base_url = "http://localhost:8000"
    
    # 1. Тренування
    print("\n🔄 Тренування моделей...")
    try:
        response = requests.post(f"{base_url}/train", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Тренування успішне:")
            for key, value in data.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ Помилка тренування: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Помилка тренування: {e}")
        return
    
    # 2. Тест рекомендацій для користувача 1
    print(f"\n🎯 Тест рекомендацій для користувача 1:")
    algorithms = ["content_based", "collaborative", "hybrid"]
    
    for algorithm in algorithms:
        try:
            payload = {
                "user_id": 1,
                "algorithm": algorithm,
                "n_recommendations": 5
            }
            
            response = requests.post(f"{base_url}/recommend", 
                                   json=payload, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get('recommendations', [])
                print(f"✅ {algorithm}: {len(recommendations)} рекомендацій")
                
                for i, rec in enumerate(recommendations[:3], 1):
                    title = rec.get('title', 'No Title')
                    artist = rec.get('artist', 'No Artist')
                    score = rec.get('predicted_rating', 0)
                    print(f"   {i}. {title} - {artist} ({score:.1f}%)")
                    
            else:
                print(f"❌ {algorithm}: HTTP {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ {algorithm}: Помилка - {e}")

if __name__ == "__main__":
    debug_ml_service() 