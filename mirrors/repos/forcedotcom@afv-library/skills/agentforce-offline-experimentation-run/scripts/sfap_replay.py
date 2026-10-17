#!/usr/bin/env python3
"""
SFAP-based replay pipeline for offline experimentation.
Reads STDM data, replays prompts via SFAP REST API with structured tool calling,
scores results, and generates a CSV report.
"""
import json, re, csv, os, sys, subprocess, time

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SFAP_BASE_URL  = os.environ.get("SFAP_BASE_URL", "https://test.api.salesforce.com/ai/gpt/v1")
SFAP_TOKEN_FILE = os.environ.get("SFAP_TOKEN_FILE", "")
CORE_TENANT_ID = os.environ.get("CORE_TENANT_ID", "")
REPLAY_MODEL   = os.environ.get("REPLAY_MODEL", "llmgateway__OpenAIGPT41")
JUDGE_MODEL    = os.environ.get("JUDGE_MODEL", REPLAY_MODEL)
OUTPUT_CSV     = os.environ.get("OUTPUT_CSV", "replay_results_sfap.csv")
ORG_ID         = os.environ.get("ORG_ID", "")
AGENT_API_NAME = os.environ.get("AGENT_API_NAME", "")
OUTPUT_JSON    = os.environ.get("OUTPUT_JSON", "replay_results.json")
STDM_DATA_FILE = os.environ.get("STDM_DATA_FILE", "/tmp/details_result.json")
LLM_STEPS_FILES = os.environ.get("LLM_STEPS_FILES", "/tmp/llm_steps_1.json,/tmp/llm_steps_2.json").split(",")

# ---------------------------------------------------------------------------
# Tool extraction is dynamic-only: definitions come from STDM step inputs
# (gen_ai.request.tools) at runtime. No hardcoded tool schemas.
# ---------------------------------------------------------------------------


def _is_routing_tools(tools):
    """True when ALL tools in the list are routing functions (go_to_* / __end_session_action__).
    Action steps may include a single go_to_* for cross-topic transfer alongside domain tools,
    so checking 'any' would mis-classify them."""
    if not tools:
        return False
    for t in tools:
        name = t.get('function', {}).get('name', '')
        if not (name.startswith('go_to_') or name == '__end_session_action__'):
            return False
    return True


def _extract_tool_call_from_step_output(step):
    """Extract the first tool invocation from a step's gen_ai.output.messages."""
    step_output = step.get('output', '') or ''
    try:
        out_json = json.loads(step_output) if isinstance(step_output, str) else step_output
        out_msgs = out_json.get('gen_ai.output.messages', [])
        for om in out_msgs:
            for inv in om.get('tool_invocations', []):
                func = inv.get('function', {})
                if func.get('name'):
                    args = func.get('arguments', '')
                    if isinstance(args, dict):
                        args = json.dumps(args)
                    return func['name'], args
    except Exception:
        pass
    return None, None


def sanitize_tools_for_sfap(tools):
    """Clean STDM tool schemas to be compatible with SFAP's OpenAI-format endpoint.
    Removes additionalProperties and empty required arrays that cause 400 errors."""
    sanitized = []
    for tool in tools:
        tool = json.loads(json.dumps(tool))  # deep copy
        func = tool.get('function', {})
        params = func.get('parameters', {})
        params.pop('additionalProperties', None)
        if 'required' in params and not params['required']:
            del params['required']
        sanitized.append(tool)
    return sanitized


def extract_tools_from_llm_responses(llm_step_map):
    """Scan all LLM responses to discover the actual tool names used by the agent."""
    seen = set()
    for step in llm_step_map.values():
        resp_text = step.get('llm_response', '') or ''
        if not resp_text:
            continue
        try:
            resp = json.loads(resp_text)
            for inv in resp.get('toolInvocations', []):
                name = inv.get('function', {}).get('name', '')
                if name:
                    seen.add(name)
        except:
            pass
    return seen


def read_token():
    if SFAP_TOKEN_FILE and os.path.exists(SFAP_TOKEN_FILE):
        with open(SFAP_TOKEN_FILE) as f:
            return f.read().strip()
    raise RuntimeError("SFAP_TOKEN_FILE not set or file not found")


def parse_prompt_to_messages(prompt_text):
    """Parse role-based prompt text into OpenAI-style messages array.

    Keeps system messages in their original position — production keeps
    subagent instructions at the end of the conversation, not merged to the top.
    Merges consecutive same-role messages to keep alternation valid.
    Appends a user "Continue." if conversation ends on assistant."""
    messages = []
    current_role = None
    current_content = []

    for line in prompt_text.split('\n'):
        stripped = line.strip()
        if stripped in ('role: system', 'role: user', 'role: assistant'):
            if current_role and current_content:
                content = '\n'.join(current_content).strip()
                if content:
                    messages.append({"role": current_role, "content": content})
            current_role = stripped.replace('role: ', '')
            current_content = []
        else:
            if current_role:
                current_content.append(line)

    if current_role and current_content:
        content = '\n'.join(current_content).strip()
        if content:
            messages.append({"role": current_role, "content": content})

    # Merge consecutive same-role messages (keeps system at original position)
    merged = []
    for m in messages:
        if merged and merged[-1]['role'] == m['role']:
            merged[-1]['content'] = f"{merged[-1]['content']}\n{m['content']}".strip()
        else:
            merged.append(m)

    if merged and merged[-1]['role'] == 'assistant':
        merged.append({"role": "user", "content": "Continue."})
    return merged


def convert_stdm_messages_for_sfap(stdm_messages):
    """Convert STDM gen_ai.input.messages to SFAP-compatible OpenAI format.

    Matches the temporal version's approach (src/replay/traces.py:_messages):
    - Folds tool-role messages into the previous message as text
    - Converts assistant tool_invocations to text (keeps content)
    - Merges consecutive same-role messages
    - Keeps system messages in their original position (does NOT merge trailing
      system into the first — production keeps subagent instructions at the end)
    - Appends a user "Continue." if conversation ends on assistant
    """
    raw = []
    for m in stdm_messages:
        role = m.get('role', '')
        content = m.get('content', '') or ''
        tool_invocations = m.get('tool_invocations', [])
        if role == 'assistant' and tool_invocations:
            parts = []
            if content.strip():
                parts.append(content)
            for inv in tool_invocations:
                func = inv.get('function', {})
                name = func.get('name', '')
                args = func.get('arguments', '')
                if isinstance(args, dict):
                    args = json.dumps(args)
                parts.append(f"[tool_call] {name}({args})")
            raw.append({"role": "assistant", "content": "\n".join(parts)})
        else:
            raw.append({"role": role, "content": content})

    out = []
    for m in raw:
        role, content = m["role"], m["content"]
        if role == "tool":
            text = f"[tool result] {content}".strip()
            if out:
                out[-1]["content"] = f"{out[-1]['content']}\n{text}".strip()
            else:
                out.append({"role": "assistant", "content": text})
            continue
        if not content.strip():
            continue
        if out and out[-1]["role"] == role:
            out[-1]["content"] = f"{out[-1]['content']}\n{content}".strip()
        else:
            out.append({"role": role, "content": content})

    if out and out[-1]["role"] == "assistant":
        out.append({"role": "user", "content": "Continue."})
    return out


def call_sfap(messages, model, tools=None, max_tokens=2048):
    """Call SFAP chat generations endpoint."""
    token = read_token()
    url = f"{SFAP_BASE_URL}/chat/generations"

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "required"

    payload_json = json.dumps(payload)

    cmd = [
        "curl", "-sS", "-w", "\n__HTTP_STATUS:%{http_code}",
        url,
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-H", "x-sfdc-app-context: EinsteinGPT",
        "-H", "x-client-feature-id: AgentBacktesting",
        "-H", f"x-sfdc-core-tenant-id: {CORE_TENANT_ID}",
        "-d", payload_json,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    output = result.stdout

    # Split response body and HTTP status
    parts = output.rsplit('\n__HTTP_STATUS:', 1)
    body = parts[0] if parts else output
    status = int(parts[1].strip()) if len(parts) > 1 else 0

    if status != 200:
        return {"error": f"HTTP {status}", "body": body[:500]}

    return json.loads(body)


def extract_tool_call(sfap_response):
    """Extract tool invocation from SFAP response."""
    try:
        gens = sfap_response.get("generation_details", {}).get("generations", [])
        if not gens:
            return None, None, None

        gen = gens[0]
        content = gen.get("content", "")
        invocations = gen.get("tool_invocations") or []

        if invocations:
            inv = invocations[0]
            func = inv.get("function", {})
            return func.get("name"), func.get("arguments", ""), content
        return None, None, content
    except Exception as e:
        return None, None, str(e)


def extract_original_tool_call(llm_response_text):
    """Extract tool invocation from the original STDM LLM response."""
    if not llm_response_text:
        return None, None, llm_response_text

    try:
        resp = json.loads(llm_response_text)
        invocations = resp.get("toolInvocations", [])
        if invocations:
            func = invocations[0].get("function", {})
            return func.get("name"), func.get("arguments", ""), resp.get("content", "")
        return None, None, resp.get("content", llm_response_text)
    except:
        return None, None, llm_response_text


def judge_text(actual, expected, question, model):
    """LLM-as-judge for text responses via SFAP."""
    prompt = f"""You are a scoring judge. Compare the predicted response against the reference response.

Output ONLY valid JSON with "reasoning" and "score" fields.

**Scoring Rubric**
1. score=1 -- the predicted response covers key information of the reference response OR it takes a different but reasonable action
2. score=0.66 -- the predicted response covers a good amount of information OR it takes a somewhat reasonable action
3. score=0.33 -- the predicted response covers little information OR it takes a less reasonable action
4. score=0 -- the predicted response covers no information OR it takes a completely unreasonable action

**Guidelines**
1. The reference answer is a reference, not strict ground truth. Be tolerant to different but reasonable answers.
2. It is fine if the predicted response sounds like an intermediate step rather than a direct answer.
3. The use case context is Salesforce Agentforce assisting customers.
4. Output valid JSON only.

[question]: {question}
[expected text]: {expected}
[predicted text]: {actual}

Output:
"""
    messages = [{"role": "user", "content": prompt}]
    resp = call_sfap(messages, model, max_tokens=512)
    if "error" in resp:
        return None, f"Judge error: {resp['error']}"

    gens = resp.get("generation_details", {}).get("generations", [])
    if not gens:
        return None, "No judge response"

    text = gens[0].get("content", "")
    try:
        # Extract JSON from response
        json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return float(parsed.get("score", 0)), parsed.get("reasoning", "")
    except:
        pass
    return None, f"Could not parse judge response: {text[:200]}"


def judge_args(actual_args, expected_args, func_name, question, model):
    """LLM-as-judge for function arguments via SFAP."""
    prompt = f"""You are a scoring judge. Compare function call arguments.

Output ONLY valid JSON with "reasoning" and "score" fields.

**Scoring Rubric**
1. score=1 -- the arguments are semantically equivalent (same values, possibly different format)
2. score=0.66 -- most arguments match, minor differences in non-critical fields
3. score=0.33 -- some arguments match but key fields differ
4. score=0 -- arguments are completely different or wrong

**Guidelines**
1. Compare semantic meaning, not exact string match.
2. Order of JSON keys does not matter.
3. The use case context is Salesforce Agentforce.
4. Output valid JSON only.

[user question]: {question}
[function name]: {func_name}
[expected arguments]: {expected_args}
[predicted arguments]: {actual_args}

Output:
"""
    messages = [{"role": "user", "content": prompt}]
    resp = call_sfap(messages, model, max_tokens=512)
    if "error" in resp:
        return None, f"Judge error: {resp['error']}"

    gens = resp.get("generation_details", {}).get("generations", [])
    if not gens:
        return None, "No judge response"

    text = gens[0].get("content", "")
    try:
        json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', text, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return float(parsed.get("score", 0)), parsed.get("reasoning", "")
    except:
        pass
    return None, f"Could not parse judge response: {text[:200]}"


# ---------------------------------------------------------------------------
# Enriched-output helpers (for HTML report)
# ---------------------------------------------------------------------------
TOOL_GROUPS = {
    'record_lookup': {'IdentifyRecordByName', 'GetRecordDetails', 'QueryRecords'},
    'record_modify': {'UpdateRecordFields', 'ExtractRecordFieldsAndValuesFromUserInput'},
    'activity': {'GetActivitiesTimeline', 'GetActivityDetails'},
    'routing_discovery': {'go_to_product_discovery'},
    'routing_cart': {'go_to_cart_and_checkout'},
    'routing_help': {'go_to_store_help'},
    'routing_off': {'go_to_off_topic'},
    'shopper_search': {'SearchProducts', 'GetProductDetails', 'GetRecommendations'},
    'shopper_cart': {'AddToCart', 'ViewCart', 'UpdateCart', 'Checkout'},
}


def names_match_lenient(golden, predicted):
    if not golden or not predicted:
        return False
    if golden.lower() == predicted.lower():
        return True
    for group in TOOL_GROUPS.values():
        if golden in group and predicted in group:
            return True
    return False


def build_structured_answer(tool_name, tool_args, text_content):
    answer = {"content": text_content or ""}
    if tool_name:
        args = tool_args
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {"raw": args} if args else {}
        answer["tool_calls"] = [{"name": tool_name, "arguments": args or {}}]
    return answer


def classify_golden_type(tool_name):
    if not tool_name:
        return "action"
    lower = tool_name.lower()
    if any(p in lower for p in ('route_to', 'go_to', 'transfer_to')):
        return "topic"
    return "action"


def build_report_json(results, csv_rows):
    rows = []
    recs = {}
    for i, (r, cr) in enumerate(zip(results, csv_rows)):
        golden = build_structured_answer(
            r.get('original_tool_name'), r.get('original_tool_args'), r.get('original_text'))
        predicted = build_structured_answer(
            r.get('replayed_tool_name'), r.get('replayed_tool_args'), r.get('replayed_text'))

        g_name = r.get('original_tool_name')
        p_name = r.get('replayed_tool_name')
        name_match = (g_name == p_name) if (g_name and p_name) else (not g_name and not p_name)
        lenient = names_match_lenient(g_name, p_name) or name_match

        args_score = cr.get('function_args_score')
        args_is_num = isinstance(args_score, (int, float))
        args_match = args_is_num and args_score >= 0.8
        args_lenient = args_is_num and args_score >= 0.5

        tool_alt = ""
        scoring_err = r.get('replay_error') or ""
        if g_name and not p_name:
            scoring_err = f"Expected tool call ({g_name}), got text response"
        elif not g_name and p_name:
            scoring_err = f"Expected text, got tool call ({p_name})"
        elif g_name and p_name and not name_match and lenient:
            tool_alt = f"Used {p_name} instead of {g_name} (functionally similar)"

        rows.append({
            'SessionRowIndex': i,
            'AiAgentSessionId': r['session_id'],
            'GoldenType': r.get('golden_type', classify_golden_type(g_name)),
            'Utterance': r['user_utterance'],
            'GoldenAnswer': json.dumps(golden),
            'PredictedAnswer': json.dumps(predicted),
            'FunctionNameAgreement': name_match,
            'FunctionNameAgreementLenient': lenient,
            'PassStrict': name_match and args_match,
            'FunctionArgsAgreement': args_match,
            'FunctionArgsAgreementLenient': args_lenient,
            'FunctionArgsScore': args_score if args_is_num else None,
            'FunctionArgsScoreReason': r.get('args_reasoning', ''),
            'ToolAltReason': tool_alt,
            'SchemaViolationNotes': '',
            'ScoringError': scoring_err,
            'BaselineModel': cr.get('original_model', ''),
            'ReplayModel': cr.get('replay_model', REPLAY_MODEL),
            'OrgId': ORG_ID,
            'AgentApiName': AGENT_API_NAME,
        })

        recs[str(i)] = {
            'messages': r.get('replay_messages', []),
            'tools': [t['function']['name'] for t in (r.get('replay_tools') or [])],
            'session_id': r['session_id'],
        }

    return {
        'metadata': {
            'baseline_model': 'openai/gpt-4.1',
            'replay_model': REPLAY_MODEL,
            'org_id': ORG_ID,
            'agent_api_name': AGENT_API_NAME,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'total_rows': len(rows),
        },
        'rows': rows,
        'recs': recs,
    }


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("SFAP Replay Pipeline")
    print("=" * 60)

    # 1. Load STDM conversation data
    print(f"\n[Phase 1] Loading STDM data from {STDM_DATA_FILE}...")
    with open(STDM_DATA_FILE) as f:
        logs = json.load(f)['result']['logs']
    idx = logs.find('DEBUG|STDM_RESULT:')
    convos = json.loads(logs[idx + len('DEBUG|STDM_RESULT:'):].split('\n')[0].strip())
    print(f"  Loaded {len(convos)} conversations")

    # Load LLM step details
    all_llm_steps = []
    for f_path in LLM_STEPS_FILES:
        f_path = f_path.strip()
        try:
            all_llm_steps.extend(json.load(open(f_path)))
        except:
            pass
    llm_step_map = {s['step_id']: s for s in all_llm_steps}
    print(f"  Loaded {len(all_llm_steps)} LLM step details")

    # 2. Build replay targets — both router (topic) and action steps per turn
    print("\n[Phase 1.5] Building replay targets...")
    replay_targets = []

    for convo in convos:
        session_id = convo['session_id']
        for turn_idx, turn in enumerate(convo.get('turns', [])):
            user_msg = None
            output_msg = None
            for msg in turn.get('messages', []):
                if msg.get('message_type') == 'Input' and msg.get('text'):
                    user_msg = msg['text'].strip()
                if msg.get('message_type') == 'Output' and msg.get('text'):
                    output_msg = msg['text'].strip()

            if not user_msg:
                continue

            topic = turn.get('topic')

            # Collect all LLM steps with tools, separating router vs action
            router_step = None
            action_step = None

            for step in turn.get('steps', []):
                if step.get('step_type') != 'LLM_STEP' or not step.get('input'):
                    continue
                try:
                    step_input = json.loads(step['input'])
                except Exception:
                    continue

                tools_from_input = step_input.get('gen_ai.request.tools', [])
                if not tools_from_input:
                    continue

                if _is_routing_tools(tools_from_input):
                    if not router_step:
                        router_step = (step, step_input, tools_from_input)
                else:
                    if not action_step:
                        action_step = (step, step_input, tools_from_input)

            # --- Emit router target (golden_type = "topic") ---
            if router_step:
                r_step, r_input, r_tools = router_step
                r_msgs = r_input.get('gen_ai.input.messages', [])
                r_tool_name, r_tool_args = _extract_tool_call_from_step_output(r_step)
                replay_targets.append({
                    'session_id': session_id,
                    'turn_index': turn_idx,
                    'user_utterance': user_msg,
                    'topic': topic,
                    'golden_type': 'topic',
                    'original_tool_name': r_tool_name,
                    'original_tool_args': r_tool_args,
                    'original_text': output_msg,
                    'prompt': (llm_step_map.get(r_step.get('step_id', ''), {})
                               .get('prompt', '')),
                    'step_name': r_step.get('name', ''),
                    'step_tools': r_tools,
                    'step_messages': r_msgs,
                })

            # --- Emit action target (golden_type = "action") ---
            if action_step:
                a_step, a_input, a_tools = action_step
                a_msgs = a_input.get('gen_ai.input.messages', [])
                a_tool_name, a_tool_args = _extract_tool_call_from_step_output(a_step)

                # Fallback: fold ACTION_STEP tool call onto this target
                if not a_tool_name:
                    for step in turn.get('steps', []):
                        if step.get('step_type') == 'ACTION_STEP':
                            try:
                                si = json.loads(step.get('input', '{}') or '{}')
                                name = si.get('actionName', '').split('.')[-1]
                                if name:
                                    a_tool_name = name
                                    args = si.get('actionInput', '')
                                    a_tool_args = json.dumps(args) if isinstance(args, dict) else (args or '')
                                    break
                            except Exception:
                                pass

                # Fallback: check llm_step_map
                if not a_tool_name:
                    step_id = a_step.get('step_id')
                    if step_id in llm_step_map:
                        resp = llm_step_map[step_id].get('llm_response', '') or ''
                        name, args, _ = extract_original_tool_call(resp)
                        if name:
                            a_tool_name = name
                            a_tool_args = args

                replay_targets.append({
                    'session_id': session_id,
                    'turn_index': turn_idx,
                    'user_utterance': user_msg,
                    'topic': topic,
                    'golden_type': 'action',
                    'original_tool_name': a_tool_name,
                    'original_tool_args': a_tool_args,
                    'original_text': output_msg,
                    'prompt': (llm_step_map.get(a_step.get('step_id', ''), {})
                               .get('prompt', '')),
                    'step_name': a_step.get('name', ''),
                    'step_tools': a_tools,
                    'step_messages': a_msgs,
                })

    topic_count = sum(1 for t in replay_targets if t['golden_type'] == 'topic')
    action_count = sum(1 for t in replay_targets if t['golden_type'] == 'action')
    print(f"  Built {len(replay_targets)} replay targets ({topic_count} router, {action_count} action)")
    for t in replay_targets:
        print(f"    Turn {t['turn_index']} [{t['golden_type']:6s}]: tool={t['original_tool_name']} user=\"{t['user_utterance'][:55]}\"")

    # 3. Replay via SFAP
    print(f"\n[Phase 2] Replaying via SFAP (model: {REPLAY_MODEL})...")
    results = []

    for i, target in enumerate(replay_targets):
        gtype = target.get('golden_type', '?')
        print(f"\n  [{i+1}/{len(replay_targets)}] Turn {target['turn_index']} [{gtype}]: \"{target['user_utterance'][:50]}\"")

        # Parse messages from prompt text, or fall back to structured STDM messages
        messages = parse_prompt_to_messages(target['prompt'])
        if not messages and target.get('step_messages'):
            messages = convert_stdm_messages_for_sfap(target['step_messages'])
        if not messages:
            print(f"    SKIP: Could not parse prompt into messages")
            continue

        # Use tool definitions from STDM step input (dynamic-only, no hardcoded fallback)
        tools = target.get('step_tools')
        if tools:
            tools = sanitize_tools_for_sfap(tools)

        print(f"    Messages: {len(messages)}, Tools: {'yes' if tools else 'no'}")

        # Call SFAP
        try:
            sfap_resp = call_sfap(messages, REPLAY_MODEL, tools=tools, max_tokens=2048)
        except Exception as e:
            print(f"    ERROR: {e}")
            results.append({**target, 'replayed_tool_name': None, 'replayed_tool_args': None,
                           'replayed_text': str(e), 'replay_error': str(e),
                           'replay_messages': messages, 'replay_tools': tools})
            continue

        if "error" in sfap_resp:
            print(f"    ERROR: {sfap_resp['error']}")
            results.append({**target, 'replayed_tool_name': None, 'replayed_tool_args': None,
                           'replayed_text': sfap_resp.get('body', ''), 'replay_error': sfap_resp['error'],
                           'replay_messages': messages, 'replay_tools': tools})
            continue

        # Extract tool call from SFAP response
        rep_tool_name, rep_tool_args, rep_text = extract_tool_call(sfap_resp)

        print(f"    Original: tool={target['original_tool_name']}, args={str(target['original_tool_args'])[:80]}")
        print(f"    Replayed: tool={rep_tool_name}, args={str(rep_tool_args)[:80]}")
        if rep_text:
            print(f"    Text: {str(rep_text)[:100]}")

        results.append({
            **target,
            'replayed_tool_name': rep_tool_name,
            'replayed_tool_args': rep_tool_args,
            'replayed_text': rep_text,
            'replay_error': None,
            'replay_messages': messages,
            'replay_tools': tools,
        })

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    # 4. Score
    print(f"\n[Phase 3] Scoring...")
    csv_rows = []

    for r in results:
        row = {
            'session_id': r['session_id'],
            'utterance': r['user_utterance'],
            'golden_type': r.get('golden_type', ''),
            'original_model': 'openai/gpt-4.1',
            'replay_model': REPLAY_MODEL,
            'actual_topic': r.get('topic', ''),
            'replayed_topic': r.get('topic', ''),
            'topic_match': 1 if r.get('topic') else '',
            'actual_action': r.get('original_tool_name', ''),
            'replayed_action': r.get('replayed_tool_name', ''),
            'function_match_score': '',
            'function_args_score': '',
            'actual_outcome': r.get('original_text', ''),
            'replayed_outcome': r.get('replayed_text', ''),
            'text_resp_score': '',
        }

        # Function name match
        if r.get('original_tool_name') and r.get('replayed_tool_name'):
            row['function_match_score'] = 1 if r['original_tool_name'] == r['replayed_tool_name'] else 0
            print(f"  Turn {r['turn_index']} [{r.get('golden_type', '?')}]: func match = {row['function_match_score']} "
                  f"({r['original_tool_name']} vs {r['replayed_tool_name']})")

            # Judge arguments on exact OR lenient name match
            lenient = names_match_lenient(r['original_tool_name'], r['replayed_tool_name'])
            if (row['function_match_score'] == 1 or lenient) and r.get('original_tool_args') and r.get('replayed_tool_args'):
                label = "exact" if row['function_match_score'] == 1 else "lenient"
                print(f"    Judging arguments ({label} name match)...")
                score, reasoning = judge_args(
                    r['replayed_tool_args'], r['original_tool_args'],
                    r['original_tool_name'], r['user_utterance'], JUDGE_MODEL
                )
                row['function_args_score'] = score if score is not None else ''
                r['args_reasoning'] = reasoning or ''
                print(f"    Args score: {score} - {str(reasoning)[:100]}")
                time.sleep(0.5)
        elif r.get('original_tool_name') and not r.get('replayed_tool_name'):
            row['function_match_score'] = 0
            print(f"  Turn {r['turn_index']}: func match = 0 (expected {r['original_tool_name']}, got text)")
        elif not r.get('original_tool_name') and r.get('replayed_tool_name'):
            row['function_match_score'] = 0
            print(f"  Turn {r['turn_index']}: func match = 0 (expected text, got {r['replayed_tool_name']})")

        # Text response scoring — for turns where replayed model returned text
        if r.get('original_text') and r.get('replayed_text'):
            print(f"  Turn {r['turn_index']}: Judging text response...")
            score, reasoning = judge_text(
                r['replayed_text'], r['original_text'], r['user_utterance'], JUDGE_MODEL
            )
            row['text_resp_score'] = score if score is not None else ''
            r['text_reasoning'] = reasoning or ''
            print(f"    Text score: {score} - {str(reasoning)[:100]}")
            time.sleep(0.5)

        csv_rows.append(row)

    # 5. Write CSV
    print(f"\n[Phase 4] Writing CSV to {OUTPUT_CSV}...")
    fieldnames = [
        'session_id', 'utterance', 'golden_type', 'original_model', 'replay_model',
        'actual_topic', 'replayed_topic', 'topic_match',
        'actual_action', 'replayed_action', 'function_match_score',
        'function_args_score',
        'actual_outcome', 'replayed_outcome', 'text_resp_score'
    ]
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    # 5b. Write enriched JSON for HTML report
    print(f"  Writing JSON to {OUTPUT_JSON}...")
    report_data = build_report_json(results, csv_rows)
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)

    # 6. Summary
    print(f"\n{'=' * 60}")
    print(f"REPLAY SUMMARY")
    print(f"{'=' * 60}")
    print(f"Sessions: {len(set(r['session_id'] for r in results))}")
    print(f"Total turns replayed: {len(results)}")
    print(f"Replay model: {REPLAY_MODEL}")

    func_matches = [r['function_match_score'] for r in csv_rows if r['function_match_score'] != '']
    func_args = [r['function_args_score'] for r in csv_rows if r['function_args_score'] != '']
    text_scores = [r['text_resp_score'] for r in csv_rows if r['text_resp_score'] != '']
    topic_matches = [r['topic_match'] for r in csv_rows if r['topic_match'] != '']

    if topic_matches:
        print(f"\nTopic Agreement:           {sum(topic_matches)/len(topic_matches)*100:.2f}% ({len(topic_matches)} turns)")
    if func_matches:
        print(f"Function Name Accuracy:    {sum(func_matches)/len(func_matches):.4f} ({len(func_matches)} turns)")
    if func_args:
        print(f"Function Argument Accuracy: {sum(func_args)/len(func_args):.4f} ({len(func_args)} turns)")
    if text_scores:
        print(f"Text Response Accuracy:    {sum(text_scores)/len(text_scores):.4f} ({len(text_scores)} turns)")

    # Breakdown by golden_type
    for gtype in ('topic', 'action'):
        gt_rows = [r for r in csv_rows if r.get('golden_type') == gtype]
        if not gt_rows:
            continue
        gt_func = [r['function_match_score'] for r in gt_rows if r['function_match_score'] != '']
        gt_args = [r['function_args_score'] for r in gt_rows if r['function_args_score'] != '']
        label = "Router" if gtype == "topic" else "Action"
        print(f"\n  [{label} steps: {len(gt_rows)} targets]")
        if gt_func:
            print(f"    Function Name Accuracy:    {sum(gt_func)/len(gt_func):.4f} ({len(gt_func)} turns)")
        if gt_args:
            print(f"    Function Argument Accuracy: {sum(gt_args)/len(gt_args):.4f} ({len(gt_args)} turns)")

    print(f"\nCSV saved to: {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
