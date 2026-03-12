"""
DB 기반 세션 관리 (Vercel 서버리스 환경용)
- Supabase sessions 테이블 우선 사용
- sessions 테이블 미존재(로컬 개발) 시 인메모리 폴백 자동 전환
- Vercel 배포 전 Supabase SQL Editor에서 sessions 테이블 생성 필요
"""
from app.database.db_client import get_supabase

# 로컬 개발용 인메모리 폴백 (sessions 테이블 없을 때 사용)
_fallback_store: dict[str, dict] = {}


async def get_session(user_token: str) -> dict:
    """세션 데이터 조회. DB 실패 시 인메모리 폴백."""
    if not user_token:
        return {}
    try:
        db = get_supabase()
        result = (
            db.table("sessions")
            .select("data")
            .eq("user_token", user_token)
            .single()
            .execute()
        )
        if result.data:
            return result.data.get("data", {})
        # DB에 없으면 폴백 확인
        return _fallback_store.get(user_token, {})
    except Exception:
        return _fallback_store.get(user_token, {})


async def update_session(user_token: str, updates: dict) -> dict:
    """기존 세션에 updates를 병합하고 저장. 병합된 세션 반환."""
    session = await get_session(user_token)
    session.update(updates)
    saved_to_db = await _save_session_db(user_token, session)
    if not saved_to_db:
        # DB 저장 실패 → 인메모리 폴백
        _fallback_store[user_token] = session
    return session


async def _save_session_db(user_token: str, data: dict) -> bool:
    """세션 전체를 DB에 upsert. 성공 여부 반환."""
    try:
        db = get_supabase()
        db.table("sessions").upsert(
            {"user_token": user_token, "data": data},
            on_conflict="user_token",
        ).execute()
        return True
    except Exception as e:
        print(f"[WARN] DB 세션 저장 실패 → 인메모리 폴백 사용 (token: {user_token[:8]}...): {e}")
        return False
