# PTX ISA Search Guide

The full PTX ISA snapshot is split into focused Markdown pages under ptx-docs/. Read MANIFEST.md for the verified version and retrieval date.

## Start from the index

Use ptx-docs/INDEX.md to browse the document hierarchy. For symbol lookup, use ripgrep first:

    rg -l 'mbarrier\.init' ptx-docs/9-instruction-set
    rg -l 'wgmma\.mma_async' ptx-docs/9-instruction-set
    rg -l 'tcgen05\.mma' ptx-docs/9-instruction-set
    rg -l 'fabric\.try_get|counted::bytes' ptx-docs/9-instruction-set

Then read the smallest matching page:

    rg -n -C 16 -- 'Syntax|Semantics|PTX ISA Notes|Target ISA Notes' \
      ptx-docs/9-instruction-set/FOCUSED_PAGE.md

The split intentionally keeps parent pages short. Detailed instruction syntax and architecture notes remain on the focused instruction page.

## Route by topic

| Topic | Directory |
|---|---|
| Machine and thread model | ptx-docs/2-programming-model/, ptx-docs/3-ptx-machine-model/ |
| Types, state spaces, variables, tensors | ptx-docs/5-state-spaces-types-and-variables/ |
| Operands and conversions | ptx-docs/6-instruction-operands/ |
| Memory ordering and scopes | ptx-docs/8-memory-consistency-model/ |
| Instructions | ptx-docs/9-instruction-set/ |
| Special registers | ptx-docs/10-special-registers/ |
| Directives and targets | ptx-docs/11-directives/ |
| Pragmas | ptx-docs/12-descriptions-ofpragmastrings/ |
| Version history | ptx-docs/13-release-notes/ |

## Instruction checklist

Before using an instruction, verify:

- exact operand grammar, types, shapes, and modifiers;
- execution granularity, such as thread, warp, warpgroup, or CTA;
- memory and proxy semantics;
- required synchronization or completion sequence;
- PTX ISA introduction version;
- target ISA requirements;
- restrictions marked undefined, deprecated, or architecture-specific.

Keep PTX ISA version, virtual target, toolkit support, and physical GPU capability separate. A target listed by the ISA does not prove that an older ptxas accepts it.

## Architecture-oriented searches

    rg -n -i 'sm_80|sm_86' ptx-docs/9-instruction-set
    rg -n -i 'sm_90|sm_90a' ptx-docs/9-instruction-set
    rg -n -i 'sm_100|sm_103' ptx-docs/9-instruction-set
    rg -n -i 'sm_110|family-specific|architecture-specific' ptx-docs

For Rubin or other preview architecture claims, use the local PTX snapshot for documented ISA facts, then verify release status and hardware mapping against current NVIDIA documentation.

## Inline PTX

The PTX ISA defines instruction semantics, not CUDA C++ inline-assembly constraints. Check both:

- PTX instruction syntax and types in ptx-docs/;
- inline PTX operand constraints and compiler behavior in the CUDA Programming Guide and current compiler documentation.

Do not copy a mnemonic into inline assembly without checking register width, address space, predication, clobbers, and target support.
