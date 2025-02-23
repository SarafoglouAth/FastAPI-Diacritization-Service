from fastapi import FastAPI, Body
import json
import os
import difflib
import string
from Levenshtein import distance as levenshtein_distance
app = FastAPI()
PRE_COMPUTED_FILE = "precomputed_accents.json"

# Create/load precomputed mapping
if not os.path.exists(PRE_COMPUTED_FILE):
    print("Generating accent map...")
    accent_map = {}

    if os.path.exists("greek_dict.dic"):
        with open("greek_dict.dic", "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                key = word.lower().translate(str.maketrans(
                    "άέήίόύώΐΰ", "αεηιουωιυ"
                ))
                accent_map[key] = word

    with open(PRE_COMPUTED_FILE, "w", encoding="utf-8") as f:
        json.dump(accent_map, f, ensure_ascii=False)

# Load precomputed data
with open(PRE_COMPUTED_FILE, "r", encoding="utf-8") as f:
    ACCENT_MAP = json.load(f)
    print(f"Loaded {len(ACCENT_MAP)} precomputed accents")


def clean_word(word):
    """Removes punctuation from the end of a word but keeps it separately."""
    if len(word) == 0:
        return word, ""
    if word[-1] in string.punctuation:
        return word[:-1], word[-1]  # Returns (cleaned word, punctuation)
    return word, ""  # No punctuation found
 
def find_closest_matches(word, accent_map, n=8):
    """Find the closest matches for a word, prioritizing words with similar diacritics and structure."""
    
    # Preserve original case to restore it later
    original_word = word

    # Convert input word to lowercase for searching
    key = word.lower().translate(str.maketrans(
        "άέήίόύώΐΰ", "αεηιουωιυ"
    ))

    # Convert dictionary keys to lowercase for accurate searching
    lower_accent_map = {k.lower(): v for k, v in accent_map.items()}

    # Step 1: Get same-length candidates first
    same_length_candidates = [w for w in lower_accent_map.keys() if len(w) == len(key)]
    
    # Use only same-length candidates if they exist, otherwise use all words
    search_space = same_length_candidates if same_length_candidates else lower_accent_map.keys()

    # Step 2: Compute similarity scores
    candidates = []
    for candidate in search_space:
        diacritized_candidate = lower_accent_map.get(candidate, candidate)

        # Calculate similarity using both difflib and Levenshtein distance
        similarity = difflib.SequenceMatcher(None, key, candidate).ratio()
        edit_distance = levenshtein_distance(key, candidate)

        # Prioritize candidates with similar diacritics
        diacritic_bonus = 1 if any(c in diacritized_candidate for c in "άέήίόύώΐΰ") else 0

        # Rank based on a combination of similarity, edit distance, and diacritic presence
        score = similarity - (edit_distance * 0.1) + diacritic_bonus  # Weighted scoring

        candidates.append((diacritized_candidate, score))

    # Step 3: Sort candidates by highest score
    sorted_candidates = sorted(candidates, key=lambda x: x[1], reverse=True)

    # Step 4: Restore original capitalization before returning
    final_suggestions = []
    for match in sorted_candidates[:n]:
        suggestion = match[0]

        # If the original word was capitalized, capitalize the suggestion
        if original_word.istitle():
            suggestion = suggestion.capitalize()
        elif original_word.isupper():
            suggestion = suggestion.upper()

        final_suggestions.append(suggestion)

    return final_suggestions or [word]

@app.post("/diacritize/", summary="Diacritize text", operation_id="diacritizeText")
async def diacritize_text(text: str = Body(...)):
    words = text.split()
    results = []
    capitalize_next = True  # Capitalize first word

    for word in words:
        base_word, punctuation = clean_word(word)

        # Process the base word to get accent suggestions
        matched = find_closest_matches(base_word, ACCENT_MAP)

        # Apply capitalization to suggestions if needed
        if capitalize_next:
            # Capitalize the first letter of each suggestion's base word
            capitalized_matched = []
            for s in matched:
                if s:  # Check if s is not empty
                    capitalized_s = s[0].upper() + s[1:]
                else:
                    capitalized_s = s
                capitalized_matched.append(capitalized_s)
            # Combine with punctuation
            suggestions = [s + punctuation for s in capitalized_matched]
        else:
            # Combine with punctuation without capitalization
            suggestions = [s + punctuation for s in matched]

        # Create the entry for this word
        entry = {
            "original": word,
            "suggestions": suggestions
        }
        results.append(entry)

        # Update capitalize_next for the next word
        capitalize_next = punctuation in ('.', '?')

    return {
        "original": text,
        "formatted": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)