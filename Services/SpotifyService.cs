using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;
using System.Linq;
using Microsoft.Extensions.Configuration;
using MusicRecommender.Models;
using System.Threading;
using System.Text;

namespace MusicRecommender.Services
{
    public class SpotifyService : ISpotifyService
    {
        private readonly IConfiguration _config;
        private readonly Random _random = new Random();
        private string? _cachedToken;
        private DateTime _tokenExpiresAt;
        private readonly SemaphoreSlim _requestThrottler = new SemaphoreSlim(1, 1);
        private DateTime _lastRequestTime = DateTime.MinValue;
        private const int MinRequestInterval = 50;
        private static readonly Dictionary<string, (List<Song> Recommendations, DateTime Expires)> _recommendationsCache = new();
        private readonly HttpClient _httpClient;

        // зафіксовані ID популярних артистів
        private readonly Dictionary<string, string> _fixedArtistIds = new()
        {
            { "the weeknd", "1Xyo4u8uXC1ZmMpatF05PJ" },
            { "drake", "3TVXtAsR1Inumwj472S9r4" },
            { "dua lipa", "6M2wZ9GZgrQXHCFfjv46we" },
            { "kendrick lamar", "2YZyLoL8N0Wb9xBt1NhZWg" },
            { "daft punk", "4tZwfgrHOc3mvqYlEYSvVi" },
            { "imagine dragons", "53XhwfbYqKCa1cC15pYq2q" },
            { "future", "1RyvyyTE3xzB2ZywiAwp0i" }
        };

        private readonly HashSet<string> _validGenres = new()
        {
            "pop", "hip-hop", "rap", "rock", "r-n-b", "dance", "electronic", 
            "alternative", "indie", "classical", "jazz", "metal", "soul"
        };

        private readonly string[] _defaultGenres = new[] 
        { 
            "pop", "hip-hop", "rock", "r-n-b", "dance"
        };

        public SpotifyService(IConfiguration config, IHttpClientFactory httpClientFactory)
        {
            _config = config ?? throw new ArgumentNullException(nameof(config));
            _httpClient = httpClientFactory?.CreateClient("spotify") ?? throw new ArgumentNullException(nameof(httpClientFactory));
            var apiEndpoint = _config["Spotify:ApiEndpoint"] ?? "https://api.spotify.com/v1/";
            _httpClient.BaseAddress = new Uri(apiEndpoint);
            _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
        }

        public async Task<string> GetAccessTokenAsync()
        {
            if (!string.IsNullOrEmpty(_cachedToken) && DateTime.UtcNow < _tokenExpiresAt)
            {
                return _cachedToken;
            }

            var clientId = _config["Spotify:ClientId"];
            var clientSecret = _config["Spotify:ClientSecret"];
            var tokenEndpoint = _config["Spotify:TokenEndpoint"] ?? "https://accounts.spotify.com/api/token";

            if (string.IsNullOrEmpty(clientId) || string.IsNullOrEmpty(clientSecret))
            {
                throw new InvalidOperationException("Spotify credentials are not configured properly");
            }

            using var client = new HttpClient();
            var auth = Convert.ToBase64String(Encoding.UTF8.GetBytes($"{clientId}:{clientSecret}"));
            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", auth);

            var content = new FormUrlEncodedContent(new[]
            {
                new KeyValuePair<string, string>("grant_type", "client_credentials")
            });

            var response = await client.PostAsync(tokenEndpoint, content);
            var responseContent = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                throw new HttpRequestException($"Failed to get Spotify token. Status: {response.StatusCode}. Response: {responseContent}");
            }

            using var tokenResponse = JsonDocument.Parse(responseContent);
            var token = tokenResponse.RootElement.GetProperty("access_token").GetString();

            if (string.IsNullOrEmpty(token))
            {
                throw new InvalidOperationException("Received empty token from Spotify");
            }

            _cachedToken = token;
            _tokenExpiresAt = DateTime.UtcNow.AddSeconds(tokenResponse.RootElement.GetProperty("expires_in").GetInt32() - 300); // 5 minutes buffer

            return token;
        }

        public async Task<List<Song>> GetSpotifyRecommendationsAsync(List<string> seedTracks, List<string> seedArtists, string? genre = null)
        {
            try
            {
                seedTracks ??= new List<string>();
                seedArtists ??= new List<string>();

                var cacheKey = string.Join(",", seedTracks.Concat(seedArtists).OrderBy(x => x));
                if (!string.IsNullOrEmpty(genre))
                    cacheKey += $"|{genre}";

                var cacheExpirationMinutes = _config.GetValue("Cache:RecommendationsExpirationMinutes", 15);
                
                if (_recommendationsCache.TryGetValue(cacheKey, out var cached) && 
                    DateTime.UtcNow < cached.Expires)
                {
                    return cached.Recommendations;
                }

                // Spotify відключив Recommendations API для нових додатків (листопад 2024)
                // Використовуємо альтернативний підхід: пошук популярних треків за жанрами/артистами
                
                var recommendations = new List<Song>();
                var token = await GetAccessTokenAsync();
                _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
                var usedArtists = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

                // Якщо є seed artists, шукаємо їх топ треки (обмежуємо до 2 треків на артиста)
                if (seedArtists.Any())
                {
                    foreach (var artistName in seedArtists.Take(3))
                    {
                        try
                        {
                            var artistTracks = await SearchSongsAsync(artistName);
                            var filteredTracks = artistTracks.Take(2).ToList(); // Максимум 2 треки на артиста
                            recommendations.AddRange(filteredTracks);
                            usedArtists.Add(artistName);
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Error getting tracks for artist {artistName}: {ex.Message}");
                        }
                    }
                }

                // Додаємо більше різноманітності через різні жанри
                var searchQueries = new List<string>();
                
                if (!string.IsNullOrEmpty(genre))
                {
                    searchQueries.Add($"genre:{genre}");
                    // Додаємо схожі жанри
                    var relatedGenres = GetRelatedGenres(genre);
                    searchQueries.AddRange(relatedGenres.Take(2).Select(g => $"genre:{g}"));
                }
                
                // Додаємо різноманітні популярні запити
                if (searchQueries.Count < 4)
                {
                    var diverseQueries = new[] { 
                        "pop hits", "indie rock", "electronic music", "r&b soul", 
                        "alternative rock", "hip hop", "latin pop", "reggaeton",
                        "k-pop", "afrobeats", "jazz fusion", "country pop"
                    };
                    
                    // Вибираємо випадкові жанри для різноманітності
                    var randomQueries = diverseQueries
                        .OrderBy(x => _random.Next())
                        .Take(4 - searchQueries.Count);
                    searchQueries.AddRange(randomQueries);
                }

                // Шукаємо по кожному запиту
                foreach (var query in searchQueries.Take(4))
                {
                    try
                    {
                        var searchResults = await GetSearchResultsAsync(query);
                        if (searchResults is { } results)
                        {
                            dynamic dynamicResults = results;
                            if (dynamicResults.songs != null)
                            {
                                var songs = ((IEnumerable<dynamic>)dynamicResults.songs)
                                    .Where(song => {
                                        // Фільтруємо артистів які вже є
                                        var artistName = song.artistName?.ToString() ?? "";
                                        return !usedArtists.Any(used => 
                                            artistName.Contains(used, StringComparison.OrdinalIgnoreCase));
                                    })
                                    .Take(5); // Максимум 5 треків на запит

                                foreach (var song in songs)
                                {
                                    recommendations.Add(new Song
                                    {
                                        Title = song.name?.ToString() ?? "",
                                        Artist = song.artistName?.ToString() ?? "",
                                        SpotifyTrackId = song.id?.ToString() ?? "",
                                        ImageUrl = song.imageUrl?.ToString() ?? "",
                                        PreviewUrl = song.previewUrl?.ToString() ?? ""
                                    });
                                    
                                    // Додаємо артиста до використаних
                                    var artistName = song.artistName?.ToString();
                                    if (!string.IsNullOrEmpty(artistName))
                                    {
                                        usedArtists.Add(artistName);
                                    }
                                }
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error searching for {query}: {ex.Message}");
                    }
                }

                // Групуємо по артистах та обмежуємо кількість треків на артиста
                var result = recommendations
                    .Where(s => !string.IsNullOrEmpty(s.SpotifyTrackId))
                    .GroupBy(s => s.Artist.ToLower()) // Групуємо по артистах
                    .SelectMany(g => g.Take(2)) // Максимум 2 треки на артиста
                    .GroupBy(s => s.SpotifyTrackId) // Видаляємо дублікати треків
                    .Select(g => g.First())
                    .OrderBy(x => _random.Next()) // Рандомізуємо
                    .Take(20)
                    .ToList();

                Console.WriteLine($"Generated {result.Count} diverse recommendations with artists: {string.Join(", ", result.Select(r => r.Artist).Distinct().Take(10))}");

                _recommendationsCache[cacheKey] = (result, DateTime.UtcNow.AddMinutes(cacheExpirationMinutes));

                return result;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetSpotifyRecommendationsAsync: {ex.Message}");
                return new List<Song>();
            }
        }

        private List<string> GetRelatedGenres(string genre)
        {
            var genreRelations = new Dictionary<string, string[]>
            {
                { "pop", new[] { "dance-pop", "electropop", "indie-pop" } },
                { "rock", new[] { "alternative-rock", "indie-rock", "pop-rock" } },
                { "hip-hop", new[] { "rap", "trap", "old-school-hip-hop" } },
                { "electronic", new[] { "house", "techno", "ambient" } },
                { "r-n-b", new[] { "soul", "neo-soul", "contemporary-r-n-b" } },
                { "indie", new[] { "indie-rock", "indie-pop", "indie-folk" } },
                { "jazz", new[] { "smooth-jazz", "fusion", "bebop" } },
                { "country", new[] { "country-pop", "alt-country", "bluegrass" } }
            };

            var lowerGenre = genre.ToLower();
            foreach (var relation in genreRelations)
            {
                if (lowerGenre.Contains(relation.Key))
                {
                    return relation.Value.ToList();
                }
            }
            
            return new List<string> { "pop", "rock", "electronic" };
        }

        private async Task<string> GetArtistIdAsync(string artistName)
        {
            try
            {
                var key = artistName.ToLower().Trim();
                if (_fixedArtistIds.ContainsKey(key))
                {
                    return _fixedArtistIds[key];
                }

            var token = await GetAccessTokenAsync();
                _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

                var response = await SendApiRequestAsync(_httpClient, 
                    $"/search?q={Uri.EscapeDataString(artistName)}&type=artist&limit=1", 
                    "artist search");

                if (!response.IsSuccessStatusCode)
                {
                    return string.Empty;
                }

                var content = await response.Content.ReadAsStringAsync();
                using var doc = JsonDocument.Parse(content);
            var items = doc.RootElement.GetProperty("artists").GetProperty("items");

                if (items.GetArrayLength() > 0)
                {
                    return items[0].GetProperty("id").GetString() ?? string.Empty;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting artist ID for {artistName}: {ex.Message}");
            }

            return string.Empty;
        }

        public async Task<List<string>> GetRelatedArtistsAsync(string artistName)
        {
            try
            {
                // Spotify відключив Related Artists API для нових додатків
                // Використовуємо альтернативний підхід: пошук схожих артистів
                
                var token = await GetAccessTokenAsync();
                _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

                // Спочатку отримуємо жанри артиста через пошук
                var searchResults = await GetSearchResultsAsync(artistName);
                var relatedArtists = new List<string>();

                if (searchResults is { } results)
                {
                    dynamic dynamicResults = results;
                    if (dynamicResults.artists != null)
                    {
                        var artists = ((IEnumerable<dynamic>)dynamicResults.artists).Take(10);
                        foreach (var artist in artists)
                        {
                            var name = artist.name?.ToString();
                            if (!string.IsNullOrEmpty(name) && 
                                !name.Equals(artistName, StringComparison.OrdinalIgnoreCase))
                            {
                                relatedArtists.Add(name);
                            }
                        }
                    }
                }

                // Якщо не знайшли достатньо через пошук, додаємо популярних артистів з фіксованого списку
                if (relatedArtists.Count < 3)
                {
                    var popularArtists = new[] { "The Weeknd", "Drake", "Dua Lipa", "Ed Sheeran", "Taylor Swift", "Billie Eilish", "Post Malone" };
                    relatedArtists.AddRange(popularArtists
                        .Where(a => !a.Equals(artistName, StringComparison.OrdinalIgnoreCase))
                        .Take(5 - relatedArtists.Count));
                }

                Console.WriteLine($"Found {relatedArtists.Count} related artists for {artistName} using alternative approach");
                return relatedArtists.Take(5).ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting related artists: {ex.Message}");
                
                // Fallback до популярних артистів
                var fallbackArtists = new[] { "The Weeknd", "Drake", "Dua Lipa", "Ed Sheeran", "Taylor Swift" };
                return fallbackArtists
                    .Where(a => !a.Equals(artistName, StringComparison.OrdinalIgnoreCase))
                    .Take(5)
                    .ToList();
            }
        }

        private async Task<HttpResponseMessage> SendApiRequestAsync(HttpClient client, string url, string operationType)
        {
            await _requestThrottler.WaitAsync();
            try
            {
                await DelayBetweenRequests();

                var maxRetries = _config.GetValue("RetryPolicy:MaxRetries", 3);
                var initialInterval = _config.GetValue("RetryPolicy:InitialRetryIntervalMs", 1000);
                var maxInterval = _config.GetValue("RetryPolicy:MaxRetryIntervalMs", 5000);

                for (int i = 0; i <= maxRetries; i++)
                {
                    try
                    {
                        var response = await client.GetAsync(url);
                        
                        if (response.StatusCode == System.Net.HttpStatusCode.TooManyRequests)
                        {
                            var retryAfter = response.Headers.RetryAfter?.Delta ?? TimeSpan.FromSeconds(2);
                            await Task.Delay(retryAfter);
                            continue;
                        }

                        if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
                        {
                            _cachedToken = null;
                            var newToken = await GetAccessTokenAsync();
                            client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", newToken);
                            continue;
                        }

                        return response;
                    }
                    catch (Exception) when (i < maxRetries)
                    {
                        var delay = Math.Min(initialInterval * Math.Pow(2, i), maxInterval);
                        await Task.Delay((int)delay);
                    }
                }

                throw new Exception($"Operation {operationType} failed after {maxRetries} retries");
            }
            finally
            {
                _requestThrottler.Release();
            }
        }

        private async Task DelayBetweenRequests()
        {
            var timeSinceLastRequest = DateTime.UtcNow - _lastRequestTime;
            if (timeSinceLastRequest.TotalMilliseconds < MinRequestInterval)
            {
                await Task.Delay(MinRequestInterval - (int)timeSinceLastRequest.TotalMilliseconds);
            }
            _lastRequestTime = DateTime.UtcNow;
        }

        private async Task<HashSet<string>> GetAvailableGenresAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("https://api.spotify.com/v1/recommendations/available-genre-seeds");
                
                if (response.IsSuccessStatusCode)
                {
                    var json = await response.Content.ReadAsStringAsync();
                    using var doc = JsonDocument.Parse(json);
                    var genres = doc.RootElement.GetProperty("genres");
                    
                    var availableGenres = new HashSet<string>();
                    foreach (var genre in genres.EnumerateArray())
                    {
                        var genreStr = genre.GetString();
                        if (!string.IsNullOrEmpty(genreStr))
                        {
                            availableGenres.Add(genreStr);
                        }
                    }
                    return availableGenres;
                }
                
                Console.WriteLine($"Failed to get available genres. Status: {response.StatusCode}");
                return _validGenres;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting available genres: {ex.Message}");
                return _validGenres;
            }
        }

        private async Task<List<string>> FilterValidGenresAsync(IEnumerable<string> genres)
        {
            var availableGenres = await GetAvailableGenresAsync();
            return genres
                .Where(g => availableGenres.Contains(g.ToLower()))
                .ToList();
        }

        public async Task<List<string>> GetArtistSuggestionsAsync(string prefix)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(prefix))
                {
                    return new List<string>();
                }

                var token = await GetAccessTokenAsync();
                _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

                // Спочатку шукаємо точні збіги в фіксованих ID
                var fixedSuggestions = _fixedArtistIds
                    .Where(x => x.Key.Contains(prefix.ToLower()))
                    .Select(x => x.Key)
                    .ToList();

                // Шукаємо через Spotify API
                var response = await SendApiRequestAsync(_httpClient,
                    $"search?q={Uri.EscapeDataString(prefix)}&type=artist&limit=50&market={_config["Spotify:Market"] ?? "US"}",
                    "artist suggestions");

                if (!response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Failed to get artist suggestions. Status: {response.StatusCode}");
                    return fixedSuggestions;
                }

                var content = await response.Content.ReadAsStringAsync();
                using var doc = JsonDocument.Parse(content);
                
                if (!doc.RootElement.TryGetProperty("artists", out var artistsElement) ||
                    !artistsElement.TryGetProperty("items", out var items))
                {
                    return fixedSuggestions;
                }

                var suggestions = new List<string>();
                suggestions.AddRange(fixedSuggestions);

                foreach (var artist in items.EnumerateArray())
                {
                    try
                    {
                        if (!artist.TryGetProperty("name", out var nameElement))
                            continue;

                        var name = nameElement.GetString() ?? string.Empty;
                        if (string.IsNullOrEmpty(name))
                            continue;

                        // Перевіряємо, чи вже є такий артист
                        if (!suggestions.Contains(name, StringComparer.OrdinalIgnoreCase))
                        {
                            suggestions.Add(name);
                        }
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error parsing artist: {ex.Message}");
                    }
                }

                // Сортуємо за релевантністю
                return suggestions
                    .OrderByDescending(s => s.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
                    .ThenByDescending(s => s.Contains(prefix, StringComparison.OrdinalIgnoreCase))
                    .ThenBy(s => s)
                    .Take(10)
                    .ToList();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting artist suggestions: {ex.Message}");
                return new List<string>();
            }
        }

        public async Task<List<Song>> SearchSongsAsync(string artistName)
        {
            try
            {
                // First try to get artist ID
                var token = await GetAccessTokenAsync();
                _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

                // First try direct search for tracks by artist
                var searchResponse = await SendApiRequestAsync(_httpClient,
                    $"search?q={Uri.EscapeDataString(artistName)}&type=track&limit=20&market={_config["Spotify:Market"] ?? "US"}",
                    "track search");

                if (searchResponse.IsSuccessStatusCode)
                {
                    var searchContent = await searchResponse.Content.ReadAsStringAsync();
                    using var searchDoc = JsonDocument.Parse(searchContent);
                    
                    if (searchDoc.RootElement.TryGetProperty("tracks", out var tracksElement) &&
                        tracksElement.TryGetProperty("items", out var items))
                    {
                        var songs = new List<Song>();
                        foreach (var item in items.EnumerateArray())
                        {
                            try
                            {
                                // Check if this track is by the requested artist
                                var artists = item.GetProperty("artists").EnumerateArray();
                                var matchingArtist = artists.Any(a => 
                                    a.GetProperty("name").GetString()?.Contains(artistName, StringComparison.OrdinalIgnoreCase) ?? false);

                                if (matchingArtist)
                                {
                                    var song = new Song
                                    {
                                        Title = item.GetProperty("name").GetString() ?? string.Empty,
                                        Artist = item.GetProperty("artists")[0].GetProperty("name").GetString() ?? string.Empty,
                                        PreviewUrl = item.TryGetProperty("preview_url", out var p) ? p.GetString() ?? string.Empty : string.Empty,
                                        SpotifyTrackId = item.GetProperty("id").GetString() ?? string.Empty
                                    };
                                    songs.Add(song);
                                }
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error parsing track: {ex.Message}");
                            }
                        }

                        if (songs.Any())
                        {
                            return songs;
                        }
                    }
                }

                // If direct search didn't work, try getting artist's top tracks
                var artistId = await GetArtistIdAsync(artistName);
                if (string.IsNullOrEmpty(artistId))
                {
                    return new List<Song>();
                }

                var response = await SendApiRequestAsync(_httpClient,
                    $"artists/{artistId}/top-tracks?market={_config["Spotify:Market"] ?? "US"}",
                    "artist top tracks");

                if (!response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Failed to get top tracks. Status: {response.StatusCode}");
                    return new List<Song>();
                }

                var content = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"Top tracks response: {content}"); // Debug logging

                using var doc = JsonDocument.Parse(content);
                var tracks = doc.RootElement.GetProperty("tracks");

                var topTracks = new List<Song>();
                foreach (var track in tracks.EnumerateArray())
                {
                    try
                    {
                        var song = new Song
                        {
                            Title = track.GetProperty("name").GetString() ?? string.Empty,
                            Artist = track.GetProperty("artists")[0].GetProperty("name").GetString() ?? string.Empty,
                            PreviewUrl = track.TryGetProperty("preview_url", out var p) ? p.GetString() ?? string.Empty : string.Empty,
                            SpotifyTrackId = track.GetProperty("id").GetString() ?? string.Empty
                        };

                        // Get track genres from artist
                        var genreResponse = await SendApiRequestAsync(_httpClient,
                            $"artists/{artistId}",
                            "artist genres");

                        if (genreResponse.IsSuccessStatusCode)
                        {
                            var genreContent = await genreResponse.Content.ReadAsStringAsync();
                            using var genreDoc = JsonDocument.Parse(genreContent);
                            if (genreDoc.RootElement.TryGetProperty("genres", out var genres))
                            {
                                song.Genre = string.Join(", ", genres.EnumerateArray().Select(g => g.GetString()));
                            }
                        }

                        topTracks.Add(song);
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error parsing track: {ex.Message}");
                    }
                }

                return topTracks;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error searching songs: {ex.Message}");
                return new List<Song>();
            }
        }

        public async Task<object> GetSearchResultsAsync(string query)
        {
            if (string.IsNullOrWhiteSpace(query))
            {
                return new { artists = Array.Empty<object>(), songs = Array.Empty<object>() };
            }

            try
            {
                var token = await GetAccessTokenAsync();
                _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

                var response = await SendApiRequestAsync(_httpClient,
                    $"search?q={Uri.EscapeDataString(query)}&type=artist,track&limit=10&market={_config["Spotify:Market"] ?? "US"}",
                    "search");

                if (!response.IsSuccessStatusCode)
                {
                    throw new Exception($"Search failed with status: {response.StatusCode}");
                }

                var content = await response.Content.ReadAsStringAsync();
                using var doc = JsonDocument.Parse(content);
                var root = doc.RootElement;

                var artists = new List<object>();
                var songs = new List<object>();

                if (root.TryGetProperty("artists", out var artistsElement) &&
                    artistsElement.TryGetProperty("items", out var artistItems))
                {
                    foreach (var artist in artistItems.EnumerateArray())
                    {
                        try
                        {
                            var name = artist.GetProperty("name").GetString() ?? string.Empty;
                            var popularity = artist.TryGetProperty("popularity", out var pop) ? pop.GetInt32() : 0;
                            var id = artist.GetProperty("id").GetString() ?? string.Empty;
                            string? imageUrl = null;

                            if (artist.TryGetProperty("images", out var images) && images.GetArrayLength() > 0)
                            {
                                imageUrl = images[0].TryGetProperty("url", out var url) ? url.GetString() : null;
                            }

                            artists.Add(new
                            {
                                type = "artist",
                                name = name,
                                id = id,
                                imageUrl = imageUrl,
                                popularity = popularity
                            });
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Error parsing artist: {ex.Message}");
                        }
                    }
                }

                if (root.TryGetProperty("tracks", out var tracksElement) &&
                    tracksElement.TryGetProperty("items", out var trackItems))
                {
                    foreach (var track in trackItems.EnumerateArray())
                    {
                        try
                        {
                            var name = track.GetProperty("name").GetString() ?? string.Empty;
                            var popularity = track.TryGetProperty("popularity", out var pop) ? pop.GetInt32() : 0;
                            var id = track.GetProperty("id").GetString() ?? string.Empty;
                            var artistName = "";
                            string? imageUrl = null;
                            string? previewUrl = null;

                            if (track.TryGetProperty("artists", out var artists_) && 
                                artists_.GetArrayLength() > 0 &&
                                artists_[0].TryGetProperty("name", out var artistNameElement))
                            {
                                artistName = artistNameElement.GetString() ?? "";
                            }

                            if (track.TryGetProperty("album", out var album) && 
                                album.TryGetProperty("images", out var images) && 
                                images.GetArrayLength() > 0)
                            {
                                imageUrl = images[0].TryGetProperty("url", out var url) ? url.GetString() : null;
                            }

                            if (track.TryGetProperty("preview_url", out var preview))
                            {
                                previewUrl = preview.GetString();
                            }

                            songs.Add(new
                            {
                                type = "track",
                                name = name,
                                id = id,
                                artistName = artistName,
                                imageUrl = imageUrl,
                                popularity = popularity,
                                previewUrl = previewUrl
                            });
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine($"Error parsing track: {ex.Message}");
                        }
                    }
                }

                var sortedArtists = artists
                    .OrderByDescending(a => {
                        var name = ((dynamic)a).name.ToString().ToLower();
                        var searchQuery = query.ToLower();
                        
                        // Якщо ім'я точно співпадає - найвищий пріоритет
                        if (name == searchQuery) return 1000 + ((dynamic)a).popularity;
                        
                        // Якщо ім'я починається з пошукового запиту - високий пріоритет
                        if (name.StartsWith(searchQuery)) return 800 + ((dynamic)a).popularity;
                        
                        // Якщо пошуковий запит є частиною імені - середній пріоритет
                        if (name.Contains(searchQuery)) return 500 + ((dynamic)a).popularity;
                        
                        // В інших випадках - низький пріоритет
                        return ((dynamic)a).popularity;
                    })
                    .ToList();

                var sortedSongs = songs
                    .OrderByDescending(s => {
                        var title = ((dynamic)s).name.ToString().ToLower();
                        var artist = ((dynamic)s).artistName.ToString().ToLower();
                        var searchQuery = query.ToLower();
                        
                        // Якщо назва точно співпадає - найвищий пріоритет
                        if (title == searchQuery) return 1000 + ((dynamic)s).popularity;
                        
                        // Якщо назва починається з пошукового запиту - високий пріоритет
                        if (title.StartsWith(searchQuery)) return 800 + ((dynamic)s).popularity;
                        
                        // Якщо ім'я виконавця точно співпадає - високий пріоритет
                        if (artist == searchQuery) return 700 + ((dynamic)s).popularity;
                        
                        // Якщо ім'я виконавця починається з пошукового запиту - середній пріоритет
                        if (artist.StartsWith(searchQuery)) return 600 + ((dynamic)s).popularity;
                        
                        // Якщо пошуковий запит є частиною назви або імені виконавця - низький пріоритет
                        if (title.Contains(searchQuery) || artist.Contains(searchQuery)) 
                            return 500 + ((dynamic)s).popularity;
                        
                        // В інших випадках - найнижчий пріоритет
                        return ((dynamic)s).popularity;
                    })
                    .ToList();

                return new
                {
                    artists = sortedArtists,
                    songs = sortedSongs
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in GetSearchResultsAsync: {ex.Message}");
                return new
                {
                    artists = Array.Empty<object>(),
                    songs = Array.Empty<object>()
                };
            }
        }

        public async Task<object> GetArtistTopTracksAsync(string artistId)
        {
            try
            {
                var token = await GetAccessTokenAsync();
                _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);

                var response = await SendApiRequestAsync(_httpClient,
                    $"artists/{artistId}/top-tracks?market={_config["Spotify:Market"] ?? "US"}",
                    "artist top tracks");

                if (!response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Failed to get top tracks. Status: {response.StatusCode}");
                    return new object[] { };
                }

                var content = await response.Content.ReadAsStringAsync();
                using var doc = JsonDocument.Parse(content);
                var tracks = doc.RootElement.GetProperty("tracks");

                var topTracks = new List<object>();
                foreach (var track in tracks.EnumerateArray())
                {
                    try
                    {
                        var name = track.GetProperty("name").GetString() ?? string.Empty;
                        var id = track.GetProperty("id").GetString() ?? string.Empty;
                        var artistName = track.GetProperty("artists")[0].GetProperty("name").GetString() ?? string.Empty;
                        string? imageUrl = null;
                        string? previewUrl = null;
                        var popularity = track.TryGetProperty("popularity", out var pop) ? pop.GetInt32() : 0;

                        if (track.TryGetProperty("album", out var album) &&
                            album.TryGetProperty("images", out var images) &&
                            images.GetArrayLength() > 0)
                        {
                            imageUrl = images[0].TryGetProperty("url", out var url) ? url.GetString() : null;
                        }

                        if (track.TryGetProperty("preview_url", out var preview))
                        {
                            previewUrl = preview.GetString();
                        }

                        topTracks.Add(new
                        {
                            type = "track",
                            name = name,
                            id = id,
                            artistName = artistName,
                            imageUrl = imageUrl,
                            popularity = popularity,
                            previewUrl = previewUrl
                        });
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Error parsing track: {ex.Message}");
                    }
                }

                return topTracks;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error getting artist top tracks: {ex.Message}");
                return new object[] { };
            }
        }
    }
}
