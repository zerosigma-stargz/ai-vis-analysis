"""
components/data_page.py — Data Page component.

Displayed when ``st.session_state.df is not None``.  Renders the active
filename header, the full data summary produced by
:func:`core.data_inspector.render_summary`, and the chat conversation area
via :func:`components.chat_area.render`.

Public interface
----------------
- ``render() -> None``  — entry point called by ``app.py``
"""

from __future__ import annotations

import streamlit as st

from components import chat_area
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
    # Header — active filename                                             #
    # ------------------------------------------------------------------ #
    st.header(f"📂 {filename}")

    # ------------------------------------------------------------------ #
    # Data summary                                                         #
    # ------------------------------------------------------------------ #
    data_inspector.render_summary(df, filename)

    # ------------------------------------------------------------------ #
    # AI Assistance section header                                         #
    # ------------------------------------------------------------------ #
    st.divider()

    help_text = (
        "💡 Cara menggunakan AI Assistance:\n\n"
        "1. Pastikan Gemini API Key sudah diisi di sidebar (panel kiri).\n"
        "2. Ketik instruksi analisis atau visualisasi di kotak Prompt yang ada di sidebar.\n"
        "3. Klik tombol **Kirim** untuk mengirim instruksi ke Gemini AI.\n\n"
        "Contoh instruksi:\n"
        "• \"Buatkan grafik bar chart total sales per kategori\"\n"
        "• \"Tampilkan pie chart distribusi profit per segment\"\n"
        "• \"Hitung rata-rata sales per region dan tampilkan hasilnya\"\n"
        "• \"Hapus kolom yang tidak diperlukan dan tampilkan 10 baris pertama\""
    )

    col_title, col_help = st.columns([0.92, 0.08])
    with col_title:
        st.subheader("🤖 Area Modifikasi DataFrame dan Visualisasi Grafik AI Assistance")
    with col_help:
        st.button(
            "❓",
            help=help_text,
            key="ai_assistance_help",
            use_container_width=True,
        )

    st.caption(
        "Gunakan Gemini AI untuk mentransformasi data, membuat grafik, dan menganalisis "
        "DataFrame secara interaktif. Ketik instruksi Anda di **Prompt Box** yang tersedia "
        "di **sidebar sebelah kiri**, lalu klik **Kirim**. Hasil analisis dan visualisasi "
        "akan muncul di bawah ini."
    )

    # ------------------------------------------------------------------ #
    # Chat area                                                            #
    # ------------------------------------------------------------------ #
    chat_area.render()
