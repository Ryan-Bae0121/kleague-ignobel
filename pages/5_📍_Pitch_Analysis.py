"""
Pitch Analysis Page - Interactive pitch visualization
Day 2: Pitch maps for teams, players, and Ignobel winners
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.io import load_artifact
from src.config import AWARDS
from src.ui_components import inject_custom_css
from src.pitch_utils import (
    draw_pitch_plotly, plot_events_scatter, plot_events_heatmap, plot_zone_activity
)
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Pitch Analysis | K League 이그노벨상",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
inject_custom_css()

st.title("📍 Pitch Analysis")

st.markdown("""
<div class="award-card">
    <div class="award-subtext">
        피치 위에서 이벤트 위치를 시각화하여 공간적 패턴을 분석합니다.
        팀별 공격 패턴, 선수별 활동 영역, 이그노벨 수상자의 주요 활동 위치를 확인할 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_pitch_data():
    events_light = load_artifact("events_light.parquet")
    player_zone = load_artifact("player_zone_activity.parquet")
    leaderboard = load_artifact("leaderboard.parquet")
    return events_light, player_zone, leaderboard

events_light, player_zone, leaderboard = load_pitch_data()

# Tabs
tab1, tab2, tab3 = st.tabs(["🏟️ 팀 피치맵", "👤 선수 활동 영역", "🏆 이그노벨 수상자 지도"])

# ============================================
# Tab 1: Team Pitch Map
# ============================================
with tab1:
    st.markdown('<div class="section-title">🏟️ 팀별 피치 이벤트 맵</div>', unsafe_allow_html=True)
    
    col_filter, col_plot = st.columns([1, 3])
    
    with col_filter:
        # Team selection
        teams = sorted(events_light["team_name_ko"].unique().tolist())
        selected_team = st.selectbox("팀 선택", teams, key="team_pitch")
        
        # Event type selection
        event_types = ["All", "Pass", "Shot", "Shot_Freekick", "Cross", "Duel", 
                      "Tackle", "Interception", "Foul", "Clearance", "Block"]
        selected_event = st.selectbox("이벤트 타입", event_types, key="event_type_team")
        
        # Visualization mode
        viz_mode = st.radio(
            "시각화 모드",
            ["히트맵 (밀도)", "스캐터 (개별 이벤트)"],
            key="viz_mode_team"
        )
        
        # Show zones
        show_zones = st.checkbox("존 경계선 표시", value=True, key="show_zones_team")
    
    with col_plot:
        # Filter team events
        team_events = events_light[events_light["team_name_ko"] == selected_team].copy()
        
        if len(team_events) == 0:
            st.warning("선택한 팀의 데이터가 없습니다.")
        else:
            # Create pitch
            fig = draw_pitch_plotly(show_zones=show_zones, width=800, height=1100)
            
            # Plot based on mode
            event_type_filter = None if selected_event == "All" else selected_event
            
            if viz_mode == "히트맵 (밀도)":
                fig = plot_events_heatmap(
                    team_events,
                    event_type=event_type_filter,
                    fig=fig,
                    show_zones=show_zones
                )
            else:
                fig = plot_events_scatter(
                    team_events,
                    event_type=event_type_filter,
                    fig=fig,
                    opacity=0.5,
                    show_zones=show_zones
                )
            
            fig.update_layout(
                title=f"{selected_team} - {selected_event if selected_event != 'All' else '모든 이벤트'}"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            st.markdown('<div class="section-title" style="margin-top: 20px;">📊 통계</div>', unsafe_allow_html=True)
            
            stats_cols = st.columns(4)
            total_events = len(team_events)
            if event_type_filter:
                filtered_events = team_events[team_events["type_name"] == event_type_filter]
            else:
                filtered_events = team_events
            
            with stats_cols[0]:
                st.metric("총 이벤트", f"{total_events:,}")
            with stats_cols[1]:
                st.metric("표시된 이벤트", f"{len(filtered_events):,}")
            with stats_cols[2]:
                st.metric("이벤트 타입", selected_event)
            with stats_cols[3]:
                success_rate = (filtered_events["is_success"].sum() / len(filtered_events) * 100) if len(filtered_events) > 0 else 0
                st.metric("성공률", f"{success_rate:.1f}%")

# ============================================
# Tab 2: Player Activity Zone
# ============================================
with tab2:
    st.markdown('<div class="section-title">👤 선수별 활동 영역</div>', unsafe_allow_html=True)
    
    col_filter, col_plot = st.columns([1, 3])
    
    with col_filter:
        # Player selection
        players = sorted(events_light["player_name_ko"].dropna().unique().tolist())
        selected_player = st.selectbox("선수 선택", players, key="player_pitch")
        
        # Event type selection
        event_types = ["All", "Pass", "Shot", "Cross", "Duel", "Tackle", "Interception"]
        selected_event = st.selectbox("이벤트 타입", event_types, key="event_type_player")
        
        # Show zones
        show_zones = st.checkbox("존 경계선 표시", value=True, key="show_zones_player")
    
    with col_plot:
        # Filter player events
        player_events = events_light[events_light["player_name_ko"] == selected_player].copy()
        
        if len(player_events) == 0:
            st.warning("선택한 선수의 데이터가 없습니다.")
        else:
            # Create pitch
            fig = draw_pitch_plotly(show_zones=show_zones, width=800, height=1100)
            
            # Plot events
            event_type_filter = None if selected_event == "All" else selected_event
            fig = plot_events_scatter(
                player_events,
                event_type=event_type_filter,
                fig=fig,
                opacity=0.6,
                show_zones=show_zones
            )
            
            # Get player zone activity
            player_zone_data = player_zone[
                (player_zone["player_name_ko"] == selected_player) &
                (player_zone["type_name"] == (selected_event if selected_event != "All" else player_zone["type_name"].iloc[0] if len(player_zone) > 0 else "Pass"))
            ]
            
            if len(player_zone_data) > 0 and show_zones:
                fig = plot_zone_activity(
                    player_zone_data,
                    fig=fig,
                    metric_col="event_count",
                    show_zones=show_zones
                )
            
            player_team = player_events["team_name_ko"].iloc[0] if len(player_events) > 0 else ""
            fig.update_layout(
                title=f"{selected_player} ({player_team}) - {selected_event if selected_event != 'All' else '모든 이벤트'}"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Top 3 zones
            if len(player_zone_data) > 0:
                st.markdown('<div class="section-title" style="margin-top: 20px;">🔥 주요 활동 존 TOP 3</div>', unsafe_allow_html=True)
                
                top_zones = player_zone_data.nlargest(3, "event_count")
                zone_cols = st.columns(3)
                
                for idx, (_, zone_row) in enumerate(top_zones.iterrows()):
                    with zone_cols[idx]:
                        zone_html = f"""
                        <div class="award-card" style="padding: 16px; text-align: center;">
                            <div class="award-title" style="font-size: 1.2rem;">{zone_row['zone']}</div>
                            <div class="award-metric" style="font-size: 2rem;">{zone_row['event_count']:.0f}</div>
                            <div class="award-subtext">이벤트 수</div>
                        </div>
                        """
                        st.markdown(zone_html, unsafe_allow_html=True)

# ============================================
# Tab 3: Ignobel Winner Map
# ============================================
with tab3:
    st.markdown('<div class="section-title">🏆 이그노벨 수상자 활동 지도</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="award-card">
        <div class="award-subtext">
            이그노벨상 수상자들이 실제로 어디서 활동했는지 피치 위에 표시합니다.
            특정 상을 선택하면, 그 상의 수상자들이 주로 활동한 위치를 확인할 수 있습니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_filter, col_plot = st.columns([1, 3])
    
    with col_filter:
        # Award selection
        award_titles = [f"{a['icon']} {a['title']}" for a in AWARDS]
        selected_award_idx = st.selectbox("상 선택", range(len(award_titles)), 
                                         format_func=lambda x: award_titles[x],
                                         key="award_pitch")
        
        selected_award = AWARDS[selected_award_idx]
        selected_award_id = selected_award["id"]
        
        # Top N winners
        top_n = st.slider("표시할 수상자 수", 1, 10, 3, key="top_n_winners")
        
        # Show zones
        show_zones = st.checkbox("존 경계선 표시", value=True, key="show_zones_ignobel")
    
    with col_plot:
        # Get winners
        award_winners = leaderboard[
            (leaderboard["award_id"] == selected_award_id) & 
            (leaderboard["rank"] <= top_n)
        ].sort_values("rank")
        
        if len(award_winners) == 0:
            st.warning("선택한 상의 수상자 데이터가 없습니다.")
        else:
            # Get player IDs
            winner_ids = award_winners["player_id"].tolist()
            winner_names = award_winners["player_name_ko"].tolist()
            
            # Filter events for winners
            winner_events = events_light[events_light["player_id"].isin(winner_ids)].copy()
            
            if len(winner_events) == 0:
                st.info("수상자의 이벤트 데이터가 없습니다.")
            else:
                # Create pitch
                fig = draw_pitch_plotly(show_zones=show_zones, width=800, height=1100)
                
                # Plot events with different colors for each player
                colors = px.colors.qualitative.Set3
                for idx, (player_id, player_name) in enumerate(zip(winner_ids, winner_names)):
                    player_events = winner_events[winner_events["player_id"] == player_id]
                    if len(player_events) > 0:
                        fig.add_trace(go.Scatter(
                            x=player_events["start_x"],
                            y=player_events["start_y"],
                            mode='markers',
                            name=player_name,
                            marker=dict(
                                color=colors[idx % len(colors)],
                                size=6,
                                opacity=0.5,
                                line=dict(width=0.5, color="white")
                            ),
                            hovertemplate=f"<b>{player_name}</b><br>" +
                                        "X: %{x:.1f}<br>" +
                                        "Y: %{y:.1f}<extra></extra>"
                        ))
                
                fig.update_layout(
                    title=f"{selected_award['icon']} {selected_award['title']} 수상자 활동 지도",
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Winner list
                st.markdown('<div class="section-title" style="margin-top: 20px;">🏆 수상자 목록</div>', unsafe_allow_html=True)
                
                winner_cols = st.columns(len(award_winners))
                for idx, (_, winner) in enumerate(award_winners.iterrows()):
                    with winner_cols[idx]:
                        rank_emoji = "🥇" if winner["rank"] == 1 else "🥈" if winner["rank"] == 2 else "🥉" if winner["rank"] == 3 else f"#{int(winner['rank'])}"
                        winner_html = f"""
                        <div class="award-card" style="padding: 16px; text-align: center;">
                            <div style="font-size: 1.5rem; margin-bottom: 8px;">{rank_emoji}</div>
                            <div class="award-player" style="font-size: 1rem;">{winner['player_name_ko']}</div>
                            <div class="award-team" style="font-size: 0.85rem;">{winner['team_name_ko']}</div>
                            <div class="award-subtext" style="margin-top: 8px;">점수: {winner['score']:.3f}</div>
                        </div>
                        """
                        st.markdown(winner_html, unsafe_allow_html=True)

