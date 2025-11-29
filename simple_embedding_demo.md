# 简单嵌入生成演示

此脚本演示如何使用 OpenAI 的 `text-embedding-3-large` 模型生成嵌入。

## 先决条件

1.  Python 3.6+
2.  `openai` Python 库 (`pip install openai`)
3.  设置为环境变量 `OPENAI_API_KEY` 的 OpenAI API 密钥。

## 代码

```python
# simple_embedding_demo.py

import os
from openai import OpenAI

# --- 配置 ---
# 确保设置了 OPENAI_API_KEY 环境变量。
# 您可以在终端中像这样设置它：
# Linux/macOS: export OPENAI_API_KEY='your-api-key-here'
# Windows (命令提示符): set OPENAI_API_KEY=your-api-key-here
# Windows (PowerShell): $env:OPENAI_API_KEY="your-api-key-here"

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

MODEL_NAME = "text-embedding-3-large"
# ----------------------

def generate_embeddings(texts, model=MODEL_NAME):
    """
    使用指定模型为文本列表生成嵌入。

    Args:
        texts (list of str): 要嵌入的文本。
        model (str): 要使用的嵌入模型的名称。

    Returns:
        list: 嵌入向量列表。
    """
    client = OpenAI(api_key=API_KEY)
    
    try:
        response = client.embeddings.create(
            model=model,
            input=texts
        )
        # 从响应中提取嵌入
        embeddings = [item.embedding for item in response.data]
        return embeddings
    except Exception as e:
        print(f"An error occurred: {e}")
        raise # 重新引发异常以进行调试

if __name__ == "__main__":
    print(f"Generating embeddings using model: {MODEL_NAME}")
    
    # 示例文本
    texts_to_embed = [
        "The quick brown fox jumps over the lazy dog.",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Embeddings are a powerful tool in natural language processing."
    ]
    
    try:
        embeddings = generate_embeddings(texts_to_embed)
        
        print(f"\nSuccessfully generated {len(embeddings)} embeddings.")
        print(f"Dimension of the first embedding: {len(embeddings[0])}")
        print(f"First 5 elements of the first embedding: {embeddings[0][:5]}")
        
        # 基本检查：所有嵌入应具有相同的长度
        lengths = [len(e) for e in embeddings]
        if all(l == lengths[0] for l in lengths):
            print(f"All embeddings have consistent dimension: {lengths[0]}")
        else:
             print(f"Warning: Embedding dimensions are inconsistent: {lengths}")

    except Exception as e:
        print(f"Demo failed: {e}")

```

## 如何运行

1.  将上面的代码保存为 `simple_embedding_demo.py`。
2.  打开终端或命令提示符。
3.  设置您的 OpenAI API 密钥：
    ```bash
    export OPENAI_API_KEY='your-actual-openai-api-key-here'
    # 或者在 Windows PowerShell 上：
    # $env:OPENAI_API_KEY="your-actual-openai-api-key-here"
    ```
4.  导航到保存文件的目录。
5.  运行脚本：
    ```bash
    python simple_embedding_demo.py
    ```

## 预期输出（格式）

输出将根据实际生成的嵌入而有所不同，但它应该类似于以下内容：

```
Generating embeddings using model: text-embedding-3-large

Successfully generated 3 embeddings.
Dimension of the first embedding: 3072
First 5 elements of the first embedding: [0.00123, -0.00456, 0.00789, ...]
All embeddings have consistent dimension: 3072
```