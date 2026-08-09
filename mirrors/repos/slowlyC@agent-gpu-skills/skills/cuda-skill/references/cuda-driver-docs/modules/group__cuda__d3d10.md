# 6.43. Direct3D 10 Interoperability

**Source:** group__CUDA__D3D10.html#group__CUDA__D3D10



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

## 6.43. Direct3D 10 Interoperability

This section describes the Direct3D 10 interoperability functions of the low-level CUDA driver application programming interface. Note that mapping of Direct3D 10 resources is performed with the graphics API agnostic, resource mapping interface described in Graphics Interoperability.

### Modules

[Direct3D 10 Interoperability [DEPRECATED]](https://docs.nvidia.com/cuda/cuda-driver-api/group__CUDA__D3D10__DEPRECATED.html#group__CUDA__D3D10__DEPRECATED)



### Enumerations

enum CUd3d10DeviceList


### Functions

CUresult cuD3D10GetDevice ( CUdevice* pCudaDevice, IDXGIAdapter* pAdapter )


Gets the CUDA device corresponding to a display adapter.

######  Parameters

`pCudaDevice`
    \- Returned CUDA device corresponding to `pAdapter`
`pAdapter`
    \- Adapter to query for CUDA device

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_FOUND, CUDA_ERROR_UNKNOWN

###### Description

Returns in `*pCudaDevice` the CUDA-compatible device corresponding to the adapter `pAdapter` obtained from IDXGIFactory::EnumAdapters.

If no device on `pAdapter` is CUDA-compatible then the call will fail.

CUresult cuD3D10GetDevices ( unsigned int* pCudaDeviceCount, CUdevice* pCudaDevices, unsigned int  cudaDeviceCount, ID3D10Device* pD3D10Device, CUd3d10DeviceList deviceList )


Gets the CUDA devices corresponding to a Direct3D 10 device.

######  Parameters

`pCudaDeviceCount`
    \- Returned number of CUDA devices corresponding to `pD3D10Device`
`pCudaDevices`
    \- Returned CUDA devices corresponding to `pD3D10Device`
`cudaDeviceCount`
    \- The size of the output device array `pCudaDevices`
`pD3D10Device`
    \- Direct3D 10 device to query for CUDA devices
`deviceList`
    \- The set of devices to return. This set may be CU_D3D10_DEVICE_LIST_ALL for all devices, CU_D3D10_DEVICE_LIST_CURRENT_FRAME for the devices used to render the current frame (in SLI), or CU_D3D10_DEVICE_LIST_NEXT_FRAME for the devices used to render the next frame (in SLI).

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_NO_DEVICE, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_FOUND, CUDA_ERROR_UNKNOWN

###### Description

Returns in `*pCudaDeviceCount` the number of CUDA-compatible device corresponding to the Direct3D 10 device `pD3D10Device`. Also returns in `*pCudaDevices` at most `cudaDeviceCount` of the CUDA-compatible devices corresponding to the Direct3D 10 device `pD3D10Device`.

If any of the GPUs being used to render `pDevice` are not CUDA capable then the call will return CUDA_ERROR_NO_DEVICE.

CUresult cuGraphicsD3D10RegisterResource ( CUgraphicsResource* pCudaResource, ID3D10Resource* pD3DResource, unsigned int  Flags )


Register a Direct3D 10 resource for access by CUDA.

######  Parameters

`pCudaResource`
    \- Returned graphics resource handle
`pD3DResource`
    \- Direct3D resource to register
`Flags`
    \- Parameters for resource registration

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_INVALID_HANDLE, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_UNKNOWN

###### Description

Registers the Direct3D 10 resource `pD3DResource` for access by CUDA and returns a CUDA handle to `pD3Dresource` in `pCudaResource`. The handle returned in `pCudaResource` may be used to map and unmap this resource until it is unregistered. On success this call will increase the internal reference count on `pD3DResource`. This reference count will be decremented when this resource is unregistered through cuGraphicsUnregisterResource().

This call is potentially high-overhead and should not be called every frame in interactive applications.

The type of `pD3DResource` must be one of the following.

  * ID3D10Buffer: may be accessed through a device pointer.

  * ID3D10Texture1D: individual subresources of the texture may be accessed via arrays

  * ID3D10Texture2D: individual subresources of the texture may be accessed via arrays

  * ID3D10Texture3D: individual subresources of the texture may be accessed via arrays


The `Flags` argument may be used to specify additional parameters at register time. The valid values for this parameter are

  * CU_GRAPHICS_REGISTER_FLAGS_NONE: Specifies no hints about how this resource will be used.

  * CU_GRAPHICS_REGISTER_FLAGS_SURFACE_LDST: Specifies that CUDA will bind this resource to a surface reference.

  * CU_GRAPHICS_REGISTER_FLAGS_TEXTURE_GATHER: Specifies that CUDA will perform texture gather operations on this resource.


Not all Direct3D resources of the above types may be used for interoperability with CUDA. The following are some limitations.

  * The primary rendertarget may not be registered with CUDA.

  * Textures which are not of a format which is 1, 2, or 4 channels of 8, 16, or 32-bit integer or floating-point data cannot be shared.

  * Surfaces of depth or stencil formats cannot be shared.


A complete list of supported DXGI formats is as follows. For compactness the notation A_{B,C,D} represents A_B, A_C, and A_D.

  * DXGI_FORMAT_A8_UNORM

  * DXGI_FORMAT_B8G8R8A8_UNORM

  * DXGI_FORMAT_B8G8R8X8_UNORM

  * DXGI_FORMAT_R16_FLOAT

  * DXGI_FORMAT_R16G16B16A16_{FLOAT,SINT,SNORM,UINT,UNORM}

  * DXGI_FORMAT_R16G16_{FLOAT,SINT,SNORM,UINT,UNORM}

  * DXGI_FORMAT_R16_{SINT,SNORM,UINT,UNORM}

  * DXGI_FORMAT_R32_FLOAT

  * DXGI_FORMAT_R32G32B32A32_{FLOAT,SINT,UINT}

  * DXGI_FORMAT_R32G32_{FLOAT,SINT,UINT}

  * DXGI_FORMAT_R32_{SINT,UINT}

  * DXGI_FORMAT_R8G8B8A8_{SINT,SNORM,UINT,UNORM,UNORM_SRGB}

  * DXGI_FORMAT_R8G8_{SINT,SNORM,UINT,UNORM}

  * DXGI_FORMAT_R8_{SINT,SNORM,UINT,UNORM}


If `pD3DResource` is of incorrect type or is already registered then CUDA_ERROR_INVALID_HANDLE is returned. If `pD3DResource` cannot be registered then CUDA_ERROR_UNKNOWN is returned. If `Flags` is not one of the above specified value then CUDA_ERROR_INVALID_VALUE is returned.

### Direct3D 10 Interoperability [DEPRECATED]

* * *
