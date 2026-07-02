import { resolveIncludes } from '../geospatial/index.ts'
import { math } from '../geospatial/shaders/index.ts'

import { ProceduralTextureBase } from './ProceduralTexture'

import perlin from './shaders/perlin.glsl?raw'
import tileableNoise from './shaders/tileableNoise.glsl?raw'
import fragmentShader from './shaders/turbulence.frag?raw'

export class Turbulence extends ProceduralTextureBase {
  constructor() {
    super({
      size: 128,
      fragmentShader: resolveIncludes(fragmentShader, {
        core: { math },
        perlin,
        tileableNoise
      })
    })
  }
}
