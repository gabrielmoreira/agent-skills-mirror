# channel

The user channel: how the conductor reaches YOUR user's thread in the
IM app and speaks there. One folder per IM app, each a complete pack
whose `app:` names the IM and whose place here names the role: the
thread page, the `open` and `send` hands, and `boot/`, the walk every
wake plays first. `ACTIVE.txt` holds one word, the folder in use; with
a single folder it may be absent.

    wechat/       WeChat, recorded on an English-system iPhone

Install one: `physiclaw playbooks install playbooks/channel/wechat
--set CONTACT=<your thread title>`. A second IM installs beside it.
Calibrated geometry is kept per IM (`learned/pages/channel-wechat.json`).
A new IM starts from `physiclaw playbooks init channel/<im>`.
