# K-League Tactical Pattern Analysis

## Description

This project analyzes K-League event data from the Dacon competition to identify:
- Which attacking patterns work well **against a specific team**
- Which defensive weaknesses (zones / pass types) each team has

The analysis uses event-level data with x,y positions to build tactical insights.

## Dataset Description

The dataset contains:
- **Event data** (`raw_data.csv`): Individual events (passes, shots, etc.) with coordinates
  - Columns: `game_id`, `action_id`, `team_id`, `start_x`, `start_y`, `end_x`, `end_y`, `type_name`, `result_name`, etc.
  - TODO: Update this section once exact competition schema is confirmed
- **Match information** (`match_info.csv`): Game metadata
  - Columns: `game_id`, `home_team_id`, `away_team_id`, `home_score`, `away_score`, `home_team_name_ko`, `away_team_name_ko`, etc.
  - TODO: Adjust column descriptions to match exact competition format

## Project Structure

```
K_league/
├── data/
│   ├── raw/              # Raw competition data
│   │   ├── raw_data.csv
│   │   └── match_info.csv
│   └── processed/        # Cleaned / feature-engineered data
├── notebooks/
│   ├── 00_data_overview.ipynb
│   ├── 01_pitch_utils_and_zones.ipynb
│   ├── 02_team_offense_analysis.ipynb
│   ├── 03_team_defense_analysis.ipynb
│   └── 04_pattern_comparison_and_story.ipynb
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── analysis_utils.py
│   └── pitch_plot.py
├── reports/
│   ├── figures/
│   └── slides/
└── README.md
```

## How to Run

### Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install pandas numpy matplotlib seaborn jupyter
   ```

4. Run Jupyter notebooks:
   ```bash
   jupyter notebook
   ```

5. Start with `notebooks/00_data_overview.ipynb` to explore the data.

### Usage

- **00_data_overview.ipynb**: Inspect raw data structure and basic statistics
- **01_pitch_utils_and_zones.ipynb**: Validate pitch plotting and zone assignment
- **02_team_offense_analysis.ipynb**: Analyze attacking patterns for a specific team
- **03_team_defense_analysis.ipynb**: Identify defensive weaknesses for a specific team
- **04_pattern_comparison_and_story.ipynb**: Compare multiple teams and generate insights

## TODO

- [ ] Create `requirements.txt` with exact package versions
- [ ] Adapt column names in `src/` modules to match exact dataset schema
- [ ] Build interactive dashboard (e.g., Streamlit or Plotly Dash)
- [ ] Implement auto-report generation for team profiles
- [ ] Add unit tests for utility functions
- [ ] Create visualization templates for common analysis patterns
- [ ] Add possession tracking and phase analysis
- [ ] Implement machine learning models for pattern prediction


