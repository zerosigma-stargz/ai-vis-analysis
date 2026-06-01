"""
components/data_page.py -- Data Page component.

Displayed when ``st.session_state.df is not None``.  Renders the active
filename header, the full data summary produced by
:func:`core.data_inspector.render_summary`, and the chat conversation area
via :func:`components.chat_area.render`.

Public interface
----------------
- ``render() -> None``  -- entry point called by ``app.py``
"""

from __future__ import annotations

import streamlit as st

from components import chat_area
from components import floating_chatbox
from core import data_inspector


def render() -> None:
    """Render the Data Page.

    Displays, in order:

    1. A header showing the name of the currently active file taken from
       ``st.session_state.original_filename``.
    2. A comprehensive data summary (shape, preview, dtypes, nulls,
       duplicates, descriptive statistics, outliers, and currency columns)
       via :func:`core.data_inspector.render_summary`.
    3. The chat conversation history via :func:`components.chat_area.render`.

    This function reads ``st.session_state.df`` and
    ``st.session_state.original_filename`` directly; both are expected to be
    set before this component is rendered.

    Requirements: 4.1, 4.2
    """
    df = st.session_state.df
    filename: str = st.session_state.get("original_filename", "")

    # ------------------------------------------------------------------ #
    # Header -- active filename                                            #
    # ------------------------------------------------------------------ #
    st.header(filename)

    # ------------------------------------------------------------------ #
    # Data summary                                                         #
    # ------------------------------------------------------------------ #
    data_inspector.render_summary(df, filename)

    # ------------------------------------------------------------------ #
    # AI Assistance section header                                         #
    # ------------------------------------------------------------------ #
    st.divider()

    help_text = (
        "Cara menggunakan:\n\n"
        "1. Pastikan Gemini API Key sudah diisi di sidebar.\n"
        "2. Ketik instruksi di chat box di bawah halaman.\n"
        "3. Tekan Enter untuk mengirim ke AI.\n\n"
        "Contoh:\n"
        "- \"Buat bar chart total sales per kategori\"\n"
        "- \"Tampilkan pie chart distribusi profit\"\n"
        "- \"Hitung rata-rata sales per region\""
    )

    col_title, col_help = st.columns([0.92, 0.08])
    with col_title:
        st.subheader("Analisis & Visualisasi AI")
    with col_help:
        st.button(
            "?",
            help=help_text,
            key="ai_assistance_help",
            width="stretch",
        )

    st.caption(
        "Gunakan Gemini AI untuk mentransformasi data, membuat grafik, dan menganalisis "
        "DataFrame secara interaktif. Ketik instruksi di kotak chat di bawah halaman, "
        "lalu tekan Enter."
    )

    # ------------------------------------------------------------------ #
    # Chat area                                                            #
    # ------------------------------------------------------------------ #
    chat_area.render()

    # ------------------------------------------------------------------ #
    # Floating chat input                                                  #
    # ------------------------------------------------------------------ #
    floating_chatbox.render()
