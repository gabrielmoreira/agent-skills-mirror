---
name: shopping-cart-expert
description: |
  购物车模块域专家。管理商品加购、数量修改、优惠计算和结算流程。
  触发关键词: 购物车、cart、加购、结算、SKU、优惠券、coupon、下单、checkout
---

# 🛒 购物车模块域专家 (`shopping-cart-expert`)

> 📌 **这是一个示例域专家**，展示如何使用 PaceNote 的模板 v4 为自己的业务模块创建域专家。
> 请参考此示例为你的实际项目创建域专家。

---

## 执行声明

```
🔧 正在执行: shopping-cart-expert (#shopping-cart-expert)
✅ 已加载购物车模块知识
⭕ 当前步骤: [根据用户问题动态填充]
```

---

## 模块概述

**购物车模块**是电商平台的核心交易模块，负责从用户加购商品到发起结算的完整流程。

### 核心职责
1. **商品管理** — 加购、删除、修改数量、规格切换
2. **价格计算** — 实时计算含优惠券/满减/会员折扣的最终价格
3. **库存校验** — 实时校验库存，处理超卖风险
4. **结算入口** — 生成结算订单数据，传递给订单模块

### 边界声明
- ❌ **不负责**: 订单创建（属于 `order-expert`）
- ❌ **不负责**: 支付处理（属于 `payment-expert`）
- ❌ **不负责**: 商品详情展示（属于 `product-expert`）

---

## 场景入口

| # | 场景 | 典型需求关键词 | 涉及核心文件 |
|---|------|--------------|-------------|
| 1 | 加购商品 | 加入购物车、加购、add to cart | `src/cart/services/CartService.ts`, `src/cart/models/CartItem.ts` |
| 2 | 修改数量 | 数量变更、增减、stepper | `src/cart/components/QuantityStepper.vue`, `src/cart/services/CartService.ts` |
| 3 | 优惠计算 | 优惠券、满减、折扣、促销 | `src/cart/services/PriceCalculator.ts`, `src/cart/models/Discount.ts` |
| 4 | 结算流程 | 结算、checkout、去付款 | `src/cart/services/CheckoutService.ts`, `src/cart/pages/Checkout.vue` |
| 5 | 库存校验 | 缺货、库存不足、超卖 | `src/cart/services/StockValidator.ts` |
| 6 | 购物车持久化 | 登录合并、离线缓存 | `src/cart/services/CartStorage.ts`, `src/cart/services/CartMerger.ts` |

---

## ⚠️ 踩坑陷阱表

| # | 陷阱描述 | ❌ 错误做法 | ✅ 正确做法 | 严重度 |
|---|---------|-----------|-----------|--------|
| 1 | 并发加购导致重复 | 前端不做防抖，连续点击多次加购 | 加购按钮 300ms 防抖 + 后端幂等校验（用 requestId） | 🔴 高 |
| 2 | 优惠计算精度丢失 | 用 float 计算价格 | 全程使用整数分（cent）计算，仅展示时转换 | 🔴 高 |
| 3 | 库存检查时机 | 仅在加购时校验库存 | 加购时校验 + 结算时二次校验 + 支付前终校验 | 🔴 高 |
| 4 | 登录后购物车合并 | 覆盖式合并（丢失匿名购物车） | 三方合并策略：取数量最大值 + 保留匿名车特有项 | 🟡 中 |
| 5 | 满减活动叠加 | 允许无限叠加优惠 | 优惠互斥规则引擎，按优先级选最优组合 | 🟡 中 |
| 6 | 大量 SKU 性能 | 购物车不限商品数渲染 | 限制 99 件 + 虚拟滚动 + 分批加载 | 🟡 中 |

---

## 依赖关系

### 上游依赖（我调用谁）

| 模块 | 交互方式 | 典型场景 |
|------|---------|---------|
| `product-service` | REST API `GET /api/products/{id}` | 加购时获取商品最新信息 |
| `inventory-service` | gRPC `CheckStock()` | 校验库存 |
| `promotion-service` | REST API `POST /api/promotions/calculate` | 计算优惠 |
| `user-service` | JWT Token 解析 | 获取用户 ID 和会员等级 |

### 下游依赖（谁调用我）

| 模块 | 交互方式 | 典型场景 |
|------|---------|---------|
| `order-service` | 事件 `CartCheckedOut` | 结算生成订单 |
| `analytics-service` | 事件 `CartItemAdded/Removed` | 行为分析 |
| `recommendation-service` | REST API `GET /api/cart/items` | 基于购物车推荐 |

---

## 配置映射

| 配置项 | 文件路径 | 作用 | 默认值 |
|--------|---------|------|--------|
| `CART_MAX_ITEMS` | `.env` | 购物车最大商品数 | `99` |
| `CART_EXPIRE_DAYS` | `.env` | 匿名购物车过期天数 | `30` |
| `PRICE_CALC_MODE` | `config/cart.yaml` | 价格计算模式（`cent`/`decimal`） | `cent` |
| `STOCK_CHECK_TIMEOUT` | `config/cart.yaml` | 库存校验超时(ms) | `3000` |
| `MERGE_STRATEGY` | `config/cart.yaml` | 登录合并策略（`max`/`sum`/`replace`） | `max` |

---

## 技术栈信息

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | Vue 3 + Pinia | 购物车状态管理用 Pinia store |
| 后端 | Node.js + Express | RESTful API |
| 缓存 | Redis | 购物车数据 + 库存预扣 |
| 消息 | RabbitMQ | 结算事件推送 |
| 数据库 | PostgreSQL | 持久化购物车（登录用户） |

---

## 搜索策略

需要搜索购物车相关代码时：

```
1. 前端代码: src/cart/ 目录
2. 后端 API: src/api/cart/ 目录
3. 数据模型: src/models/Cart*.ts
4. 测试: tests/cart/ 目录
5. 配置: config/cart.yaml
```

---

> 📌 **这只是示例**。你的域专家应该包含你项目的真实模块知识。
> 使用 `#app-skill-wizard` 可以快速为你的模块生成类似的域专家。
