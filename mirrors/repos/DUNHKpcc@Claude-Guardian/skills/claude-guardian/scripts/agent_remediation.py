#!/usr/bin/env python3
"""Offline action selection for Agent-led remediation; never an execution grant.

Only fixed catalog templates leave this module. Imported findings are untrusted
observations, not proof of native capability, consent, or successful repair.
"""
import argparse
import copy
import json
import re

from traffic_policy import policy_projection
import sys

import guardian

SCHEMA = 'guardian-remediation-selection/0.1'
INPUT_SCHEMA = 'guardian-remediation-findings/0.1'
# Fixed root members diagnostic_codes() reads beyond the shared report vocabulary.
REPORT_EXTRA_ROOT = frozenset({'errors', 'code', 'error_code', 'cancelled', 'status'})


def action(kind, module, summary, steps, evidence, verify, command=None):
    return dict(kind=kind, module_id=module, summary=summary, steps=steps,
                required_evidence=evidence, verification=verify,
                command_template=command, target_mutation_supported=False)


CATALOG = {
    'stop': action('stop', 'ENV-01', '用户已取消；停止相关操作',
                   ['等待用户重新提出或明确恢复任务，不自动重试'], [], ['重新开始时重新采集和授权']),
    'bind-target': action('clarify', 'ENV-01', '先确认目标设备、当前用户和执行位置',
                         ['核对 Agent 所在主机与用户指定设备', '只补缺失信息；云端结果不得代替本机'],
                         ['当前设备/用户/命名空间'], ['在正确目标重新检测']),
    'reaudit': action('read_only_script', 'ENV-01', '旧快照失效，重新检测',
                     ['guardian.py check 重新采系统和代理设置', 'network_check.py run 重新测网络'],
                     ['当前目标', 'B 档检测计划批准'], ['比较同一目标的新旧结果'],
                     ['python', 'scripts/network_check.py', 'run', '--target-ref', '<target-alias>']),
    'collect-proxy': action('read_only_script', 'ENV-02', '补充选定代理实例及配置证据',
                           ['先查看实际支持范围', '仅对获准精确文件使用 static-audit；版本不支持则Agent通过已核实的宿主只读接口读取必要字段'],
                           ['产品/版本', '活动配置/端口归属', '精确文件读取授权'],
                           ['分别记录文件声明、OS开关、运行时；不互相补值'],
                           ['python', 'scripts/inventory_cli.py', 'capabilities']),
    'proxy-port': action('agent_investigation', 'ENV-02', '系统代理端口与选定实例不一致',
                        ['核实当前活动网络服务、代理类型、监听实例及端口',
                         '记录原开关/主机/端口/绕过列表；向用户展示仅该服务该代理类型的差异和恢复值',
                         '取得具体修改授权后，Agent使用实际环境支持的设置接口或经过审阅的限定脚本，仅修改已核实的端口',
                         '保留PAC、绕过列表、其他服务、TUN及Codex控制路径；异常时恢复本次原值'],
                        ['新鲜P06/P09/P11/P12', '监听者归属', '活动网络服务', '控制通道保护'],
                        ['重读同一服务代理端口', '另获授权后检验同一程序的中性HTTPS路径']),
    'plan-rules': action('candidate_only', 'ENV-06', '生成已拥有扩展中的有限规则候选',
                        ['仅在已确认的问题确为规则选择/优先级时使用',
                         '已有DOMAIN/DOMAIN-SUFFIX policy更换用merge-policy；空prepend插入用rules-prepend',
                         '展示精确diff、影响、保留项、备份恢复范围；execute仍须原生适配及本次授权，当前未开放'],
                        ['规则根因', '精确文件/版本/活动扩展归属', '请求与binding', '合并优先级'],
                        ['候选解析→合并解释→内核校验→GUI读回→实际路径→订阅更新复验'],
                        ['python', 'scripts/repair_cli.py', 'preflight', '--request', '<private-request.json>',
                         '--target-path', '<owned-extension>', '--target-ref', '<target-alias>', '--entry-file', '<sanitized-entry.json>']),
    'probe-plan': action('read_only_script', 'ENV-03', '跑网络基础检测',
                         ['用户批准检测计划（B 档）后运行 network_check.py run；用了本地代理端口就加 --proxy',
                          '只联系 network_check.py endpoints 列出的中性站点，不碰 Claude；失败不自动换节点或重试'],
                         ['当前目标', 'B 档检测计划批准'],
                         ['路由、IPv4 出口、IPv6、DNS 泄露、UDP 各自看结果'],
                         ['python', 'scripts/network_check.py', 'run', '--target-ref', '<target-alias>']),
    'dns': action('agent_investigation', 'ENV-04', '定位具体DNS责任层后再改最小设置',
                  ['分别核对系统DNS、代理核心DNS、浏览器DoH与内网分流',
                   '用 network_check.py 的 DNS 泄露检测看解析服务器在哪个国家、是否 fake-ip 接管',
                   '确认责任层后展示该层精确键、原值、目标值及恢复值，由Agent按该环境已核实的接口修改；没有工具或许可才交接用户'],
                  ['系统/核心/浏览器分层证据', '内网与节点引导解析保护'],
                  ['同一名称/类型/程序复测；泄漏另按路径核对']),
    'ipv4-only-policy': action('agent_investigation', 'ENV-04', '整机只走 IPv4，IPv6 关闭',
                   ['代理核心 ipv6: false、DNS 不返回 IPv6、规则末尾拒绝 IPv6 目标',
                    'Windows 默认关闭物理网卡 IPv6（B 档，记原值）；节点用 IPv4 地址',
                    '展示差异、影响、备份与恢复，批准后修改'],
                   ['当前目标与活动配置', 'B 档计划批准'],
                   ['network_check.py run 的“IPv6 是否堵住”通过；IPv4 不可用时报告不可用，不回退 IPv6'],
                   ['python', 'scripts/network_check.py', 'run', '--target-ref', '<target-alias>']),
    'ipv6': action('agent_investigation', 'ENV-04', '区分IPv6旁路与单纯不可用',
                   ['确认同一程序的IPv4/IPv6路径', '已观察的旁路只提出应用/TUN范围修复；默认IPv4_ONLY另按策略计划核验，不整机禁用IPv6',
                    '保留节点外层IPv6；具体差异与恢复值确认后在对应客户端设置中调整'],
                   ['同程序双栈对照', '外层节点依赖'], ['复测同一地址族和路径；阻断以实测为准']),
    'udp': action('agent_investigation', 'ENV-04', '分开处理应用UDP、STUN和隧道外层UDP',
                  ['核对规则命中与节点能力', '仅调整已证实错误的应用规则；保留Hysteria2/TUIC外层UDP',
                   '用 network_check.py 的 UDP 检测比对 STUN 映射地址和 TCP 出口'],
                  ['应用协议/路径', '节点能力', '隧道外层依赖'], ['同范围UDP/STUN复测，UDP单独测']),
    'browser': action('agent_investigation', 'ENV-05', '核实实际浏览器/Profile/origin的有效策略',
                      ['核对版本、受管状态、策略接受/冲突与作用域',
                       '对Chrome/Edge仅提出受支持的非代理UDP限制及媒体影响；确认后由Agent通过已核实的接口改该项',
                       'Safari/Firefox无内置写入适配；继续调查该环境支持的设置方式，不套用Chrome策略'],
                      ['实际浏览器/Profile/origin', '有效策略', '公网候选路径证据'],
                      ['同Profile/origin复测候选及必要媒体；没有候选时换方式再测']),
    'launcher': action('agent_investigation', 'ENV-07', '查明具体程序与子进程采用的代理方式',
                       ['核对启动入口、GUI/终端差异和该版本支持的配置',
                        '只提出该启动入口的修改，展示环境变量作用域和恢复值；不输出秘密',
                        'PC0不启动Claude；真实客户端验证需独立接触交接'],
                       ['启动方式/版本', '子进程覆盖', '认证类别'], ['逐程序复测；逐个确认采用']),
    'clock': action('agent_investigation', 'ENV-08', '分开处理时钟、时区和语言；时区对齐出口地区',
                    ['先确认是否存在时钟误差；电脑（本机、VM、VPS）和手机的时区以出口IP所在地区为目标，语言按用户明确目标',
                     '记录原值并展示单项影响；用户确认后由Agent在实际系统支持的接口修改，并关闭自动设置时区',
                     '手机由用户本人在系统设置里改；不把NTP路由当时区设置'],
                    ['出口IP所在地区', '用户目标', '当前设置/管理权限'],
                    ['重读被修改项；验收页时区一项变绿；语言生效/注销另行确认']),
    'cleanup': action('agent_investigation', 'ENV-09', '先盘点精确清理对象与保留项',
                      ['列出选中对象、影响及可读备份/恢复方法',
                       '默认保护项目、CLI、凭据、历史、skills/hooks/plugins与控制通道；仅独立选择并核实的Claude专属C5数据可纳入范围',
                       '选择器不执行清理；独立选择C5后先获准盘点，再由可信宿主通过cleanup_cli.main进行精确plan/quarantine/reconcile/restore',
                       '原生归属与停用核实适配未提供；缺宿主或具体批准即阻塞；保留隔离副本及独立备份，不运行上游整目录清理'],
                      ['清理目的', '精确对象', '保留清单', '恢复验证'], ['核对选中对象与保留内容；账号恢复另走申诉']),
    'fault': action('agent_investigation', 'ENV-10', '故障阻断需要独立平台实现与真实演练',
                    ['明确保护程序、地址族、故障与控制通道',
                     '准备独立离线恢复；当前无内置系统故障注入/防火墙修复执行器'],
                    ['平台出站能力', '独立恢复', '具体演练授权'], ['正常/停止/重启/更新逐场景验收，当前记not_run']),
    'dependency': action('agent_investigation', 'ENV-01', '补足明确缺失的运行时或解析器',
                         ['核对缺失的是Python运行时、PyYAML还是系统工具',
                          '展示官方来源、版本和安装范围，取得需要的安装许可后按官方流程安装',
                          '不静默安装，不因解析失败改配置'], ['依赖名称/来源/目标环境'], ['重跑原失败命令']),
    'permission': action('clarify', 'ENV-01', '缺少对应动作授权或访问权限',
                         ['说明确切目标、数据与用途，向用户请求该动作授权', '尊重拒绝，不换路径绕过系统拒绝'],
                         ['确切范围许可'], ['许可后重新执行原限定检查']),
    'unsupported': action('agent_investigation', 'ENV-01', '当前适配器不支持该操作或版本',
                          ['记录具体产品/版本/操作缺口', 'Agent继续检查实际环境支持的接口，提出独立最小修复；不改版本声明、不替换门禁回调'],
                          ['匹配操作的原生适配与验收'], ['未支持项保持blocked，不阻断无关只读工作']),
    'input': action('clarify', 'ENV-01', '输入或采集失败，尚不能诊断为配置故障',
                    ['核对私有本地输入格式、限定路径和原始错误类别', '修正输入后有界重试；不输出秘密或扩大扫描'],
                    ['有效输入', '失败原因'], ['重跑原检查；失败保留unknown']),
    'incident': action('clarify', 'M12', '先区分连通、认证、额度、支付与账号事故',
                       ['只收集必要脱敏错误类别与当前任务', '账号停用走官方处理分支；不自动清理、换号或改网络'],
                       ['事故类别', '当前状态'], ['账号状态另按官方渠道确认']),
    'runtime': action('agent_investigation', 'ENV-01', '运行时路径不满足严格会话要求',
                      ['查看固定runtime_path_diagnostic字段以区分executable/cwd/prefix/base_prefix',
                       '核对已有可信运行时的真实目录与权限；需要安装时另取许可',
                       '保留部分元数据；不放松链接检查或伪造上下文句柄'],
                      ['受影响路径字段及原因', '可信本机运行时'], ['在合规运行时重跑诊断；DNS授权仍需单独满足']),
    'no-change': action('no_change', 'ENV-06', '当前修复请求没有待写入差异，停止本次写入流程',
                        ['保留当前文件；不创建计划、备份或回执，不改走另一条修改路径',
                         '说明本次核对的输入范围；应用、运行时和路径另测'],
                        [], ['若目标或输入变化，重新读取并计划；本结果不复用旧权限']),
    'keep': action('no_change', 'ENV-04', '现有证据不足以要求修改',
                   ['保留当前配置并解释证据边界', '仅补与用户目标有关的缺口'], [], ['没有新问题不制造修复']),
}

# Informational capability discovery only; no imported report grants C5 intent,
# ownership, a host adapter, operation consent, or execution authority.
CATALOG['cleanup']['host_handoff'] = {
    'capability': 'c5_selected_root_quarantine_restore',
    'entry_point': 'cleanup_cli.main',
    'invocation': 'in_process_with_reviewed_live_host',
    'core_module': 'cleanup_transactions',
    'operations': ['plan', 'quarantine', 'reconcile', 'restore'],
    'selection_required': 'C5-full-claude-data-reset',
    'operator_mode': 'C5-full-local-data',
    'default_host': 'unavailable',
    'native_ownership_adapter': 'unavailable',
    'execution_authorized': False,
    'permanent_purge': 'unsupported',
    'documentation': 'references/cleanup-cli-usage.md',
}

CATALOG['plan-prepend'] = copy.deepcopy(CATALOG['plan-rules'])
CATALOG['plan-prepend']['command_template'] += [
    '--candidate-kind', 'rules-prepend', '--app-info', '<authorized-Info.plist>',
    '--profile-index', '<authorized-profiles.yaml>', '--extension-uid', '<selected-rules-uid>',
    '--base-path', '<authorized-base-profile>']
CATALOG['plan-prepend']['host_handoff'] = {
    'capability': 'clash258_single_domain_rules_task',
    'entry_point': 'agent_rules_task.prepare_rules_task',
    'readback_entry_point': 'agent_rules_task.assess_supplied_readback',
    'invocation': 'in_process_supplied_snapshots',
    'executor': 'agent_supported_application',
    'execution_authorized': False,
    'builtin_apply_supported': False,
    'documentation': 'references/agent-rules-task.md',
}

GROUPS = {
    'ipv4-only-policy': 'IPV6_EXIT_OBSERVED LAYER_IPV6_PROBE_FAIL',
    'stop': 'USER_CANCELLED CANCELLED DECLINED CONSENT_TIMEOUT AUTHORIZATION_CANCELLED APPROVAL_CANCELLED APPROVAL_TIMEOUT',
    'bind-target': 'ENVIRONMENT_ENTRY_REQUIRED ENVIRONMENT_ENTRY_CHANGED ENVIRONMENT_ENTRY_PLAN_MISMATCH ENVIRONMENT_ENTRY_PLAN_BINDING_REQUIRED TARGET_NOT_BOUND TARGET_USER_CONTEXT_MISMATCH ROUTE_OR_TARGET_NEEDS_CLARIFICATION CONTEXT_CHANGED CONTEXT_EXPIRED CONTEXT_FOREIGN CONTEXT_INACTIVE CONTEXT_INACTIVE_OR_REMOTE CONTEXT_UNKNOWN CONSOLE_ACCOUNT_EQUALITY_UNPROVEN CONTROLLER_NOT_BOUND RESPONSE_CONTEXT_MISMATCH APPROVAL_CONTEXT_CHANGED INVALID_CONTEXT NATIVE_CONTEXT_NOT_BOUND',
    'reaudit': 'STALE_EVIDENCE_REAUDIT_REQUIRED SNAPSHOT_CHANGED_DURING_AUDIT PLAN_REQUIRES_STABLE_SNAPSHOT_AND_ROUTE_FACTS',
    'collect-proxy': 'LIMITED_METADATA_ONLY MINIMAL_METADATA_ONLY MISSING_ENVIRONMENT_EVIDENCE',
    'proxy-port': 'PROXY_PORT_ASSOCIATION_CONFLICT',
    'plan-rules': 'RULE_POLICY_MISMATCH',
    'plan-prepend': 'RULE_PREPEND_REQUIRED',
    'probe-plan': 'NETWORK_EFFECTIVENESS_NOT_TESTED PROXY_ENTRY_UNAVAILABLE HTTPS_PATH_UNKNOWN',
    'dns': 'DNS_PATH_CONFLICT BROWSER_DOH_CONFLICT',
    'ipv6': 'IPV6_BYPASS_OBSERVED',
    'udp': 'UDP_RULE_MISMATCH STUN_INCONCLUSIVE',
    'browser': 'WEBRTC_BYPASS_OBSERVED BROWSER_POLICY_IGNORED',
    'launcher': 'PROGRAM_PROXY_IGNORED',
    'clock': 'CLOCK_SETTING_REQUESTED TIMEZONE_LANGUAGE_GOAL',
    'cleanup': 'CLEANUP_REQUESTED',
    'fault': 'FAIL_CLOSED_UNVERIFIED',
    'dependency': 'RUNTIME_OR_PARSER_UNAVAILABLE PARSER_UNAVAILABLE',
    'permission': 'AUTHORIZATION_MISSING PERMISSION_DENIED PRECONTACT_ACTION_REJECTED LIVE_TERMINAL_REQUIRED PC0_TARGET_FORBIDDEN ENDPOINT_NEUTRALITY_UNVERIFIED RUNTIME_NOT_TRUSTED HOST_INTEGRATION_INVALID AUTHORIZATION_DENIED AUTHORIZATION_REQUIRED AUTHENTICATION_HANDOFF_REQUIRED CONTROLLER_AUTH_FAILED INTERACTIVE_TERMINAL_REQUIRED HOST_APPROVAL_UNAVAILABLE HOST_APPROVAL_FAILED CURRENT_EXACT_APPROVAL_REQUIRED',
    'unsupported': 'HOST_CAPABILITY_UNAVAILABLE UNSUPPORTED_PRODUCT_OR_VERSION NATIVE_REPAIR_ADAPTER_UNAVAILABLE NATIVE_CONTROLLER_HOST_ADAPTER_UNAVAILABLE DNS_HOST_INTEGRATION_REQUIRED WINDOWS_SESSION_DNS_UNAVAILABLE UNSUPPORTED_PLATFORM PLATFORM_UNSUPPORTED WINDOWS_API_UNAVAILABLE UNSUPPORTED_CANDIDATE_KIND UNSUPPORTED_REMEDY UNSUPPORTED_EXTENSION_TYPE UNSUPPORTED_ACTIVE_PROFILE_TYPE',
    'input': 'INPUT_OR_RESPONSE_INVALID UNSAFE_OR_OFFLINE_PATH BUDGET_EXCEEDED FILE_NOT_FOUND_IN_APPROVED_SCOPE INVENTORY_CALLBACK_FAILED OS_QUERY_FAILED OUTPUT_SAVE_FAILED COLLECTOR_INTERNAL_FAILURE INPUT_INVALID INVALID_ARGUMENTS_OR_SAVE_FAILED SESSION_FAILED TIMEOUT CLEANUP_FAILED CONTROLLER_RESPONSE_REJECTED APPROVAL_CLOCK_INVALID INVALID_APPROVAL_TIMEOUT CANCELLATION_CHECK_FAILED INVALID_CANCELLATION_CALLBACK DIAGNOSTIC_PREREQUISITES_UNRESOLVED TERMINAL_FLUSH_FAILED',
    'incident': 'INCIDENT_PRIORITY',
    'runtime': 'RUNTIME_PATH_INVALID',
    'no-change': 'NO_CHANGE_TO_RETAIN NO_CHANGE_TO_EXECUTE',
    'keep': 'FAKE_IP_WITH_WORKING_HTTPS IPV6_TIMEOUT_ONLY EGRESS_TIMEZONE_DIFFERENCE NO_CHANGE',
}
REPAIR_PREREQUISITES = {
    'BACKUP_CHANGED', 'BACKUP_DIRECTORY_CHANGED', 'BACKUP_NOT_PRIVATE',
    'INVALID_RECONCILIATION', 'LEGACY_RECOVERY_IDENTITY_UNPROVEN',
    'PREPARED_RECOVERY_REQUIRED', 'RECONCILIATION_STALE', 'RECOVERY_WITNESS_MISMATCH',
    'STAGING_CHANGED', 'EXPECTED_RECONCILIATION_REQUIRED', 'STAGING_RETAINED',
    'STAGING_CLEANUP_FAILED', 'DESCRIPTOR_CLOSE_FAILED',
    'AUTHORIZATION_SCOPE_MISMATCH', 'ACTION_AUTHORIZATION_PENDING', 'CONTEXT_MISMATCH',
    'BACKUP_DIRECTORY_NOT_PRIVATE', 'BACKUP_SCOPE_MISMATCH', 'CANDIDATE_SCOPE_MISMATCH',
    'EXPLICIT_RULES_SOURCE_SCOPE_REQUIRED', 'INVALID_EXPECTED_DIGEST', 'INVALID_RETAINED_PLAN',
    'INVALID_SOURCE_IDENTITY', 'PLAN_CHANGED', 'PLAN_DIGEST_MISMATCH',
    'PLAN_DIRECTORY_NOT_PRIVATE', 'PLAN_READBACK_FAILED', 'POST_WRITE_VERIFY_FAILED',
    'REQUEST_CHANGED', 'SOURCE_SCOPE_MISMATCH', 'SOURCE_SNAPSHOT_CHANGED', 'STALE_FILE',
    'TARGET_MISMATCH', 'NATIVE_ADAPTER_FAILURE',
    'CLASH_VERGE_RUNNING', 'PROCESS_LIST_UNAVAILABLE', 'APP_METADATA_NOT_TRUSTED',
    'BACKUP_CORRUPT', 'BACKUP_VERIFY_FAILED', 'CONCURRENT_CHANGE',
    'EXCLUSIVE_ACCESS_REQUIRED', 'EXPLICIT_SCOPE_REQUIRED', 'INVALID_DOCUMENT',
    'INVALID_EXPIRY', 'INVALID_OR_EXPIRED_PLAN', 'INVALID_PLAN',
    'INVALID_PROPOSED_BYTES', 'INVALID_RECEIPT_JSON', 'INVALID_RECOVERY',
    'INVALID_SNAPSHOT', 'INVALID_TARGET', 'PARENT_CHANGED', 'RECEIPT_CHANGED',
    'RECEIPT_DIGEST_MISMATCH', 'RECEIPT_DIRECTORY_NOT_PRIVATE',
    'RECEIPT_PATH_MISMATCH', 'RECEIPT_TOO_LARGE', 'RECOVERY_REQUIRES_RECONCILIATION',
    'ROLLBACK_CONFLICT', 'ROOT_TARGET_UNSUPPORTED', 'STAGING_VERIFY_FAILED',
    'UNSAFE_OR_UNAVAILABLE_DIRECTORY', 'UNSAFE_OR_UNAVAILABLE_FILE', 'UNSAFE_PATH',
    'UNSAFE_RECEIPT_FILE', 'UNSUPPORTED_FILE_METADATA', 'UNSUPPORTED_FILE_SIZE_OR_OWNER',
    'UNSUPPORTED_FILE_TYPE', 'WRITE_FAILED', 'XATTR_CHECK_FAILED', 'IO_FAILURE',
    'ALTERNATE_OR_UNKNOWN_STREAMS_UNSUPPORTED', 'ANCESTOR_CHANGED', 'BACKUP_DATA_MISMATCH',
    'FILESYSTEM_UNSUPPORTED', 'FILE_METADATA_UNAVAILABLE', 'HANDLE_CLOSE_FAILED',
    'INVALID_BACKUP_EXPECTATION', 'INVALID_BACKUP_STREAM', 'INVALID_BACKUP_STREAM_INPUT',
    'INVALID_BUDGET', 'LOCAL_VOLUME_GUID_PATH_REQUIRED', 'NONLOCAL_OR_UNSUPPORTED_VOLUME',
    'READ_FAILED', 'REPARSE_RECALL_OR_METADATA_UNSUPPORTED', 'SECURITY_METADATA_UNAVAILABLE',
    'UNSUPPORTED_FILE_SIZE', 'UNSUPPORTED_LINK_OR_DELETE_STATE', 'UNSUPPORTED_METADATA',
    'UNSUPPORTED_PATH', 'VOLUME_METADATA_UNAVAILABLE',
    'BASE_PROFILE_FILE_MISMATCH', 'DEADLINE_EXCEEDED', 'EXACT_RETAINED_PLAN_REQUIRED',
    'INVALID_ARGUMENTS', 'INVALID_DEADLINE', 'INVALID_REPAIR_REQUEST',
    'PROFILE_DIRECTORY_SCOPE_MISMATCH', 'AMBIGUOUS_MAPPING', 'AMBIGUOUS_OR_UNSUPPORTED_RULE',
    'AMBIGUOUS_RULE_SELECTION', 'EGRESS_BINDING_MISMATCH', 'EGRESS_GROUP_MISSING_OR_AMBIGUOUS',
    'INVALID_BINDING', 'INVALID_OR_OVERSIZED_SNAPSHOT', 'INVALID_REMEDY_REQUEST',
    'INVALID_RULE_BINDING', 'INVALID_YAML', 'OVERLAPPING_EDITS', 'REVISION_BINDING_MISSING',
    'SELECTED_RULE_SHADOWED', 'SEMANTIC_PLAN_BLOCKED', 'SNAPSHOT_REVISION_MISMATCH',
    'TARGET_OR_SCOPE_MISMATCH', 'UNEXPECTED_SEMANTIC_DELTA', 'UNSUPPORTED_BINDING',
    'UNSUPPORTED_OR_CHANGED_RULE', 'UNSUPPORTED_SCALAR_ENCODING', 'UNSUPPORTED_STRUCTURE',
    'UNSUPPORTED_YAML', 'YAML_BUDGET_EXCEEDED', 'BASE_GROUPS_REQUIRED', 'CANDIDATE_TOO_LARGE',
    'DELETE_SEQUENCE_UNSUPPORTED', 'EMPTY_INLINE_PREPEND_REQUIRED', 'EXPECTED_RULE_SEQUENCE',
    'EXPLICIT_PREPEND_OPERATION_REQUIRED', 'INVALID_BASE_GROUP', 'INVALID_PROTECTED_RULE_INDEXES',
    'INVALID_RULE_SELECTION', 'INVALID_SELECTED_RULE', 'NONEMPTY_PREPEND_UNSUPPORTED',
    'OVERLAPPING_SELECTED_RULES', 'PRIORITY_ANALYSIS_BUDGET_EXCEEDED',
    'PROTECTED_RULE_PRIORITY_CONFLICT', 'PROTECTED_RULE_TYPE_UNSUPPORTED',
    'RULE_SELECTOR_ALREADY_PRESENT', 'UNSUPPORTED_RULE_VALUE', 'AMBIGUOUS_EXTENSION_FILE_OWNER',
    'AMBIGUOUS_OR_UNSUPPORTED_BASE_PROFILE_FILE', 'APP_METADATA_BUDGET_EXCEEDED',
    'DUPLICATE_OR_INVALID_APP_METADATA_KEY', 'DUPLICATE_OR_INVALID_PROFILE_UID',
    'EXTENSION_FILE_MISMATCH', 'GLOBAL_OR_DEFAULT_EXTENSION_SCOPE_UNSUPPORTED',
    'INVALID_APP_METADATA', 'INVALID_EXTENSION_SELECTION', 'INVALID_OR_UNSUPPORTED_YAML',
    'INVALID_PROFILE_INDEX', 'MERGE_FORMAT_NOT_RULES_EXTENSION', 'PROFILE_LINK_MISSING',
    'RULES_EXTENSION_FORMAT_NOT_MERGE', 'SHARED_EXTENSION_SCOPE_UNSUPPORTED',
    'UNSAFE_PROFILE_FILE_REFERENCE', 'UNSUPPORTED_EXISTING_MERGE_FORMAT',
    'UNSUPPORTED_RULES_SEQMAP_FORMAT', 'UNSUPPORTED_RULES_SEQMAP_VALUE',
    'SELECTED_EXTENSION_NOT_ACTIVE_MERGE', 'SELECTED_EXTENSION_NOT_ACTIVE_RULES',
}
CATALOG['repair-prerequisites'] = action('clarify', 'ENV-06',
    '修复授权、快照或恢复前提有缺口，先检查当前状态',
    ['检查精确计划/目标/权限/备份冲突；重新读取并展示更新的差异',
     '可能已有写入时先检查保留回执与当前文件，按独立恢复契约处理，不重复写入',
     '不能用Agent分支绕过拒绝、失效计划或恢复冲突'],
    ['当前目标与修复状态', '精确范围许可', '可用备份恢复'], ['前提解决后重新计划与复测'])
GROUPS['repair-prerequisites'] = ' '.join(sorted(REPAIR_PREREQUISITES))
FINDING_ACTIONS = {code: key for key, codes in GROUPS.items() for code in codes.split()}
PREREQUISITE_CODES = frozenset(code for key in (
    'stop', 'bind-target', 'reaudit', 'permission', 'input', 'repair-prerequisites')
    for code in GROUPS[key].split())


def diagnostic_codes(report):
    """Read fixed diagnostic fields without guessing from text or restoring authority.

    Unknown findings may warrant investigation; an unknown error cannot establish
    that a failed operation was merely unsupported. Never recursively scan or echo
    untrusted diagnostics, paths, messages, or arbitrary nested reports.
    """
    def checked_code(value):
        if type(value) is not str or not re.fullmatch('[A-Z][A-Z0-9_]{0,95}', value):
            raise guardian.GuardianError('INPUT_OR_RESPONSE_INVALID')
        return value

    findings = report.get('findings', [])
    if type(findings) is not list or len(findings) > 128:
        raise guardian.GuardianError('INPUT_OR_RESPONSE_INVALID')
    codes = [checked_code(item.get('code') if type(item) is dict else None)
             for item in findings]
    errors = report.get('errors', [])
    if type(errors) is not list or len(errors) > 128:
        raise guardian.GuardianError('INPUT_OR_RESPONSE_INVALID')
    diagnostics = [checked_code(item.get('code') if type(item) is dict else item)
                   for item in errors]
    for key in ('code', 'error_code'):
        if key in report and report[key] is not None:
            diagnostics.append(checked_code(report[key]))
    codes.extend(code if code in FINDING_ACTIONS else 'INPUT_OR_RESPONSE_INVALID'
                 for code in diagnostics)

    missing = report.get('missing_fields', [])
    if (type(missing) is not list or len(missing) > 128
            or any(type(field) is not str or len(field) > 128 for field in missing)):
        raise guardian.GuardianError('INPUT_OR_RESPONSE_INVALID')
    if missing:
        codes.append('MISSING_ENVIRONMENT_EVIDENCE')
    if 'cancelled' in report and type(report['cancelled']) is not bool:
        raise guardian.GuardianError('INPUT_OR_RESPONSE_INVALID')
    if report.get('cancelled'):
        codes.append('USER_CANCELLED')

    states = {
        'execution_status': {'completed', 'blocked', 'failed', 'interrupted'},
        'status': {'completed', 'partial', 'blocked', 'failed', 'cancelled', 'interrupted', 'stopped'},
        'inventory_readiness': {'ready_for_probe_plan', 'ready_for_configuration_plan',
                                'needs_input', 'partial', 'blocked', 'interrupted'},
    }
    for key, allowed in states.items():
        if key not in report:
            continue
        value = report[key]
        if type(value) is not str or value not in allowed:
            raise guardian.GuardianError('INPUT_OR_RESPONSE_INVALID')
        if value in {'cancelled', 'interrupted', 'stopped'}:
            codes.append('USER_CANCELLED')
        elif value in {'blocked', 'failed'}:
            # A stated capability gap can still be investigated. An unexplained
            # failed/blocked report cannot lend its old findings to a repair.
            capability_only = codes and all(FINDING_ACTIONS.get(code) == 'unsupported' for code in codes)
            no_change_only = codes and all(FINDING_ACTIONS.get(code) == 'no-change' for code in codes)
            if value == 'failed' or not (capability_only or no_change_only):
                codes.append('DIAGNOSTIC_PREREQUISITES_UNRESOLVED')
    return codes


def select(report, target_ref):
    guardian.alias(target_ref)
    if (type(report) is not dict or type(report.get('schema_version')) is not str
            or report.get('schema_version') not in {
            INPUT_SCHEMA, 'guardian-report/0.1', 'env-inventory/0.2'}):
        raise guardian.GuardianError('INPUT_OR_RESPONSE_INVALID')
    if report['schema_version'] != INPUT_SCHEMA:
        # Saved guardian reports: unknown (possibly secret-bearing) members are rejected, not ignored.
        guardian.reject_unknown_report_members(report, extra_root=REPORT_EXTRA_ROOT)
    if report.get('target_ref') != target_ref:
        raise guardian.GuardianError('TARGET_NOT_BOUND')
    codes = diagnostic_codes(report)
    # Cancellation wins over every pending proposal, including modifications.
    if any(code in GROUPS['stop'].split() for code in codes):
        codes = ['USER_CANCELLED']
    barriers = sorted(set(codes) & PREREQUISITE_CODES)
    no_change = not barriers and any(FINDING_ACTIONS.get(code) == 'no-change' for code in codes)
    if no_change:
        # A completed no-write branch is not a missing capability to work around.
        # Genuine prerequisite failures above remain barriers, never hidden by it.
        # Independent account/incident triage is not a substitute configuration
        # repair and must remain visible even while this write branch stops.
        codes = [code for code in codes if FINDING_ACTIONS.get(code) in {'no-change', 'incident'}]
    selected = {}
    for code in codes:
        key = FINDING_ACTIONS.get(code, 'unsupported')
        if key not in selected:
            selected[key] = dict(action_id=key, **copy.deepcopy(CATALOG[key]), finding_codes=[])
        # Do not echo unrecognized codes: they may contain private data.
        selected[key]['finding_codes'].append(code if code in FINDING_ACTIONS else 'UNRECOGNIZED_FINDING')
    for item in selected.values():
        item['builtin_execution'] = 'not_available_for_target_mutation'
        item['agent_fallback'] = ('investigate_scoped_repair' if not barriers and not no_change and item['kind'] in {'agent_investigation', 'candidate_only', 'host_library_only'} else 'none')
        item['fallback_requirements'] = (['inspect_actual_target_and_supported_interface',
            'explain_exact_diff_impact_backup_and_recovery', 'obtain_required_specific_approval',
            'execute_only_reviewed_minimal_operation', 'read_back_and_redetect_same_scope',
            'never_bypass_denial_or_builtin_gate'] if item['agent_fallback'] != 'none' else [])
    return dict(schema_version=SCHEMA, target_ref=target_ref, traffic_policy=policy_projection(),
                status='stopped' if 'stop' in selected or no_change else 'selected' if selected else 'insufficient_evidence',
                actions=list(selected.values()), prerequisite_blockers=barriers, changes=[], authority='none',
                native_acceptance='not_established', environment_pass=False,
                next_phase='stop' if 'stop' in selected or no_change else 'resolve_prerequisites' if barriers else 'agent_review',
                completion='no_repair_performed')


class PrivateParser(argparse.ArgumentParser):
    def error(self, message):
        raise guardian.GuardianError('INPUT_OR_RESPONSE_INVALID')


def main(argv=None):
    parser = PrivateParser(description=__doc__)
    parser.add_argument('command', choices=['catalog', 'select'])
    parser.add_argument('--input')
    parser.add_argument('--target-ref')
    try:
        args = parser.parse_args(argv)
        if args.command == 'catalog':
            result = dict(schema_version=SCHEMA, actions=CATALOG, findings=FINDING_ACTIONS,
                          authority='none', target_mutation_supported=False)
        else:
            if not args.input or not args.target_ref:
                raise guardian.GuardianError('INPUT_OR_RESPONSE_INVALID')
            result = select(guardian.load_json(args.input), args.target_ref)
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 0
    except guardian.GuardianError as exc:
        print(json.dumps(dict(status='blocked', code=exc.code, changes=[], authority='none')))
        return 2
    except KeyboardInterrupt:
        print('{"status":"stopped","code":"USER_CANCELLED","changes":[]}')
        return 130


if __name__ == '__main__':
    sys.exit(main())
