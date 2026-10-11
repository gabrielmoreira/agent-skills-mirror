<!-- reviewed-through: c98160c0 (2026-10-10 13:51 +0800) -->
# Lessons from merged work

magpie's code is written, reviewed, merged and released by agents. Each night
the day's commits are reviewed for what had to be fixed again, what shouldn't
have merged and what was verified too thinly. What we learned is kept here.
Read this before changing code. Each lesson is a rule, then why, then the
evidence. "Seen" counts the days a review found it. A lesson seen on 3 or
more separate days moves into [docs/code-standards.md](docs/code-standards.md).

The day of 2026-10-05 had 220 commits and ~170 releases. About 40 of them
fixed something released earlier the same day or the day before. Most
fixes didn't need a second try. The ones that did fall into the patterns below.

On 2026-10-07 four lessons were seen a third day and moved into the code
standards: a fix reaches every sibling, a change re-derives what is built on
it, a red test on main is a bug now, and a merge records what was run at
the reviewed head. They are listed under
[Moved to the code standards](#moved-to-the-code-standards).

2026-10-08 had 192 commits and 18 releases (v0.1.1105 to v0.1.1122), each
tagged after a green run. Two more lessons were seen a third day and moved:
real use before building on it, and GUI tests in both engines and every
language. The acceptance checks now include `gofmt -l` and a Linux and
Windows `go vet`, since a cross-OS build skips `_test.go`.

2026-10-09 had 109 commits and 10-10 had 74 up to 13:51 (v0.1.1127 to
v0.1.1154). Every tag waited for a green run, every release has its 16
assets, and every commit over 400 lines has a body that says what was run.
What went wrong was earlier in the work. A privacy exemption was keyed on a
field's name, which let tool arguments go out unmasked. Two sessions
committing from one checkout shipped each other's files under the wrong
subjects. A known DNS-rebinding hole sat documented in a subsystem page
until the review reproduced it (fixed in c431225a). Three lessons were seen
a second day.

From 10-10 13:51 to 10-11 05:20 there were 191 commits and 18 releases
(v0.1.1155 to v0.1.1172), each tagged on a green run. Most bodies say what
was run, what was broken by hand, and what wasn't tried. What went wrong was
in the tests and in what "the same on main" meant. A test-isolation fix was
made twice and missed a package each time (#1524). Four commits shipped past
a red they called load or "the same on main" without filing it, and one of
those reds was a real rate-limit gap. Two lessons were seen a third day and
moved into the code standards: whatever a test starts ends when it does, and
a timing test leaves room on both sides.

## Reading the report

**Reproduce the reporter's exact case, on the surface they use, before you
call it fixed.** Use their provider, plan, agent and layout, and their GUI, TUI
or CLI. Check their goal (it drags, the title shows, the reason is readable),
not a step on the way to it.
- #834 came back 4 times (v0.1.920 → .925 → .931 → .938). Each round fixed
  only the agent in the screenshot. #792, #743, #791 and #933 were closed and
  reopened within hours.
- 4788cf2b put gnayiab's Cursor list error in the GUI. The reporter uses the
  TUI in WSL. Fixed in f3c05b5e.
- 60b910b7 made a warm /api/state faster. The report was the cold start
  (~8.5s of SyncCatalog). Fixed in 2a4042a9.
- Seen 1× (2026-10-05).

**Build fixtures from the reporter's literal bytes, not a similar sample you
made up.**
- #823: 878a8489 "proved" the Trae case with an invented `<tool_call>{json}`.
  The screenshot had no JSON. The reporter came back (c353f7bd), and the
  parser has grown 2 more formats since.
- 3f76105b's test used a short check-in reason. The real one was ellipsized
  (#821, eb5edced).
- 26706c33 used a different skills layout from #791's.
- For model-output parsers, collect several real failing turns first.
  Truncated and empty bodies go in the tests.
- Seen 1× (2026-10-05).

**When the vendor refuses magpie but serves its own client on the same
account, diff every header of the failing request against the official
client's. Do that before adding retries or fallbacks.**
- #256 Copilot Auto took four releases (719a6820, 026158b0, 251ef218, then
  4660fd69). Each added another fallback. The cause was a missing
  X-GitHub-Api-Version beside Copilot-Session-Token.
- Seen 1× (2026-10-05).

**Decide whether a refusal is about the account, the model or the request
content before you rest an account.**
- 5353ed54 counted WorkBuddy's "unapproved channel" (an agent's system
  prompt) as an account fault. It rested every WorkBuddy AI account for 5
  days (2033df0f).
- Test that the same request fails the same way on a second account.
- Done right on 10-07: bed306ae (#1062) told Google's 400 for an unsupported
  thinking level apart from thinking_config being turned away. It now
  remembers that the model refused reasoning off, not that the provider
  refused thoughts.
- Seen 1× (2026-10-05).

**Fix what the error is about, not only how it is worded.**
- e63fbb0e (kkgg on Discord, "GLM 直接429了"): Zhipu answered a GLM Coding
  Plan key sent to its pay-as-you-go endpoint with 429 1113 "余额不足". The
  commit relabelled the 429 as out of credit, and nothing in magpie tells the
  user the key belongs on the Coding Plan endpoint, which is what would make
  their requests work.
- When a report shows a wrong label, also ask why the request failed. Fix
  that, or point the user to the fix in the message itself.
- 10-10: 1134c7a8 reworded the "restart codex" advice. luci hit the same
  stale app-server daemon on the next release, and e611fc65 then restarted
  it from magpie.
- Seen 2× (2026-10-06, 2026-10-10).

## Fix the class, not the sample

**Scope a vendor rule to that vendor.**
- e950eb08 capped every model at 272K over one DeepSeek report. Claude [1m]
  models were capped too (531dc0aa).
- 71d2da1f priced Anthropic's 1-hour cache write onto OpenAI models
  (3a30ac87).
- Check the claim about the vendor's behaviour against its source or docs.
  Add a test that another vendor's model is unchanged.
- Seen 1× (2026-10-05).

**A restriction covers every route that reaches the thing it guards.**
- 46f03154 (#882) held keys to some models. count_tokens and System One's
  decision model weren't covered until d7a8ddc8.
- Done right on 10-07: 6b6113aa let a gateway key take the user's own value.
  It found that a local request with such a value would skip key limits, and
  moved managedKey onto access.Named, with a test that fails on the old
  check. c83c0d5f (#1112) kept a pinned MAGPIE_ADDR host while sharing, and
  checked that requests behind Tailscale Serve still count as remote.
- Seen 1× (2026-10-05).

**Scope a privacy or security exemption by where the value sits in the
protocol, never by a key's name.**
- 7137feb4 kept any object holding a "signature" or "encrypted_content" key,
  and any `*_id` key, unmasked. A tool call's input is written by the model,
  so `{"signature": …, "body": "DB_PASSWORD=… 13800138000"}` or a `user_id`
  in tool_use input went to the vendor unmasked. 1965e1f0 limited the
  exemption to thinking/reasoning blocks and Gemini's thoughtSignature, and
  never keeps anything under a tool call's arguments.
- Test the exemption with the protected key placed where the user's data
  goes: tool arguments, message text, a nested object.
- Seen 1× (2026-10-09).

**A security gap a doc names is an open bug, not a description.**
- docs/subsystems/gateway-routing.md said "There is no `Host` check, so a
  page whose own name resolves to 127.0.0.1 (DNS rebinding) counts as
  same-origin". On 10-10 the review reproduced it on main. A rebound page
  got 200 on /v1/models, /v1/chat/completions and /v1/magpie/quotas without
  a key. Fixed in c431225a.
- A same-origin exemption needs the Host checked too. A rebound page's GET
  carries no Origin at all.
- When writing such a sentence, file an issue in the same commit.
- Seen 1× (2026-10-10).

## The user's own files and settings

**Never let magpie's default override a value the user set themselves.**
- CLAUDE_CODE_AUTO_COMPACT_WINDOW overrode the user's own autoCompactWindow
  for ~150 releases (602d4ec6).
- `magpie claude model default` deleted the user's own ANTHROPIC_BASE_URL and
  dropped the stash for 12 days (fe2603ff).
- Before writing a key, list everywhere the agent reads that setting from.
  Test with user-owned values present.
- 10-09/10-10: four fixes for magpie writing over a user's own choice.
  - 603dc0c4: dsh's picked model was lost on Disconnect.
  - 5aca7d09: Codex's effort left at Default was written over with medium.
  - c65d9fb4: magpie-models.json dropped keys added by hand.
  - d9bf7c1c: ZCode's API format was put back on every start.
  - Each was written first without a test that holds a user-set value.
- Seen 2× (2026-10-05, 2026-10-10).

**A failed read, parse or hash means "unknown". It never means "empty" or
"equal".**
- relink's `fresh()` treated two unreadable folders as equal and deleted the
  copy (9fb9a8ab).
- readLogins returned an empty list on a parse error, which the next add or
  sign-out wrote back as "no accounts" (d5619d5a only retried for 15ms).
  Fixed in b363327d: the accounts read before are kept, and a file that
  doesn't parse is copied aside before it is written over.
- Done right on 10-07: d40fee80 (#1097) backs up Pi's mcp.json before
  moving it whole, and doesn't move it when the backup fails. 2c2137be
  deletes a dsh session only under its own folder, to the trash, with
  Restore, and was tried with real dsh.
- 10-11: agent/stash.go, which holds every agent's config from before
  magpie, had readLogins' bug, never looked at when b363327d fixed it. A
  stash.json that didn't parse read as empty, writes were plain
  os.WriteFile with no lock, and 40 stashes at once kept none of them
  (270b5257). 8b393938 (StepCode, the same evening) noticed and wrote its
  own strict reader beside the shared one instead of fixing it. When you
  find a shared helper wrong, fix the helper.
- Done right on 10-10: 89271cd4 (#1505) recovers zeroed state files from a
  .bak, copies a bad one aside, and deliberately doesn't recover caller
  keys (a revoked key must stay revoked).
- Seen 2× (2026-10-05, 2026-10-11).

**Before deleting or overwriting a live credential, find every record that
could match the same key.**
- 43a65950 matched Codex accounts by display name. Two Team seats of one
  email share it, so removing one deleted auth.json for both (c13f3bfb). The
  sign-out rule was then rewritten again (4c35c1b8).
- Seen 1× (2026-10-05).

**When you hand users a writable copy, test "user edits it, then sync".**
- 3c7ceb68's "Give skills as Copies" undid the user's own edits on the next
  start (20bdf1e9).
- Seen 1× (2026-10-05).

**Take another app's field types from that app's own data or validator.**
- 84554e57 wrote updatedAt as milliseconds, without trying the real Claude
  Desktop. Its skills page hung for 2 days (#863, 50d6c9a3).
- For layered vendor configs, read the vendor's merge code first. 9761248d
  guessed dsh's merge rules (#838).
- 10-06: #966's review asked that Codex's limit_reached count as "held",
  without reading the app. 38 minutes later #996 read ChatGPT.app's app.asar.
  Its composer only stops on rate_limit.allowed === false, so #996 undid part
  of #966. #996 and e2f1c6ba are how to do it: e2f1c6ba sealed its fixture
  the way OpenHanako 1.0 seals provider-catalog.json and was checked on a
  copy of the owner's real ~/.hanako.
- Seen 2× (2026-10-05, 2026-10-06).

## Verification

**Windows CI only compiles the tests, so a Windows-only red shows
nowhere.** Run the package on the Windows box before calling a Windows
failure "the same on main".
- TestCursor was red on Windows for 3 days, from 585f7f7d until #1248.
- 5d0c1dca's 16 and 76 Windows failures were called the same as main.
  Neither was filed. #923 is the open work to run more of the suite there.
- Seen 1× (2026-10-08).

**What telemetry sends is an allow-list, and a change to what is sent
re-derives every place that discloses it.**
- 169c23c1 sent `omp#` profile ids and the user's own model ids, which
  aren't in the public catalog (fixed in 2cdae80a: only known ids are sent).
- 7d663a27 sent each partner's daily counts, while the READMEs' Privacy and
  the site's "What does magpie send about me?" still listed what was sent
  before (b4aa62af).
- Grep the READMEs (en, zh) and site/public/docs (en, zh, ja) for the
  privacy text in the same commit.
- Seen 1× (2026-10-08).

**A test never loads a real third-party page.**
- 9755201b's test opened ChatGPT, whose Cloudflare challenge hung it.
  9f0831b2 and 88f2eb8a did the same with other vendor pages.
- Serve the page from httptest, built from bytes saved from the real one.
- 10-11: the same holds for a test's broken state. With the icon proxy
  turned off by hand, a library test's github.com avatar URL reached the
  real GitHub, and a worker test's stub fell through to a real fetch
  (f04792f9 moved them to .invalid hosts and a stub that throws). Break the
  change and watch where the test's requests go.
- Seen 2× (2026-10-08, 2026-10-11).

**A test that reads a dependency's source needs the dependency on disk.**
- 884dbdb2's TestTrayMenuOpenFrameIsWails read Wails' source through
  `go list -m` Dir. CI's fresh module cache hasn't unpacked it, so main was
  red on macOS and ubuntu for ~25 minutes (9b6b9966).
- Run `go mod download` for it in the test, or keep the bytes it checks in
  testdata.
- Seen 1× (2026-10-10).

**A check that a value is gone looks past text magpie generates.**
- 6c099edd's redact test checked that "ops" was gone by substring. The
  placeholder's random suffix spelled it ({{HOSTNAME_mlopsiy3}}) on macOS
  CI. f0453192 strips placeholders before the check, in its sibling
  TestMask too.
- Seen 1× (2026-10-10).

**Reproduce on CI's Go version.**
- #1184 couldn't be reproduced on go1.27.1 locally. CI ran 1.26.x, and the
  cause was a Go 1.26.8 segfault. Docker `golang:1.26.8` with
  `GOTOOLCHAIN=local` matches CI.
- Seen 1× (2026-10-08).

## Concurrency and tests

**Never send on a channel, or call anything that can block, while holding a
lock the receiver needs before it reads. Set shared state before the
handoff that lets another goroutine look at it.**
- 85fd35ab's emit sent to a full 64-slot segment while holding r.mu, and the
  reader takes r.mu first. It hung macOS -race CI for 20 minutes
  (4fb8e887). -race -count=50 locally didn't catch it. A test that fills the
  buffer first catches it every time.
- The Claude subscription run recorded run.tools after continueWith had
  already answered the agent, so a quick turn read the old tools
  (TestToolSearchLoadKeepsTheRun, c8690ca0).
- 10-08: 01e66e0f's claudeCredentials.marshal wrote into the raw map that
  every copy of the struct shares. A struct copied by value that holds a
  map is not a copy (15afd988).
- Seen 2× (2026-10-06, 2026-10-08).

**A fake or child process a test starts ends when the test does**, and
**a timing test leaves room on both sides**, are in the code standards
since 10-11. See [Moved to the code standards](#moved-to-the-code-standards).
Two habits from them:
- After a test times out, check `ps` for its binary. An orphaned
  gateway.test spun at 96% CPU for 30 minutes. Size -count to -timeout; a
  timeout panic is not a hang until its stacks show one.
- Reproduce a timing flake by injecting the delay, not by rerunning until
  it fails (0f8e4ebc, 229ce19a, 9e35eef3).

**A test named for a guarantee fails when the guarantee breaks.**
- #1318's TestHistoryWriteHoldsNoWaiter still passes with the waiter held:
  nothing in it waits while the history write is held. Filed as #1358 with
  a design that fails on the old code.
- Before merging, break the guarantee by hand and watch the test go red.
- Seen 1× (2026-10-08).

## Red tests and releases

**Flaky tests: find the cause.** "A test that fails on main is a bug to fix
now" is in the code standards. What the reviews found about finding the
cause:
- TestPluginSOCKSProxy timed out at 60s on ubuntu CI and was rerun as "load
  jitter". It takes 3s on a Mac every time, and a dead local proxy should
  refuse in milliseconds, so something on that path waits. Its cause
  isn't found yet.
- TestUnreadLoginsNotWrittenOver needed two writes inside one wall-clock
  second (a `.bad-<second>` name) and failed on Linux CI (237d216b). Test a
  name made from time.Now() across a second boundary.
- Before fixing a red CI run, `git log origin/main` for a commit that names
  that run or test. 85fd35ab and e34e53a1 fixed the same lost tail in two
  sessions at once.
- 10-07: 07e246e5 named 24 GUI failures as "the same on origin/main". Run
  alone on main, all 8 of their files pass, and so do the two the full run
  failed (api-key-theme, fold-show-grip). They fail only under the full run,
  and CI never runs the GUI suite, so nothing shows it. e95852e3 (#948) named
  TestCursor (Windows) and TestOTelRetryAfterBound the same way. Both pass on
  macOS main and on CI. Neither is filed.
- 10-08: 6ab4c16f fixed the run 0f8e4ebc had already fixed. bc7c62dc, #1216,
  a2a7fb11, 5d0c1dca and #950 each shipped past "fails the same on main".
- Done right on 10-08: #1184 found the Go 1.26.8 segfault behind its flake,
  and 30a8ce29 fixed its flake at the cause.
- 10-11: four commits named a red and shipped past it unfiled. b1396d23
  reran TestMaxRPM as load; it was a real gap (the vendor counted a late
  first request in the next request's minute, ce1ecaa4). 2305ab1f's dsh
  test and 20582866a's queued-stream test "pass alone"; both had causes
  (9c377231, 3f4287e6). db965824 said panel-usage "fails the same on
  origin/main 0a11b183", but 0a11b183 was hours old and f823a53d had fixed
  that test; on the real main it passed 3 of 3.
  - "The same on main" means on origin/main just fetched: `git fetch`, then
    name the sha you ran.
  - A red under load is a timing assumption a user will meet on a busy
    machine. File it, with its output, in the same commit.
- 10-11: two sessions again fixed one flake in the same minute (4caae1c8 and
  3f4287e6), and on 10-10 3a1ade97 landed while another fix of the same
  test was being written. Checking `git log` isn't enough while both are
  working; say on an issue, or file one, that you are on it before you
  start.
- Done right: 2bd49cc5's race was fixed at its cause in 25 minutes
  (28049bd2, -race -count=40 -cpu 1,2). 60f87223, b1cba654, 443f1cbc and
  395c4bc5 fixed flakes at their cause instead of retrying. 06420a71 fixed
  the macOS first-run check at its cause.
- Seen 3× (2026-10-05, 2026-10-06, 2026-10-07); the rule itself is in the
  code standards.

**Don't tag until a CI Test run on that commit, or one containing it, has
finished green. A cancelled run is not a pass.**
- On 10-05 nearly every CI run was cancelled by the next push. Linux-only
  TestCursorLocal failed from v0.1.877 to v0.1.892 (b7fef387).
- Batch fixes rather than tagging every commit. 294 tags in 51 hours left
  no run to finish.
- Before naming a version to a reporter, check it has all 16 assets.
  v0.1.956 was announced on #856 but never built.
- Before listing a package in market.json, check it resolves with
  `npm view`. 2f135ed4's middleware packages reached npm 5h after the
  release. Done right on 10-07: 35485f2d, 01aaa8e9 and 92e4fc32 each checked
  the package on npm first.
- 10-08: 01e66e0f's own run was cancelled, so its red showed up on the next
  commit's run. Every tag that day waited for a green run.
- Seen 2× (2026-10-05, 2026-10-08).

## Merging and closing

**Never merge a PR whose own new test fails, or with known problems a
review listed.** (Merging only the reviewed head, and writing what was run
before the merge, are in the code standards.)
- #885 and #826 merged with their own new test failing. #846 merged with
  four known-wrong translations. Fix or file the problems first.
- Seen 1× (2026-10-05).

**Keep the issue open until the reporter's case works. Reopen when they say
it doesn't.**
- On #876 the reporter couldn't reopen it themselves and had to file #888.
- Don't close as not-planned what the owner hasn't ruled on. #769 and #871
  were reversed.
- Done right on 10-07: #1050, #1053, #1063 and #958 shipped a fix and stayed
  open for the reporter.
- Seen 1× (2026-10-05).

**One commit, one goal.**
- 653cb8ee bundled ZCode sign-in with WSL session deletion.
- 5464a362 capped six pages at 1200px when #860 asked for a speed display.
- A fix found on the way goes in its own commit. 1e0829b1 hid the ja/de fix
  inside a Usage change, beside two issues (#925, #928).
- 76dc5aed bundled a Routing animation fix, a scrollbar fix and bringing the
  GUI tests up to date.
- Seen 2× (2026-10-05, 2026-10-06).

**A large commit has a body: what changed, why, and what was run.**
- 586f2bce changed 5133 lines with a subject line only. bb8a3e30, ed4476b9,
  e22d5eef and d2241a57 had no body either, so a later review can't tell
  what was verified.
- Seen 1× (2026-10-08).
- Done right on 10-09/10-10: none of the 22 commits over 400 lines lacks a
  body.

**Two sessions never commit from the same checkout.**
- 10-09 12:10: 2018882e carries the davsync subject but holds the GTK
  font-DPI fix (#1371, 7 files). b86001d4, "#1371 GTK", is empty. be203728
  is the real davsync change under the same subject. One session committed
  the other's staged files, because they shared the main checkout's index.
- Work in a worktree of your own (`git worktree add --detach`). After
  committing, `git show --stat HEAD` must list your files and only yours. An
  empty commit means another session took your index.
- Seen 1× (2026-10-09).

## Moved to the code standards

These were seen on three or more days. The rules and their evidence are in
[docs/code-standards.md](docs/code-standards.md); a review still checks
each one.

- **A fix reaches every sibling of the bug** (10-05, 10-06, 10-07). Seen
  six times on 10-05. On 10-07 cd8d64a9's sub2api balance URL was left out
  of the hint shown after a failed read.
- **A change re-derives everything built on what it changes** (10-05,
  10-06, 10-07). On 10-07: click-scroll red since 5d871723, four GUI tests
  left red by page-only test runs, and ee2588c2's test race (3e38bd76).
- **A test that fails on main is a bug to fix now** (10-05, 10-06, 10-07).
  On 10-07 dcbae2ef, 76d82528, b2345078, 07e246e5 and e95852e3 each shipped
  past "fails the same on origin/main".
- **Merge only the reviewed head, and write what was run before the merge**
  (10-05, 10-06, 10-07). On 10-07 #1037 merged with no record.
- **Real use before building on it, or telling users it works** (10-05,
  10-07, 10-08). Acceptance criterion 5. On 10-08 bbf99143 "not tried on
  Linux" broke Linux vet with the WSL2 distro there, and #1185 was reviewed
  on macOS only.
- **GUI tests in both engines, at narrow widths, in every language**
  (10-05, 10-06, 10-08). Acceptance criterion 4. On 10-08 aff4f9f2's zh-TW
  missed later strings, and usage-ledger was red ~7h after 586f2bce.
- **A fix reaches every sibling** was missed again on 10-08: #1239 fixed
  Air 9h after a8290d27, and 173ab71e fixed Gemini bodies after #950.
  Done right on 10-08: a8290d27 itself, 9fcd332b (cmd.exe quoting at one
  choke point, tried on the Windows box), 74a809dc with 84f37ac9
  (re-derived account keys), #1271/#1275 (built-in and plugin together),
  3aeb7d1b (a refusal scoped to the model) and #1288.
- **10-09/10-10, criteria still missed.**
  - Sibling: 12c0550a said "Only aBlock had this" while #1445 (open for an
    hour) listed the class. 64179e73, 13356b9d and d7186e51 followed.
  - The suite: 2da8fbe4 ran six packages, not `go test ./...`. Its testenv
    exec broke internal/proc's TestNoCommandBypassesProc, red ~50 min until
    b934d64a.
  - Real use: a3a8e257 shipped GitHub plugin icons without loading the real
    list, and the owner found none showing (52f6b3a3). aa82288f's Volcengine
    plan windows went out "not tried against the real API". It was said
    honestly, and #1427 stays open.
- **Whatever a test starts ends when the test does** (10-06, 10-08,
  10-11). On 10-11 a CLI-identity ask outliving its test wrote into the
  next test's folder (#1524). 4ee3a76b fixed it in the gateway's TestMain
  only; 9c377231 fixed it for every binary through testenv's marker, but
  the gateway isolates itself without testenv and never set the marker, so
  #1524 came back on CI (a349de82). A guard test now fails if the gateway's
  TestMain doesn't set it.
- **A timing test leaves room on both sides** (10-08, 10-09, 10-11). On
  10-10 8424a004 assumed two concurrent handlers let go in order
  (3a1ade97). On 10-11 TestMaxRPM and the queued-stream tests (above).
- **Done right on 10-10/10-11.**
  - 9e35eef3 fixed #1469 half an hour after it was filed, reproducing CI's
    numbers with an injected pause.
  - ede1e32a (#1508) audited all six pickers of the same kind and added a
    guard test that every one can be narrowed.
  - 64262a19 (Prime Agent), 9c11abbd (jcode) and b72e7d4a (#1539) were tried
    with the real binary in a sandbox, and each says what was broken by hand.
  - #1197 scoped Kimi's sampling rule to Kimi Code's endpoints and models.
- **Done right on 10-09/10-10.**
  - 229ce19a, 570b8fdb and ab72c8eb reproduced CI flakes by injecting a
    delay and fixed their cause.
  - 7f62dbf3 named the siblings the reporter's patch missed (Cursor, Muse,
    GUI, CLI) and covered them.
  - 9b51428e found the same hold-out in Factory's list.
  - #1454 stayed open until the reporter confirmed.
  - #1213 and #1282 merged at the reviewed head with the record seconds
    before.
