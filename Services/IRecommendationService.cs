using System.Collections.Generic;
using System.Threading.Tasks;
using MusicRecommender.Models;

namespace MusicRecommender.Services
{
    public interface IRecommendationService
    {
        Task<List<Song>> GetRecommendationsAsync(string artistName);
        Task<List<Song>> GetRecommendationsForMultipleArtistsAsync(List<string> artistNames);
        Task<List<Song>> GetSimpleRecommendationsAsync();
        Task<List<Song>> GetDefaultRecommendations();
        
        // ML методи тепер доступні через Python ML Service (IPythonMLService)
        // - GetKNNRecommendationsAsync() -> через PythonMLController
        // - GetSVDRecommendationsAsync() -> через PythonMLController  
        // - CompareModelsAsync() -> через PythonMLController
        // - GetSimilarTracksAsync() -> через PythonMLController
    }
} 