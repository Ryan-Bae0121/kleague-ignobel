# 🖼️ 이미지 테스트 가이드

## 다운로드된 로고 (4개)
- ✅ `fcseoul.png` - FC 서울
- ✅ `jeonbuk.png` - 전북 현대
- ✅ `pohang.png` - 포항 스틸러스
- ✅ `ulsan.png` - 울산 현대

## 테스트 방법

1. **앱 실행**:
```bash
streamlit run app.py
```

2. **확인할 페이지**:
   - **홈 페이지**: Top 3 이그노벨상 카드에 팀 로고가 표시되는지 확인
   - **Awards 페이지**: 랭킹 카드에 팀 로고가 표시되는지 확인
   - **Players 페이지**: 선수 프로필에 팀 로고가 표시되는지 확인
   - **Teams 페이지**: 팀 선택 시 로고가 표시되는지 확인

3. **예상 동작**:
   - 울산, 전북, 포항, 서울 팀 로고가 자동으로 표시됨
   - 다른 팀은 플레이스홀더(초기)가 표시됨

## 팀명 매핑 확인

데이터에 저장된 팀명 형식을 확인하려면:
```python
import pandas as pd
df = pd.read_parquet('artifacts/leaderboard.parquet')
print(df['team_name_ko'].unique())
```

## 문제 해결

### 로고가 안 보이는 경우:
1. 파일명 확인: `images/logos/` 폴더에 정확한 파일명인지 확인
2. 팀명 매핑 확인: `src/image_utils.py`의 `team_mapping` 딕셔너리 확인
3. 브라우저 콘솔 확인: F12로 이미지 로딩 오류 확인

### 팀명이 매칭 안 되는 경우:
`src/image_utils.py`의 `get_team_logo_url` 함수에서 팀명 매핑을 추가하세요.

