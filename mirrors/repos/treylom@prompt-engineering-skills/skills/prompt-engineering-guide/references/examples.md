# 미디어 생성 가이드 (Veo / Nano Banana)

Veo 동영상 생성과 Nano Banana 이미지 생성 프롬프트 가이드.

---

## Veo (Google 동영상 생성)

Veo 3.1은 Google의 최첨단 동영상 생성 모델로, 오디오와 함께 고품질 동영상을 생성합니다.

### 모델 사양

| 항목 | Veo 3.1 |
|------|---------|
| 해상도 | 720p, 1080p |
| 길이 | 4초, 6초, 8초 (확장 시 최대 141초) |
| 프레임 속도 | 24fps |
| 오디오 | 기본 포함 |

### 주요 기능

| 기능 | 설명 |
|------|------|
| **동영상 확장** | 이전 Veo 생성 동영상을 7초씩 최대 20배까지 확장 |
| **프레임별 생성** | 첫 번째/마지막 프레임 지정하여 보간 생성 |
| **참조 이미지** | 최대 3개 참조 이미지로 스타일/콘텐츠 안내 (Veo 3.1) |

### 프롬프트 필수 요소

1. **주제 (Subject)**: 사물, 사람, 동물, 풍경
2. **동작 (Action)**: 걷기, 달리기, 머리 돌리기
3. **스타일 (Style)**: SF, 공포, 필름 누아르, 만화

### 선택 요소

| 카테고리 | 예시 |
|----------|------|
| **카메라 위치/모션** | 공중 촬영, 눈높이, 돌리 샷, POV, 로우 앵글 |
| **구도** | 와이드 샷, 클로즈업, 싱글 샷, 투 샷 |
| **포커스/렌즈** | 얕은/깊은 포커스, 소프트 포커스, 매크로 렌즈, 광각 렌즈 |
| **분위기** | 파란색 톤, 야간, 따뜻한 색조 |

### 오디오 프롬프트 (Veo 3+)

```
# 대화 - 따옴표 사용
'이게 열쇠일 거야'라고 그는 중얼거렸습니다.

# 음향 효과 - 명시적 설명
타이어가 크게 삐걱거리고 엔진이 굉음을 냄

# 주변 소음 - 환경 설명
희미하고 섬뜩한 험이 배경에 울려 퍼집니다.
```

### 부정적 프롬프트

동영상에 포함하고 싶지 **않은** 요소 지정:

```
❌ 피하세요: "벽 없음", "하지 마세요"
✅ 권장: "wall, frame" (단순 나열)
```

### 프롬프트 예시

**간단한 프롬프트:**
```
눈표범 같은 털을 가진 귀여운 생물이 겨울 숲을 걷고 있는
3D 만화 스타일의 렌더링입니다.
```

**상세한 프롬프트 (권장):**
```
재미있는 만화 스타일의 짧은 3D 애니메이션 장면을 만들어 줘.
눈표범 같은 털과 표정이 풍부한 커다란 눈,
친근하고 동글동글한 모습을 한 귀여운 동물이
기발한 겨울 숲을 즐겁게 뛰어다니고 있습니다.

이 장면에는 둥글고 눈 덮인 나무, 부드럽게 떨어지는 눈송이,
나뭇가지 사이로 들어오는 따뜻한 햇빛이 담겨 있어야 합니다.
밝고 경쾌한 색상과 장난기 넘치는 애니메이션으로
낙관적이고 따뜻한 분위기를 연출하세요.
```

**대화가 포함된 프롬프트:**
```
안개가 자욱한 미국 북서부의 숲을 넓게 촬영한 장면
지친 두 등산객인 남성과 여성이 고사리를 헤치고 나아가는데
남성이 갑자기 멈춰 서서 나무를 응시합니다.

클로즈업: 나무껍질에 깊은 발톱 자국이 새겨져 있습니다.

남자: (사냥용 칼에 손을 대며) '저건 평범한 곰이 아니야.'
여성: (두려움에 목소리가 떨리며 숲을 둘러봄) '그럼 뭐야?'

거친 짖음, 부러지는 나뭇가지, 축축한 땅에 찍히는 발자국.
외로운 새가 지저귄다.
```

### 동영상 확장

이전 Veo 생성 동영상을 7초씩 최대 20배까지 확장:

```python
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=previous_operation.response.generated_videos[0].video,
    prompt="패러글라이더가 천천히 하강하는 장면으로 확장",
)
```

**제한사항:**
- 입력 동영상 최대 141초
- 가로세로 비율: 9:16 또는 16:9
- 해상도: 720p만 지원

### 참조 이미지 사용 (Veo 3.1)

최대 3개의 참조 이미지로 스타일/콘텐츠 안내:

```python
dress_reference = types.VideoGenerationReferenceImage(
    image=dress_image,
    reference_type="asset"
)

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="여성이 해변을 우아하게 걷는 모습",
    config=types.GenerateVideosConfig(
        reference_images=[dress_reference, glasses_reference, woman_reference],
    ),
)
```

---

## Nano Banana (Google 이미지 생성)

Gemini의 네이티브 이미지 생성 모델입니다. Veo 동영상의 시작 프레임이나 참조 이미지로 활용할 수 있습니다.

### 모델 비교

| 항목 | NB Pro | NB2 |
|------|--------|-----|
| **모델 코드** | `gemini-2.5-flash-image` | `gemini-3.1-flash-image-preview` |
| **프롬프트 스타일** | 태그 나열형 | 서술형(narrative) 권장 |
| **CJK 텍스트** | 보통 | 우수 |
| **속도 (1K)** | 15-20초 | 4-6초 |
| **가격 (4K)** | $0.240 | $0.151 |
| **종횡비** | 기본 5종 | 14종 (극단 비율 포함) |
| **참조 이미지** | 최대 5장 | 최대 14장 |

### 프롬프트 구조

**NB Pro** — 태그 나열형:
1. **주제 설명**: 주요 피사체 명확히 기술
2. **스타일 지정**: 사진, 그림, 3D 렌더링
3. **분위기/조명**: 색조, 조명, 전체 분위기
4. **구도**: 클로즈업, 와이드 샷, 매크로

**NB2** — 서술형 5요소 프레임워크:
1. **Subject**: 주요 피사체 상세 묘사
2. **Action**: 동작/행위/상태 설명
3. **Environment**: 배경, 장소, 시간대
4. **Mood**: 분위기, 색감, 조명
5. **Camera**: 앵글, 거리, 렌즈 효과

### 프롬프트 예시

**초현실적 이미지:**
```
소형 미니어처 서퍼들이 소박한 돌 욕실 싱크대 안에서
바다의 파도를 타는 초현실적인 매크로 사진
빈티지 황동 수도꼭지가 작동하여 끊임없이 파도가 치고 있습니다.
초현실적이고 기발하며 밝은 자연광
```

**캐릭터 디자인:**
```
눈표범 같은 털과 표정이 풍부한 커다란 눈,
친근하고 동글동글한 모습을 한 귀여운 동물
3D 만화 스타일로 렌더링
```

**패션/제품:**
```
분홍색과 푸시아색 깃털이 여러 겹으로 이루어진
하이 패션 플라밍고 드레스
```

**인물 이미지:**
```
어두운 머리와 따뜻한 갈색 눈을 가진 아름다운 여성
```

### Veo 연동 3가지 패턴

**패턴 1: 시작 프레임으로 사용**
```python
# 1. Nano Banana로 이미지 생성
image = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents="황금빛 노을이 지는 해변의 파노라마 풍경",
    config={"response_modalities":['IMAGE']}
)

# 2. Veo로 동영상 생성 (이미지를 시작 프레임으로)
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="카메라가 천천히 해변을 패닝하며 파도가 밀려옵니다",
    image=image.parts[0].as_image(),
)
```

**패턴 2: 참조 이미지로 사용 (Veo 3.1)**
```python
# 여러 참조 이미지 생성
dress_image = generate_image("하이 패션 플라밍고 드레스")
woman_image = generate_image("어두운 머리의 아름다운 여성")
glasses_image = generate_image("분홍색 하트 모양 선글라스")

# Veo에서 참조 이미지로 활용
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="여성이 해변을 우아하게 걷는 모습",
    config=types.GenerateVideosConfig(
        reference_images=[
            types.VideoGenerationReferenceImage(image=dress_image, reference_type="asset"),
            types.VideoGenerationReferenceImage(image=woman_image, reference_type="asset"),
            types.VideoGenerationReferenceImage(image=glasses_image, reference_type="asset"),
        ],
    ),
)
```

**패턴 3: 첫 번째/마지막 프레임 보간**
```python
# 첫 번째 프레임 이미지
first_image = generate_image(
    "프랑스 리비에라 해안에서 빨간색 컨버터블을 운전하는 생강색 고양이"
)

# 마지막 프레임 이미지
last_image = generate_image(
    "절벽에서 출발하는 빨간색 컨버터블과 생강색 고양이"
)

# Veo로 보간 동영상 생성
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    image=first_image,
    config=types.GenerateVideosConfig(last_frame=last_image),
)
```

### 프롬프트 최적화 팁

**설명적인 언어 사용:**
```
❌ "강아지 사진"
✅ "햇살 가득한 공원에서 뛰노는 골든 리트리버 강아지, 부드러운 자연광"
```

**스타일 혼합:**
```
"초현실주의적 + 매크로 사진 + 밝은 자연광 + 기발한"
```

**얼굴 세부정보 개선:**
```
"인물 사진 스타일로, 얼굴에 초점을 맞춘 클로즈업"
```

### 용도별 템플릿

**제품 이미지:**
```
[제품명]이 [배경]에 있습니다.
제품 촬영 스타일, 깨끗한 배경, 전문적인 조명
```

**캐릭터 디자인:**
```
[캐릭터 특징]을 가진 [캐릭터 유형]
[스타일] 스타일로 렌더링, [표정/포즈] 표현
```

**풍경 이미지:**
```
[장소]의 [시간대] 풍경
[분위기] 느낌의 [색조] 색상, [구도] 샷으로 촬영
```
