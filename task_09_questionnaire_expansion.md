# Task: Questionnaire Expansion (Q7~Q10) & Router Update

기존 6문항에서 10문항으로 질문지를 확장하고, 라우터 및 세션 처리 로직을 업데이트한다.

---

## ✅ 구현 완료 사항

### 1. STEP_CONFIG 추가 (api.py)

| 스텝 | stat_label | 질문 | field_name | 입력 타입 |
|------|------------|------|------------|-----------|
| Q7 | [ 식량 보급 시스템 점검 ] | 평소 식사 습관은? | `diet` | card_select |
| Q8 | [ 정신력 스탯 측정 ] | 최근 스트레스 수준은? | `stress` | card_select |
| Q9 | [ 좌식 생활 패턴 분석 ] | 하루 평균 앉아있는 시간은? | `sitting` | card_select |
| Q10 | [ 독소 내성 최종 검사 ] | 음주 빈도는? | `alcohol` | card_select |

**Q7 옵션값**: `0`(건강식) / `1`(보통) / `2`(패스트푸드) / `3`(인스턴트)
**Q8 옵션값**: `0`(없음) / `1`(낮음) / `2`(높음) / `3`(극한)
**Q9 옵션값**: `4`(4h미만) / `6`(4~6h) / `10`(6~10h) / `13`(10h이상)
**Q10 옵션값**: `0`(안 마심) / `1`(주1~2회) / `3`(주3~4회) / `7`(매일)

### 2. submit_step() Form 파라미터 추가
```python
diet:    Optional[str] = Form(None)   # Q7
stress:  Optional[str] = Form(None)   # Q8
sitting: Optional[str] = Form(None)   # Q9
alcohol: Optional[str] = Form(None)   # Q10
```

### 3. 단계별 세션 저장 로직
```python
elif step == 7:
    if diet is not None: session["diet_score"] = int(diet)
elif step == 8:
    if stress is not None: session["stress_score"] = int(stress)
elif step == 9:
    if sitting is not None: session["sitting_hours"] = int(sitting)
elif step == 10:
    if alcohol is not None: session["alcohol_freq"] = int(alcohol)
```

### 4. 마지막 스텝 조건 변경
```python
# 수정 전
if next_step <= 6: ...

# 수정 후
if next_step <= 10: ...
```

### 5. calculate 엔드포인트 세션 변수 추가
```python
diet_score    = session.get("diet_score", 0)
stress_score  = session.get("stress_score", 0)
sitting_hours = session.get("sitting_hours", 6)
alcohol_freq  = session.get("alcohol_freq", 0)
```
→ `convert_raw_to_scores()`, `determine_character()` 호출 시 모두 전달

### 6. Supabase 스키마 업데이트 (supabase_schema.sql)

**CREATE TABLE에 컬럼 추가**:
```sql
diet_score     INTEGER DEFAULT 0,
stress_score   INTEGER DEFAULT 0,
sitting_hours  INTEGER DEFAULT 6,
alcohol_freq   INTEGER DEFAULT 0,
```

**기존 DB용 ALTER TABLE 추가**:
```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS diet_score    INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stress_score  INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS sitting_hours INTEGER DEFAULT 6;
ALTER TABLE users ADD COLUMN IF NOT EXISTS alcohol_freq  INTEGER DEFAULT 0;
```

### 7. _save_user_result() DB 저장 컬럼 추가
```python
"diet_score": session.get("diet_score", 0),
"stress_score": session.get("stress_score", 0),
"sitting_hours": session.get("sitting_hours", 6),
"alcohol_freq": session.get("alcohol_freq", 0),
```
