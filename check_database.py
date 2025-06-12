import sqlite3
import pandas as pd

# Підключення до БД
conn = sqlite3.connect('MusicRecommender.db')

# Перевірка таблиць
tables = pd.read_sql('SELECT name FROM sqlite_master WHERE type="table"', conn)
print('Таблиці в БД:')
print(tables)

# Перевірка SongFeatures
print('\n=== SongFeatures ===')
try:
    song_features = pd.read_sql('SELECT COUNT(*) as count FROM SongFeatures', conn)
    print(f'Кількість треків в SongFeatures: {song_features.iloc[0]["count"]}')
    
    # Кілька перших записів
    sample = pd.read_sql('SELECT SpotifyTrackId, Title, Artist, Genre FROM SongFeatures LIMIT 5', conn)
    print('Приклади треків:')
    print(sample)
except Exception as e:
    print(f'Помилка з SongFeatures: {e}')

# Перевірка History
print('\n=== History ===')
try:
    history_count = pd.read_sql('SELECT COUNT(*) as count FROM History', conn)
    print(f'Кількість записів в History: {history_count.iloc[0]["count"]}')
    
    sample_history = pd.read_sql('SELECT UserId, SpotifyTrackId, Title, Artist FROM History LIMIT 5', conn)
    print('Приклади історії:')
    print(sample_history)
except Exception as e:
    print(f'Помилка з History: {e}')

# Перевірка Favorites  
print('\n=== Favorites ===')
try:
    favorites_count = pd.read_sql('SELECT COUNT(*) as count FROM Favorites', conn)
    print(f'Кількість записів в Favorites: {favorites_count.iloc[0]["count"]}')
    
    sample_favorites = pd.read_sql('SELECT UserId, SpotifyTrackId FROM Favorites LIMIT 5', conn)
    print('Приклади улюблених:')
    print(sample_favorites)
except Exception as e:
    print(f'Помилка з Favorites: {e}')

conn.close() 