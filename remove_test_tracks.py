#!/usr/bin/env python3
import sqlite3

def remove_test_tracks():
    """Видаляємо тестові треки з TestArtist з бази даних"""
    print("🗑️ Видалення тестових треків...")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        cursor = conn.cursor()
        
        # Видаляємо з SongFeatures
        cursor.execute("DELETE FROM SongFeatures WHERE Artist = 'TestArtist'")
        deleted_features = cursor.rowcount
        print(f"   ✅ Видалено {deleted_features} тестових треків з SongFeatures")
        
        # Видаляємо з UserSongInteractions
        cursor.execute("""
            DELETE FROM UserSongInteractions 
            WHERE SpotifyTrackId IN (
                SELECT SpotifyTrackId FROM SongFeatures WHERE Artist = 'TestArtist'
            )
        """)
        deleted_interactions = cursor.rowcount
        print(f"   ✅ Видалено {deleted_interactions} тестових взаємодій з UserSongInteractions")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Очищення завершено!")
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    remove_test_tracks() 