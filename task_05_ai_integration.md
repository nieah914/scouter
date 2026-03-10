# Task: OpenAI API Integration & Structured Outputs (JSON Mode)
이제 `app/services/ai.py` 파일을 작성하여 OpenAI API를 연동할 거야. 
이 파일의 목적은 앞서 `stats.py`에서 계산된 유저 데이터(통계, 캐릭터, BMI 등)를 재료로 삼아, 유쾌하고 뼈 때리는 'RPG 상태창' 분석 리포트를 텍스트로 뽑아내는 거야.

## 1. Pydantic Model 기반 JSON Schema 정의
AI의 응답이 무조건 이 구조로 떨어지도록 강제하기 위해 Pydantic을 사용해 줘.
```python
from pydantic import BaseModel

class SurvivalReport(BaseModel):
    grade: str            # 예: "A+", "B-", "F"
    title: str            # 예: "상위 15% 오크 버서커"
    summary: str          # 현재 상태를 한 줄로 요약하는 뼈 때리는 문장
    analysis_physical: str # 체격 및 전투력(상위 %)에 대한 분석
    analysis_sleep: str    # 수면 시간(HP/MP) 분석
    analysis_debuff: str   # 야근/카페인(독 상태) 분석
    disease_warning: str   # 통계 및 생활습관 기반의 취약 질병 경고
    action_plan: str       # 생존을 위한 현실적인 1줄 퀘스트(조언)
   ```
2. System Prompt (페르소나 부여)
아래의 시스템 프롬프트를 전역 변수(예: SYSTEM_PROMPT)로 정의해 줘.

"You are a cynical but highly accurate 'Status Window AI' from a modern fantasy RPG. Your job is to analyze the survival stats of a modern human based ONLY on the provided statistical data. Speak in Korean. Use game-like terminology (HP, MP, Buff, Debuff, 스탯, 방어력, 전투력 등) combined with a witty, sarcastic, and factual tone (팩트폭력).

[RULES]

DO NOT invent or hallucinate numbers. Use ONLY the calculated percentiles and data provided in the user prompt.

Output MUST be strictly in JSON format matching the schema."

3. Async OpenAI Call Function
generate_survival_report(user_stats: dict) -> dict 라는 비동기(Async) 함수를 작성해 줘.

최신 openai 패키지의 비동기 클라이언트(AsyncOpenAI)를 사용해 줘.

model="gpt-4o-mini"를 사용해 줘.

[매우 중요] 응답이 깨지는 것을 막기 위해 response_format={"type": "json_object"}를 적용하거나, 최신 Pydantic 기반 Structured Outputs 기능을 적용해 줘.

유저 데이터(user_stats)는 파이썬 딕셔너리를 통째로 문자열화(str())하거나 JSON 덤프해서 user role의 content로 전달해 줘.

4. Action Required
위 요구사항을 바탕으로 에러 핸들링(try-except 블록으로 OpenAI 서버 폭주 대응)이 포함된 app/services/ai.py 전체 코드를 작성해 줘.

개발자가 .env 파일에 OPENAI_API_KEY만 넣으면 바로 동작하도록 깔끔하게 구조화해 줘.

---

## ✅ 변경 사항 (Q7~Q10 AI 컨텍스트 반영)

### `generate_survival_report()` 호출 시 ai_stats 확장
Q7~Q10 데이터가 AI 프롬프트 컨텍스트에 추가됨:
```python
ai_stats = {
    ...,  # 기존 항목들
    "diet_score": diet_score,       # Q7: 0~3
    "stress_score": stress_score,   # Q8: 0~3
    "sitting_hours": sitting_hours, # Q9: 4/6/10/13
    "alcohol_freq": alcohol_freq,   # Q10: 0/1/3/7
}
```
→ AI가 식습관/스트레스/좌식/음주를 참고해 `analysis_debuff`, `disease_warning`, `action_plan` 항목에 반영 가능