"""
Awards Page - Browse and filter awards (Magazine Style)
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.io import load_artifact
from src.config import AWARDS
from src.viz import plot_award_distribution
from src.ui_components import inject_custom_css, render_award_card, render_small_award_card, render_sidebar_toggle

st.set_page_config(
    page_title="Awards",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
inject_custom_css()

# Render sidebar toggle
render_sidebar_toggle()

st.title("🏆 Awards")

# Load data
@st.cache_data
def load_award_data():
    leaderboard = load_artifact("leaderboard.parquet")
    return leaderboard

leaderboard = load_award_data()

# Filters - Left Sidebar Style
col_filter, col_main = st.columns([1, 4])

with col_filter:
    st.markdown("### 필터")
    
    categories = ["전체"] + list(set(a["category"] for a in AWARDS))
    selected_category = st.selectbox("카테고리", categories, key="category_filter")
    
    if selected_category == "전체":
        available_awards = AWARDS
    else:
        available_awards = [a for a in AWARDS if a["category"] == selected_category]
    
    award_titles = [f"{a['icon']} {a['title']}" for a in available_awards]
    selected_award_idx = st.selectbox("상 선택", range(len(award_titles)), 
                                     format_func=lambda x: award_titles[x],
                                     key="award_select")

selected_award = available_awards[selected_award_idx]
selected_award_id = selected_award["id"]

# Filter leaderboard
award_data = leaderboard[leaderboard["award_id"] == selected_award_id].copy()

if len(award_data) == 0:
    st.warning("선택한 상에 대한 데이터가 없습니다.")
else:
    with col_main:
        # Award Info Card
        award_info_html = f"""
        <div class="award-card-large">
            <div class="award-title-large">
                {selected_award['icon']} {selected_award['title']}
            </div>
            <div class="award-subtext" style="font-size: 1.1rem; margin-top: 16px;">
                {selected_award['description']}
            </div>
            <div class="formula-box" style="margin-top: 20px;">
                <strong>공식:</strong> {selected_award['formula']}
            </div>
        </div>
        """
        st.markdown(award_info_html, unsafe_allow_html=True)
        
        # Top Rankings
        st.markdown('<div class="section-title">📊 랭킹</div>', unsafe_allow_html=True)
        
        top_n = st.slider("표시할 인원", 5, 30, 10, key="top_n_slider")
        top_data = award_data.nsmallest(top_n, "rank").sort_values("rank")
        
        # Display as 2-column card grid
        rows = (len(top_data) + 1) // 2
        for i in range(rows):
            cols = st.columns(2)
            for j in range(2):
                idx = i * 2 + j
                if idx < len(top_data):
                    with cols[j]:
                        row = top_data.iloc[idx]
                        card_html = render_small_award_card(
                            award_icon=selected_award.get("icon", "🏆"),
                            award_title=selected_award["title"],
                            player_name=row["player_name_ko"],
                            team_name=row["team_name_ko"],
                            rank=int(row["rank"]),
                            score=row["score"]
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
        
        # Distribution (Secondary - Collapsible)
        with st.expander("📈 점수 분포 보기", expanded=False):
            dist_fig = plot_award_distribution(award_data, selected_award_id, selected_award["title"])
            st.plotly_chart(dist_fig, use_container_width=True)
