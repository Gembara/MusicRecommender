#!/usr/bin/env python3
import requests
import urllib3
import sqlite3
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_database_users():
    """Перевіряємо користувачів в базі даних"""
    print("🔍 Перевірка користувачів у базі даних:")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        
        # Перевіряємо користувачів
        df_users = pd.read_sql_query("SELECT * FROM Users", conn)
        print(f"👥 Знайдено {len(df_users)} користувачів:")
        for _, user in df_users.iterrows():
            print(f"   ID: {user['UserId']}, Ім'я: {user['UserName']}, Email: {user['Email']}")
        
        # Перевіряємо Favorites
        df_favorites = pd.read_sql_query("SELECT UserId, COUNT(*) as count FROM Favorites GROUP BY UserId", conn)
        print(f"\n❤️ Улюблені треки:")
        for _, fav in df_favorites.iterrows():
            print(f"   Користувач {fav['UserId']}: {fav['count']} улюблених треків")
        
        # Перевіряємо History
        df_history = pd.read_sql_query("SELECT UserId, COUNT(*) as count FROM History GROUP BY UserId", conn)
        print(f"\n📚 Історія прослуховування:")
        for _, hist in df_history.iterrows():
            print(f"   Користувач {hist['UserId']}: {hist['count']} записів в історії")
            
        conn.close()
        
        # Повертаємо ID останнього користувача для тестування
        if not df_users.empty:
            return int(df_users['UserId'].iloc[-1])  # Конвертуємо в звичайний int
        return None
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return None

def test_ml_with_user_id(user_id):
    """Тестуємо ML з конкретним ID користувача"""
    print(f"\n🎯 Тестування ML для користувача {user_id}:")
    
    BASE_URL = "https://localhost:5001"
    
    algorithms = ['content_based', 'collaborative', 'hybrid']
    
    for algorithm in algorithms:
        try:
            data = {
                "Algorithm": algorithm,
                "NumberOfRecommendations": 5,
                "UserId": user_id  # Явно передаємо ID користувача
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
    print("🎵 Тест поточного користувача та ML рекомендацій")
    print("=" * 50)
    
    user_id = check_database_users()
    
    if user_id:
        # Спочатку тренуємо моделі
        print(f"\n🔄 Тренування моделей...")
        try:
            response = requests.post("https://localhost:5001/ML/TrainModels", verify=False)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result.get('message', 'Тренування завершено')}")
            else:
                print("❌ Помилка тренування")
        except Exception as e:
            print(f"❌ Помилка тренування: {e}")
            
        print(f"\n🎯 Тестування ML для користувача 1:")
        test_user_id = 1  # Змінюємо на користувача Vens
        test_ml_with_user_id(test_user_id)
    else:
        print("❌ Не знайдено користувачів у базі даних") 