# 🎯 Система машинного навчання для Music Recommender

## 📋 Огляд

Ми створили окрему базу даних та систему для ефективного тренування ML моделей (KNN та інших алгоритмів) для музичних рекомендацій.

## 🗃️ Нові таблиці БД

### 1. `MLTrainingData` 
Основна таблиця для зберігання тренувальних даних:
- **Аудіо фічі**: Danceability, Energy, Valence, Tempo, Acousticness, тощо
- **Метадані**: Artist, Genre, ReleaseYear, ArtistPopularity  
- **Взаємодії**: Rating, InteractionType, PlayCount, PlayDuration
- **Контекст**: ListeningContext (morning/afternoon/evening/night), Timestamp
- **Користувацькі фічі**: UserAvgDanceability, UserAvgEnergy, тощо

### 2. `MLModelMetrics`
Статистика тренування моделей:
- Метрики якості: Accuracy, Precision, Recall, F1Score, MAE, MSE
- Дані про тренування: TrainingSamples, TestSamples, UniqueUsers, UniqueTracks
- Конфігурація: ModelConfig, FeatureImportance (JSON)

### 3. `MLUserProfiles`
ML профілі користувачів:
- **Музичні переваги**: PreferredDanceability, PreferredEnergy, тощо
- **Поведінкові патерни**: SkipRate, RepeatRate, ExplorationRate
- **Різноманітність**: GenreDiversity, ArtistDiversity
- **Кластеризація**: ClusterId для схожих користувачів

### 4. `TrackSimilarity`
Кеш схожості між треками:
- CosineSimilarity, EuclideanDistance
- AudioSimilarity, GenreSimilarity

### 5. `UserSimilarity`  
Кеш схожості між користувачами:
- CosineSimilarity, PearsonCorrelation, JaccardSimilarity
- CommonTracks (кількість спільних треків)

## 🛠️ Нові сервіси

### `MLDataCollectionService`
Автоматичний збір та підготовка тренувальних даних:
- Конвертація користувацьких взаємодій в тренувальні дані
- Обчислення рейтингів на основі типу взаємодії та тривалості прослуховування
- Створення та оновлення ML профілів користувачів
- Визначення контексту прослуховування

### `EnhancedDataLoader` (Python)
Покращений завантажувач даних для ML:
- Завантаження тренувальних даних з фільтрацією
- Підготовка даних для content-based та collaborative filtering
- Збереження метрик моделей в БД
- Отримання фічей треків для предикції

## 🔗 API Endpoints

### Збір тренувальних даних
```
POST /api/MLTraining/collect-training-data
```
Автоматично збирає нові взаємодії користувачів та конвертує їх в тренувальні дані.

### Створення/оновлення профілю користувача
```
POST /api/MLTraining/user-profile/{userId}
```
Створює або оновлює ML профіль користувача на основі його взаємодій.

### Тренування моделей
```
POST /api/MLTraining/train-models
Content-Type: application/json

{
  "ModelTypes": ["content", "collaborative", "hybrid"],
  "MinInteractionsPerUser": 5,
  "IncludeSkips": false,
  "TimeWindowDays": 30
}
```

### ML рекомендації
```
GET /api/MLTraining/recommendations/{userId}?modelType=hybrid&limit=20
```

### Статистика тренувальних даних
```
GET /api/MLTraining/training-data/stats
```

### Очищення старих даних
```
DELETE /api/MLTraining/training-data/cleanup?maxAgeDays=365
```

### Статус ML сервісу
```
GET /api/MLTraining/service/status
```

## 🔧 Налаштування

### 1. Застосування міграцій
```bash
dotnet ef database update
```

### 2. Запуск сервера
```bash
dotnet run
```

### 3. Запуск Python ML сервісу (опціонально)
```bash
cd ml_service
python start_service.py
```

## 📊 Як працює система

### 1. Збір даних
- Користувач взаємодіє з музикою (грає, скіпає, лайкає)
- `UserSongInteraction` записується в БД
- `MLDataCollectionService` конвертує взаємодії в структуровані тренувальні дані

### 2. Обчислення рейтингів
Рейтинг обчислюється на основі:
- **Тип взаємодії**: Liked (1.0), AddedToPlaylist (0.9), Played (0.6), Skipped (0.1)
- **Тривалість прослуховування**: Менше 10% = скіп, більше 80% = добре
- **Додаткові сигнали**: IsLiked, IsRepeat

### 3. Профілі користувачів
ML профіль містить:
- **Музичні переваги**: Середні значення аудіо фічей
- **Варіанси**: Наскільки різноманітні смаки користувача
- **Поведінка**: Скільки скіпає, повторює, досліджує нову музику
- **Різноманітність**: Жанрова та артистична різноманітність

### 4. Тренування моделей
- **Content-based**: Random Forest на аудіо фічах + контекст
- **Collaborative**: KNN на матриці user-item
- **Hybrid**: Комбінація обох підходів

## 🧪 Тестування

Запустіть тестовий скрипт:
```bash
python test_ml_training_system.py
```

Або тестуйте API вручну:
```bash
# Збір тренувальних даних
curl -X POST http://localhost:5000/api/MLTraining/collect-training-data

# Статистика
curl -X GET http://localhost:5000/api/MLTraining/training-data/stats

# Створення профілю користувача
curl -X POST http://localhost:5000/api/MLTraining/user-profile/1
```

## 📈 Переваги нової системи

1. **Структуровані дані**: Окремі таблиці для різних типів ML даних
2. **Автоматизація**: Автоматичний збір та підготовка тренувальних даних
3. **Масштабованість**: Індекси та оптимізовані запити для великих обсягів даних
4. **Моніторинг**: Збереження метрик моделей для аналізу продуктивності
5. **Кешування**: Попередньо обчислені схожості для швидших рекомендацій
6. **Профілювання**: Детальні профілі користувачів для персоналізації

## 🔮 Наступні кроки

1. Інтеграція з існуючою системою рекомендацій
2. Реалізація real-time оновлень профілів користувачів
3. A/B тестування різних алгоритмів
4. Додавання більш складних фічей (сезонність, настрій, тощо)
5. Впровадження deep learning моделей
6. Система зворотного зв'язку для покращення рекомендацій 