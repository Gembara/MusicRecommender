import sqlite3
import pandas as pd

# Підключення до БД
conn = sqlite3.connect('MusicRecommender.db')

print("🔧 Виправлення даних треків...")

# Виправлення SongFeatures
try:
    # Отримуємо всі треки
    query = "SELECT * FROM SongFeatures"
    songs = pd.read_sql(query, conn)
    
    print(f"Знайдено {len(songs)} треків в SongFeatures")
    
    # Виправляємо Title та Artist
    songs['Title'] = songs['Title'].astype(str).str.replace('\n', '').str.strip()
    songs['Artist'] = songs['Artist'].astype(str).str.replace('\n', '').str.strip()
    songs['Genre'] = songs['Genre'].astype(str).str.replace('\n', '').str.strip()
    
    # Видаляємо порожні або nan
    songs = songs[songs['Title'] != '']
    songs = songs[songs['Artist'] != '']
    songs = songs[songs['Title'] != 'nan']
    songs = songs[songs['Artist'] != 'nan']
    
    # Видаляємо стару таблицю та створюємо нову
    cursor = conn.cursor()
    
    # Зберігаємо виправлені дані
    for _, row in songs.iterrows():
        cursor.execute("""
            UPDATE SongFeatures 
            SET Title = ?, Artist = ?, Genre = ?
            WHERE SpotifyTrackId = ?
        """, (row['Title'], row['Artist'], row['Genre'], row['SpotifyTrackId']))
    
    print("✅ SongFeatures виправлено")
    
except Exception as e:
    print(f"❌ Помилка з SongFeatures: {e}")

# Виправлення History
try:
    query = "SELECT * FROM History"
    history = pd.read_sql(query, conn)
    
    print(f"Знайдено {len(history)} записів в History")
    
    # Виправляємо Title та Artist
    history['Title'] = history['Title'].astype(str).str.replace('\n', '').str.strip()
    history['Artist'] = history['Artist'].astype(str).str.replace('\n', '').str.strip()
    history['Genre'] = history['Genre'].astype(str).str.replace('\n', '').str.strip()
    
    # Зберігаємо виправлені дані
    for _, row in history.iterrows():
        cursor.execute("""
            UPDATE History 
            SET Title = ?, Artist = ?, Genre = ?
            WHERE Id = ?
        """, (row['Title'], row['Artist'], row['Genre'], row['Id']))
    
    print("✅ History виправлено")
    
except Exception as e:
    print(f"❌ Помилка з History: {e}")

# Commit changes
conn.commit()

# Перевірка результату
print("\n🔍 Перевірка виправлених даних:")
sample_songs = pd.read_sql("SELECT SpotifyTrackId, Title, Artist, Genre FROM SongFeatures LIMIT 5", conn)
print("SongFeatures:")
print(sample_songs)

sample_history = pd.read_sql("SELECT UserId, Title, Artist, Genre FROM History LIMIT 5", conn)
print("\nHistory:")
print(sample_history)

conn.close()
print("\n✅ Дані успішно виправлено!") 