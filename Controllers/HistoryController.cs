using Microsoft.AspNetCore.Mvc;
using MusicRecommender.Models;
using System;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using System.Collections.Generic;
using System.Linq;

namespace MusicRecommender.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class HistoryController : ControllerBase
    {
        private readonly ApplicationDbContext _context;
        private readonly ILogger<HistoryController> _logger;

        public HistoryController(ApplicationDbContext context, ILogger<HistoryController> logger)
        {
            _context = context;
            _logger = logger;
        }

        [HttpPost("add")]
        public async Task<IActionResult> AddToHistory([FromBody] Song song)
        {
            try
            {
                if (song == null || string.IsNullOrEmpty(song.SpotifyTrackId))
                {
                    return BadRequest("Invalid song data");
                }

                // Отримуємо ID користувача з сесії
                var userId = HttpContext.Session.GetInt32("UserId");
                if (!userId.HasValue)
                {
                    return Unauthorized("User not logged in");
                }

                _logger.LogInformation("Adding song to history for user {UserId}: {TrackId}", userId.Value, song.SpotifyTrackId);

                // Перевіряємо чи є такий трек в історії цього користувача
                var existingSong = await _context.History
                    .FirstOrDefaultAsync(s => s.SpotifyTrackId == song.SpotifyTrackId && s.UserId == userId.Value);

                if (existingSong != null)
                {
                    _logger.LogInformation("Updating existing song in history: {TrackId}", song.SpotifyTrackId);
                    existingSong.ListenedAt = DateTime.UtcNow;
                    existingSong.Title = song.Title;
                    existingSong.Artist = song.Artist;
                    existingSong.ImageUrl = song.ImageUrl;
                    _context.History.Update(existingSong);
                }
                else
                {
                    _logger.LogInformation("Adding new song to history: {TrackId}", song.SpotifyTrackId);
                    song.ListenedAt = DateTime.UtcNow;
                    song.UserId = userId.Value; // Прив'язуємо до користувача
                    await _context.History.AddAsync(song);
                }

                await _context.SaveChangesAsync();
                _logger.LogInformation("Successfully saved to history for user {UserId}", userId.Value);
                return Ok(new { message = "Successfully saved to history" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error saving song to history: {TrackId}", song?.SpotifyTrackId);
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpGet]
        public async Task<IActionResult> GetHistory()
        {
            try
            {
                // Отримуємо ID користувача з сесії
                var userId = HttpContext.Session.GetInt32("UserId");
                if (!userId.HasValue)
                {
                    return Ok(new List<Song>()); // Повертаємо порожню історію для неавторизованих
                }

                _logger.LogInformation("Fetching history for user {UserId}", userId.Value);
                var history = await _context.History
                    .Where(h => h.UserId == userId.Value)
                    .OrderByDescending(s => s.ListenedAt)
                    .Take(50)
                    .ToListAsync();

                _logger.LogInformation("Retrieved {Count} items from history for user {UserId}", history.Count, userId.Value);
                return Ok(history);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving history");
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteFromHistory(string id)
        {
            try
            {
                _logger.LogInformation("Attempting to delete song from history: {TrackId}", id);

                var song = await _context.History
                    .FirstOrDefaultAsync(s => s.SpotifyTrackId == id);

                if (song == null)
                {
                    _logger.LogWarning("Song not found in history: {TrackId}", id);
                    return NotFound();
                }

                _context.History.Remove(song);
                await _context.SaveChangesAsync();

                _logger.LogInformation("Successfully deleted song from history: {TrackId}", id);
                return Ok(new { message = "Successfully deleted from history" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting song from history: {TrackId}", id);
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
} 