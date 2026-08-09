---
url: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html
---

# 13. Release Notes


This section describes the history of change in the PTX ISA and implementation. The first section describes ISA and implementation changes in the current release of PTX ISA version 9.3, and the remaining sections provide a record of changes in previous releases of PTX ISA versions back to PTX ISA version 2.0.


[Table 62](#release-notes-ptx-release-history) shows the PTX release history.


Table 62 PTX Release History PTX ISA Version | CUDA Release | Supported Targets
---|---|---
PTX ISA 1.0 | CUDA 1.0 | `sm_{10,11}`
PTX ISA 1.1 | CUDA 1.1 | `sm_{10,11}`
PTX ISA 1.2 | CUDA 2.0 | `sm_{10,11,12,13}`
PTX ISA 1.3 | CUDA 2.1 | `sm_{10,11,12,13}`
PTX ISA 1.4 | CUDA 2.2 | `sm_{10,11,12,13}`
PTX ISA 1.5 | driver r190 | `sm_{10,11,12,13}`
PTX ISA 2.0 | CUDA 3.0, driver r195 | `sm_{10,11,12,13}`, `sm_20`
PTX ISA 2.1 | CUDA 3.1, driver r256 | `sm_{10,11,12,13}`, `sm_20`
PTX ISA 2.2 | CUDA 3.2, driver r260 | `sm_{10,11,12,13}`, `sm_20`
PTX ISA 2.3 | CUDA 4.0, driver r270 | `sm_{10,11,12,13}`, `sm_20`
PTX ISA 3.0 | CUDA 4.1, driver r285 | `sm_{10,11,12,13}`, `sm_20`
CUDA 4.2, driver r295 | `sm_{10,11,12,13}`, `sm_20`, `sm_30`
PTX ISA 3.1 | CUDA 5.0, driver r302 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,35}`
PTX ISA 3.2 | CUDA 5.5, driver r319 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,35}`
PTX ISA 4.0 | CUDA 6.0, driver r331 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35}`, `sm_50`
PTX ISA 4.1 | CUDA 6.5, driver r340 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52}`
PTX ISA 4.2 | CUDA 7.0, driver r346 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`
PTX ISA 4.3 | CUDA 7.5, driver r352 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`
PTX ISA 5.0 | CUDA 8.0, driver r361 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`
PTX ISA 6.0 | CUDA 9.0, driver r384 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_70`
PTX ISA 6.1 | CUDA 9.1, driver r387 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_70`, `sm_72`
PTX ISA 6.2 | CUDA 9.2, driver r396 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_70`, `sm_72`
PTX ISA 6.3 | CUDA 10.0, driver r400 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_70`, `sm_72`, `sm_75`
PTX ISA 6.4 | CUDA 10.1, driver r418 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_70`, `sm_72`, `sm_75`
PTX ISA 6.5 | CUDA 10.2, driver r440 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_70`, `sm_72`, `sm_75`
PTX ISA 7.0 | CUDA 11.0, driver r445 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_80`
PTX ISA 7.1 | CUDA 11.1, driver r455 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86}`
PTX ISA 7.2 | CUDA 11.2, driver r460 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86}`
PTX ISA 7.3 | CUDA 11.3, driver r465 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86}`
PTX ISA 7.4 | CUDA 11.4, driver r470 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87}`
PTX ISA 7.5 | CUDA 11.5, driver r495 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87}`
PTX ISA 7.6 | CUDA 11.6, driver r510 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87}`
PTX ISA 7.7 | CUDA 11.7, driver r515 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87}`
PTX ISA 7.8 | CUDA 11.8, driver r520 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_90`
PTX ISA 8.0 | CUDA 12.0, driver r525 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_{90,90a}`
PTX ISA 8.1 | CUDA 12.1, driver r530 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_{90,90a}`
PTX ISA 8.2 | CUDA 12.2, driver r535 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_{90,90a}`
PTX ISA 8.3 | CUDA 12.3, driver r545 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_{90,90a}`
PTX ISA 8.4 | CUDA 12.4, driver r550 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_{90,90a}`
PTX ISA 8.5 | CUDA 12.5, driver r555 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_{90,90a}`
CUDA 12.6, driver r560
PTX ISA 8.6 | CUDA 12.7, driver r565 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_{90,90a}`, `sm_{100,100a,101,101a}`
PTX ISA 8.7 | CUDA 12.8, driver r570 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_{90,90a}`, `sm_{100,100,101,101a}`, `sm_{120,120a}`
PTX ISA 8.8 | CUDA 12.9, driver r575 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,89}`, `sm_{90,90a}`, `sm_{100,100f,100a,101,101f,101a,103,103f,103a}`, `sm_{120,120f,120a,121,121f,121a}`
PTX ISA 9.0 | CUDA 13.0, driver r580 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,88,89}`, `sm_{90,90a}`, `sm_{100,100f,100a,103,103f,103a}`, `sm_{110,110f,110a}`, `sm_{120,120f,120a,121,121f,121a}`
PTX ISA 9.1 | CUDA 13.1, driver r590 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,88,89}`, `sm_{90,90a}`, `sm_{100,100f,100a,103,103f,103a}`, `sm_{110,110f,110a}`, `sm_{120,120f,120a,121,121f,121a}`
PTX ISA 9.2 | CUDA 13.2, driver r595 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,88,89}`, `sm_{90,90a}`, `sm_{100,100f,100a,103,103f,103a}`, `sm_{110,110f,110a}`, `sm_{120,120f,120a,121,121f,121a}`
PTX ISA 9.3 | CUDA 13.3, driver r610 | `sm_{10,11,12,13}`, `sm_20`, `sm_{30,32,35,37}`, `sm_{50,52,53}`, `sm_{60,61,62}`, `sm_{70,72,75}`, `sm_{80,86,87,88,89}`, `sm_{90,90a}`, `sm_{100,100f,100a,103,103f,103a}`, `sm_{110,110f,110a}`, `sm_{120,120f,120a,121,121f,121a}`


[Table 63](#release-notes-a-spec-f-spec-ptx-feature-release-history) shows the release history of arch-specific and family-specific PTX instructions. Apart from PTX instructions, other features and constructs that are architecture-specific and family-specific are described in following sections:


  * [Restriction on Tensor Copy instructions](#data-movement-and-conversion-instructions-tensor-copy-restrictions)

  * [TensorCore 5th Generation Matrix Shape Target ISA Notes](#tcgen05-matrix-shape-target-isa-note)


Table 63 Arch-specific/ Family-specific PTX Features Release History Instruction | Variant | PTX ISA Version | Supported Targets
---|---|---|---
`tensormap.replace` | Base variant | 8.3 | `sm_90a`
8.6 | `sm_100a`, `sm_120a`
8.8 | `sm_100f`, `sm_120f`
9.0 | `sm_110f`
`tensormap.replace.swizzle_atomicity` | 8.6 | `sm_100a`, `sm_120a`
8.8 | `sm_100f`, `sm_120f`
9.0 | `sm_110f`
`.elemtype` for `.field3` with values `13`, `14`, `15` for `new_val` | 8.7 | `sm_100a`, `sm_120a`
8.8 | `sm_100f`, `sm_120f`
9.0 | `sm_110f`
`.swizzle_mode` for `.field3` with value `4` for `new_val` | 8.8 | `sm_103a`
`wgmma.mma_async`, `wgmma.mma_async.sp`, `wgmma.fence`, `wgmma.commit_group`, `wgmma.wait_group` | Base variant | 8.0 | `sm_90a`
`setmaxnreg` | Base variant | 8.0 | `sm_90a`
8.6 | `sm_100a`, `sm_120a`
8.8 | `sm_100f`, `sm_120f`
9.0 | `sm_110f`
`multimem.ld_reduce`, `multimem.st`, `multimem.red` | Types `.e5m2`, `.e4m3`, `.e5m2x2`, `.e4m3x2`, `.e4m3x4`, `.e5m2x4` | 8.6 | `sm_100a`, `sm_120a`, `sm_121a`
8.8 | `sm_100f`
9.0 | `sm_110f`
`.acc::f16` qualifier | 8.6 | `sm_100a`, `sm_120a`, `sm_121a`
8.8 | `sm_100f`
9.0 | `sm_110f`
`cvt` |

  * `.f32` to `.e2m1x2`/`.e2m3x2`/ `.e3m2x2`/`.ue8m0x2`
  * `.e2m1x2`/`.e2m3x2`/`.e3m2x2` to `.f16x2`
  * `.ue8m0x2` to `.bf16x2`
  * `.bf16x2` to `.ue8m0x2`

| 8.6 | `sm_100a`, `sm_120a`
8.8 | `sm_100f`, `sm_120f`
9.0 | `sm_110f`
`.rs` rounding mode | 8.7 | `sm_100a`
8.8 | `sm_103a`
`.s2f6x2` type | 9.1 | `sm_100a`, `sm_103a`, `sm_110a`, `sm_120a`, `sm_121a`
`.f16x2` to `.e2m1x2`/ `.e2m3x2`/`.e3m2x2` | 9.1 | `sm_100f`, `sm_110f`, `sm_120f`
`.bf16x2` to `.e2m1x2`/ `.e2m3x2`/`.e3m2x2`/`.e4m3x2`/ `.e5m2x2` | 9.1 | `sm_100f`, `sm_110f`, `sm_120f`
`.e2m1x2`/`.e2m3x2`/ `.e3m2x2`/`.e4m3x2`/`.e5m2x2` to `.bf16x2` | 9.2 | `sm_100f`, `sm_110f`, `sm_120f`
`cp.async.bulk.tensor` | `.tile::gather4` and `.im2col::w` with `.shared::cluster` as destination state space | 8.6 | `sm_100a`
8.8 | `sm_100f`
9.0 | `sm_110f`
`.tile::scatter4` and `.im2col::w::128` | 8.6 | `sm_100a`
8.8 | `sm_100f`
9.0 | `sm_110f`
`.cta_group` | 8.6 | `sm_100a`
8.8 | `sm_100f`
9.0 | `sm_110f`
`cp.async.bulk.prefetch.tensor` | `.tile::gather4`, `.im2col::w`, `.im2col::w::128` | 8.6 | `sm_100a`
8.8 | `sm_100f`
9.0 | `sm_110f`
`redux.sync` | Type `.f32` and `.abs`, `.NaN` qualifiers | 8.6 | `sm_100a`
8.8 | `sm_100f`
`clusterlaunchcontrol.try_cancel` | `.multicast::cluster::all` | 8.6 | `sm_100a`, `sm_120a`
8.8 | `sm_100f`, `sm_120f`
9.0 | `sm_110f`
`ldmatrix` |

  * Shapes `.m16n16`, `.m8n16`
  * Type `.b8`
  * Qualifiers `.src_fmt`, `.dst_fmt`

| 8.6 | `sm_100a`, `sm_120a`
8.8 | `sm_100f`, `sm_120f`
9.0 | `sm_110f`
`stmatrix` |

  * Shapes `.m16n8`
  * Type `.b8`

| 8.6 | `sm_100a`, `sm_120a`
8.8 | `sm_100f`, `sm_120f`
9.0 | `sm_110f`
`tcgen05.alloc`, `tcgen05.dealloc`, `tcgen05.relinquish_alloc_permit` | Base variant | 8.6 | `sm_100a`
8.8 | `sm_100f`
9.0 | `sm_110f`
`tcgen05.ld`, `tcgen05.st`, `tcgen05.wait`, `tcgen05.cp`, `tcgen05.fence`, `tcgen05.commit` | Base variant | 8.6 | `sm_100a`
8.8 | `sm_100f`
9.0 | `sm_110f`
`tcgen05.ld.red` | Base variant | 8.8 | `sm_103f`
9.0 | `sm_110f`
`tcgen05.shift` | Base variant | 8.6 | `sm_100a`
8.8 | `sm_103a`
9.0 | `sm_110a`
`tcgen05.mma` | Base variant | 8.6 | `sm_100a`
8.8 | `sm_100f`
9.0 | `sm_110f`
Kind `.kind::i8` | 8.6 | `sm_100a`
9.0 | `sm_110a`
Argument `scale-input-d` | 8.6 | `sm_100a`
8.8 | `sm_100f`
Qualifiers `.scale_vec::1X`, `.scale_vec::2X`, `.scale_vec::4X` | 8.6 | `sm_100a`
Qualifiers `.block16`, `.block32` | 8.8 | `sm_100f`, `sm_110f`
K shape value `96` | 8.8 | `sm_103a`
`tcgen05.mma.sp` | Base variant | 8.6 | `sm_100a`
8.8 | `sm_100f`
9.0 | `sm_110f`
Kind `.kind::i8` | 8.6 | `sm_100a`
9.0 | `sm_110a`
Kind `.kind::mxf4nvf4` and `.kind::mxf4` | 8.6 | `sm_100a`
8.8 | `sm_103a`
9.0 | `sm_110a`
Argument `scale-input-d` | 8.6 | `sm_100a`
8.8 | `sm_100f`
Qualifiers `.scale_vec::1X`, `.scale_vec::2X`, `.scale_vec::4X` | 8.6 | `sm_100a`
Qualifiers `.block16`, `.block32` | 8.8 | `sm_100f`, `sm_110f`
`tcgen05.mma.ws`, `tcgen05.mma.ws.sp` | Base variant | 8.6 | `sm_100a`
8.8 | `sm_100f`
9.0 | `sm_110f`
Kind `.kind::i8` | 8.6 | `sm_100a`
9.0 | `sm_110a`
`mma` |

  * Types `.e3m2`, `.e2m3`, `.e2m1`
  * Qualifiers `.kind`, `.block_scale`, `.scale_vec_size`

| 8.7 | `sm_120a`
8.8 | `sm_120f`
`mma.sp` |

  * Types `.e3m2`, `.e2m3`, `.e2m1`
  * Qualifiers `.kind`, `.block_scale`, `.scale_vec_size`

| 8.7 | `sm_120a`
8.8 | `sm_120f`
Kind `.kind::mxf4nvf4` and `.kind::mxf4` | 8.7 | `sm_120a`, `sm_121a`
`add`, `sub`, `min`, `max`, `neg` | Types `.u8x4`, `.s8x4` | 9.2 | `sm_120f`
`add` | Types `.u16x2`, `.s16x2`, `.u32` with `.sat` qualifier | 9.2 | `sm_120f`
