"""Pure ENV-06 semantic planning. No I/O, raw configuration, or apply interface.

Inputs are explicitly supplied, sanitized projections, not trusted observations.
A successful compile is never native acceptance or permission to change a system.
"""
from copy import deepcopy
import re

try:
    from traffic_policy import policy_projection
except ModuleNotFoundError as _policy_import_error:
    if _policy_import_error.name != 'traffic_policy':
        raise
    # Preserve the existing standalone file-path import API without changing
    # sys.path or depending on another test/module having imported siblings.
    import importlib.util as _policy_importlib
    import sys as _policy_sys
    from pathlib import Path as _PolicyPath
    _policy_spec = _policy_importlib.spec_from_file_location(
        '_guardian_traffic_policy', _PolicyPath(__file__).with_name('traffic_policy.py'))
    _policy_module = _policy_importlib.module_from_spec(_policy_spec)
    _policy_sys.modules[_policy_spec.name] = _policy_module
    _policy_spec.loader.exec_module(_policy_module)
    policy_projection = _policy_module.policy_projection

SCHEMA = 'guardian-remedy-plan-input/0.1'
TEMPLATES = ('keep-existing', 'explicit-rule', 'tun-rule', 'scoped-compatibility')
_ALIAS = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,63}\Z')
_REVISION = re.compile(r'[a-f0-9]{64}\Z')
_VERSION = re.compile(r'\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?\Z')


class InvalidProjection(ValueError):
    """Malformed or unsanitized input; message deliberately excludes input values."""


def _object(value, allowed, required=()):
    if not isinstance(value, dict) or set(value) - set(allowed) or set(required) - set(value):
        raise InvalidProjection('invalid object shape')


def _alias(value):
    if not isinstance(value, str) or not _ALIAS.fullmatch(value):
        raise InvalidProjection('expected opaque reference')


def _aliases(value):
    if not isinstance(value, list) or len(value) > 256:
        raise InvalidProjection('expected bounded reference list')
    for item in value:
        _alias(item)
    if len(set(value)) != len(value):
        raise InvalidProjection('duplicate reference')


def _enum(value, choices):
    if not isinstance(value, str) or value not in choices:
        raise InvalidProjection('invalid enum')


def _tri(value):
    _enum(value, ('yes', 'no', 'unknown'))


def _revisions(value):
    if not isinstance(value, dict) or not value or len(value) > 32:
        raise InvalidProjection('expected revision map')
    for key, revision in value.items():
        _alias(key)
        if not isinstance(revision, str) or not _REVISION.fullmatch(revision):
            raise InvalidProjection('expected sha256 revision')


def _validate(request):
    _object(request, ('schema_version', 'target_ref', 'observed_target_ref', 'revisions',
                     'current_revisions', 'revision_refs', 'template', 'route_ref', 'scope_refs', 'facts',
                     'intent', 'cancelled'),
            ('schema_version', 'target_ref', 'observed_target_ref', 'revisions',
             'current_revisions', 'revision_refs', 'template', 'route_ref', 'scope_refs', 'facts', 'intent'))
    if request['schema_version'] != SCHEMA:
        raise InvalidProjection('unknown input schema')
    for key in ('target_ref', 'observed_target_ref', 'route_ref'):
        _alias(request[key])
    _enum(request['template'], TEMPLATES)
    _aliases(request['scope_refs'])
    if not request['scope_refs']:
        raise InvalidProjection('explicit scope required')
    for key in ('revisions', 'current_revisions'):
        _revisions(request[key])
    refs = request['revision_refs']
    if not isinstance(refs, dict) or set(refs) != set(request['revisions']):
        raise InvalidProjection('revision aliases must match private snapshot layers')
    private_digests = set(request['revisions'].values()) | set(request['current_revisions'].values())
    for value in refs.values():
        _alias(value)
        if re.fullmatch(r'[a-fA-F0-9]{64}', value) or value in private_digests:
            raise InvalidProjection('public snapshot alias must not be a private digest')
    if 'cancelled' in request and type(request['cancelled']) is not bool:
        raise InvalidProjection('cancelled must be boolean')
    facts = request['facts']
    _object(facts, ('versions', 'mode', 'explicit', 'tun', 'control', 'dns', 'groups',
                    'ipv6', 'udp', 'rules', 'ownership', 'compatibility'))
    versions = facts.get('versions', {})
    _object(versions, ('product', 'gui', 'core'))
    if 'product' in versions:
        _enum(versions['product'], ('clash-verge-rev', 'clash-verge', 'mihomo', 'unknown'))
    for key in ('gui', 'core'):
        if key in versions and (not isinstance(versions[key], str) or
                                (versions[key] != 'unknown' and not _VERSION.fullmatch(versions[key]))):
            raise InvalidProjection('invalid version')
    if 'mode' in facts:
        _enum(facts['mode'], ('rule', 'global', 'direct', 'unknown'))
    if 'explicit' in facts:
        _object(facts['explicit'], ('entry_ref', 'kind', 'adoption'), ('kind', 'adoption'))
        _enum(facts['explicit']['kind'], ('http', 'mixed', 'socks', 'unknown'))
        _tri(facts['explicit']['adoption'])
        if 'entry_ref' in facts['explicit']:
            _alias(facts['explicit']['entry_ref'])
    for key in ('tun', 'control', 'rules', 'ownership', 'compatibility'):
        shapes = {'tun': ('enabled', 'scope_known', 'vpn_vm_compatible'),
                  'control': ('dependency_known', 'preserved', 'rescue_available', 'scope_refs'),
                  'rules': ('first_match_verified', 'protected_priority_preserved', 'complete'),
                  'ownership': ('known', 'persistent_extension_available', 'gui_readback_available'),
                  'compatibility': ('scope_supported', 'ipv6_outer_node_required')}
        if key in facts:
            _object(facts[key], shapes[key])
            for field, value in facts[key].items():
                _aliases(value) if field == 'scope_refs' else _tri(value)
    for key in ('ipv6', 'udp'):
        if key in facts:
            _enum(facts[key], ('verified', 'unknown', 'unsupported'))
    if 'groups' in facts:
        groups = facts['groups']
        if not isinstance(groups, dict) or len(groups) > 256:
            raise InvalidProjection('invalid groups')
        for key, value in groups.items():
            _alias(key)
            _object(value, ('members', 'complete', 'kind', 'protocol'), ('members', 'complete'))
            if 'kind' in value:
                _enum(value['kind'], ('group', 'proxy', 'direct', 'reject', 'unknown'))
            if 'protocol' in value:
                _enum(value['protocol'], ('http', 'socks5', 'shadowsocks', 'vmess', 'vless', 'trojan', 'hysteria2', 'tuic', 'wireguard', 'unknown'))
            if value.get('kind') in ('proxy', 'direct', 'reject') and value['members']:
                raise InvalidProjection('terminal cannot have members')
            _aliases(value['members'])
            _tri(value['complete'])
    if 'dns' in facts:
        dns = facts['dns']
        _object(dns, ('nodes', 'edges', 'complete', 'local_preserved', 'browser_doh_known',
                      'bootstrap_known', 'policy_merge_known', 'responsibility'), ('nodes', 'edges'))
        _aliases(dns['nodes'])
        if 'responsibility' in dns:
            _enum(dns['responsibility'], ('system', 'mihomo', 'application', 'mixed', 'unknown'))
        for key in ('complete', 'local_preserved', 'browser_doh_known', 'bootstrap_known', 'policy_merge_known'):
            if key in dns:
                _tri(dns[key])
        if not isinstance(dns['edges'], list) or len(dns['edges']) > 1024:
            raise InvalidProjection('invalid dependency edges')
        for edge in dns['edges']:
            _object(edge, ('from', 'to', 'path'), ('from', 'to', 'path'))
            _alias(edge['from'])
            _alias(edge['to'])
            _enum(edge['path'], ('normal', 'failure', 'both'))
            if edge['from'] not in dns['nodes'] or edge['to'] not in dns['nodes']:
                raise InvalidProjection('unregistered dependency node')
    intent = request['intent']
    _object(intent, ('rule_refs', 'diagnostic_rule_refs', 'egress_group_ref', 'no_direct',
                     'ipv6_goal', 'udp_goal', 'compatibility_action'))
    for key in ('rule_refs', 'diagnostic_rule_refs'):
        if key in intent:
            _aliases(intent[key])
    if 'egress_group_ref' in intent:
        _alias(intent['egress_group_ref'])
    if 'no_direct' in intent:
        _tri(intent['no_direct'])
    for key in ('ipv6_goal', 'udp_goal'):
        if key in intent:
            _enum(intent[key], ('preserve', 'proxy', 'block', 'unknown'))
    if 'compatibility_action' in intent:
        _enum(intent['compatibility_action'], ('ipv4-only', 'restrict-webrtc', 'manual-egress'))


def _cyclic(nodes, edges):
    """Bounded iterative topological check avoids recursion on adversarial graphs."""
    successors = {node: set() for node in nodes}
    indegree = dict.fromkeys(nodes, 0)
    for source, dest in edges:
        if dest not in successors[source]:
            successors[source].add(dest)
            indegree[dest] += 1
    queue = [node for node in nodes if not indegree[node]]
    visited = 0
    while queue:
        node = queue.pop()
        visited += 1
        for dest in successors[node]:
            indegree[dest] -= 1
            if not indegree[dest]:
                queue.append(dest)
    return visited != len(nodes)


def compile_plan(request):
    """Compile a bounded projected-facts dictionary without mutating or reading anything.

    Raises InvalidProjection for malformed input. Valid but incomplete observations
    produce semantic proposals with explicit blockers; no native patch is produced.
    """
    _validate(request)
    result = {'schema_version': 'guardian-remedy-plan/0.1', 'status': 'blocked',
              'target_ref': request['target_ref'], 'route_ref': request['route_ref'],
              'traffic_policy': policy_projection(),
              'template': request['template'], 'revision_refs': deepcopy(request['revision_refs']),
              'proposed_changes': [], 'blockers': [], 'dns_checks': {},
              'protected_control_path': {'status': 'unknown'},
              'apply_supported': False, 'evidence': 'offline_projected_facts',
              'requirements': {
                  'backup': ['private version-bound snapshot of affected owned layers',
                             'verify content hashes, ownership, permissions and restoration path',
                             'never export credentials or subscription contents to this plan'],
                  'rollback': ['retain original affected values and revision bindings locally',
                               'restore only owned changes after conflict check',
                               'stop on intervening edits; preserve recovery/control connectivity',
                               'read back effective configuration after recovery'],
                  'acceptance': ['explicit action-specific authorization before any write',
                                 'version-specific schema and GUI ownership/merge validation',
                                 'review native validation side effects before execution',
                                 'effective GUI/core readback, first-match and real-path evidence',
                                 'repeat-application and subscription-refresh validation']}}

    def block(code, state='unknown'):
        item = {'code': code, 'state': state}
        if item not in result['blockers']:
            result['blockers'].append(item)

    if request.get('cancelled'):
        block('CANCELLED', 'blocked')
        return result
    if request['target_ref'] != request['observed_target_ref']:
        block('TARGET_MISMATCH', 'blocked')
    if request['revisions'] != request['current_revisions']:
        block('STALE_REVISIONS', 'blocked')
    if result['blockers']:
        return result
    facts, intent, template = request['facts'], request['intent'], request['template']
    block('NATIVE_SCHEMA_ADAPTER_NOT_IMPLEMENTED')
    block('NATIVE_ACCEPTANCE_NOT_RUN')
    versions = facts.get('versions', {})
    if any(versions.get(key, 'unknown') == 'unknown' for key in ('product', 'gui', 'core')):
        block('VERSION_UNKNOWN')
    else:
        block('VERSION_CAPABILITY_UNVERIFIED')
    control = facts.get('control', {})
    result['protected_control_path'] = {
        'status': 'projected_preserved' if control.get('preserved') == 'yes' and control.get('scope_refs') else 'unknown',
        'scope_refs': deepcopy(control.get('scope_refs', [])),
        'native_verified': False}
    if not control.get('scope_refs'):
        block('CONTROL_SCOPE_REFS_MISSING')
    for field in ('dependency_known', 'preserved', 'rescue_available'):
        if control.get(field) != 'yes':
            block('CONTROL_' + field.upper(), 'blocked' if control.get(field) == 'no' else 'unknown')
    if set(request['scope_refs']) & set(control.get('scope_refs', [])):
        block('CONTROL_SCOPE_OVERLAP', 'blocked')
    if facts.get('mode') != 'rule' and (template != 'scoped-compatibility' or intent.get('rule_refs') or intent.get('diagnostic_rule_refs')):
        block('RULE_MODE_CONFLICT' if facts.get('mode') in ('global', 'direct') else 'RULE_MODE_UNKNOWN',
              'blocked' if facts.get('mode') in ('global', 'direct') else 'unknown')
    for section, fields in {
        'rules': ('first_match_verified', 'protected_priority_preserved', 'complete'),
        'ownership': ('known', 'persistent_extension_available', 'gui_readback_available')}.items():
        for field in fields:
            if facts.get(section, {}).get(field) != 'yes':
                block(section.upper() + '_' + field.upper())

    def propose(kind, **values):
        result['proposed_changes'].append({'kind': kind, 'scope_refs': deepcopy(request['scope_refs']), **values})

    rule_refs = intent.get('rule_refs', [])
    if rule_refs:
        propose('bind_selected_rules', rule_refs=deepcopy(rule_refs),
                egress_group_ref=intent.get('egress_group_ref'),
                preserve=['organization_rules', 'rescue_routes', 'lan_routes', 'global_match', 'other_workflows'])
    elif template != 'scoped-compatibility':
        block('WORKFLOW_RULES_MISSING')
    if intent.get('diagnostic_rule_refs'):
        propose('temporary_diagnostic_rules', rule_refs=deepcopy(intent['diagnostic_rule_refs']),
                removal_required=True)
    if rule_refs and not intent.get('egress_group_ref'):
        block('EGRESS_GROUP_MISSING')
    groups = facts.get('groups', {})
    pending = [intent['egress_group_ref']] if intent.get('egress_group_ref') else []
    seen = set()
    while pending:
        ref = pending.pop()
        if ref in seen:
            continue
        seen.add(ref)
        group = groups.get(ref)
        if not group or group['complete'] != 'yes':
            block('EGRESS_GRAPH_INCOMPLETE')
        kind = group.get('kind', 'unknown') if group else 'unknown'
        if kind == 'unknown':
            block('EGRESS_NODE_TYPE_UNKNOWN')
        if kind == 'direct' and intent.get('no_direct') == 'yes':
            block('DIRECT_FALLBACK', 'blocked')
        if kind == 'proxy' and group.get('protocol', 'unknown') == 'unknown':
            block('EGRESS_PROTOCOL_UNKNOWN')
        if kind == 'group' and not group['members']:
            block('EMPTY_EGRESS_GROUP')
        if group:
            pending.extend(group['members'])
    if seen and _cyclic(sorted(seen), [(key, dest) for key in seen if key in groups
                                     for dest in groups[key]['members'] if dest in seen]):
        block('EGRESS_GRAPH_CYCLE', 'blocked')
    if template == 'explicit-rule':
        entry = facts.get('explicit', {})
        if entry.get('kind') not in ('http', 'mixed') or not entry.get('entry_ref'):
            block('HTTP_MIXED_ENTRY_UNCONFIRMED')
        else:
            propose('selected_application_proxy_binding', entry_ref=entry['entry_ref'],
                    preserve_existing_tun_vpn=True, coverage='selected applications only')
        if entry.get('adoption') != 'yes':
            block('APPLICATION_PROXY_ADOPTION_UNVERIFIED')
    elif template == 'tun-rule':
        propose('scoped_tun_route_intent', preserve=['proxy_bootstrap', 'control_path', 'vpn_vm', 'lan_services'])
        for field in ('scope_known', 'vpn_vm_compatible'):
            if facts.get('tun', {}).get(field) != 'yes':
                block('TUN_' + field.upper())
        if facts.get('explicit', {}).get('adoption') == 'yes':
            block('COMBINED_MODE_LOOP_EXCLUSIONS_UNVERIFIED')
    elif template == 'scoped-compatibility':
        action = intent.get('compatibility_action')
        if not action:
            block('COMPATIBILITY_ACTION_MISSING')
        else:
            propose('scoped_compatibility_intent', action=action, whole_machine=False,
                    preserve=['certificate_validation', 'actual_region', 'proxy_outer_transport'])
        if facts.get('compatibility', {}).get('scope_supported') != 'yes':
            block('COMPATIBILITY_SCOPE_UNVERIFIED')
        if action == 'ipv4-only' and facts.get('compatibility', {}).get('ipv6_outer_node_required') != 'no':
            block('OUTER_NODE_ADDRESS_FAMILY_DEPENDENCY_UNKNOWN')
    for protocol in ('ipv6', 'udp'):
        goal = intent.get(protocol + '_goal', 'unknown')
        if goal == 'unknown' or facts.get(protocol) != 'verified':
            block(protocol.upper() + '_PATH_UNVERIFIED')
        if goal in ('proxy', 'block'):
            propose('scoped_protocol_intent', protocol=protocol, goal=goal,
                    proof_required=True, system_wide_guarantee=False)
    dns = facts.get('dns', {})
    nodes, edges = dns.get('nodes', []), dns.get('edges', [])
    if not nodes:
        block('DNS_GRAPH_MISSING')
    if dns.get('responsibility', 'unknown') == 'unknown':
        block('DNS_RESPONSIBILITY_UNKNOWN')
    if template in ('explicit-rule', 'tun-rule'):
        propose('dns_responsibility_intent', responsibility=dns.get('responsibility', 'unknown'),
                preserve=['local_resolution', 'fake_ip_filters', 'node_bootstrap', 'corporate_dns'],
                resolver_selection='existing verified or separately user-selected provider only')
    result['dns_checks'] = {'nodes': deepcopy(nodes), 'edges': deepcopy(edges),
                            'scope': 'declared dependencies only; no resolver requests'}
    for path in ('normal', 'failure'):
        cycle = _cyclic(nodes, [(edge['from'], edge['to']) for edge in edges if edge['path'] in (path, 'both')])
        result['dns_checks'][path] = 'cycle' if cycle else ('acyclic_projected' if nodes else 'unknown')
        if cycle:
            block('DNS_' + path.upper() + '_CYCLE', 'blocked')
    for field in ('complete', 'local_preserved', 'browser_doh_known', 'bootstrap_known', 'policy_merge_known'):
        if dns.get(field) != 'yes':
            block('DNS_' + field.upper(), 'blocked' if dns.get(field) == 'no' else 'unknown')
    result['dns_checks']['local_resolution'] = 'projected_preserved' if dns.get('local_preserved') == 'yes' else 'unknown'
    result['dns_checks']['policy_rule'] = 'preserve full effective nameserver-policy; never deep-merge blindly'
    return result

