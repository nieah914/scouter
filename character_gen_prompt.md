# 캐릭터 스프라이트 생성 프롬프트 (NanoBanana)

## 공통 사양
- **프레임**: 4프레임 가로 배열 (600×150px, 1프레임당 150×150px)
- **배경**: 투명 (transparent background)
- **스타일**: 픽셀 아트, 레트로 RPG, 8-bit
- **저장 위치**: `survival-calculator-mvp/static/images/`

## 파일명 규칙
| 상태 | 파일명 |
|------|--------|
| 기본(idle) | `{character_id}_sprite.png` |
| 승리(victory) | `{character_id}_victory_sprite.png` |
| 패배(dead) | `{character_id}_dead_sprite.png` |

## 애니메이션 방식
4프레임을 빠르게 순환(loop)하여 움직임을 표현.
프레임4 → 프레임1로 자연스럽게 이어져야 함.

| 상태 | 루프 동작 |
|------|----------|
| **idle** | 숨쉬기/체중이동 — F1(중립) → F2(살짝 위) → F3(최고점) → F4(내려옴) → 반복 |
| **victory** | 점프 세레머니 — F1(준비자세 웅크림) → F2(도약) → F3(공중 최고점) → F4(착지) → 반복 |
| **dead** | 쓰러짐 — F1(충격) → F2(휘청) → F3(낙하) → F4(쓰러진 채 정지) |

---

## 1. 건강신 아바타 (health_avatar)

> 황금 흉갑+백색 망토의 완벽한 근육 영웅. 황금빛 단발, 빛나는 흰 눈, 황금 팔찌·정강이보호대, 전신 황금 오라.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, perfect muscular male hero, golden breastplate white cape golden bracers greaves, radiant golden aura, breathing idle loop: F1 both feet flat on ground arms relaxed at sides aura calm neutral pose, F2 body lifted 3px onto toes chest puffed out arms floating slightly upward aura brightening, F3 body at highest 5px tiptoe head raised chin up arms drifting outward aura fully blazing, F4 heels returning to ground arms swinging gently back aura settling, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, perfect muscular male hero, golden breastplate white cape golden bracers greaves, radiant golden aura blazing, jump celebration loop: F1 knees bent body crouching low arms pulled back ready to jump, F2 launching upward body 10px off ground arms sweeping forward and up golden burst, F3 at peak jump 20px off ground both fists raised above head legs tucked golden explosion, F4 landing feet hitting ground knees absorbing impact arms spread wide triumphant grin, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, perfect muscular male hero, golden breastplate cracked cape torn, aura extinguishing, one-shot defeat: F1 hit impact body jolting backward feet still planted shocked face aura flickering, F2 body bending back at waist knees buckling arms flailing outward, F3 body fully falling backward 45 degrees one arm reaching ground aura gone, F4 flat on back arms spread X eyes completely still, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 2. 소드마스터 (swordmaster)

> 전신 은빛 판금갑옷+파란 깃털 투구+코발트 망토. 허리에 장검, 등에 방패. 바이저 사이로 날카로운 눈만 노출.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, elite knight, full silver plate armor blue gem accents, tall helmet blue feather plume, longsword at hip, kite shield on back, royal blue cape, guard stance breathing loop: F1 both feet planted shoulder-width apart hand resting on sword pommel cape hanging still, F2 weight shifting to front foot body leaning slightly forward hand gripping sword tighter cape lifting, F3 body raised 3px on front toes head slightly forward alert scanning posture cape billowing, F4 weight returning to back foot body upright again hand relaxing cape settling, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, elite knight, full silver plate armor, blue feather plume, longsword drawn held high, royal blue cape, sword pump loop: F1 sword lowered to waist both hands gripping knees slightly bent, F2 sword sweeping upward body rising arms extending overhead, F3 sword fully raised at peak body fully extended on tiptoes cape billowing dramatically, F4 sword coming down in front body settling back knees bending ready to raise again, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, elite knight, silver armor dented visor knocked open, blue cape torn, one-shot defeat: F1 struck hard staggering right foot sliding X eyes appearing visor flying open, F2 sword dropping from grip knees giving way body tilting, F3 falling to knees both hands hitting ground armor clattering, F4 slumped facedown on ground completely motionless sword beside hand cape draped over, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 3. 리치왕 (lich_king)

> 해골 얼굴+파란 불꽃 눈, 검은 뾰족 왕관(보라 보석), 너덜한 흑자색 로브, 골격 손, 보라·초록 사령 에너지. 지면 부유.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, undead lich king, skull face cold blue flame eyes, jagged black crown purple gems, tattered dark robe, skeletal hands, purple green necrotic energy, hovering above ground, float pulse loop: F1 hovering 5px above ground arms at sides energy swirling slowly blue flames low, F2 rising to 8px above ground arms drifting slightly outward energy speeding up flames brightening, F3 at peak 11px above ground arms raised slightly head tilting back energy fully swirling crown crackling, F4 sinking to 6px arms lowering energy calming flames dimming, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, undead lich king, skull face blue flames blazing, jagged black crown, tattered dark robe, skeletal arms, massive necrotic energy explosion, maniacal laugh loop: F1 jaw dropping open wide arms at sides energy building, F2 arms sweeping upward and outward blue flames surging energy spiraling, F3 arms fully spread wide at peak skull jaw open maximally energy exploding outward crown flashing, F4 arms slowly lowering jaw partially closing energy radiating out, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, undead lich king, skull face flames extinguishing, crown cracking, tattered robe, one-shot crumble: F1 hover destabilizing tilting sideways crown askew flames sputtering, F2 losing hover dropping 15px body fragmenting bones separating, F3 mid-air fully apart skull detached crown falling robe shredding, F4 pile of bones and robe on ground crown beside it blue flames completely gone dark, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 4. 번아웃 유령 (burnout_ghost)

> 반투명 창백한 청백 몸체. 다크서클+졸린 눈. 구겨진 와이셔츠+풀린 넥타이. 넘치는 커피잔. 하체는 안개로 소멸. 구부정한 자세.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, exhausted office ghost, translucent pale blue-white body, dark circles droopy eyes, crumpled white shirt loosened necktie, overflowing coffee cup in hand, lower body fading to mist, drowsy float loop: F1 floating at base height head drooped forward eyes half-closed coffee cup tilted 30 degrees, F2 head drooping further chin nearly to chest eyes fully closed coffee tilting more spilling slightly, F3 body dipping 5px lower head fully dropped coffee almost horizontal about to spill completely, F4 head snapping back up startled eyes briefly wide coffee jerking upright, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, exhausted office ghost, translucent pale blue-white body, dark circles, crumpled shirt loosened necktie, coffee cup, shocked disbelief jump loop: F1 floating low eyes suddenly wide open coffee frozen in shock, F2 shooting upward 15px body elongating eyes huge coffee flying off to side, F3 at peak height 25px arms flailing upward coffee fully spilled mouth open in silent scream of disbelief, F4 drifting back down slowly arms falling limply eyes going droopy again exhausted, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, exhausted office ghost, translucent body, dark circles, crumpled shirt, one-shot vanish: F1 body opacity dropping to 60% edges getting blurry coffee cup dropping, F2 body opacity 30% outline barely visible only face and tie clear, F3 body opacity 10% nearly invisible only dark circles faintly visible, F4 completely invisible empty space with floating tie and upturned coffee cup, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 5. 겨울잠 곰 (hibernating_bear)

> 거대한 갈색 뚱뚱한 곰. 동그란 풍선 배. 졸린 반감긴 눈. 코에 꿀. 목 두꺼운 겨울털. 꿀단지 껴안음. 짧고 통통한 팔다리.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, large fat brown bear, enormous round belly, sleepy half-closed eyes, honey on nose, thick winter fur ruff, hugging honey pot, deep breathing belly loop: F1 sitting relaxed belly at normal size paws hugging pot eyes barely open, F2 deep inhale belly visibly expanding outward 5px larger paws stretching around bigger belly, F3 belly at maximum inflation 10px larger than F1 cheeks puffed eyes fully closed peaceful, F4 long exhale belly deflating head nodding down slightly pot shifting lower, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, large fat brown bear, enormous round belly, thick winter fur ruff, honey pot, standing roar loop: F1 rising onto hind legs body going from 4 to 2 legs belly swinging forward, F2 standing fully upright belly at full forward extent arms spread wide honey pot in one raised paw, F3 at peak fully stood roaring mouth wide open head thrown back belly shaking, F4 coming back down to all fours front paws landing heavily belly bouncing, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, large fat brown bear, enormous belly, thick fur ruff, honey pot, one-shot sleep collapse: F1 eyes shutting suddenly swaying dangerously side to side honey pot slipping, F2 tipping to the right belly leading the topple paws splaying out, F3 halfway fallen on side belly flopping honey pot in mid-air, F4 fully curled on side snoring X eyes honey pot tipped over beside nose zzz bubbles, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 6. 오거 군주 (ogre_lord)

> 짙은 녹색 피부+울퉁불퉁 근육. 이마에 굵은 뿔 두 개. 충혈된 붉은 눈+엄니. 녹슨 쇠 어깨 갑옷+가죽 허리. 거대한 뼈다귀 손에 쥠.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, massive ogre lord, dark green warty skin, two thick curved horns, bloodshot red eyes tusks, rusty iron pauldron bare muscular torso, crude loincloth, enormous bone drumstick club, lumbering sway loop: F1 weight on left foot body leaning left club resting on right shoulder, F2 weight transferring to center body straightening club lifting off shoulder slightly, F3 weight shifting to right foot body leaning right club swinging to left shoulder drool from tusks, F4 weight transferring back to center club lifting again, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, massive ogre lord, dark green skin, curved horns, bloodshot eyes, rusty pauldron, loincloth, giant bone drumstick, eating celebration loop: F1 drumstick pulled back from mouth big bite already taken cheeks bulging eyes rolling in pleasure, F2 chewing vigorously both cheeks stuffed full eyes closed in ecstasy head tilting back, F3 swallowing dramatically neck bulging free fist raised high stomping foot, F4 drumstick back to mouth for another bite drooling, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, massive ogre lord, dark green skin, curved horns, rusty pauldron, one-shot collapse: F1 hit hard lurching backward X eyes appearing drumstick flying from hand, F2 enormous body tipping forward arms pin-wheeling, F3 mid-fall body horizontal ground rushing up, F4 massive body face-down on ground shaking earth X eyes drumstick bouncing beside hand, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 7. 언데드 네크로맨서 (necromancer)

> 깊은 후드 아래 창백한 얼굴+보라빛 눈. 해골 문양 검은 로브. 앙상한 긴 검은 손톱. 해골 지팡이(초록 불꽃). 발 아래 어두운 그림자.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, dark necromancer, deep hood pale face glowing purple eyes, skull-embroidered black robe, gaunt bony hands long black fingernails, skull-topped staff green flames, dark shadow beneath, ominous sway loop: F1 standing still staff held upright robes hanging straight green flames low, F2 body swaying slightly left free hand rising slowly fingers curling robes beginning to billow, F3 body fully leaned left free hand raised head tilting examining hand purple eyes brightening green flames surging robes billowing, F4 body swaying back right hand lowering robes settling flames dimming, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, dark necromancer, deep hood blazing purple eyes, skull-embroidered robe, gaunt hands, skull staff surging green flames, summon loop: F1 staff plunged into ground both hands gripping it purple eyes narrowed concentrating energy building, F2 green energy erupting from ground around feet hands raised summoning, F3 at peak eruption undead skeleton hands reaching from ground staff crackling purple eyes blazing wide robes exploding outward, F4 energy settling staff pulled back up surveying coldly, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, dark necromancer, hood falling back, skull robe, staff cracking, one-shot collapse: F1 staggered backward hood flying off head revealing full pale face green flames sputtering, F2 staff cracking in half knees hitting ground, F3 toppling forward broken staff falling, F4 face-down on ground hood spread around head staff broken beside X eyes green flames extinguished, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 8. 드워프 탱커 (dwarf_tanker)

> 키 작고 정사각형 체형. 오렌지 두 갈래 땋은 수염. 전신 두꺼운 철제 판금갑옷. 왼손 큰 원형 방패(산 문양), 오른손 짧은 전투도끼. 뿔 없는 철제 투구.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, short stocky dwarf warrior, wide square body, long orange braided beard, full heavy iron plate armor, large round tower shield mountain emblem, short battle axe, hornless iron helmet, weight shift loop: F1 weight on right foot shield planted beside right leg axe across left shoulder beard still, F2 weight shifting to center body bouncing slightly up 3px shield lifting off ground axe swinging down, F3 weight on left foot body tilting left shield tapping ground left axe going to right shoulder beard swaying, F4 weight bouncing back to center shield lifting again, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, short stocky dwarf warrior, long orange braided beard, full iron plate armor, large round tower shield, short battle axe, helmet, stomping jump loop: F1 knees bending deeply body crouching shield and axe pulled in close, F2 leaping off ground 15px body fully extended shield raised axe raised, F3 at peak of jump 25px off ground axe and shield crashed together overhead beard flying, F4 landing with both feet simultaneously stomping hard ground cracking shield and axe lowering, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, short stocky dwarf warrior, dented iron armor, orange beard, one-shot sit-down: F1 hit hard helmet spinning on head axe fumbled from grip, F2 sitting down heavily on ground with loud clank helmet covering eyes, F3 leaning back against shield dizzy stars orbiting head beard over face, F4 fully slumped sitting propped against shield X eyes helmet sideways beard splayed snoring, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 9. 오크 버서커 (orc_berserker)

> 회록색 피부+아래턱 엄니 두 개. 충혈된 분노한 눈. 붉은 전쟁 페인팅+부족 문신. 가죽·쇠조각 조잡한 갑옷. 양손 이빠진 손도끼. 짐승이빨 목걸이.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, huge muscular orc berserker, gray-green skin, upward tusks, bloodshot red eyes, red war paint tribal tattoos, crude patchwork armor, two chipped hand axes, beast tooth necklace, aggressive sway loop: F1 leaning forward weight on front foot both axes crossed in front chest heaving, F2 rocking back weight shifting to back foot arms separating axes swinging outward to sides, F3 weight fully on back foot body upright axes raised to shoulder height snorting aggressively, F4 rocking forward again body leaning axes swinging back inward, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, huge muscular orc berserker, gray-green skin, upward tusks, war paint blazing, crude armor, two chipped axes, beast tooth necklace, berserker jump scream loop: F1 crouching low both axes pulled back behind body knees bent, F2 leaping 15px off ground arms sweeping axes forward crossing, F3 at peak 25px jump axes crossed above head screaming mouth fully open veins bulging, F4 landing both feet crashing axes slamming down to sides kneeling briefly, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, huge muscular orc berserker, gray-green skin, war paint smeared, crude armor, one-shot face-down: F1 hit staggering backward one axe flying from grip confused X eyes, F2 second axe dropping arms going limp massive body tipping forward, F3 falling forward enormous body mid-fall, F4 crashed face-down on ground both axes beside hands X eyes war paint smeared, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 10. 엘프 레인저 (elf_ranger)

> 날씬하고 키 큰 여성 엘프. 뾰족한 긴 귀. 은빛 긴 생머리. 에메랄드 초록 눈. 잎사귀 모양 초록 뺨 문신. 초록·갈색 가죽 레인저 갑옷. 등에 화살통, 손에 나무 장궁.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, slender tall female elf ranger, long pointed ears, flowing long silver hair, emerald green eyes, leaf facial tattoo, green brown leather ranger armor, longbow in hand, quiver on back, leather boots, graceful sway loop: F1 standing upright bow held at side silver hair hanging still weight on both feet, F2 weight shifting to right hip body curving slightly left hand moving to quiver touching an arrow hair beginning to sway, F3 body fully shifted to right hip left arm raising bow half-drawn hair mid-sway ears perked, F4 weight returning to center bow lowering hand leaving quiver hair settling back, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, slender tall female elf ranger, long pointed ears, flowing long silver hair, emerald green eyes, leaf facial tattoo, green brown leather ranger armor, longbow, quiver, leather boots, aerial flip celebration loop: F1 crouching low bow behind back both hands free knees bent, F2 launching upward 15px body tucking into spin hair whipping in circle, F3 at peak 25px inverted mid-backflip hair fully spread in circle above, F4 landing perfectly on one foot bow drawn in smooth flourish hair settling, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, slender tall female elf ranger, long pointed ears, silver hair disheveled, green brown armor, longbow dropped, arrows spilling, one-shot graceful fall: F1 struck stumbling sideways silver hair sweeping forward bow slipping, F2 sinking to knees both hands reaching forward hair covering face quiver spilling arrows, F3 body folding slowly to the side halfway to ground, F4 lying on side curled gently X eyes silver hair spread around head bow beside hand arrows scattered peaceful expression, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 11. 마법사 (wizard)

> 가슴까지 내려오는 흰 수염의 노인. 별·달 수놓인 남색 긴 로브. 앞으로 구부러진 높은 뾰족 남색 마법사 모자. 수정 구슬 달린 나무 지팡이. 반달형 두꺼운 눈썹, 빛나는 파란 눈.

### Idle
```
pixel art sprite sheet, 4 frames looping animation horizontal, old wizard, long white beard to chest, navy blue robe with gold star moon embroidery, tall pointed navy wizard hat brim curled, wooden staff with glowing crystal orb, crescent eyebrows, glowing blue eyes, contemplative sway loop: F1 leaning on staff slightly body weight on staff hand white beard hanging still orb softly glowing, F2 body shifting weight off staff slightly straightening free hand moving upward reaching toward orb, F3 free hand cupping orb examining it closely body leaning toward orb eyes brightening, F4 hand pulling away satisfied patting beard body leaning back on staff orb pulsing warmly, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Victory
```
pixel art sprite sheet, 4 frames looping animation horizontal, old wizard, long white beard, navy star-moon robe, tall pointed wizard hat, wooden staff glowing crystal orb, victory magic burst loop: F1 both hands on staff orb charging up body crouching, F2 launching upward 10px staff thrust overhead orb crackling, F3 at peak jump 20px off ground staff fully extended above head orb exploding in starburst hat tilting wildly beard flying, F4 floating gently back down staff lowering orb dimming beard still flying, loop back to F1, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

### Dead
```
pixel art sprite sheet, 4 frames sequential animation horizontal, old wizard, long white beard, navy star-moon robe, wizard hat, staff crystal orb going dark, one-shot topple: F1 hat spinning off head staff wobbling orb flickering confused surprised old man, F2 sitting down heavily on ground staff slipping from hands orb dark, F3 flopping slowly backward arms out beard splaying, F4 flat on back X eyes hat upside-down beside him staff beside him beard spread out orb completely dark, 150x150px per frame 600x150px total, transparent background, retro RPG 8-bit style, clean pixel art no anti-aliasing, white outline, game asset
```

---

## 생성 체크리스트

| 캐릭터 | idle | victory | dead |
|--------|------|---------|------|
| health_avatar | [ ] | [ ] | [ ] |
| swordmaster | [ ] | [ ] | [ ] |
| lich_king | [ ] | [ ] | [ ] |
| burnout_ghost | [ ] | [ ] | [ ] |
| hibernating_bear | [ ] | [ ] | [ ] |
| ogre_lord | [ ] | [ ] | [ ] |
| necromancer | [ ] | [ ] | [ ] |
| dwarf_tanker | [ ] | [ ] | [ ] |
| orc_berserker | [ ] | [ ] | [ ] |
| elf_ranger | [ ] | [ ] | [ ] |
| wizard | [ ] | [ ] | [ ] |
