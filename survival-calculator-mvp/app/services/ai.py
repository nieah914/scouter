"""
OpenAI API 연동 - RPG 상태창 팩트폭력 분석 리포트 생성

- gpt-4o-mini 모델 사용
- Structured Outputs (JSON Mode) 강제 적용
- 비동기(Async) 처리로 트래픽 병목 방지
- 할루시네이션 방지: 백엔드 계산 수치만 활용
"""
import json
import os
from pydantic import BaseModel
from openai import AsyncOpenAI
from fastapi import HTTPException

from app.config import get_settings


# ============================================================
# 1. AI 응답 JSON Schema (Pydantic 모델)
# ============================================================

class SurvivalReport(BaseModel):
    grade: str             # 예: "A+", "B-", "F"
    title: str             # 예: "상위 15% 오크 버서커"
    summary: str           # 현재 상태를 한 줄로 요약하는 팩트폭력 문장
    analysis_physical: str # 체격 및 전투력(상위 %) 분석
    analysis_sleep: str    # 수면 시간(HP/MP) 분석
    analysis_debuff: str   # 야근/카페인(독/저주) 분석
    disease_warning: str   # 통계 기반 취약 질병 경고
    action_plan: str       # 생존을 위한 현실적인 1줄 퀘스트(조언)


# ============================================================
# 2. System Prompt - RPG 상태창 AI 페르소나
# ============================================================

SYSTEM_PROMPT = """You are a cynical but highly accurate "Status Window AI" from a modern fantasy RPG.
Your job is to analyze the survival stats of a modern human based ONLY on the provided statistical data.
Speak in Korean. Use game-like terminology (HP, MP, Buff, Debuff, 스탯, 방어력, 전투력 등)
combined with a witty, sarcastic, and factual tone (팩트폭력).

[RULES]
1. DO NOT invent or hallucinate numbers. Use ONLY the calculated percentiles and statistical data provided.
2. Maintain a cynical but humorous "RPG Game System" tone throughout.
3. Output MUST be strictly in JSON format with the exact keys below.
4. All text values must be in Korean only.
5. Keep each field concise: summary (1 sentence), others (1-2 sentences max).

[REQUIRED JSON KEYS]
{
  "grade": "A+~S 또는 B-, C, D 중 하나 (백엔드에서 전달된 등급 그대로 사용)",
  "title": "유저 상태를 요약하는 재미있는 칭호 (예: '야근에 찌든 오크 행동대장', '상위 15% 심폐왕 엘프')",
  "summary": "현재 상태를 한 줄로 요약하는 뼈때리는 팩트폭력 문장",
  "analysis_physical": "체격(BMI) 및 전투력(근력/심폐 상위%)에 대한 RPG식 분석",
  "analysis_sleep": "수면 시간을 마나(MP) 또는 회복력에 빗댄 분석",
  "analysis_debuff": "커피 섭취량과 야근 빈도를 독/디버프로 해석한 분석",
  "disease_warning": "통계 기반 예상 취약 질병에 대한 RPG 게임식 저주 경고",
  "action_plan": "생존력을 높이기 위한 뼈때리는 현실 조언 1가지 (퀘스트 형식)"
}"""


# ============================================================
# 3. AI 호출 함수 (비동기)
# ============================================================

async def generate_survival_report(user_stats: dict) -> SurvivalReport:
    """
    통계 계산 결과를 받아 RPG 상태창 분석 리포트 생성

    user_stats 예시:
    {
        "gender": "M", "age": 32,
        "bmi": 26.1, "bmi_status": "1단계 비만",
        "str_score": 70, "str_percentile": 30,
        "agi_score": 45, "agi_percentile": 55,
        "hp_score": 40,  "debuff_score": 85,
        "sleep_hours": 5, "coffee_cups": 4, "overtime_days": 3,
        "character_name": "언데드 네크로맨서",
        "overall_grade": "B-",
        "expected_diseases": "고혈압, 만성피로, 대사증후군"
    }
    """
    settings = get_settings()

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    # 유저 데이터를 자연어로 포맷 (AI가 이해하기 쉽게)
    user_prompt = _format_user_prompt(user_stats)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},  # JSON Mode 강제
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.75,  # 약간의 창의성(유머) 허용
            max_tokens=800,
        )

        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)

        # Pydantic 모델로 검증
        return SurvivalReport(**data)

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"AI 응답 파싱 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석 중 서버 폭주가 발생했습니다: {e}")


def _format_user_prompt(stats: dict) -> str:
    """AI에게 전달할 유저 스탯 데이터를 명확한 텍스트로 포맷"""
    return f"""다음 현대인의 생존 스탯을 분석해 주세요.

[기본 정보]
- 성별: {"남성" if stats.get("gender") == "M" else "여성"}
- 나이: {stats.get("age", 0)}세
- BMI: {stats.get("bmi", 0)} ({stats.get("bmi_status", "정보없음")})

[전투력 스탯]
- STR(근력): 동년배 상위 {stats.get("str_percentile", 50)}% (점수: {stats.get("str_score", 50)}/100)
- AGI(심폐): 동년배 상위 {stats.get("agi_percentile", 50)}% (점수: {stats.get("agi_score", 50)}/100)

[생존력 스탯]
- HP(수면 회복력): {stats.get("sleep_hours", 7)}시간/일 (점수: {stats.get("hp_score", 70)}/100)
- DEBUFF(독/저주): 하루 커피 {stats.get("coffee_cups", 0)}잔 + 주 {stats.get("overtime_days", 0)}회 야근 (점수: {stats.get("debuff_score", 0)}/100)

[시스템 판정]
- 캐릭터 클래스: {stats.get("character_name", "마법사")}
- 종합 등급: {stats.get("overall_grade", "B")}
- 예상 취약 질병: {stats.get("expected_diseases", "일반적인 현대인 질환")}

위 데이터를 기반으로 JSON 리포트를 생성해 주세요. grade는 반드시 "{stats.get("overall_grade", "B")}"를 그대로 사용하세요."""


# ============================================================
# 4. 취약 질병 예측 (통계 기반, 할루시네이션 방지용)
# ============================================================

def predict_diseases(
    bmi_status: str,
    hp_score: int,
    debuff_score: int,
    age: int,
) -> str:
    """
    스탯 기반 예상 취약 질병 리스트 반환 (AI에게 팩트로 넘겨줌)
    """
    diseases = []

    if bmi_status in ("obese_1", "obese_2", "obese_3"):
        diseases.append("대사증후군")
        diseases.append("고혈압")
    if bmi_status in ("obese_2", "obese_3"):
        diseases.append("당뇨병 전단계")

    if hp_score <= 40:
        diseases.append("만성피로증후군")
        diseases.append("면역력 저하")

    if debuff_score >= 60:
        diseases.append("위장질환")
        if hp_score <= 40:
            diseases.append("번아웃 증후군")

    if age >= 40 and bmi_status not in ("normal", "underweight"):
        diseases.append("관절 퇴행")

    if not diseases:
        diseases.append("현재 큰 위험 없음 (유지 필요)")

    return ", ".join(diseases[:4])  # 최대 4개
