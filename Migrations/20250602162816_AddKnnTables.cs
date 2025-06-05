using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace MusicRecommender.Migrations
{
    /// <inheritdoc />
    public partial class AddKnnTables : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<float>(
                name: "Acousticness",
                table: "History",
                type: "REAL",
                nullable: false,
                defaultValue: 0f);

            migrationBuilder.AddColumn<float>(
                name: "Danceability",
                table: "History",
                type: "REAL",
                nullable: false,
                defaultValue: 0f);

            migrationBuilder.AddColumn<int>(
                name: "DurationMs",
                table: "History",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<float>(
                name: "Energy",
                table: "History",
                type: "REAL",
                nullable: false,
                defaultValue: 0f);

            migrationBuilder.AddColumn<float>(
                name: "Instrumentalness",
                table: "History",
                type: "REAL",
                nullable: false,
                defaultValue: 0f);

            migrationBuilder.AddColumn<int>(
                name: "Key",
                table: "History",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<float>(
                name: "Loudness",
                table: "History",
                type: "REAL",
                nullable: false,
                defaultValue: 0f);

            migrationBuilder.AddColumn<int>(
                name: "Mode",
                table: "History",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<int>(
                name: "Popularity",
                table: "History",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<float>(
                name: "Speechiness",
                table: "History",
                type: "REAL",
                nullable: false,
                defaultValue: 0f);

            migrationBuilder.AddColumn<float>(
                name: "Tempo",
                table: "History",
                type: "REAL",
                nullable: false,
                defaultValue: 0f);

            migrationBuilder.AddColumn<float>(
                name: "TimeSignature",
                table: "History",
                type: "REAL",
                nullable: false,
                defaultValue: 0f);

            migrationBuilder.AddColumn<float>(
                name: "Valence",
                table: "History",
                type: "REAL",
                nullable: false,
                defaultValue: 0f);

            migrationBuilder.CreateTable(
                name: "SongFeatures",
                columns: table => new
                {
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
                    Key = table.Column<float>(type: "REAL", nullable: false),
                    Mode = table.Column<float>(type: "REAL", nullable: false),
                    TimeSignature = table.Column<float>(type: "REAL", nullable: false),
                    Genre = table.Column<string>(type: "TEXT", nullable: false),
                    Artist = table.Column<string>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_SongFeatures", x => x.SpotifyTrackId);
                });

            migrationBuilder.CreateTable(
                name: "Users",
                columns: table => new
                {
                    UserId = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    UserName = table.Column<string>(type: "TEXT", nullable: false),
                    Email = table.Column<string>(type: "TEXT", nullable: false),
                    CreatedAt = table.Column<DateTime>(type: "TEXT", nullable: false),
                    PreferredGenres = table.Column<string>(type: "TEXT", nullable: false),
                    AvgDanceability = table.Column<float>(type: "REAL", nullable: false),
                    AvgEnergy = table.Column<float>(type: "REAL", nullable: false),
                    AvgValence = table.Column<float>(type: "REAL", nullable: false),
                    AvgTempo = table.Column<float>(type: "REAL", nullable: false),
                    AvgAcousticness = table.Column<float>(type: "REAL", nullable: false),
                    AvgInstrumentalness = table.Column<float>(type: "REAL", nullable: false),
                    AvgSpeechiness = table.Column<float>(type: "REAL", nullable: false),
                    AvgLoudness = table.Column<float>(type: "REAL", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Users", x => x.UserId);
                });

            migrationBuilder.CreateTable(
                name: "UserSongInteractions",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    UserId = table.Column<int>(type: "INTEGER", nullable: false),
                    SpotifyTrackId = table.Column<string>(type: "TEXT", nullable: false),
                    InteractionType = table.Column<int>(type: "INTEGER", nullable: false),
                    Rating = table.Column<float>(type: "REAL", nullable: false),
                    InteractionTime = table.Column<DateTime>(type: "TEXT", nullable: false),
                    PlayDuration = table.Column<int>(type: "INTEGER", nullable: false),
                    IsSkipped = table.Column<bool>(type: "INTEGER", nullable: false),
                    IsLiked = table.Column<bool>(type: "INTEGER", nullable: false),
                    IsRepeat = table.Column<bool>(type: "INTEGER", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_UserSongInteractions", x => x.Id);
                    table.ForeignKey(
                        name: "FK_UserSongInteractions_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "UserId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_UserSongInteractions_UserId",
                table: "UserSongInteractions",
                column: "UserId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "SongFeatures");

            migrationBuilder.DropTable(
                name: "UserSongInteractions");

            migrationBuilder.DropTable(
                name: "Users");

            migrationBuilder.DropColumn(
                name: "Acousticness",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Danceability",
                table: "History");

            migrationBuilder.DropColumn(
                name: "DurationMs",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Energy",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Instrumentalness",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Key",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Loudness",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Mode",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Popularity",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Speechiness",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Tempo",
                table: "History");

            migrationBuilder.DropColumn(
                name: "TimeSignature",
                table: "History");

            migrationBuilder.DropColumn(
                name: "Valence",
                table: "History");
        }
    }
}
