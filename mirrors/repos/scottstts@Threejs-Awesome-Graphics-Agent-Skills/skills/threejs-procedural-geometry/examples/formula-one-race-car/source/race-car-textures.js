import * as THREE from "three/webgpu";
import { PI, V2, clamp01, lerp, smooth01, spline2 } from "./mesh-kit.js";
import { PAL, PROJ } from "./design-contract.js";

/*
   GENERATED TEXTURE INPUTS
   The livery is a two-plane PROJECTOR, not a per-part unwrap: one canvas painted in the
   car's side elevation (z,y) and one painted in its plan view (z,x).  Bodywork samples
   whichever plane its world normal faces, so the paint scheme stays continuous across
   nose / chassis / sidepod / engine-cover boundaries exactly like a real wrap.
*/

function makeCanvas(w, h){
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const x = c.getContext('2d');
  x.clearRect(0, 0, w, h);
  x.lineJoin = 'round'; x.lineCap = 'round';
  return { c, x };
}
const hex = (n, a = 1) => `rgba(${(n>>16)&255},${(n>>8)&255},${n&255},${a})`;

/* ---- painting helpers, all in world metres ---------------------------------------- */
function painter(ctx, toPx, ppm){
  const P = (z, s) => toPx(z, s);           // -> [px, py]
  const api = {
    ctx, ppm,
    m: (metres) => metres * ppm,
    poly(points, { fill = null, stroke = null, width = 0.01, close = true, smooth = 0 }){
      const pts = smooth ? spline2(points.map(p => V2(p[0], p[1])), smooth, { closed: close }) .map(p => [p.x, p.y]) : points;
      ctx.beginPath();
      pts.forEach((p, i) => { const q = P(p[0], p[1]); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); });
      if (close) ctx.closePath();
      if (fill){ ctx.fillStyle = fill; ctx.fill(); }
      if (stroke){ ctx.strokeStyle = stroke; ctx.lineWidth = width * ppm; ctx.stroke(); }
    },
    /** Swept band: centreline points [[a,b],...] with per-point half-widths. */
    ribbon(points, widths, { fill = null, stroke = null, edge = 0.008, samples = 120 }){
      const cl = spline2(points.map(p => V2(p[0], p[1])), samples);
      const wl = [];
      for (let i = 0; i < samples; i++){
        const g = i / (samples - 1) * (widths.length - 1);
        const k = Math.min(Math.floor(g), widths.length - 2);
        wl.push(lerp(widths[k], widths[k + 1], smooth01(g - k)));
      }
      const left = [], right = [];
      for (let i = 0; i < samples; i++){
        const a = cl[Math.max(0, i - 1)], b = cl[Math.min(samples - 1, i + 1)];
        const t = V2(b.x - a.x, b.y - a.y); const L = Math.hypot(t.x, t.y) || 1;
        const nx = -t.y / L, ny = t.x / L;
        left.push([cl[i].x + nx * wl[i], cl[i].y + ny * wl[i]]);
        right.push([cl[i].x - nx * wl[i], cl[i].y - ny * wl[i]]);
      }
      const loop = [...left, ...right.reverse()];
      ctx.beginPath();
      loop.forEach((p, i) => { const q = P(p[0], p[1]); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); });
      ctx.closePath();
      if (stroke){ ctx.strokeStyle = stroke; ctx.lineWidth = edge * ppm; ctx.stroke(); }
      if (fill){ ctx.fillStyle = fill; ctx.fill(); }
    },
    line(points, { stroke, width = 0.006, smooth = 0 }){
      const pts = smooth ? spline2(points.map(p => V2(p[0], p[1])), smooth).map(p => [p.x, p.y]) : points;
      ctx.beginPath();
      pts.forEach((p, i) => { const q = P(p[0], p[1]); i ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); });
      ctx.strokeStyle = stroke; ctx.lineWidth = width * ppm; ctx.stroke();
    },
    rect(a, b, c, d, fill){
      const p0 = P(a, b), p1 = P(c, d);
      ctx.fillStyle = fill;
      ctx.fillRect(Math.min(p0[0],p1[0]), Math.min(p0[1],p1[1]), Math.abs(p1[0]-p0[0]), Math.abs(p1[1]-p0[1]));
    },
    /** Glyph set drawn at a world anchor; `mirror` flips handedness only, never position. */
    text(str, z, s, { size = 0.14, fill = '#fff', stroke = null, sw = 0.006, slant = 0.20, mirror = false,
                      rot = 0, align = 'center', weight = 800, spacing = 0, family = '"Arial Narrow",Arial,Helvetica,sans-serif' } = {}){
      const q = P(z, s);
      ctx.save();
      ctx.translate(q[0], q[1]);
      if (rot) ctx.rotate(rot);
      if (mirror) ctx.scale(-1, 1);
      ctx.transform(1, 0, -slant, 1, 0, 0);
      ctx.font = `${weight} ${Math.round(size * ppm)}px ${family}`;
      ctx.textAlign = align; ctx.textBaseline = 'middle';
      let s2 = str;
      if (spacing){
        const w = ctx.measureText(str).width;
        let x = align === 'center' ? -((w + spacing * ppm * (str.length - 1)) / 2) : 0;
        ctx.textAlign = 'left';
        for (const ch of s2){
          if (stroke){ ctx.lineWidth = sw * ppm; ctx.strokeStyle = stroke; ctx.strokeText(ch, x, 0); }
          ctx.fillStyle = fill; ctx.fillText(ch, x, 0);
          x += ctx.measureText(ch).width + spacing * ppm;
        }
      } else {
        if (stroke){ ctx.lineWidth = sw * ppm; ctx.strokeStyle = stroke; ctx.strokeText(s2, 0, 0); }
        ctx.fillStyle = fill; ctx.fillText(s2, 0, 0);
      }
      ctx.restore();
    },
  };
  return api;
}

/* ---- SIDE ELEVATION -------------------------------------------------------------- */
function buildLiverySide(){
  const { SIDE_W, SIDE_LAYER_H, sidePPM, Z1, Y1 } = PROJ;
  const { c, x: ctx } = makeCanvas(SIDE_W, SIDE_LAYER_H * 2);

  for (let layer = 0; layer < 2; layer++){
    // three.js is right-handed with +Z forward and +Y up, so +X is the car's LEFT flank.
    // Layer 0 (+X) reads correctly as painted; layer 1 (-X) needs mirrored glyphs.
    const mirror = layer === 1;
    const off = layer * SIDE_LAYER_H;
    const toPx = (z, y) => [(Z1 - z) * sidePPM, off + (Y1 - y) * sidePPM];
    const p = painter(ctx, toPx, sidePPM);
    const RED = hex(PAL.red), REDB = hex(PAL.redBright), WHT = hex(PAL.white);
    const GRY = hex(PAL.bodyGrey, .92), DRK = 'rgba(6,6,8,0.90)';

    /* The car is BLACK.  Everything below is an accent ribbon on a bare graphite body —
       coverage is deliberately sparse so the sculpted surface, not the paint, carries
       the form. */

    /* --- floor edge pinstripe ---------------------------------------------------- */
    p.ribbon([[1.450,0.152],[0.700,0.140],[-0.200,0.141],[-1.000,0.157],[-1.640,0.186]],
             [0.0025,0.0075,0.0085,0.0070,0.0025], { fill: RED });

    /* --- sidepod spear: slim white blade rising to the rear, crimson under-edge ---- */
    const spearC = [[0.756,0.300],[0.520,0.336],[0.140,0.372],[-0.330,0.396],[-0.830,0.404],[-1.290,0.396]];
    p.ribbon(spearC, [0.004,0.019,0.026,0.024,0.017,0.005], { fill: WHT });
    p.ribbon(spearC.map(q => [q[0], q[1] - 0.032]), [0.003,0.008,0.011,0.010,0.007,0.002], { fill: RED });

    /* --- upper shoulder flash rising onto the engine cover ----------------------- */
    p.ribbon([[0.600,0.578],[0.120,0.594],[-0.360,0.588],[-0.860,0.550],[-1.280,0.492],[-1.540,0.452]],
             [0.004,0.015,0.019,0.016,0.011,0.004], { fill: REDB });

    /* --- sidepod inlet surround --------------------------------------------------- */
    p.poly([[0.772,0.278],[0.792,0.470],[0.742,0.520],[0.660,0.512],[0.640,0.320],[0.694,0.272]],
           { stroke: RED, width: 0.010, close: true, smooth: 60 });

    /* --- nose: white blade with a crimson under-edge ------------------------------ */
    p.ribbon([[2.744,0.348],[2.560,0.378],[2.300,0.414],[2.060,0.448],[1.910,0.462]],
             [0.005,0.018,0.026,0.024,0.018], { fill: WHT });
    p.ribbon([[2.748,0.316],[2.566,0.342],[2.306,0.372],[2.066,0.404],[1.916,0.416]],
             [0.003,0.008,0.011,0.010,0.007], { fill: RED });

    /* --- race number on the nose flank -------------------------------------------- */
    p.text('27', 2.352, 0.418, { size: 0.128, fill: WHT, stroke: hex(PAL.red), sw: 0.008, mirror, slant: 0.22 });

    /* --- front wing endplate face -------------------------------------------------- */
    p.ribbon([[2.966,0.238],[2.840,0.276],[2.640,0.290],[2.446,0.276]],
             [0.010,0.016,0.016,0.010], { fill: WHT });
    p.ribbon([[2.972,0.118],[2.930,0.190],[2.884,0.238]], [0.006,0.010,0.008], { fill: RED });

    /* --- rear wing endplate --------------------------------------------------------- */
    p.ribbon([[-1.848,0.906],[-2.040,0.912],[-2.250,0.904],[-2.368,0.890]],
             [0.012,0.016,0.015,0.010], { fill: REDB });
    p.ribbon([[-2.318,0.860],[-2.334,0.760],[-2.344,0.672]], [0.010,0.013,0.009], { fill: WHT });
    p.text('27', -2.120, 0.796, { size: 0.062, fill: hex(PAL.whiteDim,.9), mirror, slant: 0.2 });

    /* --- beam wing / rear crash accents ---------------------------------------------- */
    p.ribbon([[-1.910,0.318],[-2.090,0.312],[-2.246,0.304]], [0.005,0.007,0.004], { fill: RED });

    /* --- halo pillar accent ----------------------------------------------------------- */
    p.ribbon([[1.150,0.636],[1.106,0.766],[1.056,0.866]], [0.009,0.008,0.006], { fill: REDB });

    /* --- panel shutlines --------------------------------------------------------- */
    const shut = (pts, w = 0.0055) => p.line(pts, { stroke: DRK, width: w, smooth: 90 });
    shut([[1.905,0.560],[1.900,0.400],[1.906,0.262]]);                       // bulkhead joint
    shut([[1.075,0.590],[1.078,0.470],[1.086,0.330]]);                       // cockpit front
    shut([[0.120,0.596],[0.126,0.470],[0.140,0.330]]);                       // cockpit rear
    shut([[-1.190,0.520],[-1.196,0.400],[-1.210,0.290]]);                    // sidepod exit
    shut([[0.640,0.556],[0.240,0.590],[-0.300,0.594],[-0.860,0.554],[-1.400,0.470]], 0.0048);
    shut([[0.700,0.212],[0.100,0.196],[-0.560,0.196],[-1.220,0.226]], 0.0045); // floor joint

    /* --- generated sponsor marks (fictional) --------------------------------------- */
    p.text('VF-26', -0.640, 0.520, { size: 0.044, fill: hex(PAL.whiteDim,.95), mirror, slant: 0.16, spacing: 0.004 });
    p.text('AERO-DYNAMICA', 0.130, 0.300, { size: 0.030, fill: hex(PAL.whiteDim,.85), mirror, slant: 0.14, spacing: 0.002 });
    p.text('TITAN FUELS', -1.010, 0.336, { size: 0.028, fill: hex(PAL.whiteDim,.80), mirror, slant: 0.14, spacing: 0.002 });
    p.text('GEN3 HYBRID', 1.500, 0.296, { size: 0.026, fill: hex(PAL.whiteDim,.70), mirror, slant: 0.14, spacing: 0.002 });
    p.rect(-1.380, 0.244, -1.208, 0.276, hex(PAL.white, 1));
    p.text('E-FUEL 100%', -1.294, 0.260, { size: 0.022, fill: hex(PAL.carbon,1), mirror, slant: 0 });
  }

  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 16;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  t.needsUpdate = true;
  return t;
}

/* ---- PLAN VIEW -------------------------------------------------------------------- */
function buildLiveryTop(){
  const { TOP_W, TOP_H, topPPM, Z1, X1 } = PROJ;
  const { c, x: ctx } = makeCanvas(TOP_W, TOP_H);
  const toPx = (z, xw) => [(Z1 - z) * topPPM, (X1 - xw) * topPPM];
  const p = painter(ctx, toPx, topPPM);
  const RED = hex(PAL.red), REDB = hex(PAL.redBright), WHT = hex(PAL.white), GRY = hex(PAL.bodyGrey, .9);
  const DRK = 'rgba(6,6,8,0.88)';
  const both = (fn) => { fn(1); fn(-1); };

  /* --- nose spear: narrow white blade with crimson edges ------------------------- */
  p.ribbon([[2.750,0],[2.520,0],[2.240,0],[1.980,0],[1.800,0]],
           [0.005,0.020,0.028,0.032,0.028], { fill: WHT });
  p.ribbon([[2.742,0],[2.520,0],[2.240,0],[1.980,0],[1.820,0]],
           [0.002,0.008,0.012,0.014,0.012], { fill: hex(PAL.carbonWarm, 1) });
  both(s => p.ribbon([[2.750,0.008*s],[2.520,0.026*s],[2.240,0.035*s],[1.980,0.039*s],[1.800,0.035*s]],
                     [0.0025,0.0060,0.0070,0.0070,0.0055], { fill: RED }));

  /* --- number on the nose deck (rotated into the plan frame) --------------------- */
  p.text('27', 2.372, 0, { size: 0.098, fill: hex(PAL.white), stroke: hex(PAL.red), sw: 0.006, rot: -Math.PI/2, slant: 0.22, mirror: true });

  /* --- chassis blades sweeping out to the sidepod shoulders ---------------------- */
  both(s => {
    p.ribbon([[1.870,0.078*s],[1.560,0.156*s],[1.220,0.236*s],[0.900,0.318*s],[0.700,0.380*s]],
             [0.008,0.014,0.018,0.018,0.010], { fill: WHT });
    p.ribbon([[1.866,0.048*s],[1.556,0.122*s],[1.216,0.200*s],[0.898,0.282*s],[0.698,0.344*s]],
             [0.004,0.006,0.007,0.007,0.004], { fill: REDB });
  });

  /* --- sidepod top plane: forward chevrons -------------------------------------- */
  both(s => {
    p.ribbon([[0.720,0.600*s],[0.300,0.664*s],[-0.240,0.652*s],[-0.760,0.592*s],[-1.190,0.502*s]],
             [0.006,0.022,0.026,0.020,0.006], { fill: WHT });
    p.ribbon([[0.706,0.548*s],[0.292,0.610*s],[-0.250,0.598*s],[-0.772,0.540*s],[-1.190,0.454*s]],
             [0.003,0.008,0.010,0.008,0.003], { fill: RED });
  });

  /* --- engine cover spine -------------------------------------------------------- */
  both(s => p.ribbon([[-0.240,0.058*s],[-0.660,0.052*s],[-1.090,0.041*s],[-1.500,0.026*s],[-1.660,0.016*s]],
                     [0.006,0.0055,0.0045,0.0032,0.0018], { fill: REDB }));
  p.text('27', -1.300, 0, { size: 0.056, fill: hex(PAL.white,.95), rot: -Math.PI/2, slant: 0.2, mirror: true });

  /* --- airbox collar ------------------------------------------------------------- */
  p.poly([[-0.150,0.092],[-0.330,0.100],[-0.330,-0.100],[-0.150,-0.092]], { stroke: RED, width: 0.008 });

  /* --- front wing plan: crimson leading edge, white on the outboard flaps -------- */
  both(s => {
    p.ribbon([[2.952,0.320*s],[2.918,0.600*s],[2.876,0.800*s],[2.836,0.890*s]],
             [0.0060,0.0075,0.0075,0.0050], { fill: RED });
    p.ribbon([[2.690,0.480*s],[2.652,0.680*s],[2.612,0.826*s],[2.576,0.892*s]],
             [0.0120,0.0160,0.0150,0.0090], { fill: WHT });
    p.ribbon([[2.512,0.520*s],[2.478,0.700*s],[2.444,0.832*s],[2.412,0.894*s]],
             [0.0100,0.0130,0.0120,0.0070], { fill: hex(PAL.whiteDim,.9) });
  });

  /* --- rear wing plan ------------------------------------------------------------ */
  p.rect(-1.852, -0.472, -1.986, 0.472, REDB);
  both(s => p.rect(-2.128, 0.472*s, -2.320, 0.418*s, WHT));
  p.rect(-2.150, -0.180, -2.300, 0.180, hex(PAL.white, .95));

  /* --- shutlines / cooling exits -------------------------------------------------- */
  both(s => p.line([[0.660,0.700*s],[0.120,0.742*s],[-0.420,0.716*s],[-0.960,0.612*s],[-1.230,0.520*s]],
                   { stroke: DRK, width: 0.005, smooth: 90 }));
  both(s => p.line([[1.900,0.115*s],[1.560,0.208*s],[1.180,0.300*s]], { stroke: DRK, width: 0.0045, smooth: 60 }));
  p.line([[1.905,0.100],[1.905,-0.100]], { stroke: DRK, width: 0.0055 });
  p.line([[0.115,0.240],[0.115,-0.240]], { stroke: DRK, width: 0.0055 });

  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 16;
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  t.needsUpdate = true;
  return t;
}

/* ---- carbon twill: height field -> Sobel normal + AO ------------------------------ */
function buildCarbonTexture(size = 512){
  const h = new Float32Array(size * size);
  const tow = size / 8;                       // 4 tows across in each direction (2x2 twill)
  for (let y = 0; y < size; y++){
    for (let x = 0; x < size; x++){
      const gx = Math.floor(x / tow), gy = Math.floor(y / tow);
      const over = ((gx + gy) & 3) < 2;       // 2x2 twill float pattern
      const fx = (x % tow) / tow, fy = (y % tow) / tow;
      const along = over ? fx : fy;           // filament direction of this tow
      const across = over ? fy : fx;
      const bulge = Math.sin(PI * clamp01(across)) ** 0.75;
      const filament = 0.5 + 0.5 * Math.cos(along * PI * 2 * 9);
      let v = (over ? 0.62 : 0.30) + bulge * 0.42 + filament * 0.055 * bulge;
      const seam = Math.min(across, 1 - across);
      v -= Math.exp(-seam * seam * 340) * 0.20;
      h[y * size + x] = v;
    }
  }
  const at = (x, y) => h[((y % size) + size) % size * size + (((x % size) + size) % size)];
  const data = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++){
    for (let x = 0; x < size; x++){
      const dx = (at(x+1,y) - at(x-1,y)) * 3.4;
      const dy = (at(x,y+1) - at(x,y-1)) * 3.4;
      const inv = 1 / Math.hypot(dx, dy, 1);
      const i = (y * size + x) * 4;
      data[i]   = (-dx * inv * 0.5 + 0.5) * 255;
      data[i+1] = ( dy * inv * 0.5 + 0.5) * 255;
      data[i+2] = ( inv * 0.5 + 0.5) * 255;
      data[i+3] = clamp01(at(x,y)) * 255;      // alpha carries the weave height / AO
    }
  }
  const t = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 16;
  t.generateMipmaps = true;
  t.minFilter = THREE.LinearMipmapLinearFilter;
  t.magFilter = THREE.LinearFilter;
  t.needsUpdate = true;
  return t;
}

/* ---- tyre sidewall: u = circumference, v = across the section --------------------- */
function buildTyreWall(){
  const W = 2048, H = 512;
  const { c, x: ctx } = makeCanvas(W, H);
  ctx.fillStyle = '#000000'; ctx.fillRect(0, 0, W, H);
  // v bands: 0=inner sidewall .. 0.5=tread .. 1=outer sidewall
  const rows = 22;
  for (let i = 0; i < rows; i++){                    // moulding rings on both sidewalls
    const t = i / rows;
    const yA = H * (0.055 + t * 0.30), yB = H * (0.945 - t * 0.30);
    const v = 26 + Math.sin(t * PI * 7) * 12;
    ctx.fillStyle = `rgb(${v},${v},${v + 2})`;
    ctx.fillRect(0, yA, W, H * 0.006);
    ctx.fillRect(0, yB, W, H * 0.006);
  }
  // compound band (soft = crimson) on the outboard sidewall
  const gradient = ctx.createLinearGradient(0, H * 0.80, 0, H * 0.905);
  gradient.addColorStop(0, hex(PAL.redBright, 0)); gradient.addColorStop(0.35, hex(PAL.redBright, 1));
  gradient.addColorStop(0.75, hex(PAL.red, 1)); gradient.addColorStop(1, hex(PAL.red, 0));
  ctx.fillStyle = gradient; ctx.fillRect(0, H * 0.80, W, H * 0.105);

  const label = (yc, txt, size, fill, letters) => {
    for (let k = 0; k < letters; k++){
      const cx = (k + 0.5) / letters * W;
      ctx.save(); ctx.translate(cx, yc);
      ctx.font = `800 ${size}px "Arial Narrow",Arial,sans-serif`;
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = fill; ctx.fillText(txt, 0, 0);
      ctx.restore();
    }
  };
  label(H * 0.855, 'SOFT', 44, '#f4f6f8', 4);
  label(H * 0.755, 'F  O  R  M  U  L  A   1', 26, 'rgba(210,215,220,.72)', 4);
  label(H * 0.115, '372 / 720  R18', 22, 'rgba(150,155,160,.6)', 5);
  label(H * 0.185, 'CONTROL  TYRE', 20, 'rgba(120,125,130,.45)', 5);
  // tread crown: micro texture only
  ctx.fillStyle = 'rgba(255,255,255,0.018)';
  for (let i = 0; i < 2600; i++){
    const px = Math.random() * W, py = H * 0.40 + Math.random() * H * 0.20;
    ctx.fillRect(px, py, 2 + Math.random() * 5, 1);
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = THREE.RepeatWrapping; t.wrapT = THREE.ClampToEdgeWrapping;
  t.anisotropy = 16; t.needsUpdate = true;
  return t;
}
/* ---- steering wheel display + small dials ---------------------------------------- */
function buildWheelFace(){
  const { c, x: ctx } = makeCanvas(512, 256);
  ctx.fillStyle = '#07080a'; ctx.fillRect(0, 0, 512, 256);
  ctx.fillStyle = '#0d1014'; ctx.fillRect(96, 40, 320, 150);
  // shift lights
  for (let i = 0; i < 14; i++){
    const t = i / 13;
    ctx.fillStyle = t < 0.45 ? '#12d15a' : t < 0.78 ? '#ff2d20' : '#3a6bff';
    ctx.fillRect(104 + i * 22, 12, 15, 16);
  }
  ctx.fillStyle = '#e8ecef'; ctx.font = '800 74px "Arial Narrow",sans-serif';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('4', 190, 118);
  ctx.font = '700 30px "Arial Narrow",sans-serif'; ctx.fillStyle = '#d2203c';
  ctx.fillText('P 7', 320, 88);
  ctx.fillStyle = '#7f868d'; ctx.font = '600 24px "Arial Narrow",sans-serif';
  ctx.fillText('1:23.4', 320, 140);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace; t.needsUpdate = true;
  return t;
}

export { makeCanvas, hex, painter, buildLiverySide, buildLiveryTop, buildCarbonTexture, buildTyreWall, buildWheelFace };
