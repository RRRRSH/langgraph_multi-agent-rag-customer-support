# 多智能体 RAG 客户支持系统 - 人机回环 (HITL) 计划

## 当前系统分析

基于代码审查，以下是系统当前的工作方式：

1.  **入口点 (`main.py`)**:
    *   系统首先确保 SQLite 数据库 (`travel2.sqlite`) 存在。
    *   它生成并保存 LangGraph 工作流的可视化。
    *   在配置中设置唯一的会话 `thread_id` 和固定的 `passenger_id`。
    *   它进入一个无限循环，从命令行读取用户输入 (`input("User: ")`)。
    *   用户输入由 `multi_agentic_graph`（在 `graph.py` 中定义）使用 `graph.stream()` 处理。

2.  **图执行 (`graph.py`)**:
    *   图使用 `langgraph.checkpoint.MemorySaver`，并在敏感工具节点（例如 `update_flight_sensitive_tools`）上设置了 `interrupt_before`。
    *   当发生中断时（在执行敏感工具之前），图执行暂停。
    *   `main.py` 循环通过检查 `snapshot.next`（来自 `graph.get_state()`）是否不为空来检测此暂停状态。

3.  **人机回环交互 (`main.py`)**:
    *   检测到中断后，`main.py` 手动向用户显示提示：`input("\nDo you approve of the above actions? Type `y` to continue; otherwise, explain your requested changes.\n\n")`。
    *   根据用户的响应：
        *   如果用户输入 `y`，`main.py` 调用 `graph.invoke(None, config)` 以继续图执行。
        *   如果用户提供任何其他输入（反馈/拒绝），`main.py` 创建一个包含用户反馈的 `ToolMessage` 并使用此消息调用 `graph.invoke()`。然后，触发中断的助手可以访问此消息。

4.  **状态和内存**:
    *   `MemorySaver` 检查点将对话状态（消息、`user_info`、`dialog_state`）存储在内存中，以 `thread_id` 为键。
    *   这允许对话在同一会话中的多个轮次之间持久存在（只要进程在运行）。

## 建议的 HITL 增强功能

为了改进当前的 HITL 机制，我们可以进行以下更改：

1.  **将 HITL 逻辑重构到图中**:
    *   `main.py` 中当前的 HITL 循环将 CLI 界面与 HITL 逻辑紧密耦合。这使得在其他上下文（例如 Web API）中重用图变得困难。
    *   我们可以使用专用的“人机回环”节点将 HITL 逻辑移动到图本身中。此节点将负责暂停执行并等待外部输入。
    *   图将具有处理批准和拒绝的清晰路径，使流程更加明确和易于管理。

2.  **标准化中断处理**:
    *   目前，图仅在敏感工具节点 *之前* 中断。我们可以通过创建一个通用的“请求批准”机制来标准化这一点。
    *   专用助手（如 `flight_booking_assistant`）在需要人工确认时将调用新的 `RequestApproval` 工具。
    *   图的条件路由将检测对 `RequestApproval` 的调用并路由到新的 HITL 节点。

3.  **实现 HITL 节点**:
    *   HITL 节点将是一个无状态函数，向外界发出需要人工输入的信号。
    *   它不会阻塞（像 `input()` 那样），而是更新 `State` 以指示批准处于挂起状态，可能会存储请求的详细信息和 `tool_call_id`。
    *   图执行将在此节点暂停。

4.  **修改接口层 (`main.py`)**:
    *   需要更新 `main.py`（或任何其他接口，如 Web API 处理程序）以处理此新状态。
    *   在每次 `graph.stream()` 调用之后，它将检查最终状态。
    *   如果状态指示人工批准处于挂起状态（例如，通过检查 `State` 中的新字段如 `approval_pending: bool` 或查看当前 `dialog_state` 是否为 "waiting_for_approval"），它将向人类用户显示请求。
    *   用户的响应（批准或反馈）随后将使用 `graph.invoke()` 反馈到图中，类似于当前的方法，但使用标准化的 `ProvideApproval` 工具或特定的消息格式。

5.  **重构的好处**:
    *   **解耦**: 代理的核心逻辑和 HITL 机制与特定接口（CLI、Web 等）分离。
    *   **清晰**: 图定义明确显示了可能发生人工干预的地方。
    *   **可重用性**: 同一个图可以在不同的环境中使用，并以不同的方式处理人工交互。
    *   **可维护性**: 对 HITL 流程的更改只需在图和接口层中进行，而不是分散在 `main.py` 的循环中。

这种重构的方法将使系统更加健壮，并适应未来的集成，同时保持人机回环功能的完整性，并可能使其更加复杂。
