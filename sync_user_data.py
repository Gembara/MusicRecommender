#!/usr/bin/env python3
import sqlite3
import pandas as pd
from datetime import datetime

def sync_user_data():
    """Синхронізуємо дані користувачів - додаємо записи в UserSongInteractions з History і Favorites"""
    print("🔄 Синхронізація даних користувачів...")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        cursor = conn.cursor()
        
        # 1. Додаємо з History (рейтинг 3.0, не лайкнуто)
        print("📚 Додаю дані з History...")
        history_data = pd.read_sql_query("""
            SELECT DISTINCT h.UserId, h.SpotifyTrackId, h.ListenedAt
            FROM History h
            WHERE NOT EXISTS (
                SELECT 1 FROM UserSongInteractions usi 
                WHERE usi.UserId = h.UserId AND usi.SpotifyTrackId = h.SpotifyTrackId
            )
        """, conn)
        
        added_from_history = 0
        for _, row in history_data.iterrows():
            cursor.execute("""
                INSERT INTO UserSongInteractions 
                (UserId, SpotifyTrackId, InteractionType, Rating, PlayDuration, IsLiked, IsSkipped, IsRepeat, InteractionTime)
                VALUES (?, ?, 'listen', 3.0, 180, 0, 0, 0, ?)
            """, (row['UserId'], row['SpotifyTrackId'], row['ListenedAt']))
            added_from_history += 1
        
        print(f"   ✅ Додано {added_from_history} записів з History")
        
        # 2. Додаємо з Favorites (рейтинг 5.0, лайкнуто)
        print("❤️ Додаю дані з Favorites...")
        try:
            favorites_data = pd.read_sql_query("""
                SELECT DISTINCT f.UserId, f.SpotifyTrackId
                FROM Favorites f
                WHERE NOT EXISTS (
                    SELECT 1 FROM UserSongInteractions usi 
                    WHERE usi.UserId = f.UserId AND usi.SpotifyTrackId = f.SpotifyTrackId
                )
            """, conn)
            
            added_from_favorites = 0
            for _, row in favorites_data.iterrows():
                # Оновлюємо існуючі записи або додаємо нові
                cursor.execute("""
                    INSERT OR REPLACE INTO UserSongInteractions 
                    (UserId, SpotifyTrackId, InteractionType, Rating, PlayDuration, IsLiked, IsSkipped, IsRepeat, InteractionTime)
                    VALUES (?, ?, 'favorite', 5.0, 300, 1, 0, 0, datetime('now'))
                """, (row['UserId'], row['SpotifyTrackId']))
                added_from_favorites += 1
            
            print(f"   ✅ Додано {added_from_favorites} записів з Favorites")
            
        except Exception as e:
            print(f"   ❌ Помилка з Favorites: {e}")
        
        conn.commit()
        
        # 3. Перевіряємо результат
        print("\n📊 Результат синхронізації:")
        result = pd.read_sql_query("""
            SELECT UserId, COUNT(*) as count 
            FROM UserSongInteractions 
            GROUP BY UserId 
            ORDER BY UserId
        """, conn)
        
        for _, row in result.iterrows():
            print(f"   Користувач {row['UserId']}: {row['count']} взаємодій")
        
        conn.close()
        print("✅ Синхронізація завершена!")
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    sync_user_data() 