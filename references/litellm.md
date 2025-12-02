# LiteLLM Reference Documentation

## Overview

LiteLLM is a Python library that provides a unified interface to call 100+ LLM APIs using the OpenAI format. It supports consistent output handling, retry/fallback logic, and cost tracking across multiple providers.

**Key Feature for commit-polish**: LiteLLM enables routing requests to local llamafile servers using the `llamafile/` model prefix.

## Official Documentation Sources

| Resource | URL |
|----------|-----|
| LiteLLM Documentation | https://docs.litellm.ai/ |
| Llamafile Provider Docs | https://docs.litellm.ai/docs/providers/llamafile |
| Exception Mapping | https://docs.litellm.ai/docs/exception_mapping |
| GitHub Repository | https://github.com/BerriAI/litellm |
| Llamafile Source Docs | https://github.com/BerriAI/litellm/blob/main/docs/my-website/docs/providers/llamafile.md |

## Installation

```bash
pip install litellm
# or with uv
uv add litellm
```

## Llamafile Provider Configuration

### Provider Overview

From official documentation (https://github.com/BerriAI/litellm/blob/main/docs/my-website/docs/providers/llamafile.md):

| Property | Details |
|----------|---------|
| Description | llamafile lets you distribute and run LLMs with a single file |
| Provider Route on LiteLLM | `llamafile/` (for OpenAI compatible server) |
| Provider Doc | https://github.com/Mozilla-Ocho/llamafile/blob/main/llama.cpp/server/README.md#api-endpoints |
| Supported Endpoints | `/chat/completions`, `/embeddings`, `/completions` |

### Model Prefix Requirement

All llamafile models **must** use the `llamafile/` prefix for LiteLLM to route requests correctly:

```python
model = "llamafile/mistralai/mistral-7b-instruct-v0.2"
model = "llamafile/gemma-3-3b"  # Any model name after prefix works
```

### API Base URL Configuration

The `api_base` must point to the llamafile server's OpenAI-compatible endpoint:

```python
api_base = "http://localhost:8080/v1"  # Port 8080 is llamafile default
```

**Critical**: Include the `/v1` suffix. Do NOT add additional paths like `/v1/chat/completions` - LiteLLM adds those automatically.

### Environment Variable Configuration

From official documentation, you can set the API base via environment variable:

```python
import os

os.environ["LLAMAFILE_API_BASE"] = "http://localhost:8080/v1"
```

## Python SDK Usage

### Synchronous Completion

From official LiteLLM documentation (https://github.com/BerriAI/litellm/blob/main/docs/my-website/docs/providers/llamafile.md):

```python
import litellm

response = litellm.completion(
    model="llamafile/mistralai/mistral-7b-instruct-v0.2",  # llamafile/ prefix required
    messages=[{"role": "user", "content": "Summarize this diff"}],
    api_base="http://localhost:8080/v1",
    temperature=0.2,
    max_tokens=80,
)

print(response.choices[0].message.content)
```

### Asynchronous Completion

From official LiteLLM documentation (https://github.com/BerriAI/litellm/blob/main/docs/my-website/docs/completion/stream.md):

```python
from litellm import acompletion
import asyncio

async def generate_message():
    response = await acompletion(
        model="llamafile/gemma-3-3b",
        messages=[{"role": "user", "content": "Write a commit message"}],
        api_base="http://localhost:8080/v1",
        temperature=0.3,
        max_tokens=200,
    )
    return response.choices[0].message.content

# Run async
result = asyncio.run(generate_message())
print(result)
```

### Async Streaming

```python
from litellm import acompletion
import asyncio

async def stream_response():
    response = await acompletion(
        model="llamafile/gemma-3-3b",
        messages=[{"role": "user", "content": "Hello, how are you?"}],
        api_base="http://localhost:8080/v1",
        stream=True,
    )

    async for chunk in response:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()

asyncio.run(stream_response())
```

### Embeddings

From official LiteLLM documentation:

```python
from litellm import embedding
import os

os.environ["LLAMAFILE_API_BASE"] = "http://localhost:8080/v1"

response = embedding(
    model="llamafile/sentence-transformers/all-MiniLM-L6-v2",
    input=["Hello world"],
)

print(response)
```

## Exception Handling

### Import Pattern

From official documentation (https://github.com/BerriAI/litellm/blob/main/docs/my-website/docs/exception_mapping.md):

> All exceptions can be imported from `litellm` - e.g. `from litellm import BadRequestError`

LiteLLM maps all provider exceptions to OpenAI counterparts. Import directly from `litellm`:

```python
from litellm import (
    BadRequestError,           # 400 errors
    AuthenticationError,       # 401 errors
    NotFoundError,             # 404 errors
    Timeout,                   # 408 errors (alias: openai.APITimeoutError)
    RateLimitError,            # 429 errors
    APIConnectionError,        # 500 errors / connection issues (default)
    ServiceUnavailableError,   # 503 errors
)
```

### Exception Types Reference

From official exception mapping documentation:

| Status Code | Exception Type | Inherits from | Description |
|-------------|----------------|---------------|-------------|
| 400 | `BadRequestError` | openai.BadRequestError | Invalid request |
| 400 | `ContextWindowExceededError` | litellm.BadRequestError | Token limit exceeded |
| 400 | `ContentPolicyViolationError` | litellm.BadRequestError | Content policy violation |
| 401 | `AuthenticationError` | openai.AuthenticationError | Auth failure |
| 403 | `PermissionDeniedError` | openai.PermissionDeniedError | Permission denied |
| 404 | `NotFoundError` | openai.NotFoundError | Invalid model/endpoint |
| 408 | `Timeout` | openai.APITimeoutError | Request timeout |
| 429 | `RateLimitError` | openai.RateLimitError | Rate limited |
| 500 | `APIConnectionError` | openai.APIConnectionError | Default for unmapped errors |
| 500 | `APIError` | openai.APIError | Generic 500 error |
| 503 | `ServiceUnavailableError` | openai.APIStatusError | Service unavailable |
| >=500 | `InternalServerError` | openai.InternalServerError | Unmapped 500+ errors |

### Exception Attributes

All LiteLLM exceptions include these additional attributes:

- `status_code`: HTTP status code
- `message`: Error message
- `llm_provider`: Provider that raised the exception

### Exception Handling Example

From official documentation:

```python
import litellm
import openai

try:
    response = litellm.completion(
        model="llamafile/gemma-3-3b",
        messages=[{"role": "user", "content": "Hello"}],
        api_base="http://localhost:8080/v1",
        timeout=30.0,
    )
except openai.APITimeoutError as e:
    # LiteLLM exceptions inherit from OpenAI types
    print(f"Timeout: {e}")
except litellm.APIConnectionError as e:
    print(f"Connection failed: {e.message}")
    print(f"Provider: {e.llm_provider}")
```

### Using litellm.exceptions Module

You can also import from `litellm.exceptions`:

```python
from litellm.exceptions import BadRequestError, AuthenticationError, APIError

try:
    response = litellm.completion(
        model="llamafile/gemma-3-3b",
        messages=[{"role": "user", "content": "Hello"}],
        api_base="http://localhost:8080/v1",
    )
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except BadRequestError as e:
    print(f"Bad request: {e}")
except APIError as e:
    print(f"API error: {e}")
```

### Checking If Exception Should Retry

```python
import litellm

try:
    response = litellm.completion(
        model="llamafile/gemma-3-3b",
        messages=[{"role": "user", "content": "Hello"}],
        api_base="http://localhost:8080/v1",
    )
except Exception as e:
    if hasattr(e, 'status_code'):
        should_retry = litellm._should_retry(e.status_code)
        print(f"Should retry: {should_retry}")
```

## Retry and Fallback Configuration

```python
from litellm import completion

response = completion(
    model="llamafile/gemma-3-3b",
    messages=[{"role": "user", "content": "Hello"}],
    api_base="http://localhost:8080/v1",
    num_retries=3,      # Retry 3 times on failure
    timeout=30.0,       # 30 second timeout
)
```

## Proxy Server Configuration

For proxy deployments, use `config.yaml`:

```yaml
model_list:
  - model_name: commit-polish-model
    litellm_params:
      model: llamafile/gemma-3-3b          # add llamafile/ prefix
      api_base: http://localhost:8080/v1   # add api base for OpenAI compatible provider
```

## Integration Notes for commit-polish

### Required Configuration

```toml
# ~/.config/commit-polish/config.toml
[ai]
model = "llamafile/gemma-3-3b"  # MUST have llamafile/ prefix
temperature = 0.3
max_tokens = 200
```

### Connection Verification Pattern

```python
import litellm
from litellm import APIConnectionError

def verify_llamafile_connection(api_base: str = "http://localhost:8080/v1") -> bool:
    """Check if llamafile server is running."""
    try:
        litellm.completion(
            model="llamafile/test",
            messages=[{"role": "user", "content": "test"}],
            api_base=api_base,
            max_tokens=1,
        )
        return True
    except APIConnectionError:
        return False
```

### Async Service Pattern for commit-polish

```python
import litellm
from litellm import acompletion, APIConnectionError
import asyncio

class AIService:
    """LiteLLM wrapper with llamafile routing."""

    def __init__(self, model: str, api_base: str, temperature: float = 0.3, max_tokens: int = 200):
        self.model = model
        self.api_base = api_base
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def generate_commit_message(self, diff: str, system_prompt: str) -> str:
        """Generate a commit message using the LLM."""
        try:
            response = await acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate a commit message for this diff:\n\n{diff}"},
                ],
                api_base=self.api_base,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content.strip()
        except APIConnectionError as e:
            raise RuntimeError(f"Failed to connect to llamafile server at {self.api_base}: {e.message}")
```

## Common Pitfalls to Avoid

1. **Missing `llamafile/` prefix**: Without prefix, LiteLLM won't route to OpenAI-compatible endpoint
2. **Wrong port**: Llamafile uses 8080 by default, not 8000
3. **Missing `/v1` suffix**: API base must end with `/v1`
4. **Adding extra path segments**: Do NOT use `http://localhost:8080/v1/chat/completions` - LiteLLM adds the endpoint path automatically
5. **API key requirement**: No API key needed for local llamafile (use empty string or any value if required by validation)

## Version Information

- Documentation verified against: LiteLLM GitHub repository (main branch)
- Python: 3.11+
- Llamafile: 0.9.3+

## Verification Checklist

The following details were verified against official LiteLLM documentation:

- [x] `llamafile/` prefix required for model routing
- [x] API base URL format: `http://localhost:8080/v1`
- [x] Environment variable: `LLAMAFILE_API_BASE`
- [x] Async API: `litellm.acompletion()` / `from litellm import acompletion`
- [x] Exception imports: `from litellm import APIConnectionError, BadRequestError, ...`
- [x] Exceptions inherit from OpenAI types for compatibility
- [x] Exception attributes: `status_code`, `message`, `llm_provider`
