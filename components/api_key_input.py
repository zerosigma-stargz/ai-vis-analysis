"""
API Key input component -- renders inline on the main page.

Provides a compact, styled input field for the Gemini API Key directly
on the main page, eliminating the need for a sidebar.

Public interface
----------------
- ``render() -> None`` -- entry point
- ``is_api_key_set() -> bool`` -- check if key is available
"""

from __future__ import annotations

import os

import streamlit as st


def render() -> None:
    """Render the Gemini API Key input on the main page.

    Displays a compact input area with:
    - Password field for API key when not yet set
    - Status indicator (active/inactive) when set
    - Button to change key and reset session

    When the API key is filled, shows a success indicator.
    When empty, shows prompt to enter the key.
    """
    # Initialise from environment variable if not yet set.
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.environ.get("GEMINI_API_KEY", "")

    # Only show the full input section if API key is NOT yet set.
    # Once set, show a compact status bar instead.
    if not st.session_state.api_key:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
                border: 2px solid #e0e7ff;
                border-radius: 14px;
                padding: 1.2rem 1.5rem;
                margin-bottom: 1rem;
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.6rem;
                    margin-bottom: 0.6rem;
                ">
                    <span style="font-size: 1.4rem;">🔑</span>
                    <span style="
                        font-size: 1rem;
                        font-weight: 700;
                        color: #1e1b4b;
                    ">Masukkan Gemini API Key untuk Memulai</span>
                </div>
                <div style="
                    font-size: 0.8rem;
                    color: #6b7280;
                    margin-bottom: 0.3rem;
                ">
                    Dapatkan API Key gratis dari
                    <a href="https://aistudio.google.com/app/apikey" target="_blank"
                       style="color: #667eea; font-weight: 600;">Google AI Studio</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        api_key_input: str = st.text_input(
            label="Gemini API Key",
            value="",
            type="password",
            key="api_key_input",
            placeholder="Masukkan Gemini API Key Anda...",
            label_visibility="collapsed",
        )

        # Sync widget value to session state.
        if api_key_input:
            st.session_state.api_key = api_key_input
            st.rerun()

    else:
        # Compact status bar when key is active
        col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
        with col1:
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
                    border: 1px solid #86efac;
                    border-radius: 10px;
                    padding: 0.6rem 1rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                ">
                    <span style="font-size: 1.1rem;">✅</span>
                    <span style="
                        font-size: 0.85rem;
                        font-weight: 600;
                        color: #166534;
                    ">API Key aktif — ketik instruksi di chat box bawah</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            if st.button("🔄 Ganti Key", key="change_api_key", type="secondary"):
                st.session_state.api_key = ""
                st.rerun()
        with col3:
            # Reset session button - only if df is loaded
            if st.session_state.get("df") is not None:
                if st.button("🔄 Reset Sesi", key="reset_session", type="secondary"):
                    for key in ["df", "chat_history", "last_output_type", "last_output_data"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()


def is_api_key_set() -> bool:
    """Return True if the API key is currently set in session state."""
    return bool(st.session_state.get("api_key", ""))
