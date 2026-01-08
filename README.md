# 🏆 K League 이그노벨상 웹 애플리케이션

K리그 선수들의 수비 패턴을 분석하여 데이터 기반 "이그노벨상"을 자동으로 계산하고 시상하는 웹 서비스입니다.

## 📁 프로젝트 구조

```
kleague_ignobel/
├─ app.py                          # 메인 Streamlit 앱
├─ pages/
│  ├─ 1_🏆_Awards.py              # Awards 페이지
│  ├─ 2_👤_Players.py             # Players 페이지
│  ├─ 3_🛡️_Teams.py              # Teams 페이지
│  └─ 4_📊_Methodology.py         # Methodology 페이지
├─ src/
│  ├─ config.py                    # 상 정의 및 설정
│  ├─ io.py                        # 데이터 입출력
│  ├─ preprocess.py                # 데이터 전처리
│  ├─ aggregate.py                 # 통계 집계
│  ├─ awards_engine.py             # 상 점수 계산 엔진
│  ├─ viz.py                       # 시각화 유틸리티
│  └─ text_templates.py            # 텍스트 생성 템플릿
├─ scripts/
│  └─ build_artifacts.py           # 배치 스크립트 (아티팩트 생성)
├─ artifacts/                      # 생성된 아티팩트 (parquet 파일)
└─ requirements.txt                # Python 패키지 의존성
```

## 🌐 배포된 앱

배포된 웹 서비스를 바로 사용하세요:
- **Streamlit Cloud**: [https://your-app.streamlit.app](https://your-app.streamlit.app) (배포 후 URL 업데이트)

---

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 아티팩트 생성

먼저 원본 데이터에서 통계를 계산하여 아티팩트를 생성해야 합니다:

```bash
python scripts/build_artifacts.py
```

이 스크립트는:
- `open_track2/raw_data.csv`와 `open_track2/match_info.csv`를 읽어서
- 전처리 및 집계를 수행하고
- `artifacts/` 디렉토리에 결과를 저장합니다

### 3. 웹 앱 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 열리며 웹 서비스를 사용할 수 있습니다.

## 🏆 이그노벨상 목록

1. **태클은 했지만...상** - 태클 실패율이 높은 선수
2. **카드만 남겼다상** - 수비 행동 대비 카드를 많이 받는 선수
3. **위험 지역 단골상** - 수비 3rd에서 파울을 많이 하는 선수
4. **클리어링 불안상** - 클리어링 후 10초 내 상대 슈팅을 허용하는 선수
5. **블록은 했는데...상** - 블록 실패율이 높은 선수
6. **인터셉트 헛발질상** - 인터셉트 실패율이 높은 선수
7. **듀얼은 많은데 지는 상** - 듀얼 실패율이 높은 선수
8. **자기 진영 공 뺏김상** - 수비 3rd에서 턴오버율이 높은 선수
9. **후반 집중력 붕괴상** - 후반 수비 실패율이 전반보다 크게 증가한 선수

## 📊 주요 기능

### 홈 페이지
- 오늘의 Top 3 이그노벨상
- 모든 상 목록
- 전체 통계

### Awards 페이지
- 카테고리별 상 필터링
- Top 20 랭킹 시각화
- 점수 분포 그래프
- 전체 데이터 테이블

### Players 페이지
- 선수 검색 (이름/팀명)
- 선수별 수상 내역
- 상세 통계 및 설명

### Teams 페이지
- 팀별 성과 분석
- 팀 vs 리그 평균 비교
- 카테고리별 팀 순위

### Methodology 페이지
- 각 상의 정의 및 공식 설명
- 점수 계산 방법
- AI 로직 설명

## 🔧 커스터마이징

### 새로운 상 추가하기

`src/config.py`의 `AWARDS` 리스트에 새로운 상을 추가하면 됩니다:

```python
{
    "id": "new_award_id",
    "title": "새로운 상",
    "category": "카테고리",
    "level": "player",  # or "team"
    "metric": "metric_name",  # aggregate.py에서 계산되어야 함
    "direction": "high",
    "icon": "🎯",
    "description": "상 설명",
    "formula": "계산 공식",
    "min_attempts": 5
}
```

그리고 `src/aggregate.py`와 `src/awards_engine.py`에 해당 메트릭 계산 로직을 추가하세요.

## 📝 데이터 경로

기본적으로 다음 경로에서 데이터를 읽습니다:
- `../open_track2/raw_data.csv`
- `../open_track2/match_info.csv`

경로를 변경하려면 `src/io.py`를 수정하세요.

## ⚠️ 주의사항

- 먼저 `build_artifacts.py`를 실행하여 아티팩트를 생성해야 웹 앱이 동작합니다.
- 데이터 파일이 올바른 경로에 있는지 확인하세요.
- Windows에서 경로 문제가 발생할 수 있습니다. 필요시 경로를 수정하세요.

## 📄 라이선스

이 프로젝트는 K League 데이터 분석을 위한 팬 프로젝트입니다.


