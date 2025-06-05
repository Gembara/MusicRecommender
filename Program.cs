using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Configuration;
using MusicRecommender.Services;
using MusicRecommender.Models;
using Microsoft.EntityFrameworkCore;
using Serilog;
using System;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .WriteTo.File("logs/musicrecommender.log", rollingInterval: RollingInterval.Day)
    .CreateLogger();

builder.Host.UseSerilog();

// Add services to the container.
builder.Services.AddControllersWithViews()
    .AddRazorRuntimeCompilation();

// Configure antiforgery
builder.Services.AddAntiforgery(options => {
    options.HeaderName = "RequestVerificationToken";
});

// Add memory cache
builder.Services.AddMemoryCache();

// Configure HttpClient for Spotify
builder.Services.AddHttpClient("spotify", client =>
{
    client.BaseAddress = new Uri(builder.Configuration["Spotify:ApiEndpoint"] ?? "https://api.spotify.com/v1");
    client.DefaultRequestHeaders.Add("Accept", "application/json");
    client.Timeout = TimeSpan.FromSeconds(30);
});

// Configure HttpClient for ML Service
builder.Services.AddHttpClient("mlservice", client =>
{
    var mlServiceUrl = builder.Configuration["MLService:BaseUrl"] ?? "http://localhost:8000";
    client.BaseAddress = new Uri(mlServiceUrl);
    client.DefaultRequestHeaders.Add("Accept", "application/json");
    var timeoutSeconds = builder.Configuration.GetValue<int>("MLService:TimeoutSeconds", 30);
    client.Timeout = TimeSpan.FromSeconds(timeoutSeconds);
});

// Also add default HttpClient for ML Controller
builder.Services.AddHttpClient();

// Add database context
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

// Додаємо підтримку сесій
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromHours(24); // Сесія на 24 години
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
    options.Cookie.Name = "MusicRecommender.Session";
    options.Cookie.SecurePolicy = CookieSecurePolicy.SameAsRequest;
});

// Configure services
builder.Services.AddScoped<ISpotifyService, SpotifyService>();
builder.Services.AddScoped<IRecommendationService, RecommendationService>();
builder.Services.AddScoped<ICacheService, CacheService>();

// ML Training services
builder.Services.AddScoped<MLDataCollectionService>();

var app = builder.Build();

// Configure error handling
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
else
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();

// Enable antiforgery
app.UseAntiforgery();

// Додаємо підтримку сесій
app.UseSession();

app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
