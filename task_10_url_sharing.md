# Task: Result URL Sharing

결과 화면에서 URL을 공유할 수 있는 기능을 추가한다.
무료 결과도 고유 링크로 저장/공유 가능해야 하며, 해당 링크로 재접근 시 결과가 다시 보여야 한다.

---

## ✅ 구현 완료 사항

### 1. result_link 변수 추가 (api.py)

세 엔드포인트 모두에서 `result_link`를 Jinja2 템플릿에 전달:

| 엔드포인트 | result_link 값 |
|-----------|---------------|
| `calculate_result` | `{base_url}api/result?token={user_token}` |
| `_render_paid_result` | magic_link와 동일 (`{base_url}api/result?token={user_token}`) |
| `_render_free_result` | `{base_url}api/result?token={user_token}` |

### 2. _render_free_result 개선 (api.py)

기존: 랜딩 페이지로 리다이렉트 (공유 링크 클릭 시 아무것도 안 보임)
변경: DB에서 유저 결과를 조회하여 무료 결과 화면(`is_paid=False`) 렌더링

```python
# 변경 후 동작 흐름
GET /api/result?token=xxx
  → check_payment_status(token)
    → is_paid=True  → _render_paid_result  (상세 리포트)
    → is_paid=False → _render_free_result  (무료 결과, DB에서 재조회)
```

### 3. 공유 버튼 UI 추가 (result.html)

기존 `📸 결과 공유하기` 단일 버튼 → 두 버튼으로 분리:

```html
<button onclick="shareResult()">📸 공유하기</button>     <!-- Web Share API / 텍스트+URL -->
<button onclick="copyResultLink()">🔗 URL 복사</button>  <!-- URL만 클립보드 복사 -->
```

### 4. JS 함수 변경 (result.html)

**`shareResult()` 개선**: `location.href` 대신 `result_link` (토큰 포함 URL) 사용
```javascript
const resultLink = "{{ result_link }}" || (location.origin + '/api/result?token=' + userToken);

function shareResult() {
    navigator.share({ url: resultLink, ... });  // 토큰 URL로 공유
}
```

**`copyResultLink()` 신규 추가**: URL만 복사. `clipboard.writeText` 실패 시 `prompt()`로 폴백
```javascript
function copyResultLink() {
    navigator.clipboard.writeText(resultLink)
        .then(() => alert('결과 URL이 복사됐습니다!'))
        .catch(() => { prompt('아래 URL을 복사해 주세요:', resultLink); });
}
```

### 공유 URL 동작 정리

| 사용자 | 공유 URL 접근 결과 |
|--------|-----------------|
| 무료 결과 공유 링크 클릭 | 무료 결과 화면 (게이지, 등급, 캐릭터 표시. 상세 리포트는 잠금) |
| 결제 후 매직 링크 클릭 | 전체 상세 리포트 표시 |
| DB에 데이터 없는 토큰 | 랜딩 화면으로 fallback |

---

## ✅ 추가 수정: 브라우저 직접 접근 문제 해결

### 문제
`/api/result?token=xxx`는 HTMX fragment 엔드포인트로 설계되어 있어,
브라우저에서 직접 URL을 입력하면 base.html 레이아웃 없이 fragment HTML만 반환되거나
Supabase 연결 실패 시 `components/landing.html` fragment를 반환하여
CSS/JS 없이 "스캐닝 시작하기" 텍스트만 표시됨.

### 해결

**1. pages.py — `/result` 풀페이지 라우트 추가**
```python
@router.get("/result", response_class=HTMLResponse)
async def result_page(request: Request, token: str = ""):
    return templates.TemplateResponse("result_page.html", {
        "request": request, "token": token,
    })
```

**2. templates/result_page.html 신규 생성**
```html
{% extends "base.html" %}
{% block content %}
<div hx-get="/api/result?token={{ token }}"
     hx-trigger="load"
     hx-target="#main-content"
     hx-swap="innerHTML transition:true">
    <div class="text-center py-20 space-y-3">
        <div class="text-rpg-green font-pixel text-sm animate-pulse">⚡ LOADING RESULT... ⚡</div>
        ...
    </div>
</div>
{% endblock %}
```
→ base.html을 상속하여 CSS/JS 포함한 완전한 페이지를 제공.
→ 페이지 로드 시 HTMX가 자동으로 `/api/result?token=xxx` fragment를 `#main-content`에 삽입.

**3. result_link URL 변경**
```python
# 수정 전 (fragment 엔드포인트)
f"{request.base_url}api/result?token={user_token}"

# 수정 후 (풀페이지 엔드포인트)
f"{request.base_url}result?token={user_token}"
```

### URL 흐름 정리

```
브라우저에서 http://localhost:8000/result?token=xxx 접근
    ↓
pages.py GET /result → result_page.html 렌더링 (base.html 상속, 레이아웃 완전)
    ↓
HTMX hx-trigger="load" → GET /api/result?token=xxx (fragment 요청)
    ↓
api.py result_by_token
    → is_paid=True  → _render_paid_result (상세 리포트 fragment)
    → is_paid=False → _render_free_result (무료 결과 fragment, DB에서 조회)
    ↓
#main-content에 결과 삽입 완료
```
