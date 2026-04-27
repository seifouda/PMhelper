"""Open any Plotly figure in the default browser (Phase 11).

Thin wrapper: serialises a ``plotly.graph_objects.Figure`` to a
self-contained HTML temp file and opens it in the system browser.
Reuses the robust ``_open_in_browser`` helper from interactive_network.
"""
from __future__ import annotations

import tempfile
from typing import Optional

try:
    import plotly.graph_objects as go  # type: ignore
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


def open_chart_in_browser(
        fig: "go.Figure",
        title: str = "PMhelper Chart") -> Optional[str]:
    """Write *fig* to a temp HTML file and open it in the browser.

    Parameters
    ----------
    fig : plotly.graph_objects.Figure
        The chart to display.
    title : str
        Page ``<title>`` tag.

    Returns
    -------
    str or None
        The path to the generated HTML file, or *None* on failure.
    """
    if fig is None:
        return None

    try:
        fd, path = tempfile.mkstemp(suffix=".html", prefix="pmhelper_chart_")
        import os
        os.close(fd)

        fig.update_layout(title_text=title)
        fig.write_html(
            path,
            include_plotlyjs="cdn",
            full_html=True,
            config={
                "displayModeBar": True,
                "toImageButtonOptions": {"format": "png", "scale": 2},
                "scrollZoom": True,
            },
        )

        # Reuse the robust browser-opener
        from pmhelper.utils.interactive_network import _open_in_browser
        _open_in_browser(path)
        return path
    except Exception:
        return None
