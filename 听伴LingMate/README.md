# LingMate Web

根据 `LingMate_产品设计文档.md` 与 Pencil 设计稿实现的全栈 Web 原型。

## 目录结构

- `frontend`：Vue 3 + Vite 前端
- `backend`：FastAPI 后端

## 启动方式

### 1. 启动后端

```bash
cd backend
. .venv/bin/activate
uvicorn app.main:app --reload
```

默认地址：`http://127.0.0.1:8000`

### 2. 启动前端

```bash
cd frontend
npm run dev
```

默认地址：`http://127.0.0.1:5173`

前端默认请求 `http://127.0.0.1:8000/api`。如果需要修改，可通过 `VITE_API_BASE` 环境变量覆盖。

## 已实现页面

- 首页 / 内容导入
- AI 分析页
- 八模块学习工作台
- 学习报告 / 复习页

## 后端接口

- `GET /api/home`
- `POST /api/import`
- `GET /api/lessons/{lesson_id}/analysis`
- `POST /api/lessons/{lesson_id}/start`
- `GET /api/lessons/{lesson_id}/workspace`
- `POST /api/lessons/{lesson_id}/modules/{module_key}/coach`
- `POST /api/lessons/{lesson_id}/modules/{module_key}/complete`
- `GET /api/lessons/{lesson_id}/report`
- `GET /api/review`
