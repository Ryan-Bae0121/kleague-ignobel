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

# Sidebar toggle button
render_sidebar_toggle()

# 페이지 로드 시 스크롤을 맨 위로 이동 (더 강력한 방법 - 항상 실행)
st.markdown("""
<script>
(function() {
    function scrollToTop() {
        // 모든 가능한 스크롤 요소 처리
        window.scrollTo({top: 0, left: 0, behavior: 'instant'});
        if (window.scrollTo) window.scrollTo(0, 0);
        
        // 문서 레벨 스크롤
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
        if (document.documentElement) document.documentElement.scrollTop = 0;
        if (document.body) document.body.scrollTop = 0;
        
        // Streamlit main 컨테이너 스크롤
        const mainElements = document.querySelectorAll('.main, [data-testid="stAppViewContainer"], .block-container');
        mainElements.forEach(el => {
            if (el && el.scrollTop !== undefined) {
                el.scrollTop = 0;
            }
        });
        
        // iframe 내부의 경우 parent도 처리
        try {
            if (window.parent && window.parent !== window) {
                window.parent.scrollTo(0, 0);
                if (window.parent.document && window.parent.document.body) {
                    window.parent.document.body.scrollTop = 0;
                }
            }
        } catch (e) {
            // Cross-origin 에러 무시
        }
    }
    
    // 즉시 실행
    scrollToTop();
    
    // DOM 로드 후
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', scrollToTop);
    }
    
    // Window load 후
    window.addEventListener('load', scrollToTop);
    
    // 여러 시점에서 반복 실행 (Streamlit 렌더링 지연 고려)
    [10, 50, 100, 200, 300, 500, 800, 1000, 1500, 2000].forEach(delay => {
        setTimeout(scrollToTop, delay);
    });
    
    // MutationObserver로 DOM 변경 감지 시에도 스크롤
    const observer = new MutationObserver(function() {
        scrollToTop();
    });
    
    if (document.body) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // 일정 시간 후 observer 해제 (성능 고려)
    setTimeout(function() {
        observer.disconnect();
    }, 3000);
})();
</script>
""", unsafe_allow_html=True)

st.title("🏆 Awards")

# Load data
@st.cache_data(ttl=0)  # Disable cache during development
def load_award_data():
    leaderboard = load_artifact("leaderboard.parquet")
    profiles = load_artifact("profiles.parquet")
    return leaderboard, profiles

leaderboard, profiles = load_award_data()

# Check for award_id in session state (from home page navigation) or query params
award_id_from_session = st.session_state.get("selected_award_id", None)
query_params = st.query_params
award_id_from_url = query_params.get("award_id", None)
award_id_to_select = award_id_from_session or award_id_from_url

# Filters - Left Sidebar Style
col_filter, col_main = st.columns([1, 4])

with col_filter:
    st.markdown("### 필터")
    
    categories = ["전체"] + list(set(a["category"] for a in AWARDS))
    
    # If award_id is set (from session or URL), find its category to pre-select
    default_category = "전체"
    if award_id_to_select:
        for award in AWARDS:
            if award["id"] == award_id_to_select:
                default_category = award["category"]
                break
    
    selected_category = st.selectbox("카테고리", categories, 
                                    index=categories.index(default_category) if default_category in categories else 0,
                                    key="category_filter")
    
    if selected_category == "전체":
        available_awards = AWARDS
    else:
        available_awards = [a for a in AWARDS if a["category"] == selected_category]
    
    award_titles = [f"{a['icon']} {a['title']}" for a in available_awards]
    
    # Find default award index based on session state or URL parameter
    default_award_idx = 0
    if award_id_to_select:
        for idx, award in enumerate(available_awards):
            if award["id"] == award_id_to_select:
                default_award_idx = idx
                break
    
    selected_award_idx = st.selectbox("상 선택", range(len(award_titles)), 
                                     index=default_award_idx,
                                     format_func=lambda x: award_titles[x],
                                     key="award_select")

selected_award = available_awards[selected_award_idx]
selected_award_id = selected_award["id"]

# Clear session state after using it to avoid conflicts
if award_id_from_session and award_id_from_session == selected_award_id:
    if "selected_award_id" in st.session_state:
        del st.session_state.selected_award_id

# Filter leaderboard
award_data = leaderboard[leaderboard["award_id"] == selected_award_id].copy()

if len(award_data) == 0:
    st.warning("선택한 상에 대한 데이터가 없습니다.")
else:
    with col_main:
        # Award Info Card
        description = selected_award['description']
        # Add special note for interception_fail and block_fail awards
        if selected_award_id in ["interception_fail", "block_fail"]:
            description += "<br><small style='color: #8b949e; font-style: italic;'>※ 실패율이 동일한 선수는 시도 횟수가 많은 순으로 순위가 나열됩니다.</small>"
        
        award_info_html = f"""
        <div class="award-card-large">
            <div class="award-title-large">
                <span class="award-icon">{selected_award['icon']}</span> <span class="award-title-text">{selected_award['title']}</span>
            </div>
            <div class="award-subtext" style="font-size: 1.1rem; margin-top: 16px;">
                {description}
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
                        
                        # Get attempt count for interception_fail and block_fail awards
                        attempt_info = ""
                        if selected_award_id == "interception_fail":
                            player_profile = profiles[profiles["player_id"] == row["player_id"]]
                            if len(player_profile) > 0 and "interception_attempt" in player_profile.columns:
                                attempt_count = player_profile.iloc[0]["interception_attempt"]
                                if pd.notna(attempt_count):
                                    attempt_info = f'<div style="font-size: 0.8rem; color: #8b949e; margin-top: 4px;">시도: {int(attempt_count)}회</div>'
                        elif selected_award_id == "block_fail":
                            player_profile = profiles[profiles["player_id"] == row["player_id"]]
                            if len(player_profile) > 0 and "block_attempt" in player_profile.columns:
                                attempt_count = player_profile.iloc[0]["block_attempt"]
                                if pd.notna(attempt_count):
                                    attempt_info = f'<div style="font-size: 0.8rem; color: #8b949e; margin-top: 4px;">시도: {int(attempt_count)}회</div>'
                        
                        card_html = render_small_award_card(
                            award_icon=selected_award.get("icon", "🏆"),
                            award_title=selected_award["title"],
                            player_name=row["player_name_ko"],
                            team_name=row["team_name_ko"],
                            rank=int(row["rank"]),
                            score=row["score"],
                            show_logo=True,
                            extra_info=attempt_info
                        )
                        st.markdown(card_html, unsafe_allow_html=True)
        
        # Distribution (Secondary - Collapsible)
        with st.expander("📈 점수 분포 보기", expanded=False):
            dist_fig = plot_award_distribution(award_data, selected_award_id, selected_award["title"])
            st.plotly_chart(dist_fig, use_container_width=True)
