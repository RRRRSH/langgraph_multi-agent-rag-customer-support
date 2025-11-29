# 嵌入 API 配置指南

## 问题
api2d.net 服务不支持 OpenAI 嵌入模型。这在专注于文本生成但未实现嵌入端点的 API 代理服务中很常见。

## 解决方案选项

### 选项 1：使用官方 OpenAI API 进行嵌入（推荐）

1. **获取官方 OpenAI API 密钥：**
   - 访问 https://platform.openai.com/api-keys
   - 创建一个新的 API 密钥

2. **更新您的 .env 文件：**
   ```bash
   # 保留 api2d.net 用于文本生成
   OPENAI_BASE_URL=https://openai.api2d.net/v1
   OPENAI_API_KEY=fk217050-KDsZ6DATB3qMgwe

   # 添加官方 OpenAI 用于嵌入
   EMBEDDING_API_KEY=sk-your-official-openai-api-key-here
   EMBEDDING_BASE_URL=https://api.openai.com/v1
   ```

3. **系统现在将使用：**
   - api2d.net 用于文本生成（GPT 模型）
   - 官方 OpenAI 用于嵌入

### 选项 2：使用不同的 API 提供商

一些支持嵌入的替代方案：
- **Together.ai** - 支持各种嵌入模型
- **Replicate** - 具有嵌入模型选项
- **Hugging Face Inference API** - 各种嵌入模型
- **本地嵌入模型** - 使用 sentence-transformers

### 选项 3：跳过嵌入生成（临时）

如果您想测试系统的其他部分：

1. 在 .env 中设置 `RECREATE_COLLECTIONS=False`
2. 系统将跳过嵌入生成并使用现有集合

## 成本考虑

官方 OpenAI 嵌入成本：
- text-embedding-3-small: 每 100 万个 token $0.02
- text-embedding-3-large: 每 100 万个 token $0.13
- text-embedding-ada-002: 每 100 万个 token $0.10

对于典型的 FAQ 数据，这花费很少（大多数数据集低于 1 美元）。

## 下一步

1. 选择上面的首选选项
2. 相应地更新您的 .env 文件
3. 运行嵌入测试：`poetry run python test_embedding.py`
4. 如果成功，运行向量化程序：`poetry run python vectorizer/app/main.py`

## 更新的文件

以下文件已修改以支持单独的嵌入 API 配置：
- `.env` - 添加了 EMBEDDING_API_KEY 和 EMBEDDING_BASE_URL
- `vectorizer/app/core/settings.py` - 添加了嵌入 API 设置
- `vectorizer/app/vectordb/vectordb.py` - 使用嵌入 API 配置
- `vectorizer/app/embeddings/embedding_generator.py` - 使用嵌入 API 配置
