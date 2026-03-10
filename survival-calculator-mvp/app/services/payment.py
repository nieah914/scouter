"""
토스페이먼츠 결제 검증 로직
- 로그인 없는 LocalStorage 토큰 기반 인증
- 결제 승인(Confirm) API 호출
- Supabase DB is_paid 업데이트
"""
import httpx
import base64
from fastapi import HTTPException

from app.config import get_settings
from app.database.db_client import get_supabase


TOSS_CONFIRM_URL = "https://api.tosspayments.com/v1/payments/confirm"


async def confirm_payment(
    payment_key: str,
    order_id: str,
    amount: int,
    user_token: str,
) -> dict:
    """
    토스페이먼츠 결제 승인 요청 및 DB 업데이트

    반환: { "success": bool, "message": str }
    """
    settings = get_settings()

    # 금액 검증 (990원인지 확인)
    if amount != 990:
        raise HTTPException(status_code=400, detail="결제 금액이 올바르지 않습니다.")

    # 토스페이먼츠 Basic Auth 헤더 생성
    secret_key = settings.toss_secret_key
    credentials = base64.b64encode(f"{secret_key}:".encode()).decode()

    # 토스 승인 API 호출
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                TOSS_CONFIRM_URL,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/json",
                },
                json={
                    "paymentKey": payment_key,
                    "orderId": order_id,
                    "amount": amount,
                },
                timeout=10.0,
            )
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="결제 서버 응답 시간 초과")

    if response.status_code != 200:
        error_data = response.json()
        raise HTTPException(
            status_code=400,
            detail=f"결제 승인 실패: {error_data.get('message', '알 수 없는 오류')}"
        )

    # DB 업데이트: is_paid = True
    await _update_payment_status(user_token, order_id)

    return {"success": True, "message": "결제가 완료되었습니다."}


async def _update_payment_status(user_token: str, order_id: str) -> None:
    """Supabase DB에서 해당 토큰 유저의 is_paid를 True로 업데이트"""
    try:
        db = get_supabase()
        db.table("users").update({
            "is_paid": True,
            "order_id": order_id,
        }).eq("user_token", user_token).execute()
    except Exception as e:
        # DB 업데이트 실패해도 결제는 이미 완료됨 - 로그만 기록
        print(f"[ERROR] DB 업데이트 실패 (token: {user_token}): {e}")


async def check_payment_status(user_token: str) -> bool:
    """토큰으로 결제 여부 확인"""
    try:
        db = get_supabase()
        result = (
            db.table("users")
            .select("is_paid")
            .eq("user_token", user_token)
            .single()
            .execute()
        )
        return result.data.get("is_paid", False) if result.data else False
    except Exception:
        return False
