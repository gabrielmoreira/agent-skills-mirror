"""Fixed-command repair transport, gated on a reviewed native adapter.

Conversational approval belongs to the real execution host, which must match the
exact command and plan digest against a fresh user decision. This module cannot
authenticate chat and deliberately accepts no authorization JSON or token.
Production admission is limited to the fixed macOS Clash Verge Rev 2.5.8
rules-extension scope (native_clash_verge_mac); all other scopes stay closed.
Tests may substitute a synthetic adapter; no runtime plugin or callback import
option exists.
"""
from contextlib import contextmanager
import os
import stat
import time

import recovery_cli
import transactions as tx

SCHEMA = 'guardian-retained-repair/0.3'


@contextmanager
def _native_session(document):
    """Admission must hold writer exclusion until context exit, including readback.

    Only the fixed, reviewed macOS Clash Verge Rev 2.5.8 rules-extension scope is
    admitted (native_clash_verge_mac); every other scope stays unavailable. The
    adapter yields a recheck callable. No caller-supplied adapter is accepted.
    """
    import native_clash_verge_mac
    with native_clash_verge_mac.session(document) as recheck:
        yield recheck


def retain(prepared, *, plan_path, backup_directory, cancelled=None):
    """Retain only freshly rechecked private material; never grant execution.

    A change detected after the write leaves a private artifact, but no successful
    retention result. Execution independently revalidates every retained binding.
    """
    if prepared._plan is None:
        raise tx.TransactionError('NO_CHANGE_TO_RETAIN')
    prepared.recheck_review(cancelled=cancelled)
    tx._path(backup_directory)
    document = {'schema_version': SCHEMA, 'request_digest': prepared._request_digest,
                # Bind planning context without serializing aliases into public
                # output or treating this private digest as authorization.
                'entry_digest': tx.digest(prepared._entry_basis),
                'plan': prepared._plan, 'backup_directory': backup_directory,
                'candidate_kind': prepared._candidate_kind, 'base_source': prepared._base_source,
                'metadata_sources': prepared._metadata_sources, 'extension_uid': prepared._extension_uid}
    with tx._directory(backup_directory) as backup_fd:
        info = os.fstat(backup_fd)
        if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise tx.TransactionError('BACKUP_DIRECTORY_NOT_PRIVATE')
    import json
    with tx._parent(plan_path) as (fd, name):
        info = os.fstat(fd)
        if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise tx.TransactionError('PLAN_DIRECTORY_NOT_PRIVATE')
        prepared.recheck_review(cancelled=cancelled)
        tx._write(fd, name, json.dumps(document, sort_keys=True).encode())
    prepared.recheck_review(cancelled=cancelled)
    if tx.digest(recovery_cli.load_receipt(plan_path)) != tx.digest(document):
        raise tx.TransactionError('PLAN_READBACK_FAILED')
    prepared.recheck_review(cancelled=cancelled)
    return tx.digest(document)


def _bound_document(plan_path, plan_digest, target_path, target_ref, backup_directory,
                    candidate_kind='merge-policy', base_path=None, app_info_path=None,
                    profile_index_path=None, extension_uid=None):
    if not tx._hex(plan_digest, 64):
        raise tx.TransactionError('INVALID_EXPECTED_DIGEST')
    document = recovery_cli.load_receipt(plan_path)
    if tx.digest(document) != plan_digest:
        raise tx.TransactionError('PLAN_DIGEST_MISMATCH')
    if (type(document) is not dict or set(document) != {
            'schema_version', 'request_digest', 'entry_digest', 'plan', 'backup_directory', 'candidate_kind',
            'base_source', 'metadata_sources', 'extension_uid'}
            or document['schema_version'] != SCHEMA
            or not tx._hex(document['request_digest'], 64)
            or not tx._hex(document['entry_digest'], 64)):
        raise tx.TransactionError('INVALID_RETAINED_PLAN')
    if document['candidate_kind'] != candidate_kind or document['extension_uid'] != extension_uid:
        raise tx.TransactionError('CANDIDATE_SCOPE_MISMATCH')
    extras = (base_path, app_info_path, profile_index_path, extension_uid)
    if candidate_kind == 'merge-policy':
        if (document['base_source'] is not None or document['metadata_sources'] != {}
                or any(item is not None for item in extras)):
            raise tx.TransactionError('CANDIDATE_SCOPE_MISMATCH')
    elif candidate_kind == 'rules-prepend':
        if not all(extras) or type(document['metadata_sources']) is not dict or set(document['metadata_sources']) != {'app_info', 'profile_index'}:
            raise tx.TransactionError('EXPLICIT_RULES_SOURCE_SCOPE_REQUIRED')
        sources = [(document['base_source'], base_path),
                   (document['metadata_sources']['app_info'], app_info_path),
                   (document['metadata_sources']['profile_index'], profile_index_path)]
        for source, expected_path in sources:
            if (type(source) is not dict or set(source) != {'path', 'snapshot', 'parent_identity'}
                    or source['path'] != expected_path):
                raise tx.TransactionError('SOURCE_SCOPE_MISMATCH')
            tx._path(expected_path)
            tx._snapshot(source['snapshot'])
            parent = source['parent_identity']
            if (type(parent) is not list or len(parent) != 2
                    or any(type(value) is not int or not 0 <= value <= 2**64 for value in parent)):
                raise tx.TransactionError('INVALID_SOURCE_IDENTITY')
    else:
        raise tx.TransactionError('UNSUPPORTED_CANDIDATE_KIND')
    tx._validate(document['plan'], time.time())
    if (document['plan']['path'] != target_path
            or document['plan']['target_ref'] != target_ref):
        raise tx.TransactionError('TARGET_MISMATCH')
    if document['backup_directory'] != backup_directory:
        raise tx.TransactionError('BACKUP_SCOPE_MISMATCH')
    if document['plan']['before']['sha256'] == document['plan']['after_sha256']:
        raise tx.TransactionError('NO_CHANGE_TO_EXECUTE')
    return document


def execute(*, request_path, plan_path, plan_digest, target_path, target_ref,
            backup_directory, max_seconds=30, cancelled=lambda: False, candidate_kind='merge-policy',
            base_path=None, app_info_path=None, profile_index_path=None, extension_uid=None, entry_request=None):
    """Host-approved exact command only. No generic shell/config replacement API.

    A fixed reviewed native adapter must establish context, version, ownership,
    protected scope and writer exclusion throughout commit, not merely return a
    serialized flag. The currently closed adapter gate performs no writes.
    """
    import repair_cli as r
    import environment_entry
    import copy
    entry_basis = copy.deepcopy(entry_request)
    def entry_check():
        if entry_request != entry_basis:
            raise r.RepairError('ENVIRONMENT_ENTRY_CHANGED')
        try:
            environment_entry.require_entry(entry_request, 'configuration', target_ref)
        except (environment_entry.InvalidProjection, environment_entry.EntryBlocked):
            raise r.RepairError('ENVIRONMENT_ENTRY_REQUIRED') from None
    entry_check()
    entry_digest = tx.digest(entry_basis)
    if type(max_seconds) not in (int, float) or not 0 < max_seconds <= 60:
        raise r.RepairError('INVALID_DEADLINE')
    deadline = time.monotonic() + max_seconds
    def guarded():
        r._guard(cancelled, deadline)
        entry_check()
    guarded()
    scope_args = (candidate_kind, base_path, app_info_path, profile_index_path, extension_uid)
    document = _bound_document(plan_path, plan_digest, target_path, target_ref, backup_directory, *scope_args)
    if document['entry_digest'] != entry_digest:
        raise r.RepairError('ENVIRONMENT_ENTRY_PLAN_MISMATCH')
    receipt = None
    known_recovery_id = None
    def recheck():
        entry_check()
        guarded()
        if _bound_document(plan_path, plan_digest, target_path, target_ref,
                           backup_directory, *scope_args) != document:
            raise tx.TransactionError('PLAN_CHANGED')
        prepared = r.preflight(request_path, target_path, target_ref,
                               max_seconds=max_seconds, cancelled=cancelled, candidate_kind=candidate_kind,
                               base_path=base_path, app_info_path=app_info_path,
                               profile_index_path=profile_index_path, extension_uid=extension_uid,
                               entry_request=entry_request)
        if prepared._request_digest != document['request_digest']:
            raise tx.TransactionError('REQUEST_CHANGED')
        if (prepared._base_source != document['base_source']
                or prepared._metadata_sources != document['metadata_sources']):
            raise tx.TransactionError('SOURCE_SNAPSHOT_CHANGED')
        if prepared._plan is None:
            raise tx.TransactionError('STALE_FILE')
        fresh, retained = prepared._plan, document['plan']
        if any(fresh[key] != retained[key] for key in
               ('before', 'parent_identity', 'after_sha256', 'proposed_base64')):
            raise tx.TransactionError('STALE_FILE')
        guarded()
        adapter_recheck()
        entry_check()
        for source in [document['base_source']] + list(document['metadata_sources'].values()):
            guarded()
            r._check_source(source)
        guarded()
    try:
        guarded()
        with _native_session(document) as adapter_recheck:
            recheck()
            authorization = tx.digest({'plan': document['plan'], 'backup_directory': backup_directory})
            callback_error = None
            def authorize(operation, digest, target):
                nonlocal callback_error
                try:
                    if operation != 'apply' or digest != authorization or target != target_ref:
                        raise tx.TransactionError('AUTHORIZATION_SCOPE_MISMATCH')
                    recheck()
                    return True  # Actual conversational authorization was enforced by host.
                except (tx.TransactionError, r.RepairError, r.edits.EditPlanError, r.rules_edits.RulesPlanError, r.ownership.OwnershipError) as exc:
                    callback_error = exc
                    raise
            try:
                receipt = tx.apply(document['plan'], target_ref=target_ref,
                                   backup_directory=backup_directory, authorize=authorize,
                                   exclusive_access=True)  # Only after admitted adapter's exclusion.
                guarded()
                readback = tx.verify(receipt)
                guarded()
                adapter_recheck()
                entry_check()
                for source in ([document['base_source']] + list(document['metadata_sources'].values())):
                    guarded()
                    r._check_source(source)
                guarded()
                if readback['check_status'] != 'pass':
                    raise tx.TransactionError('POST_WRITE_VERIFY_FAILED', receipt['batch'])
                result = {'schema_version': r.RESULT_SCHEMA, 'status': 'written_but_not_verified',
                        'byte_readback': 'pass', 'application_reload': 'not_run',
                        'effective_routing': 'not_run', 'receipt_digest': tx.digest(receipt),
                        'recovery_id': receipt['batch'], 'recovery': 'retained_private_receipt',
                        'phase': 'PC0', 'claude_contact': 'not_performed'}
            except (tx.TransactionError, r.RepairError, r.edits.EditPlanError, r.rules_edits.RulesPlanError, r.ownership.OwnershipError) as exc:
                code = getattr(callback_error or exc, 'code', str(callback_error or exc))
                recovery_id = (getattr(exc, 'recovery_id', None) or known_recovery_id
                               or (receipt['batch'] if receipt else None))
                known_recovery_id = recovery_id
                raise tx.TransactionError(code, recovery_id) from None
        guarded()
        return result
    except (Exception, KeyboardInterrupt) as exc:
        if isinstance(exc, (tx.TransactionError, r.RepairError, r.edits.EditPlanError, r.rules_edits.RulesPlanError, r.ownership.OwnershipError)):
            code = getattr(exc, 'code', str(exc))
        else:
            code = ('CANCELLED' if isinstance(exc, KeyboardInterrupt) else
                    'IO_FAILURE' if isinstance(exc, OSError) else 'NATIVE_ADAPTER_FAILURE')
        recovery_id = (getattr(exc, 'recovery_id', None) or known_recovery_id
                       or (receipt['batch'] if receipt else None))
        raise tx.TransactionError(code, recovery_id) from None
