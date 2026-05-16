"""
components/landing_page.py — Landing Page component.

Displayed when ``session_state.df is None``. Renders the application title,
a brief description, and a file uploader. On successful upload the parsed
DataFrame and original filename are stored in session state, which causes
the router in ``app.py`` to automatically switch to Data_Page on the next
render cycle.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.7, 3.8
"""

from __future__ import annotations

import streamlit as st

from core import file_parser


def render() -> None:
    """Render the Landing Page.

    Shows the application title, a short description of the chatbot's
    data-analysis and auto-chart-visualisation capabilities, and a
    ``st.file_uploader`` widget.

    When the user uploads a file:
    - ``file_parser.parse()`` is called to convert the file to a DataFrame.
    - On success the DataFrame is stored in ``st.session_state.df`` and the
      original filename in ``st.session_state.original_filename``.  The app
      will then route to Data_Page automatically on the next rerun.
    - On failure ``file_parser.parse()`` returns ``None`` and has already
      called ``st.error()`` internally; the Landing Page remains visible so
      the user can try a different file.

    Returns
    -------
    None
    """
    # -----------------------------------------------------------------------
    # Header & description
    # -----------------------------------------------------------------------
    st.title("🤖 Chatbot Analisis & Visualisasi Data")

    st.markdown(
        """
        Selamat datang! Aplikasi ini membantu Anda **menganalisis data** dan
        **membuat visualisasi grafik secara otomatis** hanya dengan mengunggah
        file dan mengetikkan instruksi dalam bahasa alami.

        **Kemampuan utama:**
        - 📊 Ringkasan statistik otomatis (tipe data, nilai null, outlier, dll.)
        - 💬 Chatbot berbasis **Gemini 2.5 Flash** untuk transformasi DataFrame
          dan pembuatan grafik (Matplotlib / Plotly)
        - 💰 Deteksi dan pembersihan kolom mata uang secara otomatis
        - ⬇️ Unduh hasil analisis sebagai CSV, Excel, JPG, PNG, atau PDF

        **Format file yang didukung:** CSV · TSV · JSON · JSONL · PDF · Parquet · Excel (XLSX/XLS)
        **Ukuran file maksimal:** 200 MB
        """
    )

    st.divider()

    # -----------------------------------------------------------------------
    # File uploader
    # -----------------------------------------------------------------------
    uploaded_file = st.file_uploader(
        label="Unggah file data Anda",
        type=["csv", "tsv", "json", "jsonl", "pdf", "parquet", "xlsx", "xls"],
        help=(
            "Format yang didukung: CSV, TSV, JSON, JSONL, PDF (dengan tabel), "
            "Parquet, Excel (XLSX/XLS). Ukuran maksimal 200 MB."
        ),
    )

    # -----------------------------------------------------------------------
    # Handle uploaded file
    # -----------------------------------------------------------------------
    if uploaded_file is not None:
        with st.spinner(f"Memproses file '{uploaded_file.name}'…"):
            df = file_parser.parse(uploaded_file)

        if df is not None:
            # Persist to session state — the router will switch pages on rerun
            st.session_state.df = df
            st.session_state.original_filename = uploaded_file.name
            st.rerun()
        # If df is None, file_parser.parse() has already called st.error()
        # internally, so we simply fall through and keep the Landing Page
        # visible for the user to try again.
