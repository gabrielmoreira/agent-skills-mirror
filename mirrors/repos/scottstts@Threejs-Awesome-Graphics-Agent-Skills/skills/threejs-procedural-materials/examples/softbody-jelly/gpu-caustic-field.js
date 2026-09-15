import * as THREE from "three/webgpu";
import {
  attribute,
  instanceIndex,
  positionWorld,
  screenCoordinate,
  storage,
  texture,
  uint,
  uniform,
  varying,
  vec4,
  wgsl,
  wgslFn,
} from "three/tsl";

const clamp = (value, minimum, maximum) =>
  Math.max(minimum, Math.min(maximum, value));
const lightDirection = new THREE.Vector3(
  -0.6123724357,
  -0.5,
  0.6123724357,
).normalize();

const CAUSTIC_BASE_GRID = 32;
const CAUSTIC_FINE_GRID = CAUSTIC_BASE_GRID * 2;
const CAUSTIC_RAY_STRIDE = CAUSTIC_FINE_GRID + 1;
const CAUSTIC_RAY_COUNT = CAUSTIC_RAY_STRIDE * CAUSTIC_RAY_STRIDE;
const CAUSTIC_RAY_RECORDS = 5;
const CAUSTIC_CELL_COUNT = CAUSTIC_BASE_GRID * CAUSTIC_BASE_GRID;
const CAUSTIC_BEAM_COUNT = CAUSTIC_CELL_COUNT * 8;
const GPU_CAUSTIC_SIZE = 384;

function buildOpticalBVH(positions, indices, leafSize = 8) {
  const nodes = [];
  const triangles = [];
  const levels = [];
  const centroid = (triangle) => [0, 1, 2].map((axis) =>
    (
      positions[indices[triangle * 3] * 3 + axis] +
      positions[indices[triangle * 3 + 1] * 3 + axis] +
      positions[indices[triangle * 3 + 2] * 3 + axis]
    ) / 3
  );
  const centers = Array.from(
    { length: indices.length / 3 },
    (_, triangle) => centroid(triangle),
  );
  const build = (ids, depth) => {
    const id = nodes.length;
    const node = {
      first: 0,
      count: 0,
      right: 0,
      escape: 0,
      min: [Infinity, Infinity, Infinity],
      max: [-Infinity, -Infinity, -Infinity],
    };
    nodes.push(node);
    (levels[depth] ??= []).push(id);
    for (const triangle of ids) {
      for (let vertex = 0; vertex < 3; vertex += 1) {
        for (let axis = 0; axis < 3; axis += 1) {
          const value = positions[indices[triangle * 3 + vertex] * 3 + axis];
          node.min[axis] = Math.min(node.min[axis], value);
          node.max[axis] = Math.max(node.max[axis], value);
        }
      }
    }
    if (ids.length <= leafSize) {
      node.first = triangles.length;
      node.count = ids.length;
      triangles.push(...ids);
    } else {
      const lo = [Infinity, Infinity, Infinity];
      const hi = [-Infinity, -Infinity, -Infinity];
      for (const triangle of ids) {
        for (let axis = 0; axis < 3; axis += 1) {
          lo[axis] = Math.min(lo[axis], centers[triangle][axis]);
          hi[axis] = Math.max(hi[axis], centers[triangle][axis]);
        }
      }
      const extent = hi.map((value, axis) => value - lo[axis]);
      const axis = extent.indexOf(Math.max(...extent));
      ids.sort((a, b) => centers[a][axis] - centers[b][axis]);
      const mid = ids.length >> 1;
      build(ids.slice(0, mid), depth + 1);
      node.right = build(ids.slice(mid), depth + 1);
    }
    node.escape = nodes.length;
    return id;
  };
  build(Array.from({ length: indices.length / 3 }, (_, index) => index), 0);

  const order = levels.flat();
  const topology = new Uint32Array(
    (nodes.length + triangles.length + order.length) * 4,
  );
  const bounds = new Float32Array(nodes.length * 8);
  for (let index = 0; index < nodes.length; index += 1) {
    const node = nodes[index];
    topology.set(
      [nodes.length + node.first, node.count, node.escape, node.right],
      index * 4,
    );
    bounds.set([...node.min, 0, ...node.max, 0], index * 8);
  }
  for (let index = 0; index < triangles.length; index += 1) {
    const triangle = triangles[index];
    topology.set(
      [...indices.slice(triangle * 3, triangle * 3 + 3), triangle],
      (nodes.length + index) * 4,
    );
  }
  const orderOffset = nodes.length + triangles.length;
  order.forEach((id, index) => {
    topology[(orderOffset + index) * 4] = id;
  });
  let levelStart = orderOffset;
  const refitLevels = levels.map((level) => {
    const result = { start: levelStart, count: level.length };
    levelStart += level.length;
    return result;
  }).reverse();
  return {
    topology,
    bounds,
    refitLevels,
    nodeCount: nodes.length,
  };
}

function packReceiverGeometry(geometry) {
  const attribute = geometry.attributes.position;
  const positions = new Float32Array(attribute.count * 3);
  for (let index = 0; index < attribute.count; index += 1) {
    positions.set([
      attribute.getX(index),
      attribute.getY(index),
      attribute.getZ(index),
    ], index * 3);
  }
  const index = geometry.index
    ? Uint32Array.from(geometry.index.array)
    : Uint32Array.from({ length: attribute.count }, (_, value) => value);
  const start = Math.max(0, geometry.drawRange.start);
  const end = Math.min(index.length, start + geometry.drawRange.count);
  const indices = index.slice(start, end - (end % 3));
  buildOpticalBVH(positions, indices);

  const nodes = [];
  const triangles = [];
  const centers = Array.from(
    { length: indices.length / 3 },
    (_, triangle) => [0, 1, 2].map((axis) =>
      (
        positions[indices[triangle * 3] * 3 + axis] +
        positions[indices[triangle * 3 + 1] * 3 + axis] +
        positions[indices[triangle * 3 + 2] * 3 + axis]
      ) / 3
    ),
  );
  const build = (ids) => {
    const id = nodes.length;
    const node = {
      first: 0,
      count: 0,
      right: 0,
      escape: 0,
      min: [Infinity, Infinity, Infinity],
      max: [-Infinity, -Infinity, -Infinity],
    };
    nodes.push(node);
    for (const triangle of ids) {
      for (let vertex = 0; vertex < 3; vertex += 1) {
        for (let axis = 0; axis < 3; axis += 1) {
          const value = positions[indices[triangle * 3 + vertex] * 3 + axis];
          node.min[axis] = Math.min(node.min[axis], value);
          node.max[axis] = Math.max(node.max[axis], value);
        }
      }
    }
    if (ids.length <= 8) {
      node.first = triangles.length;
      node.count = ids.length;
      triangles.push(...ids);
    } else {
      const lo = [Infinity, Infinity, Infinity];
      const hi = [-Infinity, -Infinity, -Infinity];
      for (const triangle of ids) {
        for (let axis = 0; axis < 3; axis += 1) {
          lo[axis] = Math.min(lo[axis], centers[triangle][axis]);
          hi[axis] = Math.max(hi[axis], centers[triangle][axis]);
        }
      }
      const extent = hi.map((value, axis) => value - lo[axis]);
      const axis = extent.indexOf(Math.max(...extent));
      ids.sort((a, b) => centers[a][axis] - centers[b][axis]);
      const mid = ids.length >> 1;
      build(ids.slice(0, mid));
      node.right = build(ids.slice(mid));
    }
    node.escape = nodes.length;
    return id;
  };
  build(Array.from({ length: indices.length / 3 }, (_, value) => value));

  const data = new Float32Array((nodes.length + triangles.length) * 12);
  nodes.forEach((node, index) => {
    data.set([
      ...node.min,
      node.count,
      ...node.max,
      node.escape * 3,
      (nodes.length + node.first) * 3,
      0,
      0,
      0,
    ], index * 12);
  });
  triangles.forEach((triangle, index) => {
    for (let vertex = 0; vertex < 3; vertex += 1) {
      data.set(
        [...positions.slice(
          indices[triangle * 3 + vertex] * 3,
          indices[triangle * 3 + vertex] * 3 + 3,
        ), 0],
        (nodes.length + index) * 12 + vertex * 4,
      );
    }
  });
  return { data, nodeEnd: nodes.length * 3 };
}

function gpuBuffer(data, type = "vec4", readOnly = false) {
  const size = type === "uint" ? 1 : 4;
  const node = storage(new THREE.StorageBufferAttribute(data, size), type, 0);
  return readOnly ? node.toReadOnly() : node;
}

function causticTarget(type, depthBuffer = false) {
  const target = new THREE.RenderTarget(
    GPU_CAUSTIC_SIZE,
    GPU_CAUSTIC_SIZE,
    { type, depthBuffer, stencilBuffer: false },
  );
  target.texture.colorSpace = THREE.NoColorSpace;
  target.texture.generateMipmaps = false;
  target.texture.minFilter = target.texture.magFilter = THREE.NearestFilter;
  return target;
}

const causticCommon = wgsl(`
const J_GRID: u32 = ${CAUSTIC_FINE_GRID}u;
const J_STRIDE: u32 = ${CAUSTIC_RAY_STRIDE}u;
const J_BASE: u32 = ${CAUSTIC_BASE_GRID}u;
const J_EPS: f32 = 0.000002;
fn j_box(o:vec3f,d:vec3f,lo:vec3f,hi:vec3f,limit:f32)->bool {
  var near=0.0;var far=limit;
  for(var a=0u;a<3u;a++){
    if(abs(d[a])<1e-12){if(o[a]<lo[a] || o[a]>hi[a]){return false;}}
    else {let t0=(lo[a]-o[a])/d[a];let t1=(hi[a]-o[a])/d[a];near=max(near,min(t0,t1));far=min(far,max(t0,t1));}
  }
  return far>=near;
}
fn j_triangle(o:vec3f,d:vec3f,a:vec3f,b:vec3f,c:vec3f,limit:f32)->vec3f {
  let e=b-a;let f=c-a;let h=cross(d,f);let det=dot(e,h);
  if(abs(det)<1e-15){return vec3f(-1.0);}
  let s=o-a;let u=dot(s,h)/det;let q=cross(s,e);let v=dot(d,q)/det;let t=dot(f,q)/det;
  if(u<0.0 || v<0.0 || u+v>1.0 || t<=J_EPS*0.25 || t>=limit){return vec3f(-1.0);}
  return vec3f(t,u,v);
}
fn j_refract(d:vec3f,n:vec3f,n1:f32,n2:f32)->vec4f {
  let c=clamp(-dot(d,n),0.0,1.0);let eta=n1/n2;let k=1.0-eta*eta*(1.0-c*c);
  if(k<=0.0){return vec4f(0.0);}
  let ct=sqrt(k);let rs=(n1*c-n2*ct)/max(n1*c+n2*ct,1e-12);let rp=(n2*c-n1*ct)/max(n2*c+n1*ct,1e-12);
  return vec4f(normalize(eta*d+(eta*c-ct)*n),1.0-(rs*rs+rp*rp)*0.5);
}
fn j_hit(o:vec3f,d:vec3f,limit:f32,vertices:ptr<storage,array<vec4f>,read_write>,tree:ptr<storage,array<vec4u>,read>,bounds:ptr<storage,array<vec4f>,read_write>,nodeCount:u32)->vec4f {
  var best=vec4f(limit,-1.0,0.0,0.0);var node=0u;
  loop {
    if(node>=nodeCount){break;}
    let record=(*tree)[node];
    if(!j_box(o,d,(*bounds)[node*2u].xyz,(*bounds)[node*2u+1u].xyz,best.x)){node=record.z;continue;}
    if(record.y==0u){node++;continue;}
    for(var i=0u;i<record.y;i++){
      let ids=(*tree)[record.x+i];let hit=j_triangle(o,d,(*vertices)[ids.x*2u].xyz,(*vertices)[ids.y*2u].xyz,(*vertices)[ids.z*2u].xyz,best.x);
      if(hit.x>0.0){best=vec4f(hit.x,f32(record.x+i),hit.y,hit.z);}
    }
    node=record.z;
  }
  return best;
}
fn j_normal(hit:vec4f,d:vec3f,vertices:ptr<storage,array<vec4f>,read_write>,tree:ptr<storage,array<vec4u>,read>)->vec3f {
  let ids=(*tree)[u32(hit.y)];let a=(*vertices)[ids.x*2u].xyz;let b=(*vertices)[ids.y*2u].xyz;let c=(*vertices)[ids.z*2u].xyz;
  let face=normalize(cross(b-a,c-a));
  var n=normalize((*vertices)[ids.x*2u+1u].xyz*(1.0-hit.z-hit.w)+(*vertices)[ids.y*2u+1u].xyz*hit.z+(*vertices)[ids.z*2u+1u].xyz*hit.w);
  if(dot(n,face)<0.0){n=-n;}
  if(dot(n,d)*dot(face,d)<=0.0 || abs(dot(n,d))<0.015){n=face;}
  return select(n,-n,dot(n,d)>0.0);
}
fn j_receiver(o:vec3f,d:vec3f,limit:f32,geometry:ptr<storage,array<vec4f>,read>,instances:ptr<storage,array<vec4f>,read>,count:u32)->mat2x4f {
  var best=limit;var normal=vec3f(0.0);var receiver=0.0;
  for(var mesh=0u;mesh<count;mesh++){
    let base=mesh*8u;let lo=(*instances)[base];let hi=(*instances)[base+1u];
    if(!j_box(o,d,lo.xyz,hi.xyz,best)){continue;}
    let r0=(*instances)[base+2u];let r1=(*instances)[base+3u];let r2=(*instances)[base+4u];
    let localO=vec3f(dot(r0,vec4f(o,1.0)),dot(r1,vec4f(o,1.0)),dot(r2,vec4f(o,1.0)));
    let localD=vec3f(dot(r0.xyz,d),dot(r1.xyz,d),dot(r2.xyz,d));
    let record=(*instances)[base+5u];let offset=u32(record.x);var node=0u;
    loop {
      if(node>=u32(record.y)){break;}
      let a=(*geometry)[offset+node];let b=(*geometry)[offset+node+1u];
      if(!j_box(localO,localD,a.xyz,b.xyz,best)){node=u32(b.w);continue;}
      if(a.w==0.0){node+=3u;continue;}
      let first=u32((*geometry)[offset+node+2u].x);
      for(var i=0u;i<u32(a.w);i++){
        let tri=offset+first+i*3u;let p=(*geometry)[tri].xyz;let q=(*geometry)[tri+1u].xyz;let r=(*geometry)[tri+2u].xyz;
        let hit=j_triangle(localO,localD,p,q,r,best);
        if(hit.x>0.0){
          best=hit.x;receiver=record.z;
          let n=cross(q-p,r-p);normal=normalize(r0.xyz*n.x+r1.xyz*n.y+r2.xyz*n.z);
          normal=select(normal,-normal,dot(normal,d)>0.0);
        }
      }
      node=u32(b.w);
    }
  }
  return mat2x4f(vec4f(o+d*best,receiver),vec4f(normal,best));
}
`);

const causticRefitKernel = wgslFn(`fn jelly_refit(id:u32,start:u32,vertices:ptr<storage,array<vec4f>,read_write>,tree:ptr<storage,array<vec4u>,read>,bounds:ptr<storage,array<vec4f>,read_write>)->u32 {
  let node=(*tree)[start+id].x;let record=(*tree)[node];var lo=vec3f(1e20);var hi=vec3f(-1e20);
  if(record.y>0u){for(var i=0u;i<record.y;i++){let ids=(*tree)[record.x+i];for(var c=0u;c<3u;c++){let p=(*vertices)[ids[c]*2u].xyz;lo=min(lo,p);hi=max(hi,p);}}}
  else {lo=min((*bounds)[(node+1u)*2u].xyz,(*bounds)[record.w*2u].xyz);hi=max((*bounds)[(node+1u)*2u+1u].xyz,(*bounds)[record.w*2u+1u].xyz);}
  (*bounds)[node*2u]=vec4f(lo,0.0);(*bounds)[node*2u+1u]=vec4f(hi,0.0);return 0u;
}`, [causticCommon]);

const causticTraceKernel = wgslFn(`fn jelly_trace(id:u32,phase:u32,vertices:ptr<storage,array<vec4f>,read_write>,tree:ptr<storage,array<vec4u>,read>,bounds:ptr<storage,array<vec4f>,read_write>,rays:ptr<storage,array<vec4f>,read_write>,flags:ptr<storage,array<u32>,read_write>,geometry:ptr<storage,array<vec4f>,read>,instances:ptr<storage,array<vec4f>,read>,nodeCount:u32,receiverCount:u32,source:vec4f,right:vec3f,up:vec3f,incoming:vec3f,sigma:vec3f,reach:f32)->u32 {
  let x=id%J_STRIDE;let y=id/J_STRIDE;
  let oddX=(x&1u)!=0u;let oddY=(y&1u)!=0u;
  if(phase==0u && (oddX || oddY)){return 0u;}
  if(phase==1u && !(oddX && oddY)){return 0u;}
  if(phase==2u){
    if(oddX==oddY){return 0u;}
    let cx=min(x/2u,J_BASE-1u);let cy=min(y/2u,J_BASE-1u);
    var needed=(*flags)[cy*J_BASE+cx]>0u;
    if(oddX && y>0u){needed=needed || (*flags)[(y/2u-1u)*J_BASE+cx]>0u;}
    if(oddY && x>0u){needed=needed || (*flags)[cy*J_BASE+x/2u-1u]>0u;}
    if(!needed){for(var k=0u;k<5u;k++){(*rays)[id*5u+k]=vec4f(0.0);}return 0u;}
  }
  let out=id*5u;for(var k=0u;k<5u;k++){(*rays)[out+k]=vec4f(0.0);}
  let d=incoming;
  let o=right*((f32(x)/f32(J_GRID)-0.5)*source.x+source.z)+up*((f32(y)/f32(J_GRID)-0.5)*source.y+source.w)-d*reach;
  let entry=j_hit(o,d,reach*3.0,vertices,tree,bounds,nodeCount);if(entry.y<0.0){return 0u;}
  let en=j_normal(entry,d,vertices,tree);let refracted=j_refract(d,en,1.0,1.35);
  if(refracted.w<=0.0){return 0u;}
  var direction=refracted.xyz;var throughput=refracted.w;var path=0.0;
  let ep=o+d*entry.x;var origin=ep+direction*J_EPS;var branch=1u;var escaped=false;var exitPoint=ep;
  var inside=true;
  for(var event=0u;event<8u;event++){
    let hit=j_hit(origin,direction,reach*4.0,vertices,tree,bounds,nodeCount);
    if(hit.y<0.0){if(!inside){escaped=true;}break;}
    if(!inside){let obstruction=j_receiver(origin,direction,hit.x,geometry,instances,receiverCount);if(obstruction[0].w>0.0){escaped=true;break;}}
    if(inside){path+=hit.x;}
    exitPoint=origin+direction*hit.x;
    let n=j_normal(hit,direction,vertices,tree);
    let eta1=select(1.0,1.35,inside);let eta2=select(1.35,1.0,inside);let refraction=j_refract(direction,n,eta1,eta2);
    if(refraction.w>0.0){throughput*=refraction.w;direction=refraction.xyz;inside=!inside;branch=branch*3u+1u;}
    else {direction=reflect(direction,n);branch=branch*3u+2u;}
    origin=exitPoint+direction*J_EPS;
    if(throughput*exp(-min(sigma.x,min(sigma.y,sigma.z))*path)<0.0001){break;}
  }
  if(!escaped || inside){return 0u;}
  let receiver=j_receiver(origin,direction,reach*4.0,geometry,instances,receiverCount);
  if(receiver[0].w<=0.0){return 0u;}
  (*rays)[out]=vec4f(receiver[0].xyz,f32(branch));
  (*rays)[out+1u]=vec4f(exp(-sigma*path)*throughput,receiver[0].w);
  (*rays)[out+2u]=vec4f(receiver[1].xyz,entry.x);
  (*rays)[out+3u]=vec4f(exitPoint,path);
  (*rays)[out+4u]=vec4f(direction,0.0);
  return 0u;
}`, [causticCommon]);

const causticRefineKernel = wgslFn(`fn jelly_refine(id:u32,rays:ptr<storage,array<vec4f>,read_write>,flags:ptr<storage,array<u32>,read_write>,pixel:f32)->u32 {
  let x=id%J_BASE;let y=id/J_BASE;
  var refine=false;var anyValid=false;
  let threshold=pixel*select(0.6,0.35,(*flags)[id]>0u);
  let a=y*2u*J_STRIDE+x*2u;let center=a+J_STRIDE+1u;
  let ids=array<u32,4>(a,a+2u,a+J_STRIDE*2u,a+J_STRIDE*2u+2u);
  let c=(*rays)[center*5u];let cr=(*rays)[center*5u+1u];var mean=vec3f(0.0);anyValid=anyValid || c.w>0.0;
  for(var i=0u;i<4u;i++){let p=(*rays)[ids[i]*5u];let t=(*rays)[ids[i]*5u+1u];mean+=p.xyz*0.25;anyValid=anyValid || p.w>0.0;
    refine=refine || p.w!=c.w || t.w!=cr.w || distance(t.xyz,cr.xyz)>0.12;
  }
  refine=refine || distance(mean,c.xyz)>threshold;
  refine=anyValid && refine;
  (*flags)[id]=select(0u,1u,refine);return 0u;
}`, [causticCommon]);

const beamCode = wgsl(`
const B_SIZE:f32=${GPU_CAUSTIC_SIZE}.0;
fn b_ids(id:u32,flags:ptr<storage,array<u32>,read>)->vec4u {
  let cell=id/8u;let part=id%8u;
  let root=(cell/${CAUSTIC_BASE_GRID}u)*2u*${CAUSTIC_RAY_STRIDE}u+(cell%${CAUSTIC_BASE_GRID}u)*2u;
  let refined=(*flags)[cell]>0u;
  if(!refined && part>=2u){return vec4u(0u);}
  let step=select(2u,1u,refined);let sub=select(0u,part/2u,refined);
  let a=root+(sub/2u)*${CAUSTIC_RAY_STRIDE}u+sub%2u;let b=a+step;let c=a+step*${CAUSTIC_RAY_STRIDE}u;let d=c+step;
  return select(vec4u(a,b,d,step),vec4u(a,d,c,step),(part&1u)>0u);
}
fn b_project(p:vec3f,matrix:mat4x4f)->vec3f {
  let clip=matrix*vec4f(p,1.0);let ndc=clip.xy/max(clip.w,1e-8);
  return vec3f(vec2f(ndc.x*0.5+0.5,0.5-ndc.y*0.5)*B_SIZE,clip.w);
}
fn b_valid(ids:vec4u,rays:ptr<storage,array<vec4f>,read>)->bool {
  if(ids.w==0u){return false;}
  let a=(*rays)[ids.x*5u];let b=(*rays)[ids.y*5u];let c=(*rays)[ids.z*5u];
  if(a.w<=0.0 || a.w!=b.w || a.w!=c.w){return false;}
  let identity=(*rays)[ids.x*5u+1u].w;
  if(identity!=(*rays)[ids.y*5u+1u].w || identity!=(*rays)[ids.z*5u+1u].w){return false;}
  let na=(*rays)[ids.x*5u+2u].xyz;let nb=(*rays)[ids.y*5u+2u].xyz;let nc=(*rays)[ids.z*5u+2u].xyz;
  return dot(na,nb)>0.75 && dot(na,nc)>0.75;
}
fn b_cross(a:vec2f,b:vec2f)->f32{return a.x*b.y-a.y*b.x;}
fn b_coverage(a:vec2f,b:vec2f,c:vec2f,pixel:vec2f)->f32 {
  var poly:array<vec2f,8>;var next:array<vec2f,8>;poly[0]=a;poly[1]=b;poly[2]=c;var count=3u;
  let lo=floor(pixel);let hi=lo+1.0;
  for(var edge=0u;edge<4u;edge++){
    if(count<3u){return 0.0;}var n=0u;let axis=edge/2u;let lower=(edge&1u)==0u;let bound=select(hi[axis],lo[axis],lower);
    for(var i=0u;i<count;i++){
      let p=poly[i];let q=poly[(i+1u)%count];let pin=select(p[axis]<=bound,p[axis]>=bound,lower);let qin=select(q[axis]<=bound,q[axis]>=bound,lower);
      if(pin){next[n]=p;n++;}
      if(pin!=qin){next[n]=mix(p,q,(bound-p[axis])/(q[axis]-p[axis]));n++;}
    }
    count=n;for(var i=0u;i<count;i++){poly[i]=next[i];}
  }
  var area=0.0;for(var i=1u;i+1u<count;i++){area+=b_cross(poly[i]-poly[0],poly[i+1u]-poly[0]);}
  return min(1.0,abs(area)*0.5);
}
`);

const beamVertex = wgslFn(`fn jelly_beam_vertex(id:u32,corner:vec2f,rays:ptr<storage,array<vec4f>,read>,flags:ptr<storage,array<u32>,read>,matrix:mat4x4f)->vec4f {
  let ids=b_ids(id,flags);if(!b_valid(ids,rays)){return vec4f(2.0,2.0,0.0,1.0);}
  let a=b_project((*rays)[ids.x*5u].xyz,matrix);let b=b_project((*rays)[ids.y*5u].xyz,matrix);let c=b_project((*rays)[ids.z*5u].xyz,matrix);
  if(min(a.z,min(b.z,c.z))<=0.0){return vec4f(2.0,2.0,0.0,1.0);}
  let lo=max(vec2f(0.0),floor(min(a.xy,min(b.xy,c.xy)))-1.0);let hi=min(vec2f(${GPU_CAUSTIC_SIZE}.0),ceil(max(a.xy,max(b.xy,c.xy)))+1.0);
  let pixel=mix(lo,hi,corner);return vec4f(pixel.x/${GPU_CAUSTIC_SIZE}.0*2.0-1.0,1.0-pixel.y/${GPU_CAUSTIC_SIZE}.0*2.0,0.0,1.0);
}`, [beamCode]);

const beamFragment = wgslFn(`fn jelly_beam_fragment(id:u32,pixel:vec2f,rays:ptr<storage,array<vec4f>,read>,flags:ptr<storage,array<u32>,read>,matrix:mat4x4f,receiver:texture_2d<f32>,sourceArea:f32)->vec4f {
  let sample=textureLoad(receiver,vec2i(pixel),0);
  let px=dpdx(sample.xyz);let py=dpdy(sample.xyz);let pixelArea=max(length(cross(px,py)),1e-12);
  let ids=b_ids(id,flags);if(!b_valid(ids,rays)){discard;}
  let pa=(*rays)[ids.x*5u].xyz;let pb=(*rays)[ids.y*5u].xyz;let pc=(*rays)[ids.z*5u].xyz;
  let a=b_project(pa,matrix).xy;let b=b_project(pb,matrix).xy;let c=b_project(pc,matrix).xy;
  let identity=(*rays)[ids.x*5u+1u].w;
  if(abs(sample.w-identity)>0.1){discard;}
  let area=length(cross(pb-pa,pc-pa))*0.5;
  let screenArea=abs(b_cross(b-a,c-a))*0.5;
  let power=((*rays)[ids.x*5u+1u].xyz+(*rays)[ids.y*5u+1u].xyz+(*rays)[ids.z*5u+1u].xyz)/3.0*sourceArea*f32(ids.w*ids.w);
  var energy=vec3f(0.0);
  if(screenArea<1e-5 || area<1e-14){
    if(any(vec2i(pixel)!=vec2i((a+b+c)/3.0))){discard;}energy=power/pixelArea;
  }else {
    let coverage=b_coverage(a,b,c,pixel);if(coverage<=0.0){discard;}
    energy=power/area*coverage;
  }
  let n=(*rays)[ids.x*5u+2u].xyz;let tolerance=max(sqrt(pixelArea)*2.5,0.00015);
  if(abs(dot(sample.xyz-pa,n))>tolerance){discard;}
  return vec4f(min(energy,vec3f(60000.0)),0.0);
}`, [beamCode]);

const reconstructCaustics = wgslFn(`fn jelly_reconstruct_caustics(pixel:vec2f,raw:texture_2d<f32>,receivers:texture_2d<f32>)->vec4f {
  let coord=vec2i(pixel);let limit=vec2i(textureDimensions(raw))-vec2i(1);
  let center=textureLoad(receivers,coord,0);
  let dx=dpdx(center.xyz);let dy=dpdy(center.xyz);
  let areaNormal=cross(dx,dy);let n=areaNormal/max(length(areaNormal),1e-12);
  let pixelWidth=max(length(dx),length(dy));
  var sum=vec3f(0.0);var total=0.0;
  for(var y=-1;y<=1;y++){for(var x=-1;x<=1;x++){
    let tap=clamp(coord+vec2i(x,y),vec2i(0),limit);
    let surface=textureLoad(receivers,tap,0);let delta=surface.xyz-center.xyz;
    let same=abs(surface.w-center.w)<0.1 && length(delta)<=max(pixelWidth*2.5,0.00015)
      && abs(dot(delta,n))<=max(pixelWidth*0.5,0.00005);
    if(same){
      let weight=select(1.0,4.0,x==0)*select(1.0,4.0,y==0);
      sum+=textureLoad(raw,tap,0).rgb*weight;total+=weight;
    }
  }}
  return vec4f(sum/max(total,1.0),0.0);
}`);

const sampleCausticIrradiance = wgslFn(`fn jelly_sample_caustic(world:vec3f,center:vec3f,matrix:mat4x4f,light:texture_2d<f32>,receivers:texture_2d<f32>,pixelWorld:f32)->vec3f {
  let local=world-center;let clip=matrix*vec4f(local,1.0);
  if(clip.w<=0.0){return vec3f(0.0);}
  let uv=vec2f(clip.x/clip.w*0.5+0.5,0.5-clip.y/clip.w*0.5);
  if(uv.x<=0.0 || uv.x>=1.0 || uv.y<=0.0 || uv.y>=1.0){return vec3f(0.0);}
  let localDx=dpdx(local);let localDy=dpdy(local);let uvDx=dpdx(uv);let uvDy=dpdy(uv);
  let det=max(abs(uvDx.x*uvDy.y-uvDy.x*uvDx.y),1e-9);
  let atlasScale=(1.0/${GPU_CAUSTIC_SIZE}.0)/det;
  let atlasStepU=(localDx*uvDy.y-localDy*uvDx.y)*atlasScale;
  let atlasStepV=(localDy*uvDx.x-localDx*uvDy.x)*atlasScale;
  let continuityRadius=max(length(vec2f(length(atlasStepU),length(atlasStepV)))*1.25,pixelWorld*4.0);
  let pixel=uv*${GPU_CAUSTIC_SIZE}.0-0.5;let base=floor(pixel);let fraction=fract(pixel);
  var result=vec3f(0.0);var weightSum=0.0;
  for(var y=0;y<2;y++){for(var x=0;x<2;x++){
    let coord=clamp(vec2i(base)+vec2i(x,y),vec2i(0),vec2i(${GPU_CAUSTIC_SIZE-1}));
    let surface=textureLoad(receivers,coord,0);
    let valid=abs(surface.w-1.0)<0.1 && distance(surface.xyz,local)<continuityRadius;
    let wx=select(1.0-fraction.x,fraction.x,x==1);let wy=select(1.0-fraction.y,fraction.y,y==1);
    let weight=wx*wy*select(0.0,1.0,valid);
    result+=textureLoad(light,coord,0).rgb*weight;weightSum+=weight;
  }}
  return result/max(weightSum,1e-6);
}`);

export class GPUCausticField {
  constructor(surface) {
    this.surface = surface;
    this.hierarchy = buildOpticalBVH(surface.positions, surface.indices);
    this.topologyNode = gpuBuffer(this.hierarchy.topology, "uvec4", true);
    this.boundsNode = gpuBuffer(this.hierarchy.bounds);
    this.verticesNode = gpuBuffer(
      new Float32Array(surface.positions.length / 3 * 8),
    );
    this.raysNode = gpuBuffer(
      new Float32Array(CAUSTIC_RAY_COUNT * CAUSTIC_RAY_RECORDS * 4),
    );
    this.flagsNode = gpuBuffer(new Uint32Array(CAUSTIC_CELL_COUNT), "uint");
    this.sourceNode = uniform(new THREE.Vector4());
    this.rightNode = uniform(new THREE.Vector3());
    this.upNode = uniform(new THREE.Vector3());
    this.incomingNode = uniform(lightDirection.clone());
    this.absorptionNode = uniform(new THREE.Vector3());
    this.reachNode = uniform(0.3);
    this.pixelNode = uniform(0.001);
    this.centerNode = uniform(new THREE.Vector3());
    this.lookupMatrixNode = uniform(new THREE.Matrix4());
    this.receiverTarget = causticTarget(THREE.FloatType, true);
    this.rawTarget = causticTarget(THREE.HalfFloatType);
    this.outputTarget = causticTarget(THREE.HalfFloatType);
    this.lightTexture = this.outputTarget.texture;

    this.receiverMaterial = new THREE.MeshBasicNodeMaterial({
      side: THREE.DoubleSide,
      toneMapped: false,
    });
    this.receiverMaterial.fragmentNode = vec4(
      positionWorld.sub(this.centerNode),
      1,
    );
    this.receiverGeometry = new THREE.PlaneGeometry(2, 2);
    this.receiverGeometry.computeBoundingBox();
    this.receiverMesh = new THREE.Mesh(
      this.receiverGeometry,
      this.receiverMaterial,
    );
    this.receiverMesh.rotation.x = -Math.PI / 2;
    this.receiverMesh.position.y = -0.00005;
    this.receiverMesh.frustumCulled = false;
    this.receiverScene = new THREE.Scene();
    this.receiverScene.background = new THREE.Color(0);
    this.receiverScene.add(this.receiverMesh);
    this.receiverPacked = packReceiverGeometry(this.receiverGeometry);
    this.receiverGeometryNode = gpuBuffer(
      this.receiverPacked.data,
      "vec4",
      true,
    );
    this.receiverInstancesNode = gpuBuffer(
      new Float32Array(32),
      "vec4",
      true,
    );

    const rayRead = storage(
      this.raysNode.value,
      "vec4",
      0,
    ).toReadOnly();
    const flagRead = storage(
      this.flagsNode.value,
      "uint",
      0,
    ).toReadOnly();
    this.beamGeometry = new THREE.InstancedBufferGeometry();
    this.beamGeometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(
        [0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0],
        3,
      ),
    );
    this.beamGeometry.setAttribute(
      "corner",
      new THREE.Float32BufferAttribute(
        [0, 0, 1, 0, 1, 1, 0, 1],
        2,
      ),
    );
    this.beamGeometry.setIndex([0, 1, 2, 0, 2, 3]);
    this.beamGeometry.instanceCount = CAUSTIC_BEAM_COUNT;
    this.beamMatrixNode = uniform(new THREE.Matrix4());
    this.sourceAreaNode = uniform(1);
    this.beamMaterial = new THREE.MeshBasicNodeMaterial({
      depthTest: false,
      depthWrite: false,
      transparent: true,
      side: THREE.DoubleSide,
      toneMapped: false,
      blending: THREE.CustomBlending,
      blendEquation: THREE.AddEquation,
      blendSrc: THREE.OneFactor,
      blendDst: THREE.OneFactor,
    });
    this.beamMaterial.vertexNode = beamVertex({
      id: instanceIndex,
      corner: attribute("corner", "vec2"),
      rays: rayRead,
      flags: flagRead,
      matrix: this.beamMatrixNode,
    });
    this.beamMaterial.fragmentNode = beamFragment({
      id: varying(instanceIndex),
      pixel: screenCoordinate,
      rays: rayRead,
      flags: flagRead,
      matrix: this.beamMatrixNode,
      receiver: texture(this.receiverTarget.texture),
      sourceArea: this.sourceAreaNode,
    });
    this.beamScene = new THREE.Scene();
    this.beamScene.background = new THREE.Color(0);
    this.beamMesh = new THREE.Mesh(this.beamGeometry, this.beamMaterial);
    this.beamMesh.frustumCulled = false;
    this.beamScene.add(this.beamMesh);

    this.reconstructMaterial = new THREE.MeshBasicNodeMaterial({
      depthTest: false,
      depthWrite: false,
      toneMapped: false,
    });
    this.reconstructMaterial.fragmentNode = reconstructCaustics({
      pixel: screenCoordinate,
      raw: texture(this.rawTarget.texture),
      receivers: texture(this.receiverTarget.texture),
    });
    this.reconstructQuad = new THREE.QuadMesh(this.reconstructMaterial);

    const shared = {
      vertices: this.verticesNode,
      tree: this.topologyNode,
      bounds: this.boundsNode,
    };
    this.refits = this.hierarchy.refitLevels.map((level) =>
      causticRefitKernel({
        id: instanceIndex,
        start: uint(level.start),
        ...shared,
      }).compute(level.count).setName("Caustics: refit BVH")
    );
    const args = {
      ...shared,
      rays: this.raysNode,
      flags: this.flagsNode,
      geometry: this.receiverGeometryNode,
      instances: this.receiverInstancesNode,
      nodeCount: uint(this.hierarchy.nodeCount),
      receiverCount: uint(1),
      source: this.sourceNode,
      right: this.rightNode,
      up: this.upNode,
      incoming: this.incomingNode,
      sigma: this.absorptionNode,
      reach: this.reachNode,
    };
    this.traces = [0, 1, 2].map((phase) =>
      causticTraceKernel({
        id: instanceIndex,
        phase: uint(phase),
        ...args,
      }).compute(CAUSTIC_RAY_COUNT).setName("Caustics: trace " + phase)
    );
    this.refine = causticRefineKernel({
      id: instanceIndex,
      rays: this.raysNode,
      flags: this.flagsNode,
      pixel: this.pixelNode,
    }).compute(CAUSTIC_CELL_COUNT).setName("Caustics: classify optical curvature");

    this.camera = null;
    this.atlasCamera = new THREE.PerspectiveCamera();
    this.crop = new THREE.Matrix4();
    this.viewProjection = new THREE.Matrix4();
    this.localMatrix = new THREE.Matrix4();
    this.translation = new THREE.Matrix4();
    this.axis = new THREE.Vector3();
    this.corner = new THREE.Vector3();
    this.clipCorner = new THREE.Vector4();
    this.receiverBounds = new THREE.Box3();
    this.receiverWorldBox = new THREE.Box3();
    this.receiverInverse = new THREE.Matrix4();
  }

  setCamera(camera) {
    this.camera = camera;
  }

  sampleIrradiance() {
    return sampleCausticIrradiance({
      world: positionWorld,
      center: this.centerNode,
      matrix: this.lookupMatrixNode,
      light: texture(this.outputTarget.texture),
      receivers: texture(this.receiverTarget.texture),
      pixelWorld: this.pixelNode,
    });
  }

  update(renderer, body, sigma, force = false) {
    const center = body.center;
    const positions = this.surface.positions;
    const normals = this.surface.geometry.attributes.normal.array;
    const packed = this.verticesNode.value.array;
    const box = this.surface.geometry.boundingBox;
    const size = box.getSize(
      this.sizeScratch ?? (this.sizeScratch = new THREE.Vector3()),
    );
    const span = Math.max(
      0.22,
      size.x * 2 + 0.04,
      size.z * 2 + 0.04,
      Math.max(0, box.max.y) *
        Math.max(
          Math.abs(lightDirection.x / lightDirection.y),
          Math.abs(lightDirection.z / lightDirection.y),
        ) * 2 + 0.12,
    );
    const reach = Math.max(0.15, span);
    const version = this.surface.geometry.attributes.position.version;
    const sigmaChanged =
      !this.lastSigma ||
      this.lastSigma[0] !== sigma[0] ||
      this.lastSigma[1] !== sigma[1] ||
      this.lastSigma[2] !== sigma[2];
    const transportChanged =
      force ||
      version !== this.lastVersion ||
      !this.lastCenter ||
      !this.lastCenter.equals(center) ||
      sigmaChanged;
    this.centerNode.value.copy(center);
    this.absorptionNode.value.set(...sigma);
    this.reachNode.value = reach;
    this.pixelNode.value = span / GPU_CAUSTIC_SIZE;
    this.receiverMesh.updateWorldMatrix(true, false);
    const receiverBox = this.receiverWorldBox
      .copy(this.receiverGeometry.boundingBox)
      .applyMatrix4(this.receiverMesh.matrixWorld);
    const cropMinX = center.x - reach;
    const cropMaxX = center.x + reach;
    const cropMinY = Math.min(0, center.y - reach);
    const cropMaxY = center.y + reach;
    const cropMinZ = center.z - reach;
    const cropMaxZ = center.z + reach;
    this.receiverBounds.min.set(
      Math.max(receiverBox.min.x, cropMinX),
      Math.max(receiverBox.min.y, cropMinY),
      Math.max(receiverBox.min.z, cropMinZ),
    );
    this.receiverBounds.max.set(
      Math.min(receiverBox.max.x, cropMaxX),
      Math.min(receiverBox.max.y, cropMaxY),
      Math.min(receiverBox.max.z, cropMaxZ),
    );
    if (this.receiverBounds.isEmpty()) {
      this.receiverBounds.set(
        new THREE.Vector3(center.x - reach, -0.00005, center.z - reach),
        new THREE.Vector3(center.x + reach, -0.00005, center.z + reach),
      );
    }
    if (transportChanged) {
      const inverse = this.receiverInverse
        .copy(this.receiverMesh.matrixWorld)
        .invert();
      const elements = inverse.elements;
      const record = this.receiverInstancesNode.value.array;
      const tx =
        elements[0] * center.x +
        elements[4] * center.y +
        elements[8] * center.z +
        elements[12];
      const ty =
        elements[1] * center.x +
        elements[5] * center.y +
        elements[9] * center.z +
        elements[13];
      const tz =
        elements[2] * center.x +
        elements[6] * center.y +
        elements[10] * center.z +
        elements[14];
      record.fill(0);
      record.set([
        receiverBox.min.x - center.x,
        receiverBox.min.y - center.y,
        receiverBox.min.z - center.z,
        0,
        receiverBox.max.x - center.x,
        receiverBox.max.y - center.y,
        receiverBox.max.z - center.z,
        0,
      ], 0);
      record.set([
        elements[0],
        elements[4],
        elements[8],
        tx,
        elements[1],
        elements[5],
        elements[9],
        ty,
        elements[2],
        elements[6],
        elements[10],
        tz,
      ], 8);
      record[20] = 0;
      record[21] = this.receiverPacked.nodeEnd;
      record[22] = 1;
      this.receiverInstancesNode.value.needsUpdate = true;
      for (let index = 0; index < positions.length / 3; index += 1) {
        const source = index * 3;
        const target = index * 8;
        packed[target] = positions[source] - center.x;
        packed[target + 1] = positions[source + 1] - center.y;
        packed[target + 2] = positions[source + 2] - center.z;
        packed[target + 3] = 1;
        packed[target + 4] = normals[source];
        packed[target + 5] = normals[source + 1];
        packed[target + 6] = normals[source + 2];
        packed[target + 7] = 0;
      }
      this.verticesNode.value.needsUpdate = true;
      const direction = lightDirection;
      this.axis.set(
        0,
        Math.abs(direction.z) > 0.96 ? 1 : 0,
        Math.abs(direction.z) > 0.96 ? 0 : 1,
      );
      this.rightNode.value
        .crossVectors(direction, this.axis)
        .normalize();
      this.upNode.value
        .crossVectors(this.rightNode.value, direction)
        .normalize();
      const right = this.rightNode.value;
      const up = this.upNode.value;
      let width = 0;
      let height = 0;
      for (let index = 0; index < 8; index += 1) {
        const corner = this.corner.set(
          index & 1 ? box.max.x : box.min.x,
          index & 2 ? box.max.y : box.min.y,
          index & 4 ? box.max.z : box.min.z,
        ).sub(center);
        width = Math.max(width, Math.abs(corner.dot(right)));
        height = Math.max(height, Math.abs(corner.dot(up)));
      }
      const margin = 0.001;
      this.sourceNode.value.set(
        (width + margin) * 2,
        (height + margin) * 2,
        0,
        0,
      );
      this.sourceAreaNode.value =
        this.sourceNode.value.x * this.sourceNode.value.y /
        (2 * CAUSTIC_FINE_GRID * CAUSTIC_FINE_GRID *
          Math.abs(direction.y));
      renderer.compute(this.refits);
      renderer.compute([
        this.traces[0],
        this.traces[1],
        this.refine,
        this.traces[2],
      ]);
    }
    if (this.camera) {
      this.camera.updateMatrixWorld();
      this.viewProjection.multiplyMatrices(
        this.camera.projectionMatrix,
        this.camera.matrixWorldInverse,
      );
      if (
        transportChanged ||
        !this.lastCamera ||
        !this.lastCamera.equals(this.viewProjection)
      ) {
        this.renderAtlas(renderer, center, this.viewProjection);
        if (!this.lastCamera) this.lastCamera = new THREE.Matrix4();
        this.lastCamera.copy(this.viewProjection);
      }
    }
    this.lastVersion = version;
    if (!this.lastCenter) this.lastCenter = new THREE.Vector3();
    this.lastCenter.copy(center);
    this.lastSigma = [sigma[0], sigma[1], sigma[2]];
  }

  renderAtlas(renderer, center, viewProjection = this.viewProjection) {
    const camera = this.camera;
    const bounds = this.receiverBounds;
    let minX = 1;
    let minY = 1;
    let maxX = -1;
    let maxY = -1;
    for (let index = 0; index < 8; index += 1) {
      this.clipCorner.set(
        index & 1 ? bounds.max.x : bounds.min.x,
        index & 2 ? bounds.max.y : bounds.min.y,
        index & 4 ? bounds.max.z : bounds.min.z,
        1,
      ).applyMatrix4(viewProjection);
      const point = this.clipCorner;
      if (point.w <= 0) {
        minX = -1;
        minY = -1;
        maxX = 1;
        maxY = 1;
        break;
      }
      minX = Math.min(minX, point.x / point.w);
      maxX = Math.max(maxX, point.x / point.w);
      minY = Math.min(minY, point.y / point.w);
      maxY = Math.max(maxY, point.y / point.w);
    }
    minX = Math.max(-1, minX);
    maxX = Math.min(1, maxX);
    minY = Math.max(-1, minY);
    maxY = Math.min(1, maxY);
    let width = Math.max(0.001, maxX - minX);
    let height = Math.max(0.001, maxY - minY);
    const guard = 2 / (GPU_CAUSTIC_SIZE - 4);
    const padX = width * guard;
    const padY = height * guard;
    minX = Math.max(-1, minX - padX);
    maxX = Math.min(1, maxX + padX);
    minY = Math.max(-1, minY - padY);
    maxY = Math.min(1, maxY + padY);
    width = Math.max(0.001, maxX - minX);
    height = Math.max(0.001, maxY - minY);
    this.crop.set(
      2 / width,
      0,
      0,
      -(maxX + minX) / width,
      0,
      2 / height,
      0,
      -(maxY + minY) / height,
      0,
      0,
      1,
      0,
      0,
      0,
      0,
      1,
    );
    this.atlasCamera.copy(camera);
    this.atlasCamera.projectionMatrix.premultiply(this.crop);
    this.atlasCamera.projectionMatrixInverse
      .copy(this.atlasCamera.projectionMatrix)
      .invert();
    this.localMatrix
      .multiplyMatrices(this.crop, viewProjection)
      .multiply(this.translation.makeTranslation(
        center.x,
        center.y,
        center.z,
      ));
    this.beamMatrixNode.value.copy(this.localMatrix);
    this.lookupMatrixNode.value.copy(this.localMatrix);
    const previous = renderer.getRenderTarget();
    try {
      renderer.setRenderTarget(this.receiverTarget);
      renderer.render(this.receiverScene, this.atlasCamera);
      renderer.setRenderTarget(this.rawTarget);
      renderer.render(this.beamScene, this.atlasCamera);
      renderer.setRenderTarget(this.outputTarget);
      this.reconstructQuad.render(renderer);
    } finally {
      renderer.setRenderTarget(previous);
    }
  }

  dispose() {
    for (const kernel of [
      ...this.refits,
      ...this.traces,
      this.refine,
    ]) {
      kernel.dispose?.();
    }
    this.receiverGeometry.dispose();
    this.receiverMaterial.dispose();
    this.beamGeometry.dispose();
    this.beamMaterial.dispose();
    this.reconstructMaterial.dispose();
    this.receiverTarget.dispose();
    this.rawTarget.dispose();
    this.outputTarget.dispose();
  }
}
