# Task: Frontend UI Layout & HTMX Integration (SPA Architecture)
지금부터 `templates/` 폴더 안의 프론트엔드 코드를 작성할 거야.
우리는 React를 쓰지 않고 **Jinja2 + Tailwind CSS(CDN) + HTMX(CDN)** 조합으로 '단일 페이지 애플리케이션(SPA)'처럼 동작하는 부드러운 UI를 만들 거야.
"RPG 게임 상태창"과 "픽셀 아트" 감성이 느껴지도록 Tailwind 클래스를 적극 활용해 줘.

## 1. base.html & index.html (껍데기 화면)
1. `templates/base.html` 작성
   - Tailwind CSS CDN과 HTMX CDN을 `<head>`에 포함해 줘.
   - 배경은 어두운 다크 테마(Dark mode, 예: `bg-gray-900`)로 설정하고, 텍스트는 흰색/초록색 계열로 "상태창" 느낌이 나게 해줘.
   - 폰트는 구글 폰트에서 레트로 픽셀 느낌의 폰트(예: 'DungGeunMo' 또는 'Galmuri9')를 임포트해 줘.
2. `templates/index.html` 작성
   - `base.html`을 상속받아.
   - 중앙에 모바일 화면 비율(max-w-md)의 메인 컨테이너 `<div id="main-content">`를 만들어 줘.
   - 페이지 로드 시 이 `#main-content` 안에 `templates/components/landing.html` 조각이 기본으로 렌더링되도록 해줘.

## 2. Components (교체될 조각 화면 4개)
아래 4개의 HTML 조각 파일을 `templates/components/` 안에 작성해 줘. 각 조각은 `#main-content` 컨테이너 안에서 서로 교체(Swap)될 거야.

**① `landing.html` (시작 화면)**
- RPG 로고("현대인 생존 전투력 측정기") 타이틀.
- "당신의 숨겨진 생존 스탯을 스캐닝합니다." 서브카피.
- HTMX 속성(`hx-get="/form/step/1" hx-target="#main-content" hx-swap="innerHTML transition:true"`)이 부여된 `[스캐닝 시작하기]` 버튼을 만들어 줘.

**② `step_form.html` (문답 입력 폼 - Progressive Form)**
- 진행도(Progress Bar)를 상단에 표시해 줘 (예: `[■■■□□□] 3/6`).
- 유저가 질문(나이, 키, 수면시간 등)에 답할 때마다 새로고침 없이 다음 질문 조각으로 부드럽게 넘어가는 폼 구조를 짜줘 (Form tag 안에 `hx-post="/api/submit-step"` 등의 속성 포함).

**③ `loading.html` (대기/분석 화면)**
- 깜빡이는 애니메이션 효과(Tailwind의 `animate-pulse` 등 사용).
- 텍스트: "990원어치 보충제 섭취 중...", "국민건강보험공단 데이터와 대결 중..."
- 이 화면이 렌더링된 후 2~3초 뒤에 자동으로 `/api/get-result`를 호출하여 결과를 가져오도록 `hx-get`과 `hx-trigger="load delay:2.5s"` 속성을 넣어줘.

**④ `result.html` (결과 및 페이월 화면)**
- `is_paid` 변수(Boolean)를 Jinja2로 받아서 화면을 분기해 줘.
- **if not is_paid:**
  - 알파벳 등급(예: B-)과 칭호 노출.
  - 하단 상세 정보 영역은 CSS `blur-md` 클래스로 흐리게 처리(모자이크)하고 자물쇠 아이콘 배치.
  - "잠금 해제하기 (출시 특가 990원)" 결제 버튼 노출. 버튼 클릭 시 토스페이먼츠 결제 팝업 JS 함수 호출 유도.
- **if is_paid:**
  - 블러를 모두 해제하고 상세 AI 팩트폭력 분석, 예상 취약 질병, 추천 루틴 텍스트를 깔끔한 박스 UI로 렌더링.

## 3. Action Required
- 위의 설명에 따라 `base.html`, `index.html`, 그리고 `components/` 폴더 안의 4개 파일 코드를 작성해 줘.
- HTMX를 통해 화면이 넘어갈 때 부드러운 Fade-in/Fade-out 효과가 나도록 간단한 커스텀 CSS(`static/css/style.css` 또는 `<style>` 태그 내)도 추가해 줘.

---

## ✅ 변경 사항 (구현 완료 기준)

### step_form.html / step1_form.html
- **진행도 게이지 6→10으로 변경**: 질문이 6개에서 10개로 확장되어 `{{ step }}/10`, `range(1, 11)` 로 업데이트
- step1_form.html 동일하게 `1/10`, `range(1, 11)` 반영

### result.html
- **가챠 결과 공개 연출 추가**: 화면 진입 시 캐릭터 → 등급 뱃지 → 타이틀 → 스탯 순으로 순차 공개 (JS 타임라인)
- **스탯바 UI 개선**: 단순 텍스트 레이블에서 시각적 게이지 바(`stat-bar`, `stat-bar-fill`, `data-width` 속성)로 교체 + 진입 시 0→실제값 채움 애니메이션
- **히든 캐릭터 감지 배지**: `character_id`가 히든 6종 중 하나면 `⚠ HIDDEN ENTITY DETECTED ⚠` 빨간 텍스트 표시, 일반이면 `[ SCAN COMPLETE ]` 노란 텍스트
- **캐릭터 스프라이트**: `.pixel-sprite-animated` 클래스 적용하여 Idle 애니메이션 활성화
- **초기 opacity:0**: grade-badge, char-display, char-title, stat-overview 모두 시작 시 숨김 처리 후 순차 공개

### 추가된 컴포넌트
- `step1_form.html`: Step 1 전용 템플릿 (성별 + 나이 혼합 입력) — 원래 spec에는 없었으나 UX상 별도 분리

### Step 5 질문 재설계 (셔틀런 → 일상어)
셔틀런(20m 왕복 달리기)은 학창 시절 체육 수업을 떠올려야 알 수 있어 일반인 이해도가 낮음.
**백엔드 값(running_count 65/50/35/20/0)은 그대로 유지**하고 질문·선택지 텍스트만 일상 언어로 전면 교체.

| 변경 전 | 변경 후 |
|--------|--------|
| `"20m 셔틀런 기록 또는 달리기는?"` | `"지금 당장 달리기를 한다면?"` |
| 🏃 달리기 매우 잘함 / `셔틀런 60회 이상` | 🏃 뛰면서 전화통화도 거뜬하다 / `1km 5분대` |
| 🏃 달리기 잘하는 편 / `셔틀런 40~60회` | 🏃 1km 정도는 쉬지 않고 달린다 / `1km 6~7분대` |
| 🚶 평균 수준 / `셔틀런 25~40회` | 🚶 뛰다가 중간에 걷게 된다 / `1km 8~10분대` |
| 🐌 달리기 苦手 / `셔틀런 25회 미만` | 🐌 100m만 뛰어도 숨이 턱까지 찬다 / `계단도 힘든 수준` |
| 🪑 운동? 그게 뭔데 | 🪑 달리기는 버스 놓칠 때만 한다 |
