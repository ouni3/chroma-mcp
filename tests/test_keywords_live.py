import asyncio
import sys
import logging
import json
import os
from dotenv import load_dotenv

# 1. 强制配置环境变量以连接远程 ChromaDB
os.environ["CHROMA_CLIENT_TYPE"] = "http"
os.environ["CHROMA_HOST"] = "192.168.0.104"
os.environ["CHROMA_PORT"] = "8012"
os.environ["CHROMA_SSL"] = "false"
# 确保使用 OpenAI (Gemini) 嵌入，因为 techChat 是用它生成的
os.environ["CHROMA_OPENAI_API_BASE"] = "http://192.168.0.104:8000/v1" # 假设这是你的 API Base，如果不是请修改
# 注意：如果本地没有配置 API Key，可能会报错。尝试读取本地 .env
load_dotenv()

# 2. 导入本地实现的函数
# 必须在设置环境变量后导入，虽然 server.py 是并在调用时获取 client，但是个好习惯
sys.path.append("src")
from chroma_mcp.server import chroma_generate_keywords

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_local_test():
    collection_name = "techChat"
    logger.info(f"Running LOCAL code, connecting to REMOTE DB ({os.environ['CHROMA_HOST']}:{os.environ['CHROMA_PORT']})...")
    logger.info(f"Target Collection: {collection_name}")

    try:
        # 直接调用本地函数
        keywords = await chroma_generate_keywords(
            collection_name=collection_name,
            n_clusters=10,        # 尝试生成 10 个主题
            top_k_per_cluster=5,  # 每个主题 5 个词
            use_hybrid_mode=True  # 启用混合模式
        )

        logger.info("=== Generated Keywords (Hybrid Mode) ===")
        # Pretty print the list
        print(json.dumps(keywords, indent=2, ensure_ascii=False))
        
        if len(keywords) > 0 and "__NO_DATA_FOUND__" not in keywords:
            logger.info(f"SUCCESS: Generated {len(keywords)} keywords.")
        else:
            logger.warning("Result empty or NO_DATA_FOUND.")

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_local_test())