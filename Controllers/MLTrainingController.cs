using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MusicRecommender.Models;
using MusicRecommender.Services;
using System.Diagnostics;
using System.Text.Json;
using System.Text;

namespace MusicRecommender.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class MLTrainingController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly MLDataCollectionService _dataCollectionService;
        private readonly ILogger<MLTrainingController> _logger;

        public MLTrainingController(
            ApplicationDbContext context,
            MLDataCollectionService dataCollectionService,
            ILogger<MLTrainingController> logger)
        {
            _context = context;
            _dataCollectionService = dataCollectionService;
            _logger = logger;
        }

        /// <summary>
        /// Збір нових тренувальних даних з користувацьких взаємодій
        /// </summary>
        [HttpPost("collect-training-data")]
        public async Task<IActionResult> CollectTrainingData()
        {
            try
            {
                _logger.LogInformation("🔄 Запуск збору тренувальних даних...");
                
                var processedCount = await _dataCollectionService.CollectTrainingDataAsync();
                
                return Ok(new
                {
                    success = true,
                    message = $"Оброблено {processedCount} нових взаємодій",
                    processedCount = processedCount,
                    timestamp = DateTime.UtcNow
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Помилка при зборі тренувальних даних");
                return StatusCode(500, new
                {
                    success = false,
                    message = "Помилка при зборі тренувальних даних",
                    error = ex.Message
                });
            }
        }

        /// <summary>
        /// Створення/оновлення ML профілю користувача
        /// </summary>
        [HttpPost("user-profile/{userId}")]
        public async Task<IActionResult> UpdateUserProfile(int userId)
        {
            try
            {
                var profile = await _dataCollectionService.CreateOrUpdateUserProfileAsync(userId);
                
                return Ok(new
                {
                    success = true,
                    message = $"Профіль користувача {userId} оновлено",
                    profile = new
                    {
                        userId = profile.UserId,
                        totalInteractions = profile.TotalInteractions,
                        lastUpdated = profile.LastUpdated,
                        preferences = new
                        {
                            danceability = profile.PreferredDanceability,
                            energy = profile.PreferredEnergy,
                            valence = profile.PreferredValence,
                            tempo = profile.PreferredTempo
                        },
                        behavioral = new
                        {
                            skipRate = profile.SkipRate,
                            repeatRate = profile.RepeatRate,
                            explorationRate = profile.ExplorationRate
                        },
                        diversity = new
                        {
                            genreDiversity = profile.GenreDiversity,
                            artistDiversity = profile.ArtistDiversity
                        }
                    }
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Помилка при оновленні профілю користувача {UserId}", userId);
                return StatusCode(500, new
                {
                    success = false,
                    message = $"Помилка при оновленні профілю користувача {userId}",
                    error = ex.Message
                });
            }
        }

        /// <summary>
        /// Запуск тренування ML моделей через Python сервіс
        /// </summary>
        [HttpPost("train-models")]
        public async Task<IActionResult> TrainModels([FromBody] TrainModelsRequest? request = null)
        {
            try
            {
                _logger.LogInformation("🎯 Запуск тренування ML моделей...");

                // Спочатку збираємо свіжі тренувальні дані
                await _dataCollectionService.CollectTrainingDataAsync();

                // Викликаємо Python ML сервіс
                var result = await CallPythonMLService("train", request);

                if (result.Success)
                {
                    // Зберігаємо метрики в БД (якщо є)
                    await SaveTrainingMetrics(result.Data);
                }

                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Помилка при тренуванні моделей");
                return StatusCode(500, new
                {
                    success = false,
                    message = "Помилка при тренуванні моделей",
                    error = ex.Message
                });
            }
        }

        /// <summary>
        /// Отримання рекомендацій через навчені моделі
        /// </summary>
        [HttpGet("recommendations/{userId}")]
        public async Task<IActionResult> GetMLRecommendations(int userId, 
            [FromQuery] string modelType = "hybrid", 
            [FromQuery] int limit = 20)
        {
            try
            {
                var request = new
                {
                    user_id = userId,
                    model_type = modelType,
                    limit = limit
                };

                var result = await CallPythonMLService("recommend", request);
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Помилка при отриманні ML рекомендацій для користувача {UserId}", userId);
                return StatusCode(500, new
                {
                    success = false,
                    message = $"Помилка при отриманні рекомендацій для користувача {userId}",
                    error = ex.Message
                });
            }
        }

        /// <summary>
        /// Статистика тренувальних даних
        /// </summary>
        [HttpGet("training-data/stats")]
        public async Task<IActionResult> GetTrainingDataStats()
        {
            try
            {
                var stats = new
                {
                    // Загальна статистика MLTrainingData
                    totalTrainingRecords = await _context.MLTrainingData.CountAsync(),
                    uniqueUsers = await _context.MLTrainingData.Select(m => m.UserId).Distinct().CountAsync(),
                    uniqueTracks = await _context.MLTrainingData.Select(m => m.SpotifyTrackId).Distinct().CountAsync(),
                    
                    // Статистика по типах взаємодій
                    interactionTypes = await _context.MLTrainingData
                        .GroupBy(m => m.InteractionType)
                        .Select(g => new { type = g.Key, count = g.Count() })
                        .ToListAsync(),
                    
                    // Статистика по рейтингах
                    ratingStats = await _context.MLTrainingData
                        .GroupBy(m => new { })
                        .Select(g => new
                        {
                            avgRating = g.Average(x => x.Rating),
                            minRating = g.Min(x => x.Rating),
                            maxRating = g.Max(x => x.Rating)
                        })
                        .FirstOrDefaultAsync(),
                    
                    // Користувацькі профілі
                    userProfiles = await _context.MLUserProfiles.CountAsync(),
                    
                    // Останні тренування моделей
                    recentTrainings = await _context.MLModelMetrics
                        .OrderByDescending(m => m.TrainingDate)
                        .Take(5)
                        .Select(m => new
                        {
                            modelType = m.ModelType,
                            version = m.ModelVersion,
                            trainingDate = m.TrainingDate,
                            mae = m.MAE,
                            mse = m.MSE,
                            trainingSamples = m.TrainingSamples
                        })
                        .ToListAsync(),
                    
                    // Статистика за останній тиждень
                    weeklyStats = await GetWeeklyStats()
                };

                return Ok(stats);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Помилка при отриманні статистики");
                return StatusCode(500, new
                {
                    success = false,
                    message = "Помилка при отриманні статистики",
                    error = ex.Message
                });
            }
        }

        /// <summary>
        /// Очищення старих тренувальних даних
        /// </summary>
        [HttpDelete("training-data/cleanup")]
        public async Task<IActionResult> CleanupOldTrainingData([FromQuery] int maxAgeDays = 365)
        {
            try
            {
                var maxAge = TimeSpan.FromDays(maxAgeDays);
                var deletedCount = await _dataCollectionService.CleanupOldTrainingDataAsync(maxAge);

                return Ok(new
                {
                    success = true,
                    message = $"Видалено {deletedCount} старих записів",
                    deletedCount = deletedCount,
                    maxAgeDays = maxAgeDays
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Помилка при очищенні старих даних");
                return StatusCode(500, new
                {
                    success = false,
                    message = "Помилка при очищенні старих даних",
                    error = ex.Message
                });
            }
        }

        /// <summary>
        /// Статус ML сервісу
        /// </summary>
        [HttpGet("service/status")]
        public async Task<IActionResult> GetMLServiceStatus()
        {
            try
            {
                var result = await CallPythonMLService("status", null);
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "⚠️ ML сервіс недоступний");
                return Ok(new
                {
                    success = false,
                    message = "ML сервіс недоступний",
                    error = ex.Message,
                    isOnline = false
                });
            }
        }

        #region Private Methods

        /// <summary>
        /// Виклик Python ML сервісу
        /// </summary>
        private async Task<dynamic> CallPythonMLService(string endpoint, object? data)
        {
            using var httpClient = new HttpClient();
            httpClient.Timeout = TimeSpan.FromMinutes(10); // Довгий таймаут для тренування
            
            var mlServiceUrl = "http://localhost:8000"; // Можна винести в конфігурацію
            var url = $"{mlServiceUrl}/{endpoint}";

            HttpResponseMessage response;
            
            if (data != null)
            {
                var json = JsonSerializer.Serialize(data);
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                response = await httpClient.PostAsync(url, content);
            }
            else
            {
                response = await httpClient.GetAsync(url);
            }

            var responseContent = await response.Content.ReadAsStringAsync();
            
            if (response.IsSuccessStatusCode)
            {
                return new
                {
                    Success = true,
                    Data = JsonSerializer.Deserialize<object>(responseContent),
                    StatusCode = (int)response.StatusCode
                };
            }
            else
            {
                return new
                {
                    Success = false,
                    Message = $"ML сервіс повернув помилку: {response.StatusCode}",
                    Data = responseContent,
                    StatusCode = (int)response.StatusCode
                };
            }
        }

        /// <summary>
        /// Збереження метрик тренування в БД
        /// </summary>
        private async Task SaveTrainingMetrics(object? metricsData)
        {
            if (metricsData == null) return;

            try
            {
                // Тут можна парсити метрики і зберігати в MLModelMetrics
                var metricsJson = JsonSerializer.Serialize(metricsData);
                _logger.LogInformation("📊 Метрики тренування: {Metrics}", metricsJson);
                
                // TODO: Реалізувати парсинг і збереження метрик
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "⚠️ Не вдалося зберегти метрики тренування");
            }
        }

        /// <summary>
        /// Статистика за останній тиждень
        /// </summary>
        private async Task<object> GetWeeklyStats()
        {
            var weekAgo = DateTime.UtcNow.AddDays(-7);
            
            return new
            {
                newTrainingRecords = await _context.MLTrainingData
                    .Where(m => m.Timestamp >= weekAgo)
                    .CountAsync(),
                    
                newUserProfiles = await _context.MLUserProfiles
                    .Where(p => p.LastUpdated >= weekAgo)
                    .CountAsync(),
                    
                modelTrainings = await _context.MLModelMetrics
                    .Where(m => m.TrainingDate >= weekAgo)
                    .CountAsync()
            };
        }

        #endregion
    }

    /// <summary>
    /// Запит для тренування моделей
    /// </summary>
    public class TrainModelsRequest
    {
        public string[]? ModelTypes { get; set; } // ["content", "collaborative", "hybrid"]
        public int? MinInteractionsPerUser { get; set; } = 5;
        public bool? IncludeSkips { get; set; } = false;
        public int? TimeWindowDays { get; set; } = null;
        public Dictionary<string, object>? Parameters { get; set; }
    }
} 