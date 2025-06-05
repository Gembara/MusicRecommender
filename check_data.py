#!/usr/bin/env python3
import sqlite3
import pandas as pd

def check_data():
    """Перевіряємо дані в базі після очищення"""
    print("🔍 Перевірка даних після очищення:")
    
    try:
        conn = sqlite3.connect('MusicRecommender.db')
        
        # 1. UserSongInteractions
        print("\n📊 UserSongInteractions:")
        interactions = pd.read_sql_query("""
            SELECT UserId, COUNT(*) as count 
            FROM UserSongInteractions 
            GROUP BY UserId 
            ORDER BY count DESC
        """, conn)
        
        if not interactions.empty:
            print(f"Знайдено {len(interactions)} користувачів з взаємодіями:")
            for _, row in interactions.iterrows():
                print(f"   Користувач {row['UserId']}: {row['count']} взаємодій")
        else:
            print("❌ Немає даних в UserSongInteractions")
        
        # 2. History
        print("\n📚 History:")
        history = pd.read_sql_query("""
            SELECT UserId, COUNT(*) as count 
            FROM History 
            GROUP BY UserId 
            ORDER BY count DESC
        """, conn)
        
        if not history.empty:
            print(f"Знайдено {len(history)} користувачів в History:")
            for _, row in history.iterrows():
                print(f"   Користувач {row['UserId']}: {row['count']} записів")
        
        # 3. Favorites
        print("\n❤️ Favorites:")
        try:
            favorites = pd.read_sql_query("""
                SELECT UserId, COUNT(*) as count 
                FROM Favorites 
                GROUP BY UserId 
                ORDER BY count DESC
            """, conn)
            
            if not favorites.empty:
                print(f"Знайдено {len(favorites)} користувачів в Favorites:")
                for _, row in favorites.iterrows():
                    print(f"   Користувач {row['UserId']}: {row['count']} улюблених")
            else:
                print("❌ Немає даних в Favorites")
        except Exception as e:
            print(f"❌ Помилка читання Favorites: {e}")
        
        # 4. Чи є спільні треки між History/Favorites та SongFeatures?
        print("\n🔗 Перевірка спільних треків:")
        
        # Треки з History які є в SongFeatures
        common_history = pd.read_sql_query("""
            SELECT h.SpotifyTrackId, h.Title, h.Artist, COUNT(*) as usage_count
            FROM History h
            INNER JOIN SongFeatures sf ON h.SpotifyTrackId = sf.SpotifyTrackId
            GROUP BY h.SpotifyTrackId, h.Title, h.Artist
            ORDER BY usage_count DESC
        """, conn)
        
        if not common_history.empty:
            print(f"Спільних треків між History і SongFeatures: {len(common_history)}")
            for _, row in common_history.head(5).iterrows():
                print(f"   {row['Title']} - {row['Artist']} (використовується {row['usage_count']} разів)")
        else:
            print("❌ Немає спільних треків між History і SongFeatures")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    check_data() 