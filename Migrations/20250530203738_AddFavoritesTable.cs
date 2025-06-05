using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace MusicRecommender.Migrations
{
    /// <inheritdoc />
    public partial class AddFavoritesTable : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Genre",
                table: "Favorites");

            migrationBuilder.DropColumn(
                name: "ListenedAt",
                table: "Favorites");

            migrationBuilder.DropColumn(
                name: "PreviewUrl",
                table: "Favorites");

            migrationBuilder.AlterColumn<string>(
                name: "ImageUrl",
                table: "Favorites",
                type: "TEXT",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "TEXT");

            migrationBuilder.AlterColumn<DateTime>(
                name: "AddedToFavoritesAt",
                table: "Favorites",
                type: "TEXT",
                nullable: false,
                defaultValue: new DateTime(1, 1, 1, 0, 0, 0, 0, DateTimeKind.Unspecified),
                oldClrType: typeof(DateTime),
                oldType: "TEXT",
                oldNullable: true);

            migrationBuilder.AddColumn<int>(
                name: "Id",
                table: "Favorites",
                type: "INTEGER",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.CreateTable(
                name: "History",
                columns: table => new
                {
                    SpotifyTrackId = table.Column<string>(type: "TEXT", nullable: false),
                    Title = table.Column<string>(type: "TEXT", nullable: false),
                    Artist = table.Column<string>(type: "TEXT", nullable: false),
                    Genre = table.Column<string>(type: "TEXT", nullable: false),
                    PreviewUrl = table.Column<string>(type: "TEXT", nullable: false),
                    ImageUrl = table.Column<string>(type: "TEXT", nullable: false),
                    ListenedAt = table.Column<DateTime>(type: "TEXT", nullable: true),
                    AddedToFavoritesAt = table.Column<DateTime>(type: "TEXT", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_History", x => x.SpotifyTrackId);
                });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "History");

            migrationBuilder.DropColumn(
                name: "Id",
                table: "Favorites");

            migrationBuilder.AlterColumn<string>(
                name: "ImageUrl",
                table: "Favorites",
                type: "TEXT",
                nullable: false,
                defaultValue: "",
                oldClrType: typeof(string),
                oldType: "TEXT",
                oldNullable: true);

            migrationBuilder.AlterColumn<DateTime>(
                name: "AddedToFavoritesAt",
                table: "Favorites",
                type: "TEXT",
                nullable: true,
                oldClrType: typeof(DateTime),
                oldType: "TEXT");

            migrationBuilder.AddColumn<string>(
                name: "Genre",
                table: "Favorites",
                type: "TEXT",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<DateTime>(
                name: "ListenedAt",
                table: "Favorites",
                type: "TEXT",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "PreviewUrl",
                table: "Favorites",
                type: "TEXT",
                nullable: false,
                defaultValue: "");
        }
    }
}
