#!/usr/bin/env python3
import sqlite3

def fix_spotify_ids():
    """Замінюємо фейкові track ID на справжні Spotify ID"""
    print("🔧 Виправлення Spotify ID...")
    
    # Мапінг фейкових ID на справжні Spotify ID
    spotify_mapping = {
        'track_001': '6DCZcSspjsKoFjzjrWoCdn',  # God's Plan - Drake
        'track_002': '7KXjTSCq5nL1LoYtL7XAwS',  # HUMBLE. - Kendrick Lamar
        'track_003': '2xLMifQCjDGFmkHkpNLD9h',  # Sicko Mode - Travis Scott
        'track_004': '0u2P5u6lvoDfwTYjAADbn4',  # lovely (with Khalid) - Billie Eilish
        'track_005': '3KkXRkHbMCARz0aVfEt68P',  # Sunflower - Post Malone, Swae Lee
        'track_006': '0sf0KYcqVmpUCOG2DIMHtH',  # Blinding Lights - The Weeknd
        'track_007': '21jGcNKet2qwijlDFuPiPb',  # Circles - Post Malone
        'track_008': '7wGoVu4Dady5GV0Sv4UIsx',  # Rockstar - Post Malone ft. 21 Savage
        'track_009': '7qEHsqek33rTcFNT9PFqLf',  # Someone You Loved - Lewis Capaldi
        'track_010': '6UelLqGlWMcVH1E5c4H7lY',  # Watermelon Sugar - Harry Styles
    }
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        cursor = conn.cursor()
        
        updated_count = 0
        
        for fake_id, real_id in spotify_mapping.items():
            # Оновлюємо SongFeatures
            cursor.execute("""
                UPDATE SongFeatures 
                SET SpotifyTrackId = ? 
                WHERE SpotifyTrackId = ?
            """, (real_id, fake_id))
            
            if cursor.rowcount > 0:
                print(f"   ✅ Оновлено {fake_id} → {real_id}")
                updated_count += cursor.rowcount
            
            # Оновлюємо UserSongInteractions
            cursor.execute("""
                UPDATE UserSongInteractions 
                SET SpotifyTrackId = ? 
                WHERE SpotifyTrackId = ?
            """, (real_id, fake_id))
            
            # Оновлюємо History якщо є
            cursor.execute("""
                UPDATE History 
                SET SpotifyTrackId = ? 
                WHERE SpotifyTrackId = ?
            """, (real_id, fake_id))
            
            # Оновлюємо Favorites якщо є
            cursor.execute("""
                UPDATE Favorites 
                SET SpotifyTrackId = ? 
                WHERE SpotifyTrackId = ?
            """, (real_id, fake_id))
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Оновлено {updated_count} треків зі справжніми Spotify ID!")
        print("Тепер плеєр буде працювати!")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    fix_spotify_ids() 