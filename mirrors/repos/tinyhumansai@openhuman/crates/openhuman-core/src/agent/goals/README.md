# Agent goals

TinyAgents owns goal types, lifecycle, persistence, budgets, and prompt
rendering. This directory contains OpenHuman runtime adapters for explicit
thread selection, tool registration, turn accounting, and idle continuation.

Goals are controlled by the agent tools and runtime. There is no thread-goal
frontend or `openhuman.thread_goals_*` JSON-RPC API.
