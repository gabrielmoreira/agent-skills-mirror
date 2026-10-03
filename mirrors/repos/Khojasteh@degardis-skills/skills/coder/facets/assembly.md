---
title: Assembly
category: Language
x-claim-provenance:
- claim: The Windows x64 calling convention passes the first four integer arguments in RCX, RDX, R8, and R9, requires the caller to allocate space for four register parameters even when the callee takes fewer, treats RBX, RBP, RDI, RSI, RSP, R12-R15, and XMM6-XMM15 as nonvolatile, keeps the stack pointer 16-byte aligned outside prologs, epilogs, and leaf functions, and describes how to unwind non-leaf functions through static pdata and xdata, which restricts prolog and epilog forms.
  source: https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention
  scope: Windows x64 ABI as documented for MSVC; page dated 2025-03-19.
- claim: The System V x86-64 ABI passes INTEGER-class arguments in RDI, RSI, RDX, RCX, R8, and R9, requires the stack to be 16-byte aligned immediately before a call instruction, reserves a 128-byte red zone beyond RSP that signal or interrupt handlers do not modify, and requires a called function to preserve RBP, RBX, and R12-R15.
  source: https://gitlab.com/x86-psABIs/x86-64-ABI/-/blob/master/x86-64-ABI/low-level-sys-info.tex
- claim: GCC does not parse the instructions in an asm statement; registers the code modifies beyond its outputs must be listed as clobbers, the "memory" clobber declares reads or writes of memory not named as operands, and the optimizers can discard an asm statement without volatile whose outputs are unused or move it out of a loop.
  source: https://gcc.gnu.org/onlinedocs/gcc/Extended-Asm.html
---

Instruction sequences are bound to a fixed architecture, instruction set and extensions, assembler syntax, object format, calling convention, privilege level, endianness, unwind model, and set of supported hosts, and one instruction set can carry incompatible conventions. On x86-64, the Windows ABI passes the first four integer arguments in `RCX`, `RDX`, `R8`, and `R9` and requires the caller to reserve shadow space for them, while the System V ABI passes the first six in `RDI`, `RSI`, `RDX`, `RCX`, `R8`, and `R9` and lets a function use a 128-byte red zone below the stack pointer. System V requires a called function to preserve `RBX`, `RBP`, and `R12`–`R15`, and Windows adds `RDI`, `RSI`, and `XMM6`–`XMM15` to that set, so a routine written for one convention silently breaks callers that follow the other. Directives and instructions exist only where the configured toolchain and target support them.

Caller- and callee-saved registers, flags, stack alignment, memory ownership, atomicity and ordering, fault behavior, constant-time requirements, symbol visibility, and portability guards are behavioral contracts. Both x86-64 ABIs require a 16-byte-aligned stack at calls, and Windows unwinds a non-leaf function through static data that describes its prolog, which is why prolog and epilog forms are restricted there. The required memory ordering follows from the shared-state protocol, and the architecture's documented atomic and barrier semantics decide what an instruction guarantees; instruction names do not.

Inline assembly adds a contract with the compiler. GCC does not parse the instructions in an `asm` statement and relies entirely on its declared operands and clobbers: a register the code changes without declaring it is assumed to be unchanged, the `"memory"` clobber is what tells the compiler that the statement touches memory not named in its operands, and an `asm` statement without `volatile` whose outputs are unused can be deleted or hoisted out of a loop. An intrinsic or higher-level implementation can serve portability and ownership better when it preserves the required instruction, ABI, timing, and portability contract.

Control flow, lifecycle, and ownership run through every register, flag, clobber, stack slot, address calculation, bound, alignment assumption, and exceptional exit across the binary boundary. The following are observable state as well:

- relocation and symbol records and section attributes
- unwind or CFI metadata
- inline-assembly constraints and linker scripts
- generated disassembly, feature detection, and foreign-function declarations

Behavioral evidence covers functional results plus registers, flags, stack alignment, clobbers, bounds, endianness, atomicity, unwind behavior, and invalid inputs at the supported ABI boundary. Runtime evidence comes from architecture-specific checks in controlled native or emulator environments, covering each supported feature and calling-convention variant, and algorithmic expectations are separate from exact encodings. Performance evidence comes from serialized counters or configured hardware profiling under controlled frequency and placement, and an optimization must preserve ABI, memory ordering, constant-time behavior, and unwind correctness.
