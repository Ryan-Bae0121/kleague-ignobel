"""
Batch script to build artifacts from raw data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.io import load_raw_data, load_match_info, save_artifact
from src.preprocess import preprocess_events
from src.aggregate import (
    aggregate_player_stats, calculate_clearance_panic,
    calculate_second_half_drop, calculate_def_third_turnover,
    aggregate_attack_stats
)
from src.awards_engine import calculate_metrics, compute_award_scores

print("=" * 70)
print("Building K League Ignobel Awards Artifacts")
print("=" * 70)

# 1. Load data
print("\n[1/5] Loading raw data...")
raw = load_raw_data()
match_info = load_match_info()
print(f"  Loaded {len(raw):,} events from {len(match_info):,} matches")

# 2. Preprocess
print("\n[2/5] Preprocessing events...")
preprocessed = preprocess_events(raw)
print("  Preprocessing complete")

# 3. Aggregate player stats
print("\n[3/5] Aggregating player statistics...")
player_stats = aggregate_player_stats(preprocessed)
print(f"  Aggregated stats for {len(player_stats):,} players")

# 4. Calculate special metrics
print("\n[4/6] Calculating special metrics...")
clearance_panic = calculate_clearance_panic(preprocessed)
print(f"  Clearance panic: {len(clearance_panic):,} players")

second_half_drop = calculate_second_half_drop(preprocessed)
print(f"  Second half drop: {len(second_half_drop):,} players")

def_third_turnover = calculate_def_third_turnover(preprocessed)
print(f"  Defensive third turnover: {len(def_third_turnover):,} players")

# 5. Aggregate attack stats
print("\n[5/6] Aggregating attack statistics...")
attack_stats = aggregate_attack_stats(preprocessed, match_info)
print(f"  Attack stats: {len(attack_stats):,} players")

# 6. Calculate metrics and award scores
print("\n[6/6] Calculating award scores...")
player_stats_with_metrics = calculate_metrics(
    player_stats,
    clearance_panic=clearance_panic,
    second_half_drop=second_half_drop,
    def_third_turnover=def_third_turnover,
    attack_stats=attack_stats
)

award_scores = compute_award_scores(player_stats_with_metrics)
print(f"  Calculated scores for {len(award_scores):,} award-player combinations")

# 6. Create leaderboard
leaderboard = award_scores[award_scores["rank"] <= 10].sort_values(["award_id", "rank"])

# 7. Create profiles (player summary)
profiles = player_stats_with_metrics.copy()

# 8. Save artifacts
print("\n[7/7] Saving artifacts...")
save_artifact(player_stats_with_metrics, "awards_player.parquet")
print("  Saved: awards_player.parquet")

save_artifact(award_scores, "leaderboard.parquet")
print("  Saved: leaderboard.parquet")

save_artifact(profiles, "profiles.parquet")
print("  Saved: profiles.parquet")

# Team awards (placeholder - can be expanded)
team_stats = player_stats.groupby("team_name_ko").agg({
    col: "sum" for col in player_stats.select_dtypes(include=['number']).columns
}).reset_index()
save_artifact(team_stats, "awards_team.parquet")
print("  Saved: awards_team.parquet")

print("\n" + "=" * 70)
print("[SUCCESS] All artifacts built successfully!")
print("=" * 70)

