# Llamafile Reference Documentation

## Overview

Llamafile is a Mozilla project that lets you distribute and run LLMs with a single executable file. It combines llama.cpp with Cosmopolitan Libc to create cross-platform executables that run on macOS, Windows, Linux, FreeBSD, OpenBSD, and NetBSD (both AMD64 and ARM64 architectures).

**Key Feature for commit-polish**: Llamafile serves as the local LLM backend, providing an OpenAI-compatible API on port 8080.

## Official Documentation Sources

1. **GitHub Repository**: <https://github.com/mozilla-ai/llamafile>
2. **Official Documentation Site**: <https://mozilla-ai.github.io/llamafile/>
3. **LiteLLM Integration Docs**: <https://docs.litellm.ai/docs/providers/llamafile>
4. **Server API Reference**: <https://github.com/Mozilla-Ocho/llamafile/blob/main/llama.cpp/server/README.md>
5. **Releases Page**: <https://github.com/mozilla-ai/llamafile/releases>

## Installation

### Download Binary (v0.9.3)

```bash
# Download llamafile v0.9.3 binary
curl -L -o llamafile https://github.com/mozilla-ai/llamafile/releases/download/0.9.3/llamafile-0.9.3

# Make executable
chmod 755 llamafile

# Verify it works
./llamafile --version
```

**Alternative Download URLs**:
- GitHub Release: `https://github.com/mozilla-ai/llamafile/releases/download/0.9.3/llamafile-0.9.3`
- SourceForge Mirror: `https://sourceforge.net/projects/llamafile.mirror/files/0.9.3/`

### Download a Model

```bash
# Example: Download a pre-packaged llamafile with model included
curl -LO https://huggingface.co/Mozilla/llava-v1.5-7b-llamafile/resolve/main/llava-v1.5-7b-q4.llamafile
chmod +x llava-v1.5-7b-q4.llamafile

# Or download a standalone GGUF model file
curl -L -o gemma-3-3b.gguf https://huggingface.co/Mozilla/gemma-3-3b-it-gguf/resolve/main/gemma-3-3b-it-Q4_K_M.gguf
```

## Server Mode

### Basic Server Command

```bash
./llamafile --server -m model.gguf --nobrowser --port 8080 --host 127.0.0.1
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--server` | Run in server mode (required for API access) | N/A |
| `-m`, `--model` | Path to GGUF model file | Required |
| `--nobrowser` | Don't open browser on startup | Off |
| `--port` | Server port number | 8080 |
| `--host` | Bind address | 127.0.0.1 |
| `-c`, `--ctx-size` | Prompt context size (0 = from model) | 512 |
| `-t`, `--threads` | Number of threads for generation | Auto |
| `-tb`, `--threads-batch` | Threads for batch/prompt processing | Same as -t |
| `-ngl`, `--n-gpu-layers` | Number of layers to offload to GPU | 0 |
| `--embedding` | Enable embeddings endpoint | Off |
| `-a`, `--alias` | Model alias for API responses | None |
| `--mlock` | Lock model in memory | Off |
| `--cont-batching` | Enable continuous batching | Off |
| `--parallel` | Number of parallel sequences | 1 |

### Server Command for commit-polish

```bash
# Recommended startup command for commit-polish
./llamafile --server \
    -m /path/to/gemma-3-3b.gguf \
    --nobrowser \
    --port 8080 \
    --host 127.0.0.1
```

### Network-Accessible Server

```bash
# Allow connections from other machines (use with caution)
./llamafile --server \
    -m model.gguf \
    --nobrowser \
    --host 0.0.0.0 \
    --port 8080
```

### Performance-Optimized Server

```bash
# High-performance configuration with GPU offloading
./llamafile --server \
    -m model.gguf \
    --nobrowser \
    --port 8080 \
    --host 127.0.0.1 \
    --ctx-size 4096 \
    --n-gpu-layers 99 \
    --threads 8 \
    --cont-batching \
    --parallel 4
```

## OpenAI-Compatible API

### Endpoints

When running in server mode, llamafile provides these OpenAI-compatible endpoints:

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8080/v1/chat/completions` | Chat completions (primary) |
| `http://localhost:8080/v1/completions` | Text completions |
| `http://localhost:8080/v1/embeddings` | Embeddings (requires `--embedding` flag) |
| `http://localhost:8080/health` | Health check endpoint |

**Source**: [LiteLLM llamafile provider docs](https://docs.litellm.ai/docs/providers/llamafile)

### API Usage with LiteLLM (Recommended for commit-polish)

```python
import litellm

response = litellm.completion(
    model="llamafile/gemma-3-3b",  # Use llamafile/ prefix for routing
    messages=[{"role": "user", "content": "Hello, world!"}],
    api_base="http://localhost:8080/v1",
    temperature=0.3,
    max_tokens=200
)

print(response.choices[0].message.content)
```

**Key Points for LiteLLM Integration**:
- Model name MUST use `llamafile/` prefix for proper routing
- `api_base` MUST include `/v1` suffix
- No API key required (use any placeholder value)

### API Usage with OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="sk-no-key-required"  # Any value works
)

response = client.chat.completions.create(
    model="local-model",  # Model name is flexible
    messages=[
        {"role": "user", "content": "Hello, world!"}
    ]
)

print(response.choices[0].message.content)
```

### API Usage with curl

```bash
# Chat completions
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.3,
    "max_tokens": 200
  }'

# Health check
curl http://localhost:8080/health
```

### Embeddings API

```bash
# Requires server started with --embedding flag
curl http://localhost:8080/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "input": ["Hello world"]
  }'
```

## Configuration for commit-polish

### Installer Requirements

The `commit-polish-installer` package should:

1. Download llamafile binary to `~/.local/bin/llamafile` or similar
2. Download model file to `~/.local/share/commit-polish/models/`
3. Make binary executable (`chmod 755`)

### Config File Reference

```toml
# ~/.config/commit-polish/config.toml
[ai]
model = "llamafile/gemma-3-3b"  # Must use llamafile/ prefix
temperature = 0.3
max_tokens = 200

[llamafile]
path = "/home/user/.local/bin/llamafile"
model_path = "/home/user/.local/share/commit-polish/models/gemma-3-3b.gguf"
api_base = "http://127.0.0.1:8080/v1"
```

### Server Management Script Example

```python
import subprocess
import time
import httpx

def start_llamafile(
    llamafile_path: str,
    model_path: str,
    port: int = 8080,
    host: str = "127.0.0.1"
) -> subprocess.Popen:
    """Start llamafile server as background process."""
    cmd = [
        llamafile_path,
        "--server",
        "-m", model_path,
        "--nobrowser",
        "--port", str(port),
        "--host", host,
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait for server to be ready
    _wait_for_server(host, port)
    return process


def _wait_for_server(host: str, port: int, timeout: int = 30) -> None:
    """Wait for server to respond to health checks."""
    url = f"http://{host}:{port}/health"
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = httpx.get(url, timeout=2)
            if response.status_code == 200:
                return
        except httpx.RequestError:
            pass
        time.sleep(0.5)
    raise TimeoutError(f"Server did not start within {timeout} seconds")
```

## Version History

### v0.9.3 (May 14, 2025) - Current

**What's Changed**:
- Fixed troubleshooting guide links
- Improved URL handling in JS (preserves path when building relative URLs)
- Added Plaintext output option to LocalScore
- Respects NO_COLOR environment variable
- Added Phi4 model support
- Added Qwen3 model support
- Fixed Llama 8B statistics in README

**Release**: <https://github.com/mozilla-ai/llamafile/releases/tag/0.9.3>

### Version Constants
```
LLAMAFILE_MAJOR = 0
LLAMAFILE_MINOR = 9
LLAMAFILE_PATCH = 3
```

## Recommended Models

| Model | Size | Use Case |
|-------|------|----------|
| Gemma 3 3B | ~2GB | Balanced speed/quality (recommended for commit-polish) |
| Qwen3-0.6B | ~500MB | Fast, lower quality |
| Mistral 7B | ~4GB | Higher quality, slower |
| Llama 3.1 8B | ~5GB | Best quality, slowest |

**Model Format**: All models must be in GGUF format. Quantized versions (Q4_K_M recommended) provide good balance of quality and performance.

## Common Pitfalls

1. **Port 8000 vs 8080**: Llamafile defaults to port **8080**, not 8000
2. **Missing `/v1` in API URL**: Always include `/v1` suffix for OpenAI-compatible endpoints
3. **Starting server from hook**: The hook should NOT start the server; that's the installer's job
4. **Model path issues**: Ensure GGUF model file exists and is readable
5. **Permissions**: Binary must be executable (`chmod 755`)
6. **LiteLLM prefix**: Must use `llamafile/` prefix in model name for proper routing
7. **API key confusion**: No real API key needed, but some clients require a placeholder value

## Troubleshooting

### Server Won't Start

```bash
# Check if port is already in use
lsof -i :8080

# Kill existing process if needed
kill $(lsof -t -i :8080)

# Verify model file exists and is readable
ls -la /path/to/model.gguf

# Check file permissions on llamafile binary
ls -la /path/to/llamafile
```

### Connection Refused

```bash
# Verify server is running
curl http://localhost:8080/health

# Check server is listening on expected interface
netstat -tlnp | grep 8080
```

### Performance Issues

- Use quantized models (Q4_K_M recommended for balance of quality and speed)
- Ensure GPU acceleration is working if available (`--n-gpu-layers`)
- Increase context size only if needed (`--ctx-size`)
- Enable continuous batching for multiple concurrent requests (`--cont-batching`)

### API Errors

```bash
# Test basic connectivity
curl -v http://localhost:8080/health

# Test chat completions endpoint
curl -v http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"test","messages":[{"role":"user","content":"Hi"}]}'
```

## Docker Usage (Alternative)

```bash
# Run with Docker
docker run -p 8080:8080 \
  -v /path/to/models:/models \
  ghcr.io/ggerganov/llama.cpp:server \
  -m /models/model.gguf \
  --host 0.0.0.0 \
  --port 8080

# With CUDA GPU support
docker run -p 8080:8080 \
  -v /path/to/models:/models \
  --gpus all \
  ghcr.io/ggerganov/llama.cpp:server-cuda \
  -m /models/model.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --n-gpu-layers 99
```

## References

- Mozilla llamafile GitHub: <https://github.com/mozilla-ai/llamafile>
- Mozilla llamafile Documentation: <https://mozilla-ai.github.io/llamafile/>
- LiteLLM llamafile Provider: <https://docs.litellm.ai/docs/providers/llamafile>
- llama.cpp Server Documentation: <https://github.com/ggml-org/llama.cpp/tree/master/examples/server>
- Hugging Face Mozilla Models: <https://huggingface.co/Mozilla>
