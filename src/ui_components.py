"""
Reusable UI components for sports magazine style Streamlit app
"""
import streamlit as st


def inject_custom_css():
    """Inject custom dark theme CSS"""
    st.markdown("""
    <style>
        /* Dark Theme Base */
        .stApp {
            background-color: #0e1117;
        }
        
        /* Sidebar: Always keep expanded */
        [data-testid="stSidebar"] {
            position: fixed !important;
            left: 0;
            top: 0;
            height: 100vh;
            z-index: 100;
            visibility: visible !important;
            margin-left: 0 !important;
        }
        
        [data-testid="stMainContainer"] {
            margin-left: 300px;
        }
        
        /* Sidebar styling - keep visible */
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Typography */
        h1, h2, h3 {
            color: #f8f9fa !important;
            font-weight: 700;
        }
        
        /* Card Styles */
        .award-card {
            background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
            border: 1px solid #30363d;
            border-radius: 20px;
            padding: 24px;
            margin: 16px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .award-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
            border-color: #facc15;
        }
        
        .award-card-large {
            background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
            border: 2px solid #30363d;
            border-radius: 24px;
            padding: 32px;
            margin: 20px 0;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        }
        
        .award-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #facc15;
            margin-bottom: 12px;
        }
        
        .award-title-large {
            font-size: 2rem;
            font-weight: 700;
            color: #facc15;
            margin-bottom: 16px;
        }
        
        .award-player {
            font-size: 1.25rem;
            font-weight: 600;
            color: #f8f9fa;
            margin: 8px 0;
        }
        
        .award-team {
            font-size: 1rem;
            color: #8b949e;
            margin-bottom: 16px;
        }
        
        .award-metric {
            font-size: 3rem;
            font-weight: 800;
            color: #facc15;
            margin: 16px 0;
            line-height: 1;
        }
        
        .award-metric-label {
            font-size: 0.9rem;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        }
        
        .award-subtext {
            font-size: 0.95rem;
            color: #c9d1d9;
            margin-top: 12px;
            line-height: 1.6;
        }
        
        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 700;
            margin-right: 8px;
        }
        
        .badge-rank-1 {
            background: linear-gradient(135deg, #facc15 0%, #eab308 100%);
            color: #0e1117;
        }
        
        .badge-rank-2 {
            background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
            color: #ffffff;
        }
        
        .badge-rank-3 {
            background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
            color: #ffffff;
        }
        
        .badge-rank {
            background: #30363d;
            color: #f8f9fa;
        }
        
        .badge-percentile {
            background: #21262d;
            color: #58a6ff;
            border: 1px solid #30363d;
        }
        
        /* Hero Section */
        .hero-section {
            text-align: center;
            padding: 60px 20px 40px;
            background: linear-gradient(180deg, #0e1117 0%, #161b22 100%);
            border-bottom: 2px solid #30363d;
            margin-bottom: 40px;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 900;
            color: #facc15;
            margin-bottom: 16px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        .hero-subtitle {
            font-size: 1.3rem;
            color: #8b949e;
            max-width: 800px;
            margin: 0 auto;
            line-height: 1.8;
        }
        
        /* Profile Section */
        .profile-header {
            background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
            border-radius: 24px;
            padding: 40px;
            margin-bottom: 32px;
            border: 2px solid #30363d;
        }
        
        .profile-name {
            font-size: 2.5rem;
            font-weight: 800;
            color: #f8f9fa;
            margin-bottom: 8px;
        }
        
        .profile-team {
            font-size: 1.3rem;
            color: #8b949e;
            margin-bottom: 24px;
        }
        
        .profile-summary {
            font-size: 1.1rem;
            color: #c9d1d9;
            line-height: 1.8;
            padding: 20px;
            background: #0e1117;
            border-radius: 12px;
            border-left: 4px solid #facc15;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }
        
        .stat-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #facc15;
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Comparison Card */
        .comparison-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 16px;
            padding: 20px;
            margin: 12px 0;
        }
        
        .comparison-label {
            font-size: 0.85rem;
            color: #8b949e;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        
        .comparison-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #f8f9fa;
        }
        
        .comparison-diff {
            font-size: 0.9rem;
            margin-top: 4px;
        }
        
        .comparison-diff.positive {
            color: #3fb950;
        }
        
        .comparison-diff.negative {
            color: #f85149;
        }
        
        /* Expandable Section */
        .expandable {
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #30363d;
        }
        
        .expandable-content {
            font-size: 0.9rem;
            color: #8b949e;
            line-height: 1.6;
        }
        
        /* Section Title */
        .section-title {
            font-size: 2rem;
            font-weight: 700;
            color: #f8f9fa;
            margin: 40px 0 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid #30363d;
        }
        
        /* Formula Box */
        .formula-box {
            background: #0e1117;
            border: 1px solid #30363d;
            border-left: 4px solid #facc15;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            font-family: 'Courier New', monospace;
            color: #c9d1d9;
        }
        
        /* Comparison colors */
        .worse {
            color: #f85149 !important;
            font-weight: 800;
        }
        
        .better {
            color: #3fb950 !important;
            font-weight: 800;
        }
        
        .neutral {
            color: #8b949e !important;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)


def render_award_card(award_icon: str, award_title: str, player_name: str, 
                     team_name: str, metric_value: float, metric_label: str,
                     rank: int, percentile: float = None, description: str = None,
                     is_large: bool = False):
    """Render a single award card"""
    rank_emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
    rank_class = "badge-rank-1" if rank == 1 else "badge-rank-2" if rank == 2 else "badge-rank-3" if rank == 3 else "badge-rank"
    
    title_class = "award-title-large" if is_large else "award-title"
    card_class = "award-card-large" if is_large else "award-card"
    
    percentile_html = ""
    if percentile is not None:
        percentile_html = f'<span class="badge badge-percentile">상위 {percentile:.1f}%</span>'
    
    description_html = ""
    if description:
        description_html = f'<div class="award-subtext">{description}</div>'
    
    html = f"""
    <div class="{card_class}">
        <div class="{title_class}">
            {award_icon} {award_title}
        </div>
        <div class="award-player">{player_name}</div>
        <div class="award-team">{team_name}</div>
        <div class="award-metric">{metric_value:.3f}</div>
        <div class="award-metric-label">{metric_label}</div>
        <div style="margin-top: 16px;">
            <span class="badge {rank_class}">{rank_emoji}</span>
            {percentile_html}
        </div>
        {description_html}
    </div>
    """
    return html


def render_small_award_card(award_icon: str, award_title: str, player_name: str,
                           team_name: str, rank: int, score: float):
    """Render a compact award card for lists"""
    rank_emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
    
    html = f"""
    <div class="award-card" style="padding: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <div style="font-size: 1.1rem; color: #facc15; font-weight: 600; margin-bottom: 4px;">
                    {award_icon} {award_title}
                </div>
                <div style="font-size: 1rem; color: #f8f9fa; font-weight: 500;">
                    {player_name}
                </div>
                <div style="font-size: 0.85rem; color: #8b949e; margin-top: 4px;">
                    {team_name}
                </div>
            </div>
            <div style="text-align: right;">
                <div class="badge badge-rank" style="font-size: 1.1rem; padding: 8px 16px;">
                    {rank_emoji}
                </div>
                <div style="font-size: 1.2rem; color: #facc15; font-weight: 700; margin-top: 8px;">
                    {score:.3f}
                </div>
            </div>
        </div>
    </div>
    """
    return html


def render_hero_section(title: str, subtitle: str):
    """Render hero section for home page"""
    html = f"""
    <div class="hero-section">
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """
    return html


def render_profile_header(player_name: str, team_name: str, summary: str):
    """Render player profile header"""
    html = f"""
    <div class="profile-header">
        <div class="profile-name">{player_name}</div>
        <div class="profile-team">{team_name}</div>
        <div class="profile-summary">{summary}</div>
    </div>
    """
    return html


def render_stat_card(value: str, label: str):
    """Render a single stat card"""
    html = f"""
    <div class="stat-card">
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """
    return html


def render_comparison_card(label: str, team_value: float, league_value: float, unit: str = ""):
    """Render team vs league comparison card"""
    diff = team_value - league_value
    diff_class = "positive" if diff > 0 else "negative"
    diff_sign = "+" if diff > 0 else ""
    
    html = f"""
    <div class="comparison-card">
        <div class="comparison-label">{label}</div>
        <div class="comparison-value">{team_value:.3f}{unit}</div>
        <div style="font-size: 0.85rem; color: #8b949e; margin-top: 8px;">
            리그 평균: {league_value:.3f}{unit}
        </div>
        <div class="comparison-diff {diff_class}">
            {diff_sign}{diff:.3f}{unit}
        </div>
    </div>
    """
    return html


def render_player_vs_header(player1_name: str, player1_team: str, 
                            player2_name: str, player2_team: str):
    """Render player vs player header card"""
    html = f"""
    <div class="award-card-large" style="text-align: center; padding: 40px;">
        <div style="display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 20px;">
            <div>
                <div class="award-player" style="font-size: 1.5rem; margin-bottom: 8px;">
                    {player1_name}
                </div>
                <div class="award-team" style="font-size: 1rem;">
                    {player1_team if player1_team else ""}
                </div>
            </div>
            <div style="font-size: 2rem; font-weight: 900; color: #facc15;">
                ⚔️
            </div>
            <div>
                <div class="award-player" style="font-size: 1.5rem; margin-bottom: 8px;">
                    {player2_name}
                </div>
                <div class="award-team" style="font-size: 1rem;">
                    {player2_team if player2_team else ""}
                </div>
            </div>
        </div>
    </div>
    """
    return html


def render_metric_comparison(award_title: str, award_icon: str,
                            player1_score: float, player1_percentile: float, player1_rank: int,
                            player2_score: float, player2_percentile: float, player2_rank: int,
                            worse_side: str = "tie"):
    """Render metric comparison card for two players"""
    # Determine colors
    if worse_side == "left":
        left_class = "worse"
        right_class = "better"
    elif worse_side == "right":
        left_class = "better"
        right_class = "worse"
    else:
        left_class = "neutral"
        right_class = "neutral"
    
    # Rank badges
    rank1_emoji = "🥇" if player1_rank == 1 else "🥈" if player1_rank == 2 else "🥉" if player1_rank == 3 else f"#{player1_rank}"
    rank2_emoji = "🥇" if player2_rank == 1 else "🥈" if player2_rank == 2 else "🥉" if player2_rank == 3 else f"#{player2_rank}"
    
    rank1_class = "badge-rank-1" if player1_rank == 1 else "badge-rank-2" if player1_rank == 2 else "badge-rank-3" if player1_rank == 3 else "badge-rank"
    rank2_class = "badge-rank-2" if player2_rank == 1 else "badge-rank-2" if player2_rank == 2 else "badge-rank-3" if player2_rank == 3 else "badge-rank"
    
    html = f"""
    <div class="award-card" style="margin-bottom: 20px;">
        <div class="award-title" style="margin-bottom: 20px; text-align: center;">
            {award_icon} {award_title}
        </div>
        <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 20px; align-items: center;">
            <div style="text-align: center;">
                <div class="award-metric {left_class}" style="font-size: 2.5rem;">
                    {player1_score:.3f}
                </div>
                <div style="margin-top: 12px;">
                    <span class="badge {rank1_class}">{rank1_emoji}</span>
                    <span class="badge badge-percentile">상위 {player1_percentile:.0f}%</span>
                </div>
                <div class="award-subtext" style="margin-top: 8px; font-size: 0.9rem;">
                    점수: {player1_score:.3f}
                </div>
            </div>
            <div style="text-align: center; font-size: 1.5rem; color: #8b949e; font-weight: 700;">
                vs
            </div>
            <div style="text-align: center;">
                <div class="award-metric {right_class}" style="font-size: 2.5rem;">
                    {player2_score:.3f}
                </div>
                <div style="margin-top: 12px;">
                    <span class="badge {rank2_class}">{rank2_emoji}</span>
                    <span class="badge badge-percentile">상위 {player2_percentile:.0f}%</span>
                </div>
                <div class="award-subtext" style="margin-top: 8px; font-size: 0.9rem;">
                    점수: {player2_score:.3f}
                </div>
            </div>
        </div>
    </div>
    """
    return html

