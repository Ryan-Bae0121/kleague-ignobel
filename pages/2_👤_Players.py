"""
Players Page - Search, view profiles, and compare players (Magazine Style)
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.io import load_artifact
from src.config import AWARDS
from src.ui_components import (
    inject_custom_css, render_profile_header, render_award_card, 
    render_stat_card, render_small_award_card, render_player_vs_header,
    render_metric_comparison
)
from src.text_templates import generate_player_description

# Load zone activity data
@st.cache_data
def load_zone_activity():
    try:
        return load_artifact("player_zone_activity.parquet")
    except FileNotFoundError:
        return pd.DataFrame()

st.set_page_config(
    page_title="Players | K League 이그노벨상",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
inject_custom_css()

st.title("👤 Players")

# Load data
@st.cache_data
def load_player_data():
    leaderboard = load_artifact("leaderboard.parquet")
    profiles = load_artifact("profiles.parquet")
    return leaderboard, profiles

leaderboard, profiles = load_player_data()
player_zone_activity = load_zone_activity()

# Helper functions
def get_award_info(award_id):
    """Get award config by ID"""
    for award in AWARDS:
        if award["id"] == award_id:
            return award
    return None

def fmt_score(x):
    try:
        return f"{float(x):.2f}"
    except Exception:
        return str(x)

def fmt_pct(p):
    try:
        return f"상위 {100 - float(p):.0f}%" if float(p) >= 0 else "-"
    except Exception:
        return "-"

def pick_top_awards_for_player(df_player: pd.DataFrame, topk=5) -> pd.DataFrame:
    """Pick top K awards by percentile (most extreme)"""
    return df_player.sort_values("percentile", ascending=False).head(topk)

def summarize_comparison(rows):
    """Generate comparison summary"""
    if not rows:
        return "비교할 데이터가 부족합니다."
    # Biggest absolute diff
    r = max(rows, key=lambda d: abs(d["diff"]))
    return (
        f"차이가 가장 큰 항목은 **{r['award_title']}** 입니다. "
        f"이 항목에서는 **{r['worse_name']}** 쪽이 더 '이그노벨' 성향이 강합니다."
    )

# Tabs
tab_profile, tab_compare = st.tabs(["📋 선수 프로필", "⚔️ 선수 비교"])

# ============================================
# Tab 1: Player Profile
# ============================================
with tab_profile:
    # Player search
    col_search, col_results = st.columns([1, 4])

    with col_search:
        st.markdown("### 검색")
        player_search = st.text_input("선수명 또는 팀명", placeholder="예: 아라비제", key="player_search")
        search_by_team = st.checkbox("팀으로 검색", key="search_by_team")

    # Filter players
    if player_search:
        if search_by_team:
            filtered_players = profiles[
                profiles["team_name_ko"].str.contains(player_search, case=False, na=False)
            ]
        else:
            filtered_players = profiles[
                profiles["player_name_ko"].str.contains(player_search, case=False, na=False)
            ]
    else:
        filtered_players = profiles.head(20)

    if len(filtered_players) == 0:
        st.warning("검색 결과가 없습니다.")
    else:
        # Player selection
        player_names = (filtered_players["player_name_ko"] + " (" + filtered_players["team_name_ko"] + ")").tolist()
        selected_player_idx = st.selectbox("선수 선택", range(len(player_names)), 
                                          format_func=lambda x: player_names[x],
                                          key="player_select")

        selected_player = filtered_players.iloc[selected_player_idx]
        player_id = selected_player["player_id"]
        player_name = selected_player["player_name_ko"]
        team_name = selected_player["team_name_ko"]

        with col_results:
            # Player Awards
            player_awards = leaderboard[leaderboard["player_id"] == player_id].sort_values("rank")

            # Generate summary
            if len(player_awards) > 0:
                top_award = player_awards.iloc[0]
                top_award_info = get_award_info(top_award["award_id"])
                summary = f"이번 시즌 {player_name} 선수는 '{top_award_info['title'] if top_award_info else '이그노벨상'}'에서 #{int(top_award['rank'])}위를 기록했습니다. "
                summary += f"총 {len(player_awards)}개의 상에 이름을 올렸으며, 데이터가 말하는 수비 패턴이 눈에 띕니다."
            else:
                summary = f"{player_name} 선수의 이그노벨상 수상 내역을 확인할 수 있습니다."

            # Profile Header
            profile_html = render_profile_header(player_name, team_name, summary)
            st.markdown(profile_html, unsafe_allow_html=True)

            # Quick Stats
            st.markdown('<div class="section-title">📊 주요 통계</div>', unsafe_allow_html=True)

            stats_cols = st.columns(4)
            key_stats = {
                "태클": ("tackle_attempt", "tackle_attempt"),
                "듀얼": ("duel_attempt", "duel_attempt"),
                "파울": ("foul_count", "foul_count"),
                "수비행동": ("def_actions", "def_actions")
            }

            for idx, (stat_name, stat_col) in enumerate(key_stats.items()):
                if stat_col[0] in selected_player.index:
                    value = selected_player[stat_col[0]]
                    with stats_cols[idx]:
                        st.markdown(render_stat_card(
                            f"{value:.0f}" if pd.notna(value) else "0",
                            stat_name
                        ), unsafe_allow_html=True)
            
            # Activity Zones (NEW)
            if len(player_zone_activity) > 0:
                st.markdown('<div class="section-title" style="margin-top: 30px;">📍 주요 활동 존</div>', unsafe_allow_html=True)
                
                player_zones = player_zone_activity[
                    player_zone_activity["player_id"] == player_id
                ].groupby("zone").agg({
                    "event_count": "sum"
                }).reset_index().sort_values("event_count", ascending=False)
                
                if len(player_zones) > 0:
                    top3_zones = player_zones.head(3)
                    zone_cols = st.columns(3)
                    
                    for idx, (_, zone_row) in enumerate(top3_zones.iterrows()):
                        with zone_cols[idx]:
                            zone_html = f"""
                            <div class="award-card" style="padding: 16px; text-align: center;">
                                <div class="award-title" style="font-size: 1.3rem; margin-bottom: 8px;">
                                    {zone_row['zone']}
                                </div>
                                <div class="award-metric" style="font-size: 1.8rem;">
                                    {zone_row['event_count']:.0f}
                                </div>
                                <div class="award-subtext">이벤트 수</div>
                            </div>
                            """
                            st.markdown(zone_html, unsafe_allow_html=True)

            # Awards Timeline
            if len(player_awards) > 0:
                st.markdown('<div class="section-title">🏆 수상 내역</div>', unsafe_allow_html=True)

                # Top 3 Awards
                top3 = player_awards[player_awards["rank"] <= 3].head(3)
                if len(top3) > 0:
                    top3_cols = st.columns(len(top3))
                    for idx, (_, award_row) in enumerate(top3.iterrows()):
                        with top3_cols[idx]:
                            award_info = get_award_info(award_row["award_id"])
                            if award_info:
                                card_html = render_award_card(
                                    award_icon=award_info.get("icon", "🏆"),
                                    award_title=award_info["title"],
                                    player_name=player_name,
                                    team_name=team_name,
                                    metric_value=award_row["score"],
                                    metric_label="점수",
                                    rank=int(award_row["rank"]),
                                    percentile=award_row.get("percentile"),
                                    description=award_info["description"],
                                    is_large=False
                                )
                                st.markdown(card_html, unsafe_allow_html=True)

                # All Awards List
                st.markdown('<div class="section-title" style="margin-top: 40px;">📋 전체 수상 내역</div>', unsafe_allow_html=True)

                rows = (len(player_awards) + 1) // 2
                for i in range(rows):
                    cols = st.columns(2)
                    for j in range(2):
                        idx = i * 2 + j
                        if idx < len(player_awards):
                            with cols[j]:
                                award_row = player_awards.iloc[idx]
                                award_info = get_award_info(award_row["award_id"])
                                if award_info:
                                    card_html = render_small_award_card(
                                        award_icon=award_info.get("icon", "🏆"),
                                        award_title=award_info["title"],
                                        player_name=player_name,
                                        team_name=team_name,
                                        rank=int(award_row["rank"]),
                                        score=award_row["score"]
                                    )
                                    st.markdown(card_html, unsafe_allow_html=True)

                # Detailed Description
                st.markdown('<div class="section-title" style="margin-top: 40px;">📝 상세 분석</div>', unsafe_allow_html=True)

                selected_award_for_detail = st.selectbox(
                    "자세히 볼 상 선택",
                    player_awards["award_id"].tolist(),
                    format_func=lambda x: next((a["title"] for a in AWARDS if a["id"] == x), x),
                    key="detail_award"
                )

                award_detail = player_awards[player_awards["award_id"] == selected_award_for_detail].iloc[0]
                player_stats = selected_player.to_dict()

                description = generate_player_description(
                    player_name,
                    team_name,
                    selected_award_for_detail,
                    award_detail["score"],
                    int(award_detail["rank"]),
                    award_detail["percentile"],
                    player_stats
                )

                description_html = f"""
                <div class="award-card">
                    <div class="award-subtext" style="font-size: 1rem; line-height: 1.8;">
                        {description.replace(chr(10), '<br>')}
                    </div>
                </div>
                """
                st.markdown(description_html, unsafe_allow_html=True)
            else:
                st.info("이 선수는 아직 수상 내역이 없습니다.")

# ============================================
# Tab 2: Player Comparison
# ============================================
with tab_compare:
    st.markdown(
        """
        <div class="award-card">
            <div class="award-title">⚔️ 선수 비교</div>
            <div class="award-subtext">
                두 선수를 선택하면, 각 이그노벨상(지표)에서 누가 더 '극단적인지(퍼센타일)'를 비교합니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Player selection
    players = sorted(leaderboard["player_name_ko"].dropna().unique().tolist())
    c1, c2 = st.columns(2)

    with c1:
        p1 = st.selectbox("선수 A", players, index=0, key="compare_p1")
    with c2:
        default_idx = 1 if len(players) > 1 else 0
        p2 = st.selectbox("선수 B", players, index=default_idx, key="compare_p2")

    if p1 == p2:
        st.warning("서로 다른 두 선수를 선택해 주세요.")
    else:
        df1 = leaderboard[leaderboard["player_name_ko"] == p1].copy()
        df2 = leaderboard[leaderboard["player_name_ko"] == p2].copy()

        # Get team names
        team1 = df1["team_name_ko"].iloc[0] if len(df1) > 0 else None
        team2 = df2["team_name_ko"].iloc[0] if len(df2) > 0 else None

        # Header Card
        header_html = render_player_vs_header(p1, team1, p2, team2)
        st.markdown(header_html, unsafe_allow_html=True)

        # Build comparison table
        a1 = df1[["award_id", "score", "percentile", "rank"]].rename(
            columns={"score": "score_1", "percentile": "pctl_1", "rank": "rank_1"}
        )
        a2 = df2[["award_id", "score", "percentile", "rank"]].rename(
            columns={"score": "score_2", "percentile": "pctl_2", "rank": "rank_2"}
        )

        comp = pd.merge(a1, a2, on="award_id", how="outer")
        comp["pctl_1"] = comp["pctl_1"].fillna(0)
        comp["pctl_2"] = comp["pctl_2"].fillna(0)
        comp["score_1"] = comp["score_1"].fillna(0)
        comp["score_2"] = comp["score_2"].fillna(0)
        comp["rank_1"] = comp["rank_1"].fillna(999)
        comp["rank_2"] = comp["rank_2"].fillna(999)
        comp["diff"] = comp["pctl_1"] - comp["pctl_2"]

        # Add award titles
        comp["award_title"] = comp["award_id"].apply(lambda x: get_award_info(x)["title"] if get_award_info(x) else x)
        comp["award_icon"] = comp["award_id"].apply(lambda x: get_award_info(x).get("icon", "🏆") if get_award_info(x) else "🏆")

        # Comparison mode selection
        st.markdown('<div class="section-title">📊 비교 모드</div>', unsafe_allow_html=True)
        
        comparison_mode = st.radio(
            "비교 방식",
            ["차이 큰 항목 자동 추천", "수비 5개 핵심 항목"],
            horizontal=True,
            key="compare_mode"
        )

        if comparison_mode == "차이 큰 항목 자동 추천":
            topN = st.slider("비교에 표시할 주요 항목 개수", 3, 12, 6, step=1, key="topn_auto")
            show = comp.sort_values("diff", key=lambda s: s.abs(), ascending=False).head(topN)
        else:
            # 수비 5개 핵심 항목
            core_defensive_awards = ["tackle_fail", "duel_fail", "danger_foul", "def_third_turnover", "second_half_drop"]
            show = comp[comp["award_id"].isin(core_defensive_awards)]
            if len(show) == 0:
                st.info("핵심 수비 항목 데이터가 없습니다.")
                show = comp.head(5)

        # Render comparison cards
        st.markdown('<div class="section-title">⚔️ 상별 비교</div>', unsafe_allow_html=True)
        
        rows_for_summary = []
        for _, r in show.iterrows():
            if r["diff"] > 3:
                worse = "right"  # player 2 is worse (player 1 has higher percentile)
                worse_name = p2
            elif r["diff"] < -3:
                worse = "left"  # player 1 is worse
                worse_name = p1
            else:
                worse = "tie"
                worse_name = "두 선수 비슷"

            rows_for_summary.append({
                "award_title": r["award_title"],
                "p1_pct": r["pctl_1"],
                "p2_pct": r["pctl_2"],
                "diff": r["diff"],
                "worse_name": worse_name,
            })

            metric_html = render_metric_comparison(
                award_title=r["award_title"],
                award_icon=r["award_icon"],
                player1_score=r["score_1"],
                player1_percentile=r["pctl_1"],
                player1_rank=int(r["rank_1"]) if r["rank_1"] < 999 else 999,
                player2_score=r["score_2"],
                player2_percentile=r["pctl_2"],
                player2_rank=int(r["rank_2"]) if r["rank_2"] < 999 else 999,
                worse_side=worse
            )
            st.markdown(metric_html, unsafe_allow_html=True)

        # Story summary
        st.markdown('<div class="section-title">📝 비교 요약</div>', unsafe_allow_html=True)
        
        summary_html = f"""
        <div class="award-card">
            <div class="award-title">분석 결과</div>
            <div class="award-subtext" style="font-size: 1.1rem; line-height: 1.8;">
                {summarize_comparison(rows_for_summary)}
            </div>
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #30363d;">
                <div class="award-subtext" style="font-size: 0.9rem; color: #8b949e;">
                    💡 <strong>팁:</strong> 퍼센타일이 높을수록(100에 가까울수록) 리그에서 더 '극단적인' 패턴입니다.
                    점수(score)는 상별 정의에 따라 단위가 다를 수 있으니, 비교는 퍼센타일 중심으로 보세요.
                </div>
            </div>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

        # Each player's top awards snapshot
        st.markdown('<div class="section-title" style="margin-top: 40px;">🔥 각 선수의 TOP 5</div>', unsafe_allow_html=True)
        
        left, right = st.columns(2)

        with left:
            top5_p1 = pick_top_awards_for_player(df1, topk=5)
            st.markdown(f'<div class="award-card"><div class="award-title">{p1}</div>', unsafe_allow_html=True)
            for _, r in top5_p1.iterrows():
                award_info = get_award_info(r["award_id"])
                if award_info:
                    rank_emoji = "🥇" if r["rank"] == 1 else "🥈" if r["rank"] == 2 else "🥉" if r["rank"] == 3 else f"#{int(r['rank'])}"
                    st.markdown(
                        f"""
                        <div style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #30363d;">
                            <div style="font-weight: 600; color: #f8f9fa; margin-bottom: 4px;">
                                {award_info.get('icon', '🏆')} {award_info['title']}
                            </div>
                            <div style="font-size: 0.9rem; color: #8b949e;">
                                <span class="badge badge-rank">{rank_emoji}</span>
                                점수: {fmt_score(r['score'])} · {fmt_pct(r['percentile'])}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            top5_p2 = pick_top_awards_for_player(df2, topk=5)
            st.markdown(f'<div class="award-card"><div class="award-title">{p2}</div>', unsafe_allow_html=True)
            for _, r in top5_p2.iterrows():
                award_info = get_award_info(r["award_id"])
                if award_info:
                    rank_emoji = "🥇" if r["rank"] == 1 else "🥈" if r["rank"] == 2 else "🥉" if r["rank"] == 3 else f"#{int(r['rank'])}"
                    st.markdown(
                        f"""
                        <div style="margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #30363d;">
                            <div style="font-weight: 600; color: #f8f9fa; margin-bottom: 4px;">
                                {award_info.get('icon', '🏆')} {award_info['title']}
                            </div>
                            <div style="font-size: 0.9rem; color: #8b949e;">
                                <span class="badge badge-rank">{rank_emoji}</span>
                                점수: {fmt_score(r['score'])} · {fmt_pct(r['percentile'])}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            st.markdown("</div>", unsafe_allow_html=True)
