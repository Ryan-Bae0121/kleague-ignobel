"""
Methodology Page - Explain awards and methodology (Clean Minimal Style)
"""
import streamlit as st
from src.config import AWARDS
from src.ui_components import inject_custom_css

st.set_page_config(
    page_title="Methodology",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
inject_custom_css()

st.title("📊 Methodology")

st.markdown("""
<div class="award-card" style="padding: 32px; margin-bottom: 32px;">
    <div style="font-size: 1.2rem; color: #c9d1d9; line-height: 1.8;">
        K League 이그노벨상의 계산 방법과 각 상의 정의를 설명합니다.
        <br><br>
        이 서비스는 재미와 인사이트를 위한 것이며, 선수의 실제 실력을 완전히 반영하지 않을 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

# Award Explanations
for award in AWARDS:
    award_card_html = f"""
    <div class="award-card-large" style="margin-bottom: 32px;">
        <div class="award-title-large">
            {award['icon']} {award['title']}
        </div>
        <div style="margin-top: 16px;">
            <span class="badge badge-percentile">{award['category']}</span>
            <span class="badge badge-percentile">최소 {award.get('min_attempts', 0)}회 시도</span>
        </div>
        <div class="award-subtext" style="font-size: 1.1rem; margin-top: 20px; color: #c9d1d9;">
            {award['description']}
        </div>
        <div class="formula-box" style="margin-top: 24px;">
            <strong style="color: #facc15;">공식:</strong> 
            <code style="color: #c9d1d9;">{award['formula']}</code>
        </div>
        <div style="margin-top: 20px; padding: 16px; background: #0e1117; border-radius: 8px; border-left: 4px solid #30363d;">
            <div style="font-size: 0.95rem; color: #8b949e; line-height: 1.6;">
                <strong>계산 방법:</strong> 시즌 전체 이벤트 데이터를 기반으로 선수별 통계를 집계하고, 
                각 지표 값을 계산합니다. 퍼센타일 랭킹을 사용하여 리그 내 상대적 위치를 파악합니다.
            </div>
        </div>
    </div>
    """
    st.markdown(award_card_html, unsafe_allow_html=True)

# General Methodology
st.markdown('<div class="section-title">📈 점수 계산 방법</div>', unsafe_allow_html=True)

methodology_steps = [
    {
        "step": "1",
        "title": "데이터 집계",
        "description": "시즌 전체 이벤트 데이터를 선수/팀별로 집계합니다. 각 수비 행동의 성공/실패, 위치 등을 기록합니다."
    },
    {
        "step": "2",
        "title": "지표 계산",
        "description": "각 상에 해당하는 지표를 계산합니다 (예: 실패율, 비율 등). 최소 시도 횟수 이상인 경우만 평가 대상에 포함합니다."
    },
    {
        "step": "3",
        "title": "점수 및 순위",
        "description": "각 지표 값을 점수로 사용합니다. 높은 점수 = 더 많은 '이그노벨' 요소. 퍼센타일 랭킹으로 리그 내 위치를 확인합니다."
    },
    {
        "step": "4",
        "title": "AI 기반 감지",
        "description": "퍼센타일을 사용하여 극단적인 케이스를 감지합니다. 상위 1-10%에 해당하는 선수/팀을 우선 표시합니다."
    }
]

for step_info in methodology_steps:
    step_html = f"""
    <div class="award-card" style="margin-bottom: 20px;">
        <div style="display: flex; align-items: start;">
            <div style="font-size: 2rem; font-weight: 700; color: #facc15; margin-right: 20px; min-width: 60px;">
                {step_info['step']}
            </div>
            <div>
                <div style="font-size: 1.3rem; font-weight: 600; color: #f8f9fa; margin-bottom: 8px;">
                    {step_info['title']}
                </div>
                <div class="award-subtext">
                    {step_info['description']}
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(step_html, unsafe_allow_html=True)

# 이그노벨 ↔ 공간패턴 연결 논리
st.markdown('<div class="section-title" style="margin-top: 40px;">🎯 이그노벨상과 공간 패턴의 연결</div>', unsafe_allow_html=True)

pattern_connection_html = """
<div class="award-card-large">
    <div class="award-title">공간적 설명이 가능한 이그노벨상</div>
    <div class="award-subtext" style="font-size: 1.1rem; line-height: 1.8; margin-top: 16px;">
        이그노벨상은 단순히 통계만 보여주는 것이 아닙니다. 피치 위에서 "어디서" 일어났는지 보면, 
        <strong>왜 그 선수가 그 상을 받게 되었는지</strong>를 공간적으로 설명할 수 있습니다.
        <br><br>
        <strong>예시:</strong>
        <ul style="margin-top: 12px; padding-left: 20px; color: #c9d1d9;">
            <li><strong>"위험 지역 단골상" 수상자</strong>는 주로 수비 3rd(D-L, D-C, D-R)에서 활동</li>
            <li><strong>"태클은 했지만...상" 수상자</strong>의 태클 위치를 피치맵에서 확인</li>
            <li><strong>"대포알 상" 수상자</strong>의 슛 위치 분포로 패턴 파악</li>
        </ul>
        <br>
        이렇게 <strong>이그노벨상 + 공간 패턴 분석</strong>을 결합하여, 
        단순한 수치가 아닌 <strong>"어디서 무슨 일이 일어났는지"</strong>를 시각적으로 보여줍니다.
    </div>
</div>
"""
st.markdown(pattern_connection_html, unsafe_allow_html=True)

# AI Logic Section
st.markdown('<div class="section-title" style="margin-top: 40px;">🤖 AI 로직</div>', unsafe_allow_html=True)

ai_explanation_html = """
<div class="award-card-large">
    <div class="award-subtext" style="font-size: 1.1rem; line-height: 1.8;">
        이 서비스에서는 <strong style="color: #facc15;">퍼센타일 랭킹</strong>을 사용하여 AI가 자동으로 "이그노벨" 후보를 감지합니다.
        <br><br>
        <strong>퍼센타일:</strong> 리그 내에서 자신보다 점수가 낮은 선수의 비율
        <br>
        <strong>높은 퍼센타일 (예: 95%+):</strong> 리그 상위 5% = 매우 높은 "이그노벨" 점수
        <br>
        <strong>자동 감지:</strong> 상위 퍼센타일에 있는 선수들을 자동으로 추천
    </div>
</div>
"""
st.markdown(ai_explanation_html, unsafe_allow_html=True)

# Data Source
st.markdown('<div class="section-title" style="margin-top: 40px;">📚 데이터 출처</div>', unsafe_allow_html=True)

data_source_html = """
<div class="award-card">
    <div class="award-subtext">
        <strong>데이터:</strong> K League 2024 시즌 이벤트 데이터<br>
        <strong>처리:</strong> Python (pandas, numpy)<br>
        <strong>시각화:</strong> Plotly<br>
        <strong>웹 프레임워크:</strong> Streamlit
    </div>
</div>
"""
st.markdown(data_source_html, unsafe_allow_html=True)

# Disclaimer
st.markdown('<div class="section-title" style="margin-top: 40px;">⚠️ 주의사항</div>', unsafe_allow_html=True)

disclaimer_html = """
<div class="award-card" style="border-left: 4px solid #f85149;">
    <div class="award-subtext" style="color: #8b949e;">
        이 서비스는 <strong>재미와 인사이트</strong>를 위한 것이며, 선수의 실제 실력을 완전히 반영하지 않을 수 있습니다.
        <br><br>
        • 높은 "이그노벨" 점수는 반드시 나쁜 선수를 의미하지 않습니다<br>
        • 데이터 기반 통계일 뿐이며, 상황별 맥락이 다를 수 있습니다<br>
        • 팬 서비스 및 데이터 스토리텔링을 목적으로 합니다
    </div>
</div>
"""
st.markdown(disclaimer_html, unsafe_allow_html=True)
