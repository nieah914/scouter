# Task 11: 친구 배틀 기능

결과 화면에서 친구를 초대해 전투력을 비교하는 배틀 기능을 구현한다.

---

## 기능 명세

### 배틀 흐름
1. 결과 화면 하단 "⚔ 배틀 신청하기" 버튼 클릭
2. `/battle?challenger={MY_TOKEN}` URL이 클립보드에 복사됨
3. 친구가 해당 URL 접속 → `battle_page.html` 로드
4. `battle_page.html`이 vanilla `fetch`로 `/api/components/battle?challenger=X&defender=localStorage.token` 요청
5. API가 두 유저 DB 조회 → 배틀 스코어 계산 → `battle.html` fragment 반환
6. 캐릭터 충돌 애니메이션 → 승자 캐릭터 확대 + WINNER 뱃지 표시

### 배틀 스코어 계산
```
battle_score = (str_score + agi_score + hp_score + (100 - debuff_score)) // 4
```

### UI 레이아웃
- 왼쪽: challenger (캐릭터 이미지, 이름, 배틀스코어)
- 가운데: VS 충돌 이펙트 + 결과 텍스트
- 오른쪽: defender (캐릭터 이미지 scaleX(-1) 미러, 이름, 배틀스코어)
- 승자: 캐릭터 scale(1.3) 확대 + 🏆 WINNER 뱃지 (금색)
- 패자: opacity(0.5) + DEFEATED 텍스트 (회색)
- 동점: 양쪽 동일 효과 + DRAW 텍스트

---

## ✅ 구현 완료 사항

### 1. task_11_friend_battle.md 생성

### 2. pages.py — GET /battle 라우트 추가
```python
@router.get("/battle", response_class=HTMLResponse)
async def battle_page(request: Request, challenger: str = ""):
    return templates.TemplateResponse("battle_page.html", {
        "request": request, "challenger": challenger,
    })
```

### 3. api.py — GET /api/components/battle 엔드포인트 추가
- `challenger`, `defender` 쿼리 파라미터 수신
- 두 유저 DB 조회 (`_fetch_user_for_battle`)
- 배틀 스코어 계산 (`_calc_battle_score`)
- `templates/components/battle.html` 렌더링

```python
@router.get("/components/battle", response_class=HTMLResponse)
async def component_battle(request, challenger, defender):
    ...
```

### 4. templates/battle_page.html 신규 생성
- `base.html` 상속
- vanilla `fetch` → `/api/components/battle?challenger=X&defender=Y`
- defender = `localStorage.getItem('user_token')`

### 5. templates/components/battle.html 신규 생성
- 두 캐릭터 나란히 (flexbox)
- 충돌 애니메이션 (CSS transform)
- 승자 확대 + 🏆 WINNER 뱃지

### 6. static/css/style.css — 배틀 CSS 추가
- `@keyframes battleSlideLeft/Right` — 캐릭터 충돌 진입
- `@keyframes winnerPulse` — 승자 맥박
- `@keyframes clashFlash` — 충돌 이펙트 번쩍임

### 7. templates/components/result.html — 배틀 신청 버튼 추가
```html
<button onclick="startBattle()">⚔ 배틀 신청하기</button>
```
```javascript
function startBattle() {
    const battleUrl = location.origin + '/battle?challenger=' + userToken;
    navigator.clipboard.writeText(battleUrl)
        .then(() => alert('배틀 링크가 복사됐습니다! 친구에게 보내세요 ⚔'));
}
```

---

## URL 흐름 정리

```
결과화면 → startBattle() → /battle?challenger={MY_TOKEN} (클립보드 복사)
친구 접속 → GET /result → battle_page.html (base.html 상속)
    ↓ vanilla fetch
GET /api/components/battle?challenger=MY_TOKEN&defender=FRIEND_TOKEN
    → DB에서 두 유저 조회
    → 배틀 스코어 계산
    → battle.html fragment 반환
    ↓
#battle-content에 삽입 → 배틀 애니메이션 시작
```

## Defender 없을 때 처리
- defender 토큰이 비어있거나 DB에 없으면: "친구가 아직 스캔을 완료하지 않았습니다" 안내 + 직접 시작하기 버튼
