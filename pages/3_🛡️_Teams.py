"""
Teams Page - Team comparison and analysis (Report Card Style)
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.io import load_artifact
from src.config import AWARDS
from src.ui_components import inject_custom_css, render_comparison_card, render_stat_card, render_sidebar_toggle

# Load zone data
@st.cache_data
def load_team_zone_data():
    try:
        team_zone = load_artifact("team_zone_profile.parquet")
        league_avg = load_artifact("league_zone_average.parquet")
        return team_zone, league_avg
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame()

st.set_page_config(
    page_title="Teams",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
inject_custom_css()

st.title("🛡️ Teams")

# Load data
@st.cache_data
def load_team_data():
    leaderboard = load_artifact("leaderboard.parquet")
    team_stats = load_artifact("awards_team.parquet")
    return leaderboard, team_stats

leaderboard, team_stats = load_team_data()
team_zone_profile, league_zone_avg = load_team_zone_data()

# Team selection
col_sidebar, col_main = st.columns([1, 4])

with col_sidebar:
    st.markdown("### 팀 선택")
    teams = sorted(leaderboard["team_name_ko"].unique().tolist())
    selected_team = st.selectbox("팀", teams, key="team_select")

# Filter team data
team_players = leaderboard[leaderboard["team_name_ko"] == selected_team].copy()

if len(team_players) == 0:
    st.warning("선택한 팀에 대한 데이터가 없습니다.")
    st.stop()

with col_main:
    # Team Header
    team_header_html = f"""
    <div class="profile-header">
        <div class="profile-name">{selected_team}</div>
        <div class="profile-summary" style="font-size: 1rem;">
            이번 시즌 {selected_team}의 이그노벨상 수상 현황과 리그 평균 대비 분석입니다.
        </div>
    </div>
    """
    st.markdown(team_header_html, unsafe_allow_html=True)
    
    # Team Overview Stats
    st.markdown('<div class="section-title">📊 팀 요약</div>', unsafe_allow_html=True)
    
    stats_cols = st.columns(4)
    
    team_player_count = len(team_players["player_id"].unique())
    team_award_count = len(team_players[team_players["rank"] <= 3])
    team_top1_count = len(team_players[team_players["rank"] == 1])
    avg_score = team_players["score"].mean()
    
    with stats_cols[0]:
        st.markdown(render_stat_card(f"{team_player_count}", "분석 선수"), unsafe_allow_html=True)
    with stats_cols[1]:
        st.markdown(render_stat_card(f"{team_award_count}", "Top 3 수상"), unsafe_allow_html=True)
    with stats_cols[2]:
        st.markdown(render_stat_card(f"{team_top1_count}", "1위 수상"), unsafe_allow_html=True)
    with stats_cols[3]:
        st.markdown(render_stat_card(f"{avg_score:.2f}", "평균 점수"), unsafe_allow_html=True)
    
    # Team Pattern Summary (NEW)
    if len(team_zone_profile) > 0 and len(league_zone_avg) > 0:
        st.markdown('<div class="section-title" style="margin-top: 30px;">📍 팀 대표 패턴</div>', unsafe_allow_html=True)
        
        team_zone_data = team_zone_profile[team_zone_profile["team_name_ko"] == selected_team].copy()
        
        if len(team_zone_data) > 0:
            # Aggregate by zone
            team_zones_agg = team_zone_data.groupby("zone").agg({
                "event_count": "sum"
            }).reset_index().sort_values("event_count", ascending=False)
            
            top3_zones = team_zones_agg.head(3)
            
            pattern_cols = st.columns(3)
            for idx, (_, zone_row) in enumerate(top3_zones.iterrows()):
                with pattern_cols[idx]:
                    # Get league average for comparison
                    league_val = 0
                    if len(league_zone_avg) > 0:
                        league_match = league_zone_avg[league_zone_avg["zone"] == zone_row["zone"]]
                        if len(league_match) > 0:
                            league_val = league_match["league_count"].iloc[0]
                    
                    diff = zone_row["event_count"] - league_val
                    diff_class = "better" if diff > 0 else "worse"
                    
                    zone_html = f"""
                    <div class="award-card" style="padding: 16px; text-align: center;">
                        <div class="award-title" style="font-size: 1.2rem; margin-bottom: 8px;">
                            {zone_row['zone']}
                        </div>
                        <div class="award-metric" style="font-size: 1.5rem;">
                            {zone_row['event_count']:.0f}
                        </div>
                        <div class="award-subtext" style="font-size: 0.85rem;">
                            이벤트 수<br>
                            리그 평균: {league_val:.0f}
                        </div>
                        <div class="{diff_class}" style="font-size: 0.9rem; margin-top: 8px;">
                            ({'+' if diff > 0 else ''}{diff:.0f})
                        </div>
                    </div>
                    """
                    st.markdown(zone_html, unsafe_allow_html=True)
            
            # Pattern summary text
            top_zone = top3_zones.iloc[0]
            pattern_summary = f"**{selected_team}**은(는) **{top_zone['zone']}**에서 가장 많은 활동을 보입니다. "
            
            pattern_html = f"""
            <div class="award-card" style="margin-top: 20px; padding: 16px;">
                <div class="award-subtext">
                    {pattern_summary}
                </div>
            </div>
            """
            st.markdown(pattern_html, unsafe_allow_html=True)
    
    # Category Filter
    st.markdown('<div class="section-title">📋 카테고리별 성과</div>', unsafe_allow_html=True)
    
    categories = ["전체"] + list(set(a["category"] for a in AWARDS))
    selected_category = st.selectbox("카테고리", categories, key="team_category")
    
    if selected_category == "전체":
        category_awards = AWARDS
    else:
        category_awards = [a for a in AWARDS if a["category"] == selected_category]
    
    team_category_data = team_players[team_players["award_id"].isin([a["id"] for a in category_awards])]
    
    if len(team_category_data) > 0:
        # Top Players in Category
        top_players = team_category_data.nsmallest(10, "rank")
        
        st.markdown("#### Top 10 선수")
        
        rows = (len(top_players) + 1) // 2
        for i in range(rows):
            cols = st.columns(2)
            for j in range(2):
                idx = i * 2 + j
                if idx < len(top_players):
                    with cols[j]:
                        player_row = top_players.iloc[idx]
                        award_info = next((a for a in AWARDS if a["id"] == player_row["award_id"]), None)
                        award_title = award_info["title"] if award_info else "상"
                        
                        card_html = f"""
                        <div class="award-card" style="padding: 16px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 0.9rem; color: #8b949e; margin-bottom: 4px;">
                                        {award_title}
                                    </div>
                                    <div style="font-size: 1.1rem; color: #f8f9fa; font-weight: 600;">
                                        {player_row["player_name_ko"]}
                                    </div>
                                </div>
                                <div style="text-align: right;">
                                    <div class="badge badge-rank" style="font-size: 1rem;">
                                        #{int(player_row["rank"])}
                                    </div>
                                    <div style="font-size: 1rem; color: #facc15; font-weight: 700; margin-top: 4px;">
                                        {player_row["score"]:.3f}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
    
    # Team vs League Comparison
    st.markdown('<div class="section-title" style="margin-top: 40px;">📈 리그 평균 대비</div>', unsafe_allow_html=True)
    
    comparison_data = []
    for award in AWARDS:
        award_id = award["id"]
        team_award_data = team_players[team_players["award_id"] == award_id]
        league_award_data = leaderboard[leaderboard["award_id"] == award_id]
        
        if len(team_award_data) > 0 and len(league_award_data) > 0:
            team_avg = team_award_data["score"].mean()
            league_avg = league_award_data["score"].mean()
            
            comparison_data.append({
                "award_title": award["title"],
                "team_avg": team_avg,
                "league_avg": league_avg,
                "diff": team_avg - league_avg
            })
    
    if comparison_data:
        # Display as cards in grid
        comp_cols = st.columns(3)
        for idx, comp in enumerate(comparison_data):
            with comp_cols[idx % 3]:
                comparison_html = render_comparison_card(
                    label=comp["award_title"],
                    team_value=comp["team_avg"],
                    league_value=comp["league_avg"]
                )
                st.markdown(comparison_html, unsafe_allow_html=True)
    else:
        st.info("비교 데이터가 없습니다.")
