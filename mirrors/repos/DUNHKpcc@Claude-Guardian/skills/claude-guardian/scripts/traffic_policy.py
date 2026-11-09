"""Whole-machine IPv4-only policy stamped into every report (owner 2026-10-19, 2026-10-25).

Fixed data: it states the rule, not whether a machine meets it. network_check.py
measures the machine and egress_verifier.py judges it.
"""
from dataclasses import dataclass, field

SCHEMA = 'guardian-traffic-policy/0.2'


@dataclass(frozen=True, slots=True)
class TrafficPolicy:
    schema_version: str = field(default=SCHEMA, init=False)
    policy: str = field(default='IPv4_ONLY', init=False)
    applies_to: str = field(default='whole_machine', init=False)
    ipv6: str = field(default='disabled', init=False)
    ipv6_fallback: str = field(default='forbidden', init=False)
    windows_adapter_ipv6: str = field(default='disabled_by_default', init=False)
    on_proxy_failure: str = field(default='no_direct', init=False)
    exceptions: str = field(default='explicit_user_request_only', init=False)
    measured_by: str = field(default='network_check.py', init=False)
    judged_by: str = field(default='egress_verifier.py', init=False)


_DEFAULT = TrafficPolicy()


def policy_projection():
    """A fresh copy of the fixed policy; never built from caller input."""
    return {name: getattr(_DEFAULT, name) for name in TrafficPolicy.__dataclass_fields__}
