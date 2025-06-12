#!/usr/bin/env python3
"""
Тест рекомендацій після виправлення API формату
"""

import requests
import json
import time

def test_ml_service():
    """Тестуємо ML сервіс"""
    
    base_url = "http://localhost:8000"
    
    print("🎵 Тестуємо виправлені ML рекомендації")
    print("=" * 50)
    
    # 1. Перевірка здоров'я сервісу
    print("1️⃣ Перевірка здоров'я сервісу...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health_data = response.json()
        print(f"✅ Статус: {health_data['status']}")
        print(f"📊 Моделі натреновані: {health_data['models_trained']}")
        
        if not health_data['models_trained']:
            print("⚠️ Моделі не натреновані. Тренуємо...")
            
            # 2. Тренування моделей
            train_response = requests.post(f"{base_url}/train", timeout=30)
            train_data = train_response.json()
            print(f"🎯 Тренування: {train_data['success']}")
            print(f"📈 Повідомлення: {train_data['message']}")
            
            if train_data['success']:
                print("✅ Моделі успішно натреновані!")
            else:
                print("❌ Помилка тренування")
                return
                
    except Exception as e:
        print(f"❌ Помилка перевірки сервісу: {e}")
        return
    
    print("\n" + "=" * 50)
    
    # 3. Тестуємо рекомендації
    test_user_id = 1
    test_cases = [
        ("Hybrid", f"{base_url}/recommend"),
        ("Content", f"{base_url}/recommend/content"),
        ("Collaborative", f"{base_url}/recommend/collaborative"),
        ("SVD", f"{base_url}/recommend/svd")
    ]
    
    for algorithm, endpoint in test_cases:
        print(f"\n🔍 Тестуємо {algorithm} рекомендації...")
        
        try:
            payload = {
                "user_id": test_user_id,
                "limit": 5
            }
            
            response = requests.post(endpoint, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ {algorithm}: {data['success']}")
                print(f"📝 Повідомлення: {data['message']}")
                print(f"⏱️ Час обробки: {data.get('processing_time', 0):.3f}s")
                print(f"🔧 Алгоритм: {data.get('algorithm_used', 'Unknown')}")
                
                if data['success'] and data['recommendations']:
                    print(f"🎵 Рекомендації ({len(data['recommendations'])}):")
                    
                    for i, rec in enumerate(data['recommendations'][:3], 1):
                        print(f"  {i}. 🎵 {rec['artist']}")
                        print(f"     📊 Рейтинг: {rec['predicted_rating']:.2f}")
                        print(f"     🎯 Причина: {rec['reason']}")
                        
                        # Додаткова інформація з features
                        if rec.get('features'):
                            features = rec['features']
                            if features.get('title') and features['title'] != 'Unknown':
                                print(f"     🏷️ Назва: {features['title']}")
                            if features.get('genre') and features['genre'] != 'Unknown':
                                print(f"     🎼 Жанр: {features['genre']}")
                        print()
                else:
                    print(f"⚠️ Немає рекомендацій для {algorithm}")
                    
            else:
                print(f"❌ Помилка HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Помилка тестування {algorithm}: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Тестування завершено!")

if __name__ == "__main__":
    test_ml_service() 