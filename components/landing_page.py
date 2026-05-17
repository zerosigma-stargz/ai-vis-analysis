"""
components/landing_page.py — Landing Page component.

Displayed when ``session_state.df is None``. Renders a rich, professional
landing page with hero section, capability showcase, discipline use-cases,
supported formats, and a prominent file uploader.

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
        <div style="text-align: center; padding: 2.5rem 1rem 1.5rem 1rem;">
            <div style="font-size: 3.2rem; margin-bottom: 0.4rem;">🤖</div>
            <h1 style="
                font-size: 2.4rem;
                font-weight: 800;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.6rem;
                line-height: 1.2;
            ">
                AI Assistance Analisis &amp; Visualisasi Chart Grafik Data
            </h1>
            <p style="
                font-size: 1.15rem;
                color: #6b7280;
                max-width: 640px;
                margin: 0 auto 0.5rem auto;
                line-height: 1.6;
            ">
                Ubah data mentah menjadi wawasan bermakna hanya dengan
                <strong>mengunggah file</strong> dan <strong>mengetikkan instruksi</strong>
                dalam bahasa alami — didukung <em>Gemini 2.5 Flash</em>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_capability_cards() -> None:
    """Render the four core capability cards in a 2×2 grid."""
    col1, col2 = st.columns(2, gap="medium")

    cards = [
        (
            "📊", "Inspeksi Data Otomatis",
            "Statistik deskriptif, deteksi outlier (IQR), nilai null, "
            "duplikat, dan kolom mata uang — tampil seketika tanpa konfigurasi.",
        ),
        (
            "💬", "Chatbot AI Berbasis Gemini",
            "Transformasi DataFrame, agregasi, filter, penambahan/penghapusan "
            "kolom, dan resampling time-series cukup dengan instruksi teks.",
        ),
        (
            "📈", "Visualisasi Grafik Dinamis",
            "Bar, Line, Area, Scatter, Pie, Box Plot, Heatmap, Funnel — "
            "dirender interaktif via Plotly atau Matplotlib.",
        ),
        (
            "🔍", "Analisis Grafik Otomatis",
            "Setiap grafik dilengkapi panel Chart Insight: tujuan, deskripsi "
            "pola/tren, dan tips analisis lanjutan dari Gemini AI.",
        ),
    ]

    for i, (icon, title, desc) in enumerate(cards):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
                    border: 1px solid #e0e7ff;
                    border-radius: 14px;
                    padding: 1.2rem 1.3rem;
                    margin-bottom: 0.8rem;
                    transition: box-shadow 0.2s;
                ">
                    <div style="font-size: 1.7rem; margin-bottom: 0.4rem;">{icon}</div>
                    <div style="
                        font-weight: 700;
                        font-size: 0.95rem;
                        color: #1e1b4b;
                        margin-bottom: 0.35rem;
                    ">{title}</div>
                    <div style="
                        font-size: 0.84rem;
                        color: #4b5563;
                        line-height: 1.55;
                    ">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_discipline_usecases() -> None:
    """Render a compact multi-discipline use-case section."""
    st.markdown(
        """
        <h3 style="
            font-size: 1.05rem;
            font-weight: 700;
            color: #374151;
            margin: 1.4rem 0 0.8rem 0;
            text-align: center;
            letter-spacing: 0.02em;
        ">
            🎓 Cocok untuk berbagai bidang profesional
        </h3>
        """,
        unsafe_allow_html=True,
    )

    disciplines = [
        ("🏥", "Kesehatan & Kedokteran",   "Analisis rekam medis, epidemiologi, uji klinis"),
        ("💼", "Bisnis & Keuangan",         "Laporan penjualan, forecasting, analisis risiko"),
        ("🔬", "Sains & Riset",             "Eksplorasi dataset eksperimen, statistik inferensial"),
        ("🏛️", "Kebijakan & Sosial",        "Survei, demografi, evaluasi program"),
        ("🎓", "Pendidikan & Akademik",     "Analisis nilai, penelitian kuantitatif"),
        ("⚙️", "Teknik & Manufaktur",       "Quality control, sensor data, time-series mesin"),
        ("🌿", "Lingkungan & Pertanian",    "Data iklim, hasil panen, pemantauan ekosistem"),
        ("📡", "Teknologi & Data Science",  "EDA cepat, prototyping model, feature engineering"),
    ]

    cols = st.columns(4, gap="small")
    for i, (icon, title, desc) in enumerate(disciplines):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div style="
                    background: #ffffff;
                    border: 1px solid #e5e7eb;
                    border-radius: 10px;
                    padding: 0.75rem 0.8rem;
                    margin-bottom: 0.6rem;
                    text-align: center;
                ">
                    <div style="font-size: 1.4rem;">{icon}</div>
                    <div style="
                        font-size: 0.75rem;
                        font-weight: 700;
                        color: #1f2937;
                        margin: 0.25rem 0 0.2rem 0;
                        line-height: 1.3;
                    ">{title}</div>
                    <div style="
                        font-size: 0.7rem;
                        color: #6b7280;
                        line-height: 1.4;
                    ">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_format_badges() -> None:
    """Render supported file format badges."""
    formats = [
        ("CSV", "#dbeafe", "#1d4ed8"),
        ("TSV", "#dbeafe", "#1d4ed8"),
        ("JSON", "#dcfce7", "#15803d"),
        ("JSONL", "#dcfce7", "#15803d"),
        ("PDF", "#fee2e2", "#b91c1c"),
        ("Parquet", "#fef3c7", "#b45309"),
        ("XLSX", "#f3e8ff", "#7e22ce"),
        ("XLS", "#f3e8ff", "#7e22ce"),
    ]

    badges_html = " ".join(
        f'<span style="'
        f'background:{bg}; color:{fg}; '
        f'font-size:0.75rem; font-weight:700; '
        f'padding:0.25rem 0.65rem; border-radius:999px; '
        f'display:inline-block; margin:0.15rem;'
        f'">{fmt}</span>'
        for fmt, bg, fg in formats
    )

    st.markdown(
        f"""
        <div style="
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 0.9rem 1.1rem;
            margin: 0.6rem 0 1rem 0;
            text-align: center;
        ">
            <div style="
                font-size: 0.8rem;
                font-weight: 600;
                color: #374151;
                margin-bottom: 0.5rem;
            ">📁 Format file yang didukung &nbsp;·&nbsp; Ukuran maksimal <strong>200 MB</strong></div>
            <div>{badges_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_uploader() -> None:
    """Render the file uploader widget and handle the uploaded file."""
    st.markdown(
        """
        <div style="
            text-align: center;
            font-size: 1rem;
            font-weight: 700;
            color: #1e1b4b;
            margin-bottom: 0.5rem;
        ">
            ⬆️ Mulai dengan mengunggah file data Anda
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        with st.spinner(f"⏳ Memproses '{uploaded_file.name}'…"):
            df = file_parser.parse(uploaded_file)

        if df is not None:
            st.session_state.df = df
            st.session_state.original_filename = uploaded_file.name
            st.rerun()


def _render_workflow_steps() -> None:
    """Render a compact 3-step workflow guide."""
    st.markdown(
        """
        <div style="margin: 1rem 0 0.5rem 0;">
            <div style="
                font-size: 0.8rem;
                font-weight: 700;
                color: #6b7280;
                text-align: center;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 0.7rem;
            ">Cara Penggunaan</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    steps = [
        ("1", "Unggah File", "CSV, Excel, JSON, PDF, Parquet — hingga 200 MB"),
        ("2", "Eksplorasi Otomatis", "Statistik, outlier, dan mata uang terdeteksi seketika"),
        ("3", "Chat dengan AI", "Ketik instruksi → grafik & transformasi data instan"),
    ]

    cols = st.columns(3, gap="medium")
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f"""
                <div style="text-align: center; padding: 0.5rem 0.3rem;">
                    <div style="
                        width: 2rem; height: 2rem;
                        background: linear-gradient(135deg, #667eea, #764ba2);
                        border-radius: 50%;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: 800;
                        font-size: 0.9rem;
                        margin-bottom: 0.4rem;
                    ">{num}</div>
                    <div style="
                        font-weight: 700;
                        font-size: 0.85rem;
                        color: #1f2937;
                        margin-bottom: 0.2rem;
                    ">{title}</div>
                    <div style="
                        font-size: 0.75rem;
                        color: #6b7280;
                        line-height: 1.4;
                    ">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Landing Page.

    Displays a rich, multi-section landing page:
    1. Hero headline with gradient title
    2. Four core capability cards (2×2 grid)
    3. Multi-discipline use-case tiles (4-column grid)
    4. Supported format badges + file size limit
    5. Prominent file uploader
    6. 3-step workflow guide

    On successful upload the DataFrame and filename are stored in session
    state and the app routes to Data_Page automatically.

    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.7, 3.8
    """
    # ── Hero ────────────────────────────────────────────────────────────────
    _render_hero()

    # ── Capability cards ────────────────────────────────────────────────────
    _render_capability_cards()

    st.divider()

    # ── Discipline use-cases ────────────────────────────────────────────────
    _render_discipline_usecases()

    st.divider()

    # ── Format badges ───────────────────────────────────────────────────────
    _render_format_badges()

    # ── File uploader ───────────────────────────────────────────────────────
    _render_uploader()

    st.divider()

    # ── Workflow steps ──────────────────────────────────────────────────────
    _render_workflow_steps()

    # ── Footer note ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            text-align: center;
            font-size: 0.72rem;
            color: #9ca3af;
            margin-top: 1.5rem;
            padding-bottom: 1rem;
        ">
            Didukung oleh <strong>Gemini 2.5 Flash</strong> · Python · Streamlit · Pandas · Plotly · Matplotlib
        </div>
        """,
        unsafe_allow_html=True,
    )
