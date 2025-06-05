import sqlite3
import random
from datetime import datetime, timedelta

def add_sasha():
    print("🎵 Додавання користувача Саша...")
    
    try:
        conn = sqlite3.connect('../MusicRecommender.db')
        cursor = conn.cursor()
        
        # Перевіряємо існуючих користувачів
        cursor.execute("SELECT UserId, UserName FROM Users")
        users = cursor.fetchall()
        print(f"Існуючі користувачі ({len(users)}):", users)
        
        # Перевіряємо чи існує Саша
        cursor.execute("SELECT UserId FROM Users WHERE UserName = 'Саша'")
        sasha = cursor.fetchone()
        
        if sasha:
            user_id = sasha[0]
            print(f"Саша вже існує з ID: {user_id}")
        else:
            # Додаємо Сашу
            cursor.execute("""
                INSERT INTO Users (UserName, Email, PreferredGenres, 
                                 AvgTempo, AvgEnergy, AvgDanceability, AvgValence,
                                 AvgAcousticness, AvgInstrumentalness, AvgLoudness, AvgSpeechiness,
                                 CreatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'Саша', 'sasha@music.com', 'Rock,Alternative,Indie',
                125.0, 0.75, 0.65, 0.55, 0.15, 0.05, -8.0, 0.10,
                datetime.now().isoformat()
            ))
            user_id = cursor.lastrowid
            print(f"✅ Створено Сашу з ID: {user_id}")
        
        # Перевіряємо доступні треки
        cursor.execute("SELECT SpotifyTrackId, Title, Artist FROM SongFeatures LIMIT 10")
        available_tracks = cursor.fetchall()
        print(f"Доступні треки ({len(available_tracks)}):")
        for track in available_tracks:
            print(f"  - {track[0]}: {track[1]} - {track[2]}")
        
        # Додаємо взаємодії (Саша любить енергійну музику)
        tracks = [
            ('6DCZcSspjsKoFjzjrWoCdn', 4.8),  # God's Plan
            ('7KXjTSCq5nL1LoYtL7XAwS', 5.0),  # HUMBLE.
            ('2xLMifQCjDGFmkHkpNLD9h', 4.9),  # Sicko Mode
            ('7wGoVu4Dady5GV0Sv4UIsx', 4.7),  # Rockstar
            ('0sf0KYcqVmpUCOG2DIMHtH', 4.5),  # Blinding Lights
        ]
        
        # Очищуємо старі дані Саші
        cursor.execute("DELETE FROM UserSongInteractions WHERE UserId = ?", (user_id,))
        deleted = cursor.rowcount
        print(f"Видалено {deleted} старих взаємодій")
        
        added_interactions = 0
        for track_id, rating in tracks:
            # Перевіряємо чи існує трек
            cursor.execute("SELECT SpotifyTrackId FROM SongFeatures WHERE SpotifyTrackId = ?", (track_id,))
            if cursor.fetchone():
                cursor.execute("""
                    INSERT INTO UserSongInteractions 
                    (UserId, SpotifyTrackId, InteractionType, Rating, PlayDuration, 
                     IsLiked, IsSkipped, IsRepeat, InteractionTime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, track_id, 'listen', rating, 
                    random.randint(120, 240),
                    1 if rating >= 4.0 else 0,
                    0, 1 if rating >= 4.5 else 0,
                    datetime.now().isoformat()
                ))
                added_interactions += 1
                print(f"  ✅ Додано взаємодію з треком {track_id} (рейтинг: {rating})")
            else:
                print(f"  ❌ Трек {track_id} не знайдено в базі")
        
        # Також додаємо в історію - спочатку дивимось структуру таблиці
        cursor.execute("PRAGMA table_info(History)")
        history_columns = cursor.fetchall()
        print("\nСтруктура таблиці History:")
        for col in history_columns:
            print(f"  {col[1]} ({col[2]}) - NOT NULL: {col[3]}")
        
        # Додаємо простіший запис в історію
        cursor.execute("DELETE FROM History WHERE UserId = ?", (user_id,))
        added_history = 0
        
        # Додаємо тільки основні поля, які точно існують
        for track_id, rating in tracks[:2]:  # Додаємо тільки топ 2 в історію
            cursor.execute("""
                SELECT Title, Artist FROM SongFeatures WHERE SpotifyTrackId = ?
            """, (track_id,))
            track_info = cursor.fetchone()
            
            if track_info:
                try:
                    cursor.execute("""
                        INSERT INTO History (UserId, Title, Artist, SpotifyTrackId, ImageUrl, ListenedAt)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        user_id,
                        track_info[0] or 'Unknown Track',  # Title
                        track_info[1] or 'Unknown Artist',  # Artist
                        track_id,
                        f"https://i.scdn.co/image/ab67616d0000b273default",
                        datetime.now().isoformat()
                    ))
                    added_history += 1
                    print(f"  ✅ Додано в історію: {track_info[0]} - {track_info[1]}")
                except Exception as hist_err:
                    print(f"  ❌ Помилка додавання в історію: {hist_err}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Саша успішно оновлена!")
        print(f"   👤 ID користувача: {user_id}")
        print(f"   🎵 Музичні преференції: Rock, Alternative, Indie")
        print(f"   📊 Додано {added_interactions} взаємодій")
        print(f"   📜 Додано {added_history} записів в історію")
        print(f"   🎯 Характер: Любить енергійну музику та рок")
        print(f"   ⭐ Топ треки: HUMBLE. (5.0★), Sicko Mode (4.9★), God's Plan (4.8★)")
        
        # Тепер протестуємо рекомендації
        print(f"\n🤖 Тестуємо рекомендації для Саші...")
        test_ml_for_sasha(user_id)
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

def test_ml_for_sasha(user_id):
    """Тестуємо ML рекомендації для Саші"""
    try:
        import requests
        
        # Спочатку тренуємо моделі
        print("  🎯 Тренування ML моделей...")
        train_response = requests.post('http://localhost:8000/train')
        if train_response.status_code == 200:
            print("  ✅ Моделі натреновані")
        else:
            print(f"  ❌ Помилка тренування: {train_response.status_code}")
            return
        
        # Тестуємо різні типи рекомендацій
        algorithms = ['content_based', 'collaborative', 'hybrid']
        
        for algorithm in algorithms:
            print(f"\n  🔄 Тестуємо {algorithm} рекомендації...")
            req_data = {
                'user_id': user_id,
                'algorithm': algorithm,
                'num_recommendations': 5
            }
            
            rec_response = requests.post('http://localhost:8000/recommend', json=req_data)
            if rec_response.status_code == 200:
                recommendations = rec_response.json()
                if recommendations and 'recommendations' in recommendations:
                    recs = recommendations['recommendations']
                    print(f"  ✅ Отримано {len(recs)} рекомендацій:")
                    for i, rec in enumerate(recs[:3], 1):
                        title = rec.get('title', 'Unknown')
                        artist = rec.get('artist', 'Unknown')
                        confidence = rec.get('confidence_score', 0)
                        print(f"    {i}. {title} - {artist} ({confidence:.1%})")
                else:
                    print(f"  ❌ Порожні рекомендації")
            else:
                print(f"  ❌ Помилка рекомендацій: {rec_response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("  ❌ ML сервіс недоступний. Запустіть спочатку ML сервіс командою 'py start_service.py'")
    except Exception as e:
        print(f"  ❌ Помилка тестування ML: {e}")

if __name__ == "__main__":
    add_sasha() 