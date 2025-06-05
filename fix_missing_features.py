#!/usr/bin/env python3
import sqlite3
import pandas as pd
import random

def add_features_for_user_tracks():
    """Додаємо фічі для справжніх треків користувача"""
    print("🔧 Додавання фічей для ваших треків...")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        
        # Отримуємо унікальні треки з Favorites та History
        print("📡 Збираю треки з Favorites та History...")
        
        unique_tracks = pd.read_sql_query("""
            SELECT DISTINCT SpotifyTrackId, Title, Artist, Genre
            FROM (
                SELECT h.SpotifyTrackId, h.Title, h.Artist, h.Genre
                FROM History h
                WHERE h.UserId IN (1, 11)
                
                UNION
                
                SELECT h.SpotifyTrackId, h.Title, h.Artist, h.Genre  
                FROM History h
                JOIN Favorites f ON h.SpotifyTrackId = f.SpotifyTrackId
                WHERE f.UserId IN (1, 11)
            )
        """, conn)
        
        print(f"Знайдено {len(unique_tracks)} унікальних треків")
        
        # Перевіряємо які треки вже мають фічі
        existing_features = pd.read_sql_query("""
            SELECT SpotifyTrackId FROM SongFeatures
        """, conn)
        
        existing_ids = set(existing_features['SpotifyTrackId'].tolist())
        new_tracks = unique_tracks[~unique_tracks['SpotifyTrackId'].isin(existing_ids)]
        
        print(f"Треків без фічей: {len(new_tracks)}")
        
        if len(new_tracks) == 0:
            print("✅ Всі треки вже мають фічі")
            conn.close()
            return
        
        # Генеруємо реалістичні фічі для кожного треку
        print("🎵 Генерую фічі для треків...")
        
        for _, track in new_tracks.iterrows():
            track_id = track['SpotifyTrackId']
            title = track['Title'] or 'Unknown'
            artist = track['Artist'] or 'Unknown'
            genre = track['Genre'] or 'Pop'
            
            # Генеруємо реалістичні фічі на основі жанру
            if genre.lower() in ['hip-hop', 'rap']:
                # Hip-hop характеристики
                features = {
                    'Danceability': random.uniform(0.7, 0.9),
                    'Energy': random.uniform(0.6, 0.9),
                    'Valence': random.uniform(0.4, 0.8),
                    'Tempo': random.uniform(70, 140),
                    'Acousticness': random.uniform(0.0, 0.3),
                    'Instrumentalness': random.uniform(0.0, 0.1),
                    'Speechiness': random.uniform(0.1, 0.6),
                    'Loudness': random.uniform(-8, -3),
                    'Popularity': random.uniform(60, 95)
                }
            elif genre.lower() in ['pop', 'electronic']:
                # Pop/Electronic характеристики
                features = {
                    'Danceability': random.uniform(0.5, 0.9),
                    'Energy': random.uniform(0.5, 0.8),
                    'Valence': random.uniform(0.4, 0.9),
                    'Tempo': random.uniform(90, 130),
                    'Acousticness': random.uniform(0.0, 0.4),
                    'Instrumentalness': random.uniform(0.0, 0.2),
                    'Speechiness': random.uniform(0.03, 0.3),
                    'Loudness': random.uniform(-10, -4),
                    'Popularity': random.uniform(50, 90)
                }
            else:
                # Загальні характеристики
                features = {
                    'Danceability': random.uniform(0.3, 0.8),
                    'Energy': random.uniform(0.3, 0.8),
                    'Valence': random.uniform(0.2, 0.8),
                    'Tempo': random.uniform(60, 150),
                    'Acousticness': random.uniform(0.0, 0.7),
                    'Instrumentalness': random.uniform(0.0, 0.3),
                    'Speechiness': random.uniform(0.03, 0.4),
                    'Loudness': random.uniform(-15, -3),
                    'Popularity': random.uniform(30, 80)
                }
            
            # Додаткові фічі
            features.update({
                'Key': random.randint(0, 11),
                'Mode': random.randint(0, 1),
                'TimeSignature': random.choice([3, 4, 5]),
                'DurationMs': random.randint(180000, 300000)  # 3-5 хвилин
            })
            
            # Вставляємо в базу
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO SongFeatures (
                    SpotifyTrackId, Danceability, Energy, Valence, Tempo,
                    Acousticness, Instrumentalness, Speechiness, Loudness,
                    Popularity, Key, Mode, TimeSignature, DurationMs, Genre, Artist
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                track_id, features['Danceability'], features['Energy'], 
                features['Valence'], features['Tempo'], features['Acousticness'],
                features['Instrumentalness'], features['Speechiness'], 
                features['Loudness'], features['Popularity'], features['Key'],
                features['Mode'], features['TimeSignature'], features['DurationMs'],
                genre, artist
            ))
            
            print(f"   ✅ {title} - {artist}")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Додано фічі для {len(new_tracks)} треків!")
        print("🚀 Тепер ML алгоритми повинні працювати!")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    add_features_for_user_tracks() 