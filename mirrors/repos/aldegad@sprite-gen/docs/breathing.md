# Breathe 레이어: 호흡(idle breathing) · 정지 자세 행 — 스프젠 후처리 레이어 계약

> Owns: The idle-breathing post-process layer and the static-pose row recipe · Index: [docs/README.md](README.md)

## 두 모드 — pixel 과 smooth

Breathe 레이어는 큐레이션 사이드카의 행마다 `states.<state>.breathe`로 설정하는 후처리 레이어다. `mode` 값으로 `pixel`과 `smooth`를 지원한다.

모드 선택 기준은 다음과 같다.
- `pixel`: 기본값이다 (`mode` 키를 생략하거나 `"pixel"`로 지정). 픽셀 아트를 위한 모드로, 정수 행과 열 단위의 워프를 사용해 픽셀 그리드를 온전히 유지한다. 출력 바이트와 정규화된 사이드카는 기존과 동일하며 기본 동작도 바뀌지 않았다. 작은 스프라이트와 픽셀 아트에 적합하다.
- `smooth`: 대형 일러스트, 채색된 캐릭터, 비디오 프레임에 사용한다. 픽셀 워프를 적용했을 때 몸통과 함께 머리 전체가 들리거나, 복제된 행이 셀 사이에서 깜빡임(flicker)으로 읽히는 문제를 해결한다.

smooth 모드의 고정 영역과 동작 방식은 다음과 같다.
- 머리와 강체 경계(해부학 측정이 찾은 목 라인) 위의 모든 픽셀은 모든 셀에서 바이트 단위로 제자리를 유지한다. 인물 하단 역시 제자리에 고정된다.
- rigid row, body axis, torso half width, basis rows로 이루어진 pixel 모드의 자동 해부학 측정에 강체 경계상의 목 너비를 추가해 사용한다. 모든 측정은 행의 첫 셀에서 한 번만 수행되며 해당 셀의 배치가 행 전체에 그대로 쓰인다. 비디오 셀 사이에서 정수리가 1픽셀 흔들려도 경계는 움직이지 않는다.
- 가슴은 목 아래 몸통의 `chest_y` 지점, 몸통 중심축에 위치한 원형 가중치(cos^2)를 중심으로 호흡한다. 가중치 너비는 몸통 반폭의 `chest_rx`배, 높이는 목 아래 몸통 높이의 `chest_ry`배다. 들숨 시 가슴 중심은 기준 행의 `depth`배만큼 상승하고, 가슴 타원 중심이 아닌 정점 P에서 바깥쪽으로 `depth_x`만큼 부풀어 오른다.
- 목 바로 아래 중심축 양쪽에 위치한 원형 어깨 가중치 두 개는 가슴 상승량의 `shoulder`배만큼, 가슴보다 `shoulder_lag` 호흡 주기만큼 늦게 올라간다. 측정된 너비 안쪽의 목과 목과 어깨 사이의 칼라(collar)는 움직이지 않는다. 행 전체가 통째로 오르내리지 않는다.
- 한 번의 호흡은 정지 상태에서 솟아오르는 형태다 (들숨 40%, 날숨 60%). 위상 0의 셀이 원본과 바이트 단위로 일치하므로 루프의 이음매와 루프 간 연결부가 온전히 유지된다. `breaths`는 1부터 8까지의 정수로 루프 길이에 정확히 맞춘다. 외부에서 호흡 타이밍을 맞추기 위해(예: 클립 내 큰 손 동작을 피하려는 경우) 각 들숨이 정점에 도달하는 셀 목록인 `breath_peaks`를 지정할 수 있다. 호흡 횟수는 정점의 개수가 되며, `breaths`를 함께 지정할 경우 일치해야 한다. 첫 셀은 정지 상태를 유지하고 루프는 정지 상태로 끝난다. 호흡은 셀 0, 두 정점 사이에서 날숨이 간격의 60%를 차지하고 다음 들숨이 40%를 차지하는 지점, 루프 끝의 정지 상태로 구분된다.

몸이 한쪽으로 돌아간 경우 다음 키들을 조절한다.
- `chest_tilt`: 가슴 가중치를 회전한다 (도 단위, 화면 기준 시계 방향).
- `chest_bias`: 가슴 타원 장축을 따라 가중치 정점 P를 가로 반폭의 비율로 이동한다 (-0.9에서 0.9까지, 음수는 화면 왼쪽). 가중치는 P에서 각 점을 지나는 반직선을 따라 타원 가장자리로 떨어지므로, 가까운 쪽은 짧은 거리에 걸쳐 떨어지고 먼 쪽은 긴 거리에 걸쳐 떨어진다. 가슴 또한 타원 중심이 아닌 P에서 바깥쪽으로 부풀어 오른다.
- `chest_bias_y`: 장축의 수직 방향으로 정점 P를 세로 반높이의 비율로 이동한다 (-0.9에서 0.9까지, 양수는 아래쪽). 정점 P는 타원 내부에 머물러야 하므로, `chest_bias`와 `chest_bias_y`를 합쳐 반지름의 최대 0.9까지만 허용된다 (그렇지 않으면 거부).
- `chest_dir`: 가슴 이동 방향을 수직에서 회전한다 (도 단위, 음수는 위쪽 왼쪽 방향).
- `chest_x`: 몸통 중심축에서 가슴 타원의 중심을 몸통 반폭 단위로 이동한다 (-1에서 1까지). 긴 머리 등으로 인해 몸통 중심축이 한쪽으로 쏠린 인물의 경우 가슴이 중심축 위에 위치하지 않는다. 어깨는 몸통 중심축 기준 기존 위치를 유지한다.
- `chest_flat`: 정점 P에서 가장자리까지 완전히 상승하는 구간의 비율이다 (0에서 0.9까지).
- 왼쪽을 바라보는 몸체에는 음수 값을 사용한다. 이들 키의 기본값은 모두 0이며, 새 값들이 0이거나 생략되면 기존과 동일한 바이트를 출력하고 아무 변화가 없다.

사이드카 키와 기본값, 허용 범위는 다음과 같다.

| 키 | 기본값 | 허용 범위 | 설명 |
|---|---|---|---|
| `depth` | 0.0085 | 0.005에서 0.20 | 들숨 시 가슴 중심 상승 배율 (흉상 일러스트 기준 프레임 높이의 약 0.5%) |
| `depth_x` | 0.028 | 0에서 0.20 | 정점 P에서 바깥쪽으로 부풀어 오르는 폭 |
| `chest_y` | 0.31 | 0.05에서 0.95 | 목 아래 몸통 기준 가슴 중심 세로 위치 |
| `chest_rx` | 0.83 | 0.2에서 3.0 | 몸통 반폭 대비 가슴 가중치 가로 배율 |
| `chest_ry` | 0.28 | 0.05에서 1.5 | 목 아래 몸통 높이 대비 가슴 가중치 세로 배율 |
| `shoulder` | 0.5 | 0에서 1.5 | 가슴 상승량 대비 어깨 상승 배율 |
| `shoulder_lag` | 0.08 | 0에서 0.3 | 가슴 대비 어깨 상승 지연 주기 |
| `chest_tilt` | 0 | -60에서 60 | 가슴 가중치 회전 각도 (도 단위, 시계 방향) |
| `chest_bias` | 0 | -0.9에서 0.9 | 가슴 타원 장축 방향 정점 P 이동 (가로 반폭 비율, 음수는 화면 왼쪽) |
| `chest_bias_y` | 0 | -0.9에서 0.9 | 장축 수직 방향 정점 P 이동 (세로 반높이 비율, 양수는 아래쪽) |
| `chest_dir` | 0 | -90에서 90 | 가슴 이동 방향 각도 (도 단위, 음수는 위쪽 왼쪽) |
| `chest_x` | 0 | -1에서 1 | 몸통 중심축 기준 가슴 타원 중심 이동 (몸통 반폭 단위) |
| `chest_flat` | 0 | 0에서 0.9 | 정점 P에서 가장자리까지 완전히 상승하는 구간 비율 |
| `breaths` | - | 1에서 8 | 루프에 들어맞는 정수 호흡 횟수 |
| `breath_peaks` | - | - | 각 들숨 정점 셀 목록 (외부 타이밍 조절용) |

거부 조건은 다음과 같다.
- 허용 범위를 벗어난 값은 무시되지 않고 거부된다. pixel 행에 smooth 전용 형상 키(`chest_y`, `chest_rx`, `chest_ry`, `shoulder`, `shoulder_lag`, `chest_tilt`, `chest_bias`, `chest_bias_y`, `chest_dir`, `chest_x`, `chest_flat`)나 `breath_peaks`를 지정해도 무시되지 않고 거부된다.
- 정점 P는 타원 내부에 머물러야 하므로, `chest_bias`와 `chest_bias_y`를 합쳐 반지름의 0.9를 초과하면 거부된다.
- `breath_peaks`에 셀 0의 정점이 포함되거나, 정점이 증가하는 순서가 아니거나, 정점 간격이 2셀보다 가깝거나, 마지막 정점이 루프 끝에서 1셀 이내인 경우 거부된다. `breaths`가 함께 지정되었으나 정점 개수와 일치하지 않는 경우도 거부된다.
- smooth 모드에 `lag`(pixel 모드의 진행파)를 지정하면 첫 셀을 움직이게 되므로 무시되지 않고 거부된다.
- 행별 변형 한도(0.25)를 넘는 신장, 접히는(fold) 변위장, 불투명 픽셀이 캔버스 밖으로 밀려나는 경우는 조용히 한도 내로 자르지 않고 즉시 거부한다.
- 기본 형상에서는 가슴 가중치가 몸체 내부에서 0으로 떨어지므로, 인물이 화면 가장자리나 하단에서 잘려 있어도 거부되지 않으며 픽셀이 손실되지 않는다.
- 처리 속도는 960 px 프레임 기준 약 0.2초다.

비디오 루프 셀처럼 큐레이션 실행이 아닌 프레임 폴더를 처리할 때는 독립 명령어를 사용한다.

```bash
sprite-gen breathe <frames> <out> [--mode pixel|smooth] [--depth D] [--depth-x D] [--breaths N] [--breath-peaks ...] [--lag L] [--rigid-row R] [--chest-y ...] [--chest-rx ...] [--chest-ry ...] [--shoulder ...] [--shoulder-lag ...] [--chest-tilt ...] [--chest-bias ...] [--chest-bias-y ...] [--chest-dir ...] [--chest-x ...] [--chest-flat ...]
```

`<frames>`는 파일 이름 순서대로 재생되는 PNG 프레임 폴더다. 사이드카와 동일한 검증과 베이크 처리를 거치므로 같은 값이면 동일한 바이트를 출력한다. 변환된 프레임들을 원본과 동일한 이름으로 저장하고, 적용된 설정과 위상 및 해부학 측정값을 담은 `breathe.json`을 새 폴더에 한 번에 작성한다. 심볼릭 링크를 추적하고 대소문자를 구분하지 않는 디스크의 서로 다른 표기를 동일하게 취급하는 실제 위치를 기준으로, `<out>`과 `<frames>`가 같은 폴더이거나 어느 한쪽이 다른 쪽 내부에 있는 경우 및 이미 존재하면서 비어 있지 않은 폴더는 아무것도 생성하거나 삭제하지 않고 거부하되 기존의 빈 폴더는 허용한다. `<frames>` 폴더에는 어떤 파일도 새로 쓰지 않으며, 프레임을 비롯한 기존 파일을 변경하거나 삭제하지 않는다. 결과물은 `<out>` 옆에 다른 폴더와 겹치지 않는 고유한 이름의 자체 임시 폴더에서 빌드한 뒤 한 번에 제자리로 이동하며, 작업을 완료하지 못했을 때도 오직 직접 만든 임시 폴더만 삭제하고 이전 작업의 잔여 폴더처럼 직접 만들지 않은 폴더는 그대로 둔다.

비디오 루프 셀 처리 예시는 다음과 같다.

```bash
sprite-gen breathe frames/ out_frames/ --mode smooth --depth 0.0085 --breaths 2
```

큐레이션 웹뷰 사용 시 제한사항이 있다. 웹뷰의 실시간 미리보기는 pixel 워프만 반영하므로 smooth 행은 미리보기를 지원하지 않는다. 웹뷰에서는 안내 문구와 함께 원본 프레임을 보여주며, smooth 행의 비디오 내보내기는 거부된다. 사이드카를 저장하면 smooth 설정은 작성한 내용 그대로 보존된다. 실제 결과는 compose 명령어(GIF, atlas) 또는 `sprite-gen breathe` 명령어로 확인해야 한다.

## What Breathe does (from the README, 2026-09-09)

A still idle reads as frozen. **Breathe** turns a single pose into a living loop — deterministic squash & stretch baked on top of your curated frames. No regeneration, no re-extraction, no extra art. One sidecar field:

```json
"breathe": { "depth": 0.05, "breaths": 3 }
```

- **Anatomy-aware.** The engine measures the silhouette: neck bottleneck, symmetric eye pair on neckless blobs, torso-vs-appendage width. Heads stay **bit-identical** across every frame; wings and arms get pushed, never stretched.
- **Pixel-true.** Integer row/column mapping only — every output frame is still clean pixel art on the same grid. A 1px outline stays a 1px outline: the warp preserves silhouette edges and normalizes staircase doubling, anchored on the inner line.
- **A ruler you can grab.** Drag the rigid boundary (red), the body axis (blue), and the torso width (dashed) right on the live playback. The server re-derives the anatomy on release — and the preview keeps breathing while it recalculates.
- **Byte-identical preview.** The webview mirror and the Python bake produce the same bytes, enforced by golden tests. What you watch looping is exactly what ships in the atlas.

<p align="center">
  <img src="assets/breathe-editor.png" width="760" alt="breathe region editor: rigid boundary, body axis and torso width lines over live playback, with the baked phase filmstrip" />
</p>

The same deterministic bake applies to front, side, and back views of any silhouette, including humanoids, blobs, and tentacles.

> SKILL.md Script Map 에서 옮겨온 본문(2026-09-09, 허브 슬림화). `compose_sprite_gif.py` / `compose_sprite_atlas.py` 가 굽는 호흡 레이어, 정지 자세 행 레시피, 큐레이션 뷰의 호흡 편집기 계약을 소유한다. 실측 근거·프레임 게이트는 아래 "정지 자세(Static-Pose) 행 레시피" 절.

- **에이전트 주도 호흡** (사용자가 "숨쉬기 적용해서 뽑아줘" 라고만 해도 됨): 호흡은 사이드카 필드라 뷰 없이도 켤 수 있다 — (1) `states.<state>.breathe = {"depth": 0.06, "breaths": 1, "lag": 0.1}` 만 쓰면 된다. **경계는 선언하지 않는다** — `sprite_gen/anatomy.py` 가 검출한다. 큐레이터를 거치면 그 결과가 사이드카 `anatomy` 에 얼려지고(`GET /api/breathe-anatomy`), 뷰 없이 에이전트가 `breathe` 만 쓴 런은 `anatomy` 가 비어 있어 **굽기가 매번 다시 잰다** — 굽기는 사이드카에 쓰지 않는다. 어느 쪽이든 동작한다. **굽기는 얼린 값을 신뢰하지 않는다 — 언제나 자기 기준 프레임에서 다시 잰다** (얼린 값은 큐레이터 프리뷰용 캐시다). 사이드카와 어긋나면 manifest 의 `sidecar_drift` 로 값을 실어 보고한다. 그 캐시가 아직 유효한지는 기준 프레임의 **입력** 지문(원본 파일 스탬프·픽셀편집·변형·변종)으로 판정하고, 어긋나면 큐레이터가 프리뷰·영상 내보내기를 **거부하며 갱신하라고 알린다** — 조용히 낡은 숫자로 그리지 않는다. 사람이 특정 행에 고정하고 싶을 때만 `rigid_row` 를 준다. (에이전트 직접 쓰기는 `load_curation`→`stamp_curation` 도장 경로 필수, 열린 탭은 새로고침 안내 — 함정 상세: [`troubleshooting.md`](troubleshooting.md)), (2) `compose_sprite_gif.py`/`compose_sprite_atlas.py` 가 자동으로 굽는다. 검증: gif-manifest 의 `breathe.phases`. **구 `splits`/`amplitude`/`subpixel` 은 요란하게 거부된다** — 옮기려면 `sprite-gen migrate-breathe <run-dir> --apply`.
- **정지 자세(sit/lie/carry_idle 등) 행 레시피** — 정지 1컷 + 링크 복제 @ 4fps + 허리선 호흡(breaths 3) + 눈 보이는 방향만 깜빡임. **복제 수 = `recommended_breathe_frames(breathe) − 1`** (호흡당 `SMOOTH_CYCLE_FRAMES`=6 프레임 확보; breaths 3 → 총 18컷) — 짧은 루프(옛 11컷)에 다수 호흡을 우겨넣으면 1px 위상이 매 프레임 토글해 진동으로 읽히던 걸 막는다 (maintainer 2026-07-24). 깜빡임은 **시퀀스 끝 근처**(맨 끝 아님, 뒤에 눈뜬 rest ≥2)에 배치해 루프 이음새 전에 다시 떠 스냅을 없앤다. 실측 도출 근거·자동 적용 절차·프레임 게이트: 아래 "정지 자세(Static-Pose) 행 레시피" 절 (maintainer 확정 2026-07-19, 이징 게이트 2026-07-24).
- 호흡(idle breathing)은 **후처리 레이어**다 (maintainer 확정 2026-07-18) — 스크립트가 아니라 curation.json 사이드카 `states.<state>.breathe = {depth, depth_x?, breaths, lag, rigid_row?, anatomy}` 로 선언하고, compose/GIF 가 재생 시퀀스 위에 결정론(봉투 워프, `sprite_gen/breathe.py`)으로 굽는다. 깜빡임 프레임도 그대로 숨쉰다 (프레임 선택과 직교).
  - **변형은 자르지 않고 강도를 떨군다** (2026-07-25 교체): 스프라이트 전체에 연속 변형장을 걸고 그 강도를 강체 경계에서 0 으로 테이퍼한다. `env=0` 인 행은 가로 사상이 항등이고 세로 누적이 정확히 1씩 늘어 **그 구간이 프레임 간 비트 동일**하다 — 눈·입이 몇 도트뿐이라 근사로는 표정이 뭉갠다. 가로는 행 안에서 밀도를 적분하므로 사상이 단조라 접힘이 없고, 날개 같은 부속은 밀리기만 하고 안 늘어난다.
  - **강체 경계는 가슴이 아니라 목이다.** 가슴은 해부학 개념이라 몬스터마다 다르지만 목은 기하학적 병목이라 안정적으로 잡힌다. 얼굴이 몸통에 있으면(버섯·슬라임) 대칭 눈쌍을 찾아 얼굴 아래로 내린다. 병목도 얼굴도 없으면 어깨-기울기로 떨어지고 그 사실이 `anatomy.warnings` 에 남는다.
  - 큐레이션 뷰: 줄 헤더 호흡 체크박스(즉시 on/off) + 라벨 클릭 편집기(실재생 위 **강체 경계 1개 드래그** · 세로 진폭 `depth` · 가로 진폭 `depth_x`(기본 "=세로", 0 = 가로 끄기 — maintainer 요청 2026-07-30 가로/세로 분리) · 루프당 호흡 횟수 · `auto` 되돌리기 — 즉시 반영, Esc 복원, 최종 굽기 필름스트립). 루프 길이는 시퀀스 그대로 불변이고 위상이 연속값이라 breaths 는 요청 그대로 적용된다 (범위 1~8이고 **정수여야 한다**; 밖이거나 비정수면 조용히 깎지 않고 요란하게 거부한다 — `depth` 0.005~0.20, `depth_x` null|0~0.20, `lag` 0~0.45 도 같다). 재추출/굽기 대기 없음.
  - 세로선(몸통 밴드)을 **사람이 조정하면** 보호 램프가 밴드 자체에 앵커된다 — 밴드 밖 열은 늘어나지 않고 밀리기만 한다. 자동 검출 밴드는 부속(날개·긴 팔)이 실재할 때만 켜지는 기존 계약 그대로다 (블롭에서 밴드 조정이 무력했던 버그 수리, 2026-07-30).

## 정지 자세(Static-Pose) 행 레시피

> `docs/static-pose-recipe.md` 에서 병합(2026-09-09, 본문 verbatim). 호흡 레이어와 정지 자세 레시피는 한 계약이라 한 문서가 소유한다.

합성 정지 자세 회귀에서 도출한 결정론적 레시피다.

### 적용 대상

이동/액션이 아닌 모든 "가만히 있는" 상태: `idle`, `sit`, `sit_chair`, `lie`,
`carry_idle` 등. 로코모션(walk/run/jump)과 action 행에는 적용하지 않는다.

### 레시피

1. **정지 1컷 + 링크 복제**: 추출 프레임 중 최적 정지 포즈 1장을 고르고
   (사람 검수 대상; 기본 후보 frame 0), 나머지 시퀀스는 전부 그 프레임의
   **링크 복제**로 채운다 — 편집 truth 1곳, 아틀라스 셀 공유(무비용).
2. **길이 = 호흡당 최소 프레임 확보** @ 4fps. 시퀀스 길이는
   `sprite_gen/effects/breathe.py` `recommended_breathe_frames(breathe)` 로 정한다
   (호흡당 `SMOOTH_CYCLE_FRAMES`=6 프레임): 기본 `breaths: 3` → **18컷**
   (~4.5s 루프, 호흡당 1.5s). **옛 11컷은 사이클당 ~3.7프레임이라 1px 위상이
   거의 매 프레임 토글해 호흡이 아니라 진동으로 읽힌다**. 이 게이트가 그 원인을 막는다. 깜빡임 프레임은 이 길이에
   포함되며 별도로 +하지 않는다 (아래 4).
3. **호흡 레이어**: `breathe = {depth: 0.06, breaths: 3, lag: 0.1}` 만 쓴다.
   **강체 경계는 선언하지 않는다** — `sprite_gen/effects/anatomy.py` 가 목 병목(없으면 대칭
   눈쌍 아래, 그것도 없으면 어깨-기울기)으로 검출해 사이드카 `anatomy` 에 채운다.
   **굽기는 그 값을 캐시로만 본다** — 매번 자기 기준 프레임에서 다시 재고, 사이드카와
   어긋나면 manifest 의 `sidecar_drift` 로 값을 실어 보고한다. 사이드카의 `anatomy` 는
   큐레이터 미리보기가 굽기와 같은 경계로 그리려고 들고 있는 것이고, 그게 아직 유효한지는
   `fingerprint`(기준 프레임의 **입력** 키 — `breathe.reference_key`)로 판정한다.
   특정 행에 고정해야 할 때만 `rigid_row`.
   위상이 연속값이라 이징을 위한 별도 옵션이 없다 — 부드러움은 프레임 수(위 2)로 얻는다.
4. **깜빡임은 눈이 보이는 방향만**: 시퀀스 **끝 근처**(맨 끝 아님)에 배치하고
   뒤에 눈-뜬 rest 프레임을 **최소 2장** 남긴다 — 그래야 감았다가 루프 이음새
   전에 다시 뜨며 이어진다 (맨 끝 1프레임이면 감은 채로 끝나 다음 루프 첫
   프레임에서 확 떠 스냅난다). 감은-눈은 rest 위상 프레임에
   얹어 몸통은 그대로 두고 눈만 바뀌게 한다.
   - 정면(down): 독립(unlink) 복제 2장에 감은-눈 픽셀 ops (open→closed→open
     읽히게), 뒤에 rest 프레임 ≥2.
   - 옆(side): 동일 (독립 복제 감은-눈 + 뒤 rest ≥2).
   - 뒤(up): 깜빡임 없음.
   감은-눈 픽셀은 **사람이 깎는다** — 자세마다 눈 위치가 달라 자동 이식
   금지 (포즈별 눈 좌표가 다르면 눈이 엉뚱한 데 감긴다).
5. **변형/픽셀 편집은 정지 원본 프레임에만** — 복제는 링크 동기화로 따라온다.

### 자동 적용 절차 (에이전트)

새 정지 자세 행이 추출되면 (큐레이션 없음 전제):

1. `curation.json` `states.<state>` 에: `selected=[still]`,
   `order=[still]+클론N`, `clones={새 idx: still}` (링크 기본 — 편집 복사 금지),
   breathe 위 레시피. **N = `recommended_breathe_frames(breathe) − 1`** (정지
   원본 1장 제외; 기본 breaths 3 → 17 클론 → 총 18컷). 링크 복제라 아틀라스
   셀은 안 늘어난다 — 호흡 위상당 유니크 셀만 굽는다. 18컷 `breaths: 3` 이면 유니크 칸 6개(위상이 6종만 반복).
2. fps 4 를 `sprite-request.json` 해당 상태에 기록.
3. 깜빡임(정면/옆)은 자동 생성하지 않는다 — "깜빡임 추가 대기" 로 보고하고
   사람이 정지 프레임 확정 후 눈을 깎는다.
4. 열린 큐레이션 탭이 있으면 두-작성자 충돌 방지를 위해 새로고침을 안내한다.

## Related

- [docs/README.md](README.md) — documentation index
