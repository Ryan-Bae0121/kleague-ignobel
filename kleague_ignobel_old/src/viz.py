"""
Visualization utilities
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_award_distribution(df: pd.DataFrame, award_id: str, award_title: str, metric_col: str = "score") -> go.Figure:
    """
    Create histogram/boxplot of award scores
    """
    award_data = df[df["award_id"] == award_id].copy()
    
    if len(award_data) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    fig = px.histogram(
        award_data,
        x=metric_col,
        nbins=30,
        title=f"{award_title} - Score Distribution",
        labels={metric_col: "Score", "count": "Number of Players"}
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        template="plotly_white"
    )
    
    return fig


def plot_award_ranking(df: pd.DataFrame, award_id: str, award_title: str, top_n: int = 20) -> go.Figure:
    """
    Create bar chart of top N players for an award
    """
    award_data = df[df["award_id"] == award_id].copy()
    top_data = award_data.nsmallest(top_n, "rank") if len(award_data) > 0 else pd.DataFrame()
    
    if len(top_data) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    # Sort by rank
    top_data = top_data.sort_values("rank")
    
    fig = go.Figure(data=[
        go.Bar(
            x=top_data["score"],
            y=top_data["player_name_ko"] + " (" + top_data["team_name_ko"] + ")",
            orientation="h",
            text=[f"#{int(r)}" for r in top_data["rank"]],
            textposition="outside"
        )
    ])
    
    fig.update_layout(
        title=f"{award_title} - Top {top_n}",
        xaxis_title="Score",
        yaxis_title="Player",
        height=max(400, len(top_data) * 30),
        template="plotly_white",
        yaxis={"categoryorder": "total ascending"}
    )
    
    return fig


