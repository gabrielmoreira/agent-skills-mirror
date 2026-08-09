---
url: https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html
---

# 2.2. Intro to CUDA Python

This chapter introduces CUDA kernel programming in Python. The CUDA Python ecosystem encapsulates a large and actively evolving ecosystem of tools and libraries. This chapter will start by introducing some of these components and then use a few of them to illustrate methods for writing and executing GPU code in Python.

There are a large number of ways to leverage GPU computing in Python, many of which do not require writing GPU kernels explicitly. Some components of the [CUDA Python Ecosystem](#intro-cuda-python-ecosystem) provide functions which do their operations on the GPU without the developer needing to do any specific GPU control or coding. The [NVIDIA Accelerated Computing Hub](https://github.com/NVIDIA/accelerated-computing-hub) has an [Accelerated Python User’s Guide](https://github.com/NVIDIA/accelerated-computing-hub/tree/main/Accelerated_Python_User_Guide/notebooks) , which introduces and discusses many of the different libraries and tools which enable GPU-accelerated computing in Python. This resource is a good starting point for users looking to use GPUs in Python as quickly and easily as possible without necessarily writing GPU code directly.

This chapter, on the other hand, focuses on direct control of the GPU and writing kernels in Python that execute on the GPU. This chapter focuses on [CUDA Single Instruction Multiple Thread (SIMT)](../01-introduction/programming-model.html#programming-model-warps-simt) programming in Python.

## 2.2.1. CUDA Python Ecosystem

CUDA Python is an ecosystem of tools and libraries enabling GPU computing in Python. The following list introduces the main pieces of CUDA Python, not all of which are required for the content covered here. This list is adapted from the complete list found at the [CUDA Python github repository](https://github.com/NVIDIA/cuda-python).

**Main Components** \- For GPU control and running library-provided GPU code

  * `cuda.core` \- Pythonic interface for CUDA controls such as memory and device management. Provides for Python what the CUDA Runtime provides for CUDA C++.

  * `cuda.compute` \- A Python module which provides GPU-accelerated functions provided by the [CUDA Core Compute Library (CCCL)](https://nvidia.github.io/cccl/unstable/python/compute.html).

  * `CuPy` \- A Python library which provides GPU-accelerated versions of Numpy routines, and also a GPU-accelerated version of the `ndarray` data container.


**Kernel Authoring Components**

  * `cuda.lang` \- A Python Domain-specific language (DSL) for writing CUDA kernels and device functions in the SIMT programming model using a subset the of Python language.

  * `cuda.coop` \- A Python module providing device-callable (using `cuda.lang`) primitives of the [CUDA Core Compute Library (CCCL)](https://nvidia.github.io/cccl/unstable/python/coop.html).

  * `cuda.tile` \- A Python Domain-specific language (DSL) for writing CUDA kernels and device functions in the Tile programming model.


**Other Components**

  * `cuda.pathfinder` \- A utility for locating CUDA components installed in the Python environment

  * `cuda.bindings` \- Low level Python bindings for CUDA libraries and utilities including the CUDA Driver API, CUDA Runtime API, NVRTC, NVVM, and others. `cuda.bindings` provides the same functionality available in `cuda.core` via the CUDA Driver and CUDA Runtime components. However, `cuda.bindings` provides these as Python wrappers on the C-language APIs, not native Pythonic interfaces.


### 2.2.1.1. Using CUDA Libraries in Python

CUDA C++ has a rich ecosystem of libraries which allow for GPU acceleration without the need to write kernel or GPU code directly. When CUDA C++ was introduced in 2006, there were few libraries and developers largely had to write GPU kernel code themselves. Since then, [a large number of libraries](https://developer.nvidia.com/cuda/cuda-x-libraries) have been developed which allow developers to take advantage of GPU computing in C++ without writing much, if any, GPU code.

The CUDA Python ecosystem has evolved from the other direction: Python libraries such as CuPy provided GPU-accelerated implementations of computations and algorithms to Python developers before the ability to write custom kernels directly using Python syntax and semantics became available. Many of these libraries provided Python bindings to GPU code implemented in CUDA C++.

In the modern era of CUDA, it is almost always advisable to use GPU-accelerated libraries if they provide the necessary expressiveness for your needs. Many of these libraries provide implementations tuned by GPU computing experts. When libraries are not available or sufficient, writing GPU kernels and device functions directly is available in Python as in C++.

### 2.2.1.2. Scope of This Chapter

While developers should prefer to use libraries when possible, the rest of this chapter introduces how to proceed when developers need to write custom GPU code in Python. This chapter covers writing and running custom Python code on the GPU in the same fashion as [Section 2.1](intro-to-cuda-cpp.html#intro-applications-cpp) does for C++, starting with how to specify a GPU kernel and then how to use the GPU-accelerated `ndarray` provided by cuPy to allocate memory on the GPU and provide communication between the CPU and GPU.

### 2.2.1.3. Getting Setup

In general, most of the CUDA Python ecosystem components are available on PyPi and can be installed using `pip` commands or any popular package manager for Python. All packages require that an up-to-date NVIDIA Driver is installed on the system. The CUDA Toolkit is generally not required to write or run applications in CUDA Python.

See [CUDA Python on the NVIDIA Developer Zone](https://developer.nvidia.com/how-to-cuda-python) for information about installing and configuring CUDA Python for different platforms.

### 2.2.1.4. Running CUDA Python Applications

CUDA Python applications, whether using CUDA-accelerated libraries or having user-written GPU code, are run in the same way as conventional Python applications. In this section, examples will always be run from a command line by invoking `python3` as shown below to execute a program called `cuda-python-app.py`.


    $ python3 cuda-python-app.py


## 2.2.2. SIMT Kernels in Python

As mentioned in the introduction to the [CUDA Programming Model](../01-introduction/programming-model.html#programming-model), functions which execute on the GPU which can be invoked from the host are called kernels. CUDA provides two different models: [Single Instruction Multiple Thread (SIMT)](../01-introduction/programming-model.html#programming-model-warps-simt), and [CUDA tile](../01-introduction/programming-model.html#programming-model-tile). SIMT kernels are written to be run by many parallel threads simultaneously. This notion is the same in CUDA Python and CUDA C++. This chapter introduces CUDA Python using SIMT kernels.

### 2.2.2.1. Specifying Kernels

Before specifying kernels in CUDA Python, the package `numba.cuda` must be imported. This is commonly done as shown below.


    from numba import cuda


This imports the `numba.cuda` package and allows us to use the components of the `cuda` namespace provided by that package.

To specify a function as a kernel in CUDA Python, place the decorator `@cuda.jit` on the line above the function definition as shown below.


    from numba import cuda

    @cuda.jit
    def function(input_array, output_array):
        ...


This will cause the kernel to be JIT compiled for the active GPU the first time it is launched. The default CUDA device is used when no other GPU is specified, as is the case for the examples shown in this section.

### 2.2.2.2. Launching Kernels

The number of threads that will execute a kernel are specified as part of the kernel launch. This is called the execution configuration. Each invocation of a kernel can have a unique execution configuration, such as a different block size or number of thread blocks.

#### 2.2.2.2.1. Kernel Launch

To launch a kernel, the execution configuration is placed in square braces `[ ]` after the kernel name but before the function arguments. The order of arguments is the same as in the triple chevron notation in C++ introduced in [Section 2.1.2.2.1](intro-to-cuda-cpp.html#intro-cpp-launching-kernels-triple-chevron), specifically:


    kernel_name[number_of_thread_blocks, threads_per_block](arguments, ...)


The code snippet below shows how a kernel is defined and then invoked in a Python source file.


    from numba import cuda

    @cuda.jit
    def my_kernel(input, output):
        ...

    ## launch the kernel
    my_kernel[num_thread_blocks, threads_per_block](in_array, out_array)


There is a limit to the number of threads per block, since all threads of a block reside on the same streaming multiprocessor (SM) and must share the resources of the SM. On current GPUs, a thread block may contain up to 1024 threads. If resources allow, more than one thread block can be scheduled on an SM simultaneously.

#### 2.2.2.2.2. Multi-Dimension Grids and Thread Blocks

Thread blocks and the grid of thread blocks can be 1, 2, or 3-dimensional in CUDA. When the grid or thread block is one dimensional, an integer can be used when specifying the execution configuration of a kernel launch. When the thread block or grid is 2 or 3-dimensional, a two or three dimensional tuple is used as shown below for a 2D grid and thread block launch, where `gridX` and `gridY` are the x and y dimensions of the grid, and `blockX` and `blockY` are the x and y dimensions of each thread block within the grid.


    from numba import cuda

    @cuda.jit
    def function(input, output):
        ...

    ## launch the kernel
    function[(gridX, gridY), (blockX, blockY)](in_array, out_array)


### 2.2.2.3. Thread and Grid Index Intrinsics

[Section 1.2.2.1](../01-introduction/programming-model.html#programming-model-threads-grids) introduced threads and grids, and [Section 2.2.2.2](#intro-cuda-python-launching-kernels) showed how to specify the grid and thread block size for a kernel launch. Within a kernel, each thread can access the parameters of the execution configuration as well as the thread’s index and thread block index within the grid.

The following variables can be accessed from within a kernel function to determine a thread’s identity:

  * `cuda.threadIdx.[xyz]` gives the index of a thread within its thread block. Each thread in a thread block will have a different index.

  * `cuda.blockDim.[xyz]` gives the dimensions of the thread block, which was specified in the execution configuration of the kernel launch.

  * `cuda.blockIdx.[xyz]` gives the index of a thread block within the grid. Each thread block will have a different index.

  * `cuda.gridDim.[xyz]` gives the dimensions of the grid, which was specified in the execution configuration when the kernel was launched.


Each of these variables is a 3-component vector with a `.x`, `.y`, and `.z` member. If a dimension is not specified in the execution configuration at kernel launch, it defaults to a value of 1 for dimensions and 0 for indices.

`cuda.threadIdx` and `cuda.blockIdx` are zero indexed. That is, `cuda.threadIdx.x` will take on values from 0 up to and including `cuda.blockDim.x - 1`. `.y` and `.z` operate the same in their respective dimensions.

The code for a simple vector addition kernel, which adds two vectors together element-wise, is shown below. This function takes three arrays, `A`, `B`, and `C` to implement an element-wise vector addition `C = A + B`


    # C = A + B vector addition
    @cuda.jit
    def vecadd(A, B, C):
        idx = cuda.threadIdx.x + cuda.blockIdx.x * cuda.blockDim.x
        C[idx] = A[idx] + B[idx]


The kernel begins by calculating the unique index of the thread in the grid. This kernel assumes it is being launched with 1-dimensional thread blocks in a 1-dimensional grid. The `idx` variable is a unique index from 0 to `N-1`, where N is the total number of threads in the grid, that is, `N = cuda.gridDim.x * cuda.blockDim.x`.

The pattern for computing the thread index as shown in the code block above is so common, Numba provides a shorthand syntax for this operation: `cuda.grid(n)`, where `n` is the number of dimensions. In the example above, the line


    idx = cuda.threadIdx.x + cuda.blockIdx.x * cuda.blockDim.x


can be replaced by the much simpler


    idx = cuda.grid(1)


One notable aspect of this kernel is that it does not check for out-of-bounds access to `A`, `B`, or `C`. In this chapter, we assume that these are `ndarrays` created by cuPy, which will be introduced shortly in [Section 2.2.3.3](#intro-cuda-python-ndarray). When using cuPy `ndarrays`, bounds checking is implicitly implemented by the array type.

## 2.2.3. Memory in GPU computing

Note

Python packages like cuPy and others perform GPU memory management by directly using CUDA C++ APIs, such as those covered in [Section 2.1.3.2](intro-to-cuda-cpp.html#intro-cpp-explicit-memory-management). Multiple Python packages provide wrappers and utilities for controlling GPU memory allocation. In this guide, only cuPy will be covered. The concepts are similar for most packages, and most behave in similar fashion to their C++ counterparts except where noted.

As introduced in [Section 1.2.3](../01-introduction/programming-model.html#programming-model-memory), the GPU has an attached DRAM. Data arrays which will be used in kernels generally need to be in the GPU’s DRAM before they are accessed from the kernel. In Python, controlling the location of data in memory, i.e. moving data between the CPU and GPU, is the responsibility of the programmer. This is the same situation as explicit memory management in C++, as introduced in [Section 2.1.3.2](intro-to-cuda-cpp.html#intro-cpp-explicit-memory-management).

### 2.2.3.1. Instantiating arrays on the GPU

CuPy provides functions to create `ndarray` objects of a specified type and dimension on the GPU and also to copy data between the CPU and GPU. Many of the functions in cuPy have similar function signatures to functions for creating `ndarrays` in Numpy. The following shows a few examples of how to create and fill arrays in GPU memory using CuPy.


    import cupy as cp
    import numpy as np

    ## create a matrix of zeros on the GPU
    ## when a datatype is not specified, float32 is used by default
    A_device = cp.zeros((1024, 1024))

    ## create an array of 2^20 random doubles on the GPU
    B_device = cp.rand.random((2**20), dtype=np.double)

    ## create an array of zeroes with the same shape and datatype as an existing array
    C_device = cp.zeros_like(A)


### 2.2.3.2. Copying Arrays between the Host and GPU memory

CuPy can also be used to copy data from Numpy `ndarrays` which reside in CPU memory to CuPy arrays which reside in GPU memory.


    import cupy as cp
    import numpy as np

    ## Create an array in host memory
    A_host = np.zeros((1024, 1024))
    ## Copy the array to the GPU
    A_device = cp.array(A_host)

    ## Create an array in GPU memory
    B_device = cp.rand.random((1024, 1024))
    ## copy the array to host memory
    B_host = cp.asnumpy(B_device)


### 2.2.3.3. The ndarray object type

The `ndarray` objects shown in the previous section exist either in the host memory or in the GPU memory, but not both. Passing arrays which reside on the host as arguments to kernels will result in an error. Passing arrays which reside in GPU memory to normal Python functions, i.e. not kernels, will also result in an error. CuPy does not implicitly perform the copies between CPU and GPU because they can be expensive and excessive data copying can hurt performance. As a result, CuPy requires the programmer to be intentional about when data is copied between CPU and GPU.

One advantage of using the `ndarray` type in GPU kernels is that the array carries with it the extents of its dimensions. As shown in [Section 2.2.2.3](#intro-cuda-python-thread-indexing), boundary checking is done automatically and the kernel code does not need to check for out-of-bounds access when the total number of threads needed is slightly less than the total size of the execution block or grid.

## 2.2.4. Synchronizing the CPU and the GPU

Like C++, kernel launches in CUDA Python are asynchronous with respect to the host thread. That is, the host code proceeds executing on the CPU after a kernel launch without any guarantee that the kernel has completed or even started executing. In order to guarantee that GPU kernels have completed executing, the host thread must perform some form of synchronization with the GPU.

The simplest form of synchronization is to synchronize the entire GPU. This device-wide synchronization is an operation provided by the CUDA driver and is exposed to Python by both cuPy and numba.cuda as the method `synchronize()`.


    import cupy as cp
    from numba import cuda

    ..

    ## Wait on host thread for all pending GPU work to complete
    ## this uses the interface provided by cupy
    cp.synchronize()

    ## Wait on host thread for all pending GPU work to complete
    ## this uses the interface provided by numba.cuda
    cuda.synchronize()


Device-wide synchronization waits on the host thread until all previously issued work on the GPU has completed. Finer-grain synchronization is available using CUDA streams as described in [Section 2.5](asynchronous-execution.html#asynchronous-execution). In Python, when using streams, recommended practice is to use cuda.core to create CUDA streams and perform synchronization only with specific streams as needed.

## 2.2.5. Putting it All Together

The ubiquitous first GPU kernel to perform parallel vector addition is shown in its Python form in the source listing below.


    import numpy as np
    from numba import cuda
    import cupy as cp


    ## Defines a CUDA kernel to perform C = A + B vector addition
    @cuda.jit
    def vecadd(A, B, C):
        work_index = cuda.grid(1)
        C[work_index] = A[work_index] + B[work_index]


    # note that vector size is not a power of 2 nor a multiple of the block_size defined below
    vector_size = 2**24 + 11

    device = cp.cuda.Device()
    ## Create device arrays of uniform random float32 values as input, and an array of zeros
    ## as the result vector
    a = cp.random.uniform(-1, 1, vector_size)
    b = cp.random.uniform(-1, 1, vector_size)
    c = cp.zeros_like(a)

    block_size = 256
    grid_size = int(np.ceil(vector_size/block_size))
    vecadd[grid_size, block_size](a, b, c)

    ## synchronize the CPU thread and the GPU to ensure that the kernel has completed
    ## this is included to illustrate good practices, even though the copy below would implicitly wait for
    ## the kernel to complete
    device.synchronize()

    ## Copy all 3 arrays to the CPU as ndarrays
    a_np = cp.asnumpy(a)
    b_np = cp.asnumpy(b)
    c_np = cp.asnumpy(c)

    ## Perform the copy on the CPU to verify the answer
    expected = a_np + b_np

    ## Test that the answer is correct, within floating point epsilon
    np.testing.assert_array_almost_equal(c_np, expected)

    ## The assert will print diagnostics and abort
    ## so this only prints if the assertion passes
    print("Test succeeded")


In this example, the `A` and `B` input arrays are created and initialized to random values on the GPU by CuPy. They are copied to the CPU at the end of the code only so that the CPU can perform the vector addition as well and verify that the CPU and GPU answers match.

## 2.2.6. Error Checking in CUDA Python

Any operation that affects the GPU, from memory allocation and copies to kernel launches can potentially cause an error condition to arise. As illustrated in [Section 2.1.7](intro-to-cuda-cpp.html#intro-cpp-error-checking) for C++, making sure that errors have not occurred in the course of interacting with the GPU is best practice.

In Python, CUDA errors throw exceptions which will terminate the program if they are not caught. The exceptions can be caught using normal Python syntax. The example below shows the same vector add as above, but with an error intentionally added: the number of threads per block, 2048, is larger than any current GPU can run. This will cause the kernel to fail to launch, and throw an exception, which this code will catch.


    import numpy as np
    from numba import cuda
    import cupy as cp


    ## Defines a CUDA kernel to perform C = A + B vector addition
    @cuda.jit
    def vecadd(A, B, C):
        work_index = cuda.grid(1)
        C[work_index] = A[work_index] + B[work_index]


    try:
        vector_size = 2**24 + 11

        device = cp.cuda.Device()
        a = cp.random.uniform(-1, 1, vector_size)
        b = cp.random.uniform(-1, 1, vector_size)
        c = cp.zeros_like(a)

        ## this block size is too large for any current GPUs
        block_size = 2048
        grid_size = int(np.ceil(vector_size/block_size))
        # Error: launching kernel with invalid block size
        vecadd[grid_size, block_size](a, b, c)

        device.synchronize()
        print("Test did not encounter any errors")

    except Exception as e:
        print(f"Exception occurred: {e}")


Running this code causes the error to be caught and displayed as shown below:


    $ python3 vecadd_error.py
    Exception occurred: CUDA_ERROR_INVALID_VALUE: This indicates that one or more of the parameters passed to the API call is not within an acceptable range of values.


The program exits normally having caught the exception. If this code was run without the `try:` and `except:`, it would exit abnormally and dump a traceback to the console which should show the same error.