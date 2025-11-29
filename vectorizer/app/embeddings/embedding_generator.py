from langchain_openai import OpenAIEmbeddings
from vectorizer.app.core.settings import get_settings
from vectorizer.app.core.logger import logger
from typing import Union, List
import requests

settings = get_settings()

# Configure OpenAI embeddings with embedding-specific configuration
if settings.EMBEDDING_BASE_URL:
    embeddings = OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        openai_api_key=settings.EMBEDDING_API_KEY,
        openai_api_base=settings.EMBEDDING_BASE_URL
    )
else:
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.EMBEDDING_API_KEY
    )

def generate_embedding(content: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """
    Generate embeddings using either API or local model based on configuration
    """
    # Check if local embeddings are enabled
    if settings.USE_LOCAL_EMBEDDINGS:
        logger.info("Using local embeddings")
        try:
            from .local_embedding_generator import generate_local_embedding
            return generate_local_embedding(content)
        except Exception as e:
            logger.error(f"Local embedding failed: {str(e)}")
            logger.info("Falling back to API embeddings...")
    
    # Use API embeddings
    logger.info(f"Using API embeddings. Content type: {type(content)}, Content: {content}")
    try:
        # 【核心修改】直接调用 API，绕过 LangChain 的封装问题
        if settings.EMBEDDING_BASE_URL:
            # 构造请求 URL
            base_url = settings.EMBEDDING_BASE_URL.rstrip('/')
            if not base_url.endswith("/embeddings"):
                url = f"{base_url}/embeddings"
            else:
                url = base_url
            
            headers = {
                "Authorization": f"Bearer {settings.EMBEDDING_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # 阿里云 DashScope 兼容接口通常接受标准的 OpenAI 格式
            payload = {
                "model": settings.EMBEDDING_MODEL,
                "input": content
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"API Error {response.status_code}: {response.text}")
            
            result = response.json()
            
            if isinstance(content, str):
                return result["data"][0]["embedding"]
            else:
                return [item["embedding"] for item in result["data"]]
                
        else:
            # 如果没有配置 Base URL，还是尝试用 LangChain (虽然你的情况应该都有 Base URL)
            if isinstance(content, str):
                return embeddings.embed_query(content)
            elif isinstance(content, list):
                return embeddings.embed_documents(content)
            else:
                raise ValueError("Content must be either a string or a list of strings")
                
    except Exception as e:
        logger.error(f"API embedding failed: {str(e)}")
        
        # If API fails and local embeddings aren't enabled, try to enable them
        if not settings.USE_LOCAL_EMBEDDINGS:
            logger.info("API failed, attempting to use local embeddings as fallback...")
            try:
                from .local_embedding_generator import generate_local_embedding
                return generate_local_embedding(content)
            except Exception as local_e:
                logger.error(f"Local embedding fallback also failed: {str(local_e)}")
                raise Exception(f"Both API and local embeddings failed. API error: {str(e)}, Local error: {str(local_e)}")
        else:
            raise
