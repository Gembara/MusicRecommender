# 🎵 Music Recommender ML Service 2.0

Потужний Python ML сервіс для музичних рекомендацій на основі аудіо фічей та поведінки користувачів.

## 🎯 Що робить сервіс

### 📊 Дані для тренування
- **Features (фічі)**: аудіо характеристики пісень з Spotify API
- **Labels (мітки)**: поведінка користувача (рейтинги, лайки, тривалість прослуховування)

### 🎵 Аудіо фічі
```
🎵 Danceability - танцювальність (0-1)
⚡ Energy - енергія (0-1)  
😊 Valence - настрій (0-1)
🥁 Tempo - темп (BPM, нормалізований)
🎸 Acousticness - акустичність (0-1)
🎼 Instrumentalness - інструментальність (0-1)
🗣️ Speechiness - мовність (0-1)
🔊 Loudness - гучність (dB, нормалізований)
📈 Popularity - популярність (0-100)
```

### 👤 Поведінкові мітки
```
⭐ Rating - рейтинг користувача (1-5)
❤️ IsLiked - чи подобається трек
⏱️ PlayDuration - тривалість прослуховування
⏭️ IsSkipped - чи був пропущений
```

## 🤖 ML Алгоритми

### 1. Content-Based (на основі контенту)
- **Модель**: Random Forest Regressor
- **Принцип**: аналізує аудіо характеристики улюблених треків користувача
- **Результат**: знаходить нові треки з схожими фічами

### 2. Collaborative Filtering (колаборативна фільтрація)
- **Модель**: K-Nearest Neighbors (KNN) з cosine similarity
- **Принцип**: знаходить користувачів зі схожими смаками
- **Результат**: рекомендує треки, які подобались схожим користувачам

### 3. Hybrid (гібридний підхід)
- **Принцип**: комбінує Content-Based (60%) + Collaborative (40%)
- **Переваги**: найкращий результат для більшості користувачів

## 🚀 Запуск сервісу

### Вимоги
- Python 3.8+
- SQLite база даних з проекту MusicRecommender

### Встановлення та запуск
```bash
# Перехід в папку ML сервісу
cd ml_service

# Автоматичний запуск (встановить залежності та запустить сервіс)
python start_service.py

# Або ручний запуск
pip install -r requirements.txt
python main.py
```

### Доступ до сервісу
- **API**: http://localhost:8000
- **Документація**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

## 🔧 API Endpoints

### 📚 Основні endpoint'и

#### `POST /train`
Тренування ML моделей на даних з бази
```json
{
  "success": true,
  "message": "✅ Моделі натреновано успішно!",
  "metrics": {
    "content_mse": 0.234,
    "content_mae": 0.156,
    "collaborative_sparsity": 0.892,
    "total_training_samples": 1500,
    "unique_users": 25,
    "unique_tracks": 200
  }
}
```

#### `POST /recommend/content`
Content-based рекомендації
```json
{
  "user_id": 1,
  "limit": 10
}
```

#### `POST /recommend/collaborative`  
Collaborative filtering рекомендації
```json
{
  "user_id": 1,
  "limit": 10
}
```

#### `POST /recommend/hybrid`
Гібридні рекомендації (рекомендовано)
```json
{
  "user_id": 1,
  "limit": 10
}
```

#### `GET /models/info`
Інформація про натреновані моделі та дані

### 📋 Приклад відповіді з рекомендаціями
```json
[
  {
    "track_id": "4iV5W9uYEdYUVa79Axb7Rh",
    "artist": "The Weeknd",
    "predicted_rating": 4.67,
    "reason": "Content-Based: схожі аудіо характеристики",
    "features": {
      "danceability": 0.679,
      "energy": 0.641,
      "valence": 0.486,
      "genre": "pop"
    }
  }
]
```

## 🔍 Як працює тренування

### 1. Завантаження даних
- Взаємодії користувачів з `UserSongInteractions`
- Аудіо фічі з `SongFeatures`
- Об'єднання даних за `SpotifyTrackId`

### 2. Підготовка фічей
- Нормалізація `Tempo` та `Loudness`
- Очищення від NaN значень
- Стандартизація через `StandardScaler`

### 3. Тренування моделей
- **Content**: Random Forest на аудіо фічах → предикція рейтингу
- **Collaborative**: KNN на user-item матриці → пошук схожих користувачів

### 4. Оцінка якості
- MSE (Mean Squared Error) для content-based моделі
- Розрідженість матриці для collaborative моделі
- Feature importance для розуміння важливості фічей

## 🛠️ Технічні деталі

### Архітектура
```
├── data_loader.py     # Завантаження та підготовка даних
├── ml_models.py       # ML моделі та алгоритми
├── main.py           # FastAPI додаток
├── start_service.py  # Скрипт запуску
└── models/           # Збережені моделі (створюється автоматично)
```

### Залежності
- **FastAPI**: веб фреймворк для API
- **scikit-learn**: ML алгоритми
- **pandas**: обробка даних
- **numpy**: математичні операції
- **uvicorn**: ASGI сервер

### Збереження моделей
Натреновані моделі автоматично зберігаються в папці `models/`:
- `content_model.pkl` - Random Forest модель
- `collaborative_model.pkl` - KNN модель  
- `user_item_matrix.pkl` - матриця користувач-трек
- `scaler.pkl` - нормалізатор фічей

## 🎯 Результати

Сервіс генерує персоналізовані рекомендації на основі:
- ✅ Ваших уподобань (лайки, рейтинги)
- ✅ Аудіо характеристик улюблених треків
- ✅ Поведінки схожих користувачів
- ✅ Комбінації різних підходів ML

**Рекомендації стають точнішими з часом, коли користувач додає більше взаємодій!** 🚀 