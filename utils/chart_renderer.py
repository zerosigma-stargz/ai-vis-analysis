"""
Chart renderer utility for routing Matplotlib and Plotly figures to Streamlit.

Provides a unified `render()` interface that detects the figure type and
delegates to the appropriate Streamlit display function.
"""

from typing import Any

import matplotlib.figure
import plotly.graph_objs
import streamlit as st


def _is_matplotlib(fig: Any) -> bool:
    """Check whether *fig* is a Matplotlib Figure.

    Args:
        fig: Any object to inspect.

    Returns:
        ``True`` if *fig* is an instance of :class:`matplotlib.figure.Figure`,
        ``False`` otherwise.
    """
    return isinstance(fig, matplotlib.figure.Figure)


def _is_plotly(fig: Any) -> bool:
    """Check whether *fig* is a Plotly Figure.

    Args:
        fig: Any object to inspect.

    Returns:
        ``True`` if *fig* is an instance of :class:`plotly.graph_objs.Figure`,
        ``False`` otherwise.
    """
    return isinstance(fig, plotly.graph_objs.Figure)


def render(fig: Any) -> None:
    """Render a figure object in the Streamlit app.

    Routes the figure to the correct Streamlit display function based on its
    type:

    - :class:`matplotlib.figure.Figure` → :func:`streamlit.pyplot`
    - :class:`plotly.graph_objs.Figure` → :func:`streamlit.plotly_chart`
      (with ``width="stretch"``)

    If *fig* is neither a Matplotlib nor a Plotly figure, a descriptive
    warning is shown in the UI instead of raising an exception.

    Args:
        fig: The figure object to render.  Expected to be either a
            :class:`matplotlib.figure.Figure` or a
            :class:`plotly.graph_objs.Figure`.
    """
    if _is_matplotlib(fig):
        st.pyplot(fig)
    elif _is_plotly(fig):
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning(
            f"⚠️ Tipe grafik tidak dikenali: `{type(fig).__name__}`. "
            "Hanya grafik Matplotlib (`matplotlib.figure.Figure`) dan "
            "Plotly (`plotly.graph_objs.Figure`) yang didukung."
        )
