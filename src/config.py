"""
Award configurations for K League Ignobel Awards
"""

AWARDS = [
    {
        "id": "tackle_fail",
        "title": "태클은 했지만...상",
        "category": "실패율",
        "level": "player",
        "metric": "tackle_fail_rate",
        "direction": "high",
        "icon": "⚔️",
        "description": "태클을 많이 시도하지만 실패율이 높은 선수",
        "formula": "tackle_fail_rate = tackle_fail / tackle_attempt",
        "min_attempts": 5
    },
    {
        "id": "card_per_def",
        "title": "카드만 남겼다상",
        "category": "카드",
        "level": "player",
        "metric": "card_per_def",
        "direction": "high",
        "icon": "🟨",
        "description": "수비 행동 대비 카드를 많이 받는 선수",
        "formula": "card_per_def = card_count / def_actions",
        "min_attempts": 10
    },
    {
        "id": "danger_foul",
        "title": "위험 지역 단골상",
        "category": "파울",
        "level": "player",
        "metric": "danger_foul_ratio",
        "direction": "high",
        "icon": "⚠️",
        "description": "수비 3rd에서 파울을 많이 하는 선수",
        "formula": "danger_foul_ratio = danger_foul_count / foul_count",
        "min_attempts": 3
    },
    {
        "id": "clearance_panic",
        "title": "클리어링 불안상",
        "category": "클리어링",
        "level": "player",
        "metric": "clearance_panic_rate",
        "direction": "high",
        "icon": "😰",
        "description": "클리어링 후 10초 내 상대 슈팅을 허용하는 선수",
        "formula": "clearance_panic_rate = (concede_shot_within_10s) / clearance",
        "min_attempts": 5
    },
    {
        "id": "block_fail",
        "title": "블록은 했는데...상",
        "category": "실패율",
        "level": "player",
        "metric": "block_fail_rate",
        "direction": "high",
        "icon": "🛡️",
        "description": "블록을 많이 시도하지만 실패율이 높은 선수. 실패율이 동일한 선수는 시도 횟수가 많은 순으로 순위가 나열됩니다.",
        "formula": "block_fail_rate = block_fail / block_attempt",
        "min_attempts": 3
    },
    {
        "id": "interception_fail",
        "title": "인터셉트 헛발질상",
        "category": "실패율",
        "level": "player",
        "metric": "interception_fail_rate",
        "direction": "high",
        "icon": "🎯",
        "description": "인터셉트를 많이 시도하지만 실패율이 높은 선수. 실패율이 동일한 선수는 시도 횟수가 많은 순으로 순위가 나열됩니다.",
        "formula": "interception_fail_rate = interception_fail / interception_attempt",
        "min_attempts": 5
    },
    {
        "id": "duel_fail",
        "title": "듀얼은 많은데 지는 상",
        "category": "실패율",
        "level": "player",
        "metric": "duel_fail_rate",
        "direction": "high",
        "icon": "⚔️",
        "description": "듀얼을 많이 시도하지만 실패율이 높은 선수",
        "formula": "duel_fail_rate = duel_fail / duel_attempt",
        "min_attempts": 10
    },
    {
        "id": "def_third_turnover",
        "title": "자기 진영 공 뺏김상",
        "category": "턴오버",
        "level": "player",
        "metric": "def_third_turnover_rate",
        "direction": "high",
        "icon": "🚨",
        "description": "수비 3rd에서 패스/캐리 실패율이 높은 선수",
        "formula": "def_third_turnover_rate = (pass_fail + carry_fail) / (pass + carry) in def_third",
        "min_attempts": 10
    },
    {
        "id": "second_half_drop",
        "title": "후반 집중력 붕괴상",
        "category": "체력",
        "level": "player",
        "metric": "second_half_drop",
        "direction": "high",
        "icon": "📉",
        "description": "후반 수비 실패율이 전반보다 크게 증가한 선수",
        "formula": "second_half_drop = second_half_fail_rate - first_half_fail_rate",
        "min_attempts": 20
    },
    # 공격 이그노벨상
    {
        "id": "cannon_shot",
        "title": "대포알 상",
        "category": "슈팅",
        "level": "player",
        "metric": "off_target_per_game",
        "direction": "high",
        "icon": "💥",
        "description": "슛은 많은데 빗나간 슈팅이 많은 선수",
        "formula": "off_target_per_game = off_target_shots / games",
        "min_attempts": 10
    },
    {
        "id": "chicken_chest",
        "title": "새가슴 상",
        "category": "슈팅",
        "level": "player",
        "metric": "penalty_box_miss_per_game",
        "direction": "high",
        "icon": "🐔",
        "description": "패널티 박스 안에서 슛 실패가 많은 선수",
        "formula": "penalty_box_miss_per_game = penalty_box_miss / games",
        "min_attempts": 5
    },
    {
        "id": "offside_line",
        "title": "선넘네 상",
        "category": "오프사이드",
        "level": "player",
        "metric": "offside_per_game",
        "direction": "high",
        "icon": "🚫",
        "description": "오프사이드를 자주 범하는 선수",
        "formula": "offside_per_game = offsides / games",
        "min_attempts": 1
    },
    {
        "id": "selfish_player",
        "title": "내로남불 상",
        "category": "패스",
        "level": "player",
        "metric": "receive_to_give_ratio",
        "direction": "high",
        "icon": "🤲",
        "description": "패스를 받기만 하고 주지 않는 선수",
        "formula": "receive_to_give_ratio = pass_received / pass_given",
        "min_attempts": 50
    },
    {
        "id": "cross_fail",
        "title": "어디에 줘 상",
        "category": "크로스",
        "level": "player",
        "metric": "cross_fail_per_game",
        "direction": "high",
        "icon": "🎯",
        "description": "크로스는 많은데 성공률이 낮은 선수",
        "formula": "cross_fail_per_game = cross_fail / games",
        "min_attempts": 10
    },
    {
        "id": "duel_loser_attack",
        "title": "지는 게 일상 상",
        "category": "듀얼",
        "level": "player",
        "metric": "duel_fail_per_game_attack",
        "direction": "high",
        "icon": "😢",
        "description": "듀얼 패배가 많은 공격 선수",
        "formula": "duel_fail_per_game = duel_fail / games",
        "min_attempts": 20
    },
    {
        "id": "aerial_fail",
        "title": "키 컸으면 상",
        "category": "공중볼",
        "level": "player",
        "metric": "aerial_fail_per_game",
        "direction": "high",
        "icon": "📏",
        "description": "공격 지역(상대 박스 근처)에서의 헤딩 실패가 많은 선수",
        "formula": "aerial_fail_per_game = heading_fail / games (공격 지역 start_x >= 85에서의 Duel 실패)",
        "min_attempts": 1
    }
]

# Defensive action types
DEF_ACTIONS = [
    "Tackle", "Duel", "Foul", "Interception", "Block", "Clearance",
    "Intervention", "Error", "Aerial Clearance"
]

# Card types
CARD_SET = {"Yellow_Card", "Second_Yellow_Card", "Direct_Red_Card"}

# Foul types
FOUL_TYPES = ["Foul", "Handball_Foul", "Hit"]

# Attack action types
ATTACK_ACTIONS = ["Shot", "Shot_Freekick", "Cross", "Pass", "Pass Received", "Offside", "Duel"]


