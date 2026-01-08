# 🚀 빠른 시작 가이드

## 1단계: 패키지 설치

```bash
cd kleague_ignobel
pip install -r requirements.txt
```

## 2단계: 아티팩트 생성

원본 데이터에서 통계를 계산합니다:

```bash
python scripts/build_artifacts.py
```

이 스크립트가 실행되면:
- `open_track2/raw_data.csv`와 `open_track2/match_info.csv`를 읽습니다
- 전처리 및 집계를 수행합니다
- `artifacts/` 디렉토리에 다음 파일들을 생성합니다:
  - `awards_player.parquet`
  - `leaderboard.parquet`
  - `profiles.parquet`
  - `awards_team.parquet`

**참고**: 데이터 파일이 `../open_track2/` 경로에 있어야 합니다.

## 3단계: 웹 앱 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱을 볼 수 있습니다.

## 문제 해결

### "Artifacts not found" 오류
→ `scripts/build_artifacts.py`를 먼저 실행하세요.

### 데이터 파일을 찾을 수 없음
→ `src/io.py`에서 데이터 경로를 확인하고 필요시 수정하세요.

### 페이지가 로드되지 않음
→ Streamlit을 재시작하거나 캐시를 클리어하세요:
```bash
streamlit cache clear
```

## 다음 단계

- `src/config.py`에서 새로운 상을 추가해보세요
- `src/viz.py`에서 시각화를 커스터마이징하세요
- `src/text_templates.py`에서 텍스트 템플릿을 수정하세요

