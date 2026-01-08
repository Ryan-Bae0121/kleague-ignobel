"""
Data I/O utilities
"""
from pathlib import Path
from typing import Optional
import pandas as pd

# Project root (assuming this file is in kleague_ignobel/src/)
_PROJECT_ROOT = Path(__file__).parent.parent

# Data paths - adjust relative to open_track2 directory
_OPEN_TRACK2_ROOT = _PROJECT_ROOT.parent / "open_track2"
RAW_DATA_PATH = _OPEN_TRACK2_ROOT / "raw_data.csv"
MATCH_INFO_PATH = _OPEN_TRACK2_ROOT / "match_info.csv"

# Artifacts directory
ARTIFACTS_DIR = _PROJECT_ROOT / "artifacts"


def load_raw_data(path: Optional[Path] = None) -> pd.DataFrame:
    """Load raw event data"""
    if path is None:
        path = RAW_DATA_PATH
    
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found at {path}")
    
    return pd.read_csv(path)


def load_match_info(path: Optional[Path] = None) -> pd.DataFrame:
    """Load match info data"""
    if path is None:
        path = MATCH_INFO_PATH
    
    if not path.exists():
        raise FileNotFoundError(f"Match info file not found at {path}")
    
    return pd.read_csv(path)


def save_artifact(df: pd.DataFrame, filename: str) -> Path:
    """Save artifact to parquet file"""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = ARTIFACTS_DIR / filename
    df.to_parquet(filepath, index=False)
    return filepath


def load_artifact(filename: str) -> pd.DataFrame:
    """Load artifact from parquet file"""
    filepath = ARTIFACTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Artifact not found at {filepath}")
    
    return pd.read_parquet(filepath)


