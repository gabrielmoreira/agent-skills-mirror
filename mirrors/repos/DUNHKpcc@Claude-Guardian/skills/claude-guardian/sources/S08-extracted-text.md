# S08 PDF 可搜索文字层（不完整辅助版）

来源：[原始 11 页 PDF](S08-vps-claude-tutorial.pdf)。此文件仅提取文字层，方便定位；第 3、4、5 页各有一张截图，文字提取没有包含；截图内容已在文末“截图说明”里转述，细节以原 PDF 为准。版面、换行及部分符号可能与原稿不同；以原 PDF 为准。

## PDF 第 1 页

#   自媒体      #   教程
前提：有一张外卡（美实体最好）适合编码 写作 科研项目需求（不适用游戏引擎，等computer
use 接外部mcp等）

   目标：自己购买 VPS，在 VPS 上完成 Claude 订阅、OAuth 登录，并通过 VS Code
   Remote-SSH 日常开发。

为什么选择VPS，稳定的使用环境，不用担心IP乱跳，系统 语言 时区 地区等问题，另外的好处
是kyc跳出的概率低

1.   购买 VPS
  推荐 dmit（美西premium）搬瓦房 aws vultr 等CN2 GIA带三网优化的线路（后期走图形化
VPS
界面更稳定）
如果有推荐的可以参考群和b友
好的机房IP不用担心，最后都可套静态ISP出口
推荐配置
 项目 配置
 类型 根据自己的项目需求自己选
 CPU       2c 4c
 内存 2g 4g 8g
 磁盘 根据项目自己选择
 系统 Ubuntu 24.04
 网络 公网 IPv4
 架构 x86_64
内存根据vscode配置最低2g以上，想要用的舒服上4g，大型项目8-16g
系统推荐首选ubuntu，系统完整度高，新手友好，有图形化界面，生态友好
架构首选x86，vscode兼容性最好
创建服务器
Vultr   举例：

## PDF 第 2 页

1. Products → Compute → Deploy
 2. 选择 Cloud Compute
 3. Region 选择你正常使用且 Anthropic 支持的地区
 4. OS 选择 Ubuntu 24.04 x64
 5. Plan 选择 4 vCPU / 8 GB
 6. 添加自己的 SSH Public Key
 7. 创建服务器

服务器创建后会获得公网 IPv4。
Vultr 普通实例 IPv4 在实例存续期间保持不变；如果以后需要删除/更换实例仍保留 IP，可额外使
用 Reserved IP。
记录：
           你的服务器IP
  SERVER_IP=

关于安全组，ssh 22 端口的安全性问题
如果不在乎安全性，直接公网➕ ssh key即可
在乎安全性我提供几个方案
  Tailscale + SSH Key 适合个人用户 ✅ 注意备用出口
  改个端口号，不用22 最简单
  跳板机 门槛最高，适合商业化

2.    本地连接服务器
    创建的时候系统就帮你生成好了，下载即可
dmit aws

本机生成 SSH Key：
  ssh-keygen -t ed25519 -C "workspace"

首次连接：
  ssh root@SERVER_IP

重要查询IP信息（这点很重要，如果随机到的IP不好，能找客服换就换）

## PDF 第 3 页

查询命令 bash <(curl -sL IP.Check.Place)

例如如图机房IP，算好的，如果直接用该ip没问题，想套家宽出口也ok
创建日常开发用户（这一步有没有都行，例如aws直接用下载的key来ssh就行）：
 adduser dev
 usermod -aG sudo dev

 mkdir -p /home/dev/.ssh
 cp /root/.ssh/authorized_keys /home/dev/.ssh/authorized_keys
 chown -R dev:dev /home/dev/.ssh
 chmod 700 /home/dev/.ssh
 chmod 600 /home/dev/.ssh/authorized_keys

重新连接：
 ssh dev@SERVER_IP

有条件写 .ssh config
3.   初始化开发环境

## PDF 第 4 页

基本环境 node npm git等 Node https://nodejs.org/en Git https://git-scm.com/
如果习惯使用终端开发可下载nvim mosh tmux等
nvim终端代码编辑器 mosh稳定的ssh工具 tmux终端多线程管理

重新 SSH 登录后生效。
安装 Claude Code
官方 Linux 安装方式：
  curl -fsSL https://claude.ai/install.sh | bash

验证：
  claude --version

有条件

4.   配置 VS Code Remote-SSH

## PDF 第 5 页

本地安装：
     Visual Studio Code
     Remote - SSH   扩展

编辑本机：
 ~/.ssh/config

加入：
 Host claude-workspace
     HostName SERVER_IP
     User dev
     IdentityFile ~/.ssh/id_ed25519
     ServerAliveInterval 30
     ServerAliveCountMax 6
     TCPKeepAlive yes

测试：
 ssh claude-workspace

之后项目直接放在服务器，例如：
 mkdir -p ~/workspace
 cd ~/workspace

5.   安装临时远程浏览器（通过xvfb实现linux远程屏幕）
浏览器只在：
这里建议参考up的上一期视频 防封教程

## PDF 第 6 页

Claude   注册/登录。
     养号
     购买订阅
     OAuth
  重新授权
时启动。
不需要安装完整 Ubuntu Desktop。
关于远程桌面的几种技术讨论，按照自己的需求来，拿到我文档后不会部署直接发给agent
  Xvfb + Openbox + x11vnc + noVNC 最通用，浏览器直接打开，无需用户安装客户端。缺点
  是组件稍多
  TigerVNC / Xvnc 综合最好
  Xpra 优点是资源占用小、体验比传统 VNC 好，甚至不需要完整桌面
  等等
安装：
 sudo apt install -y \
   xvfb openbox x11vnc novnc websockify

安装 Google Chrome：
 wget https://dl.google.com/linux/direct/google-chrome-
 stable_current_amd64.deb

 sudo apt install -y ./google-chrome-stable_current_amd64.deb

这里如果暴内存了，优先创建swap，实在不行再升级配置 正常只有Claude单个标签页 500mb上
下

6.   启动 VPS 浏览器
SSH   到 VPS 后执行：
 Xvfb :99 -screen 0 1440x900x24 >/tmp/xvfb.log 2>&1 &

 DISPLAY=:99 openbox >/tmp/openbox.log 2>&1 &

## PDF 第 7 页

DISPLAY=:99 google-chrome \
     --user-data-dir="$HOME/.claude-browser" \
     --no-first-run \
     --disable-dev-shm-usage \
     >/tmp/chrome.log 2>&1 &

 x11vnc \
     -display :99 \
     -localhost \
     -forever \
     -shared \
     -nopw \
     >/tmp/x11vnc.log 2>&1 &

 websockify \
     --web=/usr/share/novnc \
     127.0.0.1:6080 \
     localhost:5900 \
     >/tmp/novnc.log 2>&1 &

不要把 6080 或 5900 直接开放到公网。

7.   本地打开 VPS 浏览器
在本机新终端运行：
 ssh -L 6080:127.0.0.1:6080 claude-workspace

本地浏览器打开：
 http://127.0.0.1:6080/vnc.html

看到的 Chrome 实际运行在 VPS 上，因此 Chrome 的互联网出口是 VPS。

8.   购买 Claude 订阅
#   参考防封指南
在 VPS Chrome 中：

## PDF 第 8 页

1. 打开 https://claude.ai
2. 登录自己的 Claude 账号
3. 使用自己的真实账号及支付资料
4. Settings → Billing
5.  选择需要的套餐
 6. 完成订阅

截至 2026-09：
套餐      官方 Web 价格
Pro          $20/月
Max 5x      $100/月
Max 20x     $200/月

Pro  和 Max 均支持 Claude Code；重度 Claude Code 用户通常需要根据实际额度需求选择
Max  。

10. Claude Code OAuth
这一步之前必须从free号开始养号，养号之前做不了这步
回到 VPS SSH：
 cd ~/workspace
 claude

需要登录时执行：
 /login

如果终端给出授权 URL：
 1. 复制 URL
 2. 粘贴到 VPS Chrome
 3. 登录自己的 Claude 账号
 4. 完成 OAuth 授权
 5. 回到 VPS Terminal

## PDF 第 9 页

之后直接：
 cd ~/workspace/your-project
 claude

日常链路：
 本地 VS Code
        │
        │ Remote-SSH
        ▼
 4C8G VPS
       │
        ├── VS Code Server
        ├── 项目代码
        ├── Docker
        └── Claude Code
               │
               ▼
            Anthropic

11.   登录完成后关闭浏览器
授权完成后无需长期运行 Chrome/noVNC。
执行：
 pkill -f 'google-chrome.*.claude-browser' || true
 pkill -f 'websockify.*6080' || true
 pkill x11vnc || true
 pkill -f 'Xvfb :99' || true

这样日常不会额外占用约 0.6–1.2 GB 浏览器内存。
需要重新登录时再次执行第 6～7 步即可。

12.   推荐使用 tmux
#   可以安装claude-hud的插件，创建claudecode自动起一个tmux线程
运行 Claude Code：

## PDF 第 10 页

tmux new -A -s claude

然后：
 cd ~/workspace/your-project
 claude

即使 SSH 或本地网络断开，VPS 上的任务仍可继续。
重新连接：
 ssh claude-workspace
 tmux attach -t claude

13. 4C8G   使用建议（可选）
适合同时运行：
 VS Code Server
 Claude Code
 Node/Python Language Server
 Docker
 数据库
 项目 Build/Test
建议给系统保留 Swap：
 sudo fallocate -l 4G /swapfile
 sudo chmod 600 /swapfile
 sudo mkswap /swapfile
 sudo swapon /swapfile
 echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

大型项目建议定期检查：
 free -h
 df -h
 docker stats
 htop

## PDF 第 11 页

14.   日常使用流程
以后基本只需要：
 ① 打开 VS Code
 ② Remote-SSH → claude-workspace
 ③ 打开 ~/workspace/项目
 ④ 打开 Terminal
 ⑤ tmux new -A -s claude
 ⑥ claude
只有 Claude 登录失效、订阅管理或重新 OAuth 时，才启动 VPS 远程浏览器。

关于如何套家宽IP出口，自己搜索Ai或者查询教程即可
官方参考
  Claude 计划：https://support.claude.com/en/articles/11049762-choose-a-claude-plan
  Claude Code 安装：https://support.claude.com/en/articles/14552382-your-first-day-in-
  claude-code
  VS Code Remote-SSH    ：https://code.visualstudio.com/docs/remote/ssh
  Anthropic 支持地区：https://www.anthropic.com/supported-countries
  Vultr IPv4：https://docs.vultr.com/support/products/compute/how-do-i-get-a-vultr-compute-
  instance-dedicated-ip-address

## 截图说明（转述，细节以原 PDF 为准）

- **第 3 页：IP.Check.Place 检测报告示例。**教程用它说明“怎么看一个 VPS 的 IP 好不好”，并写道：例如图里的机房 IP，算好的；如果直接用该 IP 没问题，想套家宽出口也可以。报告分六部分：基础信息（时区、IP 类型，图中为原生 IP）；IP 类型属性（IPinfo、ipregistry、ipapi、IP2Location、AbuseIPDB 的使用类型和公司类型，图中均为“机房”）；风险评分（IP2Location、Scamalytics、ipapi 为低风险，AbuseIPDB 得分 0）；风险因子（代理、Tor、VPN、滥用、机器人为否，服务器为是）；流媒体及 AI 服务解锁（TikTok、Disney+、Netflix、Youtube、AmazonPV、Reddit、ChatGPT 的状态和地区，图中地区为美国）；邮局连通性及黑名单检测（本地 25 端口出站被阻止、远端 25 端口不可达；IP 黑名单数据库有效 423 个，正常 397，已标记 24，黑名单 2）。
- **第 4 页：**LazyVim（Neovim 发行版）的启动界面截图，配合“终端开发可下载 nvim、mosh、tmux”的说明。
- **第 5 页：**VS Code 的 Remote - SSH 扩展页面截图，配合“本地安装 VS Code 和 Remote - SSH 扩展”的说明。
