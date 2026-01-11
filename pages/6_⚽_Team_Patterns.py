"""
Team Patterns Page - Zone-based team pattern analysis
Day 3: Zone heatmap + league average comparison (Light version)
"""
import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.io import load_artifact
from src.ui_components import inject_custom_css, get_team_logo_html
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Team Patterns | K League 이그노벨상",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
inject_custom_css()


st.title("⚽ Team Patterns")

st.markdown("""
<div class="award-card">
    <div class="award-subtext">
        팀별 공격/수비 패턴을 Zone 기반으로 분석합니다. 리그 평균과 비교하여 각 팀의 특성을 파악할 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_pattern_data():
    team_zone = load_artifact("team_zone_profile.parquet")
    league_avg = load_artifact("league_zone_average.parquet")
    return team_zone, league_avg

team_zone, league_avg = load_pattern_data()

# Zone order for consistent display
ZONE_ORDER = [
    "D-L", "D-C", "D-R",
    "DM-L", "DM-C", "DM-R",
    "AM-L", "AM-C", "AM-R",
    "A-L", "A-C", "A-R"
]

EVENT_TYPES = ["Pass", "Shot", "Cross", "Duel", "Tackle", "Interception", "Foul"]

# Filters
col_filter, col_main = st.columns([1, 4])

with col_filter:
    st.markdown("### 필터")
    
    # Team selection
    teams = sorted(team_zone["team_name_ko"].unique().tolist())
    selected_team = st.selectbox("팀 선택", teams, key="pattern_team")
    
    # Show selected team logo below selectbox
    if selected_team:
        team_logo_html = get_team_logo_html(selected_team, size=60)
        if team_logo_html:
            st.markdown(f'<div style="text-align: center; margin-top: 15px; margin-bottom: 10px;">{team_logo_html}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; color: #facc15; font-weight: 600; font-size: 1.1rem;">{selected_team}</div>', unsafe_allow_html=True)
    
    # Event type
    selected_event = st.selectbox("이벤트 타입", ["All"] + EVENT_TYPES, key="pattern_event")
    
    # Metric type
    metric_type = st.radio(
        "지표",
        ["이벤트 수 (빈도)", "성공률"],
        key="pattern_metric"
    )

with col_main:
    # Filter data
    team_data = team_zone[team_zone["team_name_ko"] == selected_team].copy()
    
    if selected_event != "All":
        team_data = team_data[team_data["event_type"] == selected_event].copy()
        league_data = league_avg[league_avg["type_name"] == selected_event].copy()
    else:
        # Aggregate all event types - calculate totals and weighted averages
        # For team data
        team_data_total = team_data.groupby("zone")["event_count"].sum().reset_index()
        
        # Calculate weighted average success_rate per zone
        team_success = []
        for zone in team_data["zone"].unique():
            zone_data = team_data[team_data["zone"] == zone]
            weights = zone_data["event_count"].values
            values = zone_data["success_rate"].values
            if len(weights) > 0 and weights.sum() > 0:
                weighted_avg = np.average(values, weights=weights)
            else:
                weighted_avg = 0.0
            team_success.append({"zone": zone, "success_rate": weighted_avg})
        
        team_success_df = pd.DataFrame(team_success)
        team_data = team_data_total.merge(team_success_df, on="zone", how="left")
        team_data["success_rate"] = team_data["success_rate"].fillna(0)
        team_data["event_type"] = "All"
        
        # For league data - 팀당 평균 사용
        if "avg_events_per_team" in league_avg.columns:
            # 팀당 평균이 있으면 그것을 사용
            league_data_total = league_avg.groupby("zone")["avg_events_per_team"].sum().reset_index()
            league_data_total.columns = ["zone", "avg_events_per_team"]
        else:
            # 팀당 평균이 없으면 전체 합계를 팀 수로 나누어 평균 계산
            num_teams = team_zone["team_name_ko"].nunique()
            if num_teams > 0:
                league_data_total = league_avg.groupby("zone")["league_count"].sum().reset_index()
                league_data_total["avg_events_per_team"] = league_data_total["league_count"] / num_teams
                league_data_total = league_data_total[["zone", "avg_events_per_team"]]
            else:
                league_data_total = pd.DataFrame(columns=["zone", "avg_events_per_team"])
        
        league_success_list = []
        for zone in league_avg["zone"].unique():
            zone_data = league_avg[league_avg["zone"] == zone]
            # 팀당 평균을 가중치로 사용 (없으면 전체 합계 사용)
            weights = zone_data["avg_events_per_team"].values if "avg_events_per_team" in zone_data.columns else zone_data["league_count"].values
            values = zone_data["league_success_rate"].values
            if len(weights) > 0 and weights.sum() > 0:
                weighted_avg = np.average(values, weights=weights)
            else:
                weighted_avg = 0.0
            league_success_list.append({"zone": zone, "league_success_rate": weighted_avg})
        
        league_success_df = pd.DataFrame(league_success_list)
        league_data = league_data_total.merge(league_success_df, on="zone", how="left")
        league_data["league_success_rate"] = league_data["league_success_rate"].fillna(0)
        league_data["type_name"] = "All"
    
    # Prepare data for heatmap
    if metric_type == "이벤트 수 (빈도)":
        metric_col = "event_count"
        # 리그 평균은 팀당 평균을 사용 (전체 합계가 아닌)
        league_metric_col = "avg_events_per_team" if "avg_events_per_team" in league_data.columns else "league_count"
        title_suffix = "이벤트 수"
    else:
        metric_col = "success_rate"
        league_metric_col = "league_success_rate"
        title_suffix = "성공률"
    
    # Create zone matrix
    zone_matrix = []
    for zone in ZONE_ORDER:
        team_val = team_data[team_data["zone"] == zone][metric_col].values
        league_val = league_data[league_data["zone"] == zone][league_metric_col].values
        
        team_val = team_val[0] if len(team_val) > 0 else 0
        league_val = league_val[0] if len(league_val) > 0 else 0
        
        # 리그 평균이 없으면 0으로 처리 (데이터가 없는 경우)
        if league_val == 0 or pd.isna(league_val):
            league_val = team_val if team_val > 0 else 0  # 팀 값이 있으면 그것을 사용 (임시)
        
        diff = team_val - league_val if league_val > 0 else 0
        diff_pct = (diff / league_val * 100) if league_val > 0 else 0
        
        zone_matrix.append({
            "zone": zone,
            "team_value": team_val,
            "league_value": league_val,
            "diff": diff,
            "diff_pct": diff_pct
        })
    
    zone_df = pd.DataFrame(zone_matrix)
    
    # 1. Zone Profile Heatmap
    st.markdown('<div class="section-title">📊 Zone 프로필 히트맵</div>', unsafe_allow_html=True)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=[zone_df["team_value"].tolist()],
        x=zone_df["zone"].tolist(),
        y=[selected_team],
        colorscale="YlOrRd",
        showscale=True,
        text=[[f"{v:.1f}" for v in zone_df["team_value"]]],
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False,
        hovertemplate="<b>%{y}</b><br>" +
                      "Zone: %{x}<br>" +
                      f"{title_suffix}: %{{z:.2f}}<extra></extra>"
    ))
    
    # Plotly title에는 HTML을 넣을 수 없으므로 텍스트만 사용
    fig.update_layout(
        title=f"{selected_team} - Zone별 {title_suffix}",
        xaxis_title="Zone",
        yaxis_title="",
        height=200,
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Team vs League Comparison
    st.markdown('<div class="section-title" style="margin-top: 40px;">📈 리그 평균 대비 비교</div>', unsafe_allow_html=True)
    
    # Comparison bar chart
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        x=zone_df["zone"],
        y=zone_df["team_value"],
        name=selected_team,
        marker_color="#facc15",
        text=[f"{v:.1f}" for v in zone_df["team_value"]],
        textposition="outside"
    ))
    
    fig2.add_trace(go.Bar(
        x=zone_df["zone"],
        y=zone_df["league_value"],
        name="리그 평균",
        marker_color="#8b949e",
        opacity=0.7,
        text=[f"{v:.1f}" for v in zone_df["league_value"]],
        textposition="outside"
    ))
    
    # Plotly title에는 HTML을 넣을 수 없으므로 텍스트만 사용
    fig2.update_layout(
        title=f"{selected_team} vs 리그 평균 - Zone별 {title_suffix}",
        xaxis_title="Zone",
        yaxis_title=title_suffix,
        barmode="group",
        height=500,
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # 3. Difference Analysis
    st.markdown('<div class="section-title" style="margin-top: 40px;">📊 차이 분석</div>', unsafe_allow_html=True)
    
    # Sort by absolute difference
    zone_df_sorted = zone_df.copy()
    zone_df_sorted["abs_diff"] = zone_df_sorted["diff"].abs()
    zone_df_sorted = zone_df_sorted.sort_values("abs_diff", ascending=False)
    
    # Top differences
    st.markdown("#### 차이가 큰 Zone TOP 5")
    
    diff_cols = st.columns(5)
    for idx, (_, row) in enumerate(zone_df_sorted.head(5).iterrows()):
        with diff_cols[idx]:
            diff_class = "better" if row["diff"] > 0 else "worse"
            diff_sign = "+" if row["diff"] > 0 else ""
            
            diff_html = f"""
            <div class="award-card" style="padding: 16px; text-align: center;">
                <div class="award-title" style="font-size: 1rem;">{row['zone']}</div>
                <div class="{diff_class}" style="font-size: 1.2rem; margin: 8px 0;">
                    {diff_sign}{row['diff']:.2f}
                </div>
                <div class="award-subtext" style="font-size: 0.85rem;">
                    팀: {row['team_value']:.2f}<br>
                    리그: {row['league_value']:.2f}
                </div>
            </div>
            """
            st.markdown(diff_html, unsafe_allow_html=True)
    
    # 4. Auto-generated Summary
    st.markdown('<div class="section-title" style="margin-top: 40px;">📝 패턴 요약</div>', unsafe_allow_html=True)
    
    # Generate summary
    top_zone = zone_df_sorted.iloc[0]
    zone_name = top_zone["zone"]
    diff_val = top_zone["diff"]
    
    if diff_val > 0:
        summary_text = (
            f"**{selected_team}**은(는) **{zone_name}**에서 리그 평균보다 {diff_val:.2f} 높은 {title_suffix}를 보입니다. "
            f"이 Zone에서의 활동이 다른 팀들보다 활발한 편입니다."
        )
    else:
        summary_text = (
            f"**{selected_team}**은(는) **{zone_name}**에서 리그 평균보다 {abs(diff_val):.2f} 낮은 {title_suffix}를 보입니다. "
            f"이 Zone에서의 활동이 다른 팀들보다 상대적으로 적습니다."
        )
    
    # Add second largest difference
    if len(zone_df_sorted) > 1:
        second_zone = zone_df_sorted.iloc[1]
        if second_zone["diff"] > 0:
            summary_text += (
                f" 또한 **{second_zone['zone']}**에서도 리그 평균보다 높은 활동을 보입니다."
            )
        else:
            summary_text += (
                f" 반면 **{second_zone['zone']}**에서는 리그 평균보다 낮은 활동을 보입니다."
            )
    
    summary_html = f"""
    <div class="award-card">
        <div class="award-subtext" style="font-size: 1.1rem; line-height: 1.8;">
            {summary_text}
        </div>
    </div>
    """
    st.markdown(summary_html, unsafe_allow_html=True)
    
    # Data table
    st.markdown('<div class="section-title" style="margin-top: 40px;">📋 상세 데이터</div>', unsafe_allow_html=True)
    
    display_df = zone_df[["zone", "team_value", "league_value", "diff", "diff_pct"]].copy()
    display_df.columns = ["Zone", f"{selected_team}", "리그 평균", "차이", "차이(%)"]
    display_df["차이(%)"] = display_df["차이(%)"].round(1)
    display_df = display_df.sort_values("차이", key=lambda x: x.abs(), ascending=False)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

