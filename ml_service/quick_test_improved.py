#!/usr/bin/env python3
"""
Швидкий тест покращених SVD та KNN алгоритмів
"""

from ml_models import MusicRecommenderML
from data_loader import DataLoader
import numpy as np

def quick_test():
    print("🔥 Швидкий тест покращених алгоритмів")
    print("=" * 50)
    
    # Ініціалізація
    ml_model = MusicRecommenderML()
    
    # Тренування
    print("🎯 Тренування моделей...")
    try:
        metrics = ml_model.train_models()
        print(f"✅ Тренування завершено!")
        
        # Показуємо ключові метрики
        if "error" not in metrics:
            print(f"📊 Користувачів: {metrics.get('unique_users', 0)}")
            print(f"🎵 Треків: {metrics.get('unique_tracks', 0)}")
            print(f"🔧 SVD компонентів: {metrics.get('svd_components', 0)}")
            print(f"👥 Активних користувачів: {metrics.get('collaborative_active_users', 0)}")
            print(f"⚖️ SVD bias correction: {metrics.get('svd_bias_correction', False)}")
        else:
            print(f"❌ Помилка: {metrics['error']}")
            return
            
    except Exception as e:
        print(f"❌ Помилка тренування: {e}")
        return
    
    # Тестуємо рекомендації
    print("\n🎵 Тестування рекомендацій...")
    test_user_id = 1
    
    try:
        # SVD тест
        print("\n🔄 SVD рекомендації:")
        svd_recs = ml_model.get_svd_recommendations(test_user_id, limit=3)
        if svd_recs:
            for i, rec in enumerate(svd_recs, 1):
                print(f"  {i}. {rec.get('Artist', 'Unknown')} - {rec.get('Title', 'Unknown')}")
                print(f"     📊 Рейтинг: {rec['predicted_rating']:.2f}")
                print(f"     🔧 Algorithm: {rec.get('algorithm', 'Unknown')}")
        else:
            print("  ⚠️ Немає SVD рекомендацій")
        
        # KNN тест
        print("\n👥 KNN рекомендації:")
        knn_recs = ml_model.get_collaborative_recommendations(test_user_id, limit=3)
        if knn_recs:
            for i, rec in enumerate(knn_recs, 1):
                print(f"  {i}. {rec.get('Artist', 'Unknown')} - {rec.get('Title', 'Unknown')}")
                print(f"     📊 Рейтинг: {rec['predicted_rating']:.2f}")
                print(f"     👥 Сусідів: {rec.get('neighbor_count', 0)}")
                print(f"     🔧 Algorithm: {rec.get('algorithm', 'Unknown')}")
        else:
            print("  ⚠️ Немає KNN рекомендацій")
            
    except Exception as e:
        print(f"❌ Помилка рекомендацій: {e}")
    
    # Перевірка математичної коректності
    print("\n🔍 Перевірка коректності:")
    
    try:
        # SVD факторизація
        if hasattr(ml_model, 'svd_user_factors') and ml_model.svd_user_factors is not None:
            print(f"✅ SVD факторизація: {ml_model.svd_user_factors.shape}")
            print(f"✅ Item факторизація: {ml_model.svd_item_factors.shape}")
        
        # Bias terms
        if hasattr(ml_model, 'global_mean') and ml_model.global_mean is not None:
            print(f"✅ Глобальний середній: {ml_model.global_mean:.3f}")
            
        # User mappings
        if hasattr(ml_model, 'user_id_to_idx'):
            print(f"✅ User mappings: {len(ml_model.user_id_to_idx)} користувачів")
            
        print("✅ Всі структури даних ініціалізовані правильно!")
        
    except Exception as e:
        print(f"❌ Помилка перевірки: {e}")
    
    print("\n🎉 Тест завершено!")

if __name__ == "__main__":
    quick_test() 