#!/usr/bin/env python3
import sqlite3
import pandas as pd

def check_recommendations():
    """Перевіряємо рекомендації в базі даних"""
    print("🔍 Перевірка рекомендацій:")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        
        # Перевіряємо SongFeatures - що повертає ML
        print("\n🎵 Треки в SongFeatures:")
        features = pd.read_sql_query("""
            SELECT SpotifyTrackId, Artist, Genre, Popularity 
            FROM SongFeatures 
            ORDER BY Artist
        """, conn)
        
        print(f"Знайдено {len(features)} треків:")
        for _, track in features.iterrows():
            artist = track['Artist'] or 'Unknown'
            genre = track['Genre'] or 'Unknown'
            pop = track['Popularity'] or 0
            print(f"   {artist} - {genre} (Pop: {pop:.0f}) [ID: {track['SpotifyTrackId']}]")
        
        # Перевіряємо які треки є в History з реальними назвами
        print("\n📚 Треки в History (справжні назви):")
        history = pd.read_sql_query("""
            SELECT DISTINCT h.SpotifyTrackId, h.Title, h.Artist, h.Genre
            FROM History h
            WHERE h.Title IS NOT NULL AND h.Title != ''
            ORDER BY h.Artist
            LIMIT 10
        """, conn)
        
        print(f"Знайдено {len(history)} треків з реальними назвами:")
        for _, track in history.iterrows():
            title = track['Title'] or 'Unknown'
            artist = track['Artist'] or 'Unknown'
            genre = track['Genre'] or 'Unknown'
            print(f"   {title} - {artist} ({genre}) [ID: {track['SpotifyTrackId']}]")
        
        # Перевіряємо перетин
        print("\n🔗 Перевіряємо перетин між SongFeatures і History:")
        feature_ids = set(features['SpotifyTrackId'].tolist())
        history_ids = set(history['SpotifyTrackId'].tolist())
        
        intersection = feature_ids.intersection(history_ids)
        print(f"Спільних треків: {len(intersection)}")
        
        if intersection:
            print("Спільні треки:")
            for track_id in list(intersection)[:5]:
                # Знаходимо справжню назву
                hist_track = history[history['SpotifyTrackId'] == track_id].iloc[0]
                feat_track = features[features['SpotifyTrackId'] == track_id].iloc[0]
                
                print(f"   {hist_track['Title']} - {hist_track['Artist']} (Features: {feat_track['Artist']})")
        
        conn.close()
        
        return len(intersection) > 0
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    check_recommendations() 