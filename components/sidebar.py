"""
Sidebar component -- manages the Streamlit sidebar panel.

Handles two responsibilities:
1. **API Key input** -- password field that stores the Gemini API key in
   session state, with environment-variable initialisation and a warning
   when the key is cleared.
2. **Session reset** -- "Reset Sesi" button that clears the active DataFrame
   and chat history while preserving the API key.

Public interface
----------------
- ``render() -> None``                  -- entry point; wraps all helpers in
  ``st.sidebar``
- ``_handle_api_key_input() -> None``   -- API key widget (Tasks 12.1)
- ``_handle_reset() -> None``           -- reset session button (Task 12.3)
"""

from __future__ import annotations

import os

import streamlit as st


# ---------------------------------------------------------------------------
# Task 12.1 -- API Key input
# ---------------------------------------------------------------------------


def _handle_api_key_input() -> None:
    """Render the Gemini API Key password input in the sidebar.

    Behaviour
    ---------
    - On first render, initialises ``session_state.api_key`` from the
      ``GEMINI_API_KEY`` environment variable (if set), otherwise defaults to
      an empty string.
    - Displays a ``st.text_input`` of type ``"password"`` labelled
      *"Gemini API Key"*.
    - Syncs the widget value back to ``session_state.api_key`` on every
      render cycle.
    - Shows a :func:`streamlit.warning` when the user clears a previously
      non-empty key.

    Requirements: 1.1, 1.2, 1.4, 1.5, 11.3, 11.5
    """
    # Initialise from environment variable if the key has not been set yet.
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.environ.get("GEMINI_API_KEY", "")

    previous_key: str = st.session_state.api_key

    api_key_input: str = st.text_input(
        label="Gemini API Key",
        value=st.session_state.api_key,
        type="password",
        key="api_key_input",
        placeholder="Masukkan Gemini API Key Anda\u2026",
    )

    # Sync widget value to session state.
    st.session_state.api_key = api_key_input

    # Warn when the key is cleared after previously being set.
    if previous_key and not api_key_input:
        st.warning(
            "\u26a0\ufe0f API Key telah dihapus. Masukkan kembali untuk menggunakan fitur AI."
        )


# ---------------------------------------------------------------------------
# Task 12.3 -- Session reset
# ---------------------------------------------------------------------------


def _handle_reset() -> None:
    """Render the "Reset Sesi" button in the sidebar.

    Behaviour
    ---------
    - Only displayed when ``session_state.df`` is not ``None``.
    - On click, removes ``df``, ``chat_history``, ``last_output_type``, and
      ``last_output_data`` from session state.
    - The ``api_key`` value is **preserved** after the reset.

    Requirements: 10.1, 10.2, 10.3, 10.4
    """
    if st.session_state.get("df") is None:
        return

    st.divider()

    if st.button(
        "\U0001f504 Reset Sesi",
        use_container_width=True,
        type="secondary",
        help="Hapus data dan riwayat chat. API Key tetap tersimpan.",
    ):
        _keys_to_delete = ["df", "chat_history", "last_output_type", "last_output_data"]
        for key in _keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]

        # Trigger a rerun so the app routes back to the landing page.
        st.rerun()


# ---------------------------------------------------------------------------
# Task 12.4 -- render() entry point
# ---------------------------------------------------------------------------


def render() -> None:
    """Render all sidebar elements inside ``st.sidebar``.

    Calls, in order:
    1. :func:`_handle_api_key_input` -- always visible
    2. :func:`_handle_reset` -- visible only when ``df`` is loaded

    Requirements: 1.1, 10.1
    """
    with st.sidebar:
        st.header("\u2699\ufe0f Pengaturan")
        _handle_api_key_input()
        _handle_reset()
