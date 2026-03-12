"""
통계 계산 및 RPG 캐릭터 분류 로직

데이터 기준:
- BMI: 대한비만학회 2025 최신 기준 (BMI 25 이상 = 비만)
- 근력/심폐 백분위: 문화체육관광부 국민체력100 + KSEP 논문 기반 선형 보간법
"""
from typing import Literal


# ============================================================
# 1. Look-up Table (국민체력100 + KSEP 논문 기반)
# 각 나이대별 [상위 10% 컷, 상위 30% 컷, 상위 50% 컷, 상위 80% 컷]
# 푸시업: 1분 최대 횟수
# ============================================================

PUSHUP_TABLE = {
    "M": {
        20: [55, 41, 34, 20],
        30: [48, 31, 28, 15],
        40: [40, 27, 22, 12],
        50: [32, 21, 18, 10],
    },
    "F": {
        20: [35, 19, 17, 10],
        30: [30, 16, 15,  8],
        40: [25, 13, 12,  6],
        50: [20, 11, 10,  5],
    },
}

# 셔틀런 (20m 왕복 달리기) 횟수 기준
SHUTTLERUN_TABLE = {
    "M": {
        20: [65, 51, 40, 25],
        30: [58, 45, 35, 20],
        40: [48, 36, 28, 16],
        50: [38, 28, 22, 13],
    },
    "F": {
        20: [45, 38, 25, 15],
        30: [40, 33, 22, 12],
        40: [32, 26, 18,  9],
        50: [25, 20, 15,  7],
    },
}


def _get_age_group(age: int) -> int:
    """나이를 10년 단위 그룹으로 변환 (50세 이상은 50 고정)"""
    group = (age // 10) * 10
    return min(max(group, 20), 50)


def _linear_interpolate(score: int, table: list[int]) -> int:
    """
    선형 보간법으로 상위 퍼센트 계산
    table: [상위 10% 컷, 상위 30% 컷, 상위 50% 컷, 상위 80% 컷]
    반환: 상위 % 정수값 (낮을수록 좋음)
    """
    p10, p30, p50, p80 = table

    if score >= p10:
        return 10

    if score >= p30:
        # 10% ~ 30% 사이 보간
        ratio = (score - p30) / (p10 - p30) if (p10 - p30) > 0 else 0
        return int(30 - ratio * 20)

    if score >= p50:
        # 30% ~ 50% 사이 보간
        ratio = (score - p50) / (p30 - p50) if (p30 - p50) > 0 else 0
        return int(50 - ratio * 20)

    if score >= p80:
        # 50% ~ 80% 사이 보간
        ratio = (score - p80) / (p50 - p80) if (p50 - p80) > 0 else 0
        return int(80 - ratio * 30)

    return 85  # 하위 20%


# ============================================================
# 2. BMI 계산 (대한비만학회 2025 기준)
# ============================================================

BmiStatus = Literal["underweight", "normal", "overweight", "obese_1", "obese_2", "obese_3"]


def calculate_bmi_status(height_cm: float, weight_kg: float) -> dict:
    """
    BMI 계산 및 비만도 분류
    반환: { "bmi": float, "status": str, "label": str }
    """
    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        status, label = "underweight", "저체중"
    elif bmi < 23.0:
        status, label = "normal", "정상"
    elif bmi < 25.0:
        status, label = "overweight", "과체중(비만전단계)"
    elif bmi < 30.0:
        status, label = "obese_1", "1단계 비만"
    elif bmi < 35.0:
        status, label = "obese_2", "2단계 비만"
    else:
        status, label = "obese_3", "3단계 고도비만"

    return {"bmi": bmi, "status": status, "label": label}


# ============================================================
# 3. 백분위 계산
# ============================================================

def calculate_percentile(gender: str, age: int, score: int, stat_type: str) -> dict:
    """
    푸시업 또는 셔틀런 기록의 상위 퍼센트 계산

    stat_type: "pushup" | "running"
    반환: { "percentile": int, "score_input": int, "grade": str }
    """
    age_group = _get_age_group(age)
    table_map = PUSHUP_TABLE if stat_type == "pushup" else SHUTTLERUN_TABLE
    gender_key = "M" if gender == "M" else "F"

    table = table_map.get(gender_key, {}).get(age_group, [40, 28, 20, 10])
    percentile = _linear_interpolate(score, table)

    if percentile <= 10:
        grade = "S"
    elif percentile <= 30:
        grade = "A"
    elif percentile <= 50:
        grade = "B"
    elif percentile <= 70:
        grade = "C"
    else:
        grade = "D"

    return {"percentile": percentile, "score_input": score, "grade": grade}


# ============================================================
# 4. 스탯 점수 환산 (0~100점 스케일)
# ============================================================

def convert_raw_to_scores(
    gender: str,
    age: int,
    pushup_count: int,
    running_count: int,  # 셔틀런 횟수 (없으면 0)
    sleep_hours: float,
    coffee_cups: int,
    overtime_days: int,
    diet_score: int = 0,    # Q7: 0=건강식, 1=보통, 2=패스트푸드, 3=인스턴트
    stress_score: int = 0,  # Q8: 0=없음, 1=낮음, 2=높음, 3=극한
    sitting_hours: int = 6, # Q9: 하루 평균 좌식 시간 (4/6/10/13)
    alcohol_freq: int = 0,  # Q10: 주간 음주 일수 (0/1/3/7)
) -> dict:
    """
    유저 입력값을 0~100점 스탯으로 환산
    반환: { str_score, agi_score, hp_score, debuff_score, str_percentile, agi_percentile }
    """
    # STR (근력): 푸시업 상위 % → 점수 변환 (상위 % 낮을수록 높은 점수)
    str_data = calculate_percentile(gender, age, pushup_count, "pushup")
    str_percentile = str_data["percentile"]
    str_score = max(0, 100 - str_percentile)

    # AGI (심폐/민첩): 셔틀런 기록
    if running_count > 0:
        agi_data = calculate_percentile(gender, age, running_count, "running")
        agi_percentile = agi_data["percentile"]
    else:
        agi_percentile = 55
    agi_score = max(0, 100 - agi_percentile)

    # Q9 좌식 시간 패널티 (AGI 감소)
    sit_penalty = {4: 0, 6: 5, 10: 15, 13: 25}.get(sitting_hours, 10)
    agi_score = max(5, agi_score - sit_penalty)

    # HP (체력/수면): 수면 시간 기반
    if sleep_hours >= 7:
        base_hp = 100
    elif sleep_hours >= 6:
        base_hp = 70
    elif sleep_hours >= 5:
        base_hp = 40
    else:
        base_hp = 10

    # Q7 식습관 HP 패널티
    diet_hp_penalty = [0, 10, 20, 30][min(diet_score, 3)]
    hp_score = max(5, base_hp - diet_hp_penalty)

    # DEBUFF (독/저주): 카페인 + 야근 + 스트레스 + 식단 + 음주
    diet_debuff   = [0, 0, 5, 15][min(diet_score, 3)]
    stress_debuff = {0: 0, 1: 10, 2: 25, 3: 40}.get(stress_score, 0)
    alc_debuff    = {0: 0, 1: 5, 3: 15, 7: 30}.get(alcohol_freq, 0)
    debuff_score  = min(100,
        (coffee_cups * 10) + (overtime_days * 15) +
        diet_debuff + stress_debuff + alc_debuff
    )

    return {
        "str_score": str_score,
        "agi_score": agi_score,
        "hp_score": hp_score,
        "debuff_score": debuff_score,
        "str_percentile": str_percentile,
        "agi_percentile": agi_percentile,
    }


# ============================================================
# 5. RPG 캐릭터 분류 (Task 04)
# 폭포수(Waterfall) If-Elif-Else 방식
# ============================================================

CHARACTER_INFO = {
    # ── 히든 캐릭터 ──────────────────────────────────────────
    "health_avatar": {
        "name": "건강신 아바타",
        "emoji": "🦸",
        "id": "health_avatar",
        "quote": "이 몸의 신체는 이미 인간의 한계를 초월했지. 새벽 5시 기상, 5km 러닝, 푸시업 100개… 그게 내 아침 준비운동이야. 넌 아직 자고 있겠지만.",
    },
    "swordmaster": {
        "name": "소드마스터",
        "emoji": "👑",
        "id": "swordmaster",
        "quote": "칼을 뽑기 전에 이미 승패는 결정된다. 근력도, 심폐도, 멘탈도—모두 갈고닦은 자만이 이 칭호를 얻을 수 있지. 아직 갈 길이 있지만, 이 정도면 충분히 강하다.",
    },
    "lich_king": {
        "name": "리치왕",
        "emoji": "💀",
        "id": "lich_king",
        "quote": "죽음은 이미 두렵지 않아. 야근 연속에 커피로 연명하다 보니 산 것도 죽은 것도 아닌 존재가 됐거든. 몸은 무너졌지만 이 저주가 나를 아직 움직이게 해.",
    },
    "burnout_ghost": {
        "name": "번아웃 유령",
        "emoji": "👻",
        "id": "burnout_ghost",
        "quote": "나 지금 여기 있는 거 맞지? 가끔 내가 실체가 있는지 모르겠어. 출퇴근길 유리에 비친 내 모습이 점점 투명해지는 것 같아. 오늘도 그냥 흘러가는 하루야.",
    },
    "hibernating_bear": {
        "name": "겨울잠 곰",
        "emoji": "🐻",
        "id": "hibernating_bear",
        "quote": "겨울잠 중인데 왜 깨웠어… 소파에서 냉장고까지가 오늘의 최대 이동 거리야. 움직이면 뭐가 좋아진다고? 난 지금도 충분히 행복한데.",
    },
    "ogre_lord": {
        "name": "오거 군주",
        "emoji": "🍖",
        "id": "ogre_lord",
        "quote": "이 덩치가 약점이라고? 웃기는 소리. 내 몸무게 자체가 무기야. 한 방에 벽 부수고, 밥 한 솥에 기력 회복. 다이어트? 그게 뭔데, 먹는 거야?",
    },
    # ── 기본 캐릭터 ──────────────────────────────────────────
    "necromancer": {
        "name": "언데드 네크로맨서",
        "emoji": "🧟",
        "id": "necromancer",
        "quote": "산 자의 시간표로 사는 건 이미 포기했어. 수면? 사치야. 건강? 나중에 챙길게. 지금은 이 주문 하나만 더 완성하면… 쓰러지기 전에.",
    },
    "dwarf_tanker": {
        "name": "드워프 탱커",
        "emoji": "🛡️",
        "id": "dwarf_tanker",
        "quote": "땅딸막하다고 무시하지 마. 이 몸통이 곧 방패야. 어떤 공격도 버텨내지. 속도? 필요 없어. 난 맞아도 안 쓰러지는 게 특기거든.",
    },
    "orc_berserker": {
        "name": "오크 버서커",
        "emoji": "🏋️",
        "id": "orc_berserker",
        "quote": "생각은 나중에 해. 일단 지르고 보는 거야. 팔 근육이 뇌보다 0.3초 빠르게 반응하거든. 섬세함? 그런 건 엘프한테나 물어봐. 난 그냥 부수면 돼.",
    },
    "elf_ranger": {
        "name": "엘프 레인저",
        "emoji": "🏃",
        "id": "elf_ranger",
        "quote": "무거운 건 딱 질색이야. 빠르게 쏘고 빠르게 튀는 게 내 전략. 근력? 굳이 필요해? 적이 날 잡을 수 없으면 그만이잖아. 아, 근데 병뚜껑은 좀 어렵더라.",
    },
    "wizard": {
        "name": "마법사",
        "emoji": "🧙",
        "id": "wizard",
        "quote": "머리 쓰는 건 어느 정도 하지만, 몸 쓰는 건 마법사의 재능이 아니야. 책 한 권 드는 것도 힘들고, 뛰는 건 생각도 안 해. 마법으로 날기만을 원하지. 현실은… 버스 놓쳐서 뛰어야 했지만.",
    },
}


def determine_character(
    str_score: int,
    agi_score: int,
    hp_score: int,
    debuff_score: int,
    bmi_status: str,
    diet_score: int = 0,
    stress_score: int = 0,
    sitting_hours: int = 6,
    alcohol_freq: int = 0,
) -> dict:
    """
    스탯 점수 기반 RPG 캐릭터 판별 (폭포수 방식)
    히든 캐릭터 6종 + 기본 캐릭터 5종

    반환: CHARACTER_INFO 딕셔너리
    """
    # ── 히든 캐릭터 ─────────────────────────────────────────────
    # 🦸 울트라 히든. 건강신 아바타: 모든 스탯 완벽 + 식단/스트레스까지 완벽
    if (str_score >= 85 and agi_score >= 85 and hp_score >= 95
            and debuff_score <= 10 and diet_score == 0 and stress_score == 0):
        return CHARACTER_INFO["health_avatar"]

    # 👑 히든. 소드마스터: 모든 스탯 최상위 + 디버프 최소
    if str_score >= 80 and agi_score >= 80 and hp_score >= 70 and debuff_score <= 30:
        return CHARACTER_INFO["swordmaster"]

    # 💀 히든. 리치왕: 극한 디버프 + 수면 완전 파괴 (가장 극단적 상태)
    if debuff_score >= 80 and hp_score <= 20:
        return CHARACTER_INFO["lich_king"]

    # 👻 히든. 번아웃 유령: 극한 스트레스 + 체력 바닥 + 근력 하위 (lich king 미만 범위)
    if stress_score >= 3 and hp_score <= 35 and str_score <= 40:
        return CHARACTER_INFO["burnout_ghost"]

    # 🐻 히든. 겨울잠 곰: 고도비만 + 극단적 좌식 + 심폐 최하위
    if bmi_status in ("obese_2", "obese_3") and sitting_hours >= 10 and agi_score <= 20:
        return CHARACTER_INFO["hibernating_bear"]

    # 🍖 히든. 오거 군주: 고도비만이지만 근력은 상위권
    if bmi_status in ("obese_2", "obese_3") and str_score >= 80:
        return CHARACTER_INFO["ogre_lord"]

    # ── 기본 캐릭터 ─────────────────────────────────────────────
    # 🧟 1순위. 언데드 네크로맨서: 수면 파탄 + 야근/카페인 중독
    if hp_score <= 40 and debuff_score >= 60:
        return CHARACTER_INFO["necromancer"]

    # 🛡️ 2순위. 드워프 탱커: 과체중/비만 + 근력 평균 이상
    if bmi_status in ("obese_1", "obese_2", "obese_3") and str_score >= 50:
        return CHARACTER_INFO["dwarf_tanker"]

    # 🏋️ 3순위. 오크 버서커: 근력이 심폐보다 높고 상위 30% 이내
    if str_score >= 70 and str_score > agi_score:
        return CHARACTER_INFO["orc_berserker"]

    # 🏃 4순위. 엘프 레인저: 심폐가 근력보다 높고 상위 30% 이내
    if agi_score >= 70 and agi_score > str_score:
        return CHARACTER_INFO["elf_ranger"]

    # 🧙 기본값. 마법사: 위 조건 모두 불해당
    return CHARACTER_INFO["wizard"]


# ============================================================
# 6. 종합 등급 계산
# ============================================================

def calculate_overall_grade(
    str_score: int,
    agi_score: int,
    hp_score: int,
    debuff_score: int,
) -> str:
    """
    4개 스탯을 종합하여 A+~F 등급 산출
    """
    # 디버프는 감점 요소 (100점에서 차감)
    debuff_penalty = debuff_score
    avg = (str_score + agi_score + hp_score + (100 - debuff_penalty)) / 4

    if avg >= 85:
        return "S"
    elif avg >= 75:
        return "A+"
    elif avg >= 65:
        return "A"
    elif avg >= 55:
        return "B+"
    elif avg >= 45:
        return "B"
    elif avg >= 35:
        return "B-"
    elif avg >= 25:
        return "C"
    else:
        return "D"


def get_stat_labels(str_score: int, agi_score: int, hp_score: int, debuff_score: int) -> dict:
    """프론트엔드 표시용 스탯 레이블 반환"""
    def score_to_label(s: int) -> str:
        if s >= 80: return "최상위"
        if s >= 60: return "상위"
        if s >= 40: return "중위"
        if s >= 20: return "하위"
        return "최하위"

    return {
        "str_label": score_to_label(str_score),
        "agi_label": score_to_label(agi_score),
        "hp_label": score_to_label(hp_score),
        "debuff_label": "위험" if debuff_score >= 60 else "보통" if debuff_score >= 30 else "안전",
    }


# ============================================================
# 테스트 코드
# ============================================================

if __name__ == "__main__":
    test_cases = [
        # (gender, age, pushup, running, sleep, coffee, overtime, bmi_h, bmi_w, 예상캐릭터)
        ("M", 32, 55, 60, 5, 4, 3, 175, 80, "necromancer - 야근충 테스트"),
        ("M", 28, 60, 70, 8, 1, 0, 175, 68, "swordmaster - 갓생 테스트"),
        ("M", 35, 30, 20, 7, 2, 1, 170, 90, "dwarf_tanker - 과체중 테스트"),
        ("M", 25, 50, 15, 7, 1, 1, 175, 72, "orc_berserker - 근력형 테스트"),
        ("F", 30, 10, 45, 7, 0, 0, 162, 52, "elf_ranger - 달리기형 테스트"),
        ("M", 40, 15, 20, 7, 2, 2, 170, 70, "wizard - 기본값 테스트"),
    ]

    print("=" * 60)
    for gender, age, pushup, running, sleep, coffee, overtime, h, w, label in test_cases:
        bmi_result = calculate_bmi_status(h, w)
        scores = convert_raw_to_scores(gender, age, pushup, running, sleep, coffee, overtime)
        character = determine_character(
            scores["str_score"], scores["agi_score"],
            scores["hp_score"], scores["debuff_score"],
            bmi_result["status"]
        )
        grade = calculate_overall_grade(
            scores["str_score"], scores["agi_score"],
            scores["hp_score"], scores["debuff_score"]
        )
        print(f"[{label}]")
        print(f"  BMI: {bmi_result['bmi']} ({bmi_result['label']})")
        print(f"  STR:{scores['str_score']} AGI:{scores['agi_score']} HP:{scores['hp_score']} DEBUFF:{scores['debuff_score']}")
        print(f"  캐릭터: {character['emoji']} {character['name']} | 등급: {grade}")
        print()
