# Task: Social Proof Nudge (Conversion Rate Optimization)
유저의 990원 결제 전환율을 높이기 위해, `result.html`의 무료 버전(결제 페이월) 영역 하단에 "🔥 현재 OOO명이 생존 리포트를 확인했습니다"라는 실시간 소셜 프루프 넛지를 추가할 거야.

## 1. Backend Logic (`app/routers/api.py` 또는 `stats.py`)
- `get_paid_user_count()` 함수를 작성해 줘.
- DB(Supabase)에 접근해서 `is_paid = True`인 유저 레코드의 총개수(Count)를 가져오는 쿼리를 실행해.
- **[성능/비용 최적화]** 유저가 접속할 때마다 매번 DB에 Count 쿼리를 날리면 트래픽 폭주 시 비용이 발생할 수 있어. 따라서 FastAPI의 `lru_cache`나 전역 변수를 사용해 이 숫자를 10~15분에 한 번만 캐싱(Caching)하도록 처리해 줘.

## 2. Frontend UI (`templates/components/result.html`)
- 결제 위젯/버튼 바로 아래에 넛지 텍스트를 배치해 줘.
- **디자인 (Tailwind CSS):** 시선을 너무 방해하지 않으면서도 라이브(Live) 느낌을 주기 위해 글씨 크기는 작게(`text-sm`), 색상은 은은하게(`text-gray-400`), 불꽃 이모지(🔥)와 함께 텍스트가 부드럽게 점멸하는 애니메이션(`animate-pulse`)을 적용해 줘.
- **[방어 로직]** Jinja2 템플릿 엔진을 사용해서 넘겨받은 `paid_count` 변수가 **100 미만일 경우에는 이 넛지 UI 전체를 아예 렌더링하지 않도록(숨김 처리)** `{% if paid_count >= 100 %}` 조건문을 걸어줘. (초기에 숫자가 너무 적어 보이면 오히려 결제 전환율이 떨어질 수 있기 때문이야.)

## 3. Action Required
1. DB에서 누적 결제자 수를 가져오고 캐싱하는 백엔드 코드를 작성해 줘.
2. `result.html`에 조건부(100명 이상)로 렌더링되는 소셜 프루프 UI 코드를 작성해 줘.

---

## ✅ 변경 사항 (변경 없음, 원래 spec대로 구현)

### 구현 완료 항목
- `_get_paid_count()`: 인메모리 캐싱 변수 `_paid_count_cache` + TTL 600초(10분) 방식으로 구현
- `_get_participant_count()`: 총 참여자 수 (is_paid 무관)
- `result.html` 소셜 프루프: `{% if paid_count and paid_count >= 100 %}` 조건부 렌더링
- 넛지 위치: 결제 버튼 위 (CTA 영역 내부)
- 디자인: `animate-pulse` + `text-rpg-green font-bold` 강조
