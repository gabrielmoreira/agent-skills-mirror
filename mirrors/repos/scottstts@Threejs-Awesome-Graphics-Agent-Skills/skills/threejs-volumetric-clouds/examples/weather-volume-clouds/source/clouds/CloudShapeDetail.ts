import { resolveIncludes } from '../geospatial/index.ts'
import { math } from '../geospatial/shaders/index.ts'

import { CLOUD_SHAPE_DETAIL_TEXTURE_SIZE } from './constants'
import { Procedural3DTextureBase } from './Procedural3DTexture'

import fragmentShader from './shaders/cloudShapeDetail.frag?raw'
import perlin from './shaders/perlin.glsl?raw'
import tileableNoise from './shaders/tileableNoise.glsl?raw'

export class CloudShapeDetail extends Procedural3DTextureBase {
  constructor() {
    super({
      size: CLOUD_SHAPE_DETAIL_TEXTURE_SIZE,
      fragmentShader: resolveIncludes(fragmentShader, {
        core: { math },
        perlin,
        tileableNoise
      })
    })
  }
}
