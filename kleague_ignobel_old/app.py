"""
K League Ignobel Awards - Main Streamlit App
Sports Magazine Style UI
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.io import load_artifact
from src.config import AWARDS
from src.ui_components import (
    inject_custom_css, render_hero_section, render_award_card
)

# Page config
st.set_page_config(
    page_title="K League 이그노벨상",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS
inject_custom_css()


@st.cache_data
def load_data():
    """Load artifacts with caching"""
    try:
        leaderboard = load_artifact("leaderboard.parquet")
        profiles = load_artifact("profiles.parquet")
        return leaderboard, profiles
    except FileNotFoundError:
        st.error("⚠️ Artifacts not found. Please run `python scripts/build_artifacts.py` first.")
        st.stop()


def main():
    # Header
    st.markdown('<p class="main-header">🏆 K League 이그노벨상</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">데이터 기반 이그노벨상 시상식</p>', unsafe_allow_html=True)
    
    # Load data
    leaderboard, profiles = load_data()
    
    # Show home page
    show_home(leaderboard)


def show_home(leaderboard: pd.DataFrame):
    """Show home page with hero section and top 3 awards"""
    
    # Hero Section
    hero_html = render_hero_section(
        "K League's Most Ironic Defensive Moments",
        "데이터가 말하는 K리그 이그노벨상. 의욕은 넘치지만 결과는...? 재미있게 본 스포츠 데이터 스토리텔링"
    )
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # Top 3 Awards (one winner from each of first 3 awards)
    st.markdown('<div class="section-title">🏆 오늘의 Top 3 이그노벨상</div>', unsafe_allow_html=True)
    
    top_awards_list = []
    for award in AWARDS[:3]:
        award_id = award["id"]
        award_data = leaderboard[
            (leaderboard["award_id"] == award_id) & 
            (leaderboard["rank"] == 1)
        ]
        
        if len(award_data) > 0:
            winner = award_data.iloc[0]
            top_awards_list.append({
                "award": award,
                "winner": winner
            })
    
    # Display as large horizontal cards
    cols = st.columns(len(top_awards_list))
    for idx, item in enumerate(top_awards_list):
        with cols[idx]:
            award = item["award"]
            winner = item["winner"]
            
            card_html = render_award_card(
                award_icon=award.get("icon", "🏆"),
                award_title=award["title"],
                player_name=winner["player_name_ko"],
                team_name=winner["team_name_ko"],
                metric_value=winner["score"],
                metric_label="점수",
                rank=int(winner["rank"]),
                percentile=winner.get("percentile"),
                description=f"{award['description']} 이번 시즌 {winner['player_name_ko']} 선수가 가장 눈에 띄었습니다.",
                is_large=True
            )
            st.markdown(card_html, unsafe_allow_html=True)
    
    # All Awards Grid
    st.markdown('<div class="section-title">📋 모든 이그노벨상</div>', unsafe_allow_html=True)
    
    # Display awards as cards in grid
    award_cols = st.columns(3)
    for idx, award in enumerate(AWARDS):
        with award_cols[idx % 3]:
            award_html = f"""
            <div class="award-card" style="padding: 20px;">
                <div style="font-size: 2rem; margin-bottom: 12px;">{award.get('icon', '🏆')}</div>
                <div class="award-title" style="font-size: 1.2rem;">{award['title']}</div>
                <div class="award-subtext">{award['description']}</div>
                <div style="margin-top: 12px;">
                    <span class="badge badge-percentile">{award['category']}</span>
                </div>
            </div>
            """
            st.markdown(award_html, unsafe_allow_html=True)
    
    # Stats Footer
    st.markdown('<div style="margin-top: 60px; padding-top: 40px; border-top: 2px solid #30363d;"></div>', unsafe_allow_html=True)
    
    stats_cols = st.columns(3)
    total_players = len(leaderboard["player_id"].unique())
    total_awards = len(AWARDS)
    total_scores = len(leaderboard)
    
    with stats_cols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_players:,}</div>
            <div class="stat-label">분석 선수</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_cols[1]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_awards}</div>
            <div class="stat-label">이그노벨상</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_cols[2]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_scores:,}</div>
            <div class="stat-label">점수 기록</div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

