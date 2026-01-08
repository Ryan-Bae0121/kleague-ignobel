# 🚀 GitHub 배포 단계별 가이드 (복붙용)

## Step 1: GitHub Repository 생성 (웹에서)

1. https://github.com 접속 및 로그인
2. 우측 상단 `+` → `New repository`
3. Repository name: `kleague-ignobel`
4. Description: `K League 이그노벨상 - AI 기반 수비/공격 패턴 분석 플랫폼`
5. **Public** 선택 (필수: Streamlit Cloud는 Public repo만 지원)
6. `Add a README file` 체크 해제 (이미 있음)
7. `Create repository` 클릭

---

## Step 2: 로컬 Git 설정 및 업로드

### 방법 A: Git Bash 사용 (추천)

Git Bash를 열고 아래 명령어를 **순서대로** 실행:

```bash
# 1. 프로젝트 디렉토리로 이동
cd /c/Users/hyoju/OneDrive/Desktop/K_league/kleague_ignobel

# 2. Git 초기화 (이미 있으면 스킵)
git init

# 3. 모든 파일 추가
git add .

# 4. 첫 커밋
git commit -m "Initial commit: K League Ignobel Awards Streamlit app with pitch analysis"

# 5. 메인 브랜치로 이름 변경
git branch -M main

# 6. GitHub 원격 저장소 연결
# ⚠️ YOUR_USERNAME을 실제 GitHub 사용자명으로 변경하세요!
git remote add origin https://github.com/YOUR_USERNAME/kleague-ignobel.git

# 7. 업로드
git push -u origin main
```

### 방법 B: CMD 사용

Windows CMD를 관리자 권한으로 열고:

```cmd
cd C:\Users\hyoju\OneDrive\Desktop\K_league\kleague_ignobel

git init
git add .
git commit -m "Initial commit: K League Ignobel Awards Streamlit app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/kleague-ignobel.git
git push -u origin main
```

### 방법 C: GitHub Desktop 사용 (GUI)

1. GitHub Desktop 다운로드 및 설치
2. File → Add Local Repository
3. `kleague_ignobel` 폴더 선택
4. Publish repository 클릭
5. Repository name: `kleague-ignobel`, Public 선택
6. Publish 클릭

---

## Step 3: Streamlit Cloud 배포

### 3-1. Streamlit Cloud 가입

1. https://share.streamlit.io/ 접속
2. **Sign in with GitHub** 클릭
3. GitHub 로그인 및 권한 승인

### 3-2. 새 앱 생성

1. 대시보드에서 **"New app"** 클릭
2. **Repository**: `YOUR_USERNAME/kleague-ignobel` 선택
3. **Branch**: `main` 선택
4. **Main file path**: `app.py` 입력
5. **App URL** (선택): 원하는 URL 이름 입력
   - 예: `kleague-ignobel` → `https://kleague-ignobel.streamlit.app`

### 3-3. 배포 시작

6. **Deploy!** 버튼 클릭
7. 2-5분 대기 (자동으로 빌드 및 배포)
8. 완료되면 **"View app"** 버튼으로 접속

---

## Step 4: 배포 확인

### 4-1. 기본 동작 확인

배포된 URL에 접속하여:
- [ ] 홈 페이지 로드 확인
- [ ] 다크 테마 적용 확인
- [ ] 각 페이지 접근 확인 (Awards, Players, Teams, Methodology)
- [ ] 새 페이지 접근 확인 (Pitch Analysis, Team Patterns)

### 4-2. 데이터 로딩 확인

- [ ] 홈에서 Top 3 이그노벨상 표시 확인
- [ ] Players에서 선수 검색 작동 확인
- [ ] Pitch Analysis에서 피치 맵 표시 확인
- [ ] Team Patterns에서 Zone 히트맵 표시 확인

### 4-3. 오류 체크

- [ ] 브라우저 콘솔에 에러 없는지 확인 (F12)
- [ ] Streamlit Cloud 로그 확인 (Settings → Logs)

---

## 🔧 문제 해결

### "ModuleNotFoundError"

**해결:**
1. Streamlit Cloud 대시보드 → Settings → Reboot app
2. 그래도 안 되면 `requirements.txt` 확인 및 업데이트

### "FileNotFoundError: artifacts/..."

**해결:**
1. GitHub에서 `artifacts/` 폴더가 있는지 확인
2. `.gitignore`에서 artifacts가 무시되지 않았는지 확인
3. 필요시 다시 `git add artifacts/` → `git commit` → `git push`

### 앱이 느림

**해결:**
1. `@st.cache_data`가 모든 데이터 로딩에 적용되어 있는지 확인
2. 필요시 `events_light.parquet` 샘플링 강화

---

## ✅ 배포 완료 후

배포가 성공하면:

1. **README.md에 배포 URL 추가**
2. **공유 준비:**
   - 심사용 데모 시나리오 준비
   - 스크린샷 또는 GIF 준비
3. **문서 업데이트:**
   - QUICKSTART.md에 배포 URL 추가

---

## 📋 최종 체크리스트

- [ ] GitHub Repository 생성 완료
- [ ] 로컬 파일 Git 업로드 완료
- [ ] Streamlit Cloud 계정 생성 완료
- [ ] Streamlit Cloud 앱 배포 완료
- [ ] 배포된 앱 정상 작동 확인
- [ ] 모든 페이지 접근 가능 확인
- [ ] 데이터 로딩 정상 확인
- [ ] 배포 URL 문서화 완료

**완료!** 🎉

