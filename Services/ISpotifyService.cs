using System.Collections.Generic;
using System.Threading.Tasks;
using MusicRecommender.Models;

namespace MusicRecommender.Services
{
    public interface ISpotifyService
    {
        Task<List<Song>> GetSpotifyRecommendationsAsync(List<string> seedTracks, List<string> seedArtists, string? genre = null);
        Task<List<string>> GetRelatedArtistsAsync(string artistName);
        Task<List<string>> GetArtistSuggestionsAsync(string prefix);
        Task<List<Song>> SearchSongsAsync(string artistName);
        Task<object> GetSearchResultsAsync(string query);
        Task<object> GetArtistTopTracksAsync(string artistId);
        Task<string> GetAccessTokenAsync();
    }
} 