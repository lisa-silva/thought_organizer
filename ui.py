"""Streamlit UI for the Thought Organizer."""

from __future__ import annotations

import csv
import html
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import streamlit as st

from app import CSV_COLUMNS, DATA_PATH, append_entry
from processor import clean_text, generate_short_reminder
from router import route_entry


PALETTE = {
    "spectral_mist": "#EDEBFA",
    "quantum_pearl": "#F7F5FF",
    "soft_halo_grey": "#D9D7E8",
    "infra_lilac": "#C7A7FF",
    "cyan_aurora": "#7BE8FF",
    "rose_plasma": "#FFB7D9",
    "neo_gold": "#F7D774",
    "text": "#050505",
    "unsorted": "#BEBECF",
}

GRADIENTS = {
    "gradient_flow": "linear-gradient(90deg, #EDEBFA, #C7A7FF, #7BE8FF)",
    "gradient_emotion": "linear-gradient(90deg, #F7F5FF, #FFB7D9, #F7D774)",
    "gradient_identity": "linear-gradient(90deg, #D9D7E8, #C7A7FF, #F7D774)",
}

LAYER_COLORS = {
    "Strategy": PALETTE["infra_lilac"],
    "Ideas": PALETTE["cyan_aurora"],
    "Tasks": PALETTE["neo_gold"],
    "Research": PALETTE["soft_halo_grey"],
    "Personal Notes": PALETTE["rose_plasma"],
    "Unsorted": PALETTE["unsorted"],
}


def main() -> None:
    st.set_page_config(
        page_title="Thought Organizer",
        layout="wide",
    )
    inject_palette_css()

    selected_layer = get_selected_layer()
    rows = read_entries()

    render_header()
    render_input_panel()
    render_divider()
    render_layer_view(rows, selected_layer)
    render_table(rows, selected_layer)


def inject_palette_css() -> None:
    """Inject the full 2031 Cognitive Luminescence palette into Streamlit."""
    st.markdown(
        f"""
        <style>
            :root {{
                --spectral-mist: {PALETTE["spectral_mist"]};
                --quantum-pearl: {PALETTE["quantum_pearl"]};
                --soft-halo-grey: {PALETTE["soft_halo_grey"]};
                --infra-lilac: {PALETTE["infra_lilac"]};
                --cyan-aurora: {PALETTE["cyan_aurora"]};
                --rose-plasma: {PALETTE["rose_plasma"]};
                --neo-gold: {PALETTE["neo_gold"]};
                --text-color: {PALETTE["text"]};
                --unsorted: {PALETTE["unsorted"]};
                --gradient-flow: {GRADIENTS["gradient_flow"]};
                --gradient-emotion: {GRADIENTS["gradient_emotion"]};
                --gradient-identity: {GRADIENTS["gradient_identity"]};
            }}

            .stApp {{
                background: var(--spectral-mist);
                color: var(--text-color);
                font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }}

            .block-container {{
                padding-top: 2rem;
                padding-bottom: 3rem;
            }}

            .lum-card {{
                background: rgba(247, 245, 255, 0.92);
                border: 1px solid rgba(199, 167, 255, 0.55);
                border-radius: 8px;
                box-shadow: 0 18px 45px rgba(5, 5, 5, 0.08);
                margin: 1rem 0;
                padding: 1.25rem;
            }}

            .gradient-header {{
                background: var(--gradient-flow);
                border-radius: 8px;
                box-shadow: 0 16px 38px rgba(5, 5, 5, 0.1);
                color: var(--text-color);
                margin-bottom: 1rem;
                padding: 1.5rem;
            }}

            .gradient-header h1 {{
                font-size: clamp(2rem, 5vw, 4rem);
                letter-spacing: 0;
                line-height: 1;
                margin: 0;
            }}

            .gradient-header p {{
                font-size: 1.05rem;
                margin: 0.65rem 0 0;
                max-width: 58rem;
            }}

            .section-divider {{
                background: var(--gradient-emotion);
                border-radius: 999px;
                height: 8px;
                margin: 1.75rem 0 1.25rem;
            }}

            div.stButton > button,
            div.stFormSubmitButton > button {{
                background: var(--infra-lilac);
                border: 1px solid rgba(5, 5, 5, 0.14);
                border-radius: 8px;
                color: var(--text-color);
                font-weight: 700;
            }}

            div.stButton > button:hover,
            div.stFormSubmitButton > button:hover {{
                background: var(--cyan-aurora);
                border-color: rgba(5, 5, 5, 0.2);
                color: var(--text-color);
            }}

            .button-primary {{ background: var(--infra-lilac); }}
            .button-secondary {{ background: var(--cyan-aurora); }}
            .button-success {{ background: var(--neo-gold); }}
            .button-warning {{ background: var(--rose-plasma); }}

            .layer-buttons {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.65rem;
                margin-top: 0.75rem;
            }}

            .layer-button {{
                border: 1px solid rgba(5, 5, 5, 0.16);
                border-radius: 8px;
                color: var(--text-color) !important;
                display: inline-flex;
                font-weight: 800;
                min-height: 42px;
                padding: 0.65rem 0.9rem;
                text-decoration: none !important;
            }}

            .layer-button.selected {{
                background: var(--gradient-identity) !important;
                box-shadow: 0 10px 28px rgba(5, 5, 5, 0.16);
            }}

            .layer-chip {{
                border-radius: 999px;
                color: var(--text-color);
                display: inline-block;
                font-size: 0.85rem;
                font-weight: 800;
                padding: 0.25rem 0.65rem;
                white-space: nowrap;
            }}

            .thought-table {{
                border-collapse: collapse;
                overflow: hidden;
                width: 100%;
            }}

            .thought-table th {{
                background: var(--quantum-pearl);
                color: var(--infra-lilac);
                font-weight: 900;
                padding: 0.8rem;
                text-align: left;
            }}

            .thought-table td {{
                background: var(--spectral-mist);
                border-top: 1px solid rgba(5, 5, 5, 0.08);
                padding: 0.75rem 0.8rem;
                vertical-align: top;
            }}

            .thought-table tr:hover td {{
                background: var(--soft-halo-grey);
            }}

            .empty-state {{
                background: var(--quantum-pearl);
                border: 1px dashed var(--soft-halo-grey);
                border-radius: 8px;
                padding: 1rem;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <section class="gradient-header">
            <h1>Thought Organizer</h1>
            <p>2031 Cognitive Luminescence</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_input_panel() -> None:
    st.markdown('<section class="lum-card">', unsafe_allow_html=True)
    st.subheader("Capture")

    with st.form("thought_form", clear_on_submit=True):
        raw_text = st.text_area(
            "Raw thought",
            height=150,
            placeholder="Paste messy voice dictation or type a new thought...",
        )
        submitted = st.form_submit_button("Organize Thought", type="primary")

    if submitted:
        if raw_text.strip():
            row = process_raw_text(raw_text)
            append_entry(row)
            st.success("Thought saved.")
            render_result_card(row)
        else:
            st.warning("Enter a thought before organizing it.")

    st.markdown("</section>", unsafe_allow_html=True)


def render_result_card(row: dict[str, str]) -> None:
    layer = html.escape(row["layer"])
    category = html.escape(row["category"])
    reminder = html.escape(row["short_reminder"])
    cleaned = html.escape(row["full_cleaned_text"])
    color = LAYER_COLORS.get(row["layer"], PALETTE["unsorted"])

    st.markdown(
        f"""
        <div class="lum-card">
            <span class="layer-chip" style="background: {color};">{layer}</span>
            <h3>{reminder}</h3>
            <p><strong>Category:</strong> {category}</p>
            <p>{cleaned}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_divider() -> None:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def render_layer_view(rows: list[dict[str, str]], selected_layer: str) -> None:
    st.markdown('<section class="lum-card">', unsafe_allow_html=True)
    st.subheader("Layer View")

    counts = {layer: 0 for layer in LAYER_COLORS}
    for row in rows:
        layer = row.get("layer", "Unsorted") or "Unsorted"
        counts[layer] = counts.get(layer, 0) + 1

    buttons = [
        layer_button_html("All", "All", selected_layer, PALETTE["cyan_aurora"], len(rows))
    ]
    for layer, color in LAYER_COLORS.items():
        buttons.append(layer_button_html(layer, layer, selected_layer, color, counts.get(layer, 0)))

    st.markdown(
        f'<div class="layer-buttons">{"".join(buttons)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</section>", unsafe_allow_html=True)


def layer_button_html(label: str, value: str, selected_layer: str, color: str, count: int) -> str:
    selected_class = " selected" if selected_layer == value else ""
    href = f"?layer={quote(value)}"
    return (
        f'<a class="layer-button{selected_class}" href="{href}" '
        f'style="background: {color};">{html.escape(label)} ({count})</a>'
    )


def render_table(rows: list[dict[str, str]], selected_layer: str) -> None:
    filtered_rows = [
        row for row in rows if selected_layer == "All" or row.get("layer") == selected_layer
    ]

    st.markdown('<section class="lum-card">', unsafe_allow_html=True)
    st.subheader("Spreadsheet")

    if not filtered_rows:
        st.markdown(
            '<div class="empty-state">No entries match the selected layer.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(build_table_html(filtered_rows), unsafe_allow_html=True)

    st.markdown("</section>", unsafe_allow_html=True)


def build_table_html(rows: list[dict[str, str]]) -> str:
    headers = ["timestamp", "layer", "category", "short_reminder", "full_cleaned_text"]
    header_html = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    body_rows = []

    for row in rows:
        cells = []
        for header in headers:
            value = html.escape(row.get(header, ""))
            if header == "layer":
                color = LAYER_COLORS.get(row.get("layer", "Unsorted"), PALETTE["unsorted"])
                value = f'<span class="layer-chip" style="background: {color};">{value}</span>'
            cells.append(f"<td>{value}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    return f"""
    <div style="overflow-x: auto;">
        <table class="thought-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{''.join(body_rows)}</tbody>
        </table>
    </div>
    """


def process_raw_text(raw_text: str) -> dict[str, str]:
    cleaned_text = clean_text(raw_text)
    short_reminder = generate_short_reminder(cleaned_text)
    routing = route_entry(cleaned_text)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "layer": routing["layer"],
        "category": routing["category"],
        "short_reminder": short_reminder,
        "full_cleaned_text": cleaned_text,
    }


def read_entries(data_path: Path = DATA_PATH) -> list[dict[str, str]]:
    if not data_path.exists():
        return []

    with data_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            {column: row.get(column, "") for column in CSV_COLUMNS}
            for row in reader
        ]


def get_selected_layer() -> str:
    selected_layer = st.query_params.get("layer", "All")
    valid_layers = {"All", *LAYER_COLORS.keys()}
    return selected_layer if selected_layer in valid_layers else "All"


if __name__ == "__main__":
    main()
