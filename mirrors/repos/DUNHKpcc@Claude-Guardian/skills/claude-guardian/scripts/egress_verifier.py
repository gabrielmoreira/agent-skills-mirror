"""Read-only judgement of whole-machine IPv4-only egress from supplied observations.

The verifier collects nothing and changes nothing: the Agent supplies what it
actually observed (see references/whole-machine-ipv4.md) and this module decides
which layers are proven. ``established`` needs every required layer to pass; one
definite failure is ``violated``; anything missing stays ``incomplete``. Exit IPs
are compared but never echoed. A passing report supports only the supplied
observations; it is not a service-eligibility, IP-quality or ban-free statement.
"""
import argparse
import ipaddress
import json
import os
import re
import sys

SCHEMA = 'guardian-egress-evidence/0.1'
REPORT_SCHEMA = 'guardian-egress-report/0.1'
MAX_INPUT_BYTES = 64 * 1024
REF = re.compile(r'[A-Za-z0-9._-]{1,64}\Z')
PROCESSES = {'browser', 'terminal', 'other_app', 'background'}
LIFECYCLE = ('restart', 'sleep_wake', 'network_change')
REQUIRED = ('tun', 'core_ipv6', 'dns', 'rules', 'exit_ipv4', 'ipv6_probe', 'webrtc', 'failure_drill')

YES_NO = {'yes', 'no', 'unknown'}
SECTIONS = {
    'tun': {'enabled': YES_NO, 'strict_route': YES_NO, 'default_route_via_tun': YES_NO},
    'core': {'ipv6': {'off', 'on', 'unknown'}},
    'dns': {'ipv6': {'off', 'on', 'unknown'}, 'hijack': YES_NO, 'leak_test': {'pass', 'fail', 'not_run'}},
    'rules': {'final_match': {'proxy', 'direct', 'unknown'},
              'direct_exceptions': {'none', 'listed', 'unlisted', 'unknown'}},
}
SCALARS = {
    'firewall': {'fail_closed', 'not_configured', 'unknown'},
    'os_ipv6': {'disabled', 'enabled', 'unknown'},
    'ipv6_probe': {'unreachable', 'reachable', 'not_run'},
    'webrtc': {'no_leak', 'leak', 'not_run'},
    'failure_drill': {'no_direct', 'direct_observed', 'not_run'},
}
KEYS = {'schema_version', 'platform', 'target_ref', 'samples', 'lifecycle_checked', 'expected_exit',
        *SECTIONS, *SCALARS}


class EvidenceError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _bad(code):
    raise EvidenceError(code) from None


def _ip(value):
    try:
        return ipaddress.ip_address(value)
    except (ValueError, TypeError):
        _bad('INVALID_EXIT_ADDRESS')


def _validate(evidence):
    if type(evidence) is not dict or set(evidence) - KEYS or evidence.get('schema_version') != SCHEMA:
        _bad('INVALID_EVIDENCE')
    if evidence.get('platform') not in ('macos', 'windows', 'linux'):
        _bad('UNSUPPORTED_PLATFORM')
    if type(evidence.get('target_ref')) is not str or not REF.match(evidence['target_ref']):
        _bad('INVALID_TARGET_REF')
    for name, fields in SECTIONS.items():
        section = evidence.get(name)
        if type(section) is not dict or set(section) != set(fields):
            _bad('INVALID_' + name.upper())
        for field, allowed in fields.items():
            if section[field] not in allowed:
                _bad('INVALID_' + name.upper())
    for name, allowed in SCALARS.items():
        if evidence.get(name) not in allowed:
            _bad('INVALID_' + name.upper())
    samples = evidence.get('samples')
    if type(samples) is not list or len(samples) > 20:
        _bad('INVALID_SAMPLES')
    for sample in samples:
        if (type(sample) is not dict or set(sample) != {'family', 'exit', 'process'}
                or sample['family'] not in ('ipv4', 'ipv6') or sample['process'] not in PROCESSES):
            _bad('INVALID_SAMPLES')
        address = _ip(sample['exit'])
        if address.version != int(sample['family'][-1]):
            _bad('INVALID_SAMPLES')
    lifecycle = evidence.get('lifecycle_checked', [])
    if type(lifecycle) is not list or any(item not in LIFECYCLE for item in lifecycle):
        _bad('INVALID_LIFECYCLE')
    if 'expected_exit' in evidence and _ip(evidence['expected_exit']).version != 4:
        _bad('INVALID_EXIT_ADDRESS')


def _combine(statuses):
    if 'fail' in statuses:
        return 'fail'
    if all(item == 'pass' for item in statuses):
        return 'pass'
    return 'not_run' if 'not_run' in statuses and 'unknown' not in statuses else 'unknown'


def _flag(value, good, bad):
    return 'pass' if value == good else 'fail' if value == bad else 'unknown'


def _exit_layer(evidence, blockers):
    samples = evidence['samples']
    v4 = [item for item in samples if item['family'] == 'ipv4']
    if any(item['family'] == 'ipv6' for item in samples):
        blockers.append('IPV6_EXIT_OBSERVED')
        return 'fail'
    if not v4:
        return 'not_run'
    addresses = {str(ipaddress.ip_address(item['exit'])) for item in v4}
    expected = evidence.get('expected_exit')
    if len(addresses) > 1 or (expected is not None and addresses != {str(ipaddress.ip_address(expected))}):
        blockers.append('EXIT_ADDRESS_MISMATCH')
        return 'fail'
    if len({item['process'] for item in v4}) < 2:
        blockers.append('SAMPLES_FROM_ONE_PROCESS_KIND')
        return 'unknown'
    return 'pass'


def judge(evidence):
    _validate(evidence)
    blockers, advisories = [], []
    tun, core, dns, rules = (evidence[name] for name in ('tun', 'core', 'dns', 'rules'))
    layers = {
        'tun': _combine([_flag(tun['enabled'], 'yes', 'no'), _flag(tun['strict_route'], 'yes', 'no'),
                         _flag(tun['default_route_via_tun'], 'yes', 'no')]),
        'core_ipv6': _flag(core['ipv6'], 'off', 'on'),
        'dns': _combine([_flag(dns['ipv6'], 'off', 'on'), _flag(dns['hijack'], 'yes', 'no'),
                         {'pass': 'pass', 'fail': 'fail', 'not_run': 'not_run'}[dns['leak_test']]]),
        'rules': _combine([_flag(rules['final_match'], 'proxy', 'direct'),
                           {'none': 'pass', 'listed': 'pass', 'unlisted': 'fail',
                            'unknown': 'unknown'}[rules['direct_exceptions']]]),
        'exit_ipv4': _exit_layer(evidence, blockers),
        'ipv6_probe': {'unreachable': 'pass', 'reachable': 'fail', 'not_run': 'not_run'}[evidence['ipv6_probe']],
        'webrtc': {'no_leak': 'pass', 'leak': 'fail', 'not_run': 'not_run'}[evidence['webrtc']],
        'failure_drill': {'no_direct': 'pass', 'direct_observed': 'fail', 'not_run': 'not_run'}[evidence['failure_drill']],
    }
    blockers.extend('LAYER_%s_%s' % (name.upper(), layers[name].upper())
                    for name in REQUIRED if layers[name] != 'pass')
    if evidence['firewall'] != 'fail_closed':
        advisories.append('FIREWALL_FAIL_CLOSED_NOT_ESTABLISHED')
    if evidence['os_ipv6'] != 'disabled':
        advisories.append('OS_IPV6_NOT_DISABLED')
    required = [layers[name] for name in REQUIRED]
    status = ('violated' if 'fail' in required else
              'established' if all(item == 'pass' for item in required) else 'incomplete')
    missing = [item for item in LIFECYCLE if item not in evidence.get('lifecycle_checked', [])]
    persistent = status == 'established' and not missing
    return {'schema_version': REPORT_SCHEMA, 'target_ref': evidence['target_ref'],
            'platform': evidence['platform'], 'status': status, 'layers': layers,
            'blockers': blockers, 'advisories': advisories,
            'persistence': {'status': 'checked' if persistent else 'not_established',
                            'lifecycle_missing': missing},
            'evidence_scope': 'supplied_observations_only', 'apply_supported': False,
            'service_eligibility': 'not_assessed', 'ban_free': 'not_promised'}


def _read(path):
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_BINARY', 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        _bad('INPUT_UNREADABLE')
    with os.fdopen(fd, 'rb') as handle:
        raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        _bad('INPUT_TOO_LARGE')
    try:
        return json.loads(raw.decode('utf-8'))
    except (UnicodeError, ValueError, RecursionError):
        _bad('INVALID_EVIDENCE')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Judge whole-machine IPv4-only egress from supplied observations.')
    parser.add_argument('command', choices=['check'])
    parser.add_argument('--input', required=True, help='evidence JSON written by the Agent from real observations')
    args = parser.parse_args(argv)
    try:
        report = judge(_read(args.input))
    except EvidenceError as exc:
        print(json.dumps({'status': 'blocked', 'code': exc.code}), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
