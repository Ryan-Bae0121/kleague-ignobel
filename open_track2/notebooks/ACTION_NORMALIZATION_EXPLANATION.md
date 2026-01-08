# 경기당 액션 수 정규화 설명

## 📋 개요

`team_analystic.ipynb`의 Cell 6에서 수행하는 **경기당 액션 수 정규화**는 각 팀의 공격/수비 스타일을 비교하기 위해 **총 액션 수를 경기 수로 나누어 평균화**하는 과정입니다.

---

## 🔍 코드 분석

### 1단계: 공격 액션 수 집계

```python
# 공격 지표
attack_actions = ['Pass', 'Cross', 'Shot', 'Take-On', 'Carry']
attack_data = raw_data[raw_data['type_name'].isin(attack_actions)]
team_attack = attack_data.groupby('team_name_ko').size().rename('공격_액션_수')
```

**의미:**
- 공격 관련 이벤트 타입을 정의 (Pass, Cross, Shot, Take-On, Carry)
- 해당 이벤트들을 필터링
- 팀별로 **총 공격 액션 수**를 집계

**결과 예시:**
```
team_name_ko
울산 HD FC      16192
광주FC          15914
포항 스틸러스    14798
...
```

**문제점:**
- 각 팀이 치른 경기 수가 다를 수 있음
- 경기 수가 많은 팀이 총 액션 수가 많을 수밖에 없음
- **공정한 비교가 불가능**

---

### 2단계: 수비 액션 수 집계

```python
# 수비 지표
defense_actions = ['Tackle', 'Interception', 'Clearance', 'Block']
defense_data = raw_data[raw_data['type_name'].isin(defense_actions)]
team_defense = defense_data.groupby('team_name_ko').size().rename('수비_액션_수')
```

**의미:**
- 수비 관련 이벤트 타입을 정의 (Tackle, Interception, Clearance, Block)
- 해당 이벤트들을 필터링
- 팀별로 **총 수비 액션 수**를 집계

**결과 예시:**
```
team_name_ko
제주SK FC       2278
대전 하나 시티즌  2118
김천 상무 프로축구단 2110
...
```

**문제점:**
- 마찬가지로 경기 수 차이로 인한 불공정 비교

---

### 3단계: 경기 수 계산

```python
# 경기당 평균으로 정규화
games_per_team = match_info.groupby('home_team_name_ko').size() + match_info.groupby('away_team_name_ko').size()
games_per_team = games_per_team.fillna(0)
```

**의미:**
- 각 팀의 **홈 경기 수** 계산: `match_info.groupby('home_team_name_ko').size()`
- 각 팀의 **원정 경기 수** 계산: `match_info.groupby('away_team_name_ko').size()`
- 두 값을 더해서 **총 경기 수** 계산
- `fillna(0)`: 경기 수가 없는 경우 0으로 처리

**결과 예시:**
```
team_name_ko
울산 HD FC      20
광주FC          20
포항 스틸러스    20
...
```

**중요한 점:**
- K리그는 보통 각 팀이 같은 수의 경기를 치르지만, 데이터에 따라 다를 수 있음
- 홈 경기 수 + 원정 경기 수 = 총 경기 수

---

### 4단계: 경기당 평균 계산 (정규화)

```python
team_style = pd.DataFrame({
    '경기당_공격_액션': (team_attack / games_per_team).round(1),
    '경기당_수비_액션': (team_defense / games_per_team).round(1)
})
```

**의미:**
- **총 공격 액션 수** ÷ **경기 수** = **경기당 평균 공격 액션 수**
- **총 수비 액션 수** ÷ **경기 수** = **경기당 평균 수비 액션 수**
- `.round(1)`: 소수점 첫째 자리까지 반올림

**결과 예시:**
```
              경기당_공격_액션  경기당_수비_액션
team_name_ko                      
울산 HD FC          809.6       93.8
광주FC              795.7       95.2
포항 스틸러스           739.9       93.2
FC서울              738.0      100.0
...
```

---

## 💡 왜 정규화가 필요한가?

### 정규화 전 (총 액션 수)
```
팀 A: 총 공격 액션 16,000개 (20경기)
팀 B: 총 공격 액션 14,000개 (18경기)
```
→ 팀 A가 더 공격적? **아니다!** 경기 수 차이 때문일 수 있음

### 정규화 후 (경기당 평균)
```
팀 A: 경기당 평균 800개 (16,000 ÷ 20)
팀 B: 경기당 평균 778개 (14,000 ÷ 18)
```
→ 팀 A가 실제로 더 공격적임을 확인 가능

---

## 📊 실제 결과 해석

### 결과 데이터
```
              경기당_공격_액션  경기당_수비_액션
울산 HD FC          809.6       93.8
광주FC              795.7       95.2
포항 스틸러스           739.9       93.2
FC서울              738.0      100.0
수원FC              725.3      101.3
강원FC              717.7       96.5
...
```

### 해석 예시

**울산 HD FC:**
- 경기당 평균 **809.6개**의 공격 액션
- 경기당 평균 **93.8개**의 수비 액션
- → **매우 공격적인 스타일**, 상대적으로 수비 액션은 적음

**제주SK FC:**
- 경기당 평균 **631.5개**의 공격 액션
- 경기당 평균 **113.9개**의 수비 액션
- → **수비 중심 스타일**, 공격 액션은 적지만 수비 액션은 많음

---

## 🎯 정규화의 장점

### 1. 공정한 비교
- 경기 수가 다른 팀들도 동일한 기준으로 비교 가능
- 각 팀의 **실제 스타일**을 파악할 수 있음

### 2. 경기당 평균 지표
- "한 경기에서 평균적으로 몇 개의 액션을 하는가?"를 알 수 있음
- 팀의 **플레이 스타일**을 정량적으로 비교 가능

### 3. 시각화 용이
- 스캐터 플롯으로 공격/수비 스타일을 2차원으로 표현 가능
- 팀들이 어떤 스타일 그룹에 속하는지 시각적으로 확인 가능

---

## 📈 시각화 결과

### 스캐터 플롯 해석
```
X축: 경기당 공격 액션 수
Y축: 경기당 수비 액션 수
```

**위치별 의미:**
- **우측 상단**: 공격도 많고 수비도 많은 팀 (활발한 플레이)
- **우측 하단**: 공격은 많지만 수비는 적은 팀 (공격 중심)
- **좌측 상단**: 공격은 적지만 수비는 많은 팀 (수비 중심)
- **좌측 하단**: 공격도 적고 수비도 적은 팀 (보수적 플레이)

---

## 🔄 정규화 공식

```
경기당 평균 액션 수 = 총 액션 수 ÷ 총 경기 수

여기서:
- 총 경기 수 = 홈 경기 수 + 원정 경기 수
```

---

## ⚠️ 주의사항

### 1. 경기 수가 0인 경우
```python
games_per_team = games_per_team.fillna(0)
```
- 경기 수가 0이면 나눗셈 시 오류 발생 가능
- 실제 데이터에서는 모든 팀이 경기를 치르므로 문제 없음

### 2. 홈/원정 경기 수 불균형
- 리그에 따라 홈/원정 경기 수가 다를 수 있음
- K리그는 보통 균형 있게 배정됨

### 3. 이벤트 타입 정의
- 공격/수비 액션의 정의가 분석 목적에 맞는지 확인 필요
- 예: 'Carry'를 공격 액션에 포함하는 것이 적절한가?

---

## 💻 코드 요약

```python
# 1. 공격 액션 수 집계
attack_actions = ['Pass', 'Cross', 'Shot', 'Take-On', 'Carry']
team_attack = raw_data[raw_data['type_name'].isin(attack_actions)]\
    .groupby('team_name_ko').size()

# 2. 수비 액션 수 집계
defense_actions = ['Tackle', 'Interception', 'Clearance', 'Block']
team_defense = raw_data[raw_data['type_name'].isin(defense_actions)]\
    .groupby('team_name_ko').size()

# 3. 경기 수 계산
games_per_team = (match_info.groupby('home_team_name_ko').size() + 
                   match_info.groupby('away_team_name_ko').size()).fillna(0)

# 4. 정규화 (경기당 평균)
team_style = pd.DataFrame({
    '경기당_공격_액션': (team_attack / games_per_team).round(1),
    '경기당_수비_액션': (team_defense / games_per_team).round(1)
})
```

---

## 🎓 학습 포인트

1. **정규화의 필요성**: 총합이 아닌 평균으로 비교해야 공정함
2. **경기 수 계산**: 홈 + 원정 경기 수를 모두 고려해야 함
3. **액션 타입 정의**: 분석 목적에 맞는 이벤트 타입 선택이 중요
4. **시각화 활용**: 스캐터 플롯으로 팀 스타일을 2차원으로 표현


