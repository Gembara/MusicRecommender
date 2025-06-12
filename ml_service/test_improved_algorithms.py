#!/usr/bin/env python3
"""
Тест покращених SVD та KNN алгоритмів
"""

import sys
import os
sys.path.append('.')

from ml_models import MusicRecommenderML
from data_loader import DataLoader
import pandas as pd
import numpy as np
import time

def test_improved_algorithms():
    """Детальний тест покращених алгоритмів"""
    
    print("🎯 Тестування покращених SVD та KNN алгоритмів")
    print("=" * 60)
    
    # Ініціалізація
    ml_model = MusicRecommenderML()
    data_loader = DataLoader()
    
    # 1. Завантаження та перевірка даних
    print("\n1️⃣ Перевірка даних...")
    try:
        training_data, all_features = data_loader.prepare_training_data()
        if training_data.empty:
            print("❌ Немає даних для тестування!")
            return
        
        print(f"✅ Завантажено {len(training_data)} записів")
        print(f"👤 Користувачів: {training_data['UserId'].nunique()}")
        print(f"🎵 Треків: {training_data['SpotifyTrackId'].nunique()}")
        print(f"📊 Середній рейтинг: {training_data['Rating'].mean():.2f}")
        
        # Показуємо розподіл рейтингів
        rating_dist = training_data['Rating'].value_counts().sort_index()
        print(f"📈 Розподіл рейтингів: {dict(rating_dist)}")
        
    except Exception as e:
        print(f"❌ Помилка завантаження даних: {e}")
        return
    
    # 2. Тренування покращених моделей
    print("\n2️⃣ Тренування покращених моделей...")
    start_time = time.time()
    
    try:
        metrics = ml_model.train_models()
        training_time = time.time() - start_time
        
        if "error" in metrics:
            print(f"❌ Помилка тренування: {metrics['error']}")
            return
        
        print(f"✅ Тренування завершено за {training_time:.2f} секунд")
        
        # Показуємо метрики
        print("\n📊 Метрики тренування:")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.4f}")
            else:
                print(f"   {key}: {value}")
                
    except Exception as e:
        print(f"❌ Помилка тренування: {e}")
        return
    
    # 3. Тестування KNN алгоритму
    print("\n3️⃣ Тестування покращеного KNN алгоритму...")
    test_user_ids = training_data['UserId'].unique()[:3]  # Перші 3 користувачі
    
    for user_id in test_user_ids:
        print(f"\n👤 Користувач {user_id}:")
        
        try:
            start_time = time.time()
            knn_recs = ml_model.get_collaborative_recommendations(user_id, limit=5)
            knn_time = time.time() - start_time
            
            if knn_recs:
                print(f"✅ KNN: {len(knn_recs)} рекомендацій за {knn_time:.3f}s")
                
                for i, rec in enumerate(knn_recs[:2], 1):
                    print(f"   {i}. {rec['artist']} - {rec['title']}")
                    print(f"      📊 Рейтинг: {rec['predicted_rating']:.2f}")
                    print(f"      👥 Сусідів: {rec.get('neighbor_count', 0)}")
                    print(f"      🎯 Confidence: {rec.get('confidence', 0):.3f}")
                    print(f"      ⚖️ Bias correction: {rec.get('bias_corrected', False)}")
                    
                # Перевіряємо унікальність алгоритму
                avg_confidence = np.mean([r['confidence'] for r in knn_recs])
                print(f"   📈 Середня впевненість: {avg_confidence:.3f}")
                
            else:
                print("⚠️ KNN: Немає рекомендацій")
                
        except Exception as e:
            print(f"❌ Помилка KNN для користувача {user_id}: {e}")
    
    # 4. Тестування SVD алгоритму
    print("\n4️⃣ Тестування покращеного SVD алгоритму...")
    
    for user_id in test_user_ids:
        print(f"\n👤 Користувач {user_id}:")
        
        try:
            start_time = time.time()
            svd_recs = ml_model.get_svd_recommendations(user_id, limit=5)
            svd_time = time.time() - start_time
            
            if svd_recs:
                print(f"✅ SVD: {len(svd_recs)} рекомендацій за {svd_time:.3f}s")
                
                for i, rec in enumerate(svd_recs[:2], 1):
                    print(f"   {i}. {rec['artist']} - {rec['title']}")
                    print(f"      📊 Рейтинг: {rec['predicted_rating']:.2f}")
                    print(f"      🔧 Raw SVD: {rec.get('raw_svd_score', 0):.3f}")
                    print(f"      ⚖️ User bias: {rec.get('user_bias', 0):.3f}")
                    print(f"      🎯 Item bias: {rec.get('item_bias', 0):.3f}")
                    print(f"      🔀 Matrix factorization: {rec.get('matrix_factorization', False)}")
                    
                # Перевіряємо якість SVD
                avg_raw_score = np.mean([r.get('raw_svd_score', 0) for r in svd_recs])
                print(f"   📈 Середній raw SVD score: {avg_raw_score:.3f}")
                
            else:
                print("⚠️ SVD: Немає рекомендацій")
                
        except Exception as e:
            print(f"❌ Помилка SVD для користувача {user_id}: {e}")
    
    # 5. Порівняння алгоритмів
    print("\n5️⃣ Порівняння алгоритмів...")
    
    test_user = test_user_ids[0]  # Беремо першого користувача
    
    try:
        print(f"\n🔍 Детальне порівняння для користувача {test_user}:")
        
        # Отримуємо рекомендації від усіх алгоритмів
        content_recs = ml_model.get_content_recommendations(test_user, 3)
        knn_recs = ml_model.get_collaborative_recommendations(test_user, 3)
        svd_recs = ml_model.get_svd_recommendations(test_user, 3)
        hybrid_recs = ml_model.get_hybrid_recommendations(test_user, 3)
        
        algorithms = [
            ("Content-Based", content_recs),
            ("Improved KNN", knn_recs),
            ("Improved SVD", svd_recs),
            ("Hybrid", hybrid_recs)
        ]
        
        for alg_name, recs in algorithms:
            if recs:
                avg_rating = np.mean([r['predicted_rating'] for r in recs])
                unique_tracks = len(set(r['track_id'] for r in recs))
                print(f"   {alg_name}: {len(recs)} рек., avg={avg_rating:.2f}, unique={unique_tracks}")
            else:
                print(f"   {alg_name}: Немає рекомендацій")
        
        # Перевіряємо різноманітність
        all_track_ids = set()
        for _, recs in algorithms:
            all_track_ids.update(r['track_id'] for r in recs)
        
        print(f"\n🎨 Загальна різноманітність: {len(all_track_ids)} унікальних треків")
        
    except Exception as e:
        print(f"❌ Помилка порівняння: {e}")
    
    # 6. Тест математичної коректності
    print("\n6️⃣ Перевірка математичної коректності...")
    
    try:
        # Перевіряємо SVD факторизацію
        if hasattr(ml_model, 'svd_user_factors') and ml_model.svd_user_factors is not None:
            user_factors_shape = ml_model.svd_user_factors.shape
            item_factors_shape = ml_model.svd_item_factors.shape
            
            print(f"✅ SVD факторизація:")
            print(f"   👤 User factors: {user_factors_shape}")
            print(f"   🎵 Item factors: {item_factors_shape}")
            print(f"   🔧 Компонентів: {user_factors_shape[1]}")
            
            # Перевіряємо чи факторизація робить сенс
            if user_factors_shape[1] == item_factors_shape[1]:
                print("   ✅ Розмірності факторів сумісні")
            else:
                print("   ❌ Розмірності факторів несумісні!")
        
        # Перевіряємо bias terms
        if hasattr(ml_model, 'user_means') and ml_model.user_means is not None:
            user_mean_range = (ml_model.user_means.min(), ml_model.user_means.max())
            global_mean = ml_model.global_mean
            
            print(f"✅ Bias correction:")
            print(f"   🌍 Глобальний середній: {global_mean:.3f}")
            print(f"   👤 User bias range: [{user_mean_range[0]:.3f}, {user_mean_range[1]:.3f}]")
            
            if 1 <= global_mean <= 5:
                print("   ✅ Глобальний середній в межах норми")
            else:
                print("   ⚠️ Глобальний середній поза межами 1-5")
        
        # Перевіряємо KNN нормалізацію
        if hasattr(ml_model, 'user_item_matrix_normalized') and ml_model.user_item_matrix_normalized is not None:
            normalized_mean = np.mean(ml_model.user_item_matrix_normalized[ml_model.user_item_matrix_normalized != 0])
            print(f"✅ KNN нормалізація:")
            print(f"   📊 Середнє нормалізованої матриці: {normalized_mean:.6f}")
            
            if abs(normalized_mean) < 0.1:  # Має бути близько до 0
                print("   ✅ Нормалізація коректна")
            else:
                print("   ⚠️ Нормалізація може бути некоректною")
                
    except Exception as e:
        print(f"❌ Помилка перевірки коректності: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Тестування покращених алгоритмів завершено!")
    print("\n🔧 Основні покращення:")
    print("   📐 SVD: правильна матрична факторизація з bias correction")
    print("   👥 KNN: нормалізація рейтингів та weighted similarities")
    print("   🎯 Обидва: кращі fallback механізми та обробка edge cases")
    print("   📊 Покращені метрики впевненості та якості")

if __name__ == "__main__":
    test_improved_algorithms() 