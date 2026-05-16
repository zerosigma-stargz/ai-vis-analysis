"""
Download Manager — Provides Streamlit download buttons for DataFrames and figures.

Supports:
- DataFrame → CSV, XLSX
- Figure (Matplotlib or Plotly) → JPG, PNG, PDF
"""

from __future__ import annotations

import io
import os
from typing import Any

import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------------
# Helper: DataFrame conversion
# ---------------------------------------------------------------------------


def _df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to UTF-8 encoded CSV bytes.

    Args:
        df: The DataFrame to convert.

    Returns:
        CSV-encoded bytes with index excluded.
    """
    return df.to_csv(index=False).encode("utf-8")


def _df_to_xlsx_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to XLSX bytes using the openpyxl engine.

    Args:
        df: The DataFrame to convert.

    Returns:
        XLSX-encoded bytes.
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Helper: Figure conversion
# ---------------------------------------------------------------------------


def _fig_to_image_bytes(fig: Any, fmt: str, dpi: int = 150) -> bytes:
    """Convert a Matplotlib or Plotly figure to JPG/PNG image bytes.

    Args:
        fig: A ``matplotlib.figure.Figure`` or ``plotly.graph_objs.Figure``.
        fmt: Image format string — ``"jpg"`` or ``"png"``.
        dpi: Resolution in dots per inch (minimum 150). Ignored for Plotly.

    Returns:
        Image bytes in the requested format.

    Raises:
        TypeError: If *fig* is neither a Matplotlib nor a Plotly figure.
        ValueError: If *fmt* is not ``"jpg"`` or ``"png"``.
    """
    if fmt not in ("jpg", "jpeg", "png"):
        raise ValueError(f"Unsupported image format: {fmt!r}. Use 'jpg' or 'png'.")

    # Normalise "jpg" → "jpeg" for Matplotlib; keep "png" as-is.
    mpl_fmt = "jpeg" if fmt in ("jpg", "jpeg") else fmt
    plotly_fmt = "jpg" if fmt in ("jpg", "jpeg") else fmt

    # Ensure DPI is at least 150.
    dpi = max(dpi, 150)

    try:
        import matplotlib.figure as mpl_fig

        if isinstance(fig, mpl_fig.Figure):
            buf = io.BytesIO()
            fig.savefig(buf, format=mpl_fmt, dpi=dpi, bbox_inches="tight")
            return buf.getvalue()
    except ImportError:
        pass

    try:
        import plotly.graph_objs as go

        if isinstance(fig, go.Figure):
            return fig.to_image(format=plotly_fmt)
    except ImportError:
        pass

    raise TypeError(
        f"Unsupported figure type: {type(fig).__name__}. "
        "Expected matplotlib.figure.Figure or plotly.graph_objs.Figure."
    )


def _fig_to_pdf_bytes(fig: Any) -> bytes:
    """Convert a Matplotlib or Plotly figure to PDF bytes.

    Args:
        fig: A ``matplotlib.figure.Figure`` or ``plotly.graph_objs.Figure``.

    Returns:
        PDF bytes.

    Raises:
        TypeError: If *fig* is neither a Matplotlib nor a Plotly figure.
    """
    try:
        import matplotlib.figure as mpl_fig

        if isinstance(fig, mpl_fig.Figure):
            buf = io.BytesIO()
            fig.savefig(buf, format="pdf", bbox_inches="tight")
            return buf.getvalue()
    except ImportError:
        pass

    try:
        import plotly.graph_objs as go

        if isinstance(fig, go.Figure):
            buf = io.BytesIO()
            fig.write_image(buf, format="pdf")
            return buf.getvalue()
    except ImportError:
        pass

    raise TypeError(
        f"Unsupported figure type: {type(fig).__name__}. "
        "Expected matplotlib.figure.Figure or plotly.graph_objs.Figure."
    )


# ---------------------------------------------------------------------------
# Public render functions
# ---------------------------------------------------------------------------


def render_dataframe_downloads(df: pd.DataFrame, base_filename: str, key_suffix: str = "") -> None:
    """Render Streamlit download buttons for a DataFrame (CSV and Excel).

    Displays two side-by-side ``st.download_button`` widgets that let the
    user download *df* as a CSV or XLSX file.

    Args:
        df: The DataFrame to offer for download.
        base_filename: The original filename (with or without extension).
        key_suffix: Optional suffix to make button keys unique when multiple
            DataFrames are rendered in the same session.
    """
    # Strip extension to get the base stem.
    stem = os.path.splitext(base_filename)[0]

    col_csv, col_xlsx = st.columns(2)

    with col_csv:
        st.download_button(
            label="⬇️ Download CSV",
            data=_df_to_csv_bytes(df),
            file_name=f"{stem}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"dl_csv_{key_suffix}",
        )

    with col_xlsx:
        st.download_button(
            label="⬇️ Download Excel (.xlsx)",
            data=_df_to_xlsx_bytes(df),
            file_name=f"{stem}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key=f"dl_xlsx_{key_suffix}",
        )


def render_figure_downloads(fig: Any, base_filename: str) -> None:
    """Render Streamlit download buttons for a figure (JPG, PNG, PDF).

    Displays three side-by-side ``st.download_button`` widgets that let the
    user download *fig* as a JPG, PNG, or PDF file.

    Args:
        fig: A ``matplotlib.figure.Figure`` or ``plotly.graph_objs.Figure``.
        base_filename: The original filename (with or without extension).
            The extension is stripped and used as the stem for the download
            filenames, e.g. ``"chart.png"`` → ``"chart.jpg"`` /
            ``"chart.png"`` / ``"chart.pdf"``.
    """
    # Strip extension to get the base stem.
    stem = os.path.splitext(base_filename)[0]

    col_jpg, col_png, col_pdf = st.columns(3)

    with col_jpg:
        st.download_button(
            label="⬇️ Download JPG",
            data=_fig_to_image_bytes(fig, fmt="jpg"),
            file_name=f"{stem}.jpg",
            mime="image/jpeg",
            use_container_width=True,
        )

    with col_png:
        st.download_button(
            label="⬇️ Download PNG",
            data=_fig_to_image_bytes(fig, fmt="png"),
            file_name=f"{stem}.png",
            mime="image/png",
            use_container_width=True,
        )

    with col_pdf:
        st.download_button(
            label="⬇️ Download PDF",
            data=_fig_to_pdf_bytes(fig),
            file_name=f"{stem}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
