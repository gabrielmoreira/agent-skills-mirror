# 架构设计文档

## 1. 整体架构图

TrailSnap 采用典型的前后端分离架构，由前端展示层、后端服务层和数据存储层组成。

```mermaid
flowchart TD
    User[用户浏览器] -->|HTTP/HTTPS| FE[前端应用 (Vue 3 + Vite)]

    subgraph Frontend_Layer[前端展示层]
      FE -->|Axios / REST| API8000[后端服务 (FastAPI, :8000)]
      FE -->|Pinia| Store[全局状态管理]
      FE -->|ElementPlus| UI[UI组件库]
    end

    subgraph Backend_Layer[后端服务层]
      API8000 --> Routers[API Routers]
      Routers --> Services[业务服务层]
      Services -->|ORM| DBConn[SQLAlchemy]
      Services -->|文件操作| FS[文件系统]
      Services -->|异步任务| TM[TaskManager]
      TM -->|HTTP 调用| AI8001[AI 微服务 (FastAPI, :8001)]
    end

    subgraph AI_Service[AI 微服务]
      AI8001 --> OCR[PaddleOCR]
      AI8001 --> Face[InsightFace]
      AI8001 --> OD[对象检测]
      AI8001 --> Ticket[车票识别(YOLO+OCR)]
    end

    subgraph Data_Layer[数据层]
      DBConn --> DB[(PostgreSQL)]
      FS --> Storage[本地/挂载存储]
    end
```

## 2. 技术选型及版本

### 2.1 前端技术栈

### 2.2 后端技术栈
- **编程语言**: Python 3.12+
- **Web 框架**: FastAPI 0.122.0
- **ASGI 服务器**: Uvicorn 0.38.0
- **ORM**: SQLAlchemy 2.0.44
- **数据库迁移**: Alembic 1.17.2
- **数据库驱动**: psycopg2 (PostgreSQL)
- **任务/异步**: APScheduler、`aiohttp`
- **AI/CV (AI 微服务)**:
  - PaddleOCR ==3.3.2
  - PaddlePaddle-GPU `==3.2.0`（可选 GPU）
  - OpenCV `opencv-python-headless >=4.9.0`
  - Torch `>=2.0.0`、TorchVision `>=0.15.0`（部分模型可用）
  - InsightFace（人脸）
- **日志**: 自定义 JSON 队列日志 + 按日容量滚动（server 与 ai 均内置）

### 2.3 数据库
- **PostgreSQL**: 关系型数据库，存储用户、相册、照片元数据、系统设置等。

## 3. 目录结构与模块说明

### 3.1 根目录
- `package/server`: 后端服务代码
- `package/website`: 前端应用代码
- `doc`: 项目文档

### 3.2 后端结构 (`package/server`)
- **app/**: 核心应用代码
  - `api/`: API 路由定义 (EndPoints)，按功能模块划分 (user, album, photo, etc.)
  - `core/`: 核心配置与工具 (Logger, Config)
  - `crud/`: 数据库 CRUD 操作封装
  - `db/`: 数据库模型 (Models) 与会话管理 (Session)
  - `schemas/`: Pydantic 数据模型 (Request/Response schemas)
  - `service/`: 复杂业务逻辑与后台服务 (TaskManager, Indexer, Storage)
  - `utils/`: 通用工具函数 (Exif解析, 文件名处理)
- **railway/**: 铁路相关功能模块 (独立的数据处理与同步逻辑)
- **yolo_ocr/**: OCR 与票据识别相关模型与脚本
- **main.py**: 应用入口，路由挂载、CORS、中间件与端口配置（默认 `:8000`）

### 3.3 前端结构 (`package/website`)
- **src/**: 源代码
  - `api/`: 后端接口封装
  - `assets/`: 静态资源 (图片, CSS)
  - `components/`: 通用 Vue 组件 (PhotoGallery, TrainTicket, etc.)
  - `composables/`: 组合式函数 (Hooks)
  - `layouts/`: 页面布局组件
  - `router/`: 路由配置
  - `stores/`: Pinia 状态管理仓库
  - `types/`: TypeScript 类型定义
  - `views/`: 页面视图 (Pages)
  - `package.json`: 依赖与版本管理，内含脚本 `dev/build/preview`

### 3.4 AI 微服务结构 (`package/ai`)
- **app/main.py**: AI 服务入口（默认 `:8001`），挂载 `ocr/face/object-detection/tickets` 路由
- **app/services/**: 模型服务（`ocr_service.py`、`face_service.py`、`model_manager.py` 懒加载与资源释放）
- **app/core/logger.py**: JSON 队列日志，按日容量滚动
- **requirements.txt**: 依赖与版本约束（PaddleOCR、PaddlePaddle-GPU、Torch、OpenCV 等）

## 4. 关键交互与调用链

```mermaid
sequenceDiagram
  participant FE as 前端 (Vue)
  participant S as 后端服务 :8000
  participant AI as AI 微服务 :8001
  participant DB as PostgreSQL
  participant FS as 文件系统

  FE->>S: GET /api/ocr?photo_id=...
  S->>DB: 查询 ocr_results
  DB-->>S: 归一化多边形/文本
  S-->>FE: JSON 响应

  S->>AI: POST /ocr/predict (异步任务)
  AI->>AI: PaddleOCR 推理
  AI-->>S: rec_texts/rec_scores/rec_polys
  S->>DB: 写入 ocr_results（坐标归一化 0~1）

  FE->>S: 媒体操作/相册管理
  S->>FS: 读取/写入媒体文件
  S->>DB: 写入/查询元数据
```
