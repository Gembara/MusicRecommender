#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрація роботи SVD алгоритму для музичних рекомендацій
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import os

def create_demo_data():
    """Створює демонстраційні дані для тестування SVD"""
    print("🎵 Створення демонстраційних даних...")
    
    # Демонстраційні користувачі та треки
    users = [1, 2, 3, 4, 5]
    tracks = [
        "track_1_pop", "track_2_rock", "track_3_jazz", 
        "track_4_pop", "track_5_rock", "track_6_jazz",
        "track_7_pop", "track_8_electronic", "track_9_classical"
    ]
    
    # Створюємо матрицю рейтингів (користувач x трек)
    # Користувач 1 любить поп, Користувач 2 любить рок, і т.д.
    ratings_data = {
        1: {"track_1_pop": 5, "track_4_pop": 4, "track_7_pop": 5, "track_2_rock": 2, "track_3_jazz": 1},
        2: {"track_2_rock": 5, "track_5_rock": 4, "track_1_pop": 2, "track_8_electronic": 3, "track_3_jazz": 1},
        3: {"track_3_jazz": 5, "track_6_jazz": 4, "track_9_classical": 4, "track_1_pop": 2, "track_2_rock": 1},
        4: {"track_1_pop": 4, "track_4_pop": 5, "track_7_pop": 3, "track_8_electronic": 3, "track_9_classical": 2},
        5: {"track_8_electronic": 5, "track_2_rock": 3, "track_9_classical": 4, "track_3_jazz": 3, "track_1_pop": 2}
    }
    
    # Конвертуємо в DataFrame
    rows = []
    for user_id, user_ratings in ratings_data.items():
        for track_id, rating in user_ratings.items():
            rows.append({
                'UserId': user_id,
                'SpotifyTrackId': track_id,
                'Rating': rating
            })
    
    df = pd.DataFrame(rows)
    
    # Створюємо user-item матрицю
    user_item_matrix = df.pivot_table(
        index='UserId',
        columns='SpotifyTrackId',
        values='Rating',
        fill_value=0
    )
    
    print(f"📊 Створено матрицю {user_item_matrix.shape[0]} користувачів x {user_item_matrix.shape[1]} треків")
    print("\n🔢 User-Item матриця:")
    print(user_item_matrix)
    
    return user_item_matrix, df

def demonstrate_svd(user_item_matrix):
    """Демонструє роботу SVD алгоритму"""
    print("\n🔄 Застосування SVD...")
    
    # Створюємо SVD модель
    n_components = min(5, min(user_item_matrix.shape) - 1)
    svd_model = TruncatedSVD(n_components=n_components, random_state=42, n_iter=20)
    
    # Тренуємо на транспонованій матриці (items x users)
    items_matrix = user_item_matrix.T.values
    svd_model.fit(items_matrix)
    
    print(f"✅ SVD модель натренована з {n_components} компонентами")
    print(f"📊 Пояснена дисперсія: {svd_model.explained_variance_ratio_.sum():.3f}")
    
    # Трансформуємо треки в латентний простір
    items_transformed = svd_model.transform(items_matrix)
    
    print(f"\n🎯 Латентні представлення треків ({items_transformed.shape}):")
    track_names = user_item_matrix.columns
    for i, track in enumerate(track_names):
        print(f"{track}: {items_transformed[i][:3]}...")  # показуємо перші 3 компоненти
    
    return svd_model, items_transformed, user_item_matrix

def get_svd_recommendations(svd_model, items_transformed, user_item_matrix, user_id, limit=3):
    """Генерує SVD рекомендації для користувача"""
    print(f"\n🎵 Генерація SVD рекомендацій для користувача {user_id}...")
    
    if user_id not in user_item_matrix.index:
        print(f"❌ Користувач {user_id} не знайдений!")
        return []
    
    # Отримуємо рейтинги користувача
    user_idx = user_item_matrix.index.get_loc(user_id)
    user_ratings = user_item_matrix.iloc[user_idx].values
    
    print(f"📝 Рейтинги користувача {user_id}: {dict(zip(user_item_matrix.columns, user_ratings))}")
    
    # Знаходимо улюблені треки (рейтинг > 3)
    liked_tracks_mask = user_ratings > 3
    if not liked_tracks_mask.any():
        print(f"❌ Користувач {user_id} не має треків з високим рейтингом")
        return []
    
    # Створюємо профіль користувача в латентному просторі
    user_profile = np.mean(items_transformed[liked_tracks_mask], axis=0)
    print(f"👤 Профіль користувача в латентному просторі: {user_profile[:3]}...")
    
    # Розраховуємо схожість з усіма треками
    similarities = cosine_similarity([user_profile], items_transformed)[0]
    
    # Виключаємо прослухані треки
    listened_tracks_mask = user_ratings > 0
    similarities[listened_tracks_mask] = -1
    
    # Знаходимо топ рекомендації
    top_indices = np.argsort(similarities)[::-1][:limit]
    
    print(f"\n🏆 Топ-{limit} SVD рекомендацій:")
    recommendations = []
    for i, idx in enumerate(top_indices):
        if similarities[idx] > 0:
            track_name = user_item_matrix.columns[idx]
            similarity = similarities[idx]
            predicted_rating = similarity * 5  # нормалізуємо до 1-5
            
            recommendation = {
                'rank': i + 1,
                'track': track_name,
                'similarity': similarity,
                'predicted_rating': predicted_rating,
                'reason': 'SVD латентні фактори'
            }
            recommendations.append(recommendation)
            
            print(f"  {i+1}. {track_name}")
            print(f"     Схожість: {similarity:.3f}")
            print(f"     Передбачений рейтинг: {predicted_rating:.2f}")
            print(f"     Причина: SVD латентні фактори")
            print()
    
    return recommendations

def compare_users_in_latent_space(svd_model, items_transformed, user_item_matrix):
    """Порівнює користувачів у латентному просторі"""
    print("\n👥 Порівняння користувачів у латентному просторі...")
    
    user_profiles = []
    user_ids = []
    
    for user_id in user_item_matrix.index:
        user_ratings = user_item_matrix.loc[user_id].values
        liked_tracks_mask = user_ratings > 3
        
        if liked_tracks_mask.any():
            user_profile = np.mean(items_transformed[liked_tracks_mask], axis=0)
            user_profiles.append(user_profile)
            user_ids.append(user_id)
    
    # Розраховуємо схожість між користувачами
    if len(user_profiles) > 1:
        user_similarities = cosine_similarity(user_profiles)
        
        print("🔗 Схожість між користувачами:")
        for i, user_i in enumerate(user_ids):
            for j, user_j in enumerate(user_ids):
                if i < j:  # уникаємо дублювання
                    similarity = user_similarities[i][j]
                    print(f"  Користувач {user_i} ↔ Користувач {user_j}: {similarity:.3f}")

def main():
    """Основна функція демонстрації"""
    print("🎵 SVD Демонстрація для Music Recommender")
    print("=" * 50)
    
    # 1. Створюємо демонстраційні дані
    user_item_matrix, df = create_demo_data()
    
    # 2. Застосовуємо SVD
    svd_model, items_transformed, user_item_matrix = demonstrate_svd(user_item_matrix)
    
    # 3. Генеруємо рекомендації для кожного користувача
    for user_id in user_item_matrix.index:
        recommendations = get_svd_recommendations(
            svd_model, items_transformed, user_item_matrix, user_id, limit=3
        )
    
    # 4. Порівнюємо користувачів
    compare_users_in_latent_space(svd_model, items_transformed, user_item_matrix)
    
    print("\n✅ SVD демонстрація завершена!")
    print("\n📝 Що показала демонстрація:")
    print("   • SVD розкладає user-item матрицю на латентні фактори")
    print("   • Кожен трек представляється вектором у латентному просторі")
    print("   • Профіль користувача = середнє його улюблених треків")
    print("   • Рекомендації = треки найбільш схожі на профіль користувача")
    print("   • Схожість вимірюється через косинусну відстань")

if __name__ == "__main__":
    main() 