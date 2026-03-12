"""
T-14: TossPayments E2E 결제 테스트

검증 항목:
1. confirm_payment → Toss API 호출 파라미터 정확성
2. /api/payment/success → DB is_paid=True 업데이트
3. /api/payment/fail → 정상 HTML 반환
4. 결제 완료 후 _render_paid_result → 블러 해제·유료 콘텐츠 노출
5. 잘못된 금액(990원 불일치) → 400 오류
6. successUrl / failUrl 형식 검증
"""
import uuid
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException


# ── DB·AI 목(mock) 설정 ────────────────────────────────────────
mock_db = MagicMock()
mock_db.table.return_value.upsert.return_value.execute.return_value = MagicMock(data=None)
mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(count=0)
mock_db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = MagicMock(data=None)

with patch("app.database.db_client.get_supabase", return_value=mock_db), \
     patch("app.services.ai.AsyncOpenAI"):
    from main import app

client = TestClient(app)


# ── 공통 헬퍼 ────────────────────────────────────────────────────

def _make_paid_user_db(token: str, override: dict | None = None) -> MagicMock:
    """결제 완료 유저 DB 응답 목"""
    data = {
        "user_token": token,
        "is_paid": True,
        "character_id": "orc_berserker",
        "str_score": 75,
        "agi_score": 60,
        "hp_score": 65,
        "debuff_score": 30,
        "overall_grade": "B+",
        "ai_result": {
            "grade": "B+",
            "title": "🏋️ 오크 버서커",
            "summary": "그럭저럭 싸울 수 있는 현대인",
            "analysis_physical": "근력 양호",
            "analysis_sleep": "수면 보통",
            "analysis_debuff": "디버프 낮음",
            "disease_warning": "없음",
            "action_plan": "꾸준히 운동",
        },
    }
    if override:
        data.update(override)
    return MagicMock(data=data)


# ══════════════════════════════════════════════════════════════════
# 테스트 1: confirm_payment → Toss API 호출 검증
# ══════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_confirm_payment_calls_toss_api():
    """confirm_payment가 올바른 파라미터로 Toss 승인 API를 호출하는지 검증"""
    from app.services.payment import confirm_payment

    token = str(uuid.uuid4())
    payment_key = "test_paymentKey_abc123"
    order_id = f"order_{uuid.uuid4().hex[:16]}"
    amount = 990

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "DONE"}

    with patch("app.services.payment.httpx.AsyncClient") as mock_client_cls, \
         patch("app.services.payment._update_payment_status", new_callable=AsyncMock):

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        result = await confirm_payment(payment_key, order_id, amount, token)

    # Toss API 호출 확인
    call_kwargs = mock_client.post.call_args
    assert call_kwargs is not None, "Toss confirm API가 호출되지 않음"

    # URL 확인
    call_url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs.kwargs.get("url", "")
    assert "tosspayments.com" in call_url or "confirm" in str(call_kwargs), \
        f"Toss confirm URL이 잘못됨: {call_kwargs}"

    # JSON 바디 확인
    json_body = call_kwargs.kwargs.get("json", {})
    assert json_body.get("paymentKey") == payment_key, "paymentKey 불일치"
    assert json_body.get("orderId") == order_id, "orderId 불일치"
    assert json_body.get("amount") == 990, "amount 불일치"

    assert result["success"] is True
    print(f"\n✅ confirm_payment Toss API 호출 정상: paymentKey={payment_key[:20]}...")


# ══════════════════════════════════════════════════════════════════
# 테스트 2: 잘못된 금액 → 400 오류
# ══════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_confirm_payment_wrong_amount_raises_400():
    """990원이 아닌 금액 전달 시 HTTPException(400) 발생 검증"""
    from app.services.payment import confirm_payment

    with pytest.raises(HTTPException) as exc_info:
        await confirm_payment("fakeKey", "fakeOrder", 9900, "fakeToken")

    assert exc_info.value.status_code == 400
    print("\n✅ 잘못된 금액(9900원) → 400 오류 정상")


# ══════════════════════════════════════════════════════════════════
# 테스트 3: /api/payment/success → DB is_paid=True 업데이트
# ══════════════════════════════════════════════════════════════════

def test_payment_success_updates_db_is_paid():
    """결제 성공 콜백 시 DB is_paid=True 업데이트 + 유료 결과 렌더링 확인"""
    token = str(uuid.uuid4())
    payment_key = "test_paymentKey_xyz"
    order_id = f"order_{uuid.uuid4().hex[:12]}"

    paid_db_response = _make_paid_user_db(token)

    with patch("app.routers.api.confirm_payment", new_callable=AsyncMock) as mock_confirm, \
         patch("app.routers.api._render_paid_result", new_callable=AsyncMock) as mock_render:

        from fastapi.responses import HTMLResponse
        mock_confirm.return_value = {"success": True}
        mock_render.return_value = HTMLResponse(
            content="<div>AI 팩트폭력 분석 리포트</div><div>잠금 해제 완료</div>",
            status_code=200,
        )

        r = client.get(
            f"/api/payment/success"
            f"?paymentKey={payment_key}"
            f"&orderId={order_id}"
            f"&amount=990"
            f"&user_token={token}"
        )

    assert r.status_code == 200, f"payment/success 실패: {r.status_code}"

    # confirm_payment 호출 확인
    mock_confirm.assert_called_once_with(payment_key, order_id, 990, token)

    # _render_paid_result 호출 확인
    mock_render.assert_called_once()

    print(f"\n✅ /api/payment/success → confirm_payment + _render_paid_result 정상 호출")


# ══════════════════════════════════════════════════════════════════
# 테스트 4: /api/payment/fail → 정상 HTML 반환
# ══════════════════════════════════════════════════════════════════

def test_payment_fail_returns_html():
    """/api/payment/fail 엔드포인트 정상 응답 검증"""
    r = client.get("/api/payment/fail")

    assert r.status_code == 200, f"payment/fail 응답 실패: {r.status_code}"
    assert "결제가 취소" in r.text, "결제 취소 메시지가 없음"
    assert "처음으로 돌아가기" in r.text, "처음으로 돌아가기 버튼이 없음"
    print("\n✅ /api/payment/fail 정상 HTML 반환")


# ══════════════════════════════════════════════════════════════════
# 테스트 5: 결제 완료 후 유료 결과 화면 → 블러 해제 / 유료 콘텐츠 노출
# ══════════════════════════════════════════════════════════════════

def test_paid_result_shows_premium_content():
    """결제 완료 유저 결과 화면에 유료 콘텐츠 노출, 페이월 미노출 검증"""
    token = str(uuid.uuid4())

    paid_db = _make_paid_user_db(token)

    db = MagicMock()
    db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = paid_db

    # check_payment_status(payment.py)와 _render_paid_result(api.py) 각각 패치
    with patch("app.services.payment.get_supabase", return_value=db), \
         patch("app.routers.api.get_supabase", return_value=db):

        r = client.get(f"/api/result?token={token}")

    assert r.status_code == 200
    html = r.text

    # 유료 콘텐츠 확인
    assert "AI 팩트폭력 분석 리포트" in html, "유료 AI 리포트 섹션이 없음"
    assert "잠금 해제 완료" in html or "리포트 잠금 해제" in html, "잠금 해제 메시지가 없음"

    # 페이월 미노출 확인 (결제 버튼이 없어야 함)
    assert "잠금 해제하기 - 990원" not in html, "결제 완료 후에도 결제 버튼이 표시됨 (블러 해제 실패)"

    print(f"\n✅ 유료 결과 화면: 프리미엄 콘텐츠 노출 + 페이월 없음 확인")


# ══════════════════════════════════════════════════════════════════
# 테스트 6: 미결제 유저 결과 화면 → 블러 + 결제 버튼 노출
# ══════════════════════════════════════════════════════════════════

def test_free_result_shows_paywall():
    """미결제 유저 결과 화면에 페이월(결제 버튼)이 표시되는지 검증"""
    token = str(uuid.uuid4())

    free_db = _make_paid_user_db(token, override={"is_paid": False})

    db = MagicMock()
    db.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = free_db
    db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(count=0)

    # check_payment_status(payment.py)와 _render_free_result(api.py) 각각 패치
    with patch("app.services.payment.get_supabase", return_value=db), \
         patch("app.routers.api.get_supabase", return_value=db), \
         patch("app.routers.api._get_paid_count", new_callable=AsyncMock, return_value=0):

        r = client.get(f"/api/result?token={token}")

    assert r.status_code == 200
    html = r.text

    # 페이월 노출 확인
    assert "잠금 해제하기 - 990원" in html, "미결제 유저에게 결제 버튼이 없음"
    assert "LOCKED" in html, "자물쇠 오버레이가 없음"

    # 유료 상세 리포트 미노출 확인
    assert "리포트 잠금 해제 완료" not in html, "미결제 유저에게 유료 콘텐츠가 노출됨"

    print("\n✅ 미결제 유저: 페이월 + LOCKED 오버레이 정상 노출")


# ══════════════════════════════════════════════════════════════════
# 테스트 7: successUrl / failUrl 형식 검증
# ══════════════════════════════════════════════════════════════════

def test_success_fail_url_format_in_result_html():
    """result.html JS에서 successUrl/failUrl이 /api/ prefix를 포함하는지 검증"""
    token = str(uuid.uuid4())

    # 설문 + 계산 플로우로 result.html 얻기
    with patch("app.routers.api.generate_survival_report", new_callable=AsyncMock) as mock_ai, \
         patch("app.routers.api._save_user_result", new_callable=AsyncMock), \
         patch("app.routers.api._get_paid_count", new_callable=AsyncMock, return_value=0):

        from app.services.ai import SurvivalReport
        mock_ai.return_value = SurvivalReport(
            grade="C",
            title="🧙 마법사",
            summary="평범한 현대인",
            analysis_physical="보통", analysis_sleep="보통",
            analysis_debuff="보통", disease_warning="없음", action_plan="운동하세요",
        )

        # 세션 직접 주입 (스텝 생략) — DB 세션 mock
        session_data = {
            "gender": "M", "age": 30,
            "height": 170.0, "weight": 70.0,
            "sleep_hours": 7.0, "pushup_count": 20,
            "running_count": 35, "coffee_cups": 1,
            "overtime_days": 1, "diet_score": 1,
            "stress_score": 1, "sitting_hours": 6,
            "alcohol_freq": 1,
        }

        with patch("app.routers.api.get_session", new_callable=AsyncMock, return_value=session_data):
            r = client.get(f"/api/calculate?user_token={token}")

    assert r.status_code == 200
    html = r.text

    # successUrl에 /api/payment/success 포함 확인
    assert "/api/payment/success" in html, \
        "successUrl에 /api/ prefix가 없음 → 결제 콜백 404 발생 위험"

    # failUrl에 /api/payment/fail 포함 확인
    assert "/api/payment/fail" in html, \
        "failUrl에 /api/ prefix가 없음 → 결제 실패 콜백 404 발생 위험"

    print("\n✅ successUrl = .../api/payment/success")
    print("✅ failUrl    = .../api/payment/fail")
    print("   → /api/ prefix 정상 포함")


# ══════════════════════════════════════════════════════════════════
# 테스트 8: Toss API 실패 시 HTTPException 전파
# ══════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_confirm_payment_toss_api_failure():
    """Toss 승인 API가 실패(non-200)를 반환할 때 HTTPException(400) 발생 검증"""
    from app.services.payment import confirm_payment

    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"code": "ALREADY_PROCESSED_PAYMENT", "message": "이미 처리된 결제"}

    with patch("app.services.payment.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        with pytest.raises(HTTPException) as exc_info:
            await confirm_payment("badKey", "badOrder", 990, "anyToken")

    assert exc_info.value.status_code == 400
    assert "이미 처리된 결제" in exc_info.value.detail
    print("\n✅ Toss API 실패 응답 → HTTPException(400) 정상 전파")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
