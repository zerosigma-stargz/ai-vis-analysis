"""
Sidebar component -- manages the Streamlit sidebar panel.

Handles two responsibilities:
1. **API Key input** -- password field that stores the Gemini API key in
   session state, with environment-variable initialisation and status
   indicators.
2. **Session reset** -- "Reset Sesi" button that clears the active DataFrame
   and chat history while preserving the API key.

Public interface
----------------
- ``render() -> None`` -- entry point; wraps all widgets in ``st.sidebar``
"""

from __future__ import annotations

import os

import streamlit as st


def render() -> None:
    """Render all sidebar elements inside ``st.sidebar``.

    Displays:
    1. Header with key icon
    2. Password input for the Gemini API Key
    3. Status indicator (success or warning) based on key presence
    4. "Reset Sesi" button when a DataFrame is loaded

    Requirements: 1.1, 1.2, 1.4, 1.5, 10.1, 10.2, 10.3, 10.4, 11.3, 11.5
    """
    with st.sidebar:
        st.header("\U0001f511 Gemini API Key")
        st.caption("Masukkan API Key untuk mengaktifkan fitur AI")

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

        # Show status indicator based on key presence.
        if api_key_input:
            st.success(
                "\u2705 API Key aktif \u2014 gunakan chat box di halaman utama "
                "untuk instruksi AI"
            )
        else:
            st.warning(
                "\u26a0\ufe0f API Key belum diisi. Chat box tidak akan berfungsi "
                "tanpa API Key."
            )

        # Warn when the key is cleared after previously being set.
        if previous_key and not api_key_input:
            st.warning(
                "\u26a0\ufe0f API Key telah dihapus. Masukkan kembali untuk "
                "menggunakan fitur AI."
            )

        # Reset button -- only visible when a DataFrame is loaded.
        if st.session_state.get("df") is not None:
            st.divider()

            if st.button(
                "\U0001f504 Reset Sesi",
                width="stretch",
                type="secondary",
                help="Hapus data dan riwayat chat. API Key tetap tersimpan.",
            ):
                _keys_to_delete = [
                    "df",
                    "chat_history",
                    "last_output_type",
                    "last_output_data",
                ]
                for key in _keys_to_delete:
                    if key in st.session_state:
                        del st.session_state[key]

                st.rerun()
