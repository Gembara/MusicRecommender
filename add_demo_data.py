#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Data Generator для Music Recommender ML
Додає тестові дані для демонстрації роботи ML алгоритмів
"""

import sqlite3
import random
import uuid
from datetime import datetime, timedelta
import json

# Підключення до бази даних
def connect_db():
    return sqlite3.connect('MusicRecommender.db')

# Демо дані
DEMO_USERS = [
    {"UserId": 1, "UserName": "Vens", "Email": "vens@example.com", "PreferredGenres": '["Rock", "Electronic"]'},
    {"UserId": 2, "UserName": "Alice", "Email": "alice@example.com", "PreferredGenres": '["Pop", "R&B"]'},
    {"UserId": 3, "UserName": "Bob", "Email": "bob@example.com", "PreferredGenres": '["Jazz", "Classical"]'},
    {"UserId": 4, "UserName": "Carol", "Email": "carol@example.com", "PreferredGenres": '["Hip-Hop", "Alternative"]'},
    {"UserId": 5, "UserName": "Dave", "Email": "dave@example.com", "PreferredGenres": '["Country", "Indie"]'}
]

DEMO_ARTISTS = [
    "The Beatles", "Queen", "Led Zeppelin", "Pink Floyd", "The Rolling Stones",
    "AC/DC", "Nirvana", "Radiohead", "Coldplay", "U2",
    "David Bowie", "The Cure", "Depeche Mode", "Metallica", "Iron Maiden",
    "Red Hot Chili Peppers", "Foo Fighters", "Pearl Jam", "Soundgarden", "Green Day"
]

DEMO_GENRES = [
    "Rock", "Pop", "Electronic", "Jazz", "Classical", 
    "Hip-Hop", "R&B", "Country", "Alternative", "Indie"
]

def generate_spotify_id():
    """Генерує fake Spotify ID"""
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=22))

def generate_track_features():
    """Генерує аудіо характеристики треку"""
    return {
        'Danceability': round(random.uniform(0.0, 1.0), 3),
        'Energy': round(random.uniform(0.0, 1.0), 3),
        'Valence': round(random.uniform(0.0, 1.0), 3),
        'Tempo': round(random.uniform(60.0, 200.0), 1),
        'Acousticness': round(random.uniform(0.0, 1.0), 3),
        'Instrumentalness': round(random.uniform(0.0, 1.0), 3), 
        'Speechiness': round(random.uniform(0.0, 1.0), 3),
        'Loudness': round(random.uniform(-30.0, 0.0), 2),
        'Popularity': random.randint(0, 100),
        'Key': random.randint(0, 11),
        'Mode': random.randint(0, 1),
        'TimeSignature': random.choice([3, 4, 5]),
        'DurationMs': random.randint(120000, 360000)  # 2-6 хвилин
    }

def add_demo_data():
    """Додає демо дані до бази"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("🎵 Додавання демо-даних для Music Recommender ML...")
    
    # 1. Додаємо користувачів
    print("👥 Додавання користувачів...")
    for user in DEMO_USERS:
        # Генеруємо середні значення музичних вподобань
        avg_features = generate_track_features()
        
        cursor.execute("""
            INSERT OR REPLACE INTO Users (
                UserId, UserName, Email, CreatedAt, PreferredGenres,
                AvgDanceability, AvgEnergy, AvgValence, AvgTempo,
                AvgAcousticness, AvgInstrumentalness, AvgSpeechiness, AvgLoudness
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user["UserId"], user["UserName"], user["Email"], datetime.now(),
            user["PreferredGenres"], avg_features['Danceability'], avg_features['Energy'],
            avg_features['Valence'], avg_features['Tempo'], avg_features['Acousticness'],
            avg_features['Instrumentalness'], avg_features['Speechiness'], avg_features['Loudness']
        ))
    
    # 2. Генеруємо треки з характеристиками
    print("🎼 Генерація треків і аудіо-характеристик...")
    tracks = []
    for i in range(50):  # 50 демо треків
        track_id = generate_spotify_id()
        title = f"Demo Track {i+1}"
        artist = random.choice(DEMO_ARTISTS)
        genre = random.choice(DEMO_GENRES)
        features = generate_track_features()
        
        # Додаємо до SongFeatures
        cursor.execute("""
            INSERT OR REPLACE INTO SongFeatures (
                SpotifyTrackId, Artist, Genre, Danceability, Energy, Valence, 
                Tempo, Acousticness, Instrumentalness, Speechiness, Loudness, 
                Popularity, Key, Mode, TimeSignature, DurationMs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            track_id, artist, genre, features['Danceability'], features['Energy'],
            features['Valence'], features['Tempo'], features['Acousticness'],
            features['Instrumentalness'], features['Speechiness'], features['Loudness'],
            features['Popularity'], features['Key'], features['Mode'],
            features['TimeSignature'], features['DurationMs']
        ))
        
        tracks.append({
            'track_id': track_id,
            'title': title,
            'artist': artist,
            'genre': genre,
            'features': features
        })
    
    # 3. Генеруємо взаємодії користувачів
    print("🔄 Генерація взаємодій користувачів...")
    interaction_types = ['play', 'like', 'skip', 'repeat']
    
    for user in DEMO_USERS:
        user_id = user["UserId"]
        
        # Кожен користувач взаємодіє з 20-30 треками
        user_tracks = random.sample(tracks, random.randint(20, 30))
        
        for track in user_tracks:
            interaction_type = random.choice(interaction_types)
            rating = random.randint(1, 5)
            is_liked = rating >= 4
            is_skipped = interaction_type == 'skip'
            is_repeat = interaction_type == 'repeat'
            play_duration = random.randint(30, 240) if not is_skipped else random.randint(5, 30)
            
            cursor.execute("""
                INSERT OR REPLACE INTO UserSongInteractions (
                    UserId, SpotifyTrackId, InteractionType, Rating, PlayDuration,
                    IsLiked, IsSkipped, IsRepeat, InteractionTime
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, track['track_id'], interaction_type, rating, play_duration,
                is_liked, is_skipped, is_repeat, 
                datetime.now() - timedelta(days=random.randint(1, 30))
            ))
    
    # 4. Додаємо історію прослуховування
    print("📈 Додавання історії прослуховування...")
    for user in DEMO_USERS:
        user_id = user["UserId"]
        user_tracks = random.sample(tracks, random.randint(15, 25))
        
        for track in user_tracks:
            cursor.execute("""
                INSERT OR REPLACE INTO History (
                    UserId, SpotifyTrackId, Title, Artist, Genre, Popularity, ListenedAt
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, track['track_id'], track['title'], track['artist'],
                track['genre'], track['features']['Popularity'],
                datetime.now() - timedelta(days=random.randint(1, 60))
            ))
    
    # 5. Додаємо вподобання
    print("❤️ Додавання вподобань...")
    for user in DEMO_USERS:
        user_id = user["UserId"]
        liked_tracks = random.sample(tracks, random.randint(5, 15))
        
        for track in liked_tracks:
            cursor.execute("""
                INSERT OR REPLACE INTO Favorites (
                    UserId, SpotifyTrackId, Title, Artist, AddedAt
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                user_id, track['track_id'], track['title'], track['artist'],
                datetime.now() - timedelta(days=random.randint(1, 30))
            ))
    
    conn.commit()
    conn.close()
    
    print("✅ Демо-дані успішно додано!")
    print(f"👥 Користувачів: {len(DEMO_USERS)}")
    print(f"🎼 Треків: {len(tracks)}")
    print("🤖 Тепер ML алгоритми мають дані для тренування!")

def check_data():
    """Перевіряє кількість даних у базі"""
    conn = connect_db()
    cursor = conn.cursor()
    
    tables = [
        ('Users', 'SELECT COUNT(*) FROM Users'),
        ('SongFeatures', 'SELECT COUNT(*) FROM SongFeatures'), 
        ('UserSongInteractions', 'SELECT COUNT(*) FROM UserSongInteractions'),
        ('History', 'SELECT COUNT(*) FROM History'),
        ('Favorites', 'SELECT COUNT(*) FROM Favorites')
    ]
    
    print("📊 Поточний стан бази даних:")
    for table_name, query in tables:
        try:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count} записів")
        except Exception as e:
            print(f"  {table_name}: Помилка - {e}")
    
    conn.close()

if __name__ == "__main__":
    print("🎵 Music Recommender - Demo Data Generator")
    print("=" * 50)
    
    # Перевіряємо поточний стан
    check_data()
    print()
    
    # Додаємо демо дані
    add_demo_data()
    print()
    
    # Перевіряємо результат
    check_data() 