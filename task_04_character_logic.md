# Task: RPG Character Classification Logic
이전에 만든 `app/services/stats.py` 파일 안에 유저의 스탯(0~100점)을 기반으로 **RPG 캐릭터 클래스(직업/종족)**를 판별하는 `determine_character()` 함수를 추가해 줘.

## 1. 캐릭터 분류 원칙 (폭포수 분기)
이 로직은 "if-elif-else" 구조를 사용하여 위에서부터 아래로 순서대로 조건을 검사해야 해. 가장 먼저 조건을 만족하는 캐릭터를 반환해 줘. 
각 캐릭터별 판별 조건(Rule)은 아래와 같아.

**👑 히든. 소드마스터 (Swordmaster) - 갓생 / 사기캐**
- 조건: `str_score >= 80` AND `agi_score >= 80` AND `hp_score >= 70` AND `debuff_score <= 30`
- 의미: 근력/심폐 최상위권, 수면 6시간 이상, 카페인/야근은 적은 완벽한 밸런스형.

**🧟 1순위. 언데드 네크로맨서 (Necromancer) - 수면 파탄 / 야근 중독**
- 조건: `hp_score <= 40` AND `debuff_score >= 60`
- 의미: 다른 스탯이 아무리 높아도, 잠(HP)을 못 자고 커피/야근(DEBUFF)으로 연명하는 상태.

**🛡️ 2순위. 드워프 탱커 (Dwarf Tanker) - 체급형 근접**
- 조건: `bmi_status in ["obese_1", "obese_2", "obese_3"]` AND `str_score >= 50`
- 의미: BMI 기준 비만병(체중이 나감)이면서, 근력이 평균(50점) 이상인 맷집왕.

**🏋️ 3순위. 오크 버서커 (Orc Berserker) - 근력 몰빵형**
- 조건: `str_score >= 70` AND `str_score > agi_score`
- 의미: 달리기는 상대적으로 약하지만, 쇠질/푸시업 근력은 상위 30% 이내인 타격계.

**🏃 4순위. 엘프 레인저 (Elf Ranger) - 심폐/민첩 몰빵형**
- 조건: `agi_score >= 70` AND `agi_score > str_score`
- 의미: 근육량은 적을 수 있으나 러닝(유산소) 스탯이 상위 30% 이내인 마라토너.

**🧙 5순위. 마법사 (Wizard) - 운동 부족 / 지식인형 (Default)**
- 조건: `else` (위 5가지 조건에 모두 해당하지 않는 경우)
- 의미: 근력과 심폐 모두 70점 미만이면서 특별한 특징이 없는, 육체 대신 머리만 쓰는 현대인의 기본값.

## 2. Action Required
1. 위 조건을 완벽하게 반영한 `determine_character(str_score, agi_score, hp_score, debuff_score, bmi_status) -> str` 파이썬 함수를 작성해 줘.
2. 반환값은 순수 한글 캐릭터명(예: "언데드 네크로맨서") 문자열(String)이거나, 나중에 딕셔너리로 쓰기 편하게 식별자(ID)를 반환해도 좋아.
3. 이 함수가 정상적으로 동작하는지 확인할 수 있도록, 각 캐릭터별 조건에 맞는 더미 데이터를 넣은 하단 테스트 코드(예: `if __name__ == "__main__":`)를 아주 짧게 하나 작성해 줘.

---

## ✅ 변경 사항 (히든 캐릭터 5종 추가)

### `determine_character()` 함수 파라미터 확장
기존 5개 → 9개 (신규 4개 모두 default값 있음):
```python
def determine_character(
    str_score, agi_score, hp_score, debuff_score, bmi_status,
    diet_score=0, stress_score=0, sitting_hours=6, alcohol_freq=0
)
```

### 캐릭터 분류 체계 (6→11종, 폭포수 방식)

| 순위 | 캐릭터 | 조건 | 구분 |
|------|--------|------|------|
| 1 | 🦸 건강신 아바타 | str≥85, agi≥85, hp≥95, debuff≤10, diet=0, stress=0 | 울트라 히든 |
| 2 | 👑 소드마스터 | str≥80, agi≥80, hp≥70, debuff≤30 | 히든 |
| 3 | 💀 리치왕 | debuff≥80, hp≤20 | 히든 |
| 4 | 👻 번아웃 유령 | stress≥3, hp≤35, str≤40 | 히든 |
| 5 | 🐻 겨울잠 곰 | obese2+, sitting≥10h, agi≤20 | 히든 |
| 6 | 🍖 오거 군주 | obese2+, str≥80 | 히든 |
| 7 | 🧟 언데드 네크로맨서 | hp≤40, debuff≥60 | 기본 |
| 8 | 🛡️ 드워프 탱커 | obese1+, str≥50 | 기본 |
| 9 | 🏋️ 오크 버서커 | str≥70 > agi | 기본 |
| 10 | 🏃 엘프 레인저 | agi≥70 > str | 기본 |
| 11 | 🧙 마법사 | 기본값 (else) | 기본 |

### 히든 캐릭터별 트리거 설계 원칙
- **건강신 아바타**: 기존 소드마스터보다 엄격한 조건. Q7·Q8 응답까지 완벽해야 출현
- **리치왕**: 디버프 폭발 상태. 소드마스터와 반대 극단값
- **번아웃 유령**: Q8 스트레스=극한이 PRIMARY. 리치왕보다 덜 극단적 (debuff<80)
- **겨울잠 곰**: Q9 좌식 시간이 PRIMARY. 고도비만 + 무활동 조합
- **오거 군주**: 기존 드워프 탱커보다 상위. 고도비만이지만 근력 최상위

### api.py `_get_emoji()` 업데이트
5종 신규 character_id 이모지 매핑 추가:
```python
"health_avatar": "🦸", "lich_king": "💀",
"burnout_ghost": "👻", "hibernating_bear": "🐻", "ogre_lord": "🍖"
```
