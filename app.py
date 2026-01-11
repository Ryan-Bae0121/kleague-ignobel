"""
K League Ignobel Awards - Main Streamlit App
Sports Magazine Style UI - Streamlit 정석 방식 (JS 없이)
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import random

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.io import load_artifact
from src.config import AWARDS
from src.ui_components import (
    inject_custom_css, render_hero_section, render_award_card
)
try:
    from src.image_utils import render_team_logo, render_player_photo
    HAS_IMAGES = True
except ImportError:
    HAS_IMAGES = False

# Page config
st.set_page_config(
    page_title="K League 이그노벨상",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_custom_css()

# Add CSS for hover effects on award cards (React 호환 - 인라인 이벤트 핸들러 제거)
st.markdown("""
<style>
    /* Award card hover effects - CSS only (React 호환) */
    .clickable-award-card {
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    .clickable-award-card:hover {
        transform: translateY(-6px) !important;
        border-color: #facc15 !important;
        box-shadow: 0 16px 32px rgba(0, 0, 0, 0.5), 0 4px 8px rgba(250, 204, 21, 0.3) !important;
    }
    
    /* 모든 award_nav_ 버튼 기본 숨김 (전역) */
    button[key^="award_nav_"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
    }
    
    /* 버튼의 부모 컨테이너도 숨기기 */
    .stButton:has(button[key^="award_nav_"]) {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)



@st.cache_data(ttl=0)  # Disable cache during development
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
    show_home(leaderboard, profiles)


def show_home(leaderboard: pd.DataFrame, profiles: pd.DataFrame):
    """Show home page with hero section and top 3 awards"""
    
    # Hero Section
    hero_html = render_hero_section(
        "K League's Most Ironic Moments",
        "데이터가 말하는 K리그 이그노벨상. 의욕은 넘치지만 결과는...?<br>재미있게 본 스포츠 데이터 스토리텔링"
    )
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # Top 3 Awards (random selection on each refresh)
    st.markdown('<div class="section-title"><span class="section-emoji">🏆</span><span class="section-text"> 오늘의 Top 3 이그노벨상</span></div>', unsafe_allow_html=True)
    
    # Randomly select 3 awards (different on each refresh)
    selected_awards = random.sample(AWARDS, min(3, len(AWARDS)))
    
    top_awards_list = []
    for award in selected_awards:
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
            
            # 카드 HTML
            # Remove "실패율이 동일한 선수는..." part from description for block_fail and interception_fail
            award_description = award['description']
            if award['id'] in ["block_fail", "interception_fail"]:
                # Remove the part about "실패율이 동일한 선수는..."
                if ". 실패율이 동일한" in award_description:
                    award_description = award_description.split(". 실패율이 동일한")[0]
            
            # Get attempt count for interception_fail and block_fail awards
            attempt_info = ""
            if award['id'] == "interception_fail":
                player_profile = profiles[profiles["player_id"] == winner["player_id"]]
                if len(player_profile) > 0 and "interception_attempt" in player_profile.columns:
                    attempt_count = player_profile.iloc[0]["interception_attempt"]
                    if pd.notna(attempt_count):
                        attempt_info = f'<div style="font-size: 0.9rem; color: #8b949e; margin-top: 8px;">시도: {int(attempt_count)}회</div>'
            elif award['id'] == "block_fail":
                player_profile = profiles[profiles["player_id"] == winner["player_id"]]
                if len(player_profile) > 0 and "block_attempt" in player_profile.columns:
                    attempt_count = player_profile.iloc[0]["block_attempt"]
                    if pd.notna(attempt_count):
                        attempt_info = f'<div style="font-size: 0.9rem; color: #8b949e; margin-top: 8px;">시도: {int(attempt_count)}회</div>'
            
            card_html = render_award_card(
                award_icon=award.get("icon", "🏆"),
                award_title=award["title"],
                player_name=winner["player_name_ko"],
                team_name=winner["team_name_ko"],
                metric_value=winner["score"],
                metric_label="점수",
                rank=int(winner["rank"]),
                percentile=winner.get("percentile"),
                description=f"{award_description} 이번 시즌 {winner['player_name_ko']} 선수가 가장 눈에 띄었습니다.",
                is_large=True,
                show_images=True,
                extra_info=attempt_info
            )
            
            # Top3 카드 표시
            st.markdown(card_html, unsafe_allow_html=True)
    
    # All Awards Grid
    st.markdown('<div class="section-title"><span class="section-emoji">📋</span><span class="section-text"> 모든 이그노벨상</span></div>', unsafe_allow_html=True)
    
    # Display awards as clickable cards in grid
    award_cols = st.columns(3)
    for idx, award in enumerate(AWARDS):
        col_idx = idx % 3
        with award_cols[col_idx]:
            award_id = award['id']
            button_key = f"award_nav_{award_id}"
            
            # Remove "실패율이 동일한 선수는..." part from description for block_fail and interception_fail
            award_description = award['description']
            if award_id in ["block_fail", "interception_fail"]:
                if ". 실패율이 동일한" in award_description:
                    award_description = award_description.split(". 실패율이 동일한")[0]
            
            # 카드 HTML 표시
            card_html = f"""
            <div class="clickable-award-card" 
                 style="padding: 20px; transition: all 0.3s ease; position: relative; background: #161b22; border: 1px solid #30363d; border-radius: 16px; box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4); margin-bottom: 12px;">
                <div style="font-size: 2rem; margin-bottom: 12px;">{award.get('icon', '🏆')}</div>
                <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 8px; color: #facc15;">{award['title']}</div>
                <div style="margin-top: 8px; color: #9aa4b2; font-size: 0.9rem;">{award_description}</div>
                <div style="margin-top: 16px;">
                    <span style="padding: 4px 12px; border-radius: 12px; border: 1px solid #30363d; color: #9aa4b2; font-size: 0.85rem;">{award['category']}</span>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 상세 보기 버튼
            if st.button("상세 보기", key=button_key, use_container_width=True, type="primary"):
                st.session_state.selected_award_id = award_id
                st.session_state._scroll_to_top = True  # 스크롤 초기화 플래그
                st.switch_page("pages/1_🏆_Awards.py")
    
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
