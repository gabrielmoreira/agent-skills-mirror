# NVTX Instrumentation Guide

NVTX names application phases so Nsight Systems can relate CPU work, CUDA API calls, kernels, and memory operations to user-level intent.

## Basic ranges

Use paired push and pop calls in the same thread:

    #include <nvtx3/nvToolsExt.h>

    nvtxRangePushA("decode");
    run_decode();
    nvtxRangePop();

Use an instant mark for a point event:

    nvtxMarkA("weights-loaded");

Keep range names stable across runs so reports can be compared.

## Scope-safe C++ range

    class NvtxRange {
    public:
        explicit NvtxRange(const char* name) {
            nvtxRangePushA(name);
        }

        ~NvtxRange() {
            nvtxRangePop();
        }

        NvtxRange(const NvtxRange&) = delete;
        NvtxRange& operator=(const NvtxRange&) = delete;
    };

    void run_iteration() {
        NvtxRange range("iteration");
        launch_work();
    }

RAII prevents unbalanced ranges on early returns or exceptions.

## Domains and categories

Use domains when independent libraries may reuse the same range names:

    nvtxDomainHandle_t domain = nvtxDomainCreateA("inference");

    nvtxEventAttributes_t event = {};
    event.version = NVTX_VERSION;
    event.size = NVTX_EVENT_ATTRIB_STRUCT_SIZE;
    event.messageType = NVTX_MESSAGE_TYPE_ASCII;
    event.message.ascii = "attention";
    event.colorType = NVTX_COLOR_ARGB;
    event.color = 0xFF4C78A8;

    nvtxDomainRangePushEx(domain, &event);
    run_attention();
    nvtxDomainRangePop(domain);

    nvtxDomainDestroy(domain);

Choose colors as a visual aid, not as the only category encoding. Names and domains remain usable in CLI reports.

## Asynchronous work

An NVTX range measures the host interval between push and pop. CUDA kernels launched inside it can finish later.

Do not add cudaDeviceSynchronize solely to make a range appear to contain GPU time. That changes overlap and performance. Nsight Systems correlates CUDA API launches with GPU activity; use the timeline or GPU-aware report for device duration.

Add synchronization only when it is part of the real algorithm or an explicit measurement boundary.

## Iterations and dynamic names

Avoid creating millions of unique strings. Prefer a stable name plus a bounded category or payload when supported.

For warmup and steady state:

    nvtxRangePushA("warmup");
    run_warmup();
    nvtxRangePop();

    nvtxRangePushA("steady-state");
    run_benchmark();
    nvtxRangePop();

This makes capture-range selection and before/after comparison clearer.

## Conditional instrumentation

    #if defined(ENABLE_NVTX)
    #define NVTX_PUSH(name) nvtxRangePushA(name)
    #define NVTX_POP() nvtxRangePop()
    #else
    #define NVTX_PUSH(name) ((void)0)
    #define NVTX_POP() ((void)0)
    #endif

Integrate NVTX headers and any required platform linkage through the project's CUDA toolkit configuration. Do not assume one linker command works across every NVTX generation and platform.

## Nsight Systems workflow

    nsys profile --trace=cuda,nvtx +      -o report +      ./program

    nsys stats report.nsys-rep --report nvtx_sum
    nsys stats report.nsys-rep +      --report nvtx_sum +      --report cuda_gpu_kern_sum

For range-controlled capture, verify the active CLI syntax:

    nsys profile --help
    nsys profile --capture-range=nvtx +      --trace=cuda,nvtx +      -o report +      ./program

Range capture normally needs a matching range name or domain configuration. Read the current Nsight Systems User Guide before scripting it.

## Naming rules

- Name application phases, not individual source lines.
- Use a consistent hierarchy such as request, prefill, decode, attention.
- Keep push and pop balanced on each thread.
- Avoid high-cardinality dynamic names in hot loops.
- Instrument boundaries that remain meaningful after kernels are fused or reordered.
- Preserve instrumentation across before and after runs.

Use nsys-guide.md for collection and export details. Search nsys-docs/UserGuide.md for the current NVTX capture and trace options.
