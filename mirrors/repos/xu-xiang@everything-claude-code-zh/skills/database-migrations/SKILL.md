---
name: database-migrations
description: 跨 PostgreSQL、MySQL 及常用 ORM（Prisma、Drizzle、Django、TypeORM、golang-migrate）的模式变更（schema changes）、数据迁移、回滚及零停机部署（zero-downtime deployments）的数据库迁移最佳实践。
origin: ECC
---

# 数据库迁移模式（Database Migration Patterns）

面向生产系统的安全、可逆的数据库模式变更（Schema Changes）。

## 激活时机

- 创建或修改数据库表
- 添加/删除列或索引
- 执行数据迁移（数据回填 backfill、转换 transform）
- 规划零停机（zero-downtime）模式变更
- 为新项目设置迁移工具链

## 核心原则

1. **所有变更皆为迁移** —— 严禁手动修改生产环境数据库
2. **生产环境仅向前迁移** —— 回滚需使用新的向前迁移（forward migrations）
3. **模式迁移与数据迁移分离** —— 严禁在一次迁移中混用 DDL 和 DML
4. **针对生产规模数据进行测试** —— 在 100 行数据上正常的迁移可能会导致 1000 万行数据锁表
5. **部署后的迁移不可变** —— 严禁编辑已在生产环境运行过的迁移文件

## 迁移安全核查表（Migration Safety Checklist）

在执行任何迁移之前：

- [ ] 迁移包含 UP 和 DOWN 脚本（或明确标记为不可逆）
- [ ] 对大表不执行全表锁（使用并发操作）
- [ ] 新列具有默认值或可为空（严禁添加不带默认值的 NOT NULL）
- [ ] 索引并发创建（对于现有表，不与 CREATE TABLE 同行执行）
- [ ] 数据回填与模式变更分为独立迁移
- [ ] 已针对生产数据副本进行测试
- [ ] 已记录回滚方案

## PostgreSQL 模式

### 安全地添加列

```sql
-- 推荐：可为空的列，无锁
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- 推荐：带默认值的列（Postgres 11+ 是瞬时的，无需重写表）
ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true;

-- 糟糕：在现有表上添加不带默认值的 NOT NULL（需要全表重写）
ALTER TABLE users ADD COLUMN role TEXT NOT NULL;
-- 这会锁定表并重写每一行
```

### 无停机添加索引

```sql
-- 糟糕：在大表上会阻塞写入
CREATE INDEX idx_users_email ON users (email);

-- 推荐：非阻塞，允许并发写入
CREATE INDEX CONCURRENTLY idx_users_email ON users (email);

-- 注意：CONCURRENTLY 不能在事务块内运行
-- 大多数迁移工具需要对此进行特殊处理
```

### 重命名列（零停机）

严禁在生产环境直接重命名。请使用“扩展-收缩（expand-contract）”模式：

```sql
-- 第 1 步：添加新列（迁移文件 001）
ALTER TABLE users ADD COLUMN display_name TEXT;

-- 第 2 步：回填数据（迁移文件 002，数据迁移）
UPDATE users SET display_name = username WHERE display_name IS NULL;

-- 第 3 步：更新应用代码以同时读/写这两个列
-- 部署应用变更

-- 第 4 步：停止写入旧列，将其删除（迁移文件 003）
ALTER TABLE users DROP COLUMN username;
```

### 安全地删除列

```sql
-- 第 1 步：移除应用中所有对该列的引用
-- 第 2 步：部署不包含该列引用的应用
-- 第 3 步：在下一次迁移中删除列
ALTER TABLE orders DROP COLUMN legacy_status;

-- 对于 Django：使用 SeparateDatabaseAndState 从模型中移除
-- 而不生成 DROP COLUMN 指令（然后在下一次迁移中删除）
```

### 大规模数据迁移

```sql
-- 糟糕：在单个事务中更新所有行（会导致锁表）
UPDATE users SET normalized_email = LOWER(email);

-- 推荐：带进度的分批更新
DO $$
DECLARE
  batch_size INT := 10000;
  rows_updated INT;
BEGIN
  LOOP
    UPDATE users
    SET normalized_email = LOWER(email)
    WHERE id IN (
      SELECT id FROM users
      WHERE normalized_email IS NULL
      LIMIT batch_size
      FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS rows_updated = ROW_COUNT;
    RAISE NOTICE 'Updated % rows', rows_updated;
    EXIT WHEN rows_updated = 0;
    COMMIT;
  END LOOP;
END $$;
```

## Prisma (TypeScript/Node.js)

### 工作流

```bash
# 根据模式变更创建迁移
npx prisma migrate dev --name add_user_avatar

# 在生产环境执行待处理的迁移
npx prisma migrate deploy

# 重置数据库（仅限开发环境）
npx prisma migrate reset

# 模式变更后生成客户端
npx prisma generate
```

### Schema 示例

```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  avatarUrl String?  @map("avatar_url")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  orders    Order[]

  @@map("users")
  @@index([email])
}
```

### 自定义 SQL 迁移

用于 Prisma 无法表达的操作（并发索引、数据回填等）：

```bash
# 仅创建空白迁移，然后手动编辑 SQL
npx prisma migrate dev --create-only --name add_email_index
```

```sql
-- migrations/20240115_add_email_index/migration.sql
-- Prisma 无法生成 CONCURRENTLY，因此我们手动编写
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);
```

## Drizzle (TypeScript/Node.js)

### 工作流

```bash
# 根据模式变更生成迁移文件
npx drizzle-kit generate

# 执行迁移
npx drizzle-kit migrate

# 直接推送模式（仅限开发环境，不生成迁移文件）
npx drizzle-kit push
```

### Schema 示例

```typescript
import { pgTable, text, timestamp, uuid, boolean } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").primaryKey().defaultRandom(),
  email: text("email").notNull().unique(),
  name: text("name"),
  isActive: boolean("is_active").notNull().default(true),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
});
```

## Django (Python)

### 工作流

```bash
# 根据模型变更生成迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 显示迁移状态
python manage.py showmigrations

# 为自定义 SQL 生成空白迁移
python manage.py makemigrations --empty app_name -n description
```

### 数据迁移

```python
from django.db import migrations

def backfill_display_names(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    batch_size = 5000
    users = User.objects.filter(display_name="")
    while users.exists():
        batch = list(users[:batch_size])
        for user in batch:
            user.display_name = user.username
        User.objects.bulk_update(batch, ["display_name"], batch_size=batch_size)

def reverse_backfill(apps, schema_editor):
    pass  # 数据迁移，无需回滚逻辑

class Migration(migrations.Migration):
    dependencies = [("accounts", "0015_add_display_name")]

    operations = [
        migrations.RunPython(backfill_display_names, reverse_backfill),
    ]
```

### SeparateDatabaseAndState

从 Django 模型中移除列，但不立即从数据库中删除：

```python
class Migration(migrations.Migration):
    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(model_name="user", name="legacy_field"),
            ],
            database_operations=[],  # 暂时不触碰数据库
        ),
    ]
```

## golang-migrate (Go)

### 工作流

```bash
# 创建一对迁移文件
migrate create -ext sql -dir migrations -seq add_user_avatar

# 执行所有待处理的迁移
migrate -path migrations -database "$DATABASE_URL" up

# 回滚最后一次迁移
migrate -path migrations -database "$DATABASE_URL" down 1

# 强制指定版本（修复 dirty 状态）
migrate -path migrations -database "$DATABASE_URL" force VERSION
```

### 迁移文件示例

```sql
-- migrations/000003_add_user_avatar.up.sql
ALTER TABLE users ADD COLUMN avatar_url TEXT;
CREATE INDEX CONCURRENTLY idx_users_avatar ON users (avatar_url) WHERE avatar_url IS NOT NULL;

-- migrations/000003_add_user_avatar.down.sql
DROP INDEX IF EXISTS idx_users_avatar;
ALTER TABLE users DROP COLUMN IF EXISTS avatar_url;
```

## 零停机迁移策略（Zero-Downtime Migration Strategy）

对于关键生产变更，遵循“扩展-收缩（expand-contract）”模式：

```
阶段 1：扩展（EXPAND）
  - 添加新列/表（可为空或带默认值）
  - 部署：应用同时写入旧列和新列
  - 回填现有数据

阶段 2：迁移（MIGRATE）
  - 部署：应用从新列读取，同时写入旧列和新列
  - 验证数据一致性

阶段 3：收缩（CONTRACT）
  - 部署：应用仅使用新列
  - 在独立的迁移中删除旧列/表
```

### 时间线示例

```
第 1 天：通过迁移添加 new_status 列（可为空）
第 1 天：部署应用 v2 —— 同时写入 status 和 new_status
第 2 天：为现有行运行数据回填迁移
第 3 天：部署应用 v3 —— 仅从 new_status 读取
第 7 天：通过迁移删除旧的 status 列
```

## 反模式（Anti-Patterns）

| 反模式 | 失败原因 | 更好做法 |
|-------------|-------------|-----------------|
| 在生产环境手动执行 SQL | 无审计跟踪，不可重复 | 始终使用迁移文件 |
| 编辑已部署的迁移 | 导致环境间出现差异（drift） | 创建新的迁移文件 |
| 不带默认值的 NOT NULL | 锁表，重写所有行 | 先添加可为空列，回填数据，再添加约束 |
| 在大表上使用内联索引 | 在构建期间阻塞写入 | 使用 CREATE INDEX CONCURRENTLY |
| 模式与数据混在同一个迁移中 | 难以回滚，事务过长 | 将其分为独立的迁移 |
| 在移除代码前删除列 | 应用因缺少列而报错 | 先移除代码，在下一次部署时删除列 |
