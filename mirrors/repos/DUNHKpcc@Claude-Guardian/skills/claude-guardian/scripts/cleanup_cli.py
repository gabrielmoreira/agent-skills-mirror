"""Bounded C5 dispatcher for an independently reviewed in-process host.

The ordinary entry has no host adapter and cannot inspect selected roots or
mutate them. No serialized assertion, digest, flag or plugin path supplies one.
Host implementations must establish real identity, attribution, inactive state,
verified independent backup and writer exclusion. This module supplies none of
those native capabilities. Private documents never restore authorization.
"""
import argparse
import copy
import hashlib
import json
import os
import sys
try:
    import environment_entry
except ModuleNotFoundError as exc:
    if exc.name != 'environment_entry':
        raise
    import importlib.util
    from pathlib import Path
    _entry_spec = importlib.util.spec_from_file_location('_guardian_cleanup_entry',
                Path(__file__).with_name('environment_entry.py'))
    environment_entry = importlib.util.module_from_spec(_entry_spec)
    _entry_spec.loader.exec_module(environment_entry)

try:
    import cleanup_transactions as core
except ModuleNotFoundError as exc:
    if exc.name != 'cleanup_transactions':
        raise
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location('_guardian_cleanup_cli_core',
                Path(__file__).with_name('cleanup_transactions.py'))
    core = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core)

tx = core.tx
SCOPE = 'guardian-cleanup-operator-scope/0.1'
DOCUMENT = 'guardian-cleanup-operator-document/0.1'
# Only new-action plans gain an entry binding. Existing core journals and
# recovery receipts retain their original schema and exact recovery checks.
PLAN_DOCUMENT = 'guardian-cleanup-operator-document/0.2'
SCOPE_LIMIT = 65536
SCOPE_KEYS = {'schema_version', 'target_ref', 'mode', 'roots', 'protected_paths',
              'quarantine_directory', 'backup_ref', 'host_context_ref'}


class CLIError(Exception):
    def __init__(self, code, *, private_record_may_exist=False):
        super().__init__(code)
        self.private_record_may_exist = private_record_may_exist


def fail(code):
    raise CLIError(code) from None


def digest(value):
    return hashlib.sha256(core._encode(value)).hexdigest()


def _bindings(value):
    return {k: value[k] for k in ('backup_ref', 'host_context_ref')}


def _scope(value):
    core._keys(value, SCOPE_KEYS)
    if value['schema_version'] != SCOPE:
        fail('INVALID_SCOPE')
    core._identifier(value['backup_ref']); core._identifier(value['host_context_ref'])
    if len(core._encode(value)) > SCOPE_LIMIT:
        fail('SCOPE_TOO_LARGE')
    core._scope(value['roots'], value['protected_paths'], value['quarantine_directory'],
                value['target_ref'], value['mode'])
    return value


def _load(path, limit=core.MAX_DOCUMENT):
    tx._support()
    core._path(path)
    with tx._parent(path) as (fd, name):
        core._directory_meta(fd, private=True)
        # Size bound precedes content read, including the smaller scope bound.
        before = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if before.st_size > limit:
            fail('DOCUMENT_TOO_LARGE')
        raw, snap = tx._read(fd, name)
        if snap['mode'] != 0o600 or len(raw) > limit:
            fail('UNSAFE_DOCUMENT')
    return core._decode(raw)


def _preflight_output(path, plan):
    core._path(path)
    paths = [r['path'] for r in plan['roots']] + [plan['quarantine_directory']] + plan['protected_paths']
    if any(core._overlap(path, other) for other in paths):
        fail('OUTPUT_SCOPE_CONFLICT')
    with tx._parent(path) as (fd, name):
        identity = core._directory_meta(fd, private=True)
        if core._exists(fd, name):
            fail('OUTPUT_EXISTS')
    return identity


def _save(path, value, identity, budget):
    raw = core._encode(value)
    budget.check()
    attempted = False
    try:
        with tx._parent(path) as (fd, name):
            if core._directory_meta(fd, private=True) != identity:
                fail('OUTPUT_PARENT_CHANGED')
            budget.check()
            attempted = True
            tx._write(fd, name, raw, 0o600)
            reread, snapshot = tx._read(fd, name)
            if reread != raw or snapshot['mode'] != 0o600:
                fail('OUTPUT_READBACK_FAILED')
            budget.check()
    except (core.CleanupError, tx.TransactionError, CLIError, OSError, KeyboardInterrupt) as exc:
        if attempted:
            code = exc.code if isinstance(exc, core.CleanupError) else 'PRIVATE_RECORD_SAVE_INCOMPLETE'
            raise CLIError(code, private_record_may_exist=True) from None
        raise


def _envelope(kind, material, bindings, *, entry_digest=None):
    result = {'schema_version': PLAN_DOCUMENT if kind == 'plan' else DOCUMENT, 'kind': kind,
              'material': material, 'bindings': bindings}
    if kind == 'plan':
        if not core._hex(entry_digest, 64):
            fail('ENVIRONMENT_ENTRY_PLAN_BINDING_REQUIRED')
        result['entry_digest'] = entry_digest
    core._encode(result)
    return result


def _document(path, expected, kind):
    if not core._hex(expected, 64):
        fail('INVALID_DIGEST')
    value = _load(path)
    if type(value) is not dict or value.get('kind') != kind:
        fail('INVALID_DOCUMENT')
    version = value.get('schema_version')
    fields = ('schema_version', 'kind', 'material', 'bindings')
    if kind == 'plan' and version == PLAN_DOCUMENT:
        fields += ('entry_digest',)
        core._keys(value, fields)
        if not core._hex(value['entry_digest'], 64):
            fail('INVALID_DOCUMENT')
    elif version == DOCUMENT:
        # Legacy plans are still needed to reconcile an interrupted old
        # quarantine. Only dispatch's new-quarantine path rejects that schema.
        core._keys(value, fields)
    else:
        fail('INVALID_DOCUMENT')
    core._keys(value['bindings'], ('backup_ref', 'host_context_ref'))
    for item in value['bindings'].values():
        core._identifier(item)
    if digest(value) != expected:
        fail('DIGEST_MISMATCH')
    document = (core.CleanupPlan if kind == 'plan' else core.CleanupReceipt)(value['material'])
    return value, document


def _reserve_wrapper(plan, bindings):
    # Reserve future receipt including wrapper overhead BEFORE any root mutation.
    widest = 2**64
    rows = []
    for root in plan['roots']:
        inventory = copy.deepcopy(root['inventory']); inventory[0]['ctime_ns'] = -widest
        rows.append({'root_ref': root['root_ref'], 'location': 'quarantine', 'inventory': inventory})
    snapshot = {'sha256': 'f'*64, 'size': core.MAX_DOCUMENT, 'mode': 0o600,
                'uid': widest, 'gid': widest, 'device': widest, 'inode': widest,
                'mtime_ns': -widest, 'ctime_ns': -widest}
    receipt = {'schema_version': 'guardian-cleanup-receipt/0.1', 'plan': plan,
               'recovery_id': plan['action_id'], 'observation': {'batch_identity': [widest, widest],
                'manifest_snapshot': snapshot, 'roots': rows}}
    core._reserve(plan)
    _envelope('receipt', receipt, bindings)


def _call(host, name, *args):
    try:
        method = getattr(host, name)
        return method(*copy.deepcopy(args))
    except Exception:
        fail('HOST_CALLBACK_FAILED')


def _cancel(host):
    result = _call(host, 'cancelled')
    if type(result) is not bool:
        fail('INVALID_CANCELLATION')
    return result


def _check(host, budget):
    budget.check()


def _verify(host, plan, bindings, budget):
    budget.check()
    result = _call(host, 'verify', plan['target_ref'], plan['scope_digest'], bindings)
    budget.check()
    if result != core.HOST_OK or type(result) is not str:
        fail('HOST_SCOPE_UNVERIFIED')
    return result


def _approval(host, operation, review, target, budget):
    budget.check()
    result = _call(host, 'approve', operation, digest(review), target, review)
    budget.check()
    if result is not True:
        fail('AUTHORIZATION_REQUIRED')
    return True


def _host(host):
    if host is None:
        fail('HOST_ADAPTER_UNAVAILABLE')
    try:
        valid = all(callable(getattr(host, key, None)) for key in ('verify', 'approve', 'exclusive', 'cancelled'))
    except Exception:
        fail('INVALID_HOST_ADAPTER')
    if not valid:
        fail('INVALID_HOST_ADAPTER')


def _public(result):
    value = result.preview()
    value.update(quarantine_records_retained=True, independent_backup_retained=True,
                 backup_evidence='fresh_host_assertion', permanent_purge='unsupported')
    return value


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        fail('INVALID_ARGUMENTS')


def _parser():
    parser = _Parser(add_help=False)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('capabilities', add_help=False)
    p = sub.add_parser('validate-scope', add_help=False);p.add_argument('--scope', required=True)
    p = sub.add_parser('plan', add_help=False);p.add_argument('--scope', required=True);p.add_argument('--plan-output', required=True)
    for cmd in ('quarantine','reconcile'):
        p = sub.add_parser(cmd, add_help=False)
        p.add_argument('--plan-file',required=True);p.add_argument('--expected-plan-digest',required=True)
        if cmd == 'reconcile':p.add_argument('--receipt-output',required=True)
    p = sub.add_parser('restore',add_help=False)
    p.add_argument('--receipt-file',required=True);p.add_argument('--expected-receipt-digest',required=True)
    return parser


def dispatch(args, host=None, *, entry_request=None):
    command = args.command
    entry_basis = copy.deepcopy(entry_request)
    def entry_check(target):
        if entry_request != entry_basis:
            fail('ENVIRONMENT_ENTRY_CHANGED')
        try:
            environment_entry.require_entry(entry_request, 'offline_precheck', target)
            if command == 'quarantine' and entry_request['route']['choice'] == 'vps':
                fail('VPS_QUARANTINE_OUTSIDE_BASIC_CHECK_SCOPE')
        except (environment_entry.InvalidProjection, environment_entry.EntryBlocked):
            fail('ENVIRONMENT_ENTRY_REQUIRED')
    if command == 'capabilities':
        return {'native_acceptance':'not_run', 'host_adapter_available':host is not None,
                'permanent_purge':'unsupported', 'scope':'explicit_selected_active_roots',
                'default_mutations':'blocked_without_host'}
    if command == 'validate-scope':
        scope = _scope(_load(args.scope, SCOPE_LIMIT))
        return {'state':'scope_structure_valid','root_count':len(scope['roots']),
                'ownership':'unverified','native_acceptance':'not_run'}
    _host(host)
    def checked_cancel():
        stopped = _cancel(host)
        if command in ('plan', 'quarantine') and entry_request != entry_basis:
            fail('ENVIRONMENT_ENTRY_CHANGED')
        return stopped
    budget = core._Budget(30, checked_cancel)
    if command == 'plan':
        scope = _scope(_load(args.scope,SCOPE_LIMIT)); bindings = _bindings(scope)
        entry_check(scope['target_ref'])
        _approval(host,'read_hash_scope',scope,scope['target_ref'],budget)
        def verify(target, scope_digest):
            entry_check(target)
            verified = _verify(host,{'target_ref':target,'scope_digest':scope_digest},bindings,budget)
            entry_check(target)
            return verified
        result = core.plan(scope['roots'],scope['protected_paths'],scope['quarantine_directory'],
                           scope['target_ref'],host_check=verify,cancelled=lambda:(budget.check() or False))
        material = result.private_material();_reserve_wrapper(material,bindings)
        envelope = _envelope('plan',material,bindings,entry_digest=digest(entry_basis))
        output_identity = _preflight_output(args.plan_output,material)
        _approval(host,'save_plan',{'document':envelope,'output_path':args.plan_output},material['target_ref'],budget)
        _verify(host,material,bindings,budget)
        response = dict(result.preview(),document_digest=digest(envelope),authority='none')
        _save(args.plan_output,envelope,output_identity,budget)
        return response
    if command in ('quarantine','reconcile'):
        envelope, document = _document(args.plan_file,args.expected_plan_digest,'plan')
        plan = document.private_material()
    else:
        envelope, document = _document(args.receipt_file,args.expected_receipt_digest,'receipt')
        plan = document.private_material()['plan']
    if command == 'quarantine':
        entry_check(plan['target_ref'])
        if envelope['schema_version'] != PLAN_DOCUMENT:
            fail('ENVIRONMENT_ENTRY_PLAN_BINDING_REQUIRED')
        if envelope['entry_digest'] != digest(entry_basis):
            fail('ENVIRONMENT_ENTRY_PLAN_MISMATCH')
    bindings = envelope['bindings'];_reserve_wrapper(plan,bindings)
    def verify(target, scope_digest):
        if command == 'quarantine':
            entry_check(target)
        if target != plan['target_ref'] or scope_digest != plan['scope_digest']:
            fail('HOST_BINDING_MISMATCH')
        verified = _verify(host,plan,bindings,budget)
        if command == 'quarantine':
            entry_check(target)
        return verified
    verify(plan['target_ref'],plan['scope_digest'])
    if command == 'reconcile':
        output_identity = _preflight_output(args.receipt_output,plan)
        _approval(host,'read_reconcile',envelope,plan['target_ref'],budget)
        result = core.reconcile(document,plan['action_id'],host_check=verify,cancelled=lambda:(budget.check() or False))
        current = _envelope('receipt',result.private_material(),bindings)
        _approval(host,'save_receipt',{'document':current,'output_path':args.receipt_output},plan['target_ref'],budget)
        verify(plan['target_ref'],plan['scope_digest'])
        response = dict(_public(result),document_digest=digest(current),authority='none')
        _save(args.receipt_output,current,output_identity,budget)
        return response
    operation = 'quarantine' if command == 'quarantine' else 'restore_cleanup'
    core_digest = document.digest()
    def authorize(op, supplied_digest, target):
        if (op,supplied_digest,target) != (operation,core_digest,plan['target_ref']):
            fail('APPROVAL_BINDING_MISMATCH')
        return _approval(host,operation,envelope,target,budget)
    _approval(host,operation,envelope,plan['target_ref'],budget)
    primary = None
    result = None
    final_check = False
    try:
        exclusive = host.exclusive(plan['target_ref'],plan['scope_digest'],copy.deepcopy(bindings))
        with exclusive:
            try:
                verify(plan['target_ref'],plan['scope_digest'])
                function = core.quarantine if command == 'quarantine' else core.restore
                result = function(document,authorize=authorize,host_check=verify,
                                  exclusive_access=True,cancelled=lambda:(budget.check() or False))
            except BaseException as exc:
                primary = exc
                raise
        # A host context must not suppress an operation failure.
        if primary is not None:
            raise primary
        response = _public(result)
        final_check = True
        budget.check()
    except BaseException as exc:
        if primary is not None:
            raise primary
        if result is not None:
            count = len(plan['roots']) if command == 'quarantine' else sum(
                item['location']=='quarantine' for item in document.private_material()['observation']['roots'])
            code = exc.code if final_check and isinstance(exc,core.CleanupError) else 'HOST_EXCLUSION_FAILED'
            raise core.CleanupError(code, recovery_id=result.recovery_id,
                                   moved_count=count, stage='after_move_verified') from None
        if isinstance(exc,KeyboardInterrupt):
            fail('CANCELLED')
        fail('HOST_EXCLUSION_FAILED')
    return response


def main(argv=None, *, host=None, stdout=None, entry_request=None):
    output = sys.stdout if stdout is None else stdout
    try:
        values = sys.argv[1:] if argv is None else argv
        if type(values) is not list or len(values)>16 or any(type(v) is not str or len(v)>4096 for v in values):
            fail('INVALID_ARGUMENTS')
        args = _parser().parse_args(values)
        result = dispatch(args,host,entry_request=entry_request)
        code = 0
    except core.CleanupError as exc:
        result={'status':'blocked','code':exc.code,'recovery_id':exc.recovery_id,
                'moved_count':exc.moved_count,'stage':exc.stage};code=2
    except CLIError as exc:
        result={'status':'blocked','code':str(exc),'private_record_may_exist':exc.private_record_may_exist};code=2
    except tx.TransactionError as exc:
        result={'status':'blocked','code':str(exc)};code=2
    except KeyboardInterrupt:
        result={'status':'blocked','code':'CANCELLED'};code=2
    except (OSError,ValueError,TypeError,RecursionError):
        result={'status':'blocked','code':'INVALID_OR_UNAVAILABLE_INPUT'};code=2
    output.write(json.dumps(result,sort_keys=True)+'\n')
    return code


if __name__=='__main__':
    raise SystemExit(main())
