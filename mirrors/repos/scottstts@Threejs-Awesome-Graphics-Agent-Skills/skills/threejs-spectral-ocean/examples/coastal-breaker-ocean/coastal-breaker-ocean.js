import * as THREE from "three/webgpu";
import {
  generateCapillaryNoiseTexture,
  generateFoamPatternTexture,
  generateGravityNoiseSet,
} from "./source/noise.js";
import { WaveField } from "./source/wave-field.js";
import { Ocean } from "./source/ocean.js";
import { FoamSim } from "./source/foam.js";
import { ChainSim, sampleWaveLevel } from "./source/chain.js";
import { buildCoast } from "./source/coast.js";
import {
  coastalSkyRadiance,
  createOceanUniforms,
} from "./source/tsl.js";

const GRAVITY = 9.81;
const CAPILLARY_SIGMA_RHO = 7.4e-5;
const CAPILLARY_DISPERSION = 1.5;
const SUN_AZIMUTH = [0.65, -0.76];

export const COASTAL_BREAKER_DEFAULTS = Object.freeze({
  wavelength: 10,
  amplitude: 0.2,
  choppiness: 1.5,
  layers: 5,
  spread: 40,
  waveDir: 0,
  dispersion: 1,
  ripple: 0.2,
  rippleScale: 0.5,
  rippleAniso: 0.8,
  rippleBias: 0.8,
  sss: 1.5,
  depth: 8,
  caustics: 1,
  sun: 10,
  lean: 0.5,
  foam: 0.6,
  foamLife: 4,
  foamScale: 1,
});

export const coastalBreakerDebugModes = new Map([
  ["final", 0],
  ["normals", 1],
  ["foam", 2],
  ["shoreline", 3],
  ["wireframe", 4],
]);

export async function loadCoastalBreakerSandTextures(
  renderer,
  { baseUrl, normalUrl },
) {
  const loader = new THREE.TextureLoader();
  const [base, normal] = await Promise.all([
    loader.loadAsync(baseUrl),
    loader.loadAsync(normalUrl),
  ]);

  base.colorSpace = THREE.SRGBColorSpace;
  normal.colorSpace = THREE.NoColorSpace;

  const anisotropy = renderer.getMaxAnisotropy();
  for (const texture of [base, normal]) {
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.magFilter = THREE.LinearFilter;
    texture.minFilter = THREE.LinearMipmapLinearFilter;
    texture.generateMipmaps = true;
    texture.anisotropy = anisotropy;
    texture.needsUpdate = true;
  }

  return { base, normal };
}

export class CoastalBreakerOcean {
  constructor(renderer, { sandBase, sandNormal, parameters = {} }) {
    this.renderer = renderer;
    this.parameters = { ...COASTAL_BREAKER_DEFAULTS, ...parameters };
    this.noise = generateGravityNoiseSet();
    this.capillaryNoise = generateCapillaryNoiseTexture();
    this.foamPattern = generateFoamPatternTexture();
    this.coast = buildCoast();
    this.chain = new ChainSim(this.coast);
    this.uniforms = createOceanUniforms();

    this.waveField = new WaveField(renderer, this.noise);
    this.capillaryField = new WaveField(renderer, this.capillaryNoise);

    const sharedResources = {
      waveTex: this.waveField.texture,
      simTex: this.chain.texture,
      sdfTex: this.coast.sdfTexture,
    };
    this.foam = new FoamSim(renderer, this.uniforms, sharedResources, "world");
    this.filmFoam = new FoamSim(
      renderer,
      this.uniforms,
      sharedResources,
      "film",
      [128, 256],
    );

    this.ocean = new Ocean(this.uniforms, {
      waveTex: this.waveField.texture,
      capTex: this.capillaryField.texture,
      foamTex: this.foam.texture,
      filmFoamTex: this.filmFoam.texture,
      foamPatTex: this.foamPattern.texture,
      simTex: this.chain.texture,
      coastTex: this.chain.coastTexture,
      sdfTex: this.coast.sdfTexture,
      mainTableTex: this.coast.mainTableTexture,
      sandBase,
      sandNormal,
    });
    this.ocean.chain = this.chain;
    this.group = this.ocean.group;
    this.sandBase = sandBase;
    this.sandNormal = sandNormal;
    this.debugMode = "final";
  }

  setDebugMode(mode) {
    this.debugMode = coastalBreakerDebugModes.has(mode) ? mode : "final";
    const value = coastalBreakerDebugModes.get(this.debugMode);
    this.uniforms.debugMode.value = value === 4 ? 0 : value;
    this.parameters.wireframe = value === 4;
  }

  update(delta, cameraPosition, targetPosition) {
    const dt = Math.max(0, delta);
    const p = this.parameters;
    const eye = [cameraPosition.x, cameraPosition.y, cameraPosition.z];

    this.waveField.update(
      dt,
      Math.sqrt(GRAVITY * p.wavelength / (2 * Math.PI)) /
        (p.wavelength * this.noise.wavesPerTile),
      p.dispersion,
    );

    const capillaryK = 2 * Math.PI / p.rippleScale;
    const capillarySpeed = Math.sqrt(
      GRAVITY / capillaryK + CAPILLARY_SIGMA_RHO * capillaryK,
    );
    this.capillaryField.update(
      dt,
      capillarySpeed / (p.rippleScale * this.capillaryNoise.wavesPerTile),
      CAPILLARY_DISPERSION,
    );

    this.chain.update(
      dt,
      p,
      (x, z) => sampleWaveLevel(
        x,
        z,
        this.noise,
        this.waveField,
        this.ocean.layerCache,
      ),
      targetPosition.x,
      targetPosition.z,
    );

    const elevation = p.sun * Math.PI / 180;
    const sunDirection = [
      SUN_AZIMUTH[0] * Math.cos(elevation),
      Math.sin(elevation),
      SUN_AZIMUTH[1] * Math.cos(elevation),
    ];

    this.ocean.update(
      dt,
      p,
      this.noise,
      this.capillaryNoise,
      eye,
      sunDirection,
    );
    this.waveField.render();
    this.capillaryField.render();
    if (dt > 0) {
      this.foam.render();
      this.filmFoam.render();
    }
  }

  metrics() {
    return {
      gravityField: `${this.noise.size}² × ${this.noise.textures.length}`,
      capillaryField: `${this.capillaryNoise.size}²`,
      swashColumns: "256 × 64",
      oceanGrid: `${this.ocean.gridN}²`,
    };
  }

  dispose() {
    const geometries = new Set();
    const materials = new Set();
    this.group.traverse((object) => {
      if (object.geometry) geometries.add(object.geometry);
      if (Array.isArray(object.material)) {
        for (const material of object.material) materials.add(material);
      } else if (object.material) {
        materials.add(object.material);
      }
    });
    for (const geometry of geometries) geometry.dispose();
    for (const material of materials) material.dispose();

    for (const field of [this.waveField, this.capillaryField]) {
      field.target.dispose();
      field.material.dispose();
      field.quad.geometry.dispose();
    }
    for (const foam of [this.foam, this.filmFoam]) {
      for (const target of [...foam.targets, foam.displayTarget]) target.dispose();
      for (const material of [...foam.materials, ...foam.copyMaterials]) {
        material.dispose();
      }
      foam.quad.geometry.dispose();
    }

    for (const texture of this.noise.textures) texture.dispose();
    this.capillaryNoise.texture.dispose();
    this.foamPattern.texture.dispose();
    this.coast.sdfTexture.dispose();
    this.coast.mainTableTexture.dispose();
    this.chain.texture.dispose();
    this.chain.coastTexture.dispose();
    this.sandBase.dispose();
    this.sandNormal.dispose();
    this.group.clear();
  }
}

export { coastalSkyRadiance };
