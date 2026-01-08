# 🚀 배포 가이드 (Deployment Guide)

## ✅ 배포 준비 완료 체크리스트

### 1. 파일 크기 확인 ✅
- `events_light.parquet`: **9.73 MB** (100MB 제한 이하, 문제없음)
- 다른 아티팩트 파일들: 모두 1MB 미만
- **결론**: 파일 크기 문제 없음, 그대로 배포 가능

### 2. 필수 파일 확인 ✅
- ✅ `requirements.txt` (존재)
- ✅ `.streamlit/config.toml` (생성 완료)
- ✅ `.gitignore` (업데이트 완료)
- ✅ `app.py` (메인 파일)
- ✅ `pages/` (모든 페이지 파일)
- ✅ `src/` (모든 소스 모듈)
- ✅ `artifacts/` (모든 parquet 파일)

---

## 📦 배포 절차 (단계별)

### Step 1: GitHub Repository 생성

1. GitHub에 로그인: https://github.com
2. **New repository** 클릭
3. Repository 이름: `kleague-ignobel` (또는 원하는 이름)
4. **Public** 선택 (Streamlit Cloud는 Public repo 필요)
5. **Create repository** 클릭

---

### Step 2: 로컬에서 Git 초기화 및 업로드

**Git Bash** 또는 **CMD**에서 실행 (PowerShell보다 깔끔함):

```bash
cd "C:\Users\hyoju\OneDrive\Desktop\K_league\kleague_ignobel"

# Git 초기화 (이미 있으면 스킵)
git init

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: K League Ignobel Awards Streamlit app"

# 브랜치 이름 (main)
git branch -M main

# GitHub repo 연결 (YOUR_USERNAME을 실제 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/kleague-ignobel.git

# 업로드
git push -u origin main
```

**참고**: 이미 Git repo가 있으면:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/kleague-ignobel.git
git push -u origin main
```

---

### Step 3: Streamlit Cloud 배포

1. **Streamlit Cloud 접속**: https://share.streamlit.io/
   - 또는 https://streamlit.io/cloud 에서 "Sign up" → GitHub로 로그인

2. **New app** 클릭

3. **Repository 선택**:
   - Repository: `YOUR_USERNAME/kleague-ignobel`
   - Branch: `main`
   - Main file path: `app.py`

4. **Advanced settings** (선택사항):
   - Python version: 3.9 이상
   - Secrets: 필요 없음 (현재는 사용 안 함)

5. **Deploy** 클릭

6. **대기**: 2-5분 정도 소요

7. **완료**: URL 생성됨
   - 예: `https://kleague-ignobel.streamlit.app`

---

## 🔍 배포 후 확인 사항

### 1. 앱이 정상 로드되는지
- 홈 페이지가 표시되는지
- 다크 테마가 적용되었는지

### 2. 각 페이지 접근
- Awards 페이지
- Players 페이지 (선수 비교 포함)
- Teams 페이지
- Methodology 페이지
- **Pitch Analysis 페이지** (NEW)
- **Team Patterns 페이지** (NEW)

### 3. 데이터 로딩
- 아티팩트 파일들이 정상 로드되는지
- 피치 맵이 표시되는지
- Zone 히트맵이 작동하는지

---

## ⚠️ 문제 해결 (Troubleshooting)

### A) "ModuleNotFoundError"
- `requirements.txt`에 누락된 패키지 추가
- Streamlit Cloud에서 "Reboot app" 클릭

### B) "FileNotFoundError: artifacts/..."
- GitHub에 `artifacts/` 폴더가 올라갔는지 확인
- `.gitignore`에서 `artifacts/*.parquet`가 주석 처리되어 있는지 확인

### C) 느림/멈춤
- `@st.cache_data`가 모든 데이터 로딩에 적용되어 있는지 확인
- 필요시 `events_light.parquet` 샘플링 강화

### D) 메모리 부족
- Streamlit Cloud는 기본 1GB 메모리
- 현재 파일 크기는 문제없음 (총 ~10MB)

---

## 📝 배포 후 공유

배포 완료 후:
- URL 공유: `https://your-app.streamlit.app`
- README 업데이트: 배포 URL 추가
- 데모 시나리오 준비:
  1. 홈 → 오늘의 이그노벨
  2. 선수 비교
  3. 수상자 피치맵
  4. 팀 패턴 분석

---

## 🎯 최종 체크리스트

배포 전 확인:
- [ ] `requirements.txt` 확인
- [ ] `.streamlit/config.toml` 확인
- [ ] `.gitignore` 확인 (artifacts 포함되도록)
- [ ] 로컬에서 `streamlit run app.py` 정상 작동 확인
- [ ] GitHub에 모든 파일 업로드 확인
- [ ] Streamlit Cloud에서 배포 완료 확인

**준비 완료!** 🚀

