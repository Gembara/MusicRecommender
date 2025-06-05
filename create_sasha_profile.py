#!/usr/bin/env python3
import sqlite3
import random
from datetime import datetime, timedelta

def create_sasha_profile():
    """Створюємо профіль для користувача Саша з унікальними музичними смаками"""
    print("🎵 Створення профілю для користувача Саша...")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        cursor = conn.cursor()
        
        # Спочатку перевіримо, чи існує користувач Саша
        cursor.execute("SELECT UserId FROM Users WHERE UserName = 'Саша'")
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user[0]
            print(f"   ✅ Користувач Саша вже існує з ID: {user_id}")
        else:
            # Створюємо нового користувача Саша
            cursor.execute("""
                INSERT INTO Users (UserName, Email, PreferredGenres, 
                                 AvgTempo, AvgEnergy, AvgDanceability, AvgValence,
                                 AvgAcousticness, AvgInstrumentalness, AvgLoudness, AvgSpeechiness,
                                 CreatedAt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'Саша',
                'sasha@music.com',
                'Rock,Alternative,Indie',  # Саша любить рок та альтернативу
                125.0,   # Середній темп
                0.75,    # Висока енергія
                0.65,    # Помірна танцювальність
                0.55,    # Середня позитивність
                0.15,    # Низька акустичність (любить електричні інструменти)
                0.05,    # Мало інструментальної музики
                -8.0,    # Гучна музика
                0.10,    # Мало spoken word
                datetime.now().isoformat()
            ))
            
            user_id = cursor.lastrowid
            print(f"   ✅ Створено нового користувача Саша з ID: {user_id}")
        
        # Отримуємо список доступних треків
        cursor.execute("SELECT SpotifyTrackId, Title, Artist FROM SongFeatures")
        available_tracks = cursor.fetchall()
        
        if not available_tracks:
            print("   ❌ Не знайдено треків у базі даних")
            return False
        
        # Саша має специфічні смаки - більше любить рок та енергійну музику
        sasha_preferences = [
            # Високі рейтинги для енергійних треків
            ('6DCZcSspjsKoFjzjrWoCdn', 4.8),  # God's Plan - Drake (хоча це не рок, але енергійне)
            ('7KXjTSCq5nL1LoYtL7XAwS', 5.0),  # HUMBLE. - Kendrick Lamar (енергійний)
            ('2xLMifQCjDGFmkHkpNLD9h', 4.9),  # Sicko Mode - Travis Scott
            ('7wGoVu4Dady5GV0Sv4UIsx', 4.7),  # Rockstar - Post Malone
            ('0sf0KYcqVmpUCOG2DIMHtH', 4.5),  # Blinding Lights - The Weeknd
            # Менші рейтинги для спокійнішої музики
            ('0u2P5u6lvoDfwTYjAADbn4', 3.5),  # lovely - Billie Eilish (тихіша)
            ('7qEHsqek33rTcFNT9PFqLf', 3.2),  # Someone You Loved (балада)
            ('6UelLqGlWMcVH1E5c4H7lY', 3.8),  # Watermelon Sugar
        ]
        
        # Очищуємо попередні взаємодії Саші
        cursor.execute("DELETE FROM UserSongInteractions WHERE UserId = ?", (user_id,))
        cursor.execute("DELETE FROM History WHERE UserId = ?", (user_id,))
        
        interactions_added = 0
        history_added = 0
        
        # Додаємо взаємодії на основі преференцій Саші
        for track_id, rating in sasha_preferences:
            # Перевіряємо, чи існує такий трек
            track_exists = any(track[0] == track_id for track in available_tracks)
            if not track_exists:
                continue
                
            # Додаємо взаємодію
            cursor.execute("""
                INSERT OR REPLACE INTO UserSongInteractions 
                (UserId, SpotifyTrackId, InteractionType, Rating, PlayDuration, 
                 IsLiked, IsSkipped, IsRepeat, InteractionTime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                track_id,
                'listen',
                rating,
                random.randint(120, 240),  # Тривалість прослуховування
                1 if rating >= 4.0 else 0,  # Лайк якщо рейтинг високий
                1 if rating < 3.0 else 0,   # Скіп якщо рейтинг низький
                1 if rating >= 4.5 else 0,  # Повтор якщо дуже подобається
                (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            ))
            interactions_added += 1
            
            # Додаємо в історію прослуховування
            track_info = next((t for t in available_tracks if t[0] == track_id), None)
            if track_info:
                cursor.execute("""
                    INSERT INTO History (UserId, Title, Artist, SpotifyTrackId, 
                                       ImageUrl, ListenedAt)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    track_info[1],  # Title
                    track_info[2],  # Artist
                    track_id,
                    f"https://i.scdn.co/image/ab67616d0000b273{track_id}",
                    (datetime.now() - timedelta(days=random.randint(1, 15))).isoformat()
                ))
                history_added += 1
        
        # Додаємо кілька додаткових випадкових взаємодій для різноманітності
        other_tracks = [track for track in available_tracks 
                       if track[0] not in [pref[0] for pref in sasha_preferences]]
        
        for _ in range(min(5, len(other_tracks))):
            track = random.choice(other_tracks)
            rating = random.uniform(2.5, 4.2)  # Середні рейтинги для інших треків
            
            cursor.execute("""
                INSERT OR REPLACE INTO UserSongInteractions 
                (UserId, SpotifyTrackId, InteractionType, Rating, PlayDuration, 
                 IsLiked, IsSkipped, IsRepeat, InteractionTime)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                track[0],
                'listen',
                rating,
                random.randint(80, 200),
                1 if rating >= 3.8 else 0,
                1 if rating < 3.0 else 0,
                0,  # Рідко повторює інші треки
                (datetime.now() - timedelta(days=random.randint(1, 45))).isoformat()
            ))
            interactions_added += 1
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Профіль Саші створено успішно!")
        print(f"   👤 ID користувача: {user_id}")
        print(f"   🎵 Музичні преференції: Rock, Alternative, Indie")
        print(f"   📊 Додано {interactions_added} взаємодій")
        print(f"   📜 Додано {history_added} записів в історію")
        print(f"   🎯 Характер: Любить енергійну музику, рок та альтернативу")
        print(f"   ⭐ Високі рейтинги: HUMBLE., Sicko Mode, Rockstar")
        print(f"   👎 Нижчі рейтинги: Балади та спокійна музика")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка створення профілю: {e}")
        return False

if __name__ == "__main__":
    create_sasha_profile() 