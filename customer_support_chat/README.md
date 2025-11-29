# 客户支持聊天模块
该模块驱动一个客户支持聊天机器人，旨在处理各种工作流程，如航班预订、酒店预订、汽车租赁和短途旅行推荐。它使用设计模式构建，以实现易于维护、可扩展性和对未来变化的适应性。聊天机器人的架构允许采用多助手工作流程，其中每个任务由专门的助手处理，确保流畅的用户体验。

核心组件包括 ```状态管理系统```、用于与不同服务交互的工具，以及用于管理对话的 ```基于动态图的方法```。每个助手都旨在专注于特定任务，允许在不影响整个系统的情况下进行模块化更新和改进。


## 结构
```
customer_support_chat
├── README.md
├── __init__.py
├── app
│   ├── __init__.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── settings.py
│   │   └── state.py
│   ├── data
│   ├── graph.py
│   ├── main.py
│   └── services
│       ├── __init__.py
│       ├── assistants
│       │   ├── __init__.py
│       │   ├── assistant_base.py
│       │   ├── car_rental_assistant.py
│       │   ├── excursion_assistant.py
│       │   ├── flight_booking_assistant.py
│       │   ├── hotel_booking_assistant.py
│       │   └── primary_assistant.py
│       ├── embeddings
│       ├── tools
│       │   ├── __init__.py
│       │   ├── cars.py
│       │   ├── excursions.py
│       │   ├── flights.py
│       │   ├── hotels.py
│       │   └── lookup.py
│       ├── utils.py
│       └── vectordb
│           ├── __init__.py
│           ├── chunkenizer.py
│           ├── utils.py
│           └── vectordb.py
└── data
    ├── travel2.sqlite
    ├── travel2.sqlite.bkp
    ├── travel2.sqlite.bkp.zero
    └── user_test_fetch_data.sql
10 directories, 32 files
```

## 设计
该模块被设计为作为一个 Python 包运行，使其适合集成到更大的平台或自动化框架中，如 Airflow、Kubernetes 或 CI/CD 管道。模块化方法确保特定的助手或工具可以被重用、调整或扩展，以满足不断变化的业务需求。无论您是需要添加新的预订服务、更新交互流程还是引入新的集成，底层架构都支持以最小的努力进行这些更改。


## 客户支持聊天模块概述
customer_support_chat 模块编排了一个多智能体系统，处理各种客户支持任务，如预订航班、汽车租赁、酒店和短途旅行。该系统使用 LangChain 和 LangGraph 构建灵活的工作流程和助手，允许高效的任务委派。每个助手遵循相同的设计模式，使系统具有可扩展性，并易于使用新助手进行扩展。

本节深入探讨系统的主要组件及其用途。

## 主要文件概述
- ```assistant_base.py```
此文件是所有专用助手的基本结构，并实现了策略模式。它提供了一个通用框架，所有助手（如航班预订或汽车租赁）都使用该框架与系统交互。

-   ```Assistant Class```: 管理助手如何处理任务和用户输入的核心逻辑。它确保任务在必要时完成或升级。
-   ```CompleteOrEscalate Tool```: 助手使用此工具来完成当前任务，或者如果需要进一步操作，则将其升级到主助手。
- 此文件充当所有助手逻辑的骨干，确保不同工作流程之间的一致性。

- ```primary_assistant.py```
此文件定义了主助手，它充当主管，将任务委派给专用助手。

- ```Task Delegation Tools```: 像 ToFlightBookingAssistant、ToBookCarRental 等模型有助于根据用户需求将任务路由到专用助手。
- ```primary_assistant_runnable```: 结合主提示和工具来处理一般查询。如果请求涉及专门的任务，它会将其委派给适当的助手。
- 此助手遵循责任链模式，允许无缝委派，而无需向用户公开底层助手结构。

- ```main.py```
此文件充当系统的主要协调者。它设置环境，管理用户输入，并与图交互以执行任务。

- ```Graph Visualization```: 生成图并将其保存为图像，以便进行可视化调试和分析。
- ```Interaction Loop```: 系统进入一个循环，不断监听用户输入，处理它们，并从图中流式传输响应。
- ```Interrupt Handling```: 如果系统需要敏感操作（如修改预订），它会要求用户确认，确保对关键任务的控制。

- ```graph.py```
此文件构建多智能体工作流图，其中每个助手都表示为一个子图。

- ```Node Definitions```: 每个助手都有自己的入口、处理和出口节点，用于管理任务生命周期。
- ```Routing Logic```: 系统根据用户输入和完成任务所需的工具，将任务路由到相关助手。
- ```Primary Assistant```: 处理一般任务，并将特定任务委派给专用助手，如航班预订、汽车租赁、酒店和短途旅行。
- ```Interrupt Management```: 该图包括中断节点，当调用敏感工具（如修改预订）时暂停执行，允许用户批准或拒绝操作。

这种模块化设计允许系统高效处理复杂的工作流程，同时保持灵活性以轻松添加新功能。系统架构使其非常适合与其他工具和助手集成，从而实现可扩展的客户支持自动化。
