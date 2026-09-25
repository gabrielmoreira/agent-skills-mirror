要使用 **FastAPI + SQLAlchemy + Alembic** 实现数据库字段更新，核心是通过 Alembic 跟踪 SQLAlchemy 模型的变化，生成迁移脚本并执行。以下是完整步骤（含示例、配置细节和常见场景）：


## 一、环境准备
先确保已安装依赖（若未安装）：
```bash
pip install fastapi uvicorn sqlalchemy alembic pymysql  # pymysql用于MySQL，PostgreSQL用psycopg2-binary
```


## 二、核心概念
- **SQLAlchemy**：ORM 工具，定义数据库模型（表结构）。
- **Alembic**：数据库迁移工具，跟踪模型变化，生成/执行迁移脚本（基于 `alembic.ini` 和 `env.py` 配置）。
- **迁移脚本**：Alembic 生成的 Python 文件（存于 `alembic/versions/`），包含 `upgrade()`（更新结构）和 `downgrade()`（回滚结构）逻辑。


## 三、完整操作步骤（以 MySQL 为例）
### 步骤 1：初始化 Alembic（仅首次）
在项目根目录执行以下命令，生成 Alembic 配置文件（`alembic.ini`）和迁移目录（`alembic/`）：
```bash
alembic init alembic
```

执行后，项目结构如下：
```
your_project/
├── alembic/              # 迁移目录
│   ├── versions/         # 迁移脚本存放处
│   ├── env.py            # 迁移核心配置（关键！）
│   └── script.py.mako    # 迁移脚本模板
├── alembic.ini           # Alembic 全局配置
├── main.py               # FastAPI 主程序
└── models.py             # SQLAlchemy 模型定义
```


### 步骤 2：配置 Alembic（关键两步）
需要修改两个核心文件，让 Alembic 连接数据库并识别 SQLAlchemy 模型。

#### 2.1 配置 `alembic.ini`（数据库连接）
打开 `alembic.ini`，找到 `sqlalchemy.url` 字段，修改为你的数据库连接 URL（与 SQLAlchemy 一致）：
```ini
# alembic.ini
sqlalchemy.url = mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4

# 示例（本地MySQL）：
# sqlalchemy.url = mysql+pymysql://root:123456@localhost:3306/fastapi_db?charset=utf8mb4

# 若用SQLite（无需密码）：
# sqlalchemy.url = sqlite:///./fastapi_db.db

# 若用PostgreSQL：
# sqlalchemy.url = postgresql://user:password@localhost:5432/fastapi_db
```

#### 2.2 配置 `alembic/env.py`（识别 SQLAlchemy 模型）
Alembic 需通过 `env.py` 加载 SQLAlchemy 的模型基类（`Base`），才能对比模型与数据库的差异。

修改 `alembic/env.py` 如下：
```python
# alembic/env.py
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. 将项目根目录加入 Python 路径（否则无法导入 models）
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 2. 导入 SQLAlchemy 的 Base 基类和所有模型（必须导入所有模型，否则 Alembic 检测不到变化）
from models import Base  # 从你的模型文件导入 Base
from models import User, Item  # 导入所有定义的模型（示例：User、Item表）

# 3. 加载 alembic.ini 配置
config = context.config
fileConfig(config.config_file_name)

# 4. 告诉 Alembic 模型的元数据（关键！）
target_metadata = Base.metadata

# 以下是默认生成的代码，无需修改
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

⚠️ 关键注意：
- 必须导入 **所有 SQLAlchemy 模型**（如 `User`、`Item`），否则 Alembic 无法检测未导入模型的变化。
- 若导入报错，检查 `sys.path.append` 是否正确（确保能找到 `models.py`）。


### 步骤 3：定义/修改 SQLAlchemy 模型
假设 `models.py` 中初始模型如下（已创建 `User` 表）：
```python
# models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# 模型基类（所有模型继承此类）
Base = declarative_base()

# 初始 User 模型（含 id、name 字段）
class User(Base):
    __tablename__ = "users"  # 数据库表名

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)  # 初始字段：姓名
```

现在需要 **更新字段**（示例场景）：
1. 给 `User` 表添加非空字段 `email`（带默认值，避免现有数据报错）；
2. 修改 `name` 字段长度从 `50` 改为 `100`；
3. 删除冗余字段 `age`（假设之前有，现在移除）。

修改后的模型：
```python
# models.py（修改后）
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)  # 1. 修改长度：50→100
    email = Column(String(100), index=True, nullable=False, default="default@example.com")  # 2. 新增字段
    # age = Column(Integer)  # 3. 删除字段：注释/删除该行
```


### 步骤 4：生成迁移脚本
Alembic 会对比「当前模型」与「数据库现有结构」，自动生成迁移脚本。执行以下命令：
```bash
alembic revision --autogenerate -m "add email field, modify name length, drop age field"
```

- `--autogenerate`：自动检测模型变化，生成迁移逻辑（无需手动写 SQL）。
- `-m "描述信息"`：给迁移脚本加备注（便于后续查看历史）。

执行后，会在 `alembic/versions/` 下生成一个新的迁移脚本（文件名格式：`xxxxxx_描述信息.py`），例如 `20251129_123456_add_email_field_modify_name_length_drop_age_field.py`。


### 步骤 5：检查并编辑迁移脚本（关键！）
⚠️ **自动生成的脚本可能不完美**，必须打开迁移脚本检查逻辑，避免执行失败（比如新增非空字段未加默认值）。

打开生成的迁移脚本，核心逻辑在 `upgrade()` 和 `downgrade()` 中，示例如下：
```python
# alembic/versions/xxxxxx_xxx.py
from alembic import op
import sqlalchemy as sa

# 迁移版本号（自动生成）
revision = 'xxxxxx'
down_revision = '前一个版本号（首次迁移为None）'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. 修改 name 字段长度：从 String(50) 改为 String(100)
    op.alter_column('users', 'name', existing_type=sa.VARCHAR(length=50), type_=sa.VARCHAR(length=100), existing_nullable=True)
    # 2. 新增 email 字段（带默认值，nullable=False）
    op.add_column('users', sa.Column('email', sa.String(length=100), server_default='default@example.com', nullable=False))
    # 3. 删除 age 字段（若之前存在）
    op.drop_column('users', 'age')

def downgrade() -> None:
    # 回滚逻辑：与 upgrade 相反
    op.add_column('users', sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('users', 'email')
    op.alter_column('users', 'name', existing_type=sa.VARCHAR(length=100), type_=sa.VARCHAR(length=50), existing_nullable=True)
```

#### 常见需要手动调整的场景：
- 新增 **非空字段**：必须加 `server_default`（数据库级默认值），否则现有数据无值会报错（`nullable=False` 需配合默认值）。
- 修改字段类型：若字段已有数据（如 `String(50)` 改 `String(30)`），需确保现有数据长度≤30，否则迁移失败。
- 重命名字段：Alembic 不会自动识别重命名（会认为是「删除旧字段+新增新字段」），需手动修改脚本为 `op.rename_column('表名', '旧字段', '新字段')`。


### 步骤 6：执行迁移（更新数据库）
确认迁移脚本逻辑正确后，执行以下命令应用迁移（更新数据库结构）：
```bash
alembic upgrade head
```

- `head`：表示应用所有未执行的迁移（即最新版本）。
- 若想执行指定版本：`alembic upgrade 版本号前几位`（如 `alembic upgrade 202511`）。

执行成功后，数据库的 `users` 表会同步模型的字段变化！


### 步骤 7：验证迁移结果
可通过 SQL 客户端（如 Navicat、DBeaver）连接数据库，查看 `users` 表的字段是否已更新（`name` 长度100、新增 `email`、删除 `age`）。


### 步骤 8：回滚迁移（可选，若迁移出错）
若迁移后发现问题，可回滚到上一个版本：
```bash
# 回滚上一个版本
alembic downgrade -1

# 回滚到指定版本（如回滚到初始状态，版本号为 None）
alembic downgrade base

# 查看迁移历史（所有版本及当前版本）
alembic history --verbose
```


## 四、常见字段更新场景示例
### 场景 1：新增字段（允许为空）
模型中添加 `phone` 字段：
```python
# models.py
phone = Column(String(20), index=True, nullable=True)  # 允许为空
```
生成迁移脚本后，`upgrade()` 会自动生成：
```python
op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
```
无需手动调整，直接执行迁移即可。

### 场景 2：修改字段默认值
模型中给 `email` 字段修改默认值：
```python
# models.py
email = Column(String(100), index=True, nullable=False, default="new_default@example.com")
```
生成迁移脚本后，需手动调整为：
```python
def upgrade() -> None:
    op.alter_column('users', 'email', server_default='new_default@example.com')

def downgrade() -> None:
    op.alter_column('users', 'email', server_default='default@example.com')
```

### 场景 3：添加外键字段
模型中给 `Item` 表添加关联 `User` 的外键：
```python
# models.py
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    user_id = Column(Integer, sa.ForeignKey("users.id"))  # 外键关联 users.id
```
生成迁移脚本后，会自动生成外键约束：
```python
op.add_column('items', sa.Column('user_id', sa.Integer(), nullable=True))
op.create_foreign_key(None, 'items', 'users', ['user_id'], ['id'])
```


## 五、关键注意事项
1. **必须导入所有模型**：`env.py` 中若漏导入模型，Alembic 无法检测该模型的变化，导致迁移脚本缺失。
2. **生产环境先备份**：执行 `alembic upgrade` 前，务必备份数据库（避免迁移失败导致数据丢失）。
3. **避免手动修改数据库**：所有表结构变更必须通过「修改模型 + 生成迁移脚本 + 执行迁移」实现，禁止直接在数据库中手动改字段（会导致模型与数据库不一致）。
4. **处理数据兼容性**：修改/删除字段前，确保业务代码已兼容（如删除 `age` 字段前，先删除所有引用 `age` 的代码）。