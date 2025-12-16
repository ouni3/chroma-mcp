[Memory Bank: Active]

任务圆满完成！🎉

1.  **功能增强**: 我已在 `src/chroma_mcp/server.py` 中新增了 `chroma_embed_texts` 工具。现在您可以直接调用此工具来获取文本的向量表示，功能上已完全覆盖且超越了 `server.js`。
2.  **Docker 部署验证**:
    *   Docker 镜像已重新构建，包含了最新代码。
    *   使用您提供的参数 (`192.168.0.104:8012`) 进行了测试，连接成功！
    *   **注意**: 由于您的本地 Chroma 实例未使用 SSL，我在连接参数中显式添加了 `CHROMA_SSL=false`。

**如何配置 Claude Desktop 使用 Docker 版 Chroma MCP：**

请将以下配置添加到您的 `claude_desktop_config.json` 文件中：

```json
{
  "mcpServers": {
    "chroma": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "CHROMA_CLIENT_TYPE=http",
        "-e", "CHROMA_HOST=192.168.0.104",
        "-e", "CHROMA_PORT=8012",
        "-e", "CHROMA_SSL=false",
        "-e", "CHROMA_OPENAI_API_KEY=sk-123456",
        "-e", "CHROMA_OPENAI_API_BASE=http://192.168.0.104:8000/v1/chat/completions",
        "-e", "CHROMA_OPENAI_MODEL_NAME=gemini-embedding-001",
        "chroma-mcp"
      ]
    }
  }
}
```

**配置说明：**
*   `command`: 使用 `docker` 命令运行。
*   `args`:
    *   `run --rm -i`: 运行容器，退出后自动删除，`-i` 保持标准输入打开（MCP 协议必需）。
    *   `-e ...`: 传递环境变量配置连接。
        *   `CHROMA_CLIENT_TYPE`: 客户端类型 (http)。
        *   `CHROMA_HOST`: Chroma 服务地址。
        *   `CHROMA_PORT`: Chroma 服务端口。
        *   `CHROMA_SSL`: 是否启用 SSL (false)。
        *   `CHROMA_OPENAI_API_KEY`: 嵌入服务 API 密钥。
        *   `CHROMA_OPENAI_API_BASE`: 嵌入服务 API 地址 (兼容 OpenAI 格式)。
        *   `CHROMA_OPENAI_MODEL_NAME`: 使用的嵌入模型名称。
    *   `chroma-mcp`: 使用我们刚刚构建的镜像名称。

您可以重启 Claude Desktop 来启用新服务。如果有其他问题，请随时告诉我！

### 使用 Docker Compose 启动 (替代方案)

如果您更喜欢使用 Docker Compose 来管理服务，可以使用项目根目录下的 `docker-compose.yaml` 文件。

**启动服务：**
```bash
docker-compose up -d
```

**停止服务：**
```bash
docker-compose down
```

**注意：**
目前的 `docker-compose.yaml` 配置为使用 `sse` (Server-Sent Events) 协议在 HTTP 端口 `8000` 上运行。这使得它可以通过 HTTP 远程访问。

要使用此模式，请将 Claude Desktop 的配置更改为使用 `sse` 传输：

```json
{
  "mcpServers": {
    "chroma": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

如果您希望使用 `stdio` (标准输入输出) 模式（如之前的 `docker run` 示例），可以忽略此 Docker Compose 配置，或者修改 Compose 文件将 `MCP_TRANSPORT` 设置为 `stdio` 并移除端口映射。