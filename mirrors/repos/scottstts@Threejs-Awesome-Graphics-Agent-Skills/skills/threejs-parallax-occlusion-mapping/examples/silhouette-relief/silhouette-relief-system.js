import * as THREE from "three/webgpu";
import {
  bitangentWorld, cameraProjectionMatrix, cameraViewMatrix, color, float, mix,
  normalLocal, normalMap, normalWorld, positionLocal, positionWorld,
  tangentWorld, texture, textureLevel, uniform, uv, vec2, vec3, vec4,
} from "three/tsl";
import { parallaxOcclusionUV } from "./ParallaxOcclusion.js";
import {
  COLUMN_MAP_SIZE,
  FLOOR_MAP_SIZE,
  WALL_HEIGHT,
  WALL_MAP_SIZE,
  WALL_WIDTH,
  createColumnMap,
  createFloorMap,
  createWallMap,
} from "./bulkhead-height-maps.js";

const COLUMN_RADIUS = 0.46;
const COLUMN_HEIGHT = 3.4;
const COLUMN_U_TILES = 3;
const QUALITY_LAYERS = { low: [8, 32], medium: [16, 96], high: [32, 160] };

function buildRelief(heightMap, options, quality) {
  const { uvNode, texel, scale } = options;
  const [minLayers, maxLayers] = QUALITY_LAYERS[quality];
  const primary = parallaxOcclusionUV(heightMap, { minLayers, maxLayers, ...options });
  const normals = parallaxOcclusionUV(heightMap, { minLayers, maxLayers, ...options });
  const strength = scale.div(4.0 * texel);
  let tapAt = (coord) => normals.sample(heightMap, coord).r;
  if (primary.coverage !== null) {
    const bounds = options.sampleBounds;
    tapAt = (coord) => {
      if (bounds) {
        coord = vec2(
          coord.x.clamp(bounds[0][0], bounds[0][1]),
          coord.y.clamp(bounds[1][0], bounds[1][1]),
        );
      }
      return textureLevel(heightMap, coord, 0).r;
    };
  }
  const left = tapAt(normals.uv.sub(vec2(texel * 2.0, 0.0)));
  const right = tapAt(normals.uv.add(vec2(texel * 2.0, 0.0)));
  const bottom = tapAt(normals.uv.sub(vec2(0.0, texel * 2.0)));
  const top = tapAt(normals.uv.add(vec2(0.0, texel * 2.0)));
  const packedNormal = vec3(
    left.sub(right).mul(strength),
    bottom.sub(top).mul(strength),
    1.0,
  ).normalize().mul(0.5).add(0.5);
  return { ...primary, normalNode: normalMap(packedNormal), uvNode: uvNode || uv() };
}

function makePlatingMaterial({
  map,
  mapSize,
  scale,
  worldPerTile,
  reliefWorld,
  reliefOptions,
  quality,
  keyLightDirection,
}) {
  const material = new THREE.MeshStandardNodeMaterial();
  const relief = buildRelief(map, {
    scale,
    texel: 1.0 / mapSize,
    ...reliefOptions,
  }, quality);
  const panel = relief.sample(map);
  const height = panel.r;
  const glow = panel.g;
  const tone = panel.b;
  const plating = mix(
    color(0x33383f),
    color(0x848b94),
    height.mul(tone.mul(0.5).add(0.5)),
  );
  const paint = tone.smoothstep(0.80, 0.83)
    .mul(tone.smoothstep(0.92, 0.95).oneMinus());
  let surface = mix(
    plating,
    color(0xc7a13f).mul(height.mul(0.5).add(0.5)),
    paint,
  );
  if (relief.shadow !== null) {
    const lit = relief.shadow(
      cameraViewMatrix.mul(vec4(keyLightDirection, 0.0)).xyz,
      { steps: 20, strength: 12 },
    );
    surface = surface.mul(lit.mul(0.85).add(0.15));
  }
  material.colorNode = surface;
  material.emissiveNode = mix(
    color(0x36d8f0),
    color(0xff2fae),
    tone.smoothstep(0.45, 0.55),
  ).mul(glow.pow(2.0)).mul(3.2);
  material.opacityNode = relief.coverage;
  material.alphaTestNode = relief.coverage !== null ? float(0.5) : null;
  material.alphaToCoverage = relief.coverage !== null;
  if (relief.coverage !== null) {
    material.maskShadowNode = relief.coverage.greaterThanEqual(0.5);
  }
  const reliefOffset = relief.uv.sub(relief.uvNode);
  const reliefDrop = float(1.0).sub(height).mul(reliefWorld);
  const marched = positionWorld
    .add(tangentWorld.normalize().mul(reliefOffset.x.mul(worldPerTile[0])))
    .add(bitangentWorld.normalize().mul(reliefOffset.y.mul(worldPerTile[1])))
    .sub(normalWorld.normalize().mul(reliefDrop));
  const marchedClip = cameraProjectionMatrix
    .mul(cameraViewMatrix)
    .mul(vec4(marched, 1.0));
  material.depthNode = marchedClip.z.div(marchedClip.w);
  material.receivedShadowPositionNode = marched;
  material.normalNode = relief.normalNode;
  material.roughnessNode = mix(float(0.66), float(0.32), tone.min(0.78));
  material.metalnessNode = float(0.22);
  return material;
}

export function createSilhouetteReliefSystem({ quality = "medium", scale = 0.15 } = {}) {
  const wallMap = createWallMap();
  const columnMap = createColumnMap();
  const floorMap = createFloorMap();
  const depthScale = uniform(scale);
  const keyLightDirection = uniform(new THREE.Vector3(1, 1, 1).normalize());
  const object = new THREE.Group();
  const resources = [];

  const wallGeometry = new THREE.PlaneGeometry(WALL_WIDTH, WALL_HEIGHT);
  wallGeometry.computeTangents();
  const wallBackGeometry = wallGeometry.clone();
  wallBackGeometry.rotateY(Math.PI);
  const wallMaterial = makePlatingMaterial({
    map: wallMap,
    mapSize: WALL_MAP_SIZE,
    scale: depthScale.mul(1.2 / WALL_HEIGHT),
    worldPerTile: [WALL_WIDTH, WALL_HEIGHT],
    reliefWorld: depthScale.mul(1.2),
    reliefOptions: { silhouette: true },
    quality,
    keyLightDirection,
  });
  const wall = new THREE.Group();
  const wallFront = new THREE.Mesh(wallGeometry, wallMaterial);
  wallFront.position.z = 0.02;
  wallFront.castShadow = wallFront.receiveShadow = true;
  const wallBack = new THREE.Mesh(wallBackGeometry, wallMaterial);
  wallBack.position.z = -0.02;
  wallBack.castShadow = wallBack.receiveShadow = true;
  wall.add(wallFront, wallBack);
  wall.position.set(0, WALL_HEIGHT / 2 - 0.06, 0);
  object.add(wall);
  resources.push(wallGeometry, wallBackGeometry, wallMaterial);

  const coreMaterial = new THREE.MeshStandardNodeMaterial({
    color: 0x272c34,
    roughness: 0.6,
    metalness: 0.25,
  });
  const capMaterial = new THREE.MeshStandardNodeMaterial({
    color: 0x333944,
    roughness: 0.5,
    metalness: 0.3,
  });
  resources.push(coreMaterial, capMaterial);

  const makeShellCylinder = (radius, length, aroundTiles, reliefFactor) => {
    const group = new THREE.Group();
    const shellGeometry = new THREE.CylinderGeometry(radius, radius, length, 48, 1, true);
    shellGeometry.computeTangents();
    const tileAround = 2 * Math.PI * radius / aroundTiles;
    const ringTiles = Math.max(2, Math.round(length / tileAround));
    const uvNode = uv().mul(vec2(aroundTiles, ringTiles));
    const reliefWorld = depthScale.mul(reliefFactor * tileAround);
    const shellMaterial = makePlatingMaterial({
      map: columnMap,
      mapSize: COLUMN_MAP_SIZE,
      scale: depthScale.mul(reliefFactor),
      worldPerTile: [tileAround, length / ringTiles],
      reliefWorld,
      reliefOptions: {
        silhouette: true,
        uvNode,
        silhouetteBounds: [-1e6, 1e6],
        curvedSilhouette: true,
        curvature: [2 * Math.PI / aroundTiles, 0],
      },
      quality,
      keyLightDirection,
    });
    shellMaterial.positionNode = positionLocal.add(normalLocal.mul(reliefWorld));
    const shell = new THREE.Mesh(shellGeometry, shellMaterial);
    shell.castShadow = shell.receiveShadow = true;
    group.add(shell);

    const coreGeometry = new THREE.CylinderGeometry(radius - 0.005, radius - 0.005, length, 48);
    const core = new THREE.Mesh(coreGeometry, coreMaterial);
    core.castShadow = core.receiveShadow = true;
    group.add(core);

    const capRadius = radius + scale * reliefFactor * tileAround * 0.95;
    const capGeometry = new THREE.CylinderGeometry(capRadius, capRadius, 0.07, 48);
    for (const end of [-1, 1]) {
      const cap = new THREE.Mesh(capGeometry, capMaterial);
      cap.position.y = end * (length / 2 + 0.02);
      cap.castShadow = cap.receiveShadow = true;
      group.add(cap);
    }
    resources.push(shellGeometry, shellMaterial, coreGeometry, capGeometry);
    return group;
  };

  for (const side of [-1, 1]) {
    const column = makeShellCylinder(COLUMN_RADIUS, COLUMN_HEIGHT, COLUMN_U_TILES, 1.0);
    column.position.set(side * 2.55, COLUMN_HEIGHT / 2, 1.05);
    object.add(column);
  }
  for (const [radius, y, z] of [[0.15, 3.62, 0.32], [0.085, 3.92, 0.26]]) {
    const pipe = makeShellCylinder(radius, 10.4, 1, 0.7);
    pipe.rotation.z = Math.PI / 2;
    pipe.position.set(0, y, z);
    object.add(pipe);
  }

  const floorGeometry = new THREE.PlaneGeometry(16, 16);
  floorGeometry.rotateX(-Math.PI / 2);
  floorGeometry.computeTangents();
  const floorUv = uv().mul(5);
  const floorMaterial = makePlatingMaterial({
    map: floorMap,
    mapSize: FLOOR_MAP_SIZE,
    scale: depthScale.mul(0.4),
    worldPerTile: [3.2, 3.2],
    reliefWorld: depthScale.mul(0.4 * 3.2),
    reliefOptions: { silhouette: false, uvNode: floorUv },
    quality,
    keyLightDirection,
  });
  const floor = new THREE.Mesh(floorGeometry, floorMaterial);
  floor.receiveShadow = true;
  object.add(floor);
  resources.push(floorGeometry, floorMaterial);

  return {
    object,
    depthScale,
    keyLightDirection,
    setScale(value) { depthScale.value = value; },
    setLightDirection(value) { keyLightDirection.value.copy(value).normalize(); },
    dispose() {
      wallMap.dispose();
      columnMap.dispose();
      floorMap.dispose();
      for (const resource of resources) resource.dispose();
    },
  };
}
