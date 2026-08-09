# 6.10. Module Management

**Source:** group__CUDA__MODULE.html#group__CUDA__MODULE



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

## 6.10. Module Management

This section describes the module management functions of the low-level CUDA driver application programming interface.

### Enumerations

enum CUmoduleLoadingMode


### Functions

CUresult cuLinkAddData ( CUlinkState state, CUjitInputType type, void* data, size_t size, const char* name, unsigned int  numOptions, CUjit_option* options, void** optionValues )


Add an input to a pending linker invocation.

######  Parameters

`state`
    A pending linker action.
`type`
    The type of the input data.
`data`
    The input data. PTX must be NULL-terminated.
`size`
    The length of the input data.
`name`
    An optional name for this input in log messages.
`numOptions`
    Size of options.
`options`
    Options to be applied only for this input (overrides options from cuLinkCreate).
`optionValues`
    Array of option values, each cast to void *.

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_HANDLE, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_INVALID_IMAGE, CUDA_ERROR_INVALID_PTX, CUDA_ERROR_UNSUPPORTED_PTX_VERSION, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_NO_BINARY_FOR_GPU

###### Description

Ownership of `data` is retained by the caller. No reference is retained to any inputs after this call returns.

This method accepts only compiler options, which are used if the data must be compiled from PTX, and does not accept any of CU_JIT_WALL_TIME, CU_JIT_INFO_LOG_BUFFER, CU_JIT_ERROR_LOG_BUFFER, CU_JIT_TARGET_FROM_CUCONTEXT, or CU_JIT_TARGET.

For LTO-IR input, only LTO-IR compiled with toolkits prior to CUDA 12.0 will be accepted

CUresult cuLinkAddFile ( CUlinkState state, CUjitInputType type, const char* path, unsigned int  numOptions, CUjit_option* options, void** optionValues )


Add a file input to a pending linker invocation.

######  Parameters

`state`
    A pending linker action
`type`
    The type of the input data
`path`
    Path to the input file
`numOptions`
    Size of options
`options`
    Options to be applied only for this input (overrides options from cuLinkCreate)
`optionValues`
    Array of option values, each cast to void *

###### Returns

CUDA_SUCCESS, CUDA_ERROR_FILE_NOT_FOUNDCUDA_ERROR_INVALID_HANDLE, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_INVALID_IMAGE, CUDA_ERROR_INVALID_PTX, CUDA_ERROR_UNSUPPORTED_PTX_VERSION, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_NO_BINARY_FOR_GPU

###### Description

No reference is retained to any inputs after this call returns.

This method accepts only compiler options, which are used if the input must be compiled from PTX, and does not accept any of CU_JIT_WALL_TIME, CU_JIT_INFO_LOG_BUFFER, CU_JIT_ERROR_LOG_BUFFER, CU_JIT_TARGET_FROM_CUCONTEXT, or CU_JIT_TARGET.

This method is equivalent to invoking cuLinkAddData on the contents of the file.

For LTO-IR input, only LTO-IR compiled with toolkits prior to CUDA 12.0 will be accepted

CUresult cuLinkComplete ( CUlinkState state, void** cubinOut, size_t* sizeOut )


Complete a pending linker invocation.

######  Parameters

`state`
    A pending linker invocation
`cubinOut`
    On success, this will point to the output image
`sizeOut`
    Optional parameter to receive the size of the generated image

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_HANDLE, CUDA_ERROR_OUT_OF_MEMORY

###### Description

Completes the pending linker action and returns the cubin image for the linked device code, which can be used with cuModuleLoadData. The cubin is owned by `state`, so it should be loaded before `state` is destroyed via cuLinkDestroy. This call does not destroy `state`.

CUresult cuLinkCreate ( unsigned int  numOptions, CUjit_option* options, void** optionValues, CUlinkState* stateOut )


Creates a pending JIT linker invocation.

######  Parameters

`numOptions`
    Size of options arrays
`options`
    Array of linker and compiler options
`optionValues`
    Array of option values, each cast to void *
`stateOut`
    On success, this will contain a CUlinkState to specify and complete this action

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_JIT_COMPILER_NOT_FOUND

###### Description

If the call is successful, the caller owns the returned CUlinkState, which should eventually be destroyed with cuLinkDestroy. The device code machine size (32 or 64 bit) will match the calling application.

Both linker and compiler options may be specified. Compiler options will be applied to inputs to this linker action which must be compiled from PTX. The options CU_JIT_WALL_TIME, CU_JIT_INFO_LOG_BUFFER_SIZE_BYTES, and CU_JIT_ERROR_LOG_BUFFER_SIZE_BYTES will accumulate data until the CUlinkState is destroyed.

The data passed in via cuLinkAddData and cuLinkAddFile will be treated as relocatable (-rdc=true to nvcc) when linking the final cubin during cuLinkComplete and will have similar consequences as offline relocatable device code linking.

`optionValues` must remain valid for the life of the CUlinkState if output options are used. No other references to inputs are maintained after this call returns.

For LTO-IR input, only LTO-IR compiled with toolkits prior to CUDA 12.0 will be accepted

CUresult cuLinkDestroy ( CUlinkState state )


Destroys state for a JIT linker invocation.

######  Parameters

`state`
    State object for the linker invocation

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_HANDLE

###### Description

CUresult cuModuleEnumerateFunctions ( CUfunction* functions, unsigned int  numFunctions, CUmodule mod )


Returns the function handles within a module.

######  Parameters

`functions`
    \- Buffer where the function handles are returned to
`numFunctions`
    \- Maximum number of function handles may be returned to the buffer
`mod`
    \- Module to query from

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_HANDLE, CUDA_ERROR_INVALID_VALUE

###### Description

Returns in `functions` a maximum number of `numFunctions` function handles within `mod`. When function loading mode is set to LAZY the function retrieved may be partially loaded. The loading state of a function can be queried using cuFunctionIsLoaded. CUDA APIs may load the function automatically when called with partially loaded function handle which may incur additional latency. Alternatively, cuFunctionLoad can be used to explicitly load a function. The returned function handles become invalid when the module is unloaded.

CUresult cuModuleGetFunction ( CUfunction* hfunc, CUmodule hmod, const char* name )


Returns a function handle.

######  Parameters

`hfunc`
    \- Returned function handle
`hmod`
    \- Module to retrieve function from
`name`
    \- Name of function to retrieve

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_FOUND

###### Description

Returns in `*hfunc` the handle of the function of name `name` located in module `hmod`. If no function of that name exists, cuModuleGetFunction() returns CUDA_ERROR_NOT_FOUND.

CUresult cuModuleGetFunctionCount ( unsigned int* count, CUmodule mod )


Returns the number of functions within a module.

######  Parameters

`count`
    \- Number of functions found within the module
`mod`
    \- Module to query

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_HANDLE, CUDA_ERROR_INVALID_VALUE

###### Description

Returns in `count` the number of functions in `mod`.

CUresult cuModuleGetGlobal ( CUdeviceptr* dptr, size_t* bytes, CUmodule hmod, const char* name )


Returns a global pointer from a module.

######  Parameters

`dptr`
    \- Returned global device pointer
`bytes`
    \- Returned global size in bytes
`hmod`
    \- Module to retrieve global from
`name`
    \- Name of global to retrieve

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_FOUND

###### Description

Returns in `*dptr` and `*bytes` the base pointer and size of the global of name `name` located in module `hmod`. If no variable of that name exists, cuModuleGetGlobal() returns CUDA_ERROR_NOT_FOUND. One of the parameters `dptr` or `bytes` (not both) can be NULL in which case it is ignored.

CUresult cuModuleGetLoadingMode ( CUmoduleLoadingMode* mode )


Query lazy loading mode.

######  Parameters

`mode`
    \- Returns the lazy loading mode

###### Returns

CUDA_SUCCESS, CUDA_ERROR_INVALID_VALUE

###### Description

Returns lazy loading mode Module loading mode is controlled by CUDA_MODULE_LOADING env variable

CUresult cuModuleLoad ( CUmodule* module, const char* fname )


Loads a compute module.

######  Parameters

`module`
    \- Returned module
`fname`
    \- Filename of module to load

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_INVALID_PTX, CUDA_ERROR_UNSUPPORTED_PTX_VERSION, CUDA_ERROR_NOT_FOUND, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_FILE_NOT_FOUND, CUDA_ERROR_NO_BINARY_FOR_GPU, CUDA_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND, CUDA_ERROR_SHARED_OBJECT_INIT_FAILED, CUDA_ERROR_JIT_COMPILER_NOT_FOUND

###### Description

Takes a filename `fname` and loads the corresponding module `module` into the current context. The CUDA driver API does not attempt to lazily allocate the resources needed by a module; if the memory for functions and data (constant and global) needed by the module cannot be allocated, cuModuleLoad() fails. The file should be a cubin file as output by **nvcc** , or a PTX file either as output by **nvcc** or handwritten, or a fatbin file as output by **nvcc** from toolchain 4.0 or later, or a Tile IR file.

CUresult cuModuleLoadData ( CUmodule* module, const void* image )


Load a module's data.

######  Parameters

`module`
    \- Returned module
`image`
    \- Module data to load

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_INVALID_PTX, CUDA_ERROR_UNSUPPORTED_PTX_VERSION, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_NO_BINARY_FOR_GPU, CUDA_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND, CUDA_ERROR_SHARED_OBJECT_INIT_FAILED, CUDA_ERROR_JIT_COMPILER_NOT_FOUND

###### Description

Takes a pointer `image` and loads the corresponding module `module` into the current context. The `image` may be a cubin or fatbin as output by **nvcc** , or a NULL-terminated PTX, either as output by **nvcc** or hand-written, or Tile IR data.

CUresult cuModuleLoadDataEx ( CUmodule* module, const void* image, unsigned int  numOptions, CUjit_option* options, void** optionValues )


Load a module's data with options.

######  Parameters

`module`
    \- Returned module
`image`
    \- Module data to load
`numOptions`
    \- Number of options
`options`
    \- Options for JIT
`optionValues`
    \- Option values for JIT

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_INVALID_PTX, CUDA_ERROR_UNSUPPORTED_PTX_VERSION, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_NO_BINARY_FOR_GPU, CUDA_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND, CUDA_ERROR_SHARED_OBJECT_INIT_FAILED, CUDA_ERROR_JIT_COMPILER_NOT_FOUND

###### Description

Takes a pointer `image` and loads the corresponding module `module` into the current context. The `image` may be a cubin or fatbin as output by **nvcc** , or a NULL-terminated PTX, either as output by **nvcc** or hand-written, or Tile IR data.

CUresult cuModuleLoadFatBinary ( CUmodule* module, const void* fatCubin )


Load a module's data.

######  Parameters

`module`
    \- Returned module
`fatCubin`
    \- Fat binary to load

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_INVALID_PTX, CUDA_ERROR_UNSUPPORTED_PTX_VERSION, CUDA_ERROR_NOT_FOUND, CUDA_ERROR_OUT_OF_MEMORY, CUDA_ERROR_NO_BINARY_FOR_GPU, CUDA_ERROR_SHARED_OBJECT_SYMBOL_NOT_FOUND, CUDA_ERROR_SHARED_OBJECT_INIT_FAILED, CUDA_ERROR_JIT_COMPILER_NOT_FOUND

###### Description

Takes a pointer `fatCubin` and loads the corresponding module `module` into the current context. The pointer represents a fat binary object, which is a collection of different cubin and/or PTX files, all representing the same device code, but compiled and optimized for different architectures.

Prior to CUDA 4.0, there was no documented API for constructing and using fat binary objects by programmers. Starting with CUDA 4.0, fat binary objects can be constructed by providing the -fatbin option to **nvcc**. More information can be found in the **nvcc** document.

CUresult cuModuleUnload ( CUmodule hmod )


Unloads a module.

######  Parameters

`hmod`
    \- Module to unload

###### Returns

CUDA_SUCCESS, CUDA_ERROR_DEINITIALIZED, CUDA_ERROR_NOT_INITIALIZED, CUDA_ERROR_INVALID_CONTEXT, CUDA_ERROR_INVALID_VALUE, CUDA_ERROR_NOT_PERMITTED

###### Description

Unloads a module `hmod` from the current context. Attempting to unload a module which was obtained from the Library Management API such as cuLibraryGetModule will return CUDA_ERROR_NOT_PERMITTED.

  *

  * Use of the handle after this call is undefined behavior.

