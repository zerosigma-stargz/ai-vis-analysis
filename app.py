"""
app.py — Entry point for the Chatbot Analisis dan Visualisasi Data application.

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
    page_title="Chatbot Analisis Data",
    layout="wide",
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


def main() -> None:
    """Run the Streamlit application.

    Execution order on every render cycle:

    1. :func:`init_session_state` — ensure all session state keys exist.
    2. :func:`components.sidebar.render` — always render the sidebar.
    3. Route to :func:`components.landing_page.render` when
       ``st.session_state.df is None``, or to
       :func:`components.data_page.render` when a DataFrame is loaded.

    Requirements: 2.1, 2.5, 10.3, 11.3, 11.5
    """
    init_session_state()
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
