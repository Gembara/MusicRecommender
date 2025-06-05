#!/usr/bin/env python3
import requests
import sqlite3
from typing import Dict, List

def get_user_profile(user_id: int) -> Dict:
    """Отримуємо профіль користувача з бази даних"""
    conn = sqlite3.connect('../MusicRecommender.db')
    cursor = conn.cursor()
    
    # Базова інформація користувача
    cursor.execute("SELECT UserName, PreferredGenres FROM Users WHERE UserId = ?", (user_id,))
    user_info = cursor.fetchone()
    
    if not user_info:
        return {}
    
    # Історія прослуховування
    cursor.execute("""
        SELECT SpotifyTrackId, Rating, InteractionType 
        FROM UserSongInteractions 
        WHERE UserId = ? 
        ORDER BY Rating DESC
    """, (user_id,))
    interactions = cursor.fetchall()
    
    # Треки з історії
    cursor.execute("""
        SELECT DISTINCT s.Title, s.Artist 
        FROM UserSongInteractions ui
        JOIN SongFeatures s ON ui.SpotifyTrackId = s.SpotifyTrackId
        WHERE ui.UserId = ?
        ORDER BY ui.Rating DESC
        LIMIT 5
    """, (user_id,))
    top_tracks = cursor.fetchall()
    
    conn.close()
    
    return {
        'user_id': user_id,
        'name': user_info[0],
        'genres': user_info[1],
        'interactions_count': len(interactions),
        'top_tracks': top_tracks
    }

def get_recommendations(user_id: int, algorithm: str = 'hybrid', num_recs: int = 5) -> List[Dict]:
    """Отримуємо рекомендації для користувача"""
    try:
        response = requests.post('http://localhost:8000/recommend', json={
            'user_id': user_id,
            'algorithm': algorithm,
            'num_recommendations': num_recs
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get('recommendations', [])
        else:
            print(f"❌ Помилка API: {response.status_code}")
            return []
            
    except requests.exceptions.ConnectionError:
        print("❌ ML сервіс недоступний. Запустіть 'py start_service.py'")
        return []

def test_personal_recommendations():
    """Тестуємо персональні рекомендації для різних користувачів"""
    print("🎵 Тестування персональних рекомендацій\n")
    
    # Список користувачів для тестування
    test_users = [1, 13, 2, 3]  # Vens, Саша, TestUser1, TestUser2
    
    # Спочатку тренуємо моделі
    print("🎯 Тренування ML моделей...")
    try:
        train_response = requests.post('http://localhost:8000/train')
        if train_response.status_code == 200:
            print("✅ Моделі натреновані\n")
        else:
            print(f"❌ Помилка тренування: {train_response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ ML сервіс недоступний")
        return
    
    # Тестуємо кожного користувача
    for user_id in test_users:
        print(f"{'='*60}")
        print(f"👤 КОРИСТУВАЧ {user_id}")
        print(f"{'='*60}")
        
        # Отримуємо профіль
        profile = get_user_profile(user_id)
        if not profile:
            print(f"❌ Користувач {user_id} не знайдений\n")
            continue
        
        print(f"📋 Ім'я: {profile['name']}")
        print(f"🎭 Жанри: {profile['genres']}")
        print(f"📊 Взаємодій: {profile['interactions_count']}")
        print(f"⭐ Топ треки:")
        for i, (title, artist) in enumerate(profile['top_tracks'], 1):
            print(f"    {i}. {title} - {artist}")
        
        print(f"\n🤖 РЕКОМЕНДАЦІЇ:")
        
        # Тестуємо різні алгоритми
        algorithms = ['content_based', 'collaborative', 'hybrid']
        
        for algorithm in algorithms:
            print(f"\n🔄 {algorithm.upper()} рекомендації:")
            recommendations = get_recommendations(user_id, algorithm, 3)
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    title = rec.get('title', 'Unknown')
                    artist = rec.get('artist', 'Unknown')
                    confidence = rec.get('confidence_score', rec.get('predicted_rating', 0))
                    reason = rec.get('reason', 'Unknown reason')
                    
                    print(f"  {i}. {title} - {artist}")
                    print(f"     💯 Впевненість: {confidence:.1%}")
                    print(f"     💡 Причина: {reason}")
            else:
                print("  ❌ Немає рекомендацій")
        
        print(f"\n")
    
    # Порівняння рекомендацій
    print(f"{'='*60}")
    print("📊 ПОРІВНЯННЯ ПЕРСОНАЛІЗАЦІЇ")
    print(f"{'='*60}")
    
    print("🔍 Перевіряємо, чи отримують різні користувачі різні рекомендації...\n")
    
    user_recommendations = {}
    for user_id in test_users[:3]:  # Берємо перших 3
        recs = get_recommendations(user_id, 'hybrid', 5)
        if recs:
            user_recommendations[user_id] = [rec.get('title', 'Unknown') for rec in recs]
    
    # Аналізуємо унікальність
    all_recs = []
    for user_id, recs in user_recommendations.items():
        profile = get_user_profile(user_id)
        print(f"👤 {profile.get('name', f'User {user_id}')}:")
        for i, rec in enumerate(recs, 1):
            print(f"  {i}. {rec}")
        all_recs.extend(recs)
        print()
    
    # Статистика унікальності
    unique_recs = set(all_recs)
    total_recs = len(all_recs)
    
    print(f"📈 СТАТИСТИКА ПЕРСОНАЛІЗАЦІЇ:")
    print(f"   📝 Всього рекомендацій: {total_recs}")
    print(f"   🎯 Унікальних треків: {len(unique_recs)}")
    print(f"   📊 Рівень різноманітності: {len(unique_recs)/total_recs:.1%}")
    
    if len(unique_recs)/total_recs > 0.7:
        print(f"   ✅ ВІДМІННО! Користувачі отримують різні рекомендації")
    elif len(unique_recs)/total_recs > 0.5:
        print(f"   👍 ДОБРЕ! Помірна персоналізація")
    else:
        print(f"   ⚠️  ПОТРЕБУЄ ПОКРАЩЕННЯ! Рекомендації занадто схожі")

if __name__ == "__main__":
    test_personal_recommendations() 