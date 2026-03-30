# Ollama Cloud MCP Server

Ollama Cloud modellerine MCP protokolü üzerinden erişim.

## Kurulum

```bash
pip install mcp httpx pydantic
export OLLAMA_API_KEY=your_api_key_here
```

## Claude Code Entegrasyonu

`~/.claude.json` dosyasına ekle:

```json
{
  "mcpServers": {
    "ollama": {
      "command": "python",
      "args": ["/tam/yol/cyber-agent-team/mcp_server/ollama_mcp.py"],
      "env": {
        "OLLAMA_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Cowork / Claude Desktop Entegrasyonu

Cowork'ta MCP server olarak eklemek için:
1. Claude Desktop → Settings → MCP Servers
2. "Add Server" → Python → bu dosyanın yolunu ver
3. OLLAMA_API_KEY env variable'ını ayarla

## Mevcut Tools

| Tool | Açıklama |
|------|----------|
| `ollama_list_models` | Mevcut cloud modellerini listele |
| `ollama_chat` | Tek turlu chat completion |
| `ollama_chat_multi_turn` | Çok turlu konuşma (history ile) |
| `ollama_generate` | Basit text completion |
| `ollama_task_route` | Görev tipine göre otomatik model seç |
| `ollama_health_check` | Bağlantı durumu kontrol |

## Görev → Model Eşleştirmesi

| Görev Tipi | Model |
|-----------|-------|
| reasoning | kimi-k2-thinking:cloud |
| coding | qwen3-coder:480b-cloud |
| coding_fast | devstral-small-2:24b-cloud |
| analysis | mistral-large-3:675b-cloud |
| general | gemma3:27b-cloud |
| vision | qwen3-vl:235b-cloud |
| fast | nemotron-3-nano:30b-cloud |
| large | cogito-2.1:671b-cloud |
