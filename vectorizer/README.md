# 向量化模块 (Vectorizer Module)

本模块负责处理嵌入和向量数据库操作。以下部分概述了该模块的主要组件，该模块的设计考虑了灵活性，利用设计模式以便轻松适应各种向量数据库。该架构支持不同数据库解决方案的直接集成，确保可扩展性和可维护性。通过抽象嵌入生成和文档索引逻辑，可以无缝扩展或修改此模块以适应特定用例或数据库后端，而无需更改核心功能。

此外，该模块被设计为作为一个 Python 包运行，允许将其托管在私有存储库中并集成到自动化流程中。这意味着它可以被 Airflow 或其他管道自动化系统等工具利用，作为更大工作流的一部分实现高效的嵌入和向量数据库操作。

## 结构
```
vectorizer
├── README.md
├── __init__.py
└── app
    ├── core
    │   ├── __init__.py
    │   ├── logger.py
    │   └── settings.py
    ├── embeddings
    │   ├── __init__.py
    │   └── embedding_generator.py
    ├── main.py
    └── vectordb
        ├── __init__.py
        ├── chunkenizer.py
        ├── utils.py
        └── vectordb.py
```

### 1. `embedding_generator.py`

此文件使用 OpenAI API 为输入内容生成嵌入。它处理单个字符串和字符串列表作为输入。

- **函数: `generate_embedding`**
  - **输入:** `Union[str, List[str]]` - 接受单个字符串或字符串列表。
  - **输出:** 返回浮点数列表（嵌入）或浮点数列表的列表（如果提供了字符串列表）。

### 2. `chunkenizer.py`

此文件使用 LangChain 的 `RecursiveCharacterTextSplitter` 处理将大文本拆分为较小的块。

- **函数: `recursive_character_splitting`**
  - **输入:** 文本、块大小和块重叠。
  - **输出:** 返回文本块，用于进一步处理或嵌入生成。

### 3. `vectordb.py`

这是向量化模块的核心组件，处理与 Qdrant 的交互以存储和检索向量嵌入。它还管理 SQLite 数据库连接和内容格式化。

- **类: `VectorDB`**
  - **方法:**
    - `__init__`: 使用表名、集合名初始化向量数据库，并可选择创建集合。
    - `connect_to_qdrant`: 使用提供的设置连接到 Qdrant 客户端。
    - `create_or_clear_collection`: 创建新集合或清除现有集合。
    - `format_content`: 为不同集合类型（汽车租赁、航班、酒店等）格式化内容。
    - `generate_embedding_async`: 使用 OpenAI API 异步生成嵌入。
    - `create_embeddings_async`: 处理各种内容类型的嵌入创建的主要函数。
    - `index_regular_docs`: 将常规文档从 SQLite 索引到 Qdrant。
    - `index_faq_docs`: 处理 FAQ 文档并将其索引到 Qdrant。
    - `create_embeddings`: 运行生成嵌入的异步过程。
    - `search`: 在 Qdrant 集合上执行向量搜索。

- **异步处理:**
  - 使用 `asyncio` 和 `aiohttp` 处理文档的批处理并高效地与 OpenAI API 交互。
  - **批处理:** 块被分批处理以避免超过速率限制。

### 4. `main.py`

此文件负责创建多个集合（汽车租赁、旅行、航班、酒店和 FAQ）并将其索引到 Qdrant 中。

- **函数: `create_collections`**
  - 为每个表和集合初始化向量数据库，生成嵌入，并将其存储在 Qdrant 中。

### 5. `utils.py`

包含支持模块中各种操作的实用函数。

## 如何使用

1. **创建嵌入**:
   - 运行 `main.py` 以初始化各种集合的向量数据库并为它们生成嵌入。
   - 示例命令: `python main.py`

2. **搜索**:
   - 使用 `vectordb.py` 中的 `search` 函数对 Qdrant 中索引的嵌入执行搜索。

## 注意事项

- 在运行嵌入生成之前，请确保在环境变量或通过设置文件设置了 OpenAI API 密钥。
- `RecursiveCharacterTextSplitter` 用于将大段文本拆分为可管理的块，以确保有效的嵌入生成。
