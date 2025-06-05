"""
Тестування нової системи ML тренування
Цей скрипт перевіряє роботу нових таблиць та сервісів для машинного навчання
"""

import sqlite3
import requests
import json
from datetime import datetime
import sys

def test_database_structure():
    """Перевіряємо чи створені нові таблиці"""
    print("🔍 Перевірка структури БД...")
    
    conn = sqlite3.connect("MusicRecommender.db")
    cursor = conn.cursor()
    
    # Перевіряємо нові таблиці
    tables = ['MLTrainingData', 'MLModelMetrics', 'MLUserProfiles', 'TrackSimilarity', 'UserSimilarity']
    
    for table in tables:
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cursor.fetchone()[0] > 0:
            print(f"✅ Таблиця {table} існує")
        else:
            print(f"❌ Таблиця {table} не знайдена")
    
    conn.close()

def test_data_collection_api():
    """Тестуємо API для збору тренувальних даних"""
    print("\n🔄 Тестування API збору даних...")
    
    base_url = "http://localhost:5000"  # Adjust if needed
    
    try:
        # Тест збору тренувальних даних
        response = requests.post(f"{base_url}/api/MLTraining/collect-training-data")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Збір даних успішний: {data.get('message', 'N/A')}")
        else:
            print(f"❌ Помилка збору даних: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("⚠️ Сервер не доступний. Запустіть додаток спочатку.")
        return False
    
    return True

def test_training_data_stats_api():
    """Тестуємо API статистики тренувальних даних"""
    print("\n📊 Тестування API статистики...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/api/MLTraining/training-data/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Статистика отримана:")
            print(f"   - Всього записів: {stats.get('totalTrainingRecords', 0)}")
            print(f"   - Унікальних користувачів: {stats.get('uniqueUsers', 0)}")
            print(f"   - Унікальних треків: {stats.get('uniqueTracks', 0)}")
        else:
            print(f"❌ Помилка отримання статистики: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("⚠️ Сервер не доступний")

def create_sample_training_data():
    """Створюємо тестові дані для ML тренування"""
    print("\n📝 Створення тестових даних...")
    
    conn = sqlite3.connect("MusicRecommender.db")
    cursor = conn.cursor()
    
    # Додаємо тестові взаємодії користувачів
    sample_interactions = [
        (1, "test_track_1", 1, 0.8, "2024-01-01 10:00:00", 150, 0, 1, 0),  # User 1 liked track 1
        (1, "test_track_2", 4, 0.2, "2024-01-01 10:05:00", 30, 1, 0, 0),   # User 1 skipped track 2
        (2, "test_track_1", 2, 0.9, "2024-01-01 11:00:00", 180, 0, 1, 1),  # User 2 loved track 1
        (2, "test_track_3", 1, 0.7, "2024-01-01 11:05:00", 120, 0, 0, 0),  # User 2 played track 3
    ]
    
    for interaction in sample_interactions:
        cursor.execute("""
            INSERT OR IGNORE INTO UserSongInteractions 
            (UserId, SpotifyTrackId, InteractionType, Rating, InteractionTime, PlayDuration, IsSkipped, IsLiked, IsRepeat)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, interaction)
    
    # Додаємо тестові фічі треків
    sample_features = [
        ("test_track_1", 0.8, 0.7, 0.9, 120.0, 0.1, 0.0, 0.1, -5.0, 80.0, 180000, 1, 1, 4, "Pop", "Test Artist 1"),
        ("test_track_2", 0.3, 0.4, 0.2, 80.0, 0.8, 0.5, 0.0, -10.0, 60.0, 200000, 2, 0, 4, "Acoustic", "Test Artist 2"),
        ("test_track_3", 0.9, 0.9, 0.8, 140.0, 0.0, 0.0, 0.0, -3.0, 90.0, 160000, 5, 1, 4, "Electronic", "Test Artist 3"),
    ]
    
    for features in sample_features:
        cursor.execute("""
            INSERT OR IGNORE INTO SongFeatures 
            (SpotifyTrackId, Danceability, Energy, Valence, Tempo, Acousticness, Instrumentalness, 
             Speechiness, Loudness, Popularity, DurationMs, Key, Mode, TimeSignature, Genre, Artist)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, features)
    
    conn.commit()
    conn.close()
    print("✅ Тестові дані створені")

def check_training_data():
    """Перевіряємо чи є дані в таблиці MLTrainingData"""
    print("\n🔍 Перевірка тренувальних даних...")
    
    conn = sqlite3.connect("MusicRecommender.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM MLTrainingData")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"✅ Знайдено {count} записів тренувальних даних")
        
        # Показуємо приклад запису
        cursor.execute("SELECT * FROM MLTrainingData LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"   Приклад запису: UserId={sample[1]}, TrackId={sample[2]}, Rating={sample[20]}")
    else:
        print("❌ Немає тренувальних даних")
    
    conn.close()

def test_user_profile_creation():
    """Тестуємо створення профілю користувача"""
    print("\n👤 Тестування створення профілю користувача...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.post(f"{base_url}/api/MLTraining/user-profile/1")
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Профіль користувача створено:")
            if 'profile' in profile:
                prefs = profile['profile'].get('preferences', {})
                print(f"   - Danceability: {prefs.get('danceability', 'N/A'):.3f}")
                print(f"   - Energy: {prefs.get('energy', 'N/A'):.3f}")
                print(f"   - Valence: {prefs.get('valence', 'N/A'):.3f}")
        else:
            print(f"❌ Помилка створення профілю: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("⚠️ Сервер не доступний")

def main():
    print("🎯 Тестування системи ML тренування")
    print("=" * 50)
    
    # 1. Перевіряємо структуру БД
    test_database_structure()
    
    # 2. Створюємо тестові дані
    create_sample_training_data()
    
    # 3. Тестуємо API (якщо сервер запущений)
    print(f"\n⚠️ Для тестування API запустіть сервер командою: dotnet run")
    print(f"Після запуску сервера можна тестувати API:")
    
    response = input("\nСервер запущений? (y/n): ").lower()
    if response == 'y':
        if test_data_collection_api():
            check_training_data()
            test_training_data_stats_api()
            test_user_profile_creation()
    
    print("\n✨ Тестування завершено!")
    print("\n📋 Наступні кроки:")
    print("1. Запустіть сервер: dotnet run")
    print("2. Зробіть POST запит: /api/MLTraining/collect-training-data")
    print("3. Перегляньте статистику: GET /api/MLTraining/training-data/stats")
    print("4. Створіть профіль користувача: POST /api/MLTraining/user-profile/{userId}")

if __name__ == "__main__":
    main() 