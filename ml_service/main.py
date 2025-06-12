from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import logging
import asyncio
import time
from datetime import datetime
from ml_models import MusicRecommenderML
from enhanced_data_loader import EnhancedDataLoader
import pandas as pd

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ініціалізація FastAPI
app = FastAPI(
    title="🎵 Music Recommender ML Service Enhanced",
    description="""
    ## 🤖 Покращений сервіс музичних рекомендацій
    
    ### 🎯 Алгоритми:
    - **Content-Based**: Random Forest на аудіо характеристиках + контекст
    - **Collaborative**: KNN на матриці user-item з покращеними даними
    - **Hybrid**: Адаптивна комбінація обох підходів
    
    ### 📊 Нова система даних:
    
    - **MLTrainingData**: Структуровані тренувальні дані
    - **MLUserProfiles**: Профілі користувачів з поведінковими патернами
    - **Enhanced Features**: Контекст прослуховування, часові патерни
    
    ### 🔧 Нові можливості:
    - Автоматичний збір та підготовка тренувальних даних
    - Збереження метрик моделей в БД
    - Кешування схожостей для швидших рекомендацій
    
    Версія 3.0 для Music Recommender App 🎵
    """,
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ініціалізація ML рекомендера та покращеного завантажувача
ml_recommender = MusicRecommenderML()
enhanced_loader = EnhancedDataLoader()

# Pydantic моделі
class TrainModelsRequest(BaseModel):
    model_types: Optional[List[str]] = ["content", "collaborative", "hybrid"]
    min_interactions_per_user: int = 5
    include_skips: bool = False
    time_window_days: Optional[int] = None

class RecommendationRequest(BaseModel):
    user_id: int
    model_type: str = "hybrid"
    limit: int = 20

class SingleRecommendation(BaseModel):
    track_id: str
    artist: str = "Unknown"
    predicted_rating: float
    reason: str
    features: Optional[Dict[str, Any]] = {}

class RecommendationResponse(BaseModel):
    success: bool
    message: str
    recommendations: List[SingleRecommendation]
    processing_time: Optional[float] = None
    algorithm_used: Optional[str] = None

class TrainingResponse(BaseModel):
    success: bool
    message: str
    metrics: Optional[Dict[str, Any]] = None
    training_time: Optional[float] = None
    model_version: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    models_trained: bool
    message: str
    database_stats: Optional[Dict[str, Any]] = None

class StatusResponse(BaseModel):
    service_status: str
    version: str
    models_trained: bool
    database_connected: bool
    last_training: Optional[str] = None
    training_data_count: Optional[int] = None

@app.get("/", response_model=HealthResponse)
async def root():
    """Головна сторінка API з розширеною інформацією"""
    try:
        with enhanced_loader:
            stats = enhanced_loader.get_training_data_stats()
        
        return HealthResponse(
            status="healthy",
            version="3.0.0",
            models_trained=ml_recommender.is_trained,
            message="🎵 Enhanced Music Recommender ML Service працює!",
            database_stats=stats
        )
    except Exception as e:
        return HealthResponse(
            status="healthy",
            version="3.0.0", 
            models_trained=ml_recommender.is_trained,
            message="🎵 ML Service працює (БД недоступна)",
            database_stats=None
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Розширена перевірка здоров'я сервісу"""
    try:
        with enhanced_loader:
            stats = enhanced_loader.get_training_data_stats()
        
        return HealthResponse(
            status="healthy",
            version="3.0.0",
            models_trained=ml_recommender.is_trained,
            message="✅ Сервіс та БД працюють нормально",
            database_stats=stats
        )
    except Exception as e:
        logger.warning(f"Database connection issue: {e}")
        return HealthResponse(
            status="degraded",
            version="3.0.0",
            models_trained=ml_recommender.is_trained,
            message="⚠️ Сервіс працює, але БД недоступна"
        )

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Детальний статус сервісу для інтеграції з .NET"""
    try:
        with enhanced_loader:
            stats = enhanced_loader.get_training_data_stats()
            latest_metrics = enhanced_loader.get_latest_model_metrics("Hybrid")
        
        return StatusResponse(
            service_status="online",
            version="3.0.0",
            models_trained=ml_recommender.is_trained,
            database_connected=True,
            last_training=latest_metrics.get("TrainingDate") if latest_metrics else None,
            training_data_count=stats.get("total_interactions", 0)
        )
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return StatusResponse(
            service_status="online",
            version="3.0.0",
            models_trained=ml_recommender.is_trained,
            database_connected=False,
            last_training=None,
            training_data_count=0
        )

@app.post("/train", response_model=TrainingResponse)
async def train_models(request: TrainModelsRequest = TrainModelsRequest()):
    """
    Покращене тренування ML моделей з новою системою даних
    
    🎯 Що тренується:
    - Content-Based: Random Forest на аудіо фічах + контекст + користувацькі фічі
    - Collaborative: KNN на покращеній матриці user-item з рейтингами
    - SVD: TruncatedSVD для матричної факторизації
    - Hybrid: Адаптивна комбінація з врахуванням профілів користувачів
    
    📊 Використовуємо звичайні дані з History, Favorites, UserSongInteractions
    """
    start_time = time.time()
    
    try:
        logger.info("🚀 Початок покращеного тренування ML моделей...")
        
        # Використовуємо звичайний data_loader для отримання даних
        training_data, song_features = ml_recommender.data_loader.prepare_training_data()
        
        if training_data.empty:
            logger.warning("⚠️ Немає даних для тренування! Використовуємо мок-дані...")
            # Створюємо мінімальні тестові дані
            training_data = pd.DataFrame({
                'UserId': [1, 1, 2, 2, 3, 3] * 5,
                'SpotifyTrackId': ['track1', 'track2', 'track3', 'track4', 'track5', 'track6'] * 5,
                'Rating': [5, 4, 3, 5, 2, 4] * 5,
                'Danceability': [0.8, 0.6, 0.4, 0.9, 0.3, 0.7] * 5,
                'Energy': [0.7, 0.5, 0.6, 0.8, 0.4, 0.6] * 5,
                'Valence': [0.9, 0.6, 0.5, 0.8, 0.3, 0.7] * 5,
                'Tempo_norm': [0.7, 0.5, 0.4, 0.8, 0.3, 0.6] * 5,
                'Acousticness': [0.2, 0.4, 0.6, 0.1, 0.8, 0.3] * 5,
                'Instrumentalness': [0.1, 0.0, 0.2, 0.0, 0.5, 0.1] * 5,
                'Speechiness': [0.1, 0.2, 0.1, 0.1, 0.3, 0.2] * 5,
                'Loudness_norm': [0.6, 0.5, 0.4, 0.7, 0.3, 0.5] * 5,
                'Popularity': [80, 60, 40, 90, 30, 70] * 5
            })
            logger.info(f"📊 Створено {len(training_data)} тестових записів")
        
        # Тренування моделей через основний клас
        metrics = ml_recommender.train_models()
        
        training_time = time.time() - start_time
        
        # Збереження метрик в базу даних (якщо можливо)
        try:
            model_version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with enhanced_loader:
                enhanced_loader.save_model_metrics("Hybrid", model_version, metrics)
        except Exception as e:
            logger.warning(f"Не вдалося зберегти метрики: {e}")
        
        logger.info(f"✅ Тренування завершено за {training_time:.2f} секунд")
        
        return TrainingResponse(
            success=True,
            message=f"🎯 Всі ML моделі успішно натреновані! Content + Collaborative + SVD + Hybrid готові",
            metrics=metrics,
            training_time=training_time,
            model_version=f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка тренування: {e}")
        training_time = time.time() - start_time
        
        return TrainingResponse(
            success=False,
            message=f"❌ Помилка тренування: {str(e)}",
            training_time=training_time
        )

@app.post("/recommend")
async def get_recommendations(request: RecommendationRequest):
    """
    🔀 Гібридні рекомендації (Content + Collaborative + SVD)
    
    Комбінація всіх алгоритмів:
    - 40% Content-Based (аудіо схожість)
    - 30% Collaborative KNN (схожі користувачі)  
    - 30% SVD (латентні фактори)
    """
    start_time = time.time()
    
    try:
        if not ml_recommender.is_trained:
            logger.warning("⚠️ Моделі не натреновані, тренуємо автоматично...")
            train_result = await train_models()
            if not train_result.success:
                return RecommendationResponse(
                    success=False,
                    message="❌ Не вдалося натренувати моделі",
                    recommendations=[],
                    processing_time=time.time() - start_time
                )
        
        # Генеруємо гібридні рекомендації
        raw_recommendations = ml_recommender.get_hybrid_recommendations(
            user_id=request.user_id,
            limit=request.limit
        )
        
        # Конвертуємо в потрібний формат
        recommendations = []
        for rec in raw_recommendations:
            recommendations.append(SingleRecommendation(
                track_id=rec['track_id'],
                artist=rec.get('artist', rec.get('Artist', 'Unknown Artist')),  # правильні ключі
                predicted_rating=rec['predicted_rating'],
                reason=rec.get('reason', 'Hybrid recommendation'),
                features={
                    'title': rec.get('title', rec.get('Title', 'Unknown Track')),
                    'artist': rec.get('artist', rec.get('Artist', 'Unknown Artist')),
                    'genre': rec.get('genre', rec.get('Genre', 'Unknown Genre')),
                    'algorithm': rec.get('algorithm', 'Hybrid'),
                    'confidence': rec.get('confidence', 0.5),
                    'methods_used': rec.get('methods_used', [])
                }
            ))
        
        processing_time = time.time() - start_time
        
        return RecommendationResponse(
            success=True,
            message=f"✅ Згенеровано {len(recommendations)} гібридних рекомендацій",
            recommendations=recommendations,
            processing_time=processing_time,
            algorithm_used="Hybrid (Content + KNN + SVD)"
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка генерації рекомендацій: {e}")
        processing_time = time.time() - start_time
        
        return RecommendationResponse(
            success=False,
            message=f"❌ Помилка: {str(e)}",
            recommendations=[],
            processing_time=processing_time
        )

@app.post("/recommend/content")
async def get_content_recommendations(request: RecommendationRequest):
    """
    🎯 Content-Based рекомендації
    
    Рекомендації на основі аудіо характеристик треків:
    - Danceability, Energy, Valence, Tempo
    - Acousticness, Instrumentalness, Speechiness
    - Використовує Random Forest для предикції рейтингу
    """
    start_time = time.time()
    
    try:
        if not ml_recommender.is_trained:
            logger.warning("⚠️ Моделі не натреновані")
            return RecommendationResponse(
                success=False,
                message="❌ Моделі не натреновані. Виконайте /train спочатку",
                recommendations=[],
                processing_time=time.time() - start_time
            )
        
        raw_recommendations = ml_recommender.get_content_recommendations(
            user_id=request.user_id,
            limit=request.limit
        )
        
        # Конвертуємо в потрібний формат
        recommendations = []
        for rec in raw_recommendations:
            recommendations.append(SingleRecommendation(
                track_id=rec['track_id'],
                artist=rec.get('artist', rec.get('Artist', 'Unknown Artist')),
                predicted_rating=rec['predicted_rating'],
                reason=rec.get('reason', 'Content-based recommendation'),
                features={
                    'title': rec.get('title', rec.get('Title', 'Unknown Track')),
                    'artist': rec.get('artist', rec.get('Artist', 'Unknown Artist')),
                    'genre': rec.get('genre', rec.get('Genre', 'Unknown Genre')),
                    'algorithm': rec.get('algorithm', 'Content'),
                    'confidence': rec.get('confidence', 0.5)
                }
            ))
        
        processing_time = time.time() - start_time
        
        return RecommendationResponse(
            success=True,
            message=f"✅ {len(recommendations)} content-based рекомендацій",
            recommendations=recommendations,
            processing_time=processing_time,
            algorithm_used="Content-Based (Random Forest)"
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка content рекомендацій: {e}")
        return RecommendationResponse(
            success=False,
            message=f"❌ Помилка: {str(e)}",
            recommendations=[],
            processing_time=time.time() - start_time
        )

@app.post("/recommend/collaborative") 
async def get_collaborative_recommendations(request: RecommendationRequest):
    """
    👥 KNN Collaborative Filtering рекомендації
    
    Рекомендації на основі схожих користувачів:
    - Знаходить користувачів з схожими смаками
    - Використовує KNN (k-nearest neighbors)
    - Рекомендує треки що подобались схожим користувачам
    """
    start_time = time.time()
    
    try:
        if not ml_recommender.is_trained:
            logger.warning("⚠️ Моделі не натреновані")
            return RecommendationResponse(
                success=False,
                message="❌ Моделі не натреновані. Виконайте /train спочатку",
                recommendations=[],
                processing_time=time.time() - start_time
            )
        
        raw_recommendations = ml_recommender.get_collaborative_recommendations(
            user_id=request.user_id,
            limit=request.limit
        )
        
        # Конвертуємо в потрібний формат
        recommendations = []
        for rec in raw_recommendations:
            recommendations.append(SingleRecommendation(
                track_id=rec['track_id'],
                artist=rec.get('artist', rec.get('Artist', 'Unknown Artist')),
                predicted_rating=rec['predicted_rating'],
                reason=rec.get('reason', 'Collaborative recommendation'),
                features={
                    'title': rec.get('title', rec.get('Title', 'Unknown Track')),
                    'artist': rec.get('artist', rec.get('Artist', 'Unknown Artist')),
                    'genre': rec.get('genre', rec.get('Genre', 'Unknown Genre')),
                    'algorithm': rec.get('algorithm', 'Collaborative'),
                    'confidence': rec.get('confidence', 0.5)
                }
            ))
        
        processing_time = time.time() - start_time
        
        return RecommendationResponse(
            success=True,
            message=f"✅ {len(recommendations)} collaborative рекомендацій",
            recommendations=recommendations,
            processing_time=processing_time,
            algorithm_used="Collaborative KNN"
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка collaborative рекомендацій: {e}")
        return RecommendationResponse(
            success=False,
            message=f"❌ Помилка: {str(e)}",
            recommendations=[],
            processing_time=time.time() - start_time
        )

@app.post("/recommend/svd")
async def get_svd_recommendations(request: RecommendationRequest):
    """
    🔄 SVD Matrix Factorization рекомендації
    
    Рекомендації через матричну факторизацію:
    - TruncatedSVD для розкладу user-item матриці
    - Знаходить латентні фактори в даних
    - Рекомендує на основі схожості в латентному просторі
    """
    start_time = time.time()
    
    try:
        if not ml_recommender.is_trained:
            logger.warning("⚠️ Моделі не натреновані")
            return RecommendationResponse(
                success=False,
                message="❌ Моделі не натреновані. Виконайте /train спочатку",
                recommendations=[],
                processing_time=time.time() - start_time
            )
        
        raw_recommendations = ml_recommender.get_svd_recommendations(
            user_id=request.user_id,
            limit=request.limit
        )
        
        # Конвертуємо в потрібний формат
        recommendations = []
        for rec in raw_recommendations:
            recommendations.append(SingleRecommendation(
                track_id=rec['track_id'],
                artist=rec.get('artist', rec.get('Artist', 'Unknown Artist')),
                predicted_rating=rec['predicted_rating'],
                reason=rec.get('reason', 'SVD recommendation'),
                features={
                    'title': rec.get('title', rec.get('Title', 'Unknown Track')),
                    'artist': rec.get('artist', rec.get('Artist', 'Unknown Artist')),
                    'genre': rec.get('genre', rec.get('Genre', 'Unknown Genre')),
                    'algorithm': rec.get('algorithm', 'SVD'),
                    'confidence': rec.get('confidence', 0.5),
                    'latent_similarity': rec.get('latent_similarity', 0.0)
                }
            ))
        
        processing_time = time.time() - start_time
        
        return RecommendationResponse(
            success=True,
            message=f"✅ {len(recommendations)} SVD рекомендацій",
            recommendations=recommendations,
            processing_time=processing_time,
            algorithm_used="SVD Matrix Factorization"
        )
        
    except Exception as e:
        logger.error(f"❌ Помилка SVD рекомендацій: {e}")
        return RecommendationResponse(
            success=False,
            message=f"❌ Помилка: {str(e)}",
            recommendations=[],
            processing_time=time.time() - start_time
        )

@app.get("/models/info")
async def get_models_info():
    """Інформація про натреновані моделі"""
    try:
        with enhanced_loader:
            content_metrics = enhanced_loader.get_latest_model_metrics("Content")
            collaborative_metrics = enhanced_loader.get_latest_model_metrics("Collaborative") 
            hybrid_metrics = enhanced_loader.get_latest_model_metrics("Hybrid")
            
            return {
                "models_trained": ml_recommender.is_trained,
                "content_based": {
                    "available": content_metrics is not None,
                    "last_training": content_metrics.get("TrainingDate") if content_metrics else None,
                    "mae": content_metrics.get("MAE") if content_metrics else None
                },
                "collaborative": {
                    "available": collaborative_metrics is not None,
                    "last_training": collaborative_metrics.get("TrainingDate") if collaborative_metrics else None,
                    "sparsity": collaborative_metrics.get("collaborative_sparsity") if collaborative_metrics else None
                },
                "hybrid": {
                    "available": hybrid_metrics is not None,
                    "last_training": hybrid_metrics.get("TrainingDate") if hybrid_metrics else None,
                    "total_samples": hybrid_metrics.get("TrainingSamples") if hybrid_metrics else None
                }
            }
    except Exception as e:
        logger.error(f"Error getting models info: {e}")
        return {
            "models_trained": ml_recommender.is_trained,
            "error": str(e)
        }

@app.get("/data/stats")
async def get_data_stats():
    """Статистика тренувальних даних"""
    try:
        with enhanced_loader:
            stats = enhanced_loader.get_training_data_stats()
            return {
                "success": True,
                "stats": stats
            }
    except Exception as e:
        logger.error(f"Error getting data stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Запуск Enhanced Music Recommender ML Service...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 