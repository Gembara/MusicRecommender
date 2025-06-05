import pandas as pd
import numpy as np
import sqlite3
from typing import Tuple, Optional
import logging
import os

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Шлях до бази даних відносно ml_service директорії
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            self.db_path = os.path.join(project_root, "MusicRecommender.db")
        else:
            self.db_path = db_path
            
        logger.info(f"Використовується база даних: {self.db_path}")
        
    def connect_db(self) -> sqlite3.Connection:
        """Підключення до бази даних"""
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"База даних не знайдена: {self.db_path}")
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
                
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            logger.error(f"Помилка підключення до БД: {e}")
            raise
    
    def load_user_interactions(self) -> pd.DataFrame:
        """Завантаження взаємодій користувачів з піснями з усіх джерел"""
        
        # 1. Завантажуємо з UserSongInteractions (якщо є)
        interactions_list = []
        
        try:
            with self.connect_db() as conn:
                # Спробуємо завантажити з UserSongInteractions
                try:
                    query_interactions = """
                    SELECT 
                        UserId,
                        SpotifyTrackId,
                        InteractionType,
                        Rating,
                        PlayDuration,
                        IsLiked,
                        IsSkipped,
                        IsRepeat,
                        InteractionTime
                    FROM UserSongInteractions
                    """
                    df_interactions = pd.read_sql_query(query_interactions, conn)
                    if not df_interactions.empty:
                        interactions_list.append(df_interactions)
                        logger.info(f"Завантажено {len(df_interactions)} з UserSongInteractions")
                except Exception as e:
                    logger.info(f"UserSongInteractions не доступна: {e}")
                
                # 2. Завантажуємо з Favorites
                try:
                    query_favorites = """
                    SELECT 
                        UserId,
                        SpotifyTrackId,
                        'favorite' as InteractionType,
                        5.0 as Rating,
                        NULL as PlayDuration,
                        1 as IsLiked,
                        0 as IsSkipped,
                        0 as IsRepeat,
                        CreatedAt as InteractionTime
                    FROM Favorites
                    """
                    df_favorites = pd.read_sql_query(query_favorites, conn)
                    if not df_favorites.empty:
                        interactions_list.append(df_favorites)
                        logger.info(f"Завантажено {len(df_favorites)} з Favorites")
                except Exception as e:
                    logger.info(f"Favorites не доступна: {e}")
                
                # 3. Завантажуємо з History
                try:
                    query_history = """
                    SELECT 
                        UserId,
                        SpotifyTrackId,
                        'listen' as InteractionType,
                        3.0 as Rating,
                        NULL as PlayDuration,
                        0 as IsLiked,
                        0 as IsSkipped,
                        0 as IsRepeat,
                        ListenedAt as InteractionTime
                    FROM History
                    """
                    df_history = pd.read_sql_query(query_history, conn)
                    if not df_history.empty:
                        interactions_list.append(df_history)
                        logger.info(f"Завантажено {len(df_history)} з History")
                except Exception as e:
                    logger.info(f"History не доступна: {e}")
                
        except Exception as e:
            logger.error(f"Помилка підключення до БД: {e}")
            return pd.DataFrame()
        
        # Об'єднуємо всі джерела даних
        if interactions_list:
            df = pd.concat(interactions_list, ignore_index=True)
            
            # Видаляємо дублікати (той самий користувач + трек)
            df = df.drop_duplicates(subset=['UserId', 'SpotifyTrackId'], keep='first')
            
            logger.info(f"Загалом завантажено {len(df)} унікальних взаємодій користувачів")
            return df
        else:
            logger.warning("Не знайдено жодних взаємодій користувачів")
            return pd.DataFrame()
    
    def load_song_features(self) -> pd.DataFrame:
        """Завантаження аудіо фічей пісень"""
        query = """
        SELECT 
            SpotifyTrackId,
            Title,
            Danceability,
            Energy,
            Valence,
            Tempo,
            Acousticness,
            Instrumentalness,
            Speechiness,
            Loudness,
            Popularity,
            Key,
            Mode,
            TimeSignature,
            DurationMs,
            Genre,
            Artist
        FROM SongFeatures
        """
        
        try:
            with self.connect_db() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Завантажено {len(df)} аудіо фічей")
                return df
        except Exception as e:
            logger.error(f"Помилка завантаження фічей: {e}")
            return pd.DataFrame()
    
    def load_user_history(self, user_id: Optional[int] = None) -> pd.DataFrame:
        """Завантаження історії прослуховування"""
        query = """
        SELECT 
            UserId,
            SpotifyTrackId,
            Title,
            Artist,
            Genre,
            ListenedAt,
            Popularity
        FROM History
        """
        
        if user_id:
            query += f" WHERE UserId = {user_id}"
        
        try:
            with self.connect_db() as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Завантажено {len(df)} записів історії")
                return df
        except Exception as e:
            logger.error(f"Помилка завантаження історії: {e}")
            return pd.DataFrame()
    
    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Підготовка даних для тренування:
        - Об'єднання взаємодій з аудіо фічами
        - Очищення та нормалізація
        """
        interactions = self.load_user_interactions()
        features = self.load_song_features()
        
        if interactions.empty or features.empty:
            logger.warning("Немає даних для тренування")
            return pd.DataFrame(), pd.DataFrame()
        
        # Об'єднуємо взаємодії з фічами
        training_data = interactions.merge(
            features, 
            on='SpotifyTrackId', 
            how='inner'
        )
        
        if training_data.empty:
            logger.warning("Немає спільних треків між взаємодіями та фічами")
            return pd.DataFrame(), pd.DataFrame()
        
        # Вибираємо фічі для ML
        feature_columns = [
            'Danceability', 'Energy', 'Valence', 'Tempo',
            'Acousticness', 'Instrumentalness', 'Speechiness',
            'Loudness', 'Popularity'
        ]
        
        # Очищаємо від NaN
        training_data = training_data.dropna(subset=feature_columns + ['Rating'])
        
        # Нормалізуємо Tempo та Loudness
        if not training_data.empty:
            training_data['Tempo_norm'] = (training_data['Tempo'] - training_data['Tempo'].min()) / (training_data['Tempo'].max() - training_data['Tempo'].min())
            training_data['Loudness_norm'] = (training_data['Loudness'] - training_data['Loudness'].min()) / (training_data['Loudness'].max() - training_data['Loudness'].min())
        
        logger.info(f"Підготовлено {len(training_data)} записів для тренування")
        
        return training_data, features
    
    def get_user_profile(self, user_id: int) -> dict:
        """Створення профілю користувача на основі його історії"""
        interactions = self.load_user_interactions()
        features = self.load_song_features()
        
        if interactions.empty or features.empty:
            return {}
        
        user_interactions = interactions[interactions['UserId'] == user_id]
        if user_interactions.empty:
            return {}
        
        # Об'єднуємо з фічами
        user_data = user_interactions.merge(features, on='SpotifyTrackId', how='inner')
        
        if user_data.empty:
            return {}
        
        # Обчислюємо середні значення фічей для улюблених треків
        liked_tracks = user_data[user_data['IsLiked'] == True]
        
        if liked_tracks.empty:
            # Якщо немає лайків, беремо треки з високим рейтингом
            liked_tracks = user_data[user_data['Rating'] >= 4]
        
        if liked_tracks.empty:
            return {}
        
        profile = {
            'avg_danceability': liked_tracks['Danceability'].mean(),
            'avg_energy': liked_tracks['Energy'].mean(),
            'avg_valence': liked_tracks['Valence'].mean(),
            'avg_tempo': liked_tracks['Tempo'].mean(),
            'avg_acousticness': liked_tracks['Acousticness'].mean(),
            'preferred_genres': liked_tracks['Genre'].value_counts().to_dict(),
            'total_interactions': len(user_interactions),
            'liked_count': len(liked_tracks)
        }
        
        logger.info(f"Створено профіль для користувача {user_id}")
        return profile 