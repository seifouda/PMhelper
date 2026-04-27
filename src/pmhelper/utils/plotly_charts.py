"""
Plotly Chart Generators — one function per chart type.

Each function returns a ``plotly.graph_objects.Figure`` (or *None*)
ready to be rendered by ``PlotlyChartFrame.update_chart(fig)``.

Tabs import only the functions they need.
"""

from __future__ import annotations
from typing import Any

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import numpy as np
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# ────────────────────────────────────────────────────────────────────
# 1. Gantt (CPM)
# ────────────────────────────────────────────────────────────────────

def plotly_gantt_cpm(
        results_data: dict,
        tracking: bool = False) -> "go.Figure | None":
    """Horizontal bar Gantt from CPM results_data."""
    if not PLOTLY_AVAILABLE:
        return None
    activities = results_data.get("activities", [])
    critical_set = set(results_data.get("critical_activities", []))
    if not activities:
        return None

    sorted_acts = sorted(
        activities, key=lambda a: (
            float(
                a.get(
                    "ES", 0)), a.get(
                "id", "")))
    ids = [a.get("id", "") for a in sorted_acts]
    fig = go.Figure()

    for act in sorted_acts:
        aid = act.get("id", "")
        es = float(act.get("ES", 0))
        ef = float(act.get("EF", 0))
        lf = float(act.get("LF", 0))
        dur = ef - es
        flt = max(0, lf - ef)
        is_crit = aid in critical_set
        color = "#E74C3C" if is_crit else "#3498DB"
        name_str = act.get("name", act.get("activity", ""))

        hover = (f"<b>{aid}</b>{'<br>' + str(name_str) if name_str else ''}"
                 f"<br>ES={es:.0f}  EF={ef:.0f}  LF={lf:.0f}"
                 f"<br>Duration={dur:.0f}  Float={flt:.0f}"
                 f"<br>{'CRITICAL' if is_crit else 'Non-critical'}")

        # Main bar
        fig.add_trace(go.Bar(
            y=[aid], x=[dur], base=[es], orientation="h",
            marker=dict(color=color, opacity=0.8,
                        line=dict(width=0.5, color="#333")),
            hovertemplate=hover + "<extra></extra>",
            showlegend=False,
        ))
        # Slack bar
        if flt > 0.5:
            fig.add_trace(go.Bar(
                y=[aid], x=[flt], base=[ef], orientation="h",
                marker=dict(color="#bdc3c7", opacity=0.5,
                            line=dict(width=0.5, color="#999")),
                hovertemplate=f"Float={flt:.0f}<extra></extra>",
                showlegend=False,
            ))

    proj_dur = results_data.get("project_duration", "?")
    fig.update_layout(
        title=f"Gantt Chart — {
            len(activities)} activities, Duration: {proj_dur}",
        xaxis=dict(
            title="Time",
            showgrid=True,
            gridcolor="#eee"),
        yaxis=dict(
            title="",
            autorange="reversed",
            categoryorder="array",
            categoryarray=ids),
        barmode="overlay",
        plot_bgcolor="white",
        hovermode="closest",
        margin=dict(
            l=80,
            r=20,
            t=50,
            b=40),
        height=max(
            400,
            len(activities) *
            22 +
            100),
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 2. PERT Network Diagram
# ────────────────────────────────────────────────────────────────────

def plotly_pert_network(
        results_data: dict,
        analysis_mode: str | None = None) -> "go.Figure | None":
    """Interactive PERT network diagram (same layout engine as AON)."""
    # Reuse the network generator with minor label tweaks
    from pmhelper.utils.plotly_network import generate_plotly_network
    fig = generate_plotly_network(results_data, analysis_mode)
    if fig:
        fig.update_layout(title=dict(text=fig.layout.title.text.replace(
            "Interactive Network", "PERT Network")))
    return fig


# ────────────────────────────────────────────────────────────────────
# 3. EVM S-Curve
# ────────────────────────────────────────────────────────────────────

def plotly_scurve(
        periods: list,
        *,
        compact: bool = False) -> "go.Figure | None":
    """Cumulative PV / EV / AC S-curve.

    Parameters
    ----------
    periods : list of objects with .pv_cumulative, .ev_cumulative, .ac_cumulative, .label/.index
    compact : if True, produce a smaller chart (dashboard mini version)
    """
    if not PLOTLY_AVAILABLE or not periods:
        return None

    x = [getattr(p, "label", getattr(p, "index", i))
         for i, p in enumerate(periods)]
    pv = [getattr(p, "pv_cumulative", 0) for p in periods]
    ev = [getattr(p, "ev_cumulative", 0) for p in periods]
    ac = [getattr(p, "ac_cumulative", 0) for p in periods]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=pv,
            mode="lines+markers",
            name="PV",
            line=dict(
                color="green",
                dash="dash"),
            marker=dict(
                size=5)))
    fig.add_trace(go.Scatter(x=x, y=ev, mode="lines+markers", name="EV",
                             line=dict(color="blue"), marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=x, y=ac, mode="lines+markers", name="AC",
                             line=dict(color="red"), marker=dict(size=5)))

    h = 250 if compact else 450
    fig.update_layout(
        title="S-Curve" if compact else "Earned Value S-Curve (PV / EV / AC)",
        xaxis=dict(
            title="Period",
            showgrid=True,
            gridcolor="#eee"),
        yaxis=dict(
            title="Cumulative Value",
            showgrid=True,
            gridcolor="#eee"),
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0.5,
            xanchor="center"),
        margin=dict(
            l=60,
            r=20,
            t=50,
            b=40),
        height=h,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 4. Three-Point Estimates
# ────────────────────────────────────────────────────────────────────

def plotly_three_point(result: Any) -> "go.Figure | None":
    """4-series line chart (O / M / P / Expected) per activity."""
    if not PLOTLY_AVAILABLE:
        return None

    acts = getattr(result, "activities", [])
    if not acts:
        return None

    ids = [a.activity_id for a in acts]
    o = [a.optimistic for a in acts]
    m = [a.most_likely for a in acts]
    p = [a.pessimistic for a in acts]
    te = [a.expected for a in acts]
    crits = [a.is_critical for a in acts]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ids,
            y=o,
            mode="lines+markers",
            name="Optimistic (O)",
            line=dict(
                color="blue",
                dash="dash"),
            marker=dict(
                size=5)))
    fig.add_trace(
        go.Scatter(
            x=ids,
            y=m,
            mode="lines+markers",
            name="Most Likely (M)",
            line=dict(
                color="green"),
            marker=dict(
                size=5)))
    fig.add_trace(
        go.Scatter(
            x=ids,
            y=p,
            mode="lines+markers",
            name="Pessimistic (P)",
            line=dict(
                color="red",
                dash="dash"),
            marker=dict(
                size=5)))
    fig.add_trace(
        go.Scatter(
            x=ids,
            y=te,
            mode="lines+markers",
            name="Expected (tₑ)",
            line=dict(
                color="black",
                width=2),
            marker=dict(
                size=6,
                symbol="square")))

    # Shade critical columns
    shapes = []
    for i, c in enumerate(crits):
        if c:
            shapes.append(dict(type="rect", x0=i - 0.4, x1=i + 0.4,
                               y0=0, y1=1, yref="paper",
                               fillcolor="red", opacity=0.06, line_width=0))

    formula = getattr(result, "formula", "")
    fig.update_layout(
        title=f"Three-Point Estimates — {formula}",
        xaxis=dict(
            title="Activity",
            showgrid=True,
            gridcolor="#eee"),
        yaxis=dict(
            title="Duration",
            showgrid=True,
            gridcolor="#eee"),
        plot_bgcolor="white",
        hovermode="x unified",
        shapes=shapes,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0.5,
            xanchor="center"),
        margin=dict(
            l=60,
            r=20,
            t=50,
            b=40),
        height=400,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 5a. Financial — Cumulative Cash Flow
# ────────────────────────────────────────────────────────────────────

def plotly_financial_cf(payback_details: list,
                        initial_investment: float) -> "go.Figure | None":
    """Grouped bar chart: Cumulative CF vs Discounted Cumulative CF."""
    if not PLOTLY_AVAILABLE or not payback_details:
        return None

    periods = [d.period for d in payback_details]
    cum = [d.cumulative for d in payback_details]
    dcum = [d.discounted_cumulative for d in payback_details]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=periods, y=cum, name="Cumulative CF",
                         marker_color="#3b82f6", opacity=0.8))
    fig.add_trace(go.Bar(x=periods, y=dcum, name="Discounted Cumul. CF",
                         marker_color="#8b5cf6", opacity=0.8))
    fig.add_hline(y=initial_investment, line_dash="dash", line_color="red",
                  annotation_text=f"Investment = {initial_investment:,.0f}")
    fig.add_hline(y=0, line_color="black", line_width=0.8, opacity=0.4)

    fig.update_layout(
        title="Cumulative Cash Flow Analysis",
        barmode="group",
        xaxis=dict(title="Period", showgrid=False),
        yaxis=dict(title="Value", showgrid=True, gridcolor="#eee"),
        plot_bgcolor="white", hovermode="x unified",
        margin=dict(l=60, r=20, t=50, b=40), height=380,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 5b. Financial — Factor Scoring
# ────────────────────────────────────────────────────────────────────

def plotly_factor_scoring(result: Any) -> "go.Figure | None":
    """Bar chart comparing project scores."""
    if not PLOTLY_AVAILABLE:
        return None
    projs = getattr(result, "projects", [])
    if not projs:
        return None

    names = [p.project_name for p in projs]
    totals = [p.total for p in projs]
    colors = ["#16a34a" if p.rank == 1 else "#6b7280" for p in projs]
    model = getattr(result, "model", "")

    fig = go.Figure(
        go.Bar(
            x=names,
            y=totals,
            marker_color=colors,
            opacity=0.85))
    fig.update_layout(
        title=f"Project Scores — {model} Model",
        xaxis=dict(title="Project"),
        yaxis=dict(title="Score", showgrid=True, gridcolor="#eee"),
        plot_bgcolor="white", margin=dict(l=60, r=20, t=50, b=40), height=350,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 6. Risk Heat Map
# ────────────────────────────────────────────────────────────────────

def plotly_risk_matrix(risks: list) -> "go.Figure | None":
    """5×5 risk heat map with numbered risk dots."""
    if not PLOTLY_AVAILABLE:
        return None
    if not risks:
        return None
    try:
        import numpy as _np
    except ImportError:
        return None

    # Build 5×5 grid
    grid = _np.zeros((5, 5))
    impact_labels = ["Very Low", "Low", "Medium", "High", "Very High"]
    prob_labels = ["Very Low", "Low", "Medium", "High", "Very High"]
    # Fill exposure
    for i in range(5):
        for j in range(5):
            grid[i][j] = (i + 1) * (j + 1)

    # Risk colorscale: green → yellow → orange → red
    colorscale = [[0, "#27ae60"], [0.33, "#f1c40f"],
                  [0.66, "#e67e22"], [1.0, "#e74c3c"]]

    fig = go.Figure()
    fig.add_trace(
        go.Heatmap(
            z=grid,
            x=impact_labels,
            y=prob_labels,
            colorscale=colorscale,
            showscale=False,
            hovertemplate="Impact: %{x}<br>Probability: %{y}<br>Exposure: %{z}<extra></extra>",
        ))

    # Overlay risk dots
    for idx, r in enumerate(risks, 1):
        imp = getattr(r, "impact_score", 3)
        prob = getattr(r, "prob_score", 3)
        # Clamp to 1-5 range, convert to 0-4 index
        xi = max(0, min(4, int(imp) - 1))
        yi = max(0, min(4, int(prob) - 1))
        name = getattr(r, "name", f"R{idx}")
        cat = getattr(r, "category", "")
        exposure = getattr(r, "risk_score", imp * prob)
        hover = f"<b>R{idx}: {name}</b><br>Category: {cat}<br>Impact: {imp}<br>Probability: {prob}<br>Exposure: {exposure}"
        fig.add_trace(go.Scatter(
            x=[impact_labels[xi]], y=[prob_labels[yi]],
            mode="markers+text", text=[str(idx)],
            textposition="middle center",
            textfont=dict(size=9, color="black"),
            marker=dict(size=24, color="white", line=dict(width=1.5, color="black")),
            hovertext=hover, hoverinfo="text",
            showlegend=False,
        ))

    fig.update_layout(
        title="Risk Matrix (5×5)",
        xaxis=dict(title="Impact", side="bottom"),
        yaxis=dict(title="Probability"),
        plot_bgcolor="white",
        margin=dict(l=80, r=20, t=50, b=60), height=450,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 7a. Probability — PERT Distribution (PDF)
# ────────────────────────────────────────────────────────────────────

def plotly_pert_distribution(
        exp: float,
        std: float,
        target: float | None = None,
        probability: float | None = None) -> "go.Figure | None":
    """Normal distribution PDF with optional shaded P(T≤target) region."""
    if not PLOTLY_AVAILABLE or not SCIPY_AVAILABLE or std <= 0:
        return None

    x = np.linspace(exp - 4 * std, exp + 4 * std, 300)
    y = norm.pdf(x, exp, std)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name="PDF",
            line=dict(
                color="#2c3e50",
                width=2),
            fill="tozeroy",
            fillcolor="rgba(52,152,219,0.15)"))

    if target is not None:
        # Shaded region
        mask = x <= target
        fig.add_trace(go.Scatter(
            x=x[mask], y=y[mask], mode="lines", fill="tozeroy",
            fillcolor="rgba(39,174,96,0.35)", line=dict(width=0),
            name=f"P(T≤{target:.1f})" + (f"={probability:.1%}" if probability is not None else ""),
        ))
        fig.add_vline(
            x=target,
            line_dash="dash",
            line_color="#e74c3c",
            line_width=1.5,
            annotation_text=f"T={
                target:.1f}")

    fig.add_vline(
        x=exp,
        line_dash="dash",
        line_color="#e74c3c",
        line_width=1.5,
        annotation_text=f"μ={
            exp:.1f}")

    fig.update_layout(
        title="PERT Distribution (Normal Approximation)",
        xaxis=dict(
            title="Duration",
            showgrid=True,
            gridcolor="#eee"),
        yaxis=dict(
            title="Probability Density",
            showgrid=True,
            gridcolor="#eee"),
        plot_bgcolor="white",
        hovermode="x unified",
        margin=dict(
            l=60,
            r=20,
            t=50,
            b=40),
        height=380,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 7b. Probability — Cumulative (CDF)
# ────────────────────────────────────────────────────────────────────

def plotly_pert_cumulative(
        exp: float,
        std: float,
        target: float | None = None,
        probability: float | None = None) -> "go.Figure | None":
    """Cumulative distribution function (S-curve) with percentile markers."""
    if not PLOTLY_AVAILABLE or not SCIPY_AVAILABLE or std <= 0:
        return None

    x = np.linspace(exp - 4 * std, exp + 4 * std, 300)
    y = norm.cdf(x, exp, std)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="CDF",
                             line=dict(color="#2980b9", width=2)))

    # Percentile markers
    for p, color, label in [(0.5, "#27ae60", "P50"), (0.8, "#f39c12", "P80"),
                            (0.9, "#e74c3c", "P90"), (0.95, "#8e44ad", "P95")]:
        d = norm.ppf(p, exp, std)
        fig.add_trace(go.Scatter(
            x=[d], y=[p], mode="markers+text",
            text=[f"{label}={d:.1f}"], textposition="top right",
            textfont=dict(size=9, color=color),
            marker=dict(size=8, color=color), showlegend=False,
        ))

    if target is not None:
        p_target = norm.cdf(target, exp, std)
        fig.add_trace(
            go.Scatter(
                x=[target],
                y=[p_target],
                mode="markers+text",
                text=[
                    f"T={
                        target:.1f}\nP={
                        p_target:.1%}"],
                textposition="top left",
                marker=dict(
                    size=8,
                    color="#e74c3c",
                    symbol="square"),
                showlegend=False,
            ))
        fig.add_vline(
            x=target,
            line_dash="dash",
            line_color="#e74c3c",
            line_width=1.5)

    fig.update_layout(
        title="Cumulative Distribution (CDF)",
        xaxis=dict(
            title="Duration",
            showgrid=True,
            gridcolor="#eee"),
        yaxis=dict(
            title="Cumulative Probability",
            showgrid=True,
            gridcolor="#eee",
            tickformat=".0%"),
        plot_bgcolor="white",
        hovermode="x unified",
        margin=dict(
            l=60,
            r=20,
            t=50,
            b=40),
        height=380,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 7c. Probability — Sensitivity (horizontal bar)
# ────────────────────────────────────────────────────────────────────

def plotly_sensitivity(activities: list) -> "go.Figure | None":
    """Horizontal bar chart of variance contribution percentages."""
    if not PLOTLY_AVAILABLE:
        return None
    if not activities:
        return None

    # Collect non-zero variance activities
    items = []
    for a in activities:
        var = a.get("variance", 0)
        if isinstance(var, str):
            try:
                var = float(var)
            except ValueError:
                var = 0
        if var > 0:
            items.append((a.get("id", ""), a.get("name", ""), var))
    if not items:
        return None

    total_var = sum(v for _, _, v in items)
    items.sort(key=lambda t: t[2])
    ids = [f"{t[0]}" for t in items]
    pcts = [t[2] / total_var * 100 for t in items]
    hover = [f"{t[0]} — {t[1]}<br>{t[2] / total_var * 100:.1f}%" for t in items]

    fig = go.Figure(go.Bar(
        y=ids, x=pcts, orientation="h",
        marker_color="#e67e22",
        hovertext=hover, hoverinfo="text",
    ))
    fig.update_layout(
        title="Sensitivity Analysis — Variance Contribution",
        xaxis=dict(title="Contribution (%)", showgrid=True, gridcolor="#eee"),
        yaxis=dict(title=""),
        plot_bgcolor="white",
        margin=dict(l=70, r=20, t=50, b=40),
        height=max(300, len(items) * 22 + 100),
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 7d. Probability — Monte Carlo Histograms
# ────────────────────────────────────────────────────────────────────

def plotly_mc_results(results: Any) -> "go.Figure | None":
    """Duration + Cost histograms from Monte Carlo simulation."""
    if not PLOTLY_AVAILABLE:
        return None

    durations = getattr(results, "durations", None)
    costs = getattr(results, "costs", None)
    has_dur = durations is not None and len(durations) > 0
    has_cost = costs is not None and len(costs) > 0

    if not has_dur and not has_cost:
        return None

    rows = (1 if has_dur else 0) + (1 if has_cost else 0)
    titles = []
    if has_dur:
        titles.append("Duration Distribution")
    if has_cost:
        titles.append("Cost Distribution")

    fig = make_subplots(
        rows=rows,
        cols=1,
        subplot_titles=titles,
        vertical_spacing=0.15)
    row = 1

    if has_dur:
        fig.add_trace(go.Histogram(
            x=durations, nbinsx=40, marker_color="#3498db",
            opacity=0.8, name="Duration",
            histnorm="probability density",
        ), row=row, col=1)
        # Percentile lines
        for attr, color, label in [("p50_duration", "#27ae60", "P50"),
                                   ("p80_duration", "#f39c12", "P80"),
                                   ("p90_duration", "#e74c3c", "P90")]:
            val = getattr(results, attr, None)
            if val is not None:
                fig.add_vline(
                    x=val,
                    line_dash="dash",
                    line_color=color,
                    line_width=2,
                    annotation_text=f"{label}={
                        val:.1f}",
                    row=row,
                    col=1)
        row += 1

    if has_cost:
        fig.add_trace(go.Histogram(
            x=costs, nbinsx=40, marker_color="#e67e22",
            opacity=0.8, name="Cost",
            histnorm="probability density",
        ), row=row, col=1)
        bac = getattr(
            results,
            "bac",
            None) or getattr(
            results,
            "budget_at_completion",
            None)
        if bac is not None:
            fig.add_vline(
                x=bac,
                line_dash="solid",
                line_color="#e74c3c",
                line_width=2,
                annotation_text=f"BAC=${
                    bac:,.0f}",
                row=row,
                col=1)
        p_within = getattr(results, "p_cost_within_bac", None)
        if p_within is not None:
            fig.add_annotation(
                text=f"P(cost ≤ BAC) = {
                    p_within:.1%}",
                xref="paper",
                yref="paper",
                x=0.95,
                y=0.05 if rows == 1 else 0.48,
                showarrow=False,
                font=dict(
                    size=11,
                    color="#e74c3c"),
            )

    fig.update_layout(
        plot_bgcolor="white", hovermode="x unified",
        showlegend=False,
        margin=dict(l=60, r=20, t=50, b=40),
        height=350 * rows,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 8. RCPS — Comparison Gantt
# ────────────────────────────────────────────────────────────────────

def plotly_rcps_gantt(cpm_table, rcps_table) -> "go.Figure | None":
    """Side-by-side CPM vs RCPS horizontal bar Gantt."""
    if not PLOTLY_AVAILABLE:
        return None
    if cpm_table is None or rcps_table is None:
        return None

    try:
        import pandas as pd
        if not isinstance(cpm_table, pd.DataFrame):
            return None
    except ImportError:
        return None

    ids = list(
        cpm_table["id"]) if "id" in cpm_table.columns else list(
        range(
            len(cpm_table)))
    fig = go.Figure()

    for _, row in cpm_table.iterrows():
        aid = row.get("id", "")
        es = float(row.get("early_start", row.get("ES", 0)))
        dur = float(row.get("duration", 0))
        fig.add_trace(
            go.Bar(
                y=[aid],
                x=[dur],
                base=[es],
                orientation="h",
                marker=dict(
                    color="#3498db",
                    opacity=0.7),
                name="CPM",
                showlegend=False,
                hovertemplate=f"CPM: {aid}<br>ES={
                    es:.0f} Dur={
                    dur:.0f}<extra></extra>",
            ))

    for _, row in rcps_table.iterrows():
        aid = row.get("id", "")
        es = float(
            row.get(
                "actual_start",
                row.get(
                    "early_start",
                    row.get(
                        "ES",
                        0))))
        dur = float(row.get("duration", 0))
        fig.add_trace(
            go.Bar(
                y=[aid],
                x=[dur],
                base=[es],
                orientation="h",
                marker=dict(
                    color="#e67e22",
                    opacity=0.7),
                name="RCPS",
                showlegend=False,
                hovertemplate=f"RCPS: {aid}<br>Start={
                    es:.0f} Dur={
                    dur:.0f}<extra></extra>",
            ))

    fig.update_layout(
        title="CPM vs RCPS Schedule",
        barmode="overlay",
        xaxis=dict(
            title="Time",
            showgrid=True,
            gridcolor="#eee"),
        yaxis=dict(
            title="",
            autorange="reversed",
            categoryorder="array",
            categoryarray=ids),
        plot_bgcolor="white",
        hovermode="closest",
        margin=dict(
            l=80,
            r=20,
            t=50,
            b=40),
        height=max(
            400,
            len(ids) *
            22 +
            100),
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 9. RCPS — Resource Histogram + Cost
# ────────────────────────────────────────────────────────────────────

def plotly_rcps_histograms(
        periods: list | None = None,
        resource_profile: dict | None = None,
        resource_limit: float | None = None) -> "go.Figure | None":
    """Cost-per-period bars + resource usage bars (2-row subplot)."""
    if not PLOTLY_AVAILABLE:
        return None

    has_cost = periods is not None and len(periods) > 0
    has_res = resource_profile is not None and len(resource_profile) > 0
    if not has_cost and not has_res:
        return None

    rows = (1 if has_cost else 0) + (1 if has_res else 0)
    titles = []
    if has_cost:
        titles.append("Cost per Period")
    if has_res:
        titles.append("Resource Usage")
    fig = make_subplots(
        rows=rows,
        cols=1,
        subplot_titles=titles,
        vertical_spacing=0.15)
    row = 1

    if has_cost:
        x = list(range(len(periods)))
        pv_deltas = []
        ac_deltas = []
        prev_pv = prev_ac = 0
        for p in periods:
            pvc = getattr(p, "pv_cumulative", 0)
            acc = getattr(p, "ac_cumulative", 0)
            pv_deltas.append(pvc - prev_pv)
            ac_deltas.append(acc - prev_ac)
            prev_pv, prev_ac = pvc, acc
        fig.add_trace(
            go.Bar(
                x=x,
                y=pv_deltas,
                name="PV per period",
                marker_color="#2ecc71",
                opacity=0.8),
            row=row,
            col=1)
        fig.add_trace(
            go.Bar(
                x=x,
                y=ac_deltas,
                name="AC per period",
                marker_color="#e74c3c",
                opacity=0.8),
            row=row,
            col=1)
        fig.update_xaxes(title_text="Period", row=row, col=1)
        row += 1

    if has_res:
        rp = sorted(resource_profile.items(), key=lambda t: t[0])
        rx = [t[0] for t in rp]
        ry = [t[1] for t in rp]
        fig.add_trace(
            go.Bar(
                x=rx,
                y=ry,
                name="Resource Usage",
                marker_color="#3498db",
                opacity=0.8),
            row=row,
            col=1)
        if resource_limit is not None:
            fig.add_hline(
                y=resource_limit,
                line_dash="dash",
                line_color="#e74c3c",
                line_width=1.5,
                annotation_text=f"Limit = {resource_limit}",
                row=row,
                col=1)
        fig.update_xaxes(title_text="Time Period", row=row, col=1)

    fig.update_layout(
        barmode="group",
        plot_bgcolor="white", hovermode="x unified",
        margin=dict(l=60, r=20, t=50, b=40),
        height=300 * rows,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 10. Cost Estimation — Learning Curve
# ────────────────────────────────────────────────────────────────────

def plotly_learning_curve(curve: list, t1: float) -> "go.Figure | None":
    """Unit Cost + Cumulative Average vs unit number."""
    if not PLOTLY_AVAILABLE or not curve:
        return None

    ns = [c["n"] for c in curve]
    uts = [c["unit_time"] for c in curve]
    avgs = [c["cum_avg"] for c in curve]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ns,
            y=uts,
            mode="lines+markers",
            name="Unit Cost",
            line=dict(
                color="blue"),
            marker=dict(
                size=3)))
    fig.add_trace(
        go.Scatter(
            x=ns,
            y=avgs,
            mode="lines+markers",
            name="Cumul. Avg",
            line=dict(
                color="red",
                dash="dash"),
            marker=dict(
                size=3,
                symbol="square")))
    fig.add_hline(y=t1, line_dash="dot", line_color="grey",
                  annotation_text=f"T₁={t1}")

    fig.update_layout(
        title="Learning Curve",
        xaxis=dict(
            title="Unit Number",
            showgrid=True,
            gridcolor="#eee"),
        yaxis=dict(
            title="Cost / Time",
            showgrid=True,
            gridcolor="#eee"),
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0.5,
            xanchor="center"),
        margin=dict(
            l=60,
            r=20,
            t=50,
            b=40),
        height=350,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 11. Optimization — Time-Cost Trade-off
# ────────────────────────────────────────────────────────────────────

def plotly_time_cost_curve(
        curve_data: dict,
        result: dict) -> "go.Figure | None":
    """3-line time-cost trade-off with optimal point star marker."""
    if not PLOTLY_AVAILABLE or not curve_data:
        return None

    dur = curve_data.get("duration", [])
    dc = curve_data.get("direct_cost", [])
    ic = curve_data.get("indirect_cost", [])
    tc = curve_data.get("total_cost", [])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=dur,
            y=dc,
            mode="lines+markers",
            name="Direct Cost",
            line=dict(
                color="blue"),
            marker=dict(
                size=6)))
    fig.add_trace(
        go.Scatter(
            x=dur,
            y=ic,
            mode="lines+markers",
            name="Indirect Cost",
            line=dict(
                color="green"),
            marker=dict(
                size=6,
                symbol="square")))
    fig.add_trace(
        go.Scatter(
            x=dur,
            y=tc,
            mode="lines+markers",
            name="Total Cost",
            line=dict(
                color="red",
                width=3),
            marker=dict(
                size=6,
                symbol="triangle-up")))

    opt_dur = result.get("optimal_duration")
    opt_cost = result.get("optimal_total_cost")
    if opt_dur is not None and opt_cost is not None:
        fig.add_trace(go.Scatter(
            x=[opt_dur], y=[opt_cost], mode="markers+text",
            text=["Optimal"], textposition="top center",
            marker=dict(size=18, color="gold", symbol="star",
                        line=dict(width=2, color="black")),
            name="Optimal Point",
        ))

    fig.update_layout(
        title="Time-Cost Trade-off Curve",
        xaxis=dict(
            title="Duration",
            showgrid=True,
            gridcolor="#eee"),
        yaxis=dict(
            title="Cost",
            showgrid=True,
            gridcolor="#eee"),
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0.5,
            xanchor="center"),
        margin=dict(
            l=70,
            r=20,
            t=50,
            b=40),
        height=450,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 12. Optimization — Resource Leveling Profiles
# ────────────────────────────────────────────────────────────────────

def plotly_resource_profiles(result: dict) -> "go.Figure | None":
    """Before/after resource bar charts (2-row subplot)."""
    if not PLOTLY_AVAILABLE or not result:
        return None

    orig = result.get("original_profile")
    lev = result.get("leveled_profile")
    if orig is None and lev is None:
        return None

    def _extract(profile):
        if hasattr(profile, "to_dataframe"):
            df = profile.to_dataframe()
            return list(df["time"]), list(df["resource_usage"])
        if hasattr(profile, "profile"):
            p = profile.profile
            keys = sorted(p.keys())
            return keys, [p[k] for k in keys]
        return [], []

    ox, oy = _extract(orig) if orig else ([], [])
    lx, ly = _extract(lev) if lev else ([], [])
    rlimit = result.get("resource_limit")

    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=[
            "Original Schedule",
            "Leveled Schedule"],
        vertical_spacing=0.12)

    if ox:
        fig.add_trace(
            go.Bar(
                x=ox,
                y=oy,
                marker_color="lightcoral",
                opacity=0.7,
                name="Original"),
            row=1,
            col=1)
    if lx:
        fig.add_trace(
            go.Bar(
                x=lx,
                y=ly,
                marker_color="lightgreen",
                opacity=0.7,
                name="Leveled"),
            row=2,
            col=1)
    if rlimit is not None:
        fig.add_hline(
            y=rlimit,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"Limit: {rlimit}",
            row=1,
            col=1)
        fig.add_hline(
            y=rlimit,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"Limit: {rlimit}",
            row=2,
            col=1)

    fig.update_layout(
        plot_bgcolor="white", hovermode="x unified",
        margin=dict(l=60, r=20, t=50, b=40), height=550,
    )
    return fig


# ────────────────────────────────────────────────────────────────────
# 13. Crashing — Network per step
# ────────────────────────────────────────────────────────────────────

def plotly_crashing_network(
        G,
        step_label: str = "Network",
        critical_activities: set | None = None) -> "go.Figure | None":
    """Simple network diagram for a crash step graph."""
    if not PLOTLY_AVAILABLE:
        return None
    from pmhelper.utils.network_layout import sugiyama_layout, cleanup_virtual_nodes

    if G is None or len(G.nodes()) == 0:
        return None

    critical_activities = critical_activities or set()
    G_copy = G.copy()
    result = sugiyama_layout(G_copy)
    pos = result["pos"]
    all_pos = result["all_pos"]
    virtual_nodes = result["virtual_nodes"]
    edge_paths = result["edge_paths"]

    ex, ey = [], []
    for (u, v), path in edge_paths.items():
        wps = [all_pos[n] for n in path if n in all_pos]
        for wx, wy in wps:
            ex.append(wx)
            ey.append(wy)
        ex.append(None)
        ey.append(None)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines",
                             line=dict(color="#999", width=1),
                             hoverinfo="skip", showlegend=False))

    # Nodes
    nx_list, ny_list, nc, nt, nh = [], [], [], [], []
    for node in G_copy.nodes():
        if node in virtual_nodes or node not in pos:
            continue
        x, y = pos[node]
        nx_list.append(x)
        ny_list.append(y)
        is_crit = node in critical_activities
        nc.append("#E74C3C" if is_crit else "#3498DB")
        dur = G_copy.nodes[node].get("duration", "")
        nt.append(str(node))
        nh.append(f"<b>{node}</b><br>Dur: {dur}")

    fig.add_trace(go.Scatter(
        x=nx_list, y=ny_list, mode="markers+text",
        marker=dict(color=nc, size=16, line=dict(width=1, color="#333")),
        text=nt, textposition="middle center",
        textfont=dict(size=8, color="white"),
        hovertext=nh, hoverinfo="text", showlegend=False,
    ))

    cleanup_virtual_nodes(G_copy, virtual_nodes)

    fig.update_layout(
        title=step_label,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="white", hovermode="closest",
        margin=dict(l=10, r=10, t=40, b=10), height=400,
    )
    return fig


def plotly_pareto_frontier(solutions_df, obj1: str = "duration",
                           obj2: str = "cost") -> "go.Figure | None":
    """2-D Pareto frontier scatter (dominated + Pareto front)."""
    if not PLOTLY_AVAILABLE or solutions_df is None or solutions_df.empty:
        return None

    fig = go.Figure()

    pareto = solutions_df[solutions_df["is_pareto"]]
    dominated = solutions_df[~solutions_df["is_pareto"]]

    if not dominated.empty:
        fig.add_trace(go.Scatter(
            x=dominated[obj1], y=dominated[obj2], mode="markers",
            marker=dict(color="lightgray", size=6, opacity=0.5),
            name="Dominated",
        ))

    if not pareto.empty:
        ps = pareto.sort_values(obj1)
        fig.add_trace(go.Scatter(
            x=ps[obj1], y=ps[obj2], mode="markers+lines",
            marker=dict(color="red", size=12, symbol="star",
                        line=dict(width=1.5, color="darkred")),
            line=dict(dash="dash", width=2, color="red"),
            name="Pareto Frontier",
        ))

    fig.update_layout(
        title=dict(text=f"Pareto Frontier: {obj1.title()} vs {obj2.title()}",
                   font=dict(size=14)),
        xaxis_title=obj1.replace("_", " ").title(),
        yaxis_title=obj2.replace("_", " ").title(),
        template="plotly_white", hovermode="closest",
        margin=dict(l=60, r=20, t=50, b=50),
    )
    return fig


# ── SWOT Bubble Chart ───────────────────────────────────────────────────

def plotly_swot_bubble(analysis) -> "go.Figure | None":
    """Plotly 2×2 SWOT bubble chart.

    Parameters
    ----------
    analysis : SWOTAnalysis
        SWOT analysis object with ``.factors`` list. Each factor has
        ``category`` (STRENGTH/WEAKNESS/OPPORTUNITY/THREAT),
        ``impact`` (1-5), ``likelihood`` (1-5), ``description``.

    Returns
    -------
    go.Figure or None
    """
    if not PLOTLY_AVAILABLE or analysis is None:
        return None
    factors = getattr(analysis, "factors", [])
    if not factors:
        return None

    # Quadrant positions: category → (x_base, y_base)
    _QUAD = {
        "STRENGTH": (0.25, 0.75),
        "WEAKNESS": (0.75, 0.75),
        "OPPORTUNITY": (0.25, 0.25),
        "THREAT": (0.75, 0.25),
    }
    _COLORS = {
        "STRENGTH": "#2ecc71",
        "WEAKNESS": "#e74c3c",
        "OPPORTUNITY": "#3498db",
        "THREAT": "#f39c12",
    }

    fig = go.Figure()
    import random
    random.seed(42)

    for cat_name, (bx, by) in _QUAD.items():
        cat_factors = [
            f for f in factors if getattr(
                f.category, "name", str(
                    f.category)).upper() == cat_name]
        if not cat_factors:
            continue
        xs, ys, sizes, texts = [], [], [], []
        for f in cat_factors:
            impact = getattr(f, "impact", 3)
            likelihood = getattr(f, "likelihood", 3)
            xs.append(bx + (random.random() - 0.5) * 0.3)
            ys.append(by + (random.random() - 0.5) * 0.3)
            score = impact * likelihood
            sizes.append(max(15, score * 4))
            desc = getattr(f, "description", str(f))
            texts.append(
                f"{desc}<br>Impact: {impact}  Likelihood: {likelihood}")

        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers+text",
            marker=dict(size=sizes, color=_COLORS[cat_name], opacity=0.7,
                        line=dict(width=1, color="#2c3e50")),
            text=[getattr(f, "description", "")[:20] for f in cat_factors],
            textposition="top center", textfont=dict(size=8),
            hovertext=texts, hoverinfo="text",
            name=cat_name.title(),
        ))

    for label, (x, y) in [("Strengths", (0.25, 0.95)),
                          ("Weaknesses", (0.75, 0.95)),
                          ("Opportunities", (0.25, 0.45)),
                          ("Threats", (0.75, 0.45))]:
        fig.add_annotation(x=x, y=y, text=f"<b>{label}</b>",
                           showarrow=False, font=dict(size=13))

    fig.add_hline(y=0.5, line_dash="dash", line_color="#bdc3c7", opacity=0.6)
    fig.add_vline(x=0.5, line_dash="dash", line_color="#bdc3c7", opacity=0.6)

    fig.update_layout(
        title="SWOT Analysis — Bubble Chart",
        xaxis=dict(range=[0, 1], showticklabels=False, showgrid=False,
                   zeroline=False),
        yaxis=dict(range=[0, 1], showticklabels=False, showgrid=False,
                   zeroline=False),
        template="plotly_white", showlegend=True,
        margin=dict(l=20, r=20, t=50, b=20),
        height=550,
    )
    return fig
