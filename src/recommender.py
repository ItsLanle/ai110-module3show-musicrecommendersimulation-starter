import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Weights — must sum to 1.0
# ---------------------------------------------------------------------------
WEIGHTS = {
    "genre":        0.35,
    "mood":         0.25,
    "energy":       0.20,
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
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

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


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # Step 1 & 2: score every song using a list comprehension
    scored = [
        (song, score_song(song, user_prefs))
        for song in songs
    ]

    # Step 3: sort by score descending using a lambda key function
    scored.sort(key=lambda x: x[1], reverse=True)

    # Step 4: return top k as (song, score, explanation) tuples
    return [(song, score, f"{song['title']} scored {score}") for song, score in scored[:k]]
