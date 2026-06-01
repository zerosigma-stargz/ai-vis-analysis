"""
Sidebar component -- Gemini API Key configuration panel.

Provides a clean, minimal interface for entering and managing
the Gemini API Key.

Public interface
----------------
- ``render() -> None`` -- entry point
"""

from __future__ import annotations

import os

import streamlit as st


def render() -> None:
    """Render the sidebar with API Key input and session controls."""
    with st.sidebar:
        st.markdown(
            '<h3 style="color: #1e293b; font-weight: 700; margin-bottom: 0.2rem;">'
            'Konfigurasi API</h3>',
            unsafe_allow_html=True,
        )
        st.caption("Masukkan Gemini API Key untuk mengaktifkan fitur AI.")

        # Initialise from environment variable if not yet set.
        if "api_key" not in st.session_state:
            st.session_state.api_key = os.environ.get("GEMINI_API_KEY", "")

        previous_key: str = st.session_state.api_key

        api_key_input: str = st.text_input(
            label="Gemini API Key",
            value=st.session_state.api_key,
            type="password",
            key="api_key_input",
            placeholder="Paste API Key Anda di sini...",
        )

        # Sync widget value to session state.
        st.session_state.api_key = api_key_input

        # Status indicator
        if api_key_input:
            st.markdown(
                '<div style="background: #f0fdf4; border: 1px solid #bbf7d0; '
                'border-radius: 8px; padding: 0.5rem 0.8rem; margin-top: 0.5rem;">'
                '<span style="color: #166534; font-size: 0.82rem; font-weight: 500;">'
                'API Key terhubung</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="background: #fef9c3; border: 1px solid #fde047; '
                'border-radius: 8px; padding: 0.5rem 0.8rem; margin-top: 0.5rem;">'
                '<span style="color: #854d0e; font-size: 0.82rem; font-weight: 500;">'
                'API Key diperlukan untuk menggunakan chat AI</span></div>',
                unsafe_allow_html=True,
            )

        # Warn when the key is cleared after previously being set.
        if previous_key and not api_key_input:
            st.warning("API Key telah dihapus.")

        # Link to get API key
        st.markdown(
            '<div style="margin-top: 0.8rem; font-size: 0.78rem; color: #64748b;">'
            'Dapatkan API Key dari '
            '<a href="https://aistudio.google.com/app/apikey" target="_blank" '
            'style="color: #4f46e5; text-decoration: none; font-weight: 500;">'
            'Google AI Studio</a></div>',
            unsafe_allow_html=True,
        )

        # Divider and reset button
        if st.session_state.get("df") is not None:
            st.divider()
            if st.button(
                "Reset Sesi",
                key="reset_session_btn",
                type="secondary",
                help="Hapus data dan riwayat chat. API Key tetap tersimpan.",
            ):
                for key in ["df", "chat_history", "last_output_type", "last_output_data"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
