"""
Pitch plotting utilities for soccer event visualization.

This module provides functions to:
- Draw a soccer pitch (0-105 x / 0-68 y coordinate system)
- Visualize event locations (shots, passes, etc.)
- Visualize passes as arrows
- Visualize density/heatmaps
- Overlay zone boundaries

Assumptions:
- x: 0 (own goal line) → 105 (opponent goal line) - actual pitch length
- y: 0 (left touchline) → 68 (right touchline) - actual pitch width
This matches the actual soccer field dimensions (105m × 68m).
"""

from __future__ import annotations

from typing import Iterable, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd


def draw_pitch(
    ax: Optional[plt.Axes] = None,
    pitch_color: str = "white",
    line_color: str = "black",
    figsize: Tuple[int, int] = (7, 10),
    show: bool = False,
) -> plt.Axes:
    """
    Draw a vertical soccer pitch (0-105 x / 0-68 y) on the given axes.

    The pitch is oriented so that:
        - x: 0 -> bottom (own goal), 105 -> top (opponent goal) - actual pitch length
        - y: 0 -> left touchline, 68 -> right touchline - actual pitch width

    Parameters
    ----------
    ax : optional matplotlib Axes
        Axes to draw on. If None, a new figure and axes are created.
    pitch_color : str
        Background color of the pitch.
    line_color : str
        Color of pitch markings.
    figsize : tuple of int
        Figure size if a new figure is created.
    show : bool
        Whether to call plt.show() at the end.

    Returns
    -------
    ax : matplotlib Axes
        Axes with the pitch drawn on it.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # Set axes limits - actual pitch dimensions (105m × 68m)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 68)
    ax.set_aspect("equal")

    # Fill pitch background (zorder=0 to keep it in the background)
    pitch_bg = mpatches.Rectangle((0, 0), 105, 68, facecolor=pitch_color, edgecolor=line_color, linewidth=2, zorder=0)
    ax.add_patch(pitch_bg)

    # Outer boundaries (zorder=1 for pitch markings)
    # Top and bottom lines (goal lines)
    ax.plot([0, 105], [0, 0], color=line_color, linewidth=2, zorder=1)
    ax.plot([0, 105], [68, 68], color=line_color, linewidth=2, zorder=1)
    # Left and right lines (touchlines)
    ax.plot([0, 0], [0, 68], color=line_color, linewidth=2, zorder=1)
    ax.plot([105, 105], [0, 68], color=line_color, linewidth=2, zorder=1)

    # Halfway line
    ax.plot([52.5, 52.5], [0, 68], color=line_color, linewidth=1.5, zorder=1)

    # Center circle (radius 9.15m)
    center_circle = plt.Circle((52.5, 34), 9.15, fill=False, color=line_color, linewidth=1.5, zorder=1)
    ax.add_patch(center_circle)
    # Center spot
    ax.plot(52.5, 34, "o", color=line_color, markersize=3, zorder=1)

    # Penalty areas (both sides) (zorder=1)
    # Bottom penalty area (x: 0-16.5, y: 13.84-54.16) - 40.32m wide, centered
    penalty_area_bottom = mpatches.Rectangle(
        (0, 13.84), 16.5, 40.32, fill=False, color=line_color, linewidth=1.5, zorder=1
    )
    ax.add_patch(penalty_area_bottom)
    # Bottom six-yard box (x: 0-5.5, y: 24.84-43.16) - 18.32m wide, centered
    six_yard_bottom = mpatches.Rectangle(
        (0, 24.84), 5.5, 18.32, fill=False, color=line_color, linewidth=1.5, zorder=1
    )
    ax.add_patch(six_yard_bottom)
    # Bottom penalty spot (x: 11, y: 34)
    ax.plot(11, 34, "o", color=line_color, markersize=4, zorder=1)

    # Top penalty area (x: 88.5-105, y: 13.84-54.16)
    penalty_area_top = mpatches.Rectangle(
        (88.5, 13.84), 16.5, 40.32, fill=False, color=line_color, linewidth=1.5, zorder=1
    )
    ax.add_patch(penalty_area_top)
    # Top six-yard box (x: 99.5-105, y: 24.84-43.16)
    six_yard_top = mpatches.Rectangle(
        (99.5, 24.84), 5.5, 18.32, fill=False, color=line_color, linewidth=1.5, zorder=1
    )
    ax.add_patch(six_yard_top)
    # Top penalty spot (x: 94, y: 34)
    ax.plot(94, 34, "o", color=line_color, markersize=4, zorder=1)

    # Goals (simple rectangles) (zorder=1)
    # Bottom goal (x: -1 to 0, y: 30.34-37.66) - 7.32m wide, centered
    goal_bottom = mpatches.Rectangle(
        (-1, 30.34), 1, 7.32, facecolor=line_color, edgecolor=line_color, linewidth=1.5, zorder=1
    )
    ax.add_patch(goal_bottom)
    # Top goal (x: 105-106, y: 30.34-37.66)
    goal_top = mpatches.Rectangle(
        (105, 30.34), 1, 7.32, facecolor=line_color, edgecolor=line_color, linewidth=1.5, zorder=1
    )
    ax.add_patch(goal_top)

    # Remove axis labels and ticks for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    
    # Ensure axes limits are set correctly at the end (in case they were changed)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 68)
    ax.set_aspect("equal")

    if show:
        plt.show()

    return ax


def add_zones_to_ax(
    ax: plt.Axes,
    x_bins: Iterable[float] = (0, 26.25, 52.5, 78.75, 105),
    y_bins: Iterable[float] = (0, 22.67, 45.33, 68),
    line_style: str = "--",
    line_width: float = 0.5,
    line_color: str = "gray",
) -> None:
    """
    Overlay zone grid lines on a pitch.

    Parameters
    ----------
    ax : matplotlib Axes
        Axes with a pitch already drawn.
    x_bins, y_bins : iterable of float
        Bin edges used for zoning along x and y. Must match the bins used in
        feature_engineering.add_zone_columns.
    line_style : str
        Matplotlib linestyle for zone boundaries.
    line_width : float
        Line width for zone boundaries.
    line_color : str
        Line color for zone boundaries.
    """
    x_bins = list(x_bins)
    y_bins = list(y_bins)

    # Draw vertical lines for internal x_bins (skip first and last) (zorder=1.5 for zone lines)
    for x in x_bins[1:-1]:
        ax.axvline(x, color=line_color, linestyle=line_style, linewidth=line_width, alpha=0.7, zorder=1.5)

    # Draw horizontal lines for internal y_bins (skip first and last)
    for y in y_bins[1:-1]:
        ax.axhline(y, color=line_color, linestyle=line_style, linewidth=line_width, alpha=0.7, zorder=1.5)


def plot_events_scatter(
    events: pd.DataFrame,
    ax: Optional[plt.Axes] = None,
    x_col: str = "x",
    y_col: str = "y",
    color_col: Optional[str] = None,
    color: Optional[str] = None,
    cmap: str = "viridis",
    alpha: float = 0.7,
    size: float = 20.0,
    draw_pitch_flag: bool = True,
    **scatter_kwargs,
) -> plt.Axes:
    """
    Plot event locations as scatter points on a soccer pitch.

    Parameters
    ----------
    events : pd.DataFrame
        DataFrame with at least `x_col` and `y_col` columns.
    ax : optional matplotlib Axes
        Axes to plot on. If None, a new pitch is created.
    x_col, y_col : str
        Column names for x/y coordinates.
        TODO: Adapt to actual dataset column names (e.g., "start_x", "start_y").
    color_col : optional str
        Column name to map to color. If None, a single color is used.
    color : optional str
        Single color for all points (e.g., "blue", "red"). 
        Cannot be used together with color_col.
    cmap : str
        Colormap name used when `color_col` is provided.
    alpha : float
        Point transparency.
    size : float
        Marker size.
    draw_pitch_flag : bool
        If True and `ax` is None, call `draw_pitch` first.
    **scatter_kwargs
        Additional keyword arguments passed to `ax.scatter`.

    Returns
    -------
    ax : matplotlib Axes
        Axes with the scatter plot drawn.
    """
    if ax is None:
        if draw_pitch_flag:
            ax = draw_pitch(show=False)
        else:
            fig, ax = plt.subplots(figsize=(7, 10))
            ax.set_xlim(0, 105)
            ax.set_ylim(0, 68)
            ax.set_aspect("equal")

    if x_col not in events.columns or y_col not in events.columns:
        raise ValueError(f"Columns '{x_col}' and/or '{y_col}' not found in events DataFrame")

    # Prepare scatter arguments
    x = events[x_col]
    y = events[y_col]

    scatter_args = {
        "x": x,
        "y": y,
        "alpha": alpha,
        "s": size,
        **scatter_kwargs,
    }

    # Handle color parameter (single color string)
    if color is not None:
        if "c" in scatter_kwargs:
            raise ValueError("Cannot specify both 'color' and 'c' in scatter_kwargs")
        scatter_args["c"] = color
    elif color_col is not None:
        if color_col not in events.columns:
            raise ValueError(f"Color column '{color_col}' not found in events DataFrame")
        
        color_values = events[color_col]
        
        # Check if color_col contains categorical/string data
        if color_values.dtype == 'object' or pd.api.types.is_categorical_dtype(color_values):
            # Convert categorical to numeric for colormap
            unique_values = color_values.dropna().unique()
            value_to_num = {val: i for i, val in enumerate(unique_values)}
            scatter_args["c"] = color_values.map(value_to_num)
            scatter_args["cmap"] = cmap
        else:
            # Numeric data - use directly
            scatter_args["c"] = color_values
            scatter_args["cmap"] = cmap
    else:
        # Default color if not specified
        if "c" not in scatter_kwargs and "color" not in scatter_kwargs:
            scatter_args["c"] = "blue"

    # Set zorder to ensure data appears above pitch (zorder=2 for data)
    if "zorder" not in scatter_args:
        scatter_args["zorder"] = 2
    
    ax.scatter(**scatter_args)

    return ax


def plot_pass_arrows(
    events: pd.DataFrame,
    ax: Optional[plt.Axes] = None,
    x_start_col: str = "x_start",
    y_start_col: str = "y_start",
    x_end_col: str = "x_end",
    y_end_col: str = "y_end",
    color: str = "blue",
    alpha: float = 0.6,
    arrow_width: float = 0.002,
    head_width: float = 2.0,
    head_length: float = 2.0,
    draw_pitch_flag: bool = True,
    max_arrows: Optional[int] = 1000,
) -> plt.Axes:
    """
    Plot passes as arrows on a soccer pitch.

    Parameters
    ----------
    events : pd.DataFrame
        DataFrame with start/end coordinate columns for passes.
    ax : optional matplotlib Axes
        Axes to plot on. If None, create a new pitch.
    x_start_col, y_start_col, x_end_col, y_end_col : str
        Column names for pass start and end locations.
        TODO: Adapt to actual dataset column names (e.g., "start_x", "start_y", "end_x", "end_y").
    color : str
        Arrow color.
    alpha : float
        Arrow transparency.
    arrow_width : float
        Width of the arrow shaft (in data coordinates).
    head_width : float
        Width of the arrow head (in data coordinates).
    head_length : float
        Length of the arrow head (in data coordinates).
    draw_pitch_flag : bool
        If True and `ax` is None, draw a pitch first.
    max_arrows : optional int
        Maximum number of arrows to draw. If None, draw all.
        If events has more rows, sample randomly.
        This helps with performance for large datasets.

    Returns
    -------
    ax : matplotlib Axes
        Axes with arrows drawn.
    """
    if ax is None:
        if draw_pitch_flag:
            ax = draw_pitch(show=False)
        else:
            fig, ax = plt.subplots(figsize=(7, 10))
            ax.set_xlim(0, 105)
            ax.set_ylim(0, 68)
            ax.set_aspect("equal")

    # Check required columns
    required_cols = [x_start_col, y_start_col, x_end_col, y_end_col]
    missing_cols = [col for col in required_cols if col not in events.columns]
    if missing_cols:
        raise ValueError(f"Required columns not found: {missing_cols}")

    # Sample if too many events
    df_to_plot = events.copy()
    if max_arrows is not None and len(df_to_plot) > max_arrows:
        df_to_plot = df_to_plot.sample(n=max_arrows, random_state=42)

    # Draw arrows
    for _, row in df_to_plot.iterrows():
        x_start = row[x_start_col]
        y_start = row[y_start_col]
        x_end = row[x_end_col]
        y_end = row[y_end_col]

        # Skip if any coordinate is NaN
        if pd.isna(x_start) or pd.isna(y_start) or pd.isna(x_end) or pd.isna(y_end):
            continue

        dx = x_end - x_start
        dy = y_end - y_start

        # Only draw if there's actual movement
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            continue

        ax.arrow(
            x_start,
            y_start,
            dx,
            dy,
            head_width=head_width,
            head_length=head_length,
            fc=color,
            ec=color,
            alpha=alpha,
            width=arrow_width,
            length_includes_head=True,
            zorder=2,  # Ensure arrows appear above pitch
        )

    return ax


def simple_kde_heatmap(
    events: pd.DataFrame,
    ax: Optional[plt.Axes] = None,
    x_col: str = "x",
    y_col: str = "y",
    bins: int = 30,
    cmap: str = "Reds",
    draw_pitch_flag: bool = True,
    show_colorbar: bool = True,
) -> plt.Axes:
    """
    Plot a simple 2D histogram-based heatmap of event density on the pitch.

    This is not a full KDE; it's a 2D histogram for simplicity.

    Parameters
    ----------
    events : pd.DataFrame
        DataFrame with x,y columns.
    ax : optional matplotlib Axes
        Axes to plot on. If None, create a new pitch.
    x_col, y_col : str
        Column names for x/y coordinates.
        TODO: Adapt to actual dataset column names.
    bins : int
        Number of bins for both x and y (square grid).
    cmap : str
        Matplotlib colormap name.
    draw_pitch_flag : bool
        If True and `ax` is None, draw a pitch first.
    show_colorbar : bool
        Whether to add a colorbar to the figure.

    Returns
    -------
    ax : matplotlib Axes
        Axes with the heatmap drawn.
    """
    if ax is None:
        if draw_pitch_flag:
            ax = draw_pitch(show=False)
        else:
            fig, ax = plt.subplots(figsize=(7, 10))
            ax.set_xlim(0, 105)
            ax.set_ylim(0, 68)
            ax.set_aspect("equal")

    if x_col not in events.columns or y_col not in events.columns:
        raise ValueError(f"Columns '{x_col}' and/or '{y_col}' not found in events DataFrame")

    # Remove NaN values
    df_clean = events[[x_col, y_col]].dropna()

    if len(df_clean) == 0:
        return ax

    # Compute 2D histogram
    hist, x_edges, y_edges = np.histogram2d(
        df_clean[x_col],
        df_clean[y_col],
        bins=bins,
        range=[[0, 105], [0, 68]],
    )

    # Transpose and flip for correct orientation (imshow expects different orientation)
    hist = hist.T

    # Display as image (zorder=1.5 to appear above pitch but below other data)
    extent = [0, 105, 0, 68]
    im = ax.imshow(
        hist,
        extent=extent,
        origin="lower",
        cmap=cmap,
        alpha=0.6,
        interpolation="bilinear",
        zorder=1.5,
    )

    if show_colorbar:
        plt.colorbar(im, ax=ax, label="Event Density")
    
    # Ensure axes limits are maintained (don't let imshow change them)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 68)

    return ax


# Public API
__all__ = [
    "draw_pitch",
    "add_zones_to_ax",
    "plot_events_scatter",
    "plot_pass_arrows",
    "simple_kde_heatmap",
]


if __name__ == "__main__":
    # Quick smoke test / demo
    print("Running pitch_plot.py smoke test...")

    # Create fake data
    np.random.seed(42)
    n_points = 50
    fake_events = pd.DataFrame({
        "x": np.random.uniform(0, 100, n_points),
        "y": np.random.uniform(0, 100, n_points),
        "zone": np.random.choice(["D-L", "DM-C", "AM-R", "A-C"], n_points),
    })

    # Draw pitch with scatter
    fig, ax = plt.subplots(figsize=(7, 10))
    ax = draw_pitch(ax=ax, show=False)
    ax = add_zones_to_ax(ax)
    ax = plot_events_scatter(
        fake_events,
        ax=ax,
        x_col="x",
        y_col="y",
        color_col="zone",
        draw_pitch_flag=False,
    )
    ax.set_title("Pitch Plot Demo (Smoke Test)")
    plt.tight_layout()
    plt.savefig("pitch_demo.png", dpi=100, bbox_inches="tight")
    print("Demo plot saved as 'pitch_demo.png'")
    print("Smoke test completed successfully!")


