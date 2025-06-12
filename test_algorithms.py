#!/usr/bin/env python3
"""
🚀 Тест різних алгоритмів ML рекомендацій
Перевіряємо що кожен алгоритм дає різні результати
"""

import requests
import json
import time

# Конфігурація
ML_SERVICE_URL = "http://localhost:8001"
USER_ID = 1
LIMIT = 10

def test_health():
    """Перевірка здоров'я сервісу"""
    try:
        response = requests.get(f"{ML_SERVICE_URL}/health", timeout=5)
        print("✅ ML сервіс працює!")
        return True
    except Exception as e:
        print(f"❌ ML сервіс недоступний: {e}")
        return False

def train_models():
    """Тренування моделей"""
    print("\n🏋️ Тренування моделей...")
    try:
        response = requests.post(f"{ML_SERVICE_URL}/train", timeout=30)
        result = response.json()
        if result.get('success'):
            print("✅ Моделі натреновані!")
            print(f"   Час тренування: {result.get('training_time', 0):.2f}s")
            return True
        else:
            print(f"❌ Помилка тренування: {result.get('message')}")
            return False
    except Exception as e:
        print(f"❌ Помилка тренування: {e}")
        return False

def test_algorithm(algorithm_name, endpoint, user_id=USER_ID, limit=LIMIT):
    """Тестування окремого алгоритму"""
    print(f"\n🧪 Тестування {algorithm_name}...")
    
    try:
        payload = {"user_id": user_id, "limit": limit}
        response = requests.post(f"{ML_SERVICE_URL}{endpoint}", 
                               json=payload, 
                               timeout=10)
        
        result = response.json()
        
        if result.get('success'):
            recommendations = result.get('recommendations', [])
            print(f"✅ {algorithm_name}: {len(recommendations)} рекомендацій")
            
            # Показуємо перші 3 рекомендації
            for i, rec in enumerate(recommendations[:3]):
                track_title = rec.get('title', 'Unknown')
                artist = rec.get('artist', 'Unknown')
                rating = rec.get('predicted_rating', 0)
                reason = rec.get('reason', 'No reason')
                algorithm = rec.get('algorithm', 'Unknown')
                
                print(f"   {i+1}. {track_title} - {artist}")
                print(f"      Рейтинг: {rating:.2f} | Алгоритм: {algorithm}")
                print(f"      Причина: {reason}")
            
            return recommendations
        else:
            print(f"❌ {algorithm_name}: {result.get('message')}")
            return []
            
    except Exception as e:
        print(f"❌ Помилка {algorithm_name}: {e}")
        return []

def compare_algorithms():
    """Порівняння результатів різних алгоритмів"""
    print("\n🔍 ПОРІВНЯННЯ АЛГОРИТМІВ")
    print("=" * 50)
    
    # Тестуємо всі алгоритми
    algorithms = {
        "Content-Based": "/recommend/content",
        "Collaborative KNN": "/recommend/collaborative", 
        "SVD Matrix Factorization": "/recommend/svd",
        "Hybrid (All Combined)": "/recommend"
    }
    
    results = {}
    for name, endpoint in algorithms.items():
        results[name] = test_algorithm(name, endpoint)
    
    # Аналізуємо різноманітність
    print("\n📊 АНАЛІЗ РІЗНОМАНІТНОСТІ:")
    print("=" * 50)
    
    all_tracks = set()
    for name, recs in results.items():
        track_ids = {rec.get('track_id') for rec in recs}
        all_tracks.update(track_ids)
        print(f"{name}: {len(track_ids)} унікальних треків")
    
    print(f"\nЗагалом унікальних треків: {len(all_tracks)}")
    
    # Перевірка пересічень
    print("\n🔗 ПЕРЕСІЧЕННЯ АЛГОРИТМІВ:")
    algorithms_list = list(results.keys())
    for i, alg1 in enumerate(algorithms_list):
        for alg2 in algorithms_list[i+1:]:
            tracks1 = {rec.get('track_id') for rec in results[alg1]}
            tracks2 = {rec.get('track_id') for rec in results[alg2]}
            
            intersection = tracks1.intersection(tracks2)
            similarity = len(intersection) / max(len(tracks1), len(tracks2)) if tracks1 or tracks2 else 0
            
            print(f"   {alg1} ∩ {alg2}: {len(intersection)} спільних треків ({similarity:.1%})")

def main():
    """Головна функція"""
    print("🎵 ТЕСТУВАННЯ ML АЛГОРИТМІВ МУЗИЧНИХ РЕКОМЕНДАЦІЙ")
    print("=" * 60)
    
    # Перевірка сервісу
    if not test_health():
        print("❌ Сервіс недоступний. Запустіть ML сервіс спочатку.")
        return
    
    # Тренування моделей
    if not train_models():
        print("❌ Не вдалося натренувати моделі.")
        return
    
    # Порівняння алгоритмів
    compare_algorithms()
    
    print("\n🎯 ВИСНОВОК:")
    print("Якщо алгоритми працюють правильно, вони повинні давати різні рекомендації!")
    print("✅ Content-Based: фокус на аудіо характеристики")
    print("✅ Collaborative KNN: фокус на схожих користувачів") 
    print("✅ SVD: фокус на латентні фактори")
    print("✅ Hybrid: комбінація всіх підходів")

if __name__ == "__main__":
    main() 