import asyncio
import sys
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_test():
    url = "http://localhost:8000/sse"
    logger.info(f"Connecting to MCP Server at {url}...")

    try:
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                logger.info("Connected via SSE. Initializing...")
                await session.initialize()
                
                # List tools to verify connection
                tools_result = await session.list_tools()
                tool_names = [t.name for t in tools_result.tools]
                logger.info(f"Available tools: {tool_names}")
                
                collection_name = "test_e2e_collection"
                
                # 1. Cleanup before start (best effort)
                try:
                    logger.info(f"Cleaning up potentially existing collection '{collection_name}'...")
                    await session.call_tool("chroma_delete_collection", {"collection_name": collection_name})
                    logger.info("Previous collection deleted.")
                except Exception:
                    # Ignore error if collection doesn't exist
                    pass

                # 2. Create Collection
                logger.info(f"Creating collection '{collection_name}'...")
                await session.call_tool("chroma_create_collection", {
                    "collection_name": collection_name,
                    "metadata": {"source": "e2e_test_script"}
                })
                logger.info("Collection created.")

                # 3. Add Documents
                documents = [
                    "Machine learning is a field of inquiry devoted to understanding and building methods that 'learn'.",
                    "Chroma is an open-source vector database.",
                    "Python is a high-level, general-purpose programming language."
                ]
                ids = ["doc1", "doc2", "doc3"]
                metadatas = [{"tag": "ml"}, {"tag": "db"}, {"tag": "lang"}]
                
                logger.info(f"Adding {len(documents)} documents...")
                add_result = await session.call_tool("chroma_add_documents", {
                    "collection_name": collection_name,
                    "documents": documents,
                    "ids": ids,
                    "metadatas": metadatas
                })
                logger.info(f"Add result: {add_result}")

                # 4. Verify Count
                logger.info("Verifying document count...")
                count_result = await session.call_tool("chroma_get_collection_count", {
                    "collection_name": collection_name
                })
                # Note: Return value format depends on tool implementation. 
                # Based on server.py, it returns an int directly if using FastMCP simplified return, 
                # but via MCP protocol it comes wrapped in CallToolResult.
                # However, session.call_tool usually returns CallToolResult object.
                # Let's inspect the result content.
                logger.info(f"Count result: {count_result}")
                
                # 5. Semantic Search
                query = "vector db"
                logger.info(f"Querying for '{query}'...")
                query_result = await session.call_tool("chroma_query_documents", {
                    "collection_name": collection_name,
                    "query_texts": [query],
                    "n_results": 1
                })
                
                # The result.content is a list of Content objects (TextContent or ImageContent)
                # We need to parse the JSON string in the text content
                import json
                
                # Helper to extract text from result
                def get_text_content(result):
                    if hasattr(result, 'content') and result.content:
                        return result.content[0].text
                    return str(result)

                query_json_str = get_text_content(query_result)
                try:
                    # Chroma query result is a dict structure
                    # FastMCP tools might return the dict directly, but over wire it's text.
                    # If the tool implementation returns a Dict, FastMCP serializes it to JSON text.
                    data = json.loads(query_json_str)
                    logger.info(f"Query data: {json.dumps(data, indent=2)}")
                    
                    # Validation
                    retrieved_ids = data.get('ids', [[]])[0]
                    if "doc2" in retrieved_ids:
                         logger.info("SUCCESS: Correctly retrieved 'doc2' (Chroma doc) for query 'vector db'.")
                    else:
                         logger.error(f"FAILURE: Expected 'doc2' in results, got {retrieved_ids}")
                         sys.exit(1)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON response: {query_json_str}")
                    sys.exit(1)

                # 6. Get Document by ID
                logger.info("Retrieving doc1 by ID...")
                get_result = await session.call_tool("chroma_get_documents", {
                    "collection_name": collection_name,
                    "ids": ["doc1"]
                })
                get_data = json.loads(get_text_content(get_result))
                if get_data['ids'][0] == "doc1":
                    logger.info("SUCCESS: Verified doc1 retrieval.")
                else:
                    logger.error("FAILURE: Could not retrieve doc1.")

                # 7. Cleanup
                logger.info("Cleaning up...")
                await session.call_tool("chroma_delete_collection", {"collection_name": collection_name})
                logger.info("Collection deleted.")
                
                logger.info("E2E Test Completed Successfully!")

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_test())