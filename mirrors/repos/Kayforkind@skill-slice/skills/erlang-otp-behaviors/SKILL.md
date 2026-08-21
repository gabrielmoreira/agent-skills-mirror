---
name: erlang-otp-behaviors
version: 1.1.1
description: "Implements Erlang/OTP behaviors: gen_server, gen_statem, supervisor, and gen_event with typed callbacks and child_spec helpers. Use when writing OTP processes, supervision trees, or replacing raw spawn/receive. Not for Elixir GenServer/Phoenix, deprecated gen_fsm (use gen_statem), or BEAM NIFs. OTP 27: prefer format_status/1; format_status/2 is deprecated."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Erlang OTP Behaviors

## Overview

OTP (Open Telecom Platform) behaviors are reusable templates for the recurring shapes of concurrent processes. A behavior splits responsibilities: the OTP library handles the generic infrastructure (the receive loop, message matching, timeouts, system messages, supervision integration), and you fill in the *callback* functions with your business logic. This separation is what makes the behaviors worth using — the hard, easy-to-get-wrong parts are written once, in OTP, and tested by millions of deployments.

The four behaviors covered here:

- **`gen_server`** runs a request/response loop over private state.
- **`gen_statem`** runs a state machine where the current state selects how events are handled, with first-class timeouts and state-entry callbacks.
- **`supervisor`** starts, monitors, and restarts a fixed or dynamic set of children according to a declared strategy.
- **`gen_event`** dispatches events to a set of pluggable handlers in one manager process (supported, but see pitfalls).

Two cross-cutting habits run through all examples, and both exist for the same reason — *fail fast, at the boundary, with a clear cause*:

1. **Explicit `-spec`/`-type` declarations** so Dialyzer can prove the code's types line up before it ever runs. There is no `any()` where a precise type is known.
2. **Guards on public API functions** so a bad argument crashes in the *caller's* process at the call site, rather than being shipped as a message that corrupts server state or fails confusingly deep inside a callback.

## When to Use

Reach for an OTP behavior whenever a problem maps onto one of the shapes OTP already solves, because the behavior gives you supervision, debugging (`sys`/`dbg`), code upgrade, and consistent error reporting for free — work you would otherwise reimplement (usually inconsistently) on raw `spawn`.

- **`gen_server`** — when a process *owns* mutable state that other processes read or modify through an API. The reason it fits is serialization: a `gen_server` handles one message at a time, so you never need locks or mutexes to protect the state, and the request/response (`call`) and fire-and-forget (`cast`) split is built in.
- **`gen_statem`** — when behavior depends on an explicit *mode* and the legal transitions between modes matter (protocols, connection lifecycles, device drivers, session expiry). Encoding the mode as a state means illegal transitions become unrepresentable, and you get per-state timeouts and state-entry hooks without extra bookkeeping.
- **`supervisor`** — whenever a process's crash should be *contained and recovered* rather than propagated. A supervisor turns "let it crash" into a reliability strategy: it restarts a child to a known-good initial state instead of leaving the system in a half-broken one.
- **Supervision trees** — to structure a whole application so a failure is isolated to the smallest subtree that can recover on its own. A flat pile of processes tends to over-restart on any single fault; a tree restarts only the affected branch.
- **`gen_event`** — for simple, in-process notification fan-out to a set of trusted handlers. It is fully supported (not deprecated), but every handler runs *inside* the manager process, so prefer `gen_statem` or a dedicated pub/sub library when handlers are heavy, slow, or must fail independently.

## Prerequisites

- A modern Erlang/OTP toolchain (OTP 24+ for `auto_shutdown`; verify callbacks against [OTP 27 stdlib](https://www.erlang.org/docs/27/apps/stdlib/api-reference.html)). `format_status/2` is deprecated on `gen_server` / `gen_statem` / `gen_event` — use `format_status/1`.
- `erlc` compiler and `dialyzer` available on `PATH`.
- On Windows (PowerShell), use forward slashes or escaped backslashes in paths; `erlc` and `dialyzer` accept both.
- `kernel/include/logger.hrl` available (ships with OTP).

## Procedure

### Best Practices and the Reasoning Behind Them

1. **Put owned state behind a `gen_server`** so access is serialized and you inherit supervision and introspection. Hand-rolled `receive` loops re-solve these badly.
2. **Provide every callback the behavior expects, including catch-alls.** The compiler warns about missing/unexported callbacks; a catch-all clause turns "unexpected message" from a crash into a logged no-op.
3. **Model state with a typed record (or a typed map).** A `-record` with field types lets Dialyzer catch a wrong field write at build time; maps are more flexible when the shape evolves. Choose per how much you value rigidity vs. flexibility.
4. **Use `cast` for fire-and-forget, `call` for results.** `cast` returns immediately and never blocks the caller; reserve `call` (which blocks and can time out) for when you actually need a reply or back-pressure.
5. **Implement `terminate/2` only when there's something to clean up** (close sockets, flush buffers), and remember it runs reliably only when the process traps exits or is shut down by its supervisor.
6. **Type timeouts with the built-in `timeout()`** (`non_neg_integer() | infinity`) so intent is explicit and Dialyzer-checked — there is no special `gen:timeout()` type; `timeout()` is the standard one.
7. **Prefer `gen_statem`'s `handle_event_function` mode for branchy machines.** Keeping all transitions in one `handle_event/4` makes the full transition table reviewable in one place; use `state_functions` mode when each state's logic is large enough to deserve its own function.
8. **Expose a typed `child_spec/1` helper from worker modules.** This is a convention, not an OTP callback: it keeps a worker's start args and shutdown policy next to the worker itself, so supervisors stay declarative.
9. **Match the `restart` type to the child's role** (`permanent` / `transient` / `temporary`) rather than defaulting everything to `permanent`.
10. **Use `sys:get_state/1` and tracing to inspect live processes** when debugging — these work for any OTP behavior because the behavior handles system messages for you.
11. **Lean on `auto_shutdown` for "the tree only makes sense while X lives."** Marking a child `significant => true` and setting the supervisor's `auto_shutdown => any_significant` (or `all_significant`) lets the subtree wind itself down when that child exits for good — cleaner than a manual shutdown signal.
12. **Treat distribution as plaintext until you configure TLS.** Enable TLS distribution and guard the cookie before sending sensitive data between nodes on shared networks.

### Example 1: gen_server — Bounded Counter (`counter_server`)

This shows the standard `gen_server` skeleton hardened with types and validation. The counter is *bounded*: increments saturate at `max`, decrements floor at `0`. Guards on the public API reject bad input in the caller's process; the callbacks defend again with catch-all clauses so the server cannot be crashed by an unexpected message.

```erlang
-module(counter_server).
-behaviour(gen_server).

-include_lib("kernel/include/logger.hrl").

%% Public API
-export([start_link/0, start_link/1,
         increment/0, increment/1,
         decrement/0, decrement/1,
         get_value/0, reset/0, stop/0]).

%% Convention (not an OTP callback): a typed child spec for supervisors.
-export([child_spec/1]).

%% gen_server callbacks
-export([init/1, handle_call/3, handle_cast/2, handle_info/2,
         terminate/2, code_change/3]).

-define(SERVER, ?MODULE).

%% A typed record lets Dialyzer reject a wrong-typed field write at build time.
%% `max' is an inclusive upper bound; `infinity' means unbounded.
-record(state, {
    count = 0        :: non_neg_integer(),
    max   = infinity :: non_neg_integer() | infinity
}).

-type start_option()  :: {max, non_neg_integer() | infinity}.
-type start_options() :: [start_option()].
-export_type([start_option/0, start_options/0]).

%%%===================================================================
%%% API
%%%===================================================================

-spec start_link() -> {ok, pid()} | ignore | {error, term()}.
start_link() ->
    start_link([]).

-spec start_link(start_options()) -> {ok, pid()} | ignore | {error, term()}.
start_link(Options) when is_list(Options) ->
    gen_server:start_link({local, ?SERVER}, ?MODULE, Options, []).

%% Keeping start args + shutdown policy next to the worker keeps supervisors
%% declarative. `modules' helps the release handler during code upgrades.
-spec child_spec(start_options()) -> supervisor:child_spec().
child_spec(Options) when is_list(Options) ->
    #{id       => ?MODULE,
      start    => {?MODULE, start_link, [Options]},
      restart  => permanent,
      shutdown => 5000,
      type     => worker,
      modules  => [?MODULE]}.

-spec increment() -> ok.
increment() ->
    increment(1).

%% The guard makes a non-positive step crash the *caller* at the call site,
%% rather than silently shipping a bad message to the server.
-spec increment(pos_integer()) -> ok.
increment(N) when is_integer(N), N > 0 ->
    gen_server:cast(?SERVER, {increment, N}).

-spec decrement() -> ok.
decrement() ->
    decrement(1).

-spec decrement(pos_integer()) -> ok.
decrement(N) when is_integer(N), N > 0 ->
    gen_server:cast(?SERVER, {decrement, N}).

-spec get_value() -> non_neg_integer().
get_value() ->
    gen_server:call(?SERVER, get_value).

-spec reset() -> ok.
reset() ->
    gen_server:call(?SERVER, reset).

-spec stop() -> ok.
stop() ->
    gen_server:stop(?SERVER).

%%%===================================================================
%%% gen_server callbacks
%%%===================================================================

-spec init(start_options()) -> {ok, #state{}} | {stop, term()}.
init(Options) ->
    %% Trap exits so terminate/2 runs on supervisor shutdown and so a linked
    %% process dying arrives as a message we can decide about, not a kill.
    process_flag(trap_exit, true),
    case validate_max(proplists:get_value(max, Options, infinity)) of
        {ok, Max} ->
            {ok, #state{count = 0, max = Max}};
        {error, Reason} ->
            {stop, {invalid_max, Reason}}
    end.

-spec handle_call(term(), gen_server:from(), #state{}) ->
          {reply, term(), #state{}}.
handle_call(get_value, _From, #state{count = Count} = State) ->
    {reply, Count, State};
handle_call(reset, _From, State) ->
    {reply, ok, State#state{count = 0}};
handle_call(Request, From, State) ->
    %% A catch-all keeps one malformed call from crashing the server and
    %% blocking every other client. Reply with an error so the caller fails
    %% fast instead of waiting out the 5s call timeout.
    ?LOG_WARNING("~p: unexpected call ~p from ~p", [?MODULE, Request, From]),
    {reply, {error, {unknown_request, Request}}, State}.

-spec handle_cast(term(), #state{}) -> {noreply, #state{}}.
handle_cast({increment, N}, #state{count = Count, max = Max} = State)
  when is_integer(N), N > 0 ->
    {noreply, State#state{count = clamp_high(Count + N, Max)}};
handle_cast({decrement, N}, #state{count = Count} = State)
  when is_integer(N), N > 0 ->
    {noreply, State#state{count = max(0, Count - N)}};
handle_cast(Msg, State) ->
    ?LOG_WARNING("~p: unexpected cast ~p", [?MODULE, Msg]),
    {noreply, State}.

-spec handle_info(term(), #state{}) -> {noreply, #state{}}.
handle_info({'EXIT', Pid, Reason}, State) ->
    %% Because we trap exits, a linked process dying arrives here as a message
    %% rather than killing us. Log and decide per-link whether to act.
    ?LOG_INFO("~p: linked process ~p exited: ~p", [?MODULE, Pid, Reason]),
    {noreply, State};
handle_info(Info, State) ->
    ?LOG_INFO("~p: ignoring info message ~p", [?MODULE, Info]),
    {noreply, State}.

-spec terminate(term(), #state{}) -> ok.
terminate(Reason, #state{count = Count}) ->
    ?LOG_INFO("~p terminating (count=~p, reason=~p)", [?MODULE, Count, Reason]),
    ok.

-spec code_change(term(), #state{}, term()) -> {ok, #state{}}.
code_change(_OldVsn, State, _Extra) ->
    {ok, State}.

%%%===================================================================
%%% Internal helpers
%%%===================================================================

-spec validate_max(term()) ->
          {ok, non_neg_integer() | infinity} | {error, term()}.
validate_max(infinity) ->
    {ok, infinity};
validate_max(Max) when is_integer(Max), Max >= 0 ->
    {ok, Max};
validate_max(Other) ->
    {error, {not_a_valid_max, Other}}.

-spec clamp_high(integer(), non_neg_integer() | infinity) -> non_neg_integer().
clamp_high(Value, infinity) ->
    Value;
clamp_high(Value, Max) when Value > Max ->
    Max;
clamp_high(Value, _Max) ->
    Value.
```

### Example 2: gen_statem with `state_enter` — Door Lock (`door_fsm`)

A door has three states — `locked`, `unlocked`, `open` — and only some transitions are legal (you cannot `open` a `locked` door). Encoding states as a state machine makes the illegal transitions explicit: any action invalid for the current state is rejected with `{error, {invalid_in_state, State}}` instead of silently doing the wrong thing. `handle_event_function` mode keeps the whole transition table in one function; `state_enter` callbacks log each transition once. The unlock code is configurable and validated at `start_link`.

```erlang
-module(door_fsm).
-behaviour(gen_statem).

-include_lib("kernel/include/logger.hrl").

%% Public API
-export([start_link/0, start_link/1,
         open/0, close/0, lock/0, unlock/1, status/0, stop/0]).

%% gen_statem callbacks
-export([init/1, callback_mode/0, terminate/3, code_change/4]).

%% State callback (handle_event_function mode)
-export([handle_event/4]).

-define(SERVER, ?MODULE).
-define(DEFAULT_CODE, <<"1234">>).

-type door_state() :: locked | unlocked | open.
-type data()       :: #{code := binary(), attempts := non_neg_integer()}.
-export_type([door_state/0]).

%%%===================================================================
%%% API
%%%===================================================================

-spec start_link() -> {ok, pid()} | ignore | {error, term()}.
start_link() ->
    start_link(?DEFAULT_CODE).

%% Require a non-trivial code; a too-short code crashes the caller, not the FSM.
-spec start_link(binary()) -> {ok, pid()} | ignore | {error, term()}.
start_link(Code) when is_binary(Code), byte_size(Code) >= 4 ->
    gen_statem:start_link({local, ?SERVER}, ?MODULE, #{code => Code}, []).

-spec open() -> ok | {error, term()}.
open() ->
    gen_statem:call(?SERVER, open).

-spec close() -> ok | {error, term()}.
close() ->
    gen_statem:call(?SERVER, close).

-spec lock() -> ok | {error, term()}.
lock() ->
    gen_statem:call(?SERVER, lock).

-spec unlock(binary()) -> ok | {error, term()}.
unlock(Code) when is_binary(Code) ->
    gen_statem:call(?SERVER, {unlock, Code}).

-spec status() -> door_state().
status() ->
    gen_statem:call(?SERVER, status).

-spec stop() -> ok.
stop() ->
    gen_statem:stop(?SERVER).

%%%===================================================================
%%% gen_statem callbacks
%%%===================================================================

-spec init(#{code := binary()}) -> {ok, door_state(), data()}.
init(#{code := Code}) ->
    process_flag(trap_exit, true),
    {ok, locked, #{code => Code, attempts => 0}}.

-spec callback_mode() -> [handle_event_function | state_enter].
callback_mode() ->
    [handle_event_function, state_enter].

-spec handle_event(gen_statem:event_type(), term(), door_state(), data()) ->
          keep_state_and_data
        | {keep_state_and_data, [gen_statem:reply_action()]}
        | {keep_state, data(), [gen_statem:reply_action()]}
        | {next_state, door_state(), data(), [gen_statem:reply_action()]}.
%% state_enter: log every transition once.
handle_event(enter, OldState, NewState, _Data) ->
    ?LOG_INFO("door transition: ~p -> ~p", [OldState, NewState]),
    keep_state_and_data;
%% locked: only unlock (with correct code) is legal.
handle_event({call, From}, {unlock, Code}, locked, #{code := Code} = Data) ->
    {next_state, unlocked, Data#{attempts => 0}, [{reply, From, ok}]};
handle_event({call, From}, {unlock, WrongCode}, locked, #{attempts := A} = Data) ->
    {keep_state, Data#{attempts => A + 1}, [{reply, From, {error, wrong_code}}]};
handle_event({call, From}, open, locked, _Data) ->
    {keep_state_and_data, [{reply, From, {error, {invalid_in_state, locked}}}]};
handle_event({call, From}, lock, locked, _Data) ->
    {keep_state_and_data, [{reply, From, ok}]};
%% unlocked: can open or lock.
handle_event({call, From}, open, unlocked, Data) ->
    {next_state, open, Data, [{reply, From, ok}]};
handle_event({call, From}, lock, unlocked, Data) ->
    {next_state, locked, Data, [{reply, From, ok}]};
%% open: can only close.
handle_event({call, From}, close, open, Data) ->
    {next_state, unlocked, Data, [{reply, From, ok}]};
%% status query works in any state.
handle_event({call, From}, status, State, Data) ->
    {keep_state_and_data, [{reply, From, State}]};
%% catch-all: reject unknown events gracefully.
handle_event(EventType, EventContent, State, Data) ->
    ?LOG_WARNING("door_fsm: unexpected ~p:~p in state ~p", [EventType, EventContent, State]),
    {keep_state, Data}.

-spec terminate(term(), door_state(), data()) -> ok.
terminate(Reason, State, #{attempts := A}) ->
    ?LOG_INFO("door_fsm terminating (state=~p, attempts=~p, reason=~p)", [State, A, Reason]),
    ok.

-spec code_change(term(), door_state(), data(), term()) -> {ok, door_state(), data()}.
code_change(_OldVsn, State, Data, _Extra) ->
    {ok, State, Data}.
```

### Example 3: gen_statem with `state_functions` — Session Server (`session_server`)

A per-user session with a sliding idle timeout. `state_functions` mode gives each state its own function. The `state_timeout` action starts the idle timer on entry; a `touch` cast resets it. When the timer fires, the session stops with reason `normal` — its intended end state.

```erlang
-module(session_server).
-behaviour(gen_statem).

-include_lib("kernel/include/logger.hrl").

-export([start_link/2, touch/1, get_user/1, close/1,
         init/1, callback_mode/0, active/3, terminate/3, code_change/4]).

-type user_id() :: binary().
-export_type([user_id/0]).

-type data() :: #{user_id := user_id(), timeout := timeout()}.

%%%===================================================================
%%% API
%%%===================================================================

-spec start_link(user_id(), timeout()) -> {ok, pid()} | ignore | {error, term()}.
start_link(UserId, IdleTimeout) when is_binary(UserId), (IdleTimeout =:= infinity orelse is_integer(IdleTimeout) andalso IdleTimeout >= 0) ->
    gen_statem:start_link(?MODULE, #{user_id => UserId, timeout => IdleTimeout}, []).

-spec touch(pid()) -> ok.
touch(Pid) when is_pid(Pid) ->
    gen_statem:cast(Pid, touch).

-spec get_user(pid()) -> {ok, user_id()}.
get_user(Pid) when is_pid(Pid) ->
    gen_statem:call(Pid, get_user).

-spec close(pid()) -> ok.
close(Pid) when is_pid(Pid) ->
    gen_statem:stop(Pid).

%%%===================================================================
%%% gen_statem callbacks
%%%===================================================================

-spec init(data()) ->
          {ok, active, data(), [{state_timeout, timeout(), expire}]}.
init(#{timeout := IdleTimeout} = Data) ->
    process_flag(trap_exit, true),
    {ok, active, Data, [{state_timeout, IdleTimeout, expire}]}.

-spec callback_mode() -> state_functions.
callback_mode() ->
    state_functions.

-spec active(gen_statem:event_type(), term(), data()) ->
          {keep_state, data()}
        | {keep_state, data(), [gen_statem:action()]}
        | {stop, normal, data()}.
%% The idle timer fired: no activity for a full window, so retire the session.
active(state_timeout, expire, #{user_id := UserId} = Data) ->
    ?LOG_INFO("session for ~p expired after idle timeout", [UserId]),
    {stop, normal, Data};
%% Activity: restart the idle timer to extend the sliding window.
active(cast, touch, #{timeout := IdleTimeout} = Data) ->
    {keep_state, Data, [{state_timeout, IdleTimeout, expire}]};
active({call, From}, get_user, #{user_id := UserId} = Data) ->
    {keep_state, Data, [{reply, From, {ok, UserId}}]};
active(EventType, EventContent, Data) ->
    ?LOG_WARNING("session: unexpected ~p:~p", [EventType, EventContent]),
    {keep_state, Data}.

-spec terminate(term(), active, data()) -> ok.
terminate(Reason, _State, #{user_id := UserId}) ->
    ?LOG_INFO("session for ~p terminating (reason ~p)", [UserId, Reason]),
    ok.

-spec code_change(term(), active, data(), term()) -> {ok, active, data()}.
code_change(_OldVsn, State, Data, _Extra) ->
    {ok, State, Data}.
```

### Example 4: Dynamic Children — Session Supervisor (`session_sup`)

Sessions are created at runtime, one per login, so they need a `simple_one_for_one` supervisor: it holds a single child *template* and spawns instances on demand via `start_child/2`, appending the per-session arguments to the template's start args. The `restart => temporary` choice is deliberate and directly illustrates pitfall #7 — a session that expired or was closed must **not** be restarted, because dying is its intended end state. Restarting it would resurrect a session nobody asked for.

```erlang
-module(session_sup).
-behaviour(supervisor).

-export([start_link/0, start_session/2, init/1]).

-define(SERVER, ?MODULE).

-spec start_link() -> {ok, pid()} | ignore | {error, term()}.
start_link() ->
    supervisor:start_link({local, ?SERVER}, ?MODULE, []).

%% Spawns session_server:start_link(UserId, IdleTimeout) under the supervisor.
%% The UserId guard rejects bad input here; session_server validates the timeout.
-spec start_session(session_server:user_id(), timeout()) ->
          {ok, pid()} | {ok, pid(), term()} | {error, term()}.
start_session(UserId, IdleTimeout) when is_binary(UserId) ->
    supervisor:start_child(?SERVER, [UserId, IdleTimeout]).

-spec init([]) ->
          {ok, {supervisor:sup_flags(), [supervisor:child_spec()]}}.
init([]) ->
    SupFlags = #{strategy  => simple_one_for_one,
                 intensity => 10,
                 period    => 60},
    Template = #{id       => session_server,
                 start    => {session_server, start_link, []},
                 restart  => temporary,   %% expired/closed sessions stay dead
                 shutdown => 5000,
                 type     => worker,
                 modules  => [session_server]},
    {ok, {SupFlags, [Template]}}.
```

### Example 5: Supervision Tree (`app_supervisor`)

The top-level supervisor wires the pieces together. It uses `one_for_one` so a crash in one child doesn't disturb the others — they're independent. Note the two reuse-and-correctness details: it pulls the counter's spec from `counter_server:child_spec/1` (best practice #8), and the `session_sup` child uses `shutdown => infinity`, which is the required idiom for a supervisor child so it gets unbounded time to terminate *its own* children gracefully before the parent gives up.

```erlang
-module(app_supervisor).
-behaviour(supervisor).

-export([start_link/0, init/1]).

-define(SERVER, ?MODULE).

-spec start_link() -> {ok, pid()} | ignore | {error, term()}.
start_link() ->
    supervisor:start_link({local, ?SERVER}, ?MODULE, []).

-spec init([]) ->
          {ok, {supervisor:sup_flags(), [supervisor:child_spec()]}}.
init([]) ->
    %% intensity/period: tolerate up to 5 restarts within 60s before the
    %% supervisor itself gives up — a circuit breaker against crash loops.
    SupFlags = #{strategy  => one_for_one,
                 intensity => 5,
                 period    => 60},

    Counter = counter_server:child_spec([{max, 1000}]),

    Door = #{id       => door_fsm,
             start    => {door_fsm, start_link, [<<"4821">>]},
             restart  => permanent,
             shutdown => 5000,
             type     => worker,
             modules  => [door_fsm]},

    %% A supervisor child needs `shutdown => infinity' so it can shut down its
    %% own subtree before the parent considers it terminated.
    Sessions = #{id       => session_sup,
                 start    => {session_sup, start_link, []},
                 restart  => permanent,
                 shutdown => infinity,
                 type     => supervisor,
                 modules  => [session_sup]},

    {ok, {SupFlags, [Counter, Door, Sessions]}}.
```

> **`auto_shutdown` (OTP 24+).** This tree keeps every child independent, so it doesn't use it. When a subtree is only meaningful while one core child is alive, mark that child `significant => true` and set the supervisor's `auto_shutdown => any_significant` (or `all_significant`); the supervisor then terminates the whole subtree when that child exits *normally and for good*, instead of restarting it or leaving an orphaned tree.

## Pitfalls

These are framed as trade-offs with reasons, not absolute rules — context decides whether something is a mistake.

1. **Doing slow/blocking work inside `handle_call`.** Because a `gen_server` processes one message at a time, a blocking call stalls *every* other client and can deadlock if the blocked call waits on a reply from the same server. Offload long work to a spawned task or reply immediately and continue asynchronously.
2. **No catch-all message clause.** An unmatched `handle_call`/`handle_cast`/`handle_info` clause raises `function_clause` and crashes the process. This is *not* caught by the compiler — you must add a final catch-all clause so a stray message degrades gracefully (log + ignore) instead of taking down the server and everything it was serving.
3. **Forgetting to reply in `handle_call`.** The caller blocks in `gen_server:call/2` until the default 5000 ms timeout elapses, then *exits* with a `timeout` reason. Always return a `{reply, Reply, NewState}` tuple, or hand the `From` value to another process and return `{noreply, NewState}` so a `gen_server:reply(From, Reply)` can happen later.
4. **Choosing the wrong supervision strategy.** `one_for_one` restarts only the failed child; `one_for_all` restarts every sibling (use when children share fate); `rest_for_one` restarts the failed child and those started after it (use when later children depend on earlier ones). Picking the wrong one either restarts too much or leaves dependents pointing at a dead process.
5. **Trapping exits without a reason.** `process_flag(trap_exit, true)` is not universally required — it converts incoming exit signals into `{'EXIT', Pid, Reason}` messages and ensures `terminate/2` runs on shutdown. Set it *when* you need cleanup on shutdown or want to react to linked processes dying; leaving it off is fine for a stateless worker that needs no teardown.
6. **Circular dependencies in a tree.** If child A's start blocks on child B and B blocks on A, the supervisor's serial, ordered startup never completes. Order children so dependencies start first, or break the cycle with lazy connection/retry logic.
7. **Wrong `restart` type for the role.** `permanent` always restarts, `transient` restarts only on abnormal exit, `temporary` never restarts. `temporary` is *correct* for a session that should die when idle, and *wrong* for a database pool that must always exist — the value is right or wrong only relative to the child's purpose.
8. **Skipping `code_change`.** You only need a real `code_change/3` (or `/4`) implementation if you perform *hot* release upgrades via `release_handler`. Systems that deploy with rolling restarts can leave the default pass-through — don't add migration logic you'll never exercise.
9. **Holding very large state in the process.** Large per-process heaps lengthen garbage-collection pauses, and the full state is copied into crash reports and `sys:get_state/1` dumps. For large or read-mostly shared data, keep it in an ETS table or `persistent_term` and store only a handle in the process.
10. **No timeout in a long-lived state machine.** Without a state or generic timeout, an idle session/connection lingers forever and leaks resources. `gen_statem` state timeouts give you bounded lifetimes.
11. **Reaching for `gen_event` reflexively.** It is supported, but its shared-process model means one misbehaving handler degrades all of them. Use it for lightweight trusted fan-out; choose `gen_statem` or a pub/sub library when isolation matters.
12. **Assuming distribution is encrypted.** Erlang distribution uses *unencrypted* TCP by default and authenticates only with a shared cookie. If nodes communicate across an untrusted network, enable TLS distribution (`-proto_dist inet_tls` with `-ssl_dist_optfile`) and protect the cookie — don't assume the wire is private.

## Verification

1. **Compile all five modules** with debug info so Dialyzer and the debugger can use them:

   ```powershell
   erlc +debug_info counter_server.erl door_fsm.erl session_server.erl session_sup.erl app_supervisor.erl
   ```

   Expected: five `.beam` files produced, no warnings.

2. **Run Dialyzer** to confirm the `-spec`/`-type` declarations hold:

   ```powershell
   dialyzer --src counter_server.erl door_fsm.erl session_server.erl session_sup.erl app_supervisor.erl
   ```

   Expected: no warnings or errors. If a PLT is missing, build one first: `dialyzer --build_plt --apps erts kernel stdlib`.

3. **`counter_server` bounds check** — start it, increment a few times, and confirm state via `sys:get_state`:

   ```erlang
   {ok, _} = counter_server:start_link([{max, 3}]),
   counter_server:increment(5),
   %% saturates at 3
   {ok, 3} = {ok, counter_server:get_value()},
   counter_server:decrement(10),
   %% floors at 0
   {ok, 0} = {ok, counter_server:get_value()},
   sys:get_state(counter_server).
   ```

4. **`door_fsm` illegal transitions** — drive the transitions and confirm an illegal action returns an error:

   ```erlang
   {ok, _} = door_fsm:start_link(<<"4821">>),
   {error, {invalid_in_state, locked}} = door_fsm:open(),
   {error, wrong_code} = door_fsm:unlock(<<"9999">>),
   ok = door_fsm:unlock(<<"4821">>),
   ok = door_fsm:open(),
   unlocked = door_fsm:status().
   ```

5. **`session_server` idle timeout** — start one with a short timeout, `touch` it to confirm the window slides, then leave it idle and confirm it exits with reason `normal`:

   ```erlang
   {ok, Pid} = session_server:start_link(<<"user1">>, 1000),
   session_server:touch(Pid),
   timer:sleep(500),
   session_server:touch(Pid),
   timer:sleep(1500),
   %% process should be gone
   false = erlang:is_process_alive(Pid).
   ```

6. **Supervisor recovery** — start `app_supervisor`, kill `door_fsm`, and confirm the supervisor restarts it under `one_for_one` while siblings keep their pids:

   ```erlang
   {ok, _} = app_supervisor:start_link(),
   CounterPid = whereis(counter_server),
   SessionsPid = whereis(session_sup),
   exit(whereis(door_fsm), kill),
   timer:sleep(100),
   %% door_fsm restarted with a new pid
   true = is_pid(whereis(door_fsm)),
   %% siblings unaffected
   CounterPid = whereis(counter_server),
   SessionsPid = whereis(session_sup).
   ```

7. **Distribution security** — if these run on a distributed node over an untrusted network, confirm TLS distribution (`-proto_dist inet_tls`) and cookie protection are configured; otherwise record it as N/A for a single node.

8. **Hot upgrade** (only if you do live release upgrades) — exercise the `sys:suspend/1` → `sys:change_code/4` → `sys:resume/1` path against a running `gen_server`/`gen_statem`.

## Related Skills

- Erlang OTP Design Principles (System Documentation)
- `gen_server` Reference Manual
- `gen_statem` Reference Manual
- `supervisor` Reference Manual
- Learn You Some Erlang — The Count, Rage Against The Finite-State Machines, Supervisors
- Erlang/OTP Secure Coding & TLS Distribution guidance
