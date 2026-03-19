"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Starter example profile
    user_prefs = {
    "favorite_genre":    "afrobeat",
    "acceptable_genres": ["afrobeat", "dancehall", "r&b", "pop"],
    "disliked_genres":   ["classical", "rock"],
    "favorite_mood":     "happy",
    "acceptable_moods":  ["happy", "upbeat", "energetic"],
    "context":           "gym",

    "target_energy":       0.85,
    "energy_min":          0.70,       # hard floor — nothing below this
    "target_tempo_bpm":    110.0,
    "tempo_range":         (95, 135),  # acceptable BPM window
    "target_valence":      0.80,
    "target_danceability": 0.88,
    "target_acousticness": 0.20,

    "discovery_factor":    0.3,        # somewhat open to new genres
}


    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 50)
    print("  🎵  TOP SONG RECOMMENDATIONS")
    print("=" * 50)

    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{i}  {song['title']} — {song['artist']}")
        print(f"    Score : {score:.2f}")
        print(f"    Reason: {explanation}")
        print("-" * 50)


if __name__ == "__main__":
    main()
