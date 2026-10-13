# Claude subscription bridge: turns across Claude Code runs

A Claude subscription's requests are answered by the local `claude` binary
(`internal/gateway/claude_subscription.go`, `serveClaudeSubscription`). This
page covers how a conversation's turns find the Claude Code process, or the
saved session, that had its last turn, and what a run leaves on disk. Tool
calls within a turn (`match`, `continueWith`) are only touched on where they
meet it.

## Which Claude Code runs

`claudeBinary` (and the sign-in's `claudeExecutable`) take
`claudecode.Find`: the machine's own `claude` (`proc.FindTool`), else the
one `magpie claude-code install` downloaded into
`<cache>/claude-code/<version>/` (`internal/claudecode`), else, on Windows,
one in WSL. The download is Anthropic's native build from
`downloads.claude.ai/claude-code-releases`, the "latest" channel, as
`claude.ai/install.sh` takes it: the release's `manifest.json` gives the
platform's SHA-256 and size, and a build that doesn't match both is not
kept. It is only made when the user asks (`magpie claude-code install`, or
yes to `magpie accounts add claude`'s offer on a machine without one), for
a server or a container (Jorben on Discord). It is not on PATH and stands
in for no agent. It doesn't update itself (the bridge sets
`DISABLE_AUTOUPDATER`); installing again takes the newest and removes the
older one.

A run is started with `--dangerously-skip-permissions` (`claudeCLIArgs`):
its only tools are magpie's MCP ones, answered by the client, and
Anthropic's web search. Claude Code run as root refuses that flag ("cannot
be used with root/sudo privileges") unless `IS_SANDBOX` is `1` or
`CLAUDE_CODE_BUBBLEWRAP` is set, so a run as root, magpie's own euid 0 or
a WSL distro whose default user is root (the probe's `uid`,
`wslrun.Tool.Root`), is given `IS_SANDBOX=1` (`claudeCLI.asRoot`;
FrierenF on Discord). A run as anyone else has its env as before. Only the
bridge's run gets it; the warm-up and `/usage` runs don't skip
permissions.

The run's MCP server is magpie itself (`magpie claude-mcp-helper`,
`internal/claudebridge`), which hands each tool call back to the gateway
at `POST /_magpie/claude-mcp/<token>` (`mcpCall`), where the call is
registered in `b.calls` for the turn with its results to find. The token
is `randomToken` (24 bytes from `crypto/rand`), one per run. The callback
URL is written to `callback` in the run's own temp folder (0600) and the
helper is given that file's path, so the token is never on Claude Code's
command line. The helper calls the address the gateway listens on
(`callbackBaseURL`: `MAGPIE_ADDR`, `0.0.0.0`/`::` as `127.0.0.1`), which,
pinned to one interface's address, isn't loopback, and it sends no
gateway key. `lanGuard` therefore lets in exactly that path, by POST, with
the token of a run now live (`ownCallback`: `addCallback` when the run is
registered, `dropCallback` in `removeRun`, compared in constant time).
Every other request, and this path with a wrong, spent or encoded token,
is judged as any other. Without it the call was refused 401, never
reached the run, and every turn with tool results found no run waiting and
started a new Claude Code told the whole conversation (#1546).

## Why turns go on in one run

A run started anew is told the whole conversation in one user message
(`renderClaudePrompt`), a prefix the prompt cache has never seen, so the
conversation is written to the cache again and its images are sent again.
That message holds the history in blocks of `historyChunk` messages, and
magpie's one mark (Claude Code keeps three of Anthropic's four) is on the
last whole block, else on the caller's instructions: a later run started
anew for the same conversation within the hour reads the history up to an
earlier run's mark, found within Anthropic's 20-block lookback. A
conversation with no history (no reply that calls no tool, as a sub-agent's
loop of tool calls that Claude Code's AgentSummary asks a summary of) has
its every message but the last chunked instead. The turn to answer after a
history is not chunked, and image blocks count toward the lookback.
A turn that goes on in the run that had the last one is told only the
messages since (`renderClaudeTurn`), and Anthropic reads the rest from the
cache.

## Runtime path for a new turn

`serveClaudeSubscription`'s `start` tries, in order:

1. `subscriptionBridge.resume`: an idle run waiting at the conversation the
   request goes on from (`b.idle`). It is written the turn's messages on its
   stdin, as a user message with a uuid it is rewound to if the client gives
   up on the turn (`letGo`).
2. `subscriptionBridge.unshelve`: the saved session of a run let go past
   `idleMost` (`b.shelf`, at most `shelfMost`), which a new Claude Code
   starts from with `--resume`, told the turn's messages alone. It is
   sent `initialize` first, which Claude Code answers only once it has
   loaded the session; one that can't load it exits 1 ("No conversation
   found with session ID") without answering. `start` then lets the
   session go and goes on to step 3 in the same request, logged "Claude
   Code could not go on from the conversation's saved session". Before,
   the turn got 502 "Claude Code ended" with the safety context set, and
   an empty reply without it.
3. `retire`, then a new run told the whole conversation. When it has
   replies in it, the turns already answered are wrapped in
   `<conversation_history>`, with a note that the images and files in them
   were sent with those messages, and the turn to answer (from the message
   after the last reply that calls no tool, `historyEnd`) in
   `<current_turn>` (#1365). Told as one stretch of Human:/Assistant: text,
   earlier images read as just sent. A first turn, or messages with no
   reply among them, are told as before. `start` logs "a new Claude Code
   is told the whole conversation" with the message and image counts.

A Claude Code that ends before it answers a control request
(`cliControl`: `initialize`, the safety context) is reported with its
exit status and the end of its stderr (`endedBefore`), as one that ends
before it reads its input is (`whyEnded`). The tool-results path and
`resume` already start a new run when the one they found has ended.

## A side question after a reply (#1638)

After each turn Claude Code 2.1.290 asks its prompt suggestion: the
conversation so far, with the turn's system prompt, tools and thinking so
it shares the cache, and one more user message, "[SUGGESTION MODE: …",
with no system message after it. Its request goes on from the turn's
reply like a next turn, so `resume` gives it the conversation's run, and
the run waited at the suggestion's reply. The user's real next turn then
found no run and was told the whole conversation in a new Claude Code
(the reporter's 41 messages, 88k tokens written to the cache, minutes
after the last reply, with nothing in the log).

`ended` now keeps, beside the run's new key, the key it went on from
(`behindKey`) and the uuid of the turn that took it there (`behindTurn`).
A turn that finds no run under its own key takes one whose `behindKey` is
its key, rewinds it to `behindTurn` (as `letGo` does) and tells it only
the turn's messages ("taken back from the side question it answered
since"). The run is marked `rewound`, so it isn't shelved. A run that
can't be rewound is let go and the turn told whole to a new run, as
before. Tried with the real 2.1.290 client in `-p --prompt-suggestions`
and the real 2.1.290 as the run, against a local mock of Anthropic: one
run for the whole session, and the turn after each suggestion went on
from the reply before it. Other side requests that go on from the
conversation (extract_memories, away_summary, /btw) take the same path;
they weren't tried.

A turn after a reply that starts a new run logs why none waited
(`whyNoRun`, "claude: no run waits for this turn: …"): its run went on
with a turn this one doesn't follow, waits under another key (the model,
settings, system prompt or tools differ), waits at an earlier turn, is
busy with another request, ended (how long ago, and why: `endWhy`, set by
`abortFor`, kept in `b.lost` by conversation), or no run here has had the
conversation. Tool results that find no run waiting add what became of
the run that made the calls ("the run that made the calls ended …",
`whyCallsLost`, from `b.lostCalls`, which `removeRun` fills with the calls
the run waited on and the results it was last handed).

## A turn the client gives up on (`letGo`, #780, #1365)

When the client goes away mid-reply, a run resumed for the turn is told to
rewind (`rewind_conversation`) to the turn's user message, and waits at the
conversation before the turn (`backKey`). The turn's id lasts until its
reply ends without calling a tool: `ended` keeps `turnUUID` and `backKey`
over a reply that calls tools, so a client that goes away while the run
answers its tool results also has the whole turn taken back, its tool
rounds with it. Its next request (the same results sent again, or the next
turn) then finds no run waiting on the calls ("tool results no run
waiting"), is resumed in that run at `backKey` and told the turn since its
user message (logged "a turn taken back goes on in its run"). Before, the
turn's id was dropped with the reply that called the tool, the run was
ended, and that request was told the whole conversation in a new run.
Claude Code 2.1.295 rewinds past a tool round mid-reply (tried against a
local mock of Anthropic). A run started anew for the turn has nothing to
rewind to and is still ended; so is one with a call still in the client's
hands (`pending`). Rewinding it to its first message would leave nothing,
and its results were already handed over its MCP calls, so the results
sent again go to a new run told the whole conversation (#1638's first
case: a 499, then "tool results no run waiting" and 17 messages told).
Keeping its cache would mean taking it back to Claude Code's own
tool_result message and telling the results again as text, which wasn't
done: the reporter's requests aren't known, and a fork that took the
lead's calls (`claimResume`) looks the same from here. The log now says
which run ended and why.

### One key per waiting run

A run waits under one key (`keepIdle`, the only writer of `b.idle`);
kept again, a run leaves the key it waited at, unless another run now
waits there. Which order of calls kept one run twice in the reporter's
gateway isn't known: `ended` and `letGo` of one request exclude each
other (`serveSubscription`'s ended callback runs only when `gone()`
stopped the `AfterFunc` that calls `letGo`), so it isn't those two of one
request. `keepIdle` holds the rule whichever caller it was (#1596). Past `idleMost`, the
eviction loop takes out the key it found as oldest, not the run's own.
Before (X, Sma1lboy: magpie at 158 GB after two days of omp agents), one
run under two keys was the oldest on every pass, the pass took out only
its newer key, and the loop never ended: it held `b.mu`, stopping every
Claude subscription request, and grew its list of runs to let go without
bound. `claude_idle_test.go` (`TestClaudeIdleEvictionEnds` runs the loop
in a child process, which on the old code fails on what the loop
allocates, not on a deadline).

`keepIdle` refuses a run that has ended, and its callers then leave the
run's timer alone (#1667). A resumed turn's 30-minute timer can end a run
(`abort` → `finish` → `removeRun`) while its reply is going out, and the
reply's last event, already in the segment, still reaches the client
whole, so `ended` is told it went well. Before, the ended run was kept,
held one of `idleMost` places until pushed out, and its re-armed timer
found it closed and never took it out. `finish` sets `closed` before
`removeRun` takes `b.mu`, and `keepIdle` reads it under `b.mu`, so a run
is either refused or kept and then taken out by `removeRun`.
`TestClaudeRunEndedMidReplyIsNotKeptIdle` fires the timer before `ended`.

## Finding the run: keys

- `nextTurn` splits a request at its last reply that calls no tool: the
  conversation up to it, and the messages since (with any calls and results
  the client made itself after it).
- `ended` keeps a run whose reply was whole under
  `turnKey(owner, req, messages + reply)`: the account, model, whether an
  effort was asked, thinking off, tool choice, system prompt, the tools, web
  search, schema, and the messages as `hashMessages` reads them. The
  system prompt is taken without the client Claude Code's
  `x-anthropic-billing-header` line (`withoutBillingHeader`), which the run
  is never told and whose fields (`cch`, `cc_prompt_id`, `cc_prev_req`…)
  change every turn; with it in, no next turn found its run (#1638). The
  exact match is that key, from `nextTurn`'s split of the next request.
- It also keeps a `looseTurn`: the same settings without the tools, the
  message count, the conversation before the last turn (hashed; its system
  prompt also without the billing line), and the
  last turn's messages one by one (`messageWords`), the reply last. Shelving
  copies it, with the tool names the run's agent had, to the
  `savedSession`.

### A conversation the client rewrote (#912)

Some clients send a turn's conversation back changed. Alma takes the
`[Context: …]` block it gave the latest user message out once the turn is
over, and its `<alma_notification>` block out of the end of the reply, and
picks the tools for each turn. When the exact key misses, `rewritten`
compares the request's `looseTurn` with every idle run's and saved
session's. The request matches one when all of these hold:

- the same owner, settings and conversation before the last turn
  (`looseTurn.key`);
- the last turn has the same messages, roles, tool calls and results, and
  only these changed (`looseTurn.rewrote`):
  - a user message had one part taken out (`cutFrom`), not all of it;
  - the reply is a non-empty start of what the run said.

It is taken only when exactly one run or saved session matches. Two that
could be it are two conversations alike as far as their words go, and a
run handed the other one would answer from what that one was told.

An idle run is taken only when its agent was told every tool offered now
(`offers`). Claude Code is not told of new tools at a turn's start, only
with tool results. A saved session is taken only when the tools offered now
include every one its agent had (`toolsCover`). It is resumed with the new
list, and its earlier calls name no tool that is gone.

The run goes on with the conversation as it told it. Its Claude Code still
holds the context block and the notification. The client's next turn
brings its own context.

### Images the client took out (#1382)

Hana replaces each image before the last reply with a line of text
(`[图片已省略：…]`) in the tool result or user message that held it. Over
Chat Completions, pi-ai sent a tool's images in a user message after the
results ("Attached image(s) from tool result:" and the images); that
message is gone, and each result's text has the line added to its end. So
the step after one that read an image missed the run both ways: its tool
results failed `follows`, and its next turn failed `turnKey` and
`looseTurn.rewrote` (the message count changed).

`lostMedia` (`claude_lost_media.go`) tells this rewrite by its shape, not
by Hana's words. It compares the conversation the run had (kept as each
part's hash, `heardRuns`) with the request's, a role's messages in a row
at a time, and takes it when images or files were taken out and nothing
else changed:

- each image or file is still there, gone, or has text in its place;
- a tool result has text added to its end only when it carried images, or
  the images after the results went;
- the text before those images goes with them only when a result before
  it had text added;
- at least one image or file was taken out.

`follows` checks it when the hash misses (`toldRuns`, logged "tool results
go on in their run, the images before them taken out by the client"), and
`looseTurn.rewrote` when `cut` doesn't match; the looseTurn key no longer
has the message count, which `cut` compares itself. The run's Claude Code
still holds the images; it is told only what came since.

A client that drops the images' message without adding text to a result
goes on only when that message held images alone, no text. A tool result of an image alone (pi-ai's "(see attached image)")
whose text is replaced by the line is not this shape, and starts anew.

## Files a run leaves

- Its session: `<config>/projects/<work project>/<session>.jsonl`, for
  `--resume` (`claudeSessions`). It is removed when the run ends unless
  shelved, and when a saved session is discarded (`removeSession`).
  `sweepSessions` removes those a stopped gateway left, once older than
  `idleLongest`.
- Claude Code's temp files for the session, the images it was given:
  `<CLAUDE_CODE_TMPDIR or /tmp>/claude-<uid>/<work project>/<session>`
  (`claudeTempDir`, not on Windows). They are removed with the session
  (`removeSession`). The sweep removes those whose session file is gone and
  in which nothing changed for `tempLongest` (a day). The folder is
  the work folder's for every account, and another account's session files
  are in its own config folder.

A run started anew still sends every image in the conversation. Replacing
earlier images with a placeholder would change what the model sees, and
magpie doesn't do it.

## Tool results another request answers first

A request with tool results finds the run waiting on those calls (`match`)
and claims it (`claimResume`) until the reply it is resumed for ends. More
than one request can carry results for the same calls: Claude Code's fork
sub-agents each start from their lead's conversation as it stands, its
reply's calls answered with the placeholder "Fork started — processing in
background" and the fork's directive after, and they come at once with the
lead's own next turn; a client may also send a turn again while the first
is still answered. The first to claim the run goes on in it. Each of the
others, and one whose run has ended, is a conversation of its own from
there and gets a run started anew (`answeredElsewhere` in the log). It is
never refused: Claude Code doesn't retry a 409, and the agent that sent it
stops (ylorn on Discord).

## The user's words beside tool results (#872, #1878)

A user message can hold tool results and, after them, text blocks of the
user's: Claude Code's AgentSummary asks for its sub-agent's progress label
that way ("Describe your most recent action in 3-5 words. Do not use
tools.", JinJieBeWater), a fork its directive, and an older Claude Code a
message sent while a tool ran (#872). The words are the user's, and both
ways a run is told them keep them apart from the tool's output:

- **A run told the messages as text** (`renderParts`, for a run started
  anew and for a resumed turn): a text or file part after a tool result in
  the same message closes the result, `[end of tool result id=…]`, and is
  marked `[user message]`. Before, it ran on after the tool's last line
  (`SOURCE_LAST_LINEDescribe your…`), and the model read it as tool output
  and went on with the task. A result followed by nothing, or by another
  result, is told as before.
- **Results that go on in their run** (`match`, `continueWith`): `match`
  no longer adds the words to the last result's text, which made them part
  of the MCP result. `saidWithResults` takes them, and `continueWith`
  writes them to Claude Code's input as a user message (`queue`) before it
  hands the results over, and waits for Claude Code's `command_lifecycle`
  "queued" for that message's uuid (at most `queuedWait`, 2s; a version
  that doesn't say goes on after it). Claude Code then tells its model the
  message with the result, as one the user sent while it worked ("The user
  sent a new message while you were working: …"), within the turn. Tried
  with the real Claude Code 2.1.296 against a local mock of Anthropic: the
  next request holds the tool's output, then that reminder, and the turn
  ends with one `result`. Handed over after the results, a message could
  come after the model's reply and start a turn of its own.

Where the result ends is said by the message's parts alone. A tool whose
output says "Do not use tools." has it told as its output, inside the
result. The words of a message that holds images (pi-ai's "Attached
image(s) from tool result:" over Chat, #1382) still go with the result
before them, with the images.

A request with words beside the results still takes the run waiting on
the calls when it comes first (`claimResume`). An AgentSummary that does
is answered in the sub-agent's run, and the sub-agent's own next request
then gets a run started anew, as any request after another answered the
calls does. Starting such a request anew instead would tell the whole
conversation to a new run, a prefix the cache has never seen (#1716,
#1717), for every message sent mid-turn.

## The account's allowance on the reply (#1257)

Claude Code tells a run's account allowance in its stream-json
`rate_limit_event`, not as HTTP headers. The bridge keeps it
(`provider.NoteClaudeLimits`) and says it again on the reply as the
`anthropic-ratelimit-unified-{5h,7d,7d_oi}-{utilization,reset}` headers
Anthropic sends (`limitHeaders`, from `provider.KeptClaudeLimits`): a share
from 0 to 1 and a Unix-seconds reset, for each kept window that says when
it renews. They are set when the request comes in, from what is kept, and
again as the reply begins (`relay`'s `begin`), once the turn's own
`rate_limit_event` is in. A run on Claude Code's own home that has moved to
another account says nothing (`ClaudeCodeMovedOff`), as its event isn't
kept either.

A Claude Code signed in to claude.ai (its sign-in field set to
`claudeai`, `claudeSignIns` in `internal/agent/claude.go`) reads these into its status line's `rate_limits`, which
claude-hud shows. One that signs in to magpie with magpie's key
(`ANTHROPIC_AUTH_TOKEN`) ignores them: Claude Code 2.1.293 reads the
headers only for a claude.ai subscriber. A reply another provider answered
carries none.

## Verification

```sh
go test -tags nogui ./internal/claudecode/ -count=1
go test -tags nogui ./internal/gateway/ -run 'ClaudeSubscriptionRunsTheDownloaded|ClaudeSubscriptionWithoutClaudeCode|ClaudeRewritten|LostMedia|ImagesTakenOut|RunLetGoWhenTheClientRewrote|ClaudeSessionTempFiles|ClaudeLetGo|ClaudeSessionFiles|ClaudeOldSessions|ClaudeSubscriptionReplySaysTheAllowance|ClaudeAllowanceHeaders|ClaudeForksAnsweringTheLeadsCalls|ClaudeTurnGivenUpOn|ClaudeToolResultsGivenUpOn|ClaudePromptMarksEarlierTurns|ClaudeHistoryCachedAcrossNewRuns|ClaudeUnloadableSession|ClaudeEndedRunSaysWhy|ClaudeIdle|ClaudeSideQuestion|ClaudeNoRunSaysWhy|ClaudeToolResultsNoRunSaysWhy|ClaudePromptToldUserText|ClaudePromptKeepsInstructions|ClaudeToolResultsGoOnWithTheUsersWords|ClaudeToolResultsKeepInstructions|ToolResultKeepsUserTextSentMidTurn' -count=1
```

`claude_rewritten_test.go` has a case for each relaxation and one for each
rule that keeps another conversation out; `claude_lost_media_test.go` does
the same for images taken out, from Hana's request bodies. `claude_resume_test.go`'s harness
stands in for Claude Code with a script that keeps sessions as it does.
