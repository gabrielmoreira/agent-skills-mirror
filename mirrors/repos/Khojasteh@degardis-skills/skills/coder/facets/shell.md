---
title: Shell
category: Language
description: POSIX-style shell scripts such as sh, Bash, or Zsh, whose pipelines carry text and exit statuses rather than PowerShell objects.
x-claim-provenance:
- claim: The -e setting is ignored when executing the compound list following while, until, if, or elif, a pipeline beginning with !, or any command of an AND-OR list other than the last.
  source: https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html
  scope: POSIX.1-2024.
- claim: Without pipefail a pipeline's exit status is that of its last command; with pipefail it is zero only if every command returned zero, and otherwise the status of the last command that returned a non-zero status.
  source: https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html
  scope: POSIX.1-2024.
- claim: POSIX.1-2017 defines a pipeline's exit status as that of its last command and specifies no pipefail option.
  source: https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html
  scope: POSIX.1-2017.
- claim: Field splitting is performed on the fields produced by parameter expansion, command substitution, and arithmetic expansion, pathname expansion follows unless set -f is in effect, and quote removal comes last; a single word becomes multiple fields or none only through field splitting, pathname expansion, or the special parameters @ and *.
  source: https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html
  scope: POSIX.1-2024.
---

Syntax and command-option availability depend on the exact interpreter or dialect, supported operating systems, utilities, locale, invocation mode, and job-control assumptions, and shell options, syntax, and utility flags exist only where the configured interpreters and platforms support them. Word, byte, record, and path boundaries are behavioral contracts, as are quoting, globbing, splitting, encoding, streams, exit statuses, pipeline status, traps, signals, temporary resources, and partial-failure behavior.

Expansions apply in order — parameters, command substitutions, arithmetic, field splitting, globbing, quote removal, and redirection. Only field splitting, globbing, and the special parameters `$@` and `$*` turn one word into several fields or none, so an unquoted expansion is where a value containing whitespace, newlines, glob characters, a leading hyphen, or nothing at all becomes a different argument list.

Failure handling is weaker than it looks. Without `pipefail`, a pipeline's status is its last command's, so an earlier failure disappears; with it, the status is that of the last command that failed, and `pipefail` entered POSIX only in its 2024 edition, so an older `sh` may lack it. `set -e` is ignored in the condition of `if`, `while`, `until`, and `elif`, in a pipeline negated with `!`, and in every command of an `&&` or `||` list except the last, so a function called from any of those places runs with errors unchecked. Lifecycle and ownership run through subshells, pipelines, background jobs, process substitution where supported, file-descriptor ownership, `set -e` context, `pipefail` where supported, command-not-found behavior, and the status actually returned. State-changing scripts need to be safely repeatable where the contract requires it.

Behavior is also affected indirectly by:

- sourced files, environment mutation, and aliases or functions
- traps, temporary files, and cleanup handlers
- current-directory assumptions and external-tool variants
- text parsers whose locale or delimiter is implicit

Runtime evidence depends on every supported interpreter and platform, with representative filenames, empty input, Unicode, partial reads, command failures, signals, interrupted pipelines, and concurrent invocations as the relevant edge conditions. Output, standard error, and exit status are separate observations, and quoting is established from the argument vectors that reach external commands rather than from the rendered command text. Repeatable state-changing flows are evidenced by running them repeatedly in an isolated representative environment and observing convergence, atomicity where promised, trap cleanup, signal forwarding, and preservation of the original failure status. A performance result names the interpreter and platform and times the whole representative pipeline, counting external commands, subshells, temporary files, and bytes moved. Where that evidence locates the cost, batching work into fewer invocations or filtering earlier are the characteristic remedies, and they must preserve exit status, quoting, signal, and cleanup behavior.
