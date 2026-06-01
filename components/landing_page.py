"""
components/landing_page.py -- Landing Page component.

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.7, 3.8
"""

from __future__ import annotations

import streamlit as st

from core import file_parser


def _render_hero() -> None:
    st.markdown(
        """
        <div style="text-align: center; padding: 2.5rem 1rem 1.5rem 1rem;">
            <h1 style="
                font-size: 2.2rem;
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 0.6rem;
                line-height: 1.2;
            ">Analisis Data dengan AI</h1>
            <p style="
                font-size: 1.05rem;
                color: #475569;
                max-width: 580px;
                margin: 0 auto;
                line-height: 1.7;
            ">
                Unggah file data Anda, ketik instruksi dalam bahasa alami,
                dan dapatkan visualisasi serta insight secara otomatis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_capability_cards() -> None:
    cols = st.columns(3, gap="medium")
    cards = [
        ("Inspeksi Otomatis", "Statistik deskriptif, deteksi outlier, nilai null, dan tipe data terdeteksi seketika tanpa konfigurasi."),
        ("Chat AI", "Transformasi DataFrame, agregasi, filter, dan resampling time-series dengan instruksi bahasa alami."),
        ("Visualisasi Grafik", "Bar, Line, Area, Scatter, Pie, Box Plot, Heatmap dirender interaktif via Plotly dan Matplotlib."),
    ]
    for col, (title, desc) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div style="
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-top: 3px solid #1e40af;
                    border-radius: 8px;
                    padding: 1.3rem 1.1rem;
                    min-height: 120px;
                ">
                    <div style="
                        font-weight: 600;
                        font-size: 0.92rem;
                        color: #0f172a;
                        margin-bottom: 0.4rem;
                    ">{title}</div>
                    <div style="
                        font-size: 0.8rem;
                        color: #475569;
                        line-height: 1.55;
                    ">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_format_badges() -> None:
    formats = ["CSV", "TSV", "JSON", "JSONL", "PDF", "Parquet", "XLSX", "XLS"]
    badges = " ".join(
        f'<span style="background:#eff6ff; color:#1e40af; font-size:0.72rem; '
        f'font-weight:600; padding:0.25rem 0.6rem; border-radius:4px; '
        f'display:inline-block; margin:0.12rem;">{f}</span>'
        for f in formats
    )
    st.markdown(
        f'<div style="text-align:center; margin: 1rem 0;">'
        f'<span style="font-size:0.8rem; color:#475569; font-weight:500;">'
        f'Format didukung:</span> {badges}'
        f'<span style="font-size:0.72rem; color:#94a3b8; margin-left:0.5rem;">'
        f'Maks. 200 MB</span></div>',
        unsafe_allow_html=True,
    )


def _render_uploader() -> None:
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
    st.markdown(
        '<p style="text-align:center; font-size:0.75rem; color:#94a3b8; '
        'text-transform:uppercase; letter-spacing:0.06em; font-weight:600; '
        'margin-bottom:0.8rem;">Cara Penggunaan</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(3, gap="medium")
    steps = [
        ("1", "Unggah File", "CSV, Excel, JSON, PDF, atau Parquet"),
        ("2", "Eksplorasi", "Statistik dan outlier terdeteksi otomatis"),
        ("3", "Chat AI", "Ketik instruksi untuk grafik dan transformasi"),
    ]
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div style="
                        width: 2rem; height: 2rem;
                        background: linear-gradient(135deg, #1a365d, #1e40af);
                        border-radius: 50%;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: 700;
                        font-size: 0.85rem;
                        margin-bottom: 0.5rem;
                    ">{num}</div>
                    <div style="font-weight: 600; font-size: 0.85rem; color: #0f172a;
                         margin-bottom: 0.15rem;">{title}</div>
                    <div style="font-size: 0.76rem; color: #64748b;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render() -> None:
    """Render the Landing Page."""
    _render_hero()
    _render_capability_cards()
    st.divider()
    _render_format_badges()
    _render_uploader()
    st.divider()
    _render_workflow_steps()
    st.markdown(
        '<p style="text-align:center; font-size:0.72rem; color:#94a3b8; margin-top:2rem;">'
        'Powered by Gemini 2.5 Flash | Python | Streamlit | Pandas | Plotly</p>',
        unsafe_allow_html=True,
    )
