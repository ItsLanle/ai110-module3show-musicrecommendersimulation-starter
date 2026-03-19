"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs

# ---------------------------------------------------------------------------
# User profiles — 3 standard + 3 adversarial edge cases
# ---------------------------------------------------------------------------
PROFILES = [
    {
        "label": "High-Energy Pop",
        "prefs": {
            "favorite_genre":      "pop",
            "favorite_mood":       "happy",
            "target_energy":       0.90,
            "target_valence":      0.85,
            "target_tempo_bpm":    128.0,
            "target_danceability": 0.88,
        },
    },
    {
        "label": "Chill Lofi",
        "prefs": {
            "favorite_genre":      "lofi",
            "favorite_mood":       "chill",
            "target_energy":       0.35,
            "target_valence":      0.60,
            "target_tempo_bpm":    75.0,
            "target_danceability": 0.55,
        },
    },
    {
        "label": "Deep Intense Rock",
        "prefs": {
            "favorite_genre":      "rock",
            "favorite_mood":       "intense",
            "target_energy":       0.92,
            "target_valence":      0.45,
            "target_tempo_bpm":    150.0,
            "target_danceability": 0.65,
        },
    },
    # --- Adversarial / edge cases ---
    {
        "label": "EDGE: Conflicted (high energy + moody mood)",
        "prefs": {
            # Energy says party, mood says melancholy — can scoring handle the conflict?
            "favorite_genre":      "electronic",
            "favorite_mood":       "moody",
            "target_energy":       0.95,
            "target_valence":      0.30,
            "target_tempo_bpm":    140.0,
            "target_danceability": 0.85,
        },
    },
    {
        "label": "EDGE: Unknown Genre (reggaeton — not in dataset)",
        "prefs": {
            # No genre match is possible; scoring must fall back to other signals
            "favorite_genre":      "reggaeton",
            "favorite_mood":       "happy",
            "target_energy":       0.80,
            "target_valence":      0.75,
            "target_tempo_bpm":    100.0,
            "target_danceability": 0.80,
        },
    },
    {
        "label": "EDGE: Extreme BPM (target 200 BPM — beyond any song)",
        "prefs": {
            # Pushes tempo scoring to its floor for every song
            "favorite_genre":      "rock",
            "favorite_mood":       "intense",
            "target_energy":       0.90,
            "target_valence":      0.50,
            "target_tempo_bpm":    200.0,
            "target_danceability": 0.70,
        },
    },
]


def print_recommendations(label: str, recommendations: list) -> None:
    """Print a numbered, formatted block of recommendations for one profile."""
    print("\n" + "=" * 55)
    print(f"  Profile: {label}")
    print("=" * 55)
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{i}  {song['title']} — {song['artist']}")
        print(f"       Score : {score:.2f}")
        print(f"       Reason: {explanation}")
        print("  " + "-" * 53)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded {len(songs)} songs.\n")

    for profile in PROFILES:
        recs = recommend_songs(profile["prefs"], songs, k=5)
        print_recommendations(profile["label"], recs)

    # --- Diversity penalty demo ---
    print("\n" + "=" * 55)
    print("  DIVERSITY PENALTY DEMO  (artist=0.5, genre=0.6)")
    print("=" * 55)
    for profile in PROFILES[:3]:
        recs = recommend_songs(
            profile["prefs"], songs, k=5,
            artist_penalty=0.5,
            genre_penalty=0.6,
        )
        print_recommendations(f"{profile['label']} [diversity ON]", recs)


if __name__ == "__main__":
    main()
