"""
Award scoring engine
"""
import pandas as pd
import numpy as np
from .config import AWARDS


def calculate_metrics(player_stats: pd.DataFrame, clearance_panic: pd.DataFrame = None,
                     second_half_drop: pd.DataFrame = None, def_third_turnover: pd.DataFrame = None,
                     attack_stats: pd.DataFrame = None) -> pd.DataFrame:
    """
    Calculate all award metrics from aggregated stats
    """
    stats = player_stats.copy()
    
    # Tackle fail rate
    if "tackle_attempt" in stats.columns and "tackle_fail" in stats.columns:
        stats["tackle_fail_rate"] = np.where(
            stats["tackle_attempt"] > 0,
            stats["tackle_fail"] / stats["tackle_attempt"],
            0
        )
    
    # Card per defensive action
    if "card_count" in stats.columns and "def_actions" in stats.columns:
        stats["card_per_def"] = np.where(
            stats["def_actions"] > 0,
            stats["card_count"] / stats["def_actions"],
            0
        )
    
    # Danger foul ratio
    if "foul_count" in stats.columns and "danger_foul_count" in stats.columns:
        stats["danger_foul_ratio"] = np.where(
            stats["foul_count"] > 0,
            stats["danger_foul_count"] / stats["foul_count"],
            0
        )
    
    # Block fail rate
    if "block_attempt" in stats.columns and "block_fail" in stats.columns:
        stats["block_fail_rate"] = np.where(
            stats["block_attempt"] > 0,
            stats["block_fail"] / stats["block_attempt"],
            0
        )
    
    # Interception fail rate
    if "interception_attempt" in stats.columns and "interception_fail" in stats.columns:
        stats["interception_fail_rate"] = np.where(
            stats["interception_attempt"] > 0,
            stats["interception_fail"] / stats["interception_attempt"],
            0
        )
    
    # Duel fail rate
    if "duel_attempt" in stats.columns and "duel_fail" in stats.columns:
        stats["duel_fail_rate"] = np.where(
            stats["duel_attempt"] > 0,
            stats["duel_fail"] / stats["duel_attempt"],
            0
        )
    
    # Merge clearance panic
    if clearance_panic is not None and len(clearance_panic) > 0:
        stats = stats.merge(
            clearance_panic[["player_id", "clearance", "concede_shot10"]],
            on="player_id",
            how="left"
        )
        stats["clearance_panic_rate"] = np.where(
            stats["clearance"] > 0,
            stats["concede_shot10"] / stats["clearance"],
            0
        )
        stats["clearance"] = stats["clearance"].fillna(0)
        stats["concede_shot10"] = stats["concede_shot10"].fillna(0)
    
    # Merge second half drop
    if second_half_drop is not None and len(second_half_drop) > 0:
        stats = stats.merge(
            second_half_drop[["player_id", "second_half_drop", "first_half_rate", "second_half_rate"]],
            on="player_id",
            how="left"
        )
        stats["second_half_drop"] = stats["second_half_drop"].fillna(0)
    
    # Merge def third turnover
    if def_third_turnover is not None and len(def_third_turnover) > 0:
        stats = stats.merge(
            def_third_turnover[["player_id", "def_third_turnover_rate", "def_third_attempts", "def_third_fails"]],
            on="player_id",
            how="left"
        )
        stats["def_third_turnover_rate"] = stats["def_third_turnover_rate"].fillna(0)
    
    # Merge attack stats
    if attack_stats is not None and len(attack_stats) > 0:
        attack_cols = [
            "player_id", "off_target_per_game", "penalty_box_miss_per_game",
            "offside_per_game", "receive_to_give_ratio", "cross_fail_per_game",
            "duel_fail_per_game_attack", "aerial_fail_per_game"
        ]
        available_attack_cols = [c for c in attack_cols if c in attack_stats.columns]
        if available_attack_cols:
            stats = stats.merge(
                attack_stats[available_attack_cols],
                on="player_id",
                how="left"
            )
            # Fill NaN with 0 for attack metrics
            for col in available_attack_cols:
                if col != "player_id":
                    stats[col] = stats[col].fillna(0)
    
    return stats


def compute_award_scores(stats: pd.DataFrame, award_configs: list = None) -> pd.DataFrame:
    """
    Compute award scores and rankings
    
    Returns long-format DataFrame:
    - award_id, player_id, player_name_ko, team_name_ko
    - score, rank, percentile
    """
    if award_configs is None:
        award_configs = AWARDS
    
    results = []
    
    for award in award_configs:
        award_id = award["id"]
        metric = award["metric"]
        min_attempts = award.get("min_attempts", 0)
        
        if metric not in stats.columns:
            continue
        
        # Filter by minimum attempts
        attempt_cols = {
            "tackle_fail_rate": "tackle_attempt",
            "block_fail_rate": "block_attempt",
            "interception_fail_rate": "interception_attempt",
            "duel_fail_rate": "duel_attempt",
            "clearance_panic_rate": "clearance",
            "card_per_def": "def_actions",
            "danger_foul_ratio": "foul_count",
            "def_third_turnover_rate": "def_third_attempts",
            "second_half_drop": "def_actions",
            # Attack awards
            "off_target_per_game": "total_shots",
            "penalty_box_miss_per_game": "penalty_box_shots",
            "offside_per_game": "offsides",
            "receive_to_give_ratio": "pass_received",
            "cross_fail_per_game": "total_crosses",
            "duel_fail_per_game_attack": "total_duels_attack",
            "aerial_fail_per_game": "aerial_fail"
        }
        
        attempt_col = attempt_cols.get(metric, None)
        if attempt_col and attempt_col in stats.columns:
            filtered = stats[stats[attempt_col] >= min_attempts].copy()
        else:
            filtered = stats.copy()
        
        if len(filtered) == 0:
            continue
        
        # Calculate percentile
        scores = filtered[metric].fillna(0)
        percentile_rank = scores.rank(pct=True) * 100
        
        award_scores = pd.DataFrame({
            "award_id": award_id,
            "player_id": filtered["player_id"],
            "player_name_ko": filtered["player_name_ko"],
            "team_name_ko": filtered["team_name_ko"],
            "score": scores.values,
            "rank": scores.rank(ascending=False, method="min").astype(int),
            "percentile": percentile_rank.values
        })
        
        results.append(award_scores)
    
    if not results:
        return pd.DataFrame(columns=["award_id", "player_id", "player_name_ko", "team_name_ko", "score", "rank", "percentile"])
    
    return pd.concat(results, ignore_index=True)


def get_top_awards(award_scores: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    """Get top N winners for each award"""
    return award_scores[award_scores["rank"] <= top_n].sort_values(["award_id", "rank"])


