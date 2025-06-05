using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Configuration;
using MusicRecommender.Models;

namespace MusicRecommender.Services
{
    public interface ICacheService
    {
        Task<T?> GetOrCreateAsync<T>(string key, Func<Task<T>> factory, TimeSpan? expiration = null) where T : class;
        void Remove(string key);
        void Set(string key, object value, CacheItemType type);
        bool TryGet<T>(string key, out T? value) where T : class;
    }

    public class CacheService : ICacheService
    {
        private readonly IMemoryCache _cache;
        private readonly ILogger<CacheService> _logger;
        private readonly ConcurrentDictionary<string, SemaphoreSlim> _locks;
        private readonly ConcurrentDictionary<string, CacheItem> _cacheItems;
        private readonly IConfiguration _config;
        private readonly int _recommendationsExpirationMinutes;
        private readonly int _tokenExpirationMinutes;
        private readonly TimeSpan _defaultExpiration = TimeSpan.FromMinutes(30);

        public CacheService(IMemoryCache cache, ILogger<CacheService> logger, IConfiguration config)
        {
            _cache = cache ?? throw new ArgumentNullException(nameof(cache));
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            _config = config ?? throw new ArgumentNullException(nameof(config));
            
            _locks = new ConcurrentDictionary<string, SemaphoreSlim>();
            _cacheItems = new ConcurrentDictionary<string, CacheItem>();
            
            _recommendationsExpirationMinutes = _config.GetValue("Cache:RecommendationsExpirationMinutes", 15);
            _tokenExpirationMinutes = _config.GetValue("Cache:TokenExpirationMinutes", 50);
        }

        public async Task<T?> GetOrCreateAsync<T>(string key, Func<Task<T>> factory, TimeSpan? expiration = null) where T : class
        {
            if (string.IsNullOrEmpty(key))
                throw new ArgumentNullException(nameof(key));
                
            if (factory == null)
                throw new ArgumentNullException(nameof(factory));

            if (_cache.TryGetValue<T>(key, out var cachedValue) && cachedValue != null)
            {
                _logger.LogInformation($"Cache hit for key: {key}");
                return cachedValue;
            }

            var lockObj = _locks.GetOrAdd(key, k => new SemaphoreSlim(1, 1));
            await lockObj.WaitAsync();

            try
            {
                // Double check after acquiring lock
                if (_cache.TryGetValue<T>(key, out cachedValue) && cachedValue != null)
                {
                    return cachedValue;
                }

                _logger.LogInformation($"Cache miss for key: {key}");
                var result = await factory();

                if (result != null) // Only cache non-null results
                {
                    var cacheOptions = new MemoryCacheEntryOptions();
                    if (expiration.HasValue)
                    {
                        cacheOptions.AbsoluteExpirationRelativeToNow = expiration;
                    }
                    else
                    {
                        cacheOptions.AbsoluteExpirationRelativeToNow = _defaultExpiration;
                    }

                    _cache.Set(key, result, cacheOptions);
                }
                
                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error while creating cache entry for key: {key}");
                throw;
            }
            finally
            {
                lockObj.Release();
            }
        }

        public void Remove(string key)
        {
            if (!string.IsNullOrEmpty(key))
            {
                _cache.Remove(key);
                _cacheItems.TryRemove(key, out _);
                if (_locks.TryRemove(key, out var lockObj))
                {
                    lockObj.Dispose();
                }
            }
        }

        public void Set(string key, object value, CacheItemType type)
        {
            if (string.IsNullOrEmpty(key))
                throw new ArgumentNullException(nameof(key));

            if (value == null)
                throw new ArgumentNullException(nameof(value));

            var expirationMinutes = type switch
            {
                CacheItemType.Token => _tokenExpirationMinutes,
                CacheItemType.Recommendations => _recommendationsExpirationMinutes,
                _ => throw new ArgumentException($"Unsupported cache item type: {type}")
            };

            var item = new CacheItem
            {
                Value = value,
                ExpiresAt = DateTime.UtcNow.AddMinutes(expirationMinutes)
            };

            _cacheItems.AddOrUpdate(key, item, (_, _) => item);

            var cacheOptions = new MemoryCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(expirationMinutes)
            };

            _cache.Set(key, value, cacheOptions);
        }

        public bool TryGet<T>(string key, out T? value) where T : class
        {
            value = default;

            if (string.IsNullOrEmpty(key))
                return false;

            if (_cache.TryGetValue<T>(key, out var cachedValue) && cachedValue != null)
            {
                value = cachedValue;
                return true;
            }

            return false;
        }

        private class CacheItem
        {
            public required object Value { get; init; }
            public required DateTime ExpiresAt { get; init; }
        }
    }
} 