#!/usr/bin/env python3
"""
Проста демонстрація SVD принципів без зовнішніх бібліотек
"""

import math

def print_matrix(matrix, title=""):
    """Виводить матрицю у зручному форматі"""
    if title:
        print(f"\n{title}:")
    for row in matrix:
        print("  " + " ".join(f"{x:6.2f}" for x in row))

def svd_demo():
    """Демонстрація принципів SVD"""
    print("🎵 SVD Демонстрація для Music Recommender")
    print("=" * 50)
    
    # Створюємо демонстраційну user-item матрицю
    print("\n📊 1. Створення user-item матриці")
    print("   Рядки = Користувачі, Колонки = Треки")
    print("   Значення = Рейтинги (1-5)")
    
    # 5 користувачів, 6 треків
    user_item_matrix = [
        [5, 1, 0, 4, 0, 1],  # User 1: любить поп (треки 1,4)
        [0, 5, 4, 0, 1, 5],  # User 2: любить рок (треки 2,3,6)
        [4, 0, 0, 5, 0, 0],  # User 3: любить поп (треки 1,4)
        [0, 4, 5, 0, 5, 4],  # User 4: любить рок (треки 2,3,5,6)
        [5, 1, 0, 4, 0, 2],  # User 5: любить поп (треки 1,4)
    ]
    
    tracks = ["Pop1", "Rock1", "Rock2", "Pop2", "Rock3", "Rock4"]
    users = ["User1", "User2", "User3", "User4", "User5"]
    
    print_matrix(user_item_matrix, "User-Item матриця")
    print(f"   Треки: {tracks}")
    print(f"   Користувачі: {users}")
    
    print("\n🔍 2. Аналіз патернів")
    print("   📈 Група 1 (Pop lovers): User1, User3, User5 - люблять Pop1, Pop2")
    print("   🎸 Група 2 (Rock lovers): User2, User4 - люблять Rock1, Rock2, Rock3, Rock4")
    
    print("\n🔄 3. SVD принцип роботи")
    print("   SVD розкладає матрицю A = U × Σ × V^T")
    print("   • U: користувачі у латентному просторі")
    print("   • Σ: важливість латентних факторів")
    print("   • V^T: треки у латентному просторі")
    
    print("\n🎯 4. Латентні фактори (концептуально)")
    print("   Фактор 1: 'Pop vs Rock' (-1 = поп, +1 = рок)")
    print("   Фактор 2: 'Активність' (скільки музики слухає)")
    
    # Симуляція латентних факторів
    user_factors = [
        [-0.8, 0.6],   # User1: любить поп, середня активність
        [0.9, 0.8],    # User2: любить рок, висока активність
        [-0.7, 0.4],   # User3: любить поп, низька активність
        [0.8, 0.9],    # User4: любить рок, висока активність
        [-0.6, 0.5],   # User5: любить поп, середня активність
    ]
    
    item_factors = [
        [-0.9, 0.3],   # Pop1: чисто поп
        [0.8, 0.7],    # Rock1: чисто рок
        [0.7, 0.6],    # Rock2: рок
        [-0.8, 0.4],   # Pop2: поп
        [0.9, 0.8],    # Rock3: рок
        [0.6, 0.5],    # Rock4: рок
    ]
    
    print_matrix(user_factors, "Користувачі у латентному просторі (U)")
    print_matrix(item_factors, "Треки у латентному просторі (V)")
    
    print("\n🎵 5. Генерація рекомендацій для User1")
    user1_factors = user_factors[0]  # [-0.8, 0.6]
    print(f"   Профіль User1: {user1_factors} (любить поп, середня активність)")
    
    print("\n   Схожість з треками:")
    similarities = []
    for i, track_factors in enumerate(item_factors):
        # Обчислюємо косинусну схожість
        dot_product = sum(a * b for a, b in zip(user1_factors, track_factors))
        magnitude_user = math.sqrt(sum(x * x for x in user1_factors))
        magnitude_track = math.sqrt(sum(x * x for x in track_factors))
        similarity = dot_product / (magnitude_user * magnitude_track)
        similarities.append((tracks[i], similarity))
        
        print(f"   {tracks[i]}: {similarity:.3f}")
    
    # Сортуємо за схожістю
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    print("\n🏆 Рекомендації для User1 (за спаданням схожості):")
    for i, (track, sim) in enumerate(similarities[:3]):
        print(f"   {i+1}. {track} (схожість: {sim:.3f})")
    
    print("\n✅ 6. Висновки SVD:")
    print("   • SVD знаходить приховані фактори (жанри, настрій, тощо)")
    print("   • Зменшує розмірність даних (тисячі треків → кілька факторів)")
    print("   • Дозволяє рекомендувати треки через латентну схожість")
    print("   • Працює навіть з розрідженими даними (багато нулів)")
    print("   • Виявляє групи користувачів з подібними смаками")

if __name__ == "__main__":
    svd_demo() 