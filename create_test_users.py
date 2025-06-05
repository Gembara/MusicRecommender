#!/usr/bin/env python3
import sqlite3
import pandas as pd
import random
from datetime import datetime

def create_test_users():
    """Створюємо тестових користувачів з різними музичними смаками"""
    print("👥 Створення тестових користувачів...")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        cursor = conn.cursor()
        
        # Отримуємо доступні треки
        available_tracks = pd.read_sql_query("""
            SELECT SpotifyTrackId, Title, Artist, Genre 
            FROM SongFeatures 
            ORDER BY Popularity DESC
        """, conn)
        
        print(f"Доступно {len(available_tracks)} треків")
        
        # Створюємо різних користувачів з різними смаками
        test_users = [
            {"id": 20, "name": "HipHopFan", "preferences": ["Hip-hop"], "track_range": range(5)},
            {"id": 21, "name": "PopLover", "preferences": ["Pop"], "track_range": range(3, 8)},
            {"id": 22, "name": "MixedTaste", "preferences": ["Hip-hop", "Pop"], "track_range": range(1, 10)},
            {"id": 23, "name": "DrakeStan", "preferences": ["Hip-hop"], "track_range": range(7)},
            {"id": 24, "name": "PopStar", "preferences": ["Pop"], "track_range": range(4, 12)},
        ]
        
        added_interactions = 0
        
        for user in test_users:
            user_id = user["id"]
            user_name = user["name"]
            preferences = user["preferences"]
            
            print(f"\n🎵 Створюю користувача {user_name} (ID: {user_id})")
            
            # Фільтруємо треки за жанрами
            if preferences:
                user_tracks = available_tracks[available_tracks['Genre'].isin(preferences)]
            else:
                user_tracks = available_tracks
            
            # Вибираємо випадкові треки для цього користувача
            selected_tracks = user_tracks.iloc[list(user["track_range"])[:min(len(user_tracks), 8)]]
            
            for _, track in selected_tracks.iterrows():
                # Випадковий рейтинг залежно від жанру
                if track['Genre'] in preferences:
                    rating = random.uniform(4.0, 5.0)  # Високий рейтинг для улюблених жанрів
                else:
                    rating = random.uniform(2.5, 4.5)  # Нижчий для інших
                
                # Додаємо взаємодію
                cursor.execute("""
                    INSERT OR REPLACE INTO UserSongInteractions 
                    (UserId, SpotifyTrackId, InteractionType, Rating, PlayDuration, IsLiked, IsSkipped, IsRepeat, InteractionTime)
                    VALUES (?, ?, 'listen', ?, ?, ?, 0, 0, datetime('now'))
                """, (
                    user_id, 
                    track['SpotifyTrackId'], 
                    rating,
                    random.randint(120, 300),  # Тривалість прослуховування
                    1 if rating > 4.0 else 0   # Лайк якщо високий рейтинг
                ))
                
                added_interactions += 1
                print(f"   ✅ {track['Title']} - {track['Artist']} (рейтинг: {rating:.1f})")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Створено {len(test_users)} користувачів з {added_interactions} взаємодіями!")
        print("Тепер Collaborative Filtering буде працювати краще!")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    create_test_users() 