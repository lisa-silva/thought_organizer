"""Command-line app for organizing raw thoughts into a CSV spreadsheet."""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

from processor import clean_text, generate_short_reminder
from router import route_entry


DATA_PATH = Path(__file__).parent / "storage" / "data.csv"
CSV_COLUMNS = [
    "timestamp",
    "layer",
    "category",
    "short_reminder",
    "full_cleaned_text",
]


def main() -> None:
    """Prompt for a thought, process it, route it, and store it."""
    print("Thought Organizer")
    print("Enter a raw thought. Press Enter on an empty line to finish.\n")

    raw_text = _read_multiline_input()
    if not raw_text.strip():
        print("No input provided. Nothing was saved.")
        return

    cleaned_text = clean_text(raw_text)
    short_reminder = generate_short_reminder(cleaned_text)
    routing = route_entry(cleaned_text)

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "layer": routing["layer"],
        "category": routing["category"],
        "short_reminder": short_reminder,
        "full_cleaned_text": cleaned_text,
    }

    append_entry(row)
    _print_results(row)


def append_entry(row: dict[str, str], data_path: Path = DATA_PATH) -> None:
    """Append one processed entry to the CSV, creating headers if needed."""
    data_path.parent.mkdir(parents=True, exist_ok=True)
    should_write_header = not data_path.exists() or data_path.stat().st_size == 0

    with data_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        if should_write_header:
            writer.writeheader()
        writer.writerow(row)


def _read_multiline_input() -> str:
    lines: list[str] = []
    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line)
    return " ".join(lines)


def _print_results(row: dict[str, str]) -> None:
    print("\nSaved thought:")
    print(f"Layer: {row['layer']}")
    print(f"Category: {row['category']}")
    print(f"Reminder: {row['short_reminder']}")
    print(f"Polished professional version: {row['full_cleaned_text']}")
    print(f"CSV: {DATA_PATH}")


def _running_in_streamlit() -> bool:
    """Return True when app.py is launched with `streamlit run app.py`."""
    if "streamlit" not in sys.modules:
        return False

    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
    except Exception:
        return False

    return get_script_run_ctx() is not None


if __name__ == "__main__":
    if _running_in_streamlit():
        from ui import main as streamlit_main

        streamlit_main()
    else:
        main()
