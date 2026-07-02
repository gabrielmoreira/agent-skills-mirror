import * as THREE2 from "three/webgpu";
import {
  Fn,
  abs,
  float as float2,
  max,
  reference,
  renderGroup,
  shadowPositionWorld,
  smoothstep,
  uniform,
  vec4
} from "three/tsl";

import * as THREE from "three/webgpu";
import { float } from "three/tsl";
var BoundedShadowNode = class extends THREE.ShadowNode {
  constructor(light, shadow) {
    super(light, shadow);
  }
  setupShadowFilter(_builder, args) {
    const { filterFn, depthTexture, shadowCoord, shadow, depthLayer } = args;
    const inShadowProjection = shadowCoord.x.greaterThanEqual(0).and(shadowCoord.x.lessThanEqual(1)).and(shadowCoord.y.greaterThanEqual(0)).and(shadowCoord.y.lessThanEqual(1)).and(shadowCoord.z.greaterThanEqual(0)).and(shadowCoord.z.lessThanEqual(1));
    const shadowValue = filterFn({
      depthTexture,
      shadowCoord,
      shadow,
      depthLayer
    });
    return inShadowProjection.select(shadowValue, float(1));
  }
};

var ClipmapLight = class extends THREE2.Object3D {
  target = new THREE2.Object3D();
  castShadow = true;
  shadow;
};
var ORIGIN = new THREE2.Vector3();
var up = new THREE2.Vector3(0, 1, 0);
var lightDirection = new THREE2.Vector3();
var lightOrientationMatrix = new THREE2.Matrix4();
var cameraWorldPosition = new THREE2.Vector3();
var cameraLightPosition = new THREE2.Vector3();
var levelCenter = new THREE2.Vector3();
var regionCenter = new THREE2.Vector3();
var CachedClipmapShadowNode = class extends THREE2.ShadowBaseNode {
  light;
  camera = null;
  levels;
  maxDistance;
  lightMargin;
  shadowCameraNear;
  shadowCameraFar;
  guardBand;
  blendRatio;
  dynamicLevels;
  updateBudget;
  maxCacheAge;
  lights = [];
  _levelMapSizes;
  _halfWidths = [];
  _levelStates = [];
  _levelData = [];
  _shadowNodes = [];
  _worldToLight = new THREE2.Matrix4();
  _lastDirection = new THREE2.Vector3();
  _directionCos;
  _baseBias = 0;
  _baseNormalBias = 0;
  _firstUpdate = true;
  _initialized = false;
  constructor(light, options = {}) {
    super(light);
    this.light = light;
    this.camera = options.camera ?? null;
    if (options.mapSize !== void 0) {
      light.shadow.mapSize.set(options.mapSize, options.mapSize);
    }
    this._levelMapSizes = options.levelMapSizes ?? null;
    const firstRadius = Math.max(options.firstRadius ?? 12, 1);
    const scaleFactor = Math.max(options.scaleFactor ?? 2.5, 1.5);
    this.maxDistance = options.maxDistance ?? 2e3;
    this.levels = options.levels ?? Math.max(
      1,
      Math.ceil(
        Math.log(this.maxDistance / firstRadius) / Math.log(scaleFactor)
      ) + 1
    );
    for (let i = 0; i < this.levels; i++) {
      const halfWidth = Math.min(
        firstRadius * scaleFactor ** i,
        this.maxDistance
      );
      this._halfWidths.push(i === this.levels - 1 ? this.maxDistance : halfWidth);
    }
    this.lightMargin = options.lightMargin ?? 100;
    this.shadowCameraNear = options.shadowCameraNear ?? 1;
    this.shadowCameraFar = options.shadowCameraFar ?? 3e3;
    this.guardBand = THREE2.MathUtils.clamp(options.guardBand ?? 0.15, 0.02, 0.5);
    this.blendRatio = THREE2.MathUtils.clamp(
      options.blendRatio ?? 0.15,
      0.01,
      0.9
    );
    this.dynamicLevels = THREE2.MathUtils.clamp(
      options.dynamicLevels ?? 2,
      0,
      this.levels
    );
    this.updateBudget = Math.max(options.updateBudget ?? 2, 1);
    this.maxCacheAge = Math.max(options.maxCacheAge ?? 64, 0);
    this._directionCos = Math.cos(options.directionEpsilon ?? 2e-3);
  }
  attach() {
    ;
    this.light.shadow.shadowNode = this;
    return this;
  }
  detach() {
    const shadow = this.light.shadow;
    if (shadow.shadowNode === this) delete shadow.shadowNode;
    return this;
  }
  setCamera(camera) {
    this.camera = camera;
    return this;
  }
  setup(builder) {
    if (!this._initialized) this.init(this.camera ?? builder.camera);
    const levelData = reference("_levelData", "vec4", this).setGroup(renderGroup).setName("clipmapLevels");
    const worldToLight = uniform(this._worldToLight).setGroup(renderGroup).setName("clipmapWorldToLight");
    return Fn((fnBuilder) => {
      ;
      this.setupShadowPosition(fnBuilder);
      const lightPos = worldToLight.mul(vec4(shadowPositionWorld, 1)).xy.toVar("clipmapPosition");
      const accumulated = vec4(0, 0, 0, 0).toVar("clipmapShadow");
      const remaining = float2(1).toVar("clipmapRemaining");
      for (let i = 0; i < this.levels; i++) {
        const level = vec4().toVar(`clipmapLevel${i}`);
        level.assign(levelData.element(i));
        const levelDistance = max(
          abs(lightPos.x.sub(level.x)),
          abs(lightPos.y.sub(level.y))
        );
        const fade = float2(1).sub(
          smoothstep(level.z.mul(1 - this.blendRatio), level.z, levelDistance)
        );
        const weight = fade.mul(remaining);
        accumulated.addAssign(this._shadowNodes[i].mul(weight));
        remaining.mulAssign(float2(1).sub(fade));
      }
      return accumulated.add(vec4(remaining));
    })();
  }
  updateBefore(frame) {
    if (!this.camera || !this.light.parent) return;
    for (const levelLight of this.lights) {
      if (levelLight.parent === null) {
        this.light.parent.add(levelLight.target);
        this.light.parent.add(levelLight);
      }
    }
    lightDirection.subVectors(this.light.target.position, this.light.position).normalize();
    lightOrientationMatrix.lookAt(ORIGIN, lightDirection, up);
    this._worldToLight.copy(lightOrientationMatrix).invert();
    const directionChanged = lightDirection.dot(this._lastDirection) < this._directionCos;
    if (directionChanged) this._lastDirection.copy(lightDirection);
    cameraWorldPosition.setFromMatrixPosition(this.camera.matrixWorld);
    cameraLightPosition.copy(cameraWorldPosition).applyMatrix4(this._worldToLight);
    let budget = this._firstUpdate || directionChanged ? this.levels : this.updateBudget;
    this._firstUpdate = false;
    let baseTexelWidth = 0;
    for (let i = 0; i < this.levels; i++) {
      const state = this._levelStates[i];
      const levelLight = this.lights[i];
      const shadow = levelLight.shadow;
      const shadowCamera = shadow.camera;
      const texelWidth = (shadowCamera.right - shadowCamera.left) / shadow.mapSize.width;
      if (i === 0) baseTexelWidth = texelWidth;
      const texelScale = baseTexelWidth > 0 ? texelWidth / baseTexelWidth : 1;
      shadow.bias = this._baseBias;
      shadow.normalBias = this._baseNormalBias * texelScale;
      state.age++;
      const desiredX = Math.round(cameraLightPosition.x / texelWidth) * texelWidth;
      const desiredY = Math.round(cameraLightPosition.y / texelWidth) * texelWidth;
      const quantumZ = state.halfWidth * 0.5;
      const desiredZ = Math.round(cameraLightPosition.z / quantumZ) * quantumZ;
      const isDynamic = i < this.dynamicLevels;
      const moved = desiredX !== state.centerX || desiredY !== state.centerY || desiredZ !== state.centerZ;
      const expired = this.maxCacheAge > 0 && state.age >= this.maxCacheAge;
      const dirty = isDynamic || !state.valid || state.forceDirty || moved || expired || directionChanged;
      const canRender = isDynamic || state.forceDirty || budget > 0;
      if (dirty && canRender) {
        if (!isDynamic && !state.forceDirty) budget--;
        state.centerX = desiredX;
        state.centerY = desiredY;
        state.centerZ = desiredZ;
        state.valid = true;
        state.forceDirty = false;
        state.age = 0;
        levelCenter.set(
          desiredX,
          desiredY,
          desiredZ + state.halfWidth + this.lightMargin
        );
        levelCenter.applyMatrix4(lightOrientationMatrix);
        levelLight.position.copy(levelCenter);
        levelLight.target.position.copy(levelCenter).add(lightDirection);
        levelLight.updateMatrixWorld(true);
        levelLight.target.updateMatrixWorld(true);
        shadow.needsUpdate = true;
        const shadowNode = this._shadowNodes[i];
        if (shadowNode.shadowMap) {
          shadowNode.updateShadow(frame);
          shadow.needsUpdate = false;
        }
      }
      if (state.valid) {
        this._levelData[i].set(
          state.centerX,
          state.centerY,
          state.halfWidth * (1 - this.guardBand),
          0
        );
      }
    }
  }
  /**
   * Force levels to re-render (rate-limited by updateBudget). With a sphere,
   * only levels whose coverage intersects it are dirtied - call this when an
   * important shadow caster moves so coarse cached levels pick it up.
   */
  invalidate(worldBounds) {
    if (!worldBounds) {
      for (const state of this._levelStates) state.forceDirty = true;
      return;
    }
    regionCenter.copy(worldBounds.center).applyMatrix4(this._worldToLight);
    for (const state of this._levelStates) {
      const reach = state.halfWidth + worldBounds.radius;
      if (Math.abs(regionCenter.x - state.centerX) < reach && Math.abs(regionCenter.y - state.centerY) < reach) {
        state.forceDirty = true;
      }
    }
  }
  dispose() {
    this.detach();
    for (const shadowNode of this._shadowNodes) shadowNode.dispose?.();
    for (const levelLight of this.lights) {
      levelLight.shadow?.dispose();
      levelLight.parent?.remove(levelLight);
      levelLight.target.parent?.remove(levelLight.target);
    }
    super.dispose?.();
  }
  init(camera) {
    this.camera = camera;
    this._initialized = true;
    this._baseBias = this.light.shadow.bias;
    this._baseNormalBias = this.light.shadow.normalBias;
    for (let i = 0; i < this.levels; i++) {
      const halfWidth = this._halfWidths[i];
      const levelLight = new ClipmapLight();
      const levelShadow = this.light.shadow.clone();
      const levelMapSize = this._levelMapSizes?.[i] ?? this.light.shadow.mapSize.width;
      levelShadow.mapSize.set(levelMapSize, levelMapSize);
      levelShadow.camera.left = -halfWidth;
      levelShadow.camera.right = halfWidth;
      levelShadow.camera.top = halfWidth;
      levelShadow.camera.bottom = -halfWidth;
      levelShadow.camera.near = this.shadowCameraNear;
      levelShadow.camera.far = Math.max(
        this.shadowCameraNear + 1,
        Math.min(this.shadowCameraFar, this.lightMargin + halfWidth * 2)
      );
      levelShadow.camera.updateProjectionMatrix();
      levelShadow.autoUpdate = false;
      levelShadow.needsUpdate = false;
      levelLight.shadow = levelShadow;
      this.lights.push(levelLight);
      this._shadowNodes.push(new BoundedShadowNode(levelLight, levelShadow));
      this._levelData.push(new THREE2.Vector4(1e9, 1e9, 1e-6, 0));
      this._levelStates.push({
        halfWidth,
        centerX: Number.NaN,
        centerY: Number.NaN,
        centerZ: Number.NaN,
        valid: false,
        forceDirty: false,
        // Stagger periodic refreshes so levels never expire on the same frame.
        age: Math.floor(-(i * this.maxCacheAge) / Math.max(this.levels, 1))
      });
    }
  }
};
export {
  CachedClipmapShadowNode
};
