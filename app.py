"""
app.py — Entry point for the AI Assistance Analisis & Visualisasi Chart Grafik Data application.

This module is the top-level Streamlit entry point. It is responsible for:

1. Loading environment variables from ``.env`` via ``python-dotenv``.
2. Configuring the Streamlit page (title, layout).
3. Initialising ``st.session_state`` with default values on the first render
   cycle (and only on the first cycle — existing keys are never overwritten).
4. Rendering the sidebar on every cycle via :func:`components.sidebar.render`.
5. Routing between :func:`components.landing_page.render` (when no DataFrame
   is loaded) and :func:`components.data_page.render` (when a DataFrame is
   present in session state).

Usage
-----
Run the application with::

    streamlit run app.py

Requirements: 2.1, 2.5, 10.3, 11.3, 11.5
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Load environment variables BEFORE any Streamlit import so that os.environ
# is populated when sidebar.py reads GEMINI_API_KEY during initialisation.
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Streamlit import and page configuration.
# st.set_page_config() MUST be the very first Streamlit command called.
# ---------------------------------------------------------------------------
import streamlit as st

st.set_page_config(
    page_title="AI Assistance Analisis & Visualisasi Chart Grafik Data",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "**AI Assistance Analisis & Visualisasi Chart Grafik Data**\n\n"
            "Aplikasi analisis data berbasis AI yang didukung Gemini 2.5 Flash. "
            "Unggah file data Anda dan mulai eksplorasi dengan instruksi bahasa alami.\n\n"
            "Dibangun dengan Python · Streamlit · Pandas · Plotly · Matplotlib"
        ),
        "Get help": "https://github.com/yourusername/chatbot-analisis-data",
        "Report a bug": "https://github.com/yourusername/chatbot-analisis-data/issues",
    },
)

# ---------------------------------------------------------------------------
# Global CSS — menyeragamkan tipografi, warna, dan spacing agar konsisten
# dengan tampilan landing_page.py (gradient ungu-biru, kartu rounded, dll.)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ── Font & base ─────────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
    }

    /* ── Hide default Streamlit header decoration ────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }

    /* ── Main content area — sedikit padding atas ────────────────────────── */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px;
    }

    /* ── Sidebar — gradient subtle ungu-biru ─────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #faf8ff 0%, #f8faff 100%);
        border-right: 2px solid #e0e7ff;
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem !important;
    }

    /* ── Tombol primer — gradient ungu selaras dengan hero ───────────────── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: #ffffff;
        font-weight: 700;
        border-radius: 10px;
        padding: 0.5rem 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .stButton > button[kind="primary"]:hover {
        opacity: 0.9;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }
    .stButton > button[kind="primary"]:active {
        transform: translateY(0);
    }

    /* ── Tombol sekunder ─────────────────────────────────────────────────── */
    .stButton > button[kind="secondary"] {
        border: 2px solid #d1d5db;
        border-radius: 10px;
        font-weight: 600;
        color: #374151;
        background: #ffffff;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #faf5ff 0%, #f0f4ff 100%);
        color: #764ba2;
        transform: translateY(-1px);
    }

    /* ── st.info / st.warning / st.error — rounded dengan shadow ─────────── */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }

    /* ── st.dataframe — border halus dengan shadow ───────────────────────── */
    [data-testid="stDataFrame"] {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* ── Expander — border halus ─────────────────────────────────────────── */
    [data-testid="stExpander"] {
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
        background: #ffffff !important;
    }

    /* ── Chat message bubbles ────────────────────────────────────────────── */
    [data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 0.7rem 0.9rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    /* ── Divider — lebih tipis ───────────────────────────────────────────── */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #e5e7eb, transparent) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Metric cards ────────────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
        border: 1px solid #e0e7ff;
        border-radius: 12px;
        padding: 0.7rem 0.9rem;
        box-shadow: 0 2px 6px rgba(102, 126, 234, 0.08);
    }

    /* ── Text input & text area ──────────────────────────────────────────── */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        border-radius: 10px !important;
        border: 2px solid #e5e7eb !important;
        transition: border-color 0.3s ease !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* ── File uploader ───────────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section {
        border: 2px dashed #d1d5db !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #fafbff 0%, #f8f9ff 100%) !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #667eea !important;
        background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%) !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────────────── */
    [data-testid="stTabs"] button {
        border-radius: 8px 8px 0 0 !important;
        font-weight: 600 !important;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    /* ── Animasi fade-in untuk konten ────────────────────────────────────── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .block-container > div {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Component imports (after page config)
# ---------------------------------------------------------------------------
from components import data_page, landing_page, sidebar

# ---------------------------------------------------------------------------
# Default session state values
# ---------------------------------------------------------------------------

#: Mapping of session state keys to their default values.
#: Used by :func:`init_session_state` to populate ``st.session_state`` on the
#: first render cycle without overwriting values set in subsequent reruns.
DEFAULT_SESSION_STATE: dict = {
    "df": None,                 # pd.DataFrame | None — active DataFrame
    "original_filename": None,  # str | None — uploaded filename
    "api_key": "",              # str — Gemini API Key (from input or env var)
    "chat_history": [],         # list[ChatMessage] — conversation history
    "last_output_type": None,   # "dataframe" | "figure" | "text" | "error" | None
    "last_output_data": None,   # Any — last output data for download
}


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------


def init_session_state() -> None:
    """Initialise ``st.session_state`` with default values.

    Only keys that are **not already present** in ``st.session_state`` are
    set.  This ensures that values written during a previous render cycle
    (e.g. an uploaded DataFrame or the user's API key) are preserved across
    Streamlit reruns.

    The keys and their defaults are defined in :data:`DEFAULT_SESSION_STATE`.

    Requirements: 2.1, 2.5, 10.3, 11.3, 11.5
    """
    for key, default_value in DEFAULT_SESSION_STATE.items():
        if key not in st.session_state:
            # Use a copy for mutable defaults (lists, dicts) to avoid sharing
            # the same object across sessions in multi-user deployments.
            if isinstance(default_value, (list, dict)):
                st.session_state[key] = type(default_value)()
            else:
                st.session_state[key] = default_value


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def _render_app_header() -> None:
    """Render a compact, elegant app header with gradient branding.
    
    Displayed at the top of every page for consistent branding.
    """
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            padding: 0.8rem 1.5rem;
            border-radius: 14px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
            display: flex;
            align-items: center;
            justify-content: space-between;
        ">
            <div style="display: flex; align-items: center; gap: 0.8rem;">
                <div style="font-size: 2rem;">🤖</div>
                <div>
                    <div style="
                        font-size: 1.3rem;
                        font-weight: 800;
                        color: #ffffff;
                        line-height: 1.2;
                        letter-spacing: -0.02em;
                    ">AI Assistance Analisis & Visualisasi Chart Grafik Data</div>
                    <div style="
                        font-size: 0.75rem;
                        color: rgba(255, 255, 255, 0.85);
                        font-weight: 500;
                        margin-top: 0.1rem;
                    ">Didukung Gemini 2.5 Flash · Transformasi data dengan bahasa alami</div>
                </div>
            </div>
            <div style="
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                padding: 0.4rem 0.9rem;
                border-radius: 999px;
                font-size: 0.7rem;
                font-weight: 700;
                color: #ffffff;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">AI-Powered</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Run the Streamlit application.

    Execution order on every render cycle:

    1. :func:`init_session_state` — ensure all session state keys exist.
    2. :func:`_render_app_header` — render elegant gradient header.
    3. :func:`components.sidebar.render` — always render the sidebar.
    4. Route to :func:`components.landing_page.render` when
       ``st.session_state.df is None``, or to
       :func:`components.data_page.render` when a DataFrame is loaded.

    Requirements: 2.1, 2.5, 10.3, 11.3, 11.5
    """
    init_session_state()
    _render_app_header()
    sidebar.render()

    if st.session_state.df is None:
        landing_page.render()
    else:
        data_page.render()


# ---------------------------------------------------------------------------
# Streamlit entry point guard
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
