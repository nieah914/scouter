"""
배틀 버튼 동작 진단 테스트
- 전체 스캔 플로우 후 result_link/userToken이 제대로 렌더링되는지 확인
- startBattle() 호출 시 userToken이 비어있는 원인 추적
"""
import re
import uuid
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

# ── DB·AI 목(mock) 설정 ────────────────────────────────────
# 실제 Supabase/OpenAI 없이 테스트
mock_db = MagicMock()
mock_db.table.return_value.upsert.return_value.execute.return_value = MagicMock(data=None)
mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(count=0)

with patch("app.database.db_client.get_supabase", return_value=mock_db), \
     patch("app.services.ai.AsyncOpenAI"):
    from main import app

client = TestClient(app)

# ── 헬퍼 ─────────────────────────────────────────────────────

def full_scan_flow(token: str) -> str:
    """10단계 스캔 플로우 완주 → /api/calculate 응답 HTML 반환"""

    # DB 세션 대신 로컬 딕셔너리로 세션 시뮬레이션
    _store: dict = {}

    async def mock_update(user_token, updates):
        _store.setdefault(user_token, {}).update(updates)
        return _store[user_token]

    async def mock_get(user_token):
        return _store.get(user_token, {})

    with patch("app.routers.api.update_session", side_effect=mock_update), \
         patch("app.routers.api.get_session", side_effect=mock_get):

        # Step 1
        r = client.post("/api/submit-step1", data={"user_token": token, "gender": "M", "age": 30})
        assert r.status_code == 200, f"step1 실패: {r.status_code}"

        # Step 2~10
        payloads = [
            (2, {"height": "175", "weight": "70"}),
            (3, {"sleep_hours": "7"}),
            (4, {"pushup_count": "30"}),
            (5, {"running_count": "50"}),
            (6, {"debuff": "1_1"}),
            (7, {"diet": "1"}),
            (8, {"stress": "1"}),
            (9, {"sitting": "6"}),
            (10, {"alcohol": "1"}),
        ]
        for step, fields in payloads:
            data = {"step": str(step), "user_token": token, **fields}
            r = client.post("/api/submit-step", data=data)
            assert r.status_code == 200, f"step{step} 실패: {r.status_code}"

        # 최종 계산
        with patch("app.routers.api.generate_survival_report", new_callable=AsyncMock) as mock_ai, \
             patch("app.routers.api._save_user_result", new_callable=AsyncMock), \
             patch("app.routers.api._get_paid_count", new_callable=AsyncMock, return_value=0):

            from app.services.ai import SurvivalReport
            mock_ai.return_value = SurvivalReport(
                grade="B+",
                title="🏋️ 오크 버서커",
                summary="그럭저럭 싸울 수 있는 현대인",
                analysis_physical="근력 양호", analysis_sleep="수면 보통",
                analysis_debuff="디버프 낮음", disease_warning="없음", action_plan="꾸준히 운동",
            )
            r = client.get(f"/api/calculate?user_token={token}")

    assert r.status_code == 200, f"calculate 실패: {r.status_code}"
    return r.text


# ══════════════════════════════════════════════════════════════
# 테스트 1: /api/calculate 응답에 result_link가 포함되는지
# ══════════════════════════════════════════════════════════════
def test_result_link_is_rendered():
    token = str(uuid.uuid4())
    html = full_scan_flow(token)

    # result_link가 HTML 안에 존재해야 함
    assert "result_link" not in html or token in html, \
        "result_link 변수가 렌더링되지 않고 그대로 남아있음"

    # 실제로 토큰이 HTML에 포함됐는지 확인
    assert token in html, \
        f"응답 HTML에 user_token({token})이 없음 → result_link 미렌더링 의심"

    print(f"\n✅ result_link 정상 렌더링 확인: token={token[:8]}...")


# ══════════════════════════════════════════════════════════════
# 테스트 2: JS 변수 resultLink에 토큰이 들어있는지
# ══════════════════════════════════════════════════════════════
def test_js_result_link_contains_token():
    token = str(uuid.uuid4())
    html = full_scan_flow(token)

    # window._svResultLink = "http://...?token=<uuid>"  패턴 확인
    match = re.search(r'window\._svResultLink\s*=\s*"([^"]*)"', html)
    assert match, "JS 변수 'window._svResultLink' 를 찾을 수 없음"

    result_link_val = match.group(1)
    print(f"\n[DEBUG] _svResultLink 값: {result_link_val}")

    assert token in result_link_val, \
        f"_svResultLink에 token이 없음!\n_svResultLink={result_link_val}\ntoken={token}"

    print("✅ JS _svResultLink 안에 token 정상 포함")


# ══════════════════════════════════════════════════════════════
# 테스트 3: startBattle 함수가 HTML 내에 정의되어 있는지
# ══════════════════════════════════════════════════════════════
def test_start_battle_function_exists():
    token = str(uuid.uuid4())
    html = full_scan_flow(token)

    assert "function startBattle" in html, "startBattle 함수가 result.html에 없음"
    assert "배틀을 신청하려면 먼저 스캔을 완료해야 합니다" in html, \
        "startBattle 내 에러 메시지가 HTML에 없음"

    print("\n✅ startBattle 함수 정상 존재")


# ══════════════════════════════════════════════════════════════
# 테스트 4: userToken 추출 로직이 JS 안에 존재하는지
# ══════════════════════════════════════════════════════════════
def test_user_token_extraction_logic_exists():
    token = str(uuid.uuid4())
    html = full_scan_flow(token)

    # 전역 변수 방식으로 리팩터된 코드 확인
    assert "window._svToken" in html, \
        "window._svToken 전역 변수가 없음 → 리팩터 미반영"
    assert "window._svResultLink" in html, \
        "window._svResultLink 전역 변수가 없음"
    assert "_getToken()" in html, \
        "_getToken() 헬퍼 함수가 없음"

    print("\n✅ 전역 변수 기반 token 추출 로직 정상 존재")


def test_start_battle_uses_get_token():
    """startBattle이 클로저가 아닌 _getToken()으로 토큰을 읽는지 확인"""
    token = str(uuid.uuid4())
    html = full_scan_flow(token)

    # startBattle 함수 내에서 _getToken() 호출 확인
    match = re.search(r'function startBattle\(\)\s*\{(.*?)\}', html, re.DOTALL)
    assert match, "startBattle 함수를 찾을 수 없음"
    func_body = match.group(1)
    assert "_getToken()" in func_body, \
        f"startBattle이 _getToken()을 사용하지 않음!\n함수 본문:\n{func_body[:200]}"

    print("\n✅ startBattle이 _getToken() 사용 확인")


# ══════════════════════════════════════════════════════════════
# 테스트 5: loading.html → /api/calculate 토큰 전달 경로
#           (빈 토큰이면 landing으로 redirect 되는지)
# ══════════════════════════════════════════════════════════════
def test_calculate_with_empty_token_returns_landing():
    # get_session이 빈 dict 반환 → 세션 없음 → landing
    with patch("app.routers.api.get_session", new_callable=AsyncMock, return_value={}), \
         patch("app.routers.api._get_paid_count", new_callable=AsyncMock, return_value=0):
        r = client.get("/api/calculate?user_token=")
    assert r.status_code == 200
    # 세션 없으면 landing 화면이 와야 함
    html = r.text
    assert "스캐닝 시작하기" in html or "SYSTEM ALERT" in html or "LOADING" in html, \
        "빈 토큰 시 landing으로 돌아가지 않음"
    print("\n✅ 빈 토큰 → landing 리다이렉트 정상")


# ══════════════════════════════════════════════════════════════
# 테스트 6: 전체 흐름 통합 진단 (핵심)
#           JS 내 userToken 분기 로직을 수동 시뮬레이션
# ══════════════════════════════════════════════════════════════
def test_diagnose_user_token_in_script():
    token = str(uuid.uuid4())
    html = full_scan_flow(token)

    # _svResultLink 값 추출
    match = re.search(r'window\._svResultLink\s*=\s*"([^"]*)"', html)
    assert match, "_svResultLink를 찾을 수 없음"
    result_link_val = match.group(1)

    # Jinja2가 HTML-escape 했는지 확인 (&amp; 문제)
    if "&amp;" in result_link_val:
        print(f"\n⚠️  Jinja2가 & → &amp; HTML 이스케이프 적용됨!")
        print(f"   _svResultLink = {result_link_val}")
        print("   → new URL()이 깨지거나 searchParams.get('token')이 None 반환 가능!")
    else:
        print(f"\n✅ _svResultLink HTML 이스케이프 없음: {result_link_val}")

    # 토큰이 resultLink 안에 있는지
    assert token in result_link_val, \
        f"⛔ token이 resultLink에 없음\nresultLink={result_link_val}\ntoken={token}"

    # localStorage가 비어있다고 가정했을 때의 Python-side 시뮬레이션
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(result_link_val)
    params = parse_qs(parsed.query)
    extracted_token = params.get("token", [None])[0]

    print(f"\n[시뮬레이션] localStorage 비어있을 때:")
    print(f"  resultLink = {result_link_val}")
    print(f"  new URL(resultLink).searchParams.get('token') = {extracted_token}")

    assert extracted_token == token, \
        f"⛔ 추출된 token이 원본과 다름!\n추출={extracted_token}\n원본={token}"

    print("\n✅ 전체 진단 통과 - 이론적으로 배틀 버튼이 동작해야 함")
    print("\n💡 만약 실제 브라우저에서 여전히 실패한다면:")
    print("   → 브라우저 localStorage를 확인하거나")
    print("   → 서버 재시작 없이 변경사항이 적용되었는지 확인 필요")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
