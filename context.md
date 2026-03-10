# 현대인 생존 전투력 측정기 - 전체 컨텍스트 문서

> 이 문서는 새로운 세션에서도 전체 기획·개발·대화 내용을 즉시 파악할 수 있도록
> 지금까지의 모든 결정 사항을 하나로 정리한 마스터 컨텍스트입니다.

---

## 1. 서비스 개요

| 항목 | 내용 |
|------|------|
| **서비스명** | 현대인 생존 전투력 측정기 |
| **컨셉** | 신체·생활 데이터 입력 → 공공데이터 통계 비교 → RPG 게임 상태창 형식으로 결과 제공 |
| **타겟** | 운동/건강에 관심 있는 20~40대, 바이럴 스낵 콘텐츠 소비층 |
| **핵심 목표** | SNS 자발적 공유 유도 + 990원 초소액 결제(Micro-transaction) 모델 검증 |
| **개발 방식** | AI 바이브 코딩 (Claude Code / Cursor) |

---

## 2. 비즈니스 모델 (과금)

### 가격 전략 (앵커링)
- **표시 가격:** ~~정가 3,900원~~ → **[출시 특가 -75%] 990원**
- **심리:** "3,900원짜리를 990원에 득템"하는 느낌 → 결제 허들 붕괴
- **마진율:** 약 90% (신용카드/간편결제 수수료 ~3.3% 제외)

### 결제 수단 제한
- **허용:** 신용카드, 토스페이, 카카오페이 등 간편결제
- **차단:** 가상계좌, 계좌이체 (건당 고정 수수료 400원으로 마진 급감)
- **PG사:** 토스페이먼츠 결제위젯

### 무료 vs 유료
| 플랜 | 제공 내용 |
|------|----------|
| **무료** | 알파벳 등급(S~D) + RPG 캐릭터 타이틀 + 스탯 미리보기 |
| **유료 990원** | 상세 AI 팩트폭력 분석 + 취약 질병 경고 + 맞춤 생존 루틴 + 전국 랭킹 |

---

## 3. 기술 스택 (확정)

| 구분 | 기술 | 선택 이유 |
|------|------|----------|
| **Backend** | Python FastAPI | 비동기, AI 연동 최적, 가벼움 |
| **Frontend** | HTML + Tailwind CSS CDN + HTMX | 프레임워크 없이 SPA 경험, 바이브 코딩 최적 |
| **Database** | Supabase (PostgreSQL) | BaaS, 무료 티어, 서버 구축 불필요 |
| **AI** | OpenAI gpt-4o-mini | 가성비 최고, JSON Mode 지원 |
| **결제** | 토스페이먼츠 결제위젯 | 국내 최적, HTML 몇 줄로 연동 |
| **배포** | Vercel 또는 Render | Auto-scaling, 트래픽 폭증 대응 |

---

## 4. 프로젝트 디렉토리 구조

```
survival-calculator-mvp/
├── main.py                          # FastAPI 진입점
├── requirements.txt
├── .env / .env.example
├── supabase_schema.sql              # DB 테이블 생성 SQL
│
├── app/
│   ├── config.py                    # Pydantic Settings 환경변수
│   ├── database/db_client.py        # Supabase 클라이언트
│   ├── models/schemas.py            # Pydantic 입력 모델
│   ├── routers/
│   │   ├── pages.py                 # HTML 페이지 서빙
│   │   └── api.py                   # HTMX API (폼 처리, 결과, 결제, 랭킹)
│   └── services/
│       ├── stats.py                 # BMI + 백분위 + 캐릭터 분류 로직
│       ├── ai.py                    # OpenAI API 연동
│       └── payment.py               # 토스페이먼츠 결제 검증
│
├── templates/
│   ├── base.html                    # Tailwind CDN + HTMX CDN 다크 테마
│   ├── index.html                   # 메인 SPA 껍데기 (#main-content)
│   └── components/                  # HTMX로 교체되는 조각 화면
│       ├── landing.html
│       ├── step1_form.html          # Step1 전용 (성별+나이)
│       ├── step_form.html           # Step2~N 범용 Progressive Form
│       ├── loading.html             # 로딩 애니메이션 + auto-trigger
│       └── result.html              # 무료(블러) + 유료 결과 통합
│
└── static/
    ├── css/style.css                # 픽셀 스프라이트 CSS 애니메이션 포함
    └── images/                      # {character_id}_sprite.png 배치 위치
```

---

## 5. API 엔드포인트 구조

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 메인 페이지 |
| GET | `/api/components/landing` | 랜딩 화면 조각 |
| GET | `/api/components/form/{step}` | 스텝별 폼 조각 (1~N) |
| POST | `/api/submit-step1` | Step1 (성별+나이) 처리 |
| POST | `/api/submit-step` | Step2~N 처리 |
| GET | `/api/calculate` | 전체 스탯 계산 + AI 호출 |
| GET | `/api/payment/success` | 토스 결제 성공 콜백 |
| GET | `/api/payment/fail` | 결제 실패/취소 처리 |
| GET | `/api/result` | 매직 링크로 결과 재접근 |

---

## 6. 질문지 구성 (현재 구현 6개 + 추가 예정 4개 = 총 10개)

### 현재 구현된 6개

| 스텝 | 스탯 레이블 | 질문 | 입력 방식 |
|------|------------|------|----------|
| 1 | 기본 골격 스캔 | 성별 + 나이 | 카드 선택 + 슬라이더 |
| 2 | 피지컬 스탯 | 키 + 몸무게 | 슬라이더 (140~210cm, 30~150kg) |
| 3 | HP 스탯 (회복력) | 하루 평균 수면 시간 | 카드 선택 (8h/7h/6h/5h/4h이하) |
| 4 | 전투력 스탯 | 1분 최대 푸시업 횟수 | 숫자 입력 |
| 5 | AGI 스탯 (심폐) | 20m 셔틀런 횟수 / 달리기 수준 | 카드 선택 (5단계) |
| 6 | 디버프 스탯 | 카페인 섭취 + 야근 빈도 | 카드 선택 (5단계 조합) |

### 추가 예정 4개 (대화에서 결정)

| 스텝 | 스탯 레이블 | 질문 | 계산 반영 |
|------|------------|------|----------|
| 7 | 보급품 품질 | 식습관 (건강식~패스트푸드) | 취약 질병, AI 영양 분석 |
| 8 | 마법 방어력 | 스트레스 수준 | 번아웃/멘탈 히든 캐릭터 트리거 |
| 9 | 좌식 패시브 | 하루 앉아있는 시간 | 거북목·디스크 취약 질병 반영 |
| 10 | 포션 남용 | 주당 음주 빈도 | 디버프 점수 추가, 간 질환 반영 |

---

## 7. 스탯 계산 로직 (stats.py)

### BMI (대한비만학회 2025 기준)
```
BMI = 체중(kg) / (키(m) × 키(m))

18.5 미만     → 저체중 (underweight)
18.5~22.9     → 정상 (normal)
23.0~24.9     → 과체중/비만전단계 (overweight)
25.0~29.9     → 1단계 비만 (obese_1)
30.0~34.9     → 2단계 비만 (obese_2)
35.0 이상     → 3단계 고도비만 (obese_3)
```

### 백분위 (국민체력100 + KSEP 논문, 선형 보간법)
```
pushup_table_M = { 20: [55,41,34,20], 30: [48,31,28,15], 40: [40,27,22,12], 50: [32,21,18,10] }
shuttlerun_table_M = { 20: [65,51,40,25], 30: [58,45,35,20], ... }
→ [상위10%, 상위30%, 상위50%, 상위80%] 컷오프값으로 선형 보간하여 정확한 상위% 산출
```

### 스탯 환산 (0~100점)
```
STR = 100 - 푸시업 상위%
AGI = 100 - 셔틀런 상위%
HP  = 수면기반 (7h이상=100, 6h=70, 5h=40, 4h이하=10)
DEBUFF = (커피잔수×10) + (야근횟수×15), 최대 100
```

### 종합 등급
```
avg = (STR + AGI + HP + (100-DEBUFF)) / 4
85↑ → S  /  75↑ → A+  /  65↑ → A  /  55↑ → B+  /  45↑ → B  /  35↑ → B-  /  25↑ → C  /  미만 → D
```

---

## 8. RPG 캐릭터 분류 시스템

### 기본 6종 (폭포수 If-Elif 분기)

| 우선순위 | 캐릭터 | 이모지 | 분류 조건 |
|---------|--------|--------|----------|
| Hidden | 소드마스터 | 👑 | STR≥80 AND AGI≥80 AND HP≥70 AND DEBUFF≤30 |
| 1 | 언데드 네크로맨서 | 🧟 | HP≤40 AND DEBUFF≥60 |
| 2 | 드워프 탱커 | 🛡️ | BMI=비만 AND STR≥50 |
| 3 | 오크 버서커 | 🏋️ | STR≥70 AND STR>AGI |
| 4 | 엘프 레인저 | 🏃 | AGI≥70 AND AGI>STR |
| 5 | 마법사 | 🧙 | else (기본값) |

### 히든 5종 추가 예정 (추가 질문 연동)

| 캐릭터 | 이모지 | 트리거 조건 |
|--------|--------|------------|
| 리치왕 | 💀 | 수면4h↓ + 야근매일 + 음주매일 |
| 겨울잠 곰 | 🐻 | 운동0 + 수면9h↑ + 좌식10h↑ |
| 건강신 아바타 | 🦸 | 모든 스탯 상위 10% + 건강식 + 스트레스 낮음 |
| 번아웃 유령 | 👻 | 멘탈 최하 + 수면부족 + 야근 많음 |
| 오거 군주 | 🍖 | 과체중 + 패스트푸드 + 음주↑ + 운동0 |

---

## 9. AI 시스템 프롬프트 (ai.py)

### 페르소나
```
"You are a cynical but highly accurate 'Status Window AI' from a modern fantasy RPG.
Speak in Korean. Use game-like terminology (HP, MP, Buff, Debuff, 스탯 등)
with witty, sarcastic, factual tone (팩트폭력).
DO NOT hallucinate. Use ONLY provided statistical data."
```

### JSON 응답 스키마 (SurvivalReport Pydantic 모델)
```python
grade: str             # S, A+, A, B+, B, B-, C, D
title: str             # "야근에 찌든 오크 행동대장"
summary: str           # 한 줄 팩트폭력 요약
analysis_physical: str # 체격/전투력 분석
analysis_sleep: str    # 수면/HP 분석
analysis_debuff: str   # 카페인/야근 디버프 분석
disease_warning: str   # 취약 질병 RPG식 경고
action_plan: str       # 생존 퀘스트 1가지
```

### 데이터 출처 명시 (결과 화면 하단)
```
문화체육관광부 국민체력100 데이터(2025) 및
대한운동학회(KSEP) 한국인 체력 백분위 연구 논문 기반 선형 보간법 산출
```

---

## 10. 화면 구성 및 UX 플로우

```
① 랜딩 (landing.html)
   └─ RPG 로고 + 픽셀 캐릭터 + 참여자 수 + [스캐닝 시작하기]

② Progressive Form (step1_form.html → step_form.html × N)
   └─ 한 문항씩 HTMX 교체 + 상단 진행도 게이지 [■■■□□□ 3/N]

③ 로딩 (loading.html)
   └─ 재치있는 순차 메시지 + 진행 바
   └─ 2.5초 후 /api/calculate 자동 호출 (hx-trigger="load delay:2.5s")

④ 무료 결과 (result.html, is_paid=False)
   └─ [가챠 연출 예정] 등급 한 글자씩 공개
   └─ 캐릭터 스프라이트 아이들 애니메이션
   └─ 스탯 미리보기 + 블러 처리된 상세 리포트
   └─ 전국 랭킹 위치 표시 (추가 예정)
   └─ 소셜 프루프: "🔥 N명이 확인했습니다" (100명 미만 시 숨김)
   └─ [친구에게 도전장 보내기] (추가 예정)
   └─ [990원 잠금 해제] 버튼 + 결제 전 안내문구

⑤ 유료 결과 (result.html, is_paid=True)
   └─ 블러 해제 애니메이션 ("잠금 해제 완료!")
   └─ 상세 AI 팩트폭력 분석 (physical/sleep/debuff)
   └─ 취약 질병 경고 + 맞춤 생존 퀘스트
   └─ 매직 링크 복사 버튼
   └─ 데이터 출처 표기
```

---

## 11. 결제 플로우 (로그인 없음)

```
① 브라우저 LocalStorage에 UUID user_token 자동 생성 및 저장
② 990원 결제 버튼 클릭 → 토스페이먼츠 위젯 팝업 (신용카드/간편결제만)
③ 결제 완료 → 토스가 /api/payment/success?user_token=xxx 로 리다이렉트
④ FastAPI에서 토스 승인 API 재검증 (해킹 방지)
⑤ DB에 is_paid=True 저장 + 유료 결과 HTML 반환 (HTMX 블러 해제)
⑥ 매직 링크 생성: https://도메인/api/result?token=xxx
```

### CS 방어 안내문구 (결제 전 필수 노출)
```
"본 서비스는 로그인 없이 진행됩니다.
결제 후 제공되는 '영구 보관 링크' 분실 또는 캐시 삭제 시
리포트 복구 및 환불이 불가하오니, 결제 직후 꼭 캡처하거나 링크를 저장해 주세요."
```

---

## 12. 소셜 프루프 넛지

```python
# 10분 캐싱으로 DB 부하 방지
_paid_count_cache = {"count": 0, "updated_at": 0}
CACHE_TTL = 600  # 10분

# 100명 미만 → 숨김 (초기 흥행 부진 방어)
{% if paid_count >= 100 %}
  🔥 현재 {{ paid_count }}명이 생존 리포트를 확인했습니다
{% endif %}
```

---

## 13. 픽셀 아트 에셋 (CSS 스프라이트 애니메이션)

### 캐릭터별 이미지 생성 프롬프트 (나노바나나/Midjourney)
각 캐릭터: **16-bit pixel art, 2D horizontal sprite sheet, 4-frame idle animation in single horizontal row, SNES RPG style, plain white background, --ar 16:9**

| 캐릭터 ID | 프롬프트 키워드 |
|-----------|---------------|
| swordmaster | radiant Swordmaster, high-tech workout gear + holy knight armor, glowing aura |
| necromancer | Undead Necromancer, dark hoodie, IV drip of black coffee, trembling animation |
| dwarf_tanker | Dwarf Tanker, padded jacket as armor, heavy briefcase as shield, heavy breathing |
| orc_berserker | Orc Berserker, torn business suit over green skin, coffee cup as weapon |
| elf_ranger | Elf Ranger, modern running gear, smartwatch glowing green, bouncing animation |
| wizard | Wizard, ergonomic chair as throne, thick glasses, typing animation |

### CSS 구현 (steps() 애니메이션)
```css
.pixel-sprite {
    image-rendering: pixelated;
    width: 150px; height: 150px;
    background-size: auto 100%;
}
@keyframes idle-anim {
    from { background-position-x: 0; }
    to   { background-position-x: -100%; }
}
.pixel-sprite-animated {
    animation: idle-anim 0.8s steps(4) infinite;
}
```

### 파일 배치
```
/static/images/{character_id}_sprite.png  (4프레임 가로 스프라이트 시트)
```

---

## 14. 추가 재미/흥미 요소 (대화에서 논의, 구현 예정)

### 즉시 적용 가능 (코드 최소)
- **가챠 스타일 결과 발표:** 등급 한 글자씩 공개 (B → B- → "B- 언데드 네크로맨서!") + 캐릭터 짠! 등장 CSS 애니메이션
- **이스터에그 히든 캐릭터 5종:** 특정 스탯 조합 시 특별 캐릭터 + 특별 메시지

### 바이럴 효과 최대
- **전국 실시간 랭킹:** "당신은 전국 12,847명 중 상위 8%입니다" (DB 기반)
- **친구 배틀 링크:** `/battle?challenger=token1` → 두 캐릭터 스탯 비교 화면

### 체류 시간 증가
- **"만약에" 시뮬레이터:** 슬라이더로 수치 조절 → 실시간 등급 변화 (JS 로컬 계산, 서버 부하 없음)

### 장기 데이터 자산
- **직업군별 비교:** 직업 선택 → "개발자 평균 C+ vs 나 B-"

---

## 15. Supabase DB 스키마

```sql
CREATE TABLE users (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_token     TEXT UNIQUE NOT NULL,
    gender         TEXT,
    age            INTEGER,
    height         FLOAT,
    weight         FLOAT,
    sleep_hours    FLOAT,
    pushup_count   INTEGER,
    running_count  INTEGER,
    coffee_cups    INTEGER,
    overtime_days  INTEGER,
    -- 추가 예정 컬럼
    diet_score     INTEGER,  -- Q7 식습관
    stress_score   INTEGER,  -- Q8 멘탈
    sitting_hours  FLOAT,    -- Q9 좌식
    alcohol_score  INTEGER,  -- Q10 음주
    occupation     TEXT,     -- 직업군
    -- 계산 결과
    bmi            FLOAT,
    bmi_status     TEXT,
    str_score      INTEGER,
    agi_score      INTEGER,
    hp_score       INTEGER,
    debuff_score   INTEGER,
    character_id   TEXT,
    overall_grade  TEXT,
    ai_result      JSONB,
    is_paid        BOOLEAN DEFAULT FALSE,
    order_id       TEXT,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 16. 환경변수 목록 (.env)

```bash
OPENAI_API_KEY=sk-...          # OpenAI gpt-4o-mini 호출
SUPABASE_URL=https://...       # Supabase 프로젝트 URL
SUPABASE_KEY=...               # Supabase anon key
TOSS_CLIENT_KEY=test_ck_...    # 토스페이먼츠 클라이언트 키
TOSS_SECRET_KEY=test_sk_...    # 토스페이먼츠 시크릿 키
APP_ENV=development
SECRET_KEY=...
```

---

## 17. 현재 구현 현황

| Task | 파일 | 상태 |
|------|------|------|
| 01 | 프로젝트 구조 전체 | ✅ 완료 |
| 02 | 프론트엔드 UI 5개 화면 | ✅ 완료 |
| 03 | stats.py - BMI + 백분위 계산 | ✅ 완료 + 테스트 통과 |
| 04 | stats.py - 캐릭터 분류 6종 | ✅ 완료 + 테스트 통과 |
| 05 | ai.py - OpenAI JSON Mode | ✅ 완료 |
| 06 | payment.py - 토스페이먼츠 | ✅ 완료 |
| 07 | 소셜 프루프 넛지 | ✅ 완료 |
| 08 | CSS 스프라이트 애니메이션 | ✅ 완료 |
| - | 404 버그 수정 (/api prefix) | ✅ 수정 완료 |

### 미구현 (다음 세션에서 진행 예정)
- [ ] Q7~Q10 추가 질문 구현
- [ ] 히든 캐릭터 5종 추가
- [ ] 가챠 스타일 결과 연출
- [ ] 전국 랭킹 기능
- [ ] 친구 배틀 링크 기능
- [ ] "만약에" 시뮬레이터
- [ ] 직업군 비교

---

## 18. 서버 실행 방법

```bash
cd survival-calculator-mvp
pip install -r requirements.txt

# .env 파일에 API 키 입력 후:
uvicorn main:app --reload --port 8000
# 접속: http://localhost:8000
```

---

## 19. 운영 전 필수 체크리스트

- [ ] Supabase 프로젝트 생성 → `supabase_schema.sql` 실행
- [ ] `.env`에 실제 API 키 입력 (OpenAI, Supabase, 토스페이먼츠)
- [ ] 토스페이먼츠 개발자 콘솔 → 성공URL/실패URL 등록
- [ ] 6종 캐릭터 스프라이트 PNG 생성 → `/static/images/` 배치
- [ ] 모바일 브라우저 실제 테스트
- [ ] Vercel/Render 배포

---

## 20. 핵심 기획 원칙 요약

1. **개발 최소화:** React/Next.js 없이 FastAPI + HTMX로 단일 서버 구조
2. **이탈 최소화:** 로그인 없음, 질문 간결, 한 화면 내 결제
3. **바이럴 설계:** 무료 결과가 공유하고 싶을 만큼 재미있어야 함
4. **할루시네이션 방지:** AI에게 계산된 수치만 제공, 숫자 발명 금지
5. **수수료 방어:** 간편결제만 허용, 가상계좌/계좌이체 차단
6. **신뢰도:** 데이터 출처(국민체력100, 대한비만학회) 명시로 결제 납득시키기
