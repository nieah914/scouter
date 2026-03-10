# Task: Toss Payments Integration & No-Login Authorization Flow
결제 모델은 '출시 특가 990원'이며, 유저의 이탈을 막기 위해 **회원가입/로그인 없이** 진행해.
브라우저의 `LocalStorage`와 `app/services/payment.py`를 활용해 결제 승인 및 권한 부여(매직 링크) 로직을 구현해 줘.

## 1. No-Login Authorization (Local Storage)
- 사용자가 테스트 폼(1~6번)을 제출하고 무료 결과를 생성할 때, 백엔드는 고유한 UUID(예: `user_token`)를 생성해서 DB(Supabase)에 임시로 저장해 줘.
- 이 `user_token`을 프론트엔드(`result.html`)로 넘겨주고, 자바스크립트를 이용해 유저 브라우저의 `localStorage.setItem('user_token', ...)`으로 저장하도록 렌더링해 줘.

## 2. Toss Payments Widget Integration (Frontend)
- `templates/components/result.html` 내의 '990원 결제' 버튼 영역에 토스페이먼츠 결제위젯 Javascript SDK(`https://js.tosspayments.com/v2/standard`)를 연동해 줘.
- 버튼을 누르면 `<div id="payment-widget"></div>` 영역이 팝업 또는 인라인으로 뜨도록 해줘.
- **결제 금액:** 990원
- **결제 수단:** 신용카드, 간편결제(토스, 카카오페이 등)만 허용해. (가상계좌, 일반 계좌이체는 수수료가 비싸므로 절대 노출하지 마!)
- 결제 요청 시 `orderId`와 함께 아까 로컬스토리지에 저장한 `user_token`을 결제 성공 리다이렉트 URL 파라미터로 같이 넘겨줘. (예: `/api/payment/success?user_token=xxx`)

## 3. Payment Verification & Result Unlock (Backend)
`app/services/payment.py`와 라우터(`api.py`)를 작성해 줘.
- **결제 검증 API (`/api/payment/success`):** 
  토스에서 리다이렉트 되어 넘어온 `paymentKey`, `orderId`, `amount`(990원)를 받아서 토스페이먼츠 승인(Confirm) API로 POST 요청을 보내 검증해 줘.
- **DB 업데이트:** 
  승인이 완료되면, 함께 넘어온 `user_token`을 이용해 DB에서 해당 유저의 `is_paid` 상태를 `True`로 업데이트해 줘.
- **화면 언락 (HTMX Swap):** 
  상태가 업데이트되면, 백엔드는 블러(모자이크)가 해제된 상세 리포트 HTML 조각(`result.html`의 유료 버전 렌더링)을 반환하여 HTMX가 화면 이탈 없이 교체하도록 해줘.

## 4. CS Defense (결제 전 안내 및 매직 링크)
- 프론트엔드 결제 버튼 바로 위에 작은 글씨로 아래 문구를 필수로 삽입해 줘.
  > *"본 서비스는 로그인 없이 진행됩니다. 결제 후 제공되는 '영구 보관 링크' 분실/캐시 삭제 시 환불이 불가하오니 꼭 캡처해 주세요."*
- 결제 완료 후 렌더링 되는 화면 상단에 '내 결과 매직 링크 복사' 버튼(예: `https://our-domain.com/result?token=xxx`)을 제공하는 코드를 짜줘.

## 5. Action Required
1. 프론트엔드(`result.html`)에 들어갈 토스페이먼츠 위젯 JS 스니펫과 로컬 스토리지 핸들링 코드를 작성해 줘.
2. 백엔드 `payment.py`에 토스 승인 API 호출 로직을 작성해 줘.

---

## ✅ 변경 사항 (버그 수정)

### 결제 실패 URL `/api` prefix 누락 수정
`api.py` 결제 실패 응답에서 HTMX hx-get URL이 `/api` prefix를 빠뜨리고 있어서 404 발생하던 버그 수정:

```python
# 수정 전 (버그)
hx-get="/components/landing"

# 수정 후
hx-get="/api/components/landing"
```

### Task 06 전용 라우터 흐름 참고
- `GET /api/payment/success` → `confirm_payment()` → `_render_paid_result()` → result.html(is_paid=True) 반환
- `GET /api/payment/fail` → 실패 안내 HTML + 처음으로 돌아가기 버튼
- `GET /api/result?token=` → 매직 링크로 유료 결과 재접근
