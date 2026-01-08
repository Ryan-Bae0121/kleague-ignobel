"""
Analysis utilities for computing high-level metrics.

This module provides functions to compute success rates, zone profiles,
and other aggregated statistics for tactical analysis.
"""

from typing import Optional
import pandas as pd


def _is_success(outcome_value, event_type=None) -> bool:
    """
    Helper function to determine if an outcome represents success.

    Parameters
    ----------
    outcome_value
        Value from the outcome column (could be string, int, bool, etc.)
    event_type : optional str
        Type of event (e.g., "Shot", "Pass"). Used to determine success criteria.
        For shots, "Goal" is considered success.
        For passes, "Successful" is considered success.

    Returns
    -------
    bool
        True if the outcome represents success.
    """
    if pd.isna(outcome_value):
        return False

    if isinstance(outcome_value, str):
        outcome_lower = outcome_value.lower()
        
        # For shots, "Goal" is success
        if event_type and event_type.lower() == "shot":
            return outcome_lower in ["goal"]
        
        # For passes and other events, "Successful" is success
        return outcome_lower in ["successful", "success", "1", "true"]
    elif isinstance(outcome_value, (int, float)):
        return outcome_value == 1
    elif isinstance(outcome_value, bool):
        return outcome_value

    return False


def compute_zone_success_rate(
    events: pd.DataFrame,
    event_type_col: str = "type_name",
    outcome_col: str = "result_name",
    zone_col: str = "zone",
) -> pd.DataFrame:
    """
    Compute success rate by zone and event type.

    This function groups events by zone and event type, then computes:
    - Total attempts
    - Number of successful attempts
    - Success rate

    Parameters
    ----------
    events : pd.DataFrame
        Event DataFrame with zone, event_type, and outcome columns.
    event_type_col : str
        Column name for event type. Default: "type_name"
    outcome_col : str
        Column name for outcome/success flag. Default: "result_name"
    zone_col : str
        Column name for zone. Default: "zone"

    Returns
    -------
    pd.DataFrame
        Tidy DataFrame with columns:
        - zone, event_type, attempts, success, success_rate
    """
    if zone_col not in events.columns:
        raise ValueError(f"Zone column '{zone_col}' not found in events DataFrame")

    if event_type_col not in events.columns:
        raise ValueError(f"Event type column '{event_type_col}' not found in events DataFrame")

    if outcome_col not in events.columns:
        raise ValueError(f"Outcome column '{outcome_col}' not found in events DataFrame")

    # Compute success flag - pass event_type to _is_success for proper handling
    events = events.copy()
    events["_is_success"] = events.apply(
        lambda row: _is_success(row[outcome_col], event_type=row[event_type_col]),
        axis=1
    )

    # Group by zone and event type
    grouped = events.groupby([zone_col, event_type_col], observed=True).agg(
        attempts=("_is_success", "count"),
        success=("_is_success", "sum"),
    ).reset_index()

    # Compute success rate
    grouped["success_rate"] = grouped["success"] / grouped["attempts"]

    # Rename columns for clarity
    grouped = grouped.rename(columns={zone_col: "zone", event_type_col: "event_type"})

    return grouped


def compute_team_zone_profile(
    events: pd.DataFrame,
    team_col: str = "team_id",
    zone_col: str = "zone",
    event_type_filter: Optional[list[str]] = None,
    event_type_col: str = "type_name",
) -> pd.DataFrame:
    """
    Compute event distribution by team and zone.

    This creates a profile showing where each team tends to perform actions,
    which can be used for radar charts or heatmaps.

    Parameters
    ----------
    events : pd.DataFrame
        Event DataFrame with team and zone columns.
    team_col : str
        Column name for team ID. Default: "team_id"
        TODO: Adapt to actual dataset column names.
    zone_col : str
        Column name for zone. Default: "zone"
        TODO: Adapt if using a different zone column name.
    event_type_filter : optional list of str
        If provided, only count events of these types.
        Example: ["Pass", "Shot"] to focus on key actions.
        TODO: Adapt event type names to actual dataset values.
    event_type_col : str
        Column name for event type. Default: "type_name"
        TODO: Adapt to actual dataset column names.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - team (or team_col name), zone, event_count
        - Optionally: event_count_pct (percentage of team's total events)
    """
    df = events.copy()

    # Filter by event type if specified
    if event_type_filter is not None:
        if event_type_col not in df.columns:
            raise ValueError(f"Event type column '{event_type_col}' not found")
        df = df[df[event_type_col].isin(event_type_filter)]

    # Group by team and zone
    grouped = df.groupby([team_col, zone_col], observed=True).size().reset_index(name="event_count")

    # Add percentage of team's total events
    team_totals = grouped.groupby(team_col)["event_count"].transform("sum")
    grouped["event_count_pct"] = grouped["event_count"] / team_totals * 100

    return grouped


def compute_team_offense_metrics(
    events: pd.DataFrame,
    team_col: str = "team_id",
    zone_col: str = "zone",
    event_type_col: str = "type_name",
    outcome_col: str = "result_name",
) -> pd.DataFrame:
    """
    Compute offensive metrics by team and zone.

    This is a convenience function that combines zone success rate
    with team filtering for offense analysis.

    Parameters
    ----------
    events : pd.DataFrame
        Event DataFrame (should already be filtered to offense perspective).
    team_col : str
        Column name for team ID. Default: "team_id"
    zone_col : str
        Column name for zone. Default: "zone"
    event_type_col : str
        Column name for event type. Default: "type_name"
    outcome_col : str
        Column name for outcome. Default: "result_name"

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - team, zone, event_type, attempts, success, success_rate
    """
    success_df = compute_zone_success_rate(
        events, event_type_col=event_type_col, outcome_col=outcome_col, zone_col=zone_col
    )

    # Merge with team information
    # Note: This assumes events still has team_col
    if team_col in events.columns:
        # Get team for each zone/event_type combination
        team_zone_type = events.groupby([zone_col, event_type_col])[team_col].first().reset_index()
        success_df = success_df.merge(
            team_zone_type,
            left_on=["zone", "event_type"],
            right_on=[zone_col, event_type_col],
            how="left",
        )
        success_df = success_df.rename(columns={team_col: "team"})

    return success_df


