# 작업 히스토리

## 2026-03-10 - MVP 개발 완료

### 작업 내용
ChatHistory.md 기획 내용을 바탕으로 "현대인 생존 전투력 측정기" MVP 전체를 구현.

### 생성된 파일 목록 (`survival-calculator-mvp/`)
| 파일 | 설명 |
|------|------|
| `main.py` | FastAPI 진입점 |
| `requirements.txt` | 의존성 패키지 목록 |
| `.env` / `.env.example` | 환경변수 설정 |
| `supabase_schema.sql` | DB 테이블 생성 SQL |
| `app/config.py` | Pydantic Settings 환경변수 로딩 |
| `app/database/db_client.py` | Supabase 클라이언트 |
| `app/models/schemas.py` | Pydantic 입력 모델 |
| `app/services/stats.py` | BMI 계산 + 백분위 선형보간 + 캐릭터 분류 |
| `app/services/ai.py` | OpenAI gpt-4o-mini JSON Mode 연동 |
| `app/services/payment.py` | 토스페이먼츠 결제 검증 |
| `app/routers/pages.py` | HTML 페이지 서빙 라우터 |
| `app/routers/api.py` | HTMX API 라우터 (폼 처리 + 결과 계산 + 결제) |
| `templates/base.html` | Tailwind CDN + HTMX CDN 다크 테마 베이스 |
| `templates/index.html` | 메인 SPA 껍데기 |
| `templates/components/landing.html` | 랜딩 화면 |
| `templates/components/step1_form.html` | Step1 전용 (성별+나이) |
| `templates/components/step_form.html` | Step2~6 범용 Progressive Form |
| `templates/components/loading.html` | 로딩 애니메이션 + HTMX auto-trigger |
| `templates/components/result.html` | 무료(블러) + 유료 결과 통합 |
| `static/css/style.css` | 픽셀 스프라이트 CSS 애니메이션 포함 |

### 핵심 구현 사항
- **캐릭터 분류 테스트:** 6가지 케이스 모두 예상 캐릭터로 정확 분류 확인
- **라우터 테스트:** 전체 폼 플로우(Step1→2→3→4→5→6→로딩) 200 응답 확인
- **데이터 기반:** 대한비만학회(BMI 25=비만) + KSEP 논문 + 국민체력100 선형보간법

### 서버 실행 방법
```bash
cd survival-calculator-mvp
pip install -r requirements.txt
# .env 파일에 API 키 입력
uvicorn main:app --reload --port 8000
```

### 운영 전 필수 작업
1. Supabase 프로젝트 생성 후 `supabase_schema.sql` 실행
2. `.env`에 OpenAI, Supabase, 토스페이먼츠 실제 키 입력
3. 나노바나나/Midjourney로 6종 캐릭터 스프라이트 PNG 생성 후 `/static/images/` 배치
4. 토스페이먼츠 개발자 계정에서 성공/실패 URL 등록
5. Vercel/Render 배포
