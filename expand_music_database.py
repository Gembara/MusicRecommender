#!/usr/bin/env python3
import sqlite3
import pandas as pd
import random

def expand_music_database():
    """Додаємо більше треків схожих артистів у базу даних"""
    print("🎵 Розширення музичної бази даних...")
    
    # Схожі артисти та треки на основі Drake, Kendrick Lamar, Billie Eilish тощо
    new_tracks = [
        # Схожі на Drake (Hip-hop/R&B)
        {
            'SpotifyTrackId': 'track_001', 'Title': 'God\'s Plan', 'Artist': 'Drake', 'Genre': 'Hip-hop',
            'Danceability': 0.754, 'Energy': 0.449, 'Valence': 0.357, 'Tempo': 77.169,
            'Acousticness': 0.123, 'Instrumentalness': 0.000001, 'Speechiness': 0.109, 'Loudness': -9.211,
            'Popularity': 93, 'Key': 7, 'Mode': 1, 'TimeSignature': 4, 'DurationMs': 198973
        },
        {
            'SpotifyTrackId': 'track_002', 'Title': 'HUMBLE.', 'Artist': 'Kendrick Lamar', 'Genre': 'Hip-hop',
            'Danceability': 0.904, 'Energy': 0.621, 'Valence': 0.418, 'Tempo': 150.02,
            'Acousticness': 0.000103, 'Instrumentalness': 0, 'Speechiness': 0.134, 'Loudness': -6.842,
            'Popularity': 91, 'Key': 1, 'Mode': 0, 'TimeSignature': 4, 'DurationMs': 177000
        },
        {
            'SpotifyTrackId': 'track_003', 'Title': 'Sicko Mode', 'Artist': 'Travis Scott', 'Genre': 'Hip-hop',
            'Danceability': 0.834, 'Energy': 0.730, 'Valence': 0.446, 'Tempo': 155.008,
            'Acousticness': 0.000925, 'Instrumentalness': 0.000001, 'Speechiness': 0.222, 'Loudness': -3.714,
            'Popularity': 88, 'Key': 8, 'Mode': 0, 'TimeSignature': 4, 'DurationMs': 312820
        },
        # Схожі на Billie Eilish (Alternative/Pop)
        {
            'SpotifyTrackId': 'track_004', 'Title': 'lovely (with Khalid)', 'Artist': 'Billie Eilish', 'Genre': 'Pop',
            'Danceability': 0.327, 'Energy': 0.295, 'Valence': 0.120, 'Tempo': 115.977,
            'Acousticness': 0.905, 'Instrumentalness': 0.000002, 'Speechiness': 0.0333, 'Loudness': -13.975,
            'Popularity': 87, 'Key': 6, 'Mode': 1, 'TimeSignature': 4, 'DurationMs': 200186
        },
        {
            'SpotifyTrackId': 'track_005', 'Title': 'Sunflower', 'Artist': 'Post Malone', 'Genre': 'Pop',
            'Danceability': 0.764, 'Energy': 0.479, 'Valence': 0.923, 'Tempo': 90.030,
            'Acousticness': 0.136, 'Instrumentalness': 0, 'Speechiness': 0.0556, 'Loudness': -6.051,
            'Popularity': 89, 'Key': 6, 'Mode': 1, 'TimeSignature': 4, 'DurationMs': 158040
        },
        # Нові артисти схожі на вподобання
        {
            'SpotifyTrackId': 'track_006', 'Title': 'Blinding Lights', 'Artist': 'The Weeknd', 'Genre': 'Pop',
            'Danceability': 0.514, 'Energy': 0.730, 'Valence': 0.334, 'Tempo': 171.009,
            'Acousticness': 0.00146, 'Instrumentalness': 0.00000905, 'Speechiness': 0.0598, 'Loudness': -5.934,
            'Popularity': 92, 'Key': 1, 'Mode': 1, 'TimeSignature': 4, 'DurationMs': 200040
        },
        {
            'SpotifyTrackId': 'track_007', 'Title': 'Circles', 'Artist': 'Post Malone', 'Genre': 'Pop',
            'Danceability': 0.695, 'Energy': 0.762, 'Valence': 0.553, 'Tempo': 120.042,
            'Acousticness': 0.0158, 'Instrumentalness': 0.000000519, 'Speechiness': 0.0395, 'Loudness': -3.497,
            'Popularity': 85, 'Key': 0, 'Mode': 1, 'TimeSignature': 4, 'DurationMs': 215280
        },
        {
            'SpotifyTrackId': 'track_008', 'Title': 'Rockstar', 'Artist': '21 Savage', 'Genre': 'Hip-hop',
            'Danceability': 0.676, 'Energy': 0.540, 'Valence': 0.154, 'Tempo': 159.772,
            'Acousticness': 0.00349, 'Instrumentalness': 0, 'Speechiness': 0.409, 'Loudness': -6.090,
            'Popularity': 84, 'Key': 5, 'Mode': 0, 'TimeSignature': 4, 'DurationMs': 218147
        },
        {
            'SpotifyTrackId': 'track_009', 'Title': 'Someone You Loved', 'Artist': 'Lewis Capaldi', 'Genre': 'Pop',
            'Danceability': 0.504, 'Energy': 0.405, 'Valence': 0.446, 'Tempo': 109.891,
            'Acousticness': 0.751, 'Instrumentalness': 0, 'Speechiness': 0.0319, 'Loudness': -7.596,
            'Popularity': 86, 'Key': 1, 'Mode': 1, 'TimeSignature': 4, 'DurationMs': 182160
        },
        {
            'SpotifyTrackId': 'track_010', 'Title': 'Watermelon Sugar', 'Artist': 'Harry Styles', 'Genre': 'Pop',
            'Danceability': 0.548, 'Energy': 0.816, 'Valence': 0.557, 'Tempo': 95.39,
            'Acousticness': 0.122, 'Instrumentalness': 0.00000234, 'Speechiness': 0.0465, 'Loudness': -4.209,
            'Popularity': 87, 'Key': 2, 'Mode': 1, 'TimeSignature': 4, 'DurationMs': 174000
        },
    ]
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        cursor = conn.cursor()
        
        added_count = 0
        for track in new_tracks:
            # Перевіряємо чи трек вже існує
            existing = cursor.execute(
                "SELECT COUNT(*) FROM SongFeatures WHERE SpotifyTrackId = ?", 
                (track['SpotifyTrackId'],)
            ).fetchone()[0]
            
            if existing == 0:
                cursor.execute("""
                    INSERT INTO SongFeatures (
                        SpotifyTrackId, Title, Artist, Genre, Danceability, Energy, Valence, Tempo,
                        Acousticness, Instrumentalness, Speechiness, Loudness, Popularity, 
                        Key, Mode, TimeSignature, DurationMs
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    track['SpotifyTrackId'], track['Title'], track['Artist'], track['Genre'],
                    track['Danceability'], track['Energy'], track['Valence'], track['Tempo'],
                    track['Acousticness'], track['Instrumentalness'], track['Speechiness'], 
                    track['Loudness'], track['Popularity'], track['Key'], track['Mode'], 
                    track['TimeSignature'], track['DurationMs']
                ))
                added_count += 1
                print(f"   ✅ Додано: {track['Title']} - {track['Artist']}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Додано {added_count} нових треків у базу даних!")
        print("Тепер ML зможе рекомендувати нових артистів!")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    expand_music_database() 