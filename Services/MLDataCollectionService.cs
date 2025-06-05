using Microsoft.EntityFrameworkCore;
using MusicRecommender.Models;
using System.Text.Json;

namespace MusicRecommender.Services
{
    public class MLDataCollectionService
    {
        private readonly ApplicationDbContext _context;
        private readonly ILogger<MLDataCollectionService> _logger;

        public MLDataCollectionService(ApplicationDbContext context, ILogger<MLDataCollectionService> logger)
        {
            _context = context;
            _logger = logger;
        }

        /// <summary>
        /// Збір нових тренувальних даних з користувацьких взаємодій
        /// </summary>
        public async Task<int> CollectTrainingDataAsync()
        {
            _logger.LogInformation("🔄 Починаємо збір тренувальних даних...");

            var lastCollectionTime = await GetLastCollectionTimeAsync();
            var newInteractions = await GetNewInteractionsAsync(lastCollectionTime);

            _logger.LogInformation($"📊 Знайдено {newInteractions.Count} нових взаємодій");

            int processedCount = 0;
            foreach (var interaction in newInteractions)
            {
                try
                {
                    await ProcessInteractionAsync(interaction);
                    processedCount++;
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "❌ Помилка при обробці взаємодії {InteractionId}", interaction.Id);
                }
            }

            await UpdateCollectionTimestampAsync();
            
            _logger.LogInformation($"✅ Оброблено {processedCount} взаємодій");
            return processedCount;
        }

        /// <summary>
        /// Створення запису тренувальних даних з взаємодії користувача
        /// </summary>
        private async Task ProcessInteractionAsync(UserSongInteraction interaction)
        {
            // Перевіряємо, чи не існує вже запис
            var existing = await _context.MLTrainingData
                .FirstOrDefaultAsync(m => m.UserId == interaction.UserId && 
                                        m.SpotifyTrackId == interaction.SpotifyTrackId);

            if (existing != null) return; // Вже обробили цю взаємодію

            // Отримуємо фічі треку
            var songFeatures = await _context.SongFeatures
                .FirstOrDefaultAsync(sf => sf.SpotifyTrackId == interaction.SpotifyTrackId);

            if (songFeatures == null)
            {
                _logger.LogWarning("⚠️ Не знайдено фічі для треку {TrackId}", interaction.SpotifyTrackId);
                return;
            }

            // Отримуємо інформацію про трек
            var song = await _context.History
                .FirstOrDefaultAsync(s => s.SpotifyTrackId == interaction.SpotifyTrackId);

            // Обчислюємо профіль користувача на момент взаємодії
            var userProfile = await CalculateUserProfileAsync(interaction.UserId, interaction.InteractionTime);

            // Визначаємо рейтинг на основі типу взаємодії
            float rating = CalculateRatingFromInteraction(interaction);

            // Створюємо запис тренувальних даних
            var trainingData = new MLTrainingData
            {
                UserId = interaction.UserId,
                SpotifyTrackId = interaction.SpotifyTrackId,
                
                // Аудіо фічі
                Danceability = songFeatures.Danceability,
                Energy = songFeatures.Energy,
                Valence = songFeatures.Valence,
                Tempo = songFeatures.Tempo,
                Acousticness = songFeatures.Acousticness,
                Instrumentalness = songFeatures.Instrumentalness,
                Speechiness = songFeatures.Speechiness,
                Loudness = songFeatures.Loudness,
                Popularity = songFeatures.Popularity,
                DurationMs = songFeatures.DurationMs,
                Key = (int)songFeatures.Key,
                Mode = (int)songFeatures.Mode,
                TimeSignature = (int)songFeatures.TimeSignature,
                
                // Мета-дані
                Artist = song?.Artist ?? songFeatures.Artist ?? "Unknown",
                Genre = songFeatures.Genre ?? song?.Genre ?? "Unknown",
                ReleaseYear = 2023, // Default for now since Song model doesn't have ReleaseYear
                ArtistPopularity = 50.0f, // Default for now since SongFeatures doesn't have ArtistPopularity
                
                // Взаємодія
                Rating = rating,
                InteractionType = (int)interaction.InteractionType,
                PlayCount = interaction.IsRepeat ? 2 : 1, // Estimating PlayCount
                PlayDuration = CalculatePlayDurationPercentage(interaction),
                
                // Контекст
                ListeningContext = DetermineListeningContext(interaction.InteractionTime),
                Timestamp = interaction.InteractionTime,
                
                // Профіль користувача
                UserAvgDanceability = userProfile.AvgDanceability,
                UserAvgEnergy = userProfile.AvgEnergy,
                UserAvgValence = userProfile.AvgValence,
                UserAvgTempo = userProfile.AvgTempo
            };

            _context.MLTrainingData.Add(trainingData);
            await _context.SaveChangesAsync();
        }

        /// <summary>
        /// Обчислення профілю користувача на певний момент часу
        /// </summary>
        private async Task<(float AvgDanceability, float AvgEnergy, float AvgValence, float AvgTempo)> 
            CalculateUserProfileAsync(int userId, DateTime timestamp)
        {
            // Беремо останні 50 взаємодій користувача до вказаного часу
            var recentInteractions = await _context.UserSongInteractions
                .Where(i => i.UserId == userId && i.InteractionTime < timestamp)
                .OrderByDescending(i => i.InteractionTime)
                .Take(50)
                .Select(i => i.SpotifyTrackId)
                .ToListAsync();

            if (!recentInteractions.Any())
                return (0.5f, 0.5f, 0.5f, 120f); // Дефолтні значення

            var features = await _context.SongFeatures
                .Where(sf => recentInteractions.Contains(sf.SpotifyTrackId))
                .ToListAsync();

            if (!features.Any())
                return (0.5f, 0.5f, 0.5f, 120f);

            return (
                features.Average(f => f.Danceability),
                features.Average(f => f.Energy),
                features.Average(f => f.Valence),
                features.Average(f => f.Tempo)
            );
        }

        /// <summary>
        /// Обчислення рейтингу на основі взаємодії
        /// </summary>
        private float CalculateRatingFromInteraction(UserSongInteraction interaction)
        {
            // Базовий рейтинг на основі типу взаємодії
            float baseRating = interaction.InteractionType switch
            {
                InteractionType.Liked => 1.0f,
                InteractionType.AddedToPlaylist => 0.9f,
                InteractionType.Repeated => 0.8f,
                InteractionType.Played => 0.6f,
                InteractionType.Skipped => 0.1f,
                InteractionType.Disliked => 0.0f,
                _ => 0.5f
            };

            // Модифікуємо на основі тривалості прослуховування
            if (interaction.PlayDuration > 0)
            {
                // Приблизна тривалість треку 180 секунд
                float playPercentage = Math.Min(interaction.PlayDuration / 180f, 1.0f);
                if (playPercentage < 0.1f) // менше 10% - скіп
                    baseRating = Math.Min(baseRating, 0.2f);
                else if (playPercentage > 0.8f) // більше 80% - хороший сигнал
                    baseRating = Math.Min(baseRating + 0.2f, 1.0f);
            }

            // Бонуси/штрафи
            if (interaction.IsLiked) baseRating = Math.Min(baseRating + 0.3f, 1.0f);
            if (interaction.IsSkipped) baseRating = Math.Max(baseRating - 0.4f, 0.0f);
            if (interaction.IsRepeat) baseRating = Math.Min(baseRating + 0.1f, 1.0f);

            return Math.Max(0.0f, Math.Min(1.0f, baseRating));
        }

        /// <summary>
        /// Обчислення відсотка прослуховування
        /// </summary>
        private float CalculatePlayDurationPercentage(UserSongInteraction interaction)
        {
            if (interaction.PlayDuration <= 0) return 0.0f;
            
            // Приблизна тривалість треку 180 секунд (3 хвилини)
            float approximateTrackDuration = 180f;
            return Math.Min(interaction.PlayDuration / approximateTrackDuration, 1.0f);
        }

        /// <summary>
        /// Визначення контексту прослуховування за часом
        /// </summary>
        private string DetermineListeningContext(DateTime timestamp)
        {
            var hour = timestamp.Hour;
            return hour switch
            {
                >= 6 and < 12 => "morning",
                >= 12 and < 17 => "afternoon",
                >= 17 and < 22 => "evening",
                _ => "night"
            };
        }

        /// <summary>
        /// Отримання нових взаємодій для обробки
        /// </summary>
        private async Task<List<UserSongInteraction>> GetNewInteractionsAsync(DateTime since)
        {
            return await _context.UserSongInteractions
                .Where(i => i.InteractionTime > since)
                .OrderBy(i => i.InteractionTime)
                .ToListAsync();
        }

        /// <summary>
        /// Отримання часу останнього збору даних
        /// </summary>
        private async Task<DateTime> GetLastCollectionTimeAsync()
        {
            var lastRecord = await _context.MLTrainingData
                .OrderByDescending(m => m.Timestamp)
                .FirstOrDefaultAsync();

            return lastRecord?.Timestamp ?? DateTime.MinValue;
        }

        /// <summary>
        /// Оновлення мітки часу збору даних
        /// </summary>
        private async Task UpdateCollectionTimestampAsync()
        {
            // Можна зберегти в окремій таблиці налаштувань
            // Поки що просто логуємо
            _logger.LogInformation("📅 Оновлено час останнього збору: {Time}", DateTime.UtcNow);
        }

        /// <summary>
        /// Створення/оновлення ML профілю користувача
        /// </summary>
        public async Task<MLUserProfile> CreateOrUpdateUserProfileAsync(int userId)
        {
            _logger.LogInformation("👤 Оновлення ML профілю користувача {UserId}", userId);

            var existingProfile = await _context.MLUserProfiles
                .FirstOrDefaultAsync(p => p.UserId == userId);

            // Отримуємо всі тренувальні дані користувача
            var userTrainingData = await _context.MLTrainingData
                .Where(m => m.UserId == userId)
                .ToListAsync();

            if (!userTrainingData.Any())
            {
                _logger.LogWarning("⚠️ Немає тренувальних даних для користувача {UserId}", userId);
                return existingProfile ?? new MLUserProfile { UserId = userId };
            }

            // Обчислюємо музичні переваги
            var preferences = CalculatePreferences(userTrainingData);
            var behavioral = CalculateBehavioralPatterns(userTrainingData);
            var diversity = await CalculateDiversityMetricsAsync(userTrainingData);

            var profile = existingProfile ?? new MLUserProfile { UserId = userId };
            
            // Оновлюємо профіль
            profile.PreferredDanceability = preferences.Danceability;
            profile.PreferredEnergy = preferences.Energy;
            profile.PreferredValence = preferences.Valence;
            profile.PreferredTempo = preferences.Tempo;
            profile.PreferredAcousticness = preferences.Acousticness;
            profile.PreferredInstrumentalness = preferences.Instrumentalness;
            profile.PreferredSpeechiness = preferences.Speechiness;
            profile.PreferredLoudness = preferences.Loudness;
            
            profile.DanceabilityVariance = preferences.DanceabilityVar;
            profile.EnergyVariance = preferences.EnergyVar;
            profile.ValenceVariance = preferences.ValenceVar;
            profile.TempoVariance = preferences.TempoVar;
            
            profile.SkipRate = behavioral.SkipRate;
            profile.RepeatRate = behavioral.RepeatRate;
            profile.ExplorationRate = behavioral.ExplorationRate;
            
            profile.GenreDiversity = diversity.GenreDiversity;
            profile.ArtistDiversity = diversity.ArtistDiversity;
            
            profile.LastUpdated = DateTime.UtcNow;
            profile.TotalInteractions = userTrainingData.Count;

            if (existingProfile == null)
                _context.MLUserProfiles.Add(profile);
            
            await _context.SaveChangesAsync();
            
            _logger.LogInformation("✅ Оновлено ML профіль користувача {UserId}", userId);
            return profile;
        }

        private (float Danceability, float Energy, float Valence, float Tempo, 
                float Acousticness, float Instrumentalness, float Speechiness, float Loudness,
                float DanceabilityVar, float EnergyVar, float ValenceVar, float TempoVar) 
            CalculatePreferences(List<MLTrainingData> data)
        {
            // Зважуємо за рейтингом - більший вплив треків з вищим рейтингом
            var weightedData = data.Where(d => d.Rating > 0.3f).ToList(); // Фільтруємо скіпи
            
            if (!weightedData.Any()) return (0.5f, 0.5f, 0.5f, 120f, 0.5f, 0.5f, 0.5f, -10f, 0.1f, 0.1f, 0.1f, 30f);

            var totalWeight = weightedData.Sum(d => d.Rating);
            
            return (
                weightedData.Sum(d => d.Danceability * d.Rating) / totalWeight,
                weightedData.Sum(d => d.Energy * d.Rating) / totalWeight,
                weightedData.Sum(d => d.Valence * d.Rating) / totalWeight,
                weightedData.Sum(d => d.Tempo * d.Rating) / totalWeight,
                weightedData.Sum(d => d.Acousticness * d.Rating) / totalWeight,
                weightedData.Sum(d => d.Instrumentalness * d.Rating) / totalWeight,
                weightedData.Sum(d => d.Speechiness * d.Rating) / totalWeight,
                weightedData.Sum(d => d.Loudness * d.Rating) / totalWeight,
                
                // Варіанси
                CalculateVariance(weightedData.Select(d => d.Danceability)),
                CalculateVariance(weightedData.Select(d => d.Energy)),
                CalculateVariance(weightedData.Select(d => d.Valence)),
                CalculateVariance(weightedData.Select(d => d.Tempo))
            );
        }

        private (float SkipRate, float RepeatRate, float ExplorationRate) 
            CalculateBehavioralPatterns(List<MLTrainingData> data)
        {
            if (!data.Any()) return (0f, 0f, 0.5f);

            var skipRate = data.Count(d => d.InteractionType == (int)InteractionType.Skipped) / (float)data.Count;
            var repeatRate = data.Count(d => d.PlayCount > 1) / (float)data.Count;
            
            // Exploration rate - скільки різних артистів/жанрів
            var uniqueArtists = data.Select(d => d.Artist).Distinct().Count();
            var explorationRate = Math.Min(uniqueArtists / (float)data.Count, 1.0f);

            return (skipRate, repeatRate, explorationRate);
        }

        private async Task<(float GenreDiversity, float ArtistDiversity)> 
            CalculateDiversityMetricsAsync(List<MLTrainingData> data)
        {
            if (!data.Any()) return (0f, 0f);

            var uniqueGenres = data.Select(d => d.Genre).Distinct().Count();
            var uniqueArtists = data.Select(d => d.Artist).Distinct().Count();
            
            var genreDiversity = uniqueGenres / (float)Math.Min(data.Count, 20); // Нормалізовано
            var artistDiversity = uniqueArtists / (float)Math.Min(data.Count, 50);

            return (Math.Min(genreDiversity, 1.0f), Math.Min(artistDiversity, 1.0f));
        }

        private float CalculateVariance(IEnumerable<float> values)
        {
            var list = values.ToList();
            if (list.Count < 2) return 0f;
            
            var mean = list.Average();
            var variance = list.Sum(x => (x - mean) * (x - mean)) / list.Count;
            return (float)Math.Sqrt(variance); // Стандартне відхилення
        }

        /// <summary>
        /// Очищення старих тренувальних даних
        /// </summary>
        public async Task<int> CleanupOldTrainingDataAsync(TimeSpan maxAge)
        {
            var cutoffDate = DateTime.UtcNow - maxAge;
            
            var oldData = await _context.MLTrainingData
                .Where(m => m.Timestamp < cutoffDate)
                .ToListAsync();

            if (oldData.Any())
            {
                _context.MLTrainingData.RemoveRange(oldData);
                await _context.SaveChangesAsync();
                
                _logger.LogInformation("🗑️ Видалено {Count} старих записів тренувальних даних", oldData.Count);
            }

            return oldData.Count;
        }
    }
} 