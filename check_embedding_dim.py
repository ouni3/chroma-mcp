import os
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# 模拟 Docker Compose 中的环境变量配置
os.environ["CHROMA_OPENAI_API_KEY"] = "sk-123456" # 随意的值，取决于代理是否检查
os.environ["CHROMA_OPENAI_API_BASE"] = "http://192.168.0.104:8000/v1" 
os.environ["CHROMA_OPENAI_MODEL_NAME"] = "gemini-embedding-001"

def get_embedding_function():
    api_key = os.environ["CHROMA_OPENAI_API_KEY"]
    api_base = os.environ["CHROMA_OPENAI_API_BASE"]
    model_name = os.environ["CHROMA_OPENAI_MODEL_NAME"]
    
    print(f"Testing embedding with:")
    print(f"  API Base: {api_base}")
    print(f"  Model: {model_name}")

    return OpenAIEmbeddingFunction(
        api_key=api_key,
        api_base=api_base,
        model_name=model_name
    )

try:
    ef = get_embedding_function()
    # 嵌入一个简单文本
    embeddings = ef(["hello world"])
    
    if embeddings:
        dim = len(embeddings[0])
        print(f"\nResulting Dimension: {dim}")
    else:
        print("No embeddings returned.")

except Exception as e:
    print(f"Error generating embedding: {e}")