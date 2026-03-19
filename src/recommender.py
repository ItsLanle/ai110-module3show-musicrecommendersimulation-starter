import csv
from collections import defaultdict
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Weights — must sum to 1.0
# EXPERIMENT: energy doubled (0.20→0.40), genre halved (0.35→0.175).
#             mood reduced 0.25→0.225 to keep total = 1.0.
# ---------------------------------------------------------------------------
WEIGHTS = {
    "genre":        0.175,  # CHANGED: halved from 0.35
    "mood":         0.225,  # CHANGED: trimmed from 0.25 to keep sum = 1.0
    "energy":       0.40,   # CHANGED: doubled from 0.20
    "valence":      0.10,
    "tempo_bpm":    0.05,
    "danceability": 0.05,
}

# ---------------------------------------------------------------------------
# Mood groups — songs with related moods earn partial mood credit
# ---------------------------------------------------------------------------
MOOD_GROUPS = {
    "happy":   ["happy", "upbeat"],
    "chill":   ["chill", "relaxed", "focused"],
    "intense": ["intense", "energetic"],
    "moody":   ["moody", "melancholic"],
}

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Store the song catalog for use in recommendations."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs ranked by score for the given user profile."""
        user_prefs = {
            "favorite_genre":      user.favorite_genre,
            "favorite_mood":       user.favorite_mood,
            "target_energy":       user.target_energy,
            "target_valence":      0.5,
            "target_tempo_bpm":    120.0,
            "target_danceability": 0.5,
        }
        scored = sorted(
            self.songs,
            key=lambda song: score_song(vars(song), user_prefs),
            reverse=True,
        )
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a sentence explaining why a song was recommended to a user."""
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"genre matches ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"mood matches ({song.mood})")
        elif are_moods_related(song.mood, user.favorite_mood):
            reasons.append(f"mood is related ({song.mood} ~ {user.favorite_mood})")
        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff <= 0.2:
            reasons.append(f"energy is close ({song.energy:.2f} vs {user.target_energy:.2f})")
        if not reasons:
            return f"{song.title} by {song.artist} is a general recommendation."
        return f"{song.title} by {song.artist}: {', '.join(reasons)}."

def are_moods_related(mood_a: str, mood_b: str) -> bool:
    """Return True if two moods belong to the same mood group."""
    for group in MOOD_GROUPS.values():
        if mood_a in group and mood_b in group:
            return True
    return False


def score_song(song: Dict, user_prefs: Dict) -> float:
    """
    Scoring Rule: evaluates ONE song against ONE user preference dictionary.
    Returns a score between 0.0 and 1.0.
    """
    score = 0.0

    # Genre — binary match (35%)
    if song["genre"] == user_prefs["favorite_genre"]:
        score += WEIGHTS["genre"]

    # Mood — tiered match (25%)
    if song["mood"] == user_prefs["favorite_mood"]:
        score += WEIGHTS["mood"]
    elif are_moods_related(song["mood"], user_prefs["favorite_mood"]):
        score += WEIGHTS["mood"] * 0.5

    # Energy — proximity scoring (20%)
    score += WEIGHTS["energy"] * (1 - (song["energy"] - user_prefs["target_energy"]) ** 2)

    # Valence — proximity scoring (10%)
    score += WEIGHTS["valence"] * (1 - (song["valence"] - user_prefs["target_valence"]) ** 2)

    # Tempo — proximity scoring, normalized to 0-1 using 200 BPM as max (5%)
    tempo_diff = abs(song["tempo_bpm"] - user_prefs["target_tempo_bpm"]) / 200
    score += WEIGHTS["tempo_bpm"] * (1 - tempo_diff ** 2)

    # Danceability — proximity scoring (5%)
    score += WEIGHTS["danceability"] * (1 - (song["danceability"] - user_prefs["target_danceability"]) ** 2)

    return round(score, 4)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def build_explanation(song: Dict, user_prefs: Dict, penalized: bool = False) -> str:
    """Build a human-readable explanation of why a song was recommended."""
    reasons = []

    if song["genre"] == user_prefs["favorite_genre"]:
        reasons.append(f"genre matched ({song['genre']})")

    if song["mood"] == user_prefs["favorite_mood"]:
        reasons.append(f"mood matched ({song['mood']})")
    elif are_moods_related(song["mood"], user_prefs["favorite_mood"]):
        reasons.append(f"related mood ({song['mood']} ~ {user_prefs['favorite_mood']})")

    energy_diff = abs(song["energy"] - user_prefs["target_energy"])
    if energy_diff <= 0.2:
        reasons.append(f"energy close ({song['energy']:.2f} vs {user_prefs['target_energy']:.2f})")

    tempo_diff = abs(song["tempo_bpm"] - user_prefs["target_tempo_bpm"]) / 200
    if tempo_diff <= 0.15:
        reasons.append(f"tempo close ({song['tempo_bpm']:.0f} BPM)")

    if penalized:
        reasons.append("diversity penalty applied")

    if not reasons:
        return "general match"
    return ", ".join(reasons)


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    artist_penalty: float = 1.0,
    genre_penalty: float = 1.0,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    artist_penalty / genre_penalty: multiplier applied each time a song's
    artist or genre is already represented in the selected results.
    1.0 = no penalty (default); 0.5 = halve the score on each repeat.
    """
    # Step 1: score every song once
    candidates = [(song, score_song(song, user_prefs)) for song in songs]

    # Step 2: greedy selection with compounding diversity penalty
    selected = []
    artist_counts: Dict[str, int] = defaultdict(int)
    genre_counts:  Dict[str, int] = defaultdict(int)

    for _ in range(min(k, len(candidates))):
        # Apply accumulated penalties to every remaining candidate
        penalized_candidates = [
            (song, base * (artist_penalty ** artist_counts[song["artist"]])
                       * (genre_penalty  ** genre_counts[song["genre"]]))
            for song, base in candidates
        ]

        # Pick the highest effective score
        best_song, best_score = max(penalized_candidates, key=lambda x: x[1])

        # Record selection and update counts
        selected.append((best_song, best_score))
        artist_counts[best_song["artist"]] += 1
        genre_counts[best_song["genre"]]   += 1

        # Remove the selected song from the candidate pool
        candidates = [(s, sc) for s, sc in candidates if s["id"] != best_song["id"]]

    # Step 3: return (song, effective_score, explanation) tuples
    return [
        (
            song,
            round(score, 4),
            build_explanation(
                song, user_prefs,
                penalized=(round(score, 4) < score_song(song, user_prefs)),
            ),
        )
        for song, score in selected
    ]
