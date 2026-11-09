#!/usr/bin/env python3
"""Read-only inventory entrypoint. No discovery, network, grants, or implicit saves.

Interactive consent is only a CLI boundary, not authenticated human consent or
host/OS permission. Target identity/local hydrated storage remain caller assertions.
A host must separately establish these before invoking static-audit. Pseudo-TTYs
can be automated: this interface is not protection against a malicious caller.
"""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import stat
import sys

import clash_inventory
import environment_entry

MAX_REQUEST_BYTES = 65536
BOUNDARY = ('Caller-asserted target/user/namespace and local hydrated storage; '
            'terminal response is not authenticated consent or host/OS approval. '
            'No saved grants, OS isolation, controller access, or readiness claim.')


class InputError(Exception):
    def __init__(self, code):
        self.code = code


class HelpRequested(Exception):
    def __init__(self, text):
        self.text = text


class Parser(argparse.ArgumentParser):
    def print_help(self, file=None):
        # Keep help in the same JSON/output-stream contract without SystemExit.
        raise HelpRequested(self.format_help())

    def error(self, message):
        # argparse normally repeats unknown arguments, which may contain secrets.
        raise InputError('INVALID_ARGUMENTS')


def _path(value):
    if (type(value) is not str or len(value) > 4096 or not value
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise InputError('UNSAFE_OR_OFFLINE_PATH')
    path = Path(value)
    if not path.is_absolute() or '..' in path.parts or value.startswith(('//', '\\\\')) or str(path) != value:
        raise InputError('UNSAFE_OR_OFFLINE_PATH')
    return path


def read_request(filename):
    """Read only an explicit bounded regular request; reject ancestor links too.

    Caller must establish request-file storage is local/hydrated before invocation.
    This POSIX adapter intentionally fails closed on Windows; capabilities works.
    """
    if os.name != 'posix' or not hasattr(os, 'O_NOFOLLOW') or os.open not in os.supports_dir_fd:
        raise InputError('HOST_CAPABILITY_UNAVAILABLE')
    path = _path(filename)
    fd = None
    try:
        fd = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = child
        child = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        os.close(fd)
        fd = child
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise InputError('UNSAFE_OR_OFFLINE_PATH')
        if before.st_size > MAX_REQUEST_BYTES:
            raise InputError('BUDGET_EXCEEDED')
        data = bytearray()
        while len(data) <= MAX_REQUEST_BYTES:
            chunk = os.read(fd, min(8192, MAX_REQUEST_BYTES + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        if len(data) > MAX_REQUEST_BYTES:
            raise InputError('BUDGET_EXCEEDED')
        after = os.fstat(fd)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after):
            raise InputError('SNAPSHOT_CHANGED_DURING_AUDIT')
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise InputError('INPUT_OR_RESPONSE_INVALID')
                result[key] = value
            return result
        def constant(value):
            raise InputError('INPUT_OR_RESPONSE_INVALID')
        return json.loads(data.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    finally:
        if fd is not None:
            os.close(fd)


def validate_request(request, target):
    """Validate the complete CLI envelope before displaying scope or opening files."""
    if type(request) is not dict or set(request) != {
            'schema_version', 'target_ref', 'target_binding', 'application', 'files', 'entry_request'}:
        raise InputError('INPUT_OR_RESPONSE_INVALID')
    if request['schema_version'] != 'guardian-static-cli-request/2':
        raise InputError('INPUT_OR_RESPONSE_INVALID')
    if type(target) is not str or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,47}', target):
        raise InputError('TARGET_NOT_BOUND')
    if request['target_ref'] != target:
        raise InputError('TARGET_NOT_BOUND')
    entry = environment_entry.require_entry(request['entry_request'], 'offline_precheck', target)
    if entry['target_role'] != 'local':
        raise InputError('TARGET_USER_CONTEXT_MISMATCH')
    expected = {'target_ref': target, 'binding_state': 'bound', 'declared_os': 'macos',
                'execution_location': 'native_local', 'desktop_user_relation': 'same',
                'filesystem_namespace': 'host_desktop'}
    if request['target_binding'] != expected or sys.platform != 'darwin':
        raise InputError('TARGET_USER_CONTEXT_MISMATCH')
    if request['application'] != {'product': 'clash-verge-rev', 'gui_version': '2.5.5', 'core_version': '1.19.0'}:
        raise InputError('UNSUPPORTED_PRODUCT_OR_VERSION')
    files = request['files']
    if type(files) is not list or not 1 <= len(files) <= clash_inventory.MAX_FILES:
        raise InputError('INPUT_OR_RESPONSE_INVALID')
    refs, paths = set(), set()
    for item in files:
        if type(item) is not dict or set(item) != {'source_ref', 'kind', 'path'}:
            raise InputError('INPUT_OR_RESPONSE_INVALID')
        ref, kind = item['source_ref'], item['kind']
        if (type(ref) is not str or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,47}', ref)
                or type(kind) is not str or kind not in clash_inventory.LAYERS or ref in refs):
            raise InputError('INPUT_OR_RESPONSE_INVALID')
        path = _path(item['path'])
        if path in paths:
            raise InputError('INPUT_OR_RESPONSE_INVALID')
        refs.add(ref)
        paths.add(path)


def confirm_scope(request, incoming, prompt):
    if not incoming.isatty() or not prompt.isatty():
        raise InputError('LIVE_TERMINAL_REQUIRED')
    prompt.write(BOUNDARY + '\n')
    prompt.write('Read only these exact files on target ' + request['target_ref'] + ':\n')
    for item in request['files']:
        prompt.write(json.dumps({'source_ref': item['source_ref'], 'path': item['path']}, ensure_ascii=True) + '\n')
    prompt.write('Confirm the host/OS permits these reads, this is the intended native desktop/user, '
                 'and all files are local and already hydrated. Type READ to approve this run; anything else cancels: ')
    prompt.flush()
    if incoming.readline(16) != 'READ\n':
        raise InputError('USER_CANCELLED')


def _base():
    return {'schema_version': 'guardian-inventory-cli-result/1', 'status': 'partial',
            'changes': [], 'contact_phase': 'precontact', 'gate_state': 'closed',
            'permission_restorable': False, 'boundary': BOUNDARY}


def run(argv=None, *, incoming=None, outgoing=None, prompt=None):
    incoming = sys.stdin if incoming is None else incoming
    outgoing = sys.stdout if outgoing is None else outgoing
    prompt = sys.stderr if prompt is None else prompt
    result = _base()
    code = 0
    try:
        parser = Parser(prog='inventory_cli.py', description=__doc__)
        commands = parser.add_subparsers(dest='command', required=True, parser_class=Parser)
        commands.add_parser('capabilities')
        audit = commands.add_parser('static-audit')
        audit.add_argument('--request', required=True, help='Absolute local hydrated request JSON path')
        audit.add_argument('--target-ref', required=True, help='Exact independently checked target alias')
        args = parser.parse_args(argv)
        if args.command == 'capabilities':
            result['cli'] = {'static_audit': 'macos_terminal_only', 'mutations': 'unavailable',
                             'network_check': 'scripts/network_check.py run',
                             'update_check': 'scripts/update_check.py check'}
        else:
            request = read_request(args.request)
            validate_request(request, args.target_ref)
            entry_snapshot = deepcopy(request['entry_request'])
            confirm_scope(request, incoming, prompt)
            validate_request(request, args.target_ref)
            if request['entry_request'] != entry_snapshot:
                raise InputError('ENTRY_CHANGED')
            library_request = dict(request, schema_version='guardian-clash-inventory/0.1',
                                   operation='audit', contact_phase='precontact', gate_state='closed',
                                   authorization={'approved_paths': [f['path'] for f in request['files']],
                                                  'local_hydrated_files': True})
            # The library contract remains strict and does not persist entry declarations.
            del library_request['entry_request']
            result['inventory'] = clash_inventory.audit_inventory(library_request, args.target_ref)
            errors = result['inventory']['errors']
            if errors:
                code = 3 if any(e['code'] in {'AUTHORIZATION_MISSING', 'PERMISSION_DENIED', 'USER_CANCELLED'} for e in errors) else 2
            result['status'] = result['inventory']['status']
    except HelpRequested as exc:
        result.update(status='help', help=exc.text)
    except KeyboardInterrupt:
        result.update(status='cancelled', error_code='USER_CANCELLED')
        code = 3
    except (environment_entry.InvalidProjection, environment_entry.EntryBlocked) as exc:
        result.update(status='blocked', error_code=str(exc))
        if isinstance(exc, environment_entry.EntryBlocked):
            result['entry_gaps'] = list(exc.gaps)
        code = 2
    except InputError as exc:
        result.update(status='blocked', error_code=exc.code)
        code = 3 if exc.code in {'LIVE_TERMINAL_REQUIRED', 'USER_CANCELLED'} else 2
    except PermissionError:
        result.update(status='blocked', error_code='PERMISSION_DENIED')
        code = 3
    except (OSError, ValueError, TypeError, KeyError, RecursionError):
        result.update(status='blocked', error_code='INPUT_OR_RESPONSE_INVALID')
        code = 2
    except Exception:
        result.update(status='blocked', error_code='INTERNAL_ERROR')
        code = 4
    outgoing.write(json.dumps(result, ensure_ascii=True, sort_keys=True) + '\n')
    return code


if __name__ == '__main__':
    raise SystemExit(run())
