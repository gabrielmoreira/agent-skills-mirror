import * as THREE from "three/webgpu";

export const FLOOR_MAP_SIZE = 1024;
export const WALL_MAP_SIZE = 1024;
export const COLUMN_MAP_SIZE = 512;
export const WALL_WIDTH = 9.0;
export const WALL_HEIGHT = 4.2;

function createRandom(seed) {
  return () => {
    seed |= 0;
    seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

function wearEdges(context, random, x, y, w, h, height) {
  const bright = `rgb(${Math.min(235, Math.round(height + 26))},0,190)`;
  for (let e = 0; e < 3; e += 1) {
    const side = Math.floor(random() * 4);
    const along = 0.08 + random() * 0.55;
    const run = 0.12 + random() * 0.3;
    context.fillStyle = bright;
    if (side === 0) context.fillRect(x + along * w, y, run * w, 2);
    if (side === 1) context.fillRect(x + along * w, y + h - 2, run * w, 2);
    if (side === 2) context.fillRect(x, y + along * h, 2, run * h);
    if (side === 3) context.fillRect(x + w - 2, y + along * h, 2, run * h);
  }
  if (random() < 0.3) {
    context.fillStyle = "rgb(58,0,64)";
    context.fillRect(x + (0.1 + random() * 0.8) * w, random() < 0.5 ? y : y + h - 4, 5, 4);
  }
}

function grimeShadow(context, x, y, w, h) {
  context.globalAlpha = 0.16;
  context.fillStyle = "rgb(40,0,12)";
  context.fillRect(x, y, w, h);
  context.globalAlpha = 0.12;
  context.fillRect(x, y, w, h * 0.45);
  context.globalAlpha = 1;
}

export function createFloorMap() {
  const random = createRandom(7);
  const size = FLOOR_MAP_SIZE;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d");
  context.fillStyle = "rgb(28,0,90)";
  context.fillRect(0, 0, size, size);

  const splits = (count) => {
    const values = [0];
    for (let i = 1; i < count; i += 1) {
      values.push((i + (random() - 0.5) * 0.55) / count * size);
    }
    values.push(size);
    return values;
  };
  const xs = splits(6);
  const ys = splits(6);

  for (let i = 0; i < xs.length - 1; i += 1) {
    for (let j = 0; j < ys.length - 1; j += 1) {
      const x = xs[i];
      const y = ys[j];
      const w = xs[i + 1] - x;
      const h = ys[j + 1] - y;
      const inset = 7;
      const height = 150 + random() * 75;
      const variation = 50 + random() * 140;
      context.fillStyle = `rgb(${Math.round(height)},0,${Math.round(variation)})`;
      context.fillRect(x + inset, y + inset, w - inset * 2, h - inset * 2);
      const type = random();

      if (type < 0.16) {
        const slots = 3 + Math.floor(random() * 3);
        for (let s = 0; s < slots; s += 1) {
          const sy = y + inset + 14 + (s + 0.5) / slots * (h - inset * 2 - 28);
          context.fillStyle = "rgb(55,0,80)";
          context.fillRect(x + w * 0.25, sy - 4, w * 0.5, 8);
        }
      } else if (type < 0.34) {
        context.fillStyle = "rgb(90,255,0)";
        context.fillRect(x + inset + 12, y + h / 2 - 5, w - inset * 2 - 24, 10);
      } else if (type < 0.46) {
        for (let d = 0; d < 3; d += 1) {
          context.fillStyle = `rgb(${Math.round(height + 6)},0,216)`;
          context.fillRect(x + w * (0.16 + d * 0.26), y + h * 0.46, w * 0.16, 12);
        }
      } else if (type < 0.56) {
        for (let gy = 0; gy < 4; gy += 1) {
          for (let gx = 0; gx < 4; gx += 1) {
            context.fillStyle = "rgb(38,0,50)";
            context.fillRect(x + w * (0.2 + gx * 0.16), y + h * (0.2 + gy * 0.16), w * 0.1, h * 0.1);
          }
        }
      }

      context.fillStyle = `rgb(${Math.round(height - 45)},0,${Math.round(variation)})`;
      for (const [rx, ry] of [
        [x + inset + 14, y + inset + 14],
        [x + w - inset - 14, y + inset + 14],
        [x + inset + 14, y + h - inset - 14],
        [x + w - inset - 14, y + h - inset - 14],
      ]) {
        context.beginPath();
        context.arc(rx, ry, 5, 0, Math.PI * 2);
        context.fill();
      }
      wearEdges(context, random, x + inset, y + inset, w - inset * 2, h - inset * 2, height);
    }
  }

  const map = new THREE.CanvasTexture(canvas);
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.anisotropy = 4;
  map.name = "floorPanelMap";
  return map;
}

export function createWallMap() {
  const random = createRandom(21);
  const size = WALL_MAP_SIZE;
  const px = (w) => Math.round(w / WALL_WIDTH * size);
  const py = (h) => Math.round(size - h / WALL_HEIGHT * size);
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d");

  context.fillStyle = "rgb(30,0,60)";
  context.fillRect(0, 0, size, size);
  let edge = 0;
  while (edge < size) {
    const w = size * (0.12 + random() * 0.1);
    const height = 128 + random() * 26;
    const variation = 46 + random() * 60;
    context.fillStyle = `rgb(${Math.round(height)},0,${Math.round(variation)})`;
    context.fillRect(edge + 3, 0, w - 6, size);
    edge += w;
  }

  for (let row = 0; row < 3; row += 1) {
    const rowY = py(3.1 - row * 0.82);
    const rowH = py(3.1 - row * 0.82 - 0.74) - rowY;
    let plateX = row % 2 === 0 ? 0 : -px(0.5);
    while (plateX < size) {
      const plateW = px(0.9 + random() * 0.7);
      const height = 150 + random() * 55;
      const variation = 60 + random() * 130;
      context.fillStyle = `rgb(${Math.round(height)},0,${Math.round(variation)})`;
      context.fillRect(plateX + 4, rowY, plateW - 8, rowH - 6);
      if (random() < 0.3) {
        for (let s = 0; s < 4; s += 1) {
          context.fillStyle = "rgb(52,0,44)";
          context.fillRect(plateX + plateW * 0.22, rowY + rowH * 0.2 + s * rowH * 0.15, plateW * 0.5, 7);
        }
        grimeShadow(context, plateX + plateW * 0.18, rowY + rowH * 0.72, plateW * 0.58, rowH * 0.28);
      }
      wearEdges(context, random, plateX + 4, rowY, plateW - 8, rowH - 6, height);
      plateX += plateW;
    }
  }

  context.fillStyle = "rgb(176,0,74)";
  context.fillRect(0, py(0.62), size, size - py(0.62));
  context.globalAlpha = 0.3;
  for (let s = 0; s < 14; s += 1) {
    context.fillStyle = "rgb(120,0,40)";
    context.fillRect(random() * size, py(0.1 + random() * 0.4), 50 + random() * 120, 3);
  }
  context.globalAlpha = 1;
  grimeShadow(context, 0, py(0.2), size, size - py(0.2));
  for (let c = 0; c < size / 40 + 1; c += 1) {
    context.fillStyle = c % 2 === 0 ? "rgb(176,0,216)" : "rgb(150,0,52)";
    context.beginPath();
    context.moveTo(c * 40, py(0.78));
    context.lineTo(c * 40 + 22, py(0.78));
    context.lineTo(c * 40 + 44, py(0.62));
    context.lineTo(c * 40 + 22, py(0.62));
    context.closePath();
    context.fill();
  }

  for (let riser = 0; riser < 3; riser += 1) {
    const rx = px(2.0 + riser * 0.28);
    context.fillStyle = "rgb(196,0,96)";
    context.fillRect(rx, py(3.42), px(0.14), py(0.8) - py(3.42));
    for (let clamp = 0; clamp < 4; clamp += 1) {
      const cy = py(3.1 - clamp * 0.72);
      context.fillStyle = "rgb(224,0,110)";
      context.fillRect(rx - 5, cy, px(0.14) + 10, 16);
      grimeShadow(context, rx - 5, cy + 16, px(0.14) + 10, 22);
    }
  }

  const doorHalf = px(1.15);
  const doorTop = py(2.75);
  const frame = px(0.22);
  context.fillStyle = "rgb(235,0,96)";
  context.fillRect(size / 2 - doorHalf - frame, doorTop - frame, (doorHalf + frame) * 2, size - doorTop + frame);
  context.fillStyle = "rgb(214,0,88)";
  context.fillRect(size / 2 - doorHalf - Math.round(frame * 0.55), doorTop - Math.round(frame * 0.55), (doorHalf + Math.round(frame * 0.55)) * 2, size - doorTop + Math.round(frame * 0.55));
  context.fillStyle = "rgb(96,255,30)";
  context.fillRect(size / 2 - doorHalf - Math.round(frame * 0.3), doorTop - Math.round(frame * 0.3), (doorHalf + Math.round(frame * 0.3)) * 2, size - doorTop + Math.round(frame * 0.3));
  context.fillStyle = "rgb(50,0,40)";
  context.fillRect(size / 2 - doorHalf, doorTop, doorHalf * 2, size - doorTop);
  for (const doorSide of [-1, 1]) {
    const leafX = doorSide === -1 ? size / 2 - doorHalf + 8 : size / 2 + 10;
    const leafW = doorHalf - 18;
    for (let rib = 0; rib < 7; rib += 1) {
      context.fillStyle = rib % 2 === 0 ? "rgb(84,0,70)" : "rgb(68,0,58)";
      context.fillRect(leafX, doorTop + 10 + rib * (size - doorTop - 20) / 7, leafW, (size - doorTop - 20) / 7 - 4);
    }
  }
  const sill = Math.round(frame * 0.55);
  context.fillStyle = "rgb(214,0,88)";
  context.fillRect(size / 2 - doorHalf - sill, py(0.16), (doorHalf + sill) * 2, size - py(0.16));

  context.fillStyle = "rgb(205,0,120)";
  context.fillRect(size / 2 + doorHalf + frame + 8, py(1.85), px(0.18), py(1.55) - py(1.85));
  context.fillStyle = "rgb(120,255,30)";
  context.fillRect(size / 2 + doorHalf + frame + 14, py(1.78), px(0.09), 8);

  const signX = px(6.9);
  const signW = px(0.6);
  context.fillStyle = "rgb(70,0,44)";
  context.fillRect(signX - 8, py(3.35) - 8, signW + 16, py(1.05) - py(3.35) + 16);
  for (let glyph = 0; glyph < 6; glyph += 1) {
    const gy = py(3.2 - glyph * 0.36);
    for (let cell = 0; cell < 9; cell += 1) {
      if (random() < 0.55) {
        context.fillStyle = "rgb(70,255,255)";
        context.fillRect(signX + (cell % 3) * signW / 3 + 3, gy + Math.floor(cell / 3) * 22, signW / 3 - 6, 18);
      }
    }
  }

  context.fillStyle = "rgb(216,0,84)";
  context.fillRect(0, py(4.2), size, py(3.55) - py(4.2));
  context.fillStyle = "rgb(88,255,30)";
  context.fillRect(px(0.4), py(3.55), size - px(0.8), 7);
  for (let block = 0; block < 12; block += 1) {
    context.fillStyle = block % 2 === 0 ? "rgb(230,0,90)" : "rgb(64,0,60)";
    context.fillRect(block * size / 12, 0, size / 12, py(3.98));
    context.fillStyle = block % 2 === 0 ? "rgb(226,0,86)" : "rgb(60,0,58)";
    context.fillRect(0, block * size / 12, px(0.16), size / 12);
    context.fillRect(size - px(0.16), block * size / 12, px(0.16), size / 12);
  }

  const map = new THREE.CanvasTexture(canvas);
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.anisotropy = 4;
  map.name = "wallBulkheadMap";
  return map;
}

export function createColumnMap() {
  const random = createRandom(34);
  const size = COLUMN_MAP_SIZE;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d");
  const strips = 8;
  for (let s = 0; s < strips; s += 1) {
    const x = Math.round(s / strips * size);
    const w = Math.round(size / strips);
    const height = 84 + random() * 62;
    const variation = 40 + random() * 120;
    context.fillStyle = `rgb(${Math.round(height)},0,${Math.round(variation)})`;
    context.fillRect(x, 0, w, size);
    context.fillStyle = "rgb(36,0,60)";
    context.fillRect(x, 0, 6, size);
  }
  context.fillStyle = "rgb(120,0,216)";
  context.fillRect(0, Math.round(size * 0.30), size, Math.round(size * 0.07));
  context.globalAlpha = 0.5;
  for (let n = 0; n < 8; n += 1) {
    context.fillStyle = "rgb(100,0,90)";
    context.fillRect(random() * size, size * 0.30 + random() * size * 0.05, 14 + random() * 26, 3);
  }
  context.globalAlpha = 1;
  const flange = Math.round(size * 0.13);
  context.fillStyle = "rgb(226,0,96)";
  context.fillRect(0, 0, size, flange);
  context.fillRect(0, size - flange, size, flange);
  for (let b = 0; b < 8; b += 1) {
    const bx = Math.round((b + 0.5) / 8 * size);
    for (const by of [Math.round(flange * 0.5), size - Math.round(flange * 0.5)]) {
      context.fillStyle = "rgb(206,0,96)";
      context.beginPath(); context.arc(bx, by, 11, 0, Math.PI * 2); context.fill();
      context.fillStyle = "rgb(248,0,150)";
      context.beginPath(); context.arc(bx, by, 7, 0, Math.PI * 2); context.fill();
    }
  }
  context.fillStyle = "rgb(84,255,40)";
  context.fillRect(0, Math.round(size * 0.62) - 5, size, 10);
  const map = new THREE.CanvasTexture(canvas);
  map.wrapS = map.wrapT = THREE.RepeatWrapping;
  map.anisotropy = 4;
  map.name = "columnFlangeMap";
  return map;
}
