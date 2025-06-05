using Microsoft.AspNetCore.Mvc;
using MusicRecommender.Models;
using MusicRecommender.Services;
using Microsoft.EntityFrameworkCore;

namespace MusicRecommender.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly IRecommendationService _recommendationService;
        private readonly ILogger<AuthController> _logger;

        public AuthController(
            ApplicationDbContext context,
            IRecommendationService recommendationService,
            ILogger<AuthController> logger)
        {
            _context = context;
            _recommendationService = recommendationService;
            _logger = logger;
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginRequest request)
        {
            try
            {
                if (string.IsNullOrEmpty(request.UserName))
                {
                    return BadRequest(new { success = false, message = "UserName is required" });
                }

                // Шукаємо існуючого користувача
                var existingUser = await _context.Users
                    .FirstOrDefaultAsync(u => u.UserName == request.UserName);
                
                int userId;
                
                if (existingUser != null)
                {
                    userId = existingUser.UserId;
                }
                else
                {
                    // Створюємо нового користувача
                    var newUser = new User
                    {
                        UserName = request.UserName,
                        Email = request.Email ?? "",
                        CreatedAt = DateTime.UtcNow
                    };
                    
                    _context.Users.Add(newUser);
                    await _context.SaveChangesAsync();
                    userId = newUser.UserId;
                    
                    _logger.LogInformation($"Created new user: {request.UserName} with ID: {userId}");
                }
                
                if (userId <= 0)
                {
                    return BadRequest(new { success = false, message = "Error creating/getting user" });
                }

                // Зберігаємо ID користувача в сесії
                HttpContext.Session.SetInt32("UserId", userId);
                HttpContext.Session.SetString("UserName", request.UserName);

                _logger.LogInformation($"User {request.UserName} logged in with ID {userId}");

                return Ok(new
                {
                    success = true,
                    userId = userId,
                    userName = request.UserName,
                    message = "Successfully logged in"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error during login for user {request.UserName}");
                return StatusCode(500, new { success = false, message = "Internal server error" });
            }
        }

        [HttpPost("logout")]
        public IActionResult Logout()
        {
            try
            {
                var userName = HttpContext.Session.GetString("UserName");
                HttpContext.Session.Clear();
                
                _logger.LogInformation($"User {userName} logged out");

                return Ok(new { success = true, message = "Successfully logged out" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during logout");
                return StatusCode(500, new { success = false, message = "Internal server error" });
            }
        }

        [HttpGet("current")]
        public IActionResult GetCurrentUser()
        {
            try
            {
                var userId = HttpContext.Session.GetInt32("UserId");
                var userName = HttpContext.Session.GetString("UserName");

                if (userId.HasValue && !string.IsNullOrEmpty(userName))
                {
                    return Ok(new
                    {
                        success = true,
                        isLoggedIn = true,
                        userId = userId.Value,
                        userName = userName
                    });
                }

                return Ok(new
                {
                    success = true,
                    isLoggedIn = false,
                    userId = (int?)null,
                    userName = (string?)null
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting current user");
                return StatusCode(500, new { success = false, message = "Internal server error" });
            }
        }
    }

    public class LoginRequest
    {
        public string UserName { get; set; } = string.Empty;
        public string? Email { get; set; }
    }
} 