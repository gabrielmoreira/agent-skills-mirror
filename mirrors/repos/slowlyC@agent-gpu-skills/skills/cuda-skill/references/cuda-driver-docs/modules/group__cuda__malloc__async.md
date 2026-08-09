# 6.15. Stream Ordered Memory Allocator

**Source:** group__CUDA__MALLOC__ASYNC.html#group__CUDA__MALLOC__ASYNC



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

## 6.15. Stream Ordered Memory Allocator

This section describes the stream ordered memory allocator exposed by the low-level CUDA driver application programming interface.

**overview**

The asynchronous allocator allows the user to allocate and free in stream order. All asynchronous accesses of the allocation must happen between the stream executions of the allocation and the free. If the memory is accessed outside of the promised stream order, a use before allocation / use after free error will cause undefined behavior.

The allocator is free to reallocate the memory as long as it can guarantee that compliant memory accesses will not overlap temporally. The allocator may refer to internal stream ordering as well as inter-stream dependencies (such as CUDA events and null stream dependencies) when establishing the temporal guarantee. The allocator may also insert inter-stream dependencies to establish the temporal guarantee.

**Supported Platforms**

Whether or not a device supports the integrated stream ordered memory allocator may be queried by calling cuDeviceGetAttribute() with the device attribute CU_DEVICE_ATTRIBUTE_MEMORY_POOLS_SUPPORTED

### Functions

CUresult cuMemAllocAsync ( CUdeviceptr* dptr, size_t bytesize, CUstream hStream )


Allocates memory with stream ordered semantics.

######  Parameters

`dptr`
    \- Returned device pointer
`bytesize`
    \- Number of bytes to allocate
`hStream`
    \- The stream establishing the stream ordering contract and the memory pool to allocate from

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT (default stream specified with no current context), CUDA_ERROR_NOT_SUPPORTED, CUDA_ERROR_OUT_OF_MEMORY

###### Description

Inserts an allocation operation into `hStream`. A pointer to the allocated memory is returned immediately in *dptr. The allocation must not be accessed until the the allocation operation completes. The allocation comes from the memory pool current to the stream's device.

  * The default memory pool of a device contains device memory from that device.

  * Basic stream ordering allows future work submitted into the same stream to use the allocation. Stream query, stream synchronize, and CUDA events can be used to guarantee that the allocation operation completes before work submitted in a separate stream runs.

  * During stream capture, this function results in the creation of an allocation node. In this case, the allocation is owned by the graph instead of the memory pool. The memory pool's properties are used to set the node's creation parameters.


CUresult cuMemAllocFromPoolAsync ( CUdeviceptr* dptr, size_t bytesize, CUmemoryPool pool, CUstream hStream )


Allocates memory from a specified pool with stream ordered semantics.

######  Parameters

`dptr`
    \- Returned device pointer
`bytesize`
    \- Number of bytes to allocate
`pool`
    \- The pool to allocate from
`hStream`
    \- The stream establishing the stream ordering semantic

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT (default stream specified with no current context), CUDA_ERROR_NOT_SUPPORTED, CUDA_ERROR_OUT_OF_MEMORY

###### Description

Inserts an allocation operation into `hStream`. A pointer to the allocated memory is returned immediately in *dptr. The allocation must not be accessed until the the allocation operation completes. The allocation comes from the specified memory pool.

  * The specified memory pool may be from a device different than that of the specified `hStream`.

  * Basic stream ordering allows future work submitted into the same stream to use the allocation. Stream query, stream synchronize, and CUDA events can be used to guarantee that the allocation operation completes before work submitted in a separate stream runs.

  * During stream capture, this function results in the creation of an allocation node. In this case, the allocation is owned by the graph instead of the memory pool. The memory pool's properties are used to set the node's creation parameters.


CUresult cuMemFreeAsync ( CUdeviceptr dptr, CUstream hStream )


Frees memory with stream ordered semantics.

######  Parameters

`dptr`
    \- memory to free
`hStream`
    \- The stream establishing the stream ordering contract.

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT (default stream specified with no current context), CUDA_ERROR_NOT_SUPPORTED

###### Description

Inserts a free operation into `hStream`. The allocation must not be accessed after stream execution reaches the free. After this API returns, accessing the memory from any subsequent work launched on the GPU or querying its pointer attributes results in undefined behavior.

During stream capture, this function results in the creation of a free node and must therefore be passed the address of a graph allocation.

CUresult cuMemGetDefaultMemPool ( CUmemoryPool* pool_out, CUmemLocation* location, CUmemAllocationType type )


Returns the default memory pool for a given location and allocation type.

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZEDCUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_INVALID_DEVICE, CUDA_ERROR_NOT_SUPPORTED

###### Description

The memory location can be of one of CU_MEM_LOCATION_TYPE_DEVICE, CU_MEM_LOCATION_TYPE_HOST, or CU_MEM_LOCATION_TYPE_HOST_NUMA. The allocation type can be one of CU_MEM_ALLOCATION_TYPE_PINNED or CU_MEM_ALLOCATION_TYPE_MANAGED. When the allocation type is CU_MEM_ALLOCATION_TYPE_MANAGED, the location type can also be CU_MEM_LOCATION_TYPE_NONE to indicate no preferred location for the managed memory pool.

CUresult cuMemGetMemPool ( CUmemoryPool* pool, CUmemLocation* location, CUmemAllocationType type )


Gets the current memory pool for a memory location and of a particular allocation type.

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE

###### Description

The memory location can be of one of CU_MEM_LOCATION_TYPE_DEVICE, CU_MEM_LOCATION_TYPE_HOST or CU_MEM_LOCATION_TYPE_HOST_NUMA, or CU_MEM_LOCATION_TYPE_HOST_NUMA. The allocation type can be one of CU_MEM_ALLOCATION_TYPE_PINNED or CU_MEM_ALLOCATION_TYPE_MANAGED. When the allocation type is CU_MEM_ALLOCATION_TYPE_MANAGED, the location type can also be CU_MEM_LOCATION_TYPE_NONE to indicate no preferred location for the managed memory pool. In all other cases, the call returns CUDA_ERROR_INVALID_VALUE

Returns the last pool provided to cuMemSetMemPool or cuDeviceSetMemPool for this location and allocation type or the location's default memory pool if cuMemSetMemPool or cuDeviceSetMemPool for that allocType and location has never been called. By default the current mempool of a location is the default mempool for a device. Otherwise the returned pool must have been set with cuDeviceSetMemPool.

CUresult cuMemPoolCreate ( CUmemoryPool* pool, const CUmemPoolProps* poolProps )


Creates a memory pool.

###### Returns

CUDA_SUCCESS, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_NOT_PERMITTED, CUDA_ERROR_NOT_SUPPORTED

###### Description

Creates a CUDA memory pool and returns the handle in `pool`. The `poolProps` determines the properties of the pool such as the backing device and IPC capabilities.

To create a memory pool for HOST memory not targeting a specific NUMA node, applications must set set CUmemPoolProps::CUmemLocation::type to CU_MEM_LOCATION_TYPE_HOST. CUmemPoolProps::CUmemLocation::id is ignored for such pools. Pools created with the type CU_MEM_LOCATION_TYPE_HOST are not IPC capable and CUmemPoolProps::handleTypes must be 0, any other values will result in CUDA_ERROR_INVALID_VALUE. To create a memory pool targeting a specific host NUMA node, applications must set CUmemPoolProps::CUmemLocation::type to CU_MEM_LOCATION_TYPE_HOST_NUMA and CUmemPoolProps::CUmemLocation::id must specify the NUMA ID of the host memory node. Specifying CU_MEM_LOCATION_TYPE_HOST_NUMA_CURRENT as the CUmemPoolProps::CUmemLocation::type will result in CUDA_ERROR_INVALID_VALUE.

By default, the pool's memory will be accessible from the device it is allocated on. In the case of pools created with CU_MEM_LOCATION_TYPE_HOST_NUMA or CU_MEM_LOCATION_TYPE_HOST, their default accessibility will be from the host CPU. Applications can control the maximum size of the pool by specifying a non-zero value for CUmemPoolProps::maxSize. If set to 0, the maximum size of the pool will default to a system dependent value.

Applications that intend to use CU_MEM_HANDLE_TYPE_FABRIC based memory sharing must ensure: (1) `nvidia-caps-imex-channels` character device is created by the driver and is listed under /proc/devices (2) have at least one IMEX channel file accessible by the user launching the application.

When exporter and importer CUDA processes have been granted access to the same IMEX channel, they can securely share memory.

The IMEX channel security model works on a per user basis. Which means all processes under a user can share memory if the user has access to a valid IMEX channel. When multi-user isolation is desired, a separate IMEX channel is required for each user.

These channel files exist in /dev/nvidia-caps-imex-channels/channel* and can be created using standard OS native calls like mknod on Linux. For example: To create channel0 with the major number from /proc/devices users can execute the following command: `mknod /dev/nvidia-caps-imex-channels/channel0 c <major number>=""> 0`

To create a managed memory pool, applications must set CUmemPoolProps::CUmemAllocationType to CU_MEM_ALLOCATION_TYPE_MANAGED. CUmemPoolProps::CUmemAllocationHandleType must also be set to CU_MEM_HANDLE_TYPE_NONE since IPC is not supported. For managed memory pools, CUmemPoolProps::CUmemLocation will be treated as the preferred location for all allocations created from the pool. An application can also set CU_MEM_LOCATION_TYPE_NONE to indicate no preferred location. CUmemPoolProps::maxSize must be set to zero for managed memory pools. CUmemPoolProps::usage should be zero as decompress for managed memory is not supported. For managed memory pools, all devices on the system must have non-zero concurrentManagedAccess. If not, this call returns CUDA_ERROR_NOT_SUPPORTED

Specifying CU_MEM_HANDLE_TYPE_NONE creates a memory pool that will not support IPC.

CUresult cuMemPoolDestroy ( CUmemoryPool pool )


Destroys the specified memory pool.

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE

###### Description

If any pointers obtained from this pool haven't been freed or the pool has free operations that haven't completed when cuMemPoolDestroy is invoked, the function will return immediately and the resources associated with the pool will be released automatically once there are no more outstanding allocations.

Destroying the current mempool of a device sets the default mempool of that device as the current mempool for that device.

A device's default memory pool cannot be destroyed.

CUresult cuMemPoolExportPointer ( CUmemPoolPtrExportData* shareData_out, CUdeviceptr ptr )


Export data to share a memory pool allocation between processes.

######  Parameters

`shareData_out`
    \- Returned export data
`ptr`
    \- pointer to memory being exported

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_OUT_OF_MEMORY

###### Description

Constructs `shareData_out` for sharing a specific allocation from an already shared memory pool. The recipient process can import the allocation with the cuMemPoolImportPointer api. The data is not a handle and may be shared through any IPC mechanism.

CUresult cuMemPoolExportToShareableHandle ( void* handle_out, CUmemoryPool pool, CUmemAllocationHandleType handleType, unsigned long long flags )


Exports a memory pool to the requested handle type.

######  Parameters

`handle_out`
    \- Returned OS handle
`pool`
    \- pool to export
`handleType`
    \- the type of handle to create
`flags`
    \- must be 0

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_OUT_OF_MEMORY

###### Description

Given an IPC capable mempool, create an OS handle to share the pool with another process. A recipient process can convert the shareable handle into a mempool with cuMemPoolImportFromShareableHandle. Individual pointers can then be shared with the cuMemPoolExportPointer and cuMemPoolImportPointer APIs. The implementation of what the shareable handle is and how it can be transferred is defined by the requested handle type.

: To create an IPC capable mempool, create a mempool with a CUmemAllocationHandleType other than CU_MEM_HANDLE_TYPE_NONE.

CUresult cuMemPoolGetAccess ( CUmemAccess_flags* flags, CUmemoryPool memPool, CUmemLocation* location )


Returns the accessibility of a pool from a device.

######  Parameters

`flags`
    \- the accessibility of the pool from the specified location
`memPool`
    \- the pool being queried
`location`
    \- the location accessing the pool

###### Description

Returns the accessibility of the pool's memory from the specified location.

CUresult cuMemPoolGetAttribute ( CUmemoryPool pool, CUmemPool_attribute attr, void* value )


Gets attributes of a memory pool.

######  Parameters

`pool`
    \- The memory pool to get attributes of
`attr`
    \- The attribute to get
`value`
    \- Retrieved value

###### Returns

CUDA_SUCCESS, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_VALUE

###### Description

Supported attributes are:

  * CU_MEMPOOL_ATTR_RELEASE_THRESHOLD: (value type = cuuint64_t) Amount of reserved memory in bytes to hold onto before trying to release memory back to the OS. When more than the release threshold bytes of memory are held by the memory pool, the allocator will try to release memory back to the OS on the next call to stream, event or context synchronize. (default 0)

  * CU_MEMPOOL_ATTR_REUSE_FOLLOW_EVENT_DEPENDENCIES: (value type = int) Allow cuMemAllocAsync to use memory asynchronously freed in another stream as long as a stream ordering dependency of the allocating stream on the free action exists. Cuda events and null stream interactions can create the required stream ordered dependencies. (default enabled)

  * CU_MEMPOOL_ATTR_REUSE_ALLOW_OPPORTUNISTIC: (value type = int) Allow reuse of already completed frees when there is no dependency between the free and allocation. (default enabled)

  * CU_MEMPOOL_ATTR_REUSE_ALLOW_INTERNAL_DEPENDENCIES: (value type = int) Allow cuMemAllocAsync to insert new stream dependencies in order to establish the stream ordering required to reuse a piece of memory released by cuMemFreeAsync (default enabled).

  * CU_MEMPOOL_ATTR_RESERVED_MEM_CURRENT: (value type = cuuint64_t) Amount of backing memory currently allocated for the mempool

  * CU_MEMPOOL_ATTR_RESERVED_MEM_HIGH: (value type = cuuint64_t) High watermark of backing memory allocated for the mempool since the last time it was reset.

  * CU_MEMPOOL_ATTR_USED_MEM_CURRENT: (value type = cuuint64_t) Amount of memory from the pool that is currently in use by the application.

  * CU_MEMPOOL_ATTR_USED_MEM_HIGH: (value type = cuuint64_t) High watermark of the amount of memory from the pool that was in use by the application.


The following properties can be also be queried on imported and default pools:

  * CU_MEMPOOL_ATTR_ALLOCATION_TYPE: (value type = CUmemAllocationType) The allocation type of the mempool

  * CU_MEMPOOL_ATTR_EXPORT_HANDLE_TYPES: (value type = CUmemAllocationHandleType) Available export handle types for the mempool. For imported pools this value is always CU_MEM_HANDLE_TYPE_NONE as an imported pool cannot be re-exported

  * CU_MEMPOOL_ATTR_LOCATION_ID: (value type = int) The location id for the mempool. If the location type for this pool is CU_MEM_LOCATION_TYPE_INVISIBLE then ID will be CU_DEVICE_INVALID.

  * CU_MEMPOOL_ATTR_LOCATION_TYPE: (value type = CUmemLocationType) The location type for the mempool. For imported memory pools where the device is not directly visible to the importing process or pools imported via fabric handles across nodes this will be CU_MEM_LOCATION_TYPE_INVISIBLE.

  * CU_MEMPOOL_ATTR_MAX_POOL_SIZE: (value type = cuuint64_t) Maximum size of the pool in bytes, this value may be higher than what was initially passed to cuMemPoolCreate due to alignment requirements. A value of 0 indicates no maximum size. For CU__MEM_ALLOCATION_TYPE_MANAGED and IPC imported pools this value will be system dependent.

  * CU_MEMPOOL_ATTR_HW_DECOMPRESS_ENABLED: (value type = int) Indicates whether the pool has hardware compresssion enabled


CUresult cuMemPoolImportFromShareableHandle ( CUmemoryPool* pool_out, void* handle, CUmemAllocationHandleType handleType, unsigned long long flags )


imports a memory pool from a shared handle.

######  Parameters

`pool_out`
    \- Returned memory pool
`handle`
    \- OS handle of the pool to open
`handleType`
    \- The type of handle being imported
`flags`
    \- must be 0

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_OUT_OF_MEMORY

###### Description

Specific allocations can be imported from the imported pool with cuMemPoolImportPointer.

If `handleType` is CU_MEM_HANDLE_TYPE_FABRIC and the importer process has not been granted access to the same IMEX channel as the exporter process, this API will error as CUDA_ERROR_NOT_PERMITTED.

Imported memory pools do not support creating new allocations. As such imported memory pools may not be used in cuDeviceSetMemPool or cuMemAllocFromPoolAsync calls.

CUresult cuMemPoolImportPointer ( CUdeviceptr* ptr_out, CUmemoryPool pool, CUmemPoolPtrExportData* shareData )


Import a memory pool allocation from another process.

######  Parameters

`ptr_out`
    \- pointer to imported memory
`pool`
    \- pool from which to import
`shareData`
    \- data specifying the memory to import

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_OUT_OF_MEMORY

###### Description

Returns in `ptr_out` a pointer to the imported memory. The imported memory must not be accessed before the allocation operation completes in the exporting process. The imported memory must be freed from all importing processes before being freed in the exporting process. The pointer may be freed with cuMemFree or cuMemFreeAsync. If cuMemFreeAsync is used, the free must be completed on the importing process before the free operation on the exporting process.

The cuMemFreeAsync api may be used in the exporting process before the cuMemFreeAsync operation completes in its stream as long as the cuMemFreeAsync in the exporting process specifies a stream with a stream dependency on the importing process's cuMemFreeAsync.

CUresult cuMemPoolSetAccess ( CUmemoryPool pool, const CUmemAccessDesc* map, size_t count )


Controls visibility of pools between devices.

######  Parameters

`pool`
    \- The pool being modified
`map`
    \- Array of access descriptors. Each descriptor instructs the access to enable for a single gpu.
`count`
    \- Number of descriptors in the map array.

###### Returns

CUDA_SUCCESS, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_VALUE

###### Description

CUresult cuMemPoolSetAttribute ( CUmemoryPool pool, CUmemPool_attribute attr, void* value )


Sets attributes of a memory pool.

######  Parameters

`pool`
    \- The memory pool to modify
`attr`
    \- The attribute to modify
`value`
    \- Pointer to the value to assign

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE

###### Description

Supported attributes are:

  * CU_MEMPOOL_ATTR_RELEASE_THRESHOLD: (value type = cuuint64_t) Amount of reserved memory in bytes to hold onto before trying to release memory back to the OS. When more than the release threshold bytes of memory are held by the memory pool, the allocator will try to release memory back to the OS on the next call to stream, event or context synchronize. (default 0)

  * CU_MEMPOOL_ATTR_REUSE_FOLLOW_EVENT_DEPENDENCIES: (value type = int) Allow cuMemAllocAsync to use memory asynchronously freed in another stream as long as a stream ordering dependency of the allocating stream on the free action exists. Cuda events and null stream interactions can create the required stream ordered dependencies. (default enabled)

  * CU_MEMPOOL_ATTR_REUSE_ALLOW_OPPORTUNISTIC: (value type = int) Allow reuse of already completed frees when there is no dependency between the free and allocation. (default enabled)

  * CU_MEMPOOL_ATTR_REUSE_ALLOW_INTERNAL_DEPENDENCIES: (value type = int) Allow cuMemAllocAsync to insert new stream dependencies in order to establish the stream ordering required to reuse a piece of memory released by cuMemFreeAsync (default enabled).

  * CU_MEMPOOL_ATTR_RESERVED_MEM_HIGH: (value type = cuuint64_t) Reset the high watermark that tracks the amount of backing memory that was allocated for the memory pool. It is illegal to set this attribute to a non-zero value.

  * CU_MEMPOOL_ATTR_USED_MEM_HIGH: (value type = cuuint64_t) Reset the high watermark that tracks the amount of used memory that was allocated for the memory pool.


CUresult cuMemPoolTrimTo ( CUmemoryPool pool, size_t minBytesToKeep )


Tries to release memory back to the OS.

######  Parameters

`pool`
    \- The memory pool to trim
`minBytesToKeep`
    \- If the pool has less than minBytesToKeep reserved, the TrimTo operation is a no-op. Otherwise the pool will be guaranteed to have at least minBytesToKeep bytes reserved after the operation.

###### Returns

CUDA_SUCCESS, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_VALUE

###### Description

Releases memory back to the OS until the pool contains fewer than minBytesToKeep reserved bytes, or there is no more memory that the allocator can safely release. The allocator cannot release OS allocations that back outstanding asynchronous allocations. The OS allocations may happen at different granularity from the user allocations.

  * : Allocations that have not been freed count as outstanding.

  * : Allocations that have been asynchronously freed but whose completion has not been observed on the host (eg. by a synchronize) can count as outstanding.


CUresult cuMemSetMemPool ( CUmemLocation* location, CUmemAllocationType type, CUmemoryPool pool )


Sets the current memory pool for a memory location and allocation type.

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE

###### Description

The memory location can be of one of CU_MEM_LOCATION_TYPE_DEVICE, CU_MEM_LOCATION_TYPE_HOST or or CU_MEM_LOCATION_TYPE_HOST_NUMA. The allocation type can be one of CU_MEM_ALLOCATION_TYPE_PINNED or CU_MEM_ALLOCATION_TYPE_MANAGED. When the allocation type is CU_MEM_ALLOCATION_TYPE_MANAGED, the location type can also be CU_MEM_LOCATION_TYPE_NONE to indicate no preferred location for the managed memory pool. CU_MEM_ALLOCATION_TYPE_MANAGED can not be used with CU_MEM_LOCATION_TYPE_DEVICE_MEMORY_NODE. In all other cases, the call returns CUDA_ERROR_INVALID_VALUE.

When a memory pool is set as the current memory pool, the location parameter should be the same as the location of the pool. The location and allocation type specified must match those of the pool otherwise CUDA_ERROR_INVALID_VALUE is returned. By default, a memory location's current memory pool is its default memory pool that can be obtained via cuMemGetDefaultMemPool. If the location type is CU_MEM_LOCATION_TYPE_DEVICE and the allocation type is CU_MEM_ALLOCATION_TYPE_PINNED, then this API is the equivalent of calling cuDeviceSetMemPool with the location id as the device. For further details on the implications, please refer to the documentation for cuDeviceSetMemPool.

Use cuMemAllocFromPoolAsync to specify asynchronous allocations from a device different than the one the stream runs on.
