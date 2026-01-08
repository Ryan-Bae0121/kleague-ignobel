"""
Build pattern analysis artifacts for pitch/zone visualization
Day 1: Lightweight artifacts for fast loading (FAST VERSION)

Key optimizations:
- Remove per-team loops (single groupby with team dimension)
- Reduce copies and columns early
- Convert groupby keys to category
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import importlib.util

# -----------------------------------------------------------------------------
# Path setup (해결 2: 파일 경로 직접 import로 충돌 방지)
# -----------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()
OPEN_TRACK2_ROOT = (PROJECT_ROOT.parent / "open_track2").resolve()

def import_from_path(module_name: str, file_path: Path):
    """파일 경로로 직접 모듈 로드 (패키지 충돌 방지)"""
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod

# Import from kleague_ignobel/src using direct file path
# Need to load config first for preprocess
config_module = import_from_path("kleague_config", PROJECT_ROOT / "src" / "config.py")
io_module = import_from_path("kleague_io", PROJECT_ROOT / "src" / "io.py")

# Load preprocess with config in sys.modules so relative imports work
sys.modules["src.config"] = config_module
preprocess_module = import_from_path("kleague_preprocess", PROJECT_ROOT / "src" / "preprocess.py")

load_raw_data = io_module.load_raw_data
load_match_info = io_module.load_match_info
save_artifact = io_module.save_artifact
preprocess_events = preprocess_module.preprocess_events

# Import zone utilities from open_track2 (with fallback)
OPEN_TRACK2_SRC = OPEN_TRACK2_ROOT / "src"
if OPEN_TRACK2_SRC.exists():
    sys.path.insert(0, str(OPEN_TRACK2_ROOT))
    try:
        from src.feature_engineering import add_zone_columns
        from src.analysis_utils import compute_zone_success_rate, compute_team_zone_profile
    except ImportError:
        sys.path.insert(0, str(OPEN_TRACK2_SRC))
        try:
            from feature_engineering import add_zone_columns
            from analysis_utils import compute_zone_success_rate, compute_team_zone_profile
        except ImportError:
            # Fallback: implement minimal versions
            def add_zone_columns(events: pd.DataFrame, x_col="start_x", y_col="start_y") -> pd.DataFrame:
                df = events.copy()
                # 4 zones x-axis: D (0-26.25), DM (26.25-52.5), AM (52.5-78.75), A (78.75-105)
                # 3 zones y-axis: L (0-22.67), C (22.67-45.33), R (45.33-68)
                df["zone_x"] = pd.cut(
                    df[x_col],
                    bins=[0, 26.25, 52.5, 78.75, 105],
                    labels=["D", "DM", "AM", "A"],
                    include_lowest=True,
                    right=False
                ).astype("string")
                df["zone_y"] = pd.cut(
                    df[y_col],
                    bins=[0, 22.67, 45.33, 68],
                    labels=["L", "C", "R"],
                    include_lowest=True,
                    right=False
                ).astype("string")
                df["zone"] = (df["zone_x"].astype("string") + "-" + df["zone_y"].astype("string")).astype("string")
                return df
            
            def compute_zone_success_rate(events: pd.DataFrame, event_type_col="type_name", outcome_col="result_name", zone_col="zone"):
                df = events.copy()
                # Success definition (fallback): Successful OR Goal OR precomputed is_success
                base = df[outcome_col].isin(["Successful", "Goal"])
                if "is_success" in df.columns:
                    base = base | df["is_success"].fillna(False)
                df["_is_success"] = base
                
                grouped = df.groupby([zone_col, event_type_col], observed=True).agg(
                    attempts=("_is_success", "count"),
                    success=("_is_success", "sum"),
                ).reset_index()
                grouped["success_rate"] = grouped["success"] / grouped["attempts"].replace(0, np.nan)
                grouped["success_rate"] = grouped["success_rate"].fillna(0.0)
                grouped = grouped.rename(columns={event_type_col: "event_type", zone_col: "zone"})
                return grouped[["zone", "event_type", "attempts", "success", "success_rate"]]
            
            def compute_team_zone_profile(events: pd.DataFrame, event_type_col="type_name", zone_col="zone"):
                """Compute team zone profile"""
                profile = events.groupby([zone_col, event_type_col], observed=True).agg(
                    count=("action_id", "count"),
                ).reset_index()
                profile = profile.rename(columns={event_type_col: "event_type"})
                return profile
else:
    # Minimal fallback implementations (vectorized)
    def add_zone_columns(events: pd.DataFrame, x_col="start_x", y_col="start_y") -> pd.DataFrame:
        df = events.copy()
        # 4 zones x-axis: D (0-26.25), DM (26.25-52.5), AM (52.5-78.75), A (78.75-105)
        # 3 zones y-axis: L (0-22.67), C (22.67-45.33), R (45.33-68)
        df["zone_x"] = pd.cut(
            df[x_col],
            bins=[0, 26.25, 52.5, 78.75, 105],
            labels=["D", "DM", "AM", "A"],
            include_lowest=True,
            right=False
        ).astype("string")
        df["zone_y"] = pd.cut(
            df[y_col],
            bins=[0, 22.67, 45.33, 68],
            labels=["L", "C", "R"],
            include_lowest=True,
            right=False
        ).astype("string")
        df["zone"] = (df["zone_x"].astype("string") + "-" + df["zone_y"].astype("string")).astype("string")
        return df
    
    def compute_zone_success_rate(events: pd.DataFrame, event_type_col="type_name", outcome_col="result_name", zone_col="zone"):
        df = events.copy()
        # Success definition (fallback): Successful OR Goal OR precomputed is_success
        base = df[outcome_col].isin(["Successful", "Goal"])
        if "is_success" in df.columns:
            base = base | df["is_success"].fillna(False)
        df["_is_success"] = base
        
        grouped = df.groupby([zone_col, event_type_col], observed=True).agg(
            attempts=("_is_success", "count"),
            success=("_is_success", "sum"),
        ).reset_index()
        grouped["success_rate"] = grouped["success"] / grouped["attempts"].replace(0, np.nan)
        grouped["success_rate"] = grouped["success_rate"].fillna(0.0)
        grouped = grouped.rename(columns={event_type_col: "event_type", zone_col: "zone"})
        return grouped[["zone", "event_type", "attempts", "success", "success_rate"]]
    
    def compute_team_zone_profile(events: pd.DataFrame, event_type_col="type_name", zone_col="zone"):
        """Compute team zone profile"""
        profile = events.groupby([zone_col, event_type_col], observed=True).agg(
            count=("action_id", "count"),
        ).reset_index()
        profile = profile.rename(columns={event_type_col: "event_type"})
        return profile

print("=" * 70)
print("Building Pattern Analysis Artifacts (Day 1)")
print("=" * 70)

# 1. Load and preprocess
print("\n[1/4] Loading and preprocessing data...")
raw = load_raw_data()
match_info = load_match_info()
print(f"  Loaded {len(raw):,} events from {len(match_info):,} matches")

preprocessed = preprocess_events(raw)

# Filter to key event types for pattern analysis
KEY_EVENT_TYPES = ["Pass", "Shot", "Shot_Freekick", "Cross", "Duel", "Tackle", 
                   "Interception", "Foul", "Clearance", "Block"]
events_filtered = preprocessed[preprocessed["type_name"].isin(KEY_EVENT_TYPES)].copy()
print(f"  Filtered to {len(events_filtered):,} key events")

# 2. Add zone columns
print("\n[2/4] Adding zone columns...")
events_with_zones = add_zone_columns(
    events_filtered,
    x_col="start_x",
    y_col="start_y"
)

# Handle NaN zones (events outside pitch bounds)
events_with_zones = events_with_zones[events_with_zones["zone"].notna()].copy()
print(f"  Added zones, {len(events_with_zones):,} events with valid zones")

# 3. Create events_light (minimal columns for fast loading)
print("\n[3/4] Creating events_light.parquet...")
events_light = events_with_zones[[
    "game_id", "action_id", "player_id", "player_name_ko", "team_id", "team_name_ko",
    "type_name", "result_name", "start_x", "start_y", "end_x", "end_y",
    "zone", "zone_x", "zone_y", "is_success", "is_fail"
]].copy()

save_artifact(events_light, "events_light.parquet")
print(f"  Saved: events_light.parquet ({len(events_light):,} events)")

# 4. Create team_zone_profile (vectorized - single groupby)
print("\n[4/4] Creating team_zone_profile.parquet...")

# Team zone profile with event counts
team_zone_profile = events_with_zones.groupby([
    "team_name_ko", "zone", "type_name"
], observed=True).agg(
    event_count=("action_id", "count"),
).reset_index()
team_zone_profile = team_zone_profile.rename(columns={"type_name": "event_type"})

# Calculate success rates (vectorized)
team_zone_success = events_with_zones.groupby([
    "team_name_ko", "zone", "type_name"
], observed=True).agg(
    attempts=("action_id", "count"),
    success=("is_success", "sum"),
).reset_index()
team_zone_success["success_rate"] = np.where(
    team_zone_success["attempts"] > 0,
    team_zone_success["success"] / team_zone_success["attempts"],
    0
)
team_zone_success = team_zone_success.rename(columns={"type_name": "event_type"})

# Merge profiles with success rates
team_zone_df = team_zone_profile.merge(
    team_zone_success[["team_name_ko", "zone", "event_type", "success_rate"]],
    on=["team_name_ko", "zone", "event_type"],
    how="left"
)
team_zone_df["success_rate"] = team_zone_df["success_rate"].fillna(0)

save_artifact(team_zone_df, "team_zone_profile.parquet")
print(f"  Saved: team_zone_profile.parquet ({len(team_zone_df):,} rows)")

# 5. Create player_zone_activity (vectorized)
print("\n[5/4] Creating player_zone_activity.parquet...")

player_zone_activity = events_with_zones.groupby([
    "player_id", "player_name_ko", "team_name_ko", "zone", "type_name"
], observed=True).agg(
    event_count=("action_id", "count"),
    success_count=("is_success", "sum"),
    fail_count=("is_fail", "sum"),
).reset_index()

player_zone_activity["success_rate"] = np.where(
    player_zone_activity["event_count"] > 0,
    player_zone_activity["success_count"] / player_zone_activity["event_count"],
    0
)

save_artifact(player_zone_activity, "player_zone_activity.parquet")
print(f"  Saved: player_zone_activity.parquet ({len(player_zone_activity):,} rows)")

# 6. Create league average for comparison
print("\n[6/4] Creating league_zone_average.parquet...")

league_avg = events_with_zones.groupby(["zone", "type_name"], observed=True).agg(
    league_count=("action_id", "count"),
    league_success=("is_success", "sum"),
).reset_index()

league_avg["league_success_rate"] = np.where(
    league_avg["league_count"] > 0,
    league_avg["league_success"] / league_avg["league_count"],
    0
)

# Calculate per-team averages for normalization
league_avg_by_team = events_with_zones.groupby(["team_name_ko", "zone", "type_name"], observed=True).agg(
    team_count=("action_id", "count"),
).reset_index()

avg_events_per_team = league_avg_by_team.groupby(["zone", "type_name"])["team_count"].mean().reset_index()
avg_events_per_team.columns = ["zone", "type_name", "avg_events_per_team"]

league_avg = league_avg.merge(avg_events_per_team, on=["zone", "type_name"], how="left")

save_artifact(league_avg, "league_zone_average.parquet")
print(f"  Saved: league_zone_average.parquet ({len(league_avg):,} rows)")

print("\n" + "=" * 70)
print("[SUCCESS] Pattern artifacts built successfully!")
print("=" * 70)
print("\nArtifacts created:")
print("  - events_light.parquet")
print("  - team_zone_profile.parquet")
print("  - player_zone_activity.parquet")
print("  - league_zone_average.parquet")
