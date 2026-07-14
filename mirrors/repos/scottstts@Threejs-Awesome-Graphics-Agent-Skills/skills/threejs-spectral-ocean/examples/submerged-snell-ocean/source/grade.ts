import {
  ClampToEdgeWrapping,
  Data3DTexture,
  LinearFilter,
  RGBAFormat,
  UnsignedByteType,
} from 'three'
import { lut3D } from 'three/addons/tsl/display/Lut3DNode.js'
import {
  clamp,
  float,
  screenUV,
  smoothstep,
  texture3D,
  uniform,
  vec4,
} from 'three/tsl'

const LUT_SIZE = 32
type AnyNode = object
const asColor = (node: AnyNode) => node as ReturnType<typeof vec4>

export const gradeParams = {
  exposureEV: uniform(0),
  lutIntensity: uniform(1),
  vignette: uniform(0.115),
}

export const dreamLutTexture = createDreamLutTexture()

/** Apply the display-referred 32-cube grade and spatial vignette. */
export function dreamGrade(inputColor: AnyNode) {
  const input = clamp(asColor(inputColor), 0, 1)
  const graded = lut3D(
    input,
    texture3D(dreamLutTexture),
    LUT_SIZE,
    gradeParams.lutIntensity,
  ) as unknown as ReturnType<typeof vec4>
  const centered = screenUV.sub(0.5)
  const falloff = smoothstep(0.38, 0.94, centered.length().mul(1.34))
  const vignetted = graded.rgb.mul(
    float(1).sub(falloff.mul(gradeParams.vignette)),
  )
  return vec4(vignetted.clamp(0, 1), float(1))
}

function createDreamLutTexture(): Data3DTexture {
  const data = new Uint8Array(LUT_SIZE ** 3 * 4)
  let offset = 0
  for (let blue = 0; blue < LUT_SIZE; blue++) {
    for (let green = 0; green < LUT_SIZE; green++) {
      for (let red = 0; red < LUT_SIZE; red++) {
        const graded = gradeSample([
          red / (LUT_SIZE - 1),
          green / (LUT_SIZE - 1),
          blue / (LUT_SIZE - 1),
        ])
        data[offset++] = Math.round(graded[0] * 255)
        data[offset++] = Math.round(graded[1] * 255)
        data[offset++] = Math.round(graded[2] * 255)
        data[offset++] = 255
      }
    }
  }
  const texture = new Data3DTexture(data, LUT_SIZE, LUT_SIZE, LUT_SIZE)
  texture.format = RGBAFormat
  texture.type = UnsignedByteType
  texture.minFilter = LinearFilter
  texture.magFilter = LinearFilter
  texture.wrapS = ClampToEdgeWrapping
  texture.wrapT = ClampToEdgeWrapping
  texture.wrapR = ClampToEdgeWrapping
  texture.generateMipmaps = false
  texture.needsUpdate = true
  texture.name = 'underwaterDreamGrade32'
  return texture
}

function gradeSample(
  color: [number, number, number],
): [number, number, number] {
  const lift = [0.011, 0.026, 0.033] as const
  const gain = [1.042, 1.008, 0.972] as const
  const balanced = color.map(
    (channel, index) => channel * gain[index] + lift[index] * (1 - channel),
  ) as [number, number, number]
  const luminance =
    balanced[0] * 0.2126 +
    balanced[1] * 0.7152 +
    balanced[2] * 0.0722
  const saturation = Math.max(...balanced) - Math.min(...balanced)
  const vibrance = 1 + 0.17 * (1 - saturation)
  return balanced.map((channel) =>
    Math.max(0, Math.min(1, luminance + (channel - luminance) * vibrance)),
  ) as [number, number, number]
}
