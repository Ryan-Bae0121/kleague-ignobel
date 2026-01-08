"""
Aggregation logic for player and team statistics
"""
import pandas as pd
import numpy as np
from .config import DEF_ACTIONS, FOUL_TYPES, CARD_SET


def aggregate_player_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate season-level statistics per player
    
    Returns DataFrame with columns:
    - player_id, player_name_ko, team_name_ko
    - tackle_attempt, tackle_fail
    - duel_attempt, duel_fail
    - foul_count, danger_foul_count
    - clearance_attempt
    - block_attempt, block_fail
    - interception_attempt, interception_fail
    - card_count
    - def_actions (total)
    """
    results = []
    
    # Tackle stats
    tackle = df[df["type_name"] == "Tackle"].copy()
    if len(tackle) > 0:
        tackle_stats = tackle.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            tackle_attempt=("action_id", "count"),
            tackle_fail=("is_fail", "sum"),
        ).reset_index()
        results.append(tackle_stats)
    
    # Duel stats
    duel = df[df["type_name"] == "Duel"].copy()
    if len(duel) > 0:
        duel_stats = duel.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            duel_attempt=("action_id", "count"),
            duel_fail=("is_fail", "sum"),
        ).reset_index()
        results.append(duel_stats)
    
    # Foul stats
    foul = df[df["type_name"].isin(FOUL_TYPES)].copy()
    if len(foul) > 0:
        foul_stats = foul.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            foul_count=("action_id", "count"),
            danger_foul_count=("in_def_third", "sum"),
        ).reset_index()
        results.append(foul_stats)
    
    # Clearance stats
    clearance = df[df["type_name"].isin(["Clearance", "Aerial Clearance"])].copy()
    if len(clearance) > 0:
        clearance_stats = clearance.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            clearance_attempt=("action_id", "count"),
        ).reset_index()
        results.append(clearance_stats)
    
    # Block stats
    block = df[df["type_name"] == "Block"].copy()
    if len(block) > 0:
        block_stats = block.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            block_attempt=("action_id", "count"),
            block_fail=("is_fail", "sum"),
        ).reset_index()
        results.append(block_stats)
    
    # Interception stats
    interception = df[df["type_name"] == "Interception"].copy()
    if len(interception) > 0:
        interception_stats = interception.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            interception_attempt=("action_id", "count"),
            interception_fail=("is_fail", "sum"),
        ).reset_index()
        results.append(interception_stats)
    
    # Card count
    cards = df[df["is_card"]].copy()
    if len(cards) > 0:
        card_stats = cards.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            card_count=("action_id", "count"),
        ).reset_index()
        results.append(card_stats)
    
    # Total defensive actions
    def_actions = df[df["type_name"].isin(DEF_ACTIONS)].copy()
    if len(def_actions) > 0:
        def_stats = def_actions.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            def_actions=("action_id", "count"),
        ).reset_index()
        results.append(def_stats)
    
    # Merge all stats
    if not results:
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=[
            "player_id", "player_name_ko", "team_name_ko",
            "tackle_attempt", "tackle_fail",
            "duel_attempt", "duel_fail",
            "foul_count", "danger_foul_count",
            "clearance_attempt",
            "block_attempt", "block_fail",
            "interception_attempt", "interception_fail",
            "card_count", "def_actions"
        ])
    
    # Merge all dataframes
    agg_df = results[0]
    for r in results[1:]:
        agg_df = agg_df.merge(r, on=["player_id", "player_name_ko", "team_name_ko"], how="outer")
    
    # Fill NaN with 0
    numeric_cols = agg_df.select_dtypes(include=['number']).columns
    agg_df[numeric_cols] = agg_df[numeric_cols].fillna(0)
    
    # Fill text columns
    text_cols = ["player_name_ko", "team_name_ko"]
    for col in text_cols:
        if col in agg_df.columns:
            agg_df[col] = agg_df.groupby("player_id")[col].ffill().bfill()
    
    return agg_df


def calculate_clearance_panic(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate clearance panic rate (clearance followed by opponent shot within 10s)
    """
    clr = df[df["type_name"].isin(["Clearance", "Aerial Clearance"])].copy()
    shots = df[df["type_name"] == "Shot"].copy()
    
    if len(clr) == 0 or len(shots) == 0:
        return pd.DataFrame(columns=["player_id", "player_name_ko", "team_name_ko", "clearance", "concede_shot10"])
    
    results = []
    
    for (game_id, period_id), clr_group in clr.groupby(["game_id", "period_id"]):
        shots_group = shots[(shots["game_id"] == game_id) & (shots["period_id"] == period_id)].copy()
        
        if len(shots_group) == 0:
            continue
        
        clr_group = clr_group.sort_values("time_seconds").reset_index(drop=True)
        shots_group = shots_group.sort_values("time_seconds").reset_index(drop=True)
        
        try:
            m = pd.merge_asof(
                clr_group, shots_group,
                on="time_seconds",
                direction="forward",
                suffixes=("_clr", "_shot"),
                allow_exact_matches=True
            )
            
            # Check for team_id_shot column (may have suffix)
            team_col = "team_id_shot" if "team_id_shot" in m.columns else "team_id"
            time_col_shot = "time_seconds_shot" if "time_seconds_shot" in m.columns else "time_seconds"
            time_col_clr = "time_seconds_clr" if "time_seconds_clr" in m.columns else "time_seconds"
            
            m = m.dropna(subset=[time_col_shot, team_col])
            
            if len(m) == 0:
                continue
            
            # Fix time difference calculation
            if time_col_clr in m.columns and time_col_shot in m.columns:
                m["time_diff"] = m[time_col_shot] - m[time_col_clr]
            elif "time_seconds" in m.columns:
                # If no suffix, use same column (shouldn't happen but handle it)
                m["time_diff"] = 0
                continue
            else:
                continue
            
            # Get team columns
            team_id_clr_col = "team_id_clr" if "team_id_clr" in m.columns else "team_id"
            team_id_shot_col = team_col
            
            m["shot_within_10s"] = (
                (m["time_diff"] <= 10) & 
                (m["time_diff"] >= 0) & 
                (m[team_id_shot_col] != m[team_id_clr_col])
            )
            
            results.append(m)
        except (ValueError, KeyError):
            continue
    
    if len(results) == 0:
        return pd.DataFrame(columns=["player_id", "player_name_ko", "team_name_ko", "clearance", "concede_shot10"])
    
    m = pd.concat(results, ignore_index=True)
    
    if "player_id_clr" not in m.columns:
        return pd.DataFrame(columns=["player_id", "player_name_ko", "team_name_ko", "clearance", "concede_shot10"])
    
    score = m.groupby(["player_id_clr", "player_name_ko_clr", "team_name_ko_clr"]).agg(
        clearance=("action_id_clr", "count"),
        concede_shot10=("shot_within_10s", "sum"),
    ).reset_index()
    
    score.columns = ["player_id", "player_name_ko", "team_name_ko", "clearance", "concede_shot10"]
    return score


def calculate_second_half_drop(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate second half defensive drop rate
    """
    def_actions = df[df["type_name"].isin(DEF_ACTIONS)].copy()
    
    if len(def_actions) == 0:
        return pd.DataFrame()
    
    def_actions["is_def_fail"] = (
        def_actions["result_name"] == "Unsuccessful"
    ) | (def_actions["type_name"] == "Error")
    
    g = def_actions.groupby(["player_id", "player_name_ko", "team_name_ko", "period_id"]).agg(
        def_actions=("action_id", "count"),
        def_fails=("is_def_fail", "sum"),
    ).reset_index()
    
    g["fail_rate"] = g["def_fails"] / g["def_actions"]
    
    p = g.pivot_table(
        index=["player_id", "player_name_ko", "team_name_ko"],
        columns="period_id",
        values="fail_rate",
        fill_value=0
    ).reset_index()
    
    period_cols = [col for col in p.columns if col in [1, 2]]
    if len(period_cols) == 2:
        p["first_half_rate"] = p[1]
        p["second_half_rate"] = p[2]
        p["second_half_drop"] = p["second_half_rate"] - p["first_half_rate"]
        
        total_actions = def_actions.groupby(["player_id", "player_name_ko", "team_name_ko"]).size().reset_index(name="total_actions")
        p = p.merge(total_actions, on=["player_id", "player_name_ko", "team_name_ko"])
        
        return p
    
    return pd.DataFrame()


def calculate_def_third_turnover(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate defensive third turnover rate
    """
    turnover = df[
        df["type_name"].isin(["Pass", "Carry"]) & 
        df["in_def_third"]
    ].copy()
    
    if len(turnover) == 0:
        return pd.DataFrame()
    
    g = turnover.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
        def_third_attempts=("action_id", "count"),
        def_third_fails=("is_fail", "sum"),
    ).reset_index()
    
    g["def_third_turnover_rate"] = g["def_third_fails"] / g["def_third_attempts"]
    
    return g


def aggregate_attack_stats(df: pd.DataFrame, match_info_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Aggregate attack-related statistics for Ignobel Awards
    
    Returns DataFrame with:
    - shot_off_target_per_game
    - penalty_box_miss_per_game
    - offside_per_game
    - receive_to_give_ratio
    - cross_fail_per_game
    - duel_fail_per_game_attack
    - aerial_fail_per_game
    """
    results = []
    
    # Get player games count (for per-game calculations)
    player_games = df.groupby(["player_id", "player_name_ko", "team_name_ko"])["game_id"].nunique().reset_index()
    player_games.columns = ["player_id", "player_name_ko", "team_name_ko", "games"]
    
    # 1. 대포알 상: 슛은 많은데 Off Target이 많은 선수
    shots = df[df["type_name"].isin(["Shot", "Shot_Freekick"])].copy()
    if len(shots) > 0:
        shot_stats = shots.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            total_shots=("action_id", "count"),
            off_target_shots=("result_name", lambda x: (x == "Off Target").sum()),
        ).reset_index()
        results.append(shot_stats)
    
    # 2. 새가슴 상: 패널티 박스 안에서 슛 실패
    penalty_box_shots = shots[
        (shots["start_x"] >= 88.5) & 
        (shots["start_y"] >= 13.84) & 
        (shots["start_y"] <= 54.16)
    ].copy()
    if len(penalty_box_shots) > 0:
        pb_stats = penalty_box_shots.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            penalty_box_shots=("action_id", "count"),
            penalty_box_miss=("result_name", lambda x: (~x.isin(["Goal", "On Target"])).sum()),
        ).reset_index()
        results.append(pb_stats)
    
    # 3. 선넘네 상: 오프사이드
    offsides = df[df["type_name"] == "Offside"].copy()
    if len(offsides) > 0:
        offside_stats = offsides.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            offsides=("action_id", "count"),
        ).reset_index()
        results.append(offside_stats)
    
    # 4. 내로남불 상: Pass Received는 많은데 본인 Pass는 적음
    pass_received = df[df["type_name"] == "Pass Received"].copy()
    pass_given = df[df["type_name"] == "Pass"].copy()
    if len(pass_received) > 0:
        pass_recv_stats = pass_received.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            pass_received=("action_id", "count"),
        ).reset_index()
        results.append(pass_recv_stats)
    if len(pass_given) > 0:
        pass_give_stats = pass_given.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            pass_given=("action_id", "count"),
        ).reset_index()
        results.append(pass_give_stats)
    
    # 5. 어디에 줘 상: Cross는 많은데 성공률 낮음
    crosses = df[df["type_name"] == "Cross"].copy()
    if len(crosses) > 0:
        cross_stats = crosses.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            total_crosses=("action_id", "count"),
            cross_success=("result_name", lambda x: (x == "Successful").sum()),
        ).reset_index()
        cross_stats["cross_fail"] = cross_stats["total_crosses"] - cross_stats["cross_success"]
        cross_stats = cross_stats.drop(columns=["cross_success"])
        results.append(cross_stats)
    
    # 6. 지는 게 일상 상 (공격 버전): Duel 패배가 많은 선수
    # Note: This might overlap with defensive duel_fail, but we'll keep it for attack context
    attack_duels = df[df["type_name"] == "Duel"].copy()
    if len(attack_duels) > 0:
        duel_attack_stats = attack_duels.groupby(["player_id", "player_name_ko", "team_name_ko"]).agg(
            total_duels_attack=("action_id", "count"),
            duel_fail_attack=("is_fail", "sum"),
        ).reset_index()
        results.append(duel_attack_stats)
    
    # 7. 키 컸으면 상: 공중볼 경합 실패
    if len(attack_duels) > 0:
        aerial_stats = attack_duels[attack_duels["is_fail"]].groupby(
            ["player_id", "player_name_ko", "team_name_ko"]
        ).agg(
            aerial_fail=("action_id", "count"),
        ).reset_index()
        results.append(aerial_stats)
    
    # Merge all stats
    if not results:
        return pd.DataFrame()
    
    agg_df = results[0]
    for r in results[1:]:
        agg_df = agg_df.merge(r, on=["player_id", "player_name_ko", "team_name_ko"], how="outer")
    
    # Merge with player_games
    agg_df = agg_df.merge(player_games, on=["player_id", "player_name_ko", "team_name_ko"], how="left")
    agg_df["games"] = agg_df["games"].fillna(1)  # Default to 1 if no games found
    
    # Fill NaN with 0
    numeric_cols = agg_df.select_dtypes(include=['number']).columns
    agg_df[numeric_cols] = agg_df[numeric_cols].fillna(0)
    
    # Calculate per-game metrics
    if "off_target_shots" in agg_df.columns and "games" in agg_df.columns:
        agg_df["off_target_per_game"] = agg_df["off_target_shots"] / agg_df["games"]
    
    if "penalty_box_miss" in agg_df.columns and "games" in agg_df.columns:
        agg_df["penalty_box_miss_per_game"] = agg_df["penalty_box_miss"] / agg_df["games"]
    
    if "offsides" in agg_df.columns and "games" in agg_df.columns:
        agg_df["offside_per_game"] = agg_df["offsides"] / agg_df["games"]
    
    if "pass_received" in agg_df.columns and "pass_given" in agg_df.columns:
        agg_df["receive_to_give_ratio"] = np.where(
            agg_df["pass_given"] > 0,
            agg_df["pass_received"] / agg_df["pass_given"],
            0
        )
    
    if "cross_fail" in agg_df.columns and "games" in agg_df.columns:
        agg_df["cross_fail_per_game"] = agg_df["cross_fail"] / agg_df["games"]
    
    if "duel_fail_attack" in agg_df.columns and "games" in agg_df.columns:
        agg_df["duel_fail_per_game_attack"] = agg_df["duel_fail_attack"] / agg_df["games"]
    
    if "aerial_fail" in agg_df.columns and "games" in agg_df.columns:
        agg_df["aerial_fail_per_game"] = agg_df["aerial_fail"] / agg_df["games"]
    
    return agg_df


def aggregate_team_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate team-level statistics (similar to player but by team_id)
    """
    # For now, we'll use the same logic but group by team
    # In practice, you might want different aggregations for teams
    player_stats = aggregate_player_stats(df)
    
    if len(player_stats) == 0:
        return pd.DataFrame()
    
    # Group by team and sum (simple approach)
    team_cols = [c for c in player_stats.columns if c not in ["player_id", "player_name_ko"]]
    team_stats = player_stats.groupby("team_name_ko")[team_cols].sum().reset_index()
    team_stats["team_id"] = player_stats.groupby("team_name_ko")["player_id"].first().values  # Approximate
    
    return team_stats

