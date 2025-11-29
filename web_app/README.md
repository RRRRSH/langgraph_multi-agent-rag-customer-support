# 多智能体 RAG 客户支持 Web 应用程序

此目录包含 FastAPI Web 应用程序，该程序为客户支持系统提供多用户聊天界面。

## 安装

1. 导航到此目录：`cd web_app`
2. 安装依赖项：`poetry install`

## 运行应用程序

1. 确保已安装主项目依赖项并且 Qdrant 服务正在运行。
2. 从此目录运行：`poetry run uvicorn web_app.app.main:app --reload --host 0.0.0.0 --port 8000`
3. 在浏览器中访问应用程序：`http://localhost:8000`