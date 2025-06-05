using Microsoft.AspNetCore.Mvc;
using MusicRecommender.Models;
using MusicRecommender.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using Microsoft.Extensions.Configuration;
using Microsoft.EntityFrameworkCore;

namespace MusicRecommender.Controllers
{
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger;
        private readonly ISpotifyService _spotify;
        private readonly IRecommendationService _recommendations;
        private readonly IConfiguration _configuration;
        private readonly ApplicationDbContext _context;

        public HomeController(
            ILogger<HomeController> logger,
            ISpotifyService spotify,
            IRecommendationService recommendations,
            IConfiguration configuration,
            ApplicationDbContext context)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            _spotify = spotify ?? throw new ArgumentNullException(nameof(spotify));
            _recommendations = recommendations ?? throw new ArgumentNullException(nameof(recommendations));
            _configuration = configuration;
            _context = context;
        }

        public IActionResult Index()
        {
            ViewBag.SpotifyClientId = _configuration["Spotify:ClientId"];
            return View();
        }

        public async Task<IActionResult> History()
        {
            try
            {
                // Отримуємо ID користувача з сесії
                var userId = HttpContext.Session.GetInt32("UserId");
                
                var history = await _context.History
                    .Where(h => userId.HasValue ? h.UserId == userId.Value : h.UserId == null) // Показуємо історію поточного користувача або загальну
                    .OrderByDescending(s => s.ListenedAt)
                    .Take(50)
                    .ToListAsync();

                return View(history);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error loading history");
                return View(new List<Song>());
            }
        }

        public async Task<IActionResult> Favorites()
        {
            try
            {
                // Отримуємо ID користувача з сесії
                var userId = HttpContext.Session.GetInt32("UserId");
                
                if (!userId.HasValue)
                {
                    // Якщо користувач не авторизований, показуємо порожню сторінку
                    return View(new List<Favorite>());
                }

                var favorites = await _context.Favorites
                    .Where(f => f.UserId == userId.Value)
                    .OrderByDescending(f => f.AddedToFavoritesAt)
                    .ToListAsync();

                return View(favorites);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error loading favorites");
                return View(new List<Favorite>());
            }
        }

        [HttpGet]
        public async Task<JsonResult> Autocomplete(string q)
        {
            if (string.IsNullOrEmpty(q))
            {
                return Json(new { artists = new object[] { }, songs = new object[] { } });
            }

            var results = await _spotify.GetSearchResultsAsync(q);
            return Json(results);
        }

        [HttpGet]
        public async Task<IActionResult> Artist(string name)
        {
            if (string.IsNullOrEmpty(name))
            {
                return RedirectToAction("Index");
            }

            var songs = await _spotify.SearchSongsAsync(name);
            ViewBag.ArtistName = name;
            return View(songs);
        }

        [HttpGet]
        public async Task<JsonResult> GetArtistTracks(string artistId)
        {
            try
            {
                if (string.IsNullOrEmpty(artistId))
        {
                    return Json(new object[] { });
                }

                var tracks = await _spotify.GetArtistTopTracksAsync(artistId);
                return Json(tracks);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting tracks for artist {ArtistId}", artistId);
                return Json(new object[] { });
            }
        }

        [HttpGet]
        public async Task<IActionResult> Recommend(string artistName)
        {
            try
            {
                var recommendations = await _recommendations.GetRecommendationsAsync(artistName);
                ViewBag.ArtistName = artistName;
                return View("Recommend", recommendations);
        }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting recommendations for artist {ArtistName}", artistName);
                return RedirectToAction(nameof(Index));
            }
        }

        [HttpGet]
        public async Task<IActionResult> SimpleRecommendations()
        {
            try
            {
                var recommendations = await _recommendations.GetSimpleRecommendationsAsync();
                ViewBag.PageTitle = "Рекомендації для вас";
                ViewBag.Description = "На основі вашої історії прослуховувань";
                return View("Recommend", recommendations);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting simple recommendations");
                ViewBag.PageTitle = "Рекомендації";
                ViewBag.Description = "Виникла помилка при завантаженні рекомендацій";
                return View("Recommend", new List<Song>());
            }
        }

        [HttpGet]
        public IActionResult PythonML()
        {
            ViewBag.PageTitle = "Python ML Рекомендації";
            ViewBag.Description = "Порівняння алгоритмів машинного навчання: KNN vs SVD";
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
