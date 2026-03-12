"""
HTMX 비동기 통신 API 라우터
- 컴포넌트 조각(Fragment) 서빙
- 스텝 폼 제출 처리
- 결과 계산 및 AI 호출
- 결제 검증
- 소셜 프루프
"""
import uuid
import time
from typing import Optional
from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.stats import (
    calculate_bmi_status, convert_raw_to_scores,
    determine_character, calculate_overall_grade,
    get_stat_labels,
)
from app.services.ai import generate_survival_report, predict_diseases
from app.services.payment import confirm_payment, check_payment_status
from app.services.session import get_session, update_session
from app.database.db_client import get_supabase
from app.config import get_settings

import os as _os
router = APIRouter()
_BASE_DIR = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
templates = Jinja2Templates(directory=_os.path.join(_BASE_DIR, "templates"))

# 커스텀 필터 등록
def format_number(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)

templates.env.filters["format_number"] = format_number


# ============================================================
# HTMX 컴포넌트 서빙
# ============================================================

@router.get("/components/landing", response_class=HTMLResponse)
async def component_landing(request: Request):
    """랜딩 화면 조각"""
    participant_count = await _get_participant_count()
    return templates.TemplateResponse("components/landing.html", {
        "request": request,
        "participant_count": participant_count,
    })


@router.get("/components/battle", response_class=HTMLResponse)
async def component_battle(
    request: Request,
    challenger: str = Query(default=""),
    defender: str = Query(default=""),
):
    """친구 배틀 결과 fragment"""
    # Challenger 조회 (필수)
    challenger_data = await _fetch_user_for_battle(challenger)
    if not challenger_data:
        return HTMLResponse("""
        <div class="text-center py-16 space-y-4">
            <div class="text-4xl">❓</div>
            <div class="font-pixel text-rpg-red text-sm">도전자 데이터를 찾을 수 없습니다</div>
            <div class="text-rpg-gray text-xs">링크가 만료되었거나 잘못된 토큰입니다.</div>
            <button onclick="location.href='/'"
                    class="text-rpg-green border border-rpg-green rounded px-4 py-2 text-sm font-pixel">
                나도 측정하기
            </button>
        </div>""")

    # Defender 조회 (없으면 안내 화면)
    defender_data = await _fetch_user_for_battle(defender) if defender else None
    if not defender_data:
        return HTMLResponse(f"""
        <div class="space-y-4">
            <div class="text-center font-pixel text-rpg-yellow text-xs tracking-widest">⚔ BATTLE CHALLENGE ⚔</div>
            <div class="border-2 border-rpg-border bg-rpg-panel rounded-lg p-6 text-center space-y-4">
                <div class="text-4xl">{challenger_data['emoji']}</div>
                <div class="font-pixel text-rpg-green text-sm">{challenger_data['character_name']}</div>
                <div class="text-rpg-gray text-xs">배틀 스코어: <span class="text-white font-bold">{challenger_data['battle_score']}</span></div>
                <div class="border-t border-rpg-border pt-4 space-y-2">
                    <div class="text-rpg-yellow text-sm font-pixel">⚔ 당신에게 배틀을 신청했습니다!</div>
                    <div class="text-rpg-gray text-xs">먼저 당신의 전투력을 측정하면 배틀 결과를 확인할 수 있어요</div>
                </div>
            </div>
            <button onclick="location.href='/'"
                    class="w-full bg-rpg-green text-black font-pixel font-bold py-3 rounded-lg text-sm">
                ⚡ 나도 측정하고 배틀하기
            </button>
        </div>""")

    # 배틀 스코어 계산
    c_score = _calc_battle_score(challenger_data)
    d_score = _calc_battle_score(defender_data)
    challenger_data["battle_score"] = c_score
    defender_data["battle_score"] = d_score

    if c_score > d_score:
        winner = "challenger"
        score_diff = c_score - d_score
    elif d_score > c_score:
        winner = "defender"
        score_diff = d_score - c_score
    else:
        winner = "draw"
        score_diff = 0

    # defender의 결과 링크
    my_result_link = f"{request.base_url}result?token={defender}" if defender else ""

    return templates.TemplateResponse("components/battle.html", {
        "request": request,
        "challenger_data": challenger_data,
        "defender_data": defender_data,
        "winner": winner,
        "score_diff": score_diff,
        "my_result_link": my_result_link,
    })


# 스텝별 폼 설정
STEP_CONFIG = {
    1: {
        "stat_label": "[ 기본 정보 스캐닝 ]",
        "question": "용사의 성별과 나이를 알려주세요.",
        "input_type": "mixed_step1",
    },
    2: {
        "stat_label": "[ 피지컬 스탯 측정 ]",
        "question": "키와 몸무게를 입력해 주세요.",
        "input_type": "slider",
        "fields": [
            {"name": "height", "label": "키", "min": 140, "max": 210, "step": 1, "default": 170, "unit": "cm"},
            {"name": "weight", "label": "몸무게", "min": 30, "max": 150, "step": 1, "default": 70, "unit": "kg"},
        ],
    },
    3: {
        "stat_label": "[ HP 스탯 - 회복력 측정 ]",
        "question": "하루 평균 수면 시간은 얼마인가요?",
        "input_type": "card_select",
        "field_name": "sleep_hours",
        "options": [
            {"value": "8", "label": "😴 8시간 이상", "desc": "수면 만렙 / HP 풀충전"},
            {"value": "7", "label": "😊 7시간",     "desc": "권장 수면량 / 양호"},
            {"value": "6", "label": "😐 6시간",     "desc": "약간 부족 / 주의"},
            {"value": "5", "label": "😵 5시간",     "desc": "수면 부족 / 위험"},
            {"value": "4", "label": "💀 4시간 이하", "desc": "좀비 상태 / 매우 위험"},
        ],
    },
    4: {
        "stat_label": "[ 전투력 스탯 측정 ]",
        "question": "1분 동안 최대 푸시업 횟수는?",
        "input_type": "number",
        "fields": [
            {"name": "pushup_count", "label": "1분 푸시업 횟수", "min": 0, "max": 200,
             "placeholder": "예: 30", "unit": "회"},
        ],
    },
    5: {
        "stat_label": "[ AGI 스탯 - 심폐지구력 측정 ]",
        "question": "지금 당장 달리기를 한다면?",
        "input_type": "card_select",
        "field_name": "running_count",
        "options": [
            {"value": "65", "label": "🏃 뛰면서 전화통화도 거뜬하다",   "desc": "1km 5분대 / 전국 상위 10% 수준"},
            {"value": "50", "label": "🏃 1km 정도는 쉬지 않고 달린다",  "desc": "1km 6~7분대 / 상위 30% 수준"},
            {"value": "35", "label": "🚶 뛰다가 중간에 걷게 된다",      "desc": "1km 8~10분대 / 평균 수준"},
            {"value": "20", "label": "🐌 100m만 뛰어도 숨이 턱까지 찬다", "desc": "계단도 힘든 수준 / 하위"},
            {"value": "0",  "label": "🪑 달리기는 버스 놓칠 때만 한다", "desc": "일상 운동량 거의 없음"},
        ],
    },
    6: {
        "stat_label": "[ 디버프 스탯 - 생존 독소 측정 ]",
        "question": "하루 카페인 섭취량과 야근 빈도는?",
        "input_type": "card_select",
        "field_name": "debuff",
        "options": [
            {"value": "0_0",  "label": "☕ 안 마심 + 칼퇴",       "desc": "평화로운 마을 주민 / 디버프 없음"},
            {"value": "1_1",  "label": "☕ 1잔 + 주 1회 야근",     "desc": "약간의 독 상태"},
            {"value": "2_2",  "label": "☕☕ 2잔 + 주 2회 야근",   "desc": "지속적인 독 데미지"},
            {"value": "3_3",  "label": "☕☕☕ 3잔 + 주 3회 야근", "desc": "중독 상태 / 주의"},
            {"value": "5_5",  "label": "💉 4잔+ + 거의 매일 야근", "desc": "카페인 도핑 + 저주 / 위험"},
        ],
    },
    7: {
        "stat_label": "[ 식량 보급 시스템 점검 ]",
        "question": "평소 식사 습관은 어떤가요?",
        "input_type": "card_select",
        "field_name": "diet",
        "options": [
            {"value": "0", "label": "🥗 건강식 위주",          "desc": "채소·단백질 균형 / 식단 만렙"},
            {"value": "1", "label": "🍱 그럭저럭 먹는 편",     "desc": "평균적인 식단 / 무난"},
            {"value": "2", "label": "🍕 배달·패스트푸드 자주", "desc": "나트륨·지방 과다 / 위험"},
            {"value": "3", "label": "🍔 매일 인스턴트",        "desc": "생명 유지만 / 식단 최하위"},
        ],
    },
    8: {
        "stat_label": "[ 정신력 스탯 측정 ]",
        "question": "최근 스트레스 수준은?",
        "input_type": "card_select",
        "field_name": "stress",
        "options": [
            {"value": "0", "label": "😌 스트레스? 뭔데 그게",  "desc": "정신력 풀충전 / 멘탈 강자"},
            {"value": "1", "label": "🙂 가끔 스트레스 받음",   "desc": "관리 가능한 수준 / 양호"},
            {"value": "2", "label": "😤 꽤 스트레스 받는 중",  "desc": "번아웃 경계선 / 주의"},
            {"value": "3", "label": "🤯 지금 폭발 직전",       "desc": "긴급 멘탈 수리 필요 / 위험"},
        ],
    },
    9: {
        "stat_label": "[ 좌식 생활 패턴 분석 ]",
        "question": "하루 평균 앉아있는 시간은?",
        "input_type": "card_select",
        "field_name": "sitting",
        "options": [
            {"value": "4",  "label": "🏃 4시간 미만",  "desc": "활동적인 생활 패턴 / 최상"},
            {"value": "6",  "label": "🚶 4~6시간",      "desc": "적절한 활동량 / 양호"},
            {"value": "10", "label": "🪑 6~10시간",     "desc": "주의 필요한 좌식 / 경계"},
            {"value": "13", "label": "🛋️ 10시간 이상", "desc": "극단적 좌식 / 위험 수준"},
        ],
    },
    10: {
        "stat_label": "[ 독소 내성 최종 검사 ]",
        "question": "음주 빈도는 어떻게 되나요?",
        "input_type": "card_select",
        "field_name": "alcohol",
        "options": [
            {"value": "0", "label": "🚫 거의 안 마심", "desc": "간 클린 / 최상"},
            {"value": "1", "label": "🍺 주 1~2회",     "desc": "적당한 수준 / 양호"},
            {"value": "3", "label": "🍻 주 3~4회",     "desc": "과음 경계 / 주의"},
            {"value": "7", "label": "🥂 거의 매일",    "desc": "간에게 미안함 / 위험"},
        ],
    },
}


@router.get("/components/form/{step}", response_class=HTMLResponse)
async def component_form(request: Request, step: int):
    """스텝별 폼 조각 반환"""
    # Step 1은 전용 템플릿 사용 (성별 + 나이 혼합)
    if step == 1:
        return templates.TemplateResponse("components/step1_form.html", {"request": request})

    if step not in STEP_CONFIG:
        return HTMLResponse("<div>잘못된 단계입니다.</div>", status_code=400)

    config = STEP_CONFIG[step].copy()
    config["step"] = step
    config["request"] = request
    return templates.TemplateResponse("components/step_form.html", config)


# ============================================================
# 스텝 폼 제출 처리
# ============================================================

@router.post("/submit-step", response_class=HTMLResponse)
async def submit_step(
    request: Request,
    step: int = Form(...),
    user_token: str = Form(...),
    gender: Optional[str] = Form(None),
    age: Optional[int] = Form(None),
    height: Optional[float] = Form(None),
    weight: Optional[float] = Form(None),
    sleep_hours: Optional[str] = Form(None),
    pushup_count: Optional[int] = Form(None),
    running_count: Optional[str] = Form(None),
    debuff: Optional[str] = Form(None),
    diet: Optional[str] = Form(None),
    stress: Optional[str] = Form(None),
    sitting: Optional[str] = Form(None),
    alcohol: Optional[str] = Form(None),
):
    """각 단계 답변 저장 후 다음 화면 반환"""

    # 단계별 저장할 필드 수집
    updates: dict = {}
    if step == 1:
        if gender: updates["gender"] = gender
        if age:    updates["age"] = age
    elif step == 2:
        if height: updates["height"] = float(height)
        if weight: updates["weight"] = float(weight)
    elif step == 3:
        if sleep_hours: updates["sleep_hours"] = float(sleep_hours)
    elif step == 4:
        if pushup_count is not None: updates["pushup_count"] = int(pushup_count)
    elif step == 5:
        if running_count: updates["running_count"] = int(running_count)
    elif step == 6:
        if debuff:
            parts = debuff.split("_")
            updates["coffee_cups"]   = int(parts[0]) if len(parts) > 0 else 0
            updates["overtime_days"] = int(parts[1]) if len(parts) > 1 else 0
    elif step == 7:
        if diet is not None: updates["diet_score"] = int(diet)
    elif step == 8:
        if stress is not None: updates["stress_score"] = int(stress)
    elif step == 9:
        if sitting is not None: updates["sitting_hours"] = int(sitting)
    elif step == 10:
        if alcohol is not None: updates["alcohol_freq"] = int(alcohol)

    # DB 세션에 병합 저장
    if updates:
        await update_session(user_token, updates)

    # 다음 단계 또는 로딩 화면으로
    next_step = step + 1
    if next_step <= 10:
        config = STEP_CONFIG[next_step].copy()
        config["step"] = next_step
        config["request"] = request
        return templates.TemplateResponse("components/step_form.html", config)
    else:
        # 마지막 단계 → 로딩 화면
        return templates.TemplateResponse("components/loading.html", {"request": request})


# ============================================================
# 스텝 1 전용 처리 (성별 + 나이 혼합 입력)
# ============================================================

@router.post("/submit-step1", response_class=HTMLResponse)
async def submit_step1(
    request: Request,
    user_token: str = Form(...),
    gender: str = Form(...),
    age: int = Form(...),
):
    await update_session(user_token, {"gender": gender, "age": age})

    config = STEP_CONFIG[2].copy()
    config["step"] = 2
    config["request"] = request
    return templates.TemplateResponse("components/step_form.html", config)


# ============================================================
# 결과 계산 (AI 호출)
# ============================================================

@router.get("/calculate", response_class=HTMLResponse)
async def calculate_result(
    request: Request,
    user_token: str = Query(default=""),
):
    """세션 데이터로 스탯 계산 + AI 리포트 생성 + DB 저장"""

    # 세션에서 유저 데이터 로드
    session = await get_session(user_token)
    if not session:
        # 세션 없으면 처음으로
        return templates.TemplateResponse("components/landing.html", {
            "request": request, "participant_count": 0
        })

    gender        = session.get("gender", "M")
    age           = session.get("age", 30)
    height        = session.get("height", 170.0)
    weight        = session.get("weight", 70.0)
    sleep_hours   = session.get("sleep_hours", 7.0)
    pushup        = session.get("pushup_count", 0)
    running       = session.get("running_count", 0)
    coffee        = session.get("coffee_cups", 0)
    overtime      = session.get("overtime_days", 0)
    diet_score    = session.get("diet_score", 0)
    stress_score  = session.get("stress_score", 0)
    sitting_hours = session.get("sitting_hours", 6)
    alcohol_freq  = session.get("alcohol_freq", 0)

    # 스탯 계산
    bmi_data = calculate_bmi_status(height, weight)
    scores   = convert_raw_to_scores(
        gender, age, pushup, running, sleep_hours, coffee, overtime,
        diet_score, stress_score, sitting_hours, alcohol_freq,
    )
    character = determine_character(
        scores["str_score"], scores["agi_score"],
        scores["hp_score"], scores["debuff_score"],
        bmi_data["status"],
        diet_score, stress_score, sitting_hours, alcohol_freq,
    )
    grade  = calculate_overall_grade(
        scores["str_score"], scores["agi_score"],
        scores["hp_score"], scores["debuff_score"]
    )
    labels = get_stat_labels(
        scores["str_score"], scores["agi_score"],
        scores["hp_score"], scores["debuff_score"]
    )
    diseases = predict_diseases(
        bmi_data["status"], scores["hp_score"],
        scores["debuff_score"], age,
    )

    # AI 리포트 생성
    ai_stats = {
        "gender": gender, "age": age,
        "bmi": bmi_data["bmi"], "bmi_status": bmi_data["label"],
        "str_score": scores["str_score"], "str_percentile": scores["str_percentile"],
        "agi_score": scores["agi_score"], "agi_percentile": scores["agi_percentile"],
        "hp_score": scores["hp_score"],   "debuff_score": scores["debuff_score"],
        "sleep_hours": sleep_hours, "coffee_cups": coffee, "overtime_days": overtime,
        "diet_score": diet_score, "stress_score": stress_score,
        "sitting_hours": sitting_hours, "alcohol_freq": alcohol_freq,
        "character_name": character["name"],
        "overall_grade": grade,
        "expected_diseases": diseases,
    }

    try:
        report = await generate_survival_report(ai_stats)
    except Exception:
        # AI 실패 시 기본 리포트 사용
        from app.services.ai import SurvivalReport
        report = SurvivalReport(
            grade=grade,
            title=f"{character['emoji']} {character['name']}",
            summary="스캐너 서버가 잠시 과부하 상태입니다. 그래도 결과는 진짜입니다.",
            analysis_physical=f"동년배 상위 {scores['str_percentile']}%의 근력 스탯 보유.",
            analysis_sleep=f"하루 {sleep_hours}시간 수면. HP 회복력 상태: {labels['hp_label']}.",
            analysis_debuff=f"커피 {coffee}잔 + 주 {overtime}회 야근. 디버프 상태: {labels['debuff_label']}.",
            disease_warning=f"예상 취약 질환: {diseases}",
            action_plan="오늘부터 수면 7시간 확보를 1순위 퀘스트로 설정하라."
        )

    # DB에 유저 및 AI 결과 저장
    await _save_user_result(user_token, session, bmi_data, scores, character, grade, report)

    # 소셜 프루프 카운트
    paid_count = await _get_paid_count()
    settings = get_settings()

    result_link = f"{request.base_url}result?token={user_token}"

    return templates.TemplateResponse("components/result.html", {
        "request": request,
        "is_paid": False,
        "character_id": character["id"],
        "character_emoji": character["emoji"],
        "character_quote": character.get("quote", ""),
        "grade": report.grade,
        "title": report.title,
        "summary": report.summary,
        "report": report,
        "str_score": scores["str_score"],
        "agi_score": scores["agi_score"],
        "hp_score": scores["hp_score"],
        "str_label": labels["str_label"],
        "agi_label": labels["agi_label"],
        "hp_label": labels["hp_label"],
        "debuff_label": labels["debuff_label"],
        "debuff_score": scores["debuff_score"],
        "paid_count": paid_count,
        "toss_client_key": settings.toss_client_key,
        "magic_link": "",
        "result_link": result_link,
    })


# ============================================================
# 결제 검증 (토스페이먼츠 콜백)
# ============================================================

@router.get("/payment/success", response_class=HTMLResponse)
async def payment_success(
    request: Request,
    paymentKey: str = Query(...),
    orderId: str = Query(...),
    amount: int = Query(...),
    user_token: str = Query(...),
):
    """토스페이먼츠 결제 성공 콜백 처리"""

    # 결제 승인 및 DB 업데이트
    await confirm_payment(paymentKey, orderId, amount, user_token)

    # 유료 결과 렌더링
    return await _render_paid_result(request, user_token)


@router.get("/payment/fail", response_class=HTMLResponse)
async def payment_fail(request: Request):
    """결제 실패/취소 처리"""
    return HTMLResponse("""
    <div class="text-center space-y-4 p-6">
        <div class="text-3xl">😢</div>
        <div class="text-white font-pixel text-sm">결제가 취소되었습니다.</div>
        <button hx-get="/api/components/landing" hx-target="#main-content" hx-swap="innerHTML"
                class="text-rpg-green border border-rpg-green rounded px-4 py-2 text-sm">
            처음으로 돌아가기
        </button>
    </div>
    """)


# ============================================================
# 매직 링크로 유료 결과 직접 접근
# ============================================================

@router.get("/result", response_class=HTMLResponse)
async def result_by_token(
    request: Request,
    token: str = Query(...),
):
    """매직 링크로 유료 결과 접근"""
    is_paid = await check_payment_status(token)
    if is_paid:
        return await _render_paid_result(request, token)
    else:
        return await _render_free_result(request, token)


# ============================================================
# 소셜 프루프 (Task 07)
# ============================================================

# 캐싱 변수
_paid_count_cache: dict = {"count": 0, "updated_at": 0}
_CACHE_TTL = 600  # 10분


async def _get_paid_count() -> int:
    """누적 결제자 수 (10분 캐싱)"""
    now = time.time()
    if now - _paid_count_cache["updated_at"] > _CACHE_TTL:
        try:
            db = get_supabase()
            result = db.table("users").select("id", count="exact").eq("is_paid", True).execute()
            _paid_count_cache["count"] = result.count or 0
            _paid_count_cache["updated_at"] = now
        except Exception:
            pass  # 캐시 값 유지
    return _paid_count_cache["count"]


async def _get_participant_count() -> int:
    """총 참여자 수"""
    try:
        db = get_supabase()
        result = db.table("users").select("id", count="exact").execute()
        return result.count or 0
    except Exception:
        return 0


# ============================================================
# 내부 헬퍼
# ============================================================

async def _save_user_result(
    user_token: str, session: dict,
    bmi_data: dict, scores: dict,
    character: dict, grade: str, report
) -> None:
    """Supabase에 유저 결과 저장 (upsert)"""
    try:
        db = get_supabase()
        db.table("users").upsert({
            "user_token": user_token,
            "gender": session.get("gender"),
            "age": session.get("age"),
            "height": session.get("height"),
            "weight": session.get("weight"),
            "sleep_hours": session.get("sleep_hours"),
            "pushup_count": session.get("pushup_count"),
            "running_count": session.get("running_count"),
            "coffee_cups": session.get("coffee_cups"),
            "overtime_days": session.get("overtime_days"),
            "diet_score": session.get("diet_score", 0),
            "stress_score": session.get("stress_score", 0),
            "sitting_hours": session.get("sitting_hours", 6),
            "alcohol_freq": session.get("alcohol_freq", 0),
            "bmi": bmi_data["bmi"],
            "bmi_status": bmi_data["status"],
            "str_score": scores["str_score"],
            "agi_score": scores["agi_score"],
            "hp_score": scores["hp_score"],
            "debuff_score": scores["debuff_score"],
            "character_id": character["id"],
            "overall_grade": grade,
            "ai_result": report.model_dump(),
            "is_paid": False,
        }, on_conflict="user_token").execute()
    except Exception as e:
        print(f"[ERROR] DB 저장 실패: {e}")


async def _render_paid_result(request: Request, user_token: str) -> HTMLResponse:
    """결제 완료된 유저에게 상세 리포트 렌더링"""
    try:
        db = get_supabase()
        result = db.table("users").select("*").eq("user_token", user_token).single().execute()
        data = result.data

        if not data:
            return HTMLResponse("<div class='text-white text-center p-4'>결과를 찾을 수 없습니다.</div>")

        character = {
            "id": data.get("character_id", "wizard"),
            "emoji": _get_emoji(data.get("character_id", "wizard")),
        }

        from app.services.ai import SurvivalReport
        ai_raw = data.get("ai_result", {})
        report = SurvivalReport(**ai_raw) if ai_raw else _get_default_report(data)

        labels = get_stat_labels(
            data.get("str_score", 50), data.get("agi_score", 50),
            data.get("hp_score", 50),  data.get("debuff_score", 50),
        )
        magic_link = f"{request.base_url}result?token={user_token}"

        from app.services.stats import CHARACTER_INFO
        char_quote = CHARACTER_INFO.get(character["id"], {}).get("quote", "")
        return templates.TemplateResponse("components/result.html", {
            "request": request,
            "is_paid": True,
            "character_id": character["id"],
            "character_emoji": character["emoji"],
            "character_quote": char_quote,
            "grade": report.grade,
            "title": report.title,
            "summary": report.summary,
            "report": report,
            "str_score": data.get("str_score", 50),
            "agi_score": data.get("agi_score", 50),
            "hp_score": data.get("hp_score", 50),
            "str_label": labels["str_label"],
            "agi_label": labels["agi_label"],
            "hp_label": labels["hp_label"],
            "debuff_label": labels["debuff_label"],
            "debuff_score": data.get("debuff_score", 0),
            "paid_count": 0,
            "toss_client_key": "",
            "magic_link": magic_link,
            "result_link": magic_link,
        })
    except Exception as e:
        return HTMLResponse(f"<div class='text-white text-center p-4'>오류: {e}</div>")


async def _render_free_result(request: Request, user_token: str) -> HTMLResponse:
    """비결제 유저에게 무료 결과 렌더링 (공유 링크 재접근 시)"""
    try:
        db = get_supabase()
        result = db.table("users").select("*").eq("user_token", user_token).single().execute()
        data = result.data
        if not data:
            return templates.TemplateResponse("components/landing.html", {
                "request": request, "participant_count": 0
            })

        character = {
            "id": data.get("character_id", "wizard"),
            "emoji": _get_emoji(data.get("character_id", "wizard")),
        }
        from app.services.ai import SurvivalReport
        ai_raw = data.get("ai_result", {})
        report = SurvivalReport(**ai_raw) if ai_raw else _get_default_report(data)
        labels = get_stat_labels(
            data.get("str_score", 50), data.get("agi_score", 50),
            data.get("hp_score", 50),  data.get("debuff_score", 50),
        )
        paid_count = await _get_paid_count()
        settings = get_settings()
        result_link = f"{request.base_url}result?token={user_token}"

        from app.services.stats import CHARACTER_INFO
        char_quote = CHARACTER_INFO.get(character["id"], {}).get("quote", "")
        return templates.TemplateResponse("components/result.html", {
            "request": request,
            "is_paid": False,
            "character_id": character["id"],
            "character_emoji": character["emoji"],
            "character_quote": char_quote,
            "grade": report.grade,
            "title": report.title,
            "summary": report.summary,
            "report": report,
            "str_score": data.get("str_score", 50),
            "agi_score": data.get("agi_score", 50),
            "hp_score": data.get("hp_score", 50),
            "str_label": labels["str_label"],
            "agi_label": labels["agi_label"],
            "hp_label": labels["hp_label"],
            "debuff_label": labels["debuff_label"],
            "debuff_score": data.get("debuff_score", 0),
            "paid_count": paid_count,
            "toss_client_key": settings.toss_client_key,
            "magic_link": "",
            "result_link": result_link,
        })
    except Exception:
        return templates.TemplateResponse("components/landing.html", {
            "request": request, "participant_count": 0
        })


def _calc_battle_score(user_data: dict) -> int:
    """배틀 스코어 = (STR + AGI + HP + (100 - DEBUFF)) // 4"""
    return (
        user_data.get("str_score", 50)
        + user_data.get("agi_score", 50)
        + user_data.get("hp_score", 50)
        + (100 - user_data.get("debuff_score", 0))
    ) // 4


async def _fetch_user_for_battle(token: str) -> dict | None:
    """DB에서 배틀용 유저 데이터 조회"""
    if not token:
        return None
    try:
        db = get_supabase()
        result = db.table("users").select(
            "character_id, str_score, agi_score, hp_score, debuff_score, overall_grade"
        ).eq("user_token", token).single().execute()
        data = result.data
        if not data:
            return None
        character_id = data.get("character_id", "wizard")
        return {
            "character_id": character_id,
            "emoji": _get_emoji(character_id),
            "character_name": _get_character_name(character_id),
            "str_score": data.get("str_score", 50),
            "agi_score": data.get("agi_score", 50),
            "hp_score": data.get("hp_score", 50),
            "debuff_score": data.get("debuff_score", 0),
            "overall_grade": data.get("overall_grade", "B"),
            "battle_score": 0,  # _calc_battle_score에서 채워짐
        }
    except Exception:
        return None


def _get_character_name(character_id: str) -> str:
    name_map = {
        "health_avatar":    "건강신 아바타",
        "swordmaster":      "소드마스터",
        "lich_king":        "리치왕",
        "burnout_ghost":    "번아웃 유령",
        "hibernating_bear": "겨울잠 곰",
        "ogre_lord":        "오거 군주",
        "necromancer":      "언데드 네크로맨서",
        "dwarf_tanker":     "드워프 탱커",
        "orc_berserker":    "오크 버서커",
        "elf_ranger":       "엘프 레인저",
        "wizard":           "마법사",
    }
    return name_map.get(character_id, "용사")


def _get_emoji(character_id: str) -> str:
    emoji_map = {
        "health_avatar":   "🦸",
        "swordmaster":     "👑",
        "lich_king":       "💀",
        "burnout_ghost":   "👻",
        "hibernating_bear":"🐻",
        "ogre_lord":       "🍖",
        "necromancer":     "🧟",
        "dwarf_tanker":    "🛡️",
        "orc_berserker":   "🏋️",
        "elf_ranger":      "🏃",
        "wizard":          "🧙",
    }
    return emoji_map.get(character_id, "🧙")


def _get_default_report(data: dict):
    from app.services.ai import SurvivalReport
    return SurvivalReport(
        grade=data.get("overall_grade", "B"),
        title="전투력 측정 완료",
        summary="당신의 생존 스탯이 분석되었습니다.",
        analysis_physical="체력 스탯 분석 완료.",
        analysis_sleep="수면 스탯 분석 완료.",
        analysis_debuff="디버프 스탯 분석 완료.",
        disease_warning="건강 관리에 주의하세요.",
        action_plan="꾸준한 운동과 충분한 수면이 최고의 버프입니다.",
    )
