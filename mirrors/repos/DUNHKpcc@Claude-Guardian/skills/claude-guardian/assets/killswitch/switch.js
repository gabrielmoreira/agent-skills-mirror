'use strict';
const $ = id => document.getElementById(id);
let currentAction = 'status', pendingAction = null, stopped = false;
const descriptions = {
  on: ['开启网络保护', '整机出口模式会影响所有软件：代理停止时，其他软件也可能断网。国内直连、局域网、虚拟机和远程连接须先核对例外。保持代理运行，未及时确认会自动恢复原策略。'],
  off: ['关闭网络保护', '保护和开机加载都会关闭。请先退出相关应用及后台进程；关闭后可能恢复直连。'],
  uninstall: ['卸载防护', '先恢复未保护状态，再移除防护组件。终端会核实相关应用已经退出。'],
  status: ['读取系统状态', '系统可能要求管理员授权；这一步只读取状态，不修改防火墙。']
};
function render(s) {
  $('preview').hidden = !s.preview;
  const known = !s.stale && !s.failed;
  const active = known && s.protection === 'on';
  const coverage = s.coverage;
  const wholeMachine = coverage?.scope === 'whole_machine';
  $('coverage-label').textContent = wholeMachine ? (coverage.stage === 'planned' ? '开启前预检' : '整机出口配置') : '应用覆盖';
  const verified = active && (!coverage || coverage.status === 'pass');
  $('coverage-row').hidden = !coverage;
  $('coverage').textContent = !known ? '需要刷新' : coverage?.status === 'fail' ? '失败，暂停使用' : coverage?.status === 'pass' ? (wholeMachine ? '规则已核实' : '已核实') : '待核实';
  const off = known && s.protection === 'off';
  $('title').textContent = s.pending ? '在本机完成确认' : active ? (verified ? '保护已开启' : coverage.status === 'fail' ? (wholeMachine ? '出口配置变化，请检查' : '应用覆盖失败，暂停使用') : '配置已开启，覆盖待核实') : off ? '保护已关闭' : '先看看当前状态';
  $('summary').textContent = s.pending ? '操作终端已打开，完成后会更新这里。' : active ? (verified ? (wholeMachine ? '整机出站规则与审核基线一致，实际出口另行验收。' : '防直连规则已生效。') : (wholeMachine ? '请核对出站放行规则、代理与网卡条件。' : '恢复应用前，请让 Agent 核对当前版本和组件覆盖。')) : off ? '当前未启用这套防直连保护。' : '读取系统防火墙，确认保护是否生效。';
  $('symbol').className = 'symbol' + (verified ? ' on' : off ? ' off' : '');
  $('protection').textContent = s.stale ? '需要刷新' : active ? '已开启' : off ? '已关闭' : '待核实';
  $('startup').textContent = s.stale ? '需要刷新' : s.startup === true ? '已开启' : s.startup === false ? '已关闭' : '待核实';
  $('checked').textContent = s.checked_at ? new Date(s.checked_at * 1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', second:'2-digit'}) : '—';
  $('message').textContent = [s.message, coverage?.message].filter(Boolean).join(' ') || '请先完成首次部署。';
  currentAction = active ? 'off' : off ? 'on' : 'status';
  $('primary').textContent = s.pending ? '等待本机确认…' : active ? '关闭保护' : off ? '开启保护' : '刷新状态 ↻';
  for (const id of ['primary','refresh','on','off','uninstall']) $(id).disabled = s.pending;
  document.querySelector('main').classList.toggle('busy', s.pending);
}
async function request(route, body) {
  const res = await fetch(route, body ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)} : {});
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || '无法连接本机界面。');
  return data;
}
function ask(action) {
  pendingAction = action;
  $('dialog-title').textContent = descriptions[action][0];
  $('dialog-copy').textContent = descriptions[action][1];
  $('confirm').showModal();
}
$('primary').onclick = () => ask(currentAction);
$('refresh').onclick = () => ask('status');
for (const action of ['on','off','uninstall']) $(action).onclick = () => ask(action);
$('cancel').onclick = () => $('confirm').close();
$('continue').onclick = async () => {
  $('confirm').close();
  try { render(await request('action', {action:pendingAction})); }
  catch (e) { $('message').textContent = e.message; }
};
$('close').onclick = async () => {
  try { await request('close', {}); } catch (e) { $('message').textContent = e.message; return; }
  stopped = true;
  $('title').textContent = '界面已退出';
  $('summary').textContent = '网络保护保持原状态，可关闭此窗口。';
  document.querySelectorAll('button').forEach(b => b.disabled = true);
};
async function poll() {
  if (stopped) return;
  try { render(await request('state')); }
  catch (_) {
    $('title').textContent = '界面连接已结束';
    $('summary').textContent = '保护保持原状态，重新打开桌面入口即可。';
    document.querySelectorAll('button').forEach(b => b.disabled = true);
    stopped = true;
  }
  if (!stopped) setTimeout(poll, 1500);
}
poll();
