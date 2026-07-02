// .example-captures/audit-build/procedural-tower-building-entry.ts
import * as THREE2 from "three/webgpu";

function createRandom(seed) {
  let state = seed >>> 0;
  const next = () => {
    state += 1831565813;
    let value = state;
    value = Math.imul(value ^ value >>> 15, value | 1);
    value ^= value + Math.imul(value ^ value >>> 7, value | 61);
    return ((value ^ value >>> 14) >>> 0) / 4294967296;
  };
  return {
    next,
    range: (min, max) => min + (max - min) * next(),
    int: (min, max) => Math.floor(min + (max - min + 1) * next()),
    chance: (odds) => next() < odds
  };
}

function exposedEdgesFor(rect, allRects) {
  return ["front", "back", "left", "right"].flatMap((side) => exposedSegments(rect, allRects, side).map((segment, index) => toEdge(rect, side, segment, index)));
}
function exposedSegments(rect, allRects, side) {
  const base = side === "front" || side === "back" ? { a: rect.x - rect.width / 2, b: rect.x + rect.width / 2 } : { a: rect.z - rect.depth / 2, b: rect.z + rect.depth / 2 };
  const blockers = allRects.filter((candidate) => candidate !== rect).flatMap((candidate) => blockerSegment(rect, candidate, side));
  return subtractSegments([base], blockers);
}
function blockerSegment(rect, other, side) {
  const epsilon = 1e-3;
  if (side === "front") {
    const touches2 = Math.abs(rect.z + rect.depth / 2 - (other.z - other.depth / 2)) < epsilon;
    return touches2 ? overlap(rect.x - rect.width / 2, rect.x + rect.width / 2, other.x - other.width / 2, other.x + other.width / 2) : [];
  }
  if (side === "back") {
    const touches2 = Math.abs(rect.z - rect.depth / 2 - (other.z + other.depth / 2)) < epsilon;
    return touches2 ? overlap(rect.x - rect.width / 2, rect.x + rect.width / 2, other.x - other.width / 2, other.x + other.width / 2) : [];
  }
  if (side === "right") {
    const touches2 = Math.abs(rect.x + rect.width / 2 - (other.x - other.width / 2)) < epsilon;
    return touches2 ? overlap(rect.z - rect.depth / 2, rect.z + rect.depth / 2, other.z - other.depth / 2, other.z + other.depth / 2) : [];
  }
  const touches = Math.abs(rect.x - rect.width / 2 - (other.x + other.width / 2)) < epsilon;
  return touches ? overlap(rect.z - rect.depth / 2, rect.z + rect.depth / 2, other.z - other.depth / 2, other.z + other.depth / 2) : [];
}
function overlap(a0, a1, b0, b1) {
  const a = Math.max(a0, b0);
  const b = Math.min(a1, b1);
  return b - a > 0.01 ? [{ a, b }] : [];
}
function subtractSegments(source, blockers) {
  let result = source;
  for (const blocker of blockers) {
    result = result.flatMap((segment) => subtractSegment(segment, blocker));
  }
  return result.filter((segment) => segment.b - segment.a > 0.25);
}
function subtractSegment(segment, blocker) {
  if (blocker.b <= segment.a || blocker.a >= segment.b) return [segment];
  const result = [];
  if (blocker.a > segment.a) result.push({ a: segment.a, b: blocker.a });
  if (blocker.b < segment.b) result.push({ a: blocker.b, b: segment.b });
  return result;
}
function toEdge(rect, side, segment, index) {
  const length = segment.b - segment.a;
  const axisCenter = (segment.a + segment.b) / 2;
  const localCenter = side === "front" || side === "back" ? axisCenter - rect.x : axisCenter - rect.z;
  return {
    id: `${rect.suffix}-${side}-${index}`,
    side,
    center: localCenter,
    length,
    x: rect.x,
    z: rect.z,
    isOuterCornerStart: true,
    isOuterCornerEnd: true,
    isInnerCornerStart: length < (side === "front" || side === "back" ? rect.width : rect.depth) - 0.01,
    isInnerCornerEnd: length < (side === "front" || side === "back" ? rect.width : rect.depth) - 0.01
  };
}

var BAY_WIDTH = 3.2;
var FLOOR_HEIGHT = 3.35;
var PODIUM_FLOOR_HEIGHT = 4.45;
function createMassTiers(settings) {
  const random = createRandom(settings.seed);
  const podiumHeight = settings.podiumFloors * PODIUM_FLOOR_HEIGHT;
  const crownFloors = settings.crown ? Math.max(1, settings.setbackFloors) : 0;
  const shaftFloors = Math.max(1, settings.floors - settings.podiumFloors - crownFloors);
  const fullWidth = settings.widthBays * BAY_WIDTH;
  const fullDepth = settings.depthBays * BAY_WIDTH;
  const towerScale = clamp(settings.towerScale + random.range(-0.05, 0.04), 0.62, 0.96);
  const setbackInset = BAY_WIDTH * (1 - towerScale) * random.range(0.86, 1.08);
  if (settings.massingPattern === "twin-towers") {
    return createTwinTowerTiers(settings, random, {
      podiumHeight,
      crownFloors,
      shaftFloors,
      fullWidth,
      fullDepth,
      setbackInset
    });
  }
  const tiers = createFootprintTiers({
    name: "podium",
    role: "podium",
    style: podiumFootprintStyle(settings),
    width: fullWidth,
    depth: fullDepth,
    y0: 0,
    height: podiumHeight,
    floors: settings.podiumFloors,
    inset: 0,
    settings
  });
  const shaftSlices = splitShaftFloors(settings.variant, shaftFloors, random);
  let y = podiumHeight;
  for (let index = 0; index < shaftSlices.length; index++) {
    const floors = shaftSlices[index];
    const inset = shaftInset(settings.variant, setbackInset, index, random);
    const shaftStyle = tierFootprintStyle(settings, "shaft", index);
    const adjusted = directionalInset(settings, clampedSpan(fullWidth, inset), clampedSpan(fullDepth, inset), index);
    tiers.push(...createFootprintTiers({
      name: `shaft-${index + 1}`,
      role: "shaft",
      style: shaftStyle,
      width: adjusted.width,
      depth: adjusted.depth,
      baseX: adjusted.x,
      baseZ: adjusted.z,
      y0: y,
      height: floors * FLOOR_HEIGHT,
      floors,
      inset,
      settings
    }));
    y += floors * FLOOR_HEIGHT;
  }
  if (settings.crown) {
    const crownInset = (tiers[tiers.length - 1]?.inset ?? setbackInset) + BAY_WIDTH * random.range(0.42, 0.68);
    const adjusted = directionalInset(settings, clampedSpan(fullWidth, crownInset), clampedSpan(fullDepth, crownInset), shaftSlices.length);
    tiers.push(...createFootprintTiers({
      name: "crown",
      role: "crown",
      style: tierFootprintStyle(settings, "crown", shaftSlices.length),
      width: adjusted.width,
      depth: adjusted.depth,
      baseX: adjusted.x,
      baseZ: adjusted.z,
      y0: y,
      height: crownFloors * FLOOR_HEIGHT,
      floors: crownFloors,
      inset: crownInset,
      settings
    }));
  }
  return tiers;
}
function createFootprintTiers(input) {
  const pieces = footprintPieces(input.style, input.width, input.depth, input.settings);
  const baseX = input.baseX ?? 0;
  const baseZ = input.baseZ ?? 0;
  return pieces.map((piece) => ({
    name: piece.suffix === "main" ? input.name : `${input.name}-${piece.suffix}`,
    role: input.role,
    width: piece.width,
    depth: piece.depth,
    x: baseX + piece.x,
    z: baseZ + piece.z,
    y0: input.y0,
    height: input.height,
    floors: input.floors,
    inset: input.inset,
    facadeEdges: exposedEdgesFor(piece, pieces).map((edge) => ({
      ...edge,
      x: baseX + edge.x,
      z: baseZ + edge.z
    }))
  }));
}
function footprintPieces(style, width, depth, settings) {
  if (style === "free-court") return freeCourtPieces(width, depth, settings);
  if (style === "l-shape") {
    const frontDepth = depth * 0.58;
    const rearDepth = depth - frontDepth;
    const wingWidth = width * 0.44;
    return [
      {
        suffix: "front-bar",
        width,
        depth: frontDepth,
        x: 0,
        z: depth / 2 - frontDepth / 2
      },
      {
        suffix: "rear-wing",
        width: wingWidth,
        depth: rearDepth,
        x: -width / 2 + wingWidth / 2,
        z: -depth / 2 + rearDepth / 2
      }
    ];
  }
  if (style === "t-shape") {
    const crossDepth = depth * 0.36;
    const stemDepth = depth - crossDepth;
    const stemWidth = width * 0.46;
    return [
      {
        suffix: "cross-bar",
        width,
        depth: crossDepth,
        x: 0,
        z: depth / 2 - crossDepth / 2
      },
      {
        suffix: "stem",
        width: stemWidth,
        depth: stemDepth,
        x: 0,
        z: -depth / 2 + stemDepth / 2
      }
    ];
  }
  if (style === "u-shape") {
    const frontDepth = depth * 0.34;
    const wingDepth = depth - frontDepth;
    const wingWidth = width * 0.26;
    return [
      {
        suffix: "front-bar",
        width,
        depth: frontDepth,
        x: 0,
        z: depth / 2 - frontDepth / 2
      },
      {
        suffix: "left-wing",
        width: wingWidth,
        depth: wingDepth,
        x: -width / 2 + wingWidth / 2,
        z: -depth / 2 + wingDepth / 2
      },
      {
        suffix: "right-wing",
        width: wingWidth,
        depth: wingDepth,
        x: width / 2 - wingWidth / 2,
        z: -depth / 2 + wingDepth / 2
      }
    ];
  }
  if (style === "courtyard-block") {
    const bar = Math.max(BAY_WIDTH * 2, Math.min(width, depth) * 0.24);
    return [
      { suffix: "front-bar", width, depth: bar, x: 0, z: depth / 2 - bar / 2 },
      { suffix: "back-bar", width, depth: bar, x: 0, z: -depth / 2 + bar / 2 },
      { suffix: "left-bar", width: bar, depth: depth - bar * 2, x: -width / 2 + bar / 2, z: 0 },
      { suffix: "right-bar", width: bar, depth: depth - bar * 2, x: width / 2 - bar / 2, z: 0 }
    ];
  }
  const blockScale = style === "high-rise-block" ? 0.86 : 1;
  return [{
    suffix: "main",
    width: width * blockScale,
    depth: depth * blockScale,
    x: 0,
    z: 0
  }];
}
function createTwinTowerTiers(settings, random, input) {
  const tiers = createFootprintTiers({
    name: "podium",
    role: "podium",
    style: "rectangle",
    width: input.fullWidth,
    depth: input.fullDepth,
    y0: 0,
    height: input.podiumHeight,
    floors: settings.podiumFloors,
    inset: 0,
    settings
  });
  const gap = Math.max(BAY_WIDTH * 2.2, input.fullWidth * 0.18);
  const towerWidth = Math.max(BAY_WIDTH * 4, (input.fullWidth - gap) * 0.46);
  const towerDepth = input.fullDepth * 0.82;
  const towerOffset = gap / 2 + towerWidth / 2;
  const shaftSlices = splitShaftFloors(settings.variant, input.shaftFloors, random);
  let y = input.podiumHeight;
  for (let index = 0; index < shaftSlices.length; index++) {
    const floors = shaftSlices[index];
    const inset = shaftInset(settings.variant, input.setbackInset * 0.72, index, random);
    const towerSpan = {
      width: clampedSpan(towerWidth, inset * 0.55),
      depth: clampedSpan(towerDepth, inset * 0.55)
    };
    tiers.push(...createFootprintTiers({
      name: `shaft-${index + 1}-west-tower`,
      role: "shaft",
      style: tierFootprintStyle(settings, "shaft", index),
      width: towerSpan.width,
      depth: towerSpan.depth,
      baseX: -towerOffset + inset * 0.18,
      y0: y,
      height: floors * FLOOR_HEIGHT,
      floors,
      inset,
      settings
    }));
    tiers.push(...createFootprintTiers({
      name: `shaft-${index + 1}-east-tower`,
      role: "shaft",
      style: settings.secondaryFootprintStyle,
      width: towerSpan.width,
      depth: towerSpan.depth,
      baseX: towerOffset - inset * 0.18,
      y0: y,
      height: floors * FLOOR_HEIGHT,
      floors,
      inset,
      settings
    }));
    y += floors * FLOOR_HEIGHT;
  }
  if (settings.skybridgeEnabled) {
    const bridgeY = input.podiumHeight + clamp(settings.skybridgeFloor, 1, input.shaftFloors) * FLOOR_HEIGHT;
    tiers.push(...createFootprintTiers({
      name: "skybridge",
      role: "bridge",
      style: "rectangle",
      width: gap + towerWidth * 0.42,
      depth: Math.max(BAY_WIDTH * 1.2, input.fullDepth * 0.18),
      y0: bridgeY,
      height: FLOOR_HEIGHT * 1.15,
      floors: 1,
      inset: 0,
      settings
    }));
  }
  if (settings.crown) {
    const crownInset = input.setbackInset + BAY_WIDTH * random.range(0.42, 0.68);
    const crownSpan = {
      width: clampedSpan(towerWidth, crownInset * 0.55),
      depth: clampedSpan(towerDepth, crownInset * 0.55)
    };
    for (const [name, baseX, style] of [
      ["crown-west-tower", -towerOffset + crownInset * 0.18, settings.footprintStyle],
      ["crown-east-tower", towerOffset - crownInset * 0.18, settings.secondaryFootprintStyle]
    ]) {
      tiers.push(...createFootprintTiers({
        name,
        role: "crown",
        style,
        width: crownSpan.width,
        depth: crownSpan.depth,
        baseX,
        y0: y,
        height: input.crownFloors * FLOOR_HEIGHT,
        floors: input.crownFloors,
        inset: crownInset,
        settings
      }));
    }
  }
  return tiers;
}
function freeCourtPieces(width, depth, settings) {
  const minBar = BAY_WIDTH * 1.8;
  const innerWidth = clamp(width * settings.innerCourtWidth, BAY_WIDTH * 2, width - minBar * 2);
  const innerDepth = clamp(depth * settings.innerCourtDepth, BAY_WIDTH * 2, depth - minBar * 2);
  const cxLimit = Math.max(0, (width - innerWidth) / 2 - minBar);
  const czLimit = Math.max(0, (depth - innerDepth) / 2 - minBar);
  const cx = clamp(settings.innerCourtOffsetX * width * 0.5, -cxLimit, cxLimit);
  const cz = clamp(settings.innerCourtOffsetZ * depth * 0.5, -czLimit, czLimit);
  const outerX0 = -width / 2;
  const outerX1 = width / 2;
  const outerZ0 = -depth / 2;
  const outerZ1 = depth / 2;
  const courtX0 = cx - innerWidth / 2;
  const courtX1 = cx + innerWidth / 2;
  const courtZ0 = cz - innerDepth / 2;
  const courtZ1 = cz + innerDepth / 2;
  return [
    { suffix: "front-bar", width, depth: outerZ1 - courtZ1, x: 0, z: (outerZ1 + courtZ1) / 2 },
    { suffix: "back-bar", width, depth: courtZ0 - outerZ0, x: 0, z: (outerZ0 + courtZ0) / 2 },
    { suffix: "left-bar", width: courtX0 - outerX0, depth: innerDepth, x: (outerX0 + courtX0) / 2, z: cz },
    { suffix: "right-bar", width: outerX1 - courtX1, depth: innerDepth, x: (courtX1 + outerX1) / 2, z: cz }
  ].filter((piece) => piece.width > 0.25 && piece.depth > 0.25);
}
function splitShaftFloors(variant, floors, random) {
  if (floors <= 4) return [floors];
  if (variant === "classic-bank") return [floors];
  if (variant === "corner-hq") {
    const lower2 = Math.max(3, Math.ceil(floors * random.range(0.56, 0.72)));
    return [lower2, floors - lower2].filter(Boolean);
  }
  const lower = Math.max(3, Math.floor(floors * random.range(0.36, 0.5)));
  const middle = Math.max(3, Math.floor(floors * random.range(0.26, 0.38)));
  const upper = floors - lower - middle;
  return [lower, middle, Math.max(1, upper)].filter(Boolean);
}
function shaftInset(variant, baseInset, step, random) {
  if (variant === "classic-bank") return baseInset;
  const jitter = random.range(-0.08, 0.12);
  if (variant === "corner-hq") return baseInset * (0.65 + step * 0.95 + jitter);
  return baseInset * (0.75 + step * 1.15 + jitter);
}
function tierFootprintStyle(settings, role, index) {
  if (settings.massingPattern === "outer-ring") return "free-court";
  if (settings.footprintStyle === "high-rise-block") return "high-rise-block";
  if (settings.footprintHeightMode === "full-height") return settings.footprintStyle;
  if (settings.footprintHeightMode === "lower-tiers-only") return role === "shaft" && index === 0 ? settings.footprintStyle : "rectangle";
  return "rectangle";
}
function podiumFootprintStyle(settings) {
  if (settings.massingPattern === "outer-ring") return "free-court";
  return settings.footprintStyle;
}
function directionalInset(settings, width, depth, step) {
  const amount = Math.min(BAY_WIDTH * settings.hardInsetAmount * (step + 1) * 0.42, Math.min(width, depth) * 0.38);
  if (settings.hardInsetSide === "none" || amount <= 1e-3) return { width, depth, x: 0, z: 0 };
  if (settings.hardInsetSide === "front") return { width, depth: Math.max(BAY_WIDTH * 4, depth - amount), x: 0, z: -amount / 2 };
  if (settings.hardInsetSide === "back") return { width, depth: Math.max(BAY_WIDTH * 4, depth - amount), x: 0, z: amount / 2 };
  if (settings.hardInsetSide === "left") return { width: Math.max(BAY_WIDTH * 4, width - amount), depth, x: amount / 2, z: 0 };
  return { width: Math.max(BAY_WIDTH * 4, width - amount), depth, x: -amount / 2, z: 0 };
}
function clampedSpan(span, inset) {
  return Math.max(BAY_WIDTH * 4, span - inset * 2);
}
function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

var facadeSides = ["front", "back", "left", "right"];
function sideSpan(tier, side) {
  return side === "front" || side === "back" ? tier.width : tier.depth;
}
function exposedEdges(tier, side) {
  return tier.facadeEdges?.filter((edge) => edge.side === side) ?? [{
    id: `${tier.name}-${side}`,
    side,
    center: 0,
    length: sideSpan(tier, side),
    x: tier.x,
    z: tier.z,
    isOuterCornerStart: true,
    isOuterCornerEnd: true,
    isInnerCornerStart: false,
    isInnerCornerEnd: false
  }];
}
function edgeBayCount(edge, minimum = 3) {
  return Math.max(minimum, Math.round(edge.length / BAY_WIDTH));
}
function edgeBayCenter(edge, index, count) {
  const width = edge.length / count;
  return edge.center - edge.length / 2 + width * (index + 0.5);
}
function edgeSeamCenter(edge, index, count) {
  return edge.center - edge.length / 2 + edge.length / count * index;
}
function place(input) {
  return {
    id: input.id,
    side: input.side,
    tierName: input.tier.name,
    center: input.center,
    y: input.y,
    width: input.width,
    height: input.height,
    depth: input.depth,
    floorIndex: input.floorIndex,
    bayIndex: input.bayIndex,
    edgeId: input.edge?.id,
    xOffset: input.edge?.x,
    zOffset: input.edge?.z,
    normalOffset: input.normalOffset,
    moduleVariant: input.moduleVariant
  };
}
function roofPlace(input) {
  return {
    id: input.id,
    side: "roof",
    tierName: "roof",
    center: input.center,
    roofZ: input.roofZ,
    y: input.y,
    width: input.width,
    height: input.height,
    depth: input.depth,
    floorIndex: 0,
    bayIndex: input.bayIndex ?? 0
  };
}

function createCrownPlacements(settings, tier, side) {
  return exposedEdges(tier, side).flatMap((edge) => createCrownEdgePlacements(settings, tier, side, edge));
}
function createCrownEdgePlacements(settings, tier, side, edge) {
  const count = edgeBayCount(edge, 3);
  const bay = edge.length / count;
  const result = [];
  for (let index = 0; index < count; index++) {
    const id = crownModule(settings, side, index, count);
    result.push(place({
      id,
      side,
      tier,
      center: edgeBayCenter(edge, index, count),
      y: tier.y0,
      width: bay,
      height: tier.height,
      depth: id === "corner-parapet" ? 1.16 : 0.92,
      floorIndex: 0,
      bayIndex: index,
      edge
    }));
  }
  result.push(...crownTrim(tier, side, edge));
  result.push(...crownTopOrnaments(settings, tier, side, edge));
  return result;
}
function crownModule(settings, side, index, count) {
  const edge = index === 0 || index === count - 1;
  if (edge && settings.crownStyle !== "flat-parapet") return "corner-parapet";
  if (settings.crownStyle === "flat-parapet") return edge ? "corner-parapet" : "parapet-section";
  if (settings.crownStyle === "corner-parapets" && index % 2 === 0) return "parapet-section";
  if (side === "back" && index % 3 === 1) return "parapet-section";
  return "crown-window-bay";
}
function crownTrim(tier, side, edge) {
  const span = edge.length;
  return [
    place({
      id: "small-cornice",
      side,
      tier,
      center: edge.center,
      y: tier.y0 - 0.26,
      width: span,
      height: 0.36,
      depth: 0.62,
      floorIndex: -1,
      bayIndex: -1,
      edge
    }),
    place({
      id: "large-cornice",
      side,
      tier,
      center: edge.center,
      y: tier.y0 + tier.height - 0.74,
      width: span,
      height: 0.8,
      depth: 1.06,
      floorIndex: 0,
      bayIndex: -2,
      edge
    }),
    place({
      id: "corner-cornice",
      side,
      tier,
      center: edge.center - span / 2 + 0.72,
      y: tier.y0 + tier.height - 0.82,
      width: 1.44,
      height: 0.86,
      depth: 1.14,
      floorIndex: 0,
      bayIndex: -3,
      edge
    }),
    place({
      id: "corner-cornice",
      side,
      tier,
      center: edge.center + span / 2 - 0.72,
      y: tier.y0 + tier.height - 0.82,
      width: 1.44,
      height: 0.86,
      depth: 1.14,
      floorIndex: 0,
      bayIndex: -4,
      edge
    }),
    ...cornerTrimJoints(tier, side, edge, tier.y0 - 0.24, "belt-corner-joint", 0.62),
    ...cornerTrimJoints(tier, side, edge, tier.y0 + tier.height - 0.78, "cornice-corner-joint", 1)
  ];
}
function crownTopOrnaments(settings, tier, side, edge) {
  const span = edge.length;
  const count = Math.max(1, Math.round(span / 4 * settings.crownDecorationDensity));
  const panelWidth = span / count;
  const y = tier.y0 + tier.height - 0.02;
  const result = [];
  for (let index = 0; index < count; index++) {
    const id = crownDecorationPanel(settings, index);
    result.push(place({
      id,
      side,
      tier,
      center: edge.center - span / 2 + panelWidth * (index + 0.5),
      y,
      width: panelWidth,
      height: id === "crown-cartouche-panel" ? 1.25 : 1,
      depth: 0.84,
      floorIndex: 1,
      bayIndex: index,
      edge
    }));
  }
  if ((side === "front" || side === "back") && settings.crownStyle !== "flat-parapet") {
    result.push(place({
      id: "crown-pediment",
      side,
      tier,
      center: edge.center,
      y: y + 0.82,
      width: Math.min(5.4, span * 0.36),
      height: 1.45,
      depth: 1,
      floorIndex: 2,
      bayIndex: -5,
      edge
    }));
  }
  for (const edgeSign of [-1, 1]) {
    const id = crownFinial(settings);
    result.push(place({
      id,
      side,
      tier,
      center: edge.center + edgeSign * (span / 2 - 0.5),
      y: y + 0.86,
      width: 0.8,
      height: id === "crown-obelisk-finial" ? 2.2 : 1.6,
      depth: 0.8,
      floorIndex: 2,
      bayIndex: edgeSign < 0 ? -6 : -7,
      edge
    }));
  }
  result.push(...edgeFinials(settings, tier, side, edge, y + 0.78));
  return result;
}
function crownDecorationPanel(settings, index) {
  if (settings.crownDecorationStyle === "restrained") return "attic-crest-panel";
  if (settings.crownDecorationStyle === "skyline") return index % 2 === 0 ? "crown-cartouche-panel" : "attic-crest-panel";
  return index % 3 === 1 ? "crown-cartouche-panel" : "attic-crest-panel";
}
function crownFinial(settings) {
  if (settings.crownDecorationStyle === "restrained") return "corner-finial";
  if (settings.crownDecorationStyle === "skyline") return "crown-obelisk-finial";
  return "crown-urn-finial";
}
function edgeFinials(settings, tier, side, edge, y) {
  if (settings.crownFinialRhythm === "corners-only" || settings.crownFinialDensity <= 0.01) return [];
  const spacing = finialSpacing(settings);
  const usableSpan = Math.max(0, edge.length - 2.2);
  const count = Math.max(0, Math.floor(usableSpan / spacing * densityMultiplier(settings.crownFinialDensity)));
  if (count <= 0) return [];
  const step = usableSpan / (count + 1);
  const id = edgeFinialId(settings);
  const result = [];
  for (let index = 0; index < count; index++) {
    const center = edge.center - usableSpan / 2 + step * (index + 1);
    result.push(place({
      id,
      side,
      tier,
      center,
      y,
      width: id === "crown-obelisk-finial" ? 0.8 : 0.68,
      height: id === "crown-obelisk-finial" ? 2 : 1.16,
      depth: id === "crown-obelisk-finial" ? 0.8 : 0.68,
      floorIndex: 3,
      bayIndex: 100 + index,
      edge
    }));
  }
  return result;
}
function finialSpacing(settings) {
  if (settings.crownFinialRhythm === "edge-sparse") return 5.2;
  if (settings.crownFinialRhythm === "edge-dense") return 2.1;
  if (settings.crownFinialRhythm === "skyline-spikes") return 3.4;
  return 3.2;
}
function densityMultiplier(value) {
  return 0.35 + value * 1.35;
}
function edgeFinialId(settings) {
  if (settings.crownFinialRhythm === "skyline-spikes") return "crown-obelisk-finial";
  if (settings.crownDecorationStyle === "classical") return "crown-pillar-finial";
  if (settings.crownDecorationStyle === "skyline") return "crown-obelisk-finial";
  return "corner-finial";
}
function cornerTrimJoints(tier, side, edge, y, id, depth) {
  return [-1, 1].map((edgeSign) => place({
    id,
    side,
    tier,
    center: edge.center + edgeSign * (edge.length / 2 - 0.32),
    y,
    width: 0.86,
    height: id === "cornice-corner-joint" ? 0.92 : 0.46,
    depth,
    floorIndex: -9,
    bayIndex: edgeSign < 0 ? -90 : -91,
    edge
  }));
}

var PLINTH_HEIGHT = 0.74;
function createPodiumPlacements(settings, tier, side) {
  return exposedEdges(tier, side).flatMap((edge) => createPodiumEdgePlacements(settings, tier, side, edge));
}
function createPodiumEdgePlacements(settings, tier, side, edge) {
  const count = edgeBayCount(edge, side === "front" || side === "back" ? 5 : 3);
  const bay = edge.length / count;
  const result = [];
  for (let index = 0; index < count; index++) {
    const center = edgeBayCenter(edge, index, count);
    result.push(place({
      id: settings.buildingArchetype === "federal-fortress" ? "rusticated-base-block" : "granite-plinth",
      side,
      tier,
      center,
      y: 0,
      width: bay,
      height: settings.buildingArchetype === "federal-fortress" ? 2.1 : PLINTH_HEIGHT,
      depth: 0.72,
      floorIndex: -1,
      bayIndex: index,
      edge
    }));
    result.push(...podiumBayStack(settings, tier, side, edge, center, bay, index, count));
  }
  result.push(...podiumHorizontalTrim(tier, side, edge));
  result.push(...podiumColumns(settings, tier, side, edge, count));
  result.push(...frontageDetails(settings, tier, side, edge, count));
  return result;
}
function podiumBayStack(settings, tier, side, edge, center, bay, index, count) {
  const result = [];
  for (let floor = 0; floor < tier.floors; floor++) {
    const y = floor === 0 ? PLINTH_HEIGHT : floor * PODIUM_FLOOR_HEIGHT;
    const height = floor === 0 ? PODIUM_FLOOR_HEIGHT - PLINTH_HEIGHT + 0.08 : PODIUM_FLOOR_HEIGHT - 0.18;
    const id = floor === 0 ? groundModule(settings, side, index, count) : upperPodiumModule(side, index, count, floor);
    result.push(place({
      id,
      side,
      tier,
      center,
      y,
      width: bay,
      height,
      depth: podiumDepth(id),
      floorIndex: floor,
      bayIndex: index,
      edge
    }));
    if (floor > 0 && settings.ornamentDensity > 0.45 && index % 3 === 1) {
      result.push(place({
        id: "spandrel-panel",
        side,
        tier,
        center,
        y: y + 0.28,
        width: bay * 0.82,
        height: 0.82,
        depth: 0.54,
        floorIndex: floor,
        bayIndex: index,
        edge
      }));
    }
  }
  return result;
}
function groundModule(settings, side, index, count) {
  const center = Math.floor(count / 2);
  const edge = index === 0 || index === count - 1;
  if (side === "front") {
    if (settings.buildingArchetype === "federal-fortress") return index % 2 === 0 ? "bank-grille" : "barred-window";
    if (settings.buildingArchetype === "temple-bank-podium" && Math.abs(index - center) <= 2) return "storefront-curtain-wall";
    if ((settings.cornerEntrance || settings.entranceType === "corner-bank" || settings.podiumStyle === "corner-entrance") && edge) {
      return "corner-entrance";
    }
    if (index === center && settings.entranceType === "center-revolving") return "revolving-door-bay";
    if (Math.abs(index - center) === 1 || settings.entranceType === "paired-lobby") return "lobby-door";
    if (settings.colonnade && settings.podiumStyle === "colonnade" && index % 2 === 0) return "paired-column";
    return "tall-lobby-window";
  }
  if (side === "back") return index % 3 === 0 ? "loading-dock-bay" : "security-door";
  if (settings.podiumStyle === "service-bank" && index % 2 === 0) return "loading-dock-bay";
  if (edge) return settings.buildingArchetype === "federal-fortress" ? "bank-grille" : "service-door";
  return "tall-lobby-window";
}
function upperPodiumModule(side, index, count, floor) {
  if (index === 0 || index === count - 1) return "corner-bay";
  if (side === "back" && (index + floor) % 4 === 0) return "blank-bay";
  if (floor % 2 === 0 && index % 3 === 1) return "deep-window-well";
  return side === "front" ? "tall-lobby-window" : "window-4m";
}
function podiumDepth(id) {
  if (id === "paired-column") return 1.8;
  if (id === "corner-entrance") return 1.55;
  if (id === "revolving-door-bay") return 1.5;
  if (id === "loading-dock-bay") return 1.2;
  return 1.1;
}
function podiumHorizontalTrim(tier, side, edge) {
  const span = edge.length;
  const top = tier.y0 + tier.height;
  const result = [
    place({
      id: "belt-course-large",
      side,
      tier,
      center: edge.center,
      y: PODIUM_FLOOR_HEIGHT - 0.26,
      width: span,
      height: 0.52,
      depth: 0.72,
      floorIndex: 1,
      bayIndex: -1,
      edge
    }),
    place({
      id: "large-cornice",
      side,
      tier,
      center: edge.center,
      y: top - 0.78,
      width: span,
      height: 0.78,
      depth: 1,
      floorIndex: tier.floors,
      bayIndex: -1,
      edge
    })
  ];
  if (tier.floors > 2) {
    result.push(place({
      id: "small-cornice",
      side,
      tier,
      center: edge.center,
      y: PODIUM_FLOOR_HEIGHT * 2 - 0.18,
      width: span,
      height: 0.36,
      depth: 0.62,
      floorIndex: 2,
      bayIndex: -1,
      edge
    }));
  }
  for (const edgeSign of [-1, 1]) {
    result.push(place({
      id: "corner-cornice",
      side,
      tier,
      center: edge.center + edgeSign * (span / 2 - 0.8),
      y: top - 0.92,
      width: 1.6,
      height: 0.92,
      depth: 1.1,
      floorIndex: tier.floors,
      bayIndex: edgeSign < 0 ? 0 : 999,
      edge
    }));
  }
  result.push(...cornerTrimJoints2(tier, side, edge, PODIUM_FLOOR_HEIGHT - 0.24, "belt-corner-joint", 0.72));
  result.push(...cornerTrimJoints2(tier, side, edge, top - 0.82, "cornice-corner-joint", 1.05));
  return result;
}
function cornerTrimJoints2(tier, side, edge, y, id, depth) {
  return [-1, 1].map((edgeSign) => place({
    id,
    side,
    tier,
    center: edge.center + edgeSign * (edge.length / 2 - 0.32),
    y,
    width: 0.86,
    height: id === "cornice-corner-joint" ? 0.9 : 0.46,
    depth,
    floorIndex: -9,
    bayIndex: edgeSign < 0 ? -90 : -91,
    edge
  }));
}
function podiumColumns(settings, tier, side, edge, count) {
  const result = [];
  const firstFloorHeight = PODIUM_FLOOR_HEIGHT - PLINTH_HEIGHT + 0.08;
  if (side === "front" && settings.colonnade && settings.podiumStyle === "colonnade") {
    const bedY = porticoBedY(tier);
    const columnHeight = bedY + 0.08;
    const projection = settings.porticoProjection;
    const bedWidth = Math.max(edge.length - 0.8, edge.length * 0.9);
    result.push(place({
      id: "large-cornice",
      side,
      tier,
      center: edge.center,
      y: bedY - 0.08,
      width: bedWidth,
      height: 1.05,
      depth: projection + 1.45,
      floorIndex: 0,
      bayIndex: -40,
      edge,
      normalOffset: projection * 0.5
    }));
    result.push(place({
      id: "dentil-corbel-course",
      side,
      tier,
      center: edge.center,
      y: bedY - 0.34,
      width: bedWidth,
      height: 0.52,
      depth: projection + 1.2,
      floorIndex: 0,
      bayIndex: -41,
      edge,
      normalOffset: projection * 0.5
    }));
    for (const seam of [0, count]) {
      result.push(place({
        id: "square-corner-pylon",
        side,
        tier,
        center: edgeSeamCenter(edge, seam, count),
        y: 0,
        width: 1.55,
        height: columnHeight,
        depth: 1.35,
        floorIndex: 0,
        bayIndex: seam,
        edge,
        normalOffset: projection
      }));
    }
    for (let index = 1; index < count; index++) {
      if (index % 2 === 0) continue;
      result.push(place({
        id: "colossal-column",
        side,
        tier,
        center: edgeSeamCenter(edge, index, count),
        y: 0,
        width: 1.7,
        height: columnHeight,
        depth: 1.7,
        floorIndex: 0,
        bayIndex: index,
        edge,
        normalOffset: projection
      }));
    }
    return result;
  }
  for (let index = 1; index < count; index++) {
    const center = edgeSeamCenter(edge, index, count);
    const useRound = side === "front" && settings.colonnade && settings.podiumStyle === "colonnade";
    const everyOtherFront = side === "front" && index % 2 === 1;
    const sidePier = side !== "front" && index % 3 === 0;
    if (!everyOtherFront && !sidePier) continue;
    const id = side !== "front" && settings.buildingArchetype === "temple-bank-podium" ? "round-column" : side === "front" && index % 2 === 1 ? "round-column" : useRound ? "round-column" : "square-column";
    result.push(place({
      id,
      side,
      tier,
      center,
      y: PLINTH_HEIGHT,
      width: useRound ? 1.15 : 0.92,
      height: firstFloorHeight,
      depth: useRound ? 1.35 : 0.86,
      floorIndex: 0,
      bayIndex: index,
      edge,
      normalOffset: side === "front" ? settings.porticoProjection * 0.55 : 0
    }));
  }
  return result;
}
function frontageDetails(settings, tier, side, edge, count) {
  if (side !== "front") return [];
  const y = Math.max(0.8, tier.height - 3.2);
  const result = [];
  const projection = settings.podiumStyle === "colonnade" ? settings.porticoProjection : 0;
  const ceremonialSpan = settings.podiumStyle === "colonnade" ? Math.max(edge.length - 0.8, edge.length * 0.9) : Math.min(edge.length * 0.82, 14);
  if (settings.buildingArchetype === "temple-bank-podium" || settings.buildingArchetype === "board-of-trade-tower") {
    result.push(place({ id: "triangular-pediment", side, tier, center: edge.center, y: tier.height - 0.2, width: ceremonialSpan, height: 3, depth: projection + 1.55, floorIndex: 10, bayIndex: -10, edge, normalOffset: projection * 0.5 }));
    result.push(place({ id: "company-frieze", side, tier, center: edge.center, y: tier.height - 1, width: ceremonialSpan * 0.96, height: 0.9, depth: projection + 0.9, floorIndex: 10, bayIndex: -11, edge, normalOffset: projection * 0.5 }));
    result.push(place({ id: "pediment-eagle", side, tier, center: edge.center, y: tier.height + 0.75, width: 2.4, height: 1.2, depth: 0.45, floorIndex: 10, bayIndex: -12, edge, normalOffset: projection + 0.12 }));
    for (const sideSign of [-1, 1]) {
      result.push(place({ id: "acroterion-scroll", side, tier, center: edge.center + sideSign * Math.min(edge.length * 0.36, 6), y: tier.height + 1.35, width: 0.9, height: 1, depth: 0.5, floorIndex: 10, bayIndex: -13 + sideSign, edge, normalOffset: projection + 0.18 }));
    }
    result.push(place({ id: "clock-medallion", side, tier, center: edge.center, y, width: 1.8, height: 1.8, depth: 0.5, floorIndex: 9, bayIndex: -20, edge, normalOffset: 0.12 }));
  }
  result.push(place({ id: "wall-plaque", side, tier, center: edgeBayCenter(edge, Math.max(0, count - 2), count), y: 1.65, width: 1.15, height: 1.4, depth: 0.28, floorIndex: 0, bayIndex: -21, edge }));
  result.push(place({ id: "address-plaque", side, tier, center: edgeBayCenter(edge, 1, count), y: 1.3, width: 0.85, height: 0.55, depth: 0.2, floorIndex: 0, bayIndex: -22, edge }));
  result.push(place({ id: "flag-mount", side, tier, center: edge.center - edge.length * 0.32, y: 3.1, width: 1.35, height: 1.6, depth: 0.7, floorIndex: 0, bayIndex: -23, edge }));
  result.push(place({ id: "wall-lamp", side, tier, center: edge.center + edge.length * 0.28, y: 2.25, width: 0.55, height: 1.4, depth: 0.65, floorIndex: 0, bayIndex: -24, edge }));
  if (settings.buildingArchetype === "federal-fortress") {
    result.push(place({ id: "wall-camera", side, tier, center: edge.center + edge.length * 0.36, y: 3.9, width: 0.55, height: 0.45, depth: 0.7, floorIndex: 0, bayIndex: -25, edge }));
  }
  result.push(place({ id: "sidewalk-entry", side, tier, center: edge.center, y: -0.02, width: Math.min(5.2, edge.length * 0.38), height: 0.45, depth: 1.4, floorIndex: -2, bayIndex: -26, edge, normalOffset: projection + 0.45 }));
  for (let index = 1; index < count; index += 3) {
    result.push(place({ id: "bollard", side, tier, center: edgeSeamCenter(edge, index, count), y: -0.02, width: 0.45, height: 1.1, depth: 0.45, floorIndex: -2, bayIndex: -30 - index, edge }));
  }
  return result;
}
function porticoBedY(tier) {
  return Math.min(tier.height - 3.2, PODIUM_FLOOR_HEIGHT * 2 - 0.08);
}

function createRoofPlacements(settings, tier) {
  const y = tier.y0 + tier.height + 0.12;
  if (settings.roofStyle === "pyramidal-metal" || settings.roofStyle === "statue-tower") {
    return [
      roofPlace({ id: "sloped-metal-roof", center: tier.x, roofZ: tier.z, y, width: tier.width * 0.92, height: Math.min(6.2, tier.depth * 0.32), depth: tier.depth * 0.92, bayIndex: 0 }),
      ...settings.roofStyle === "statue-tower" ? [
        roofPlace({ id: "roof-lantern", center: tier.x, roofZ: tier.z, y: y + Math.min(6.2, tier.depth * 0.32), width: 2.4, height: 1.8, depth: 2.4, bayIndex: 1 }),
        roofPlace({ id: "roof-statue-mast", center: tier.x, roofZ: tier.z, y: y + Math.min(8, tier.depth * 0.32 + 1.5), width: 1.7, height: 5.8, depth: 1.7, bayIndex: 2 })
      ] : [
        roofPlace({ id: "roof-crest", center: tier.x, roofZ: tier.z, y: y + Math.min(6.2, tier.depth * 0.32), width: 1.4, height: 2.4, depth: 1.4, bayIndex: 2 })
      ]
    ];
  }
  const result = [
    ...terraceRailings(tier, y, 0)
  ];
  if (settings.roofEquipmentDensity > 0.12) {
    result.push(roofPlace({
      id: "roof-mech-box",
      center: tier.x - tier.width * 0.22,
      roofZ: tier.z - tier.depth * 0.04,
      y,
      width: 3.6,
      height: 2,
      depth: 2.8,
      bayIndex: 2
    }));
  }
  if (settings.roofEquipmentDensity > 0.32) {
    result.push(roofPlace({
      id: "hvac-cluster",
      center: tier.x + tier.width * 0.2,
      roofZ: tier.z - tier.depth * 0.12,
      y,
      width: 4.3,
      height: 2.2,
      depth: 3,
      bayIndex: 3
    }));
  }
  if (settings.roofEquipmentDensity > 0.58) {
    result.push(roofPlace({
      id: "roof-mech-box",
      center: tier.x,
      roofZ: tier.z + tier.depth * 0.22,
      y,
      width: 2.6,
      height: 1.55,
      depth: 2.2,
      bayIndex: 4
    }));
  }
  if (settings.roofEquipmentDensity > 0.66) {
    result.push(roofPlace({
      id: "antenna",
      center: tier.x + tier.width * 0.36,
      roofZ: tier.z + tier.depth * 0.28,
      y,
      width: 0.8,
      height: 4.6,
      depth: 0.8,
      bayIndex: 5
    }));
  }
  return result;
}
function terraceRailings(tier, y, offset) {
  return [
    roofPlace({
      id: "roof-railing",
      center: tier.x - tier.width * 0.18,
      roofZ: tier.z - tier.depth * 0.44,
      y,
      width: tier.width * 0.58,
      height: 1.1,
      depth: 0.4,
      bayIndex: offset
    }),
    roofPlace({
      id: "roof-railing",
      center: tier.x + tier.width * 0.18,
      roofZ: tier.z + tier.depth * 0.44,
      y,
      width: tier.width * 0.58,
      height: 1.1,
      depth: 0.4,
      bayIndex: offset + 1
    })
  ];
}

function createShaftPlacements(settings, tier, side) {
  return exposedEdges(tier, side).flatMap((edge) => createShaftEdgePlacements(settings, tier, side, edge));
}
function createShaftEdgePlacements(settings, tier, side, edge) {
  const count = edgeBayCount(edge, 4);
  const bay = edge.length / count;
  const result = [];
  result.push(...verticalZones(settings, tier, side, edge, count));
  for (let floor = 0; floor < tier.floors; floor++) {
    for (let index = 0; index < count; index++) {
      if (isReservedVerticalZone(settings, side, index, count)) continue;
      const center = edgeBayCenter(edge, index, count);
      result.push(...shaftBay(settings, tier, side, edge, center, bay, index, count, floor));
    }
    result.push(...floorTrim(tier, side, edge, floor));
  }
  result.push(...verticalPilasters(settings, tier, side, edge, count));
  result.push(...tierTrim(tier, side, edge));
  return result;
}
function shaftBay(settings, tier, side, edge, center, bay, index, count, floor) {
  const id = shaftModule(settings, side, index, count, floor);
  const y = tier.y0 + floor * FLOOR_HEIGHT;
  const ornamental = id !== "corner-bay" && id !== "blank-bay" && settings.ornamentDensity > 0.52 && (floor + index) % 5 === 2;
  if (!ornamental) {
    return [place({
      id,
      side,
      tier,
      center,
      y,
      width: bay,
      height: FLOOR_HEIGHT,
      depth: id === "corner-bay" ? 1.08 : 0.84,
      floorIndex: floor,
      bayIndex: index,
      edge
    })];
  }
  const upperId = id === "double-window-bay" ? "double-window-bay" : "window-3m";
  return [
    place({
      id: (floor + index) % 2 === 0 ? "carved-spandrel-vine" : "spandrel-panel",
      side,
      tier,
      center,
      y: y + 0.18,
      width: bay * 0.84,
      height: 0.82,
      depth: 0.56,
      floorIndex: floor,
      bayIndex: index,
      edge
    }),
    place({
      id: upperId,
      side,
      tier,
      center,
      y: y + 0.92,
      width: bay,
      height: FLOOR_HEIGHT - 0.96,
      depth: 0.78,
      floorIndex: floor,
      bayIndex: index,
      edge
    })
  ];
}
function shaftModule(settings, side, index, count, floor) {
  const edge = index === 0 || index === count - 1;
  if (edge) return cornerPierId(settings);
  if (side === "back" && floor % 5 === 0 && index % 3 === 1) return "structural-blank-wall";
  if (side !== "front" && index === Math.floor(count / 2)) return "recessed-window-slot";
  if (settings.buildingArchetype === "terra-cotta-arcade") return floor % 4 === 0 ? "arcade-bay" : floor % 2 === 0 ? "arched-window-bay" : "brick-window-bay";
  if (settings.buildingArchetype === "federal-fortress") return floor % 4 === 0 ? "deep-window-well" : "window-3m";
  if (floor % 5 === 0 && index % 4 === 1) return "double-window-bay";
  if (settings.shaftRhythm === "paired") return index % 2 === 0 ? "double-window-bay" : "window-3m";
  if (settings.shaftRhythm === "chicago-grid") return index % 3 === 1 ? "window-4m" : "window-3m";
  return floor % 4 === 0 && index % 3 === 0 ? "double-window-bay" : "window-4m";
}
function floorTrim(tier, side, edge, floor) {
  const y = tier.y0 + floor * FLOOR_HEIGHT;
  const span = edge.length;
  return [
    place({
      id: "floor-band-strip",
      side,
      tier,
      center: edge.center,
      y: y - 0.16,
      width: span,
      height: 0.36,
      depth: 0.54,
      floorIndex: floor,
      bayIndex: -1,
      edge
    }),
    place({
      id: "window-sill-strip",
      side,
      tier,
      center: edge.center,
      y: y + 0.56,
      width: span,
      height: 0.24,
      depth: 0.58,
      floorIndex: floor,
      bayIndex: -2,
      edge
    }),
    place({
      id: "lintel-strip",
      side,
      tier,
      center: edge.center,
      y: y + FLOOR_HEIGHT - 0.48,
      width: span,
      height: 0.26,
      depth: 0.54,
      floorIndex: floor,
      bayIndex: -3,
      edge
    }),
    ...cornerTrimJoints3(tier, side, edge, y - 0.16, "belt-corner-joint", 0.58)
  ];
}
function verticalPilasters(settings, tier, side, edge, count) {
  const result = [];
  const cadence = settings.shaftRhythm === "paired" ? 2 : 3;
  for (let index = 1; index < count; index++) {
    if (index % cadence !== 0) continue;
    result.push(place({
      id: tier.floors > 4 ? "pilaster-bundle" : "vertical-pilaster-strip",
      side,
      tier,
      center: edgeSeamCenter(edge, index, count),
      y: tier.y0,
      width: 0.58,
      height: tier.height,
      depth: 0.72,
      floorIndex: -1,
      bayIndex: index,
      edge
    }));
  }
  return result;
}
function tierTrim(tier, side, edge) {
  const span = edge.length;
  return [
    place({
      id: "belt-course-large",
      side,
      tier,
      center: edge.center,
      y: tier.y0 - 0.34,
      width: span,
      height: 0.54,
      depth: 0.74,
      floorIndex: -1,
      bayIndex: -4,
      edge
    }),
    place({
      id: "dentil-corbel-course",
      side,
      tier,
      center: edge.center,
      y: tier.y0 + tier.height - 0.3,
      width: span,
      height: 0.36,
      depth: 0.58,
      floorIndex: tier.floors,
      bayIndex: -5,
      edge
    }),
    place({
      id: "belt-course-small",
      side,
      tier,
      center: edge.center,
      y: tier.y0 + Math.max(FLOOR_HEIGHT, tier.height * 0.5),
      width: span,
      height: 0.32,
      depth: 0.52,
      floorIndex: Math.floor(tier.floors / 2),
      bayIndex: -6,
      edge
    }),
    ...cornerTrimJoints3(tier, side, edge, tier.y0 - 0.34, "belt-corner-joint", 0.74),
    ...cornerTrimJoints3(tier, side, edge, tier.y0 + tier.height - 0.3, "cornice-corner-joint", 0.88)
  ];
}
function cornerTrimJoints3(tier, side, edge, y, id, depth) {
  return [-1, 1].map((edgeSign) => place({
    id,
    side,
    tier,
    center: edge.center + edgeSign * (edge.length / 2 - 0.32),
    y,
    width: 0.86,
    height: id === "cornice-corner-joint" ? 0.88 : 0.42,
    depth,
    floorIndex: -9,
    bayIndex: edgeSign < 0 ? -90 : -91,
    edge
  }));
}
function verticalZones(settings, tier, side, edge, count) {
  const result = [];
  const center = Math.floor(count / 2);
  const bay = edge.length / count;
  if (side === "front" && (settings.buildingArchetype === "board-of-trade-tower" || settings.buildingArchetype === "high-rise-pyramid")) {
    const axisBays = clampedOddAxisBays(settings.centralAxisBays, count);
    const halfAxis = Math.floor(axisBays / 2);
    result.push(place({ id: "central-glass-shaft", side, tier, center: edgeBayCenter(edge, center, count), y: tier.y0, width: bay * axisBays, height: tier.height, depth: 1.02, floorIndex: -1, bayIndex: center, edge }));
    for (const pierIndex of [center - halfAxis - 1, center + halfAxis + 1]) {
      if (pierIndex <= 0 || pierIndex >= count - 1) continue;
      result.push(place({ id: "solid-side-pier", side, tier, center: edgeBayCenter(edge, pierIndex, count), y: tier.y0, width: bay, height: tier.height, depth: 0.86, floorIndex: -1, bayIndex: pierIndex, edge }));
    }
  }
  if (side !== "front") {
    const serviceIndex = side === "back" ? center : Math.max(1, Math.floor(count * 0.35));
    const slotIndex = Math.min(count - 2, serviceIndex + 1);
    result.push(place({ id: "structural-blank-wall", side, tier, center: edgeBayCenter(edge, serviceIndex, count), y: tier.y0, width: bay, height: tier.height, depth: 0.62, floorIndex: -1, bayIndex: serviceIndex, edge }));
    if (slotIndex !== serviceIndex) {
      result.push(place({ id: "recessed-window-slot", side, tier, center: edgeBayCenter(edge, slotIndex, count), y: tier.y0, width: bay, height: tier.height, depth: 0.95, floorIndex: -1, bayIndex: slotIndex, edge }));
    }
  }
  for (const cornerIndex of [0, count - 1]) {
    result.push(place({
      id: cornerPierId(settings),
      side,
      tier,
      center: edgeBayCenter(edge, cornerIndex, count),
      y: tier.y0,
      width: bay,
      height: tier.height,
      depth: 1.1,
      floorIndex: -1,
      bayIndex: cornerIndex,
      edge,
      moduleVariant: cornerIndex === 0 ? "start" : "end"
    }));
  }
  return result;
}
function isReservedVerticalZone(settings, side, index, count) {
  const center = Math.floor(count / 2);
  if (side === "front" && (settings.buildingArchetype === "board-of-trade-tower" || settings.buildingArchetype === "high-rise-pyramid")) {
    const axisBays = clampedOddAxisBays(settings.centralAxisBays, count);
    const halfAxis = Math.floor(axisBays / 2);
    return Math.abs(index - center) <= halfAxis || index === center - halfAxis - 1 || index === center + halfAxis + 1 || index === 0 || index === count - 1;
  }
  if (side !== "front") {
    const serviceIndex = side === "back" ? center : Math.max(1, Math.floor(count * 0.35));
    const slotIndex = Math.min(count - 2, serviceIndex + 1);
    return index === serviceIndex || slotIndex !== serviceIndex && index === slotIndex || index === 0 || index === count - 1;
  }
  return index === 0 || index === count - 1;
}
function cornerPierId(settings) {
  return settings.cornerTreatment === "rounded-piers" ? "rounded-corner-pier" : "wrapped-corner-pier";
}
function clampedOddAxisBays(value, count) {
  const max = Math.max(1, Math.min(5, count - 4));
  const oddMax = max % 2 === 0 ? max - 1 : max;
  const requested = Math.max(1, Math.round(value));
  const oddRequested = requested % 2 === 0 ? requested + 1 : requested;
  return Math.max(1, Math.min(oddRequested, Math.max(1, oddMax)));
}

function createKitPlacements(settings, tiers) {
  const placements = tiers.flatMap(
    (tier) => facadeSides.flatMap((side) => {
      if (tier.role === "podium") return createPodiumPlacements(settings, tier, side);
      if (tier.role === "crown") return createCrownPlacements(settings, tier, side);
      return createShaftPlacements(settings, tier, side);
    })
  );
  for (const tier of roofHostTiers(tiers)) placements.push(...createRoofPlacements(settings, tier));
  return placements;
}
function roofHostTiers(tiers) {
  const crowns = topTiers(tiers.filter((tier) => tier.role === "crown"));
  if (crowns.length > 0) return crowns;
  return topTiers(tiers.filter((tier) => tier.role === "shaft" || tier.role === "bridge"));
}
function topTiers(tiers) {
  if (tiers.length === 0) return [];
  const maxTop = Math.max(...tiers.map((tier) => tier.y0 + tier.height));
  return tiers.filter((tier) => Math.abs(tier.y0 + tier.height - maxTop) < 1e-3);
}

var financialCoreModules = [
  module("round-column", "Round column", "base", "Fluted column with stacked torus/plinth rings and cap blocks.", [1.3, 6.2, 1.3]),
  module("square-column", "Square column", "base", "Panelized square pier with bevelled base and capital courses.", [1.35, 6.1, 1.1]),
  module("paired-column", "Paired column", "base", "Two fluted columns carrying a shared classical entablature.", [4.4, 5.8, 1.5]),
  module("tall-lobby-window", "Tall lobby window", "base", "Tall bronze storefront window with deep limestone surround.", [3.2, 5.3, 0.9]),
  module("lobby-door", "Lobby door", "base", "Bronze double door with transom, lintel, and carved stone portal.", [3.4, 5.4, 1]),
  module("revolving-door-bay", "Revolving door bay", "base", "Curved bronze/glass revolving entry set inside stone side columns.", [4.2, 5.6, 1.4]),
  module("service-door", "Service door", "base", "Narrow black-metal service door with transom grille and stone jambs.", [2.8, 4.8, 0.9]),
  module("loading-dock-bay", "Loading dock bay", "base", "Roll-up loading shutter with heavy industrial lintel and side bollards.", [4.2, 4.9, 1]),
  module("granite-plinth", "Granite plinth", "base", "Dark granite foundation block with limestone upper cap.", [3.2, 1.15, 0.7]),
  module("corner-entrance", "Corner entrance", "base", "Wrapped corner portal with two street-facing bronze doors.", [4.4, 5.6, 1.6]),
  module("colossal-column", "Colossal column", "base", "Ten-meter fluted entry-order column with separate plinth, shaft, and ionic capital.", [1.7, 10.4, 1.7]),
  module("square-corner-pylon", "Square corner pylon", "base", "Massive square portico end pylon paired with a round column order.", [1.8, 10.2, 1.5]),
  module("triangular-pediment", "Triangular pediment", "base", "Full-depth temple-bank pediment with raking cornice and tympanum face.", [10, 3, 1.5]),
  module("pediment-eagle", "Pediment eagle/seal", "base", "Raised institutional eagle and shield relief for pediment centers.", [2.2, 1.1, 0.35]),
  module("acroterion-scroll", "Acroterion scroll", "base", "Corner scroll ornament for pediment and parapet ends.", [0.9, 1, 0.45]),
  module("company-frieze", "Company frieze", "base", "Long carved company-name frieze tablet below a bank pediment.", [8, 0.9, 0.45]),
  module("clock-medallion", "Clock medallion", "base", "Large round clock/medallion centerpiece with stone surround.", [2, 2, 0.45]),
  module("rusticated-base-block", "Rusticated base block", "base", "Deep rusticated stone block with horizontal courses for fortress bases.", [3.2, 2.4, 0.9]),
  module("bank-grille", "Bank grille", "base", "Large barred banking hall grille set into a heavy stone surround.", [3.4, 4.4, 0.9]),
  module("barred-window", "Metal-barred window", "base", "Small secure ground-floor window with bronze/black security bars.", [2.6, 2.8, 0.72]),
  module("storefront-curtain-wall", "Storefront curtain wall", "base", "Tall black bronze/glass wall set behind a column portico.", [4.6, 7, 0.7]),
  module("security-door", "Security door", "base", "Heavy institutional security door with grille transom and side stone reveals.", [2.8, 4.4, 0.9]),
  module("wall-plaque", "Wall plaque", "base", "Mounted bronze/stone bank plaque integrated into the facade.", [1.2, 1.4, 0.22]),
  module("address-plaque", "Address plaque", "base", "Small address number plaque with raised bronze numerals.", [0.9, 0.55, 0.18]),
  module("flag-mount", "Flag/banner mount", "base", "Angled flag/banner bracket mounted to stone facade.", [1.4, 1.6, 0.5]),
  module("bollard", "Bollard", "base", "Short black street bollard for bank frontage security.", [0.45, 1.1, 0.45]),
  module("wall-camera", "Wall camera", "base", "Small security camera pod and wall arm.", [0.55, 0.45, 0.7]),
  module("wall-lamp", "Wall lamp", "base", "Classical wall lamp with bracket and glass globe.", [0.55, 1.4, 0.6]),
  module("sidewalk-entry", "Sidewalk plinth/entry", "base", "Stone sidewalk threshold with curb, stair lip, and door landing.", [4.2, 0.45, 1.4]),
  module("window-3m", "3m window bay", "shaft", "Narrow office bay with bronze sash, sill, spandrel, and pilaster sides.", [3, 3.35, 0.72]),
  module("window-4m", "4m window bay", "shaft", "Wide office bay with paired vertical bronze sash and carved spandrel.", [4, 3.35, 0.74]),
  module("double-window-bay", "Double-window bay", "shaft", "Twin office windows divided by a central stone mullion and rosette spandrels.", [4.2, 3.35, 0.78]),
  module("blank-bay", "Blank bay", "shaft", "Stone service bay with framed slab panels and vertical reveal grooves.", [3.2, 3.35, 0.5]),
  module("corner-bay", "Corner bay", "shaft", "Wrapped corner bay with return-facing window and shared corner pilaster.", [3.2, 3.35, 1.2]),
  module("vertical-pilaster-strip", "Vertical pilaster strip", "shaft", "Reusable fluted pilaster with base block, cap, and inset channels.", [0.72, 3.35, 0.52]),
  module("spandrel-panel", "Spandrel panel", "shaft", "Carved floral medallion panel for between-window courses.", [3.4, 1, 0.42]),
  module("floor-band-strip", "Floor-band strip", "shaft", "Greek-key floor divider band with cap and base fillets.", [4, 0.58, 0.42]),
  module("central-glass-shaft", "Central glass shaft", "shaft", "Multi-floor recessed black-glass vertical slot framed by stone piers.", [5.6, 13.4, 1]),
  module("solid-side-pier", "Solid side pier", "shaft", "Tall blank structural pier flanking a central vertical shaft.", [1.4, 13.4, 0.86]),
  module("buttress-pier", "Buttress pier", "shaft", "Projecting multi-floor buttress pier with stepped cap blocks.", [1.1, 10, 1]),
  module("pilaster-bundle", "Pilaster bundle", "shaft", "Grouped vertical pilasters spanning multiple floors.", [1.2, 10, 0.74]),
  module("recessed-window-slot", "Recessed window slot", "shaft", "Deep continuous vertical window slot with narrow stacked panes.", [2.2, 10, 0.95]),
  module("arched-window-bay", "Arched window bay", "shaft", "Arched stone window bay with voussoirs and bronze sash.", [3.2, 4, 0.85]),
  module("arcade-bay", "Romanesque arcade bay", "shaft", "Tall arched arcade bay with cylindrical colonnettes and deep reveal.", [3.6, 5.2, 1.1]),
  module("brick-window-bay", "Terra-cotta window bay", "shaft", "Red masonry/terra-cotta bay with black sash and brick coursing.", [3.2, 3.35, 0.7]),
  module("deep-window-well", "Deep window well", "shaft", "Deeply recessed window surround with stepped sill/lintel hierarchy.", [3.2, 3.35, 1]),
  module("carved-spandrel-vine", "Carved vine spandrel", "shaft", "Decorative carved spandrel panel with vine/leaf relief.", [3.4, 1, 0.42]),
  module("wrapped-corner-pier", "Wrapped corner pier", "shaft", "Structural corner pier wrapping both facade directions without stretching.", [1.2, 10, 1.2]),
  module("rounded-corner-pier", "Rounded corner pier", "shaft", "Rounded/chamfered structural corner pier for Chicago financial tower corners.", [1.4, 10, 1.35]),
  module("structural-blank-wall", "Structural blank wall", "shaft", "Tall blank wall zone for party walls, service cores, and side facades.", [3.2, 10, 0.62]),
  module("belt-course-small", "Belt course small", "trim", "Slim belt course with bevelled upper/lower beads.", [4, 0.34, 0.42]),
  module("belt-course-large", "Belt course large", "trim", "Large ornamented belt course with dentils and carved frieze panels.", [4, 0.72, 0.62]),
  module("window-sill-strip", "Window sill strip", "trim", "Projecting sill strip with underside drip return.", [3.4, 0.28, 0.5]),
  module("lintel-strip", "Lintel strip", "trim", "Horizontal lintel strip with panel seams and raised edge fillets.", [3.4, 0.38, 0.48]),
  module("small-cornice", "Small cornice", "trim", "Short projecting cornice with dentil underside.", [4, 0.72, 0.85]),
  module("large-cornice", "Large cornice", "trim", "Deep classical cornice with bracket blocks and carved frieze.", [4.6, 1.1, 1.1]),
  module("corner-cornice", "Corner cornice", "trim", "L-shaped cornice section wrapping around a building corner.", [4.2, 1.1, 1.4]),
  module("belt-corner-joint", "Belt corner joint", "trim", "Authored L/corner connector for horizontal belt and sill courses.", [1.3, 0.52, 1.3]),
  module("cornice-corner-joint", "Cornice corner joint", "trim", "Heavy projecting corner block that joins cornice runs without open slab ends.", [1.6, 0.95, 1.6]),
  module("dentil-corbel-course", "Dentil corbel course", "trim", "Course-aligned dentil/corbel band with bracket rhythm.", [4, 0.95, 0.9]),
  module("crown-window-bay", "Crown window bay", "crown", "Short attic/crown bay with heavy pilasters and parapet rail blocks.", [3.6, 3, 0.85]),
  module("parapet-section", "Parapet section", "crown", "Ornamented parapet wall with raised piers and inset panels.", [4, 2, 0.72]),
  module("corner-parapet", "Corner parapet", "crown", "L-shaped parapet corner with cap blocks and round finial bases.", [3.6, 2.1, 1.2]),
  module("attic-crest-panel", "Attic crest panel", "crown", "Raised top crest with small rosette tablets and a projecting cap course.", [4, 1, 0.82]),
  module("crown-pediment", "Crown pediment", "crown", "Stepped central pediment block for bank tower crowns.", [4.8, 1.45, 1]),
  module("corner-finial", "Corner finial", "crown", "Small limestone urn/obelisk finial for parapet corners.", [0.8, 1.6, 0.8]),
  module("crown-urn-finial", "Crown urn finial", "crown", "Rounded classical urn finial for dense crown decoration rhythms.", [0.9, 1.4, 0.9]),
  module("crown-obelisk-finial", "Crown obelisk finial", "crown", "Tall stepped obelisk finial for skyline crown silhouettes.", [0.85, 2.2, 0.85]),
  module("crown-pillar-finial", "Crown pillar finial", "crown", "Small repeated parapet pillar/mini-pylon for edge finial rhythms.", [0.7, 1.2, 0.7]),
  module("crown-cartouche-panel", "Crown cartouche panel", "crown", "Raised cartouche/parapet relief panel used as a crown decoration module.", [3, 1.25, 0.74]),
  module("sloped-metal-roof", "Sloped metal roof", "roof", "Pyramidal/hipped standing-seam metal roof with ribs, hips, and ridge cap.", [10, 4, 10]),
  module("roof-statue-mast", "Roof statue mast", "roof", "Board-of-trade style roof sculpture mast on a stone/metal pedestal.", [1.6, 5.8, 1.6]),
  module("roof-lantern", "Roof lantern", "roof", "Open steel lantern/platform frame below a sculpture mast.", [2.4, 1.8, 2.4]),
  module("roof-crest", "Roof crest", "roof", "Ornamental roof crest/flagpole base for skyline silhouettes.", [1.4, 2.4, 1.4]),
  module("roof-mech-box", "Roof mech box", "roof", "Panelized rooftop mechanical box with vent grilles and cap slab.", [3.6, 2, 2.8]),
  module("hvac-cluster", "HVAC cluster", "roof", "Grouped cylindrical fans and rectangular condenser boxes.", [4.2, 2.1, 2.8]),
  module("roof-railing", "Roof railing", "roof", "Bronze roof safety railing with posts and horizontal bars.", [4.4, 1.15, 0.42]),
  module("antenna", "Antenna", "roof", "Stacked mast antenna with collars and small equipment nodes.", [0.8, 4.8, 0.8])
];
function module(id, label, group, description, size) {
  return {
    id,
    label,
    group,
    description,
    implemented: true,
    quality: "kit-ready",
    defaultSize: { width: size[0], height: size[1], depth: size[2] }
  };
}

var stone = [0.9, 0.84, 0.73];
var stoneDark = [0.58, 0.54, 0.47];
var stoneWarm = [0.78, 0.7, 0.6];
var granite = [0.25, 0.24, 0.23];
var glass = [0.018, 0.026, 0.03];
var bronze = [0.7, 0.45, 0.2];
var bronzeDark = [0.24, 0.15, 0.08];
var blackMetal = [0.035, 0.034, 0.032];
var roofMetal = [0.18, 0.19, 0.18];

function profiledCylinder(input) {
  const segments = input.segments ?? 40;
  for (let index = 0; index < segments; index++) {
    const a0 = index / segments * Math.PI * 2;
    const a1 = (index + 1) / segments * Math.PI * 2;
    const r0 = fluteRadius(a0, input.radius, input.flutes);
    const r1 = fluteRadius(a1, input.radius, input.flutes);
    quad(input.ctx, input.slot, [
      point(input, a1, r1, input.y0),
      point(input, a0, r0, input.y0),
      point(input, a0, r0, input.y1),
      point(input, a1, r1, input.y1)
    ], input.color);
  }
}
function stackedColumn(input) {
  const h = input.y1 - input.y0;
  const bands = [
    [0, 0.06, input.radius * 1.38],
    [0.06, 0.12, input.radius * 1.22],
    [0.12, 0.18, input.radius * 1.02],
    [0.18, 0.84, input.radius],
    [0.84, 0.9, input.radius * 1.06],
    [0.9, 0.95, input.radius * 1.24],
    [0.95, 1, input.radius * 1.42]
  ];
  for (const [a, b, radius] of bands) {
    profiledCylinder({
      ctx: input.ctx,
      slot: "limestone",
      x: input.x,
      z: input.z,
      y0: input.y0 + h * a,
      y1: input.y0 + h * b,
      radius,
      color: input.color,
      segments: radius === input.radius ? 56 : 44,
      flutes: radius === input.radius ? 18 : void 0
    });
  }
}
function point(input, angle, radius, y) {
  return [
    input.x + Math.cos(angle) * radius,
    y,
    input.z + Math.sin(angle) * radius
  ];
}
function quad(ctx, slot, points, color) {
  ctx.writer.appendQuad(slot, points.map(ctx.transform), color);
}
function fluteRadius(angle, radius, flutes) {
  if (!flutes) return radius;
  return radius * (0.93 + Math.max(0, Math.sin(angle * flutes)) * 0.07);
}

function slab(ctx, slot, rect, color) {
  const { x0, x1, y0, y1, z0, z1 } = rect;
  quad2(ctx, slot, [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], color);
  quad2(ctx, slot, [[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]], color);
  quad2(ctx, slot, [[x1, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1]], color);
  quad2(ctx, slot, [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], color);
  quad2(ctx, slot, [[x0, y1, z1], [x1, y1, z1], [x1, y1, z0], [x0, y1, z0]], color);
}
function solidBox(ctx, slot, min, max, color) {
  const [x0, y0, z0] = min;
  const [x1, y1, z1] = max;
  quad2(ctx, slot, [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], color);
  quad2(ctx, slot, [[x1, y0, z0], [x0, y0, z0], [x0, y1, z0], [x1, y1, z0]], color);
  quad2(ctx, slot, [[x1, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1]], color);
  quad2(ctx, slot, [[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]], color);
  quad2(ctx, slot, [[x0, y1, z1], [x1, y1, z1], [x1, y1, z0], [x0, y1, z0]], color);
  quad2(ctx, slot, [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], color);
}
function bevelBlock(ctx, slot, min, max, bevel, color) {
  solidBox(ctx, slot, [min[0] + bevel, min[1] + bevel, min[2]], [max[0] - bevel, max[1] - bevel, max[2]], color);
  slab(ctx, slot, { x0: min[0], x1: min[0] + bevel, y0: min[1] + bevel, y1: max[1] - bevel, z0: min[2], z1: max[2] }, color);
  slab(ctx, slot, { x0: max[0] - bevel, x1: max[0], y0: min[1] + bevel, y1: max[1] - bevel, z0: min[2], z1: max[2] }, color);
  slab(ctx, slot, { x0: min[0] + bevel, x1: max[0] - bevel, y0: min[1], y1: min[1] + bevel, z0: min[2], z1: max[2] }, color);
  slab(ctx, slot, { x0: min[0] + bevel, x1: max[0] - bevel, y0: max[1] - bevel, y1: max[1], z0: min[2], z1: max[2] }, color);
}
function quad2(ctx, slot, points, color) {
  ctx.writer.appendQuad(
    slot,
    points.map(ctx.transform),
    color
  );
}

var roundColumnModule = (ctx) => {
  stackedColumn({
    ctx,
    x: 0,
    z: 0.18,
    y0: 0,
    y1: ctx.height,
    radius: Math.min(ctx.width, ctx.depth) * 0.28,
    color: stone
  });
  ctx.anchors.capital = [0, ctx.height * 0.92, 0.18];
};
var squareColumnModule = (ctx) => {
  const w = ctx.width / 2;
  bevelBlock(ctx, "limestone", [-w, 0, -0.1], [w, ctx.height, 0.42], 0.08, stone);
  for (let index = 1; index < 6; index++) {
    const y = ctx.height / 6 * index;
    slab(ctx, "limestone", { x0: -w + 0.08, x1: w - 0.08, y0: y - 0.025, y1: y + 0.025, z0: 0.43, z1: 0.5 }, stoneDark);
  }
  slab(ctx, "limestone", { x0: -w - 0.12, x1: w + 0.12, y0: 0, y1: 0.34, z0: -0.16, z1: 0.58 }, stoneWarm);
  slab(ctx, "limestone", { x0: -w - 0.14, x1: w + 0.14, y0: ctx.height - 0.48, y1: ctx.height, z0: -0.16, z1: 0.6 }, stoneWarm);
};
var pairedColumnModule = (ctx) => {
  const columnY0 = 0.15;
  const columnY1 = ctx.height - 0.62;
  for (const x of [-ctx.width * 0.28, ctx.width * 0.28]) {
    stackedColumn({ ctx, x, z: 0.22, y0: columnY0, y1: columnY1, radius: 0.3, color: stone });
    solidBox(ctx, "granite", [x - 0.48, 0, -0.22], [x + 0.48, 0.24, 0.68], stoneDark);
  }
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: ctx.height - 0.72, y1: ctx.height - 0.28, z0: -0.12, z1: 0.72 }, stoneWarm);
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.12, x1: ctx.width / 2 + 0.12, y0: ctx.height - 0.28, y1: ctx.height, z0: -0.18, z1: 0.84 }, stone);
  solidBox(ctx, "bronze", [-0.08, 0.35, 0], [0.08, ctx.height - 0.95, 0.08], bronze);
};

function dentils(ctx, x0, x1, y0, y1, z0, z1, count) {
  const step = (x1 - x0) / count;
  for (let index = 0; index < count; index += 2) {
    slab(ctx, "ornament", {
      x0: x0 + step * index + step * 0.18,
      x1: x0 + step * (index + 1) - step * 0.18,
      y0,
      y1,
      z0,
      z1
    }, stone);
  }
}
function greekKey(ctx, x0, x1, y, z0, z1, count) {
  const step = (x1 - x0) / count;
  for (let index = 0; index < count; index++) {
    const left = x0 + index * step;
    slab(ctx, "ornament", { x0: left + step * 0.08, x1: left + step * 0.9, y0: y, y1: y + 0.08, z0, z1 }, stoneDark);
    slab(ctx, "ornament", { x0: left + step * 0.08, x1: left + step * 0.18, y0: y, y1: y + 0.32, z0, z1 }, stoneDark);
    slab(ctx, "ornament", { x0: left + step * 0.18, x1: left + step * 0.72, y0: y + 0.24, y1: y + 0.32, z0, z1 }, stoneDark);
    slab(ctx, "ornament", { x0: left + step * 0.62, x1: left + step * 0.72, y0: y + 0.12, y1: y + 0.32, z0, z1 }, stoneDark);
  }
}
function rosette(ctx, x, y, z0, z1, radius) {
  for (let index = 0; index < 12; index++) {
    const angle = index / 12 * Math.PI * 2;
    const cx = x + Math.cos(angle) * radius * 0.42;
    const cy = y + Math.sin(angle) * radius * 0.42;
    slab(ctx, "ornament", { x0: cx - radius * 0.06, x1: cx + radius * 0.06, y0: cy - radius * 0.18, y1: cy + radius * 0.18, z0, z1 }, stone);
  }
  slab(ctx, "ornament", { x0: x - radius * 0.14, x1: x + radius * 0.14, y0: y - radius * 0.14, y1: y + radius * 0.14, z0, z1 }, stoneDark);
}
function bronzeMullions(ctx, x0, x1, y0, y1, z0, z1, splits) {
  for (let index = 1; index < splits; index++) {
    const x = x0 + (x1 - x0) / splits * index;
    slab(ctx, "bronze", { x0: x - 0.035, x1: x + 0.035, y0, y1, z0, z1 }, bronze);
  }
  const mid = y0 + (y1 - y0) * 0.58;
  slab(ctx, "bronze", { x0, x1, y0: mid - 0.035, y1: mid + 0.035, z0, z1 }, bronzeDark);
}

function framedWindow(input) {
  const { ctx, x0, x1, y0, y1, side, top, bottom } = input;
  slab(ctx, "limestone", { x0, x1: x0 + side, y0, y1, z0: -0.08, z1: 0.28 }, stone);
  slab(ctx, "limestone", { x0: x1 - side, x1, y0, y1, z0: -0.08, z1: 0.28 }, stone);
  slab(ctx, "limestone", { x0: x0 + side, x1: x1 - side, y0: y1 - top, y1, z0: -0.08, z1: 0.26 }, stone);
  slab(ctx, "limestone", { x0: x0 + side, x1: x1 - side, y0, y1: y0 + bottom, z0: -0.08, z1: 0.22 }, stoneWarm);
  const apertureX0 = x0 + side;
  const apertureX1 = x1 - side;
  const apertureY0 = y0 + bottom;
  const apertureY1 = y1 - top;
  slab(ctx, "black-metal", { x0: apertureX0 - 0.04, x1: apertureX1 + 0.04, y0: apertureY0 - 0.04, y1: apertureY1 + 0.04, z0: -0.1, z1: 0.04 }, blackMetal);
  slab(ctx, "glass", { x0: apertureX0 - 0.01, x1: apertureX1 + 0.01, y0: apertureY0 - 0.01, y1: apertureY1 + 0.01, z0: 0.02, z1: 0.08 }, glass);
  bronzeMullions(ctx, apertureX0 + 0.04, apertureX1 - 0.04, apertureY0 + 0.04, apertureY1 - 0.04, 0.08, 0.18, input.splits);
  if (input.spandrel) {
    const sy0 = y0 + 0.12;
    const sy1 = y0 + bottom - 0.14;
    slab(ctx, "ornament", { x0: apertureX0, x1: apertureX1, y0: sy0, y1: sy1, z0: 0.1, z1: 0.22 }, stone);
    rosette(ctx, (apertureX0 + apertureX1) / 2, (sy0 + sy1) / 2, 0.22, 0.34, Math.min(apertureX1 - apertureX0, sy1 - sy0) * 0.32);
  }
}
function bronzeDoor(input) {
  const { ctx, x0, x1, y0, y1 } = input;
  slab(ctx, "black-metal", { x0: x0 - 0.03, x1: x1 + 0.03, y0: y0 - 0.03, y1: y1 + 0.03, z0: -0.1, z1: 0.02 }, blackMetal);
  slab(ctx, input.shutter ? "black-metal" : "glass", { x0, x1, y0, y1, z0: 0.02, z1: 0.08 }, input.shutter ? blackMetal : glass);
  if (input.shutter) {
    for (let index = 1; index < 8; index++) {
      const y = y0 + (y1 - y0) / 8 * index;
      slab(ctx, "bronze", { x0: x0 + 0.1, x1: x1 - 0.1, y0: y - 0.02, y1: y + 0.02, z0: -0.1, z1: 0.02 }, bronze);
    }
    return;
  }
  bronzeMullions(ctx, x0, x1, y0, y1, 0.02, 0.16, input.revolving ? 3 : 2);
  slab(ctx, "bronze", { x0, x1, y0: y0 + 0.14, y1: y0 + 0.28, z0: -0.12, z1: 0.08 }, bronze);
}

var tallLobbyWindowModule = (ctx) => {
  portal(ctx, 0.46, 0.72);
  framedWindow({ ctx, x0: -ctx.width / 2 + 0.34, x1: ctx.width / 2 - 0.34, y0: 0.34, y1: ctx.height - 0.48, side: 0.22, top: 0.28, bottom: 0.58, splits: 3, spandrel: true });
};
var lobbyDoorModule = (ctx) => {
  portal(ctx, 0.52, 0.86);
  bronzeDoor({ ctx, x0: -ctx.width / 2 + 0.64, x1: ctx.width / 2 - 0.64, y0: 0.34, y1: ctx.height - 1 });
  slab(ctx, "bronze", { x0: -0.55, x1: 0.55, y0: ctx.height - 0.88, y1: ctx.height - 0.72, z0: 0.04, z1: 0.18 }, bronze);
};
var revolvingDoorBayModule = (ctx) => {
  portal(ctx, 0.46, 0.94);
  for (const x of [-ctx.width * 0.34, ctx.width * 0.34]) {
    profiledCylinder({ ctx, slot: "limestone", x, z: 0.38, y0: 0.2, y1: ctx.height - 0.52, radius: 0.22, color: stone, segments: 32, flutes: 14 });
  }
  bronzeDoor({ ctx, x0: -ctx.width * 0.22, x1: ctx.width * 0.22, y0: 0.28, y1: ctx.height - 0.92, revolving: true });
  profiledCylinder({ ctx, slot: "bronze", x: 0, z: 0.14, y0: 0.24, y1: ctx.height - 0.92, radius: ctx.width * 0.22, color: bronze, segments: 32 });
};
var cornerEntranceModule = (ctx) => {
  lobbyDoorModule(ctx);
  solidBox(ctx, "limestone", [ctx.width / 2 - 0.24, 0, -ctx.depth * 0.42], [ctx.width / 2 + 0.22, ctx.height, 0.44], stone);
  bronzeDoor({ ctx, x0: ctx.width / 2 - 0.18, x1: ctx.width / 2 + 0.1, y0: 0.4, y1: ctx.height - 1.2 });
};
function portal(ctx, jamb, projection) {
  const x0 = -ctx.width / 2;
  const x1 = ctx.width / 2;
  slab(ctx, "limestone", { x0, x1: x0 + jamb, y0: 0, y1: ctx.height, z0: -0.12, z1: projection }, stone);
  slab(ctx, "limestone", { x0: x1 - jamb, x1, y0: 0, y1: ctx.height, z0: -0.12, z1: projection }, stone);
  slab(ctx, "limestone", { x0: x0 + jamb, x1: x1 - jamb, y0: ctx.height - 0.72, y1: ctx.height, z0: -0.12, z1: projection }, stoneWarm);
  slab(ctx, "limestone", { x0, x1, y0: 0, y1: 0.34, z0: -0.1, z1: projection * 0.72 }, stoneDark);
  dentils(ctx, x0 + 0.22, x1 - 0.22, ctx.height - 0.56, ctx.height - 0.38, projection, projection + 0.18, 11);
}

function archedOpening(input) {
  const { ctx, x0, x1, y0, y1, depth } = input;
  const width = x1 - x0;
  const spring = y0 + (y1 - y0) * 0.58;
  const radius = width * 0.5;
  slab(ctx, "limestone", { x0, x1, y0, y1, z0: -0.18, z1: -0.04 }, stoneWarm);
  slab(ctx, "black-metal", { x0: x0 + 0.34, x1: x1 - 0.34, y0: y0 + 0.22, y1: spring + radius * 0.88, z0: -0.04, z1: 0.06 }, stoneDark);
  slab(ctx, "limestone", { x0, x1: x0 + 0.34, y0, y1, z0: -0.1, z1: depth }, stone);
  slab(ctx, "limestone", { x0: x1 - 0.34, x1, y0, y1, z0: -0.1, z1: depth }, stone);
  slab(ctx, "limestone", { x0: x0 + 0.34, x1: x1 - 0.34, y0: y1 - 0.34, y1, z0: -0.1, z1: depth * 0.72 }, stoneWarm);
  archRing(ctx, x0 + width / 2, spring, radius, 0.34, -0.1, depth);
  slab(ctx, "glass", { x0: x0 + 0.42, x1: x1 - 0.42, y0: y0 + 0.3, y1: spring + radius * 0.72, z0: 0.06, z1: 0.12 }, glass);
  bronzeMullions(ctx, x0 + 0.36, x1 - 0.36, y0 + 0.3, spring + radius * 0.72, 0.06, 0.18, 2);
  if (input.bars) {
    const count = 5;
    for (let index = 0; index < count; index++) {
      const x = x0 + 0.5 + (width - 1) / (count - 1) * index;
      slab(ctx, "black-metal", { x0: x - 0.035, x1: x + 0.035, y0: y0 + 0.2, y1: spring + radius * 0.65, z0: 0.18, z1: 0.26 }, stoneDark);
    }
  }
}
function triangularPedimentProfile(input) {
  const { ctx, width, height, depth } = input;
  const w = width / 2;
  const zBack = -depth * 0.62;
  solidBox(ctx, "limestone", [-w, 0, zBack], [w, height * 0.28, depth * 0.62], stoneWarm);
  triangleFace(ctx, [-w, height * 0.28, depth * 0.55], [0, height, depth * 0.72], [w, height * 0.28, depth * 0.55], stone);
  triangleFace(ctx, [-w, height * 0.28, zBack], [0, height, zBack], [w, height * 0.28, zBack], stone);
  triangleFace(ctx, [-w * 0.82, height * 0.34, depth * 0.74], [0, height * 0.82, depth * 0.92], [w * 0.82, height * 0.34, depth * 0.74], stoneWarm);
  dentils(ctx, -w + 0.35, w - 0.35, height * 0.16, height * 0.26, depth * 0.62, depth * 0.84, Math.max(8, Math.floor(width * 1.1)));
}
function carvedSeal(ctx, x, y, z0, z1, radius) {
  rosette(ctx, x, y, z0, z1, radius);
  slab(ctx, "ornament", { x0: x - radius * 0.5, x1: x + radius * 0.5, y0: y - radius * 0.08, y1: y + radius * 0.08, z0, z1 }, stoneDark);
  slab(ctx, "ornament", { x0: x - radius * 0.08, x1: x + radius * 0.08, y0: y - radius * 0.46, y1: y + radius * 0.46, z0, z1 }, stoneDark);
}
function archRing(ctx, cx, cy, radius, thickness, z0, z1) {
  const segments = 18;
  for (let index = 0; index < segments; index++) {
    const a0 = Math.PI - Math.PI * index / segments;
    const a1 = Math.PI - Math.PI * (index + 1) / segments;
    const outer0 = point2(cx, cy, radius, a0, z1);
    const outer1 = point2(cx, cy, radius, a1, z1);
    const inner1 = point2(cx, cy, radius - thickness, a1, z1);
    const inner0 = point2(cx, cy, radius - thickness, a0, z1);
    const outerBack0 = point2(cx, cy, radius, a0, z0);
    const outerBack1 = point2(cx, cy, radius, a1, z0);
    const innerBack1 = point2(cx, cy, radius - thickness, a1, z0);
    const innerBack0 = point2(cx, cy, radius - thickness, a0, z0);
    ctx.writer.appendQuad("limestone", [
      ctx.transform(outer0),
      ctx.transform(inner0),
      ctx.transform(inner1),
      ctx.transform(outer1)
    ], stone);
    ctx.writer.appendQuad("limestone", [
      ctx.transform(outerBack1),
      ctx.transform(innerBack1),
      ctx.transform(innerBack0),
      ctx.transform(outerBack0)
    ], stone);
    ctx.writer.appendQuad("limestone", [
      ctx.transform(outerBack0),
      ctx.transform(outer0),
      ctx.transform(outer1),
      ctx.transform(outerBack1)
    ], stone);
    ctx.writer.appendQuad("limestone", [
      ctx.transform(inner0),
      ctx.transform(innerBack0),
      ctx.transform(innerBack1),
      ctx.transform(inner1)
    ], stone);
  }
}
function triangleFace(ctx, a, b, c, color) {
  ctx.writer.appendQuad("limestone", [
    ctx.transform(a),
    ctx.transform(b),
    ctx.transform(c),
    ctx.transform(c)
  ], color);
}
function point2(cx, cy, radius, angle, z) {
  return [cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius, z];
}

var colossalColumnModule = (ctx) => {
  const capitalScale = ctx.width * 0.44;
  const capitalY = ctx.height - capitalScale * 0.28;
  stackedColumn({ ctx, x: 0, z: 0.22, y0: 0, y1: capitalY, radius: ctx.width * 0.24, color: stone });
  ionicCapital(ctx, 0, capitalY, capitalScale);
  solidBox(ctx, "limestone", [-ctx.width * 0.56, ctx.height - 0.18, -0.12], [ctx.width * 0.56, ctx.height, 0.78], stoneWarm);
  solidBox(ctx, "granite", [-ctx.width * 0.46, 0, -0.32], [ctx.width * 0.46, 0.42, 0.72], granite);
};
var squareCornerPylonModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width / 2, 0, -0.18], [ctx.width / 2, ctx.height, 0.72], stone);
  for (let index = 1; index < 9; index++) {
    const y = ctx.height / 9 * index;
    slab(ctx, "limestone", { x0: -ctx.width / 2 + 0.12, x1: ctx.width / 2 - 0.12, y0: y - 0.035, y1: y + 0.035, z0: 0.72, z1: 0.86 }, stoneDark);
  }
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.18, x1: ctx.width / 2 + 0.18, y0: ctx.height - 0.72, y1: ctx.height, z0: -0.18, z1: 0.94 }, stoneWarm);
};
var triangularPedimentModule = (ctx) => {
  triangularPedimentProfile({ ctx, width: ctx.width, height: ctx.height, depth: ctx.depth });
  dentils(ctx, -ctx.width / 2 + 0.35, ctx.width / 2 - 0.35, 0.12, 0.28, ctx.depth * 0.72, ctx.depth * 0.96, Math.max(10, Math.floor(ctx.width)));
};
var pedimentEagleModule = (ctx) => {
  carvedSeal(ctx, 0, ctx.height * 0.56, 0.08, 0.34, Math.min(ctx.width, ctx.height) * 0.32);
  for (const side of [-1, 1]) {
    slab(ctx, "ornament", { x0: side * 0.12, x1: side * ctx.width * 0.42, y0: ctx.height * 0.48, y1: ctx.height * 0.64, z0: 0.12, z1: 0.34 }, stoneWarm);
  }
};
var acroterionScrollModule = (ctx) => {
  profiledCylinder({ ctx, slot: "limestone", x: 0, z: 0.18, y0: 0.08, y1: ctx.height * 0.72, radius: ctx.width * 0.2, color: stone, segments: 24 });
  rosette(ctx, 0, ctx.height * 0.54, 0.26, 0.48, ctx.width * 0.34);
  solidBox(ctx, "limestone", [-ctx.width * 0.32, 0, -0.08], [ctx.width * 0.32, 0.16, 0.42], stoneDark);
};
var companyFriezeModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -ctx.depth * 0.68, z1: 0.42 }, stoneWarm);
  const letters = Math.max(8, Math.floor(ctx.width / 0.42));
  for (let index = 0; index < letters; index++) {
    const x = -ctx.width / 2 + 0.35 + index * ((ctx.width - 0.7) / letters);
    slab(ctx, "ornament", { x0: x - 0.055, x1: x + 0.055, y0: ctx.height * 0.28, y1: ctx.height * 0.72, z0: 0.42, z1: 0.54 }, stoneDark);
  }
};
var clockMedallionModule = (ctx) => {
  rosette(ctx, 0, ctx.height / 2, 0.08, 0.32, ctx.width * 0.42);
  profiledCylinder({ ctx, slot: "bronze", x: 0, z: 0.34, y0: ctx.height * 0.46, y1: ctx.height * 0.54, radius: ctx.width * 0.38, color: bronze, segments: 48 });
  slab(ctx, "black-metal", { x0: -0.035, x1: 0.035, y0: ctx.height * 0.5, y1: ctx.height * 0.78, z0: 0.48, z1: 0.58 }, blackMetal);
  slab(ctx, "black-metal", { x0: 0, x1: ctx.width * 0.24, y0: ctx.height * 0.49, y1: ctx.height * 0.55, z0: 0.48, z1: 0.58 }, blackMetal);
};
var rusticatedBaseBlockModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width / 2, 0, -0.12], [ctx.width / 2, ctx.height, 0.58], stoneWarm);
  const rows = Math.max(3, Math.floor(ctx.height / 0.45));
  for (let row = 1; row < rows; row++) {
    const y = ctx.height / rows * row;
    slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: y - 0.025, y1: y + 0.025, z0: 0.58, z1: 0.74 }, stoneDark);
  }
};
var bankGrilleModule = (ctx) => {
  framedWindow({ ctx, x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, side: 0.42, top: 0.46, bottom: 0.42, splits: 3 });
  grilleBars(ctx, -ctx.width * 0.32, ctx.width * 0.32, 0.56, ctx.height - 0.62, 7);
};
var barredWindowModule = (ctx) => {
  framedWindow({ ctx, x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, side: 0.34, top: 0.38, bottom: 0.42, splits: 2 });
  grilleBars(ctx, -ctx.width * 0.26, ctx.width * 0.26, 0.48, ctx.height - 0.44, 5);
};
var storefrontCurtainWallModule = (ctx) => {
  slab(ctx, "black-metal", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.06, z1: 0.12 }, blackMetal);
  slab(ctx, "glass", { x0: -ctx.width / 2 + 0.12, x1: ctx.width / 2 - 0.12, y0: 0.18, y1: ctx.height - 0.18, z0: 0, z1: 0.08 }, glass);
  grilleBars(ctx, -ctx.width / 2 + 0.2, ctx.width / 2 - 0.2, 0.28, ctx.height - 0.28, 4);
};
var securityDoorModule = (ctx) => {
  bronzeDoor({ ctx, x0: -ctx.width * 0.28, x1: ctx.width * 0.28, y0: 0.32, y1: ctx.height - 0.52, shutter: true });
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: -ctx.width * 0.32, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.55 }, stone);
  slab(ctx, "limestone", { x0: ctx.width * 0.32, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.55 }, stone);
  slab(ctx, "black-metal", { x0: -ctx.width * 0.24, x1: ctx.width * 0.24, y0: ctx.height - 0.82, y1: ctx.height - 0.46, z0: 0.08, z1: 0.24 }, blackMetal);
};
var wallPlaqueModule = (ctx) => {
  slab(ctx, "bronze", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: 0.04, z1: 0.18 }, bronzeDark);
  slab(ctx, "bronze", { x0: -ctx.width / 2 + 0.08, x1: ctx.width / 2 - 0.08, y0: 0.08, y1: ctx.height - 0.08, z0: 0.18, z1: 0.26 }, bronze);
};
var addressPlaqueModule = (ctx) => {
  wallPlaqueModule(ctx);
  for (const x of [-0.18, 0, 0.18]) {
    slab(ctx, "black-metal", { x0: x - 0.035, x1: x + 0.035, y0: ctx.height * 0.25, y1: ctx.height * 0.75, z0: 0.28, z1: 0.36 }, blackMetal);
  }
};
var flagMountModule = (ctx) => {
  solidBox(ctx, "bronze", [-0.08, 0.1, 0], [0.08, 0.36, 0.22], bronze);
  solidBox(ctx, "bronze", [0, 0.24, 0.16], [ctx.width * 0.5, 0.32, ctx.depth], bronze);
  slab(ctx, "ornament", { x0: ctx.width * 0.2, x1: ctx.width * 0.5, y0: 0.32, y1: ctx.height, z0: ctx.depth * 0.72, z1: ctx.depth }, stoneWarm);
};
var bollardModule = (ctx) => {
  profiledCylinder({ ctx, slot: "black-metal", x: 0, z: 0, y0: 0, y1: ctx.height, radius: ctx.width * 0.22, color: blackMetal, segments: 24 });
  profiledCylinder({ ctx, slot: "bronze", x: 0, z: 0, y0: ctx.height * 0.78, y1: ctx.height, radius: ctx.width * 0.26, color: bronze, segments: 24 });
};
var wallCameraModule = (ctx) => {
  solidBox(ctx, "black-metal", [-0.08, 0.1, 0], [0.08, ctx.height * 0.7, 0.24], blackMetal);
  solidBox(ctx, "black-metal", [-ctx.width * 0.35, ctx.height * 0.34, 0.18], [ctx.width * 0.35, ctx.height * 0.62, ctx.depth], blackMetal);
};
var wallLampModule = (ctx) => {
  solidBox(ctx, "bronze", [-0.05, 0, 0], [0.05, ctx.height * 0.68, 0.18], bronze);
  profiledCylinder({ ctx, slot: "glass", x: 0, z: ctx.depth * 0.55, y0: ctx.height * 0.45, y1: ctx.height, radius: ctx.width * 0.22, color: glass, segments: 20 });
};
var sidewalkEntryModule = (ctx) => {
  solidBox(ctx, "granite", [-ctx.width / 2, 0, -ctx.depth / 2], [ctx.width / 2, ctx.height * 0.45, ctx.depth / 2], granite);
  solidBox(ctx, "limestone", [-ctx.width * 0.42, ctx.height * 0.45, -ctx.depth * 0.28], [ctx.width * 0.42, ctx.height, ctx.depth * 0.48], stone);
};
function ionicCapital(ctx, x, y, scale) {
  slab(ctx, "limestone", { x0: x - scale, x1: x + scale, y0: y, y1: y + scale * 0.26, z0: -0.16, z1: 0.8 }, stoneWarm);
  for (const side of [-1, 1]) {
    rosette(ctx, x + side * scale * 0.55, y + scale * 0.28, 0.62, 0.88, scale * 0.32);
  }
}
function grilleBars(ctx, x0, x1, y0, y1, count) {
  for (let index = 0; index < count; index++) {
    const x = x0 + (x1 - x0) / Math.max(1, count - 1) * index;
    slab(ctx, "black-metal", { x0: x - 0.035, x1: x + 0.035, y0, y1, z0: 0.18, z1: 0.3 }, blackMetal);
  }
}

var serviceDoorModule = (ctx) => {
  frame(ctx, 0.42);
  bronzeDoor({ ctx, x0: -ctx.width * 0.23, x1: ctx.width * 0.23, y0: 0.35, y1: ctx.height - 0.85 });
  slab(ctx, "black-metal", { x0: -0.42, x1: 0.42, y0: ctx.height - 0.72, y1: ctx.height - 0.46, z0: -0.08, z1: 0.12 }, blackMetal);
};
var loadingDockBayModule = (ctx) => {
  frame(ctx, 0.52);
  bronzeDoor({ ctx, x0: -ctx.width * 0.34, x1: ctx.width * 0.34, y0: 0.36, y1: ctx.height - 0.7, shutter: true });
  solidBox(ctx, "bronze", [-ctx.width * 0.46, 0, 0.12], [-ctx.width * 0.38, 0.82, 0.28], bronze);
  solidBox(ctx, "bronze", [ctx.width * 0.38, 0, 0.12], [ctx.width * 0.46, 0.82, 0.28], bronze);
};
var granitePlinthModule = (ctx) => {
  solidBox(ctx, "granite", [-ctx.width / 2, 0, -ctx.depth / 2], [ctx.width / 2, ctx.height * 0.72, ctx.depth / 2], granite);
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: ctx.height * 0.72, y1: ctx.height, z0: -ctx.depth / 2, z1: ctx.depth / 2 + 0.08 }, stone);
};
function frame(ctx, jamb) {
  const x0 = -ctx.width / 2;
  const x1 = ctx.width / 2;
  slab(ctx, "limestone", { x0, x1: x0 + jamb, y0: 0, y1: ctx.height, z0: -0.1, z1: 0.64 }, stone);
  slab(ctx, "limestone", { x0: x1 - jamb, x1, y0: 0, y1: ctx.height, z0: -0.1, z1: 0.64 }, stone);
  slab(ctx, "limestone", { x0: x0 + jamb, x1: x1 - jamb, y0: ctx.height - 0.72, y1: ctx.height, z0: -0.1, z1: 0.64 }, stoneWarm);
  slab(ctx, "limestone", { x0, x1, y0: 0, y1: 0.32, z0: -0.1, z1: 0.42 }, stoneDark);
}

var baseModuleRuntimes = [
  { id: "round-column", builder: roundColumnModule, slots: ["limestone"] },
  { id: "square-column", builder: squareColumnModule, slots: ["limestone"] },
  { id: "paired-column", builder: pairedColumnModule, slots: ["limestone", "granite", "bronze"] },
  { id: "tall-lobby-window", builder: tallLobbyWindowModule, slots: ["limestone", "glass", "bronze", "ornament"] },
  { id: "lobby-door", builder: lobbyDoorModule, slots: ["limestone", "glass", "bronze", "ornament"] },
  { id: "revolving-door-bay", builder: revolvingDoorBayModule, slots: ["limestone", "glass", "bronze", "ornament"] },
  { id: "service-door", builder: serviceDoorModule, slots: ["limestone", "glass", "bronze", "black-metal"] },
  { id: "loading-dock-bay", builder: loadingDockBayModule, slots: ["limestone", "bronze", "black-metal"] },
  { id: "granite-plinth", builder: granitePlinthModule, slots: ["granite", "limestone"] },
  { id: "corner-entrance", builder: cornerEntranceModule, slots: ["limestone", "glass", "bronze", "ornament"] },
  { id: "colossal-column", builder: colossalColumnModule, slots: ["limestone", "granite", "ornament"] },
  { id: "square-corner-pylon", builder: squareCornerPylonModule, slots: ["limestone"] },
  { id: "triangular-pediment", builder: triangularPedimentModule, slots: ["limestone", "ornament"] },
  { id: "pediment-eagle", builder: pedimentEagleModule, slots: ["ornament"] },
  { id: "acroterion-scroll", builder: acroterionScrollModule, slots: ["limestone", "ornament"] },
  { id: "company-frieze", builder: companyFriezeModule, slots: ["limestone", "ornament"] },
  { id: "clock-medallion", builder: clockMedallionModule, slots: ["limestone", "bronze", "black-metal", "ornament"] },
  { id: "rusticated-base-block", builder: rusticatedBaseBlockModule, slots: ["limestone"] },
  { id: "bank-grille", builder: bankGrilleModule, slots: ["limestone", "glass", "bronze", "black-metal", "ornament"] },
  { id: "barred-window", builder: barredWindowModule, slots: ["limestone", "glass", "bronze", "black-metal", "ornament"] },
  { id: "storefront-curtain-wall", builder: storefrontCurtainWallModule, slots: ["glass", "black-metal", "bronze"] },
  { id: "security-door", builder: securityDoorModule, slots: ["limestone", "black-metal", "bronze"] },
  { id: "wall-plaque", builder: wallPlaqueModule, slots: ["bronze"] },
  { id: "address-plaque", builder: addressPlaqueModule, slots: ["bronze", "black-metal"] },
  { id: "flag-mount", builder: flagMountModule, slots: ["bronze", "ornament"] },
  { id: "bollard", builder: bollardModule, slots: ["black-metal", "bronze"] },
  { id: "wall-camera", builder: wallCameraModule, slots: ["black-metal"] },
  { id: "wall-lamp", builder: wallLampModule, slots: ["bronze", "glass"] },
  { id: "sidewalk-entry", builder: sidewalkEntryModule, slots: ["granite", "limestone"] }
];

var crownWindowBayModule = (ctx) => {
  framedWindow({ ctx, x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, side: 0.42, top: 0.48, bottom: 0.56, splits: 2 });
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.08, x1: ctx.width / 2 + 0.08, y0: ctx.height - 0.42, y1: ctx.height, z0: -0.08, z1: 0.58 }, stone);
};
var parapetSectionModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.42 }, stoneWarm);
  for (const x of [-ctx.width * 0.34, 0, ctx.width * 0.34]) {
    slab(ctx, "limestone", { x0: x - 0.12, x1: x + 0.12, y0: 0.18, y1: ctx.height - 0.22, z0: 0.42, z1: 0.58 }, stoneDark);
    rosette(ctx, x, ctx.height * 0.55, 0.58, 0.72, 0.22);
  }
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.12, x1: ctx.width / 2 + 0.12, y0: ctx.height - 0.22, y1: ctx.height, z0: -0.08, z1: 0.58 }, stone);
};
var cornerParapetModule = (ctx) => {
  parapetSectionModule(ctx);
  solidBox(ctx, "limestone", [ctx.width / 2 - 0.28, 0, -ctx.depth * 0.5], [ctx.width / 2 + 0.28, ctx.height, 0.52], stone);
  for (const z of [-ctx.depth * 0.38, 0.38]) {
    profiledCylinder({ ctx, slot: "limestone", x: ctx.width / 2, z, y0: ctx.height - 0.02, y1: ctx.height + 0.42, radius: 0.13, color: stone, segments: 20 });
  }
};

function louverBox(ctx, width, height, depth) {
  solidBox(ctx, "roof", [-width / 2, 0, -depth / 2], [width / 2, height, depth / 2], roofMetal);
  for (let index = 0; index < 7; index++) {
    const y = 0.35 + index * 0.18;
    slab(ctx, "black-metal", { x0: -width / 2 - 0.02, x1: width / 2 + 0.02, y0: y, y1: y + 0.045, z0: depth / 2 + 0.02, z1: depth / 2 + 0.08 }, blackMetal);
  }
}
function fanCylinder(ctx, x, z, radius, height) {
  profiledCylinder({ ctx, slot: "black-metal", x, z, y0: 0, y1: height, radius, color: blackMetal, segments: 28 });
  profiledCylinder({ ctx, slot: "roof", x, z, y0: height, y1: height + 0.16, radius: radius * 1.12, color: roofMetal, segments: 28 });
}
function railing(ctx, width, height) {
  for (let index = 0; index <= 6; index++) {
    const x = -width / 2 + width / 6 * index;
    solidBox(ctx, "bronze", [x - 0.035, 0, -0.035], [x + 0.035, height, 0.035], bronze);
  }
  for (const y of [height * 0.46, height * 0.9]) {
    solidBox(ctx, "bronze", [-width / 2, y - 0.03, -0.035], [width / 2, y + 0.03, 0.035], bronze);
  }
}

var roofMechBoxModule = (ctx) => {
  louverBox(ctx, ctx.width, ctx.height, ctx.depth);
};
var hvacClusterModule = (ctx) => {
  solidBox(ctx, "roof", [-ctx.width * 0.45, 0, -ctx.depth * 0.35], [-ctx.width * 0.1, ctx.height * 0.55, ctx.depth * 0.25], roofMetal);
  fanCylinder(ctx, ctx.width * 0.16, -ctx.depth * 0.2, 0.45, ctx.height * 0.62);
  fanCylinder(ctx, ctx.width * 0.36, ctx.depth * 0.18, 0.36, ctx.height * 0.48);
  solidBox(ctx, "black-metal", [-ctx.width * 0.38, ctx.height * 0.16, ctx.depth * 0.28], [-ctx.width * 0.08, ctx.height * 0.42, ctx.depth * 0.36], blackMetal);
};
var roofRailingModule = (ctx) => {
  railing(ctx, ctx.width, ctx.height);
};
var antennaModule = (ctx) => {
  profiledCylinder({ ctx, slot: "black-metal", x: 0, z: 0, y0: 0, y1: ctx.height, radius: 0.035, color: blackMetal, segments: 14 });
  for (const y of [0.7, 1.5, 2.4, 3.3]) {
    profiledCylinder({ ctx, slot: "bronze", x: 0, z: 0, y0: y, y1: y + 0.08, radius: 0.16, color: bronze, segments: 16 });
  }
  solidBox(ctx, "black-metal", [-0.25, 1.1, -0.025], [0.25, 1.16, 0.025], blackMetal);
  solidBox(ctx, "black-metal", [-0.18, 2.1, -0.025], [0.18, 2.16, 0.025], blackMetal);
};

var slopedMetalRoofModule = (ctx) => {
  const x0 = -ctx.width / 2;
  const x1 = ctx.width / 2;
  const z0 = -ctx.depth / 2;
  const z1 = ctx.depth / 2;
  const ridge = [0, ctx.height, 0];
  roofTriangle(ctx, [x0, 0, z1], [x1, 0, z1], ridge);
  roofTriangle(ctx, [x1, 0, z0], [x0, 0, z0], ridge);
  roofTriangle(ctx, [x1, 0, z1], [x1, 0, z0], ridge);
  roofTriangle(ctx, [x0, 0, z0], [x0, 0, z1], ridge);
  for (let index = -5; index <= 5; index++) {
    if (index === 0) continue;
    const x = ctx.width / 12 * index;
    roofSeam(ctx, [x, 0.04, z1], ridge, 0.035);
    roofSeam(ctx, [x, 0.04, z0], ridge, 0.035);
  }
  for (let index = -3; index <= 3; index++) {
    if (index === 0) continue;
    const z = ctx.depth / 8 * index;
    roofSeam(ctx, [x1, 0.04, z], ridge, 0.035);
    roofSeam(ctx, [x0, 0.04, z], ridge, 0.035);
  }
  solidBox(ctx, "roof", [-0.08, ctx.height * 0.95, -0.18], [0.08, ctx.height + 0.12, 0.18], roofMetal);
};
var roofLanternModule = (ctx) => {
  solidBox(ctx, "black-metal", [-ctx.width / 2, 0, -ctx.depth / 2], [ctx.width / 2, 0.12, ctx.depth / 2], blackMetal);
  for (const x of [-ctx.width * 0.42, ctx.width * 0.42]) {
    for (const z of [-ctx.depth * 0.42, ctx.depth * 0.42]) {
      solidBox(ctx, "black-metal", [x - 0.05, 0, z - 0.05], [x + 0.05, ctx.height, z + 0.05], blackMetal);
    }
  }
  solidBox(ctx, "black-metal", [-ctx.width / 2, ctx.height - 0.12, -ctx.depth / 2], [ctx.width / 2, ctx.height, ctx.depth / 2], blackMetal);
};
var roofStatueMastModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width * 0.32, 0, -ctx.depth * 0.32], [ctx.width * 0.32, ctx.height * 0.14, ctx.depth * 0.32], stoneDark);
  profiledCylinder({ ctx, slot: "limestone", x: 0, z: 0, y0: ctx.height * 0.14, y1: ctx.height * 0.88, radius: ctx.width * 0.12, color: stone, segments: 32, flutes: 8 });
  for (const x of [-ctx.width * 0.18, ctx.width * 0.18]) {
    solidBox(ctx, "limestone", [x - 0.08, ctx.height * 0.28, -0.05], [x + 0.08, ctx.height * 0.86, 0.05], stone);
  }
  profiledCylinder({ ctx, slot: "bronze", x: 0, z: 0, y0: ctx.height * 0.88, y1: ctx.height, radius: ctx.width * 0.16, color: bronze, segments: 24 });
};
var roofCrestModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width * 0.35, 0, -ctx.depth * 0.3], [ctx.width * 0.35, ctx.height * 0.2, ctx.depth * 0.3], stoneDark);
  profiledCylinder({ ctx, slot: "bronze", x: 0, z: 0, y0: ctx.height * 0.2, y1: ctx.height, radius: 0.04, color: bronze, segments: 12 });
  slab(ctx, "ornament", { x0: 0.04, x1: ctx.width * 0.48, y0: ctx.height * 0.56, y1: ctx.height * 0.82, z0: 0, z1: ctx.depth * 0.18 }, stone);
};
function roofTriangle(ctx, a, b, c) {
  ctx.writer.appendQuad("roof", [
    ctx.transform(a),
    ctx.transform(b),
    ctx.transform(c),
    ctx.transform(c)
  ], roofMetal);
}
function roofSeam(ctx, a, b, halfWidth) {
  const dx = b[0] - a[0];
  const dz = b[2] - a[2];
  const length = Math.hypot(dx, dz) || 1;
  const nx = -dz / length * halfWidth;
  const nz = dx / length * halfWidth;
  ctx.writer.appendQuad("roof", [
    ctx.transform([a[0] - nx, a[1], a[2] - nz]),
    ctx.transform([a[0] + nx, a[1], a[2] + nz]),
    ctx.transform([b[0] + nx * 0.18, b[1] + 0.04, b[2] + nz * 0.18]),
    ctx.transform([b[0] - nx * 0.18, b[1] + 0.04, b[2] - nz * 0.18])
  ], roofMetal);
}

var atticCrestPanelModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height * 0.48, z0: -0.08, z1: 0.42 }, stoneWarm);
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.12, x1: ctx.width / 2 + 0.12, y0: ctx.height * 0.48, y1: ctx.height, z0: -0.08, z1: 0.62 }, stone);
  dentils(ctx, -ctx.width / 2 + 0.2, ctx.width / 2 - 0.2, ctx.height * 0.12, ctx.height * 0.28, 0.42, 0.62, Math.max(5, Math.floor(ctx.width * 1.2)));
  for (const x of [-ctx.width * 0.28, 0, ctx.width * 0.28]) {
    rosette(ctx, x, ctx.height * 0.64, 0.62, 0.78, 0.18);
  }
};
var crownPedimentModule = (ctx) => {
  const w = ctx.width / 2;
  solidBox(ctx, "limestone", [-w, 0, -0.08], [w, ctx.height * 0.42, 0.62], stoneWarm);
  solidBox(ctx, "limestone", [-w * 0.72, ctx.height * 0.42, -0.08], [w * 0.72, ctx.height * 0.72, 0.72], stone);
  solidBox(ctx, "limestone", [-w * 0.42, ctx.height * 0.72, -0.08], [w * 0.42, ctx.height, 0.86], stone);
  slab(ctx, "ornament", { x0: -w * 0.46, x1: w * 0.46, y0: ctx.height * 0.14, y1: ctx.height * 0.36, z0: 0.62, z1: 0.82 }, stoneDark);
  rosette(ctx, 0, ctx.height * 0.56, 0.72, 0.94, 0.28);
};
var cornerFinialModule = (ctx) => {
  solidBox(ctx, "limestone", [-0.28, 0, -0.28], [0.28, ctx.height * 0.18, 0.28], stoneDark);
  profiledCylinder({ ctx, slot: "limestone", x: 0, z: 0, y0: ctx.height * 0.18, y1: ctx.height * 0.72, radius: 0.22, color: stone, segments: 28, flutes: 8 });
  profiledCylinder({ ctx, slot: "limestone", x: 0, z: 0, y0: ctx.height * 0.72, y1: ctx.height, radius: 0.11, color: stoneWarm, segments: 24 });
};
var crownUrnFinialModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width * 0.28, 0, -ctx.depth * 0.28], [ctx.width * 0.28, ctx.height * 0.18, ctx.depth * 0.28], stoneDark);
  profiledCylinder({ ctx, slot: "limestone", x: 0, z: 0, y0: ctx.height * 0.18, y1: ctx.height * 0.62, radius: ctx.width * 0.25, color: stone, segments: 28 });
  profiledCylinder({ ctx, slot: "limestone", x: 0, z: 0, y0: ctx.height * 0.62, y1: ctx.height * 0.84, radius: ctx.width * 0.16, color: stoneWarm, segments: 24 });
  solidBox(ctx, "limestone", [-ctx.width * 0.2, ctx.height * 0.84, -ctx.depth * 0.2], [ctx.width * 0.2, ctx.height, ctx.depth * 0.2], stoneWarm);
};
var crownObeliskFinialModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width * 0.34, 0, -ctx.depth * 0.34], [ctx.width * 0.34, ctx.height * 0.18, ctx.depth * 0.34], stoneDark);
  solidBox(ctx, "limestone", [-ctx.width * 0.22, ctx.height * 0.18, -ctx.depth * 0.22], [ctx.width * 0.22, ctx.height * 0.74, ctx.depth * 0.22], stone);
  solidBox(ctx, "limestone", [-ctx.width * 0.1, ctx.height * 0.74, -ctx.depth * 0.1], [ctx.width * 0.1, ctx.height, ctx.depth * 0.1], stoneWarm);
};
var crownPillarFinialModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width * 0.32, 0, -ctx.depth * 0.32], [ctx.width * 0.32, ctx.height * 0.18, ctx.depth * 0.32], stoneDark);
  solidBox(ctx, "limestone", [-ctx.width * 0.22, ctx.height * 0.18, -ctx.depth * 0.22], [ctx.width * 0.22, ctx.height * 0.76, ctx.depth * 0.22], stone);
  solidBox(ctx, "limestone", [-ctx.width * 0.36, ctx.height * 0.76, -ctx.depth * 0.3], [ctx.width * 0.36, ctx.height * 0.9, ctx.depth * 0.3], stoneWarm);
  solidBox(ctx, "limestone", [-ctx.width * 0.18, ctx.height * 0.9, -ctx.depth * 0.18], [ctx.width * 0.18, ctx.height, ctx.depth * 0.18], stoneWarm);
};
var crownCartouchePanelModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.46 }, stoneWarm);
  slab(ctx, "ornament", { x0: -ctx.width * 0.34, x1: ctx.width * 0.34, y0: ctx.height * 0.2, y1: ctx.height * 0.78, z0: 0.46, z1: 0.66 }, stoneDark);
  rosette(ctx, 0, ctx.height * 0.52, 0.66, 0.86, Math.min(ctx.width, ctx.height) * 0.2);
};

var crownRoofRuntimes = [
  { id: "crown-window-bay", builder: crownWindowBayModule, slots: ["limestone", "glass", "bronze"] },
  { id: "parapet-section", builder: parapetSectionModule, slots: ["limestone", "ornament"] },
  { id: "corner-parapet", builder: cornerParapetModule, slots: ["limestone", "ornament"] },
  { id: "attic-crest-panel", builder: atticCrestPanelModule, slots: ["limestone", "ornament"] },
  { id: "crown-pediment", builder: crownPedimentModule, slots: ["limestone", "ornament"] },
  { id: "corner-finial", builder: cornerFinialModule, slots: ["limestone"] },
  { id: "crown-urn-finial", builder: crownUrnFinialModule, slots: ["limestone"] },
  { id: "crown-obelisk-finial", builder: crownObeliskFinialModule, slots: ["limestone"] },
  { id: "crown-pillar-finial", builder: crownPillarFinialModule, slots: ["limestone"] },
  { id: "crown-cartouche-panel", builder: crownCartouchePanelModule, slots: ["limestone", "ornament"] },
  { id: "sloped-metal-roof", builder: slopedMetalRoofModule, slots: ["roof"] },
  { id: "roof-statue-mast", builder: roofStatueMastModule, slots: ["limestone", "bronze"] },
  { id: "roof-lantern", builder: roofLanternModule, slots: ["black-metal"] },
  { id: "roof-crest", builder: roofCrestModule, slots: ["limestone", "bronze", "ornament"] },
  { id: "roof-mech-box", builder: roofMechBoxModule, slots: ["roof", "black-metal"] },
  { id: "hvac-cluster", builder: hvacClusterModule, slots: ["roof", "black-metal"] },
  { id: "roof-railing", builder: roofRailingModule, slots: ["bronze"] },
  { id: "antenna", builder: antennaModule, slots: ["black-metal", "bronze"] }
];

var window3mModule = (ctx) => {
  shaftFrame(ctx, 0.32);
  framedWindow({ ctx, x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, side: 0.32, top: 0.32, bottom: 0.74, splits: 2, spandrel: true });
};
var window4mModule = (ctx) => {
  shaftFrame(ctx, 0.34);
  framedWindow({ ctx, x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, side: 0.3, top: 0.32, bottom: 0.76, splits: 3, spandrel: true });
};
var doubleWindowBayModule = (ctx) => {
  shaftFrame(ctx, 0.3);
  const gap = 0.18;
  framedWindow({ ctx, x0: -ctx.width / 2, x1: -gap, y0: 0, y1: ctx.height, side: 0.24, top: 0.32, bottom: 0.78, splits: 2, spandrel: false });
  framedWindow({ ctx, x0: gap, x1: ctx.width / 2, y0: 0, y1: ctx.height, side: 0.24, top: 0.32, bottom: 0.78, splits: 2, spandrel: false });
  slab(ctx, "limestone", { x0: -gap, x1: gap, y0: 0.16, y1: ctx.height - 0.16, z0: -0.08, z1: 0.3 }, stone);
  for (const x of [-ctx.width * 0.23, ctx.width * 0.23]) {
    rosette(ctx, x, 0.46, 0.16, 0.3, 0.32);
  }
};
function shaftFrame(ctx, pier) {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: -ctx.width / 2 + pier, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.28 }, stoneDark);
  slab(ctx, "limestone", { x0: ctx.width / 2 - pier, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.28 }, stoneDark);
}

var blankBayModule = (ctx) => {
  panelGrid(ctx, -ctx.width / 2, ctx.width / 2, 0, ctx.height);
  slab(ctx, "limestone", { x0: -ctx.width / 2 + 0.34, x1: ctx.width / 2 - 0.34, y0: 0.38, y1: ctx.height - 0.38, z0: -0.06, z1: 0.18 }, stoneWarm);
};
var cornerBayModule = (ctx) => {
  window3mModule(ctx);
  slab(ctx, "limestone", { x0: ctx.width / 2 - 0.22, x1: ctx.width / 2 + 0.22, y0: 0, y1: ctx.height, z0: -ctx.depth * 0.5, z1: 0.42 }, stone);
};
var verticalPilasterStripModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.42 }, stone);
  for (const x of [-0.18, 0, 0.18]) {
    slab(ctx, "limestone", { x0: x - 0.025, x1: x + 0.025, y0: 0.34, y1: ctx.height - 0.34, z0: 0.42, z1: 0.54 }, stoneDark);
  }
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.08, x1: ctx.width / 2 + 0.08, y0: 0, y1: 0.26, z0: -0.1, z1: 0.5 }, stoneWarm);
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.08, x1: ctx.width / 2 + 0.08, y0: ctx.height - 0.34, y1: ctx.height, z0: -0.1, z1: 0.5 }, stoneWarm);
};
var spandrelPanelModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.2 }, stoneWarm);
  slab(ctx, "ornament", { x0: -ctx.width / 2 + 0.25, x1: ctx.width / 2 - 0.25, y0: 0.16, y1: ctx.height - 0.16, z0: 0.2, z1: 0.36 }, stone);
  rosette(ctx, 0, ctx.height / 2, 0.36, 0.5, Math.min(ctx.width, ctx.height) * 0.32);
};
var floorBandStripModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.26 }, stone);
  greekKey(ctx, -ctx.width / 2 + 0.15, ctx.width / 2 - 0.15, ctx.height * 0.22, 0.26, 0.44, Math.max(3, Math.floor(ctx.width)));
};
function panelGrid(ctx, x0, x1, y0, y1) {
  slab(ctx, "limestone", { x0, x1, y0, y1, z0: -0.08, z1: 0.12 }, stone);
  const midX = (x0 + x1) / 2;
  const midY = (y0 + y1) / 2;
  slab(ctx, "limestone", { x0: midX - 0.025, x1: midX + 0.025, y0: y0 + 0.18, y1: y1 - 0.18, z0: 0.12, z1: 0.22 }, stoneDark);
  slab(ctx, "limestone", { x0: x0 + 0.18, x1: x1 - 0.18, y0: midY - 0.025, y1: midY + 0.025, z0: 0.12, z1: 0.22 }, stoneDark);
}

var centralGlassShaftModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: -ctx.width * 0.36, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.5 }, stoneDark);
  slab(ctx, "limestone", { x0: ctx.width * 0.36, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.5 }, stoneDark);
  slab(ctx, "black-metal", { x0: -ctx.width * 0.34, x1: ctx.width * 0.34, y0: 0.12, y1: ctx.height - 0.12, z0: -0.04, z1: 0.12 }, blackMetal);
  const floors = Math.max(3, Math.floor(ctx.height / 3.35));
  for (let floor = 0; floor < floors; floor++) {
    const y0 = floor * (ctx.height / floors) + 0.18;
    const y1 = (floor + 1) * (ctx.height / floors) - 0.18;
    slab(ctx, "glass", { x0: -ctx.width * 0.28, x1: ctx.width * 0.28, y0, y1, z0: 0.12, z1: 0.2 }, glass);
    slab(ctx, "bronze", { x0: -ctx.width * 0.28, x1: ctx.width * 0.28, y0: y1 - 0.035, y1: y1 + 0.035, z0: 0.2, z1: 0.32 }, bronze);
  }
};
var solidSidePierModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width / 2, 0, -0.1], [ctx.width / 2, ctx.height, 0.56], stone);
  slab(ctx, "limestone", { x0: -ctx.width / 2 + 0.14, x1: ctx.width / 2 - 0.14, y0: 0.3, y1: ctx.height - 0.3, z0: 0.56, z1: 0.7 }, stoneDark);
};
var buttressPierModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width / 2, 0, -0.1], [ctx.width / 2, ctx.height, 0.72], stone);
  for (let index = 0; index < 4; index++) {
    const y = ctx.height / 4 * index;
    slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.08, x1: ctx.width / 2 + 0.08, y0: y, y1: y + 0.26, z0: -0.1, z1: 0.9 }, stoneWarm);
  }
};
var pilasterBundleModule = (ctx) => {
  for (const x of [-0.32, 0, 0.32]) {
    slab(ctx, "limestone", { x0: x - 0.12, x1: x + 0.12, y0: 0, y1: ctx.height, z0: -0.06, z1: 0.58 }, stone);
    slab(ctx, "limestone", { x0: x - 0.035, x1: x + 0.035, y0: 0.42, y1: ctx.height - 0.42, z0: 0.58, z1: 0.72 }, stoneDark);
  }
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: ctx.height - 0.45, y1: ctx.height, z0: -0.08, z1: 0.78 }, stoneWarm);
};
var recessedWindowSlotModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.12, z1: 0.68 }, stoneDark);
  slab(ctx, "black-metal", { x0: -ctx.width * 0.28, x1: ctx.width * 0.28, y0: 0.25, y1: ctx.height - 0.25, z0: -0.04, z1: 0.08 }, blackMetal);
  const panes = Math.max(3, Math.floor(ctx.height / 1.65));
  for (let index = 0; index < panes; index++) {
    const y0 = 0.35 + index * ((ctx.height - 0.7) / panes);
    const y1 = 0.35 + (index + 0.72) * ((ctx.height - 0.7) / panes);
    slab(ctx, "glass", { x0: -ctx.width * 0.2, x1: ctx.width * 0.2, y0, y1, z0: 0.08, z1: 0.18 }, glass);
  }
};
var archedWindowBayModule = (ctx) => {
  archedOpening({ ctx, x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, depth: 0.72 });
};
var arcadeBayModule = (ctx) => {
  archedOpening({ ctx, x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, depth: 0.94 });
  for (const x of [-ctx.width * 0.42, ctx.width * 0.42]) {
    slab(ctx, "terra-cotta", { x0: x - 0.12, x1: x + 0.12, y0: 0, y1: ctx.height, z0: 0.66, z1: 0.94 }, stoneWarm);
  }
};
var brickWindowBayModule = (ctx) => {
  solidBox(ctx, "terra-cotta", [-ctx.width / 2, 0, -0.08], [ctx.width / 2, ctx.height, 0.32], [1, 1, 1]);
  brickCourses(ctx);
  framedWindow({ ctx, x0: -ctx.width * 0.32, x1: ctx.width * 0.32, y0: 0.32, y1: ctx.height - 0.28, side: 0.18, top: 0.24, bottom: 0.42, splits: 2 });
};
var deepWindowWellModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.18, z1: 0.82 }, stone);
  framedWindow({ ctx, x0: -ctx.width * 0.34, x1: ctx.width * 0.34, y0: 0.28, y1: ctx.height - 0.26, side: 0.22, top: 0.28, bottom: 0.54, splits: 2 });
  slab(ctx, "limestone", { x0: -ctx.width * 0.44, x1: ctx.width * 0.44, y0: 0.02, y1: 0.34, z0: 0.82, z1: 1.06 }, stoneWarm);
  slab(ctx, "limestone", { x0: -ctx.width * 0.44, x1: ctx.width * 0.44, y0: ctx.height - 0.42, y1: ctx.height, z0: 0.82, z1: 1.08 }, stoneWarm);
};
var carvedSpandrelVineModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.06, z1: 0.24 }, stoneWarm);
  greekKey(ctx, -ctx.width / 2 + 0.15, ctx.width / 2 - 0.15, ctx.height * 0.16, 0.24, 0.42, Math.max(4, Math.floor(ctx.width)));
  for (const x of [-ctx.width * 0.25, 0, ctx.width * 0.25]) {
    rosette(ctx, x, ctx.height * 0.58, 0.42, 0.6, 0.22);
  }
};
var wrappedCornerPierModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width / 2, 0, -ctx.depth / 2], [ctx.width / 2, ctx.height, 0.62], stone);
  solidBox(ctx, "limestone", [ctx.width / 2 - 0.28, 0, -ctx.depth / 2], [ctx.width / 2 + 0.32, ctx.height, ctx.depth / 2], stone);
};
var roundedCornerPierModule = (ctx) => {
  const x0 = -ctx.width / 2;
  const x1 = ctx.width / 2;
  const chamfer = Math.min(ctx.width * 0.28, 0.62);
  const variant = ctx.moduleVariant ?? "both";
  const bevelStart = variant === "start" || variant === "both";
  const bevelEnd = variant === "end" || variant === "both";
  const flatX0 = bevelStart ? x0 + chamfer : x0;
  const flatX1 = bevelEnd ? x1 - chamfer : x1;
  solidBox(ctx, "limestone", [flatX0, 0, -0.34], [flatX1, ctx.height, 0.48], stone);
  if (bevelStart) {
    solidBox(ctx, "limestone", [x0, 0, -0.34], [x0 + chamfer * 0.25, ctx.height, 0.1], stone);
    chamferFace(ctx, x0 + chamfer * 0.25, x0 + chamfer, 0.1, 0.48);
  }
  if (bevelEnd) {
    solidBox(ctx, "limestone", [x1 - chamfer * 0.25, 0, -0.34], [x1, ctx.height, 0.1], stone);
    chamferFace(ctx, x1 - chamfer, x1 - chamfer * 0.25, 0.48, 0.1);
  }
  for (let index = 0; index < 5; index++) {
    const y = ctx.height / 5 * index;
    slab(ctx, "limestone", { x0: flatX0 - 0.04, x1: flatX1 + 0.04, y0: y, y1: y + 0.18, z0: -0.34, z1: 0.6 }, stoneWarm);
  }
};
var structuralBlankWallModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width / 2, 0, -0.08], [ctx.width / 2, ctx.height, 0.34], stoneWarm);
  const rows = Math.max(5, Math.floor(ctx.height / 1.2));
  for (let index = 1; index < rows; index++) {
    const y = ctx.height / rows * index;
    slab(ctx, "limestone", { x0: -ctx.width / 2 + 0.08, x1: ctx.width / 2 - 0.08, y0: y - 0.02, y1: y + 0.02, z0: 0.34, z1: 0.44 }, stoneDark);
  }
};
function chamferFace(ctx, x0, x1, z0, z1) {
  ctx.writer.appendQuad("limestone", [
    ctx.transform([x0, 0, z0]),
    ctx.transform([x1, 0, z1]),
    ctx.transform([x1, ctx.height, z1]),
    ctx.transform([x0, ctx.height, z0])
  ], stone);
}
function brickCourses(ctx) {
  const rows = Math.max(8, Math.floor(ctx.height / 0.28));
  for (let row = 1; row < rows; row++) {
    const y = ctx.height / rows * row;
    slab(ctx, "terra-cotta", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: y - 0.01, y1: y + 0.01, z0: 0.32, z1: 0.42 }, stoneDark);
  }
}

var shaftModuleRuntimes = [
  { id: "window-3m", builder: window3mModule, slots: ["limestone", "glass", "bronze", "ornament"] },
  { id: "window-4m", builder: window4mModule, slots: ["limestone", "glass", "bronze", "ornament"] },
  { id: "double-window-bay", builder: doubleWindowBayModule, slots: ["limestone", "glass", "bronze", "ornament"] },
  { id: "blank-bay", builder: blankBayModule, slots: ["limestone"] },
  { id: "corner-bay", builder: cornerBayModule, slots: ["limestone", "glass", "bronze", "ornament"] },
  { id: "vertical-pilaster-strip", builder: verticalPilasterStripModule, slots: ["limestone"] },
  { id: "spandrel-panel", builder: spandrelPanelModule, slots: ["limestone", "ornament"] },
  { id: "floor-band-strip", builder: floorBandStripModule, slots: ["limestone", "ornament"] },
  { id: "central-glass-shaft", builder: centralGlassShaftModule, slots: ["limestone", "glass", "bronze", "black-metal"] },
  { id: "solid-side-pier", builder: solidSidePierModule, slots: ["limestone"] },
  { id: "buttress-pier", builder: buttressPierModule, slots: ["limestone"] },
  { id: "pilaster-bundle", builder: pilasterBundleModule, slots: ["limestone"] },
  { id: "recessed-window-slot", builder: recessedWindowSlotModule, slots: ["limestone", "glass", "black-metal"] },
  { id: "arched-window-bay", builder: archedWindowBayModule, slots: ["limestone", "glass", "bronze", "black-metal"] },
  { id: "arcade-bay", builder: arcadeBayModule, slots: ["limestone", "terra-cotta", "glass", "bronze", "black-metal"] },
  { id: "brick-window-bay", builder: brickWindowBayModule, slots: ["terra-cotta", "limestone", "glass", "bronze", "ornament"] },
  { id: "deep-window-well", builder: deepWindowWellModule, slots: ["limestone", "glass", "bronze", "ornament"] },
  { id: "carved-spandrel-vine", builder: carvedSpandrelVineModule, slots: ["limestone", "ornament"] },
  { id: "wrapped-corner-pier", builder: wrappedCornerPierModule, slots: ["limestone"] },
  { id: "rounded-corner-pier", builder: roundedCornerPierModule, slots: ["limestone"] },
  { id: "structural-blank-wall", builder: structuralBlankWallModule, slots: ["limestone"] }
];

var smallCorniceModule = (ctx) => {
  cornice(ctx, 0.55, 0.28);
};
var largeCorniceModule = (ctx) => {
  cornice(ctx, 0.82, 0.42);
  dentils(ctx, -ctx.width / 2 + 0.2, ctx.width / 2 - 0.2, 0.1, 0.32, 0.62, 0.9, Math.max(5, Math.floor(ctx.width * 1.4)));
  for (const x of [-ctx.width * 0.3, 0, ctx.width * 0.3]) {
    rosette(ctx, x, ctx.height * 0.5, 0.72, 0.95, 0.22);
  }
};
var cornerCorniceModule = (ctx) => {
  largeCorniceModule(ctx);
  solidBox(ctx, "limestone", [ctx.width / 2 - 0.24, 0, -ctx.depth * 0.65], [ctx.width / 2 + 0.26, ctx.height, 0.82], stone);
  slab(ctx, "ornament", { x0: ctx.width / 2 - 0.18, x1: ctx.width / 2 + 0.18, y0: 0.18, y1: ctx.height - 0.18, z0: -ctx.depth * 0.55, z1: -ctx.depth * 0.12 }, stoneWarm);
};
var beltCornerJointModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width / 2, 0, -ctx.depth / 2], [ctx.width / 2, ctx.height, ctx.depth / 2], stoneWarm);
  solidBox(ctx, "limestone", [-ctx.width / 2 - 0.08, ctx.height * 0.58, -ctx.depth / 2 - 0.08], [ctx.width / 2 + 0.08, ctx.height, ctx.depth / 2 + 0.08], stone);
};
var corniceCornerJointModule = (ctx) => {
  solidBox(ctx, "limestone", [-ctx.width / 2, 0, -ctx.depth / 2], [ctx.width / 2, ctx.height * 0.34, ctx.depth / 2], stoneWarm);
  solidBox(ctx, "limestone", [-ctx.width / 2 - 0.14, ctx.height * 0.34, -ctx.depth / 2 - 0.14], [ctx.width / 2 + 0.14, ctx.height * 0.74, ctx.depth / 2 + 0.14], stone);
  solidBox(ctx, "limestone", [-ctx.width / 2 - 0.24, ctx.height * 0.74, -ctx.depth / 2 - 0.24], [ctx.width / 2 + 0.24, ctx.height, ctx.depth / 2 + 0.24], stone);
};
function cornice(ctx, projection, friezeDepth) {
  const back = -Math.max(0.08, ctx.depth * 0.45);
  const front = Math.max(projection, ctx.depth * 0.55);
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height * 0.34, z0: back, z1: front * 0.7 }, stoneWarm);
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.12, x1: ctx.width / 2 + 0.12, y0: ctx.height * 0.34, y1: ctx.height * 0.72, z0: back, z1: front }, stone);
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.18, x1: ctx.width / 2 + 0.18, y0: ctx.height * 0.72, y1: ctx.height, z0: back, z1: front + friezeDepth }, stone);
}

var beltCourseSmallModule = (ctx) => {
  bead(ctx, 0, ctx.height, 0.32);
};
var beltCourseLargeModule = (ctx) => {
  bead(ctx, 0, ctx.height, 0.48);
  slab(ctx, "ornament", { x0: -ctx.width / 2 + 0.16, x1: ctx.width / 2 - 0.16, y0: ctx.height * 0.34, y1: ctx.height * 0.76, z0: 0.26, z1: 0.48 }, stoneWarm);
  dentils(ctx, -ctx.width / 2 + 0.2, ctx.width / 2 - 0.2, ctx.height * 0.08, ctx.height * 0.24, 0.42, 0.66, Math.max(6, Math.floor(ctx.width * 1.5)));
};
var windowSillStripModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: ctx.height * 0.32, y1: ctx.height, z0: -0.08, z1: 0.46 }, stone);
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.1, x1: ctx.width / 2 + 0.1, y0: 0, y1: ctx.height * 0.34, z0: -0.08, z1: 0.6 }, stoneWarm);
};
var lintelStripModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.42 }, stone);
  for (let index = 1; index < Math.max(2, Math.floor(ctx.width)); index++) {
    const x = -ctx.width / 2 + ctx.width / Math.floor(ctx.width) * index;
    slab(ctx, "limestone", { x0: x - 0.025, x1: x + 0.025, y0: 0.08, y1: ctx.height - 0.08, z0: 0.42, z1: 0.5 }, stoneDark);
  }
};
var floorBandStripModule2 = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: 0, y1: ctx.height, z0: -0.08, z1: 0.32 }, stone);
  greekKey(ctx, -ctx.width / 2 + 0.18, ctx.width / 2 - 0.18, ctx.height * 0.2, 0.32, 0.54, Math.max(4, Math.floor(ctx.width * 1.25)));
};
var dentilCorbelCourseModule = (ctx) => {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0: ctx.height * 0.36, y1: ctx.height, z0: -0.08, z1: 0.62 }, stone);
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.1, x1: ctx.width / 2 + 0.1, y0: 0, y1: ctx.height * 0.28, z0: -0.08, z1: 0.8 }, stoneWarm);
  const count = Math.max(4, Math.floor(ctx.width * 1.2));
  dentils(ctx, -ctx.width / 2 + 0.16, ctx.width / 2 - 0.16, ctx.height * 0.1, ctx.height * 0.36, 0.62, 0.92, count);
};
function bead(ctx, y0, y1, z) {
  slab(ctx, "limestone", { x0: -ctx.width / 2, x1: ctx.width / 2, y0, y1, z0: -0.08, z1: z }, stone);
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.08, x1: ctx.width / 2 + 0.08, y0, y1: y0 + 0.12, z0: -0.08, z1: z + 0.14 }, stoneWarm);
  slab(ctx, "limestone", { x0: -ctx.width / 2 - 0.08, x1: ctx.width / 2 + 0.08, y0: y1 - 0.12, y1, z0: -0.08, z1: z + 0.14 }, stoneWarm);
}

var trimCorniceRuntimes = [
  { id: "belt-course-small", builder: beltCourseSmallModule, slots: ["limestone"] },
  { id: "belt-course-large", builder: beltCourseLargeModule, slots: ["limestone", "ornament"] },
  { id: "window-sill-strip", builder: windowSillStripModule, slots: ["limestone"] },
  { id: "lintel-strip", builder: lintelStripModule, slots: ["limestone"] },
  { id: "floor-band-strip", builder: floorBandStripModule2, slots: ["limestone", "ornament"] },
  { id: "small-cornice", builder: smallCorniceModule, slots: ["limestone", "ornament"] },
  { id: "large-cornice", builder: largeCorniceModule, slots: ["limestone", "ornament"] },
  { id: "corner-cornice", builder: cornerCorniceModule, slots: ["limestone", "ornament"] },
  { id: "belt-corner-joint", builder: beltCornerJointModule, slots: ["limestone"] },
  { id: "cornice-corner-joint", builder: corniceCornerJointModule, slots: ["limestone"] },
  { id: "dentil-corbel-course", builder: dentilCorbelCourseModule, slots: ["limestone", "ornament"] }
];

var runtimes = [
  ...baseModuleRuntimes,
  ...shaftModuleRuntimes,
  ...trimCorniceRuntimes,
  ...crownRoofRuntimes
];
var kitModuleRuntimeById = new Map(
  runtimes.map((runtime) => [runtime.id, runtime])
);
function getKitModuleRuntime(id) {
  const runtime = kitModuleRuntimeById.get(id);
  if (!runtime) throw new Error(`Missing financial core module builder: ${id}`);
  return runtime;
}
function missingKitModuleIds() {
  return financialCoreModules.map((module2) => module2.id).filter((id) => !kitModuleRuntimeById.has(id));
}
function assertCompleteKitRegistry() {
  const missing = missingKitModuleIds();
  if (missing.length > 0) {
    throw new Error(`Financial core kit is missing module builders: ${missing.join(", ")}`);
  }
}

function assertGeneratorInvariants(placements) {
  const missing = missingKitModuleIds();
  if (missing.length > 0) {
    throw new Error(`Financial core kit is missing module builders: ${missing.join(", ")}`);
  }
  const duplicates = duplicateSurfaceOwners(placements);
  if (duplicates.length > 0) {
    throw new Error(`Duplicate facade surface owner regions: ${duplicates.join(", ")}`);
  }
}
function duplicateSurfaceOwners(placements) {
  const owners = /* @__PURE__ */ new Set();
  const duplicates = /* @__PURE__ */ new Set();
  for (const placement of placements) {
    if (placement.side === "roof") continue;
    const key = surfaceKey(placement);
    if (owners.has(key)) duplicates.add(key);
    owners.add(key);
  }
  return [...duplicates];
}
function unusedModuleIds(placements) {
  const used = new Set(placements.map((placement) => placement.id));
  return financialCoreModules.map((module2) => module2.id).filter((id) => !used.has(id));
}
function surfaceKey(placement) {
  return [
    placement.side,
    placement.tierName,
    placement.edgeId ?? "whole-side",
    rounded(placement.xOffset ?? 0),
    rounded(placement.zOffset ?? 0),
    rounded(placement.center - placement.width / 2),
    rounded(placement.center + placement.width / 2),
    rounded(placement.y),
    rounded(placement.y + placement.height),
    rounded(placement.normalOffset ?? 0)
  ].join(":");
}
function rounded(value) {
  return Math.round(value * 100) / 100;
}

function createFinancialBuildingPlan(settings) {
  const tiers = createMassTiers(settings);
  const placements = createKitPlacements(settings, tiers);
  assertGeneratorInvariants(placements);
  return {
    settings,
    bayWidth: BAY_WIDTH,
    floorHeight: FLOOR_HEIGHT,
    tiers,
    bays: legacyBays(placements),
    placements,
    diagnostics: {
      duplicateSurfaceOwners: duplicateSurfaceOwners(placements),
      missingModuleIds: missingKitModuleIds(),
      unusedModuleIds: unusedModuleIds(placements)
    }
  };
}
function legacyBays(placements) {
  return placements.filter((placement) => placement.side !== "roof").map((placement) => ({
    kind: "blank",
    side: placement.side,
    tierName: placement.tierName,
    alongStart: placement.center - placement.width / 2,
    alongEnd: placement.center + placement.width / 2,
    y0: placement.y,
    y1: placement.y + placement.height,
    floorIndex: placement.floorIndex,
    bayIndex: placement.bayIndex,
    isCorner: placement.id.includes("corner")
  }));
}

import * as THREE from "three/webgpu";

var materialSlots = [
  "limestone",
  "granite",
  "terra-cotta",
  "glass",
  "bronze",
  "black-metal",
  "ornament",
  "roof"
];

var STONE_TILE_METERS = 1.45;
var STONE_ATLAS_COLUMNS = 3;
var STONE_ATLAS_ROWS = 2;
var ATLAS_PADDING = 4e-3;
var COHERENT_STONE_CELL = 4;
var KitMeshWriter = class {
  buffers = Object.fromEntries(
    materialSlots.map((slot) => [slot, emptyBuffer()])
  );
  appendQuad(slot, corners, color, uvScale = 0.35) {
    if (slot === "limestone" || slot === "ornament") {
      this.appendAtlasQuad(slot, corners, color);
      return;
    }
    const width = distance(corners[0], corners[1]) * uvScale;
    const height = distance(corners[1], corners[2]) * uvScale;
    this.appendQuadRaw(slot, corners, color, [
      [0, 0],
      [width, 0],
      [width, height],
      [0, height]
    ]);
  }
  appendAtlasQuad(slot, corners, color) {
    const width = distance(corners[0], corners[1]);
    const height = distance(corners[1], corners[2]);
    const uCuts = segmentCuts(width);
    const vCuts = segmentCuts(height);
    const atlasCell = chooseStoneAtlasCell(slot);
    for (let u = 0; u < uCuts.length - 1; u++) {
      for (let v = 0; v < vCuts.length - 1; v++) {
        const u0 = uCuts[u];
        const u1 = uCuts[u + 1];
        const v0 = vCuts[v];
        const v1 = vCuts[v + 1];
        const subCorners = [
          bilerp(corners, u0, v0),
          bilerp(corners, u1, v0),
          bilerp(corners, u1, v1),
          bilerp(corners, u0, v1)
        ];
        const uSpan = Math.min(1, width * (u1 - u0) / STONE_TILE_METERS);
        const vSpan = Math.min(1, height * (v1 - v0) / STONE_TILE_METERS);
        this.appendQuadRaw(slot, subCorners, color, atlasUvs(atlasCell, uSpan, vSpan));
      }
    }
  }
  appendQuadRaw(slot, corners, color, uvs) {
    const buffer = this.buffers[slot];
    const base = buffer.positions.length / 3;
    const normal = faceNormal(corners);
    for (let index = 0; index < 4; index++) {
      buffer.positions.push(...corners[index]);
      buffer.normals.push(...normal);
      buffer.uvs.push(...uvs[index]);
      buffer.colors.push(...color);
    }
    buffer.indices.push(base, base + 1, base + 2, base, base + 2, base + 3);
  }
  appendBox(slot, min, max, color, faces = {}) {
    const add = (face) => faces[face] !== false;
    const [x0, y0, z0] = min;
    const [x1, y1, z1] = max;
    if (add("front")) this.appendQuad(slot, [[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], color);
    if (add("back")) this.appendQuad(slot, [[x1, y0, z0], [x0, y0, z0], [x0, y1, z0], [x1, y1, z0]], color);
    if (add("right")) this.appendQuad(slot, [[x1, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1]], color);
    if (add("left")) this.appendQuad(slot, [[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]], color);
    if (add("top")) this.appendQuad(slot, [[x0, y1, z1], [x1, y1, z1], [x1, y1, z0], [x0, y1, z0]], color);
    if (add("bottom")) this.appendQuad(slot, [[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], color);
  }
  appendFrom(other) {
    for (const slot of materialSlots) {
      const target = this.buffers[slot];
      const source = other.buffers[slot];
      const offset = target.positions.length / 3;
      target.positions.push(...source.positions);
      target.normals.push(...source.normals);
      target.uvs.push(...source.uvs);
      target.colors.push(...source.colors);
      target.indices.push(...source.indices.map((index) => index + offset));
    }
  }
  toGeometries() {
    return Object.fromEntries(
      materialSlots.map((slot) => [slot, toGeometry(this.buffers[slot])])
    );
  }
  triangleCount() {
    return materialSlots.reduce(
      (sum, slot) => sum + this.buffers[slot].indices.length / 3,
      0
    );
  }
};
function emptyBuffer() {
  return { positions: [], normals: [], uvs: [], colors: [], indices: [] };
}
function segmentCuts(length) {
  if (length <= 1e-3) return [0, 1];
  const count = Math.max(1, Math.ceil(length / STONE_TILE_METERS));
  return Array.from({ length: count + 1 }, (_, index) => Math.min(1, index * STONE_TILE_METERS / length));
}
function chooseStoneAtlasCell(slot) {
  if (slot === "ornament") return COHERENT_STONE_CELL;
  return COHERENT_STONE_CELL;
}
function atlasUvs(cell, uSpan, vSpan) {
  const column = cell % STONE_ATLAS_COLUMNS;
  const rowFromTop = Math.floor(cell / STONE_ATLAS_COLUMNS);
  const cellWidth = 1 / STONE_ATLAS_COLUMNS;
  const cellHeight = 1 / STONE_ATLAS_ROWS;
  const u0 = column * cellWidth + ATLAS_PADDING;
  const v0 = 1 - (rowFromTop + 1) * cellHeight + ATLAS_PADDING;
  const u1 = u0 + (cellWidth - ATLAS_PADDING * 2) * uSpan;
  const v1 = v0 + (cellHeight - ATLAS_PADDING * 2) * vSpan;
  return [
    [u0, v0],
    [u1, v0],
    [u1, v1],
    [u0, v1]
  ];
}
function toGeometry(buffer) {
  if (buffer.positions.length === 0) return null;
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(buffer.positions, 3));
  geometry.setAttribute("normal", new THREE.Float32BufferAttribute(buffer.normals, 3));
  geometry.setAttribute("uv", new THREE.Float32BufferAttribute(buffer.uvs, 2));
  geometry.setAttribute("color", new THREE.Float32BufferAttribute(buffer.colors, 3));
  geometry.setIndex(buffer.indices);
  geometry.computeBoundingSphere();
  return geometry;
}
function faceNormal(corners) {
  const a = subtract(corners[1], corners[0]);
  const b = subtract(corners[2], corners[0]);
  const n = cross(a, b);
  const length = Math.hypot(...n) || 1;
  return [n[0] / length, n[1] / length, n[2] / length];
}
function subtract(a, b) {
  return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
}
function bilerp(corners, u, v) {
  const bottom = lerp(corners[0], corners[1], u);
  const top = lerp(corners[3], corners[2], u);
  return lerp(bottom, top, v);
}
function lerp(a, b, t) {
  return [
    a[0] + (b[0] - a[0]) * t,
    a[1] + (b[1] - a[1]) * t,
    a[2] + (b[2] - a[2]) * t
  ];
}
function cross(a, b) {
  return [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0]
  ];
}
function distance(a, b) {
  return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
}

function facadeTransform(input) {
  const offsetX = input.offsetX ?? 0;
  const offsetZ = input.offsetZ ?? 0;
  const normalOffset = input.normalOffset ?? 0;
  return ([x, y, z]) => {
    if (input.side === "front") return [offsetX + input.center + x, input.y + y, offsetZ + input.buildingDepth / 2 + normalOffset + z];
    if (input.side === "back") return [offsetX + input.center - x, input.y + y, offsetZ - input.buildingDepth / 2 - normalOffset - z];
    if (input.side === "right") return [offsetX + input.buildingWidth / 2 + normalOffset + z, input.y + y, offsetZ - input.center - x];
    return [offsetX - input.buildingWidth / 2 - normalOffset - z, input.y + y, offsetZ + input.center + x];
  };
}
function roofTransform(input) {
  return ([x, y, z]) => [input.x + x, input.y + y, input.z + z];
}

function appendMassCaps(writer, tiers) {
  for (const tier of tiers) appendTierSoffit(writer, tier);
  for (const tier of tiers) {
    if (tier.role === "shaft") continue;
    appendTierDeck(writer, tier, tier.role === "crown");
  }
  appendSameLevelConnectors(writer, tiers);
}
function appendTierSoffit(writer, tier) {
  if (tier.y0 <= 1e-3) return;
  const y0 = tier.y0 - 0.16;
  const y1 = tier.y0;
  const x0 = tier.x - tier.width / 2;
  const x1 = tier.x + tier.width / 2;
  const z0 = tier.z - tier.depth / 2;
  const z1 = tier.z + tier.depth / 2;
  writer.appendBox("limestone", [x0, y0, z0], [x1, y1, z1], stoneDark);
  writer.appendBox("limestone", [x0, y0 - 0.16, z1 - 0.22], [x1, y1, z1 + 0.08], stoneDark);
  writer.appendBox("limestone", [x0, y0 - 0.16, z0 - 0.08], [x1, y1, z0 + 0.22], stoneDark);
  writer.appendBox("limestone", [x1 - 0.22, y0 - 0.16, z0], [x1 + 0.08, y1, z1], stoneDark);
  writer.appendBox("limestone", [x0 - 0.08, y0 - 0.16, z0], [x0 + 0.22, y1, z1], stoneDark);
}
function appendTierDeck(writer, tier, roof) {
  const y = tier.y0 + tier.height;
  const deckTop = y - 0.035;
  writer.appendBox(
    roof ? "roof" : "limestone",
    [tier.x - tier.width / 2, y - 0.14, tier.z - tier.depth / 2],
    [tier.x + tier.width / 2, deckTop, tier.z + tier.depth / 2],
    roof ? roofMetal : stoneDark
  );
  appendDeckEdges(writer, tier, deckTop, roof);
}
function appendSameLevelConnectors(writer, tiers) {
  const levels = /* @__PURE__ */ new Map();
  for (const tier of tiers) {
    const key = `${tier.role}:${tier.y0}:${tier.height}`;
    levels.set(key, [...levels.get(key) ?? [], tier]);
  }
  for (const group of levels.values()) {
    if (group.length < 2) continue;
    for (let a = 0; a < group.length; a++) {
      for (let b = a + 1; b < group.length; b++) appendConnector(writer, group[a], group[b]);
    }
  }
}
function appendConnector(writer, a, b) {
  const y = a.y0 + a.height;
  const slabY0 = y - 0.16;
  const slabY1 = y - 0.035;
  const ax0 = a.x - a.width / 2;
  const ax1 = a.x + a.width / 2;
  const az0 = a.z - a.depth / 2;
  const az1 = a.z + a.depth / 2;
  const bx0 = b.x - b.width / 2;
  const bx1 = b.x + b.width / 2;
  const bz0 = b.z - b.depth / 2;
  const bz1 = b.z + b.depth / 2;
  if (almostEqual(az0, bz1) || almostEqual(az1, bz0)) {
    const x0 = Math.max(ax0, bx0);
    const x1 = Math.min(ax1, bx1);
    if (x1 <= x0) return;
    const z = almostEqual(az0, bz1) ? az0 : az1;
    writer.appendBox("limestone", [x0, slabY0, z - 0.18], [x1, slabY1, z + 0.18], stoneDark);
  }
  if (almostEqual(ax0, bx1) || almostEqual(ax1, bx0)) {
    const z0 = Math.max(az0, bz0);
    const z1 = Math.min(az1, bz1);
    if (z1 <= z0) return;
    const x = almostEqual(ax0, bx1) ? ax0 : ax1;
    writer.appendBox("limestone", [x - 0.18, slabY0, z0], [x + 0.18, slabY1, z1], stoneDark);
  }
}
function almostEqual(a, b) {
  return Math.abs(a - b) < 1e-3;
}
function appendDeckEdges(writer, tier, y, roof) {
  const slot = roof ? "roof" : "limestone";
  const color = roof ? roofMetal : stoneDark;
  const x0 = tier.x - tier.width / 2;
  const x1 = tier.x + tier.width / 2;
  const z0 = tier.z - tier.depth / 2;
  const z1 = tier.z + tier.depth / 2;
  writer.appendBox(slot, [x0, y, z1 - 0.18], [x1, y + 0.34, z1 + 0.12], color);
  writer.appendBox(slot, [x0, y, z0 - 0.12], [x1, y + 0.34, z0 + 0.18], color);
  writer.appendBox(slot, [x1 - 0.18, y, z0], [x1 + 0.12, y + 0.34, z1], color);
  writer.appendBox(slot, [x0 - 0.12, y, z0], [x0 + 0.18, y + 0.34, z1], color);
  writer.appendBox("granite", [x0 + 0.3, y + 0.02, z1 - 0.08], [x1 - 0.3, y + 0.08, z1 + 0.02], stoneDark);
}

var topologyColors = {
  podium: [0.46, 0.56, 0.68],
  shaft: [0.58, 0.62, 0.54],
  crown: [0.66, 0.55, 0.42],
  bridge: [0.5, 0.64, 0.66]
};
function compileFinancialBuilding(plan) {
  assertCompleteKitRegistry();
  const writer = new KitMeshWriter();
  if (plan.settings.debugMode === "topology") {
    for (const tier of plan.tiers) appendTopologyBlock(writer, tier);
  } else {
    appendMassCaps(writer, plan.tiers);
    for (const placement of plan.placements) appendPlacement(writer, plan, placement);
  }
  const moduleUsage = moduleUsageFrom(plan.placements);
  return {
    geometries: writer.toGeometries(),
    triangleCount: writer.triangleCount(),
    moduleCount: plan.placements.length,
    plan,
    moduleUsage
  };
}
function appendPlacement(writer, plan, placement) {
  const runtime = getKitModuleRuntime(placement.id);
  const tier = plan.tiers.find((candidate) => candidate.name === placement.tierName);
  const transform = placement.side === "roof" ? roofTransform({ x: placement.center, y: placement.y, z: placement.roofZ ?? 0 }) : facadeTransform({
    side: placement.side,
    buildingWidth: tier?.width ?? plan.tiers[0].width,
    buildingDepth: tier?.depth ?? plan.tiers[0].depth,
    center: placement.center,
    y: placement.y,
    offsetX: placement.xOffset ?? tier?.x ?? 0,
    offsetZ: placement.zOffset ?? tier?.z ?? 0,
    normalOffset: placement.normalOffset ?? 0
  });
  runtime.builder({
    writer,
    transform,
    moduleId: placement.id,
    width: placement.width,
    height: placement.height,
    depth: placement.depth,
    anchors: {},
    moduleVariant: placement.moduleVariant
  });
}
function appendTopologyBlock(writer, tier) {
  writer.appendBox(
    "limestone",
    [tier.x - tier.width / 2, tier.y0, tier.z - tier.depth / 2],
    [tier.x + tier.width / 2, tier.y0 + tier.height, tier.z + tier.depth / 2],
    topologyColors[tier.role]
  );
}
function moduleUsageFrom(placements) {
  const usage = {};
  for (const module2 of financialCoreModules) usage[module2.id] = 0;
  for (const placement of placements) usage[placement.id] = (usage[placement.id] ?? 0) + 1;
  return usage;
}

// .example-captures/audit-build/procedural-tower-building-entry.ts
var PROCEDURAL_FINANCIAL_TOWER_SETTINGS = Object.freeze({
  seed: 1042,
  variant: "setback-tower",
  widthBays: 9,
  depthBays: 7,
  floors: 17,
  podiumFloors: 3,
  setbackFloors: 2,
  towerScale: 0.82,
  ornamentDensity: 0.72,
  colonnade: true,
  cornerEntrance: true,
  crown: true,
  materialVariant: "light-limestone",
  debugMode: "beauty",
  activeTab: "building",
  selectedModuleId: "round-column",
  podiumStyle: "colonnade",
  entranceType: "center-revolving",
  shaftRhythm: "chicago-grid",
  crownStyle: "windowed-crown",
  roofEquipmentDensity: 0.7,
  massingPattern: "single-tower",
  footprintStyle: "rectangle",
  secondaryFootprintStyle: "rectangle",
  footprintHeightMode: "full-height",
  hardInsetSide: "none",
  hardInsetAmount: 0,
  innerCourtWidth: 0.38,
  innerCourtDepth: 0.42,
  innerCourtOffsetX: 0,
  innerCourtOffsetZ: 0,
  skybridgeEnabled: true,
  skybridgeFloor: 8,
  buildingArchetype: "board-of-trade-tower",
  roofStyle: "statue-tower",
  porticoProjection: 1.8,
  centralAxisBays: 3,
  cornerTreatment: "rounded-piers",
  crownDecorationStyle: "classical",
  crownDecorationDensity: 0.6,
  crownFinialRhythm: "edge-regular",
  crownFinialDensity: 0.55
});
var renderOrder = [
  "limestone",
  "granite",
  "terra-cotta",
  "ornament",
  "glass",
  "bronze",
  "black-metal",
  "roof"
];
var debugModeMap = /* @__PURE__ */ new Map([
  ["final", "beauty"],
  ["beauty", "beauty"],
  ["topology", "topology"],
  ["facade-ids", "facade-ids"]
]);
function createBuildingPlan(overrides = {}) {
  return createFinancialBuildingPlan({
    ...PROCEDURAL_FINANCIAL_TOWER_SETTINGS,
    ...overrides
  });
}
function generateBuilding(settings = {}) {
  return compileFinancialBuilding(createBuildingPlan(settings));
}
function compileBuilding(planOrSettings = createBuildingPlan(), materials = {}) {
  let settings = normalizeSettings(planOrSettings);
  let generated = compileFinancialBuilding(createFinancialBuildingPlan(settings));
  const root = new THREE2.Group();
  const meshes = /* @__PURE__ */ new Map();
  applyGeneratedGeometry(generated);
  function applyGeneratedGeometry(nextGenerated) {
    generated = nextGenerated;
    for (const slot of renderOrder) {
      const geometry = generated.geometries[slot];
      let mesh = meshes.get(slot);
      if (!geometry) {
        if (mesh) {
          root.remove(mesh);
          mesh.geometry.dispose();
          meshes.delete(slot);
        }
        continue;
      }
      if (!mesh) {
        mesh = new THREE2.Mesh(geometry, materials[slot] ?? fallbackMaterial(slot));
        mesh.name = `procedural-financial-tower:${slot}`;
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        meshes.set(slot, mesh);
        root.add(mesh);
      } else {
        mesh.geometry.dispose();
        mesh.geometry = geometry;
      }
    }
  }
  return {
    root,
    get moduleCount() {
      return generated.moduleCount;
    },
    get triangleCount() {
      return generated.triangleCount;
    },
    get plan() {
      return generated.plan;
    },
    get moduleUsage() {
      return generated.moduleUsage;
    },
    setDebugMode(modeName) {
      const debugMode = debugModeMap.get(modeName) ?? "beauty";
      settings = { ...settings, debugMode };
      applyGeneratedGeometry(
        compileFinancialBuilding(createFinancialBuildingPlan(settings))
      );
    },
    dispose() {
      for (const mesh of meshes.values()) {
        mesh.geometry.dispose();
      }
    }
  };
}
function normalizeSettings(planOrSettings) {
  const sourceSettings = planOrSettings?.settings ?? planOrSettings;
  return {
    ...PROCEDURAL_FINANCIAL_TOWER_SETTINGS,
    ...sourceSettings
  };
}
function fallbackMaterial(slot) {
  return new THREE2.MeshStandardMaterial({
    color: slot === "glass" ? 462868 : 16052196,
    roughness: slot === "glass" ? 0.08 : 0.8,
    metalness: slot === "glass" ? 0.72 : 0.02,
    vertexColors: true
  });
}
export {
  PROCEDURAL_FINANCIAL_TOWER_SETTINGS,
  compileBuilding,
  compileFinancialBuilding,
  createBuildingPlan,
  createFinancialBuildingPlan,
  generateBuilding
};
