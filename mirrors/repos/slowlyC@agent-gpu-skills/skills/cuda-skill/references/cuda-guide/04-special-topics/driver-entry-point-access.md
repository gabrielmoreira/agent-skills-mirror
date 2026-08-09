---
url: https://docs.nvidia.com/cuda/cuda-programming-guide/04-special-topics/driver-entry-point-access.html
---

# 4.20. Driver Entry Point Access

## 4.20.1. Introduction

The `Driver Entry Point Access APIs` provide a way to retrieve the address of a CUDA driver function. Starting from CUDA 11.3, users can call into available CUDA driver APIs using function pointers obtained from these APIs.

These APIs provide functionality similar to their counterparts, dlsym on POSIX platforms and GetProcAddress on Windows. The provided APIs will let users:

  * Retrieve the address of a driver function using the `CUDA Driver API.`

  * Retrieve the address of a driver function using the `CUDA Runtime API.`

  * Request _per-thread default stream_ version of a CUDA driver function. For more details, see [Retrieve Per-thread Default Stream Versions](#retrieve-per-thread-default-stream-versions).

  * Access new CUDA features on older toolkits but with a newer driver.


## 4.20.2. Driver Function Typedefs

To help retrieve the CUDA Driver API entry points, the CUDA Toolkit provides access to headers containing the function pointer definitions for all CUDA driver APIs. These headers are installed with the CUDA Toolkit and are made available in the toolkit’s `include/` directory. The table below summarizes the header files containing the `typedefs` for each CUDA API header file.

Table 27 Typedefs header files for CUDA driver APIs API header file | API Typedef header file
---|---
`cuda.h` | `cudaTypedefs.h`
`cudaGL.h` | `cudaGLTypedefs.h`
`cudaProfiler.h` | `cudaProfilerTypedefs.h`
`cudaVDPAU.h` | `cudaVDPAUTypedefs.h`
`cudaEGL.h` | `cudaEGLTypedefs.h`
`cudaD3D9.h` | `cudaD3D9Typedefs.h`
`cudaD3D10.h` | `cudaD3D10Typedefs.h`
`cudaD3D11.h` | `cudaD3D11Typedefs.h`

The above headers do not define actual function pointers themselves; they define the typedefs for function pointers. For example, `cudaTypedefs.h` has the below typedefs for the driver API `cuMemAlloc`:


    typedef CUresult (CUDAAPI *PFN_cuMemAlloc_v3020)(CUdeviceptr_v2 *dptr, size_t bytesize);
    typedef CUresult (CUDAAPI *PFN_cuMemAlloc_v2000)(CUdeviceptr_v1 *dptr, unsigned int bytesize);


CUDA driver symbols have a version based naming scheme with a `_v*` extension in its name except for the first version. When the signature or the semantics of a specific CUDA driver API changes, we increment the version number of the corresponding driver symbol. In the case of the `cuMemAlloc` driver API, the first driver symbol name is `cuMemAlloc` and the next symbol name is `cuMemAlloc_v2`. The typedef for the first version which was introduced in CUDA 2.0 (2000) is `PFN_cuMemAlloc_v2000`. The typedef for the next version which was introduced in CUDA 3.2 (3020) is `PFN_cuMemAlloc_v3020`.

The `typedefs` can be used to more easily define a function pointer of the appropriate type in code:


    PFN_cuMemAlloc_v3020 pfn_cuMemAlloc_v2;
    PFN_cuMemAlloc_v2000 pfn_cuMemAlloc_v1;


## 4.20.3. Driver Function Retrieval

Using the Driver Entry Point Access APIs and the appropriate typedef, we can get the function pointer to any CUDA driver API.

### 4.20.3.1. Using the Driver API

The driver API requires CUDA version as an argument to get the ABI compatible version for the requested driver symbol. CUDA Driver APIs have a per-function ABI denoted with a `_v*` extension. For example, consider the versions of `cuStreamBeginCapture` and their corresponding `typedefs` from `cudaTypedefs.h`:


    // cuda.h
    CUresult CUDAAPI cuStreamBeginCapture(CUstream hStream);
    CUresult CUDAAPI cuStreamBeginCapture_v2(CUstream hStream, CUstreamCaptureMode mode);

    // cudaTypedefs.h
    typedef CUresult (CUDAAPI *PFN_cuStreamBeginCapture_v10000)(CUstream hStream);
    typedef CUresult (CUDAAPI *PFN_cuStreamBeginCapture_v10010)(CUstream hStream, CUstreamCaptureMode mode);


From the above `typedefs` in the code snippet, version suffixes `_v10000` and `_v10010` indicate that the above APIs were introduced in CUDA 10.0 and CUDA 10.1 respectively.


    #include <cudaTypedefs.h>

    // Declare the entry points for cuStreamBeginCapture
    PFN_cuStreamBeginCapture_v10000 pfn_cuStreamBeginCapture_v1;
    PFN_cuStreamBeginCapture_v10010 pfn_cuStreamBeginCapture_v2;

    // Get the function pointer to the cuStreamBeginCapture driver symbol
    cuGetProcAddress("cuStreamBeginCapture", &pfn_cuStreamBeginCapture_v1, 10000, CU_GET_PROC_ADDRESS_DEFAULT, &driverStatus);
    // Get the function pointer to the cuStreamBeginCapture_v2 driver symbol
    cuGetProcAddress("cuStreamBeginCapture", &pfn_cuStreamBeginCapture_v2, 10010, CU_GET_PROC_ADDRESS_DEFAULT, &driverStatus);


Referring to the code snippet above, to retrieve the address to the `_v1` version of the driver API `cuStreamBeginCapture`, the CUDA version argument should be exactly 10.0 (10000). Similarly, the CUDA version for retrieving the address to the `_v2` version of the API should be 10.1 (10010). Specifying a higher CUDA version for retrieving a specific version of a driver API might not always be portable. For example, using 11030 here would still return the `_v2` symbol, but if a hypothetical `_v3` version is released in CUDA 11.3, the `cuGetProcAddress` API would start returning the newer `_v3` symbol instead when paired with a CUDA 11.3 driver. Since the ABI and function signatures of the `_v2` and `_v3` symbols might differ, calling the `_v3` function using the `_v10010` typedef intended for the `_v2` symbol would exhibit undefined behavior.

Note that requesting a driver API with an invalid CUDA version will return an error `CUDA_ERROR_NOT_FOUND`. In the above code examples, passing in a version less than 10000 (CUDA 10.0) would be invalid.

### 4.20.3.2. Using the Runtime API

The runtime API `cudaGetDriverEntryPointByVersion` uses the provided CUDA version to get the ABI compatible version for the requested driver symbol in the same way `cuGetProcAddress` does. In the below code snippet, the minimum CUDA version required would be CUDA 11.2 as `cuMemAllocAsync` was introduced then.


    #include <cudaTypedefs.h>

    int cudaVersion;
    // Ensure a CUDA driver >= 11.2 is installed or we will get an error from cuGetProcAddress
    status = cuDriverGetVersion(&cudaVersion);
    if (cudaVersion >= 11020) {

       // Declare the entry point
       PFN_cuMemAllocAsync_v11020 pfn_cuMemAllocAsync;

       // Initialize the entry point
       cudaGetDriverEntryPointByVersion("cuMemAllocAsync", &pfn_cuMemAllocAsync, 11020, cudaEnableDefault, &driverStatus);

       // Call the entry point
       if(driverStatus == cudaDriverEntryPointSuccess && pfn_cuMemAllocAsync) {
           pfn_cuMemAllocAsync(...);
       }
    }


### 4.20.3.3. Retrieve Per-thread Default Stream Versions

Some CUDA driver APIs can be configured to have _default stream_ or _per-thread default stream_ semantics. Driver APIs having _per-thread default stream_ semantics are suffixed with __ptsz_ or __ptds_ in their name. For example, `cuLaunchKernel` has a _per-thread default stream_ variant named `cuLaunchKernel_ptsz`. With the Driver Entry Point Access APIs, users can request for the _per-thread default stream_ version of the driver API `cuLaunchKernel` instead of the _default stream_ version. Configuring the CUDA driver APIs for _default stream_ or _per-thread default stream_ semantics affects the synchronization behavior. More details can be found [here](https://docs.nvidia.com/cuda/cuda-driver-api/stream-sync-behavior.html#stream-sync-behavior__default-stream).

The _default stream_ or _per-thread default stream_ versions of a driver API can be obtained by one of the following ways:

  * Use the compilation flag `--default-stream per-thread` or define the macro `CUDA_API_PER_THREAD_DEFAULT_STREAM` to get _per-thread default stream_ behavior.

  * Force _default stream_ or _per-thread default stream_ behavior using the flags `CU_GET_PROC_ADDRESS_LEGACY_STREAM/cudaEnableLegacyStream` or `CU_GET_PROC_ADDRESS_PER_THREAD_DEFAULT_STREAM/cudaEnablePerThreadDefaultStream` respectively.


### 4.20.3.4. Access New CUDA features

It is always recommended to install the latest CUDA toolkit to access new CUDA driver features, but if for some reason, a user does not want to update or does not have access to the latest toolkit, the API can be used to access new CUDA features with only an updated CUDA driver. For discussion, let us assume the user is on CUDA 12.3 and wants to use a new driver API `cuFoo` available in the CUDA 12.5 driver. The below code snippet illustrates this use-case:


    int main()
    {
        // Manually define the prototype as cudaTypedefs.h in CUDA 12.3 does not have the cuFoo typedef
        typedef CUresult (CUDAAPI *PFN_cuFoo_v12050)(...);
        PFN_cuFoo_v12050 pfn_cuFoo = NULL;
        CUdriverProcAddressQueryResult driverStatus;
        int cudaVersion;

        // Ensure a CUDA driver >= 12.5 is installed or we will get an error from cuGetProcAddress
        CUresult status = cuDriverGetVersion(&cudaVersion);
        if (cudaVersion >= 12050) {
            // Get the address for cuFoo API using cuGetProcAddress. Specify CUDA version as
            // 12050 since cuFoo was introduced then
            CUresult status = cuGetProcAddress("cuFoo", &pfn_cuFoo, 12050, CU_GET_PROC_ADDRESS_DEFAULT, &driverStatus);

            if (status == CUDA_SUCCESS && pfn_cuFoo) {
                pfn_cuFoo(...);
            }
            else {
                printf("Cannot retrieve the address to cuFoo - driverStatus = %d\n", driverStatus);
                assert(0);
            }
        }

        // rest of code here
    }


In the next example, we discuss how to get a new version of an API released in a minor version of the CUDA Toolkit. Note that in the cuda.h header the version macro that would bump `cuDeviceGetUuid` to _v2 is not done until a major boundary. So during the 11.4+ releases the following example illustrates how to get the _v2 version.

Note in this case the original (not the _v2 version) typedef looks like:


    typedef CUresult (CUDAAPI *PFN_cuDeviceGetUuid_v9020)(CUuuid *uuid, CUdevice_v1 dev);


But the _v2 version typedef looks like:


    typedef CUresult (CUDAAPI *PFN_cuDeviceGetUuid_v11040)(CUuuid *uuid, CUdevice_v1 dev);



    #include <cudaTypedefs.h>

    CUuuid uuid;
    CUdevice dev;
    CUresult status;
    int cudaVersion;
    CUdriverProcAddressQueryResult driverStatus;

    status = cuDeviceGet(&dev, 0); // Get device 0
    // handle status

    // Ensure a CUDA driver >= 11.4 is installed or we will get an error from cuGetProcAddress
    status = cuDriverGetVersion(&cudaVersion);
    if (cudaVersion >= 11040) {
       PFN_cuDeviceGetUuid_v11040 pfn_cuDeviceGetUuid;
       status = cuGetProcAddress("cuDeviceGetUuid", &pfn_cuDeviceGetUuid, 11040, CU_GET_PROC_ADDRESS_DEFAULT, &driverStatus);
       if(CUDA_SUCCESS == status && pfn_cuDeviceGetUuid) {
          pfn_cuDeviceGetUuid(&uuid, dev);
       }
    }


## 4.20.4. Guidelines for cuGetProcAddress

Below are guidelines to keep in mind when using `cuGetProcAddress`.

  * Code the CUDA version passed to `cuGetProcAddress` to match the typedef version (do not use a compile time constant such as `CUDA_VERSION` or a dynamic version such as returned from `cuDriverGetVersion`)

  * Check the current driver version (such as from `cuDriverGetVersion`) is sufficient before calling `cuGetProcAddress` or an error is expected or an unexpected symbol may be returned


### 4.20.4.1. Guidelines for Runtime API Usage

Unless specified otherwise, the CUDA runtime API `cudaGetDriverEntryPointByVersion` will have similar guidelines as the driver entry point `cuGetProcAddress` since it allows for the user to request a specific CUDA driver version.

## 4.20.5. Determining cuGetProcAddress Failure Reasons

There are two types of errors with cuGetProcAddress. Those are (1) API/usage errors and (2) inability to find the driver API requested. The first error type will return error codes from the API via the CUresult return value. Things like passing NULL as the `pfn` variable or passing invalid `flags`.

The second error type encodes in the `CUdriverProcAddressQueryResult *symbolStatus` and can be used to help distinguish potential issues with the driver not being able to find the symbol requested. Take the following example:


    // cuDeviceGetExecAffinitySupport was introduced in release CUDA 11.4
    #include <cuda.h>
    CUdriverProcAddressQueryResult driverStatus;
    cudaVersion = ...;
    status = cuGetProcAddress("cuDeviceGetExecAffinitySupport", &pfn, cudaVersion, 0, &driverStatus);
    if (CUDA_SUCCESS == status) {
        if (CU_GET_PROC_ADDRESS_VERSION_NOT_SUFFICIENT == driverStatus) {
            printf("We can use the new feature when you upgrade cudaVersion to 11.4, but CUDA driver is good to go!\n");
            // Indicating cudaVersion was < 11.4 but run against a CUDA driver >= 11.4
        }
        else if (CU_GET_PROC_ADDRESS_SYMBOL_NOT_FOUND == driverStatus) {
            printf("Please update both CUDA driver and cudaVersion to at least 11.4 to use the new feature!\n");
            // Indicating driver is < 11.4 since string not found, doesn't matter what cudaVersion was
        }
        else if (CU_GET_PROC_ADDRESS_SUCCESS == driverStatus && pfn) {
            printf("You're using cudaVersion and CUDA driver >= 11.4, using new feature!\n");
            pfn();
        }
    }


The first case with the return code `CU_GET_PROC_ADDRESS_VERSION_NOT_SUFFICIENT` indicates that the `symbol` was found when searching in the CUDA driver but it was added later than the `cudaVersion` supplied. In the example, specifying `cudaVersion` as anything 11030 or less and when running against a CUDA driver >= CUDA 11.4 would give this result of `CU_GET_PROC_ADDRESS_VERSION_NOT_SUFFICIENT`. This is because `cuDeviceGetExecAffinitySupport` was added in CUDA 11.4 (11040).

The second case with the return code `CU_GET_PROC_ADDRESS_SYMBOL_NOT_FOUND` indicates that the `symbol` was not found when searching in the CUDA driver. This can be due to a few reasons such as unsupported CUDA function due to older driver as well as just having a typo. In the latter, similar to the last example if the user had put `symbol` as CUDeviceGetExecAffinitySupport - notice the capital CU to start the string - `cuGetProcAddress` would not be able to find the API because the string doesn’t match. In the former case an example might be the user developing an application against a CUDA driver supporting the new API, and deploying the application against an older CUDA driver. Using the last example, if the developer developed against CUDA 11.4 or later but was deployed against a CUDA 11.3 driver, during their development they may have had a successful `cuGetProcAddress`, but when deploying an application running against a CUDA 11.3 driver the call would no longer work with the `CU_GET_PROC_ADDRESS_SYMBOL_NOT_FOUND` returned in `driverStatus`.