import * as THREE from "three/webgpu";
import { attribute, float, uniform } from "three/tsl";
import { GPUCausticField } from "./gpu-caustic-field.js";

export const SOFTBODY_JELLY_DEFAULTS = Object.freeze({
  density: 1050,
  shear: 600,
  bulk: 65000,
  damping: 3,
  gravity: 9.81,
  step: 1 / 240,
  iterations: 3,
  staticFriction: 0.65,
  dynamicFriction: 0.42,
  restitution: 0.065,
  floor: 0.00015,
  maxGrabForce: 2.8,
});

export const SOFTBODY_JELLY_LOOKS = Object.freeze({
  berry: Object.freeze({ surface: "#ffe0eb", attenuation: "#ed5187", sigma: Object.freeze([5, 46, 23]) }),
  mint: Object.freeze({ surface: "#dbfff0", attenuation: "#4dc9a0", sigma: Object.freeze([40, 8, 20]) }),
  honey: Object.freeze({ surface: "#fff1d5", attenuation: "#edb643", sigma: Object.freeze([5, 17, 58]) }),
});

export const SOFTBODY_JELLY_DEBUG_MODES = Object.freeze([
  { value: "final", label: "Final specimen" },
  { value: "wireframe", label: "Simulation mesh" },
  { value: "shadow", label: "Refractive shadow" },
  { value: "caustics", label: "RGB caustics" },
]);

const PHYS = { ...SOFTBODY_JELLY_DEFAULTS };
const clamp = (value, minimum, maximum) =>
  Math.max(minimum, Math.min(maximum, value));
const LOOKS = {
  berry: { ...SOFTBODY_JELLY_LOOKS.berry, sigma: [...SOFTBODY_JELLY_LOOKS.berry.sigma] },
  mint: { ...SOFTBODY_JELLY_LOOKS.mint, sigma: [...SOFTBODY_JELLY_LOOKS.mint.sigma] },
  honey: { ...SOFTBODY_JELLY_LOOKS.honey, sigma: [...SOFTBODY_JELLY_LOOKS.honey.sigma] },
};
const state = {
  paused: false,
  dragging: false,
  flavour: "berry",
  ready: false,
  failed: false,
  disposed: false,
  orbiting: false,
  debugMode: "final",
};

let camera;
let controls;
let domElement;
let body;
let jelly;
let wire;
let gripMarker;
let gripLine;
let optics;
let jellyMaterial;
let accumulator = 0;
let opticalClock = 0;
let activePointer = null;
let interactionCleanups = [];

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const dragPlane = new THREE.Plane();
const rawTarget = new THREE.Vector3();
const pointerPoint = new THREE.Vector3();
const viewDirection = new THREE.Vector3();
const lightDirection = new THREE.Vector3(
  -0.6123724357,
  -0.5,
  0.6123724357,
).normalize();
const resources = new Set();
const keep = (object) => (resources.add(object), object);

  function determinant(a,b,c,d,e,f,g,h,i) {
    return a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g);
  }
  function inverse3(m) {
    const [a,b,c,d,e,f,g,h,i] = m;
    const det = determinant(a,b,c,d,e,f,g,h,i);
    if (Math.abs(det) < 1e-24) throw new Error('Degenerate rest element.');
    const s = 1/det;
    return [(e*i-f*h)*s,(c*h-b*i)*s,(b*f-c*e)*s,
      (f*g-d*i)*s,(a*i-c*g)*s,(c*d-a*f)*s,
      (d*h-e*g)*s,(b*g-a*h)*s,(a*e-b*d)*s];
  }

  export function makeFlowerCage() {
    // Regular triangular-lattice cross sections avoid the radial centre fan.
    // The outer contour, dimensions and five-lobed profile are unchanged, but the
    // cap topology now has valence six through its interior for clean subdivision.
    const latticeRadius=6, layers=5;
    const planar=[], index=new Map(), ringOrder=new Map(), xyz=[], triangles=[], tets=[];
    const key=(q,r)=>q+','+r;

    for(let q=-latticeRadius;q<=latticeRadius;q++) for(let r=-latticeRadius;r<=latticeRadius;r++) {
      if(Math.max(Math.abs(q),Math.abs(r),Math.abs(q+r))>latticeRadius) continue;
      index.set(key(q,r),planar.length);
      planar.push([q,r]);
    }

    // Number each hexagonal lattice ring continuously around the centre. Mapping
    // that ordinal to angle keeps every ring circular and preserves the
    // 36-sample outer star contour exactly.
    const walk=[[-1,1],[-1,0],[0,-1],[1,-1],[1,0],[0,1]];
    for(let ring=1;ring<=latticeRadius;ring++) {
      let q=ring,r=0,ordinal=0;
      for(const [dq,dr] of walk) for(let step=0;step<ring;step++) {
        ringOrder.set(key(q,r),[ring,ordinal++]);
        q+=dq; r+=dr;
      }
    }

    // Elementary triangles of the regular lattice. Interior vertices have six
    // neighbours instead of dozens of radial edges meeting at one pole.
    const neighbours=[[1,0],[0,1],[-1,1],[-1,0],[0,-1],[1,-1]], triKeys=new Set();
    for(const [q,r] of planar) {
      const a=index.get(key(q,r));
      for(let k=0;k<6;k++) {
        const [dq0,dr0]=neighbours[k],[dq1,dr1]=neighbours[(k+1)%6];
        const kb=key(q+dq0,r+dr0),kc=key(q+dq1,r+dr1);
        if(!index.has(kb)||!index.has(kc)) continue;
        const tri=[a,index.get(kb),index.get(kc)], triKey=tri.slice().sort((x,y)=>x-y).join(',');
        if(triKeys.has(triKey)) continue;
        triKeys.add(triKey); triangles.push(tri);
      }
    }

    const perLayer=planar.length;
    for(let layer=0;layer<=layers;layer++) {
      const t=layer/layers,rounding=.88+.12*Math.pow(Math.sin(Math.PI*t),.6);
      for(const [q,r] of planar) {
        if(q===0&&r===0) { xyz.push(0,.010+t*.042,0); continue; }
        const [ring,ordinal]=ringOrder.get(key(q,r));
        const u=ring/latticeRadius,angle=ordinal/(6*ring)*Math.PI*2;
        const lobes=1+.19*Math.cos(5*angle)+.018*Math.cos(10*angle);
        const radius=.032*u*lobes*rounding;
        xyz.push(radius*Math.cos(angle),.010+t*.042+.0024*(1-2*t)*Math.pow(u,4),radius*Math.sin(angle));
      }
    }

    // A globally ordered prism split gives identical diagonals to adjacent cells.
    for (let l=0; l<layers; l++) for (const tri of triangles) {
      const sorted=tri.slice().sort((a,b)=>a-b);
      const [a,b,c]=sorted.map(v=>v+l*perLayer);
      const A=a+perLayer, B=b+perLayer, C=c+perLayer;
      tets.push([a,b,c,C], [a,b,B,C], [a,A,B,C]);
    }
    const pos = new Float64Array(xyz), faceMap = new Map();
    let totalVolume=0;
    for (const tet of tets) {
      const matrix = () => {
        const [a,b,c,d]=tet.map(v=>v*3);
        return [pos[b]-pos[a],pos[c]-pos[a],pos[d]-pos[a],
          pos[b+1]-pos[a+1],pos[c+1]-pos[a+1],pos[d+1]-pos[a+1],
          pos[b+2]-pos[a+2],pos[c+2]-pos[a+2],pos[d+2]-pos[a+2]];
      };
      let det=determinant(...matrix());
      if (det<0) { [tet[1],tet[2]]=[tet[2],tet[1]]; det=-det; }
      if (det<1e-13) throw new Error('Invalid tetrahedralisation.');
      totalVolume+=det/6;
      const [a,b,c,d]=tet;
      for (const f of [[a,c,b],[a,b,d],[a,d,c],[b,c,d]]) {
        const key=f.slice().sort((x,y)=>x-y).join(',');
        if (faceMap.has(key)) faceMap.delete(key); else faceMap.set(key,f);
      }
    }
    const boundary=[...faceMap.values()];
    // Runtime construction assertions are not an automatically executed test suite.
    const edgeCounts=new Map();
    for (const f of boundary) for (let i=0;i<3;i++) {
      const a=f[i],b=f[(i+1)%3],key=Math.min(a,b)+','+Math.max(a,b);
      edgeCounts.set(key,(edgeCounts.get(key)||0)+1);
    }
    if ([...edgeCounts.values()].some(v=>v!==2)) throw new Error('The optical surface must be watertight.');
    return {pos,tets,boundary,totalVolume};
  }

  export function makeSmoothSurface(cage) {
    // Two Loop-subdivision passes smooth the rendered/optical shell while the
    // underlying tetrahedral simulation cage remains unchanged.
    const cageIds=[...new Set(cage.boundary.flat())];
    const local=new Map(cageIds.map((v,i)=>[v,i]));
    let faces=cage.boundary.map(f=>f.map(v=>local.get(v)));
    let stencils=cageIds.map(v=>[[v,1]]);

    const blendStencil=terms=> {
      const weights=new Map();
      for (const [stencil,scale] of terms) for (const [id,w] of stencil)
        weights.set(id,(weights.get(id)||0)+w*scale);
      return [...weights].filter(([,w])=>Math.abs(w)>1e-12);
    };

    const subdivide=()=> {
      const neighbours=stencils.map(()=>new Set()),edges=new Map();
      for (const f of faces) for (let i=0;i<3;i++) {
        const a=f[i],b=f[(i+1)%3],opposite=f[(i+2)%3];
        neighbours[a].add(b);neighbours[b].add(a);
        const key=Math.min(a,b)+','+Math.max(a,b);
        if(!edges.has(key)) edges.set(key,{a:Math.min(a,b),b:Math.max(a,b),op:[]});
        edges.get(key).op.push(opposite);
      }

      const next=stencils.map((stencil,i)=> {
        const n=neighbours[i].size;
        const beta=(5/8-Math.pow(3/8+Math.cos(2*Math.PI/n)/4,2))/n;
        return blendStencil([[stencil,1-n*beta],...[...neighbours[i]].map(j=>[stencils[j],beta])]);
      });

      for(const edge of edges.values()) {
        if(edge.op.length!==2) throw new Error('Non-manifold subdivision edge.');
        edge.index=next.length;
        next.push(blendStencil([[stencils[edge.a],3/8],[stencils[edge.b],3/8],
          [stencils[edge.op[0]],1/8],[stencils[edge.op[1]],1/8]]));
      }

      const edgeIndex=(a,b)=>edges.get(Math.min(a,b)+','+Math.max(a,b)).index;
      const nextFaces=[];
      for(const [a,b,c] of faces) {
        const ab=edgeIndex(a,b),bc=edgeIndex(b,c),ca=edgeIndex(c,a);
        nextFaces.push([a,ab,ca],[b,bc,ab],[c,ca,bc],[ab,bc,ca]);
      }
      stencils=next;faces=nextFaces;
    };

    subdivide();
    subdivide();

    const indices=faces.flat();
    const positions=new Float32Array(stencils.length*3);
    const geometry=keep(new THREE.BufferGeometry());
    geometry.setAttribute('position',new THREE.BufferAttribute(positions,3).setUsage(THREE.DynamicDrawUsage));
    geometry.setIndex(indices);
    const opticalThickness=new Float32Array(stencils.length).fill(.03);
    geometry.setAttribute('opticalThickness',new THREE.BufferAttribute(opticalThickness,1).setUsage(THREE.DynamicDrawUsage));
    return {geometry,stencils,positions,indices:geometry.index.array};
  }
  export class SoftBody {
    constructor(cage) {
      this.cage=cage; this.x=cage.pos.slice(); this.rest=cage.pos.slice();
      this.previous=this.x.slice(); this.velocity=new Float64Array(this.x.length);
      this.mass=new Float64Array(this.x.length/3); this.inverseMass=new Float64Array(this.mass.length);
      this.contact=new Float64Array(this.mass.length); this.grab=null;
      this.sleeping=false; this.quietTime=0; this.grounded=false; this.internalRms=0; this.rigidRms=0;
      this.elements=[]; this.gradient=new Float64Array(12); this.hydroGradient=new Float64Array(12); this.F=new Float64Array(9);
      const uniqueEdges=new Set(); this.edges=[];
      for (const ids of cage.tets) {
        const [a,b,c,d]=ids.map(v=>v*3),p=this.rest;
        const dm=[p[b]-p[a],p[c]-p[a],p[d]-p[a],p[b+1]-p[a+1],p[c+1]-p[a+1],p[d+1]-p[a+1],p[b+2]-p[a+2],p[c+2]-p[a+2],p[d+2]-p[a+2]];
        const volume=determinant(...dm)/6,inv=inverse3(dm);
        const gradients=new Float64Array(12);
        for(let k=0;k<3;k++) {
          gradients[3+k]=inv[k]; gradients[6+k]=inv[3+k]; gradients[9+k]=inv[6+k];
          gradients[k]=-inv[k]-inv[3+k]-inv[6+k];
        }
        this.elements.push({ids,offsets:ids.map(v=>v*3),volume,gradients,lambdaD:0,lambdaH:0,lambdaB:0});
        for(const i of ids) this.mass[i]+=PHYS.density*volume/4;
        for(let i=0;i<4;i++) for(let j=i+1;j<4;j++) {
          const a=Math.min(ids[i],ids[j]),b=Math.max(ids[i],ids[j]),key=a+','+b;
          if(!uniqueEdges.has(key)) { uniqueEdges.add(key); this.edges.push([a,b]); }
        }
      }
      for(let i=0;i<this.mass.length;i++) this.inverseMass[i]=1/this.mass[i];
      this.totalMass=this.mass.reduce((a,b)=>a+b,0);
      this.surface=makeSmoothSurface(cage);
      this.center=new THREE.Vector3(); this.updateSurface();
    }
    deformation(e) {
      const x=this.x,g=e.gradients,f=this.F;
      f.fill(0);
      for(let v=0;v<4;v++) {
        const i=e.offsets[v],j=v*3;
        // Translation-free evaluation avoids catastrophic cancellation far from origin.
        if(v===0) continue;
        const a=e.offsets[0],dx=x[i]-x[a],dy=x[i+1]-x[a+1],dz=x[i+2]-x[a+2];
        f[0]+=dx*g[j]; f[1]+=dx*g[j+1]; f[2]+=dx*g[j+2];
        f[3]+=dy*g[j]; f[4]+=dy*g[j+1]; f[5]+=dy*g[j+2];
        f[6]+=dz*g[j]; f[7]+=dz*g[j+1]; f[8]+=dz*g[j+2];
      }
      return f;
    }
    project(e,C,compliance,key,inequality=false) {
      const grad=this.gradient,w=this.inverseMass,x=this.x;
      let denom=compliance;
      for(let v=0;v<4;v++) { const j=3*v; denom+=w[e.ids[v]]*(grad[j]**2+grad[j+1]**2+grad[j+2]**2); }
      if(denom<1e-16) return;
      let delta=(-C-compliance*e[key])/denom;
      if(inequality) delta=Math.max(0,e[key]+delta)-e[key];
      e[key]+=delta;
      for(let v=0;v<4;v++) {
        const j=v*3,i=e.offsets[v],s=w[e.ids[v]]*delta;
        x[i]+=s*grad[j]; x[i+1]+=s*grad[j+1]; x[i+2]+=s*grad[j+2];
      }
    }
    // Stable compressible neo-Hookean energy per rest volume:
    // W = mu/2 * (||F||² - 3) + bulk/2 * (J - 1 - mu/bulk)².
    // Its stress vanishes at F=I; the two XPBD constraints split this energy.
    // An additional unilateral determinant barrier resists element inversion.
    // Coupled neo-Hookean XPBD solve. The prior split solved the
    // deviatoric and hydrostatic terms independently; that split leaves a small
    // artificial rest stress, so the constraint solver itself can keep feeding
    // energy into the jelly after physical damping has removed the real motion.
    // Solving the two terms together makes their forces cancel exactly at F=I.
    solveElastic(e,h) {
      const f=this.deformation(e),g=e.gradients,dg=this.gradient,hg=this.hydroGradient;
      let norm=0; for(let k=0;k<9;k++) norm+=f[k]*f[k];
      norm=Math.sqrt(norm); if(norm<1e-12) return;

      const a=f[0],b=f[1],c=f[2],d=f[3],ee=f[4],ff=f[5],gg=f[6],hh=f[7],ii=f[8];
      const c0=ee*ii-ff*hh,c1=ff*gg-d*ii,c2=d*hh-ee*gg;
      const c3=c*hh-b*ii,c4=a*ii-c*gg,c5=b*gg-a*hh;
      const c6=b*ff-c*ee,c7=c*d-a*ff,c8=a*ee-b*d;
      const J=a*c0+b*c1+c*c2;
      const alphaD=1/(PHYS.shear*e.volume*h*h),alphaH=1/(PHYS.bulk*e.volume*h*h);
      let dd=alphaD,hhMass=alphaH,dh=0;

      for(let v=0;v<4;v++) {
        const j=v*3,x=g[j],y=g[j+1],z=g[j+2],w=this.inverseMass[e.ids[v]];
        dg[j]=(a*x+b*y+c*z)/norm;
        dg[j+1]=(d*x+ee*y+ff*z)/norm;
        dg[j+2]=(gg*x+hh*y+ii*z)/norm;
        hg[j]=c0*x+c1*y+c2*z;
        hg[j+1]=c3*x+c4*y+c5*z;
        hg[j+2]=c6*x+c7*y+c8*z;
        for(let k=0;k<3;k++) {
          dd+=w*dg[j+k]*dg[j+k];
          hhMass+=w*hg[j+k]*hg[j+k];
          dh+=w*dg[j+k]*hg[j+k];
        }
      }

      // Same compressible neo-Hookean energy as before:
      // W = mu/2 (||F||^2 - 3) + K/2 (J - 1 - mu/K)^2.
      const rd=-norm-alphaD*e.lambdaD;
      const rh=-(J-1-PHYS.shear/PHYS.bulk)-alphaH*e.lambdaH;
      const denominator=dd*hhMass-dh*dh;
      if(Math.abs(denominator)<1e-20) return;
      const dlD=(rd*hhMass-rh*dh)/denominator;
      const dlH=(rh*dd-rd*dh)/denominator;
      e.lambdaD+=dlD; e.lambdaH+=dlH;

      for(let v=0;v<4;v++) {
        const i=e.offsets[v],j=v*3,w=this.inverseMass[e.ids[v]];
        this.x[i]+=w*(dlD*dg[j]+dlH*hg[j]);
        this.x[i+1]+=w*(dlD*dg[j+1]+dlH*hg[j+1]);
        this.x[i+2]+=w*(dlD*dg[j+2]+dlH*hg[j+2]);
      }
    }

    // Keep the established inversion barrier so extreme-deformation
    // behavior is unchanged; only the ordinary elastic solve is corrected.
    solveBarrier(e) {
      const f=this.deformation(e),g=e.gradients,out=this.gradient;
      const [a,b,c,d,ee,ff,gg,hh,ii]=f;
      const c0=ee*ii-ff*hh,c1=ff*gg-d*ii,c2=d*hh-ee*gg;
      const c3=c*hh-b*ii,c4=a*ii-c*gg,c5=b*gg-a*hh;
      const c6=b*ff-c*ee,c7=c*d-a*ff,c8=a*ee-b*d;
      const J=a*c0+b*c1+c*c2;
      if(J>=.16 && e.lambdaB===0) return;
      for(let v=0;v<4;v++) {
        const j=v*3,g0=g[j],g1=g[j+1],g2=g[j+2];
        out[j]=c0*g0+c1*g1+c2*g2;
        out[j+1]=c3*g0+c4*g1+c5*g2;
        out[j+2]=c6*g0+c7*g1+c8*g2;
      }
      this.project(e,J-.16,0,'lambdaB',true);
    }
    solveGrab(h) {
      const grab=this.grab; if(!grab) return;
      const p=grab.point; p.set(0,0,0);
      let denominator=0;
      for(const [id,weight] of grab.weights) {
        p.x+=this.x[id*3]*weight; p.y+=this.x[id*3+1]*weight; p.z+=this.x[id*3+2]*weight;
        denominator+=this.inverseMass[id]*weight*weight;
      }
      const alpha=1/(90*h*h); denominator+=alpha;
      for(let axis=0;axis<3;axis++) {
        const C=p.getComponent(axis)-grab.target.getComponent(axis);
        // Force limit keeps teleports from driving the FEM into a singular state.
        const dl=(-C-alpha*grab.lambda[axis])/denominator;
        const next=clamp(grab.lambda[axis]+dl,-PHYS.maxGrabForce*h*h,PHYS.maxGrabForce*h*h);
        const change=next-grab.lambda[axis]; grab.lambda[axis]=next;
        for(const [id,weight] of grab.weights) this.x[id*3+axis]+=this.inverseMass[id]*weight*change;
      }
    }
    step(h) {
      if(this.grab) this.wake();
      if(this.sleeping) return;
      const x=this.x,v=this.velocity,old=this.previous;
      old.set(x); this.contact.fill(0);
      for(let i=0;i<this.mass.length;i++) {
        const j=i*3; v[j+1]-=PHYS.gravity*h;
        x[j]+=v[j]*h; x[j+1]+=v[j+1]*h; x[j+2]+=v[j+2]*h;
      }
      for(const e of this.elements) e.lambdaD=e.lambdaH=e.lambdaB=0;
      if(this.grab) this.grab.lambda.fill(0);
      for(let iteration=0;iteration<PHYS.iterations;iteration++) {
        const reverse=(iteration&1)!==0;
        for(let n=0;n<this.elements.length;n++) {
          const e=this.elements[reverse?this.elements.length-1-n:n];
          this.solveElastic(e,h); this.solveBarrier(e);
        }
        this.solveGrab(h);
        for(let i=0;i<this.mass.length;i++) {
          const j=i*3;
          if(x[j+1]<PHYS.floor) {
            this.contact[i]+=PHYS.floor-x[j+1]; x[j+1]=PHYS.floor;
          }
        }
      }
      for(let i=0;i<this.mass.length;i++) {
        const j=i*3,normal=this.contact[i],incoming=v[j+1];
        if(normal>0) {
          const dx=x[j]-old[j],dz=x[j+2]-old[j+2],tangent=Math.hypot(dx,dz);
          const friction=tangent<PHYS.staticFriction*normal ? 1 : Math.min(1,PHYS.dynamicFriction*normal/(tangent+1e-20));
          x[j]-=dx*friction; x[j+2]-=dz*friction;
        }
        v[j]=(x[j]-old[j])/h; v[j+1]=(x[j+1]-old[j+1])/h; v[j+2]=(x[j+2]-old[j+2])/h;
        if(normal>0 && incoming<0) {
          const bounce=incoming<-.18 ? -incoming*PHYS.restitution : 0;
          v[j+1]=Math.max(v[j+1],bounce);
        }
      }
      // Damping is applied to the complete motion, not only deformation.
      // Decompose velocity into COM translation + rigid rotation + internal
      // deformation so the sleep diagnostics can still distinguish them, then
      // exponentially damp both parts at the user-selected s^-1 rate.  This is
      // frame-rate independent linear viscous drag and prevents a released jelly
      // from carrying rigid-body translation or spin indefinitely.
      this.applyDamping(h);

      // The system sleeps from RMS body speed, not the
      // maximum speed of the noisiest node. That distinction is important:
      // XPBD floor contact can leave tiny local chatter indefinitely even after
      // the macroscopic wobble is gone.
      this.grounded=false;
      for(let i=0;i<this.contact.length;i++) if(this.contact[i]>0) { this.grounded=true; break; }
      // XPBD contact/constraint projection has a small reconstructed-velocity
      // noise floor even when the rendered shape is effectively still.  Sleep
      // therefore distinguishes real rigid-body motion from internal solver
      // chatter instead of waiting for an unreachable absolute-speed threshold.
      this.quietTime=!this.grab&&this.grounded&&this.rigidRms<.004&&this.internalRms<.021 ? this.quietTime+h : 0;
      if(this.quietTime>.45) {
        this.sleeping=true;
        v.fill(0); this.internalRms=this.rigidRms=0;
        old.set(x);
      }
    }

    wake() {
      this.sleeping=false;
      this.quietTime=0;
    }


    applyDamping(h) {
      const x=this.x,v=this.velocity,mass=this.mass,total=this.totalMass;
      if(total<=0) return;

      let cx=0,cy=0,cz=0,vx=0,vy=0,vz=0;
      for(let i=0;i<mass.length;i++) {
        const j=i*3,w=mass[i];
        cx+=x[j]*w; cy+=x[j+1]*w; cz+=x[j+2]*w;
        vx+=v[j]*w; vy+=v[j+1]*w; vz+=v[j+2]*w;
      }
      cx/=total; cy/=total; cz/=total;
      vx/=total; vy/=total; vz/=total;

      let ixx=0,iyy=0,izz=0,ixy=0,ixz=0,iyz=0,lx=0,ly=0,lz=0;
      for(let i=0;i<mass.length;i++) {
        const j=i*3,w=mass[i],rx=x[j]-cx,ry=x[j+1]-cy,rz=x[j+2]-cz;
        const ux=v[j]-vx,uy=v[j+1]-vy,uz=v[j+2]-vz;
        ixx+=w*(ry*ry+rz*rz); iyy+=w*(rx*rx+rz*rz); izz+=w*(rx*rx+ry*ry);
        ixy-=w*rx*ry; ixz-=w*rx*rz; iyz-=w*ry*rz;
        lx+=w*(ry*uz-rz*uy); ly+=w*(rz*ux-rx*uz); lz+=w*(rx*uy-ry*ux);
      }

      let wx=0,wy=0,wz=0;
      const det=determinant(ixx,ixy,ixz,ixy,iyy,iyz,ixz,iyz,izz);
      if(Math.abs(det)>1e-18) {
        const inv=inverse3([ixx,ixy,ixz,ixy,iyy,iyz,ixz,iyz,izz]);
        wx=inv[0]*lx+inv[1]*ly+inv[2]*lz;
        wy=inv[3]*lx+inv[4]*ly+inv[5]*lz;
        wz=inv[6]*lx+inv[7]*ly+inv[8]*lz;
      }

      // Exact exponential decay for dv/dt = -damping * v.  Applying the same
      // decay to rigid and internal components makes the control dissipate the
      // whole jelly's kinetic energy while retaining the rigid/internal split
      // purely for diagnostics and sleeping.
      const decay=Math.exp(-Math.max(0,PHYS.damping)*h);
      let internal2=0,rigid2=0;
      for(let i=0;i<mass.length;i++) {
        const j=i*3,w=mass[i],rx=x[j]-cx,ry=x[j+1]-cy,rz=x[j+2]-cz;
        const rigidX=vx+wy*rz-wz*ry;
        const rigidY=vy+wz*rx-wx*rz;
        const rigidZ=vz+wx*ry-wy*rx;
        const dx=(v[j]-rigidX)*decay,dy=(v[j+1]-rigidY)*decay,dz=(v[j+2]-rigidZ)*decay;
        const dampedRigidX=rigidX*decay,dampedRigidY=rigidY*decay,dampedRigidZ=rigidZ*decay;
        v[j]=dampedRigidX+dx; v[j+1]=dampedRigidY+dy; v[j+2]=dampedRigidZ+dz;
        internal2+=w*(dx*dx+dy*dy+dz*dz);
        rigid2+=w*(dampedRigidX*dampedRigidX+dampedRigidY*dampedRigidY+dampedRigidZ*dampedRigidZ);
      }
      this.internalRms=Math.sqrt(internal2/total);
      this.rigidRms=Math.sqrt(rigid2/total);
    }

    updateSurface() {
      const {positions,stencils,geometry}=this.surface;
      for(let i=0;i<stencils.length;i++) {
        let x=0,y=0,z=0;
        for(const [id,w] of stencils[i]) { const j=id*3; x+=this.x[j]*w; y+=this.x[j+1]*w; z+=this.x[j+2]*w; }
        positions[3*i]=x; positions[3*i+1]=y; positions[3*i+2]=z;
      }
      geometry.attributes.position.needsUpdate=true;
      geometry.computeVertexNormals(); geometry.computeBoundingSphere(); geometry.computeBoundingBox();
      this.center.set(0,0,0);
      for(let i=0;i<this.mass.length;i++) {
        const w=this.mass[i]/this.totalMass;
        this.center.x+=this.x[i*3]*w; this.center.y+=this.x[i*3+1]*w; this.center.z+=this.x[i*3+2]*w;
      }
    }
    energy() {
      let E=0;
      for(let i=0;i<this.mass.length;i++) { const j=i*3; E+=.5*this.mass[i]*(this.velocity[j]**2+this.velocity[j+1]**2+this.velocity[j+2]**2); }
      return E;
    }
    volumeRatio() {
      let volume=0;
      for(const e of this.elements) volume+=determinant(...this.deformation(e))*e.volume;
      return volume/this.cage.totalVolume;
    }
    reset() {
      this.x.set(this.rest); this.previous.set(this.rest); this.velocity.fill(0); this.grab=null;
      this.grounded=false; this.internalRms=this.rigidRms=0; this.wake();
      this.updateSurface();
    }
    nudge() {
      if(this.grab) return;
      this.wake();
      // A modest impulse and torque, not an authored wobble animation.
      for(let i=0;i<this.mass.length;i++) {
        const j=i*3,dy=this.x[j+1]-this.center.y;
        this.velocity[j]+=.095+dy*3; this.velocity[j+1]+=.12; this.velocity[j+2]+=.025;
      }
    }
    isFinite() {
      for(let i=0;i<this.x.length;i++) if(!Number.isFinite(this.x[i])||!Number.isFinite(this.velocity[i])||Math.abs(this.x[i])>3) return false;
      return true;
    }
  }
  export class SurfaceBVH {
    constructor(surface) {
      this.surface=surface; this.p=surface.positions; this.index=surface.indices;
      this.centroids=new Float32Array(this.index.length);
      for(let t=0;t<this.index.length/3;t++) for(let axis=0;axis<3;axis++) {
        this.centroids[t*3+axis]=(this.p[this.index[t*3]*3+axis]+this.p[this.index[t*3+1]*3+axis]+this.p[this.index[t*3+2]*3+axis])/3;
      }
      const build=ids=> {
        const node={min:[0,0,0],max:[0,0,0],left:null,right:null,ids:null};
        if(ids.length<=8) node.ids=ids;
        else {
          const ranges=[0,1,2].map(axis=> {
            let lo=Infinity,hi=-Infinity; for(const id of ids) { const x=this.centroids[id*3+axis]; lo=Math.min(lo,x); hi=Math.max(hi,x); } return hi-lo;
          });
          const axis=ranges.indexOf(Math.max(...ranges));
          ids.sort((a,b)=>this.centroids[a*3+axis]-this.centroids[b*3+axis]);
          const mid=ids.length>>1; node.left=build(ids.slice(0,mid)); node.right=build(ids.slice(mid));
        }
        return node;
      };
      this.root=build(Array.from({length:this.index.length/3},(_,i)=>i)); this.refit();
    }
    refit() {
      const p=this.p,ix=this.index;
      const visit=node=> {
        if(node.ids) {
          node.min.fill(Infinity); node.max.fill(-Infinity);
          for(const t of node.ids) for(let c=0;c<3;c++) for(let a=0;a<3;a++) {
            const v=p[ix[t*3+c]*3+a]; node.min[a]=Math.min(node.min[a],v); node.max[a]=Math.max(node.max[a],v);
          }
        } else {
          visit(node.left); visit(node.right);
          for(let a=0;a<3;a++) { node.min[a]=Math.min(node.left.min[a],node.right.min[a]); node.max[a]=Math.max(node.left.max[a],node.right.max[a]); }
        }
      }; visit(this.root);
    }
    hit(o,d,maxDistance=Infinity) {
      const p=this.p,ix=this.index; let nearest=maxDistance,result=null;
      const box=node=> {
        let lo=0,hi=nearest;
        for(let a=0;a<3;a++) {
          if(Math.abs(d[a])<1e-12) { if(o[a]<node.min[a]||o[a]>node.max[a]) return false; }
          else {
            let t0=(node.min[a]-o[a])/d[a],t1=(node.max[a]-o[a])/d[a];
            if(t0>t1) [t0,t1]=[t1,t0]; lo=Math.max(lo,t0); hi=Math.min(hi,t1);
            if(hi<lo) return false;
          }
        } return true;
      };
      const visit=node=> {
        if(!box(node)) return;
        if(!node.ids) { visit(node.left); visit(node.right); return; }
        for(const t of node.ids) {
          const a=ix[t*3]*3,b=ix[t*3+1]*3,c=ix[t*3+2]*3;
          const e1x=p[b]-p[a],e1y=p[b+1]-p[a+1],e1z=p[b+2]-p[a+2];
          const e2x=p[c]-p[a],e2y=p[c+1]-p[a+1],e2z=p[c+2]-p[a+2];
          const hx=d[1]*e2z-d[2]*e2y,hy=d[2]*e2x-d[0]*e2z,hz=d[0]*e2y-d[1]*e2x;
          const det=e1x*hx+e1y*hy+e1z*hz; if(Math.abs(det)<1e-14) continue;
          const inv=1/det,sx=o[0]-p[a],sy=o[1]-p[a+1],sz=o[2]-p[a+2];
          const u=(sx*hx+sy*hy+sz*hz)*inv; if(u<0||u>1) continue;
          const qx=sy*e1z-sz*e1y,qy=sz*e1x-sx*e1z,qz=sx*e1y-sy*e1x;
          const v=(d[0]*qx+d[1]*qy+d[2]*qz)*inv; if(v<0||u+v>1) continue;
          const distance=(e2x*qx+e2y*qy+e2z*qz)*inv;
          if(distance>1e-7 && distance<nearest) { nearest=distance; result={t,u,v,distance}; }
        }
      }; visit(this.root); return result;
    }
    normal(hit,d,entering) {
      const ix=this.index,p=this.p,n=this.surface.geometry.attributes.normal.array;
      const a=ix[hit.t*3]*3,b=ix[hit.t*3+1]*3,c=ix[hit.t*3+2]*3,w=1-hit.u-hit.v;
      let x=n[a]*w+n[b]*hit.u+n[c]*hit.v,y=n[a+1]*w+n[b+1]*hit.u+n[c+1]*hit.v,z=n[a+2]*w+n[b+2]*hit.u+n[c+2]*hit.v;
      // At sharp deformation, a shading normal can point across the true face.
      // Fall back to its geometric normal before orienting against the ray.
      const ex=p[b]-p[a],ey=p[b+1]-p[a+1],ez=p[b+2]-p[a+2];
      const fx=p[c]-p[a],fy=p[c+1]-p[a+1],fz=p[c+2]-p[a+2];
      const gx=ey*fz-ez*fy,gy=ez*fx-ex*fz,gz=ex*fy-ey*fx;
      const sign=entering?1:-1;
      if((x*d[0]+y*d[1]+z*d[2])*sign>-.015) { x=gx; y=gy; z=gz; }
      const len=Math.hypot(x,y,z)||1;
      x=x/len*sign; y=y/len*sign; z=z/len*sign;
      if(x*d[0]+y*d[1]+z*d[2]>0) { x=-x; y=-y; z=-z; }
      return [x,y,z];
    }
  }

  export function refractRay(d,n,n1,n2) {
    const cosine=clamp(-(d[0]*n[0]+d[1]*n[1]+d[2]*n[2]),0,1),eta=n1/n2;
    const k=1-eta*eta*(1-cosine*cosine);
    if(k<0) return null;
    const ct=Math.sqrt(k),a=eta*cosine-ct;
    const rs=(n1*cosine-n2*ct)/(n1*cosine+n2*ct+1e-20);
    const rp=(n2*cosine-n1*ct)/(n2*cosine+n1*ct+1e-20);
    return {direction:[eta*d[0]+a*n[0],eta*d[1]+a*n[1],eta*d[2]+a*n[2]],transmission:1-(rs*rs+rp*rp)/2};
  }

export class RefractiveLightField {
  constructor(surface) {
    this.size=192; this.span=.22; this.minSpan=.22; this.maxSpan=.75; this.origin=new THREE.Vector2();
    this.originNode=uniform(this.origin); this.spanNode=uniform(this.span);
    this.bvh=new SurfaceBVH(surface); this.surface=surface;
    this.shadow=new Float32Array(this.size*this.size);
    this.contact=new Float32Array(this.size*this.size);
    this.blurScratch=new Float32Array(this.size*this.size);
    this.shadowBytes=new Uint8Array(this.size*this.size*4);
    this.shadowTexture=this.makeTexture(this.shadowBytes);
    this.gpu=new GPUCausticField(surface); this.lightTexture=this.gpu.lightTexture;
    this.cleanup=keep({ dispose: () => this.gpu.dispose() });
  }
  setCamera(camera) {
    this.gpu.setCamera(camera);
  }
  sampleIrradiance() {
    return this.gpu.sampleIrradiance();
  }
  makeTexture(data) {
    const tex=keep(new THREE.DataTexture(data,this.size,this.size,THREE.RGBAFormat,THREE.UnsignedByteType));
    tex.minFilter=tex.magFilter=THREE.LinearFilter; tex.generateMipmaps=false;
    tex.colorSpace=THREE.NoColorSpace; tex.needsUpdate=true; return tex;
  }
  rasterTriangle(a,b,c,buffer,value) {
    const n=this.size,scale=n/this.span;
    const ax=(a[0]-this.origin.x)*scale,ay=(a[1]-this.origin.y)*scale;
    const bx=(b[0]-this.origin.x)*scale,by=(b[1]-this.origin.y)*scale;
    const cx=(c[0]-this.origin.x)*scale,cy=(c[1]-this.origin.y)*scale;
    const area=(bx-ax)*(cy-ay)-(by-ay)*(cx-ax); if(Math.abs(area)<1e-9) return;
    const minX=clamp(Math.floor(Math.min(ax,bx,cx)),0,n-1),maxX=clamp(Math.ceil(Math.max(ax,bx,cx)),0,n-1);
    const minY=clamp(Math.floor(Math.min(ay,by,cy)),0,n-1),maxY=clamp(Math.ceil(Math.max(ay,by,cy)),0,n-1);
    for(let y=minY;y<=maxY;y++) for(let x=minX;x<=maxX;x++) {
      const px=x+.5,py=y+.5;
      const u=((bx-px)*(cy-py)-(by-py)*(cx-px))/area;
      const v=((cx-px)*(ay-py)-(cy-py)*(ax-px))/area;
      if(u>=0 && v>=0 && u+v<=1) buffer[y*n+x]=Math.max(buffer[y*n+x],value);
    }
  }
  blur(buffer) {
    const n=this.size,tmp=this.blurScratch;
    for(let y=0;y<n;y++) for(let x=0;x<n;x++) {
      let sum=0; for(let k=-2;k<=2;k++) sum+=buffer[y*n+clamp(x+k,0,n-1)]*(3-Math.abs(k)); tmp[y*n+x]=sum/9;
    }
    for(let y=0;y<n;y++) for(let x=0;x<n;x++) {
      let sum=0; for(let k=-2;k<=2;k++) sum+=tmp[clamp(y+k,0,n-1)*n+x]*(3-Math.abs(k)); buffer[y*n+x]=sum/9;
    }
  }
  clearTextureBorder(bytes,pixels=2) {
    const n=this.size;
    for(let y=0;y<n;y++) for(let x=0;x<n;x++) {
      if(x>=pixels&&x<n-pixels&&y>=pixels&&y<n-pixels) continue;
      const i=(y*n+x)*4; bytes[i]=bytes[i+1]=bytes[i+2]=0; bytes[i+3]=255;
    }
  }
  updateViewThickness(camera) {
    const p=this.surface.positions,n=this.surface.geometry.attributes.normal.array;
    const thickness=this.surface.geometry.attributes.opticalThickness;
    for(let i=0;i<p.length;i+=3) {
      let dx=p[i]-camera.position.x,dy=p[i+1]-camera.position.y,dz=p[i+2]-camera.position.z;
      const length=Math.hypot(dx,dy,dz)||1; dx/=length;dy/=length;dz/=length;
      const normal=[n[i],n[i+1],n[i+2]];
      if(dx*normal[0]+dy*normal[1]+dz*normal[2]>-.01) continue;
      const refraction=refractRay([dx,dy,dz],normal,1,1.35); if(!refraction) continue;
      const dir=refraction.direction,o=[p[i]+dir[0]*2e-6,p[i+1]+dir[1]*2e-6,p[i+2]+dir[2]*2e-6];
      const hit=this.bvh.hit(o,dir);
      thickness.array[i/3]=hit?clamp(hit.distance,.0002,.16):.002;
    }
    thickness.needsUpdate=true;
  }
  update(body) {
    this.bvh.refit(); this.shadow.fill(0); this.contact.fill(0);
    const D=[lightDirection.x,lightDirection.y,lightDirection.z];
    const p=this.surface.positions,ix=this.surface.indices;
    let minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity;
    for(let i=0;i<p.length;i+=3) {
      const x=p[i],y=p[i+1],z=p[i+2];
      const sx=x-y*D[0]/D[1],sz=z-y*D[2]/D[1];
      minX=Math.min(minX,x,sx); maxX=Math.max(maxX,x,sx);
      minZ=Math.min(minZ,z,sz); maxZ=Math.max(maxZ,z,sz);
    }
    const guard=.030;
    const required=Math.max(maxX-minX,maxZ-minZ)+guard*2;
    this.span=clamp(required,this.minSpan,this.maxSpan);
    this.spanNode.value=this.span;
    const centerX=(minX+maxX)/2,centerZ=(minZ+maxZ)/2;
    this.origin.set(centerX-this.span/2,centerZ-this.span/2);
    for(let t=0;t<ix.length;t+=3) {
      const vertices=[ix[t]*3,ix[t+1]*3,ix[t+2]*3];
      const projected=vertices.map(i=>[p[i]-p[i+1]*D[0]/D[1],p[i+2]-p[i+1]*D[2]/D[1]]);
      this.rasterTriangle(...projected,this.shadow,1);
      const height=(p[vertices[0]+1]+p[vertices[1]+1]+p[vertices[2]+1])/3;
      if(height<.016) this.rasterTriangle(...vertices.map(i=>[p[i],p[i+2]]),this.contact,Math.exp(-height/.0028));
    }
    this.blur(this.shadow); this.blur(this.contact);
    for(let i=0;i<this.size*this.size;i++) {
      this.shadowBytes[i*4]=Math.round(this.shadow[i]*255);
      this.shadowBytes[i*4+1]=Math.round(this.contact[i]*255);
      this.shadowBytes[i*4+2]=0; this.shadowBytes[i*4+3]=255;
    }
    this.clearTextureBorder(this.shadowBytes); this.shadowTexture.needsUpdate=true;
  }
  updateGPU(renderer,body,force=false) {
    this.gpu.update(renderer,body,LOOKS[state.flavour].sigma,force);
  }
}


function applyFlavour(name) {
  if (!LOOKS[name]) throw new Error("Unknown softbody-jelly flavour: " + name);
  state.flavour = name;
  const look = LOOKS[name];
  if (jellyMaterial) {
    jellyMaterial.color.set(look.surface);
    jellyMaterial.attenuationColor.setRGB(
      ...look.sigma.map((sigma) =>
        Math.exp(-sigma * jellyMaterial.attenuationDistance),
      ),
      THREE.LinearSRGBColorSpace,
    );
  }
  opticalClock = 1;
}

function eventPointer(event) {
  const rect = domElement.getBoundingClientRect();
  pointer.set(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1,
  );
  camera.updateMatrixWorld();
  raycaster.setFromCamera(pointer, camera);
}

function stopGrab(event) {
  if (event && event.pointerId !== activePointer) return;
  if (event && activePointer !== null) event.stopImmediatePropagation();
  const previousPointer = activePointer;
  activePointer = null;
  if (body) body.grab = null;
  state.dragging = false;
  if (controls) controls.enabled = true;
  if (gripMarker) gripMarker.visible = false;
  if (gripLine) gripLine.visible = false;
  if (
    previousPointer !== null &&
    domElement?.hasPointerCapture?.(previousPointer)
  ) {
    domElement.releasePointerCapture(previousPointer);
  }
  if (domElement?.style) domElement.style.cursor = "grab";
}

function beginGrab(event) {
  if (
    !state.ready ||
    state.paused ||
    state.failed ||
    state.orbiting ||
    event.button !== 0 ||
    activePointer !== null
  ) {
    return;
  }
  eventPointer(event);
  jelly.updateMatrixWorld();
  const hit = raycaster.intersectObject(jelly, false)[0];
  if (!hit) return;

  event.preventDefault();
  event.stopImmediatePropagation();
  activePointer = event.pointerId;
  if (controls) controls.enabled = false;
  state.dragging = true;
  domElement.setPointerCapture?.(activePointer);
  if (domElement.style) domElement.style.cursor = "grabbing";

  const { a, b, c } = hit.face;
  const p = body.surface.positions;
  const triangle = new THREE.Triangle(
    new THREE.Vector3().fromArray(p, a * 3),
    new THREE.Vector3().fromArray(p, b * 3),
    new THREE.Vector3().fromArray(p, c * 3),
  );
  const barycentric = triangle.getBarycoord(
    hit.point,
    new THREE.Vector3(),
  );
  if (!barycentric) {
    stopGrab();
    return;
  }

  const weights = new Map();
  for (const [surfaceId, bary] of [
    [a, barycentric.x],
    [b, barycentric.y],
    [c, barycentric.z],
  ]) {
    for (const [id, weight] of body.surface.stencils[surfaceId]) {
      weights.set(id, (weights.get(id) || 0) + weight * bary);
    }
  }
  const weightList = [...weights].filter(([, weight]) => weight > 1e-8);
  const sum = weightList.reduce((total, [, weight]) => total + weight, 0);
  if (!Number.isFinite(sum) || sum <= 0) {
    stopGrab();
    return;
  }
  for (const pair of weightList) pair[1] /= sum;

  body.wake();
  body.grab = {
    weights: weightList,
    target: hit.point.clone(),
    point: hit.point.clone(),
    lambda: new Float64Array(3),
  };
  camera.getWorldDirection(viewDirection);
  dragPlane.setFromNormalAndCoplanarPoint(viewDirection, hit.point);
  rawTarget.copy(hit.point);
  gripMarker.position.copy(hit.point);
  gripMarker.visible = true;
  gripLine.visible = true;
}

function movePointer(event) {
  if (!state.ready || state.failed) return;
  if (activePointer !== null && event.pointerId !== activePointer) return;
  eventPointer(event);

  if (state.dragging && body.grab) {
    event.preventDefault();
    event.stopImmediatePropagation();
    if (raycaster.ray.intersectPlane(dragPlane, pointerPoint)) {
      rawTarget.set(
        clamp(pointerPoint.x, -0.13, 0.13),
        clamp(pointerPoint.y, 0.002, 0.145),
        clamp(pointerPoint.z, -0.13, 0.13),
      );
    }
  } else if (event.pointerType === "mouse" && domElement.style) {
    domElement.style.cursor = raycaster.intersectObject(jelly, false).length
      ? "grab"
      : "default";
  }
}

function updateGrabTarget(h) {
  if (!body.grab) return;
  const target = body.grab.target;
  const delta = pointerPoint.copy(rawTarget).sub(target);
  const distance = delta.length();
  if (distance > 0) {
    target.addScaledVector(
      delta,
      Math.min(1 - Math.exp(-32 * h), 0.65 * h / distance),
    );
  }
}

function updateGripDisplay() {
  if (!body.grab) return;
  const point = body.grab.point;
  point.set(0, 0, 0);
  for (const [id, weight] of body.grab.weights) {
    point.x += body.x[id * 3] * weight;
    point.y += body.x[id * 3 + 1] * weight;
    point.z += body.x[id * 3 + 2] * weight;
  }
  gripMarker.position.copy(point);
  const positions = gripLine.geometry.attributes.position;
  positions.setXYZ(0, point.x, point.y, point.z);
  positions.setXYZ(
    1,
    body.grab.target.x,
    body.grab.target.y,
    body.grab.target.z,
  );
  positions.needsUpdate = true;
}

function setupInteraction() {
  if (!domElement) return;
  domElement.addEventListener("pointerdown", beginGrab, true);
  domElement.addEventListener("pointermove", movePointer, {
    capture: true,
    passive: false,
  });
  domElement.addEventListener("pointerup", stopGrab, true);
  domElement.addEventListener("pointercancel", stopGrab, true);
  domElement.addEventListener("lostpointercapture", stopGrab);
  interactionCleanups.push(() => {
    domElement.removeEventListener("pointerdown", beginGrab, true);
    domElement.removeEventListener("pointermove", movePointer, true);
    domElement.removeEventListener("pointerup", stopGrab, true);
    domElement.removeEventListener("pointercancel", stopGrab, true);
    domElement.removeEventListener("lostpointercapture", stopGrab);
  });

  if (controls) {
    const onStart = () => {
      state.orbiting = true;
    };
    const onEnd = () => {
      state.orbiting = false;
    };
    controls.addEventListener("start", onStart);
    controls.addEventListener("end", onEnd);
    interactionCleanups.push(() => {
      controls.removeEventListener("start", onStart);
      controls.removeEventListener("end", onEnd);
    });
  }
}

function createJellyMaterial() {
  const material = keep(new THREE.MeshPhysicalNodeMaterial({
    color: "#ffe0eb",
    roughness: 0.075,
    metalness: 0,
    transmission: 1,
    thickness: 0.035,
    ior: 1.35,
    dispersion: 0.025,
    attenuationDistance: 0.035,
    attenuationColor: "#ed5187",
    clearcoat: 0.42,
    clearcoatRoughness: 0.05,
    transparent: false,
    side: THREE.FrontSide,
    flatShading: false,
  }));
  material.thicknessNode = attribute("opticalThickness", "float");
  return material;
}

export function createSoftbodyJellySystem({
  camera: viewCamera,
  controls: orbitControls = null,
  domElement: inputElement = null,
} = {}) {
  if (body && !state.disposed) {
    throw new Error("Only one softbody-jelly system can be active per module.");
  }

  Object.assign(PHYS, SOFTBODY_JELLY_DEFAULTS);
  state.paused = false;
  state.dragging = false;
  state.flavour = "berry";
  state.ready = false;
  state.failed = false;
  state.disposed = false;
  state.orbiting = false;
  state.debugMode = "final";
  accumulator = 0;
  opticalClock = 0;
  activePointer = null;
  interactionCleanups = [];
  camera = viewCamera;
  controls = orbitControls;
  domElement = inputElement;

  body = new SoftBody(makeFlowerCage());
  optics = new RefractiveLightField(body.surface);
  if (camera) optics.setCamera(camera);

  jellyMaterial = createJellyMaterial();
  jelly = new THREE.Mesh(body.surface.geometry, jellyMaterial);
  jelly.name = "SoftbodyJelly";
  jelly.frustumCulled = false;

  wire = new THREE.Mesh(
    body.surface.geometry,
    keep(new THREE.MeshBasicNodeMaterial({
      color: "#7a2048",
      wireframe: true,
      transparent: true,
      opacity: 0.24,
      depthWrite: false,
    })),
  );
  wire.visible = false;
  wire.frustumCulled = false;
  wire.renderOrder = 2;

  gripMarker = new THREE.Mesh(
    keep(new THREE.SphereGeometry(0.0012, 16, 12)),
    keep(new THREE.MeshBasicNodeMaterial({
      color: "#ffffff",
      transparent: true,
      opacity: 0.82,
      depthTest: false,
    })),
  );
  gripMarker.visible = false;
  gripMarker.renderOrder = 4;

  const lineGeometry = keep(new THREE.BufferGeometry());
  lineGeometry.setAttribute(
    "position",
    new THREE.BufferAttribute(
      new Float32Array(6),
      3,
    ).setUsage(THREE.DynamicDrawUsage),
  );
  gripLine = new THREE.Line(
    lineGeometry,
    keep(new THREE.LineBasicNodeMaterial({
      color: "#586b75",
      transparent: true,
      opacity: 0.38,
      depthTest: false,
      depthWrite: false,
    })),
  );
  gripLine.frustumCulled = false;
  gripLine.visible = false;
  gripLine.renderOrder = 3;

  const group = new THREE.Group();
  group.name = "SoftbodyJellySystem";
  group.add(jelly, wire, gripMarker, gripLine);

  applyFlavour("berry");
  optics.update(body);
  if (camera) optics.updateViewThickness(camera);
  setupInteraction();
  state.ready = true;

  function reset() {
    stopGrab();
    body.reset();
    accumulator = 0;
    opticalClock = 1;
  }

  function nudge() {
    if (!state.paused) body.nudge();
  }

  function setPaused(paused) {
    state.paused = Boolean(paused);
    stopGrab();
    accumulator = 0;
  }

  function setDebugMode(mode) {
    const next = SOFTBODY_JELLY_DEBUG_MODES.some((entry) => entry.value === mode)
      ? mode
      : "final";
    state.debugMode = next;
    wire.visible = next === "wireframe";
    jelly.visible = next !== "shadow" && next !== "caustics";
    if (next !== "wireframe") {
      gripMarker.visible = false;
      gripLine.visible = false;
    }
  }

  function update({ delta = 0, rawDelta = delta, camera: view = camera } = {}) {
    if (state.disposed || state.failed || !state.ready) return;

    const wallDelta = Math.min(Math.max(Number(delta) || 0, 0), 0.05);
    let stepped = false;
    if (!state.paused) {
      accumulator += wallDelta;
      let steps = 0;
      while (accumulator >= PHYS.step && steps < 12) {
        updateGrabTarget(PHYS.step);
        body.step(PHYS.step);
        accumulator -= PHYS.step;
        steps += 1;
        stepped = true;
      }
      if (steps === 12) accumulator = Math.min(accumulator, PHYS.step);
    }

    if (stepped) {
      if (!body.isFinite()) {
        reset();
        state.paused = true;
      }
      body.updateSurface();
    }
    updateGripDisplay();

    opticalClock += Math.min(Math.max(Number(rawDelta) || 0, 0), 0.05);
    if (opticalClock >= 1 / 24) {
      optics.update(body);
      if (view) optics.updateViewThickness(view);
      opticalClock = 0;
    }
  }

  function dispose() {
    if (state.disposed) return;
    state.disposed = true;
    state.ready = false;
    stopGrab();
    for (const cleanup of interactionCleanups.splice(0)) cleanup();
    for (const resource of resources) resource.dispose();
    resources.clear();
    group.clear();
    body = null;
    jelly = null;
    wire = null;
    gripMarker = null;
    gripLine = null;
    optics = null;
    jellyMaterial = null;
    camera = null;
    controls = null;
    domElement = null;
  }

  return {
    group,
    body,
    optics,
    jelly,
    wire,
    material: jellyMaterial,
    setDebugMode,
    setFlavour: applyFlavour,
    setPaused,
    setParameters({ shear, damping } = {}) {
      if (Number.isFinite(shear)) PHYS.shear = shear;
      if (Number.isFinite(damping)) PHYS.damping = damping;
      body.wake();
    },
    reset,
    nudge,
    updateGPU(renderer, force = false) {
      if (renderer) optics.updateGPU(renderer, body, force);
    },
    update,
    metrics() {
      return {
        mass: (body.totalMass * 1000).toFixed(1) + " g",
        volume: (body.volumeRatio() * 100).toFixed(1) + " %",
        energy: (body.energy() * 1000).toFixed(1) + " mJ",
        opticalField: optics.size + "×" + optics.size,
        fixedStep: PHYS.step.toFixed(5) + " s",
      };
    },
    dispose,
  };
}
