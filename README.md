# 🎵 Music Recommender App

Інтелектуальна система музичних рекомендацій з використанням машинного навчання та інтеграцією з Spotify API.

## 🚀 Особливості

### 🎯 Core Features
- **Розумні рекомендації** з використанням 3 ML алгоритмів
- **Spotify інтеграція** для отримання музичних даних
- **Персоналізовані плейлисти** на основі історії прослуховування
- **Улюблені треки** з можливістю управління
- **Історія прослуховування** з аналітикою

### 🤖 ML Service Features
- **Content-Based Filtering** - Random Forest на аудіо характеристиках
- **Collaborative Filtering** - KNN на user-item матриці
- **Hybrid Approach** - Адаптивна комбінація алгоритмів
- **Enhanced Data Collection** - Збір контекстних даних для покращення якості
- **Real-time Training** - Динамічне оновлення моделей

## 🏗️ Архітектура

```
MusicRecommender/
├── 🎯 ASP.NET Core Web App (Frontend + API)
│   ├── Controllers/        # API контролери
│   ├── Services/          # Бізнес логіка
│   ├── Models/            # Моделі даних
│   ├── Views/             # Razor Pages
│   └── wwwroot/           # Статичні файли
│
├── 🤖 ML Service (Python FastAPI)
│   ├── main.py            # FastAPI сервіс
│   ├── ml_models.py       # ML алгоритми
│   ├── enhanced_data_loader.py  # Завантаження даних
│   └── requirements.txt   # Python залежності
│
├── 📊 Database (SQLite)
│   ├── Songs              # Каталог музики
│   ├── Users              # Користувачі
│   ├── Favorites          # Улюблені треки
│   ├── ListeningHistory   # Історія прослуховування
│   ├── MLTrainingData     # Дані для тренування ML
│   └── MLUserProfiles     # Профілі користувачів
│
└── 🔧 Scripts & Tools
    ├── create_test_users.py      # Створення тестових користувачів
    ├── expand_music_database.py  # Розширення музичної БД
    └── test_ml_training_system.py # Тестування ML системи
```

## 🚀 Технології

### Backend
- **ASP.NET Core 8.0** - Web framework
- **Entity Framework Core** - ORM
- **SQLite** - База даних
- **Newtonsoft.Json** - JSON обробка

### ML Service
- **Python 3.8+** - Мова програмування
- **FastAPI** - Веб фреймворк для ML API
- **scikit-learn** - Machine Learning
- **pandas** - Обробка даних
- **numpy** - Числові обчислення

### Frontend
- **HTML/CSS/JavaScript** - Клієнтська частина
- **Bootstrap** - UI фреймворк
- **Chart.js** - Візуалізація даних

### Інтеграції
- **Spotify Web API** - Музичні дані
- **HTTP Client** - Інтеграція між сервісами

## 📊 ML Метрики

Система відстежує наступні метрики для оцінки якості моделей:

### Content-Based Model
- **MAE (Mean Absolute Error)** - Середня абсолютна помилка
- **MSE (Mean Squared Error)** - Середньоквадратична помилка
- **Feature Count** - Кількість використаних ознак

### Collaborative Filtering
- **Matrix Sparsity** - Розрідженість user-item матриці
- **User Coverage** - Покриття користувачів
- **Item Coverage** - Покриття треків

### Dataset Metrics
- **Training Samples** - Кількість тренувальних зразків
- **Unique Users** - Унікальні користувачі
- **Unique Tracks** - Унікальні треки
- **Training Duration** - Час тренування

## 🛠️ Встановлення та запуск

### Передумови
- .NET 8.0 SDK
- Python 3.8+
- Spotify Developer Account

### Крок 1: Клонування репозиторію
```bash
git clone <repository-url>
cd MusicRecommender
```

### Крок 2: Налаштування .NET застосунку
```bash
# Відновлення пакетів
dotnet restore

# Створення бази даних
dotnet ef database update

# Запуск веб-застосунку
dotnet run
```

### Крок 3: Налаштування ML сервісу
```bash
cd ml_service

# Встановлення Python залежностей
pip install -r requirements.txt

# Запуск ML сервісу
python main.py
```

### Крок 4: Налаштування Spotify API
1. Створіть додаток на [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Додайте ваші Client ID та Client Secret в `appsettings.json`
3. Налаштуйте Redirect URI

## 🔧 Конфігурація

### appsettings.json
```json
{
  "Spotify": {
    "ClientId": "your_spotify_client_id",
    "ClientSecret": "your_spotify_client_secret",
    "RedirectUri": "https://localhost:5001/callback"
  },
  "MLService": {
    "BaseUrl": "http://localhost:8000"
  }
}
```

## 📈 Використання

### Веб-інтерфейс
1. Відкрийте браузер та перейдіть на `https://localhost:5001`
2. Авторизуйтесь через Spotify
3. Досліджуйте рекомендації, додавайте улюблені треки
4. Переглядайте історію прослуховування

### ML API
ML сервіс доступний на `http://localhost:8000` з наступними endpoint'ами:

- `GET /` - Статус сервісу
- `POST /train` - Тренування моделей
- `POST /recommend` - Отримання рекомендацій
- `GET /models/info` - Інформація про моделі
- `GET /data/stats` - Статистика даних

### API Documentation
Детальна документація API доступна на:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Тестування

### Запуск ML тестів
```bash
python test_ml_training_system.py
```

### Створення тестових даних
```bash
python create_test_users.py
python expand_music_database.py
python add_demo_data.py
```

## 📊 Моніторинг

Система надає детальну аналітику:
- Метрики якості ML моделей
- Статистика використання
- Лоції тренування та помилок
- Performance metrics

## 🤝 Внесок

1. Fork репозиторій
2. Створіть feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit ваші зміни (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Відкрийте Pull Request

## 📝 Ліцензія

Цей проект ліцензовано під MIT License - деталі в файлі [LICENSE](LICENSE).

## 👥 Автори

- **Розробник** - Система музичних рекомендацій з ML

## 🙏 Подяки

- Spotify за надання Web API
- scikit-learn спільнота за ML алгоритми
- ASP.NET Core команда за веб фреймворк #   M u s i c R e c o m m e n d e r  
 