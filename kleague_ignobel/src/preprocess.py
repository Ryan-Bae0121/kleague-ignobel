"""
Data preprocessing utilities
"""
import pandas as pd
try:
    from .config import CARD_SET
except ImportError:
    # Fallback for direct file loading
    from src.config import CARD_SET


def preprocess_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess raw event data
    
    Adds:
    - is_success, is_fail flags
    - is_card flag
    - in_def_third flag
    - Time sorting
    """
    df = df.copy()
    
    # Time sorting (for time-based analysis)
    df = df.sort_values(["game_id", "period_id", "time_seconds", "action_id"]).reset_index(drop=True)
    
    # Success/fail flags
    df["is_success"] = df["result_name"] == "Successful"
    df["is_fail"] = df["result_name"] == "Unsuccessful"
    
    # Card flag
    df["is_card"] = df["result_name"].isin(CARD_SET)
    
    # Defensive third (start_x <= 35)
    df["in_def_third"] = df["start_x"] <= 35
    
    return df


