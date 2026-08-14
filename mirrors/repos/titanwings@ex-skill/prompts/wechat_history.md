# Prompt: 编写微信聊天记录导出工具（Mac + Windows）

## 角色与目标

你是一位精通逆向工程、数据库加密解密、跨平台桌面开发的高级工程师。请帮我编写一个 **微信 PC/Mac 端聊天记录导出工具**，要求支持 macOS 和 Windows 双平台。

---

## 背景知识（你必须基于以下事实来编码）

### 微信本地数据库架构

1. **数据库引擎**：微信使用 SQLCipher（基于 SQLite 的加密扩展）存储聊天记录，腾讯在此基础上封装了自己的 WCDB 框架。
2. **加密方式**：AES-256-CBC 加密，密钥为 32 字节（64 个十六进制字符）。
3. **密钥获取**：密钥在微信进程运行时存在于内存中，需要微信处于**登录状态**才能提取。
4. **数据库文件均使用相同的密钥**（同一个微信账号下）。

### 数据库文件位置

**macOS：**
```
~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/{version_hash}/{wxid_hash}/Message/msg_0.db ~ msg_N.db
```
- 联系人数据库：`../Contact/wccontact_new2.db`
- 群聊数据库：`../Group/group_new.db`
- 每个 msg_X.db 对应不同的聊天记录分片

**Windows：**
```
C:\Users\{username}\Documents\WeChat Files\{wxid_xxxxx}\Msg\Multi\MSG0.db ~ MSGN.db
```
- 单个数据库文件超过约 240MB 时会自动拆分为 MSG1.db、MSG2.db……
- 联系人等信息在同目录或上级目录的其他 .db 文件中

### SQLCipher 解密参数

**macOS 版微信使用 SQLCipher 3 参数：**
```
PRAGMA cipher_page_size = 1024;
PRAGMA kdf_iter = 64000;
PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1;
PRAGMA cipher_hmac_algorithm = HMAC_SHA1;
```

**Windows 版微信使用 SQLCipher 4 或自定义参数：**
```
PRAGMA cipher_page_size = 4096;
PRAGMA kdf_iter = 64000;
PRAGMA cipher_hmac_algorithm = HMAC_SHA256;
PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA256;
```
- Windows 版的 salt 为数据库文件的前 16 字节
- 密钥派生：`key = PBKDF2_HMAC_SHA1(raw_password, salt, 64000, 32)`
- HMAC 校验盐：`mac_salt = bytes([b ^ 0x3a for b in salt])`

---

## 功能需求

请按以下模块分别编写代码：

### 模块 1：密钥提取

#### macOS 密钥提取（Python + subprocess 调用 lldb）

编写一个 Python 脚本，自动执行以下流程：
1. 检测微信进程是否正在运行（`pgrep WeChat`）
2. 使用 lldb 附加到微信进程
3. 在 `sqlite3_key` 函数设置断点
4. 等待微信触发数据库操作（可能需要用户手动登录或发消息）
5. 断点命中后，从寄存器（x86: `$rsi`，ARM: `$x1`）读取密钥指针
6. 读取该指针指向的 32 字节内存数据
7. 将 32 字节转为 64 字符的十六进制字符串输出
8. 自动 detach 并退出 lldb

**关键代码提示：**
```
# lldb 命令序列（ARM Mac）
lldb -p <pid>
br set -n sqlite3_key
c
# 断点命中后：
memory read --size 1 --format x --count 32 $x1
# 对于 Intel Mac，寄存器是 $rsi
```

请封装为一个函数 `get_key_mac() -> str`，返回 hex 格式密钥。

**注意事项：**
- macOS 需要关闭 SIP 才能使用 lldb 附加到微信进程
  - Intel Mac：重启按住 Command+R → 终端 → `csrutil disable; reboot`
  - ARM Mac：关机 → 长按开机键 → 恢复模式 → 终端 → `csrutil disable; reboot`
- 脚本应检测 SIP 状态并给出提示
- 需要 sudo 权限
- 一个微信账号对应一个密钥，如果切换账号需要重新获取

#### Windows 密钥提取（Python + ctypes/pymem）

编写一个 Python 脚本，使用内存扫描方式提取密钥：
1. 使用 `pymem` 或 `ctypes` 打开 `WeChat.exe` 进程
2. 获取 `WeChatWin.dll` 模块的基地址
3. 通过已知的偏移地址（offset）定位密钥在内存中的位置
4. 读取 32 字节密钥数据

**关键逻辑：**
```python
import pymem

pm = pymem.Pymem("WeChat.exe")
module = pymem.process.module_from_name(pm.process_handle, "WeChatWin.dll")
base_addr = module.lpBaseOfDll

# 偏移地址随微信版本变化，需要维护一个版本-偏移映射表
# 例如微信 3.9.x 版本的偏移可能是：
# key_offset = 0x??????
key_addr = base_addr + key_offset
key_bytes = pm.read_bytes(key_addr, 32)
key_hex = key_bytes.hex()
```

请封装为函数 `get_key_windows() -> str`。

**注意事项：**
- 偏移地址会随微信版本更新而变化
- 请提供一个配置文件或字典，允许用户手动更新偏移
- 需要以管理员权限运行
- 提供自动检测微信版本号的功能（读取 WeChat.exe 的文件版本信息）

### 模块 2：数据库解密

编写一个通用的解密函数，输入加密的 .db 文件路径和密钥，输出解密后的 .db 文件：

```python
def decrypt_db(input_path: str, output_path: str, key_hex: str, platform: str = "mac") -> bool:
    """
    解密微信 SQLCipher 数据库
    
    参数：
        input_path: 加密的 .db 文件路径
        output_path: 解密后的输出路径
        key_hex: 64 字符十六进制密钥
        platform: "mac" 或 "windows"，决定使用的 SQLCipher 参数
    
    返回：
        True 表示成功，False 表示失败
    """
```

**两种实现方式（请都写出来，让用户选择）：**

**方式 A：使用 pysqlcipher3**
```python
from pysqlcipher3 import dbapi2 as sqlite
```

**方式 B：使用纯 Python 手动解密（不依赖 sqlcipher）**
- 读取文件前 16 字节作为 salt
- 使用 PBKDF2 派生密钥
- 逐页解密（每页 1024 或 4096 字节）
- 校验 HMAC
- 写入标准 SQLite 文件头（"SQLite format 3\0"）
- 输出为普通 SQLite 数据库文件

### 模块 3：数据库自动发现与批量解密

```python
def find_and_decrypt_all(platform: str, key_hex: str, output_dir: str) -> list:
    """
    自动查找所有微信数据库文件并批量解密
    
    返回解密成功的文件列表
    """
```

功能：
- 自动定位微信数据库目录（支持自定义路径覆盖）
- 遍历所有 .db 文件
- 跳过已解密的文件（检查文件头是否已经是 "SQLite format 3"）
- 处理 WAL 日志：解密前先执行 `PRAGMA wal_checkpoint` 合并最新数据
- 显示进度条
- 返回所有成功解密的文件路径列表

### 模块 4：聊天记录解析与导出

解密后的数据库是标准 SQLite，请编写解析逻辑：

**聊天记录表结构（msg_X.db 中的各表）：**
- 每个聊天会话对应一个表，表名通常是 `Chat_<hash>` 格式
- 关键字段：
  - `mesLocalID` / `localId`：消息本地 ID
  - `mesSvrID`：服务器消息 ID
  - `msgCreateTime` / `createTime`：Unix 时间戳（秒）
  - `msgContent` / `content`：消息内容（文本消息直接存储，其他类型为 XML）
  - `msgType` / `type`：消息类型
  - `msgStatus`：消息状态
  - `msgImgStatus`：图片状态

**消息类型编码：**
```
1    = 文本消息
3    = 图片消息
34   = 语音消息
42   = 名片
43   = 视频消息
47   = 表情包（自定义表情）
48   = 位置消息
49   = 分享链接/文件/小程序（需解析 XML 子类型）
10000 = 系统消息（撤回、红包、拍一拍等）
10002 = 系统消息（群通知等）
```

**导出格式（请全部实现）：**

1. **导出为 CSV**
   - 字段：时间、发送者、消息类型、内容、是否撤回
   - 时间格式化为 `YYYY-MM-DD HH:MM:SS`
   - 编码 UTF-8 with BOM（兼容 Excel）

2. **导出为 HTML**
   - 模拟微信聊天界面样式
   - 区分发送和接收消息（左右气泡）
   - 图片消息显示缩略图（如果本地有图片文件）
   - 支持按日期分组显示

3. **导出为 JSON**
   - 结构化输出，包含完整元数据
   - 便于后续程序处理或 AI 训练使用

### 模块 5：主程序入口（CLI）

提供命令行界面：

```
python wechat_export.py --platform mac|windows [options]

选项：
  --key KEY_HEX          直接提供密钥（跳过自动提取）
  --db-path PATH         手动指定数据库目录
  --output-dir PATH      输出目录（默认 ./output）
  --format csv|html|json|all  导出格式（默认 all）
  --contact WXID         只导出指定联系人的记录
  --date-from YYYY-MM-DD 起始日期过滤
  --date-to YYYY-MM-DD   结束日期过滤
  --merge                合并所有 msg_X.db 为单一数据库
  --extract-key          仅提取密钥并输出
```

---

## 技术要求

1. **语言**：Python 3.10+
2. **依赖管理**：提供 `requirements.txt` 和 `pyproject.toml`
3. **必要依赖**：
   - `pysqlcipher3`（可选，方式 A）
   - `pycryptodome`（方式 B 的手动解密）
   - `pymem`（Windows 密钥提取）
   - `rich`（终端进度条和美化输出）
   - `click` 或 `argparse`（CLI 参数解析）
4. **错误处理**：每个关键步骤都要有异常捕获和友好的错误提示
5. **日志**：使用 Python logging 模块，支持 DEBUG/INFO/WARNING/ERROR 级别
6. **类型注解**：所有函数都要有完整的 type hints
7. **注释**：关键逻辑用中文注释说明
8. **跨平台兼容**：使用 `pathlib.Path` 处理路径，用 `platform.system()` 判断系统

---

## 安全与合规提醒

- 在 README 和程序启动时明确声明：**本工具仅用于导出用户自己的聊天记录，禁止用于非法用途**
- 密钥仅保存在本地，不上传任何网络
- 解密后的数据库文件应提醒用户妥善保管

---

## 项目结构

请按以下结构组织代码：

```
wechat-export/
├── README.md                 # 使用说明（中文）
├── requirements.txt
├── pyproject.toml
├── wechat_export.py          # 主入口（CLI）
├── src/
│   ├── __init__.py
│   ├── key_extractor.py      # 模块 1：密钥提取（mac + windows）
│   ├── decryptor.py          # 模块 2：数据库解密
│   ├── db_finder.py          # 模块 3：数据库发现与批量处理
│   ├── parser.py             # 模块 4：聊天记录解析
│   ├── exporter.py           # 模块 4：导出为 csv/html/json
│   ├── models.py             # 数据模型定义
│   └── utils.py              # 工具函数（时间转换、路径处理等）
├── templates/
│   └── chat.html             # HTML 导出模板
├── config/
│   └── wx_version_offsets.json  # Windows 微信版本与内存偏移映射
└── tests/
    ├── test_decryptor.py
    └── test_parser.py
```

---

## 输出要求

1. 请完整输出每个文件的代码，不要省略
2. 代码必须可以直接运行（安装依赖后）
3. 如果某些功能由于微信版本更新可能失效，请在代码注释中标注，并提供用户自行适配的指引
4. 在 README 中提供详细的安装步骤和使用示例，包括：
   - macOS 关闭 SIP 的完整步骤
   - Windows 以管理员权限运行的方法
   - 常见问题排查（FAQ）