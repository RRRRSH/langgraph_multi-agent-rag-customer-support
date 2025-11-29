# `multi-agent-rag-customer-support-main` 的 Qwen 代码上下文

## 项目概览

本项目实现了一个用于客户支持的 **多智能体检索增强生成 (RAG) 系统**，专门针对旅行场景（例如瑞士航空）。它使用 Python 构建，并使用了 **LangChain** 和 **LangGraph** 等关键库。

核心思想是拥有一个主助手来处理一般查询，并将更复杂、专门的任务（如预订航班、汽车、酒店或短途旅行）路由到专用的子助手。这种架构增强了模块化、可扩展性，并允许进行细粒度的控制，特别是对于需要用户确认的敏感操作。

**主要特点：**
*   **多智能体架构：** 利用 LangGraph 定义具有主助手和专用助手的有状态工作流。
*   **RAG 集成：** 采用 Qdrant 向量数据库高效检索相关信息（例如航班详情、政策）以增强 LLM 的响应。
*   **安全机制：** 实施“敏感工具”，在执行前暂停工作流并需要明确的用户批准。
*   **可观测性：** 集成 LangSmith 以跟踪和监控智能体交互。
*   **模块化设计：** 代码结构化为不同的模块（`customer_support_chat`、`vectorizer`），以便清晰地分离关注点。

## 项目结构

```
E:\multi-agent-rag-customer-support-main\
├── .dev.env                # 环境变量模板
├── .gitignore
├── docker-compose.yml      # 定义 Qdrant 等服务
├── Dockerfile
├── Makefile                # 定义常用项目命令
├── poetry.lock             # Poetry 依赖锁定文件
├── pyproject.toml          # 项目元数据和依赖项 (Poetry)
├── README.md               # 主项目文档
├── .vscode\                # VS Code 配置
│   └── launch.json
├── customer_support_chat\  # 主应用程序模块
│   ├── README.md           # 详细模块文档
│   ├── __init__.py
│   ├── app\                # 核心应用程序逻辑
│   │   ├── __init__.py
│   │   ├── core\           # 核心组件（状态、设置、日志记录器）
│   │   ├── data\           # （可能）本地数据文件
│   │   ├── graph.py        # 定义 LangGraph 工作流
│   │   ├── main.py         # 聊天应用程序的主要入口点
│   │   └── services\       # 助手、工具、实用程序、向量数据库接口
│   └── data\               # 本地 SQLite 数据库 (travel2.sqlite)
├── graphs\                 # 图形可视化的输出目录
│   └── multi-agent-rag-system-graph.png
├── images\                 # 文档图片
└── vectorizer\             # 用于生成嵌入和填充 Qdrant 的模块
    ├── README.md           # 详细模块文档
    ├── __init__.py
    └── app\                # 核心向量化逻辑
        ├── __init__.py
        ├── core\           # 核心组件（日志记录器、设置）
        ├── embeddings\     # 嵌入生成逻辑
        ├── main.py         # 向量化过程的入口点
        └── vectordb\       # Qdrant 数据库交互逻辑
```

## 主要技术

*   **语言：** Python 3.12+
*   **包管理器：** Poetry
*   **核心框架/库：**
    *   `langgraph`: 用于构建多智能体状态机/图。
    *   `langchain`: 用于 LLM 交互、提示和工具。
    *   `langchain-openai`: 用于 OpenAI LLM 和嵌入集成。
    *   `qdrant-client`: 用于与 Qdrant 向量数据库交互。
    *   **向量数据库：** Qdrant（可以通过 Docker 本地运行）
    *   **数据源：** 包含旅行相关数据的 SQLite 数据库 (`travel2.sqlite`)。
    *   **可观测性：** LangSmith（可选）
    *   **环境管理：** `python-dotenv`

## 构建和运行

**先决条件：**
*   Python 3.12+
*   Poetry
*   Docker 和 Docker Compose
*   OpenAI API Key
*   LangSmith API Key（可选）

**设置和执行步骤：**

1.  **环境设置：**
    *   复制环境模板：`cp .dev.env .env`
    *   编辑 `.env` 并填写您的 `OPENAI_API_KEY` 和可选的 `LANGCHAIN_API_KEY`。

2.  **安装依赖项：**
    *   运行 `poetry install` 以安装 `pyproject.toml` 中定义的所有 Python 依赖项。

3.  **准备向量数据库 (Qdrant)：**
    *   在后台启动 Qdrant 服务：`docker compose up qdrant -d`
    *   *（可选）* 访问 Qdrant UI：`http://localhost:6333/dashboard#`。

4.  **生成并存储嵌入：**
    *   运行向量化程序以处理数据并填充 Qdrant：`poetry run python vectorizer/app/main.py`

5.  **运行客户支持聊天应用程序：**
    *   启动主聊天应用程序：`poetry run python ./customer_support_chat/app/main.py`
    *   通过命令行与聊天机器人交互。输入 `quit`、`exit` 或 `q` 停止。

## 开发约定

*   **依赖管理：** 依赖项使用 Poetry 管理 (`pyproject.toml`, `poetry.lock`)。
*   **模块化：** 代码分为 `vectorizer` 和 `customer_support_chat` 模块。每个模块都有自己的 `README.md`。
*   **状态管理：** 使用 `langgraph.checkpoint.memory.MemorySaver` 进行跨对话轮次的内存状态持久化。
*   **图定义：** 对话流程在 `customer_support_chat/app/graph.py` 中使用 LangGraph 的 `StateGraph` 定义。
*   **助手：** 专用助手继承自 `customer_support_chat/app/services/assistants/assistant_base.py` 中的基类。
*   **工具：** 工具（LLM 可以调用的函数）定义在 `customer_support_chat/app/services/tools/` 中。
*   **配置：** 应用程序设置通过 `core/settings.py` 中的 Pydantic 模型管理，从环境变量加载。
*   **日志记录：** 使用在 `core/logger.py` 中配置的自定义日志记录器。

## Qwen Added Memories
- 在生成包含多行文本的 Markdown 文件时，直接在 write_file 的 content 参数中使用 '
' 字符串会导致文件内容中出现字面量的 
，而不是实际的换行符。正确的做法是在 Python 字符串中使用实际的换行符（例如，使用三重引号 ''' 或 """ 包裹多行字符串，或在字符串中使用 
 但确保它被解释为换行符而不是字面量）。当需要从包含字面量 
 的文件创建正确格式的文件时，必须使用脚本（如 PowerShell 或 Python）来替换这些字面量。
- 用户希望为当前的多智能体RAG客服系统增加多用户支持功能，包括：1) 允许多个用户同时使用；2) 保存用户的聊天记录；3) 提供一个HTML形式的用户聊天界面。
