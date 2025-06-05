using Microsoft.AspNetCore.Mvc;
using MusicRecommender.Models;
using MusicRecommender.Services;
using Microsoft.EntityFrameworkCore;
using System.Text.Json;

namespace MusicRecommender.Controllers
{
    public class MLController : Controller
    {
        private readonly ApplicationDbContext _context;
        private readonly ILogger<MLController> _logger;
        private readonly HttpClient _httpClient;
        private readonly IConfiguration _configuration;

        public MLController(
            ApplicationDbContext context,
            ILogger<MLController> logger,
            HttpClient httpClient,
            IConfiguration configuration)
        {
            _context = context;
            _logger = logger;
            _httpClient = httpClient;
            _configuration = configuration;
        }

        /// <summary>
        /// Сторінка ML рекомендацій
        /// </summary>
        public IActionResult Index()
        {
            return View();
        }

        /// <summary>
        /// Перевірка статусу Python ML сервісу
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> CheckMLServiceStatus()
        {
            try
            {
                var mlServiceUrl = _configuration.GetValue<string>("MLService:BaseUrl", "http://localhost:8000");
                var response = await _httpClient.GetAsync($"{mlServiceUrl}/health");
                
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    return Json(new { success = true, status = "online", data = content });
                }
                else
                {
                    return Json(new { success = false, status = "offline", message = "ML сервіс недоступний" });
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking ML service status");
                return Json(new { success = false, status = "error", message = "Помилка підключення до ML сервісу" });
            }
        }

        /// <summary>
        /// Отримати ML рекомендації для користувача
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> GetMLRecommendations([FromBody] MLRecommendationRequest request)
        {
            try
            {
                var userId = HttpContext.Session.GetInt32("UserId");
                if (!userId.HasValue)
                {
                    // Для тестування використовуємо першого доступного користувача
                    var testUser = await _context.Users.FirstOrDefaultAsync();
                    if (testUser != null)
                    {
                        userId = testUser.UserId;
                        _logger.LogInformation($"Using test user ID {userId} for ML recommendations");
                    }
                    else
                    {
                        return Json(new { success = false, message = "Немає користувачів у системі для тестування ML" });
                    }
                }

                var mlServiceUrl = _configuration.GetValue<string>("MLService:BaseUrl", "http://localhost:8000");
                
                // Підготовляємо дані для ML сервісу
                var mlRequest = new
                {
                    user_id = userId.Value,
                    algorithm = request.Algorithm ?? "hybrid",
                    n_recommendations = request.NumberOfRecommendations ?? 10
                };

                var jsonContent = JsonSerializer.Serialize(mlRequest);
                var httpContent = new StringContent(jsonContent, System.Text.Encoding.UTF8, "application/json");
                
                var response = await _httpClient.PostAsync($"{mlServiceUrl}/recommend", httpContent);
                
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    var mlResponse = JsonSerializer.Deserialize<MLRecommendationResponse>(content);
                    
                    return Json(new 
                    { 
                        success = true, 
                        data = mlResponse,
                        message = $"Отримано {mlResponse?.recommendations?.Count ?? 0} рекомендацій з ML сервісу (користувач ID: {userId})"
                    });
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("ML service error: {Error}", errorContent);
                    return Json(new { success = false, message = "Помилка отримання рекомендацій з ML сервісу" });
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting ML recommendations");
                return Json(new { success = false, message = "Помилка отримання ML рекомендацій: " + ex.Message });
            }
        }

        /// <summary>
        /// Тренування ML моделей
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> TrainModels()
        {
            try
            {
                var mlServiceUrl = _configuration.GetValue<string>("MLService:BaseUrl", "http://localhost:8000");
                var response = await _httpClient.PostAsync($"{mlServiceUrl}/train", new StringContent(""));
                
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    return Json(new { success = true, data = content, message = "Тренування ML моделей завершено успішно" });
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("ML training error: {Error}", errorContent);
                    return Json(new { success = false, message = "Помилка тренування ML моделей" });
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error training ML models");
                return Json(new { success = false, message = "Помилка тренування ML моделей: " + ex.Message });
            }
        }

        /// <summary>
        /// Статистика ML системи
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> GetMLStats()
        {
            try
            {
                var stats = new
                {
                    Users = await _context.Users.CountAsync(),
                    Interactions = await _context.UserSongInteractions.CountAsync(),
                    SongFeatures = await _context.SongFeatures.CountAsync(),
                    History = await _context.History.CountAsync(),
                    Favorites = await _context.Favorites.CountAsync(),
                    LastTraining = "Не тренувалася", // TODO: додати дату останнього тренування
                    MLServiceStatus = "Перевіряється..."
                };

                return Json(new { success = true, data = stats });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting ML stats");
                return Json(new { success = false, message = "Помилка отримання статистики ML" });
            }
        }
    }

    // Модель запиту для ML рекомендацій
    public class MLRecommendationRequest
    {
        public string? Algorithm { get; set; } = "hybrid";
        public int? NumberOfRecommendations { get; set; } = 10;
    }

    // Модель відповіді від ML сервісу
    public class MLRecommendationResponse
    {
        public List<MLRecommendation>? recommendations { get; set; }
        public string? algorithm_used { get; set; }
        public double? execution_time { get; set; }
        public string? message { get; set; }
    }

    public class MLRecommendation
    {
        public string? track_id { get; set; }
        public string? title { get; set; }
        public string? artist { get; set; }
        public double? confidence_score { get; set; }
        public string? algorithm { get; set; }
    }
} 