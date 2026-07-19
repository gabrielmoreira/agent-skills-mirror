---
description: Start the Agentlas Telegram Connect workflow.
---
Update fallback: 자동 업데이트가 안 되면 `hephaestus update`를 한 번 실행하세요. 업데이트하지 않아도 현재 버전 명령은 그대로 동작합니다.

# /hep-connect

Telegram Connect is a guided setup flow for one job: choose who should answer
in Telegram, connect a bot, pair a chat, send a test message, and keep the
receipt.

Product rules:

- Telegram only until this channel is reliable.
- Show real local targets, not mock cards.
- Token handling must go through a runtime-owned secret store. Do not ask the
  user to paste a BotFather token into ordinary chat.
- Connection state is explicit:
  `Draft -> Token checked -> Chat paired -> Test passed -> Running`.
- A user can add unlimited chat bindings. Session memory belongs to the binding,
  not to the global bot.
- Team, org, and saved-group bindings use one session per Telegram chat.
  Single-agent direct chats can keep one session per user.

When the Desktop app is available, use the `/connect` surface as the operator
home. When implementation is requested, edit the real Agentlas Desktop and
Hephaestus codebase and verify token check, chat pairing, test send, and
delivery receipt before claiming live Telegram delivery.
