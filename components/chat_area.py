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

from utils import chart_renderer, download_manager


def _render_message(message: dict[str, Any], msg_index: int = 0) -> None:
    """Render a single chat message in the appropriate Streamlit widget.

    Dispatches on ``message["role"]`` and ``message["content_type"]``:

    - **user** role: displays the content as plain text inside a user chat
      bubble.
    - **assistant** role:

      - ``content_type="dataframe"`` — interactive table via
        :func:`streamlit.dataframe` followed by CSV/XLSX download buttons.
      - ``content_type="figure"`` — chart rendered by
        :func:`utils.chart_renderer.render` followed by JPG/PNG/PDF download
        buttons.
      - ``content_type="text"`` — plain text via :func:`streamlit.write`.
      - ``content_type="error"`` — error detail inside an expanded
        :func:`streamlit.expander` with :func:`streamlit.code`.

    Args:
        message: A ``ChatMessage`` dict as described in the module docstring.
        msg_index: Position of this message in chat_history, used to generate
            unique keys for download buttons.
    """
    role: str = message.get("role", "assistant")
    content_type: str = message.get("content_type", "text")
    content: Any = message.get("content")

    # Base filename used for download buttons (strip extension later inside
    # download_manager, which already handles that).
    base_filename: str = st.session_state.get("original_filename", "download")

    if role == "user":
        with st.chat_message("user"):
            st.write(content)
        return

    # --- assistant messages ---
    with st.chat_message("assistant"):
        if content_type == "dataframe":
            st.dataframe(content, use_container_width=True)
            download_manager.render_dataframe_downloads(
                content, base_filename, key_suffix=str(msg_index)
            )

        elif content_type == "figure":
            chart_renderer.render(content)
            download_manager.render_figure_downloads(content, base_filename)

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
