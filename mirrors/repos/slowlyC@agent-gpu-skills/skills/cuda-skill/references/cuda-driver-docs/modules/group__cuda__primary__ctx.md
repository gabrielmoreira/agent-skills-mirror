# 6.7. Primary Context Management

**Source:** group__CUDA__PRIMARY__CTX.html#group__CUDA__PRIMARY__CTX



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

## 6.7. Primary Context Management

This section describes the primary context management functions of the low-level CUDA driver application programming interface.

The primary context is unique per device and shared with the CUDA runtime API. These functions allow integration with other libraries using CUDA.

### Functions

CUresult cuDevicePrimaryCtxGetState ( CUdevice dev, unsigned int* flags, int* active )


Get the state of the primary context.

######  Parameters

`dev`
    \- Device to get primary context flags for
`flags`
    \- Pointer to store flags
`active`
    \- Pointer to store context state; 0 = inactive, 1 = active

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_DEVICE, CUDA_ERROR_INVALID_VALUE

###### Description

Returns in `*flags` the flags for the primary context of `dev`, and in `*active` whether it is active. See cuDevicePrimaryCtxSetFlags for flag values.

CUresult cuDevicePrimaryCtxRelease ( CUdevice dev )


Release the primary context on the GPU.

######  Parameters

`dev`
    \- Device which primary context is released

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_DEVICE, CUDA_ERROR_INVALID_CONTEXT

###### Description

Releases the primary context interop on the device. A retained context should always be released once the user is done using it. The context is automatically reset once the last reference to it is released. This behavior is different when the primary context was retained by the CUDA runtime from CUDA 4.0 and earlier. In this case, the primary context remains always active.

Releasing a primary context that has not been previously retained will fail with CUDA_ERROR_INVALID_CONTEXT.

Please note that unlike cuCtxDestroy() this method does not pop the context from stack in any circumstances.

CUresult cuDevicePrimaryCtxReset ( CUdevice dev )


Destroy all allocations and reset all state on the primary context.

######  Parameters

`dev`
    \- Device for which primary context is destroyed

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_DEVICE, CUDA_ERROR_PRIMARY_CONTEXT_ACTIVE

###### Description

Explicitly destroys and cleans up all resources associated with the current device in the current process.

Note that it is responsibility of the calling function to ensure that no other module in the process is using the device any more. For that reason it is recommended to use cuDevicePrimaryCtxRelease() in most cases. However it is safe for other modules to call cuDevicePrimaryCtxRelease() even after resetting the device. Resetting the primary context does not release it, an application that has retained the primary context should explicitly release its usage.

CUresult cuDevicePrimaryCtxRetain ( CUcontext* pctx, CUdevice dev )


Retain the primary context on the GPU.

######  Parameters

`pctx`
    \- Returned context handle of the new context
`dev`
    \- Device for which primary context is requested

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_DEVICE, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_UNKNOWN

###### Description

Retains the primary context on the device. Once the user successfully retains the primary context, the primary context will be active and available to the user until the user releases it with cuDevicePrimaryCtxRelease() or resets it with cuDevicePrimaryCtxReset(). Unlike cuCtxCreate() the newly retained context is not pushed onto the stack.

Retaining the primary context for the first time will fail with CUDA_ERROR_UNKNOWN if the compute mode of the device is CU_COMPUTEMODE_PROHIBITED. The function cuDeviceGetAttribute() can be used with CU_DEVICE_ATTRIBUTE_COMPUTE_MODE to determine the compute mode of the device. The nvidia-smi tool can be used to set the compute mode for devices. Documentation for nvidia-smi can be obtained by passing a -h option to it.

Please note that the primary context always supports pinned allocations. Other flags can be specified by cuDevicePrimaryCtxSetFlags().

CUresult cuDevicePrimaryCtxSetFlags ( CUdevice dev, unsigned int  flags )


Set flags for the primary context.

######  Parameters

`dev`
    \- Device for which the primary context flags are set
`flags`
    \- New flags for the device

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_DEVICE, CUDA_ERROR_INVALID_VALUE

###### Description

Sets the flags for the primary context on the device overwriting perviously set ones.

The three LSBs of the `flags` parameter can be used to control how the OS thread, which owns the CUDA context at the time of an API call, interacts with the OS scheduler when waiting for results from the GPU. Only one of the scheduling flags can be set when creating a context.

  * CU_CTX_SCHED_SPIN: Instruct CUDA to actively spin when waiting for results from the GPU. This can decrease latency when waiting for the GPU, but may lower the performance of CPU threads if they are performing work in parallel with the CUDA thread.


  * CU_CTX_SCHED_YIELD: Instruct CUDA to yield its thread when waiting for results from the GPU. This can increase latency when waiting for the GPU, but can increase the performance of CPU threads performing work in parallel with the GPU.


  * CU_CTX_SCHED_BLOCKING_SYNC: Instruct CUDA to block the CPU thread on a synchronization primitive when waiting for the GPU to finish work.


  * CU_CTX_BLOCKING_SYNC: Instruct CUDA to block the CPU thread on a synchronization primitive when waiting for the GPU to finish work.

**Deprecated:** This flag was deprecated as of CUDA 4.0 and was replaced with CU_CTX_SCHED_BLOCKING_SYNC.


  * CU_CTX_SCHED_AUTO: The default value if the `flags` parameter is zero, uses a heuristic based on the number of active CUDA contexts in the process C and the number of logical processors in the system P. If C > P, then CUDA will yield to other OS threads when waiting for the GPU (CU_CTX_SCHED_YIELD), otherwise CUDA will not yield while waiting for results and actively spin on the processor (CU_CTX_SCHED_SPIN). Additionally, on Tegra devices, CU_CTX_SCHED_AUTO uses a heuristic based on the power profile of the platform and may choose CU_CTX_SCHED_BLOCKING_SYNC for low-powered devices.


  * CU_CTX_LMEM_RESIZE_TO_MAX: Instruct CUDA to not reduce local memory after resizing local memory for a kernel. This can prevent thrashing by local memory allocations when launching many kernels with high local memory usage at the cost of potentially increased memory usage.

**Deprecated:** This flag is deprecated and the behavior enabled by this flag is now the default and cannot be disabled.


  * CU_CTX_COREDUMP_ENABLE: If GPU coredumps have not been enabled globally with cuCoredumpSetAttributeGlobal or environment variables, this flag can be set during context creation to instruct CUDA to create a coredump if this context raises an exception during execution. These environment variables are described in the CUDA-GDB user guide under the "GPU core dump support" section. The initial settings will be taken from the global settings at the time of context creation. The other settings that control coredump output can be modified by calling cuCoredumpSetAttribute from the created context after it becomes current.


  * CU_CTX_USER_COREDUMP_ENABLE: If user-triggered GPU coredumps have not been enabled globally with cuCoredumpSetAttributeGlobal or environment variables, this flag can be set during context creation to instruct CUDA to create a coredump if data is written to a certain pipe that is present in the OS space. These environment variables are described in the CUDA-GDB user guide under the "GPU core dump support" section. It is important to note that the pipe name *must* be set with cuCoredumpSetAttributeGlobal before creating the context if this flag is used. Setting this flag implies that CU_CTX_COREDUMP_ENABLE is set. The initial settings will be taken from the global settings at the time of context creation. The other settings that control coredump output can be modified by calling cuCoredumpSetAttribute from the created context after it becomes current.


  * CU_CTX_SYNC_MEMOPS: Ensures that synchronous memory operations initiated on this context will always synchronize. See further documentation in the section titled "API Synchronization behavior" to learn more about cases when synchronous memory operations can exhibit asynchronous behavior.


