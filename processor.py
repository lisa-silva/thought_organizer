"""Text processing helpers for the thought organizer CLI."""

from __future__ import annotations

import re
from string import capwords


FILLER_WORDS = {
    "actually",
    "basically",
    "i mean",
    "kind of",
    "literally",
    "okay",
    "oh my gosh",
    "oh yeah",
    "so",
    "sort of",
    "uh",
    "um",
    "well",
    "you know",
}

COMMON_CORRECTIONS = {
    "dont": "do not",
    "can't": "cannot",
    "cant": "cannot",
    "couldnt": "could not",
    "didnt": "did not",
    "doesnt": "does not",
    "gonna": "going to",
    "gotta": "need to",
    "im": "I am",
    "ive": "I have",
    "shouldnt": "should not",
    "thats": "that is",
    "theres": "there is",
    "wanna": "want to",
    "wasnt": "was not",
    "werent": "were not",
    "wont": "will not",
}

PROFESSIONAL_REPLACEMENTS = {
    "a lot of": "many",
    "ASAP": "as soon as possible",
    "asap": "as soon as possible",
    "boss": "manager",
    "cool": "useful",
    "fix": "resolve",
    "full of words that do not make sense": "verbose and may be unclear",
    "full of words": "verbose",
    "get": "obtain",
    "huge": "lengthy",
    "i want it to be professional": "I would like the message to be presented in a professional tone",
    "mess": "issue",
    "do not make sense": "may be unclear",
    "right before it": "as a result",
    "right before you know it": "as a result",
    "spit out": "produce",
    "stuff": "items",
    "thing": "matter",
    "things": "matters",
}

CAPITALIZED_TERMS = {
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
    "january",
    "february",
    "march",
    "april",
    "copilot",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
}

REMINDER_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}


def clean_text(raw_text: str) -> str:
    """Clean messy input and rewrite it in a professional tone."""
    text = (raw_text or "").strip()
    if not text:
        return ""

    text = _normalize_spacing(text)
    text = _apply_phrase_replacements(text, PROFESSIONAL_REPLACEMENTS)
    text = _apply_phrase_replacements(text, COMMON_CORRECTIONS)
    text = _remove_fillers(text)
    text = _remove_dictation_asides(text)
    text = _deduplicate_repeated_words(text)
    text = _normalize_spacing(text)
    text = _format_sentences(text)
    text = _capitalize_known_terms(text)
    text = _split_long_sentence(text)

    return text


def generate_professional_version(raw_text: str) -> str:
    """Create a copy-ready professional rewrite from raw dictation."""
    return clean_text(raw_text)


def generate_short_reminder(cleaned_text: str) -> str:
    """Return a concise 5-10 word reminder phrase for an entry."""
    words = re.findall(r"[A-Za-z0-9']+", cleaned_text)
    keywords = [
        word
        for word in words
        if len(word) > 2 and word.lower() not in REMINDER_STOPWORDS
    ]

    if not keywords:
        keywords = words

    reminder_words = keywords[:10]
    if len(reminder_words) < 5:
        reminder_words = words[:10]

    reminder = " ".join(reminder_words[:10]).strip()
    return capwords(reminder) if reminder else "Review New Thought"


def _normalize_spacing(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    return text.strip()


def _remove_fillers(text: str) -> str:
    for filler in sorted(FILLER_WORDS, key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(filler)}\b,?\s*", "", text, flags=re.IGNORECASE)
    return text


def _remove_dictation_asides(text: str) -> str:
    aside_patterns = [
        r"\bsorry for the words\b,?\s*",
        r"\bsorry\b,?\s*",
        r"\boops\b,?\s*",
        r"\bmy mouth does not talk that way\b,?\s*",
    ]
    for pattern in aside_patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text


def _deduplicate_repeated_words(text: str) -> str:
    return re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", text, flags=re.IGNORECASE)


def _apply_phrase_replacements(text: str, replacements: dict[str, str]) -> str:
    for source, target in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        text = re.sub(rf"\b{re.escape(source)}\b", target, text, flags=re.IGNORECASE)
    return text


def _format_sentences(text: str) -> str:
    if not re.search(r"[.!?]$", text):
        text += "."

    parts = re.split(r"([.!?]\s*)", text)
    sentences: list[str] = []
    for index in range(0, len(parts), 2):
        sentence = parts[index].strip()
        punctuation = parts[index + 1].strip() if index + 1 < len(parts) else "."
        if not sentence:
            continue
        sentence = sentence[0].upper() + sentence[1:]
        sentence = re.sub(r"\bi\b", "I", sentence)
        sentences.append(f"{sentence}{punctuation}")

    return " ".join(sentences)


def _capitalize_known_terms(text: str) -> str:
    for term in CAPITALIZED_TERMS:
        text = re.sub(rf"\b{term}\b", term.capitalize(), text, flags=re.IGNORECASE)
    return text


def _split_long_sentence(text: str) -> str:
    """Break common voice-dictation run-ons into cleaner sentence boundaries."""
    text = re.sub(r"\bbut unfortunately\b", "However,", text, flags=re.IGNORECASE)
    text = re.sub(r"\bso that is why\b", "That is why", text, flags=re.IGNORECASE)
    text = re.sub(r"\band I want it to be\b", "I want it to be", text, flags=re.IGNORECASE)
    text = re.sub(r"\band I need it to\b", "I need it to", text, flags=re.IGNORECASE)
    text = re.sub(r"\bcan we can do that\b", "Can we do that", text, flags=re.IGNORECASE)
    text = re.sub(r"\bvoice dictating I want\b", "voice dictating. I want", text, flags=re.IGNORECASE)
    text = re.sub(r"\bvoice dictating I need\b", "voice dictating. I need", text, flags=re.IGNORECASE)
    return _normalize_spacing(text)
