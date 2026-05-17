"""
Sidebar component — manages the Streamlit sidebar panel.

Handles three responsibilities:
1. **API Key input** — password field that stores the Gemini API key in
   session state, with environment-variable initialisation and a warning
   when the key is cleared.
2. **Prompt submission** — text area + "Kirim" button that sends the user's
   prompt to :class:`core.gemini_client.GeminiClient`, executes the returned
   code via :func:`core.code_executor.execute`, and appends both the user
   message and the AI response to ``session_state.chat_history``.
3. **Session reset** — "Reset Sesi" button that clears the active DataFrame
   and chat history while preserving the API key.

Public interface
----------------
- ``render() -> None``                  — entry point; wraps all helpers in
  ``st.sidebar``
- ``_handle_api_key_input() -> None``   — API key widget (Tasks 12.1)
- ``_handle_prompt_submission() -> None`` — prompt + send button (Task 12.2)
- ``_handle_reset() -> None``           — reset session button (Task 12.3)
"""

from __future__ import annotations

import os
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
            "🔑 **Kuota Gemini API Key Habis**\n\n"
            "Kuota penggunaan API Key Anda telah habis. "
            "Silakan masukkan **API Key baru** di kolom *Gemini API Key* di atas "
            "untuk melanjutkan sesi analisis.",
            icon="⚠️",
        )
    elif error_msg.startswith(_ERR_INVALID_KEY):
        st.error(
            "🔑 **Gemini API Key Tidak Valid**\n\n"
            "API Key yang Anda masukkan tidak dikenali oleh Google. "
            "Silakan periksa dan masukkan **API Key yang benar** "
            "di kolom *Gemini API Key* di atas.",
            icon="❌",
        )

    # Clear the stored key so the password input becomes editable again
    # and the user is prompted to enter a new one.
    st.session_state.api_key = ""


# ---------------------------------------------------------------------------
# Task 12.1 — API Key input
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
        placeholder="Masukkan Gemini API Key Anda…",
    )

    # Sync widget value to session state.
    st.session_state.api_key = api_key_input

    # Warn when the key is cleared after previously being set.
    if previous_key and not api_key_input:
        st.warning(
            "⚠️ API Key telah dihapus. Masukkan kembali untuk menggunakan fitur AI."
        )


# ---------------------------------------------------------------------------
# Task 12.2 — Prompt submission
# ---------------------------------------------------------------------------


def _handle_prompt_submission() -> None:
    """Render the prompt text area and "Kirim" button in the sidebar.

    Behaviour
    ---------
    - Only displayed when ``session_state.df`` is not ``None``.
    - The "Kirim" button is disabled when ``session_state.api_key`` is empty
      (requirement 1.3).
    - On click:

      1. Builds ``df_schema`` from the active DataFrame.
      2. Creates a :class:`~core.gemini_client.GeminiClient` with the current
         API key.
      3. Calls :meth:`~core.gemini_client.GeminiClient.generate_code` with the
         prompt and schema.
      4. If code generation succeeds, calls
         :func:`~core.code_executor.execute` with the generated code and the
         active DataFrame.
      5. Appends a *user* message and an *assistant* message to
         ``session_state.chat_history``.
      6. If the execution output is a DataFrame, updates
         ``session_state.df``.

    Requirements: 1.3, 5.1, 5.2, 5.5, 5.7, 5.8, 6.1, 6.2
    """
    df: pd.DataFrame | None = st.session_state.get("df")

    if df is None:
        return

    prompt: str = st.text_area(
        label="Prompt",
        placeholder=(
            "Contoh: Buat grafik batang jumlah penjualan per bulan.\n"
            "Atau: Hapus kolom 'id' dan tampilkan 10 baris pertama."
        ),
        key="prompt_box",
        label_visibility="collapsed",
        height=150,
    )

    api_key: str = st.session_state.get("api_key", "")
    send_disabled: bool = not bool(api_key)

    if st.button(
        "Kirim",
        disabled=send_disabled,
        use_container_width=True,
        type="primary",
    ):
        if not prompt.strip():
            st.warning("⚠️ Prompt tidak boleh kosong.")
            return

        # Build DataFrame schema for the system prompt.
        # Include datetime column info and date range to help Gemini generate correct time-series code.
        datetime_cols = []
        date_ranges = {}
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
                    parsed = pd.to_datetime(df[col].dropna().head(20), errors='coerce')
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

        with st.spinner("Menghubungi Gemini AI…"):
            client = GeminiClient(api_key=api_key)
            code, error_msg = client.generate_code(prompt=prompt, df_schema=df_schema)

        if error_msg:
            # Check for quota-exhausted / invalid-key errors first — these
            # need a prominent UI notification and the key must be cleared.
            if _is_api_key_error(error_msg):
                _show_api_key_error(error_msg)
                return

            # Generation failed — record an error assistant message.
            _append_messages(
                prompt=prompt,
                user_content=prompt,
                assistant_content_type="error",
                assistant_content=error_msg,
            )
            return

        # Execute the generated code in the sandbox.
        with st.spinner("Mengeksekusi kode…"):
            result = code_executor.execute(code=code, df=df)

        # If the output is a figure, generate AI insight for it.
        chart_insight: dict | None = None
        chart_insight_error: str | None = None

        if result["output_type"] == "figure":
            with st.spinner("Menganalisis grafik…"):
                # Detect chart type hint from the prompt
                chart_type_hint = ""
                prompt_lower = prompt.lower()
                for keyword in ("bar", "line", "scatter", "pie", "box", "heatmap", "area", "histogram"):
                    if keyword in prompt_lower:
                        chart_type_hint = keyword + " chart"
                        break

                chart_insight, chart_insight_error = client.generate_chart_insight(
                    prompt=prompt,
                    df_schema=df_schema,
                    chart_type=chart_type_hint,
                )

            # If insight generation hit a quota/key error, show the warning
            # but still display the chart — the insight panel will show a
            # fallback message.
            if chart_insight_error and _is_api_key_error(chart_insight_error):
                _show_api_key_error(chart_insight_error)
                chart_insight_error = "Analisis grafik tidak tersedia karena API Key bermasalah."

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
# Task 12.3 — Session reset
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
        "🔄 Reset Sesi",
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
# Task 12.4 — render() entry point
# ---------------------------------------------------------------------------


def render() -> None:
    """Render all sidebar elements inside ``st.sidebar``.

    Calls, in order:
    1. :func:`_handle_api_key_input` — always visible
    2. :func:`_handle_prompt_submission` — visible only when ``df`` is loaded
    3. :func:`_handle_reset` — visible only when ``df`` is loaded

    Requirements: 1.1, 5.1, 10.1
    """
    with st.sidebar:
        st.header("⚙️ Pengaturan")
        _handle_api_key_input()
        st.divider()
        _handle_prompt_submission()
        _handle_reset()
