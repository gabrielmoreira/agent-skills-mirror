#!/usr/bin/env python3
"""Narrow MCP transport for provider-enforced CCB role commands."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
LIB_DIR = PROJECT_ROOT / 'lib'
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from cli.context import CliContextBuilder
from cli.models import ParsedAskCommand
from cli.services.ask import submit_ask


PROTOCOL_VERSION = '2024-11-05'
SERVER_INFO = {'name': 'ccb-role-command', 'version': '0.1.0'}
FRONTDESK_TOOL_NAME = 'ccb_frontdesk_ask_planner'
DETAILER_TOOL_NAME = 'ccb_task_detailer_replan_planner'
_REQUEST_ID_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$')
_TOOL_DEFS = [
    {
        'name': FRONTDESK_TOOL_NAME,
        'description': 'Submit one silent Frontdesk intake handoff to the resident Planner.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'request_id': {
                    'type': 'string',
                    'description': 'The CCB request id used for exact-once handoff.',
                },
                'evidence': {
                    'type': 'string',
                    'description': 'Complete Intake Evidence or Blocked Evidence authored by Frontdesk.',
                },
            },
            'required': ['request_id', 'evidence'],
            'additionalProperties': False,
        },
    },
    {
        'name': DETAILER_TOOL_NAME,
        'description': 'Submit one versioned silent Task Detailer replan request to the resident Planner.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'activation_id': {
                    'type': 'string',
                    'description': 'Current managed Task Detailer activation id.',
                },
                'request': {
                    'type': 'string',
                    'description': 'Exact ccb.detailer.replan_request.v1 JSON authored by Task Detailer.',
                },
            },
            'required': ['activation_id', 'request'],
            'additionalProperties': False,
        },
    },
]


def _send(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + '\n')
    sys.stdout.flush()


def _result(request_id: Any, payload: dict[str, Any]) -> None:
    _send({'jsonrpc': '2.0', 'id': request_id, 'result': payload})


def _error(request_id: Any, code: int, message: str) -> None:
    _send({'jsonrpc': '2.0', 'id': request_id, 'error': {'code': code, 'message': message}})


def _tool_ok(payload: dict[str, Any]) -> dict[str, Any]:
    return {'content': [{'type': 'text', 'text': json.dumps(payload, ensure_ascii=True)}]}


def _tool_error(message: str) -> dict[str, Any]:
    return {'content': [{'type': 'text', 'text': message}], 'isError': True}


def _project_root() -> Path:
    raw = str(os.environ.get('CCB_CALLER_PROJECT_ROOT') or '').strip()
    if not raw:
        raise RuntimeError('managed role command is missing CCB_CALLER_PROJECT_ROOT')
    root = Path(raw).expanduser().resolve()
    if not (root / '.ccb' / 'ccb.config').is_file():
        raise RuntimeError('managed role command project is not initialized')
    return root


def _validate_frontdesk_request(request_id: str, evidence: str) -> None:
    actor = str(os.environ.get('CCB_CALLER_ACTOR') or '').strip().lower()
    if actor != 'frontdesk':
        raise RuntimeError('managed role command is restricted to frontdesk')
    if not _REQUEST_ID_RE.fullmatch(request_id):
        raise RuntimeError('request_id must match [A-Za-z0-9][A-Za-z0-9_-]{0,79}')
    nonempty = [line.strip() for line in evidence.splitlines() if line.strip()]
    if not nonempty or nonempty[0] not in {'**Intake Evidence**', '**Blocked Evidence**'}:
        raise RuntimeError('evidence must start with **Intake Evidence** or **Blocked Evidence**')
    if f'CCB_REQ_ID: {request_id}' not in evidence:
        raise RuntimeError('evidence CCB_REQ_ID must match request_id')


def submit_frontdesk_planner(args: dict[str, Any]) -> dict[str, Any]:
    request_id = str(args.get('request_id') or '').strip()
    evidence = str(args.get('evidence') or '')
    try:
        _validate_frontdesk_request(request_id, evidence)
        project_root = _project_root()
        command = ParsedAskCommand(
            project=None,
            target='planner',
            sender=None,
            message=evidence,
            task_id=f'act-frontdesk-{request_id}',
            compact=True,
            silence=True,
            inline_request=True,
        )
        context = CliContextBuilder().build(
            command,
            cwd=project_root,
            bootstrap_if_missing=False,
        )
        summary = submit_ask(context, command)
        if len(summary.jobs) != 1:
            raise RuntimeError('frontdesk Planner handoff did not create exactly one job')
        job = summary.jobs[0]
        return _tool_ok(
            {
                'status': 'submitted',
                'project_id': summary.project_id,
                'job_id': job['job_id'],
                'target_name': job.get('target_name') or job.get('agent_name'),
                'silence_on_success': True,
                'task_id': f'act-frontdesk-{request_id}',
            }
        )
    except Exception as exc:
        return _tool_error(str(exc))


def submit_task_detailer_replan(args: dict[str, Any]) -> dict[str, Any]:
    activation_id = str(args.get('activation_id') or '').strip()
    request_text = str(args.get('request') or '')
    try:
        actor = str(os.environ.get('CCB_CALLER_ACTOR') or '').strip().lower()
        if actor not in {'task_detailer', 'ccb_task_detailer'}:
            raise RuntimeError('managed role command is restricted to task_detailer')
        if not re.fullmatch(r'act-[A-Za-z0-9][A-Za-z0-9_-]{0,79}', activation_id):
            raise RuntimeError('activation_id must identify the current managed Detailer activation')
        try:
            request = json.loads(request_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f'request must be valid JSON: {exc}') from exc
        if not isinstance(request, dict) or request.get('schema') != 'ccb.detailer.replan_request.v1':
            raise RuntimeError('request must use ccb.detailer.replan_request.v1')
        identity = str(request.get('request_identity') or '').strip().lower()
        if not re.fullmatch(r'sha256:[0-9a-f]{64}', identity):
            raise RuntimeError('request_identity must use sha256:<64 lowercase hex>')
        revision = request.get('task_revision')
        if isinstance(revision, bool) or not isinstance(revision, int) or revision <= 0:
            raise RuntimeError('task_revision must be a positive integer')
        task_id = str(request.get('task_id') or '').strip()
        if not _REQUEST_ID_RE.fullmatch(task_id):
            raise RuntimeError('task_id is invalid')
        project_root = _project_root()
        command = ParsedAskCommand(
            project=None,
            target='planner',
            sender=None,
            message=request_text,
            task_id=f'detailer-replan-{identity.removeprefix("sha256:")[:32]}',
            compact=True,
            silence=True,
            inline_request=True,
        )
        context = CliContextBuilder().build(
            command,
            cwd=project_root,
            bootstrap_if_missing=False,
        )
        summary = submit_ask(context, command)
        if len(summary.jobs) != 1:
            raise RuntimeError('Task Detailer Planner replan handoff did not create exactly one job')
        job = summary.jobs[0]
        return _tool_ok(
            {
                'status': 'submitted',
                'project_id': summary.project_id,
                'job_id': job['job_id'],
                'target_name': job.get('target_name') or job.get('agent_name'),
                'silence_on_success': True,
                'task_id': command.task_id,
                'activation_id': activation_id,
                'request_identity': identity,
            }
        )
    except Exception as exc:
        return _tool_error(str(exc))


def _handle_request(message: dict[str, Any]) -> bool:
    method = message.get('method')
    request_id = message.get('id')
    if method == 'initialize':
        params = message.get('params') if isinstance(message.get('params'), dict) else {}
        _result(
            request_id,
            {
                'protocolVersion': params.get('protocolVersion') or PROTOCOL_VERSION,
                'capabilities': {'tools': {'list': True}},
                'serverInfo': SERVER_INFO,
            },
        )
        return True
    if method == 'initialized':
        return True
    if method == 'tools/list':
        _result(request_id, {'tools': _TOOL_DEFS})
        return True
    if method == 'tools/call':
        params = message.get('params') if isinstance(message.get('params'), dict) else {}
        tool_name = params.get('name')
        if tool_name not in {FRONTDESK_TOOL_NAME, DETAILER_TOOL_NAME}:
            _result(request_id, _tool_error('unknown tool'))
            return True
        args = params.get('arguments') if isinstance(params.get('arguments'), dict) else {}
        if tool_name == FRONTDESK_TOOL_NAME:
            _result(request_id, submit_frontdesk_planner(args))
        else:
            _result(request_id, submit_task_detailer_replan(args))
        return True
    if method in {'shutdown', 'exit'}:
        _result(request_id, {})
        return False
    if request_id is not None:
        _error(request_id, -32601, f'unknown method: {method}')
    return True


def main() -> int:
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except Exception:
            continue
        if not isinstance(message, dict):
            continue
        try:
            if not _handle_request(message):
                break
        except Exception:
            request_id = message.get('id')
            if request_id is not None:
                _error(request_id, -32603, 'internal error')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
