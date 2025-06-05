using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using MusicRecommender.Models;
using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using System.Linq;

namespace MusicRecommender.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class FavoritesController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly ILogger<FavoritesController> _logger;

        public FavoritesController(ApplicationDbContext context, ILogger<FavoritesController> logger)
        {
            _context = context;
            _logger = logger;
        }

        [HttpPost("add")]
        public async Task<IActionResult> AddToFavorites([FromBody] AddToFavoritesRequest request)
        {
            try
            {
                // Отримуємо ID користувача з сесії
                var userId = HttpContext.Session.GetInt32("UserId");
                if (!userId.HasValue)
                {
                    return Unauthorized(new { success = false, message = "User not logged in" });
                }

                if (string.IsNullOrEmpty(request.SpotifyTrackId))
                {
                    return BadRequest(new { success = false, message = "SpotifyTrackId is required" });
                }

                // Перевіряємо чи трек вже в улюблених у цього користувача
                var existingFavorite = await _context.Favorites
                    .FirstOrDefaultAsync(f => f.SpotifyTrackId == request.SpotifyTrackId && f.UserId == userId.Value);

                if (existingFavorite != null)
                {
                    return Ok(new { success = true, message = "Track is already in favorites" });
                }

                var favorite = new Favorite
                {
                    SpotifyTrackId = request.SpotifyTrackId,
                    Title = request.Title ?? "",
                    Artist = request.Artist ?? "",
                    ImageUrl = request.ImageUrl,
                    AddedToFavoritesAt = DateTime.UtcNow,
                    UserId = userId.Value
                };

                _context.Favorites.Add(favorite);
                await _context.SaveChangesAsync();

                _logger.LogInformation("Added track {TrackId} to favorites for user {UserId}", request.SpotifyTrackId, userId.Value);

                return Ok(new { success = true, message = "Successfully added to favorites" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error adding track to favorites");
                return StatusCode(500, new { success = false, message = "Internal server error" });
            }
        }

        [HttpDelete("remove/{spotifyTrackId}")]
        public async Task<IActionResult> RemoveFromFavorites(string spotifyTrackId)
        {
            try
            {
                // Отримуємо ID користувача з сесії
                var userId = HttpContext.Session.GetInt32("UserId");
                if (!userId.HasValue)
                {
                    return Unauthorized(new { success = false, message = "User not logged in" });
                }

                var favorite = await _context.Favorites
                    .FirstOrDefaultAsync(f => f.SpotifyTrackId == spotifyTrackId && f.UserId == userId.Value);

                if (favorite == null)
                {
                    return NotFound(new { success = false, message = "Favorite not found" });
                }

                _context.Favorites.Remove(favorite);
                await _context.SaveChangesAsync();

                _logger.LogInformation("Removed track {TrackId} from favorites for user {UserId}", spotifyTrackId, userId.Value);

                return Ok(new { success = true, message = "Successfully removed from favorites" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error removing track from favorites");
                return StatusCode(500, new { success = false, message = "Internal server error" });
            }
        }

        [HttpGet("check/{spotifyTrackId}")]
        public async Task<IActionResult> CheckFavorite(string spotifyTrackId)
        {
            try
            {
                // Отримуємо ID користувача з сесії
                var userId = HttpContext.Session.GetInt32("UserId");
                if (!userId.HasValue)
                {
                    return Ok(new { success = true, isFavorite = false });
                }

                var favorite = await _context.Favorites
                    .AnyAsync(f => f.SpotifyTrackId == spotifyTrackId && f.UserId == userId.Value);

                return Ok(new { success = true, isFavorite = favorite });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking favorite status");
                return StatusCode(500, new { success = false, message = "Internal server error" });
            }
        }

        [HttpGet]
        public async Task<IActionResult> GetFavorites()
        {
            try
            {
                // Отримуємо ID користувача з сесії
                var userId = HttpContext.Session.GetInt32("UserId");
                if (!userId.HasValue)
                {
                    return Ok(new { success = true, data = new object[] { } });
                }

                var favorites = await _context.Favorites
                    .Where(f => f.UserId == userId.Value)
                    .OrderByDescending(f => f.AddedToFavoritesAt)
                    .ToListAsync();

                return Ok(new { success = true, data = favorites });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting favorites");
                return StatusCode(500, new { success = false, message = "Internal server error" });
            }
        }
    }

    public class AddToFavoritesRequest
    {
        public string SpotifyTrackId { get; set; } = string.Empty;
        public string? Title { get; set; }
        public string? Artist { get; set; }
        public string? ImageUrl { get; set; }
    }
} 