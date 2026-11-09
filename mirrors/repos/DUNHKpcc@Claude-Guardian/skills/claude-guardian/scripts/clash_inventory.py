"""Bounded, non-mutating ENV-02 static inventory (ENV v0.3 §§5,19).

Call audit_inventory(request, expected_target_ref). The host must first authorize
exact local, hydrated paths and establish target/user/filesystem identity. This
module does not discover files, launch software, use a controller, or fetch data.
Version metadata is supplied by the host and remains reported, not verified.

Version labels 2.5.5 / 1.19.0 identify synthetic schema fixtures only;
no product releases have been certified by this module. In particular, the
Mihomo label is a fixture label, not an independently verified compatibility range;
this is NOT native application compatibility certification. POSIX descriptor
traversal rejects all links; Windows safe native reads are not implemented.
PyYAML is optional, never installed automatically. Raw bytes/hashes/paths and
exception text never leave the local read/parse boundary. Revisions are opaque
per-call aliases, unsuitable for cross-session apply authorization.
"""
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import time
import uuid

try:
    import yaml
except ImportError:
    yaml = None

MAX_BYTES = 4 * 1024 * 1024
MAX_FILES = 32
MAX_DEPTH = 64
MAX_NODES = 20000
MAX_SECONDS = 90
SCHEMA_FIXTURE_GUI_VERSIONS = {'2.5.5'}
SCHEMA_FIXTURE_CORE_VERSIONS = {'1.19.0'}
LAYERS = {'gui_settings': 'gui_declared', 'profile': 'file_declared',
          'global_extension': 'file_declared', 'profile_extension': 'file_declared',
          'generated_config': 'file_declared'}
ALIAS = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,47}\Z')


PUBLIC_ERROR_CODES = frozenset({
    'INPUT_OR_RESPONSE_INVALID', 'UNSAFE_OR_OFFLINE_PATH',
    'HOST_CAPABILITY_UNAVAILABLE', 'BUDGET_EXCEEDED',
    'SNAPSHOT_CHANGED_DURING_AUDIT', 'FILE_NOT_FOUND_IN_APPROVED_SCOPE',
    'PERMISSION_DENIED', 'RUNTIME_OR_PARSER_UNAVAILABLE', 'USER_CANCELLED',
    'INVENTORY_CALLBACK_FAILED', 'PRECONTACT_ACTION_REJECTED', 'TARGET_NOT_BOUND',
    'TARGET_USER_CONTEXT_MISMATCH', 'UNSUPPORTED_PRODUCT_OR_VERSION',
    'AUTHORIZATION_MISSING',
})


def _public_code(code):
    return code if isinstance(code, str) and code in PUBLIC_ERROR_CODES else 'INPUT_OR_RESPONSE_INVALID'


class InventoryError(Exception):
    def __init__(self, code):
        self.code = _public_code(code)
        super().__init__(self.code)


def _fail(code='INPUT_OR_RESPONSE_INVALID'):
    raise InventoryError(code)


# Keep this small alias screen aligned with guardian.KNOWN_CREDENTIAL_VALUE.
# This standalone collector must not depend on sibling import-path setup.
KNOWN_CREDENTIAL_VALUE = re.compile(
    r"(?i)(?:(?<![A-Za-z0-9])sk-(?:ant-)?[A-Za-z0-9_-]{12,}"
    r"|(?<![A-Za-z0-9])(?:ghp_|github_pat_)[A-Za-z0-9_-]{12,}"
    r"|bearer\s+\S+|(?:password|secret|token|api[_-]?key|authorization)\s*[:=]\s*\S+)")


def _alias(value):
    if (not isinstance(value, str) or not ALIAS.fullmatch(value)
            or KNOWN_CREDENTIAL_VALUE.search(value)):
        _fail()
    return value


def _path(value):
    if not isinstance(value, str) or len(value) > 4096 or '\x00' in value:
        _fail('UNSAFE_OR_OFFLINE_PATH')
    p = Path(value)
    if not p.is_absolute() or value.startswith(('//', '\\\\')) or '..' in p.parts:
        _fail('UNSAFE_OR_OFFLINE_PATH')
    return p


def _read(path):
    """Open each ancestor relative to its pinned descriptor, never follow links."""
    if os.name != 'posix' or not hasattr(os, 'O_NOFOLLOW') or os.open not in os.supports_dir_fd:
        _fail('HOST_CAPABILITY_UNAVAILABLE')
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
            _fail('UNSAFE_OR_OFFLINE_PATH')
        if before.st_size > MAX_BYTES:
            _fail('BUDGET_EXCEEDED')
        chunks, size = [], 0
        while True:
            data = os.read(fd, min(65536, MAX_BYTES + 1 - size))
            if not data:
                break
            chunks.append(data)
            size += len(data)
            if size > MAX_BYTES:
                _fail('BUDGET_EXCEEDED')
        after = os.fstat(fd)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after):
            _fail('SNAPSHOT_CHANGED_DURING_AUDIT')
        raw = b''.join(chunks)
        return raw, (identity(after), hashlib.sha256(raw).digest())
    except FileNotFoundError:
        _fail('FILE_NOT_FOUND_IN_APPROVED_SCOPE')
    except PermissionError:
        _fail('PERMISSION_DENIED')
    except OSError:
        _fail('UNSAFE_OR_OFFLINE_PATH')
    finally:
        if fd is not None:
            os.close(fd)


def _parse(raw, check_budget=lambda: None):
    if yaml is None:
        _fail('RUNTIME_OR_PARSER_UNAVAILABLE')
    if len(raw) > MAX_BYTES:
        _fail('BUDGET_EXCEEDED')
    try:
        text = raw.decode('utf-8')
        depth = nodes = documents = 0
        for event in yaml.parse(text, Loader=yaml.SafeLoader):
            nodes += 1
            if nodes % 64 == 0:
                check_budget()
            if nodes > MAX_NODES:
                _fail('BUDGET_EXCEEDED')
            if isinstance(event, yaml.events.AliasEvent) or getattr(event, 'anchor', None):
                _fail()  # zero aliases/anchors is the deliberately bounded subset
            tag = getattr(event, 'tag', None)
            if tag is not None:
                _fail()  # no explicit tags, constructors, merge directives or includes
            if isinstance(event, yaml.events.DocumentStartEvent):
                documents += 1
                if documents > 1:
                    _fail()
            if isinstance(event, (yaml.events.MappingStartEvent, yaml.events.SequenceStartEvent)):
                depth += 1
                if depth > MAX_DEPTH:
                    _fail('BUDGET_EXCEEDED')
            if isinstance(event, (yaml.events.MappingEndEvent, yaml.events.SequenceEndEvent)):
                depth -= 1

        class StrictLoader(yaml.SafeLoader):
            pass

        def mapping(loader, node):
            result = {}
            for key_node, value_node in node.value:
                key = loader.construct_object(key_node, deep=True)
                if not isinstance(key, str) or key == '<<' or key in result:
                    _fail()
                result[key] = loader.construct_object(value_node, deep=True)
            return result
        StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
        result = yaml.load(text, Loader=StrictLoader)
        if not isinstance(result, dict):
            _fail()
        return result
    except InventoryError:
        raise
    except (yaml.YAMLError, UnicodeError, ValueError, TypeError, RecursionError):
        _fail()


def _field(mapping, key, kind):
    if key not in mapping:
        return {'state': 'unknown', 'value': None}
    value = mapping[key]
    valid = (type(value) is bool if kind == 'bool' else
             type(value) is int and 0 <= value <= 65535 if kind == 'port' else
             isinstance(value, str) and value in kind)
    return {'state': 'observed' if valid else 'unknown', 'value': value if valid else None}


def _project(obj, kind):
    """Whitelist projections; strings from unbounded source vocabularies never escape."""
    if kind == 'gui_settings':
        return {key: _field(obj, key, 'bool') for key in
                ('enable_system_proxy', 'enable_tun_mode', 'enable_auto_launch')}
    out = {key: _field(obj, key, 'port') for key in
           ('port', 'socks-port', 'mixed-port', 'redir-port', 'tproxy-port')}
    out.update({key: _field(obj, key, 'bool') for key in ('allow-lan', 'ipv6')})
    out['mode'] = _field(obj, 'mode', {'rule', 'global', 'direct'})
    for section, fields in {'tun': {'enable': 'bool', 'auto-route': 'bool',
                                   'strict-route': 'bool', 'stack': {'system', 'gvisor', 'mixed'}},
                            'dns': {'enable': 'bool', 'ipv6': 'bool', 'respect-rules': 'bool',
                                    'enhanced-mode': {'fake-ip', 'redir-host'}}}.items():
        sub = obj.get(section)
        out[section] = {key: _field(sub if isinstance(sub, dict) else {}, key, typ)
                        for key, typ in fields.items()}
    out['controller_authentication'] = {'state': 'unknown', 'value': None}
    if 'secret' in obj and isinstance(obj['secret'], str):
        out['controller_authentication'] = {'state': 'observed', 'value': bool(obj['secret'])}
    groups = obj.get('proxy-groups')
    out['groups'] = {'state': 'unknown', 'value': None}
    if isinstance(groups, list):
        projected = []
        for index, group in enumerate(groups):
            if not isinstance(group, dict):
                _fail()
            members = group.get('proxies')
            projected.append({'group_ref': 'group-%d' % (index + 1),
                              'type': _field(group, 'type', {'select', 'url-test', 'fallback', 'load-balance', 'relay'}),
                              'direct_candidate': {'state': 'observed' if isinstance(members, list) else 'unknown',
                                                   'value': 'DIRECT' in members if isinstance(members, list) else None},
                              'runtime_selection': {'state': 'unknown', 'value': None}})
        out['groups'] = {'state': 'observed', 'value': projected}
    rules = obj.get('rules')
    out['rule_count'] = {'state': 'observed' if isinstance(rules, list) else 'unknown',
                         'value': len(rules) if isinstance(rules, list) else None}
    out['rule_matching'] = {'state': 'unknown', 'value': None}
    return out


def audit_inventory(request, expected_target_ref, cancel_check=None):
    """Return only sanitized static evidence or structured errors, never raise raw errors.

    request keys: schema_version=guardian-clash-inventory/0.1, target_ref,
    target_binding, operation=audit, contact_phase=precontact, gate_state=closed,
    authorization={approved_paths:[absolute paths], local_hydrated_files:True},
    application={product:clash-verge-rev, gui_version:2.5.5, core_version:1.19.0},
    files=[{source_ref:alias, kind:one of LAYERS, path:absolute path}].
    The authorization object is host evidence, not a mechanism for obtaining consent.
    Optional cancel_check() returns True to cancel. The 90-second cooperative budget
    bounds parser work between events; filesystem stalls require a host timeout.
    """
    report = {'schema_version': 'guardian-clash-inventory/0.1', 'operation': 'audit',
              'module_ids': ['ENV-02'], 'status': 'partial', 'changes': [],
              'contact_phase': 'precontact', 'gate_state': 'closed',
              'collector_external_network': 'forbidden', 'files': [], 'errors': [],
              'runtime': {'state': 'unknown', 'coverage': 'not_collected'},
              'snapshot': {'state': 'unknown', 'scope': 'approved_static_files_only'},
              'provenance': 'partial', 'conflicts': [],
              'limitations': ['No runtime, active-profile, listener or process verification',
                              'No extension merge, JavaScript evaluation or rule matching',
                              'Version metadata supplied by host; native acceptance not_run',
                              'Storage locality/hydration requires prior host validation',
                              'No cross-session revision or group identity guarantee']}
    deadline = time.monotonic() + MAX_SECONDS

    def check_budget():
        if cancel_check is not None:
            try:
                cancelled = bool(cancel_check())
            except Exception:
                _fail('INVENTORY_CALLBACK_FAILED')
            if cancelled:
                _fail('USER_CANCELLED')
        if time.monotonic() >= deadline:
            _fail('BUDGET_EXCEEDED')

    try:
        # Reject unknown typed envelope fields before invoking host callbacks or
        # reading any source. Raw configuration keys remain parser inputs below.
        nested_keys = {
            'target_binding': {'target_ref', 'binding_state', 'declared_os',
                               'execution_location', 'desktop_user_relation', 'filesystem_namespace'},
            'authorization': {'approved_paths', 'local_hydrated_files'},
            'application': {'product', 'gui_version', 'core_version'},
        }
        if isinstance(request, dict):
            for key, allowed_keys in nested_keys.items():
                if key in request and (type(request[key]) is not dict or set(request[key]) - allowed_keys):
                    _fail()
        check_budget()
        if not isinstance(request, dict):
            _fail()
        allowed = {'schema_version', 'target_ref', 'target_binding', 'operation', 'contact_phase',
                   'gate_state', 'authorization', 'application', 'files'}
        if set(request) - allowed:
            _fail()
        if request.get('operation') != 'audit' or request.get('contact_phase') != 'precontact' or request.get('gate_state') != 'closed':
            _fail('PRECONTACT_ACTION_REJECTED')
        if request.get('schema_version') != report['schema_version']:
            _fail()
        target = _alias(request.get('target_ref'))
        if target != expected_target_ref:
            _fail('TARGET_NOT_BOUND')
        binding = request.get('target_binding')
        if not isinstance(binding, dict) or binding.get('binding_state') != 'bound' or binding.get('target_ref') != target:
            _fail('TARGET_NOT_BOUND')
        if any(binding.get(k) != v for k, v in {'execution_location': 'native_local',
               'desktop_user_relation': 'same', 'filesystem_namespace': 'host_desktop'}.items()):
            _fail('TARGET_USER_CONTEXT_MISMATCH')
        if binding.get('declared_os') not in {'macos', 'windows'}:
            _fail('UNSUPPORTED_PRODUCT_OR_VERSION')
        if {'macos': 'darwin', 'windows': 'win32'}[binding['declared_os']] != sys.platform:
            _fail('TARGET_USER_CONTEXT_MISMATCH')
        report['target_ref'] = target
        authorization = request.get('authorization')
        if not isinstance(authorization, dict) or authorization.get('local_hydrated_files') is not True:
            _fail('AUTHORIZATION_MISSING')
        approved = authorization.get('approved_paths')
        if not isinstance(approved, list) or not 1 <= len(approved) <= MAX_FILES:
            _fail('AUTHORIZATION_MISSING')
        approved = {_path(p) for p in approved}
        app = request.get('application')
        if not isinstance(app, dict) or app.get('product') != 'clash-verge-rev' or app.get('gui_version') not in SCHEMA_FIXTURE_GUI_VERSIONS or app.get('core_version') not in SCHEMA_FIXTURE_CORE_VERSIONS:
            _fail('UNSUPPORTED_PRODUCT_OR_VERSION')
        report['application'] = {'state': 'reported', 'product': 'clash-verge-rev',
                                  'gui_version': app['gui_version'], 'core_version': app['core_version'],
                                  'version_scope': 'synthetic_schema_fixture_only',
                                  'native_compatibility': 'not_validated'}
        files = request.get('files')
        if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
            _fail('BUDGET_EXCEEDED')
        selected, refs, paths = [], set(), set()
        for item in files:
            if not isinstance(item, dict) or set(item) != {'source_ref', 'kind', 'path'}:
                _fail()
            ref, path = _alias(item['source_ref']), _path(item['path'])
            if ref in refs or path in paths or item['kind'] not in LAYERS:
                _fail()
            if path not in approved:
                _fail('AUTHORIZATION_MISSING')
            refs.add(ref); paths.add(path)
            selected.append((ref, path, item['kind']))
        if yaml is None:
            _fail('RUNTIME_OR_PARSER_UNAVAILABLE')
        snapshots = []
        for ref, path, kind in selected:
            check_budget()
            try:
                raw, snapshot = _read(path)
                check_budget()
                values = _project(_parse(raw, check_budget), kind)
                check_budget()
                revision = 'revision-' + uuid.uuid4().hex
                report['files'].append({'source_ref': ref, 'source_revision': revision,
                                        'layer': LAYERS[kind], 'kind': kind, 'state': 'observed',
                                        'observed_at': datetime.now(timezone.utc).isoformat(),
                                        'coverage': 'static_declaration_only', 'values': values})
                snapshots.append((ref, path, snapshot))
            except InventoryError as exc:
                if exc.code in {'USER_CANCELLED', 'BUDGET_EXCEEDED', 'INVENTORY_CALLBACK_FAILED'}:
                    raise
                report['errors'].append({'source_ref': ref, 'code': _public_code(exc.code)})
        for ref, path, before in snapshots:
            check_budget()
            try:
                _, after = _read(path)
                check_budget()
                if before != after:
                    _fail('SNAPSHOT_CHANGED_DURING_AUDIT')
            except InventoryError as exc:
                if exc.code in {'USER_CANCELLED', 'BUDGET_EXCEEDED', 'INVENTORY_CALLBACK_FAILED'}:
                    raise
                report['errors'].append({'source_ref': ref, 'code': 'SNAPSHOT_CHANGED_DURING_AUDIT'})
                for entry in report['files']:
                    if entry['source_ref'] == ref:
                        entry['state'] = 'stale'
        check_budget()
        report['snapshot']['state'] = ('changed' if any(e['code'] == 'SNAPSHOT_CHANGED_DURING_AUDIT' for e in report['errors'])
                                        else 'incomplete' if report['errors'] else 'stable_observed_subset')
        for field in ('mode', 'mixed-port', 'ipv6', 'allow-lan'):
            values = [(entry['source_ref'], entry['values'].get(field, {})) for entry in report['files'] if entry['state'] == 'observed']
            observed = [(ref, value['value']) for ref, value in values if value.get('state') == 'observed']
            if len({value for _, value in observed}) > 1:
                report['conflicts'].append({'field': field, 'source_refs': [ref for ref, _ in observed], 'state': 'conflict', 'resolution': 'layer_precedence_not_inferred'})
        check_budget()
    except InventoryError as exc:
        report['snapshot']['state'] = 'unknown'
        report['errors'].append({'code': _public_code(exc.code)})
        report['status'] = 'blocked'
    except Exception:
        report['snapshot']['state'] = 'unknown'
        report['errors'].append({'code': 'INPUT_OR_RESPONSE_INVALID'})
        report['status'] = 'blocked'
    return report
