"""
API Key input component -- renders inline on the main page.

Public interface
----------------
- ``render() -> None``
- ``is_api_key_set() -> bool``
"""

from __future__ import annotations

import os

import streamlit as st


def render() -> None:
    """Render the Gemini API Key input inline on the main page."""
    if "api_key" not in st.session_state:
        st.session_state.api_key = os.environ.get("GEMINI_API_KEY", "")

    if not st.session_state.api_key:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #f0f7ff 0%, #e0f2fe 100%);
                border: 1px solid #bfdbfe;
                border-left: 4px solid #1e40af;
                border-radius: 8px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
            ">
                <div style="
                    font-size: 0.92rem;
                    font-weight: 600;
                    color: #0f172a;
                    margin-bottom: 0.3rem;
                ">Masukkan Gemini API Key</div>
                <div style="
                    font-size: 0.78rem;
                    color: #475569;
                ">
                    Dapatkan API Key dari
                    <a href="https://aistudio.google.com/app/apikey" target="_blank"
                       style="color: #1e40af; text-decoration: none; font-weight: 500;">Google AI Studio</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        api_key_value: str = st.text_input(
            label="Gemini API Key",
            value="",
            type="password",
            key="api_key_input",
            placeholder="Paste API Key Anda di sini...",
            label_visibility="collapsed",
        )

        if api_key_value:
            st.session_state.api_key = api_key_value
            st.rerun()

    else:
        col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
        with col1:
            st.markdown(
                """
                <div style="
                    background: #ecfdf5;
                    border: 1px solid #a7f3d0;
                    border-radius: 8px;
                    padding: 0.5rem 1rem;
                ">
                    <span style="
                        font-size: 0.82rem;
                        font-weight: 500;
                        color: #065f46;
                    ">API Key terhubung - ketik instruksi di chat box bawah</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            if st.button("Ganti Key", key="change_api_key", type="secondary"):
                st.session_state.api_key = ""
                st.rerun()
        with col3:
            if st.session_state.get("df") is not None:
                if st.button("Reset Sesi", key="reset_session", type="secondary"):
                    for key in ["df", "chat_history", "last_output_type", "last_output_data"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()


def is_api_key_set() -> bool:
    """Return True if the API key is currently set in session state."""
    return bool(st.session_state.get("api_key", ""))
