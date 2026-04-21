---
name: clawrouter
description: Hosted-gateway LLM router — save 67% on inference costs. A local proxy that forwards each request to the blockrun.ai gateway, which routes to the cheapest capable model across 55+ models from OpenAI, Anthropic, Google, DeepSeek, xAI, NVIDIA, and more. 11 free NVIDIA models included. Not a local-inference tool — prompts are sent to the blockrun.ai gateway.
homepage: https://blockrun.ai/clawrouter.md
repository: https://github.com/BlockRunAI/ClawRouter
license: MIT
metadata:
  {
    "openclaw":
      {
        "emoji": "🦀",
        "requires": { "config": ["models.providers.blockrun"] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "@blockrun/clawrouter",
              "bins": ["clawrouter"],
              "label": "Install ClawRouter (npm)",
            },
          ],
      },
  }
---

# ClawRouter

Hosted-gateway LLM router that saves 67% on inference costs by forwarding each request to the blockrun.ai gateway, which picks the cheapest model capable of handling it across 55+ models from 9 providers (11 free NVIDIA models). All billing flows through one USDC wallet; you do not hold provider API keys.

**This is not a local-inference tool.** ClawRouter is a thin local proxy. Your prompts are sent over HTTPS to the blockrun.ai gateway for model execution. If your workload requires inference that never leaves your machine, use a local runtime like Ollama — ClawRouter is not the right tool for that use case.

Source: https://github.com/BlockRunAI/ClawRouter · npm: https://www.npmjs.com/package/@blockrun/clawrouter · License: MIT.

## Data Flow

```
Your app → localhost proxy (ClawRouter) → https://blockrun.ai/api  (or sol.blockrun.ai/api)
                                              ↓
                                        OpenAI / Anthropic / Google / etc.
                                              ↓
                                        Response → back through proxy → your app
```

**Sent to blockrun.ai on every request:** the model name, the full prompt/messages body, sampling params (temperature, max_tokens, tools, etc.), and an `X-PAYMENT` header containing a signed x402 USDC micropayment.

**Not sent:** your wallet private key (only the detached payment signature is sent), any other local files, environment variables, or OpenClaw config beyond what's needed for this request.

**Blockrun's privacy stance:** https://blockrun.ai/privacy. Treat prompts the same way you'd treat prompts sent to any hosted LLM API (OpenAI, Anthropic, etc.) — do not send data you would not share with a third-party API provider.

## Credentials & Local Key Storage

ClawRouter does **not** collect or forward third-party provider API keys. You do not supply OpenAI, Anthropic, Google, DeepSeek, xAI, or NVIDIA credentials — the blockrun.ai gateway owns those relationships.

**What `models.providers.blockrun` stores (fully enumerated):**

| Field | Sensitive | Purpose |
|-------|-----------|---------|
| `walletKey` | Yes | EVM private key used to sign USDC micropayments via x402. **Auto-generated locally on first run** — no user input required. Never transmitted over the network; only detached payment signatures are sent. |
| `solanaKey` | Yes | Solana keypair (BIP-44 `m/44'/501'/0'/0'`). Auto-derived from the same local mnemonic via `@scure/bip32` + `@scure/bip39`. |
| `gateway` | No | Gateway URL. Defaults: `https://blockrun.ai/api` (Base) · `https://sol.blockrun.ai/api` (Solana). |
| `routing` | No | Optional override of the default four-tier router. |

**How and where keys are stored:**

- Keys live in the OpenClaw user config file — typically `~/.config/openclaw/config.json` on Linux, `~/Library/Application Support/openclaw/config.json` on macOS, `%APPDATA%\openclaw\config.json` on Windows — under the `models.providers.blockrun` path.
- Written by OpenClaw's standard config writer with `0600` permissions on POSIX systems (owner read/write only).
- **Stored in plaintext**, the same way every OpenClaw provider's API key is stored. ClawRouter does not add an extra encryption layer; your filesystem permissions are the security boundary. If you require an encrypted keystore, run OpenClaw on an encrypted volume (FileVault, LUKS, BitLocker) or use a dedicated burner wallet funded only with what you intend to spend.
- Auto-generation uses `@scure/bip39` to produce a 24-word mnemonic, then BIP-44 derivation for both chains. Source: [`src/wallet.ts`](https://github.com/BlockRunAI/ClawRouter/blob/main/src/wallet.ts).

**Operational guidance:** treat the wallet as a spending account with a small top-up, not a long-term store of value. Fund it with what you expect to spend on LLM calls. If the host machine is compromised, the wallet key is compromised — rotate and refund.

## Supply-Chain Integrity

- Every release is tagged on GitHub: https://github.com/BlockRunAI/ClawRouter/releases
- Every release publishes to npm with a matching version: https://www.npmjs.com/package/@blockrun/clawrouter?activeTab=versions
- The `skills/release/SKILL.md` mandatory checklist enforces: same version in `package.json`, matching git tag, matching GitHub release, and matching npm publish.
- To verify locally: `npm pack @blockrun/clawrouter@<version>` and compare the tarball contents to the tagged commit.

## Install

```bash
openclaw plugins install @blockrun/clawrouter
```

The structured `install` block above tells OpenClaw to install the auditable npm package `@blockrun/clawrouter`. Source for every version is on GitHub; every release is tagged.

## Setup

```bash
# Enable smart routing (auto-picks cheapest model per request)
openclaw models set blockrun/auto

# Or pin a specific model
openclaw models set openai/gpt-4o
```

## How Routing Works

ClawRouter classifies each request into one of four tiers:

- **SIMPLE** (40% of traffic) — factual lookups, greetings, translations → Gemini Flash ($0.60/M, 99% savings)
- **MEDIUM** (30%) — summaries, explanations, data extraction → DeepSeek Chat ($0.42/M, 99% savings)
- **COMPLEX** (20%) — code generation, multi-step analysis → Claude Opus ($75/M, best quality)
- **REASONING** (10%) — proofs, formal logic, multi-step math → o3 ($8/M, 89% savings)

Rules handle ~80% of requests in <1ms. Only ambiguous queries hit the LLM classifier (~$0.00003 per classification).

## Available Models

55+ models including: gpt-5.4, gpt-4o, o3, claude-opus-4.7, claude-opus-4.6, claude-sonnet-4.6, gemini-3.1-pro, gemini-2.5-flash, deepseek-chat, grok-3, kimi-k2.6, kimi-k2.5, and 11 free NVIDIA models (nemotron-ultra-253b, deepseek-v3.2, mistral-large-675b, qwen3-coder-480b, devstral-2-123b, llama-4-maverick, glm-4.7, gpt-oss-120b, gpt-oss-20b, nemotron-3-super-120b, nemotron-super-49b).

## Example Output

```
[ClawRouter] google/gemini-2.5-flash (SIMPLE, rules, confidence=0.92)
             Cost: $0.0025 | Baseline: $0.308 | Saved: 99.2%
```
