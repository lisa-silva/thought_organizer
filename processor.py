"""Text processing helpers for the thought organizer CLI."""

from __future__ import annotations

import re
from string import capwords


FILLER_WORDS = {
    "actually",
    "basically",
    "i mean",
    "kind of",
    "like",
    "literally",
    "okay",
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
    "get": "obtain",
    "mess": "issue",
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
    "may",
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
    text = _apply_phrase_replacements(text, COMMON_CORRECTIONS)
    text = _remove_fillers(text)
    text = _apply_phrase_replacements(text, PROFESSIONAL_REPLACEMENTS)
    text = _normalize_spacing(text)
    text = _format_sentences(text)
    text = _capitalize_known_terms(text)

    return text


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
