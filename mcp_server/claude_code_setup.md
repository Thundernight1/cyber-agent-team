# Claude Code MCP Kurulum

## 1. Bağımlılıkları kur (Terminal'de çalıştır)

```bash
brew install pipx
pipx install mcp
pipx inject mcp httpx pydantic
```

## 2. ~/.claude.json dosyasına ekle

```bash
# Önce mevcut dosyayı gör:
cat ~/.claude.json
```

Dosyaya `mcpServers` ekle (yoksa oluştur):

```json
{
  "mcpServers": {
    "ollama": {
      "command": "python3",
      "args": ["/Users/myz21/Desktop/cyber-agent-team/mcp_server/ollama_mcp.py"],
      "env": {
        "OLLAMA_API_KEY": "b7ee7272a1a743efbfc3ad2ffdfcc6e4.JsYK6oMWPHUVAcsgjqvpXNuQ"
      }
    }
  }
}
```

## 3. Claude Code'u yeniden başlat

```bash
# Claude Code'u kapat ve yeniden aç
# veya:
claude mcp list   # ollama görünmeli
```

## 4. Test

Claude Code'da şunu yaz:
```
ollama_health_check çalıştır
```

Cloud bağlantısı onaylanmalı.

---
**NOT:** API key'i değiştirince burası ve .env dosyasını güncelle.
