import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
import logging
from typing import List, Dict, Tuple
from data_loader import DataLoader

logger = logging.getLogger(__name__)

class MusicRecommenderML:
    def __init__(self):
        self.data_loader = DataLoader()
        self.content_model = None  # Content-based модель
        self.collaborative_model = None  # Collaborative filtering модель
        self.scaler = StandardScaler()
        self.feature_columns = [
            'Danceability', 'Energy', 'Valence', 'Tempo_norm',
            'Acousticness', 'Instrumentalness', 'Speechiness',
            'Loudness_norm', 'Popularity'
        ]
        self.is_trained = False
        
    def train_models(self) -> Dict[str, float]:
        """
        Тренування обох моделей:
        1. Content-Based: Random Forest для предикції рейтингу на основі аудіо фічей
        2. Collaborative: KNN для знаходження схожих користувачів
        """
        logger.info("🎯 Початок тренування ML моделей...")
        
        # Завантажуємо дані
        training_data, all_features = self.data_loader.prepare_training_data()
        
        if training_data.empty:
            logger.error("❌ Немає даних для тренування!")
            return {"error": "Немає даних для тренування"}
        
        logger.info(f"📊 Дані для тренування: {len(training_data)} записів")
        
        # 1. Тренування Content-Based моделі
        content_metrics = self._train_content_based_model(training_data)
        
        # 2. Тренування Collaborative Filtering моделі
        collaborative_metrics = self._train_collaborative_model(training_data)
        
        self.is_trained = True
        
        metrics = {
            **content_metrics,
            **collaborative_metrics,
            "total_training_samples": len(training_data),
            "unique_users": training_data['UserId'].nunique(),
            "unique_tracks": training_data['SpotifyTrackId'].nunique()
        }
        
        logger.info("✅ Тренування завершено успішно!")
        return metrics
    
    def _train_content_based_model(self, data: pd.DataFrame) -> Dict[str, float]:
        """Тренування Content-Based моделі"""
        logger.info("🎵 Тренування Content-Based моделі...")
        
        # Підготовка фічей
        X = data[self.feature_columns].fillna(0)
        y = data['Rating'].values
        
        # Нормалізація фічей
        X_scaled = self.scaler.fit_transform(X)
        
        # Розділення на тренувальний та тестовий набори
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Тренування Random Forest
        self.content_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.content_model.fit(X_train, y_train)
        
        # Оцінка моделі
        y_pred = self.content_model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Важливість фічей
        feature_importance = dict(zip(
            self.feature_columns,
            self.content_model.feature_importances_
        ))
        
        logger.info(f"📈 Content Model - MSE: {mse:.3f}, MAE: {mae:.3f}")
        logger.info(f"🔍 Найважливіші фічі: {sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]}")
        
        return {
            "content_mse": mse,
            "content_mae": mae,
            "content_feature_importance": feature_importance
        }
    
    def _train_collaborative_model(self, data: pd.DataFrame) -> Dict[str, float]:
        """Тренування Collaborative Filtering моделі"""
        logger.info("👥 Тренування Collaborative Filtering моделі...")
        
        # Створюємо матрицю user-item
        user_item_matrix = data.pivot_table(
            index='UserId',
            columns='SpotifyTrackId',
            values='Rating',
            fill_value=0
        )
        
        # Тренування KNN моделі
        self.collaborative_model = NearestNeighbors(
            n_neighbors=min(5, len(user_item_matrix) - 1),
            metric='cosine',
            algorithm='brute'
        )
        
        self.collaborative_model.fit(user_item_matrix.values)
        self.user_item_matrix = user_item_matrix
        
        # Простий розрахунок точності
        sparsity = 1 - (data.shape[0] / (user_item_matrix.shape[0] * user_item_matrix.shape[1]))
        
        logger.info(f"🔍 Collaborative Model - Розрідженість матриці: {sparsity:.3f}")
        logger.info(f"👤 Користувачів: {user_item_matrix.shape[0]}, 🎵 Треків: {user_item_matrix.shape[1]}")
        
        return {
            "collaborative_sparsity": sparsity,
            "collaborative_users": user_item_matrix.shape[0],
            "collaborative_items": user_item_matrix.shape[1]
        }
    
    def get_content_recommendations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Рекомендації на основі контенту (аудіо фічі)"""
        if not self.is_trained or self.content_model is None:
            logger.warning("⚠️ Модель не натренована!")
            return []
        
        logger.info(f"🎯 Генерація content-based рекомендацій для користувача {user_id}")
        
        # Отримуємо профіль користувача
        user_profile = self.data_loader.get_user_profile(user_id)
        if not user_profile:
            logger.warning(f"❌ Не знайдено профіль користувача {user_id}")
            return []
        
        # Завантажуємо всі доступні треки
        all_features = self.data_loader.load_song_features()
        if all_features.empty:
            return []
        
        # Отримуємо треки, які користувач вже слухав (з усіх джерел)
        user_interactions = self.data_loader.load_user_interactions()
        user_tracks = user_interactions[user_interactions['UserId'] == user_id]['SpotifyTrackId'].unique()
        listened_tracks = set(user_tracks)
        
        logger.info(f"Користувач {user_id} має {len(listened_tracks)} треків в історії: {list(listened_tracks)[:5]}...")
        
        # Фільтруємо нові треки (які користувач НЕ слухав)
        new_tracks = all_features[~all_features['SpotifyTrackId'].isin(listened_tracks)]
        
        logger.info(f"Знайдено {len(new_tracks)} нових треків для рекомендації")
        
        if new_tracks.empty:
            logger.warning("❌ Немає нових треків для рекомендації")
            return []
        
        # Нормалізуємо фічі нових треків
        new_tracks = new_tracks.copy()
        new_tracks['Tempo_norm'] = (new_tracks['Tempo'] - new_tracks['Tempo'].min()) / (new_tracks['Tempo'].max() - new_tracks['Tempo'].min())
        new_tracks['Loudness_norm'] = (new_tracks['Loudness'] - new_tracks['Loudness'].min()) / (new_tracks['Loudness'].max() - new_tracks['Loudness'].min())
        
        # Підготовка фічей для предикції
        X_new = new_tracks[self.feature_columns].fillna(0)
        X_new_scaled = self.scaler.transform(X_new)
        
        # Предикція рейтингів
        predicted_ratings = self.content_model.predict(X_new_scaled)
        
        # Додаємо предиковані рейтинги
        new_tracks = new_tracks.copy()
        new_tracks['predicted_rating'] = predicted_ratings
        
        # Сортуємо за предикованим рейтингом
        recommendations = new_tracks.nlargest(limit, 'predicted_rating')
        
        # Форматування результату
        result = []
        for _, track in recommendations.iterrows():
            result.append({
                'track_id': track['SpotifyTrackId'],
                'title': track.get('Title', 'Unknown Track'),
                'artist': track.get('Artist', 'Unknown'),
                'predicted_rating': float(track['predicted_rating']),
                'reason': 'Content-Based: схожі аудіо характеристики',
                'features': {
                    'danceability': float(track['Danceability']),
                    'energy': float(track['Energy']),
                    'valence': float(track['Valence']),
                    'genre': track.get('Genre', 'Unknown')
                }
            })
        
        logger.info(f"✅ Згенеровано {len(result)} content-based рекомендацій")
        return result
    
    def get_collaborative_recommendations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Рекомендації на основі схожих користувачів"""
        if not self.is_trained or self.collaborative_model is None:
            logger.warning("⚠️ Collaborative модель не натренована!")
            return []
        
        logger.info(f"👥 Генерація collaborative рекомендацій для користувача {user_id}")
        
        if user_id not in self.user_item_matrix.index:
            logger.warning(f"❌ Користувач {user_id} не знайдений у матриці")
            return []
        
        # Знаходимо схожих користувачів
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        user_vector = self.user_item_matrix.iloc[user_idx].values.reshape(1, -1)
        
        distances, indices = self.collaborative_model.kneighbors(user_vector)
        
        # Отримуємо рекомендації від схожих користувачів
        similar_users = [self.user_item_matrix.index[i] for i in indices[0][1:]]  # Виключаємо самого користувача
        
        # Агрегуємо рейтинги від схожих користувачів
        recommendations_scores = {}
        user_tracks = set(self.user_item_matrix.columns[self.user_item_matrix.iloc[user_idx] > 0])
        
        for similar_user_id in similar_users:
            similar_user_idx = self.user_item_matrix.index.get_loc(similar_user_id)
            similar_user_ratings = self.user_item_matrix.iloc[similar_user_idx]
            
            # Рекомендуємо треки, які подобались схожим користувачам, але не слухав поточний
            for track_id, rating in similar_user_ratings[similar_user_ratings > 3].items():
                if track_id not in user_tracks:
                    if track_id not in recommendations_scores:
                        recommendations_scores[track_id] = []
                    recommendations_scores[track_id].append(rating)
        
        # Обчислюємо середні рейтинги
        avg_recommendations = {
            track_id: np.mean(ratings) 
            for track_id, ratings in recommendations_scores.items()
        }
        
        # Сортуємо за рейтингом
        sorted_recommendations = sorted(
            avg_recommendations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
        
        # Додаємо інформацію про треки
        all_features = self.data_loader.load_song_features()
        result = []
        
        for track_id, predicted_rating in sorted_recommendations:
            track_info = all_features[all_features['SpotifyTrackId'] == track_id]
            if not track_info.empty:
                track = track_info.iloc[0]
                result.append({
                    'track_id': track_id,
                    'title': track.get('Title', 'Unknown Track'),
                    'artist': track.get('Artist', 'Unknown'),
                    'predicted_rating': float(predicted_rating),
                    'reason': f'Collaborative: рекомендовано схожими користувачами {similar_users[:2]}',
                    'features': {
                        'danceability': float(track['Danceability']),
                        'energy': float(track['Energy']),
                        'valence': float(track['Valence']),
                        'genre': track.get('Genre', 'Unknown')
                    }
                })
        
        logger.info(f"✅ Згенеровано {len(result)} collaborative рекомендацій")
        return result
    
    def get_hybrid_recommendations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Гібридні рекомендації (комбінація content-based + collaborative)"""
        logger.info(f"🔀 Генерація гібридних рекомендацій для користувача {user_id}")
        
        # Отримуємо рекомендації з обох моделей
        content_recs = self.get_content_recommendations(user_id, limit * 2)
        collaborative_recs = self.get_collaborative_recommendations(user_id, limit * 2)
        
        # Комбінуємо з вагами: 60% content + 40% collaborative
        combined_scores = {}
        
        for rec in content_recs:
            track_id = rec['track_id']
            combined_scores[track_id] = {
                'score': rec['predicted_rating'] * 0.6,
                'info': rec,
                'methods': ['content']
            }
        
        for rec in collaborative_recs:
            track_id = rec['track_id']
            if track_id in combined_scores:
                combined_scores[track_id]['score'] += rec['predicted_rating'] * 0.4
                combined_scores[track_id]['methods'].append('collaborative')
            else:
                combined_scores[track_id] = {
                    'score': rec['predicted_rating'] * 0.4,
                    'info': rec,
                    'methods': ['collaborative']
                }
        
        # Сортуємо за комбінованим скором
        sorted_combined = sorted(
            combined_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:limit]
        
        # Форматуємо результат
        result = []
        for track_id, data in sorted_combined:
            info = data['info'].copy()
            info['predicted_rating'] = float(data['score'])
            info['reason'] = f"Hybrid: {', '.join(data['methods'])}"
            result.append(info)
        
        logger.info(f"✅ Згенеровано {len(result)} гібридних рекомендацій")
        return result
    
    def save_models(self, path: str = "models/"):
        """Збереження натренованих моделей"""
        import os
        os.makedirs(path, exist_ok=True)
        
        if self.content_model:
            joblib.dump(self.content_model, f"{path}/content_model.pkl")
            joblib.dump(self.scaler, f"{path}/scaler.pkl")
        
        if self.collaborative_model:
            joblib.dump(self.collaborative_model, f"{path}/collaborative_model.pkl")
            joblib.dump(self.user_item_matrix, f"{path}/user_item_matrix.pkl")
        
        logger.info(f"💾 Моделі збережено в {path}")
    
    def load_models(self, path: str = "models/"):
        """Завантаження збережених моделей"""
        import os
        try:
            if os.path.exists(f"{path}/content_model.pkl"):
                self.content_model = joblib.load(f"{path}/content_model.pkl")
                self.scaler = joblib.load(f"{path}/scaler.pkl")
            
            if os.path.exists(f"{path}/collaborative_model.pkl"):
                self.collaborative_model = joblib.load(f"{path}/collaborative_model.pkl")
                self.user_item_matrix = joblib.load(f"{path}/user_item_matrix.pkl")
            
            self.is_trained = True
            logger.info(f"📥 Моделі завантажено з {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка завантаження моделей: {e}")
            return False 