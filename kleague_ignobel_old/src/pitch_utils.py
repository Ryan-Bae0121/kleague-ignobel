"""
Pitch plotting utilities for Plotly
Lightweight version for Streamlit
"""
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


def draw_pitch_plotly(fig=None, pitch_color="#0a2e36", line_color="#ffffff", 
                     width=700, height=1000, show_zones=False):
    """
    Draw a soccer pitch on Plotly figure
    
    Pitch dimensions: 105m x 68m (x: 0-105, y: 0-68)
    """
    if fig is None:
        fig = go.Figure()
    
    # Pitch outline
    pitch_rect = dict(
        type="rect",
        x0=0, y0=0, x1=105, y1=68,
        line=dict(color=line_color, width=2),
        fillcolor=pitch_color,
        layer="below"
    )
    fig.add_shape(pitch_rect)
    
    # Center line
    fig.add_shape(
        type="line",
        x0=52.5, y0=0, x1=52.5, y1=68,
        line=dict(color=line_color, width=1.5),
        layer="below"
    )
    
    # Center circle
    theta = np.linspace(0, 2*np.pi, 100)
    circle_x = 52.5 + 9.15 * np.cos(theta)
    circle_y = 34 + 9.15 * np.sin(theta)
    fig.add_trace(go.Scatter(
        x=circle_x, y=circle_y,
        mode='lines',
        line=dict(color=line_color, width=1.5),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Penalty boxes
    # Left penalty box
    fig.add_shape(
        type="rect",
        x0=0, y0=13.84, x1=16.5, y1=54.16,
        line=dict(color=line_color, width=1.5),
        fillcolor="rgba(0,0,0,0)",
        layer="below"
    )
    
    # Right penalty box
    fig.add_shape(
        type="rect",
        x0=88.5, y0=13.84, x1=105, y1=54.16,
        line=dict(color=line_color, width=1.5),
        fillcolor="rgba(0,0,0,0)",
        layer="below"
    )
    
    # Goals
    fig.add_shape(
        type="rect",
        x0=-2, y0=30.34, x1=0, y1=37.66,
        line=dict(color=line_color, width=2),
        fillcolor="rgba(0,0,0,0)",
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=105, y0=30.34, x1=107, y1=37.66,
        line=dict(color=line_color, width=2),
        fillcolor="rgba(0,0,0,0)",
        layer="below"
    )
    
    # Zone boundaries (if requested)
    if show_zones:
        # X-axis zones: 0-26.25, 26.25-52.5, 52.5-78.75, 78.75-105
        for x in [26.25, 52.5, 78.75]:
            fig.add_shape(
                type="line",
                x0=x, y0=0, x1=x, y1=68,
                line=dict(color=line_color, width=0.5, dash="dash"),
                opacity=0.3,
                layer="below"
            )
        
        # Y-axis zones: 0-22.67, 22.67-45.33, 45.33-68
        for y in [22.67, 45.33]:
            fig.add_shape(
                type="line",
                x0=0, y0=y, x1=105, y1=y,
                line=dict(color=line_color, width=0.5, dash="dash"),
                opacity=0.3,
                layer="below"
            )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(
            range=[-5, 110],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            scaleanchor="y",
            scaleratio=1
        ),
        yaxis=dict(
            range=[-5, 73],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        width=width,
        height=height,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig


def plot_events_scatter(events_df: pd.DataFrame, event_type: str = None,
                       fig=None, color_col: str = None, size_col: str = None,
                       opacity: float = 0.6, show_zones: bool = False):
    """
    Plot events as scatter points on pitch
    """
    if fig is None:
        fig = draw_pitch_plotly(show_zones=show_zones)
    
    # Filter by event type if specified
    if event_type:
        plot_df = events_df[events_df["type_name"] == event_type].copy()
    else:
        plot_df = events_df.copy()
    
    if len(plot_df) == 0:
        return fig
    
    # Sample if too many points (for performance)
    if len(plot_df) > 5000:
        plot_df = plot_df.sample(n=5000, random_state=42)
    
    # Color mapping
    if color_col and color_col in plot_df.columns:
        colors = plot_df[color_col]
    else:
        colors = "red"
    
    # Size mapping
    if size_col and size_col in plot_df.columns:
        sizes = plot_df[size_col]
    else:
        sizes = 5
    
    # Add scatter
    fig.add_trace(go.Scatter(
        x=plot_df["start_x"],
        y=plot_df["start_y"],
        mode='markers',
        marker=dict(
            color=colors,
            size=sizes,
            opacity=opacity,
            line=dict(width=0.5, color="white")
        ),
        text=plot_df.get("player_name_ko", ""),
        hovertemplate="<b>%{text}</b><br>" +
                      "X: %{x:.1f}<br>" +
                      "Y: %{y:.1f}<extra></extra>",
        showlegend=False
    ))
    
    return fig


def plot_events_heatmap(events_df: pd.DataFrame, event_type: str = None,
                       fig=None, show_zones: bool = False, bins_x=21, bins_y=14):
    """
    Plot events as 2D histogram/heatmap on pitch
    """
    if fig is None:
        fig = draw_pitch_plotly(show_zones=show_zones)
    
    # Filter by event type if specified
    if event_type:
        plot_df = events_df[events_df["type_name"] == event_type].copy()
    else:
        plot_df = events_df.copy()
    
    if len(plot_df) == 0:
        return fig
    
    # Create 2D histogram
    hist, xedges, yedges = np.histogram2d(
        plot_df["start_x"],
        plot_df["start_y"],
        bins=[bins_x, bins_y],
        range=[[0, 105], [0, 68]]
    )
    
    # Create heatmap
    fig.add_trace(go.Heatmap(
        x=(xedges[:-1] + xedges[1:]) / 2,
        y=(yedges[:-1] + yedges[1:]) / 2,
        z=hist.T,
        colorscale="YlOrRd",
        showscale=True,
        opacity=0.6,
        hovertemplate="Count: %{z}<extra></extra>",
        zmin=0
    ))
    
    return fig


def plot_zone_activity(zone_activity_df: pd.DataFrame, fig=None, 
                      metric_col: str = "event_count", show_zones: bool = True):
    """
    Plot zone activity as heatmap
    zone_activity_df should have: zone_x, zone_y, and metric_col
    """
    if fig is None:
        fig = draw_pitch_plotly(show_zones=show_zones)
    
    # Zone centers (approximate)
    zone_centers = {
        "D": 13.125, "DM": 39.375, "AM": 65.625, "A": 91.875,  # x-axis
        "L": 11.335, "C": 34.0, "R": 56.665  # y-axis
    }
    
    # Create zone heatmap data
    zone_data = []
    for _, row in zone_activity_df.iterrows():
        zone = row.get("zone", "")
        if "-" in zone:
            zone_x, zone_y = zone.split("-")
            x_center = zone_centers.get(zone_x, 52.5)
            y_center = zone_centers.get(zone_y, 34)
            value = row.get(metric_col, 0)
            zone_data.append({
                "x": x_center,
                "y": y_center,
                "value": value,
                "zone": zone
            })
    
    if not zone_data:
        return fig
    
    zone_df = pd.DataFrame(zone_data)
    
    # Add zone activity as scatter with size
    max_value = zone_df["value"].max()
    if max_value > 0:
        sizes = (zone_df["value"] / max_value * 100).clip(10, 200)
    else:
        sizes = 50
    
    fig.add_trace(go.Scatter(
        x=zone_df["x"],
        y=zone_df["y"],
        mode='markers+text',
        marker=dict(
            size=sizes,
            color=zone_df["value"],
            colorscale="YlOrRd",
            showscale=True,
            colorbar=dict(title=metric_col),
            opacity=0.7,
            line=dict(width=2, color="white")
        ),
        text=zone_df["zone"],
        textfont=dict(size=10, color="white"),
        hovertemplate="<b>Zone: %{text}</b><br>" +
                      f"{metric_col}: %{{marker.color}}<extra></extra>",
        showlegend=False
    ))
    
    return fig

