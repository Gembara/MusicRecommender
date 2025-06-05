#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестування ML функціональності через API
"""

import requests
import json
import time

# Базовий URL додатку
BASE_URL = "https://localhost:5001"

def test_add_data():
    """Додати тестові дані через API"""
    print("🔄 Додавання тестових даних...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/Test/AddTestData",
            verify=False  # Ігноруємо SSL сертифікат для localhost
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ {result.get('message')}")
                return True
            else:
                print(f"❌ {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def check_ml_service():
    """Перевірити стан ML сервісу"""
    print("🔄 Перевірка ML сервісу...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/ML/CheckMLServiceStatus",
            verify=False
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ ML сервіс: {result.get('status')}")
                return True
            else:
                print(f"❌ ML сервіс недоступний")
                return False
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def train_ml_models():
    """Тренувати ML моделі"""
    print("🔄 Тренування ML моделей...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ML/TrainModels",
            verify=False
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Тренування: {result.get('message')}")
                return True
            else:
                print(f"❌ Тренування не вдалося: {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_ml_recommendations():
    """Тестувати ML рекомендації"""
    print("🔄 Тестування рекомендацій...")
    
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
                    
                    # Показуємо перші 3 рекомендації
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

def main():
    """Головна функція"""
    print("🎵 Music Recommender - ML Test Suite")
    print("=" * 50)
    
    # Крок 1: Перевіряємо ML сервіс
    if not check_ml_service():
        print("\n❌ ML сервіс недоступний. Запустіть Python ML сервіс на порту 8000")
        return
    
    # Крок 2: Додаємо тестові дані
    if not test_add_data():
        print("\n❌ Не вдалося додати тестові дані")
        return
    
    # Крок 3: Тренуємо моделі
    print("\n" + "="*30)
    if not train_ml_models():
        print("\n❌ Не вдалося натренувати моделі")
        return
    
    # Крок 4: Тестуємо рекомендації
    print("\n" + "="*30)
    test_ml_recommendations()
    
    print("\n🎉 Тестування завершено!")

if __name__ == "__main__":
    # Вимикаємо попередження про SSL
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    main() 