"""
Floating chat box component -- sticky chat input at the bottom of the page.

Handles prompt submission by sending the user's instruction to
:class:`core.gemini_client.GeminiClient`, executing the returned code via
:func:`core.code_executor.execute`, and appending both the user message and
the AI response to ``session_state.chat_history``.

Public interface
----------------
- ``render() -> None`` -- entry point called by ``data_page.py``
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st

from core import code_executor
from core.gemini_client import GeminiClient


# ---------------------------------------------------------------------------
# Error type prefixes returned by GeminiClient
# ---------------------------------------------------------------------------

_ERR_QUOTA = "QUOTA_EXHAUSTED:"
_ERR_INVALID_KEY = "INVALID_KEY:"


def _is_api_key_error(error_msg: str) -> bool:
    """Return True if the error is a quota-exhausted or invalid-key error."""
    return error_msg.startswith(_ERR_QUOTA) or error_msg.startswith(_ERR_INVALID_KEY)


def _show_api_key_error(error_msg: str) -> None:
    """Display a prominent warning and clear the stored API key.

    When the quota is exhausted or the key is invalid, the API key is removed
    from session state so the input field becomes active again and the user
    can enter a new key immediately.
    """
    if error_msg.startswith(_ERR_QUOTA):
        st.error(
            "\U0001f511 **Kuota Gemini API Key Habis**\n\n"
            "Kuota penggunaan API Key Anda telah habis. "
            "Silakan masukkan **API Key baru** di kolom *Gemini API Key* di sidebar "
            "untuk melanjutkan sesi analisis.",
            icon="\u26a0\ufe0f",
        )
    elif error_msg.startswith(_ERR_INVALID_KEY):
        st.error(
            "\U0001f511 **Gemini API Key Tidak Valid**\n\n"
            "API Key yang Anda masukkan tidak dikenali oleh Google. "
            "Silakan periksa dan masukkan **API Key yang benar** "
            "di kolom *Gemini API Key* di sidebar.",
            icon="\u274c",
        )

    # Clear the stored key so the password input becomes editable again
    # and the user is prompted to enter a new one.
    st.session_state.api_key = ""


def _append_messages(
    prompt: str,
    user_content: str,
    assistant_content_type: str,
    assistant_content: Any,
    chart_insight: dict | None = None,
    chart_insight_error: str | None = None,
) -> None:
    """Append a user message and an assistant message to chat history.

    Parameters
    ----------
    prompt:
        The original user prompt text.
    user_content:
        Content stored in the user message (same as *prompt* in practice).
    assistant_content_type:
        One of ``"dataframe"``, ``"figure"``, ``"text"``, or ``"error"``.
    assistant_content:
        The actual output data (DataFrame, Figure, str, etc.).
    chart_insight:
        AI-generated insight dict for figure outputs (keys: tujuan, deskripsi, tips).
    chart_insight_error:
        Error message if insight generation failed.
    """
    now: str = datetime.now().isoformat()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User message.
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content_type": "text",
            "content": user_content,
            "timestamp": now,
            "prompt": None,
        }
    )

    # Assistant message.
    assistant_msg: dict[str, Any] = {
        "role": "assistant",
        "content_type": assistant_content_type,
        "content": assistant_content,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
    }

    # Attach chart insight data if this is a figure response.
    if assistant_content_type == "figure":
        assistant_msg["chart_insight"] = chart_insight
        assistant_msg["chart_insight_error"] = chart_insight_error

    st.session_state.chat_history.append(assistant_msg)


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------


def render() -> None:
    """Render the floating chat input at the bottom of the page.

    Uses ``st.chat_input`` which is sticky at the bottom by default.
    When the user submits a prompt, it triggers the full Gemini AI pipeline:
    code generation, execution, chart insight (if applicable), and appends
    the results to the chat history.

    Requirements: 5.1, 5.2, 5.5, 5.7, 5.8, 6.1, 6.2
    """
    prompt: str | None = st.chat_input(
        "Ketik instruksi analisis atau visualisasi...",
    )

    if prompt is None:
        return

    # Check API key is available.
    api_key: str = st.session_state.get("api_key", "")
    if not api_key:
        st.toast(
            "\u26a0\ufe0f Silakan masukkan **Gemini API Key** di sidebar terlebih dahulu.",
            icon="\u26a0\ufe0f",
        )
        return

    df: pd.DataFrame | None = st.session_state.get("df")
    if df is None:
        return

    # Note: st.chat_input guarantees a non-empty string on submission,
    # so an empty-prompt guard is not needed here.

    # Build DataFrame schema for the system prompt.
    # Include datetime column info and date range to help Gemini generate
    # correct time-series code.
    datetime_cols: list[str] = []
    date_ranges: dict[str, Any] = {}
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
            date_ranges[col] = {
                "min": str(df[col].min()),
                "max": str(df[col].max()),
            }
        elif df[col].dtype == object:
            # Try to detect string columns that look like dates
            sample_vals = df[col].dropna().head(5).tolist()
            try:
                parsed = pd.to_datetime(df[col].dropna().head(20), errors="coerce")
                if parsed.notna().sum() >= 10:
                    datetime_cols.append(col)
                    date_ranges[col] = {
                        "min": str(parsed.min()),
                        "max": str(parsed.max()),
                        "sample_raw": sample_vals[:3],
                        "note": "kolom string yang dapat dikonversi ke datetime",
                    }
            except Exception:
                pass

    df_schema: dict[str, Any] = {
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "shape": df.shape,
        "sample": df.head(3).to_dict(orient="records"),
        "datetime_columns": datetime_cols,
        "date_ranges": date_ranges,
    }

    with st.spinner("Menghubungi Gemini AI\u2026"):
        client = GeminiClient(api_key=api_key)
        code, error_msg = client.generate_code(prompt=prompt, df_schema=df_schema)

    if error_msg:
        # Check for quota-exhausted / invalid-key errors first -- these
        # need a prominent UI notification and the key must be cleared.
        if _is_api_key_error(error_msg):
            _show_api_key_error(error_msg)
            return

        # Generation failed -- record an error assistant message.
        _append_messages(
            prompt=prompt,
            user_content=prompt,
            assistant_content_type="error",
            assistant_content=error_msg,
        )
        st.rerun()
        return

    # Execute the generated code in the sandbox.
    with st.spinner("Mengeksekusi kode\u2026"):
        result = code_executor.execute(code=code, df=df)

    # If the output is a figure, generate AI insight for it.
    chart_insight: dict | None = None
    chart_insight_error: str | None = None

    if result["output_type"] == "figure":
        with st.spinner("Menganalisis grafik\u2026"):
            # Detect chart type hint from the prompt
            chart_type_hint = ""
            prompt_lower = prompt.lower()
            for keyword in (
                "bar",
                "line",
                "scatter",
                "pie",
                "box",
                "heatmap",
                "area",
                "histogram",
            ):
                if keyword in prompt_lower:
                    chart_type_hint = keyword + " chart"
                    break

            chart_insight, chart_insight_error = client.generate_chart_insight(
                prompt=prompt,
                df_schema=df_schema,
                chart_type=chart_type_hint,
            )

        # If insight generation hit a quota/key error, show the warning
        # but still display the chart -- the insight panel will show a
        # fallback message.
        if chart_insight_error and _is_api_key_error(chart_insight_error):
            _show_api_key_error(chart_insight_error)
            chart_insight_error = (
                "Analisis grafik tidak tersedia karena API Key bermasalah."
            )

    # Append user message and AI response to chat history.
    _append_messages(
        prompt=prompt,
        user_content=prompt,
        assistant_content_type=result["output_type"],
        assistant_content=result["data"],
        chart_insight=chart_insight,
        chart_insight_error=chart_insight_error,
    )

    # Update the active DataFrame if the output is a transformed DataFrame.
    if result["output_type"] == "dataframe" and isinstance(
        result["data"], pd.DataFrame
    ):
        st.session_state.df = result["data"]

    # Rerun so the chat area and data page reflect the latest state.
    st.rerun()
