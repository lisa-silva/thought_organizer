# Thought Organizer

A small command-line Python app that turns messy raw thoughts into organized spreadsheet rows.

## Files

- `app.py` runs the command-line interface.
- `processor.py` cleans raw text and creates a short reminder.
- `router.py` routes cleaned text into a layer and category.
- `config/categories.json` stores keyword mappings.
- `storage/data.csv` stores saved entries.

## How To Run

From this folder, run:

```bash
python app.py
```

Paste or type your raw thought. Press Enter on an empty line to save it.

The app will:

1. Clean grammar, spelling, filler words, and informal phrasing.
2. Generate a 5-10 word reminder.
3. Route the thought into a layer and category.
4. Append the result to `storage/data.csv`.

## How To Add Categories

Open `config/categories.json`. The structure is:

```json
{
  "Layer Name": {
    "Category Name": [
      "keyword",
      "another keyword"
    ]
  }
}
```

To add a new category, add it under the layer where it belongs:

```json
{
  "Tasks": {
    "Invoices": [
      "invoice",
      "billing",
      "payment"
    ]
  }
}
```

The router checks the cleaned thought for these keywords. Multi-word keywords, such as `follow up`, receive extra weight. If no keyword matches, the entry is routed to `Unsorted`.

## Example

Input:

```text
um i need to follow up with sam about the roadmap meeting and maybe send the notes by friday
```

Output:

```text
Layer: Tasks
Category: Follow Up
Reminder: Need Follow Up Sam Roadmap Meeting Send Notes Friday
Cleaned text: I need to follow up with sam about the roadmap meeting and maybe send the notes by friday.
```

CSV row:

```csv
timestamp,layer,category,short_reminder,full_cleaned_text
2026-07-13T14:30:00,Tasks,Follow Up,Need Follow Up Sam Roadmap Meeting Send Notes Friday,I need to follow up with sam about the roadmap meeting and maybe send the notes by friday.
```
