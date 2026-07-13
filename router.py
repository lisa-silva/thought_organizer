"""Keyword-based routing for thought organizer entries."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


CONFIG_PATH = Path(__file__).parent / "config" / "categories.json"
UNSORTED = "Unsorted"


def load_category_mappings(config_path: Path | str = CONFIG_PATH) -> dict[str, dict[str, list[str]]]:
    """Load layer/category keyword mappings from JSON."""
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as file:
        data: Any = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("categories.json must contain an object of layers.")

    return data


def route_entry(text: str, mappings: dict[str, dict[str, list[str]]] | None = None) -> dict[str, str]:
    """Detect the best layer and category for cleaned text."""
    mappings = mappings or load_category_mappings()
    normalized_text = text.lower()

    best_layer = UNSORTED
    best_category = UNSORTED
    best_score = 0

    for layer, categories in mappings.items():
        for category, keywords in categories.items():
            score = _score_keywords(normalized_text, keywords)
            if score > best_score:
                best_layer = layer
                best_category = category
                best_score = score

    return {
        "layer": best_layer,
        "category": best_category,
    }


def _score_keywords(text: str, keywords: list[str]) -> int:
    score = 0
    for keyword in keywords:
        normalized_keyword = keyword.lower().strip()
        if not normalized_keyword:
            continue

        if " " in normalized_keyword:
            if normalized_keyword in text:
                score += 3
            continue

        if re.search(rf"\b{re.escape(normalized_keyword)}\b", text):
            score += 1

    return score
