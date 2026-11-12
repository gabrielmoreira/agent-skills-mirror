"""Offline adaptive interview; no network, subprocess, file writes or implicit consent.

Public API: new_state, record_fact, record_facts, set_context, next_question, assessment,
required_references, references_for_topics, record_capabilities, record_work_item,
record_scope_confirmation, record_plan_approval, record_plan_result,
request_critical_confirmation, resolve_critical_confirmation, use_critical_confirmation,
authorization_check, authorization_summary,
mark_asked, defer_branch, resume_branch, complete_purchase, dumps_state,
loads_state, validate_state, resume_interview, record_resume_review,
resume_review_prompt, resume_scope_keys, cleanup_assessment,
report_subscription_conflict, resolve_subscription_conflict. All updates return copies. Persisting returned JSON
is exclusively the host's responsibility and requires explicit opt-in per scope.

Example::
    s = new_state("laptop-a", "claude-a")
    s = record_fact(s, "Q-J01", "first_subscription", source="user:turn-1")
    s = record_fact(s, "Q-C02", "windows", source="user:turn-1")
    question = next_question(s)  # one relevant question, never a whole form
    s = mark_asked(s, question["id"])

Values are sanitized categorical facts, never passwords, card numbers, gift-card
codes or authentication material. The host translates prompts and performs domain
reasoning using references/intake.md. An answer is never an action authorization.
G3 is deliberately always closed here: use the separate action/contact gates.
"""
from copy import deepcopy
from datetime import datetime, timezone
import json
import hashlib
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

SCHEMA_VERSION = "1.0.0"
FACT_STATES = frozenset({"unasked", "reported", "observed", "inferred", "unknown",
                         "declined", "conflict", "stale", "not_applicable", "deferred"})
JOURNEYS = frozenset({"first_subscription", "returning_subscription", "existing_subscriber", "unknown"})
ALIASES = {"Q-OS01": "Q-C02", "Q-L05": "Q-N06", "Q-Z02": "Q-C12", "Q-G05": "Q-P07"}
RETIRED = "Q-C07"

QUESTION_PROMPTS = {'Q-J01': '这次是第一次准备订阅（包括只用过免费版）、以前订阅过目前无有效订阅准备重订、当前已有订阅，还是不确定？',
 'Q-J02': '你说用过/是老手：现在还有有效订阅，还是准备开通/重新开通？',
 'Q-C01': '主要用网页/Desktop 聊天，还是 Claude Code 编程？这次具体想完成什么？',
 'Q-C02': '这次用 Mac 还是 Windows？',
 'Q-C03': '以前 Claude 账号被明确停用/封禁过吗，还是只遇到报错？',
 'Q-C04': '准备用的 Claude 账号注册了吗？已有账号现在能正常登录吗？',
 'Q-C05': '用本机、虚拟机、VPS，还是先比较？本机默认建议。',
 'Q-C06': '已有账号通过什么方式登录/接入？不懂名称可描述界面。',
 'Q-C08': '你这次想订阅什么套餐？ 选好了直接说；未决定先按用途和预算比较。',
 'Q-C09': '实际在哪个国家/地区使用？是否有跨地区安排？无需详细地址。',
 'Q-C10': '希望逐步指导，还是直接给检查项和命令？',
 'Q-C11': '老用户这次主要是续费/升级、调整使用方案，还是检查环境/解决问题？',
 'Q-C12': '哪些已有项目、历史、客户端或配置不能动？',
 # Derived implementation ID (Q-C13).
 'Q-C13': '为判断这次具体客户端功能的套餐依赖：当前订阅是什么套餐，涉及哪项功能？只说已知情况，不确定或暂不回答也可以；无需打开 Claude。',
 'Q-OS01': '本机是 Mac 还是 Windows？',
 'Q-OS02': '如果 Windows：是 Windows 10/11？具体 Edition（Home、Home Single Language、Pro……）是什么？',
 'Q-OS03': '如果 Mac：macOS 大致版本是什么？',
 'Q-OS04': '如果想更改语言：你指的是 Windows 显示语言，还是键盘输入、地区格式、浏览器或单个 App？',
 'Q-OS05': '如果 Windows 无法改显示语言：是否看到“许可证仅支持一种显示语言”等原文？',
 'Q-OS06': '如果无法改时区：是手动下拉灰色、自动设置开关灰色、报错，还是改完自动恢复？',
 'Q-OS07': '如果时区故障：“自动设置时区”开启吗？电脑是个人管理还是公司/学校管理？',
 'Q-OS08': '如果时间显示异常：实际时间是否准确，还是仅时区偏移/名称不对？',
 'Q-OS09': '是否确有需要修改 Windows/macOS 的语言/时区，还是只想检查能否正常使用 Claude？',
 'Q-OS10': 'Windows 10 是否有合适的安全更新安排（ESU/迁移/组织维护）？',
 'Q-OS11': '如果涉及 macOS 的语言/时间：需要系统级还是单个 App 的变化？',
 'Q-OS12': '当前 OS 选项不在 Mac/Windows 内，本次想了解共用规则还是要选 VM/VPS？',
 'Q-H01': '被限制的是 Claude 账号，还是 Apple/Google 商店账号、支付卡或某个客户端？',
 'Q-H02': '最近一次与本次任务有关的事件，大约何时发生？目前恢复了吗？',
 'Q-H03': '当时显示什么错误/通知？有可脱敏的原文或局部截图吗？',
 'Q-H04': '出现问题前正在注册、登录、订阅、更新客户端还是执行任务？',
 'Q-H05': '当时在什么设备/环境、通过什么客户端和计费渠道使用？',
 'Q-H06': '是否正在申诉、身份核验或处理退款？有没有官方回复要求你完成的事项？',
 'Q-H07': '之后做过哪些退出、重装、清理或配置修改？有需要保留/导出的数据吗？',
 'Q-H08': '本次是否沿用当时的设备/网络/付款工具？哪些变了？',
 'Q-N01': '当前是普通网络直接连接，还是使用代理/VPN/公司网络？软件名称知道就说。',
 'Q-N02': '浏览器、Code、代理分别运行在哪里？使用系统代理、应用代理、TUN 还是不确定？',
 'Q-N03': '网络是否常切换、自动换节点或跨地区？有计划长期固定使用的环境吗？',
 'Q-N04': '还有手机、其他电脑或远程工作区同时/交替使用吗？各自用来做什么？',
 'Q-N05': '已做过哪些网络测试？何时、在哪个设备、用哪个程序测的？',
 'Q-N06': '是否受公司网络、证书、安全软件、代理策略或设备管理限制？',
 'Q-P01': '你提到的购买对象是 Claude 订阅还是 API/其他服务？',
 'Q-P02': '这次相关的原套餐/旧购买渠道及待处理订单是什么？',
 'Q-P03': '可用于付款的设备有 iPhone/iPad、Android，还是只有电脑？',
 'Q-P04': '已有可用的商店账户/余额、银行卡、企业付款方式，还是尚未准备？',
 'Q-P05': '月费和一次性准备费用能接受什么范围？',
 'Q-P06': '更倾向哪种可行付款方式？需要先比较步骤吗？',
 'Q-P07': '后续准备怎样续费？需要说明账单查看与取消入口吗？',
 'Q-A01': 'A1 设备',
 'Q-A02': 'A2 Apple 账户',
 'Q-A03': 'A3 商店地区',
 'Q-A04': 'A4 App 与内购',
 'Q-A05': 'A5 服务账户对应',
 'Q-A06': '这次旧订单的购买渠道、状态或待处理扣费/退款还有哪些未说明？只补缺口，不确定或暂不回答也可以。',
 'Q-A07': 'A7 礼品卡',
 'Q-A08': 'A8 结账条件',
 'Q-A09': 'A9 来源',
 'Q-A10': 'A10 后续续费与改区影响',
 'Q-G01': '有可用 Android 设备，并能使用官方 Google Play 与 Claude App 吗？',
 'Q-G02': '有能正常登录验证的 Google 账户吗？Play 国家/地区和付款选项是什么？',
 'Q-G03': '当前购买页能看到目标套餐和可用付款选项吗？',
 'Q-G04': '手机 App 登录的 Claude 是否为这次准备使用的目标账户？',
 'Q-G05': '后续怎样续费，是否需要说明账单与取消入口？',
 'Q-W01': '准备使用的是信用卡/借记卡/企业卡？发行国家或地区是什么？',
 'Q-W02': '结账要求的账单资料能否如实填写？',
 'Q-W03': '是否支持所需的线上/周期付款，出现过拒付或验证提示吗？',
 'Q-W04': '当前结账总额、计费周期和后续续费安排是否符合本次选择？',
 'Q-I01': 'API/服务由哪一平台、哪一个组织或项目计费？',
 'Q-I02': '你是否有该项目的使用与付款权限？',
 'Q-I03': '本次是个人开发还是面向其他用户的服务？预计如何调用？',
 'Q-I04': '预算、费用上限和告警应如何设置？',
 'Q-E01': '是否确有企业结算需求和可用企业主体，而非单纯个人订阅？',
 'Q-E02': '由谁负责企业审核、付款和后续维护？',
 'Q-L01': '目标客户端安装了吗？用哪种方式安装、版本是什么？',
 'Q-L02': '系统/架构是否满足当前客户端要求？',
 'Q-L03': '当前有 MCP、插件、hooks、代理网关或其他开发工具吗？',
 'Q-L04': 'Claude 是否需要读取本机项目、调用本机软件或操作图形界面？',
 'Q-L05': '设备归个人还是组织管理？哪些权限和变更可接受？',
 'Q-V01': '已有虚拟机还是准备新建？使用什么虚拟化软件？',
 'Q-V02': '宿主与客机各是什么系统/架构？',
 'Q-V03': '可供 VM 使用的内存/磁盘大约多少？已有项目需要保留吗？',
 'Q-V04': '虚拟机怎样联网，代理在宿主还是客机？',
 'Q-V05': '需要共享哪些目录、剪贴板或工具？是否已有账号凭据挂载？',
 'Q-V06': '有没有快照/备份和可用的恢复方式？',
 'Q-S01': 'VPS 是用作开发机（Claude Code 跑在 VPS 上），还是只想当代理出口节点（那属于本机路线的出口选择）？',
 'Q-S02': '已有 VPS 还是新建？地区、系统和大致资源是什么？',
 'Q-S03': '是否能正常 SSH？有没有独立的控制台/救援入口？',
 'Q-S04': '上面有生产服务、数据库或未备份项目吗？',
 'Q-S05': '项目和数据能否存到远端？需依赖哪些本机应用或硬件？',
 'Q-S06': '服务器月费、流量和维护成本能接受多少？',
 'Q-S07': '希望终端、Remote-SSH 还是远程浏览器？如何备份和维护？',
 'Q-Z01': '这次只要讲解/计划，还是允许指定范围的只读检查？',
 'Q-Z02': '具体有哪些项目、历史、CLI、配置和其他服务必须保留？',
 'Q-Z03': '允许哪些具体变更，是否需要组织管理员处理？',
 'Q-Z04': '有没有备份、回滚或独立救援条件？',
 'Q-Z05': '是否保存/导出不含秘密的本次进度，还是仅留在当前对话？',
 'Q-C07': 'retired；从展示集、调度、画像必填和就绪要求中删除，不复用编号'}
DEVICE_CLEANUP_VALUES = {
    'Q-D01': frozenset({'current_restriction_on_target', 'past_restriction_on_target',
                       'ordinary_error_only', 'other_device_only', 'none_reported'}),
    'Q-D02': frozenset({'audit_only', 'full_claude_data_reset', 'other_scope', 'no_cleanup'}),
}
QUESTION_PROMPTS.update({
    'Q-D01': '本次选定设备 {target_alias} 曾用过被明确停用/封禁的 Claude 账号吗？请区分当前限制、过去限制、普通报错、仅其他设备、没有这类经历或不确定；无需账号名。',
    'Q-D02': '对 {target_alias} 的 Claude 本地数据，这次要只看清单、规划完整重置、暂不清理，还是其他范围？完整重置可另选已核实属于 Claude 的历史、配置与扩展；实际操作前另行确认保护清单、备份和影响。',
})
QUESTION_PROMPTS[RETIRED] = "Retired; never collect account ownership"
# Route, egress-source and mobile facts (ADR-018). Values are categorical; an unknown
# or declined answer is a fact state, never a value.
ROUTE_EXIT_VALUES = {
    'Q-X01': frozenset({'airport', 'self_built', 'residential_carpool', 'existing_stable_exit', 'undecided'}),
    'Q-X02': frozenset({'with_residential_exit', 'own_vps_ip_only', 'undecided'}),
    'Q-M01': frozenset({'ios', 'android', 'both', 'none'}),
    'Q-V07': frozenset({'omarchy', 'macos', 'other'}),
    'Q-V08': frozenset({'lan_bridged', 'shared_nat', 'other'}),
    'Q-V09': frozenset({'direct', 'remote_unreachable'}),
    'Q-S08': frozenset({'vps_own_ip', 'residential_chain', 'undecided'}),
    'Q-T01': frozenset({'none', 'evening_slow', 'drops', 'slow_transfer', 'desktop_lag', 'wrong_exit'}),
}
QUESTION_PROMPTS.update({
    'Q-X01': '固定出口 IP 想用哪种来源：纯净机场、自建梯（可搭配家宽出口）、家宽拼车，还是已经有稳定出口？还没想好也可以。',
    'Q-X02': '自建梯要不要搭配家宽出口，还是先只用 VPS 自己的 IP？',
    'Q-M01': '注册、登录或内购会在手机上做吗？是 iPhone/iPad、Android、两种都有，还是都没有？',
    'Q-V07': '虚拟机的客机系统用 Omarchy、macOS，还是其他？',
    'Q-V08': '虚拟机的网卡是 LAN 独立网卡（桥接），还是与宿主机共用的 shared NAT？',
    'Q-V09': '这台 Linux 机器你能直接连上管理，还是它在别人的网络或 NAT 之后、需要反向隧道才能管理（进阶路线）？',
    'Q-S08': 'VPS 的出口用 VPS 自己的 IP，还是在其上套一层家宽出口？',
    'Q-T01': '当前连接有没有问题：晚高峰慢、断流、大文件传输慢、远程桌面卡、出口 IP 不对，还是都没有？',
})
EXPOSURE_PROMPTS = {
    'Q-H01': '可能泄露的是哪类凭据、涉及哪个服务或客户端？只说类别和对象，不要发送密码、令牌或密钥内容。',
    'Q-H03': '有什么迹象提示凭据可能泄露？只提供脱敏后的提示或现象，不要贴原始秘密或完整日志。',
    'Q-H04': '发现泄露前做过什么相关操作，或把信息发到了哪类位置？不要贴具体秘密或含密链接。',
    'Q-H05': '哪些设备、客户端或自动任务可能使用这类凭据？只列受影响对象，不读取凭据内容。',
    'Q-H06': '是否已经通过官方渠道处理这次泄露，或收到需要完成的保护指示？不知道可以说明。',
}

# Context is routing metadata supplied explicitly by the host, never inferred
# from expertise, equipment ownership, IP geolocation or a default proposal.
CONTEXT_DEFAULTS = {
    "task": "subscription_preparation", "incident": "none", "incident_resolved": False,
    "incident_origin": "host", "account_incident_resolved": False, "device_incident_resolved": False, "device_incident_resolution_ref": None, "cleanup_offer_dismissed_ref": None,
    "ambiguous_experience": False, "subscription_conflict": False,
    "billing_channel": "unselected", "route": "local",
    "route_selection_basis": "default_proposal", "contact_phase": "PC0",
    "os_issue": "none", "language_change_needed": False,
    "timezone_issue": False, "windows10": False, "compatibility_needed": False,
    "plan_compatibility_needed": False,
    "current_order_plan_stale": False,
    "budget_needed": False, "gift_card": False, "buying_gift_card": False,
    "changing_store_region": False, "organization_task": False,
    "billing_product_ambiguous": False, "existing_test": False,
    "integration_used": False, "change_planned": False,
    "persistence_requested": False, "purchase_completed": False,
    "paused": False, "blocked_reason": None,
}
# Optional additive fields preserve the published schema-1 input contract.
PLAN_CONTEXT_FIELDS = {"plan_compatibility_needed", "current_order_plan_stale"}
INCIDENT_CONTEXT_FIELDS = {"incident_origin", "account_incident_resolved"}
DEVICE_CONTEXT_FIELDS = {"device_incident_resolved", "device_incident_resolution_ref", "cleanup_offer_dismissed_ref"}
ENUM_CONTEXT = {
    "task": {"subscription_preparation", "renew", "upgrade", "change_channel", "billing_issue",
             "environment", "network", "incident", "api", "enterprise", "compare", "cleanup"},
    "incident": {"none", "credential_exposure", "data_risk", "suspension", "identity_review",
                 "duplicate_charge", "unknown_error"},
    "incident_origin": {"host", "legacy_unverified"},
    "billing_channel": {"unselected", "apple", "google", "web", "api", "enterprise", "compare"},
    "route": {"local", "vm", "vps", "compare"},
    "route_selection_basis": {"default_proposal", "explicit_choice", "task_context", "accepted_default"},
    "contact_phase": {"PC0", "PC1", "PC2"},
    "os_issue": {"none", "display_language", "input_method", "locale", "browser_language", "app_language", "timezone"},
}
ACCOUNT_QUESTIONS = {"Q-J01", "Q-J02", "Q-C03", "Q-C04", "Q-C06", "Q-C08", "Q-C13"} | {qid for qid in QUESTION_PROMPTS if qid.startswith(("Q-P", "Q-A", "Q-G", "Q-W", "Q-I", "Q-E"))}
SENSITIVE_QUESTIONS = {"Q-D01", "Q-D02", "Q-J01", "Q-J02", "Q-C03", "Q-C09", "Q-C13", "Q-P04", "Q-W02", "Q-I02", "Q-Z01", "Q-Z03", "Q-Z05"}
POSTCONTACT = {"Q-A04", "Q-A05", "Q-A08", "Q-G03", "Q-G04", "Q-W04"}
RESOLVED = {"reported", "observed", "not_applicable"}
BILLING_TASKS = {"renew", "upgrade", "change_channel", "billing_issue"}
PLAN_DEPENDENCY_TASKS = {"environment", "network", "cleanup"}
PURCHASE_TASKS = {"subscription_preparation", "renew", "upgrade", "change_channel", "compare"}
# Only these explicit current-account categories establish an incident. Historical,
# stale, inferred and refused answers are not evidence of a current emergency.
ACCOUNT_INCIDENT_VALUES = {
    "Q-C03": {"current_suspension": "suspension"},
    "Q-C04": {"suspended": "suspension", "current_suspension": "suspension",
              "identity_review": "identity_review", "unknown_error": "unknown_error"},
}

class InterviewError(ValueError):
    """Invalid or unsafe interview data."""


def _now():
    return datetime.now(timezone.utc).isoformat()


def canonical(question_id):
    if question_id not in QUESTION_PROMPTS or question_id == RETIRED:
        raise InterviewError("Unknown or retired question ID")
    return ALIASES.get(question_id, question_id)


def _safe(value):
    """Conservative defense in depth, not a promise to detect arbitrary secrets."""
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise InterviewError("JSON keys must be strings")
            if re.search(r"password|passwd|secret|token|api.?key|private.?key|card.?number|gift.?code|ownership", key, re.I):
                raise InterviewError("Secret or retired ownership field rejected")
            _safe(child)
    elif isinstance(value, list):
        for item in value:
            _safe(item)
    elif isinstance(value, str):
        if re.search(r"(?:password|passwd|pwd|secret|token|api[_-]?key|authorization)\s*[:=]\s*\S+|[a-z][a-z0-9+.-]*://[^\s/@:]+:[^\s/@]+@|\bBearer\s+[A-Za-z0-9._~-]+", value, re.I):
            raise InterviewError("Credential assignment or credential-bearing URL rejected")
        if len(value) > 2000 or re.search(r"(?:sk-(?:ant-)?|ghp_|github_pat_)[A-Za-z0-9_-]{12,}|-----BEGIN .*PRIVATE KEY|(?:\d[ -]?){13,19}", value):
            raise InterviewError("Unsanitized or oversized value rejected")
    elif isinstance(value, float) and (value != value or abs(value) == float("inf")):
        raise InterviewError("Non-finite numbers are not JSON facts")
    elif value is not None and type(value) not in (bool, int, float):
        raise InterviewError("Only JSON values are supported")


def new_state(target_alias, account_alias, *, task_id="task-1"):
    """Create in-memory state. Aliases must be non-identifying local labels."""
    state = {
        "schema_version": SCHEMA_VERSION, "task_id": task_id,
        "target_alias": target_alias, "account_alias": account_alias,
        "facts": {}, "context": {key: deepcopy(value) for key, value in CONTEXT_DEFAULTS.items()
                                   if key not in DEVICE_CONTEXT_FIELDS | PLAN_CONTEXT_FIELDS},
        "asked_question_ids": [], "deferred_branches": [],
        "current_subscription": {"status": "unknown", "source": None, "observed_at": None},
        "payment_intent": "unresolved", "purchase_intent": "subscription_preparation",
        "persistence_consent": {"private_save": False, "export": False, "public_export": False},
    }
    validate_state(state)
    return state


def _sync_task_intent(state):
    """Refresh derived task labels, never subscription evidence or permissions."""
    context = state['context']
    if not (context['purchase_completed'] and state['purchase_intent'] == 'completed'):
        state['purchase_intent'] = ('subscription_preparation'
                                    if context['task'] in PURCHASE_TASKS else 'none')
        if context['task'] in PURCHASE_TASKS:
            state['payment_intent'] = (context['task'] if context['task'] in {'renew','upgrade','change_channel'}
                else {'first_subscription':'new_subscription','returning_subscription':'resubscribe'}.get(journey(state),'unresolved'))
    if context['task'] == 'billing_issue':
        state['payment_intent'] = 'troubleshoot'
    if context['task'] in {'environment', 'network', 'incident', 'cleanup'} or state['purchase_intent'] == 'completed':
        state['payment_intent'] = 'none'


def _validate_date(value):
    if value is not None:
        try:
            date = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if date.tzinfo is None:
                raise ValueError()
            return date
        except (ValueError, TypeError, AttributeError):
            raise InterviewError("Timestamp must be timezone-aware ISO 8601") from None


def validate_state(state):
    """Fail closed for unknown versions, fields, aliases, secret keys or malformed facts."""
    if not isinstance(state, dict) or state.get("schema_version") != SCHEMA_VERSION:
        raise InterviewError("Unsupported interview schema version")
    required = {"schema_version", "task_id", "target_alias", "account_alias", "facts", "context",
                "asked_question_ids", "deferred_branches", "current_subscription", "payment_intent",
                "purchase_intent", "persistence_consent"}
    if set(state) - required - {'resume_review', 'purchase_completion', 'subscription_review', 'authorization',
                                'capabilities', 'work_items', 'reference_topics'} or required - set(state):
        raise InterviewError("Unexpected or missing state fields")
    _safe(state)
    _validate_workflow_records(state)
    if 'authorization' in state:
        _validate_authorization(state)
    for name in ("task_id", "target_alias", "account_alias"):
        if not isinstance(state[name], str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", state[name]):
            raise InterviewError("Use short non-identifying aliases")
    ctx = state["context"]
    if (not isinstance(ctx, dict) or set(ctx) - set(CONTEXT_DEFAULTS)
            or set(CONTEXT_DEFAULTS) - set(ctx) - INCIDENT_CONTEXT_FIELDS - DEVICE_CONTEXT_FIELDS - PLAN_CONTEXT_FIELDS):
        raise InterviewError("Invalid routing context")
    for name, default in CONTEXT_DEFAULTS.items():
        if name not in ctx:
            continue
        if name in ENUM_CONTEXT and (not isinstance(ctx[name], str) or ctx[name] not in ENUM_CONTEXT[name]):
            raise InterviewError("Invalid context enum: " + name)
        if isinstance(default, bool) and type(ctx[name]) is not bool:
            raise InterviewError("Routing flags must be booleans")
    if ctx["blocked_reason"] is not None and not isinstance(ctx["blocked_reason"], str):
        raise InterviewError("Invalid blocker")
    if not isinstance(ctx.get("route"), str):
        raise InterviewError("Invalid route")
    if ctx["route_selection_basis"] == "accepted_default" and ctx["route"] != "local":
        raise InterviewError("Only local is the default proposal")
    if ctx['route'] == 'compare' and ctx['route_selection_basis'] != 'default_proposal':
        raise InterviewError('Comparison cannot establish route confirmation')
    if not isinstance(state["facts"], dict):
        raise InterviewError("Facts must be an object")
    for qid, fact in state["facts"].items():
        if canonical(qid) != qid:
            raise InterviewError("Store canonical IDs only")
        keys = {"value", "state", "source", "subject_ref", "observed_at", "applies_when",
                "required_for", "sensitivity", "clarification_count", "blocker_reason"}
        optional = {'retained_fields'} if qid == 'Q-P02' else set()
        if (not isinstance(fact, dict) or set(fact) - keys - optional or keys - set(fact)
                or not isinstance(fact["state"], str) or fact["state"] not in FACT_STATES):
            raise InterviewError("Invalid fact envelope")
        expected_subject = state["account_alias" if qid in ACCOUNT_QUESTIONS else "target_alias"]
        if fact["subject_ref"] != expected_subject:
            raise InterviewError("Fact target mismatch; question requires its specific account/device role")
        if fact["state"] == "inferred" and qid in SENSITIVE_QUESTIONS:
            raise InterviewError("Inference cannot establish protected facts")
        if fact["state"] in {"reported", "observed", "inferred"} and not fact["source"]:
            raise InterviewError("Fact provenance is required")
        if fact["state"] in {"unknown", "declined", "unasked", "deferred"} and fact["value"] is not None:
            raise InterviewError("Missing or refused facts must not masquerade as values")
        if type(fact["clarification_count"]) is not int or not 0 <= fact["clarification_count"] <= 1:
            raise InterviewError("At most one clarification is permitted")
        if fact["sensitivity"] != "low" or not isinstance(fact["required_for"], list) or any(x not in {"intake", "plan", "purchase", "apply"} for x in fact["required_for"]):
            raise InterviewError("Invalid fact metadata")
        for field in ("source", "applies_when", "blocker_reason"):
            if fact[field] is not None and not isinstance(fact[field], str):
                raise InterviewError("Fact metadata must be text or null")
        _validate_date(fact["observed_at"])
        if 'retained_fields' in fact:
            retained = fact['retained_fields']
            current_value = (isinstance(fact['value'], dict)
                             and fact['state'] in {'reported', 'observed', 'stale', 'conflict'})
            terminal_value = (fact['value'] is None
                              and fact['state'] in {'unknown', 'declined', 'deferred', 'stale', 'conflict'})
            if (not isinstance(retained, dict) or len(retained) != 1
                    or not (current_value or terminal_value)):
                raise InterviewError('Invalid scoped P02 retained field')
            for key, origin in retained.items():
                if (key not in {'plan', 'billing_channel', 'status', 'page_relation'}
                        or (isinstance(fact['value'], dict) and key in fact['value']) or not isinstance(origin, dict)
                        or set(origin) != {'value', 'state', 'source', 'subject_ref', 'observed_at'}
                        or not _p02_field_valid(key, origin['value'])
                        or type(origin['state']) is not str or origin['state'] not in {'reported', 'observed'}
                        or type(origin['source']) is not str or not origin['source']
                        or origin['subject_ref'] != expected_subject):
                    raise InterviewError('Invalid scoped P02 provenance')
                prior_date = _validate_date(origin['observed_at'])
                date = _validate_date(fact['observed_at'])
                if prior_date is not None and (date is None or prior_date > date):
                    raise InterviewError('Retained P02 field cannot postdate its current reply')
        if qid == 'Q-C13' and fact['state'] in {'reported', 'observed'}:
            if (type(fact['value']) is not str or not fact['value'].strip()
                    or fact['value'] == 'selected_unspecified'):
                raise InterviewError('Current plan requires an explicit nonempty plan report')
        if qid in DEVICE_CLEANUP_VALUES and fact['value'] is not None:
            if type(fact['value']) is not str or fact['value'] not in DEVICE_CLEANUP_VALUES[qid]:
                raise InterviewError('Invalid device cleanup category')
        if qid in DEVICE_CLEANUP_VALUES and fact['state'] in RESOLVED and fact['value'] is None:
            raise InterviewError('Device cleanup category required')
        if qid in ROUTE_EXIT_VALUES and fact['value'] is not None:
            if type(fact['value']) is not str or fact['value'] not in ROUTE_EXIT_VALUES[qid]:
                raise InterviewError('Invalid route or exit category')
        if qid in ROUTE_EXIT_VALUES and fact['state'] in {'reported', 'observed'} and fact['value'] is None:
            raise InterviewError('Route or exit category required')
        if qid in {"Q-J01", "Q-J02"} and fact["state"] in RESOLVED and (not isinstance(fact["value"], str) or fact["value"] not in JOURNEYS):
            raise InterviewError("Invalid subscription journey")
    choice = state['facts'].get('Q-C05')
    if choice is not None and ctx['route_selection_basis'] != 'default_proposal':
        selected = 'local' if choice['value'] == 'accepted_default' else choice['value']
        if choice['state'] not in {'reported', 'observed'} or selected != ctx['route']:
            # Old schema-1 snapshots can contain the former sticky-context bug.
            # There is no timestamped host-choice record with which to resolve
            # this conflict losslessly. Reject instead of rewriting its history.
            raise InterviewError('Stored route confirmation contradicts Q-C05; a current route reply is required')
    for reference_key in ('cleanup_offer_dismissed_ref', 'device_incident_resolution_ref'):
        reference = ctx.get(reference_key)
        if reference is not None and (type(reference) is not str or
                not re.fullmatch(r'[0-9a-f]{8}(?:\.[0-9a-f]{8}){7}', reference)):
            raise InterviewError('Invalid device episode reference')
    if ctx.get('device_incident_resolved', False):
        if (_value(state, 'Q-D01') != 'current_restriction_on_target' or
                ctx.get('device_incident_resolution_ref') != _device_episode_ref(state)):
            raise InterviewError('Device incident resolution requires current bound history')
    elif ctx.get('device_incident_resolution_ref') is not None:
        raise InterviewError('Device incident resolution reference without resolution')
    for field in ("asked_question_ids", "deferred_branches"):
        if not isinstance(state[field], list) or len(state[field]) != len(set(state[field])):
            raise InterviewError("Progress lists must be unique")
    for qid in state["asked_question_ids"]:
        if canonical(qid) != qid:
            raise InterviewError("Progress must use canonical IDs")
    if any(branch not in {"incident", "core", "os", "network", "payment", "local", "vm", "vps", "protection", "cleanup", "compatibility"} for branch in state["deferred_branches"]):
        raise InterviewError("Invalid deferred branch")
    consent = state["persistence_consent"]
    if not isinstance(consent, dict) or set(consent) != {"private_save", "export", "public_export"} or any(type(v) is not bool for v in consent.values()):
        raise InterviewError("Invalid persistence consent")
    current = state["current_subscription"]
    if not isinstance(current, dict) or set(current) != {"status", "source", "observed_at"} or current["status"] not in {"unknown", "none_reported", "active_reported", "observed_active", "conflict"}:
        raise InterviewError("Invalid current subscription")
    _validate_date(current["observed_at"])
    journey_facts = [fact for qid, fact in state["facts"].items() if qid in {"Q-J01", "Q-J02"}
                     and fact["state"] in {"reported", "observed"}]
    if len({fact["value"] for fact in journey_facts}) > 1:
        raise InterviewError("Conflicting subscription journey records")
    expected_status = {"first_subscription": {"none_reported"}, "returning_subscription": {"none_reported"},
                       "existing_subscriber": {"active_reported", "observed_active"}, "unknown": {"unknown"}}
    selected_journey = journey_facts[0]["value"] if journey_facts else "unknown"
    if current["status"] not in expected_status[selected_journey] | {"conflict"}:
        raise InterviewError("Derived subscription status contradicts current journey evidence")
    if state["payment_intent"] not in {"unresolved", "new_subscription", "resubscribe", "renew", "upgrade", "change_channel", "troubleshoot", "none"}:
        raise InterviewError("Invalid payment intent")
    if state["purchase_intent"] not in {"subscription_preparation", "completed", "none"}:
        raise InterviewError("Invalid purchase intent")
    receipt = state.get('purchase_completion')
    if 'purchase_completion' in state:
        if (not isinstance(receipt, dict) or set(receipt) != {'account_alias', 'source', 'observed_at', 'observed'}
                or receipt['account_alias'] != state['account_alias']
                or not isinstance(receipt['source'], str) or not receipt['source']
                or type(receipt['observed']) is not bool or receipt['observed_at'] is None):
            raise InterviewError('Invalid account-bound purchase completion receipt')
        _validate_date(receipt['observed_at'])
    _validate_resume_review(state)
    _validate_subscription_review(state)
    return state


def record_fact(state, question_id, value=None, *, state_name="reported", source=None,
                subject_ref=None, observed_at=None, blocker_reason=None, clarification=False,
                correction=False, current_reply=False):
    """Absorb each useful fact in a reply; does not mark actions authorized.

    Replacing an answer is an explicit host correction. Cross-object answers fail
    rather than overwrite a different machine/account's facts. Unknown/refused
    answers are terminal until the user volunteers a correction.

    Supplied incident timestamps identify evidence, not its import time. Replaying
    the same evidence cannot refresh it or reopen a resolved episode. Older or
    contradictory same-time evidence requires correction=True to explicitly
    replace a mistaken record without fabricating a newer observation time.
    Omitting observed_at means a new reply, even with the same source/value.
    A host with a genuinely current reply may set current_reply=True to preserve
    its explicit observation time. Historical data must never be relabeled as
    current; neither this flag nor correction is permission for external action.
    """
    if type(current_reply) is not bool:
        raise InterviewError('Current reply must be an explicit boolean')
    return _record_fact(state, question_id, value, state_name=state_name, source=source,
                        subject_ref=subject_ref, observed_at=observed_at,
                        blocker_reason=blocker_reason, clarification=clarification,
                        correction=correction, fresh_reply=current_reply or observed_at is None)


def _record_fact(state, question_id, value=None, *, state_name="reported", source=None,
                 subject_ref=None, observed_at=None, blocker_reason=None, clarification=False,
                 correction=False, fresh_reply=False):
    validate_state(state)
    qid = canonical(question_id)
    if type(state_name) is not str or state_name not in FACT_STATES:
        raise InterviewError("Invalid answer state")
    if type(correction) is not bool:
        raise InterviewError("Correction must be an explicit boolean")
    _validate_date(observed_at)
    result = deepcopy(state)
    _normalize_incident_context(result)
    _normalize_subscription_review(result)
    _normalize_current_order_plan(result)
    if qid in {"Q-J01", "Q-J02", "Q-C02", "Q-C03", "Q-C04", "Q-C05", "Q-C08", "Q-C13", "Q-C11", "Q-P06"} and value is not None and not isinstance(value, str):
        raise InterviewError("This routing fact requires a categorical string")
    if qid in ROUTE_EXIT_VALUES and value is not None and (type(value) is not str or value not in ROUTE_EXIT_VALUES[qid]):
        raise InterviewError("Invalid route or exit category")
    old = result["facts"].get(qid, {})
    count = old.get("clarification_count", 0) + int(clarification)
    if count > 1:
        raise InterviewError("Clarification exhausted; permit unknown, decline or pause")
    fact = {"value": deepcopy(value), "state": state_name, "source": source,
            "subject_ref": subject_ref or state["account_alias" if qid in ACCOUNT_QUESTIONS else "target_alias"], "observed_at": observed_at if observed_at is not None else _now(),
            "applies_when": "current task and target", "required_for": ["intake", "plan"],
            "sensitivity": "low", "clarification_count": count, "blocker_reason": blocker_reason}
    if (qid == 'Q-P02' and fresh_reply and not correction
            and state_name in {'reported', 'observed', 'unknown', 'declined', 'deferred'}):
        _retain_p02_complement(result, fact)
    prior_facts = result["facts"].copy()
    result["facts"][qid] = fact
    if (qid == 'Q-P02' and state_name in {'reported', 'observed'}
            and (not old or json.dumps(old['value'], sort_keys=True) != json.dumps(value, sort_keys=True))):
        _stale_old_order_followup(result)
    if qid == 'Q-D01' and result['context'].get('device_incident_resolved', False):
        if _device_episode_ref(result) != _device_episode_ref(state):
            result['context'].update(device_incident_resolved=False, device_incident_resolution_ref=None)
    if qid in DEVICE_CLEANUP_VALUES:
        validate_state(result)
    protected_order = (qid == 'Q-P02' and (old.get('state') in {'stale', 'conflict'}
                       or _upgrade_only_task(state) or state['context']['subscription_conflict']
                       or result['context'].get('current_order_plan_stale', False)))
    if (qid in ACCOUNT_INCIDENT_VALUES or qid in DEVICE_CLEANUP_VALUES or qid == "Q-C13" or qid.startswith("Q-H") or protected_order) and state_name in {"reported", "observed"}:
        # Validate the full candidate before a replay can return early; malformed
        # provenance, targets and metadata must not hide behind idempotency.
        validate_state(result)
        replay = _incident_evidence_replay(prior_facts, qid, fact, correction=correction,
                                           fresh_reply=fresh_reply)
        if replay is not None:
            result["facts"][qid] = deepcopy(replay)
            result["facts"][qid]["value"] = deepcopy(value)
            if qid == 'Q-D01' and state['context'].get('device_incident_resolved', False):
                result['context'].update(device_incident_resolved=True,
                    device_incident_resolution_ref=state['context']['device_incident_resolution_ref'])
            validate_state(result)
            return result
    if qid == 'Q-P02' and state_name in {'reported', 'observed'}:
        if old.get('state') in {'stale', 'conflict'} and not fresh_reply:
            fact.update(state='stale', blocker_reason='Historical order evidence requires a fresh current reply')
        review = result.get('subscription_review')
        if review is not None and review['status'] == 'unresolved':
            report = _current_subscription_report(review)
            if report['observed_at'] is not None and (not fresh_reply or
                    _validate_date(fact['observed_at']) < _validate_date(report['observed_at'])):
                fact.update(state='stale', blocker_reason='Current contradiction requires a fresh account/status reply')
            if report['detail'] is None and fact['state'] in {'reported', 'observed'}:
                report['detail'] = deepcopy(fact)
        if (fresh_reply and fact['state'] in {'reported', 'observed'} and isinstance(value, dict)
                and _named_plan(value.get('plan')) and _after_purchase_completion(result, fact)):
            if 'current_order_plan_stale' in result['context']:
                # Explicit false records that this runtime saw a fresh P02 plan
                # after the obligation. Do not mistake stale legacy C13 for a
                # new invalidation on the next load/device change.
                result['context']['current_order_plan_stale'] = False
    if qid == 'Q-C13' and state_name in {'reported', 'observed'}:

        # A historical snapshot is not a current reply. Neither a newer import
        # nor a changed source can discharge an existing freshness obligation.
        subscription_time = _validate_date(state['current_subscription']['observed_at'])
        plan_time = _validate_date(fact['observed_at'])
        if (old.get('state') in {'stale', 'conflict'} and not fresh_reply or
                subscription_time is not None and plan_time is not None and plan_time < subscription_time):
            fact.update(state='stale',
                        blocker_reason='Historical current-plan evidence requires a fresh current reply')
    if qid in {"Q-J01", "Q-J02"}:
        # These IDs describe one fact. A correction supersedes the alternative
        # entry instead of allowing registry priority to override recency.
        other = "Q-J02" if qid == "Q-J01" else "Q-J01"
        result["facts"].pop(other, None)
        result["current_subscription"] = {"status": "unknown", "source": source, "observed_at": fact["observed_at"]}
        result["payment_intent"] = "unresolved"
    if qid in {"Q-J01", "Q-J02"} and state_name in {"reported", "observed"}:
        status = {"first_subscription": "none_reported", "returning_subscription": "none_reported",
                  "existing_subscriber": "active_reported", "unknown": "unknown"}.get(value)
        result["current_subscription"] = {"status": status, "source": source, "observed_at": fact["observed_at"]}
        result["payment_intent"] = {"first_subscription": "new_subscription", "returning_subscription": "resubscribe"}.get(value, "unresolved")
    if qid in {"Q-J01", "Q-J02"} and journey(result) != journey(state):
        _stale_current_plan(result, 'Subscription stage changed; current plan requires a fresh report')
    if qid == 'Q-C05':
        if state_name in {'reported', 'observed'} and value == 'accepted_default':
            # Reject a nonexistent proposal before historical evidence can be
            # demoted to stale and bypass this explicit acceptance check.
            context = result['context']
            if context['route'] != 'local' or context['route_selection_basis'] not in {'default_proposal', 'accepted_default'}:
                raise InterviewError('No current local default proposal to accept')
        if old and not fresh_reply and state_name in {'reported', 'observed'}:
            old_time = _validate_date(old['observed_at'])
            choice_time = _validate_date(fact['observed_at'])
            if old_time is not None and choice_time is not None and choice_time < old_time:
                raise InterviewError('Older route evidence requires a fresh current reply')
        if (old and not fresh_reply and state_name in {'reported', 'observed'}
                and (old['state'] not in {'reported', 'observed'}
                     or not isinstance(old['value'], str)
                     or old['value'] not in {'local', 'vm', 'vps', 'accepted_default'})):
            fact.update(state='stale', blocker_reason='Withdrawn route requires a fresh current reply')
        if fact['state'] in {'reported', 'observed'} and value in {'local', 'vm', 'vps'}:
            result['context'].update(route=value, route_selection_basis='explicit_choice')
        elif fact['state'] in {'reported', 'observed'} and value == 'accepted_default':
            # Acceptance applies only to an actual current local proposal, not
            # to a withdrawn VM/VPS choice or comparison. It grants no action.
            result['context']['route_selection_basis'] = 'accepted_default'
        else:
            # Retract a confirmed choice without silently returning to local.
            # An unanswered proposal is different: unknown/refusal/defer does
            # not create agreement, but leaves that actual proposal available
            # for a later explicit acceptance. Explicit comparison replaces it.
            if (state['context']['route_selection_basis'] != 'default_proposal'
                    or fact['state'] in {'reported', 'observed'} and value == 'compare'):
                result['context'].update(route='compare', route_selection_basis='default_proposal')
    if qid == "Q-C11" and state_name in {"reported", "observed"} and value in ENUM_CONTEXT["task"]:
        if value != result['context']['task']:
            _clear_cleanup_goal(result)
            result['context'].pop('plan_compatibility_needed', None)
        result["context"]["task"] = value
        result["payment_intent"] = value if value in {"renew", "upgrade", "change_channel"} else "none"
    if qid == "Q-P06" and state_name in {"reported", "observed"} and value in ENUM_CONTEXT["billing_channel"]:
        result["context"]["billing_channel"] = value
    if qid in ACCOUNT_INCIDENT_VALUES and state_name in {"reported", "observed"}:
        if result["context"]["incident_origin"] == "legacy_unverified":
            # This fresh account correction replaces an unattributed old cache,
            # not a separately identified host incident.
            result["context"].update(incident="none", incident_origin="host")
    if (qid in ACCOUNT_INCIDENT_VALUES and state_name in {"reported", "observed"}
            and value in ACCOUNT_INCIDENT_VALUES[qid]):
        # A fresh current report reopens triage. Do not cache the derived incident
        # in host context: corrections/staleness must not leave it stuck there or
        # overwrite a separately reported credential/data emergency.
        if (_account_incident(state) != ACCOUNT_INCIDENT_VALUES[qid][value]
                or _account_incident_resolved(state)):
            _refresh_incident_answers(result)
        result["context"]["account_incident_resolved"] = False
    if qid in DEVICE_CLEANUP_VALUES and state_name in {'reported', 'observed'}:
        result['context'].pop('cleanup_offer_dismissed_ref', None)
    if (qid == 'Q-D01' and state_name in {'reported', 'observed'}
            and value == 'current_restriction_on_target'
            and not _device_triage(state)):
        _refresh_incident_answers(result)
        result['context'].update(device_incident_resolved=False, device_incident_resolution_ref=None)
    _invalidate_changed_route(result, state['context'])
    review = result.get('resume_review')
    if review is not None and qid in review['retained_keys']:
        # Only explicit fresh reports retire retained evidence. Re-rendering,
        # loading, and replaying an old observation cannot make it current.
        if fresh_reply and not (qid == 'Q-P02' and 'plan' in fact.get('retained_fields', {})):
            # A current channel answer/refusal has not refreshed the retained
            # plan's evidence across an actual interruption.
            review['retained_keys'].remove(qid)
    _refresh_resume_binding(result)
    _sync_task_intent(result)
    validate_state(result)
    return result


def _incident_evidence_replay(prior_facts, qid, fact, *, correction, fresh_reply):
    """Return retained evidence for a replay, or reject ambiguous chronology.

    C03 and C04 both describe account incidents. They share a time boundary, but
    a newer answer to one question does not silently erase the other's evidence.
    Explicit corrections can retain their real observation date. Exact replays
    still preserve resolution, staleness and the original clarification budget.
    """
    old = prior_facts.get(qid)
    observed = _validate_date(fact["observed_at"])
    def same_observation(previous):
        return (previous["source"] == fact["source"]
                and _validate_date(previous["observed_at"]) == observed)
    # Python equality conflates JSON true/1 (including nested values). Evidence
    # identity must preserve JSON types as well as its content and provenance.
    same_value = (old is not None and json.dumps(old["value"], sort_keys=True, allow_nan=False)
                  == json.dumps(fact["value"], sort_keys=True, allow_nan=False))
    if not fresh_reply and same_value and same_observation(old):
        return old
    relevant = ([previous for key, previous in prior_facts.items() if key in ACCOUNT_INCIDENT_VALUES]
                if qid in ACCOUNT_INCIDENT_VALUES else [old] if old else [])
    if not correction:
        for previous in relevant:
            previous_time = _validate_date(previous["observed_at"])
            if observed is not None and previous_time is not None and observed < previous_time:
                raise InterviewError("Older incident evidence requires an explicit correction")
        if not fresh_reply and old and _validate_date(old["observed_at"]) == observed:
            raise InterviewError("Conflicting same-time incident evidence requires an explicit correction")
    category = ACCOUNT_INCIDENT_VALUES[qid].get(fact["value"]) if qid in ACCOUNT_INCIDENT_VALUES else None
    if category and not fresh_reply:
        for key, previous in prior_facts.items():
            if (key in ACCOUNT_INCIDENT_VALUES
                    and isinstance(previous["value"], str)
                    and ACCOUNT_INCIDENT_VALUES[key].get(previous["value"]) == category
                    and same_observation(previous)):
                return previous
    return None


def record_facts(state, answers, *, source=None):
    """Atomically absorb normalized facts from one reply, before choosing a question.

    The host extracts explicit facts; this is not a natural-language parser.
    Each item uses question_id, value, optional state and source. Per-item source
    overrides the shared source. Duplicate canonical/alternative journey IDs are
    rejected instead of applying order-dependent corrections within one reply.
    Journey facts precede derived task updates regardless of JSON order. A
    resolved old-subscriber task conflicts with an explicit first/returning
    subscription journey and requires host clarification, not a guessed intent.
    Invalid input returns no partial state and never mutates the caller's state.
    No envelope field can grant action, contact or persistence permission.
    """
    validate_state(state)
    if not isinstance(answers, list) or not 1 <= len(answers) <= len(QUESTION_PROMPTS):
        raise InterviewError("Expected a bounded nonempty answer list")
    seen = set()
    for item in answers:
        if not isinstance(item, dict) or not isinstance(item.get("question_id"), str) or set(item) - {"question_id", "value", "state", "source"}:
            raise InterviewError("Invalid answer envelope")
        state_name = item.get("state", "reported")
        if type(state_name) is not str or state_name not in FACT_STATES:
            raise InterviewError("Invalid answer state")
        qid = canonical(item["question_id"])
        identity = "Q-J01" if qid == "Q-J02" else qid
        if identity in seen:
            raise InterviewError("Duplicate fact in one reply; clarify before recording")
        seen.add(identity)
    result = deepcopy(state)
    observed_at = _now()
    # Routing and task changes precede fresh facts from the same atomic reply.
    # Device episode precedes its explicit same-reply incident clarification.
    ordered = sorted(answers, key=lambda item: (
        0 if item['question_id'] in {'Q-J01', 'Q-J02'} else
        1 if item['question_id'] in {'Q-C05', 'Q-C11'} else
        2 if item['question_id'] == 'Q-D01' else
        3 if item['question_id'] in ACCOUNT_INCIDENT_VALUES else
        4 if item['question_id'] == 'Q-P02' else 5, item['question_id']))
    for item in ordered:
        if (item["question_id"] == "Q-C11" and item.get("state", "reported") in {"reported", "observed"}
                and journey(result) in {"first_subscription", "returning_subscription"}):
            raise InterviewError("Old-subscriber task conflicts with subscription journey; clarify first")
        result = _record_fact(result, item["question_id"], item.get("value"),
                              state_name=item.get("state", "reported"),
                              source=item.get("source", source), observed_at=observed_at,
                              fresh_reply=True)
    return result


def set_context(state, **changes):
    """Set explicit routing facts, not permissions. Context never opens G3.

    incident_resolved alone resolves the currently presented incidents for legacy
    callers. With an explicit incident it applies only to that host incident;
    account_incident_resolved can independently resolve current account evidence.
    Reporting an incident again after resolution starts a fresh episode unless
    the caller explicitly includes incident_resolved=True in the same update.
    A different route cannot inherit the prior choice basis. Supply its explicit
    basis in this call, or use a current Q-C05 answer. A contradictory retained
    Q-C05 requires the latter; routing flags cannot override that user answer.
    """
    validate_state(state)
    result = deepcopy(state)
    _normalize_incident_context(result)
    _normalize_subscription_review(result)
    _normalize_current_order_plan(result)
    if 'current_order_plan_stale' in changes:
        raise InterviewError('Current-order plan freshness is derived from evidence, not routing flags')
    if changes.get('subscription_conflict') is False and result['context']['subscription_conflict']:
        raise InterviewError('Unresolved subscription conflict requires current evidence-bound resolution')
    if state["context"]["paused"] and changes.get("paused") is False:
        raise InterviewError("Use resume_interview for an interrupted session")
    if 'task' in changes and changes['task'] != state['context']['task']:
        _clear_cleanup_goal(result)
        result['context'].pop('plan_compatibility_needed', None)
    if {'device_incident_resolution_ref', 'cleanup_offer_dismissed_ref'} & set(changes):
        raise InterviewError('Device episode reference is derived from current history')
    result["context"].update(changes)
    if 'route' in changes and changes['route'] != state['context']['route'] and 'route_selection_basis' not in changes:
        result['context']['route_selection_basis'] = 'default_proposal'
    if changes.get('subscription_conflict') is True and not state['context']['subscription_conflict']:
        _start_subscription_review(result, source='host:subscription_conflict', observed_at=_now())
        _stale_current_plan(result, 'Actual subscription conflict requires current-plan clarification')
    if 'device_incident_resolved' in changes:
        result['context']['device_incident_resolution_ref'] = (_device_episode_ref(result)
            if changes['device_incident_resolved'] is True else None)
    _invalidate_changed_route(result, state['context'], refreshed_context=changes)
    _refresh_resume_binding(result)
    if "incident" in changes:
        result["context"]["incident_origin"] = "host"
    if ("incident" in changes and changes["incident"] != "none"
            and (changes["incident"] != state["context"]["incident"]
                 or state["context"]["incident_resolved"])
            and "incident_resolved" not in changes):
        result["context"]["incident_resolved"] = False
    if ("incident_resolved" in changes and "incident" not in changes
            and "account_incident_resolved" not in changes):
        # Existing callers use this to resolve the incidents currently presented.
        result["context"]["account_incident_resolved"] = changes["incident_resolved"]
    if ("incident" in changes and result["context"]["incident"] != "none"
            and not result["context"]["incident_resolved"]
            and (state["context"]["incident"] != changes["incident"]
                 or state["context"]["incident_resolved"] or _legacy_incident_review(state))):
        _refresh_incident_answers(result)
    validate_state(result)
    _sync_task_intent(result)
    validate_state(result)
    return result


def journey(state):
    for qid in ("Q-J02", "Q-J01"):
        fact = state["facts"].get(qid, {})
        if fact.get("state") in {"reported", "observed"} and fact.get("value") in JOURNEYS:
            return fact["value"]
    return "unknown"


def _value(state, qid):
    qid = canonical(qid)
    fact = state["facts"].get(qid, {})
    if (qid == 'Q-P02' and fact.get('state') in {'unknown', 'declined', 'deferred'}
            and 'retained_fields' in fact):
        # The null outcome applies only to the scoped gap, not its older known
        # complement. Stale/conflict envelopes never enter this active path.
        return {key: origin['value'] for key, origin in fact['retained_fields'].items()}
    if fact.get('state') not in {'reported', 'observed'}:
        return None
    value = fact.get('value')
    if qid == 'Q-P02' and 'retained_fields' in fact:
        return {**{key: origin['value'] for key, origin in fact['retained_fields'].items()}, **value}
    return value


def _p02_component(fact, key):
    value = fact.get('value')
    if isinstance(value, dict) and key in value:
        return value[key], fact
    origin = fact.get('retained_fields', {}).get(key, {})
    return origin.get('value'), origin


def _p02_field_valid(key, value):
    return (_named_plan(value) if key == 'plan' else type(value) is str and value in {
        'billing_channel': {'apple', 'google', 'web'},
        'status': {'active', 'none', 'expired'},
        'page_relation': {'same_target', 'other_target', 'outdated'}}[key])


def _retain_p02_complement(state, fact):
    """Only an actual answer to the one scoped gap reuses its known complement.

    Keep the older field's own provenance; never restamp it as a new answer.
    A null terminal reply describes the gap alone, not the valid complement.
    Complete-order replacements, imports and corrections do not use this path.
    """
    old = state['facts'].get('Q-P02', {})
    value = fact['value']
    terminal = fact['state'] in {'unknown', 'declined', 'deferred'} and value is None
    old_terminal = old.get('state') in {'unknown', 'declined', 'deferred'} and 'retained_fields' in old
    if (old.get('state') not in {'reported', 'observed'} and not old_terminal
            or not isinstance(value, dict) and not terminal):
        return
    if _subscription_conflict_active(state):
        gaps = _conflict_detail_gaps(state)
        fields = {'subscription_status': ('status', 'page_relation'),
                  'page_relation': ('page_relation', 'status')}
    elif _upgrade_only_task(state):
        gaps = _upgrade_order_gaps(state)
        fields = {'current_plan': ('plan', 'billing_channel'),
                  'current_channel': ('billing_channel', 'plan')}
    else:
        return
    if len(gaps) != 1:
        return
    requested, complement = fields[gaps[0]]
    if not terminal and (not _p02_field_valid(requested, value.get(requested)) or complement in value):
        return
    retained, origin = _p02_component(old, complement)
    if _p02_field_valid(complement, retained):
        fact['retained_fields'] = {complement: {key: deepcopy(origin[key]) for key in
            ('state', 'source', 'subject_ref', 'observed_at')}}
        fact['retained_fields'][complement]['value'] = deepcopy(retained)


def _account_incident(state):
    """Derive account triage from current evidence, never from persisted caches."""
    for qid, categories in ACCOUNT_INCIDENT_VALUES.items():
        if qid == "Q-C03" and _legacy_incident_review(state):
            continue
        value = _value(state, qid)
        if isinstance(value, str) and value in categories:
            return categories[value]
    return "none"


def _urgent_incident(state):
    context = state["context"]
    return ((not context["incident_resolved"] and not _legacy_incident_review(state)
             and context["incident"] != "none")
            or (not _account_incident_resolved(state) and _account_incident(state) != "none"))


def _account_incident_resolved(state):
    return state["context"].get("account_incident_resolved", state["context"]["incident_resolved"])


def _legacy_incident_review(state):
    context = state["context"]
    origin = context.get("incident_origin")
    return (origin == "legacy_unverified" or
            (origin is None and context["incident"] == "suspension" and "Q-C03" in state["facts"]))


def _normalize_incident_context(state):
    """Upgrade only missing lifecycle metadata in an already validated copy.

    Published schema-1 cached Q-C03 suspension without provenance. It cannot be
    distinguished from an explicit host incident, so require fresh clarification
    rather than asserting either current suspension or resolution.
    """
    context = state["context"]
    if "incident_origin" not in context:
        legacy = _legacy_incident_review(state)
        context["incident_origin"] = "legacy_unverified" if legacy else "host"
        if legacy:
            fact = state["facts"]["Q-C03"]
            fact.update(state="stale", clarification_count=0,
                        blocker_reason="Legacy incident attribution and current status require confirmation")
            state["asked_question_ids"] = [qid for qid in state["asked_question_ids"] if qid != "Q-C03"]
    context.setdefault("account_incident_resolved", context["incident_resolved"])


def _refresh_incident_answers(state):
    """A new incident cannot reuse another episode's object, notice or recovery."""
    incident_ids = set(_ids("H", 1, 8))
    for qid in incident_ids & state["facts"].keys():
        state["facts"][qid].update(state="stale", clarification_count=0,
                                   blocker_reason="New incident requires current episode evidence")
    state["asked_question_ids"] = [qid for qid in state["asked_question_ids"] if qid not in incident_ids]


def _ids(prefix, start, end):
    return ["Q-%s%02d" % (prefix, i) for i in range(start, end + 1)]


def _device_episode_ref(state):
    fact = state['facts'].get('Q-D01')
    digest = hashlib.sha256(json.dumps(fact, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    # Fixed dots interrupt digit runs without exempting any field from _safe.
    # Preserve every digest bit; hyphens/spaces would still resemble card data.
    return '.'.join(digest[index:index + 8] for index in range(0, 64, 8))


def _cleanup_offer_dismissed(state):
    return state['context'].get('cleanup_offer_dismissed_ref') == _device_episode_ref(state)


def _clear_cleanup_goal(state):
    if 'Q-D01' in state['facts']:
        state['context']['cleanup_offer_dismissed_ref'] = _device_episode_ref(state)
    state['facts'].pop('Q-D02', None)
    state['asked_question_ids'] = [q for q in state['asked_question_ids'] if q != 'Q-D02']


def _device_triage(state):
    return (_value(state, 'Q-D01') == 'current_restriction_on_target'
            and not state['context'].get('device_incident_resolved', False))


def _invalidate_device_cleanup(state):
    """A route change cannot silently reuse a device association or reset goal."""
    if 'device_incident_resolved' in state['context']:
        state['context'].update(device_incident_resolved=False, device_incident_resolution_ref=None)
    for qid in DEVICE_CLEANUP_VALUES:
        if qid in state['facts']:
            state['facts'][qid].update(state='stale', blocker_reason='target_route_changed', clarification_count=0)
        if qid in state['asked_question_ids']:
            state['asked_question_ids'].remove(qid)


def _invalidate_changed_route(state, previous, *, refreshed_context=()):
    """Retire only route-bound planning evidence, never erase asset history.

    These aliases and facts are interview metadata, not a native TargetBinding
    or execution capability. The host must separately retire any action plan
    and target authorization that depended on the former choice.
    """
    context = state['context']
    changed = context['route'] != previous['route']
    was_confirmed = previous['route_selection_basis'] != 'default_proposal'
    withdrawn = was_confirmed and context['route_selection_basis'] == 'default_proposal'
    if not changed and not withdrawn:
        return
    # A scope belongs to one confirmed route; changing or withdrawing it never revives later.
    _stale_authorization(state, 'route_changed_or_withdrawn')
    _invalidate_device_cleanup(state)
    if not was_confirmed:
        return
    prefix = {'local': 'Q-L', 'vm': 'Q-V', 'vps': 'Q-S'}.get(previous['route'])
    dependent = {'Q-N02', 'Q-N05', 'Q-Z01', 'Q-Z03', 'Q-Z04', 'Q-X01', 'Q-X02'}
    dependent.update(qid for qid in state['facts'] if prefix and qid.startswith(prefix))
    for qid in dependent:
        fact = state['facts'].get(qid)
        # Do not turn a terminal refusal/unknown into an automatic new question.
        if fact and fact['state'] in {'reported', 'observed', 'inferred', 'stale', 'conflict', 'not_applicable'}:
            fact.update(state='stale', blocker_reason='route_choice_changed_or_withdrawn', clarification_count=0)
            state['asked_question_ids'] = [key for key in state['asked_question_ids'] if key != qid]
    for flag in ('existing_test', 'compatibility_needed', 'integration_used', 'change_planned'):
        if flag not in refreshed_context:
            context[flag] = False
    if 'plan_compatibility_needed' not in refreshed_context:
        context.pop('plan_compatibility_needed', None)


def _cleanup_mode(state):
    return (state['context']['task'] == 'cleanup' or
            _value(state, 'Q-D02') in {'audit_only', 'full_claude_data_reset', 'other_scope'})


def cleanup_assessment(state):
    """Pure selected-device goal projection; no inventory, apply or consent."""
    validate_state(state)
    if _billing_only_task(state) and not _cleanup_mode(state) and not _device_triage(state):
        return None
    if not (_cleanup_mode(state) or any(q in state['facts'] for q in DEVICE_CLEANUP_VALUES)):
        return None
    history = _value(state, 'Q-D01')
    intent = _value(state, 'Q-D02')
    trigger = ('explicit_full_reset' if intent == 'full_claude_data_reset' else
               'explicit_audit' if intent == 'audit_only' else
               'confirmed_target_history' if history == 'past_restriction_on_target' and intent != 'no_cleanup' and not _cleanup_offer_dismissed(state) else 'none')
    level = {'full_claude_data_reset': 'C5-full-claude-data-reset', 'audit_only': 'C0-audit'}.get(intent, 'unselected')
    step = ('scope_inventory' if level != 'unselected' else
            'select_cleanup_goal' if trigger == 'confirmed_target_history' or state['context']['task'] == 'cleanup' and intent is None else 'none')
    if _urgent_incident(state) or _legacy_incident_review(state) or _device_triage(state):
        step = 'incident_triage'
    elif intent == 'no_cleanup':
        step = 'none'
    elif state.get('resume_review', {}).get('status') in {'pending', 'unresolved'}:
        step = 'resume_review'
    elif state['context']['paused'] or state['context']['blocked_reason'] or 'cleanup' in state['deferred_branches']:
        step = 'deferred'
    return {'selected_target': state['target_alias'],
            'device_history': history or state['facts'].get('Q-D01', {}).get('state', 'unknown'),
            'trigger': trigger, 'requested_level': level, 'next_step': step,
            'plan_only': True, 'action_authorized': False, 'execution_status': 'not_run',
            'restriction_removal_claim': False}


def _stale_old_order_followup(state):
    """A materially different/expired P02 cannot reuse another order's A06."""
    fact = state['facts'].get('Q-A06')
    if fact and fact['state'] in {'reported', 'observed', 'stale', 'conflict'}:
        fact.update(state='stale', blocker_reason='Old-order facts changed; refresh only the relevant gaps',
                    clarification_count=0)
        state['asked_question_ids'] = [qid for qid in state['asked_question_ids'] if qid != 'Q-A06']


def _stale_current_plan(state, reason):
    """Retain account provenance, never revive an older effective plan."""
    plan, _ = _p02_component(state['facts'].get('Q-P02', {}), 'plan')
    if _named_plan(plan):
        # P02 remains valid historical order/channel evidence. Only its use as
        # the current plan is invalidated; do not erase or restamp that history.
        state['context']['current_order_plan_stale'] = True
        state['facts']['Q-P02']['clarification_count'] = 0
        state['asked_question_ids'] = [qid for qid in state['asked_question_ids'] if qid != 'Q-P02']
    fact = state['facts'].get('Q-C13')
    if fact and fact['state'] in {'reported', 'observed', 'stale', 'conflict'}:
        fact.update(state='stale', blocker_reason=reason, clarification_count=0)
        state['asked_question_ids'] = [qid for qid in state['asked_question_ids'] if qid != 'Q-C13']


def _named_plan(value):
    return type(value) is str and bool(value.strip()) and value != 'selected_unspecified'


def _order_plan_stale(state):
    context = state['context']
    return (context.get('current_order_plan_stale', False)
            or 'current_order_plan_stale' not in context
            and state['facts'].get('Q-C13', {}).get('state') in {'stale', 'conflict'})


def _after_purchase_completion(state, fact):
    date = _validate_date(fact.get('observed_at'))
    barriers = [state.get('purchase_completion', {}).get('observed_at')]
    if _order_plan_stale(state):
        barriers.append(state['current_subscription']['observed_at'])
    return all(value is None or date is not None and date >= _validate_date(value)
               for value in barriers)


def _normalize_current_order_plan(state):
    # Legacy completed states may predate the component freshness marker.
    fact = state['facts'].get('Q-P02', {})
    value, origin = _p02_component(fact, 'plan')
    if _named_plan(value) and (_order_plan_stale(state) or not _after_purchase_completion(state, origin)):
        if not state['context'].get('current_order_plan_stale', False):
            fact['clarification_count'] = 0
            state['asked_question_ids'] = [qid for qid in state['asked_question_ids'] if qid != 'Q-P02']
        state['context']['current_order_plan_stale'] = True


def _current_plan_needed(state):
    return (state['context'].get('plan_compatibility_needed', False)
            and state['context']['task'] in PLAN_DEPENDENCY_TASKS
            and journey(state) == 'existing_subscriber')


# One bounded subscription contradiction, not a billing/entitlement authority.
SUBSCRIPTION_OUTCOMES = {'existing_subscription', 'other_target_page', 'outdated_page'}


def _subscription_binding(state):
    return {**{key: state[key] for key in ('task_id', 'target_alias', 'account_alias')},
            'task': state['context']['task']}


def _subscription_conflict_active(state):
    return (state['context']['subscription_conflict']
            and state['context']['task'] in PURCHASE_TASKS | BILLING_TASKS
            and not _cleanup_mode(state))


def _current_subscription_report(review):
    return review.get('latest_report', review)


def _conflict_detail_gaps(state):
    fact = state['facts'].get('Q-P02', {})
    value = _value(state, 'Q-P02')
    value = value if isinstance(value, dict) else {}
    review = state.get('subscription_review')
    report = _current_subscription_report(review) if review else None
    gaps = []
    for key, gap in [('status', 'subscription_status'), ('page_relation', 'page_relation')]:
        _, origin = _p02_component(fact, key)
        old = (report and report['observed_at'] is not None and (origin.get('observed_at') is None
               or _validate_date(origin['observed_at']) < _validate_date(report['observed_at'])))
        if old or not _p02_field_valid(key, value.get(key)):
            gaps.append(gap)
    return gaps


def _prepare_subscription_detail(state, report):
    """A new observed report needs its own detail, not the prior episode's reply."""
    if report['observed_at'] is None:  # Legacy date unknown; retain its existing answers.
        return
    fact = state['facts'].get('Q-P02')
    if fact is not None and not _conflict_detail_gaps(state):
        report['detail'] = deepcopy(fact)
        return
    if fact is not None:
        fact.update(state='stale', clarification_count=0,
                    blocker_reason='New subscription contradiction requires current account/status detail')
    state['asked_question_ids'] = [qid for qid in state['asked_question_ids'] if qid != 'Q-P02']


def _start_subscription_review(state, *, source, observed_at):
    previous = state.get('subscription_review')
    if previous and previous['resolution'] is not None:
        if observed_at is None or _validate_date(observed_at) <= _validate_date(previous['resolution']['observed_at']):
            raise InterviewError('A new contradiction must follow the resolved episode')
    sequence = previous['sequence'] + 1 if previous else 1
    original = {qid: deepcopy(fact) for qid, fact in state['facts'].items()
                if qid in {'Q-J01', 'Q-J02', 'Q-P02'}}
    binding = _subscription_binding(state)
    digest = hashlib.sha256(json.dumps([binding, sequence, source, observed_at, original],
                                       sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()
    state['subscription_review'] = {
        'episode_id': '.'.join(digest[i:i + 8] for i in range(0, 64, 8)),
        'sequence': sequence, 'binding': binding, 'source': source,
        'observed_at': observed_at, 'original': original, 'detail': None,
        'status': 'unresolved', 'resolution': None}
    state['context']['subscription_conflict'] = True
    _prepare_subscription_detail(state, state['subscription_review'])


def _normalize_subscription_review(state):
    # A legacy true flag contains no page observation date. Retain that unknown,
    # rather than manufacturing a current observation on every load or retry.
    if state['context']['subscription_conflict'] and 'subscription_review' not in state:
        _start_subscription_review(state, source='legacy:subscription_conflict', observed_at=None)


def _resolution_answers(outcome, answers):
    if not isinstance(answers, list) or not 2 <= len(answers) <= 3:
        raise InterviewError('Resolution requires current journey and related order facts')
    values = {}
    for item in answers:
        if (not isinstance(item, dict) or set(item) - {'question_id', 'value', 'state'}
                or not {'question_id', 'value'}.issubset(item)
                or type(item['question_id']) is not str
                or item['question_id'] not in {'Q-J01', 'Q-P02', 'Q-C11'}
                or item['question_id'] in values
                or type(item.get('state', 'reported')) is not str
                or item.get('state', 'reported') not in {'reported', 'observed'}):
            raise InterviewError('Invalid current subscription resolution facts')
        values[item['question_id']] = item['value']
    if not {'Q-J01', 'Q-P02'}.issubset(values):
        raise InterviewError('Resolution requires current journey and related order facts')
    order = values['Q-P02']
    if (not isinstance(order, dict) or order.get('pending_issue') != 'none_reported'
            or order.get('billing_channel') is not None and (type(order['billing_channel']) is not str
                or order['billing_channel'] not in {'apple', 'google', 'web', 'none'})
            or order.get('plan') is not None and (type(order['plan']) is not str
                or not order['plan'].strip() or order['plan'] == 'selected_unspecified')):
        raise InterviewError('Resolution requires explicit current related-order status')
    if outcome == 'existing_subscription':
        if (values['Q-J01'] != 'existing_subscriber' or order.get('status') != 'active'
                or order.get('page_relation') != 'same_target'
                or order.get('billing_channel') == 'none'):
            raise InterviewError('Existing-subscription resolution requires matching current evidence')
        if 'Q-C11' in values and (type(values['Q-C11']) is not str
                or values['Q-C11'] not in ENUM_CONTEXT['task'] - {'subscription_preparation'}):
            raise InterviewError('Resolution next task must be an explicit supported task')
    elif outcome in {'other_target_page', 'outdated_page'}:
        if (type(values['Q-J01']) is not str or values['Q-J01'] not in {'first_subscription', 'returning_subscription'}
                or type(order.get('status')) is not str or order.get('status') not in {'none', 'expired'}
                or order.get('page_relation') != {'other_target_page': 'other_target',
                                                  'outdated_page': 'outdated'}[outcome]
                or 'Q-C11' in values):
            raise InterviewError('Page clarification requires matching same-account absence evidence')
    else:
        raise InterviewError('Unsupported subscription resolution outcome')
    return values


def _validate_subscription_review(state):
    review = state.get('subscription_review')
    if review is None and 'subscription_review' not in state:
        return
    keys = {'episode_id', 'sequence', 'binding', 'source', 'observed_at', 'original',
            'detail', 'status', 'resolution'}
    if (not isinstance(review, dict) or set(review) - keys - {'latest_report'} or keys - set(review)
            or type(review['episode_id']) is not str
            or not re.fullmatch(r'[0-9a-f]{8}(?:\.[0-9a-f]{8}){7}', review['episode_id'])
            or type(review['sequence']) is not int or review['sequence'] < 1
            or type(review['source']) is not str or not review['source']
            or type(review['status']) is not str or review['status'] not in {'unresolved', 'resolved'}):
        raise InterviewError('Invalid subscription review episode')
    _validate_date(review['observed_at'])
    binding = review['binding']
    if (not isinstance(binding, dict) or set(binding) != {'task_id', 'target_alias', 'account_alias', 'task'}
            or any(type(binding[key]) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', binding[key])
                   for key in ('task_id', 'target_alias', 'account_alias'))
            or type(binding['task']) is not str or binding['task'] not in ENUM_CONTEXT['task']
            or binding['account_alias'] != state['account_alias']):
        raise InterviewError('Subscription review account binding mismatch')
    if state['context']['subscription_conflict'] != (review['status'] == 'unresolved'):
        raise InterviewError('Subscription review contradicts unresolved flag')
    original = review['original']
    if not isinstance(original, dict) or set(original) - {'Q-J01', 'Q-J02', 'Q-P02'}:
        raise InterviewError('Invalid original subscription evidence')
    # Reuse the ordinary fact validator without accepting an arbitrary historical
    # state or trusting a snapshot's source/time/subject metadata.
    for facts in (original, {} if review['detail'] is None else {'Q-P02': review['detail']}):
        probe = new_state(binding['target_alias'], binding['account_alias'], task_id=binding['task_id'])
        probe['facts'] = deepcopy(facts)
        probe['current_subscription']['status'] = 'conflict'
        validate_state(probe)
    latest = review.get('latest_report')
    if 'latest_report' in review:
        if (not isinstance(latest, dict) or set(latest) != {'source', 'observed_at', 'binding', 'detail'}
                or type(latest['source']) is not str or not latest['source'] or latest['observed_at'] is None):
            raise InterviewError('Invalid latest subscription contradiction report')
        date = _validate_date(latest['observed_at'])
        opened = _validate_date(review['observed_at'])
        if opened is not None and date <= opened:
            raise InterviewError('Latest contradiction must follow the initial report')
        rb = latest['binding']
        if (not isinstance(rb, dict) or set(rb) != set(binding) or rb['account_alias'] != binding['account_alias']
                or any(type(rb[key]) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', rb[key])
                       for key in ('task_id', 'target_alias', 'account_alias'))
                or type(rb['task']) is not str or rb['task'] not in ENUM_CONTEXT['task']):
            raise InterviewError('Invalid latest contradiction binding')
        if latest['detail'] is not None:
            probe = new_state(rb['target_alias'], rb['account_alias'], task_id=rb['task_id'])
            probe['facts'] = {'Q-P02': deepcopy(latest['detail'])}
            validate_state(probe)
            if latest['detail']['observed_at'] is None or _validate_date(latest['detail']['observed_at']) < date:
                raise InterviewError('Latest contradiction detail predates its report')
    resolution = review['resolution']
    if review['status'] == 'unresolved':
        if resolution is not None:
            raise InterviewError('Unresolved subscription episode cannot carry a resolution')
    else:
        if (not isinstance(resolution, dict)
                or set(resolution) != {'binding', 'outcome', 'answers', 'source', 'observed_at'}
                or type(resolution['source']) is not str or not resolution['source']
                or resolution['observed_at'] is None):
            raise InterviewError('Invalid subscription resolution record')
        rb = resolution['binding']
        if (not isinstance(rb, dict) or set(rb) != set(binding)
                or rb['account_alias'] != binding['account_alias']
                or any(type(rb[key]) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', rb[key])
                       for key in ('task_id', 'target_alias', 'account_alias'))
                or type(rb['task']) is not str or rb['task'] not in ENUM_CONTEXT['task']):
            raise InterviewError('Invalid subscription resolution binding')
        date = _validate_date(resolution['observed_at'])
        opened = _validate_date(_current_subscription_report(review)['observed_at'])
        if opened is not None and date <= opened:
            raise InterviewError('Resolution must follow the actual contradiction')
        retained = list(original.values()) + ([] if review['detail'] is None else [review['detail']])
        if latest and latest['detail'] is not None:
            retained.append(latest['detail'])
        if any(fact['observed_at'] is not None and date < _validate_date(fact['observed_at']) for fact in retained):
            raise InterviewError('Resolution predates retained subscription evidence')
        if type(resolution['outcome']) is not str or resolution['outcome'] not in SUBSCRIPTION_OUTCOMES:
            raise InterviewError('Unsupported subscription resolution outcome')
        values = _resolution_answers(resolution['outcome'], resolution['answers'])
        if resolution['outcome'] != 'existing_subscription':
            prior_journey = next((fact['value'] for qid, fact in original.items()
                                  if qid in {'Q-J01', 'Q-J02'} and fact['state'] in {'reported', 'observed'}), None)
            if values['Q-J01'] != prior_journey:
                raise InterviewError('Page clarification contradicts original subscription journey')


def report_subscription_conflict(state, *, source, observed_at=None, current_reply=False):
    """Record the host's actual current same-account/task contradiction.

    Use only sanitized reported/authorized evidence. This is not page access,
    natural-language detection, entitlement verification, or action permission.
    Keep the initial episode and one latest report. Exact retries retain dates;
    a newer actual report advances the evidence barrier and refreshes only its
    focused clarification. An old resolution cannot clear that newer evidence.
    """
    result = deepcopy(validate_state(state))
    if type(current_reply) is not bool or not isinstance(source, str) or not source:
        raise InterviewError('Actual subscription contradiction requires provenance')
    _safe(source)
    date = _validate_date(observed_at)
    if observed_at is not None and not current_reply:
        raise InterviewError('Historical import cannot establish a current subscription episode')
    retained = state.get('subscription_review')
    if retained is not None and observed_at is not None:
        for report in (retained, _current_subscription_report(retained)):
            if source == report['source'] and date == _validate_date(report['observed_at']):
                return result
    if state['context']['subscription_conflict']:
        _normalize_subscription_review(result)
        review = result['subscription_review']
        report = _current_subscription_report(review)
        effective_at = observed_at or _now()
        date = _validate_date(effective_at)
        old_date = _validate_date(report['observed_at'])
        if source == report['source'] and date == old_date:
            return result
        if old_date is not None and date <= old_date:
            raise InterviewError('Older or same-time changed contradiction cannot replace current evidence')
        if (report['detail'] is not None and report['detail']['observed_at'] is not None
                and date < _validate_date(report['detail']['observed_at'])):
            raise InterviewError('New contradiction cannot discard later retained detail evidence')
        review['latest_report'] = {'source': source, 'observed_at': effective_at,
                                  'binding': _subscription_binding(result), 'detail': None}
        _prepare_subscription_detail(result, review['latest_report'])
        _stale_current_plan(result, 'New actual subscription evidence requires current-plan clarification')
        return validate_state(result)
    prior = state.get('subscription_review', {}).get('resolution')
    if date is not None and prior is not None and date <= _validate_date(prior['observed_at']):
        raise InterviewError('Replayed contradiction cannot reopen a resolved episode')
    _start_subscription_review(result, source=source, observed_at=observed_at or _now())
    _stale_current_plan(result, 'Actual subscription conflict requires current-plan clarification')
    return validate_state(result)


def resolve_subscription_conflict(state, *, episode_id, account_ref, target_ref, task_id,
                                  outcome, answers, source, observed_at=None, current_reply=False):
    """Atomically record one explicit current reply resolving this exact episode.

    Supported normalized outcomes require compatible journey/order evidence.
    For active-subscription discovery, omit C11 if the next task was not specified;
    the one relevant task question remains open. Other-target page evidence does
    not switch accounts; use begin_task only for an actually requested new target.
    Unknown/declined/deferred stop P02 repeats without clearing the contradiction.
    Exact retries preserve timestamps and all later facts. No outcome is a purchase.
    """
    result = deepcopy(validate_state(state))
    _normalize_subscription_review(result)
    review = result.get('subscription_review')
    if (review is None or episode_id != review['episode_id']
            or (account_ref, target_ref, task_id) != (state['account_alias'], state['target_alias'], state['task_id'])):
        raise InterviewError('No matching current account/task subscription episode')
    if type(current_reply) is not bool or not isinstance(source, str) or not source:
        raise InterviewError('Resolution requires explicit current provenance')
    _safe({'answers': answers, 'source': source, 'outcome': outcome})
    date = _validate_date(observed_at)
    if type(outcome) is not str or outcome not in SUBSCRIPTION_OUTCOMES | {'unknown', 'declined', 'deferred'}:
        raise InterviewError('Unsupported subscription resolution outcome')
    if outcome in SUBSCRIPTION_OUTCOMES:
        values = _resolution_answers(outcome, answers)
    elif answers != []:
        raise InterviewError('Unresolved reply cannot contain affirmative resolution facts')
    receipt = {'binding': _subscription_binding(state), 'outcome': outcome,
               'answers': deepcopy(answers), 'source': source, 'observed_at': observed_at or _now()}
    prior = review['resolution']
    if prior is not None:
        # Task changes made by the original resolution are expected. Its original
        # binding remains immutable; device/task-id changes are not the same retry.
        same = (all(prior[key] == receipt[key] for key in ('outcome', 'answers', 'source'))
                and all(prior['binding'][key] == receipt['binding'][key]
                        for key in ('task_id', 'target_alias', 'account_alias'))
                and (observed_at is None or date == _validate_date(prior['observed_at'])))
        if same:
            return deepcopy(state)
        raise InterviewError('Subscription episode already resolved')
    if state['context']['task'] not in PURCHASE_TASKS | BILLING_TASKS:
        raise InterviewError('Resolve subscription evidence only in its dependent billing task')
    if observed_at is not None and not current_reply:
        raise InterviewError('Resolution must be a current reply, not an imported snapshot')
    date = _validate_date(receipt['observed_at'])
    report = _current_subscription_report(review)
    opened = _validate_date(report['observed_at'])
    evidence = list(review['original'].values()) + list(state['facts'].get(qid, {})
                for qid in ('Q-J01', 'Q-J02', 'Q-P02'))
    if review['detail'] is not None:
        evidence.append(review['detail'])
    if report is not review and report['detail'] is not None:
        evidence.append(report['detail'])
    if (opened is not None and date <= opened or any(
            fact.get('observed_at') is not None and date < _validate_date(fact['observed_at'])
            for fact in evidence)):
        raise InterviewError('Stale resolution cannot clear current subscription evidence')
    if outcome not in SUBSCRIPTION_OUTCOMES:
        return _record_fact(result, 'Q-P02', state_name=outcome, source=source,
                            observed_at=receipt['observed_at'], fresh_reply=True)
    if outcome != 'existing_subscription':
        prior_journey = next((fact['value'] for qid, fact in review['original'].items()
                              if qid in {'Q-J01', 'Q-J02'} and fact['state'] in {'reported', 'observed'}), None)
        if values['Q-J01'] != prior_journey:
            raise InterviewError('Page clarification must preserve the original subscription journey')
    # Remove an old task answer when discovery did not establish the next task.
    # Do not use complete_purchase: this reply is no completed-purchase report.
    result['subscription_review'].update(status='resolved', resolution=receipt)
    result['context']['subscription_conflict'] = False
    if outcome == 'existing_subscription':
        result['facts'].pop('Q-C11', None)
        result['asked_question_ids'] = [qid for qid in result['asked_question_ids'] if qid != 'Q-C11']
        result['context']['task'] = 'subscription_preparation'
        result['context']['purchase_completed'] = False
        result['purchase_intent'] = 'none'
    for item in sorted(answers, key=lambda item: {'Q-J01': 0, 'Q-C11': 1, 'Q-P02': 2}[item['question_id']]):
        result = _record_fact(result, item['question_id'], item['value'],
                              state_name=item.get('state', 'reported'), source=source,
                              observed_at=receipt['observed_at'], fresh_reply=True)
    _refresh_resume_binding(result)
    _sync_task_intent(result)
    return validate_state(result)


def _old_billing_needed(state):
    c = state['context']
    return (_subscription_conflict_active(state)
            or journey(state) == 'existing_subscriber' and c['task'] in BILLING_TASKS
            or journey(state) == 'returning_subscription' and c['task'] in {'billing_issue', 'change_channel'})


def _billing_only_task(state):
    return state['context']['task'] == 'billing_issue' and _old_billing_needed(state)


def _upgrade_only_task(state):
    return state['context']['task'] == 'upgrade' and journey(state) == 'existing_subscriber'


def _subscription_task_needed(state):
    return (journey(state) == 'existing_subscriber'
            and state['context']['task'] == 'subscription_preparation'
            and state.get('subscription_review', {}).get('status') == 'resolved')


def _upgrade_order_gaps(state):
    order = _value(state, 'Q-P02')
    order = order if isinstance(order, dict) else {}
    fact = state['facts'].get('Q-P02', {})
    _, plan_origin = _p02_component(fact, 'plan')
    plan = (order.get('plan') if not _order_plan_stale(state)
            and _after_purchase_completion(state, plan_origin) else None)
    if not _named_plan(plan):
        plan = _value(state, 'Q-C13')
    gaps = []
    if type(plan) is not str or not plan.strip() or plan == 'selected_unspecified':
        gaps.append('current_plan')
    if type(order.get('billing_channel')) is not str or order['billing_channel'] not in {'apple', 'google', 'web'}:
        gaps.append('current_channel')
    return gaps


def _focused_subscription_task(state):
    return (_billing_only_task(state) or _upgrade_only_task(state)
            or _subscription_conflict_active(state) or _subscription_task_needed(state))


def _ask_apple_old_order(state):
    value = _value(state, 'Q-P02')
    old_channel = value.get('billing_channel') if isinstance(value, dict) else None
    channel = (old_channel if isinstance(old_channel, str) and old_channel in {'apple', 'google', 'web'}
               else state['context']['billing_channel'])
    return (channel == 'apple' and not _old_order_covered(state)
            and state['facts'].get('Q-P02', {}).get('state') not in {'unknown', 'declined', 'deferred'})


def _old_order_covered(state):
    """Only explicit complete old-order categories cover A06; never future channel.

    Legacy free-text P02 remains valid but carries no machine-readable completeness
    claim. The host may instead record P02/A06 together from the same real reply.
    """
    value = _value(state, 'Q-P02')
    return (isinstance(value, dict) and isinstance(value.get('billing_channel'), str)
            and value['billing_channel'] in {'apple', 'google', 'web'}
            and all(isinstance(value.get(key), str) and value[key].strip()
                    for key in ('status', 'pending_issue')))


def _old_order_needs_clarification(state):
    # Structured partial non-Apple orders have no A06 follow-up. Do not let a
    # reported partial object turn a missing billing dependency into G2 pass.
    if _subscription_conflict_active(state):
        return (state['facts'].get('Q-P02', {}).get('state') in {'reported', 'observed'}
                and bool(_conflict_detail_gaps(state)))
    if _upgrade_only_task(state):
        return (state['facts'].get('Q-P02', {}).get('state') in {'reported', 'observed'}
                and bool(_upgrade_order_gaps(state)))
    return (isinstance(_value(state, 'Q-P02'), dict) and not _old_order_covered(state)
            and not _ask_apple_old_order(state) and _value(state, 'Q-A06') is None)


def applicable_questions(state):
    """Return ordered branch requirements for the host, never a user-facing form."""
    validate_state(state)
    c = state["context"]
    requirements = []
    def add(branch, stage, ids):
        for qid in ids:
            qid = canonical(qid)
            if not any(x["id"] == qid for x in requirements):
                requirements.append({"id": qid, "branch": branch, "stage": stage,
                                     "postcontact": qid in POSTCONTACT})
    urgent = _urgent_incident(state)
    if urgent:
        add("incident", "I0", _ids("H", 1, 7))
        # Do not delay protective/official incident handling with purchasing.
        return requirements
    if _legacy_incident_review(state):
        add("incident", "I0", ["Q-C03"])
        return requirements
    if _device_triage(state):
        add('incident', 'I0', ['Q-H01', 'Q-C04'])
        return requirements
    if _cleanup_mode(state):
        if _value(state, 'Q-D02') == 'no_cleanup':
            return requirements
        add('cleanup', 'I2', ['Q-D02', 'Q-C02', 'Q-C01'])
        if _value(state, 'Q-C02') == 'macos':
            add('cleanup', 'I2', ['Q-OS03'])
        elif _value(state, 'Q-C02') == 'windows':
            add('cleanup', 'I2', ['Q-OS02'])
        if c['route_selection_basis'] == 'default_proposal':
            add('cleanup', 'I3', ['Q-C05'])
        add('cleanup', 'I5', ['Q-C12', 'Q-Z01'])
        if _value(state, 'Q-D02') in {'full_claude_data_reset', 'other_scope'}:
            add('cleanup', 'I5', ['Q-Z03', 'Q-Z04'])
        if _current_plan_needed(state):
            add('compatibility', 'I5', ['Q-C13'])
        return requirements
    if _subscription_conflict_active(state):
        # Coverage of the description is not resolution. Stop the dependent
        # purchase survey until the actual account/subscription mismatch clears.
        add('payment', 'I4', ['Q-P02'])
        return requirements
    if _subscription_task_needed(state):
        add('core', 'I1', ['Q-C11'])
        return requirements
    if _upgrade_only_task(state):
        add('payment', 'I4', ['Q-P02'])
        add('core', 'I2', ['Q-C08'])
        if c['compatibility_needed']:
            # An explicitly identified client dependency is separate from the
            # ordinary new-purchase/deployment survey and remains a real gap.
            add('compatibility', 'I5', ['Q-C02', 'Q-L02'])
        if c['budget_needed'] or _value(state, 'Q-C08') in {'compare', 'undecided'}:
            add('core', 'I2', ['Q-C01'])
            add('payment', 'I4', ['Q-P05'])
        if c['billing_product_ambiguous']:
            add('payment', 'I4', ['Q-P01'])
        return requirements
    if _billing_only_task(state):
        # A legacy refund/restoration explanation must not require unrelated
        # purchase, device-history or deployment prerequisites. Urgent current
        # incidents and an explicitly active cleanup goal retain priority above.
        add('core', 'I1', ['Q-J02' if _value(state, 'Q-J02') in JOURNEYS - {'unknown'} else 'Q-J01'])
        if c['billing_product_ambiguous']:
            add('payment', 'I4', ['Q-P01'])
        add('payment', 'I4', ['Q-P02'])
        if _ask_apple_old_order(state):
            add('payment', 'I4', ['Q-A06'])
        return requirements
    if _value(state, 'Q-C03') == 'past_suspension' and 'Q-D01' not in state['facts']:
        add('cleanup', 'I3', ['Q-D01'])
    if _value(state, 'Q-D01') == 'past_restriction_on_target' and not _cleanup_offer_dismissed(state):
        add('cleanup', 'I3', ['Q-D02'])
    if 'Q-D01' in state['facts'] and state['facts']['Q-D01']['state'] in {'unasked', 'stale', 'conflict'}:
        add('cleanup', 'I3', ['Q-D01'])
    add("core", "I1", ["Q-J02" if (c["ambiguous_experience"] and journey(state) == "unknown") or _value(state, "Q-J02") in JOURNEYS - {"unknown"} else "Q-J01"])
    j = journey(state)
    if j == "existing_subscriber" and c["task"] == "subscription_preparation":
        add("core", "I1", ["Q-C11"])
    purchase = (c["task"] in PURCHASE_TASKS and (j != "existing_subscriber" or c["task"] != "subscription_preparation") and not c["purchase_completed"])
    add("core", "I2", ["Q-C02", "Q-C01"])
    os = _value(state, "Q-C02")
    if os == "windows":
        add("os", "I2", ["Q-OS02"])
        if c["os_issue"] != "none":
            add("os", "I2", ["Q-OS09"])
        if c["os_issue"] in {"display_language", "input_method", "locale", "browser_language", "app_language"}:
            add("os", "I2", ["Q-OS04"])
        if c["os_issue"] == "display_language":
            add("os", "I2", ["Q-OS05"])
        if c["timezone_issue"] or c["os_issue"] == "timezone":
            add("os", "I2", _ids("OS", 6, 8))
        if c["windows10"]:
            add("os", "I2", ["Q-OS10"])
    elif os == "macos":
        add("os", "I2", ["Q-OS03"])
        if c["os_issue"] != "none":
            add("os", "I2", ["Q-OS09", "Q-OS11"])
    elif os in {"linux", "mobile_only", "other"}:
        add("os", "I2", ["Q-OS12"])
        if os == "mobile_only":
            add("os", "I2", ["Q-M01"])
    if purchase:
        add("core", "I2", ["Q-C08"])
    add("core", "I3", ["Q-C03", "Q-C04"])
    if c["route_selection_basis"] == "default_proposal":
        add("core", "I3", ["Q-C05"])
    if _value(state, "Q-C04") not in (None, "unregistered"):
        add("core", "I3", ["Q-C06"])
    if (_value(state, "Q-C03") in {"past_suspension", "past_incident"}
            or (c["incident_resolved"] and c["incident"] != "none")
            or (_account_incident_resolved(state) and _account_incident(state) != "none")):
        add("incident", "I3", _ids("H", 1, 8))
    add("network", "I4", ["Q-C09", "Q-N01", "Q-N02", "Q-N03", "Q-N04", "Q-N06"])
    if c["existing_test"]:
        add("network", "I4", ["Q-N05"])
    old = _old_billing_needed(state)
    if old:
        add("payment", "I4", ["Q-P02"])
        if _ask_apple_old_order(state):
            add("payment", "I4", ["Q-A06"])
    if purchase or c["task"] in {"api", "enterprise", "billing_issue"}:
        if c["billing_product_ambiguous"]:
            add("payment", "I4", ["Q-P01"])
        channel = c["billing_channel"]
        if channel in {"unselected", "compare"}:
            add("payment", "I4", ["Q-P03", "Q-P04", "Q-P06"])
        if c["budget_needed"] or _value(state, "Q-C08") in {"compare", "undecided"}:
            add("payment", "I4", ["Q-P05"])
        add("payment", "I4", ["Q-P07"])
        if channel == "apple":
            add("payment", "I4", _ids("A", 1, 5) + ["Q-M01"])
            if c["gift_card"]:
                add("payment", "I4", ["Q-A07", "Q-A08"])
            if c["buying_gift_card"]:
                add("payment", "I4", ["Q-A09"])
            add("payment", "I4", ["Q-A10"])
        elif channel == "google":
            add("payment", "I4", _ids("G", 1, 5) + ["Q-M01"])
        elif channel == "web":
            add("payment", "I4", _ids("W", 1, 4))
        if channel == "api" or c["task"] == "api":
            add("payment", "I4", ["Q-I01", "Q-I03", "Q-I04"])
            if c["organization_task"]:
                add("payment", "I4", ["Q-I02"])
        if channel == "enterprise" or c["task"] == "enterprise":
            add("payment", "I4", _ids("E", 1, 2))
    if c["route_selection_basis"] != "default_proposal" and c["route"] != "compare":
        route = c["route"]
        if route == "local":
            add(route, "I5", ["Q-L01", "Q-L04"])
            if c["compatibility_needed"]:
                add(route, "I5", ["Q-L02"])
            if c["integration_used"]:
                add(route, "I5", ["Q-L03"])
            add(route, "I5", ["Q-X01"])
            if _value(state, "Q-X01") == "self_built":
                add(route, "I5", ["Q-X02", "Q-T01"])
        elif route == "vm":
            add(route, "I5", _ids("V", 1, 6) + ["Q-V07", "Q-V08", "Q-V09", "Q-X01"])
            if _value(state, "Q-X01") == "self_built":
                add(route, "I5", ["Q-X02", "Q-T01"])
        elif route == "vps":
            add(route, "I5", _ids("S", 1, 7) + ["Q-S08", "Q-T01"])
    if _current_plan_needed(state):
        add("compatibility", "I5", ["Q-C13"])
    add("protection", "I5", ["Q-C12", "Q-Z01", "Q-C10"])
    if c["change_planned"]:
        add("protection", "I5", ["Q-Z03", "Q-Z04"])
    if c["persistence_requested"]:
        add("protection", "I5", ["Q-Z05"])
    return requirements


def _plan_identity_missing(fact):
    # A current reported selection is useful even when its name was not supplied.
    # This reserved categorical value adds no field/schema or implied plan choice.
    return (fact.get('state') in {'reported', 'observed'}
            and fact.get('value') == 'selected_unspecified')


def next_question(state):
    """Choose one unanswered relevant question, or None on pause/terminal coverage.

    An emitted question is not yet asked: call mark_asked after delivering it.
    Unknown/declined/deferred answers are not re-asked automatically. Stale or
    conflicting facts receive at most one clarification. PC0 never asks the host
    to launch Claude or perform a live payment check.
    """
    validate_state(state)
    if state["context"]["paused"] or state["context"]["blocked_reason"]:
        return None
    if (state.get("resume_review", {}).get("status") == "pending"
            and not _urgent_incident(state) and not _legacy_incident_review(state) and not _device_triage(state)):
        return None
    for item in applicable_questions(state):
        if item["branch"] in state["deferred_branches"]:
            continue
        if item["postcontact"] and state["context"]["contact_phase"] == "PC0":
            continue
        fact = state["facts"].get(item["id"], {})
        status = fact.get("state", "unasked")
        if item["id"] == "Q-C03" and _legacy_incident_review(state) and status in RESOLVED:
            status = "stale"
        unnamed_plan = item['id'] == 'Q-C08' and _plan_identity_missing(fact)
        partial_order = item['id'] == 'Q-P02' and _old_order_needs_clarification(state)
        clarification = status in {"conflict", "stale"} or unnamed_plan or partial_order
        if status != "unasked" and not (clarification and fact.get("clarification_count", 0) == 0):
            continue
        if item["id"] in state["asked_question_ids"] and not clarification:
            continue
        prompt = '你已经选好套餐；具体是哪一个套餐？' if unnamed_plan else QUESTION_PROMPTS[item['id']]
        if item['id'] == 'Q-P02' and _subscription_conflict_active(state):
            missing = _conflict_detail_gaps(state)
            detail = ('这条提示对应这次目标账号吗，当前订阅状态是什么' if len(missing) == 2
                      else '当前订阅状态是什么' if 'subscription_status' in missing
                      else '这条提示对应这次目标账号吗')
            prompt = f'先前的订阅自述与相关页面/订单提示不一致：{detail}？只补这处不一致；不确定或暂不回答也可以。'
        elif item['id'] == 'Q-P02' and _upgrade_only_task(state):
            missing = _upgrade_order_gaps(state)
            detail = '当前套餐和原购买渠道' if len(missing) == 2 else '当前套餐' if 'current_plan' in missing else '原购买渠道'
            prompt = f'升级所需的{detail}是什么？只说已知情况；不确定或暂不回答也可以，无需打开 Claude。'
        if item['id'] in DEVICE_CLEANUP_VALUES:
            prompt = prompt.format(target_alias=state['target_alias'])
        if (item['id'] in EXPOSURE_PROMPTS and state['context']['incident'] == 'credential_exposure'
                and not state['context']['incident_resolved']):
            prompt = EXPOSURE_PROMPTS[item['id']]
        return {**item, "prompt": prompt, "clarification": clarification,
                "allowed_outcomes": ["reported", "unknown", "declined", "deferred"],
                "requires_action_authorization": False}
    return None


def mark_asked(state, question_id):
    validate_state(state)
    qid = canonical(question_id)
    result = deepcopy(state)
    if qid not in {i["id"] for i in applicable_questions(state)}:
        raise InterviewError("Question is not applicable")
    if qid not in result["asked_question_ids"]:
        result["asked_question_ids"].append(qid)
    fact = result["facts"].get(qid)
    if fact and (fact["state"] in {"conflict", "stale"} or
                 (qid == 'Q-C08' and _plan_identity_missing(fact)) or
                 (qid == 'Q-P02' and _old_order_needs_clarification(state)) or
                 (qid == "Q-C03" and _legacy_incident_review(state))):
        fact["clarification_count"] = 1
    validate_state(result)
    return result


def defer_branch(state, branch):
    result = deepcopy(validate_state(state))
    if branch not in result["deferred_branches"]:
        result["deferred_branches"].append(branch)
    validate_state(result)
    return result


def resume_branch(state, branch):
    result = deepcopy(validate_state(state))
    if branch in result["deferred_branches"]:
        result["deferred_branches"].remove(branch)
    return result


# Owner materials an answer must attach (ADR-011, ADR-019). Paths are relative to
# the skill root and mirror the SKILL.md attachment table; S02 always leads payments.
REFERENCE_PATHS = {
    'S02': 'sources/S02-ai-payments.md', 'S03': 'sources/S03-claude-experience.pdf',
    'S04': 'sources/S04-claude-guide.md', 'S05': 'sources/S05-local-protection.md',
    'S06': 'sources/S06-macos-cleanup-sanitized.md', 'S07': 'sources/S07-vps-script-catalog.md',
    'S08': 'sources/S08-vps-claude-tutorial.pdf', 'R01': 'sources/vps-recommendations/INDEX.md',
    'R02': 'sources/R02-vps-line-optimization.md',
    'onboarding': 'references/account-onboarding.md', 'mobile': 'references/mobile-guidance.md',
    'egress': 'references/egress-ip-options.md', 'vm': 'references/vm-guidance.md',
    'vps': 'references/vps-guidance.md', 'line': 'references/line-optimization.md',
    'vm_firewall': 'assets/vm-killswitch/install-flclash-killswitch.sh',
    'advanced': 'references/advanced-route.md',
    'adv_tunnel': 'assets/remote-hardening/install-reverse-tunnel.sh',
    'adv_heal': 'assets/remote-hardening/flclash-crash-heal.sh',
    'vps_firewall': 'assets/vps-firewall/vps-guard.sh',
    'vm_ssh': 'assets/vm-killswitch/enable-guest-ssh.sh',
    'vm_tun': 'assets/vm-killswitch/install-flclash-tun.sh',
    'win_ipv6': 'references/agent-remediation.md',
    'win_network_tx': 'references/windows-network-transaction.md',
    'local_fw': 'references/local-firewall-prompts.md',
    'mac_dns': 'references/macos-dns-case-lessons.md',
    'auth': 'references/authorization-tiers.md',
    'whole_ipv4': 'references/whole-machine-ipv4.md',
    'incidents': 'references/incidents-and-integrations.md',
    'identity_review': 'references/accounts-and-payments.md',
    'cleanup_cli': 'references/cleanup-cli-usage.md',
    'win_cleanup': 'references/windows-cleanup.md',
    'routes': 'references/routes-and-platforms.md',
    'network': 'references/network-and-remedies.md',
    'trace': 'references/trace-cleanup.md',
    'linux_cleanup': 'references/linux-cleanup.md',
    'illegal_tools': 'references/illegal-tools-cleanup.md',
    'remote': 'references/local-advanced-route.md',
}
PAYMENT_REFERENCE_TASKS = {"subscription_preparation", "renew", "upgrade", "change_channel", "billing_issue", "compare"}
REFERENCE_TOPICS = ('payment', 'registration', 'suspension', 'identity_review', 'cleanup',
                    'trace_cleanup', 'ip_quality', 'local_protection', 'whole_machine_egress',
                    'line_optimization', 'vps', 'vm', 'mobile', 'egress', 'remote_assistance', 'illegal_tools')


def references_for_topics(topics, *, os_name='unknown'):
    """Route normalized conversation topics without interview state or execution."""
    if (not isinstance(topics, list) or any(not isinstance(t, str) or t not in REFERENCE_TOPICS for t in topics)
            or os_name not in ('unknown', 'macos', 'windows', 'linux', 'mobile_only')):
        raise InterviewError('Invalid reference topics or platform')
    out = []
    routes = {
        'payment': ('S02',), 'registration': ('onboarding', 'S03', 'S04'),
        'suspension': ('onboarding', 'S03', 'S04', 'incidents'),
        'identity_review': ('onboarding', 'S03', 'S04', 'incidents', 'identity_review'),
        'trace_cleanup': ('trace',), 'ip_quality': ('S07',),
        'local_protection': ('S05', 'local_fw'), 'whole_machine_egress': ('whole_ipv4', 'win_ipv6'),
        'line_optimization': ('line', 'R02'), 'vps': ('vps', 'S08', 'R01', 'S07'),
        'vm': ('vm', 'egress'), 'mobile': ('mobile', 'S03'), 'egress': ('egress', 'R01'),
        'remote_assistance': ('remote',), 'illegal_tools': ('illegal_tools',),
    }
    ordered = (['payment'] if 'payment' in topics else []) + [t for t in topics if t != 'payment']
    for topic in ordered:
        keys = list(routes.get(topic, ()))
        if os_name == 'windows' and topic in {'local_protection', 'whole_machine_egress', 'egress'}:
            keys.append('win_network_tx')
        if topic in {'cleanup', 'trace_cleanup'}:
            if os_name in {'macos', 'unknown'}:
                keys += ['S06', 'cleanup_cli']
            if os_name in {'windows', 'unknown'}:
                keys += ['win_cleanup']
            if os_name in {'linux', 'unknown'}:
                keys += ['linux_cleanup']
        for key in keys:
            item = {'path': REFERENCE_PATHS[key], 'topic': topic}
            if topic == 'mobile' and key == 'S03':
                item['locator'] = 'p.4'
            if topic in {'suspension', 'identity_review'}:
                if key == 'onboarding':
                    item['locator'] = '#a0b'
                elif key == 'S03':
                    item['locator'] = 'p.5'
                elif key == 'identity_review':
                    item['locator'] = '#a3-真实身份核验异常会话与凭据保护'
            _merge_reference(out, item)
    return out


def _merge_reference(out, item):
    if item['path'] in {REFERENCE_PATHS['S07'], REFERENCE_PATHS['trace']}:
        item.update(type='checklist', execution_report_required=True)
    existing = next((r for r in out if r['path'] == item['path']), None)
    if existing is None:
        out.append(item)
    elif item.get('locator') and item['locator'] not in existing.get('locator', '').split(', '):
        existing['locator'] = ', '.join(filter(None, (existing.get('locator'), item['locator'])))


def required_references(state):
    """Ordered owner materials the answer must attach for the current facts.

    A planning aid for the host, never an action authorization or evidence that
    any listed step was performed.
    """
    validate_state(state)
    c = state['context']
    out = []

    def add(key, topic, locator=None):
        item = {'path': REFERENCE_PATHS[key], 'topic': topic}
        if locator:
            item['locator'] = locator
        _merge_reference(out, item)

    os_value = _value(state, 'Q-C02')
    mobile = _value(state, 'Q-M01')
    if c['task'] in PAYMENT_REFERENCE_TASKS or c['billing_channel'] != 'unselected':
        add('S02', 'payment')
    if c['task'] != 'cleanup' and (journey(state) in {'first_subscription', 'returning_subscription'}
                                   or _value(state, 'Q-C04') == 'unregistered'):
        for key in ('onboarding', 'S03', 'S04'):
            add(key, 'registration')
    if (mobile in {'ios', 'android', 'both'} or c['billing_channel'] in {'apple', 'google'}
            or os_value == 'mobile_only'):
        add('mobile', 'mobile')
        add('S03', 'mobile', 'p.4')
    confirmed = c['route_selection_basis'] != 'default_proposal'
    route = c['route'] if confirmed else None
    egress = _value(state, 'Q-X01')
    residential = _value(state, 'Q-X02') == 'with_residential_exit'
    if route in {'local', 'vm', 'vps'}:
        add('auth', 'authorization')
        add('routes', 'route', {'local': '#r-local-独立操作卡', 'vm': '#r-vm-独立操作卡m08',
                                'vps': '#r-vps-独立操作卡m09'}[route])
    if c['task'] in {'network', 'environment'}:
        add('network', 'network_diagnosis')
        if os_value == 'windows':
            add('win_network_tx', 'network_recovery')
    if route == 'local':
        add('egress', 'egress')
        add('whole_ipv4', 'whole_machine_egress')
        if os_value == 'windows':
            add('local_fw', 'local_firewall', '#windows')
            add('S05', 'local_protection')
            add('win_ipv6', 'windows_ipv6', '#windows-adapter-ipv6-hint')
            add('win_network_tx', 'network_recovery')
        elif os_value == 'macos':
            add('local_fw', 'local_firewall', '#mac')
            add('mac_dns', 'mac_dns')
    elif route == 'vm':
        add('vm', 'vm')
        add('egress', 'egress')
        if _value(state, 'Q-V07') != 'macos':
            add('vm_ssh', 'vm')
            add('vm_tun', 'vm')
            if _value(state, 'Q-V09') == 'remote_unreachable':
                add('advanced', 'advanced_route')
                add('adv_tunnel', 'advanced_route')
                add('adv_heal', 'advanced_route')
            add('vm_firewall', 'vm')
    elif route == 'vps':
        add('vps', 'vps')
        add('S08', 'vps')
        add('R01', 'vps')
        add('S07', 'vps')
        exit_kind = _value(state, 'Q-S08')
        if exit_kind == 'vps_own_ip':
            add('vps_firewall', 'vps')
        elif exit_kind == 'residential_chain':
            add('R02', 'vps')
            add('line', 'vps')
            add('vm_firewall', 'vps')
    if route in {'local', 'vm'} and egress == 'self_built':
        add('R01', 'egress')
        add('S07', 'egress')
        if residential:
            add('R02', 'egress')
            add('line', 'egress')
    line_issue = _value(state, 'Q-T01')
    if line_issue not in (None, 'none'):
        add('line', 'line_optimization')
        add('R02', 'line_optimization')
        if line_issue in {'evening_slow', 'drops'}:
            add('R01', 'line_optimization')
    restriction = _value(state, 'Q-D01') in {'current_restriction_on_target', 'past_restriction_on_target'}
    if c['incident'] in {'suspension', 'identity_review'} or restriction:
        # Short-term ban timeline (S03 p.5) and identity-verification triage.
        add('onboarding', 'ban_timeline', '#a0b')
        add('S03', 'ban_timeline', 'p.5')
        add('S04', 'ban_timeline')
        add('incidents', 'incident_triage')
        if c['incident'] == 'identity_review':
            add('identity_review', 'identity_verification', '#a3-真实身份核验异常会话与凭据保护')
    if c['task'] == 'cleanup':
        if os_value in {'macos', None, 'unknown'}:
            add('S06', 'cleanup')
            add('cleanup_cli', 'cleanup')
        if os_value in {'windows', None, 'unknown'}:
            add('win_cleanup', 'cleanup')
    if state.get('reference_topics'):
        platform = os_value if os_value in ('macos', 'windows', 'linux', 'mobile_only') else 'unknown'
        for item in references_for_topics(state['reference_topics'], os_name=platform):
            _merge_reference(out, item)
    if any(item['path'] == REFERENCE_PATHS['S02'] for item in out):
        out.sort(key=lambda item: item['path'] != REFERENCE_PATHS['S02'])
    return out


def assessment(state):
    """Separate coverage, planning readiness and action authorization explicitly."""
    validate_state(state)
    required = applicable_questions(state)
    unresolved = []
    for item in required:
        fact = state["facts"].get(item["id"], {})
        reason = None
        if item["branch"] in state["deferred_branches"]:
            reason = "branch_deferred"
        elif item["id"] == "Q-C03" and _legacy_incident_review(state):
            reason = "legacy_incident_unverified"
        elif item["postcontact"] and state["context"]["contact_phase"] == "PC0":
            reason = "requires_contact_gate"
        elif item['id'] == 'Q-C08' and _plan_identity_missing(fact):
            reason = 'target_plan_identity_missing'
        elif item['id'] == 'Q-P02' and _subscription_conflict_active(state) and _conflict_detail_gaps(state):
            reason = 'subscription_detail_incomplete'
        elif item['id'] == 'Q-P02' and _old_order_needs_clarification(state):
            reason = 'old_order_incomplete'
        elif item['id'] == 'Q-P02' and _upgrade_only_task(state) and not _subscription_conflict_active(state) and _upgrade_order_gaps(state):
            reason = 'current_plan_or_channel_missing'
        elif item['id'] == 'Q-C13' and (fact.get('state') not in {'reported', 'observed'}
                                          or _plan_identity_missing(fact)):
            reason = 'current_plan_missing' if fact.get('state') in RESOLVED else fact.get('state', 'unasked')
        elif fact.get("state", "unasked") not in RESOLVED:
            reason = fact.get("state", "unasked")
        if reason:
            unresolved.append({"id": item["id"], "reason": reason})
    c = state["context"]
    if c["route_selection_basis"] == "default_proposal" and not _focused_subscription_task(state) and not (_cleanup_mode(state) and _value(state, "Q-D02") == "no_cleanup") and not any(x["id"] == "Q-C05" for x in unresolved):
        unresolved.append({"id": "Q-C05", "reason": "route_unconfirmed"})
    if not _cleanup_mode(state) and journey(state) == "unknown" and not any(x["id"] in {"Q-J01", "Q-J02"} for x in unresolved):
        unresolved.append({"id": "Q-J01", "reason": "journey_unknown"})
    urgent = _urgent_incident(state)
    outcome = "complete" if not unresolved else "partial"
    if urgent:
        outcome = "emergency_deferred"
    if c["paused"]:
        outcome = "paused"
    if c["blocked_reason"]:
        outcome = "blocked"
    review = state.get("resume_review")
    review_blocks = review is not None and review["status"] in {"pending", "unresolved"}
    result = {"traffic_policy": policy_projection(),
            "stage": next((i["stage"] for i in required if any(u["id"] == i["id"] for u in unresolved)), "I6"),
            "G1": {"status": outcome, "unresolved_fields": unresolved},
            "G2": {"status": "pass" if outcome == "complete" and not review_blocks else "blocked",
                   "conditional_plan_only": outcome != "complete" or review_blocks},
            "G3": {"status": "blocked", "reason": "Interview answers are not specific action authorization; action and contact gates must be checked separately"},
            "active_branches": list(dict.fromkeys(i["branch"] for i in required)),
            "deferred_branches": list(state["deferred_branches"]),
            "route_confirmation": "unconfirmed" if c["route_selection_basis"] == "default_proposal" else "confirmed",
            "current_subscription": deepcopy(state["current_subscription"])}
    if state['context']['subscription_conflict']:
        episode = state.get('subscription_review')
        result['subscription_review'] = {
            'status': 'unresolved', 'episode_id': episode['episode_id'] if episode else None,
            'blocks_current_task': _subscription_conflict_active(state)}
        if _subscription_conflict_active(state):
            result['G2'].update(status='blocked', conditional_plan_only=True,
                                reason='subscription_conflict_unresolved')
    if _upgrade_only_task(state):
        result['upgrade_scope'] = {'current_order_gaps': _upgrade_order_gaps(state),
                                   'billing_feasibility': 'not_established'}
    if any(item['id'] == 'Q-C13' for item in required):
        result['current_plan_dependency'] = {
            'question_id': 'Q-C13', 'fact_state': state['facts'].get('Q-C13', {}).get('state', 'unasked'),
            'compatibility': 'not_established', 'unrelated_planning_available': True}
    cleanup = cleanup_assessment(state)
    if cleanup is not None:
        result['cleanup'] = cleanup
        if cleanup['next_step'] == 'incident_triage':
            result['G2'].update(status='blocked', conditional_plan_only=True, reason='device_cleanup_incident_triage_required')
    if urgent:
        # Projection only: distinguish emergency postponement from explicit user
        # deferral. Never resolve the real incident or change retained facts.
        routine = deepcopy(state)
        routine['context'].update(incident_resolved=True, account_incident_resolved=True)
        pending = {item['id'] for item in assessment(routine)['G1']['unresolved_fields']}
        result['emergency_deferred_branches'] = list(dict.fromkeys(
            item['branch'] for item in applicable_questions(routine)
            if item['branch'] != 'incident' and item['id'] in pending))
    references = required_references(state)
    if references:
        result['required_references'] = references
    if state.get('authorization'):
        result['authorization'] = authorization_summary(state)
    if 'capabilities' in state:
        result['capabilities'] = {k: v for k, v in state['capabilities'].items() if k not in {'source', 'target_ref'}}
    if 'work_items' in state:
        pending = [item for item in state['work_items'] if item['status'] == 'pending']
        pending.sort(key=lambda item: not item['blocking_next_session'])
        result['follow_up'] = {
            'blocking_next_session': any(item['blocking_next_session'] for item in pending),
            'items': [{k: item[k] for k in ('id', 'kind', 'status', 'blocking_next_session')} for item in pending]}
    if review is not None:
        result["resume_review"] = {key: deepcopy(review[key]) for key in
                                   ("event_id", "status", "response", "scope_keys", "changed_keys", "reported_at")}
        if review_blocks:
            result["G2"]["reason"] = ("resume_target_rebind_required" if review["response"] == "target_changed"
                                      else "resume_review_required" if review["status"] == "pending"
                                      else "resume_review_unresolved")
    return result


def record_capabilities(state, capabilities):
    """Retain target observations, never infer them from the controller platform."""
    result = deepcopy(state)
    result['capabilities'] = deepcopy(capabilities)
    validate_state(result)
    return result


def record_work_item(state, item):
    """Upsert a private handoff or acceptance obligation; unfinished acceptance persists."""
    validate_state(state)
    if not isinstance(item, dict):
        raise InterviewError('Invalid work item')
    item = deepcopy(item)
    item['blocking_next_session'] = item.get('kind') == 'acceptance' and item.get('status') == 'pending'
    result = deepcopy(state)
    items = result.setdefault('work_items', [])
    items[:] = [old for old in items if old['id'] != item.get('id')]
    items.append(item)
    validate_state(result)
    return result


def _validate_workflow_records(state):
    if 'reference_topics' in state:
        references_for_topics(state['reference_topics'])
    if 'capabilities' in state:
        c = state['capabilities']
        if (not isinstance(c, dict) or set(c) != {'target_ref', 'platform', 'python', 'network_check', 'egress_verifier', 'source'}
                or c['target_ref'] != state['target_alias']
                or c['platform'] not in ('macos', 'windows', 'linux', 'unknown')
                or any(c[k] not in ('available', 'missing', 'unknown') for k in ('python', 'network_check', 'egress_verifier'))
                or not isinstance(c['source'], str) or not c['source'].strip()):
            raise InterviewError('Invalid target capability observations')
    if 'work_items' not in state:
        return
    items = state['work_items']
    if not isinstance(items, list):
        raise InterviewError('Invalid work items')
    seen = set()
    fields = {'id', 'target_ref', 'kind', 'status', 'scope', 'impact', 'prerequisites',
              'return_evidence', 'reason', 'blocking_next_session'}
    for item in items:
        if (not isinstance(item, dict) or set(item) != fields
                or not isinstance(item['id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', item['id'])
                or item['id'] in seen or item['target_ref'] != state['target_alias']
                or item['kind'] not in ('manual_action', 'acceptance') or item['status'] not in ('pending', 'completed')
                or any(not isinstance(item[k], str) or not item[k].strip() for k in ('scope', 'impact', 'reason'))
                or type(item['blocking_next_session']) is not bool
                or item['blocking_next_session'] != (item['kind'] == 'acceptance' and item['status'] == 'pending')
                or not isinstance(item['prerequisites'], list)
                or not isinstance(item['return_evidence'], list) or not item['return_evidence']
                or any(not isinstance(e, str) or not e.strip() for e in item['return_evidence'])):
            raise InterviewError('Invalid target work item')
        seen.add(item['id'])
        for prerequisite in item['prerequisites']:
            if (not isinstance(prerequisite, dict) or set(prerequisite) != {'check', 'status'}
                    or not isinstance(prerequisite['check'], str) or not prerequisite['check'].strip()
                    or prerequisite['status'] not in ('pass', 'not_run', 'blocked')
                    or item['status'] == 'completed' and prerequisite['status'] != 'pass'):
                raise InterviewError('Unfinished or invalid prerequisite')



# --- Tiered authorization records (ADR-025/ADR-026) -------------------------------------------
# Traceability only: these records are written from explicit user replies supplied by the
# host. They never execute anything, and answering interview questions never creates them.
ACTION_TIERS = {
    # A: inside a confirmed scope, no further question
    'readonly_diagnosis': 'A', 'research': 'A', 'plan_drafting': 'A', 'dry_run': 'A', 'detection_page': 'A',
    # B: approved once as part of a plan; the Agent can undo it and it cannot cut its own access
    'backup_export': 'B', 'rollback_fuse': 'B', 'allow_rules': 'B', 'install_client': 'B', 'install_tun': 'B',
    'guest_ssh': 'B', 'ssh_forward': 'B', 'novnc_local': 'B', 'realm_relay': 'B', 'bbr_temporary': 'B',
    'fault_drill_local': 'B',
    # C: the user must confirm at that moment
    'default_outbound_block': 'C', 'killswitch_enable': 'C', 'inbound_firewall_enable': 'C',
    'ssh_config_change': 'C', 'bbr_persist': 'C', 'nic_ipv6_disable': 'C', 'fault_drill_remote': 'C',
    'data_cleanup': 'C', 'org_device_policy': 'C',
    'account_action': 'C', 'payment': 'C', 'credential_handling': 'C', 'claude_contact': 'C',
}
# Done by the user personally; a confirmation never lets the Agent perform them.
USER_ONLY_ACTIONS = frozenset({'account_action', 'payment', 'credential_handling', 'claude_contact'})
AUTH_SAFEGUARDS = frozenset({'independent_access', 'second_session', 'snapshot'})
AUTH_PRESERVED = frozenset({'projects', 'history', 'other_apps', 'lan_devices', 'vpn', 'codex_channel'})
AUTH_ROLLBACK = frozenset({'automatic_fuse', 'manual_documented', 'none'})
AUTH_PLAN_STATUS = frozenset({'approved', 'completed', 'rolled_back', 'failed', 'stale'})
AUTH_DECISIONS = frozenset({'confirmed', 'cancelled', 'modified'})
AUTH_CONFIRMATION_STATUS = frozenset({'pending', 'confirmed', 'cancelled', 'modified', 'used', 'stale'})
AUTH_LIMIT = 100


def authorization_action_tier(action):
    """Tier of a known action; anything unknown is C (when unsure, use the higher tier)."""
    return ACTION_TIERS.get(action, 'C') if isinstance(action, str) else 'C'


def _auth_user_source(source):
    if type(source) is not str or not re.fullmatch(r'user:[A-Za-z0-9_.:-]{1,120}', source):
        raise InterviewError("Authorization must come from the user's explicit reply (source user:...)")
    return source


def _auth_label(value, what):
    if type(value) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', value):
        raise InterviewError('Use a short non-identifying ' + what)
    return value


def _auth_actions(values, *, tiers):
    if isinstance(values, (str, bytes)) or not isinstance(values, (list, tuple, set, frozenset)) or not values:
        raise InterviewError('Actions must be a nonempty list')
    out = []
    for action in values:
        if type(action) is not str or action not in ACTION_TIERS:
            raise InterviewError('Unknown action; unknown actions are tier C and need a confirmation')
        if ACTION_TIERS[action] not in tiers:
            raise InterviewError('Action tier not allowed here: ' + action)
        if action not in out:
            out.append(action)
    if len(out) > 40:
        raise InterviewError('Too many actions')
    return sorted(out)


def _auth_binding(state):
    ctx = state['context']
    return {'target_alias': state['target_alias'], 'account_alias': state['account_alias'],
            'task_id': state['task_id'], 'route': ctx['route']}


def _auth_record(state):
    return state.setdefault('authorization', {'scopes': [], 'plans': [], 'confirmations': []})


def _auth_active_scope(state):
    """The active scope whose binding still matches the current state, else None."""
    record = state.get('authorization')
    if not record:
        return None
    for scope in reversed(record['scopes']):
        if scope['status'] == 'active':
            return scope if scope['binding'] == _auth_binding(state) and \
                state['context']['route_selection_basis'] != 'default_proposal' else None
    return None


def _stale_authorization(state, reason):
    record = state.get('authorization')
    if not record:
        return
    for scope in record['scopes']:
        if scope['status'] == 'active':
            scope['status'] = 'stale'
            scope['stale_reason'] = reason
    for plan in record['plans']:
        if plan['status'] == 'approved':
            plan['status'] = 'stale'
    for item in record['confirmations']:
        if item['status'] in {'pending', 'confirmed'}:
            item['status'] = 'stale'


def _validate_authorization(state):
    record = state['authorization']
    if (not isinstance(record, dict) or set(record) != {'scopes', 'plans', 'confirmations'}
            or any(not isinstance(record[k], list) or len(record[k]) > AUTH_LIMIT for k in record)):
        raise InterviewError('Invalid authorization record')
    scope_ids = set()
    active = 0
    for scope in record['scopes']:
        keys = {'scope_id', 'status', 'binding', 'allowed_actions', 'safeguards', 'preserved', 'source',
                'observed_at', 'stale_reason'}
        if (not isinstance(scope, dict) or set(scope) - keys or keys - {'stale_reason'} - set(scope)
                or scope['status'] not in {'active', 'stale', 'revoked'}
                or not isinstance(scope['binding'], dict)
                or set(scope['binding']) != {'target_alias', 'account_alias', 'task_id', 'route'}
                or not isinstance(scope['allowed_actions'], list)
                or any(a not in ACTION_TIERS or ACTION_TIERS[a] == 'C' for a in scope['allowed_actions'])
                or not isinstance(scope['safeguards'], list) or set(scope['safeguards']) - AUTH_SAFEGUARDS
                or not isinstance(scope['preserved'], list) or set(scope['preserved']) - AUTH_PRESERVED):
            raise InterviewError('Invalid authorization scope')
        _auth_label(scope['scope_id'], 'scope id')
        _auth_user_source(scope['source'])
        _validate_date(scope['observed_at'])
        if scope['scope_id'] in scope_ids:
            raise InterviewError('Duplicate scope id')
        scope_ids.add(scope['scope_id'])
        active += scope['status'] == 'active'
    if active > 1:
        raise InterviewError('Only one active scope')
    plan_ids = set()
    for plan in record['plans']:
        keys = {'plan_id', 'scope_id', 'steps', 'status', 'approved_source', 'approved_at',
                'result_source', 'result_at'}
        if (not isinstance(plan, dict) or set(plan) != keys or plan['status'] not in AUTH_PLAN_STATUS
                or plan['scope_id'] not in scope_ids or not isinstance(plan['steps'], list) or not plan['steps']
                or any(a not in ACTION_TIERS or ACTION_TIERS[a] != 'B' for a in plan['steps'])):
            raise InterviewError('Invalid plan approval')
        _auth_label(plan['plan_id'], 'plan id')
        _auth_user_source(plan['approved_source'])
        _validate_date(plan['approved_at'])
        if plan['plan_id'] in plan_ids:
            raise InterviewError('Duplicate plan id')
        plan_ids.add(plan['plan_id'])
    conf_ids = set()
    for item in record['confirmations']:
        keys = {'confirmation_id', 'scope_id', 'action', 'reason', 'rollback', 'status', 'requested_at',
                'resolved_source', 'resolved_at'}
        if (not isinstance(item, dict) or set(item) != keys or item['status'] not in AUTH_CONFIRMATION_STATUS
                or item['scope_id'] not in scope_ids or item['action'] not in ACTION_TIERS
                or ACTION_TIERS[item['action']] != 'C' or item['rollback'] not in AUTH_ROLLBACK
                or not isinstance(item['reason'], str) or not 1 <= len(item['reason']) <= 200):
            raise InterviewError('Invalid critical confirmation')
        _auth_label(item['confirmation_id'], 'confirmation id')
        _validate_date(item['requested_at'])
        if item['resolved_source'] is not None:
            _auth_user_source(item['resolved_source'])
        if item['confirmation_id'] in conf_ids:
            raise InterviewError('Duplicate confirmation id')
        conf_ids.add(item['confirmation_id'])


def record_scope_confirmation(state, *, source, allowed_actions, safeguards=(), preserved=(), observed_at=None):
    """Record the user's explicit scope confirmation (tier A and B only; never C).

    Requires an explicitly chosen route. The scope is bound to this target, account,
    task and route; a different binding, a resume or a route change retires it.
    """
    validate_state(state)
    _auth_user_source(source)
    _validate_date(observed_at)
    if state['context']['route_selection_basis'] == 'default_proposal' or state['context']['route'] == 'compare':
        raise InterviewError('Confirm a route before confirming a scope')
    actions = _auth_actions(allowed_actions, tiers={'A', 'B'})
    for name, values, allowed in (('safeguards', safeguards, AUTH_SAFEGUARDS), ('preserved', preserved, AUTH_PRESERVED)):
        if isinstance(values, str) or set(values) - allowed:
            raise InterviewError('Unknown ' + name + ' value')
    result = deepcopy(state)
    record = _auth_record(result)
    if len(record['scopes']) >= AUTH_LIMIT:
        raise InterviewError('Authorization history is full')
    for old in record['scopes']:
        if old['status'] == 'active':
            old['status'] = 'revoked'
    _stale_authorization(result, 'scope_replaced')
    record['scopes'].append({
        'scope_id': 'scope-%d' % (len(record['scopes']) + 1), 'status': 'active', 'binding': _auth_binding(result),
        'allowed_actions': actions, 'safeguards': sorted(set(safeguards)), 'preserved': sorted(set(preserved)),
        'source': source, 'observed_at': observed_at if observed_at is not None else _now()})
    return validate_state(result)


def record_plan_approval(state, *, plan_id, steps, source, observed_at=None):
    """Record one tier-B plan the user approved as a whole; all steps must be in the active scope."""
    validate_state(state)
    _auth_label(plan_id, 'plan id')
    _auth_user_source(source)
    _validate_date(observed_at)
    scope = _auth_active_scope(state)
    if scope is None:
        raise InterviewError('A current scope confirmation is required first')
    actions = _auth_actions(steps, tiers={'B'})
    if set(actions) - set(scope['allowed_actions']):
        raise InterviewError('Plan steps must be inside the confirmed scope')
    result = deepcopy(state)
    record = _auth_record(result)
    if any(plan['plan_id'] == plan_id for plan in record['plans']):
        raise InterviewError('Plan id already used')
    if len(record['plans']) >= AUTH_LIMIT:
        raise InterviewError('Authorization history is full')
    record['plans'].append({'plan_id': plan_id, 'scope_id': scope['scope_id'], 'steps': actions,
                            'status': 'approved', 'approved_source': source,
                            'approved_at': observed_at if observed_at is not None else _now(),
                            'result_source': None, 'result_at': None})
    return validate_state(result)


def record_plan_result(state, plan_id, *, status, source, observed_at=None):
    """Record how an approved plan ended (completed, rolled_back or failed); retried identically is idempotent."""
    validate_state(state)
    if status not in {'completed', 'rolled_back', 'failed'}:
        raise InterviewError('Invalid plan result')
    if type(source) is not str or not re.fullmatch(r'(user|agent|host):[A-Za-z0-9_.:-]{1,120}', source):
        raise InterviewError('Result source needs a user, agent or host label')
    _validate_date(observed_at)
    result = deepcopy(state)
    record = _auth_record(result)
    plan = next((item for item in record['plans'] if item['plan_id'] == plan_id), None)
    if plan is None:
        raise InterviewError('Unknown plan')
    if plan['status'] == status:
        return validate_state(result)
    if plan['status'] != 'approved':
        raise InterviewError('Only an approved plan can receive a result')
    plan.update(status=status, result_source=source, result_at=observed_at if observed_at is not None else _now())
    return validate_state(result)


def request_critical_confirmation(state, *, action, reason, rollback, requested_at=None):
    """Open a tier-C confirmation the user must answer at that moment (the Agent then pauses)."""
    validate_state(state)
    if type(action) is not str or action not in ACTION_TIERS or ACTION_TIERS[action] != 'C':
        raise InterviewError('Only tier C actions need a confirmation')
    if rollback not in AUTH_ROLLBACK:
        raise InterviewError('State how the action is undone')
    _safe(reason)
    if type(reason) is not str or not 1 <= len(reason) <= 200:
        raise InterviewError('Give a short reason')
    _validate_date(requested_at)
    scope = _auth_active_scope(state)
    if scope is None:
        raise InterviewError('A current scope confirmation is required first')
    result = deepcopy(state)
    record = _auth_record(result)
    if len(record['confirmations']) >= AUTH_LIMIT:
        raise InterviewError('Authorization history is full')
    record['confirmations'].append({
        'confirmation_id': 'c-%d' % (len(record['confirmations']) + 1), 'scope_id': scope['scope_id'],
        'action': action, 'reason': reason, 'rollback': rollback, 'status': 'pending',
        'requested_at': requested_at if requested_at is not None else _now(),
        'resolved_source': None, 'resolved_at': None})
    return validate_state(result)


def resolve_critical_confirmation(state, confirmation_id, *, decision, source, observed_at=None):
    """Record the user's answer to a pending confirmation. Silence never resolves it."""
    validate_state(state)
    if decision not in AUTH_DECISIONS:
        raise InterviewError('Invalid decision')
    _auth_user_source(source)
    _validate_date(observed_at)
    result = deepcopy(state)
    record = _auth_record(result)
    item = next((c for c in record['confirmations'] if c['confirmation_id'] == confirmation_id), None)
    if item is None:
        raise InterviewError('Unknown confirmation')
    if item['status'] != 'pending':
        raise InterviewError('Only a pending confirmation can be answered')
    item.update(status=decision, resolved_source=source, resolved_at=observed_at if observed_at is not None else _now())
    return validate_state(result)


def use_critical_confirmation(state, action):
    """Consume one confirmed tier-C confirmation for this action (one-time); fails when none is usable."""
    check = authorization_check(state, action)
    if not check['allowed'] or check['tier'] != 'C':
        raise InterviewError('No usable confirmation: ' + check['reason'])
    result = deepcopy(state)
    item = next(c for c in result['authorization']['confirmations'] if c['confirmation_id'] == check['confirmation_id'])
    item['status'] = 'used'
    return validate_state(result)


def authorization_check(state, action):
    """Read-only: may the Agent perform this action now? A planning aid, never an execution grant."""
    validate_state(state)
    tier = authorization_action_tier(action)
    out = {'action': action if isinstance(action, str) else None, 'tier': tier, 'allowed': False, 'reason': None}
    if isinstance(action, str) and action in USER_ONLY_ACTIONS:
        out['reason'] = 'user_performs_this'
        return out
    scope = _auth_active_scope(state)
    if scope is None:
        out['reason'] = 'scope_not_active'
        return out
    record = state['authorization']
    if tier == 'A':
        out.update(allowed=True, reason='inside_confirmed_scope')
    elif tier == 'B':
        plan = next((p for p in record['plans'] if p['status'] == 'approved' and p['scope_id'] == scope['scope_id']
                     and action in p['steps']), None)
        if plan is None:
            out['reason'] = 'no_approved_plan'
        else:
            out.update(allowed=True, reason='approved_plan', plan_id=plan['plan_id'])
    else:
        item = next((c for c in record['confirmations'] if c['status'] == 'confirmed'
                     and c['scope_id'] == scope['scope_id'] and c['action'] == action), None)
        if item is None:
            pending = any(c['status'] == 'pending' and c['action'] == action for c in record['confirmations'])
            out['reason'] = 'confirmation_pending' if pending else 'confirmation_required'
        else:
            out.update(allowed=True, reason='confirmed_by_user', confirmation_id=item['confirmation_id'])
    return out


def authorization_summary(state):
    """Compact traceable view for assessments; empty dict when no authorization was recorded."""
    record = state.get('authorization')
    if not record:
        return {}
    latest = record['scopes'][-1] if record['scopes'] else None
    current = _auth_active_scope(state)
    counts = {}
    for plan in record['plans']:
        counts[plan['status']] = counts.get(plan['status'], 0) + 1
    return {'scope': 'active' if current else ('stale' if latest and latest['status'] in {'active', 'stale'} else 'none'),
            'binding_valid': current is not None,
            'plans': counts,
            'pending_confirmations': [{'id': c['confirmation_id'], 'action': c['action']}
                                      for c in record['confirmations'] if c['status'] == 'pending'],
            'note': 'Records trace user replies; they are not an execution grant. G3 stays blocked here.'}


def complete_purchase(state, *, source, observed_at=None, observed=False):
    """Record a reported/observed completed purchase without executing one.

    The same explicit completion source/time/status is an idempotent evidence
    retry, not a second purchase that can invalidate later current-plan reports.
    """
    validate_state(state)
    if not isinstance(source, str) or not source or type(observed) is not bool:
        raise InterviewError('Completion requires explicit provenance and observed boolean')
    _safe(source)
    completed_at = _validate_date(observed_at)
    receipt = state.get('purchase_completion')
    if completed_at is not None and receipt is not None:
        receipt_at = _validate_date(receipt['observed_at'])
        if (receipt['source'] == source and receipt_at == completed_at and receipt['observed'] == observed):
            return deepcopy(state)
        if completed_at <= receipt_at:
            raise InterviewError('Older or conflicting completion evidence cannot replace the retained receipt')
    current = state['current_subscription']
    current_at = _validate_date(current['observed_at'])
    plan = state['facts'].get('Q-C13', {})
    plan_at = _validate_date(plan.get('observed_at'))
    order = state['facts'].get('Q-P02', {})
    value = _value(state, 'Q-P02')
    _, origin = _p02_component(order, 'plan')
    order_at = _validate_date(origin.get('observed_at'))
    if (isinstance(value, dict) and _named_plan(value.get('plan'))
            and not _order_plan_stale(state)
            and _after_purchase_completion(state, origin) and order_at is not None
            and (plan_at is None or order_at > plan_at)):
        plan, plan_at = order, order_at
    if completed_at is not None and (current_at is not None and completed_at < current_at
            or current['status'] in {'active_reported', 'observed_active'}
            and plan.get('state') in {'reported', 'observed'} and plan_at is not None and completed_at < plan_at):
        # Historical completion evidence cannot overwrite newer account or plan
        # evidence, reset a later task, or remove its dependency. It can only
        # stale an older retained plan whose effective state is unclear.
        result = deepcopy(state)
        if plan_at is not None and plan_at <= completed_at:
            _stale_current_plan(result, 'Historical completed purchase postdates the retained plan')
        return validate_state(result)
    result = record_fact(state, "Q-J01", "existing_subscriber", source=source,
                         state_name="observed" if observed else "reported", observed_at=observed_at)
    result['purchase_completion'] = {
        'account_alias': result['account_alias'], 'source': source,
        'observed_at': result['current_subscription']['observed_at'], 'observed': observed}
    result["facts"].pop("Q-J02", None)
    result["current_subscription"]["status"] = "observed_active" if observed else "active_reported"
    _stale_current_plan(result, 'Completed purchase requires an explicit current-plan report')
    result['context'].pop('plan_compatibility_needed', None)
    result["context"].update(purchase_completed=True, task="environment")
    result["purchase_intent"] = "completed"
    result["payment_intent"] = "none"
    review = result.get('resume_review')
    if review is not None:
        remaining = [key for key in review['retained_keys'] if key not in {'Q-J01', 'Q-J02'}]
        if review['status'] in ('reviewed', 'not_required'):
            if set(remaining) - set(review['scope_keys']):
                # Preserve the completed receipt and old off-route obligations.
                # The same live route needs no new review; another route cannot
                # inherit an unchanged report that never covered its old facts.
                review['binding'] = _resume_binding(result)
                review['retained_keys'] = remaining
            else:
                del result['resume_review']
        else:
            # Completing purchase resolves obsolete billing uncertainty, not
            # retained environmental or target-change uncertainty.
            review['binding'] = _resume_binding(result)
            review['retained_keys'] = remaining
            review['scope_keys'] = [key for key in review['scope_keys'] if key not in {'Q-J01', 'Q-J02'}]
            if not review['scope_keys'] and review['response'] != 'target_changed':
                if remaining:
                    review.update(status='not_required', response=None, changed_keys=[],
                                  source=None, reported_at=None)
                else:
                    del result['resume_review']
    validate_state(result)
    return result


def dumps_state(state, *, host_opt_in=False, scope="private_save"):
    """Return validated private JSON only with explicit host permission for scope.

    This function does not write files. An answer to Q-Z05 alone never authorizes
    storage; host_opt_in must represent separately obtained specific permission.
    Pattern screening cannot guarantee removal of all identifying/secret data.
    Public publication requires a separate manually reviewed artifact, not this state.
    """
    result = deepcopy(validate_state(state))
    _normalize_incident_context(result)
    _normalize_subscription_review(result)
    _normalize_current_order_plan(result)
    _sync_task_intent(result)
    if scope == "public_export":
        raise InterviewError("Public export requires a separately reviewed redacted artifact")
    if scope not in result["persistence_consent"] or host_opt_in is not True:
        raise InterviewError("Explicit host opt-in for persistence/export is required")
    result["persistence_consent"][scope] = True
    return json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False)


def loads_state(serialized):
    """Deserialize state; not a session-resume event and never action permission.

    Hosts call resume_interview separately after an actual interruption.
    """
    if not isinstance(serialized, str) or len(serialized) > 250000:
        raise InterviewError("Invalid or oversized saved interview")
    def unique_pairs(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise InterviewError("Duplicate JSON keys")
            obj[key] = value
        return obj
    try:
        result = json.loads(serialized, object_pairs_hook=unique_pairs,
                            parse_constant=lambda value: (_ for _ in ()).throw(InterviewError("Non-finite JSON number")))
    except (ValueError, TypeError, RecursionError) as exc:
        raise InterviewError("Invalid saved interview: " + str(exc)) from None
    validate_state(result)
    _normalize_incident_context(result)
    _normalize_subscription_review(result)
    _normalize_current_order_plan(result)
    _sync_task_intent(result)
    # Saved permission is historical evidence, not new permission to save/export.
    result["persistence_consent"] = {key: False for key in result["persistence_consent"]}
    return result


# Resume review is a planning obligation, never an operation/identity permission.
# An explicit event boundary is separate from ordinary JSON deserialization.
RESUME_FIELD_KEYS = frozenset(
    {'Q-D01', 'Q-D02', 'Q-C02', 'Q-C04', 'Q-C06', 'Q-C09', 'Q-C13', 'Q-P02', 'Q-Z04', 'Q-J01', 'Q-J02'} |
    {f'Q-OS{i:02d}' for i in range(2, 13)} |
    {f'Q-N{i:02d}' for i in range(1, 7)} |
    {f'Q-L{i:02d}' for i in range(1, 5)} |
    {f'Q-V{i:02d}' for i in range(1, 7)} |
    {f'Q-S{i:02d}' for i in range(1, 8)})
RESUME_RESPONSES = frozenset({'unchanged', 'changed', 'unknown', 'declined', 'deferred', 'target_changed'})


def _resume_binding(state):
    return {**{key: state[key] for key in ('task_id', 'target_alias', 'account_alias')},
            **{key: state['context'][key] for key in ('task', 'route', 'route_selection_basis')}}


def _validate_resume_review(state):
    review = state.get('resume_review')
    if review is None and 'resume_review' not in state:
        return
    required = {'event_id', 'binding', 'scope_keys', 'retained_keys', 'status', 'response',
                'changed_keys', 'source', 'reported_at'}
    if not isinstance(review, dict) or set(review) != required:
        raise InterviewError('Invalid resume review')
    if not isinstance(review['event_id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', review['event_id']):
        raise InterviewError('Use a short non-identifying resume event label')
    if review['binding'] != _resume_binding(state):
        raise InterviewError('Resume review target or task mismatch')
    for name in ('scope_keys', 'retained_keys', 'changed_keys'):
        keys = review[name]
        if (not isinstance(keys, list) or any(type(key) is not str or key not in RESUME_FIELD_KEYS for key in keys)
                or len(keys) != len(set(keys))):
            raise InterviewError('Invalid resume scope keys')
    if not set(review['changed_keys']).issubset(review['scope_keys']):
        raise InterviewError('Changed facts are outside the reviewed scope')
    if review['status'] not in ('pending', 'reviewed', 'unresolved', 'not_required'):
        raise InterviewError('Invalid resume review status')
    if review['status'] in ('pending', 'not_required'):
        if review['status'] == 'not_required' and review['scope_keys']:
            raise InterviewError('Nonempty resume scope requires review')
        if any(review[key] is not None for key in ('response', 'source', 'reported_at')) or review['changed_keys']:
            raise InterviewError('Pending resume review cannot contain an answer')
    else:
        response = review['response']
        if type(response) is not str or response not in RESUME_RESPONSES:
            raise InterviewError('Invalid resume response')
        if not isinstance(review['source'], str) or not review['source'] or review['reported_at'] is None:
            raise InterviewError('Resume response requires current reported provenance')
        _validate_date(review['reported_at'])
        if (response == 'changed') != bool(review['changed_keys']):
            raise InterviewError('Changed response requires a nonempty scoped key set')
        expected = 'reviewed' if response in ('unchanged', 'changed') else 'unresolved'
        if review['status'] != expected:
            raise InterviewError('Resume response contradicts its status')


def _resume_current_order_plan(state):
    plan, _ = _p02_component(state['facts'].get('Q-P02', {}), 'plan')
    return (_named_plan(plan)
            and (journey(state) == 'existing_subscriber'
                 or state['context'].get('current_order_plan_stale', False)))


def resume_scope_keys(state):
    """Snapshot retained topics, including dormant conditionals in the chosen route.

    A later flag must not activate an old fact omitted from review. Fresh answers
    supplied after this snapshot are current reports, not another interruption.
    The prompt explicitly includes the bounded retained conditional topics.
    """
    validate_state(state)
    allowed = {key for key in RESUME_FIELD_KEYS if not key.startswith(('Q-L', 'Q-V', 'Q-S', 'Q-J'))}
    if not _resume_current_order_plan(state):
        allowed.discard('Q-P02')
    if state['context']['route_selection_basis'] != 'default_proposal':
        prefix = {'local': 'Q-L', 'vm': 'Q-V', 'vps': 'Q-S'}.get(state['context']['route'])
        if prefix:
            allowed.update(key for key in RESUME_FIELD_KEYS if key.startswith(prefix))
    if state['context']['task'] in PURCHASE_TASKS | BILLING_TASKS:
        allowed.update({'Q-J01', 'Q-J02'})
    return sorted(key for key, fact in state['facts'].items() if key in allowed
                  and (fact['state'] in {'reported', 'observed', 'inferred', 'stale', 'conflict'}
                       or key == 'Q-P02' and 'plan' in fact.get('retained_fields', {})))


def resume_interview(state, *, resume_id):
    """Start an explicit actual interruption boundary, not a load/save round trip.

    The host supplies a fresh non-identifying event label for each interruption;
    the same label is only an idempotent retry of that event. It is not a secret,
    authorization token, or native identity proof. Existing facts/contact history
    and chosen route are retained. A completed old event cannot review a new one.
    """
    result = deepcopy(validate_state(state))
    _safe(resume_id)
    if type(resume_id) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', resume_id):
        raise InterviewError('Use a short non-identifying resume event label')
    old = result.get('resume_review')
    result['context']['paused'] = False
    result['persistence_consent'] = {key: False for key in result['persistence_consent']}
    _stale_authorization(result, 'session_resumed')
    if old is not None and old['event_id'] == resume_id:
        if state['context']['paused'] and old['status'] in {'reviewed', 'not_required'}:
            raise InterviewError('A new interruption requires a new resume event label')
        return validate_state(result)
    result['resume_review'] = {
        'event_id': resume_id, 'binding': _resume_binding(result),
        'scope_keys': resume_scope_keys(result),
        'retained_keys': sorted(key for key, fact in result['facts'].items()
                                if key in RESUME_FIELD_KEYS
                                and (key != 'Q-P02' or _resume_current_order_plan(result))
                                and (fact['state'] in {'reported', 'observed', 'inferred', 'stale', 'conflict'}
                                     or key == 'Q-P02' and 'plan' in fact.get('retained_fields', {}))),
        'status': 'pending', 'response': None,
        'changed_keys': [], 'source': None, 'reported_at': None}
    if not result['resume_review']['scope_keys']:
        result['resume_review']['status'] = 'not_required'
    return validate_state(result)


def _refresh_resume_binding(state):
    """Rebind only retained relevant facts, never manufacture an interruption."""
    review = state.get('resume_review')
    if review is not None and review['binding'] != _resume_binding(state):
        del state['resume_review']
        scope = sorted(set(resume_scope_keys(state)) & set(review['retained_keys']))
        review['binding'] = _resume_binding(state)
        review['scope_keys'] = scope
        if review['response'] != 'target_changed':
            review.update(status='pending' if scope else 'not_required', response=None,
                          changed_keys=[], source=None, reported_at=None)
        state['resume_review'] = review


def record_resume_review(state, *, resume_id, response, source, changed_keys=(), reported_at=None):
    """Record one fresh user report; changed keys alone are marked stale atomically.

    Unknown/refused/deferred/target-changed answers stop automatic review prompts
    and keep personalized planning conditional. Generic guidance and incident
    triage remain available. Resolving an unresolved review is an explicit later
    reply. A repeated successful response never invalidates refreshed facts again.
    """
    result = deepcopy(validate_state(state))
    review = result.get('resume_review')
    if (review is None or review['status'] == 'not_required'
            or type(resume_id) is not str or resume_id != review['event_id']):
        raise InterviewError('No matching resume review event')
    if type(response) is not str or response not in RESUME_RESPONSES:
        raise InterviewError('Invalid resume response')
    if type(changed_keys) not in (list, tuple):
        raise InterviewError('Changed facts must be a bounded list')
    keys = list(changed_keys)
    if (any(type(key) is not str or key not in review['scope_keys'] for key in keys)
            or len(keys) != len(set(keys))):
        raise InterviewError('Changed facts are outside the reviewed scope')
    if (response == 'changed') != bool(keys):
        raise InterviewError('Changed response requires a nonempty scoped key set')
    if not isinstance(source, str) or not source:
        raise InterviewError('Resume response requires current reported provenance')
    _validate_date(reported_at)
    candidate = {**review, 'response': response, 'changed_keys': sorted(keys),
                 'status': 'reviewed' if response in ('unchanged', 'changed') else 'unresolved',
                 'source': source, 'reported_at': _now() if reported_at is None else reported_at}
    result['resume_review'] = candidate
    validate_state(result)  # Also screens provenance before the idempotent path.
    same = (review['response'] == response and review['changed_keys'] == candidate['changed_keys']
            and review['source'] == source)
    if same:
        return deepcopy(state)
    if review['status'] == 'reviewed':
        raise InterviewError('Resume event already reviewed; start a new event for a new change')
    if response == 'changed':
        result = invalidate_facts(result, keys, reason='Reported change since interview interruption')
    return validate_state(result)


def resume_review_prompt(state):
    """One scoped host prompt, separate from the stable Q registry; no action."""
    validate_state(state)
    review = state.get('resume_review')
    if state['context']['task'] == 'cleanup' and _value(state, 'Q-D02') == 'no_cleanup':
        return None
    if (review is None or review['status'] != 'pending' or state['context']['paused']
            or state['context']['blocked_reason'] or _urgent_incident(state) or _legacy_incident_review(state) or _device_triage(state)):
        return None
    route = {'local': '本机', 'vm': '虚拟机', 'vps': 'VPS', 'compare': '方案比较'}[state['context']['route']]
    if state['context']['route_selection_basis'] == 'default_proposal':
        route = '路线尚未确认（本机只是默认候选）的'
    keys = set(review['scope_keys'])
    topics = []
    if keys & ({'Q-C02'} | {f'Q-OS{i:02d}' for i in range(2, 13)}):
        topics.append('系统/版本、语言和时间设置')
    if keys & {f'Q-N{i:02d}' for i in range(1, 7)}:
        topics.append('网络/代理及此前测试')
    if keys & {f'Q-V{i:02d}' for i in range(1, 7)}:
        topics.append('虚拟机资源、网络、共享和恢复条件')
    if keys & {f'Q-S{i:02d}' for i in range(1, 8)}:
        topics.append('服务器、SSH/救援、数据、费用和使用方式')
    if keys & {f'Q-L{i:02d}' for i in range(1, 5)}:
        topics.append('客户端版本/兼容性、集成和本机依赖')
    if keys & {'Q-C04', 'Q-C06'}:
        topics.append('账号登录情况')
    if 'Q-C13' in keys:
        topics.append('已记录的当前套餐及本次功能依赖（不涉及购买或付款）')
    if 'Q-P02' in keys:
        topics.append('已记录的当前套餐和原购买渠道（不涉及实际付款）')
    if 'Q-C09' in keys:
        topics.append('使用地区/跨地区安排（无需详细地址）')
    if keys & {'Q-D01', 'Q-D02'}:
        topics.append('选定设备的限制历史和本次清理目标（不是操作授权）')
    if 'Q-Z04' in keys:
        topics.append('备份/救援条件')
    if keys & {'Q-J01', 'Q-J02'}:
        topics.append('订阅状态')
    detail = '；上次记录的' + '、'.join(topics) + '（含本路线已记录但尚未展开的条件项）有没有变化' if topics else ''
    return {'kind': 'resume_review', 'event_id': review['event_id'],
            'scope_keys': list(review['scope_keys']),
            'prompt': f'继续上次的{route}任务：还是原来的目标设备和账号吗{detail}？可以说没变、具体变化、不确定、暂不回答或稍后再说；换了目标请先说明。',
            'allowed_outcomes': ['unchanged', 'changed', 'unknown', 'declined', 'deferred', 'target_changed'],
            'requires_action_authorization': False}


# Machine-readable schema entrypoint; runtime validation adds cross-field and
# target-binding constraints not expressible in this compact schema.
STATE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:claude-guardian:interview:1.0.0", "type": "object",
    "required": list(new_state("target", "account")), "additionalProperties": False,
    "properties": {
        "schema_version": {"const": SCHEMA_VERSION},
        **{key: {"type": "string"} for key in ("task_id", "target_alias", "account_alias", "payment_intent", "purchase_intent")},
        **{key: {"type": "object"} for key in ("facts", "context", "current_subscription", "persistence_consent")},
        **{key: {"type": "array", "items": {"type": "string"}, "uniqueItems": True} for key in ("asked_question_ids", "deferred_branches")},
    },
}


def invalidate_facts(state, question_ids, *, reason):
    """Mark only relevant changed/expired facts stale; retain their provenance.

    The host chooses affected fields based on current task and evidence age.
    There is deliberately no arbitrary permanent validity or global re-interview.
    """
    result = deepcopy(validate_state(state))
    _normalize_subscription_review(result)
    if not isinstance(reason, str) or not reason:
        raise InterviewError("A refresh reason is required")
    question_ids = list(question_ids)
    for question_id in question_ids:
        qid = canonical(question_id)
        if qid in result["facts"]:
            result["facts"][qid].update(state="stale", blocker_reason=reason, clarification_count=0)
        if qid in result["asked_question_ids"]:
            result["asked_question_ids"].remove(qid)
    if 'Q-P02' in question_ids:
        _stale_old_order_followup(result)
    if 'Q-C13' in question_ids:
        _stale_current_plan(result, reason)
    if 'Q-D01' in question_ids and 'device_incident_resolved' in result['context']:
        result['context'].update(device_incident_resolved=False, device_incident_resolution_ref=None)
    if 'Q-C05' in question_ids:
        result['context'].update(route='compare', route_selection_basis='default_proposal')
        _invalidate_changed_route(result, state['context'])
        _refresh_resume_binding(result)
    if any(qid in {"Q-J01", "Q-J02"} for qid in question_ids) and journey(result) == "unknown":
        result["current_subscription"] = {"status": "unknown", "source": None, "observed_at": None}
        result["payment_intent"] = "unresolved"
        _stale_current_plan(result, "Subscription evidence became stale; current plan requires reconfirmation")
    validate_state(result)
    return result


def begin_task(state, *, task_id, task, target_alias=None, account_alias=None):
    """Start an explicitly requested new task without silently reusing its old goal.

    Same-target facts are retained. A new device keeps only explicitly account-bound
    subscription/account facts; a new account starts fresh. No data/credentials move.
    A new purchase target must be supplied afresh; previous C08 is not entitlement.
    """
    validate_state(state)
    target_alias = target_alias or state["target_alias"]
    account_alias = account_alias or state["account_alias"]
    if (target_alias, account_alias) != (state["target_alias"], state["account_alias"]):
        result = new_state(target_alias, account_alias, task_id=task_id)
        if account_alias == state["account_alias"]:
            # A different device does not imply a different subscription.
            keep = {"Q-J01", "Q-J02", "Q-C03", "Q-C04", "Q-C06", "Q-C13", "Q-P02"}
            result["facts"] = {qid: deepcopy(fact) for qid, fact in state["facts"].items()
                               if qid in keep and fact["subject_ref"] == account_alias}
            result["current_subscription"] = deepcopy(state["current_subscription"])
            original = deepcopy(state)
            _normalize_subscription_review(original)
            if 'subscription_review' in original:
                result['subscription_review'] = original['subscription_review']
                result['context']['subscription_conflict'] = state['context']['subscription_conflict']
            if 'current_order_plan_stale' in original['context']:
                result['context']['current_order_plan_stale'] = original['context']['current_order_plan_stale']
            if 'purchase_completion' in state:
                result['purchase_completion'] = deepcopy(state['purchase_completion'])
            if _legacy_incident_review(state):
                result["context"].update(incident=state["context"]["incident"],
                                         incident_origin="legacy_unverified")
            if _account_incident(state) != "none":
                # A device change does not create a new account incident or undo
                # the host's explicit resolution of the retained account facts.
                result["context"]["account_incident_resolved"] = _account_incident_resolved(state)
    else:
        result = deepcopy(state)
        _normalize_subscription_review(result)
        result.pop("resume_review", None)
        old_task = result["task_id"]
        result["task_id"] = task_id
        for fact in result["facts"].values():
            if fact["subject_ref"] == old_task:
                fact["subject_ref"] = task_id
        _clear_cleanup_goal(result)
        reset_ids = {"Q-D02", "Q-C01", "Q-C11", "Q-Z01", "Q-Z03", "Q-Z04", "Q-Z05"}
        if task in PURCHASE_TASKS:
            reset_ids |= {"Q-C08", "Q-P05", "Q-P06", "Q-P07"} | POSTCONTACT
        for qid in reset_ids:
            result["facts"].pop(qid, None)
        result["asked_question_ids"] = [q for q in result["asked_question_ids"] if q not in reset_ids]
        result["deferred_branches"] = []
        result["persistence_consent"] = {key: False for key in result["persistence_consent"]}
        result["context"].update(paused=False, blocked_reason=None, purchase_completed=False,
                                 change_planned=False, persistence_requested=False, contact_phase="PC0")
    if task in {'billing_issue', 'change_channel'}:
        result = invalidate_facts(result, ['Q-P02', 'Q-A06'], reason='New billing task requires relevant old-order review')
    review = state.get('resume_review')
    if (review is not None and review['status'] in {'pending', 'unresolved'}
            and ('Q-C13' in set(review['retained_keys']) | set(review['scope_keys'])
                 or 'Q-P02' in review['retained_keys'])):
        _stale_current_plan(result, 'Unresolved interruption review requires a fresh current-plan report')
    result["context"].pop("plan_compatibility_needed", None)
    _normalize_current_order_plan(result)
    result["context"]["task"] = task
    result["purchase_intent"] = "subscription_preparation" if task in PURCHASE_TASKS else "none"
    result["payment_intent"] = task if task in {"renew", "upgrade", "change_channel"} else "unresolved" if task in PURCHASE_TASKS else "none"
    validate_state(result)
    return result


FACT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["value", "state", "source", "subject_ref", "observed_at", "applies_when",
                 "required_for", "sensitivity", "clarification_count", "blocker_reason"],
    "properties": {
        "value": {}, "state": {"enum": sorted(FACT_STATES)},
        **{key: {"type": ["string", "null"]} for key in ("source", "observed_at", "applies_when", "blocker_reason")},
        "subject_ref": {"type": "string"}, "sensitivity": {"const": "low"},
        "clarification_count": {"type": "integer", "minimum": 0, "maximum": 1},
        "required_for": {"type": "array", "items": {"enum": ["intake", "plan", "purchase", "apply"]}},
    },
}
# Only P02 may retain the complementary field from a scoped current reply.
# Generic facts remain closed; runtime adds exact account and chronology checks.
P02_RETAINED_VALUE_SCHEMAS = {
    'plan': {'type': 'string', 'pattern': r'\S', 'not': {'const': 'selected_unspecified'}},
    'billing_channel': {'enum': ['apple', 'google', 'web']},
    'status': {'enum': ['active', 'none', 'expired']},
    'page_relation': {'enum': ['same_target', 'other_target', 'outdated']}}
P02_FACT_SCHEMA = {
    **FACT_SCHEMA,
    'properties': {**FACT_SCHEMA['properties'], 'retained_fields': {
        'type': 'object', 'additionalProperties': False, 'minProperties': 1, 'maxProperties': 1,
        'properties': {key: {
            'type': 'object', 'additionalProperties': False,
            'required': ['value', 'state', 'source', 'subject_ref', 'observed_at'],
            'properties': {'value': value_schema, 'state': {'enum': ['reported', 'observed']},
                           'source': {'type': 'string', 'minLength': 1},
                           'subject_ref': {'type': 'string'}, 'observed_at': {'type': ['string', 'null']}}}
            for key, value_schema in P02_RETAINED_VALUE_SCHEMAS.items()}}},
    'allOf': [{'if': {'required': ['retained_fields']}, 'then': {
        'anyOf': [
            {'properties': {'value': {'type': 'object'},
                            'state': {'enum': ['reported', 'observed', 'stale', 'conflict']}}},
            {'properties': {'value': {'type': 'null'},
                            'state': {'enum': ['unknown', 'declined', 'deferred']}}},
            {'properties': {'value': {'type': 'null'},
                            'state': {'enum': ['stale', 'conflict']}}}],
        'allOf': [{'if': {'properties': {'retained_fields': {'required': [key]}}},
                   'then': {'properties': {'value': {'not': {'type': 'object', 'required': [key]}}}}}
                  for key in P02_RETAINED_VALUE_SCHEMAS]}}]}


STATE_SCHEMA["properties"]["facts"] = {
    "type": "object", "additionalProperties": False,
    "properties": {qid: FACT_SCHEMA for qid in QUESTION_PROMPTS if qid != RETIRED and qid not in ALIASES},
}
STATE_SCHEMA['properties']['facts']['properties']['Q-P02'] = P02_FACT_SCHEMA
STATE_SCHEMA["properties"]["context"] = {
    "type": "object", "additionalProperties": False,
    "required": [key for key in CONTEXT_DEFAULTS if key not in INCIDENT_CONTEXT_FIELDS | DEVICE_CONTEXT_FIELDS | PLAN_CONTEXT_FIELDS],
    "properties": {key: {"enum": sorted(ENUM_CONTEXT[key])} if key in ENUM_CONTEXT else
                   {"type": "boolean"} if type(value) is bool else {"type": ["string", "null"]}
                   for key, value in CONTEXT_DEFAULTS.items()},
}
STATE_SCHEMA["properties"]["persistence_consent"] = {
    "type": "object", "additionalProperties": False,
    "required": ["private_save", "export", "public_export"],
    "properties": {key: {"type": "boolean"} for key in ("private_save", "export", "public_export")},
}


STATE_SCHEMA["properties"]["resume_review"] = {
    "type": "object", "additionalProperties": False,
    "required": ["event_id", "binding", "scope_keys", "retained_keys", "status", "response", "changed_keys", "source", "reported_at"],
    "properties": {
        "event_id": {"type": "string", "pattern": "^[A-Za-z0-9_-]{1,80}$"},
        "binding": {"type": "object", "additionalProperties": False,
                    "required": ["task_id", "target_alias", "account_alias", "task", "route", "route_selection_basis"],
                    "properties": {key: {"type": "string"} for key in
                                   ("task_id", "target_alias", "account_alias", "task", "route", "route_selection_basis")}},
        **{key: {"type": "array", "uniqueItems": True, "items": {"enum": sorted(RESUME_FIELD_KEYS)}}
           for key in ("scope_keys", "retained_keys", "changed_keys")},
        "status": {"enum": ["pending", "reviewed", "unresolved", "not_required"]},
        "response": {"enum": [None] + sorted(RESUME_RESPONSES)},
        "source": {"type": ["string", "null"]},
        "reported_at": {"type": ["string", "null"]},
    },
}

# Optional lifecycle receipt, not a purchase or entitlement authorization.
STATE_SCHEMA['properties']['purchase_completion'] = {
    'type': 'object', 'additionalProperties': False,
    'required': ['account_alias', 'source', 'observed_at', 'observed'],
    'properties': {**{key: {'type': 'string'} for key in ('account_alias', 'source', 'observed_at')},
                   'observed': {'type': 'boolean'}}}

# Device facts are categorical even through the published schema interface.
for _device_qid, _device_values in DEVICE_CLEANUP_VALUES.items():
    STATE_SCHEMA['properties']['facts']['properties'][_device_qid] = {
        **FACT_SCHEMA, 'properties': {**FACT_SCHEMA['properties'],
                                     'value': {'enum': [None] + sorted(_device_values)}}}

for _route_qid, _route_values in ROUTE_EXIT_VALUES.items():
    STATE_SCHEMA['properties']['facts']['properties'][_route_qid] = {
        **FACT_SCHEMA, 'properties': {**FACT_SCHEMA['properties'],
                                     'value': {'enum': [None] + sorted(_route_values)}}}

# Optional, validated in code (_validate_authorization); the schema only fixes the shape.
STATE_SCHEMA['properties']['authorization'] = {
    'type': 'object', 'additionalProperties': False, 'required': ['scopes', 'plans', 'confirmations'],
    'properties': {key: {'type': 'array', 'maxItems': 100, 'items': {'type': 'object'}}
                   for key in ('scopes', 'plans', 'confirmations')}}

for _episode_ref_key in ('device_incident_resolution_ref', 'cleanup_offer_dismissed_ref'):
    STATE_SCHEMA['properties']['context']['properties'][_episode_ref_key] = {
        'type': ['string', 'null'], 'pattern': r'^[0-9a-f]{8}(?:\.[0-9a-f]{8}){7}$'}

# Optional schema-1 extension. Runtime validation checks bounded evidence,
# resolution facts and account bindings; old states without it remain valid.
STATE_SCHEMA['properties']['subscription_review'] = {
    'type': 'object', 'additionalProperties': False,
    'required': ['episode_id', 'sequence', 'binding', 'source', 'observed_at',
                 'original', 'detail', 'status', 'resolution'],
    'properties': {
        'episode_id': {'type': 'string', 'pattern': r'^[0-9a-f]{8}(?:\.[0-9a-f]{8}){7}$'},
        'sequence': {'type': 'integer', 'minimum': 1},
        'binding': {'type': 'object'}, 'source': {'type': 'string', 'minLength': 1},
        'observed_at': {'type': ['string', 'null']},
        'original': {'type': 'object', 'additionalProperties': False,
                     'properties': {'Q-J01': FACT_SCHEMA, 'Q-J02': FACT_SCHEMA, 'Q-P02': P02_FACT_SCHEMA}},
        'detail': {'anyOf': [P02_FACT_SCHEMA, {'type': 'null'}]},
        'status': {'enum': ['unresolved', 'resolved']},
        'resolution': {'type': ['object', 'null']}}}
STATE_SCHEMA['properties']['subscription_review']['properties']['latest_report'] = {
    'type': 'object', 'additionalProperties': False,
    'required': ['source', 'observed_at', 'binding', 'detail'],
    'properties': {'source': {'type': 'string', 'minLength': 1}, 'observed_at': {'type': 'string'},
                   'binding': {'type': 'object'}, 'detail': {'anyOf': [P02_FACT_SCHEMA, {'type': 'null'}]}}}
