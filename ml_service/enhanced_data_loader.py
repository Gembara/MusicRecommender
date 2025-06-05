import sqlite3
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class EnhancedDataLoader:
    """
    Покращений завантажувач даних для ML тренування
    Працює з новою структурою БД MLTrainingData
    """
    
    def __init__(self, db_path: str = "../MusicRecommender.db"):
        self.db_path = db_path
        self.connection = None
        
    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Отримання з'єднання з БД"""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
        return self.connection
    
    def load_ml_training_data(self, 
                            min_interactions_per_user: int = 5,
                            include_skips: bool = False,
                            time_window_days: Optional[int] = None) -> pd.DataFrame:
        """
        Завантаження тренувальних даних з нової таблиці MLTrainingData
        
        Args:
            min_interactions_per_user: Мінімум взаємодій на користувача
            include_skips: Включити скіпи (rating < 0.3)
            time_window_days: Тільки дані за останні N днів
        """
        logger.info("📊 Завантаження ML тренувальних даних...")
        
        conn = self.get_connection()
        
        # Базовий запит
        base_query = """
        SELECT 
            UserId, SpotifyTrackId, 
            Danceability, Energy, Valence, Tempo, Acousticness, 
            Instrumentalness, Speechiness, Loudness, Popularity,
            DurationMs, [Key], Mode, TimeSignature,
            Artist, Genre, ReleaseYear, ArtistPopularity,
            Rating, InteractionType, PlayCount, PlayDuration,
            ListeningContext, Timestamp,
            UserAvgDanceability, UserAvgEnergy, UserAvgValence, UserAvgTempo
        FROM MLTrainingData
        WHERE 1=1
        """
        
        conditions = []
        params = []
        
        # Фільтр за рейтингом
        if not include_skips:
            conditions.append("Rating >= ?")
            params.append(0.3)
        
        # Фільтр за часом
        if time_window_days:
            cutoff_date = (datetime.now() - timedelta(days=time_window_days)).isoformat()
            conditions.append("Timestamp >= ?")
            params.append(cutoff_date)
        
        # Збираємо запит
        if conditions:
            query = base_query + " AND " + " AND ".join(conditions)
        else:
            query = base_query
            
        query += " ORDER BY Timestamp DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        
        if df.empty:
            logger.warning("⚠️ Не знайдено тренувальних даних!")
            return df
        
        logger.info(f"📈 Завантажено {len(df)} записів тренувальних даних")
        
        # Фільтрація користувачів з мінімальною кількістю взаємодій
        user_counts = df['UserId'].value_counts()
        valid_users = user_counts[user_counts >= min_interactions_per_user].index
        df_filtered = df[df['UserId'].isin(valid_users)]
        
        logger.info(f"👥 Користувачів після фільтрації: {df_filtered['UserId'].nunique()}")
        logger.info(f"🎵 Унікальних треків: {df_filtered['SpotifyTrackId'].nunique()}")
        
        return df_filtered
    
    def load_user_profiles(self) -> pd.DataFrame:
        """Завантаження ML профілів користувачів"""
        logger.info("👤 Завантаження ML профілів користувачів...")
        
        conn = self.get_connection()
        
        query = """
        SELECT 
            UserId, PreferredDanceability, PreferredEnergy, PreferredValence, PreferredTempo,
            PreferredAcousticness, PreferredInstrumentalness, PreferredSpeechiness, PreferredLoudness,
            DanceabilityVariance, EnergyVariance, ValenceVariance, TempoVariance,
            SkipRate, RepeatRate, ExplorationRate,
            GenreDiversity, ArtistDiversity, ClusterId,
            TotalInteractions, LastUpdated
        FROM MLUserProfiles
        """
        
        df = pd.read_sql_query(query, conn)
        logger.info(f"👥 Завантажено {len(df)} профілів користувачів")
        
        return df
    
    def prepare_content_based_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Підготовка даних для content-based моделі
        
        Returns:
            X: Фічі треків + контекст
            y: Цільова змінна (рейтинг)
        """
        logger.info("🎯 Підготовка даних для content-based моделі...")
        
        # Аудіо фічі треку
        audio_features = [
            'Danceability', 'Energy', 'Valence', 'Tempo', 'Acousticness',
            'Instrumentalness', 'Speechiness', 'Loudness', 'Popularity'
        ]
        
        # Користувацькі фічі
        user_features = [
            'UserAvgDanceability', 'UserAvgEnergy', 'UserAvgValence', 'UserAvgTempo'
        ]
        
        # Контекстні фічі
        context_features = self._extract_context_features(df)
        
        # Об'єднуємо всі фічі
        X = df[audio_features + user_features].copy()
        
        # Додаємо контекстні фічі
        for col, values in context_features.items():
            X[col] = values
            
        # Нормалізація Tempo та Loudness
        X['Tempo_norm'] = (X['Tempo'] - X['Tempo'].min()) / (X['Tempo'].max() - X['Tempo'].min())
        X['Loudness_norm'] = (X['Loudness'] - X['Loudness'].min()) / (X['Loudness'].max() - X['Loudness'].min())
        
        # Заповнюємо NaN
        X = X.fillna(0)
        
        # Цільова змінна
        y = df['Rating']
        
        logger.info(f"📊 Підготовлено {X.shape[0]} зразків з {X.shape[1]} фічами")
        
        return X, y
    
    def prepare_collaborative_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Підготовка даних для collaborative filtering
        
        Returns:
            user_item_matrix: Матриця user-item з рейтингами
        """
        logger.info("👥 Підготовка даних для collaborative filtering...")
        
        # Створюємо матрицю user-item
        user_item_matrix = df.pivot_table(
            index='UserId',
            columns='SpotifyTrackId', 
            values='Rating',
            fill_value=0
        )
        
        logger.info(f"📊 Матриця {user_item_matrix.shape[0]} користувачів x {user_item_matrix.shape[1]} треків")
        
        # Розрахунок розрідженості
        sparsity = 1 - (df.shape[0] / (user_item_matrix.shape[0] * user_item_matrix.shape[1]))
        logger.info(f"🔍 Розрідженість матриці: {sparsity:.3f}")
        
        return user_item_matrix
    
    def _extract_context_features(self, df: pd.DataFrame) -> Dict[str, List]:
        """Витягування контекстних фічей"""
        context_features = {}
        
        # Час доби (one-hot encoding)
        time_contexts = ['morning', 'afternoon', 'evening', 'night']
        for context in time_contexts:
            context_features[f'context_{context}'] = (df['ListeningContext'] == context).astype(int)
        
        # Рік випуску (нормалізований)
        if 'ReleaseYear' in df.columns:
            min_year = df['ReleaseYear'].min()
            max_year = df['ReleaseYear'].max()
            if max_year > min_year:
                context_features['release_year_norm'] = (df['ReleaseYear'] - min_year) / (max_year - min_year)
            else:
                context_features['release_year_norm'] = [0.5] * len(df)
        
        # Тип взаємодії (one-hot)
        interaction_types = [1, 2, 3, 4]  # Like, Skip, Play, Save
        for int_type in interaction_types:
            context_features[f'interaction_type_{int_type}'] = (df['InteractionType'] == int_type).astype(int)
        
        return context_features
    
    def get_user_interaction_history(self, user_id: int, limit: int = 100) -> pd.DataFrame:
        """Отримання історії взаємодій користувача"""
        conn = self.get_connection()
        
        query = """
        SELECT * FROM MLTrainingData 
        WHERE UserId = ? 
        ORDER BY Timestamp DESC 
        LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=[user_id, limit])
        return df
    
    def get_track_features_for_prediction(self, track_ids: List[str]) -> pd.DataFrame:
        """Отримання фічей треків для предикції"""
        if not track_ids:
            return pd.DataFrame()
            
        conn = self.get_connection()
        
        # Створюємо плейсхолдери для SQL запиту
        placeholders = ','.join(['?' for _ in track_ids])
        
        query = f"""
        SELECT DISTINCT
            sf.SpotifyTrackId,
            sf.Danceability, sf.Energy, sf.Valence, sf.Tempo, sf.Acousticness,
            sf.Instrumentalness, sf.Speechiness, sf.Loudness, sf.Popularity,
            sf.DurationMs, sf.[Key], sf.Mode, sf.TimeSignature,
            h.Artist, sf.Genre, h.ReleaseYear, sf.ArtistPopularity
        FROM SongFeatures sf
        LEFT JOIN History h ON sf.SpotifyTrackId = h.SpotifyTrackId
        WHERE sf.SpotifyTrackId IN ({placeholders})
        """
        
        df = pd.read_sql_query(query, conn, params=track_ids)
        
        # Нормалізація
        if not df.empty:
            df['Tempo_norm'] = (df['Tempo'] - df['Tempo'].min()) / (df['Tempo'].max() - df['Tempo'].min())
            df['Loudness_norm'] = (df['Loudness'] - df['Loudness'].min()) / (df['Loudness'].max() - df['Loudness'].min())
            df = df.fillna(0)
        
        return df
    
    def save_model_metrics(self, model_type: str, model_version: str, metrics: Dict) -> None:
        """Збереження метрик моделі в БД"""
        conn = self.get_connection()
        
        insert_query = """
        INSERT INTO MLModelMetrics (
            ModelType, ModelVersion, Accuracy, Precision, Recall, F1Score, MAE, MSE,
            TrainingSamples, TestSamples, UniqueUsers, UniqueTracks,
            TrainingDate, TrainingDuration, ModelConfig, FeatureImportance
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        training_duration_seconds = metrics.get('training_duration', 0)
        training_duration_str = f"{training_duration_seconds:.2f} seconds"
        
        params = [
            model_type,
            model_version,
            metrics.get('accuracy', 0.0),
            metrics.get('precision', 0.0),
            metrics.get('recall', 0.0),
            metrics.get('f1_score', 0.0),
            metrics.get('mae', 0.0),
            metrics.get('mse', 0.0),
            metrics.get('training_samples', 0),
            metrics.get('test_samples', 0),
            metrics.get('unique_users', 0),
            metrics.get('unique_tracks', 0),
            datetime.now().isoformat(),
            training_duration_str,
            json.dumps(metrics.get('config', {})),
            json.dumps(metrics.get('feature_importance', {}))
        ]
        
        conn.execute(insert_query, params)
        conn.commit()
        
        logger.info(f"✅ Збережено метрики для моделі {model_type} v{model_version}")
    
    def get_latest_model_metrics(self, model_type: str) -> Optional[Dict]:
        """Отримання останніх метрик моделі"""
        conn = self.get_connection()
        
        query = """
        SELECT * FROM MLModelMetrics 
        WHERE ModelType = ? 
        ORDER BY TrainingDate DESC 
        LIMIT 1
        """
        
        cursor = conn.execute(query, [model_type])
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        
        return None
    
    def cleanup_old_metrics(self, keep_last_n: int = 10) -> int:
        """Очищення старих метрик (залишаємо тільки останні N для кожного типу моделі)"""
        conn = self.get_connection()
        
        # Отримуємо ID записів для видалення
        query = """
        WITH RankedMetrics AS (
            SELECT Id, ModelType,
                   ROW_NUMBER() OVER (PARTITION BY ModelType ORDER BY TrainingDate DESC) as rn
            FROM MLModelMetrics
        )
        SELECT Id FROM RankedMetrics WHERE rn > ?
        """
        
        cursor = conn.execute(query, [keep_last_n])
        ids_to_delete = [row[0] for row in cursor.fetchall()]
        
        if ids_to_delete:
            placeholders = ','.join(['?' for _ in ids_to_delete])
            delete_query = f"DELETE FROM MLModelMetrics WHERE Id IN ({placeholders})"
            conn.execute(delete_query, ids_to_delete)
            conn.commit()
            
            logger.info(f"🗑️ Видалено {len(ids_to_delete)} старих записів метрик")
        
        return len(ids_to_delete)
    
    def get_training_data_stats(self) -> Dict:
        """Отримання статистики тренувальних даних"""
        conn = self.get_connection()
        
        stats = {}
        
        # Загальна статистика
        cursor = conn.execute("SELECT COUNT(*) FROM MLTrainingData")
        stats['total_interactions'] = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(DISTINCT UserId) FROM MLTrainingData")
        stats['unique_users'] = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(DISTINCT SpotifyTrackId) FROM MLTrainingData")
        stats['unique_tracks'] = cursor.fetchone()[0]
        
        # Статистика по типах взаємодій
        cursor = conn.execute("""
            SELECT InteractionType, COUNT(*) 
            FROM MLTrainingData 
            GROUP BY InteractionType
        """)
        stats['interaction_types'] = dict(cursor.fetchall())
        
        # Статистика по рейтингах
        cursor = conn.execute("""
            SELECT 
                AVG(Rating) as avg_rating,
                MIN(Rating) as min_rating,
                MAX(Rating) as max_rating
            FROM MLTrainingData
        """)
        rating_stats = cursor.fetchone()
        stats['rating_stats'] = {
            'avg': rating_stats[0],
            'min': rating_stats[1],
            'max': rating_stats[2]
        }
        
        return stats 