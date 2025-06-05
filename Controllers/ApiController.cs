using Microsoft.AspNetCore.Mvc;
using System;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using MusicRecommender.Services;

namespace MusicRecommender.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class MusicController : ControllerBase
    {
        private readonly ISpotifyService _spotifyService;
        private readonly ILogger<MusicController> _logger;

        public MusicController(ISpotifyService spotifyService, ILogger<MusicController> logger)
        {
            _spotifyService = spotifyService;
            _logger = logger;
        }

        [HttpGet("search")]
        public async Task<IActionResult> SearchMusic([FromQuery] string query)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(query))
                {
                    return Ok(new { success = false, message = "Пошуковий запит не може бути порожнім" });
                }

                var searchResults = await _spotifyService.GetSearchResultsAsync(query);
                
                return Ok(new 
                { 
                    success = true, 
                    data = searchResults,
                    message = "Пошук виконано успішно"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error searching music for query: {Query}", query);
                return Ok(new 
                { 
                    success = false, 
                    message = "Помилка пошуку музики" 
                });
            }
        }
    }
} 