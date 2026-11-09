"""Read-only linkage validation for supplied Clash Verge Rev 2.5.8 snapshots.

Source: official v2.5.8, commit 4337bd85758d54d7b9044b2da3c9ac1176eae1f3.
This offline adapter does not establish native ownership, active runtime,
writer exclusion, user approval, or application-effective acceptance.
"""
import hashlib
import plistlib
import re
import time
from xml.parsers.expat import ExpatError

import config_edit_plan as compiler

VERSION = '2.5.8'
SOURCE_COMMIT = '4337bd85758d54d7b9044b2da3c9ac1176eae1f3'
MAX_PLIST_BYTES = 256 * 1024
BASENAME = re.compile(r'[A-Za-z0-9_-]{1,120}\.yaml\Z')


class OwnershipError(ValueError):
    """Fixed privacy-preserving failure codes only."""


def _fail(code):
    raise OwnershipError(code) from None


def _scalar(node):
    yaml = compiler.yaml
    if not isinstance(node, yaml.nodes.ScalarNode) or node.tag != 'tag:yaml.org,2002:str':
        _fail('INVALID_PROFILE_INDEX')
    return node.value


def _map(node):
    try:
        return compiler._mapping(node)
    except compiler.EditPlanError:
        _fail('INVALID_PROFILE_INDEX')


def _parse(raw):
    try:
        return compiler._parse(raw)[1]
    except compiler.EditPlanError as exc:
        if str(exc) == 'PARSER_UNAVAILABLE':
            _fail('PARSER_UNAVAILABLE')
        _fail('INVALID_OR_UNSUPPORTED_YAML')


class _StrictPlistDict(dict):
    def __setitem__(self, key, value):
        if type(key) is not str or key in self:
            _fail('DUPLICATE_OR_INVALID_APP_METADATA_KEY')
        if len(self) >= 4096:
            _fail('APP_METADATA_BUDGET_EXCEEDED')
        super().__setitem__(key, value)


def _plist(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_PLIST_BYTES:
        _fail('INVALID_APP_METADATA')
    try:
        value = plistlib.loads(raw, dict_type=_StrictPlistDict)
        budget = 4096
        stack = [(value, 0)]
        while stack:
            item, depth = stack.pop()
            budget -= 1
            if budget < 0 or depth > 32:
                _fail('APP_METADATA_BUDGET_EXCEEDED')
            if isinstance(item, dict):
                stack.extend((child, depth + 1) for child in item.values())
            elif type(item) is list:
                stack.extend((child, depth + 1) for child in item)
        if not isinstance(value, dict):
            _fail('INVALID_APP_METADATA')
        return value
    except OwnershipError:
        raise
    except (ValueError, TypeError, OverflowError, RecursionError, plistlib.InvalidFileException, ExpatError):
        _fail('INVALID_APP_METADATA')


class PrivateLinkage:
    __slots__ = ('_material', '_blockers', '_extension_kind')

    def __init__(self, material, blockers, extension_kind='merge'):
        self._extension_kind = extension_kind
        self._material = tuple(sorted(material.items()))
        self._blockers = tuple(blockers)

    def __repr__(self):
        return '<PrivateLinkage: supplied metadata only; native execution blocked>'

    def __reduce_ex__(self, protocol):
        raise TypeError('private linkage serialization disabled')

    def private_material(self):
        return dict(self._material)

    def public_report(self):
        return {'schema_version': 'guardian-clash258-linkage/0.1',
                'status': 'supplied_metadata_only', 'product': 'clash-verge-rev',
                'version': VERSION, 'source_commit': SOURCE_COMMIT,
                'format': 'existing_merge_mapping' if self._extension_kind == 'merge' else 'rules_seqmap',
                'rule_merge_semantics': ('replaces_base_rules_sequence' if self._extension_kind == 'merge'
                                         else 'prepend_then_filtered_base_then_append'),
                'apply_supported': False, 'native_ownership': 'not_verified',
                'native_acceptance': 'not_run', 'writer_exclusion': 'not_established',
                'blockers': list(self._blockers)}


def inspect_linkage(app_plist, profile_index, extension, *, selected_uid, selected_basename,
                    max_seconds=5, cancelled=lambda: False, extension_kind='merge'):
    """Inspect only supplied bytes; no file paths are opened or discovered.

    A matched bundle/version string proves the supplied metadata's declaration,
    not code signature, process identity, installed version or runtime ownership.
    The caller must bind all three snapshots to actual approved native reads.
    """
    if type(max_seconds) not in (int, float) or not 0 < max_seconds <= 60:
        _fail('INVALID_DEADLINE')
    deadline = time.monotonic() + max_seconds
    def guard():
        try:
            stopped = cancelled()
        except Exception:
            _fail('CANCELLED')
        if stopped:
            _fail('CANCELLED')
        if time.monotonic() >= deadline:
            _fail('DEADLINE_EXCEEDED')
    guard()
    if extension_kind not in ('merge', 'rules'):
        _fail('UNSUPPORTED_EXTENSION_TYPE')
    if (type(selected_uid) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', selected_uid)
            or type(selected_basename) is not str or not BASENAME.fullmatch(selected_basename)):
        _fail('INVALID_EXTENSION_SELECTION')
    if selected_uid.casefold() in {'merge', 'script', 'rules', 'proxies', 'groups'}:
        _fail('GLOBAL_OR_DEFAULT_EXTENSION_SCOPE_UNSUPPORTED')
    info = _plist(app_plist)
    if (info.get('CFBundleIdentifier') != 'io.github.clash-verge-rev.clash-verge-rev'
            or info.get('CFBundleShortVersionString') != VERSION
            or info.get('CFBundleVersion') != VERSION):
        _fail('UNSUPPORTED_PRODUCT_OR_VERSION')
    guard()
    index = _map(_parse(profile_index))
    guard()
    current = _scalar(index.get('current'))
    items = index.get('items')
    if not isinstance(items, compiler.yaml.nodes.SequenceNode) or not 1 <= len(items.value) <= 1024:
        _fail('INVALID_PROFILE_INDEX')
    by_uid = {}
    for node in items.value:
        guard()
        item = _map(node)
        uid = _scalar(item.get('uid'))
        if not uid or len(uid) > 128 or uid in by_uid:
            _fail('DUPLICATE_OR_INVALID_PROFILE_UID')
        if 'file' in item:
            filename_value = _scalar(item['file'])
            if not re.fullmatch(r'[A-Za-z0-9_-]{1,120}\.(?:yaml|yml|js)', filename_value):
                _fail('UNSAFE_PROFILE_FILE_REFERENCE')
        by_uid[uid] = item
    if current not in by_uid or selected_uid not in by_uid:
        _fail('PROFILE_LINK_MISSING')
    active, selected = by_uid[current], by_uid[selected_uid]
    if _scalar(active.get('type')) not in ('local', 'remote'):
        _fail('UNSUPPORTED_ACTIVE_PROFILE_TYPE')
    option = _map(active.get('option'))
    if _scalar(option.get(extension_kind)) != selected_uid:
        _fail('SELECTED_EXTENSION_NOT_ACTIVE_' + extension_kind.upper())
    if _scalar(selected.get('type')) != extension_kind:
        _fail('UNSUPPORTED_EXTENSION_TYPE')
    for uid, item in by_uid.items():
        if uid == current:
            continue
        kind = _scalar(item.get('type'))
        if kind not in ('local', 'remote'):
            continue
        other_option = item.get('option')
        if other_option is None or getattr(other_option, 'tag', '') == 'tag:yaml.org,2002:null':
            continue
        other_options = _map(other_option)
        for key in ('merge', 'rules', 'script', 'groups', 'proxies'):
            node = other_options.get(key)
            if node is not None and getattr(node, 'tag', '') != 'tag:yaml.org,2002:null':
                if _scalar(node) == selected_uid:
                    _fail('SHARED_EXTENSION_SCOPE_UNSUPPORTED')
    filename = _scalar(selected.get('file'))
    if filename != selected_basename or not BASENAME.fullmatch(filename):
        _fail('EXTENSION_FILE_MISMATCH')
    # Duplicate aliases to the selected file obscure ownership even with distinct IDs.
    if sum(_scalar(item['file']).casefold() == filename.casefold() for item in by_uid.values()
           if 'file' in item) != 1:
        _fail('AMBIGUOUS_EXTENSION_FILE_OWNER')
    guard()
    merge = _map(_parse(extension))
    guard()
    if extension_kind == 'merge':
        if (not isinstance(merge.get('rules'), compiler.yaml.nodes.SequenceNode)
                or not isinstance(merge.get('proxy-groups'), compiler.yaml.nodes.SequenceNode)):
            _fail('UNSUPPORTED_EXISTING_MERGE_FORMAT')
        if any(key in merge for key in ('prepend', 'append', 'delete')):
            _fail('RULES_EXTENSION_FORMAT_NOT_MERGE')
    else:
        for key in ('prepend', 'append', 'delete'):
            node = merge.get(key)
            if not isinstance(node, compiler.yaml.nodes.SequenceNode):
                _fail('UNSUPPORTED_RULES_SEQMAP_FORMAT')
            if any(not isinstance(item, compiler.yaml.nodes.ScalarNode)
                   or item.tag != 'tag:yaml.org,2002:str' for item in node.value):
                _fail('UNSUPPORTED_RULES_SEQMAP_VALUE')
        if 'rules' in merge or 'proxy-groups' in merge:
            _fail('MERGE_FORMAT_NOT_RULES_EXTENSION')
    blockers = ['NATIVE_CONTEXT_NOT_BOUND', 'WRITER_EXCLUSION_NOT_ESTABLISHED',
                'CORE_VERSION_NOT_VERIFIED', 'EFFECTIVE_MERGE_CHAIN_UNVERIFIED',
                'NATIVE_ACCEPTANCE_NOT_RUN']
    for key in ('script', 'merge', 'rules', 'proxies', 'groups'):
        if key == extension_kind:
            continue
        node = option.get(key)
        if node is not None and getattr(node, 'tag', '') != 'tag:yaml.org,2002:null':
            _scalar(node)
            blockers.append('PROFILE_' + key.upper() + '_CHAIN_UNSUPPORTED')
    # Global Script executes too; its presence is never treated as harmless code.
    if 'Script' in by_uid:
        blockers.append('GLOBAL_SCRIPT_CHAIN_UNSUPPORTED')
    base_basename = None
    if extension_kind == 'rules':
        base_basename = _scalar(active.get('file'))
        if (not BASENAME.fullmatch(base_basename) or base_basename == filename
                or sum(_scalar(item['file']).casefold() == base_basename.casefold() for item in by_uid.values()
                       if 'file' in item) != 1):
            _fail('AMBIGUOUS_OR_UNSUPPORTED_BASE_PROFILE_FILE')
    material = {'current_uid': current, 'extension_uid': selected_uid,
                'extension_basename': filename, 'base_basename': base_basename,
                'app_metadata_sha256': hashlib.sha256(app_plist).hexdigest(),
                'profile_index_sha256': hashlib.sha256(profile_index).hexdigest(),
                'extension_sha256': hashlib.sha256(extension).hexdigest(),
                'source_commit': SOURCE_COMMIT, 'version': VERSION, 'extension_kind': extension_kind}
    guard()
    return PrivateLinkage(material, blockers, extension_kind)
