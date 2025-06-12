import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity, pairwise_distances
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
import logging
from typing import List, Dict, Tuple
from data_loader import DataLoader
import os
from scipy.sparse import csr_matrix
from scipy.spatial.distance import cosine

logger = logging.getLogger(__name__)

class MusicRecommenderML:
    def __init__(self):
        self.data_loader = DataLoader()
        self.content_model = None  # Content-based модель
        self.collaborative_model = None  # Collaborative filtering модель
        self.svd_model = None  # SVD модель
        self.scaler = StandardScaler()
        self.feature_columns = [
            'Danceability', 'Energy', 'Valence', 'Tempo_norm',
            'Acousticness', 'Instrumentalness', 'Speechiness',
            'Loudness_norm', 'Popularity'
        ]
        self.is_trained = False
        
        # Додаткові атрибути для покращених алгоритмів
        self.user_item_matrix = None
        self.user_item_matrix_normalized = None
        self.user_means = None
        self.item_means = None
        self.global_mean = None
        self.svd_user_factors = None
        self.svd_item_factors = None
        self.user_id_to_idx = {}
        self.item_id_to_idx = {}
        self.idx_to_user_id = {}
        self.idx_to_item_id = {}
        
    def train_models(self) -> Dict[str, float]:
        """
        Тренування всіх моделей з покращеними алгоритмами:
        1. Content-Based: Random Forest для предикції рейтингу на основі аудіо фічей
        2. Collaborative: покращений KNN з нормалізацією та weighted similarities
        3. SVD: правильна матрична факторизація з bias terms
        """
        logger.info("🎯 Початок тренування покращених ML моделей...")
        
        # Завантажуємо дані
        training_data, all_features = self.data_loader.prepare_training_data()
        
        if training_data.empty:
            logger.error("❌ Немає даних для тренування!")
            return {"error": "Немає даних для тренування"}
        
        logger.info(f"📊 Дані для тренування: {len(training_data)} записів")
        
        # Підготовка базових структур даних
        self._prepare_user_item_mappings(training_data)
        
        # 1. Тренування Content-Based моделі
        content_metrics = self._train_content_based_model(training_data)
        
        # 2. Тренування покращеної Collaborative Filtering моделі
        collaborative_metrics = self._train_improved_collaborative_model(training_data)
        
        # 3. Тренування покращеної SVD моделі
        svd_metrics = self._train_improved_svd_model(training_data)
        
        self.is_trained = True
        
        metrics = {
            **content_metrics,
            **collaborative_metrics,
            **svd_metrics,
            "total_training_samples": len(training_data),
            "unique_users": training_data['UserId'].nunique(),
            "unique_tracks": training_data['SpotifyTrackId'].nunique()
        }
        
        logger.info("✅ Тренування покращених моделей завершено успішно!")
        return metrics
    
    def _prepare_user_item_mappings(self, data: pd.DataFrame):
        """Підготовка індексних мапінгів для користувачів та елементів"""
        unique_users = sorted(data['UserId'].unique())
        unique_items = sorted(data['SpotifyTrackId'].unique())
        
        self.user_id_to_idx = {user_id: idx for idx, user_id in enumerate(unique_users)}
        self.item_id_to_idx = {item_id: idx for idx, item_id in enumerate(unique_items)}
        self.idx_to_user_id = {idx: user_id for user_id, idx in self.user_id_to_idx.items()}
        self.idx_to_item_id = {idx: item_id for item_id, idx in self.item_id_to_idx.items()}
        
        logger.info(f"📋 Мапінги створені: {len(unique_users)} користувачів, {len(unique_items)} треків")

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
    
    def _train_improved_collaborative_model(self, data: pd.DataFrame) -> Dict[str, float]:
        """Покращена Collaborative Filtering модель з нормалізацією та weighted similarities"""
        logger.info("👥 Тренування покращеної Collaborative Filtering моделі...")
        
        # Створюємо покращену user-item матрицю
        n_users = len(self.user_id_to_idx)
        n_items = len(self.item_id_to_idx)
        
        # Створюємо розріджену матрицю для ефективності
        user_indices = [self.user_id_to_idx[uid] for uid in data['UserId']]
        item_indices = [self.item_id_to_idx[iid] for iid in data['SpotifyTrackId']]
        ratings = data['Rating'].values
        
        # Створюємо щільну матрицю для KNN (невелика кількість користувачів)
        self.user_item_matrix = np.zeros((n_users, n_items))
        for u_idx, i_idx, rating in zip(user_indices, item_indices, ratings):
            self.user_item_matrix[u_idx, i_idx] = rating
        
        # Обчислюємо середні рейтинги для нормалізації
        self.user_means = np.array([
            np.mean(self.user_item_matrix[u][self.user_item_matrix[u] > 0]) 
            if np.any(self.user_item_matrix[u] > 0) else 3.0 
            for u in range(n_users)
        ])
        
        self.global_mean = np.mean(ratings)
        
        # Створюємо нормалізовану матрицю (віднімаємо середні рейтинги користувачів)
        self.user_item_matrix_normalized = self.user_item_matrix.copy()
        for u_idx in range(n_users):
            mask = self.user_item_matrix[u_idx] > 0
            self.user_item_matrix_normalized[u_idx][mask] -= self.user_means[u_idx]
        
        # Тренування покращеної KNN моделі з pearson correlation
        # Використовуємо тільки користувачів з мінімум 2 рейтингами
        active_users_mask = np.sum(self.user_item_matrix > 0, axis=1) >= 2
        self.active_user_indices = np.where(active_users_mask)[0]
        
        if len(self.active_user_indices) < 2:
            logger.warning("⚠️ Недостатньо активних користувачів для collaborative filtering")
            self.collaborative_model = None
            return {"collaborative_error": "Недостатньо даних"}
        
        # Використовуємо нормалізовану матрицю для навчання KNN
        active_user_matrix = self.user_item_matrix_normalized[self.active_user_indices]
        
        # Кастомна метрика схожості (adjusted cosine similarity)
        self.collaborative_model = NearestNeighbors(
            n_neighbors=min(10, len(self.active_user_indices)),
            metric='cosine',
            algorithm='brute'
        )
        
        # Замінюємо нулі на середні значення для покращення cosine similarity
        filled_matrix = active_user_matrix.copy()
        for i in range(len(filled_matrix)):
            mask = active_user_matrix[i] == 0
            filled_matrix[i][mask] = 0  # Залишаємо нулі, але використовуємо weights
        
        self.collaborative_model.fit(filled_matrix)
        
        # Зберігаємо додаткову інформацію для кращих рекомендацій
        self.active_user_matrix = active_user_matrix
        
        # Обчислюємо метрики
        sparsity = 1 - (np.count_nonzero(self.user_item_matrix) / (n_users * n_items))
        avg_user_ratings = np.mean([np.sum(self.user_item_matrix[u] > 0) for u in range(n_users)])
        
        logger.info(f"🔍 Покращена Collaborative Model:")
        logger.info(f"   📊 Розрідженість: {sparsity:.3f}")
        logger.info(f"   👤 Активних користувачів: {len(self.active_user_indices)}")
        logger.info(f"   📈 Середня кількість рейтингів на користувача: {avg_user_ratings:.1f}")
        
        return {
            "collaborative_sparsity": sparsity,
            "collaborative_active_users": len(self.active_user_indices),
            "collaborative_avg_ratings_per_user": avg_user_ratings,
            "collaborative_normalization": "user_mean_centered"
        }
    
    def _train_improved_svd_model(self, data: pd.DataFrame) -> Dict[str, float]:
        """Покращена SVD модель з правильною матричною факторизацією та bias terms"""
        logger.info("🔄 Тренування покращеної SVD моделі...")
        
        n_users = len(self.user_id_to_idx)
        n_items = len(self.item_id_to_idx)
        
        # Створюємо правильну user-item матрицю (users x items)
        user_item_dense = self.user_item_matrix.copy()
        
        # Заповнюємо нулі середніми значеннями для SVD
        filled_matrix = user_item_dense.copy()
        for u_idx in range(n_users):
            user_ratings = user_item_dense[u_idx]
            rated_items = user_ratings > 0
            if np.any(rated_items):
                user_mean = np.mean(user_ratings[rated_items])
                filled_matrix[u_idx][~rated_items] = user_mean
            else:
                filled_matrix[u_idx][:] = self.global_mean
        
        # Нормалізуємо матрицю віднімаючи глобальний середній + user bias + item bias
        self.item_means = np.array([
            np.mean(filled_matrix[:, i][filled_matrix[:, i] > 0]) 
            if np.any(filled_matrix[:, i] > 0) else self.global_mean 
            for i in range(n_items)
        ])
        
        # Створюємо bias-corrected матрицю
        bias_corrected_matrix = filled_matrix.copy()
        for u_idx in range(n_users):
            for i_idx in range(n_items):
                if user_item_dense[u_idx, i_idx] > 0:  # тільки для реальних рейтингів
                    bias_corrected_matrix[u_idx, i_idx] = (
                        filled_matrix[u_idx, i_idx] - self.global_mean - 
                        (self.user_means[u_idx] - self.global_mean) - 
                        (self.item_means[i_idx] - self.global_mean)
                    )
        
        # Визначаємо оптимальну кількість компонентів
        max_components = min(50, min(n_users, n_items) - 1, 
                           int(np.sqrt(np.count_nonzero(user_item_dense))))
        n_components = max(5, max_components)
        
        # Тренуємо SVD на bias-corrected матриці
        self.svd_model = TruncatedSVD(
            n_components=n_components,
            random_state=42,
            n_iter=10,
            algorithm='randomized'
        )
        
        # Фітуємо SVD на транспонованій матриці (для кращої стабільності)
        U_reduced = self.svd_model.fit_transform(bias_corrected_matrix)
        Vt_reduced = self.svd_model.components_
        
        # Зберігаємо факторизовані матриці
        self.svd_user_factors = U_reduced  # [n_users, n_components]
        self.svd_item_factors = Vt_reduced.T  # [n_items, n_components]
        
        # Обчислюємо якість реконструкції
        reconstructed = U_reduced @ Vt_reduced
        mask = user_item_dense > 0
        if np.any(mask):
            mse_reconstruction = np.mean((bias_corrected_matrix[mask] - reconstructed[mask]) ** 2)
        else:
            mse_reconstruction = 0.0
        
        explained_variance_ratio = self.svd_model.explained_variance_ratio_.sum()
        
        logger.info(f"🔍 Покращена SVD Model:")
        logger.info(f"   🔧 Компонентів: {n_components}")
        logger.info(f"   📊 Пояснена дисперсія: {explained_variance_ratio:.3f}")
        logger.info(f"   🎯 MSE реконструкції: {mse_reconstruction:.3f}")
        logger.info(f"   ⚖️ Використовується bias correction")
        
        return {
            "svd_components": n_components,
            "svd_explained_variance": explained_variance_ratio,
            "svd_reconstruction_mse": mse_reconstruction,
            "svd_users": n_users,
            "svd_items": n_items,
            "svd_bias_correction": True
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
                'artist': track.get('Artist', 'Unknown Artist'),
                'Title': track.get('Title', 'Unknown Track'),  # Додаємо з великою літерою
                'Artist': track.get('Artist', 'Unknown Artist'),  # Додаємо з великою літерою
                'Genre': track.get('Genre', 'Unknown Genre'),  # Додаємо з великою літерою
                'predicted_rating': float(track['predicted_rating']),
                'reason': 'Content-Based: схожі аудіо характеристики',
                'algorithm': 'Content',
                'features': {
                    'danceability': float(track['Danceability']),
                    'energy': float(track['Energy']),
                    'valence': float(track['Valence']),
                    'genre': track.get('Genre', 'Unknown Genre')
                }
            })
        
        logger.info(f"✅ Згенеровано {len(result)} content-based рекомендацій")
        return result
    
    def get_collaborative_recommendations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Покращені KNN Collaborative Filtering рекомендації з weighted similarities"""
        if not self.is_trained or self.collaborative_model is None:
            logger.warning("⚠️ Покращена collaborative модель не натренована!")
            return []

        logger.info(f"👥 Генерація покращених collaborative рекомендацій для користувача {user_id}")

        try:
            if user_id not in self.user_id_to_idx:
                logger.warning(f"❌ Користувач {user_id} не знайдений у системі")
                return self._get_popular_items_fallback(limit)

            user_idx = self.user_id_to_idx[user_id]
            
            # Перевіряємо чи є користувач серед активних
            if user_idx not in self.active_user_indices:
                logger.warning(f"❌ Користувач {user_id} не є активним")
                return self._get_popular_items_fallback(limit)

            # Знаходимо індекс у активній матриці
            active_idx = np.where(self.active_user_indices == user_idx)[0][0]
            user_profile = self.active_user_matrix[active_idx:active_idx+1]

            # Знаходимо схожих користувачів
            distances, neighbor_indices = self.collaborative_model.kneighbors(
                user_profile, 
                n_neighbors=min(8, len(self.active_user_matrix))
            )
            
            # Виключаємо самого користувача
            neighbor_indices = neighbor_indices[0][1:]
            neighbor_distances = distances[0][1:]

            if len(neighbor_indices) == 0:
                logger.warning(f"❌ Не знайдено схожих користувачів для {user_id}")
                return self._get_popular_items_fallback(limit)

            # Конвертуємо distances в similarities (adjusted)
            neighbor_similarities = []
            for dist in neighbor_distances:
                if dist == 0:
                    sim = 1.0
                else:
                    sim = 1 / (1 + dist)  # Конвертуємо cosine distance в similarity
                neighbor_similarities.append(sim)

            # Отримуємо треки які користувач вже слухав
            user_interactions = self.data_loader.load_user_interactions()
            user_tracks = user_interactions[user_interactions['UserId'] == user_id]['SpotifyTrackId'].unique()
            listened_tracks = set(user_tracks)

            # Обчислюємо weighted рейтинги від сусідів
            item_scores = {}
            
            for neighbor_active_idx, similarity in zip(neighbor_indices, neighbor_similarities):
                neighbor_user_idx = self.active_user_indices[neighbor_active_idx]
                neighbor_ratings = self.user_item_matrix[neighbor_user_idx]
                neighbor_mean = self.user_means[neighbor_user_idx]
                
                # Знаходимо треки з високими рейтингами у сусіда
                for item_idx, rating in enumerate(neighbor_ratings):
                    if rating >= 4.0:  # тільки високооцінені треки
                        item_id = self.idx_to_item_id[item_idx]
                        
                        if item_id not in listened_tracks:
                            if item_id not in item_scores:
                                item_scores[item_id] = {
                                    'weighted_sum': 0.0,
                                    'similarity_sum': 0.0,
                                    'neighbor_count': 0,
                                    'max_rating': 0.0,
                                    'ratings': []
                                }
                            
                            # Weighted rating з врахуванням bias
                            adjusted_rating = rating - neighbor_mean + self.user_means[user_idx]
                            weighted_rating = adjusted_rating * similarity
                            
                            item_scores[item_id]['weighted_sum'] += weighted_rating
                            item_scores[item_id]['similarity_sum'] += similarity
                            item_scores[item_id]['neighbor_count'] += 1
                            item_scores[item_id]['max_rating'] = max(item_scores[item_id]['max_rating'], rating)
                            item_scores[item_id]['ratings'].append(rating)

            # Створюємо рекомендації з покращеним скорингом
            recommendations = []
            song_features = self.data_loader.load_song_features()
            features_dict = song_features.set_index('SpotifyTrackId').to_dict('index')

            for item_id, score_data in item_scores.items():
                if score_data['similarity_sum'] > 0:
                    # Покращена формула рейтингу
                    base_prediction = score_data['weighted_sum'] / score_data['similarity_sum']
                    
                    # Бонуси та штрафи
                    neighbor_bonus = min(0.5, score_data['neighbor_count'] * 0.1)
                    diversity_bonus = 0.2 if score_data['neighbor_count'] >= 3 else 0
                    confidence_penalty = -0.3 if score_data['similarity_sum'] < 0.5 else 0
                    
                    final_prediction = base_prediction + neighbor_bonus + diversity_bonus + confidence_penalty
                    final_prediction = max(1.0, min(5.0, final_prediction))
                    
                    track_info = features_dict.get(item_id, {})
                    
                    recommendation = {
                        'track_id': item_id,
                        'title': track_info.get('Title', 'Unknown Track'),
                        'artist': track_info.get('Artist', 'Unknown Artist'),
                        'genre': track_info.get('Genre', 'Unknown Genre'),
                        'Title': track_info.get('Title', 'Unknown Track'),
                        'Artist': track_info.get('Artist', 'Unknown Artist'),
                        'Genre': track_info.get('Genre', 'Unknown Genre'),
                        'predicted_rating': float(final_prediction),
                        'reason': f'KNN: {score_data["neighbor_count"]} схожих користувачів (weighted)',
                        'algorithm': 'Improved_KNN',
                        'neighbor_count': score_data['neighbor_count'],
                        'weighted_average': float(base_prediction),
                        'max_neighbor_rating': float(score_data['max_rating']),
                        'confidence': min(0.95, score_data['similarity_sum']),
                        'neighbor_similarities': neighbor_similarities[:score_data['neighbor_count']],
                        'bias_corrected': True,
                        'similarity_sum': float(score_data['similarity_sum'])
                    }
                    
                    recommendations.append(recommendation)

            # Сортуємо за predicted_rating та confidence
            recommendations.sort(key=lambda x: (x['predicted_rating'], x['confidence']), reverse=True)
            
            logger.info(f"✅ Згенеровано {len(recommendations)} покращених collaborative рекомендацій")
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"❌ Помилка покращених collaborative рекомендацій: {e}")
            return self._get_popular_items_fallback(limit)
    
    def get_svd_recommendations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Покращені SVD рекомендації з правильною матричною факторизацією та bias correction"""
        if not self.is_trained or self.svd_model is None:
            logger.warning("⚠️ Покращена SVD модель не натренована!")
            return []
        
        logger.info(f"🔄 Генерація покращених SVD рекомендацій для користувача {user_id}")
        
        try:
            if user_id not in self.user_id_to_idx:
                logger.warning(f"❌ Користувач {user_id} не знайдений у системі")
                return self._get_popular_items_fallback(limit)
            
            user_idx = self.user_id_to_idx[user_id]
            user_mean = self.user_means[user_idx]
            
            # Отримуємо латентний профіль користувача
            user_latent_profile = self.svd_user_factors[user_idx]  # [n_components]
            
            # Обчислюємо рейтинги для всіх треків через матричну факторизацію
            predicted_ratings = []
            
            for item_idx in range(len(self.idx_to_item_id)):
                item_latent = self.svd_item_factors[item_idx]  # [n_components]
                
                # SVD prediction: bias + user_factors × item_factors
                raw_prediction = np.dot(user_latent_profile, item_latent)
                
                # Додаємо bias terms
                bias_corrected_prediction = (
                    self.global_mean + 
                    (user_mean - self.global_mean) + 
                    (self.item_means[item_idx] - self.global_mean) + 
                    raw_prediction
                )
                
                predicted_ratings.append((item_idx, bias_corrected_prediction, raw_prediction))
            
            # Сортуємо за передбаченими рейтингами
            predicted_ratings.sort(key=lambda x: x[1], reverse=True)
            
            # Отримуємо треки які користувач вже слухав
            user_interactions = self.data_loader.load_user_interactions()
            user_tracks = user_interactions[user_interactions['UserId'] == user_id]['SpotifyTrackId'].unique()
            listened_tracks = set(user_tracks)
            
            # Створюємо рекомендації
            recommendations = []
            song_features = self.data_loader.load_song_features()
            features_dict = song_features.set_index('SpotifyTrackId').to_dict('index')
            
            for item_idx, predicted_rating, raw_score in predicted_ratings:
                if len(recommendations) >= limit:
                    break
                
                item_id = self.idx_to_item_id[item_idx]
                
                # Пропускаємо треки які користувач вже слухав
                if item_id in listened_tracks:
                    continue
                
                # Нормалізуємо рейтинг до діапазону 1-5
                normalized_rating = max(1.0, min(5.0, predicted_rating))
                
                track_info = features_dict.get(item_id, {})
                
                # Обчислюємо confidence на основі латентних факторів
                user_norm = np.linalg.norm(user_latent_profile)
                item_norm = np.linalg.norm(self.svd_item_factors[item_idx])
                if user_norm > 0 and item_norm > 0:
                    latent_similarity = np.dot(user_latent_profile, self.svd_item_factors[item_idx]) / (user_norm * item_norm)
                    confidence = min(0.95, abs(latent_similarity) + 0.3)
                else:
                    confidence = 0.5
                
                recommendation = {
                    'track_id': item_id,
                    'title': track_info.get('Title', 'Unknown Track'),
                    'artist': track_info.get('Artist', 'Unknown Artist'),
                    'genre': track_info.get('Genre', 'Unknown Genre'),
                    'Title': track_info.get('Title', 'Unknown Track'),
                    'Artist': track_info.get('Artist', 'Unknown Artist'),
                    'Genre': track_info.get('Genre', 'Unknown Genre'),
                    'predicted_rating': float(normalized_rating),
                    'reason': f'SVD: матрична факторизація з {self.svd_model.n_components} факторами',
                    'algorithm': 'Improved_SVD',
                    'raw_svd_score': float(raw_score),
                    'bias_corrected_prediction': float(predicted_rating),
                    'confidence': float(confidence),
                    'latent_similarity': float(latent_similarity) if 'latent_similarity' in locals() else 0.0,
                    'user_bias': float(user_mean - self.global_mean),
                    'item_bias': float(self.item_means[item_idx] - self.global_mean),
                    'global_mean': float(self.global_mean),
                    'matrix_factorization': True
                }
                
                recommendations.append(recommendation)
            
            logger.info(f"✅ Згенеровано {len(recommendations)} покращених SVD рекомендацій")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Помилка покращених SVD рекомендацій: {e}")
            return self._get_popular_items_fallback(limit)
    
    def _get_popular_items_fallback(self, limit: int) -> List[Dict]:
        """Fallback рекомендації на основі популярності"""
        try:
            logger.info("🔄 Використовуємо fallback на основі популярності")
            
            song_features = self.data_loader.load_song_features()
            user_interactions = self.data_loader.load_user_interactions()
            
            # Обчислюємо популярність треків
            track_popularity = user_interactions.groupby('SpotifyTrackId').agg({
                'Rating': ['count', 'mean']
            }).reset_index()
            
            track_popularity.columns = ['SpotifyTrackId', 'rating_count', 'avg_rating']
            track_popularity = track_popularity[track_popularity['rating_count'] >= 2]
            track_popularity = track_popularity.sort_values(['avg_rating', 'rating_count'], ascending=False)
            
            recommendations = []
            features_dict = song_features.set_index('SpotifyTrackId').to_dict('index')
            
            for _, row in track_popularity.head(limit).iterrows():
                track_id = row['SpotifyTrackId']
                track_info = features_dict.get(track_id, {})
                
                recommendation = {
                    'track_id': track_id,
                    'title': track_info.get('Title', 'Unknown Track'),
                    'artist': track_info.get('Artist', 'Unknown Artist'),
                    'genre': track_info.get('Genre', 'Unknown Genre'),
                    'Title': track_info.get('Title', 'Unknown Track'),
                    'Artist': track_info.get('Artist', 'Unknown Artist'),
                    'Genre': track_info.get('Genre', 'Unknown Genre'),
                    'predicted_rating': float(row['avg_rating']),
                    'reason': f'Популярний трек (mid={row["avg_rating"]:.2f}, n={row["rating_count"]})',
                    'algorithm': 'Popularity_Fallback',
                    'rating_count': int(row['rating_count']),
                    'confidence': 0.7
                }
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Помилка fallback рекомендацій: {e}")
            return []
    
    def get_hybrid_recommendations(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Гібридні рекомендації (комбінація content-based + collaborative + SVD)"""
        logger.info(f"🔀 Генерація гібридних рекомендацій для користувача {user_id}")
        
        # Отримуємо рекомендації з усіх моделей (більше треків для різноманітності)
        content_recs = self.get_content_recommendations(user_id, limit * 3)
        collaborative_recs = self.get_collaborative_recommendations(user_id, limit * 3)
        svd_recs = self.get_svd_recommendations(user_id, limit * 3)
        
        # Створюємо різноманітний пул рекомендацій
        combined_scores = {}
        
        # Content-Based: фокус на аудіо схожості (40%)
        for i, rec in enumerate(content_recs):
            track_id = rec['track_id']
            # Даємо більший вага першим рекомендаціям
            weight = 0.4 * (1.0 - i * 0.01)  # зменшуємо вагу для кожного наступного
            combined_scores[track_id] = {
                'score': rec['predicted_rating'] * weight,
                'info': rec,
                'methods': ['content'],
                'diversity_bonus': 0.1  # бонус за контент-схожість
            }
        
        # Collaborative: фокус на схожих користувачах (30%)
        for i, rec in enumerate(collaborative_recs):
            track_id = rec['track_id']
            weight = 0.3 * (1.0 - i * 0.01)
            if track_id in combined_scores:
                combined_scores[track_id]['score'] += rec['predicted_rating'] * weight
                combined_scores[track_id]['methods'].append('collaborative')
                combined_scores[track_id]['diversity_bonus'] += 0.15  # більший бонус за множинні методи
            else:
                combined_scores[track_id] = {
                    'score': rec['predicted_rating'] * weight,
                    'info': rec,
                    'methods': ['collaborative'],
                    'diversity_bonus': 0.05
                }
        
        # SVD: фокус на латентні фактори (30%)
        for i, rec in enumerate(svd_recs):
            track_id = rec['track_id']
            weight = 0.3 * (1.0 - i * 0.01)
            if track_id in combined_scores:
                combined_scores[track_id]['score'] += rec['predicted_rating'] * weight
                combined_scores[track_id]['methods'].append('svd')
                combined_scores[track_id]['diversity_bonus'] += 0.2  # найбільший бонус за SVD
            else:
                combined_scores[track_id] = {
                    'score': rec['predicted_rating'] * weight,
                    'info': rec,
                    'methods': ['svd'],
                    'diversity_bonus': 0.1
                }
        
        # Додаємо бонус за різноманітність
        for track_id, data in combined_scores.items():
            data['final_score'] = data['score'] + data['diversity_bonus']
        
        # Сортуємо за фінальним скором
        sorted_combined = sorted(
            combined_scores.items(),
            key=lambda x: x[1]['final_score'],
            reverse=True
        )[:limit]
        
        # Форматуємо результат з детальною інформацією
        result = []
        for track_id, data in sorted_combined:
            info = data['info'].copy()
            info['predicted_rating'] = float(data['final_score'])
            
            # Створюємо детальний опис причини рекомендації
            methods = data['methods']
            if len(methods) == 1:
                method_desc = {
                    'content': 'Content-Based: схожі аудіо характеристики',
                    'collaborative': 'Collaborative: схожі користувачі',
                    'svd': 'SVD: латентні музичні фактори'
                }
                info['reason'] = method_desc.get(methods[0], 'Hybrid')
            else:
                info['reason'] = f"Hybrid: {' + '.join(methods)} ({len(methods)} методи)"
            
            info['methods_used'] = methods
            info['diversity_score'] = float(data['diversity_bonus'])
            result.append(info)
        
        logger.info(f"✅ Згенеровано {len(result)} гібридних рекомендацій")
        return result
    
    def save_models(self, path: str = "models/"):
        """Збереження натренованих моделей"""
        os.makedirs(path, exist_ok=True)
        
        if self.content_model:
            joblib.dump(self.content_model, f"{path}/content_model.pkl")
            joblib.dump(self.scaler, f"{path}/scaler.pkl")
        
        if self.collaborative_model:
            joblib.dump(self.collaborative_model, f"{path}/collaborative_model.pkl")
            joblib.dump(self.user_item_matrix, f"{path}/user_item_matrix.pkl")
        
        if self.svd_model:
            joblib.dump(self.svd_model, f"{path}/svd_model.pkl")
            joblib.dump(self.user_item_matrix_normalized, f"{path}/user_item_matrix_normalized.pkl")
            joblib.dump(self.user_means, f"{path}/user_means.pkl")
            joblib.dump(self.item_means, f"{path}/item_means.pkl")
            joblib.dump(self.global_mean, f"{path}/global_mean.pkl")
            joblib.dump(self.svd_user_factors, f"{path}/svd_user_factors.pkl")
            joblib.dump(self.svd_item_factors, f"{path}/svd_item_factors.pkl")
        
        logger.info(f"💾 Моделі збережено в {path}")
    
    def load_models(self, path: str = "models/"):
        """Завантаження збережених моделей"""
        try:
            if os.path.exists(f"{path}/content_model.pkl"):
                self.content_model = joblib.load(f"{path}/content_model.pkl")
                self.scaler = joblib.load(f"{path}/scaler.pkl")
            
            if os.path.exists(f"{path}/collaborative_model.pkl"):
                self.collaborative_model = joblib.load(f"{path}/collaborative_model.pkl")
                self.user_item_matrix = joblib.load(f"{path}/user_item_matrix.pkl")
            
            if os.path.exists(f"{path}/svd_model.pkl"):
                self.svd_model = joblib.load(f"{path}/svd_model.pkl")
                self.user_item_matrix_normalized = joblib.load(f"{path}/user_item_matrix_normalized.pkl")
                self.user_means = joblib.load(f"{path}/user_means.pkl")
                self.item_means = joblib.load(f"{path}/item_means.pkl")
                self.global_mean = joblib.load(f"{path}/global_mean.pkl")
                self.svd_user_factors = joblib.load(f"{path}/svd_user_factors.pkl")
                self.svd_item_factors = joblib.load(f"{path}/svd_item_factors.pkl")
            
            self.is_trained = True
            logger.info(f"📥 Моделі завантажено з {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Помилка завантаження моделей: {e}")
            return False 