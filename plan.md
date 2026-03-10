# 현대인 생존 전투력 측정기 - MVP 개발 계획서

## 프로젝트 개요
- **서비스명:** 현대인 생존 전투력 측정기
- **컨셉:** 신체/생활 데이터 입력 → 공공데이터 통계 비교 → RPG 상태창 형식 결과 제공
- **기술 스택:** Python FastAPI + HTMX + Tailwind CSS + Supabase + OpenAI API
- **과금 모델:** ~~3,900원~~ → 990원 (앵커링 전략)

---

## Todo List

### Task 01 - 프로젝트 초기 셋업 및 디렉토리 구조 생성
- [ ] 프로젝트 디렉토리 구조 생성 (`survival-calculator-mvp/`)
- [ ] `requirements.txt` 작성 (fastapi, uvicorn, openai, supabase, jinja2 등)
- [ ] `main.py` FastAPI 진입점 작성
- [ ] `app/config.py` 환경변수 설정 작성
- [ ] `app/__init__.py`, `routers/`, `services/`, `models/`, `database/` 폴더 구조 생성
- [ ] `.env.example` 환경변수 템플릿 작성

### Task 02 - 프론트엔드 UI (HTMX + Tailwind CSS SPA)
- [ ] `templates/base.html` - Tailwind CDN + HTMX CDN 포함 다크 테마 베이스
- [ ] `templates/index.html` - 메인 컨테이너 (`#main-content`)
- [ ] `templates/components/landing.html` - RPG 로고 + 시작 버튼
- [ ] `templates/components/step_form.html` - 6단계 Progressive Form (진행도 게이지)
- [ ] `templates/components/loading.html` - 재치있는 로딩 애니메이션
- [ ] `templates/components/result.html` - 무료 블러 결과 + 유료 상세 리포트 통합
- [ ] `static/css/style.css` - 픽셀 폰트, 페이드 인/아웃 커스텀 CSS

### Task 03 - 통계 계산 로직 (stats.py)
- [ ] `calculate_bmi_status()` - 대한비만학회 기준 BMI 산출
- [ ] `calculate_percentile()` - 국민체력100 + KSEP 논문 기반 선형 보간 백분위
- [ ] `convert_raw_to_scores()` - 스탯 점수 환산 (STR/AGI/HP/DEBUFF 0~100점)
- [ ] 근력(푸시업) 및 심폐(러닝) Look-up Table 하드코딩

### Task 04 - RPG 캐릭터 분류 로직 (character logic in stats.py)
- [ ] `determine_character()` - 폭포수 분기 캐릭터 판별 함수
  - 👑 소드마스터 (갓생 완전체 히든)
  - 🧟 언데드 네크로맨서 (수면파탄 + 야근중독)
  - 🛡️ 드워프 탱커 (과체중 + 근력형)
  - 🏋️ 오크 버서커 (근력 몰빵)
  - 🏃 엘프 레인저 (심폐 몰빵)
  - 🧙 마법사 (기본값 / 운동부족)
- [ ] 각 캐릭터 조건별 테스트 코드 작성

### Task 05 - OpenAI AI 연동 (ai.py)
- [ ] `SurvivalReport` Pydantic 모델 정의 (JSON Schema)
- [ ] RPG 상태창 컨셉 System Prompt 정의
- [ ] `generate_survival_report()` 비동기 함수 (gpt-4o-mini + JSON Mode)
- [ ] 에러 핸들링 (try-except)

### Task 06 - 결제 연동 (payment.py + 토스페이먼츠)
- [ ] LocalStorage 기반 `user_token` UUID 생성 및 저장 로직
- [ ] `templates/components/result.html` 토스페이먼츠 위젯 JS 삽입
- [ ] 결제 수단 제한 (신용카드/간편결제만, 가상계좌 제외)
- [ ] `/api/payment/success` 검증 엔드포인트 (FastAPI)
- [ ] DB `is_paid = True` 업데이트 로직
- [ ] HTMX 블러 해제 + 상세 리포트 렌더링
- [ ] 결제 전 안내문구 삽입 (환불불가 고지)
- [ ] 매직 링크 생성 및 복사 버튼

### Task 07 - 소셜 프루프 넛지 (social_proof)
- [ ] `get_paid_user_count()` - DB 누적 결제자 수 조회 (캐싱 적용, 10~15분)
- [ ] 결제 버튼 하단 넛지 UI 추가 ("🔥 현재 OOO명이 확인했습니다")
- [ ] 100명 미만 시 숨김 처리 (`{% if paid_count >= 100 %}`)

### Task 08 - 픽셀 아트 CSS 스프라이트 애니메이션
- [ ] `static/css/style.css` - `.pixel-sprite` CSS 클래스 + `steps()` 애니메이션
- [ ] `image-rendering: pixelated` 적용 (안티앨리어싱 방지)
- [ ] `@keyframes idle-anim` - 4프레임 스프라이트 순환
- [ ] `result.html` - `character_id` 기반 동적 이미지 교체
- [ ] 모바일 반응형 처리

---

## 라우터 구조 (API Endpoints)
| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 메인 랜딩 페이지 |
| GET | `/form/step/{step}` | 각 문항 폼 조각 반환 (HTMX) |
| POST | `/api/submit-step` | 문항 답변 저장 + 다음 단계 반환 |
| POST | `/api/calculate` | 전체 스탯 계산 + AI 결과 생성 |
| GET | `/api/result` | 결과 조각 반환 (token 기반) |
| POST | `/api/payment/success` | 토스 결제 검증 및 is_paid 업데이트 |
| GET | `/api/social-proof` | 누적 결제자 수 반환 |

---

## DB 테이블 구조 (Supabase)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_token TEXT UNIQUE NOT NULL,
  gender TEXT,
  age INT,
  height FLOAT,
  weight FLOAT,
  sleep_hours INT,
  pushup_count INT,
  running_pace FLOAT,
  coffee_cups INT,
  overtime_days INT,
  bmi FLOAT,
  bmi_status TEXT,
  str_score INT,
  agi_score INT,
  hp_score INT,
  debuff_score INT,
  character_id TEXT,
  ai_result JSONB,
  is_paid BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 진행 현황
- [x] ChatHistory.md 기획 내용 검토 완료
- [x] plan.md 작성 완료
- [x] Task 01: 프로젝트 구조 생성 (디렉토리, requirements.txt, main.py, config.py, db_client.py)
- [x] Task 02: 프론트엔드 UI (base.html, index.html, landing/step_form/loading/result.html, style.css)
- [x] Task 03: 통계 계산 로직 (BMI, 선형보간 백분위, 스탯 환산 - 테스트 통과)
- [x] Task 04: 캐릭터 분류 로직 (6종 폭포수 분기, 전체 테스트 통과)
- [x] Task 05: OpenAI 연동 (SurvivalReport Pydantic 모델, 비동기 gpt-4o-mini JSON Mode)
- [x] Task 06: 결제 연동 (토스페이먼츠 검증, LocalStorage 토큰, 매직 링크)
- [x] Task 07: 소셜 프루프 넛지 (10분 캐싱, 100명 미만 숨김)
- [x] Task 08: 픽셀 아트 CSS 스프라이트 애니메이션 (steps() 4프레임)

## 다음 단계 (운영 전 필수)
- [ ] Supabase 프로젝트 생성 및 supabase_schema.sql 실행
- [ ] .env 파일에 실제 API 키 입력 (OpenAI, Supabase, 토스페이먼츠)
- [ ] 픽셀 아트 캐릭터 이미지 생성 (나노바나나/Midjourney 프롬프트 활용)
- [ ] /static/images/ 에 {character_id}_sprite.png 파일 배치
- [ ] Vercel 또는 Render에 배포
