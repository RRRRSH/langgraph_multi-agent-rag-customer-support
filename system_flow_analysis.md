# 系统流程分析

本文档提供了系统启动过程和执行流程的技术分析。

## 1. 系统启动 (`main.py`)

当通过 `poetry run python ./customer_support_chat/app/main.py` 启动系统时，会发生以下序列：

*   **数据库准备：** `download_and_prepare_db()` 函数确保 SQLite 数据库 (`travel2.sqlite`) 存在于 `customer_support_chat/data/` 目录中。如果缺失，它会从预定义的 URL 下载。它还会更新数据库中的日期字段以反映当前时间。
*   **图可视化：** 系统生成 LangGraph 工作流的可视化表示，并将其保存为 `graphs/multi-agent-rag-system-graph.png`。
*   **会话初始化：**
    *   在配置中设置唯一的会话 `thread_id` 和固定的 `passenger_id`。
    *   `thread_id`: 由 `langgraph.checkpoint.MemorySaver` 使用，用于在内存中持久化对话状态。这使得在同一会话中可以进行多轮对话。
    *   `passenger_id`: 硬编码为 `"5102 899977"`。此 ID 对于从 SQLite 数据库检索特定于用户的信息（特别是航班预订）至关重要。目前，系统就像所有用户都是这一个乘客一样运行。
*   **主交互循环：**
    *   系统进入一个无限的 `while True:` 循环。
    *   它使用 `input("User: ")` 提示用户输入。
    *   如果用户输入 `quit`、`exit` 或 `q`，循环中断，程序退出。
    *   否则，用户的输入由 `multi_agentic_graph` 处理。

## 2. 图执行 (`graph.py`, `state.py`)

`multi_agentic_graph` (`langgraph.graph.StateGraph` 的实例) 定义了工作流。该图的状态由 `State` TypedDict (`customer_support_chat/app/core/state.py`) 管理，其中包括 `messages`（对话历史）、`user_info`（检索到的航班详情）和 `dialog_state`（当前助手上下文）。

*   **初始状态：** 执行总是从 `fetch_user_info` 节点开始。
*   **`fetch_user_info` 节点：** 此节点使用配置中的 `passenger_id` 调用 `fetch_user_flight_information`（来自 `tools.flights`）以检索用户当前的航班预订。此信息存储在 `State` 的 `user_info` 键下。
*   **主助手：** 获取用户信息后，控制权传递给 `primary_assistant` 节点。此助手分析用户的输入和当前的 `State`（包括 `user_info`）。
*   **路由逻辑：** `primary_assistant` 使用其 LLM 和工具来确定下一步：
    *   如果它可以直接处理请求（例如，使用 RAG 回答一般问题），它会与其工具（如 `primary_assistant_tools` 节点）交互并响应。
    *   如果请求需要专门的任务（航班更新、汽车租赁、酒店预订、短途旅行），它会调用相应的 "To..." 工具（例如 `ToFlightBookingAssistant`）。这向图发出信号以委派任务。
*   **专用助手：** 如果发生委派，图会路由到 `enter_...` 节点（例如 `enter_update_flight`），该节点为专用助手（例如 `update_flight`）设置上下文。然后此助手接管，与其特定工具交互。
*   **工具执行：**
    *   助手通过生成 `tool_calls` 来调用工具。
    *   图将这些调用路由到相应的 `..._tools` 节点（例如 `update_flight_safe_tools`、`update_flight_sensitive_tools`）。
    *   **安全工具：** 被视为安全的工具（例如 `search_flights`、`search_hotels`）直接执行。它们的结果反馈给调用助手。
    *   **敏感工具：** 修改数据或执行关键操作的工具（例如 `update_ticket_to_new_flight`、`cancel_ticket`）被标记为敏感。
*   **针对敏感操作的人机回环 (HITL)：**
    *   当即将执行敏感工具时，图配置为 `interrupt_before=["..._sensitive_tools"]`。
    *   这导致 `graph.stream()` 在敏感工具节点运行 *之前* 暂停。
    *   控制权返回给 `main.py`。

## 3. 人类交互 (`main.py`)

`main.py` 脚本处理由中断引起的暂停：

*   **中断检测：** 在 `graph.stream()` 之后，`main.py` 调用 `multi_agentic_graph.get_state(config)`。如果返回的 `snapshot.next` 不为空，则表示中断（挂起的敏感操作）。
*   **用户提示：** `main.py` 向用户显示提示，显示挂起的操作并请求批准：`input("\nDo you approve of the above actions? Type `y` to continue; otherwise, explain your requested changes.\n\n")`。
*   **批准处理：**
    *   如果用户输入 `y`，`main.py` 调用 `multi_agentic_graph.invoke(None, config)`。这告诉图恢复执行并继续执行敏感工具。
    *   如果用户提供任何其他输入，`main.py` 假定它是反馈/拒绝。它构造一个包含用户输入和挂起操作的 `tool_call_id` 的 `ToolMessage`。然后它使用此消息调用 `multi_agentic_graph.invoke()`。图将此消息路由回请求敏感操作的助手，允许它根据用户的反馈调整其行为。
*   **继续：** 处理中断后，`main.py` 继续其循环，处理由恢复的图执行生成的任何新消息，然后等待下一个用户输入。

这种 用户输入 -> 图处理 -> 潜在 HITL 暂停 -> 用户响应 -> 图继续 的循环构成了系统的核心交互循环。

## 4. 数据源

系统依赖于两个主要数据源：

*   **Qdrant 向量数据库：** 用于检索增强生成 (RAG)。助手使用搜索工具（例如 `search_flights`）查询此数据库以获取相关信息以增强其响应。Qdrant 中的数据源自 SQLite 数据库和其他来源，由 `vectorizer` 模块处理和嵌入。
*   **SQLite (`travel2.sqlite`)：** 存储结构化数据，如用户机票、航班详情、预订。像 `fetch_user_flight_information`、`update_ticket_to_new_flight` 和 `cancel_ticket` 这样的工具直接查询或修改此数据库。配置中的 `passenger_id` 对于这些数据库交互至关重要，以确保（当前硬编码的）用户的数据隔离。
