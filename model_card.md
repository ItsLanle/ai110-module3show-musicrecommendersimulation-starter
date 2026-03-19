# 🎧 Model Card: Music Recommender Simulation

---

## 1. Model Name

**MusicMuse 1.0**

A simple rule-based music recommender that matches songs to a user's taste using weighted scoring.

---

## 2. Goal / Task

MusicMuse looks at what kind of music a user likes — their favorite genre, mood, and energy level — and returns the 5 songs from the catalog that best match those preferences.

It does not learn over time. It does not track listening history. It just scores every song against the user's stated preferences and picks the highest-scoring ones.

---

## 3. Data Used

- **Catalog size:** 20 songs
- **Features per song:** genre, mood, energy (0–1), tempo in BPM, valence (how positive it sounds), danceability, and acousticness
- **Genres represented:** lofi, pop, afrobeat, classical, country, electronic, rock, ambient, jazz, synthwave, indie pop, indie, folk
- **Moods represented:** happy, chill, relaxed, intense, moody, melancholic, energetic, focused, inspirational, upbeat

**Limits:**
- 8 out of 13 genres have only one song. That is not enough variety for users with those tastes.
- The dataset skews toward Western music styles. Genres like afrobeats, reggaeton, K-pop, or Latin music are missing or barely present.
- No song lyrics, language, or cultural context is included.

---

## 4. Algorithm Summary

The system scores each song from 0 to 1 based on how well it matches the user. Here is how each piece contributes:

| What is checked | How much it matters |
|---|---|
| Genre match | 17.5% — does the song's genre match the user's favorite? |
| Mood match | 22.5% — does the mood match? Related moods get half credit |
| Energy match | 40% — is the song's energy level close to what the user wants? |
| Valence match | 10% — does the positivity level match? |
| Tempo match | 5% — is the BPM close to the target? |
| Danceability match | 5% — is the danceability score close? |

Songs that match on more categories score higher. The top 5 scores are returned as recommendations.

For mood, the system uses groups — for example, "chill," "relaxed," and "focused" are treated as related. An exact match earns full points; a related match earns half.

---

## 5. Observed Behavior / Biases

**The dataset is too small.** With only 20 songs, 8 out of 13 genres have just one song each. If your favorite genre is rock or jazz, the system finds one good match and then has nothing else to offer in that style. It fills the rest of the list with whatever is closest in energy or mood, which often feels random.

**The same songs keep showing up.** Because the catalog is small, a handful of songs (like *Sunrise City* and *Lagos Sunrise*) score well across many different user profiles. This means two very different users might get nearly the same recommendations — that is a sign the system is not actually personalizing very well.

**High-energy users get fewer good matches.** Most songs in the dataset sit in the mid-energy range. If a user wants very high energy (above 0.85), only 3–4 songs qualify. The system ends up recommending those same tracks over and over with no variety.

**When preferences conflict, the system just picks a side.** If a user wants high energy but a sad mood, the system does not try to balance those — it just gives more points to whichever signal its weights favor. The user never asked for that trade-off, but the system makes it silently.

**Genre is still the biggest factor, even after the weight experiment.** Even at 17.5%, genre is the single largest weight. Users whose genre is missing from the dataset are penalized from the start, while users with popular genres (lofi, pop) almost always get better results. That is an unfair advantage based on taste, not quality.

---

## 6. Evaluation Process

I tested six different user profiles — three normal listeners and three tricky edge cases designed to find weaknesses.

**The three normal profiles were:**
- A happy pop fan who likes high energy and fast tempo
- A chill lofi listener who wants calm, quiet music to focus
- A rock fan who likes intense, loud, fast songs

**The three edge case profiles were:**
- A user who wanted high energy but a sad mood at the same time (conflicting signals)
- A user whose favorite genre (reggaeton) does not exist in the catalog at all
- A user who set their target tempo to 200 BPM, which no song in the dataset can reach

**What I looked for:** I checked whether the top 5 results felt like songs that person would actually want to hear, and whether the reasons made sense.

**What surprised me:** The lofi profile worked almost perfectly — the two lofi songs both scored 1.00 and felt like exactly the right picks. The rock profile also nailed #1. But things got strange after that.

**Why does Gym Hero keep showing up for Happy Pop fans?**
Think of it like a checklist. The system gives points for matching genre, mood, energy, tempo, and danceability. *Gym Hero* is a pop song tagged as "intense," not "happy." But it still earns partial points for being pop and having high energy. When the catalog only has two pop songs, *Gym Hero* is basically the runner-up by default — there is nothing else pop-flavored to compete with it. It is not that the system thinks *Gym Hero* is a happy song. It is that the system ran out of better options and *Gym Hero* came closest on the remaining signals. This is a dataset size problem more than a logic problem.

**The biggest surprise overall** was the conflicted profile. Before adjusting the weights, the system recommended an electronic song with no mood match at all to a user who said they wanted moody music — simply because the genre matched. After doubling the energy weight and trimming the genre weight, the actually moody songs moved to the top. That showed how much a single number in the weights can change what the system thinks a person wants.

---

## 7. Intended Use and Non-Intended Use

**What it is designed for:**
- A classroom exercise to explore how scoring and weighting work in recommendation systems
- Testing and experimenting with how changing weights affects results
- Learning how real apps like Spotify or Apple Music might think about matching music to listeners

**What it should NOT be used for:**
- A real product for actual users — the catalog is too small and the logic is too simple
- Making decisions about what music is "good" or "better" — the scores only reflect similarity to stated preferences, not quality
- Representing any real cultural or musical community — the dataset is too limited and biased toward certain styles

---

## 8. Ideas for Improvement

**1. Grow the dataset.** Adding 200+ songs across more genres — especially underrepresented ones like reggaeton, K-pop, Afrobeats, and Latin — would make the recommendations feel much more personal and varied.

**2. Add a diversity rule.** This has now been implemented as a diversity penalty. The `recommend_songs` function accepts `artist_penalty` and `genre_penalty` multipliers. Each time a song's artist or genre already appears in the selected results, its score is multiplied by the penalty — so the second lofi song gets its score × 0.6, the third would get × 0.6², and so on. This pushed variety into the top 5 without hard-blocking any genre.

**3. Learn from listening behavior.** Instead of asking users to fill out a preference form, track which songs they skip or replay and adjust the weights automatically over time. This is how real recommenders like Spotify work — they learn your taste rather than asking you to describe it.

---

## 9. Personal Reflection

**What was my biggest learning moment?**

My biggest learning moment was realizing that the weights decide everything. When I doubled the energy weight and cut the genre weight in half, the entire top result changed for one of my test profiles. A song that had nothing to do with the user's mood suddenly dropped out of first place, and the right song moved up. I had always thought of a recommender as something that "finds good songs." But really it is just a calculator — and whoever sets the numbers decides what "good" means.

**How did using AI tools help me, and when did I need to double-check them?**

AI tools helped me move faster. When I was stuck on how to write the scoring loop cleanly, the suggestion to use a list comprehension with a lambda sort key was exactly right and saved me time. The explanation of why certain songs kept ranking high also helped me connect the math to the real output.

But I did need to double-check one thing: when the weight changes were suggested, the numbers did not add up to 1.0. Doubling energy added 0.20 but halving genre only freed up 0.175 — a gap of 0.025 that would have quietly broken the scoring. I had to catch that myself and trim the mood weight slightly to fix it. That reminded me that AI suggestions are a starting point, not a final answer. You still have to check the math.

**What surprised me about how a simple algorithm can still "feel" like a recommendation?**

I was surprised by how convincing the output looked even though the logic is so basic. When the lofi profile returned *Library Rain* and *Midnight Coding* both at score 1.00, it genuinely felt like the system "got it." The terminal printout with numbered results, scores, and reasons made it look polished and smart. But underneath it is just multiplication and sorting. The feeling of intelligence came from the formatting and the fact that the answers happened to be correct — not from any real understanding of music.

**What would I try next if I extended this project?**

I would try three things. First, I would expand the song catalog to at least 200 songs so the recommendations actually vary between users. Second, I already built a diversity penalty — but I would tune the penalty values more carefully and test what happens when it is very strong (close to 0.0) versus very weak (close to 1.0). Third, I would try replacing the fixed weights with something that adjusts based on which songs a user skips or replays — moving from a system that asks "what do you like?" to one that learns "what do you actually listen to."

---

## Challenge 3 Reflection — Diversity and Fairness Logic

Building the diversity penalty taught me something I did not expect: fairness and accuracy can conflict. Before the penalty, the Chill Lofi profile was technically "accurate" — all three lofi songs scored near 1.00 and they were exactly what the user asked for. But the list felt wrong because it was just the same genre three times in a row.

The penalty fixed that by pushing the second and third lofi songs down and surfacing ambient, jazz, and classical tracks instead. But those songs were not what the user originally asked for. The system got more diverse but less accurate at the same time. That trade-off is real in every recommender — Spotify and YouTube make the same choice constantly when they mix in new artists so you do not get stuck in a bubble.

The most interesting design decision was using a multiplier instead of a hard block. A hard limit like "no more than one lofi song" is simple but blunt — it would block a lofi song even if nothing else comes close. A multiplier just makes repeated genres less competitive, so they can still appear if they are truly the best remaining option. That feels more honest to what the user actually wants.

The terminal output made the effect easy to see. The `[diversity ON]` label next to each profile and the `"diversity penalty applied"` reason tag in the results made it clear exactly which songs were promoted and which were held back — and why.
