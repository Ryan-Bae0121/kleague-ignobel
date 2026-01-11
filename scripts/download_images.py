"""
Script to download K League team logos and player photos
"""
import requests
from pathlib import Path
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.image_utils import IMAGES_DIR, LOGOS_DIR, PLAYERS_DIR, download_image_from_url
from src.io import load_artifact

# K League team logo URLs (example - replace with actual URLs)
TEAM_LOGO_URLS = {
    "울산 현대": "https://example.com/logos/ulsan.png",
    "전북 현대": "https://example.com/logos/jeonbuk.png",
    "포항 스틸러스": "https://example.com/logos/pohang.png",
    # Add more teams...
}

def download_team_logos():
    """Download all team logos"""
    print("📥 팀 로고 다운로드 중...")
    
    # Load teams from data
    try:
        leaderboard = load_artifact("leaderboard.parquet")
        teams = leaderboard["team_name_ko"].unique()
        
        for team in teams:
            # Try to find logo URL
            # You can modify this to match actual logo URLs
            team_id = team.replace(" ", "_").lower()
            logo_url = TEAM_LOGO_URLS.get(team, None)
            
            if logo_url:
                save_path = LOGOS_DIR / f"{team_id}.png"
                if not save_path.exists():
                    print(f"  다운로드 중: {team} -> {save_path}")
                    download_image_from_url(logo_url, save_path)
                else:
                    print(f"  이미 존재: {team}")
    except Exception as e:
        print(f"⚠️ 오류: {e}")
        print("   팀 로고를 수동으로 다운로드하거나 image_mapping.csv를 사용하세요.")


def download_player_photos():
    """Download player photos from image_mapping.csv"""
    print("📥 선수 사진 다운로드 중...")
    
    mapping_path = IMAGES_DIR / "image_mapping.csv"
    if not mapping_path.exists():
        print("⚠️ image_mapping.csv 파일이 없습니다.")
        print("   먼저 이미지 URL 매핑 파일을 만들어주세요.")
        return
    
    df = pd.read_csv(mapping_path, encoding='utf-8-sig')
    
    if 'player_photo_url' not in df.columns:
        print("⚠️ player_photo_url 컬럼이 없습니다.")
        return
    
    for _, row in df.iterrows():
        if pd.notna(row.get('player_photo_url')) and row.get('player_photo_url'):
            player_name = row.get('player_name_ko', '')
            photo_url = row['player_photo_url']
            
            player_id = player_name.replace(" ", "_").lower()
            save_path = PLAYERS_DIR / f"{player_id}.jpg"
            
            if not save_path.exists():
                print(f"  다운로드 중: {player_name} -> {save_path}")
                download_image_from_url(photo_url, save_path)
            else:
                print(f"  이미 존재: {player_name}")


def main():
    """Main function"""
    print("🏆 K League 이미지 다운로더\n")
    
    # Create directories
    LOGOS_DIR.mkdir(parents=True, exist_ok=True)
    PLAYERS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download logos
    download_team_logos()
    
    print("\n" + "="*50 + "\n")
    
    # Download player photos
    download_player_photos()
    
    print("\n✅ 완료!")
    print(f"\n📁 이미지 위치:")
    print(f"   로고: {LOGOS_DIR}")
    print(f"   선수: {PLAYERS_DIR}")


if __name__ == "__main__":
    main()

