"""Emotion scoring functionality for Casey conversations."""

# Emotion keywords mapping
EMOTION_KEYWORDS = {
    "frustrated": [
        "frustrated",
        "annoyed",
        "irritating",
        "redo",
        "pain",
        "stuck",
        "blocked",
    ],
    "concerned": ["worried", "concerned", "anxious", "unsure", "uncertain"],
    "confident": ["confident", "sure", "certain", "ready", "good"],
    "excited": ["excited", "eager", "enthusiastic", "can't wait", "love"],
    "tired": ["tired", "exhausted", "overwhelmed", "burned out"],
    "confused": ["confused", "unclear", "don't understand", "lost"],
}


def score_emotion(text: str) -> str:
    """Score the emotional tone of text and return the dominant emotion.

    Args:
        text: Input text to analyze

    Returns:
        String representing the dominant emotion, or 'neutral' if none detected
    """
    if not text:
        return "neutral"

    text_lower = text.lower()
    scores = {}

    # Calculate scores for each emotion
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1
        scores[emotion] = score

    # Find dominant emotion
    max_score = max(scores.values()) if scores else 0
    if max_score == 0:
        return "neutral"

    # Return emotion with highest score
    dominant_emotion = max(scores.items(), key=lambda x: x[1])[0]
    return dominant_emotion


def get_emotion_scores(text: str) -> dict[str, float]:
    """Get detailed emotion scores for text.

    Args:
        text: Input text to analyze

    Returns:
        Dictionary mapping emotion names to normalized scores (0.0-1.0)
    """
    if not text:
        return dict.fromkeys(EMOTION_KEYWORDS.keys(), 0.0)

    text_lower = text.lower()
    scores = {}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        hits = sum(1 for keyword in keywords if keyword in text_lower)
        # Normalize by number of keywords for this emotion
        normalized_score = min(hits / len(keywords), 1.0)
        scores[emotion] = normalized_score

    return scores
