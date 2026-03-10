# Task: Pixel Art Sprite CSS Animation (Idle/Walk)
서비스의 메인 랜딩 화면과 결과 화면(`result.html`)에 노출될 RPG 캐릭터 이미지를 살아 움직이게 만들 거야.
우리는 무거운 GIF나 자바스크립트를 쓰지 않고, 3~4개 프레임이 가로로 나열된 투명 PNG '스프라이트 시트(Sprite Sheet)'와 **순수 CSS의 `steps()` 함수**를 활용할 거야.

## 1. Static Asset Setup
- `/static/images/` 폴더 경로에 `character_sprite.png`라는 이미지가 있다고 가정해 줘.
- 이 이미지는 가로로 길게 4개의 프레임이 붙어있는 구조야. (예: 1프레임당 150px * 150px 이라면, 전체 이미지 크기는 600px * 150px)

## 2. CSS Sprite Animation Logic (`static/css/style.css`)
- `.pixel-sprite` 라는 공통 CSS 클래스를 만들어 줘.
- **이미지 렌더링 설정:** 픽셀 아트가 브라우저에서 안티앨리어싱(흐릿하게 뭉개짐) 없이 선명한 네모난 픽셀 그대로 보이도록 `image-rendering: pixelated;` 속성을 반드시 넣어줘.
- **애니메이션 키프레임:** `background-position`을 `0`에서 `-100%` (또는 프레임 너비의 곱)로 이동시키는 `@keyframes idle-anim`을 작성해 줘.
- **steps() 적용:** 프레임이 부드럽게 스르륵 넘어가는 게 아니라 딱딱 끊기며 레트로 게임처럼 보이도록 `animation: idle-anim 0.8s steps(4) infinite;` 속성을 적용해 줘.

## 3. Frontend Integration (`templates/components/result.html` 등)
- 결과 화면에서 부여받은 직업/종족(예: 오크 버서커)에 맞는 캐릭터 스프라이트를 띄우는 HTML `<div>` 태그를 작성해 줘.
- 백엔드에서 넘겨준 `character_id` 변수를 이용해 `background-image: url('/static/images/{{ character_id }}_sprite.png');` 형태로 이미지가 동적으로 교체되도록 인라인 스타일을 짜거나 Jinja2 로직을 구성해 줘.
- 모바일 화면에서도 깨지지 않도록 반응형(Responsive) 처리를 약간 추가해 줘 (예: `transform: scale(1.5)` 등).

## 4. Action Required
1. 위 조건을 완벽히 충족하는 CSS 파일(`style.css`)의 코드를 작성해 줘.
2. `result.html`에 이 CSS 클래스를 적용하여 캐릭터가 움직이도록 하는 HTML 렌더링 코드를 추가해 줘.

---

## ✅ 변경 사항 (가챠 연출 + 히든 캐릭터 이미지 확장)

### style.css 추가된 애니메이션

**가챠 등급 뱃지 공개 연출**
```css
@keyframes gradeReveal {
    0%   { transform: scale(0.4) rotateY(90deg); opacity: 0; filter: brightness(4); }
    50%  { transform: scale(1.25) rotateY(0deg); opacity: 1; filter: brightness(2); }
    75%  { transform: scale(0.95); filter: brightness(1.3); }
    100% { transform: scale(1); opacity: 1; filter: brightness(1); }
}
.gacha-grade-reveal { animation: gradeReveal 0.65s cubic-bezier(...) forwards; }
```

**캐릭터 바운스 등장**
```css
@keyframes charBounceIn {
    0%   { transform: translateY(-30px) scale(0.7); opacity: 0; }
    60%  { transform: translateY(6px) scale(1.08); opacity: 1; }
    100% { transform: translateY(0) scale(1); opacity: 1; }
}
.gacha-char-reveal { animation: charBounceIn 0.55s ease forwards; }
```

**스탯바 초기 숨김 → 채움 전환**
```css
/* 원본 .stat-bar-fill에 통합 (중복 선언 금지) */
.stat-bar-fill {
    height: 100%;
    background: var(--rpg-green);
    border-radius: 4px;
    width: 0;                                                    /* 초기값 */
    transition: width 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94); /* 부드러운 채움 */
}
```

> ⚠️ **버그 이력 1**: 최초 구현 시 `.stat-bar-fill`을 가챠 섹션에 중복 선언하면서 `width: 0 !important` 사용.
> CSS `!important`는 JS `element.style.width` 인라인 설정보다 우선순위가 높아 게이지가 항상 0으로 고정되는 버그 발생.
> → 중복 선언 제거 후 원본 선언에 `width: 0` (일반 값)으로 통합하여 해결.

> ⚠️ **버그 이력 2**: `calculate_result` 및 `_render_paid_result`에서 `str_score`, `agi_score`, `hp_score`를 Jinja2 템플릿 컨텍스트에 전달하지 않음.
> Jinja2는 미정의 변수를 빈 문자열 `""`로 렌더링 → `data-width=""` → JS `'' || '0'` = `'0%'` → 게이지 항상 0.
> → 세 엔드포인트(calculate_result, _render_paid_result, _render_free_result) 모두에 `str_score`, `agi_score`, `hp_score` 추가하여 해결.

### result.html 변경 사항
- 캐릭터 스프라이트에 `.pixel-sprite-animated` 클래스 추가 → Idle 애니메이션 활성화
- 등급 뱃지 `id="grade-badge"`, 캐릭터 `id="char-display"`, 타이틀 `id="char-title"`, 스탯 `id="stat-overview"` → JS 가챠 시퀀스 타겟
- 스탯바 `<div class="stat-bar"><div class="stat-bar-fill" data-width="{{ score }}">` 방식으로 교체
- JS 스탯바 채움: **double requestAnimationFrame** 사용 — 브라우저가 `width:0` 초기 상태를 한 프레임 렌더링한 뒤 최종 값으로 변경해야 transition이 발동됨. `rAF` 1회로는 렌더링 전에 값이 쓰여 transition이 작동하지 않는 타이밍 버그 발생.
- 히든 캐릭터 여부에 따라 상단 배지 텍스트 분기:
  - 히든: `⚠ HIDDEN ENTITY DETECTED ⚠` (빨간색, animate-pulse)
  - 일반: `[ SCAN COMPLETE ]` (노란색)

### 스프라이트 이미지 필요 목록 (11종)
기존 6종에서 5종 추가:
```
/static/images/health_avatar_sprite.png   ← 신규
/static/images/lich_king_sprite.png        ← 신규
/static/images/burnout_ghost_sprite.png   ← 신규
/static/images/hibernating_bear_sprite.png ← 신규
/static/images/ogre_lord_sprite.png       ← 신규
/static/images/swordmaster_sprite.png     ← 기존
/static/images/necromancer_sprite.png     ← 기존
/static/images/dwarf_tanker_sprite.png    ← 기존
/static/images/orc_berserker_sprite.png   ← 기존
/static/images/elf_ranger_sprite.png      ← 기존
/static/images/wizard_sprite.png          ← 기존
```
