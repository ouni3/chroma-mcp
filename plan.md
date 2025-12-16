# 远程部署计划 (192.168.0.104)

## 目标
为 IP 为 `192.168.0.104` 的服务器创建 Docker 部署配置，使 Chroma MCP Server 能够运行并连接到同一台服务器上的 ChromaDB (端口 8012)。

## 拟创建文件

### 1. `docker-compose.remote.yaml`
用于远程服务器的 Docker Compose 配置。

```yaml
services:
  chroma-mcp:
    # 如果需要在远程构建，取消注释 build 部分
    # build: .
    image: chroma-mcp:latest
    container_name: chroma-mcp-server
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      # MCP Server 配置 (SSE 模式)
      - MCP_TRANSPORT=sse
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000

      # Chroma 数据库连接配置
      # 默认连接到宿主机的 192.168.0.104:8012
      - CHROMA_CLIENT_TYPE=http
      - CHROMA_HOST=${CHROMA_HOST:-192.168.0.104}
      - CHROMA_PORT=${CHROMA_PORT:-8012}
      - CHROMA_SSL=${CHROMA_SSL:-false}
      
      # 嵌入服务配置
      - CHROMA_OPENAI_API_KEY=${CHROMA_OPENAI_API_KEY}
      - CHROMA_OPENAI_API_BASE=${CHROMA_OPENAI_API_BASE}
      - CHROMA_OPENAI_MODEL_NAME=${CHROMA_OPENAI_MODEL_NAME:-gemini-embedding-001}
    
    # 确保容器可以访问宿主机网络
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

### 2. `.env.remote.example`
远程部署的环境变量模板。

```bash
# Chroma 连接配置
CHROMA_HOST=192.168.0.104
CHROMA_PORT=8012
CHROMA_SSL=false

# 嵌入模型配置 (Gemini 示例)
CHROMA_OPENAI_API_KEY=your_api_key_here
CHROMA_OPENAI_API_BASE=http://192.168.0.104:8000/v1/chat/completions
CHROMA_OPENAI_MODEL_NAME=gemini-embedding-001
```

## 执行步骤
1. 切换到 Code 模式。
2. 创建 `docker-compose.remote.yaml`。
3. 创建 `.env.remote.example`。
4. 更新 `deploy.md` 包含远程部署说明。