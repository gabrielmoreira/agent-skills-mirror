---
url: https://docs.nvidia.com/cuda/parallel-thread-execution/index.html
---

# 10. Special Registers


PTX includes a number of predefined, read-only variables, which are visible as special registers and accessed through `mov` or `cvt` instructions.


The special registers are:


  * `%tid`

  * `%ntid`

  * `%laneid`

  * `%warpid`

  * `%nwarpid`

  * `%ctaid`

  * `%nctaid`

  * `%smid`

  * `%nsmid`

  * `%gridid`

  * `%is_explicit_cluster`

  * `%clusterid`

  * `%nclusterid`

  * `%cluster_ctaid`

  * `%cluster_nctaid`

  * `%cluster_ctarank`

  * `%cluster_nctarank`

  * `%lanemask_eq`, `%lanemask_le`, `%lanemask_lt`, `%lanemask_ge`, `%lanemask_gt`

  * `%clock`, `%clock_hi`, `%clock64`

  * `%pm0, ..., %pm7`

  * `%pm0_64, ..., %pm7_64`

  * `%envreg0, ..., %envreg31`

  * `%globaltimer`, `%globaltimer_lo`, `%globaltimer_hi`

  * `%reserved_smem_offset_begin`, `%reserved_smem_offset_end`, `%reserved_smem_offset_cap`, `%reserved_smem_offset<2>`

  * `%total_smem_size`

  * `%aggr_smem_size`

  * `%dynamic_smem_size`

  * `%current_graph_exec`
