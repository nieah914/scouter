# 프로젝트 운영 규칙 — 현대인 생존 전투력 측정기

## 프로젝트 경로
- 루트: `/Users/nieah914/Desktop/1_개인/01_workspace/01_scouter/`
- MVP 서버: `survival-calculator-mvp/`
- 서버 실행: `cd survival-calculator-mvp && uvicorn main:app --reload --port 8000`

---

## RULE 1 — 매 세션 시작 시 필수 (예외 없음)

세션을 시작하거나 새 작업을 받으면, 코드에 손대기 전에 반드시 아래 순서를 따른다:

1. /notion-todo 스킬을 이용해서 해야할일들을 읽는다
2. 미완료 태스크(`[ ]`) 중 우선순위가 가장 높은 것을 파악한다
3. 사용자 요청이 todolist의 태스크와 연관되면 해당 태스크 번호를 언급하고 진행한다

---

## RULE 2 — 코드 작성 요청 시 워크플로우

반드시 아래 순서대로 진행한다. 순서를 건너뛰지 않는다.

```
1. plan.md 에 작업 계획을 Todo List 형식으로 작성
2. 계획서 기반으로 코드 작성
3. 코드 테스트 및 리팩토링
4. 코드 문서화 (docstring, 주석 등)
5. 문서 리뷰 및 수정
6. history.md 에 완료 내역 기록 (날짜, 변경 파일, 요약)
7. /notion-todo 에서 해당 항목을 [x] ✅ 로 변경
```

---

## RULE 3 — 기획/계획 변경 또는 제안 시

- 대화 내용을 `context.md` 에 기록한다 (사용자 질문 + Claude 제안 형식)
- 변경 사항은 해당 `task_XX_*.md` 파일에도 반영한다

---

## RULE 4 — 파일 수정 원칙

- 파일을 수정하기 전에 반드시 Read 도구로 먼저 읽는다
- 변경은 최소 범위로 한다 (요청하지 않은 리팩토링 금지)
- `.env` 는 절대 git에 커밋하지 않는다

---

## RULE 5 — 기술 스택 핵심 규칙

- 모든 API 경로는 `/api/` prefix 로 시작한다 (`app.include_router(api.router, prefix="/api")`)
- HTMX fragment 엔드포인트와 풀페이지 라우트를 혼용하지 않는다
- Supabase 클라이언트는 `get_supabase()` 헬퍼를 통해서만 사용한다
- 세션은 인메모리 `_session_store` (token → dict) 방식이다
