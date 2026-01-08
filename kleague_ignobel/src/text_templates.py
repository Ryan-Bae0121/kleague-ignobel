"""
Text generation templates for award descriptions
"""
from .config import AWARDS


def get_award_info(award_id: str) -> dict:
    """Get award configuration by ID"""
    for award in AWARDS:
        if award["id"] == award_id:
            return award
    return None


def generate_player_description(player_name: str, team_name: str, award_id: str, 
                                score: float, rank: int, percentile: float, 
                                stats: dict = None) -> str:
    """
    Generate description text for a player's award
    """
    award_info = get_award_info(award_id)
    if not award_info:
        return f"{player_name} 선수가 수상했습니다!"
    
    award_title = award_info["title"]
    icon = award_info.get("icon", "🏆")
    
    # Base message
    if rank == 1:
        rank_text = "🥇 1위"
    elif rank == 2:
        rank_text = "🥈 2위"
    elif rank == 3:
        rank_text = "🥉 3위"
    else:
        rank_text = f"#{rank}위"
    
    message = f"{icon} **{award_title}** {rank_text}\n\n"
    message += f"{player_name} ({team_name}) 선수는 {award_title}에서 "
    message += f"점수 {score:.3f}을 기록하여 상위 {percentile:.1f}%에 위치했습니다.\n\n"
    message += f"**설명**: {award_info['description']}\n\n"
    message += f"**공식**: `{award_info['formula']}`"
    
    # Add specific stats if available
    if stats:
        if award_id == "tackle_fail" and "tackle_attempt" in stats:
            message += f"\n\n태클 시도: {stats.get('tackle_attempt', 0):.0f}회, 실패: {stats.get('tackle_fail', 0):.0f}회"
        elif award_id == "card_per_def" and "card_count" in stats:
            message += f"\n\n수비 행동: {stats.get('def_actions', 0):.0f}회, 카드: {stats.get('card_count', 0):.0f}장"
        elif award_id == "danger_foul" and "foul_count" in stats:
            message += f"\n\n전체 파울: {stats.get('foul_count', 0):.0f}회, 수비3rd 파울: {stats.get('danger_foul_count', 0):.0f}회"
    
    return message


def generate_award_card_html(player_name: str, team_name: str, award_id: str,
                             score: float, rank: int) -> str:
    """
    Generate HTML card for award display
    """
    award_info = get_award_info(award_id)
    if not award_info:
        return ""
    
    icon = award_info.get("icon", "🏆")
    title = award_info["title"]
    
    # Rank emoji
    if rank == 1:
        rank_emoji = "🥇"
    elif rank == 2:
        rank_emoji = "🥈"
    elif rank == 3:
        rank_emoji = "🥉"
    else:
        rank_emoji = f"#{rank}"
    
    html = f"""
    <div style="
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    ">
        <h3 style="margin: 0; color: #2c3e50;">
            {icon} {title} {rank_emoji}
        </h3>
        <p style="font-size: 18px; margin: 10px 0; color: #34495e;">
            <strong>{player_name}</strong> ({team_name})
        </p>
        <p style="font-size: 14px; color: #7f8c8d;">
            Score: {score:.3f}
        </p>
    </div>
    """
    return html


