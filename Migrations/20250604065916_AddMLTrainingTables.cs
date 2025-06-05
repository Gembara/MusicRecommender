using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace MusicRecommender.Migrations
{
    /// <inheritdoc />
    public partial class AddMLTrainingTables : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "MLModelMetrics",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    ModelType = table.Column<string>(type: "TEXT", nullable: false),
                    ModelVersion = table.Column<string>(type: "TEXT", nullable: false),
                    Accuracy = table.Column<float>(type: "REAL", nullable: false),
                    Precision = table.Column<float>(type: "REAL", nullable: false),
                    Recall = table.Column<float>(type: "REAL", nullable: false),
                    F1Score = table.Column<float>(type: "REAL", nullable: false),
                    MAE = table.Column<float>(type: "REAL", nullable: false),
                    MSE = table.Column<float>(type: "REAL", nullable: false),
                    TrainingSamples = table.Column<int>(type: "INTEGER", nullable: false),
                    TestSamples = table.Column<int>(type: "INTEGER", nullable: false),
                    UniqueUsers = table.Column<int>(type: "INTEGER", nullable: false),
                    UniqueTracks = table.Column<int>(type: "INTEGER", nullable: false),
                    TrainingDate = table.Column<DateTime>(type: "TEXT", nullable: false),
                    TrainingDuration = table.Column<TimeSpan>(type: "TEXT", nullable: false),
                    ModelConfig = table.Column<string>(type: "TEXT", nullable: false),
                    FeatureImportance = table.Column<string>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MLModelMetrics", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "MLTrainingData",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    UserId = table.Column<int>(type: "INTEGER", nullable: false),
                    SpotifyTrackId = table.Column<string>(type: "TEXT", nullable: false),
                    Danceability = table.Column<float>(type: "REAL", nullable: false),
                    Energy = table.Column<float>(type: "REAL", nullable: false),
                    Valence = table.Column<float>(type: "REAL", nullable: false),
                    Tempo = table.Column<float>(type: "REAL", nullable: false),
                    Acousticness = table.Column<float>(type: "REAL", nullable: false),
                    Instrumentalness = table.Column<float>(type: "REAL", nullable: false),
                    Speechiness = table.Column<float>(type: "REAL", nullable: false),
                    Loudness = table.Column<float>(type: "REAL", nullable: false),
                    Popularity = table.Column<float>(type: "REAL", nullable: false),
                    DurationMs = table.Column<float>(type: "REAL", nullable: false),
                    Key = table.Column<int>(type: "INTEGER", nullable: false),
                    Mode = table.Column<int>(type: "INTEGER", nullable: false),
                    TimeSignature = table.Column<int>(type: "INTEGER", nullable: false),
                    Artist = table.Column<string>(type: "TEXT", nullable: false),
                    Genre = table.Column<string>(type: "TEXT", nullable: false),
                    ReleaseYear = table.Column<int>(type: "INTEGER", nullable: false),
                    ArtistPopularity = table.Column<float>(type: "REAL", nullable: false),
                    Rating = table.Column<float>(type: "REAL", nullable: false),
                    InteractionType = table.Column<int>(type: "INTEGER", nullable: false),
                    PlayCount = table.Column<int>(type: "INTEGER", nullable: false),
                    PlayDuration = table.Column<float>(type: "REAL", nullable: false),
                    ListeningContext = table.Column<string>(type: "TEXT", nullable: false),
                    Timestamp = table.Column<DateTime>(type: "TEXT", nullable: false),
                    UserAvgDanceability = table.Column<float>(type: "REAL", nullable: false),
                    UserAvgEnergy = table.Column<float>(type: "REAL", nullable: false),
                    UserAvgValence = table.Column<float>(type: "REAL", nullable: false),
                    UserAvgTempo = table.Column<float>(type: "REAL", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MLTrainingData", x => x.Id);
                    table.ForeignKey(
                        name: "FK_MLTrainingData_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "UserId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "MLUserProfiles",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    UserId = table.Column<int>(type: "INTEGER", nullable: false),
                    PreferredDanceability = table.Column<float>(type: "REAL", nullable: false),
                    PreferredEnergy = table.Column<float>(type: "REAL", nullable: false),
                    PreferredValence = table.Column<float>(type: "REAL", nullable: false),
                    PreferredTempo = table.Column<float>(type: "REAL", nullable: false),
                    PreferredAcousticness = table.Column<float>(type: "REAL", nullable: false),
                    PreferredInstrumentalness = table.Column<float>(type: "REAL", nullable: false),
                    PreferredSpeechiness = table.Column<float>(type: "REAL", nullable: false),
                    PreferredLoudness = table.Column<float>(type: "REAL", nullable: false),
                    DanceabilityVariance = table.Column<float>(type: "REAL", nullable: false),
                    EnergyVariance = table.Column<float>(type: "REAL", nullable: false),
                    ValenceVariance = table.Column<float>(type: "REAL", nullable: false),
                    TempoVariance = table.Column<float>(type: "REAL", nullable: false),
                    SkipRate = table.Column<float>(type: "REAL", nullable: false),
                    RepeatRate = table.Column<float>(type: "REAL", nullable: false),
                    ExplorationRate = table.Column<float>(type: "REAL", nullable: false),
                    PreferredListeningTimes = table.Column<string>(type: "TEXT", nullable: false),
                    PreferredGenres = table.Column<string>(type: "TEXT", nullable: false),
                    GenreDiversity = table.Column<float>(type: "REAL", nullable: false),
                    ArtistDiversity = table.Column<float>(type: "REAL", nullable: false),
                    ClusterId = table.Column<int>(type: "INTEGER", nullable: false),
                    LastUpdated = table.Column<DateTime>(type: "TEXT", nullable: false),
                    TotalInteractions = table.Column<int>(type: "INTEGER", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MLUserProfiles", x => x.Id);
                    table.ForeignKey(
                        name: "FK_MLUserProfiles_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "UserId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "TrackSimilarity",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    TrackId1 = table.Column<string>(type: "TEXT", nullable: false),
                    TrackId2 = table.Column<string>(type: "TEXT", nullable: false),
                    CosineSimilarity = table.Column<float>(type: "REAL", nullable: false),
                    EuclideanDistance = table.Column<float>(type: "REAL", nullable: false),
                    AudioSimilarity = table.Column<float>(type: "REAL", nullable: false),
                    GenreSimilarity = table.Column<float>(type: "REAL", nullable: false),
                    CalculatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_TrackSimilarity", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "UserSimilarity",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    UserId1 = table.Column<int>(type: "INTEGER", nullable: false),
                    UserId2 = table.Column<int>(type: "INTEGER", nullable: false),
                    CosineSimilarity = table.Column<float>(type: "REAL", nullable: false),
                    PearsonCorrelation = table.Column<float>(type: "REAL", nullable: false),
                    JaccardSimilarity = table.Column<float>(type: "REAL", nullable: false),
                    CommonTracks = table.Column<int>(type: "INTEGER", nullable: false),
                    CalculatedAt = table.Column<DateTime>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserSimilarity", x => x.Id);
                });

            migrationBuilder.CreateIndex(
                name: "IX_MLModelMetrics_ModelType_TrainingDate",
                table: "MLModelMetrics",
                columns: new[] { "ModelType", "TrainingDate" });

            migrationBuilder.CreateIndex(
                name: "IX_MLTrainingData_Timestamp",
                table: "MLTrainingData",
                column: "Timestamp");

            migrationBuilder.CreateIndex(
                name: "IX_MLTrainingData_UserId_SpotifyTrackId",
                table: "MLTrainingData",
                columns: new[] { "UserId", "SpotifyTrackId" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_MLUserProfiles_ClusterId",
                table: "MLUserProfiles",
                column: "ClusterId");

            migrationBuilder.CreateIndex(
                name: "IX_MLUserProfiles_UserId",
                table: "MLUserProfiles",
                column: "UserId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_TrackSimilarity_TrackId1_TrackId2",
                table: "TrackSimilarity",
                columns: new[] { "TrackId1", "TrackId2" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_UserSimilarity_UserId1_UserId2",
                table: "UserSimilarity",
                columns: new[] { "UserId1", "UserId2" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "MLModelMetrics");

            migrationBuilder.DropTable(
                name: "MLTrainingData");

            migrationBuilder.DropTable(
                name: "MLUserProfiles");

            migrationBuilder.DropTable(
                name: "TrackSimilarity");

            migrationBuilder.DropTable(
                name: "UserSimilarity");
        }
    }
}
