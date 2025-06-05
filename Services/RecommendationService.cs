using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MusicRecommender.Models;
using Microsoft.Extensions.Logging;
using Microsoft.EntityFrameworkCore;

namespace MusicRecommender.Services
{
    public class RecommendationService : IRecommendationService
    {
        private readonly ISpotifyService _spotify;
        private readonly ILogger<RecommendationService> _logger;
        private readonly ApplicationDbContext _context;
        private const int MAX_SEED_TRACKS = 2;
        private const int MAX_SEED_ARTISTS = 2;
        private readonly Random _random = new Random();

        public RecommendationService(
            ISpotifyService spotify, 
            ILogger<RecommendationService> logger,
            ApplicationDbContext context)
        {
            _spotify = spotify ?? throw new ArgumentNullException(nameof(spotify));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            _context = context ?? throw new ArgumentNullException(nameof(context));
        }

        private async Task<List<Song>> GetSeedTracksAsync()
        {
            try
            {
                // Get tracks from history
                var historyTracks = await _context.History
                    .OrderByDescending(s => s.ListenedAt)
                    .Take(5)
                    .ToListAsync();

                // Get tracks from favorites
                var favoriteTracks = await _context.Favorites
                    .OrderByDescending(f => f.AddedToFavoritesAt)
                    .Take(5)
                    .Select(f => new Song
                    {
                        SpotifyTrackId = f.SpotifyTrackId,
                        Title = f.Title,
                        Artist = f.Artist,
                        ImageUrl = f.ImageUrl ?? string.Empty,
                        ListenedAt = null,
                        AddedToFavoritesAt = f.AddedToFavoritesAt
                    })
                    .ToListAsync();

                // Combine and shuffle tracks
                var allTracks = historyTracks.Concat(favoriteTracks).ToList();
                return allTracks.OrderBy(x => _random.Next()).Take(MAX_SEED_TRACKS).ToList();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting seed tracks");
                return new List<Song>();
            }
        }

        public async Task<List<Song>> GetRecommendationsAsync(string artistName)
        {
            try
            {
                // Get seed tracks from history and favorites
                var seedTracks = await GetSeedTracksAsync();
                
                if (string.IsNullOrWhiteSpace(artistName))
                {
                    return await GetPersonalizedRecommendations(seedTracks);
                }

                var recommendations = new List<Song>();
                
                // Try to get recommendations using the artist and seed tracks
                var artistRecs = await _spotify.GetSpotifyRecommendationsAsync(
                    seedTracks.Take(MAX_SEED_TRACKS).Select(s => s.SpotifyTrackId).ToList(),
                    new List<string> { artistName });

                recommendations.AddRange(artistRecs);

                // If we don't have enough recommendations, try getting more using just the artist
                if (recommendations.Count < 10)
                {
                    var moreRecs = await _spotify.GetSpotifyRecommendationsAsync(
                        new List<string>(),
                        new List<string> { artistName });
                    recommendations.AddRange(moreRecs.Where(r => !recommendations.Any(x => x.SpotifyTrackId == r.SpotifyTrackId)));
                }

                return recommendations.Take(10).ToList();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting recommendations for artist: {ArtistName}", artistName);
                return new List<Song>();
            }
        }

        public async Task<List<Song>> GetRecommendationsForMultipleArtistsAsync(List<string> artistNames)
        {
            try
            {
                // Get seed tracks from history and favorites
                var seedTracks = await GetSeedTracksAsync();
                
                if (artistNames == null || !artistNames.Any())
                {
                    return await GetPersonalizedRecommendations(seedTracks);
                }

                var recommendations = new List<Song>();
                
                // Get recommendations for each artist using seed tracks
                foreach (var artist in artistNames.Take(MAX_SEED_ARTISTS))
                {
                    var artistRecs = await _spotify.GetSpotifyRecommendationsAsync(
                        seedTracks.Take(MAX_SEED_TRACKS).Select(s => s.SpotifyTrackId).ToList(),
                        new List<string> { artist });

                    recommendations.AddRange(artistRecs);
                }

                // If we don't have enough recommendations, try with related artists
                if (recommendations.Count < 15)
                {
                    foreach (var artist in artistNames.Take(MAX_SEED_ARTISTS))
                    {
                        var relatedArtists = await _spotify.GetRelatedArtistsAsync(artist);
                        if (relatedArtists.Any())
                        {
                            var relatedRecs = await _spotify.GetSpotifyRecommendationsAsync(
                                seedTracks.Take(MAX_SEED_TRACKS).Select(s => s.SpotifyTrackId).ToList(),
                                relatedArtists.Take(2).ToList());

                            recommendations.AddRange(relatedRecs);
                        }
                    }
                }

                // If we still don't have recommendations, use personalized recommendations
                if (!recommendations.Any())
                {
                    return await GetPersonalizedRecommendations(seedTracks);
                }

                return FilterAndRandomizeRecommendations(recommendations);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting recommendations for multiple artists {ArtistNames}", string.Join(", ", artistNames));
                return await GetDefaultRecommendations();
            }
        }

        private async Task<List<Song>> GetPersonalizedRecommendations(List<Song> seedTracks)
        {
            try
            {
                if (!seedTracks.Any())
                {
                    _logger.LogWarning("No seed tracks available for personalized recommendations");
                    return new List<Song>();
                }

                var recommendations = await _spotify.GetSpotifyRecommendationsAsync(
                    seedTracks.Select(s => s.SpotifyTrackId).ToList(),
                    new List<string>());

                return recommendations.Take(10).ToList();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting personalized recommendations");
                return new List<Song>();
            }
        }

        private List<Song> FilterAndRandomizeRecommendations(List<Song> recommendations)
        {
            return recommendations
                .Where(s => s != null && !string.IsNullOrEmpty(s.SpotifyTrackId))
                .GroupBy(s => s.SpotifyTrackId) // Remove duplicates
                .Select(g => g.First())
                .OrderBy(x => _random.Next()) // Randomize
                .Take(20)
                .ToList();
        }

        public async Task<List<Song>> GetDefaultRecommendations()
        {
            try
            {
                // Get popular tracks from history as fallback
                var popularTracks = await _context.History
                    .GroupBy(h => h.SpotifyTrackId)
                    .Select(g => new { TrackId = g.Key, Count = g.Count(), Track = g.First() })
                    .OrderByDescending(x => x.Count)
                    .Take(20)
                    .Select(x => x.Track)
                    .ToListAsync();

                if (popularTracks.Any())
                {
                    return popularTracks.OrderBy(x => _random.Next()).Take(10).ToList();
                }

                // If no history, get some random favorites
                var randomFavorites = await _context.Favorites
                    .OrderBy(x => Guid.NewGuid())
                    .Take(10)
                    .Select(f => new Song
                    {
                        SpotifyTrackId = f.SpotifyTrackId,
                        Title = f.Title,
                        Artist = f.Artist,
                        ImageUrl = f.ImageUrl ?? string.Empty,
                        AddedToFavoritesAt = f.AddedToFavoritesAt
                    })
                    .ToListAsync();

                return randomFavorites;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting default recommendations");
                return new List<Song>();
            }
        }

        public async Task<List<Song>> GetSimpleRecommendationsAsync()
        {
            try
            {
                _logger.LogInformation("Getting simple recommendations based on user history");

                // 1. Аналізуємо історію прослуховувань користувача
                var historyTracks = await _context.History
                    .OrderByDescending(s => s.ListenedAt)
                    .Take(100) // Останні 100 треків
                    .ToListAsync();

                var favoriteTracks = await _context.Favorites
                    .OrderByDescending(f => f.AddedToFavoritesAt)
                    .ToListAsync();

                if (!historyTracks.Any() && !favoriteTracks.Any())
                {
                    _logger.LogWarning("No history or favorites found for simple recommendations");
                    return await GetDefaultRecommendations();
                }

                // 2. Знаходимо найпопулярніших артистів користувача
                var artistFrequency = new Dictionary<string, int>();
                
                // Рахуємо частоту артистів в історії (вага x2)
                foreach (var track in historyTracks)
                {
                    var artist = track.Artist?.Trim();
                    if (!string.IsNullOrEmpty(artist))
                    {
                        artistFrequency[artist] = artistFrequency.GetValueOrDefault(artist, 0) + 2;
                    }
                }

                // Рахуємо частоту артистів в улюблених (вага x3)
                foreach (var favorite in favoriteTracks)
                {
                    var artist = favorite.Artist?.Trim();
                    if (!string.IsNullOrEmpty(artist))
                    {
                        artistFrequency[artist] = artistFrequency.GetValueOrDefault(artist, 0) + 3;
                    }
                }

                // 3. Отримуємо топ-артистів
                var topArtists = artistFrequency
                    .OrderByDescending(kv => kv.Value)
                    .Take(5)
                    .Select(kv => kv.Key)
                    .ToList();

                _logger.LogInformation("Top artists for recommendations: {Artists}", string.Join(", ", topArtists));

                // 4. Збираємо треки, які користувач ще не слухав
                var allListenedTrackIds = historyTracks.Select(t => t.SpotifyTrackId).ToHashSet();
                var allFavoriteTrackIds = favoriteTracks.Select(f => f.SpotifyTrackId).ToHashSet();
                var allKnownTrackIds = allListenedTrackIds.Union(allFavoriteTrackIds).ToHashSet();

                var recommendations = new List<Song>();

                // 5. Для кожного топ-артиста знаходимо нові треки
                foreach (var artist in topArtists.Take(3)) // Беремо топ-3 артистів
                {
                    try
                    {
                        var artistTracks = await _spotify.SearchSongsAsync(artist);
                        
                        // Фільтруємо треки, які користувач ще не слухав
                        var newTracks = artistTracks
                            .Where(t => !allKnownTrackIds.Contains(t.SpotifyTrackId))
                            .Take(4) // По 4 треки від кожного артиста
                            .ToList();

                        recommendations.AddRange(newTracks);
                        
                        _logger.LogInformation("Found {Count} new tracks for artist {Artist}", newTracks.Count, artist);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning(ex, "Error getting tracks for artist {Artist}", artist);
                    }
                }

                // 6. Якщо недостатньо рекомендацій, додаємо популярні треки
                if (recommendations.Count < 10)
                {
                    try
                    {
                        var defaultRecs = await GetDefaultRecommendations();
                        var newDefaultTracks = defaultRecs
                            .Where(t => !allKnownTrackIds.Contains(t.SpotifyTrackId))
                            .Take(10 - recommendations.Count)
                            .ToList();

                        recommendations.AddRange(newDefaultTracks);
                        _logger.LogInformation("Added {Count} default recommendations", newDefaultTracks.Count);
                    }
                    catch (Exception ex)
                    {
                        _logger.LogWarning(ex, "Error getting default recommendations");
                    }
                }

                // 7. Перемішуємо та повертаємо результат
                var finalRecommendations = recommendations
                    .GroupBy(s => s.SpotifyTrackId) // Видаляємо дублікати
                    .Select(g => g.First())
                    .OrderBy(x => _random.Next()) // Перемішуємо
                    .Take(15)
                    .ToList();

                _logger.LogInformation("Returning {Count} simple recommendations", finalRecommendations.Count);
                return finalRecommendations;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting simple recommendations");
                return await GetDefaultRecommendations();
            }
        }
    }
} 