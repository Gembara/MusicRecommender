﻿// <auto-generated />
using System;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;
using MusicRecommender.Models;

#nullable disable

namespace MusicRecommender.Migrations
{
    [DbContext(typeof(ApplicationDbContext))]
    partial class ApplicationDbContextModelSnapshot : ModelSnapshot
    {
        protected override void BuildModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder.HasAnnotation("ProductVersion", "9.0.0");

            modelBuilder.Entity("MusicRecommender.Models.Favorite", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<DateTime>("AddedToFavoritesAt")
                        .HasColumnType("TEXT");

                    b.Property<string>("Artist")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<string>("ImageUrl")
                        .HasColumnType("TEXT");

                    b.Property<string>("SpotifyTrackId")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<string>("Title")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<int>("UserId")
                        .HasColumnType("INTEGER");

                    b.HasKey("Id");

                    b.HasIndex("SpotifyTrackId");

                    b.HasIndex("UserId");

                    b.ToTable("Favorites", (string)null);
                });

            modelBuilder.Entity("MusicRecommender.Models.MLModelMetrics", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<float>("Accuracy")
                        .HasColumnType("REAL");

                    b.Property<float>("F1Score")
                        .HasColumnType("REAL");

                    b.Property<string>("FeatureImportance")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("MAE")
                        .HasColumnType("REAL");

                    b.Property<float>("MSE")
                        .HasColumnType("REAL");

                    b.Property<string>("ModelConfig")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<string>("ModelType")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<string>("ModelVersion")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("Precision")
                        .HasColumnType("REAL");

                    b.Property<float>("Recall")
                        .HasColumnType("REAL");

                    b.Property<int>("TestSamples")
                        .HasColumnType("INTEGER");

                    b.Property<DateTime>("TrainingDate")
                        .HasColumnType("TEXT");

                    b.Property<TimeSpan>("TrainingDuration")
                        .HasColumnType("TEXT");

                    b.Property<int>("TrainingSamples")
                        .HasColumnType("INTEGER");

                    b.Property<int>("UniqueTracks")
                        .HasColumnType("INTEGER");

                    b.Property<int>("UniqueUsers")
                        .HasColumnType("INTEGER");

                    b.HasKey("Id");

                    b.HasIndex("ModelType", "TrainingDate");

                    b.ToTable("MLModelMetrics");
                });

            modelBuilder.Entity("MusicRecommender.Models.MLTrainingData", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<float>("Acousticness")
                        .HasColumnType("REAL");

                    b.Property<string>("Artist")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("ArtistPopularity")
                        .HasColumnType("REAL");

                    b.Property<float>("Danceability")
                        .HasColumnType("REAL");

                    b.Property<float>("DurationMs")
                        .HasColumnType("REAL");

                    b.Property<float>("Energy")
                        .HasColumnType("REAL");

                    b.Property<string>("Genre")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("Instrumentalness")
                        .HasColumnType("REAL");

                    b.Property<int>("InteractionType")
                        .HasColumnType("INTEGER");

                    b.Property<int>("Key")
                        .HasColumnType("INTEGER");

                    b.Property<string>("ListeningContext")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("Loudness")
                        .HasColumnType("REAL");

                    b.Property<int>("Mode")
                        .HasColumnType("INTEGER");

                    b.Property<int>("PlayCount")
                        .HasColumnType("INTEGER");

                    b.Property<float>("PlayDuration")
                        .HasColumnType("REAL");

                    b.Property<float>("Popularity")
                        .HasColumnType("REAL");

                    b.Property<float>("Rating")
                        .HasColumnType("REAL");

                    b.Property<int>("ReleaseYear")
                        .HasColumnType("INTEGER");

                    b.Property<float>("Speechiness")
                        .HasColumnType("REAL");

                    b.Property<string>("SpotifyTrackId")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("Tempo")
                        .HasColumnType("REAL");

                    b.Property<int>("TimeSignature")
                        .HasColumnType("INTEGER");

                    b.Property<DateTime>("Timestamp")
                        .HasColumnType("TEXT");

                    b.Property<float>("UserAvgDanceability")
                        .HasColumnType("REAL");

                    b.Property<float>("UserAvgEnergy")
                        .HasColumnType("REAL");

                    b.Property<float>("UserAvgTempo")
                        .HasColumnType("REAL");

                    b.Property<float>("UserAvgValence")
                        .HasColumnType("REAL");

                    b.Property<int>("UserId")
                        .HasColumnType("INTEGER");

                    b.Property<float>("Valence")
                        .HasColumnType("REAL");

                    b.HasKey("Id");

                    b.HasIndex("Timestamp");

                    b.HasIndex("UserId", "SpotifyTrackId")
                        .IsUnique();

                    b.ToTable("MLTrainingData");
                });

            modelBuilder.Entity("MusicRecommender.Models.MLUserProfile", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<float>("ArtistDiversity")
                        .HasColumnType("REAL");

                    b.Property<int>("ClusterId")
                        .HasColumnType("INTEGER");

                    b.Property<float>("DanceabilityVariance")
                        .HasColumnType("REAL");

                    b.Property<float>("EnergyVariance")
                        .HasColumnType("REAL");

                    b.Property<float>("ExplorationRate")
                        .HasColumnType("REAL");

                    b.Property<float>("GenreDiversity")
                        .HasColumnType("REAL");

                    b.Property<DateTime>("LastUpdated")
                        .HasColumnType("TEXT");

                    b.Property<float>("PreferredAcousticness")
                        .HasColumnType("REAL");

                    b.Property<float>("PreferredDanceability")
                        .HasColumnType("REAL");

                    b.Property<float>("PreferredEnergy")
                        .HasColumnType("REAL");

                    b.Property<string>("PreferredGenres")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("PreferredInstrumentalness")
                        .HasColumnType("REAL");

                    b.Property<string>("PreferredListeningTimes")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("PreferredLoudness")
                        .HasColumnType("REAL");

                    b.Property<float>("PreferredSpeechiness")
                        .HasColumnType("REAL");

                    b.Property<float>("PreferredTempo")
                        .HasColumnType("REAL");

                    b.Property<float>("PreferredValence")
                        .HasColumnType("REAL");

                    b.Property<float>("RepeatRate")
                        .HasColumnType("REAL");

                    b.Property<float>("SkipRate")
                        .HasColumnType("REAL");

                    b.Property<float>("TempoVariance")
                        .HasColumnType("REAL");

                    b.Property<int>("TotalInteractions")
                        .HasColumnType("INTEGER");

                    b.Property<int>("UserId")
                        .HasColumnType("INTEGER");

                    b.Property<float>("ValenceVariance")
                        .HasColumnType("REAL");

                    b.HasKey("Id");

                    b.HasIndex("ClusterId");

                    b.HasIndex("UserId")
                        .IsUnique();

                    b.ToTable("MLUserProfiles");
                });

            modelBuilder.Entity("MusicRecommender.Models.Song", b =>
                {
                    b.Property<string>("SpotifyTrackId")
                        .HasColumnType("TEXT");

                    b.Property<float>("Acousticness")
                        .HasColumnType("REAL");

                    b.Property<DateTime?>("AddedToFavoritesAt")
                        .HasColumnType("TEXT");

                    b.Property<string>("Artist")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("Danceability")
                        .HasColumnType("REAL");

                    b.Property<int>("DurationMs")
                        .HasColumnType("INTEGER");

                    b.Property<float>("Energy")
                        .HasColumnType("REAL");

                    b.Property<string>("Genre")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<string>("ImageUrl")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("Instrumentalness")
                        .HasColumnType("REAL");

                    b.Property<int>("Key")
                        .HasColumnType("INTEGER");

                    b.Property<DateTime?>("ListenedAt")
                        .HasColumnType("TEXT");

                    b.Property<float>("Loudness")
                        .HasColumnType("REAL");

                    b.Property<int>("Mode")
                        .HasColumnType("INTEGER");

                    b.Property<int>("Popularity")
                        .HasColumnType("INTEGER");

                    b.Property<string>("PreviewUrl")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("Speechiness")
                        .HasColumnType("REAL");

                    b.Property<float>("Tempo")
                        .HasColumnType("REAL");

                    b.Property<float>("TimeSignature")
                        .HasColumnType("REAL");

                    b.Property<string>("Title")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<int?>("UserId")
                        .HasColumnType("INTEGER");

                    b.Property<float>("Valence")
                        .HasColumnType("REAL");

                    b.HasKey("SpotifyTrackId");

                    b.HasIndex("UserId");

                    b.ToTable("History", (string)null);
                });

            modelBuilder.Entity("MusicRecommender.Models.SongFeatures", b =>
                {
                    b.Property<string>("SpotifyTrackId")
                        .HasColumnType("TEXT");

                    b.Property<float>("Acousticness")
                        .HasColumnType("REAL");

                    b.Property<string>("Artist")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("Danceability")
                        .HasColumnType("REAL");

                    b.Property<float>("DurationMs")
                        .HasColumnType("REAL");

                    b.Property<float>("Energy")
                        .HasColumnType("REAL");

                    b.Property<string>("Genre")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<float>("Instrumentalness")
                        .HasColumnType("REAL");

                    b.Property<float>("Key")
                        .HasColumnType("REAL");

                    b.Property<float>("Loudness")
                        .HasColumnType("REAL");

                    b.Property<float>("Mode")
                        .HasColumnType("REAL");

                    b.Property<float>("Popularity")
                        .HasColumnType("REAL");

                    b.Property<float>("Speechiness")
                        .HasColumnType("REAL");

                    b.Property<float>("Tempo")
                        .HasColumnType("REAL");

                    b.Property<float>("TimeSignature")
                        .HasColumnType("REAL");

                    b.Property<float>("Valence")
                        .HasColumnType("REAL");

                    b.HasKey("SpotifyTrackId");

                    b.ToTable("SongFeatures", (string)null);
                });

            modelBuilder.Entity("MusicRecommender.Models.TrackSimilarity", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<float>("AudioSimilarity")
                        .HasColumnType("REAL");

                    b.Property<DateTime>("CalculatedAt")
                        .HasColumnType("TEXT");

                    b.Property<float>("CosineSimilarity")
                        .HasColumnType("REAL");

                    b.Property<float>("EuclideanDistance")
                        .HasColumnType("REAL");

                    b.Property<float>("GenreSimilarity")
                        .HasColumnType("REAL");

                    b.Property<string>("TrackId1")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<string>("TrackId2")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.HasKey("Id");

                    b.HasIndex("TrackId1", "TrackId2")
                        .IsUnique();

                    b.ToTable("TrackSimilarity");
                });

            modelBuilder.Entity("MusicRecommender.Models.User", b =>
                {
                    b.Property<int>("UserId")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<float>("AvgAcousticness")
                        .HasColumnType("REAL");

                    b.Property<float>("AvgDanceability")
                        .HasColumnType("REAL");

                    b.Property<float>("AvgEnergy")
                        .HasColumnType("REAL");

                    b.Property<float>("AvgInstrumentalness")
                        .HasColumnType("REAL");

                    b.Property<float>("AvgLoudness")
                        .HasColumnType("REAL");

                    b.Property<float>("AvgSpeechiness")
                        .HasColumnType("REAL");

                    b.Property<float>("AvgTempo")
                        .HasColumnType("REAL");

                    b.Property<float>("AvgValence")
                        .HasColumnType("REAL");

                    b.Property<DateTime>("CreatedAt")
                        .HasColumnType("TEXT");

                    b.Property<string>("Email")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<string>("PreferredGenres")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<string>("UserName")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.HasKey("UserId");

                    b.ToTable("Users", (string)null);
                });

            modelBuilder.Entity("MusicRecommender.Models.UserSimilarity", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<DateTime>("CalculatedAt")
                        .HasColumnType("TEXT");

                    b.Property<int>("CommonTracks")
                        .HasColumnType("INTEGER");

                    b.Property<float>("CosineSimilarity")
                        .HasColumnType("REAL");

                    b.Property<float>("JaccardSimilarity")
                        .HasColumnType("REAL");

                    b.Property<float>("PearsonCorrelation")
                        .HasColumnType("REAL");

                    b.Property<int>("UserId1")
                        .HasColumnType("INTEGER");

                    b.Property<int>("UserId2")
                        .HasColumnType("INTEGER");

                    b.HasKey("Id");

                    b.HasIndex("UserId1", "UserId2")
                        .IsUnique();

                    b.ToTable("UserSimilarity");
                });

            modelBuilder.Entity("MusicRecommender.Models.UserSongInteraction", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("INTEGER");

                    b.Property<DateTime>("InteractionTime")
                        .HasColumnType("TEXT");

                    b.Property<int>("InteractionType")
                        .HasColumnType("INTEGER");

                    b.Property<bool>("IsLiked")
                        .HasColumnType("INTEGER");

                    b.Property<bool>("IsRepeat")
                        .HasColumnType("INTEGER");

                    b.Property<bool>("IsSkipped")
                        .HasColumnType("INTEGER");

                    b.Property<int>("PlayDuration")
                        .HasColumnType("INTEGER");

                    b.Property<float>("Rating")
                        .HasColumnType("REAL");

                    b.Property<string>("SpotifyTrackId")
                        .IsRequired()
                        .HasColumnType("TEXT");

                    b.Property<int>("UserId")
                        .HasColumnType("INTEGER");

                    b.HasKey("Id");

                    b.HasIndex("UserId");

                    b.ToTable("UserSongInteractions", (string)null);
                });

            modelBuilder.Entity("MusicRecommender.Models.Favorite", b =>
                {
                    b.HasOne("MusicRecommender.Models.User", "User")
                        .WithMany()
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("User");
                });

            modelBuilder.Entity("MusicRecommender.Models.MLTrainingData", b =>
                {
                    b.HasOne("MusicRecommender.Models.User", "User")
                        .WithMany()
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("User");
                });

            modelBuilder.Entity("MusicRecommender.Models.MLUserProfile", b =>
                {
                    b.HasOne("MusicRecommender.Models.User", "User")
                        .WithMany()
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("User");
                });

            modelBuilder.Entity("MusicRecommender.Models.Song", b =>
                {
                    b.HasOne("MusicRecommender.Models.User", "User")
                        .WithMany()
                        .HasForeignKey("UserId");

                    b.Navigation("User");
                });

            modelBuilder.Entity("MusicRecommender.Models.UserSongInteraction", b =>
                {
                    b.HasOne("MusicRecommender.Models.User", "User")
                        .WithMany()
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("User");
                });
#pragma warning restore 612, 618
        }
    }
}
