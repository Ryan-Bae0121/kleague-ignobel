"""
Feature engineering utilities for soccer event data.

This module provides functions to add derived features like zones,
filter data by team perspective, and extract possession sequences.
"""

from typing import Optional
import pandas as pd
import numpy as np


def add_zone_columns(
    events: pd.DataFrame,
    x_bins: Optional[list[int]] = None,
    y_bins: Optional[list[int]] = None,
    x_col: str = "start_x",
    y_col: str = "start_y",
) -> pd.DataFrame:
    """
    Add zone columns to event data based on x,y coordinates.

    Creates categorical zone labels for both x and y dimensions,
    and a combined zone label.

    Parameters
    ----------
    events : pd.DataFrame
        DataFrame with coordinate columns.
    x_bins : optional list of int
        Bin edges for x-axis (pitch length).
        Default: [0, 25, 50, 75, 100] (Defense, Defensive Mid, Attacking Mid, Attack)
        TODO: Adjust if dataset uses different coordinate system.
    y_bins : optional list of int
        Bin edges for y-axis (pitch width).
        Default: [0, 33, 66, 100] (Left, Center, Right)
        TODO: Adjust if dataset uses different coordinate system.
    x_col : str
        Column name for x coordinates. Default: "start_x"
        TODO: Adapt to actual dataset column names.
    y_col : str
        Column name for y coordinates. Default: "start_y"
        TODO: Adapt to actual dataset column names.

    Returns
    -------
    pd.DataFrame
        DataFrame with added columns:
        - `zone_x`: categorical label (e.g., "D", "DM", "AM", "A")
        - `zone_y`: categorical label (e.g., "L", "C", "R")
        - `zone`: combined label (e.g., "AM-R")
    """
    df = events.copy()

    # Default bins - actual pitch dimensions (105m × 68m)
    # Divide into 4 zones along x-axis and 3 zones along y-axis
    if x_bins is None:
        x_bins = [0, 26.25, 52.5, 78.75, 105]  # D, DM, AM, A
    if y_bins is None:
        y_bins = [0, 22.67, 45.33, 68]  # L, C, R

    # X-axis labels (from own goal to opponent goal)
    x_labels = ["D", "DM", "AM", "A"]  # Defense, Defensive Mid, Attacking Mid, Attack
    if len(x_bins) - 1 != len(x_labels):
        # Adjust labels if bins don't match
        x_labels = [f"X{i}" for i in range(len(x_bins) - 1)]

    # Y-axis labels (left to right)
    y_labels = ["L", "C", "R"]  # Left, Center, Right
    if len(y_bins) - 1 != len(y_labels):
        y_labels = [f"Y{i}" for i in range(len(y_bins) - 1)]

    # Create zone_x
    df["zone_x"] = pd.cut(
        df[x_col],
        bins=x_bins,
        labels=x_labels,
        include_lowest=True,
        right=False,
    ).astype(str)

    # Create zone_y
    df["zone_y"] = pd.cut(
        df[y_col],
        bins=y_bins,
        labels=y_labels,
        include_lowest=True,
        right=False,
    ).astype(str)

    # Create combined zone
    df["zone"] = df["zone_x"] + "-" + df["zone_y"]

    return df


def filter_team_vs_opponent(
    events: pd.DataFrame,
    team_col: str = "team_id",
    team_name_col: str = "team_name_ko",
    opponent_col: Optional[str] = None,
    target_team: str | int = None,
    as_defender: bool = True,
    match_info: Optional[pd.DataFrame] = None,
    team_name_en_map: Optional[dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Filter events for offense/defense perspective analysis.

    This function helps analyze:
    - Offense: actions BY a specific team (as_defender=False)
    - Defense: actions AGAINST a specific team (as_defender=True)

    Parameters
    ----------
    events : pd.DataFrame
        Event DataFrame with team identifiers.
    team_col : str
        Column name for the team that performed the action.
        Default: "team_id"
    team_name_col : str
        Column name for the team name (Korean).
        Default: "team_name_ko"
    opponent_col : optional str
        Column name for the opponent team.
        If None, opponent is inferred from match_info.
    target_team : str or int
        The team ID or name to filter for.
        If string, will match against team_name_col.
        If int, will match against team_col.
    as_defender : bool
        If True: filter events where opponent == target_team (defense perspective).
        If False: filter events where team == target_team (offense perspective).
    match_info : optional pd.DataFrame
        Match info DataFrame with home_team_id, away_team_id columns.
        Used to infer opponent if opponent_col is None.

    Returns
    -------
    pd.DataFrame
        Filtered DataFrame.
    """
    if target_team is None:
        raise ValueError("target_team must be provided")

    df = events.copy()

    # Determine if target_team is ID or name, and get the actual team_id
    if isinstance(target_team, str):
        # If team_name_en_map is provided, try to convert English name to Korean
        if team_name_en_map is not None:
            # Create reverse mapping (English -> Korean)
            en_to_ko_map = {v: k for k, v in team_name_en_map.items()}
            if target_team in en_to_ko_map:
                target_team = en_to_ko_map[target_team]
        
        # Try to find team_id from team_name_ko
        if team_name_col in df.columns:
            matching_teams = df[df[team_name_col] == target_team][team_col].unique()
            if len(matching_teams) == 0:
                # Try to find from match_info if available
                if match_info is not None:
                    home_match = match_info[match_info["home_team_name_ko"] == target_team]["home_team_id"].unique()
                    away_match = match_info[match_info["away_team_name_ko"] == target_team]["away_team_id"].unique()
                    matching_teams = pd.concat([pd.Series(home_match), pd.Series(away_match)]).unique()
                
                if len(matching_teams) == 0:
                    raise ValueError(f"Team '{target_team}' not found in data. Available teams: {df[team_name_col].unique()[:10]}")
            
            target_team_id = matching_teams[0]
        else:
            raise ValueError(f"team_name_col '{team_name_col}' not found in events DataFrame")
    else:
        # target_team is already an ID
        target_team_id = target_team

    if as_defender:
        # Defense perspective: actions AGAINST target_team
        if opponent_col is not None:
            mask = df[opponent_col] == target_team_id
        elif match_info is not None:
            # Infer opponent from match_info
            merged = df.merge(
                match_info,
                on="game_id",
                how="left",
                suffixes=("", "_match"),
            )
            # If target_team is home, filter where team_id == away_team_id
            # If target_team is away, filter where team_id == home_team_id
            mask = (
                (merged["home_team_id"] == target_team_id) & (merged[team_col] == merged["away_team_id"])
            ) | (
                (merged["away_team_id"] == target_team_id) & (merged[team_col] == merged["home_team_id"])
            )
            result = merged[mask].copy()
            # Remove duplicate columns from merge
            cols_to_drop = [c for c in result.columns if c.endswith("_match") and c.replace("_match", "") in result.columns]
            if cols_to_drop:
                result = result.drop(columns=cols_to_drop)
            return result
        else:
            raise ValueError(
                "Either opponent_col or match_info must be provided for defense perspective"
            )
    else:
        # Offense perspective: actions BY target_team
        mask = df[team_col] == target_team_id

    return df[mask].copy()


def extract_possessions(
    events: pd.DataFrame,
    by: Optional[list[str]] = None,
    time_col: str = "time_seconds",
    team_col: str = "team_id",
    game_col: str = "game_id",
    max_gap_seconds: float = 5.0,
) -> pd.DataFrame:
    """
    Add a possession_id column to events using a simple heuristic.

    A possession is defined as a sequence of events by the same team
    with no gap longer than max_gap_seconds.

    Parameters
    ----------
    events : pd.DataFrame
        Event DataFrame.
    by : optional list of str
        Columns to group by before computing possessions.
        Default: [game_col, "period_id"] if "period_id" exists, else [game_col].
        TODO: Adapt to actual dataset columns.
    time_col : str
        Column name for event time. Default: "time_seconds"
        TODO: Adapt to actual dataset column names.
    team_col : str
        Column name for team ID. Default: "team_id"
        TODO: Adapt to actual dataset column names.
    game_col : str
        Column name for game ID. Default: "game_id"
        TODO: Adapt to actual dataset column names.
    max_gap_seconds : float
        Maximum time gap (seconds) between events to consider them
        part of the same possession.

    Returns
    -------
    pd.DataFrame
        DataFrame with added `possession_id` column.
        TODO: This heuristic should be refined if the dataset provides
        a better possession definition.
    """
    df = events.copy().sort_values(by=[game_col, time_col])

    if by is None:
        by = [game_col]
        if "period_id" in df.columns:
            by.append("period_id")

    df["possession_id"] = None

    for group_key, group in df.groupby(by):
        possession_id = 0
        prev_team = None
        prev_time = None

        for idx, row in group.iterrows():
            current_team = row[team_col]
            current_time = row[time_col]

            # Check if this starts a new possession
            if (
                prev_team is None
                or prev_team != current_team
                or (prev_time is not None and (current_time - prev_time) > max_gap_seconds)
            ):
                possession_id += 1

            df.at[idx, "possession_id"] = f"{group_key}_{possession_id}" if isinstance(group_key, tuple) else f"{group_key}_{possession_id}"

            prev_team = current_team
            prev_time = current_time

    return df


