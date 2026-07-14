# Thought Organizer

A small Python app that turns messy raw thoughts into organized spreadsheet rows. It includes both a command-line interface and a Streamlit interface styled with the 2031 Cognitive Luminescence palette.

## Files

- `app.py` runs the command-line interface, and also opens the Streamlit UI when launched with `streamlit run app.py`.
- `ui.py` runs the Streamlit interface.
- `processor.py` cleans raw text and creates a short reminder.
- `router.py` routes cleaned text into a layer and category.
- `.streamlit/theme.toml` documents the requested palette theme.
- `.streamlit/config.toml` applies the global Streamlit theme.
- `config/categories.json` stores keyword mappings.
- `storage/data.csv` stores saved entries.

## How To Run The CLI

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

## How To Run The Streamlit UI

Install Streamlit if needed:

```bash
pip install streamlit
```

Then run:

```bash
streamlit run app.py
```

You can also run `streamlit run ui.py` directly. The requested theme definition lives in `.streamlit/theme.toml`, and Streamlit's standard global theme settings live in `.streamlit/config.toml`. `ui.py` injects the same palette through HTML/CSS so the interface reflects the theme at runtime. If the app is already running while you edit theme values, restart the Streamlit server so the page reloads the styling.

## 2031 Cognitive Luminescence Palette

The Streamlit UI uses the full 2031 palette:

- Luminescent Neutrals: `spectral_mist` `#EDEBFA`, `quantum_pearl` `#F7F5FF`, `soft_halo_grey` `#D9D7E8`
- Spectral Intelligence accents: `infra_lilac` `#C7A7FF`, `cyan_aurora` `#7BE8FF`, `rose_plasma` `#FFB7D9`, `neo_gold` `#F7D774`
- Cognitive Flow gradients: `gradient_flow`, `gradient_emotion`, and `gradient_identity`

The global Streamlit theme is:

```toml
[theme]
primaryColor = "#C7A7FF"
backgroundColor = "#EDEBFA"
secondaryBackgroundColor = "#F7F5FF"
textColor = "#050505"
font = "Inter"
```

## Layer-Based Color Logic

The Streamlit Layer View and spreadsheet chips use these colors:

- Strategy: `infra_lilac` `#C7A7FF`
- Ideas: `cyan_aurora` `#7BE8FF`
- Tasks: `neo_gold` `#F7D774`
- Research: `soft_halo_grey` `#D9D7E8`
- Personal Notes: `rose_plasma` `#FFB7D9`
- Unsorted: neutral spectral grey `#BEBECF`

In Layer View, each layer button uses its assigned color. The selected layer is highlighted with `gradient_identity`.

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
