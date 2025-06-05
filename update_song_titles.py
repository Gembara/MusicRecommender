#!/usr/bin/env python3
import sqlite3
import pandas as pd

def update_song_titles():
    """Оновлюємо назви треків в SongFeatures з реальними назвами з History"""
    print("🔧 Оновлення назв треків...")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        cursor = conn.cursor()
        
        # Отримуємо справжні назви з History
        print("📚 Отримую справжні назви з History...")
        history_tracks = pd.read_sql_query("""
            SELECT DISTINCT SpotifyTrackId, Title, Artist, Genre
            FROM History
            WHERE Title IS NOT NULL AND Title != '' AND Title != 'Unknown'
        """, conn)
        
        print(f"Знайдено {len(history_tracks)} треків з реальними назвами")
        
        # Оновлюємо SongFeatures
        updated_count = 0
        for _, track in history_tracks.iterrows():
            track_id = track['SpotifyTrackId']
            title = track['Title']
            artist = track['Artist']
            
            # Перевіряємо чи є цей трек в SongFeatures
            cursor.execute("SELECT COUNT(*) FROM SongFeatures WHERE SpotifyTrackId = ?", (track_id,))
            if cursor.fetchone()[0] > 0:
                # Оновлюємо назву (додаємо колонку Title якщо її немає)
                try:
                    cursor.execute("""
                        UPDATE SongFeatures 
                        SET Artist = ?, Title = ? 
                        WHERE SpotifyTrackId = ?
                    """, (artist, title, track_id))
                    updated_count += 1
                    print(f"   ✅ {title} - {artist}")
                except sqlite3.OperationalError:
                    # Якщо колонки Title немає, додаємо її
                    try:
                        cursor.execute("ALTER TABLE SongFeatures ADD COLUMN Title TEXT")
                        cursor.execute("""
                            UPDATE SongFeatures 
                            SET Artist = ?, Title = ? 
                            WHERE SpotifyTrackId = ?
                        """, (artist, title, track_id))
                        updated_count += 1
                        print(f"   ✅ {title} - {artist} (додана колонка Title)")
                    except Exception as e:
                        print(f"   ❌ Помилка для {title}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Оновлено {updated_count} треків!")
        return updated_count > 0
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    update_song_titles() 