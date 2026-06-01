"""
Chat Area component — renders the conversation history stored in session state.

Each message in ``st.session_state.chat_history`` is a ``ChatMessage`` dict
with the following schema::

    class ChatMessage(TypedDict):
        role: Literal["user", "assistant"]
        content_type: Literal["text", "dataframe", "figure", "error"]
        content: Any        # str | pd.DataFrame | Figure
        timestamp: str      # ISO 8601 string
        prompt: str | None  # original user prompt (only for role="assistant")

Public interface
----------------
- ``render() -> None``          — iterate chat history and render each message
- ``_render_message(message: dict) -> None``  — render a single message
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def _render_chart_insight(insight: dict | None, error: str | None) -> None:
    """Render the AI-generated chart insight panel below a figure.

    Displays three sections in a styled container:
    - **Tujuan Grafik** — purpose of the chart
    - **Deskripsi Isi Grafik** — description of patterns and findings
    - **💡 Tips Insight** — actionable tips for the user

    Parameters
    ----------
    insight : dict | None
        Dict with keys ``"tujuan"``, ``"deskripsi"``, and ``"tips"`` (list of str).
        If ``None`` or not a valid dict, a fallback message is shown.
    error : str | None
        Error message if insight generation failed.
    """
    st.markdown("---")

    # Guard: if insight is not a proper dict (e.g. raw JSON string leaked through),
    # treat it as unavailable rather than displaying garbage to the user.
    if error or not isinstance(insight, dict):
        st.info(
            "ℹ️ Analisis grafik tidak tersedia saat ini."
            + (f" ({error})" if error else "")
        )
        return

    tujuan: str = insight.get("tujuan", "")
    deskripsi: str = insight.get("deskripsi", "")
    tips: list[str] = insight.get("tips", [])

    # Ensure values are plain strings — never render raw dicts/lists as text
    if not isinstance(tujuan, str):
        tujuan = str(tujuan)
    if not isinstance(deskripsi, str):
        deskripsi = str(deskripsi)
    if not isinstance(tips, list):
        tips = [str(tips)] if tips else []

    # If all fields are empty after normalisation, show fallback
    if not tujuan and not deskripsi and not tips:
        st.info("ℹ️ Analisis grafik tidak tersedia saat ini.")
        return

    # Tujuan Grafik
    if tujuan:
        with st.container(border=True):
            st.markdown("#### 🎯 Tujuan Grafik")
            st.write(tujuan)

    # Deskripsi Isi Grafik
    if deskripsi:
        with st.container(border=True):
            st.markdown("#### 📖 Deskripsi Isi Grafik")
            st.write(deskripsi)

    # Tips Insight — only render non-empty string tips
    clean_tips = [t for t in tips if isinstance(t, str) and t.strip()]
    if clean_tips:
        with st.container(border=True):
            st.markdown("#### 💡 Tips Insight")
            for tip in clean_tips:
                st.markdown(f"- {tip}")


def _render_message(message: dict[str, Any], msg_index: int = 0) -> None:
    """Render a single chat message in the appropriate Streamlit widget.

    Dispatches on ``message["role"]`` and ``message["content_type"]``:

    - **user** role: displays the content as plain text inside a user chat
      bubble.
    - **assistant** role:

      - ``content_type="dataframe"`` — interactive table via
        :func:`streamlit.dataframe`.
      - ``content_type="figure"`` — chart rendered by
        :func:`utils.chart_renderer.render`, followed by an AI-generated
        insight panel (tujuan, deskripsi, tips).
      - ``content_type="text"`` — plain text via :func:`streamlit.write`.
      - ``content_type="error"`` — error detail inside an expanded
        :func:`streamlit.expander` with :func:`streamlit.code`.

    Args:
        message: A ``ChatMessage`` dict as described in the module docstring.
        msg_index: Position of this message in chat_history, used to generate
            unique keys for widgets.
    """
    role: str = message.get("role", "assistant")
    content_type: str = message.get("content_type", "text")
    content: Any = message.get("content")

    if role == "user":
        with st.chat_message("user"):
            st.write(content)
        return

    # --- assistant messages ---
    with st.chat_message("assistant"):
        if content_type == "dataframe":
            st.dataframe(content, width="stretch")

        elif content_type == "figure":
            from utils import chart_renderer
            chart_renderer.render(content)
            # Render AI-generated insight panel
            insight: dict | None = message.get("chart_insight")
            insight_error: str | None = message.get("chart_insight_error")
            _render_chart_insight(insight, insight_error)

        elif content_type == "text":
            st.write(content)

        elif content_type == "error":
            with st.expander("❌ Error Detail", expanded=True):
                st.code(content, language="python")

        else:
            # Fallback for unknown content types — display as text.
            st.write(content)


def render() -> None:
    """Render the full chat history from ``st.session_state.chat_history``.

    Iterates over every ``ChatMessage`` stored in the session state list and
    delegates rendering to :func:`_render_message`.  If the chat history is
    empty or not yet initialised, nothing is displayed.
    """
    chat_history: list[dict[str, Any]] = st.session_state.get("chat_history", [])

    for idx, message in enumerate(chat_history):
        _render_message(message, msg_index=idx)
