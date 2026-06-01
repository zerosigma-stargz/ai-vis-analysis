"""
app.py -- Entry point for the AI Data Analysis & Visualization application.

This module is the top-level Streamlit entry point. It is responsible for:

1. Loading environment variables from ``.env`` via ``python-dotenv``.
2. Configuring the Streamlit page (title, layout).
3. Initialising ``st.session_state`` with default values on the first render
   cycle (and only on the first cycle -- existing keys are never overwritten).
4. Rendering the sidebar via :func:`components.sidebar.render`.
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
    page_title="AI Data Analysis & Visualization",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "**AI Data Analysis & Visualization**\n\n"
            "Aplikasi analisis data berbasis AI yang didukung Gemini 2.5 Flash. "
            "Unggah file data Anda dan mulai eksplorasi dengan instruksi bahasa alami.\n\n"
            "Dibangun dengan Python, Streamlit, Pandas, Plotly, Matplotlib"
        ),
        "Get help": "https://github.com/yourusername/chatbot-analisis-data",
        "Report a bug": "https://github.com/yourusername/chatbot-analisis-data/issues",
    },
)

# ---------------------------------------------------------------------------
# Global CSS -- minimalist, professional styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: "Inter", -apple-system, system-ui, sans-serif;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] {
        background: #ffffff !important;
        border-bottom: 1px solid #e2e8f0;
    }
    [data-testid="stToolbar"] { visibility: hidden; }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1100px;
    }

    /* Sidebar - light blue tinted gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f0f7ff 100%);
        border-right: 2px solid #1e40af;
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1a365d 0%, #1e40af 100%);
        border: none;
        color: #ffffff;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.2);
    }

    .stButton > button[kind="secondary"] {
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        font-weight: 500;
        color: #374151;
        background: #ffffff;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #1e40af;
        color: #1e40af;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 8px !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
    }

    /* Divider */
    hr {
        border: none !important;
        height: 1px !important;
        background: #e2e8f0 !important;
        margin: 1.2rem 0 !important;
    }

    /* Metric */
    [data-testid="stMetric"] {
        background: #f0f7ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
    }

    /* Input fields */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        border-radius: 8px !important;
        border: 1px solid #e2e8f0 !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: #1e40af !important;
        box-shadow: 0 0 0 2px rgba(30, 64, 175, 0.1) !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] section {
        border: 2px dashed #d1d5db !important;
        border-radius: 8px !important;
        background: #f9fafb !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #1e40af !important;
        background: #f0f7ff !important;
    }

    /* Tabs */
    [data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 2px solid #1e40af !important;
        color: #1e40af !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Component imports (after page config)
# ---------------------------------------------------------------------------
from components import sidebar, data_page, landing_page

# ---------------------------------------------------------------------------
# Default session state values
# ---------------------------------------------------------------------------

#: Mapping of session state keys to their default values.
#: Used by :func:`init_session_state` to populate ``st.session_state`` on the
#: first render cycle without overwriting values set in subsequent reruns.
DEFAULT_SESSION_STATE: dict = {
    "df": None,                 # pd.DataFrame | None -- active DataFrame
    "original_filename": None,  # str | None -- uploaded filename
    "api_key": "",              # str -- Gemini API Key (from input or env var)
    "chat_history": [],         # list[ChatMessage] -- conversation history
    "last_output_type": None,   # "dataframe" | "figure" | "text" | "error" | None
    "last_output_data": None,   # Any -- last output data for download
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
    """Render a professional app header with mountain blue accent."""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #1a365d 0%, #1e40af 50%, #0369a1 100%);
            padding: 1rem 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.2rem;
        ">
            <h1 style="
                font-size: 1.4rem;
                font-weight: 700;
                color: #ffffff;
                margin: 0;
                line-height: 1.3;
            ">AI Data Analysis & Visualization</h1>
            <p style="
                font-size: 0.8rem;
                color: rgba(255, 255, 255, 0.8);
                margin: 0.2rem 0 0 0;
            ">Analisis data dan buat visualisasi dengan instruksi bahasa alami</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Run the Streamlit application.

    Execution order on every render cycle:

    1. :func:`init_session_state` -- ensure all session state keys exist.
    2. :func:`components.sidebar.render` -- render sidebar with API key input.
    3. :func:`_render_app_header` -- render minimal header.
    4. Route to :func:`components.landing_page.render` when
       ``st.session_state.df is None``, or to
       :func:`components.data_page.render` when a DataFrame is loaded.

    Requirements: 2.1, 2.5, 10.3, 11.3, 11.5
    """
    init_session_state()
    sidebar.render()
    _render_app_header()

    if st.session_state.df is None:
        landing_page.render()
    else:
        data_page.render()


# ---------------------------------------------------------------------------
# Streamlit entry point guard
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
