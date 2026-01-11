"""
Image utilities for K League logos and player photos
"""
import streamlit as st
from pathlib import Path
import requests
from typing import Optional
import pandas as pd

# Image directories
PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / "images"
LOGOS_DIR = IMAGES_DIR / "logos"
PLAYERS_DIR = IMAGES_DIR / "players"

# Create directories if they don't exist
IMAGES_DIR.mkdir(exist_ok=True)
LOGOS_DIR.mkdir(exist_ok=True)
PLAYERS_DIR.mkdir(exist_ok=True)


def get_team_logo_url(team_name: str) -> Optional[str]:
    """
    Get team logo URL from various sources.
    Returns placeholder if not found.
    """
    # Team name mapping (Korean to file names)
    # 실제 데이터에 있는 팀명 형식 및 모든 로고 파일명
    team_mapping = {
        # 울산 - 실제 데이터: "울산 HD FC"
        "울산": "ulsan",
        "울산 현대": "ulsan",
        "울산현대": "ulsan",
        "울산 HD FC": "ulsan",
        "울산HD FC": "ulsan",
        "울산 HD": "ulsan",
        # 전북 - 실제 데이터: "전북 현대 모터스"
        "전북": "jeonbuk",
        "전북 현대": "jeonbuk",
        "전북현대": "jeonbuk",
        "전북 현대 모터스": "jeonbuk",
        "전북현대 모터스": "jeonbuk",
        # 포항 - 실제 데이터: "포항 스틸러스"
        "포항": "pohang",
        "포항 스틸러스": "pohang",
        "포항스틸러스": "pohang",
        # 서울 - 실제 데이터: "FC서울"
        "서울": "fcseoul",
        "FC 서울": "fcseoul",
        "FC서울": "fcseoul",
        "서울 FC": "fcseoul",
        # 인천 - 실제 데이터: "인천 유나이티드"
        "인천": "incheon",
        "인천 유나이티드": "incheon",
        # 수원
        "수원": "suwon",
        "수원 삼성": "suwon",
        "수원FC": "suwon",
        "수원 FC": "suwon",
        # 대전 - 실제 데이터: "대전 하나 시티즌"
        "대전": "daejeon",
        "대전 시티즌": "daejeon",
        "대전 하나 시티즌": "daejeon",
        "대전하나 시티즌": "daejeon",
        # 대구 - 실제 데이터: "대구FC"
        "대구": "daegu",
        "대구FC": "daegu",
        "대구 FC": "daegu",
        # 광주 - 실제 데이터: "광주FC"
        "광주": "gwangju",
        "광주FC": "gwangju",
        "광주 FC": "gwangju",
        # 강원 - 실제 데이터: "강원FC"
        "강원": "gangwon",
        "강원FC": "gangwon",
        "강원 FC": "gangwon",
        # 제주 - 실제 데이터: "제주SK FC"
        "제주": "jeju",
        "제주 유나이티드": "jeju",
        "제주SK FC": "jeju",
        "제주 SK FC": "jeju",
        # 김천 - 실제 데이터: "김천 상무 프로축구단"
        "김천": "gimcheon",
        "김천 상무": "gimcheon",
        "김천 상무 프로축구단": "gimcheon",
        "김천상무 프로축구단": "gimcheon",
    }
    
    # Try exact match first
    team_id = team_mapping.get(team_name)
    
    # Try partial match (contains)
    if not team_id:
        for key, value in team_mapping.items():
            if key in team_name or team_name in key:
                team_id = value
                break
    
    # If still not found, try to extract from team name
    if not team_id:
        # Extract first word or common patterns
        team_lower = team_name.lower().replace(" ", "_").replace("fc", "").strip("_")
        # Try common patterns
        for key, value in team_mapping.items():
            if key.lower() in team_name.lower():
                team_id = value
                break
    
    # Try local files with the team_id
    if team_id:
        # Try .png first
        local_path = LOGOS_DIR / f"{team_id}.png"
        if local_path.exists():
            return str(local_path.resolve())
        # Try .jpg
        local_path = LOGOS_DIR / f"{team_id}.jpg"
        if local_path.exists():
            return str(local_path.resolve())
    
    # Try direct filename match (remove spaces, special chars)
    sanitized = team_name.lower().replace(" ", "").replace("fc", "").replace("현대", "").replace("모터스", "").replace("스틸러스", "").replace("유나이티드", "")
    direct_path = LOGOS_DIR / f"{sanitized}.png"
    if direct_path.exists():
        return str(direct_path.resolve())
    direct_path = LOGOS_DIR / f"{sanitized}.jpg"
    if direct_path.exists():
        return str(direct_path.resolve())
    
    # Debug: List all available logo files
    available_logos = [f.stem for f in LOGOS_DIR.iterdir() if f.is_file() and f.suffix in ['.png', '.jpg']]
    
    # Fallback to placeholder
    return None


def get_player_photo_url(player_name: str, team_name: str = None) -> Optional[str]:
    """
    Get player photo URL.
    Returns placeholder if not found.
    """
    # Try local file first
    player_id = player_name.replace(" ", "_").lower()
    local_path = PLAYERS_DIR / f"{player_id}.jpg"
    
    if local_path.exists():
        return str(local_path)
    
    return None


def render_team_logo(team_name: str, size: int = 80, style: str = "circle"):
    """
    Render team logo in Streamlit
    """
    logo_url = get_team_logo_url(team_name)
    
    if logo_url:
        if Path(logo_url).exists():
            # Local file
            st.image(logo_url, width=size)
        else:
            # URL
            st.image(logo_url, width=size)
    else:
        # Placeholder
        placeholder_html = f"""
        <div style="
            width: {size}px;
            height: {size}px;
            border-radius: {'50%' if style == 'circle' else '12px'};
            background: linear-gradient(135deg, #30363d 0%, #1c2128 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #facc15;
            font-weight: 700;
            font-size: {size // 3}px;
            border: 2px solid #facc15;
        ">
            {team_name[0] if team_name else '?'}
        </div>
        """
        st.markdown(placeholder_html, unsafe_allow_html=True)


def render_player_photo(player_name: str, team_name: str = None, size: int = 120, style: str = "circle"):
    """
    Render player photo in Streamlit
    """
    photo_url = get_player_photo_url(player_name, team_name)
    
    if photo_url:
        if Path(photo_url).exists():
            st.image(photo_url, width=size)
        else:
            st.image(photo_url, width=size)
    else:
        # Placeholder with initials
        initials = "".join([name[0] for name in player_name.split()[:2]]) or player_name[0]
        placeholder_html = f"""
        <div style="
            width: {size}px;
            height: {size}px;
            border-radius: {'50%' if style == 'circle' else '12px'};
            background: linear-gradient(135deg, #30363d 0%, #1c2128 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #facc15;
            font-weight: 700;
            font-size: {size // 3}px;
            border: 3px solid #facc15;
            box-shadow: 0 4px 12px rgba(250, 204, 21, 0.3);
        ">
            {initials}
        </div>
        """
        st.markdown(placeholder_html, unsafe_allow_html=True)


def download_image_from_url(url: str, save_path: Path) -> bool:
    """
    Download image from URL and save locally
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        st.error(f"Failed to download image: {e}")
    return False


def create_image_mapping_csv():
    """
    Create a CSV template for image URL mappings
    """
    template = pd.DataFrame({
        'team_name_ko': [],
        'team_logo_url': [],
        'player_name_ko': [],
        'player_photo_url': []
    })
    
    csv_path = IMAGES_DIR / "image_mapping.csv"
    template.to_csv(csv_path, index=False, encoding='utf-8-sig')
    st.info(f"이미지 매핑 템플릿이 생성되었습니다: {csv_path}")


@st.cache_data
def load_image_mapping() -> pd.DataFrame:
    """
    Load image URL mappings from CSV
    """
    csv_path = IMAGES_DIR / "image_mapping.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path, encoding='utf-8-sig')
    return pd.DataFrame()

