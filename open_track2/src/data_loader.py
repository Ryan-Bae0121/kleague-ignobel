"""
Data loading utilities for K-League event data.

This module provides functions to load raw and processed data files.
Column names are kept generic with TODO comments where adaptation is needed.
"""

from pathlib import Path
from typing import Optional
import pandas as pd

# Get project root directory (parent of src/)
# This file is in src/, so project root is parent
_PROJECT_ROOT = Path(__file__).parent.parent

# Data directory paths (relative to project root)
DATA_DIR = _PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def load_raw_events(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load raw event data from CSV file.

    Parameters
    ----------
    path : optional Path
        Path to the raw events CSV file.
        If None, defaults to `RAW_DIR / "raw_data.csv"`.
        TODO: Adjust filename if the competition uses a different name.

    Returns
    -------
    pd.DataFrame
        DataFrame containing event data with columns like:
        - game_id, action_id, team_id, player_id
        - start_x, start_y, end_x, end_y (coordinates)
        - type_name, result_name
        TODO: Update docstring once exact schema is confirmed.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    """
    if path is None:
        path = RAW_DIR / "raw_data.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Raw events file not found at {path}. "
            "Please ensure the data file exists or provide a different path."
        )

    df = pd.read_csv(path)
    return df


def load_match_info(path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load match information from CSV file.

    Parameters
    ----------
    path : optional Path
        Path to the match info CSV file.
        If None, defaults to `RAW_DIR / "match_info.csv"`.
        TODO: Adjust filename if the competition uses a different name.

    Returns
    -------
    pd.DataFrame
        DataFrame containing match metadata with columns like:
        - game_id, home_team_id, away_team_id
        - home_score, away_score
        - home_team_name_ko, away_team_name_ko
        TODO: Update docstring once exact schema is confirmed.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    """
    if path is None:
        path = RAW_DIR / "match_info.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Match info file not found at {path}. "
            "Please ensure the data file exists or provide a different path."
        )

    df = pd.read_csv(path)
    return df


def save_processed(df: pd.DataFrame, filename: str) -> Path:
    """
    Save a processed DataFrame to the processed data directory.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to save.
    filename : str
        Filename (e.g., "events_with_zones.csv").
        Will be saved to `PROCESSED_DIR / filename`.

    Returns
    -------
    Path
        Path to the saved file.
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    filepath = PROCESSED_DIR / filename
    df.to_csv(filepath, index=False)
    return filepath


def load_processed(filename: str) -> pd.DataFrame:
    """
    Load a processed DataFrame from the processed data directory.

    Parameters
    ----------
    filename : str
        Filename to load from `PROCESSED_DIR`.

    Returns
    -------
    pd.DataFrame
        Loaded DataFrame.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    filepath = PROCESSED_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Processed file not found at {filepath}")

    return pd.read_csv(filepath)


if __name__ == "__main__":
    # Quick test / demo
    print("Loading raw events...")
    try:
        events = load_raw_events()
        print(f"Events shape: {events.shape}")
        print(f"Columns: {list(events.columns)}")
        print("\nFirst few rows:")
        print(events.head())
        # TODO: Adjust column names below to match actual dataset
        # if "x" in events.columns and "y" in events.columns:
        #     print(f"\nCoordinate ranges:")
        #     print(f"x: {events['x'].min():.1f} - {events['x'].max():.1f}")
        #     print(f"y: {events['y'].min():.1f} - {events['y'].max():.1f}")
    except FileNotFoundError as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50)
    print("Loading match info...")
    try:
        match_info = load_match_info()
        print(f"Match info shape: {match_info.shape}")
        print(f"Columns: {list(match_info.columns)}")
        print("\nFirst few rows:")
        print(match_info.head())
    except FileNotFoundError as e:
        print(f"Error: {e}")

