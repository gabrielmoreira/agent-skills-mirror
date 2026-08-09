# CUDA Skill Documentation Manifest

Checked and retrieved from NVIDIA documentation on 2026-07-22.

| Document set | Snapshot | Markdown inventory | Official source |
|---|---:|---:|---|
| PTX ISA | 9.3 | 488 sections + index | [Parallel Thread Execution ISA](https://docs.nvidia.com/cuda/parallel-thread-execution/) |
| CUDA Runtime API | 13.3.1 | 38 modules + 67 structures + index | [CUDA Runtime API](https://docs.nvidia.com/cuda/cuda-runtime-api/) |
| CUDA Driver API | 13.3.1 | 50 modules + 84 structures + index | [CUDA Driver API](https://docs.nvidia.com/cuda/cuda-driver-api/) |
| CUDA Programming Guide | 13.3 | 43 pages + index | [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/) |
| CUDA C++ Best Practices Guide | Current CUDA 13.3 documentation set | 72 sections + index | [CUDA C++ Best Practices Guide](https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/) |
| Nsight Compute | 2026.2.1 | 8 documents + index | [Nsight Compute Documentation](https://docs.nvidia.com/nsight-compute/) |
| Nsight Systems | 2026.3 | 4 documents + index | [Nsight Systems Documentation](https://docs.nvidia.com/nsight-systems/) |

The CUDA snapshots track NVIDIA's current stable documentation set. CUDA developer-preview documentation is not mixed into these references.

"Latest" means latest official release verified on the checked date. For release status, preview architectures, supported targets, CLI options, metrics, and report formats, verify the current NVIDIA page before making a time-sensitive claim.

## Update policy

- Scrape into a fresh staging root.
- Treat `--force` as overwrite-matching-files, not clean-output.
- Keep raw API cache for inspection and retry.
- Stop with a nonzero exit code when discovery or page fetching fails.
- Compare staged and live file sets before merging.
- Do not remove renamed or obsolete files without explicit user approval.
