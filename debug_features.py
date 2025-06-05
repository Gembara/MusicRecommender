#!/usr/bin/env python3
import sqlite3
import pandas as pd

def debug_song_features():
    """Перевіряємо чи є фічі для улюблених треків"""
    print("🔍 Перевірка фічей пісень для ML:")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        
        # Улюблені треки користувача 11
        print("\n❤️ Улюблені треки користувача 11:")
        favorites = pd.read_sql_query("""
            SELECT f.SpotifyTrackId
            FROM Favorites f 
            WHERE f.UserId = 11
        """, conn)
        
        print(f"Знайдено {len(favorites)} улюблених треків")
        for _, fav in favorites.head(5).iterrows():
            track_id = fav['SpotifyTrackId']
            print(f"   Track ID: {track_id}")
        
        # Історія користувача 11  
        print("\n📚 Історія користувача 11:")
        history = pd.read_sql_query("""
            SELECT h.SpotifyTrackId, h.Title, h.Artist
            FROM History h 
            WHERE h.UserId = 11
        """, conn)
        
        print(f"Знайдено {len(history)} записів в історії")
        for _, hist in history.head(5).iterrows():
            print(f"   {hist['Title']} - {hist['Artist']} (ID: {hist['SpotifyTrackId']})")
        
        # Всі фічі в базі
        print("\n🎵 Фічі пісень в SongFeatures:")
        features = pd.read_sql_query("SELECT SpotifyTrackId, Artist FROM SongFeatures", conn)
        print(f"Знайдено {len(features)} фічей")
        for _, feat in features.head(5).iterrows():
            print(f"   {feat['Artist']} (ID: {feat['SpotifyTrackId']})")
        
        # Перевіряємо перетин
        print("\n🔗 Перетин улюблених треків з фічами:")
        fav_ids = set(favorites['SpotifyTrackId'].tolist())
        feat_ids = set(features['SpotifyTrackId'].tolist())
        
        intersection = fav_ids.intersection(feat_ids)
        print(f"Спільних треків: {len(intersection)} з {len(fav_ids)} улюблених")
        
        if intersection:
            print("Спільні треки:")
            for track_id in list(intersection)[:3]:
                print(f"   Track ID: {track_id}")
        else:
            print("❌ НЕМАЄ СПІЛЬНИХ ТРЕКІВ! Це причина 0 рекомендацій")
            
        # Перевіряємо історію з фічами
        print("\n🔗 Перетин історії з фічами:")
        hist_ids = set(history['SpotifyTrackId'].tolist())
        hist_intersection = hist_ids.intersection(feat_ids)
        print(f"Спільних треків з історії: {len(hist_intersection)} з {len(hist_ids)}")
        
        conn.close()
        
        if len(intersection) == 0 and len(hist_intersection) == 0:
            print("\n💡 РІШЕННЯ:")
            print("Потрібно додати фічі для ваших улюблених/прослуханих треків")
            print("Або додати треки з існуючих фічей до улюблених")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    debug_song_features() 