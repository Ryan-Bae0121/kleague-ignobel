"""
Case study module for team offense/defense pattern analysis.

This module provides functions to summarize offensive and defensive patterns
for individual teams, to be used in case study notebooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from .feature_engineering import add_zone_columns
from .analysis_utils import compute_zone_success_rate


@dataclass
class OffenseSummary:
    """Summary of a team's offensive patterns."""
    team_name_ko: str
    n_actions: int
    n_passes: int
    n_shots: int
    n_goals: int
    shot_on_target: int
    main_attacking_zones: pd.DataFrame  # top zones by shot attempts or xG-like proxy
    pass_zone_success: pd.DataFrame     # zone-level pass success rates


@dataclass
class DefenseSummary:
    """Summary of a team's defensive patterns."""
    team_name_ko: str
    n_actions_faced: int
    n_opponent_shots: int
    n_goals_conceded: int
    dangerous_zones: pd.DataFrame       # zones where opponents are most dangerous
    opponent_pass_zone_success: pd.DataFrame


def add_opponent_columns(
    events: pd.DataFrame,
    match_info: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge match_info into events and add opponent team columns.

    Assumes match_info has at least:
        - 'game_id'
        - 'home_team_id', 'away_team_id'
        - 'home_team_name_ko', 'away_team_name_ko'

    Adds:
        - 'home_team_id', 'away_team_id'
        - 'home_team_name_ko', 'away_team_name_ko'
        - 'opponent_team_name_ko'

    Returns a new DataFrame (does not modify input in-place).
    """
    # Select relevant columns from match_info
    match_cols = [
        'game_id',
        'home_team_id', 'away_team_id',
        'home_team_name_ko', 'away_team_name_ko'
    ]
    
    # Check which columns exist
    available_cols = [col for col in match_cols if col in match_info.columns]
    if 'game_id' not in available_cols:
        raise ValueError("match_info must contain 'game_id' column")
    
    # Merge
    events_merged = events.merge(
        match_info[available_cols],
        on='game_id',
        how='left',
        suffixes=('', '_match')
    )
    
    # Compute opponent_team_name_ko
    if 'home_team_id' in available_cols and 'away_team_id' in available_cols:
        events_merged["opponent_team_name_ko"] = np.where(
            events_merged["team_id"] == events_merged["home_team_id"],
            events_merged["away_team_name_ko"],
            events_merged["home_team_name_ko"],
        )
    else:
        # If team_id columns are missing, we can't compute opponent
        # This is a fallback - ideally match_info should have these
        events_merged["opponent_team_name_ko"] = None
    
    return events_merged


def _is_shot(row: pd.Series) -> bool:
    """Helper to check if an event is a shot."""
    return row.get("type_name") == "Shot"


def _is_goal(row: pd.Series) -> bool:
    """Helper to check if an event is a goal."""
    return row.get("type_name") == "Shot" and row.get("result_name") == "Goal"


def compute_basic_offense_counts(events: pd.DataFrame) -> Tuple[int, int, int, int]:
    """
    Compute basic offensive counts from a view of events
    where 'team_name_ko' represents the attacking team.

    Returns
    -------
    n_actions : int
        Total number of events.
    n_passes : int
        Number of events with type_name == "Pass".
    n_shots : int
        Number of events with type_name == "Shot".
    n_goals : int
        Number of events where type_name == "Shot" and result_name == "Goal".
    """
    n_actions = len(events)
    
    if "type_name" not in events.columns:
        return n_actions, 0, 0, 0
    
    n_passes = (events["type_name"] == "Pass").sum()
    n_shots = (events["type_name"] == "Shot").sum()
    
    if "result_name" not in events.columns:
        n_goals = 0
    else:
        n_goals = ((events["type_name"] == "Shot") & (events["result_name"] == "Goal")).sum()
    
    return n_actions, n_passes, n_shots, n_goals


def compute_basic_defense_counts(events: pd.DataFrame) -> Tuple[int, int, int]:
    """
    Compute basic defensive counts from a view of events
    where each row represents an *opponent* action against the target team.

    Returns
    -------
    n_actions_faced : int
    n_opponent_shots : int
    n_goals_conceded : int
    """
    n_actions_faced = len(events)
    
    if "type_name" not in events.columns:
        return n_actions_faced, 0, 0
    
    n_opponent_shots = (events["type_name"] == "Shot").sum()
    
    if "result_name" not in events.columns:
        n_goals_conceded = 0
    else:
        n_goals_conceded = ((events["type_name"] == "Shot") & (events["result_name"] == "Goal")).sum()
    
    return n_actions_faced, n_opponent_shots, n_goals_conceded


def summarize_offense(
    events: pd.DataFrame,
    team_name_ko: str,
    zone_bins_x: Optional[List[float]] = None,
    zone_bins_y: Optional[List[float]] = None,
) -> OffenseSummary:
    """
    Build an offensive summary for a given team.

    Parameters
    ----------
    events : pd.DataFrame
        Full event DataFrame (with 'team_name_ko', 'type_name', 'result_name',
        'start_x', 'start_y', etc.).
    team_name_ko : str
        Korean team name to analyze.
    zone_bins_x, zone_bins_y : optional list of float
        Bin edges for zoning. If None, use sensible defaults (0-105, 0-68).

    Returns
    -------
    OffenseSummary
    """
    # Filter events for that team as attacker
    team_events = events[events["team_name_ko"] == team_name_ko].copy()
    
    if len(team_events) == 0:
        # Return empty summary if no events found
        return OffenseSummary(
            team_name_ko=team_name_ko,
            n_actions=0,
            n_passes=0,
            n_shots=0,
            n_goals=0,
            shot_on_target=0,
            main_attacking_zones=pd.DataFrame(columns=["zone", "shot_attempts", "goals"]),
            pass_zone_success=pd.DataFrame(columns=["zone", "event_type", "attempts", "success", "success_rate"]),
        )
    
    # Add zone columns if not already present
    if "zone" not in team_events.columns:
        # Convert zone_bins to int if needed (for compatibility with add_zone_columns)
        if zone_bins_x is not None:
            zone_bins_x = [int(x) for x in zone_bins_x]
        if zone_bins_y is not None:
            zone_bins_y = [int(y) for y in zone_bins_y]
        
        team_events = add_zone_columns(
            team_events,
            x_bins=zone_bins_x,
            y_bins=zone_bins_y,
            x_col="start_x",
            y_col="start_y",
        )
    
    # Compute basic counts
    n_actions, n_passes, n_shots, n_goals = compute_basic_offense_counts(team_events)
    
    # Shot on target count
    if "result_name" in team_events.columns:
        shots = team_events[team_events["type_name"] == "Shot"]
        shot_on_target = (
            (shots["result_name"] == "On Target") | 
            (shots["result_name"] == "Goal")
        ).sum()
    else:
        shot_on_target = 0
    
    # Pass zone success
    passes = team_events[team_events["type_name"] == "Pass"].copy()
    if len(passes) > 0 and "zone" in passes.columns:
        pass_zone_success = compute_zone_success_rate(
            passes,
            event_type_col="type_name",
            outcome_col="result_name",
            zone_col="zone",
        )
        # Filter to Pass events only (in case compute_zone_success_rate returns multiple types)
        pass_zone_success = pass_zone_success[pass_zone_success["event_type"] == "Pass"]
    else:
        pass_zone_success = pd.DataFrame(columns=["zone", "event_type", "attempts", "success", "success_rate"])
    
    # Main attacking zones (from shots)
    shots = team_events[team_events["type_name"] == "Shot"].copy()
    if len(shots) > 0 and "zone" in shots.columns:
        zone_shots = shots.groupby("zone", observed=True).agg(
            shot_attempts=("type_name", "count"),
            goals=("result_name", lambda x: (x == "Goal").sum() if "result_name" in shots.columns else 0),
        ).reset_index()
        zone_shots = zone_shots.sort_values("shot_attempts", ascending=False)
        # Take top 5
        main_attacking_zones = zone_shots.head(5)
    else:
        main_attacking_zones = pd.DataFrame(columns=["zone", "shot_attempts", "goals"])
    
    return OffenseSummary(
        team_name_ko=team_name_ko,
        n_actions=n_actions,
        n_passes=n_passes,
        n_shots=n_shots,
        n_goals=n_goals,
        shot_on_target=shot_on_target,
        main_attacking_zones=main_attacking_zones,
        pass_zone_success=pass_zone_success,
    )


def summarize_defense(
    events: pd.DataFrame,
    team_name_ko: str,
    zone_bins_x: Optional[List[float]] = None,
    zone_bins_y: Optional[List[float]] = None,
) -> DefenseSummary:
    """
    Build a defensive summary for a given team.

    Here, we interpret `events` such that:
    - 'team_name_ko' is the acting team in each row.
    - 'opponent_team_name_ko' is the defending team.

    We construct a view where opponents' actions *against* `team_name_ko`
    are analyzed.

    Parameters
    ----------
    events : pd.DataFrame
        Full event DataFrame with an 'opponent_team_name_ko' column added
        via `add_opponent_columns`.
    team_name_ko : str
        Korean team name (the defending team here).
    zone_bins_x, zone_bins_y : optional
        Bin edges for zoning.

    Returns
    -------
    DefenseSummary
    """
    # Filter events where the opponent is the target team
    opp_events = events[events["opponent_team_name_ko"] == team_name_ko].copy()
    
    if len(opp_events) == 0:
        # Return empty summary if no events found
        return DefenseSummary(
            team_name_ko=team_name_ko,
            n_actions_faced=0,
            n_opponent_shots=0,
            n_goals_conceded=0,
            dangerous_zones=pd.DataFrame(columns=["zone", "shot_attempts_against", "goals_conceded"]),
            opponent_pass_zone_success=pd.DataFrame(columns=["zone", "event_type", "attempts", "success", "success_rate"]),
        )
    
    # Add zone columns if not already present
    if "zone" not in opp_events.columns:
        # Convert zone_bins to int if needed
        if zone_bins_x is not None:
            zone_bins_x = [int(x) for x in zone_bins_x]
        if zone_bins_y is not None:
            zone_bins_y = [int(y) for y in zone_bins_y]
        
        opp_events = add_zone_columns(
            opp_events,
            x_bins=zone_bins_x,
            y_bins=zone_bins_y,
            x_col="start_x",
            y_col="start_y",
        )
    
    # Compute basic defensive counts
    n_actions_faced, n_opponent_shots, n_goals_conceded = compute_basic_defense_counts(opp_events)
    
    # Opponent pass zone success
    opp_passes = opp_events[opp_events["type_name"] == "Pass"].copy()
    if len(opp_passes) > 0 and "zone" in opp_passes.columns:
        opponent_pass_zone_success = compute_zone_success_rate(
            opp_passes,
            event_type_col="type_name",
            outcome_col="result_name",
            zone_col="zone",
        )
        # Filter to Pass events only
        opponent_pass_zone_success = opponent_pass_zone_success[
            opponent_pass_zone_success["event_type"] == "Pass"
        ]
    else:
        opponent_pass_zone_success = pd.DataFrame(columns=["zone", "event_type", "attempts", "success", "success_rate"])
    
    # Dangerous zones (from opponent shots)
    opp_shots = opp_events[opp_events["type_name"] == "Shot"].copy()
    if len(opp_shots) > 0 and "zone" in opp_shots.columns:
        zone_shots_against = opp_shots.groupby("zone", observed=True).agg(
            shot_attempts_against=("type_name", "count"),
            goals_conceded=("result_name", lambda x: (x == "Goal").sum() if "result_name" in opp_shots.columns else 0),
        ).reset_index()
        zone_shots_against = zone_shots_against.sort_values(
            ["shot_attempts_against", "goals_conceded"],
            ascending=[False, False]
        )
        # Take top 5
        dangerous_zones = zone_shots_against.head(5)
    else:
        dangerous_zones = pd.DataFrame(columns=["zone", "shot_attempts_against", "goals_conceded"])
    
    return DefenseSummary(
        team_name_ko=team_name_ko,
        n_actions_faced=n_actions_faced,
        n_opponent_shots=n_opponent_shots,
        n_goals_conceded=n_goals_conceded,
        dangerous_zones=dangerous_zones,
        opponent_pass_zone_success=opponent_pass_zone_success,
    )


def summarize_team_case_study(
    events_with_opponent: pd.DataFrame,
    team_name_ko: str,
    zone_bins_x: Optional[List[float]] = None,
    zone_bins_y: Optional[List[float]] = None,
) -> Dict[str, object]:
    """
    Compute both offense and defense summaries for a single team.

    Parameters
    ----------
    events_with_opponent : pd.DataFrame
        Events with 'opponent_team_name_ko' and zone columns available
        (or those will be added inside).
    team_name_ko : str
        Korean name of the team.
    zone_bins_x, zone_bins_y : optional
        Zone bin edges.

    Returns
    -------
    dict
        {
            "team_name_ko": ...,
            "offense": OffenseSummary,
            "defense": DefenseSummary,
        }
    """
    offense = summarize_offense(
        events_with_opponent,
        team_name_ko,
        zone_bins_x=zone_bins_x,
        zone_bins_y=zone_bins_y,
    )
    
    defense = summarize_defense(
        events_with_opponent,
        team_name_ko,
        zone_bins_x=zone_bins_x,
        zone_bins_y=zone_bins_y,
    )
    
    return {
        "team_name_ko": team_name_ko,
        "offense": offense,
        "defense": defense,
    }


def generate_text_insights(
    offense: OffenseSummary,
    defense: DefenseSummary,
    top_k_zones: int = 3,
) -> Dict[str, List[str]]:
    """
    Generate simple human-readable bullet-point insights for offense and defense.
    The goal is not perfect language, but structured text we can print in notebooks.

    Returns a dict:
    {
        "offense": [...],
        "defense": [...],
    }
    """
    offense_insights = []
    defense_insights = []
    
    # Offense insights
    offense_insights.append(
        f"공격 이벤트 총 {offense.n_actions:,}회, 그 중 패스 {offense.n_passes:,}회, "
        f"슛 {offense.n_shots:,}회, 득점 {offense.n_goals:,}골"
    )
    
    if offense.shot_on_target > 0:
        offense_insights.append(
            f"유효슈팅 {offense.shot_on_target:,}회"
        )
    
    # Main attacking zones
    if len(offense.main_attacking_zones) > 0:
        top_zones = offense.main_attacking_zones.head(top_k_zones)
        zone_texts = []
        for _, row in top_zones.iterrows():
            zone = row["zone"]
            shot_attempts = int(row["shot_attempts"])
            goals = int(row["goals"])
            zone_texts.append(f"{zone} (슈팅 {shot_attempts}회, 골 {goals}골)")
        offense_insights.append(
            f"주요 공격 지역: {', '.join(zone_texts)}"
        )
    
    # Pass zone success
    if len(offense.pass_zone_success) > 0:
        top_pass_zones = offense.pass_zone_success.nlargest(top_k_zones, "success_rate")
        pass_texts = []
        for _, row in top_pass_zones.iterrows():
            zone = row["zone"]
            success_rate = row["success_rate"]
            attempts = int(row["attempts"])
            pass_texts.append(f"{zone} (성공률 {success_rate:.1%}, 시도 {attempts}회)")
        offense_insights.append(
            f"패스 성공률이 높은 존: {', '.join(pass_texts)}"
        )
    
    # Defense insights
    defense_insights.append(
        f"상대 공격 이벤트를 총 {defense.n_actions_faced:,}회 허용, "
        f"그 중 슛 {defense.n_opponent_shots:,}회, 실점 {defense.n_goals_conceded:,}골"
    )
    
    # Dangerous zones
    if len(defense.dangerous_zones) > 0:
        top_dangerous = defense.dangerous_zones.head(top_k_zones)
        dangerous_texts = []
        for _, row in top_dangerous.iterrows():
            zone = row["zone"]
            shot_attempts_against = int(row["shot_attempts_against"])
            goals_conceded = int(row["goals_conceded"])
            dangerous_texts.append(f"{zone} (슈팅 {shot_attempts_against}회, 실점 {goals_conceded}골)")
        defense_insights.append(
            f"상대에게 자주 슛을 허용하는 지역: {', '.join(dangerous_texts)}"
        )
    
    return {
        "offense": offense_insights,
        "defense": defense_insights,
    }


__all__ = [
    "OffenseSummary",
    "DefenseSummary",
    "add_opponent_columns",
    "summarize_offense",
    "summarize_defense",
    "summarize_team_case_study",
    "generate_text_insights",
]


if __name__ == "__main__":
    # Placeholder for manual testing
    # This module is designed to be used in notebooks with actual data loading
    print("case_study.py module loaded successfully.")
    print("Use this module in a Jupyter notebook with actual event data.")

