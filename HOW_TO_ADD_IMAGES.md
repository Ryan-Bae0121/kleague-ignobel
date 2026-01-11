# 🖼️ K리그 이미지 추가 가이드

## 📁 폴더 구조

이미지는 다음 폴더에 저장됩니다:
```
images/
├── logos/          # 팀 로고 (PNG)
│   ├── ulsan.png
│   ├── jeonbuk.png
│   └── ...
├── players/        # 선수 사진 (JPG)
│   ├── player_name.jpg
│   └── ...
└── image_mapping.csv  # 이미지 URL 매핑 (선택사항)
```

## 방법 1: 수동으로 이미지 다운로드 (가장 간단)

### 1-1. 팀 로고
1. K리그 공식 웹사이트나 위키피디아에서 로고 찾기
2. `images/logos/` 폴더에 저장
3. 파일명: `팀이름.png` (예: `ulsan.png`, `jeonbuk.png`)

### 1-2. 선수 사진
1. K리그 공식 웹사이트에서 선수 사진 찾기
2. `images/players/` 폴더에 저장
3. 파일명: `선수이름.jpg` (예: `김민수.jpg`)

## 방법 2: URL 매핑 CSV 사용 (대량 다운로드)

### 2-1. CSV 템플릿 생성
```python
# Streamlit 앱에서 실행
from src.image_utils import create_image_mapping_csv
create_image_mapping_csv()
```

### 2-2. CSV 파일 편집
`images/image_mapping.csv` 파일을 열고 아래 형식으로 입력:

```csv
team_name_ko,team_logo_url,player_name_ko,player_photo_url
울산 현대,https://example.com/logos/ulsan.png,김민수,https://example.com/players/kim.jpg
전북 현대,https://example.com/logos/jeonbuk.png,이철수,https://example.com/players/lee.jpg
```

### 2-3. 자동 다운로드
```bash
python scripts/download_images.py
```

## 방법 3: 웹 스크래핑 (고급)

K리그 공식 웹사이트나 데이터베이스에서 자동으로 이미지를 가져오는 스크립트를 만들 수 있습니다.

```python
# 예시: K리그 공식 API 또는 웹사이트에서 가져오기
import requests
from bs4 import BeautifulSoup

def scrape_team_logos():
    # K리그 공식 웹사이트에서 로고 URL 추출
    # ...
    pass
```

## 방법 4: 공개 이미지 URL 직접 사용

### 4-1. 위키피디아 활용
- K리그 위키피디아 페이지에서 이미지 URL 가져오기
- 예: `https://upload.wikimedia.org/wikipedia/ko/.../ulsan_logo.png`

### 4-2. K리그 공식 웹사이트
- K리그 공식 웹사이트에서 이미지 URL 가져오기
- `image_mapping.csv`에 URL 추가

## 📝 이미지 파일명 규칙

### 팀 로고
- 파일명: `팀이름_영문.png`
- 예: `ulsan.png`, `jeonbuk.png`, `pohang.png`

### 선수 사진
- 파일명: `선수이름.jpg` 또는 `선수이름.png`
- 공백은 언더스코어로: `김_민수.jpg`

## 🔧 이미지 소스 추천

### 무료 이미지 소스
1. **위키피디아**: 팀 로고, 선수 사진
   - URL: `https://ko.wikipedia.org/wiki/K리그1`
2. **K리그 공식 웹사이트**: 공식 로고 및 선수 사진
   - URL: `https://www.kleague.com`
3. **Transfermarkt**: 선수 프로필 사진
   - URL: `https://www.transfermarkt.com/k-league-1/startseite/wettbewerb/RSL1`

## ⚠️ 주의사항

1. **저작권**: 이미지 사용 시 저작권 확인 필수
2. **이미지 크기**: 
   - 로고: 200x200px 권장
   - 선수 사진: 300x300px 권장
3. **파일 형식**: PNG (로고), JPG (사진)
4. **파일 크기**: 각 파일 500KB 이하 권장

## 🚀 빠른 시작

1. **폴더 생성** (자동):
   ```bash
   python -c "from pathlib import Path; (Path('images') / 'logos').mkdir(parents=True, exist_ok=True); (Path('images') / 'players').mkdir(parents=True, exist_ok=True)"
   ```

2. **수동 다운로드**:
   - 몇 개의 팀 로고를 직접 다운로드해서 `images/logos/`에 저장

3. **앱 실행**:
   ```bash
   streamlit run app.py
   ```

4. **확인**: 
   - Awards 페이지에서 로고/사진이 표시되는지 확인

## 💡 팁

- 처음에는 주요 팀 로고만 추가해도 충분합니다
- 선수 사진은 상위 랭킹 선수 위주로 추가하면 효과적입니다
- 이미지가 없으면 자동으로 플레이스홀더가 표시됩니다

