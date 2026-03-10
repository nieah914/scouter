# Todo List — 현대인 생존 전투력 측정기

> 작업 시작 전 이 파일을 확인하고, 완료된 항목은 ✅로 표시한다.

---

## 🔴 HIGH — 기능 구현 (코딩 필요)

### [x] T-11: 친구 배틀 기능 ✅
- **설명**: 결과 화면에서 "⚔ 배틀 신청하기" 버튼 → challenger 토큰이 포함된 URL 공유 → 상대방이 링크 열면 자신의 결과(defender)와 대결 화면
- **배틀 로직**: `battle_score = (str + agi + hp + (100 - debuff)) // 4`
- **UI**: 왼쪽 challenger, 오른쪽 defender, 캐릭터 충돌 애니메이션, 승자 확대 + WINNER 뱃지
- **필요 파일**:
  - [ ] `app/routers/pages.py` — `GET /battle?challenger=TOKEN` 라우트 추가
  - [ ] `app/routers/api.py` — `GET /api/components/battle?challenger=TOKEN&defender=TOKEN` 엔드포인트 추가
  - [ ] `templates/battle_page.html` — base.html 상속, vanilla fetch로 배틀 fragment 로드
  - [ ] `templates/components/battle.html` — 배틀 결과 fragment
  - [ ] `static/css/style.css` — 배틀 애니메이션 CSS 추가
  - [ ] `templates/components/result.html` — "⚔ 배틀 신청하기" 버튼 + `startBattle()` JS 추가
- **배틀 URL 흐름**:
  ```
  결과화면 → startBattle() → /battle?challenger={MY_TOKEN}
  상대방 접속 → battle_page.html → fetch /api/components/battle?challenger=X&defender=localStorage.token
  ```

---

## 🟡 MEDIUM — 에셋 생성 (이미지 프롬프트)

### [ ] T-12: 캐릭터 스프라이트 이미지 생성
- **설명**: 11개 캐릭터 × 3가지 상태(Idle/Victory/Dead) = 33종 스프라이트 시트 필요
- **사양**: 4프레임 가로 배열, 1프레임 150×150px → 전체 600×150px, 투명 PNG
- **애니메이션 스타일**: 픽셀 아트, retro RPG, 8-bit

| 캐릭터 | character_id | idle | victory | dead |
|--------|-------------|------|---------|------|
| 건강신 아바타 | health_avatar | ✅필요 | ✅필요 | ✅필요 |
| 소드마스터 | swordmaster | ✅필요 | ✅필요 | ✅필요 |
| 리치왕 | lich_king | ✅필요 | ✅필요 | ✅필요 |
| 번아웃 유령 | burnout_ghost | ✅필요 | ✅필요 | ✅필요 |
| 겨울잠 곰 | hibernating_bear | ✅필요 | ✅필요 | ✅필요 |
| 오거 군주 | ogre_lord | ✅필요 | ✅필요 | ✅필요 |
| 언데드 네크로맨서 | necromancer | ✅필요 | ✅필요 | ✅필요 |
| 드워프 탱커 | dwarf_tanker | ✅필요 | ✅필요 | ✅필요 |
| 오크 버서커 | orc_berserker | ✅필요 | ✅필요 | ✅필요 |
| 엘프 레인저 | elf_ranger | ✅필요 | ✅필요 | ✅필요 |
| 마법사 | wizard | ✅필요 | ✅필요 | ✅필요 |

- **파일 명명 규칙**:
  - `{character_id}_sprite.png` — idle (기존)
  - `{character_id}_victory_sprite.png` — victory
  - `{character_id}_dead_sprite.png` — dead
- **저장 위치**: `survival-calculator-mvp/static/images/`

#### 이미지 생성 프롬프트 (Midjourney / NightCafe / NanoBanana)
```
pixel art sprite sheet, 4 frames horizontal, {CHARACTER} character, {STATE} animation,
150x150px per frame (600x150px total), transparent background, retro RPG 8-bit style,
clean pixel art, no anti-aliasing, white outline, game asset
```

**캐릭터별 키워드**:
- `health_avatar`: glowing golden hero, radiant aura, muscular
- `swordmaster`: armored knight, shining sword, blue cape
- `lich_king`: undead lich, dark crown, robe, necrotic energy
- `burnout_ghost`: pale ghost, dark circles, slouching, fading transparency
- `hibernating_bear`: large fat bear, sleepy eyes, belly
- `ogre_lord`: massive ogre, holding drumstick, green skin, horns
- `necromancer`: hooded necromancer, skull staff, bone armor
- `dwarf_tanker`: stout dwarf, heavy shield, beard
- `orc_berserker`: muscular orc, dual axes, rage expression
- `elf_ranger`: slim elf, bow, forest green, pointed ears
- `wizard`: robed mage, glowing staff, pointy hat

**상태별 키워드**:
- `idle`: standing, breathing cycle, slight bob
- `victory`: arms raised, celebrating, jumping, triumphant
- `dead`: fallen down, X eyes, lying flat, knocked out

---

## 🟡 MEDIUM — 인프라 연결

### [ ] T-13: Supabase 실제 연결
- Supabase 프로젝트 생성 (free tier)
- `supabase_schema.sql` 실행 (CREATE TABLE + ALTER TABLE 4개 컬럼 포함)
- `.env` 파일에 `SUPABASE_URL`, `SUPABASE_KEY` 입력
- 테스트: 결과 저장 → DB 확인

### [ ] T-14: TossPayments 실제 연결
- TossPayments 개발자 콘솔에서 successUrl, failUrl 등록
  - `successUrl`: `{BASE_URL}/api/payment/success`
  - `failUrl`: `{BASE_URL}/api/payment/fail`
- `.env`에 `TOSS_CLIENT_KEY`, `TOSS_SECRET_KEY` 입력
- 결제 플로우 E2E 테스트

---

## 🟢 LOW — 배포

### [ ] T-15: Vercel / Render 배포
- `requirements.txt` 최신화
- 환경변수 서버에 등록
- 도메인 연결 (optional)

---

## ✅ 완료된 태스크

| 태스크 | 내용 |
|--------|------|
| T-01 | 프로젝트 기획 및 기술 스택 결정 |
| T-02 | FastAPI 프로젝트 구조 설정 |
| T-03 | Supabase 스키마 설계 |
| T-04 | TossPayments 결제 연동 |
| T-05 | OpenAI GPT-4o-mini 질병 예측 |
| T-06 | 설문 → 스탯 계산 로직 |
| T-07 | 결과 화면 (result.html) |
| T-08 | 픽셀 아트 스프라이트 CSS 애니메이션 + 가챠 연출 |
| T-09 | 설문 10문항 확장 (식습관/스트레스/좌식/음주) + 히든 캐릭터 5종 |
| T-10 | 결과 URL 공유 기능 (풀페이지 /result 라우트 + 공유 버튼) |
| T-11 | 친구 배틀 기능 (배틀 URL 공유 + 배틀 결과 화면 + 캐릭터 충돌 애니메이션) |
