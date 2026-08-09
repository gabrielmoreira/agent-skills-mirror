# 6.26. Occupancy

**Source:** group__CUDA__OCCUPANCY.html#group__CUDA__OCCUPANCY



 v13.3.1


  * 1\. Difference between the driver and runtime APIs

  * 2\. API synchronization behavior

  * 3\. Stream synchronization behavior

  * 4\. Graph object thread safety

  * 5\. Rules for version mixing

  * 6\. Modules

    * 6.1. Data types used by CUDA driver

    * 6.2. Error Handling

    * 6.3. Initialization

    * 6.4. Version Management

    * 6.5. Device Management

    * [6.6. Device Management [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__DEVICE__DEPRECATED.html#group__CUDA__DEVICE__DEPRECATED)

    * 6.7. Primary Context Management

    * 6.8. Context Management

    * [6.9. Context Management [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__CTX__DEPRECATED.html#group__CUDA__CTX__DEPRECATED)

    * 6.10. Module Management

    * [6.11. Module Management [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__MODULE__DEPRECATED.html#group__CUDA__MODULE__DEPRECATED)

    * 6.12. Library Management

    * 6.13. Memory Management

    * 6.14. Virtual Memory Management

    * 6.15. Stream Ordered Memory Allocator

    * 6.16. Multicast Object Management

    * 6.17. Logical Endpoint

    * 6.18. Unified Addressing

    * 6.19. Stream Management

    * 6.20. Event Management

    * 6.21. External Resource Interoperability

    * 6.22. Stream Memory Operations

    * 6.23. Execution Control

    * [6.24. Execution Control [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__EXEC__DEPRECATED.html#group__CUDA__EXEC__DEPRECATED)

    * 6.25. Graph Management

    * 6.26. Occupancy

    * [6.27. Texture Reference Management [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__TEXREF__DEPRECATED.html#group__CUDA__TEXREF__DEPRECATED)

    * [6.28. Surface Reference Management [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__SURFREF__DEPRECATED.html#group__CUDA__SURFREF__DEPRECATED)

    * 6.29. Texture Object Management

    * 6.30. Surface Object Management

    * 6.31. Tensor Map Object Managment

    * 6.32. Peer Context Memory Access

    * 6.33. Graphics Interoperability

    * 6.34. Driver Entry Point Access

    * 6.35. Coredump Attributes Control API

    * 6.36. Green Contexts

    * 6.37. Error Log Management Functions

    * 6.38. CUDA Checkpointing

    * [6.39. Profiler Control [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__PROFILER__DEPRECATED.html#group__CUDA__PROFILER__DEPRECATED)

    * 6.40. Profiler Control

    * 6.41. OpenGL Interoperability

      * [6.41.1. OpenGL Interoperability [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__GL__DEPRECATED.html#group__CUDA__GL__DEPRECATED)

    * 6.42. Direct3D 9 Interoperability

      * [6.42.1. Direct3D 9 Interoperability [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__D3D9__DEPRECATED.html#group__CUDA__D3D9__DEPRECATED)

    * 6.43. Direct3D 10 Interoperability

      * [6.43.1. Direct3D 10 Interoperability [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__D3D10__DEPRECATED.html#group__CUDA__D3D10__DEPRECATED)

    * 6.44. Direct3D 11 Interoperability

      * [6.44.1. Direct3D 11 Interoperability [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__D3D11__DEPRECATED.html#group__CUDA__D3D11__DEPRECATED)

    * 6.45. VDPAU Interoperability

    * 6.46. EGL Interoperability

  * 7\. Data Structures

    * 7.1. CU_DEV_SM_RESOURCE_GROUP_PARAMS

    * 7.2. CUaccessPolicyWindow_v1

    * 7.3. CUarrayMapInfo_v1

    * 7.4. CUasyncNotificationInfo

    * 7.5. CUcheckpointCheckpointArgs

    * 7.6. CUcheckpointGpuPair

    * 7.7. CUcheckpointLockArgs

    * 7.8. CUcheckpointRestoreArgs

    * 7.9. CUcheckpointUnlockArgs

    * 7.10. CUctxCigParam

    * 7.11. CUctxCreateParams

    * 7.12. CUDA_ARRAY3D_DESCRIPTOR_v2

    * 7.13. CUDA_ARRAY_DESCRIPTOR_v2

    * 7.14. CUDA_ARRAY_MEMORY_REQUIREMENTS_v1

    * 7.15. CUDA_ARRAY_SPARSE_PROPERTIES_v1

    * 7.16. CUDA_BATCH_MEM_OP_NODE_PARAMS_v1

    * 7.17. CUDA_BATCH_MEM_OP_NODE_PARAMS_v2

    * 7.18. CUDA_CHILD_GRAPH_NODE_PARAMS

    * 7.19. CUDA_CONDITIONAL_NODE_PARAMS

    * 7.20. CUDA_EVENT_RECORD_NODE_PARAMS

    * 7.21. CUDA_EVENT_WAIT_NODE_PARAMS

    * 7.22. CUDA_EXT_SEM_SIGNAL_NODE_PARAMS_v1

    * 7.23. CUDA_EXT_SEM_SIGNAL_NODE_PARAMS_v2

    * 7.24. CUDA_EXT_SEM_WAIT_NODE_PARAMS_v1

    * 7.25. CUDA_EXT_SEM_WAIT_NODE_PARAMS_v2

    * 7.26. CUDA_EXTERNAL_MEMORY_BUFFER_DESC_v1

    * 7.27. CUDA_EXTERNAL_MEMORY_HANDLE_DESC_v1

    * 7.28. CUDA_EXTERNAL_MEMORY_MIPMAPPED_ARRAY_DESC_v1

    * 7.29. CUDA_EXTERNAL_SEMAPHORE_HANDLE_DESC_v1

    * 7.30. CUDA_EXTERNAL_SEMAPHORE_SIGNAL_PARAMS_v1

    * 7.31. CUDA_EXTERNAL_SEMAPHORE_WAIT_PARAMS_v1

    * 7.32. CUDA_GRAPH_INSTANTIATE_PARAMS

    * 7.33. CUDA_HOST_NODE_PARAMS_v1

    * 7.34. CUDA_HOST_NODE_PARAMS_v2

    * 7.35. CUDA_KERNEL_NODE_PARAMS_v1

    * 7.36. CUDA_KERNEL_NODE_PARAMS_v2

    * 7.37. CUDA_KERNEL_NODE_PARAMS_v3

    * 7.38. CUDA_LAUNCH_PARAMS_v1

    * 7.39. CUDA_MEM_ALLOC_NODE_PARAMS_v1

    * 7.40. CUDA_MEM_ALLOC_NODE_PARAMS_v2

    * 7.41. CUDA_MEM_FREE_NODE_PARAMS

    * 7.42. CUDA_MEMCPY2D_v2

    * 7.43. CUDA_MEMCPY3D_PEER_v1

    * 7.44. CUDA_MEMCPY3D_v2

    * 7.45. CUDA_MEMCPY_NODE_PARAMS

    * 7.46. CUDA_MEMSET_NODE_PARAMS_v1

    * 7.47. CUDA_MEMSET_NODE_PARAMS_v2

    * 7.48. CUDA_POINTER_ATTRIBUTE_P2P_TOKENS_v1

    * 7.49. CUDA_RESOURCE_DESC_v1

    * 7.50. CUDA_RESOURCE_VIEW_DESC_v1

    * 7.51. CUDA_TEXTURE_DESC_v1

    * 7.52. CUdevprop_v1

    * 7.53. CUdevResource

    * 7.54. CUdevSmResource

    * 7.55. CUdevWorkqueueConfigResource

    * 7.56. CUdevWorkqueueResource

    * 7.57. CUeglFrame_v1

    * 7.58. CUexecAffinityParam_v1

    * 7.59. CUexecAffinitySmCount_v1

    * 7.60. CUextent3D_v1

    * 7.61. CUgraphEdgeData

    * 7.62. CUgraphExecUpdateResultInfo_v1

    * 7.63. CUgraphNodeParams

    * 7.64. CUipcEventHandle_v1

    * 7.65. CUipcMemHandle_v1

    * 7.66. CUlaunchAttribute

    * 7.67. CUlaunchAttributeValue

    * 7.68. CUlaunchConfig

    * 7.69. CUlaunchMemSyncDomainMap

    * 7.70. CUlogicalEndpointFabricHandle

    * 7.71. CUlogicalEndpointProp

    * 7.72. CUmemAccessDesc_v1

    * 7.73. CUmemAllocationProp_v1

    * 7.74. CUmemcpy3DOperand_v1

    * 7.75. CUmemcpyAttributes_v1

    * 7.76. CUmemDecompressParams

    * 7.77. CUmemFabricHandle_v1

    * 7.78. CUmemLocation_v1

    * 7.79. CUmemPoolProps_v1

    * 7.80. CUmemPoolPtrExportData_v1

    * 7.81. CUmulticastObjectProp_v1

    * 7.82. CUoffset3D_v1

    * 7.83. CUstreamBatchMemOpParams_v1

    * 7.84. CUstreamCigCaptureParams

    * 7.85. CUstreamCigParam

    * 7.86. CUtensorMap

  * 8\. Data Fields

  * 9\. Deprecated List


## Search Results


< Previous | Next >

CUDA Driver API (PDF) \- v13.3.1 (older) \- Last updated June 29, 2026 \- [Send Feedback](mailto:CUDAIssues@nvidia.com?subject=CUDA%20Toolkit%20Documentation%20Feedback:%20CUDA%20Driver%20API)

## 6.26. Occupancy

This section describes the occupancy calculation functions of the low-level CUDA driver application programming interface.

### Functions

CUresult cuOccupancyAvailableDynamicSMemPerBlock ( size_t* dynamicSmemSize, CUfunction func, int  numBlocks, int  blockSize )


Returns dynamic shared memory available per block when launching `numBlocks` blocks on SM.

######  Parameters

`dynamicSmemSize`
    \- Returned maximum dynamic shared memory
`func`
    \- Kernel function for which occupancy is calculated
`numBlocks`
    \- Number of blocks to fit on SM
`blockSize`
    \- Size of the blocks

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_UNKNOWN

###### Description

Returns in `*dynamicSmemSize` the maximum size of dynamic shared memory to allow `numBlocks` blocks per SM.

Note that the API can also be used with context-less kernel CUkernel by querying the handle using cuLibraryGetKernel() and then passing it to the API by casting to CUfunction. Here, the context to use for calculations will be the current context.



CUresult cuOccupancyMaxActiveBlocksPerMultiprocessor ( int* numBlocks, CUfunction func, int  blockSize, size_t dynamicSMemSize )


Returns occupancy of a function.

######  Parameters

`numBlocks`
    \- Returned occupancy
`func`
    \- Kernel for which occupancy is calculated
`blockSize`
    \- Block size the kernel is intended to be launched with
`dynamicSMemSize`
    \- Per-block dynamic shared memory usage intended, in bytes

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_UNKNOWN

###### Description

Returns in `*numBlocks` the number of the maximum active blocks per streaming multiprocessor.

Note that the API can also be used with context-less kernel CUkernel by querying the handle using cuLibraryGetKernel() and then passing it to the API by casting to CUfunction. Here, the context to use for calculations will be the current context.

CUresult cuOccupancyMaxActiveBlocksPerMultiprocessorWithFlags ( int* numBlocks, CUfunction func, int  blockSize, size_t dynamicSMemSize, unsigned int  flags )


Returns occupancy of a function.

######  Parameters

`numBlocks`
    \- Returned occupancy
`func`
    \- Kernel for which occupancy is calculated
`blockSize`
    \- Block size the kernel is intended to be launched with
`dynamicSMemSize`
    \- Per-block dynamic shared memory usage intended, in bytes
`flags`
    \- Requested behavior for the occupancy calculator

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_UNKNOWN

###### Description

Returns in `*numBlocks` the number of the maximum active blocks per streaming multiprocessor.

The `Flags` parameter controls how special cases are handled. The valid flags are:

  * CU_OCCUPANCY_DEFAULT, which maintains the default behavior as cuOccupancyMaxActiveBlocksPerMultiprocessor;


  * CU_OCCUPANCY_DISABLE_CACHING_OVERRIDE, which suppresses the default behavior on platform where global caching affects occupancy. On such platforms, if caching is enabled, but per-block SM resource usage would result in zero occupancy, the occupancy calculator will calculate the occupancy as if caching is disabled. Setting CU_OCCUPANCY_DISABLE_CACHING_OVERRIDE makes the occupancy calculator to return 0 in such cases. More information can be found about this feature in the "Unified L1/Texture Cache" section of the Maxwell tuning guide.


Note that the API can also be with launch context-less kernel CUkernel by querying the handle using cuLibraryGetKernel() and then passing it to the API by casting to CUfunction. Here, the context to use for calculations will be the current context.

CUresult cuOccupancyMaxActiveClusters ( int* numClusters, CUfunction func, const CUlaunchConfig* config )


Given the kernel function (`func`) and launch configuration (`config`), return the maximum number of clusters that could co-exist on the target device in `*numClusters`.

######  Parameters

`numClusters`
    \- Returned maximum number of clusters that could co-exist on the target device
`func`
    \- Kernel function for which maximum number of clusters are calculated
`config`
    \- Launch configuration for the given kernel function

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_INVALID_CLUSTER_SIZE, CUDA_ERROR_UNKNOWN

###### Description

If the function has required cluster size already set (see cudaFuncGetAttributes / cuFuncGetAttribute), the cluster size from config must either be unspecified or match the required size. Without required sizes, the cluster size must be specified in config, else the function will return an error.

Note that various attributes of the kernel function may affect occupancy calculation. Runtime environment may affect how the hardware schedules the clusters, so the calculated occupancy is not guaranteed to be achievable.

Note that the API can also be used with context-less kernel CUkernel by querying the handle using cuLibraryGetKernel() and then passing it to the API by casting to CUfunction. Here, the context to use for calculations will either be taken from the specified stream `config->hStream` or the current context in case of NULL stream.

CUresult cuOccupancyMaxPotentialBlockSize ( int* minGridSize, int* blockSize, CUfunction func, CUoccupancyB2DSize blockSizeToDynamicSMemSize, size_t dynamicSMemSize, int  blockSizeLimit )


Suggest a launch configuration with reasonable occupancy.

######  Parameters

`minGridSize`
    \- Returned minimum grid size needed to achieve the maximum occupancy
`blockSize`
    \- Returned maximum block size that can achieve the maximum occupancy
`func`
    \- Kernel for which launch configuration is calculated
`blockSizeToDynamicSMemSize`
    \- A function that calculates how much per-block dynamic shared memory `func` uses based on the block size
`dynamicSMemSize`
    \- Dynamic shared memory usage intended, in bytes
`blockSizeLimit`
    \- The maximum block size `func` is designed to handle

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_UNKNOWN

###### Description

Returns in `*blockSize` a reasonable block size that can achieve the maximum occupancy (or, the maximum number of active warps with the fewest blocks per multiprocessor), and in `*minGridSize` the minimum grid size to achieve the maximum occupancy.

If `blockSizeLimit` is 0, the configurator will use the maximum block size permitted by the device / function instead.

If per-block dynamic shared memory allocation is not needed, the user should leave both `blockSizeToDynamicSMemSize` and `dynamicSMemSize` as 0.

If per-block dynamic shared memory allocation is needed, then if the dynamic shared memory size is constant regardless of block size, the size should be passed through `dynamicSMemSize`, and `blockSizeToDynamicSMemSize` should be NULL.

Otherwise, if the per-block dynamic shared memory size varies with different block sizes, the user needs to provide a unary function through `blockSizeToDynamicSMemSize` that computes the dynamic shared memory needed by `func` for any given block size. `dynamicSMemSize` is ignored. An example signature is:


    ‎    // Take block size, returns dynamic shared memory needed
              size_t blockToSmem(int blockSize);

Note that the API can also be used with context-less kernel CUkernel by querying the handle using cuLibraryGetKernel() and then passing it to the API by casting to CUfunction. Here, the context to use for calculations will be the current context.

CUresult cuOccupancyMaxPotentialBlockSizeWithFlags ( int* minGridSize, int* blockSize, CUfunction func, CUoccupancyB2DSize blockSizeToDynamicSMemSize, size_t dynamicSMemSize, int  blockSizeLimit, unsigned int  flags )


Suggest a launch configuration with reasonable occupancy.

######  Parameters

`minGridSize`
    \- Returned minimum grid size needed to achieve the maximum occupancy
`blockSize`
    \- Returned maximum block size that can achieve the maximum occupancy
`func`
    \- Kernel for which launch configuration is calculated
`blockSizeToDynamicSMemSize`
    \- A function that calculates how much per-block dynamic shared memory `func` uses based on the block size
`dynamicSMemSize`
    \- Dynamic shared memory usage intended, in bytes
`blockSizeLimit`
    \- The maximum block size `func` is designed to handle
`flags`
    \- Options

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_UNKNOWN

###### Description

An extended version of cuOccupancyMaxPotentialBlockSize. In addition to arguments passed to cuOccupancyMaxPotentialBlockSize, cuOccupancyMaxPotentialBlockSizeWithFlags also takes a `Flags` parameter.

The `Flags` parameter controls how special cases are handled. The valid flags are:

  * CU_OCCUPANCY_DEFAULT, which maintains the default behavior as cuOccupancyMaxPotentialBlockSize;


  * CU_OCCUPANCY_DISABLE_CACHING_OVERRIDE, which suppresses the default behavior on platform where global caching affects occupancy. On such platforms, the launch configurations that produces maximal occupancy might not support global caching. Setting CU_OCCUPANCY_DISABLE_CACHING_OVERRIDE guarantees that the the produced launch configuration is global caching compatible at a potential cost of occupancy. More information can be found about this feature in the "Unified L1/Texture Cache" section of the Maxwell tuning guide.


Note that the API can also be used with context-less kernel CUkernel by querying the handle using cuLibraryGetKernel() and then passing it to the API by casting to CUfunction. Here, the context to use for calculations will be the current context.

CUresult cuOccupancyMaxPotentialClusterSize ( int* clusterSize, CUfunction func, const CUlaunchConfig* config )


Given the kernel function (`func`) and launch configuration (`config`), return the maximum cluster size in `*clusterSize`.

######  Parameters

`clusterSize`
    \- Returned maximum cluster size that can be launched for the given kernel function and launch configuration
`func`
    \- Kernel function for which maximum cluster size is calculated
`config`
    \- Launch configuration for the given kernel function

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_UNKNOWN

###### Description

The cluster dimensions in `config` are ignored. If func has a required cluster size set (see cudaFuncGetAttributes / cuFuncGetAttribute),`*clusterSize` will reflect the required cluster size.

By default this function will always return a value that's portable on future hardware. A higher value may be returned if the kernel function allows non-portable cluster sizes.

This function will respect the compile time launch bounds.

Note that the API can also be used with context-less kernel CUkernel by querying the handle using cuLibraryGetKernel() and then passing it to the API by casting to CUfunction. Here, the context to use for calculations will either be taken from the specified stream `config->hStream` or the current context in case of NULL stream.


