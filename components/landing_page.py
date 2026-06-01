"""
components/landing_page.py -- Landing Page component.

Displayed when ``session_state.df is None``. Renders a clean, minimalist
landing page with hero section, capability cards, supported formats,
file uploader, and a 3-step workflow guide.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.7, 3.8
"""

from __future__ import annotations

import streamlit as st

from core import file_parser


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _render_hero() -> None:
    """Render the hero / headline section."""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 1rem 1.5rem 1rem;">
            <h1 style="
                font-size: 2rem;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 0.5rem;
                line-height: 1.3;
            ">Analisis Data dengan AI</h1>
            <p style="
                font-size: 1rem;
                color: #64748b;
                max-width: 560px;
                margin: 0 auto;
                line-height: 1.6;
            ">
                Unggah file data, ketik instruksi dalam bahasa alami,
                dan dapatkan visualisasi serta insight secara otomatis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_capability_cards() -> None:
    """Render three capability cards in a single row."""
    cols = st.columns(3, gap="medium")
    cards = [
        ("Inspeksi Otomatis", "Statistik, outlier, dan tipe data terdeteksi seketika."),
        ("Chat AI", "Transformasi data dan buat grafik dengan instruksi teks."),
        ("Visualisasi", "Bar, Line, Scatter, Pie, Box Plot, Heatmap, dan lainnya."),
    ]
    for col, (title, desc) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div style="
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 1.2rem;
                    text-align: center;
                    min-height: 100px;
                ">
                    <div style="
                        font-weight: 600;
                        font-size: 0.9rem;
                        color: #1e293b;
                        margin-bottom: 0.3rem;
                    ">{title}</div>
                    <div style="
                        font-size: 0.8rem;
                        color: #64748b;
                        line-height: 1.5;
                    ">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_format_badges() -> None:
    """Render supported file format badges."""
    formats = ["CSV", "TSV", "JSON", "JSONL", "PDF", "Parquet", "XLSX", "XLS"]
    badges = " ".join(
        f'<span style="background:#f1f5f9; color:#475569; font-size:0.72rem; '
        f'font-weight:600; padding:0.2rem 0.6rem; border-radius:4px; '
        f'display:inline-block; margin:0.15rem;">{f}</span>'
        for f in formats
    )
    st.markdown(
        f'<div style="text-align:center; margin: 0.8rem 0;">'
        f'<span style="font-size:0.78rem; color:#64748b; font-weight:500;">'
        f'Format didukung:</span> {badges}'
        f'<span style="font-size:0.72rem; color:#94a3b8; margin-left:0.5rem;">'
        f'Maks. 200 MB</span></div>',
        unsafe_allow_html=True,
    )


def _render_uploader() -> None:
    """Render the file uploader widget and handle the uploaded file."""
    uploaded_file = st.file_uploader(
        label="Pilih file data",
        type=["csv", "tsv", "json", "jsonl", "pdf", "parquet", "xlsx", "xls"],
        help=(
            "Format yang didukung: CSV, TSV, JSON, JSONL, PDF (dengan tabel), "
            "Parquet, Excel (XLSX/XLS). Ukuran maksimal 200 MB."
        ),
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        with st.spinner(f"Memproses '{uploaded_file.name}'..."):
            df = file_parser.parse(uploaded_file)

        if df is not None:
            st.session_state.df = df
            st.session_state.original_filename = uploaded_file.name
            st.rerun()


def _render_workflow_steps() -> None:
    """Render a compact 3-step workflow guide."""
    st.markdown(
        """
        <div style="margin: 1rem 0; text-align: center;">
            <p style="font-size: 0.78rem; color: #94a3b8; text-transform: uppercase;
               letter-spacing: 0.05em; font-weight: 600; margin-bottom: 0.8rem;">
               Cara Penggunaan</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(3, gap="medium")
    steps = [
        ("1. Unggah File", "CSV, Excel, JSON, PDF, atau Parquet"),
        ("2. Eksplorasi", "Statistik dan outlier terdeteksi otomatis"),
        ("3. Chat AI", "Ketik instruksi untuk grafik dan transformasi"),
    ]
    for col, (title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="font-weight: 600; font-size: 0.85rem; color: #1e293b;
                         margin-bottom: 0.2rem;">{title}</div>
                    <div style="font-size: 0.75rem; color: #64748b;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Landing Page.

    Displays a clean, minimalist landing page:
    1. Hero headline
    2. Three capability cards
    3. Supported format badges
    4. File uploader
    5. 3-step workflow guide

    On successful upload the DataFrame and filename are stored in session
    state and the app routes to Data_Page automatically.

    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.7, 3.8
    """
    # -- Hero
    _render_hero()

    # -- Capability cards
    _render_capability_cards()

    st.divider()

    # -- Format badges
    _render_format_badges()

    # -- File uploader
    _render_uploader()

    st.divider()

    # -- Workflow steps
    _render_workflow_steps()

    # -- Footer
    st.markdown(
        '<p style="text-align:center; font-size:0.7rem; color:#94a3b8; margin-top:1.5rem;">'
        'Powered by Gemini 2.5 Flash</p>',
        unsafe_allow_html=True,
    )
