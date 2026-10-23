import * as THREE from 'three/webgpu';
import {
	Fn, If, Loop, Break, float, int, uint, vec2, vec3, vec4, ivec3, uvec2, uvec3,
	instancedArray, instanceIndex, vertexIndex, uniform, select, mix, clamp, smoothstep,
	min, max, abs, floor, fract, exp, length, normalize, cross, dot, sin,
	atomicAdd, atomicLoad, atomicStore, atomicMin, atomicMax, textureStore, texture, texture3D, uv, pass,
	workgroupArray, workgroupBarrier, workgroupId, invocationLocalIndex, cos,
	getViewPosition, interleavedGradientNoise, screenCoordinate, varying, positionWorld, positionView,
	normalView, normalMap, transformNormalToView, faceDirection, mx_noise_float, mx_noise_vec3,
	mx_fractal_noise_float, mx_worley_noise_float
} from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';

/** Material-lattice combustion coupled to sheet mechanics and a 3D pyro volume. */
export async function createSimulatedPaperBurning({ renderer, scene, camera, printTex }) {
//  Constants
// =====================================================================================

const PW = 0.297, PH = 0.210;                        // A4 sheet, metres
const NPX = 256, NPZ = 182, NP = NPX * NPZ;          // cloth / combustion lattice (≈1.16 mm)
const NFX = 128, NFY = 56, NFZ = 96;                 // pyro grid
const NFXY = NFX * NFY, NV = NFXY * NFZ, NC = NFX * NFZ;
const DX = 0.4 / NFX;                                // 3.125 mm voxels
const FMIN = new THREE.Vector3( - 0.2, 0, - 0.15 );
const FSIZE = new THREE.Vector3( NFX * DX, NFY * DX, NFZ * DX );
const SUB = 10;                                      // cloth substeps per frame
const SOLVE_PAIRS = 2;                               // Jacobi iteration pairs per substep
const FRAME_DT = 1 / 60;
const JACOBI = 24;                                   // pressure iterations (even)
const STEP = 0.0022, MAXSTEPS = 200;                 // volume march
const DTW = 1024, DTH = 724;                         // baked crease detail (≈0.29 mm)

const I = ( v ) => int( v );
const FMINn = vec3( FMIN.x, FMIN.y, FMIN.z );
const FSIZEn = vec3( FSIZE.x, FSIZE.y, FSIZE.z );

// =====================================================================================
//  CPU-side authoring: crumpled rest shape, fracture cells, material heterogeneity
// =====================================================================================

function mulberry32( a ) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul( a ^ a >>> 15, 1 | a ); t = t + Math.imul( t ^ t >>> 7, 61 | t ) ^ t; return ( ( t ^ t >>> 14 ) >>> 0 ) / 4294967296; }; }

function makeNoise( seed ) {
	const r = mulberry32( seed ), p = new Uint8Array( 512 ), gx = new Float32Array( 256 ), gy = new Float32Array( 256 );
	for ( let i = 0; i < 256; i ++ ) { p[ i ] = i; const a = r() * Math.PI * 2; gx[ i ] = Math.cos( a ); gy[ i ] = Math.sin( a ); }
	for ( let i = 255; i > 0; i -- ) { const j = Math.floor( r() * ( i + 1 ) ); const t = p[ i ]; p[ i ] = p[ j ]; p[ j ] = t; }
	for ( let i = 0; i < 256; i ++ ) p[ i + 256 ] = p[ i ];
	const f = ( t ) => t * t * t * ( t * ( t * 6 - 15 ) + 10 );
	const g = ( h, x, y ) => gx[ h ] * x + gy[ h ] * y;
	const n2 = ( x, y ) => {
		const X = Math.floor( x ), Y = Math.floor( y ), xf = x - X, yf = y - Y, xi = X & 255, yi = Y & 255;
		const u = f( xf ), v = f( yf );
		const a = g( p[ p[ xi ] + yi ], xf, yf ), b = g( p[ p[ xi + 1 ] + yi ], xf - 1, yf );
		const c = g( p[ p[ xi ] + yi + 1 ], xf, yf - 1 ), d = g( p[ p[ xi + 1 ] + yi + 1 ], xf - 1, yf - 1 );
		return 1.414 * ( ( a + ( b - a ) * u ) + ( ( c + ( d - c ) * u ) - ( a + ( b - a ) * u ) ) * v );
	};
	n2.fbm = ( x, y, o = 4 ) => { let s = 0, a = 0.5, fr = 1; for ( let i = 0; i < o; i ++ ) { s += a * n2( x * fr, y * fr ); fr *= 2.03; a *= 0.5; } return s; };
	return n2;
}

function buildSheet( seed ) {

	const rnd = mulberry32( seed );
	const nz = makeNoise( seed * 7 + 1 );
	const sstep = ( a, b, x ) => { const t = Math.min( 1, Math.max( 0, ( x - a ) / ( b - a ) ) ); return t * t * ( 3 - 2 * t ); };

	// --- crumple: superposed finite crease segments with tent profiles (sharp ridges, flat facets).
	//     Specified by slope rather than height so small creases stay as steep as big ones.
	const folds = [];
	const addFolds = ( n, r0, r1, s0, s1, l0, l1 ) => {
		for ( let i = 0; i < n; i ++ ) {
			const ang = rnd() * Math.PI, r = r0 + Math.pow( rnd(), 1.5 ) * ( r1 - r0 );
			folds.push( { cx: ( rnd() - 0.5 ) * PW * 1.15, cz: ( rnd() - 0.5 ) * PH * 1.15, nx: Math.cos( ang ), nz: Math.sin( ang ),
				r, a: r * ( s0 + rnd() * ( s1 - s0 ) ) * ( rnd() < 0.58 ? 1 : - 1 ), L: l0 + rnd() * ( l1 - l0 ) } );
		}
	};
	addFolds( 14, 0.03, 0.06, 0.06, 0.12, 0.14, 0.36 );
	addFolds( 150, 0.007, 0.024, 0.12, 0.30, 0.04, 0.16 );
	addFolds( 280, 0.0022, 0.007, 0.08, 0.22, 0.012, 0.05 );

	// spatial bins so each sample only visits creases that can reach it
	const BIN = 0.01, BX = Math.ceil( PW / BIN ) + 2, BZ = Math.ceil( PH / BIN ) + 2;
	const bins = Array.from( { length: BX * BZ }, () => [] );
	for ( const f of folds ) {
		const ext = f.L * 0.5 + f.r * 1.5;
		const hx = Math.abs( f.nz ) * ext + Math.abs( f.nx ) * f.r, hz = Math.abs( f.nx ) * ext + Math.abs( f.nz ) * f.r;
		const x0 = Math.max( 0, Math.floor( ( f.cx - hx + PW / 2 ) / BIN ) + 1 ), x1 = Math.min( BX - 1, Math.floor( ( f.cx + hx + PW / 2 ) / BIN ) + 1 );
		const z0 = Math.max( 0, Math.floor( ( f.cz - hz + PH / 2 ) / BIN ) + 1 ), z1 = Math.min( BZ - 1, Math.floor( ( f.cz + hz + PH / 2 ) / BIN ) + 1 );
		for ( let bz = z0; bz <= z1; bz ++ ) for ( let bx = x0; bx <= x1; bx ++ ) bins[ bz * BX + bx ].push( f );
	}
	const crumpleAt = ( x, z ) => {
		const bx = Math.min( BX - 1, Math.max( 0, Math.floor( ( x + PW / 2 ) / BIN ) + 1 ) ), bz = Math.min( BZ - 1, Math.max( 0, Math.floor( ( z + PH / 2 ) / BIN ) + 1 ) );
		let h = 0;
		for ( const f of bins[ bz * BX + bx ] ) {
			const dx = x - f.cx, dz = z - f.cz;
			const d = dx * f.nx + dz * f.nz;
			if ( Math.abs( d ) >= f.r ) continue;
			const t = - dx * f.nz + dz * f.nx;
			h += f.a * ( 1 - Math.abs( d ) / f.r ) * ( 1 - sstep( f.L * 0.5, f.L * 0.5 + f.r * 1.5, Math.abs( t ) ) );
		}
		return h;
	};

	const rest = new Float32Array( NP * 4 );
	const hs = new Float32Array( NP );
	for ( let iz = 0; iz < NPZ; iz ++ ) for ( let ix = 0; ix < NPX; ix ++ ) {
		hs[ iz * NPX + ix ] = crumpleAt( ( ix / ( NPX - 1 ) - 0.5 ) * PW, ( iz / ( NPZ - 1 ) - 0.5 ) * PH );
	}
	// high-pass crease detail the 1.16 mm lattice cannot carry: full-res crumple minus its
	// bilinear reconstruction from the lattice samples, in millimetres (used as a bump map)
	const detail = new Uint16Array( DTW * DTH * 4 );
	for ( let j = 0; j < DTH; j ++ ) for ( let i = 0; i < DTW; i ++ ) {
		const u = ( i + 0.5 ) / DTW, v = ( j + 0.5 ) / DTH;
		const hf = crumpleAt( ( u - 0.5 ) * PW, ( v - 0.5 ) * PH );
		const gx = u * ( NPX - 1 ), gz = v * ( NPZ - 1 );
		const x0 = Math.min( NPX - 2, Math.floor( gx ) ), z0 = Math.min( NPZ - 2, Math.floor( gz ) ), fx = gx - x0, fz = gz - z0;
		const hl = ( hs[ z0 * NPX + x0 ] * ( 1 - fx ) + hs[ z0 * NPX + x0 + 1 ] * fx ) * ( 1 - fz ) + ( hs[ ( z0 + 1 ) * NPX + x0 ] * ( 1 - fx ) + hs[ ( z0 + 1 ) * NPX + x0 + 1 ] * fx ) * fz;
		detail[ ( j * DTW + i ) * 4 ] = THREE.DataUtils.toHalfFloat( ( hf - hl ) * 1000 );
	}

	const sorted = Array.from( hs ).sort( ( a, b ) => a - b );
	const h0 = sorted[ Math.floor( NP * 0.12 ) ];
	for ( let i = 0; i < NP; i ++ ) {
		const ix = i % NPX, iz = Math.floor( i / NPX );
		rest[ i * 4 + 0 ] = ( ix / ( NPX - 1 ) - 0.5 ) * PW;
		rest[ i * 4 + 1 ] = Math.max( 0.00025, hs[ i ] - h0 + 0.00025 );
		rest[ i * 4 + 2 ] = ( iz / ( NPZ - 1 ) - 0.5 ) * PH;
		rest[ i * 4 + 3 ] = 1;
	}

	// --- fracture: domain-warped Voronoi with clustered seeds -> mix of large plates and small flakes
	const seeds = [];
	for ( let i = 0; i < 46; i ++ ) seeds.push( [ ( rnd() - 0.5 ) * PW, ( rnd() - 0.5 ) * PH ] );
	for ( let c = 0; c < 24; c ++ ) {
		const cx = ( rnd() - 0.5 ) * PW, cz = ( rnd() - 0.5 ) * PH, sp = 0.006 + rnd() * 0.022, n = 3 + Math.floor( rnd() * 11 );
		for ( let k = 0; k < n; k ++ ) {
			const a = rnd() * Math.PI * 2, r = sp * Math.sqrt( - 2 * Math.log( 1 - rnd() * 0.999 ) );
			seeds.push( [ cx + Math.cos( a ) * r, cz + Math.sin( a ) * r ] );
		}
	}
	const props = new Float32Array( NP * 4 );
	const shrinkN = new Float32Array( NP ), crumpleN = new Float32Array( NP );
	const cellOf = new Int32Array( NP );
	const cellRand = seeds.map( () => rnd() );
	for ( let i = 0; i < NP; i ++ ) {
		const x = rest[ i * 4 ], z = rest[ i * 4 + 2 ];
		const wx = x + 0.0055 * nz( x * 55, z * 55 ) + 0.0018 * nz( x * 210 + 31, z * 210 );
		const wz = z + 0.0055 * nz( x * 55 + 17, z * 55 - 9 ) + 0.0018 * nz( x * 210, z * 210 + 57 );
		let best = 1e9, bi = 0;
		for ( let s = 0; s < seeds.length; s ++ ) {
			const dx = wx - seeds[ s ][ 0 ], dz = wz - seeds[ s ][ 1 ], d = dx * dx + dz * dz;
			if ( d < best ) { best = d; bi = s; }
		}
		cellOf[ i ] = bi;
		props[ i * 4 + 0 ] = bi;
		// in-plane conductivity heterogeneity (fibre density / moisture)
		const cn = 0.5 + 0.5 * nz.fbm( x * 22 + 3, z * 22 - 4, 5 ), cm = 0.5 + 0.5 * nz( x * 90 - 11, z * 90 + 5 );
		props[ i * 4 + 1 ] = 0.25 + 1.6 * sstep( 0.25, 0.75, cn ) * ( 0.55 + 0.45 * cm ) + 0.15 * nz( x * 400, z * 400 );
		// ignition-temperature heterogeneity (sizing, ink, moisture): the main source of front fingering
		props[ i * 4 + 2 ] = Math.min( 1, Math.max( 0, 0.5 + 0.6 * nz.fbm( x * 26 - 8, z * 26 + 2, 4 ) + 0.35 * nz( x * 110 + 4, z * 110 - 7 ) + 0.3 * nz( x * 330 - 2, z * 330 + 9 ) ) );
		props[ i * 4 + 3 ] = cellRand[ bi ];
		// char shrinkage heterogeneity: uneven contraction is what buckles char into crumpled flakes
		shrinkN[ i ] = Math.max( 0, 0.3 + 1.4 * ( 0.5 + 0.5 * nz.fbm( x * 95 + 21, z * 95 - 13, 3 ) ) );
		crumpleN[ i ] = nz( x * 70 + cellRand[ bi ] * 17, z * 70 );
	}
	// --- char flake goal shapes for shape matching. Each fracture cell gets its own curled, shrunk,
	//     crumpled rest shape: pyrolysis shrinks the exposed face more than the back, so flakes roll
	//     up about a random axis (tighter for small flakes), some cup the other way and land as domes.
	const nCells = seeds.length;
	const cellCount = new Int32Array( nCells );
	for ( let i = 0; i < NP; i ++ ) cellCount[ cellOf[ i ] ] ++;
	const cellStart = new Int32Array( nCells + 1 );
	for ( let c = 0; c < nCells; c ++ ) cellStart[ c + 1 ] = cellStart[ c ] + cellCount[ c ];
	const cellList = new Int32Array( NP ), fill = cellStart.slice( 0, nCells );
	for ( let i = 0; i < NP; i ++ ) cellList[ fill[ cellOf[ i ] ] ++ ] = i;
	const goal = new Float32Array( NP * 4 );
	for ( let c = 0; c < nCells; c ++ ) {
		let cx = 0, cz = 0;
		for ( let k = cellStart[ c ]; k < cellStart[ c + 1 ]; k ++ ) { const i = cellList[ k ]; cx += rest[ i * 4 ]; cz += rest[ i * 4 + 2 ]; }
		const n = Math.max( 1, cellCount[ c ] ); cx /= n; cz /= n;
		const size = Math.sqrt( n ) * ( PW / ( NPX - 1 ) );
		const th = rnd() * Math.PI, ax = Math.cos( th ), az = Math.sin( th ), px = - az, pz = ax;
		const Rc = Math.min( 0.016, Math.max( 0.0022, size * ( 0.1 + 0.32 * rnd() ) ) );
		const dir = rnd() < 0.8 ? 1 : - 1;
		const s = 0.72 + 0.12 * rnd();
		const twist = ( rnd() - 0.5 ) * 0.6 / Math.max( size, 0.004 );
		for ( let k = cellStart[ c ]; k < cellStart[ c + 1 ]; k ++ ) {
			const i = cellList[ k ];
			const dx = rest[ i * 4 ] - cx, dz = rest[ i * 4 + 2 ] - cz;
			const a = ( dx * ax + dz * az ) * s, d = ( dx * px + dz * pz ) * s;
			const phi = Math.max( - 3.4, Math.min( 3.4, d / Rc + a * twist * 0.15 ) );
			const along = a, across = Rc * Math.sin( phi ), up = dir * Rc * ( 1 - Math.cos( phi ) );
			const wob = 0.0012 * nz( rest[ i * 4 ] * 160 + c, rest[ i * 4 + 2 ] * 160 );
			goal[ i * 4 + 0 ] = cx + along * ax + across * px;
			goal[ i * 4 + 1 ] = up + rest[ i * 4 + 1 ] * 0.6 + wob;
			goal[ i * 4 + 2 ] = cz + along * az + across * pz;
			goal[ i * 4 + 3 ] = 1;
		}
	}

	return { rest, props, shrinkN, crumpleN, detail, cellStart, cellList, goal, nCells };

}
const U = {
	dt: uniform( FRAME_DT / SUB ), fdt: uniform( FRAME_DT ), bdt: uniform( FRAME_DT / SUB ), time: uniform( 0 ),
	ignitePos: uniform( new THREE.Vector3( - PW / 2, 0, PH / 2 ) ), ignite: uniform( 0 ),
	// cloth
	aero: uniform( 1.6 ), aeroT: uniform( 0.25 ), lift: uniform( 9.0 ), friction: uniform( 0.86 ),
	bend: uniform( 0.8 ), shearC: uniform( 0.02 ), wS: uniform( 0.28 ), wT: uniform( 0.2 ),
	shrink: uniform( 0.3 ), glueBase: uniform( 0.02 ), glueVar: uniform( 0.16 ), ashCut: uniform( 0.6 ), brittleT: uniform( 0.25 ), brittleVar: uniform( 1.1 ), tearGap: uniform( 0.7 ), curl: uniform( 0.0 ), crumple: uniform( 1.5e-5 ), charComp: uniform( 1.5 ), charDamp: uniform( 18.0 ), charBend: uniform( 0.3 ), sleep: uniform( 0.95 ), flakeK: uniform( 0.6 ), oxid: uniform( 1.0 ), heatCurl: uniform( 0.0 ), pop: uniform( 0.5 ),
	// combustion on the sheet
	diff: uniform( 110.0 ), react: uniform( 12.0 ), heat: uniform( 5.0 ), cool: uniform( 1.4 ), airC: uniform( 0.5 ), scorch: uniform( 1.6 ),
	igBase: uniform( 0.7 ), igVar: uniform( 1.7 ),
	// pyro
	emitFuel: uniform( 6.0 ), emitHeat: uniform( 3.5 ), emitHeat2: uniform( 0.3 ),
	burnRate: uniform( 15.0 ), burnHeat: uniform( 2.4 ), flameGain: uniform( 9.0 ), soot: uniform( 0.10 ), expand: uniform( 0.35 ),
	coolT: uniform( 6.0 ), flameDecay: uniform( 34.0 ), smokeDecay: uniform( 0.9 ), smoulderSmoke: uniform( 2.0 ), smoulderHeat: uniform( 4.5 ),
	buoy: uniform( 4.5 ), vort: uniform( 22.0 ), turb: uniform( 4.5 ), velDiss: uniform( 0.4 ),
	// look
	fireEmit: uniform( 38.0 ), fireTmax: uniform( 4.5 ), flameLo: uniform( 0.14 ), flameHi: uniform( 0.6 ), flameDetail: uniform( 1.2 ), fireAbs: uniform( 18.0 ), smokeAbs: uniform( 30.0 ), smokeAmb: uniform( 1.0 ),
	wind: uniform( new THREE.Vector3( - 2.6, 0, 0.65 ) ), windAmt: uniform( 0 ), sootKeep: uniform( 1 ), windDrag: uniform( 2.4 ), windLift: uniform( 0.9 ), windEddy: uniform( 4.0 ),
	lightNear: uniform( 0.55 ), lightFar: uniform( 0.30 ),
	projInv: uniform( new THREE.Matrix4() ), camWorld: uniform( new THREE.Matrix4() ), camPos: uniform( new THREE.Vector3() )
};

// =====================================================================================
//  GPU buffers
// =====================================================================================

const sheet = buildSheet( 20241 );

const burnInit = new Float32Array( NP * 4 );
for ( let i = 0; i < NP; i ++ ) burnInit[ i * 4 ] = 1;

const restBuf = instancedArray( sheet.rest, 'vec4' );
const posBuf = instancedArray( new Float32Array( sheet.rest ), 'vec4' );
const velBuf = instancedArray( NP, 'vec4' );
const predA = instancedArray( NP, 'vec4' );
const predB = instancedArray( NP, 'vec4' );
const nrmBuf = instancedArray( NP, 'vec4' );
const burnA = instancedArray( burnInit, 'vec4' );   // x fuel, y temperature, z scorch, w pyrolysis rate
const burnB = instancedArray( new Float32Array( burnInit ), 'vec4' );
const propsBuf = instancedArray( sheet.props, 'vec4' ); // x cell id, y conductivity, z reactivity, w cell random
const shrinkBuf = instancedArray( sheet.shrinkN, 'float' );
const crumpleBuf = instancedArray( sheet.crumpleN, 'float' );

const velFA = instancedArray( NV, 'vec4' ), velFB = instancedArray( NV, 'vec4' );
const scalA = instancedArray( NV, 'vec4' ), scalB = instancedArray( NV, 'vec4' ); // x temperature, y fuel, z soot, w flame
const presA = instancedArray( NV, 'float' ), presB = instancedArray( NV, 'float' );
const divBuf = instancedArray( NV, 'float' ), expBuf = instancedArray( NV, 'float' );
const curlBuf = instancedArray( NV, 'vec4' );
const emitFuel = instancedArray( NV, 'int' ).toAtomic();
const emitHeat = instancedArray( NV, 'int' ).toAtomic();
const emitSmoke = instancedArray( NV, 'int' ).toAtomic();
const sootAcc = instancedArray( NC, 'int' ).toAtomic();
const colBuf = instancedArray( NC, 'vec4' );
const bboxAtom = instancedArray( 8, 'int' ).toAtomic();
const bboxBuf = instancedArray( 2, 'vec4' );

const detailTex = new THREE.DataTexture( sheet.detail, DTW, DTH, THREE.RGBAFormat, THREE.HalfFloatType );
detailTex.magFilter = detailTex.minFilter = THREE.LinearFilter;
detailTex.needsUpdate = true;

// artwork printed on the sheet (centre offset and width in metres, sheet frame)
const PRINT_W = PW * 0.86, PRINT_CX = 0.0, PRINT_CZ = - 0.003;
const printAspect = uniform(printTex.image.width / printTex.image.height);
const volTex = new THREE.Storage3DTexture( NFX, NFY, NFZ );
volTex.type = THREE.HalfFloatType; volTex.format = THREE.RGBAFormat; volTex.generateMipmaps = false;
volTex.magFilter = volTex.minFilter = THREE.LinearFilter;
const groundTex = new THREE.StorageTexture( NFX, NFZ );
groundTex.type = THREE.HalfFloatType; groundTex.generateMipmaps = false;
groundTex.magFilter = groundTex.minFilter = THREE.LinearFilter;

// =====================================================================================
//  Shared TSL helpers
// =====================================================================================

const charOf = ( b ) => float( 1 ).sub( b.x );
// finale: each flake breaks loose at its own gust strength, so the pile peels away progressively
const windRelease = ( cellRnd ) => smoothstep( cellRnd.mul( 0.45 ).add( 0.04 ), cellRnd.mul( 0.45 ).add( 0.14 ), U.windAmt );

// Glue between fracture cells survives pyrolysis (char-to-char bonds hold, so a burnt region contracts
// as one mass) and fails once oxidation has weakened either side past a per-pair threshold. Fully
// oxidised particles (ash) lose every link and vanish. The link state is the ash level in [0, 1].
const pairThr = ( ca, cb ) => fract( sin( min( ca, cb ).mul( 12.9898 ).add( max( ca, cb ).mul( 78.233 ) ) ).mul( 43758.5453 ) ).mul( U.glueVar ).add( U.glueBase );
const ashOf = ( b ) => clamp( b.z.sub( 1.0 ), 0.0, 1.0 );
// Spent char embrittles as it cools: each cell cracks free of its neighbours at its own temperature
// (after the hot contraction has pulled the burnt region together), encoded as +10 on the link state.
// The paper also tears along the pyrolysis front (char beside sound paper has no strength), so the
// contracting char does not drag the unburnt sheet. Link state: x = ash (+10 when embrittled), y = char.
const linkOf = ( b, cellRnd ) => vec2( ashOf( b ).add( select( charOf( b ).greaterThan( 0.97 ).and( b.y.lessThan( cellRnd.mul( U.brittleVar ).add( U.brittleT ) ) ), 10.0, 0.0 ) ), charOf( b ) );
const connected = ( ca, cb, la, lb ) => ca.equal( cb ).and( max( la.x.mod( 10.0 ), lb.x.mod( 10.0 ) ).lessThan( U.ashCut ) )
	.or( ca.notEqual( cb ).and( max( la.x, lb.x ).lessThan( pairThr( ca, cb ) ) ).and( abs( la.y.sub( lb.y ) ).lessThan( U.tearGap ) ).and( U.windAmt.lessThan( 0.2 ) ) );
// per-particle link state cached once per frame: x cell id, y ash/embrittlement, z char, w cell random
const linkBuf = instancedArray( NP, 'vec4' );
const connL = ( Li, Lj ) => connected( Li.x, Lj.x, Li.yz, Lj.yz );

// Connectivity only changes once per frame, so every lattice neighbour the solvers and the renderer
// use is resolved once into a 24-bit mask per particle; each later test is a single bit lookup.
const NB_OFFS = [];
for ( const r of [ 1, 2, 4, 8, 12, 40 ] ) NB_OFFS.push( [ r, 0 ], [ - r, 0 ], [ 0, r ], [ 0, - r ] );
for ( const r of [ 1, 2 ] ) NB_OFFS.push( [ r, r ], [ - r, - r ], [ - r, r ], [ r, - r ] );
const nbBit = ( ox, oz ) => { const k = NB_OFFS.findIndex( ( o ) => o[ 0 ] === ox && o[ 1 ] === oz ); if ( k < 0 ) throw new Error( `no bit for ${ ox },${ oz }` ); return k; };
const connBuf = instancedArray( NP, 'uint' );
const hasNb = ( mask, ox, oz ) => mask.shiftRight( uint( nbBit( ox, oz ) ) ).bitAnd( uint( 1 ) ).equal( uint( 1 ) );

const makeSampler = ( buf ) => Fn( ( [ p ] ) => {
	const g = p.sub( FMINn ).div( DX ).sub( 0.5 );
	const gc = clamp( g, vec3( 0.0 ), vec3( NFX - 1.001, NFY - 1.001, NFZ - 1.001 ) ).toVar();
	const fl = floor( gc );
	const f = gc.sub( fl ).toVar();
	const i0 = ivec3( fl ).toVar();
	const b = i0.x.add( i0.y.mul( I( NFX ) ) ).add( i0.z.mul( I( NFXY ) ) ).toVar();
	const e = ( o ) => buf.element( b.add( I( o ) ) );
	const x00 = mix( e( 0 ), e( 1 ), f.x ), x10 = mix( e( NFX ), e( NFX + 1 ), f.x );
	const x01 = mix( e( NFXY ), e( NFXY + 1 ), f.x ), x11 = mix( e( NFXY + NFX ), e( NFXY + NFX + 1 ), f.x );
	return mix( mix( x00, x10, f.y ), mix( x01, x11, f.y ), f.z );
} );
const sampleVelA = makeSampler( velFA );
const sampleScalA = makeSampler( scalA );

const voxOf = ( id ) => ( { i: id.mod( I( NFX ) ), j: id.div( I( NFX ) ).mod( I( NFY ) ), k: id.div( I( NFXY ) ) } );
const cellCenter = ( i, j, k ) => vec3( float( i ), float( j ), float( k ) ).add( 0.5 ).mul( DX ).add( FMINn );
const vidx = ( i, j, k ) => i.add( j.mul( I( NFX ) ) ).add( k.mul( I( NFXY ) ) );
const atC = ( buf, i, j, k ) => buf.element( vidx( clamp( i, I( 0 ), I( NFX - 1 ) ), clamp( j, I( 0 ), I( NFY - 1 ) ), clamp( k, I( 0 ), I( NFZ - 1 ) ) ) );

// approximate blackbody ramp, t in [0,1]
const fireColor = Fn( ( [ t ] ) => {
	const c1 = vec3( 1.0, 0.16, 0.02 ), c2 = vec3( 1.0, 0.34, 0.05 ), c3 = vec3( 1.0, 0.56, 0.16 ), c4 = vec3( 1.0, 0.82, 0.50 );
	return mix( mix( mix( c1, c2, smoothstep( 0.0, 0.35, t ) ), c3, smoothstep( 0.35, 0.7, t ) ), c4, smoothstep( 0.7, 1.0, t ) );
} );

// =====================================================================================
//  Sheet: XPBD (small-step, Jacobi) with heat-driven shrink, buckling, and cell fracture
// =====================================================================================

const kIntegrate = Fn( () => {
	const id = I( instanceIndex );
	const p = posBuf.element( id ).xyz.toVar();
	const v = velBuf.element( id ).xyz.toVar();
	const b = burnA.element( id ).toVar();
	const pr = propsBuf.element( id );
	const ch = charOf( b );
	const sigma = ch.mul( - 0.5 ).add( 1.0 ).toVar();        // areal density drops as cellulose pyrolyses
	const n = nrmBuf.element( id ).xyz.toVar();
	const inDomain = p.x.greaterThan( FMIN.x ).and( p.x.lessThan( FMIN.x + FSIZE.x ) ).and( p.z.greaterThan( FMIN.z ) ).and( p.z.lessThan( FMIN.z + FSIZE.z ) ).and( p.y.lessThan( FSIZE.y ) );
	const air = select( inDomain, sampleVelA( p ).xyz, U.wind.mul( U.windAmt ) );
	const rel = air.sub( v ).toVar();
	const vn = dot( rel, n );
	const aero = n.mul( vn.mul( abs( vn ) ) ).mul( U.aero ).add( rel.sub( n.mul( vn ) ).mul( U.aeroT ) ).div( sigma );
	// buoyant lift from the flame sheet sitting on the burning band
	const lift = smoothstep( 0.8, 3.0, b.y ).mul( b.x.mul( 0.7 ).add( 0.3 ) ).mul( U.lift );
	// char cracking: a short impulse window as a cell crosses its break threshold (stress release)
	const win = smoothstep( 0.86, 0.9, ch ).mul( smoothstep( 0.97, 0.93, ch ) );
	const h1 = fract( sin( pr.x.mul( 91.7 ) ).mul( 47453.1 ) ), h2 = fract( sin( pr.x.mul( 37.3 ) ).mul( 15731.7 ) );
	const awayDir = normalize( vec3( p.x.sub( U.ignitePos.x ), 0.0, p.z.sub( U.ignitePos.z ) ).add( vec3( h1.sub( 0.5 ), 0, h2.sub( 0.5 ) ).mul( 2.5 ) ).negate() );
	const pop = awayDir.mul( 0.6 ).add( vec3( 0, 1.0, 0 ) ).mul( win ).mul( U.pop ).mul( pr.w.mul( 1.5 ).add( 0.5 ) ).mul( 14.0 );
	// finale gust on light char. Wind is structured: gust patches travel downwind (bursts and lulls),
	// eddies swirl and lift, and pressure lift depends on how each bit of a flake faces the flow,
	// with per-point flutter, so flakes tumble and flip instead of sliding as one sheet.
	const release = windRelease( pr.w ).toVar();
	const gustRel = vec3( rel.x, 0, rel.z );
	const gq = vec3( p.x.mul( 8.0 ).sub( U.wind.x.mul( U.time ).mul( 6.0 ) ), p.z.mul( 8.0 ).sub( U.wind.z.mul( U.time ).mul( 6.0 ) ), U.time.mul( 0.5 ) );
	const gustPatch = smoothstep( - 0.3, 0.5, mx_noise_float( gq ) ).mul( 1.3 ).add( 0.08 );
	const eddy = mx_noise_vec3( p.mul( 28.0 ).add( vec3( U.time.mul( 1.7 ), U.time.mul( 2.3 ), U.time.mul( - 1.1 ) ) ) ).mul( U.windEddy );
	const restP = restBuf.element( id ).xyz;
	const flutter = sin( U.time.mul( 13.0 ).add( restP.x.mul( 420.0 ) ).add( restP.z.mul( 310.0 ) ) ).mul( 0.6 ).add( sin( U.time.mul( 5.1 ).add( pr.w.mul( 23.0 ) ) ).mul( 0.4 ) );
	const faceLift = abs( n.y ).oneMinus().mul( 0.9 ).add( 0.2 );
	const windF = U.windAmt.mul( release ).mul( smoothstep( 0.6, 0.95, ch ) ).mul( gustPatch ).div( sigma ).toVar();
	const gustAcc = gustRel.mul( U.windDrag )
		.add( vec3( 0, dot( gustRel, gustRel ).mul( U.windLift ).mul( faceLift ).mul( flutter.add( 0.45 ) ), 0 ) )
		.add( eddy.mul( length( gustRel ).add( 0.3 ) ) )
		.mul( windF );
	const acc = vec3( 0, - 9.81, 0 ).add( aero ).add( vec3( 0, lift, 0 ) ).add( pop ).add( gustAcc );
	v.addAssign( acc.mul( U.dt ) );
	// cooled char is limp and dead: strong damping lets broken flakes settle instead of buzzing
	const coldChar = ch.mul( smoothstep( 1.2, 0.4, b.y ) ).mul( release.oneMinus() );
	v.mulAssign( exp( U.dt.mul( coldChar.mul( U.charDamp ).add( 0.8 ) ).negate() ) );
	predA.element( id ).assign( vec4( p.add( v.mul( U.dt ) ), 1 ) );
} )().compute( NP ).setName( 'sheetIntegrate' );

// membrane stencil: [dx, dz, type] 0 stretch, 1 shear, 2 long-range tension limit
const OFFS = [
	[ 1, 0, 0 ], [ - 1, 0, 0 ], [ 0, 1, 0 ], [ 0, - 1, 0 ],
	[ 1, 1, 1 ], [ 1, - 1, 1 ], [ - 1, 1, 1 ], [ - 1, - 1, 1 ],
	[ 12, 0, 2 ], [ - 12, 0, 2 ], [ 0, 12, 2 ], [ 0, - 12, 2 ],
	[ 40, 0, 2 ], [ - 40, 0, 2 ], [ 0, 40, 2 ], [ 0, - 40, 2 ]
];

const nbInfo = ( ix, iz, ox, oz ) => {
	const jx = ix.add( I( ox ) ), jz = iz.add( I( oz ) );
	const conds = [];
	if ( ox > 0 ) conds.push( jx.lessThan( I( NPX ) ) );
	if ( ox < 0 ) conds.push( jx.greaterThanEqual( I( 0 ) ) );
	if ( oz > 0 ) conds.push( jz.lessThan( I( NPZ ) ) );
	if ( oz < 0 ) conds.push( jz.greaterThanEqual( I( 0 ) ) );
	const inside = conds.reduce( ( a, c ) => a.and( c ) );
	const jid = clamp( jz, I( 0 ), I( NPZ - 1 ) ).mul( I( NPX ) ).add( clamp( jx, I( 0 ), I( NPX - 1 ) ) );
	return { inside, jid };
};

const makeSolve = ( src, dst ) => Fn( () => {
	const id = I( instanceIndex );
	const ix = id.mod( I( NPX ) ), iz = id.div( I( NPX ) );
	const mask = connBuf.element( id ).toVar();
	const Pi = src.element( id ).xyz.toVar();
	const Ri = restBuf.element( id ).xyz.toVar();
	const pr = propsBuf.element( id ).toVar();
	const Li = linkBuf.element( id ).toVar();
	const chi = Li.z;
	const dS = vec3( 0 ).toVar(), dB = vec3( 0 ).toVar(), dT = vec3( 0 ).toVar();

	// --- membrane: stretch + shear distance constraints, plus long-range tension-only limits
	for ( const [ ox, oz, type ] of OFFS ) {
		const { inside, jid } = nbInfo( ix, iz, ox, oz );
		const Pj = src.element( jid ).xyz;
		const Rj = restBuf.element( jid ).xyz;
		const Lj = linkBuf.element( jid );
		const chj = Lj.z;
		// long-range strain limits only bind sound paper (they would tether separated char flakes)
		const valid = select( hasNb( mask, ox, oz ), 1.0, 0.0 ).mul( type === 2 ? smoothstep( 0.5, 0.2, max( chi, chj ) ) : float( 1.0 ) );
		const s = chi.add( chj ).mul( 0.5 ).mul( U.shrink ).mul( shrinkBuf.element( id ).add( shrinkBuf.element( jid ) ).mul( 0.5 ) ).oneMinus();
		const rest = length( Ri.sub( Rj ) ).mul( s );
		const d = Pi.sub( Pj );
		const len = max( length( d ), 1e-9 );
		let C = len.sub( rest );
		if ( type === 2 ) C = max( C, 0.0 );
		// char may strain in-plane: a doubly-curved (cupped) char flake cannot stay isometric
		const comp = ( type === 1 ? U.shearC : float( 0.0 ) ).add( chi.add( chj ).mul( 0.5 ).mul( U.charComp ) );
		const k = float( 1 ).div( comp.add( 2.0 ) ); // mass-independent: keeps the Jacobi sweep inside its stability bound
		const corr = d.mul( k.mul( C ).div( len ).negate() ).mul( valid );
		if ( type === 2 ) dT.addAssign( corr ); else dS.addAssign( corr );
	}

	// --- bending: gather this particle's own curvature-constraint step and the equal-and-opposite
	//     reactions from every neighbour whose stencil contains it (momentum-conserving)
	for ( const ring of BEND_RINGS ) {
		const acc = bendBuf.element( id.mul( I( NBR ) ).add( I( ring.slot ) ) ).xyz.toVar();
		for ( const [ ox, oz ] of ring.st ) {
			const { inside, jid } = nbInfo( ix, iz, ox, oz );
			const v = select( hasNb( mask, ox, oz ), 1.0, 0.0 );
			const bj = bendBuf.element( jid.mul( I( NBR ) ).add( I( ring.slot ) ) );
			acc.subAssign( bj.xyz.mul( bj.w ).mul( v ) );
		}
		dB.addAssign( acc );
	}
	const dq = dS.mul( U.wS ).add( dT.mul( U.wT ) ).add( dB ).toVar();
	const Q = Pi.add( dq.mul( min( float( 1 ), float( 0.002 ).div( length( dq ).add( 1e-12 ) ) ) ) ).toVar();
	const yMin = pr.w.mul( 0.0005 ).add( 0.00012 );
	Q.y.assign( max( Q.y, yMin ) );
	dst.element( id ).assign( vec4( Q, 1 ) );
} )().compute( NP );

// Bending constraint per particle and stencil: C = (P_i − mean P_j)·n − c, the discrete Laplacian
// (curvature vector) measured along the co-rotated normal. Linear in out-of-plane displacement, so
// the crumple holds under gravity. Axis and diagonal stencils at several radii keep it isotropic
// (axis-only stencils let char buckle into a lattice-aligned egg-crate). Pyrolysis rewrites the
// target c: char curls, cups and crumples; hot paper lifts. Each slot stores the PBD step Δλ·n (own
// correction) and 1/cnt (each neighbour's reaction share).
const axisSt = ( r ) => [ [ r, 0 ], [ - r, 0 ], [ 0, r ], [ 0, - r ] ];
const diagSt = ( r ) => [ [ r, r ], [ - r, - r ], [ - r, r ], [ r, - r ] ];
const BEND_RINGS = [
	{ st: axisSt( 1 ), d2: 1, kr: 0.18 }, { st: diagSt( 1 ), d2: 2, kr: 0.13 },
	{ st: axisSt( 2 ), d2: 4, kr: 0.15 }, { st: diagSt( 2 ), d2: 8, kr: 0.11 },
	{ st: axisSt( 4 ), d2: 16, kr: 0.14 }, { st: axisSt( 8 ), d2: 64, kr: 0.12, paperOnly: true }
].map( ( r, slot ) => ( { ...r, slot } ) );
const NBR = BEND_RINGS.length;
const bendBuf = instancedArray( NP * NBR, 'vec4' );

const makeBendEval = ( src ) => Fn( () => {
	const id = I( instanceIndex );
	const ix = id.mod( I( NPX ) ), iz = id.div( I( NPX ) );
	const mask = connBuf.element( id ).toVar();
	const Pi = src.element( id ).xyz.toVar();
	const Ri = restBuf.element( id ).xyz.toVar();
	const bi = burnA.element( id ).toVar();
	const pr = propsBuf.element( id ).toVar();
	const Li = linkBuf.element( id ).toVar();
	const chi = Li.z;
	const hti = smoothstep( 0.35, 1.1, bi.y ).mul( chi.oneMinus() ).toVar();
	// crumple target kept smooth (≈1.5 cm wavelength) so all stencils agree on it; each flake also
	// curls with its own strength (cell random), the dominant look of burnt paper
	const crN = crumpleBuf.element( id );
	const curv = chi.mul( U.curl.mul( pr.w.mul( 1.4 ).add( 0.3 ) ).negate().add( crN.mul( U.crumple ) ) )
		.sub( hti.mul( U.heatCurl ) ).toVar();
	// relaxation drops on char: its curl/crumple targets fight the membrane, and the reciprocal Jacobi
	// gather would otherwise over-relax into a checkerboard limit cycle (flakes that never settle)
	const stiff = U.bend.mul( mix( float( 1.0 ), U.charBend, chi ) ).toVar();
	const safeN = ( v ) => v.div( max( length( v ), 1e-12 ) );
	const normalOf = ( tx, tz ) => safeN( cross( tz, tx ) );
	for ( const ring of BEND_RINGS ) {
		const nb = ring.st.map( ( [ ox, oz ] ) => {
			const { inside, jid } = nbInfo( ix, iz, ox, oz );
			const v = select( hasNb( mask, ox, oz ), 1.0, 0.0 ).toVar();
			return { v, P: src.element( jid ).xyz, R: restBuf.element( jid ).xyz };
		} );
		const cnt = nb[ 0 ].v.add( nb[ 1 ].v ).add( nb[ 2 ].v ).add( nb[ 3 ].v ).toVar();
		const ok = nb[ 0 ].v.add( nb[ 1 ].v ).greaterThan( 0.5 ).and( nb[ 2 ].v.add( nb[ 3 ].v ).greaterThan( 0.5 ) );
		const inv = float( 1 ).div( max( cnt, 1.0 ) ).toVar();
		const avgP = nb[ 0 ].P.mul( nb[ 0 ].v ).add( nb[ 1 ].P.mul( nb[ 1 ].v ) ).add( nb[ 2 ].P.mul( nb[ 2 ].v ) ).add( nb[ 3 ].P.mul( nb[ 3 ].v ) ).mul( inv );
		const avgR = nb[ 0 ].R.mul( nb[ 0 ].v ).add( nb[ 1 ].R.mul( nb[ 1 ].v ) ).add( nb[ 2 ].R.mul( nb[ 2 ].v ) ).add( nb[ 3 ].R.mul( nb[ 3 ].v ) ).mul( inv );
		const side = ( key, a, b, c ) => mix( c, nb[ a ][ key ], nb[ a ].v ).sub( mix( c, nb[ b ][ key ], nb[ b ].v ) );
		const nR = normalOf( side( 'R', 0, 1, Ri ), side( 'R', 2, 3, Ri ) );
		const nP = normalOf( side( 'P', 0, 1, Pi ), side( 'P', 2, 3, Pi ) ).toVar();
		const c = dot( Ri.sub( avgR ), nR ).add( curv.mul( ring.d2 ) );
		const C = dot( Pi.sub( avgP ), nP ).sub( c );
		const dl = C.negate().div( inv.add( 1.0 ) ).mul( stiff ).mul( ring.kr ).mul( select( ok, 1.0, 0.0 ) ).mul( ring.paperOnly ? chi.oneMinus() : float( 1.0 ) );
		bendBuf.element( id.mul( I( NBR ) ).add( I( ring.slot ) ) ).assign( vec4( nP.mul( dl ), inv ) );
	}
} )().compute( NP );

const kBendA = makeBendEval( predA ).setName( 'bendEvalA' );
const kBendB = makeBendEval( predB ).setName( 'bendEvalB' );

const kSolveAB = makeSolve( predA, predB ).setName( 'sheetSolveAB' );
const kSolveBA = makeSolve( predB, predA ).setName( 'sheetSolveBA' );

// =====================================================================================
//  Char flakes: per-fracture-cell shape matching (Müller 2005) toward authored curled goal
//  shapes, with the rotation extracted by the robust quaternion polar iteration (Müller 2016).
//  Only pyrolysed particles take part, so a cell curls progressively as the front crosses it.
//  Unconditionally stable and momentum-conserving: flakes curl, lift, tumble and pile up.
// =====================================================================================

const NCELL = sheet.nCells;
const cellStartBuf = instancedArray( sheet.cellStart, 'int' );
const cellListBuf = instancedArray( sheet.cellList, 'int' );
const goalBuf = instancedArray( sheet.goal, 'vec4' );
const cellRot = instancedArray( new Float32Array( NCELL * 4 ).map( ( _, i ) => ( i % 4 === 3 ? 1 : 0 ) ), 'vec4' ); // quaternion (warm start)
const cellCom = instancedArray( NCELL, 'vec4' );   // xyz current centroid, w total weight
const cellQbar = instancedArray( NCELL, 'vec4' );  // goal-shape centroid of the participating subset
const SMW = 64;

const flakeWeight = ( b ) => smoothstep( 0.72, 0.93, charOf( b ) ).mul( select( ashOf( b ).greaterThan( U.ashCut ), 0.0, 1.0 ) );

const quatMul = ( a, b ) => vec4(
	a.w.mul( b.x ).add( a.x.mul( b.w ) ).add( a.y.mul( b.z ) ).sub( a.z.mul( b.y ) ),
	a.w.mul( b.y ).sub( a.x.mul( b.z ) ).add( a.y.mul( b.w ) ).add( a.z.mul( b.x ) ),
	a.w.mul( b.z ).add( a.x.mul( b.y ) ).sub( a.y.mul( b.x ) ).add( a.z.mul( b.w ) ),
	a.w.mul( b.w ).sub( a.x.mul( b.x ) ).sub( a.y.mul( b.y ) ).sub( a.z.mul( b.z ) )
);
const quatRotate = ( q, v ) => {
	const t = cross( q.xyz, v ).mul( 2.0 );
	return v.add( t.mul( q.w ) ).add( cross( q.xyz, t ) );
};

const kShapeReduce = Fn( () => {
	const cell = I( workgroupId.x );
	const lid = I( invocationLocalIndex );
	const s0 = workgroupArray( 'vec4', SMW ), s1 = workgroupArray( 'vec4', SMW );
	const s2 = workgroupArray( 'vec4', SMW ), s3 = workgroupArray( 'vec4', SMW ), s4 = workgroupArray( 'vec4', SMW );
	const a0 = vec4( 0 ).toVar(), a1 = vec4( 0 ).toVar(), a2 = vec4( 0 ).toVar(), a3 = vec4( 0 ).toVar(), a4 = vec4( 0 ).toVar();
	const start = cellStartBuf.element( cell ), end = cellStartBuf.element( cell.add( I( 1 ) ) );
	Loop( { start: start.add( lid ), end, type: 'int', condition: '<', update: SMW }, ( { i } ) => {
		const pid = cellListBuf.element( i );
		const w = flakeWeight( burnA.element( pid ) );
		const p = predA.element( pid ).xyz;
		const q = goalBuf.element( pid ).xyz;
		a0.addAssign( vec4( p.mul( w ), w ) );
		a1.addAssign( vec4( q.mul( w ), 0 ) );
		a2.addAssign( vec4( q.mul( p.x.mul( w ) ), 0 ) );
		a3.addAssign( vec4( q.mul( p.y.mul( w ) ), 0 ) );
		a4.addAssign( vec4( q.mul( p.z.mul( w ) ), 0 ) );
	} );
	s0.element( lid ).assign( a0 ); s1.element( lid ).assign( a1 ); s2.element( lid ).assign( a2 ); s3.element( lid ).assign( a3 ); s4.element( lid ).assign( a4 );
	workgroupBarrier();
	for ( let k = SMW / 2; k >= 1; k >>= 1 ) {
		If( lid.lessThan( I( k ) ), () => {
			for ( const s of [ s0, s1, s2, s3, s4 ] ) s.element( lid ).addAssign( s.element( lid.add( I( k ) ) ) );
		} );
		workgroupBarrier();
	}
	If( lid.equal( I( 0 ) ), () => {
		const W = s0.element( I( 0 ) ).w.toVar();
		If( W.greaterThan( 2.0 ), () => {
			const c = s0.element( I( 0 ) ).xyz.div( W ).toVar();
			const qb = s1.element( I( 0 ) ).xyz.div( W ).toVar();
			// A = Σ w p qᵀ − W c q̄ᵀ ; rows indexed by p component, columns by q component
			const r0 = s2.element( I( 0 ) ).xyz.sub( qb.mul( c.x.mul( W ) ) );
			const r1 = s3.element( I( 0 ) ).xyz.sub( qb.mul( c.y.mul( W ) ) );
			const r2 = s4.element( I( 0 ) ).xyz.sub( qb.mul( c.z.mul( W ) ) );
			const col0 = vec3( r0.x, r1.x, r2.x ).toVar(), col1 = vec3( r0.y, r1.y, r2.y ).toVar(), col2 = vec3( r0.z, r1.z, r2.z ).toVar();
			const q = cellRot.element( cell ).toVar();
			for ( let it = 0; it < 6; it ++ ) {
				const R0 = quatRotate( q, vec3( 1, 0, 0 ) ), R1 = quatRotate( q, vec3( 0, 1, 0 ) ), R2 = quatRotate( q, vec3( 0, 0, 1 ) );
				const om = cross( R0, col0 ).add( cross( R1, col1 ) ).add( cross( R2, col2 ) )
					.div( abs( dot( R0, col0 ).add( dot( R1, col1 ) ).add( dot( R2, col2 ) ) ).add( 1e-12 ) ).toVar();
				const wl = length( om );
				If( wl.greaterThan( 1e-7 ), () => {
					const half = wl.mul( 0.5 );
					const dq = vec4( om.div( wl ).mul( sin( half ) ), cos( half ) );
					q.assign( normalize( quatMul( dq, q ) ) );
				} );
			}
			cellRot.element( cell ).assign( q );
			cellCom.element( cell ).assign( vec4( c, W ) );
			cellQbar.element( cell ).assign( vec4( qb, 0 ) );
		} ).Else( () => {
			cellCom.element( cell ).assign( vec4( 0 ) );
		} );
	} );
} )().compute( NCELL * SMW, [ SMW ] ).setName( 'flakeReduce' );

const kShapeApply = Fn( () => {
	const id = I( instanceIndex );
	const pr = propsBuf.element( id );
	const cell = I( pr.x );
	const cm = cellCom.element( cell ).toVar();
	const w = flakeWeight( burnA.element( id ) ).mul( select( cm.w.greaterThan( 2.0 ), 1.0, 0.0 ) );
	If( w.greaterThan( 0.0 ), () => {
		const g = cm.xyz.add( quatRotate( cellRot.element( cell ), goalBuf.element( id ).xyz.sub( cellQbar.element( cell ).xyz ) ) );
		const p = predA.element( id ).xyz.toVar();
		p.assign( mix( p, g, w.mul( U.flakeK ) ) );
		p.y.assign( max( p.y, pr.w.mul( 0.0005 ).add( 0.00012 ) ) );
		predA.element( id ).assign( vec4( p, 1 ) );
	} );
} )().compute( NP ).setName( 'flakeApply' );

const kLink = Fn( () => {
	const id = I( instanceIndex );
	const pr = propsBuf.element( id );
	const lk = linkOf( burnA.element( id ), pr.w );
	linkBuf.element( id ).assign( vec4( pr.x, lk.x, lk.y, pr.w ) );
} )().compute( NP ).setName( 'linkState' );

const kConn = Fn( () => {
	const id = I( instanceIndex );
	const ix = id.mod( I( NPX ) ), iz = id.div( I( NPX ) );
	const Li = linkBuf.element( id ).toVar();
	const m = uint( 0 ).toVar();
	NB_OFFS.forEach( ( [ ox, oz ], k ) => {
		const { inside, jid } = nbInfo( ix, iz, ox, oz );
		If( inside.and( connL( Li, linkBuf.element( jid ) ) ), () => { m.assign( m.bitOr( uint( ( 1 << k ) >>> 0 ) ) ); } );
	} );
	connBuf.element( id ).assign( m );
} )().compute( NP ).setName( 'connMask' );

const kFinalize = Fn( () => {
	const id = I( instanceIndex );
	const q = predA.element( id ).xyz.toVar();
	const x = posBuf.element( id ).xyz.toVar();
	const pr = propsBuf.element( id );
	// sleeping: spent char (fully pyrolysed and cooled) stops responding, so the curled flakes keep the
	// shape they took while hot instead of buzzing under conflicting curvature/contact constraints
	const bF = burnA.element( id );
	const release = windRelease( pr.w ).toVar();
	const sleep = smoothstep( 0.9, 0.99, charOf( bF ) ).mul( smoothstep( 0.7, 0.2, bF.y ) ).mul( U.sleep ).mul( release.oneMinus() );
	q.assign( mix( q, x, sleep ) );
	const v = q.sub( x ).div( U.dt ).toVar();
	const yMin = pr.w.mul( 0.0005 ).add( 0.00012 );
	If( q.y.lessThan( yMin.add( 0.0002 ) ), () => {
		const fr = mix( U.friction, float( 0.997 ), release );
		v.x.mulAssign( fr ); v.z.mulAssign( fr );
	} );
	const sp = length( v );
	v.mulAssign( min( float( 1 ), float( 3 ).div( sp.add( 1e-6 ) ) ) );
	posBuf.element( id ).assign( vec4( q, 1 ) );
	velBuf.element( id ).assign( vec4( v, 0 ) );
} )().compute( NP ).setName( 'sheetFinalize' );

const kNormals = Fn( () => {
	const id = I( instanceIndex );
	const ix = id.mod( I( NPX ) ), iz = id.div( I( NPX ) );
	const mask = connBuf.element( id ).toVar();
	const P = posBuf.element( id ).xyz.toVar();
	const ci = propsBuf.element( id ).x.toVar();
	const chi = charOf( burnA.element( id ) ).toVar();
	const nb = ( ox, oz ) => {
		const { inside, jid } = nbInfo( ix, iz, ox, oz );
		const ok = hasNb( mask, ox, oz );
		return select( ok, posBuf.element( jid ).xyz, P );
	};
	const tx = nb( 1, 0 ).sub( nb( - 1, 0 ) );
	const tz = nb( 0, 1 ).sub( nb( 0, - 1 ) );
	const n = cross( tz, tx ).toVar();
	const l = length( n );
	nrmBuf.element( id ).assign( vec4( select( l.greaterThan( 1e-12 ), n.div( l ), vec3( 0, 1, 0 ) ), 0 ) );
} )().compute( NP ).setName( 'sheetNormals' );

// =====================================================================================
//  Sheet combustion: material-space reaction–diffusion (fuel, temperature, scorch),
//  coupled both ways with the gas temperature of the pyro grid
// =====================================================================================

const makeBurn = ( src, dst ) => Fn( () => {
	const id = I( instanceIndex );
	const ix = id.mod( I( NPX ) ), iz = id.div( I( NPX ) );
	const b = src.element( id ).toVar();
	const pr = propsBuf.element( id ).toVar();
	const F = b.x, T = b.y;
	const chi = charOf( b ).toVar();
	const lap = float( 0 ).toVar();
	const p = posBuf.element( id ).xyz.toVar();
	// conduction follows physical contact, not glue: a lattice neighbour conducts while it is still
	// touching (a torn edge keeps heating the paper it just tore from; drifted-apart flakes do not)
	const h = PW / ( NPX - 1 );
	for ( const [ ox, oz ] of [ [ 1, 0 ], [ - 1, 0 ], [ 0, 1 ], [ 0, - 1 ] ] ) {
		const { inside, jid } = nbInfo( ix, iz, ox, oz );
		const bj = src.element( jid );
		const contact = smoothstep( h * 3.0, h * 1.3, length( posBuf.element( jid ).xyz.sub( p ) ) );
		lap.addAssign( select( inside, bj.y.sub( T ).mul( contact ), 0.0 ) );
	}
	const gasT = sampleScalA( p.add( nrmBuf.element( id ).xyz.mul( 0.0015 ) ) ).x;
	const tIg = pr.z.mul( U.igVar ).add( U.igBase ).toVar();
	// flaming pyrolysis above the local ignition temperature, plus a slow smouldering path that
	// eventually consumes unburnt islands left behind the front
	const r = U.react.mul( pr.z.mul( - 0.3 ).add( 1.15 ) ).mul( F ).mul( smoothstep( tIg.sub( 0.15 ), tIg.add( 0.15 ), T ).add( smoothstep( 0.35, 1.0, T ).mul( 0.04 ) ) ).toVar();
	const dIg = p.sub( U.ignitePos );
	const ign = U.ignite.mul( exp( dot( dIg, dIg ).div( - 0.012 * 0.012 ) ) );
	const dT = U.diff.mul( pr.y ).mul( lap )
		// hot gas heats sound paper toward ignition; spent char only loses heat to the gas (its own smoke
		// plume must not keep it smouldering indefinitely)
		.add( select( chi.greaterThan( 0.9 ), min( U.airC.mul( gasT.sub( T ) ), 0.0 ), U.airC.mul( gasT.sub( T ) ) ) )
		.add( r.mul( U.heat ) )
		.sub( U.cool.mul( T ) )
		.add( ign );
	const Fn2 = max( F.sub( r.mul( U.bdt ) ), 0.0 );
	const Tn = clamp( T.add( dT.mul( U.bdt ) ), 0.0, 7.0 );
	// z: scorch in [0,1] ahead of the front; beyond 1 it carries char oxidation (ash = z − 1). Glowing
	// char keeps oxidising after the flame passes, in patches, eating holes from the hot edges inward
	const scorchUp = select( b.z.lessThan( 1.0 ), U.bdt.mul( U.scorch ).mul( smoothstep( 0.3, 0.95, T ) ), 0.0 );
	const oxVar = smoothstep( 0.75, 1.3, shrinkBuf.element( id ) ).mul( 0.85 ).add( 0.15 );
	const oxid = U.bdt.mul( U.oxid ).mul( smoothstep( 0.93, 0.99, chi ) ).mul( smoothstep( 0.8, 2.4, T ) ).mul( oxVar );
	const Sn = min( b.z.add( scorchUp ).add( select( b.z.greaterThanEqual( 0.98 ), oxid, 0.0 ) ), 2.0 );
	dst.element( id ).assign( vec4( Fn2, Tn, Sn, r ) );
} )().compute( NP );

const kBurnAB = makeBurn( burnA, burnB ).setName( 'burnAB' );
const kBurnBA = makeBurn( burnB, burnA ).setName( 'burnBA' );

// splat pyrolysis gases + heat from the sheet into the pyro grid, and soot onto the floor
const kSplat = Fn( () => {
	const id = I( instanceIndex );
	const b = burnA.element( id ).toVar();
	const p = posBuf.element( id ).xyz.toVar();
	const n = nrmBuf.element( id ).xyz;
	const ch = charOf( b );
	If( b.w.greaterThan( 0.002 ).or( b.y.greaterThan( 0.3 ) ), () => {
		const up = n.mul( select( n.y.lessThan( 0.0 ), - 1.0, 1.0 ) );
		const pe = p.add( up.mul( 0.0022 ) );
		const g = ivec3( floor( pe.sub( FMINn ).div( DX ) ) ).toVar();
		const gi = clamp( g.x, I( 0 ), I( NFX - 1 ) ), gj = clamp( g.y, I( 0 ), I( NFY - 1 ) ), gk = clamp( g.z, I( 0 ), I( NFZ - 1 ) );
		atomicAdd( emitFuel.element( vidx( gi, gj, gk ) ), I( b.w.mul( 1000.0 ) ) );
		atomicAdd( emitHeat.element( vidx( gi, gj, gk ) ), I( smoothstep( 1.0, 3.5, b.y ).mul( ch ).mul( 1000.0 ) ) );
		// smouldering: char that has stopped flaming but is still hot pyrolyses without a flame and
		// smokes until it cools, so the last spot to go out keeps smoking for a second or two
		const smoulder = smoothstep( 0.85, 1.0, ch ).mul( smoothstep( 0.3, 0.75, b.y ) ).mul( smoothstep( 2.6, 1.3, b.y ) ).mul( smoothstep( 0.4, 0.02, b.w ) );
		atomicAdd( emitSmoke.element( vidx( gi, gj, gk ) ), I( smoulder.mul( 1000.0 ) ) );
		If( p.y.lessThan( 0.006 ), () => {
			atomicAdd( sootAcc.element( gi.add( gk.mul( I( NFX ) ) ) ), I( b.w.mul( 30.0 ).add( smoothstep( 1.4, 3.5, b.y ).mul( ch ).mul( 3.0 ) ) ) );
		} );
	} );
} )().compute( NP ).setName( 'sheetSplat' );

// =====================================================================================
//  Pyro: collocated-grid smoke/fire solver (RK2 semi-Lagrangian, combustion, buoyancy,
//  vorticity confinement, gas expansion, Jacobi pressure projection)
// =====================================================================================

const kAdvect = Fn( () => {
	const id = I( instanceIndex );
	const { i, j, k } = voxOf( id );
	const p = cellCenter( i, j, k ).toVar();
	const v0 = velFA.element( id ).xyz;
	const vm = sampleVelA( p.sub( v0.mul( U.fdt.mul( 0.5 ) ) ) ).xyz;
	const pb = p.sub( vm.mul( U.fdt ) ).toVar();
	velFB.element( id ).assign( vec4( sampleVelA( pb ).xyz.mul( exp( U.fdt.mul( U.velDiss ).negate() ) ), 0 ) );
	scalB.element( id ).assign( sampleScalA( pb ) );
} )().compute( NV ).setName( 'advect' );

const kCombust = Fn( () => {
	const id = I( instanceIndex );
	const s = scalB.element( id ).toVar();
	const eF = float( atomicLoad( emitFuel.element( id ) ) ).mul( 0.001 ).toVar();
	const eH = float( atomicLoad( emitHeat.element( id ) ) ).mul( 0.001 ).toVar();
	const eS = float( atomicLoad( emitSmoke.element( id ) ) ).mul( 0.001 ).toVar();
	atomicStore( emitFuel.element( id ), I( 0 ) );
	atomicStore( emitHeat.element( id ), I( 0 ) );
	atomicStore( emitSmoke.element( id ), I( 0 ) );
	const dt = U.fdt;
	const T = s.x.add( eF.mul( U.emitHeat ).add( eH.mul( U.emitHeat2 ) ).add( eS.mul( U.smoulderHeat ) ).mul( dt ) ).toVar();
	const fu = s.y.add( eF.mul( U.emitFuel ).mul( dt ) ).toVar();
	const burn = fu.mul( exp( U.burnRate.mul( dt ).negate() ).oneMinus() ).mul( smoothstep( 0.35, 0.8, T ) ).toVar();
	fu.subAssign( burn );
	T.addAssign( burn.mul( U.burnHeat ) );
	const fl = s.w.add( burn.mul( U.flameGain ) ).mul( exp( U.flameDecay.mul( dt ).negate() ) );
	const sm = s.z.add( burn.mul( U.soot ) ).add( eS.mul( U.smoulderSmoke ).mul( dt ) ).mul( exp( U.smokeDecay.mul( dt ).negate() ) );
	expBuf.element( id ).assign( burn.mul( U.expand ).div( dt ) );
	const Tc = T.mul( exp( U.coolT.mul( dt ).negate() ) ).sub( T.mul( T ).mul( T ).mul( T ).mul( 0.004 ).mul( dt ) );
	scalA.element( id ).assign( vec4( clamp( Tc, 0.0, 6.0 ), fu.mul( exp( dt.mul( - 1.5 ) ) ), sm, min( fl, 4.0 ) ) );
} )().compute( NV ).setName( 'combust' );

const kCurl = Fn( () => {
	const id = I( instanceIndex );
	const { i, j, k } = voxOf( id );
	const xp = atC( velFB, i.add( I( 1 ) ), j, k ), xm = atC( velFB, i.sub( I( 1 ) ), j, k );
	const yp = atC( velFB, i, j.add( I( 1 ) ), k ), ym = atC( velFB, i, j.sub( I( 1 ) ), k );
	const zp = atC( velFB, i, j, k.add( I( 1 ) ) ), zm = atC( velFB, i, j, k.sub( I( 1 ) ) );
	const w = vec3(
		yp.z.sub( ym.z ).sub( zp.y.sub( zm.y ) ),
		zp.x.sub( zm.x ).sub( xp.z.sub( xm.z ) ),
		xp.y.sub( xm.y ).sub( yp.x.sub( ym.x ) )
	).div( 2 * DX ).toVar();
	curlBuf.element( id ).assign( vec4( w, length( w ) ) );
} )().compute( NV ).setName( 'curl' );

const kForces = Fn( () => {
	const id = I( instanceIndex );
	const { i, j, k } = voxOf( id );
	const s = scalA.element( id ).toVar();
	const c = curlBuf.element( id ).toVar();
	const eta = vec3(
		atC( curlBuf, i.add( I( 1 ) ), j, k ).w.sub( atC( curlBuf, i.sub( I( 1 ) ), j, k ).w ),
		atC( curlBuf, i, j.add( I( 1 ) ), k ).w.sub( atC( curlBuf, i, j.sub( I( 1 ) ), k ).w ),
		atC( curlBuf, i, j, k.add( I( 1 ) ) ).w.sub( atC( curlBuf, i, j, k.sub( I( 1 ) ) ).w )
	).toVar();
	const N = eta.div( length( eta ).add( 1e-5 ) );
	const mask = smoothstep( 0.03, 0.6, s.x.add( s.w ) );
	const conf = cross( N, c.xyz ).mul( U.vort.mul( DX ) ).mul( mask );
	const p = cellCenter( i, j, k );
	const tn = mx_noise_vec3( p.mul( vec3( 48, 30, 48 ) ).add( vec3( 0, U.time.mul( - 2.6 ), U.time.mul( 0.7 ) ) ) );
	const turb = tn.mul( U.turb ).mul( min( s.x, 2.0 ) );
	const buoy = vec3( 0, s.x.mul( U.buoy ).sub( s.z.mul( 0.4 ) ), 0 );
	const vel = velFB.element( id ).xyz.toVar();
	// finale wind: gusty, spatially varying, slower in the floor boundary layer; relaxes the air toward it
	const gust = smoothstep( - 0.3, 0.5, mx_noise_float( vec3( p.x.mul( 8.0 ).sub( U.wind.x.mul( U.time ).mul( 6.0 ) ), p.z.mul( 8.0 ).sub( U.wind.z.mul( U.time ).mul( 6.0 ) ), U.time.mul( 0.5 ) ) ) ).mul( 1.3 ).add( 0.08 );
	const layer = smoothstep( 0.0, 0.025, p.y ).mul( 0.6 ).add( 0.4 );
	vel.addAssign( U.wind.mul( gust.mul( layer ) ).sub( vel ).mul( U.windAmt.mul( U.fdt ).mul( 14.0 ) ) );
	const v = vel.add( conf.add( turb ).add( buoy ).mul( U.fdt ) );
	velFB.element( id ).assign( vec4( v, 0 ) );
} )().compute( NV ).setName( 'forces' );

const kDiv = Fn( () => {
	const id = I( instanceIndex );
	const { i, j, k } = voxOf( id );
	const vC = velFB.element( id ).toVar();
	const uR = atC( velFB, i.add( I( 1 ) ), j, k ).x, uL = atC( velFB, i.sub( I( 1 ) ), j, k ).x;
	const vU = atC( velFB, i, j.add( I( 1 ) ), k ).y;
	const vD = select( j.greaterThan( I( 0 ) ), atC( velFB, i, j.sub( I( 1 ) ), k ).y, vC.y.negate() );
	const wF = atC( velFB, i, j, k.add( I( 1 ) ) ).z, wB = atC( velFB, i, j, k.sub( I( 1 ) ) ).z;
	divBuf.element( id ).assign( uR.sub( uL ).add( vU.sub( vD ) ).add( wF.sub( wB ) ).div( 2 * DX ).sub( expBuf.element( id ) ) );
} )().compute( NV ).setName( 'divergence' );

const pNb = ( src, id, i, j, k ) => {
	const pC = src.element( id );
	return {
		pL: select( i.greaterThan( I( 0 ) ), atC( src, i.sub( I( 1 ) ), j, k ), 0.0 ),
		pR: select( i.lessThan( I( NFX - 1 ) ), atC( src, i.add( I( 1 ) ), j, k ), 0.0 ),
		pD: select( j.greaterThan( I( 0 ) ), atC( src, i, j.sub( I( 1 ) ), k ), pC ),
		pU: select( j.lessThan( I( NFY - 1 ) ), atC( src, i, j.add( I( 1 ) ), k ), 0.0 ),
		pB: select( k.greaterThan( I( 0 ) ), atC( src, i, j, k.sub( I( 1 ) ) ), 0.0 ),
		pF: select( k.lessThan( I( NFZ - 1 ) ), atC( src, i, j, k.add( I( 1 ) ) ), 0.0 )
	};
};

const makeJacobi = ( src, dst ) => Fn( () => {
	const id = I( instanceIndex );
	const { i, j, k } = voxOf( id );
	const n = pNb( src, id, i, j, k );
	dst.element( id ).assign( n.pL.add( n.pR ).add( n.pD ).add( n.pU ).add( n.pB ).add( n.pF ).sub( divBuf.element( id ).mul( DX * DX ) ).div( 6 ) );
} )().compute( NV );
const kJacAB = makeJacobi( presA, presB ).setName( 'jacobiAB' );
const kJacBA = makeJacobi( presB, presA ).setName( 'jacobiBA' );

const kProject = Fn( () => {
	const id = I( instanceIndex );
	const { i, j, k } = voxOf( id );
	const n = pNb( presA, id, i, j, k );
	const grad = vec3( n.pR.sub( n.pL ), n.pU.sub( n.pD ), n.pF.sub( n.pB ) ).div( 2 * DX );
	const v = velFB.element( id ).xyz.sub( grad ).toVar();
	If( j.equal( I( 0 ) ), () => { v.y.assign( max( v.y, 0.0 ) ); } );
	velFA.element( id ).assign( vec4( v, 0 ) );
} )().compute( NV ).setName( 'project' );

const kBBoxClear = Fn( () => {
	const id = I( instanceIndex );
	If( id.lessThan( I( 3 ) ), () => { atomicStore( bboxAtom.element( id ), I( 100000 ) ); } )
		.Else( () => { atomicStore( bboxAtom.element( id ), I( - 100000 ) ); } );
} )().compute( 8 ).setName( 'bboxClear' );

const kVolume = Fn( () => {
	const id = I( instanceIndex );
	const { i, j, k } = voxOf( id );
	const s = scalA.element( id ).toVar();
	textureStore( volTex, uvec3( i, j, k ), vec4( s.w, s.x, s.z, s.y ) );
	If( s.w.add( s.z ).greaterThan( 0.002 ), () => {
		atomicMin( bboxAtom.element( I( 0 ) ), i ); atomicMin( bboxAtom.element( I( 1 ) ), j ); atomicMin( bboxAtom.element( I( 2 ) ), k );
		atomicMax( bboxAtom.element( I( 4 ) ), i ); atomicMax( bboxAtom.element( I( 5 ) ), j ); atomicMax( bboxAtom.element( I( 6 ) ), k );
		atomicMax( bboxAtom.element( I( 7 ) ), I( s.w.mul( 1000.0 ) ) ); // peak flame density (drives flame-out detection)
	} );
} )().compute( NV ).setName( 'volumeTex' );

const kBBox = Fn( () => {
	const lo = vec3( float( atomicLoad( bboxAtom.element( I( 0 ) ) ) ), float( atomicLoad( bboxAtom.element( I( 1 ) ) ) ), float( atomicLoad( bboxAtom.element( I( 2 ) ) ) ) ).toVar();
	const hi = vec3( float( atomicLoad( bboxAtom.element( I( 4 ) ) ) ), float( atomicLoad( bboxAtom.element( I( 5 ) ) ) ), float( atomicLoad( bboxAtom.element( I( 6 ) ) ) ) ).toVar();
	const lw = lo.sub( 1.0 ).mul( DX ).add( FMINn );
	const hw = hi.add( 2.0 ).mul( DX ).add( FMINn );
	const empty = lo.x.greaterThan( hi.x );
	bboxBuf.element( I( 0 ) ).assign( vec4( select( empty, vec3( 1 ), max( lw, FMINn ) ), max( float( atomicLoad( bboxAtom.element( I( 7 ) ) ) ).mul( 0.001 ), 0.0 ) ) );
	bboxBuf.element( I( 1 ) ).assign( vec4( select( empty, vec3( - 1 ), min( hw, FMINn.add( FSIZEn ) ) ), 0 ) );
} )().compute( 1 ).setName( 'bbox' );

// column-integrated flame power -> blurred near/far irradiance maps for fire light on floor and sheet
const kColumn = Fn( () => {
	const id = I( instanceIndex );
	const i = id.mod( I( NFX ) ), k = id.div( I( NFX ) );
	const e = float( 0 ).toVar();
	Loop( { start: I( 0 ), end: I( NFY ), type: 'int' }, ( { i: j } ) => {
		const s = scalA.element( vidx( i, j, k ) );
		const kT = smoothstep( 0.3, 3.2, s.x );
		e.addAssign( s.w.mul( kT.mul( kT ).mul( 3.0 ).add( 0.25 ) ).mul( float( j ).mul( - 0.02 ).add( 1.2 ) ) );
	} );
	colBuf.element( id ).assign( vec4( e.mul( DX ), 0, 0, 0 ) );
} )().compute( NC ).setName( 'column' );

const kGroundTex = Fn( () => {
	const id = I( instanceIndex );
	const i = id.mod( I( NFX ) ), k = id.div( I( NFX ) );
	const near = float( 0 ).toVar(), far = float( 0 ).toVar(), soot = float( 0 ).toVar();
	let wn = 0, wf = 0, ws = 0;
	const at2 = ( buf, di, dk ) => buf.element( clamp( i.add( I( di ) ), I( 0 ), I( NFX - 1 ) ).add( clamp( k.add( I( dk ) ), I( 0 ), I( NFZ - 1 ) ).mul( I( NFX ) ) ) );
	for ( let a = - 3; a <= 3; a ++ ) for ( let c = - 3; c <= 3; c ++ ) {
		const w = Math.exp( - ( a * a + c * c ) / 4.5 ); wn += w;
		near.addAssign( at2( colBuf, a, c ).x.mul( w ) );
	}
	for ( let a = - 4; a <= 4; a ++ ) for ( let c = - 4; c <= 4; c ++ ) {
		const w = Math.exp( - ( a * a + c * c ) / 9.0 ); wf += w;
		far.addAssign( at2( colBuf, a * 3, c * 3 ).x.mul( w ) );
	}
	for ( let a = - 1; a <= 1; a ++ ) for ( let c = - 1; c <= 1; c ++ ) {
		const w = ( a === 0 && c === 0 ) ? 4 : ( a === 0 || c === 0 ) ? 2 : 1; ws += w;
		const sidx = clamp( i.add( I( a ) ), I( 0 ), I( NFX - 1 ) ).add( clamp( k.add( I( c ) ), I( 0 ), I( NFZ - 1 ) ).mul( I( NFX ) ) );
		soot.addAssign( float( atomicLoad( sootAcc.element( sidx ) ) ).mul( w ) );
	}
	textureStore( groundTex, uvec2( i, k ), vec4( near.div( wn ), far.div( wf ), soot.div( ws ).mul( U.sootKeep.mul( 0.000025 ) ), 0 ) );
} )().compute( NC ).setName( 'groundTex' );

// ---- reset
const kResetSheet = Fn( () => {
	const id = I( instanceIndex );
	posBuf.element( id ).assign( restBuf.element( id ) );
	velBuf.element( id ).assign( vec4( 0 ) );
	burnA.element( id ).assign( vec4( 1, 0, 0, 0 ) );
	burnB.element( id ).assign( vec4( 1, 0, 0, 0 ) );
	nrmBuf.element( id ).assign( vec4( 0, 1, 0, 0 ) );
} )().compute( NP ).setName( 'resetSheet' );

const kResetFluid = Fn( () => {
	const id = I( instanceIndex );
	velFA.element( id ).assign( vec4( 0 ) ); velFB.element( id ).assign( vec4( 0 ) );
	scalA.element( id ).assign( vec4( 0 ) ); scalB.element( id ).assign( vec4( 0 ) );
	presA.element( id ).assign( 0 ); presB.element( id ).assign( 0 );
	expBuf.element( id ).assign( 0 );
} )().compute( NV ).setName( 'resetFluid' );

const kResetFlakes = Fn( () => {
	const id = I( instanceIndex );
	If( id.lessThan( I( NCELL ) ), () => {
		cellRot.element( id ).assign( vec4( 0, 0, 0, 1 ) );
		cellCom.element( id ).assign( vec4( 0 ) );
	} );
} )().compute( NCELL ).setName( 'resetFlakes' );

// separate pass: the accumulators would push the reset past the per-stage storage-buffer limit
const kResetEmit = Fn( () => {
	const id = I( instanceIndex );
	atomicStore( emitFuel.element( id ), I( 0 ) ); atomicStore( emitHeat.element( id ), I( 0 ) ); atomicStore( emitSmoke.element( id ), I( 0 ) );
	If( id.lessThan( I( NC ) ), () => { atomicStore( sootAcc.element( id ), I( 0 ) ); } );
} )().compute( NV ).setName( 'resetEmit' );

// =====================================================================================
//  Materials
// =====================================================================================

const fireLight = ( wp ) => {
	const g = texture( groundTex, wp.xz.sub( vec2( FMIN.x, FMIN.z ) ).div( vec2( FSIZE.x, FSIZE.z ) ) );
	const inside = smoothstep( 0.0, 0.01, wp.x.sub( FMIN.x ) ).mul( smoothstep( 0.0, 0.01, float( FMIN.x + FSIZE.x ).sub( wp.x ) ) )
		.mul( smoothstep( 0.0, 0.01, wp.z.sub( FMIN.z ) ) ).mul( smoothstep( 0.0, 0.01, float( FMIN.z + FSIZE.z ).sub( wp.z ) ) );
	return { irr: g.r.mul( U.lightNear ).add( g.g.mul( U.lightFar ) ).mul( inside ), soot: g.b.mul( inside ) };
};
const FIRE_LIGHT_COL = vec3( 1.0, 0.42, 0.12 );

// screen-space bump from a procedural height (Mikkelsen), on top of an arbitrary base normal
const perturb = ( n, h, scale ) => {
	const sx = positionView.dFdx(), sy = positionView.dFdy();
	const R1 = cross( sy, n ), R2 = cross( n, sx );
	const det = dot( sx, R1 );
	const grad = R1.mul( h.dFdx() ).add( R2.mul( h.dFdy() ) ).mul( scale ).mul( det.sign() );
	return normalize( abs( det ).mul( n ).sub( grad ) );
};
// ---- paper: vertices pulled from the simulation buffers; triangles spanning broken glue collapse
const paperMat = new THREE.MeshStandardNodeMaterial( { side: THREE.DoubleSide } );
paperMat.shadowSide = THREE.DoubleSide;
{
	const vI = I( vertexIndex );
	const quad = vI.div( I( 6 ) ), corner = vI.mod( I( 6 ) );
	const qx = quad.mod( I( NPX - 1 ) ), qz = quad.div( I( NPX - 1 ) );
	const isB = corner.greaterThanEqual( I( 3 ) );
	const cxo = select( corner.equal( I( 2 ) ).or( corner.equal( I( 3 ) ) ).or( corner.equal( I( 5 ) ) ), I( 1 ), I( 0 ) );
	const czo = select( corner.equal( I( 1 ) ).or( corner.equal( I( 4 ) ) ).or( corner.equal( I( 5 ) ) ), I( 1 ), I( 0 ) );
	const pIdx = qz.add( czo ).mul( I( NPX ) ).add( qx.add( cxo ) );
	const idxAt = ( a, b ) => qz.add( I( b ) ).mul( I( NPX ) ).add( qx.add( I( a ) ) );
	const t0 = select( isB, idxAt( 1, 0 ), idxAt( 0, 0 ) ), t1 = idxAt( 0, 1 ), t2 = select( isB, idxAt( 1, 1 ), idxAt( 1, 0 ) );
	const mAt = ( a, b ) => connBuf.element( idxAt( a, b ) );
	const visA = hasNb( mAt( 0, 0 ), 0, 1 ).and( hasNb( mAt( 0, 1 ), 1, - 1 ) ).and( hasNb( mAt( 0, 0 ), 1, 0 ) );
	const visB = hasNb( mAt( 1, 0 ), - 1, 1 ).and( hasNb( mAt( 0, 1 ), 1, 0 ) ).and( hasNb( mAt( 1, 0 ), 0, 1 ) );
	const visible = select( isB, visB, visA );
	paperMat.positionNode = select( visible, posBuf.element( pIdx ).xyz, vec3( 0, - 10, 0 ) );

	const vBurn = varying( burnA.element( pIdx ), 'vBurn' );
	const vNrm = varying( nrmBuf.element( pIdx ).xyz, 'vNrm' );
	const vUv = varying( vec2( float( qx.add( cxo ) ).div( NPX - 1 ), float( qz.add( czo ) ).div( NPZ - 1 ) ), 'vUv' );

	const m = vUv.mul( vec2( PW, PH ) );
	const F = vBurn.x, T = vBurn.y, S = vBurn.z;
	const n1 = mx_fractal_noise_float( vec3( m.mul( 150.0 ), 1.3 ), 3, 2.0, 0.5, 1.0 );
	const n2 = mx_noise_float( vec3( m.mul( 820.0 ), 7.1 ) );
	const fiber = mx_fractal_noise_float( vec3( m.mul( vec2( 1400.0, 1600.0 ) ), 3.3 ), 2, 2.0, 0.5, 1.0 );
	const c = F.oneMinus().add( n1.mul( 0.11 ) ).add( n2.mul( 0.035 ) ).toVar();
	const charM = smoothstep( 0.47, 0.57, c ).toVar();
	const scorchM = smoothstep( 0.05, 0.9, S.add( n1.mul( 0.22 ) ) ).toVar();
	// printed page: tibo.png laid out landscape with generous margins, reading upright from the
	// default camera (text baseline along +x, page top toward −z); toner multiplies the stock
	const pm = m.sub( vec2( PW * 0.5, PH * 0.5 ) ).sub( vec2( PRINT_CX, PRINT_CZ ) ).div( vec2( PRINT_W, float( PRINT_W ).div( printAspect ) ) ).add( 0.5 ).toVar();
	const inPrint = pm.x.greaterThanEqual( 0.0 ).and( pm.x.lessThanEqual( 1.0 ) ).and( pm.y.greaterThanEqual( 0.0 ) ).and( pm.y.lessThanEqual( 1.0 ) );
	const ink = texture( printTex, vec2( pm.x, pm.y.oneMinus() ) );
	const toner = select( inPrint, mix( vec3( 1.0 ), ink.rgb, ink.a ), vec3( 1.0 ) );
	const paperCol = vec3( 0.80, 0.795, 0.77 ).mul( fiber.mul( 0.025 ).add( 1 ) ).mul( toner );
	let col = mix( paperCol, vec3( 0.55, 0.40, 0.22 ).mul( toner ), scorchM.mul( 0.55 ) );
	col = mix( col, vec3( 0.26, 0.13, 0.05 ), smoothstep( 0.12, 0.36, c ) );
	col = mix( col, vec3( 0.07, 0.035, 0.018 ), smoothstep( 0.32, 0.48, c ) );
	const charCol = vec3( 0.021, 0.019, 0.018 ).mul( mx_noise_float( vec3( m.mul( 300.0 ), 2.2 ) ).mul( 0.35 ).add( 1 ) );
	col = mix( col, charCol, charM );
	// fine grey ash where the char got hottest
	const ashM = smoothstep( 0.55, 0.95, mx_noise_float( vec3( m.mul( 520.0 ), 9.9 ) ) ).mul( charM ).mul( smoothstep( 0.92, 1.0, F.oneMinus() ) ).mul( 0.35 );
	col = mix( col, vec3( 0.22, 0.21, 0.2 ), ashM );

	// glowing pyrolysis edge + smouldering char
	const band = smoothstep( 0.26, 0.42, c ).mul( smoothstep( 0.66, 0.5, c ) );
	const heatK = smoothstep( 0.7, 3.2, T );
	// the glowing rim is broken up: embers only where the char fibres are thin and hot
	const rimBreak = smoothstep( - 0.2, 0.45, mx_noise_float( vec3( m.mul( 380.0 ), U.time.mul( 1.5 ) ) ) );
	const edgeGlow = fireColor( heatK.mul( 0.7 ) ).mul( band ).mul( heatK.mul( heatK ) ).mul( rimBreak.mul( 3.2 ).add( 0.4 ) );
	const embers = smoothstep( 0.25, 0.75, mx_noise_float( vec3( m.mul( 260.0 ), U.time.mul( 0.6 ) ) ) );
	const smoulder = vec3( 1.0, 0.18, 0.03 ).mul( charM ).mul( smoothstep( 1.0, 2.6, T ) ).mul( embers ).mul( 1.6 );

	const fl = fireLight( positionWorld );
	const albedo = col.toVar();

	paperMat.colorNode = albedo;
	paperMat.roughnessNode = mix( float( 0.82 ), float( 0.5 ), charM );
	const nBase = transformNormalToView( normalize( vNrm ) ).mul( faceDirection ).normalize();
	const crease = texture( detailTex, vUv ).r;
	paperMat.normalNode = perturb( nBase, crease.mul( charM.mul( - 0.85 ).add( 1.0 ) ), 0.001 );
	const transl = charM.oneMinus().mul( 0.6 ).add( 1.0 );
	const emis = edgeGlow.add( smoulder ).add( albedo.mul( FIRE_LIGHT_COL ).mul( fl.irr ).mul( transl ) );
	paperMat.emissiveNode = emis;
}
const paperGeo = new THREE.BufferGeometry();
paperGeo.setAttribute( 'position', new THREE.BufferAttribute( new Float32Array( ( NPX - 1 ) * ( NPZ - 1 ) * 6 * 3 ), 3 ) );
paperGeo.boundingSphere = new THREE.Sphere( new THREE.Vector3(), 2 );
const paper = new THREE.Mesh( paperGeo, paperMat );
paper.frustumCulled = false;
paper.castShadow = true;
paper.receiveShadow = true;
scene.add( paper );

// =====================================================================================
//  Post: depth-aware volumetric fire composite, bloom, grain
// =====================================================================================

const renderPipeline = new THREE.RenderPipeline( renderer );
const scenePass = pass( scene, camera );
const sceneColor = scenePass.getTextureNode( 'output' );
const sceneDepth = scenePass.getTextureNode( 'depth' );

const composite = Fn( () => {
	const suv = uv();
	const base = sceneColor.sample( suv ).toVar();
	const d = sceneDepth.sample( suv ).r;
	const vp = getViewPosition( suv, d, U.projInv );
	const wp = U.camWorld.mul( vec4( vp, 1 ) ).xyz;
	const ro = U.camPos;
	const toP = wp.sub( ro );
	const tScene = length( toP );
	const rd = toP.div( tScene ).toVar();
	const bmin = bboxBuf.element( I( 0 ) ).xyz, bmax = bboxBuf.element( I( 1 ) ).xyz;
	const inv = vec3( 1 ).div( rd );
	const ta = bmin.sub( ro ).mul( inv ), tb = bmax.sub( ro ).mul( inv );
	const tmn = min( ta, tb ), tmx = max( ta, tb );
	const t0 = max( max( tmn.x, tmn.y ), max( tmn.z, 0.0 ) ).toVar();
	const t1 = min( min( tmx.x, tmx.y ), min( tmx.z, tScene ) ).toVar();
	const L = vec3( 0 ).toVar();
	const Tr = float( 1 ).toVar();
	If( t1.greaterThan( t0 ), () => {
		const t = t0.add( interleavedGradientNoise( screenCoordinate.xy ).mul( STEP ) ).toVar();
		Loop( MAXSTEPS, () => {
			If( t.greaterThan( t1 ).or( Tr.lessThan( 0.01 ) ), () => { Break(); } );
			const p = ro.add( rd.mul( t ) ).toVar();
			const s = texture3D( volTex, p.sub( FMINn ).div( FSIZEn ), float( 0 ) ).toVar();
			If( s.x.add( s.z ).greaterThan( 0.0008 ), () => {
				// sub-voxel flame detail: two octaves of noise scrolling upward with the plume and stretched
				// vertically, used to carve the flame density into licking tongues (soft level set)
				const q = p.mul( vec3( 150, 95, 150 ) ).add( vec3( 0, U.time.mul( - 36.0 ), 0 ) );
				const n1 = mx_noise_float( q );
				const n2 = mx_noise_float( q.mul( 2.3 ).add( vec3( 4.1, U.time.mul( - 30.0 ), 1.7 ) ) );
				const det = n1.mul( 0.75 ).add( n2.mul( 0.35 ) );
				const fl = smoothstep( U.flameLo, U.flameHi, s.x.mul( det.mul( U.flameDetail ).add( 1.0 ) ) ).mul( min( s.x.mul( 3.0 ), 1.0 ) ).toVar();
				// colour from reaction intensity and gas temperature: dense reacting cores run yellow-white, thin licks orange-red
				const kT = clamp( smoothstep( 0.3, U.fireTmax, s.y ).mul( 0.6 ).add( smoothstep( 0.2, 2.0, s.x ).mul( 0.45 ) ), 0.0, 1.0 );
				const em = fireColor( kT ).mul( fl ).mul( U.fireEmit ).mul( kT.mul( kT ).mul( 2.2 ).add( 0.3 ) );
				// smoke: slow-rising wisps carved from the grid density, scattering soft daylight
				const sq = p.mul( vec3( 120, 75, 120 ) ).add( vec3( U.time.mul( 0.4 ), U.time.mul( - 3.0 ), 0 ) );
				const wisp = mx_noise_float( sq ).mul( 0.7 ).add( mx_noise_float( sq.mul( 2.1 ).add( 3.7 ) ).mul( 0.35 ) );
				const smk = s.z.mul( smoothstep( - 0.45, 0.55, wisp ).mul( 1.6 ) ).toVar();
				const sig = fl.mul( U.fireAbs ).add( smk.mul( U.smokeAbs ) );
				const a = exp( sig.mul( - STEP ) );
				L.addAssign( Tr.mul( em ).mul( STEP ) );
				const smokeCol = vec3( 0.40, 0.40, 0.42 ).mul( U.smokeAmb ).add( fireColor( float( 0.4 ) ).mul( fl.mul( 0.6 ) ) );
				L.addAssign( Tr.mul( a.oneMinus() ).mul( smk.mul( U.smokeAbs ).div( sig.add( 1e-5 ) ) ).mul( smokeCol ) );
				Tr.mulAssign( a );
			} );
			t.addAssign( STEP );
		} );
	} );
	return vec4( base.rgb.mul( Tr ).add( L ), 1 );
} )();

const bloomPass = bloom( composite, 0.22, 0.45, 1.1 );
const finalNode = Fn( () => {
	const c = composite.rgb.add( bloomPass.rgb );
	const q = uv().sub( 0.5 );
	const vig = smoothstep( 0.95, 0.25, length( q.mul( vec2( 1.0, 1.1 ) ) ) ).mul( 0.25 ).add( 0.75 );
	const grain = interleavedGradientNoise( screenCoordinate.xy.add( U.time.mul( 517.0 ) ) ).sub( 0.5 ).mul( 0.018 );
	return vec4( c.mul( vig ).add( grain ), 1 );
} )();
renderPipeline.outputNode = finalNode;

// =====================================================================================
//  Simulation driver
// =====================================================================================

let simTime = 0, paused = false, frame = 0;
const BURN_PAIRS = 8;
U.bdt.value = FRAME_DT / ( BURN_PAIRS * 2 );

function stepSheet( withBurn ) {
	const list = [];
	// combustion runs on the material lattice at its own fixed step (diffusion stability), then the
	// link state it implies is cached once for every constraint and render test this frame
	if ( withBurn ) for ( let k = 0; k < BURN_PAIRS; k ++ ) list.push( kBurnAB, kBurnBA );
	list.push( kLink, kConn );
	for ( let s = 0; s < SUB; s ++ ) {
		list.push( kIntegrate );
		for ( let it = 0; it < SOLVE_PAIRS; it ++ ) list.push( kBendA, kSolveAB, kBendB, kSolveBA );
		list.push( kShapeReduce, kShapeApply, kFinalize );
	}
	list.push( kNormals );
	renderer.compute( list );
}

function stepFluid() {
	const list = [ kSplat, kAdvect, kCombust, kCurl, kForces, kDiv ];
	for ( let i = 0; i < JACOBI / 2; i ++ ) list.push( kJacAB, kJacBA );
	list.push( kProject, kBBoxClear, kVolume, kBBox, kColumn, kGroundTex );
	renderer.compute( list );
}

const IGNITE_CORNER = new THREE.Vector3( - PW / 2 + 0.004, 0.002, PH / 2 - 0.004 );
let igniteUntil = 0;

function reset() {
	// clear every piece of time/finale state first: the settling pre-roll below runs the full solver,
	// so a leftover gust (on loop) would blow the fresh sheet into a wad before it is lit
	simTime = 0;
	finale = { checking: false, nextCheck: 3, burntAt: - 1, windStart: - 1, lastFlame: 3, lastFlameWall: playClock };
	U.windAmt.value = 0; U.sootKeep.value = 1; U.time.value = 0; U.ignite.value = 0;
	renderer.compute( [ kResetSheet, kResetFluid, kResetEmit, kResetFlakes ] );
	// let the crumpled sheet settle under gravity before lighting it
	for ( let i = 0; i < 70; i ++ ) stepSheet( false );
	stepFluid();
	U.ignitePos.value.copy( IGNITE_CORNER );
	igniteUntil = 1.1;
}

// finale: once the sheet is spent and the embers have cooled, a gust clears the floor; the
// animation then loops from the beginning while playing
const WIND_AFTER_FLAMEOUT = 5.0;   // real seconds after the last visible flame
const FLAME_VISIBLE = 0.06;          // peak flame density the renderer can still show
const LOOP_AFTER_WIND = 3.0;         // real seconds of wind before the next cycle
let playClock = 0;                   // real seconds of playback, pauses excluded
let finale = { checking: false, nextCheck: 3, burntAt: - 1, windStart: - 1, lastFlame: 3, lastFlameWall: 0 };
async function checkBurnout() {
	const state = finale;
	state.checking = true;
	try {
		// flame-out is judged on what is visible: the peak flame density in the fire volume. Once it has
		// stayed below the level the renderer can show for two checks in a row, the last flame is out.
		const peakFlame = new Float32Array( await renderer.getArrayBufferAsync( bboxBuf.value ) )[ 3 ];
		if ( state === finale && state.burntAt < 0 ) {
			state.quiet = peakFlame < FLAME_VISIBLE ? ( state.quiet || 0 ) + 1 : 0;
			if ( state.quiet >= 2 ) { state.burntAt = state.lastFlame; state.burntWall = state.lastFlameWall; }
			else if ( peakFlame >= FLAME_VISIBLE ) { state.lastFlame = simTime; state.lastFlameWall = playClock; }
		}
	} catch ( e ) { console.warn( 'burnout check failed', e ); }
	state.checking = false;
}
function updateFinale() {
	if ( finale.burntAt < 0 && ! finale.checking && simTime > finale.nextCheck ) { finale.nextCheck = simTime + 0.25; checkBurnout(); }
	if ( finale.burntAt >= 0 && finale.windStart < 0 && playClock > finale.burntWall + WIND_AFTER_FLAMEOUT ) { finale.windStart = simTime; finale.windWall = playClock; }
	if ( finale.windStart >= 0 ) {
		const t = simTime - finale.windStart;
		if ( playClock > finale.windWall + LOOP_AFTER_WIND ) finale.done = true;
		const ramp = THREE.MathUtils.smoothstep( t, 0, 0.7 );   // a gust arrives in a fraction of a second
		U.windAmt.value = ramp * ( 0.8 + 0.2 * Math.sin( t * 2.7 ) * Math.sin( t * 1.3 + 1 ) );
		U.sootKeep.value = Math.max( 0.35, 1 - 0.1 * Math.max( 0, t - 1.5 ) );
	}
}

function simulate() {
	U.time.value = simTime;
	updateFinale();
	U.ignite.value = simTime < igniteUntil ? 26 : 0;
	stepSheet( true );
	stepFluid();
	simTime += FRAME_DT;
}

reset();
let acc = 0;
return {
  fireLight, FIRE_LIGHT_COL, U,
  ignite(hit) {
    if (Math.abs(hit.x) < PW / 2 + 0.01 && Math.abs(hit.z) < PH / 2 + 0.01) {
      U.ignitePos.value.copy(hit);
      igniteUntil = simTime + 0.7;
    }
  },
  update(wallDt) {
    wallDt = Math.min(wallDt, 0.1);
    acc = Math.min(acc + wallDt, FRAME_DT * 2);
    playClock += wallDt;
    let n = 0;
    while (acc >= FRAME_DT * 0.98 && n < 2) { simulate(); acc -= FRAME_DT; n++; }
    if (finale.done) { reset(); acc = 0; }
  },
  render() {
    camera.updateMatrixWorld();
    U.projInv.value.copy(camera.projectionMatrixInverse);
    U.camWorld.value.copy(camera.matrixWorld);
    U.camPos.value.copy(camera.position);
    renderPipeline.render();
  },
  setDebugMode(mode) {
    renderPipeline.outputNode = mode === 'nopost' ? composite
      : mode === 'sheet' ? sceneColor
      : mode === 'ground' ? texture(groundTex) : finalNode;
    renderPipeline.needsUpdate = true;
  },
  reset,
  dispose() {
    renderPipeline.dispose(); volTex.dispose(); groundTex.dispose(); detailTex.dispose();
    paper.removeFromParent(); paper.geometry.dispose(); paper.material.dispose();
  },
};
}
