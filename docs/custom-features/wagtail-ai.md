# Wagtail AI

AI-assisted content editing in the Wagtail admin, powered by [wagtail-ai](https://wagtail-ai.readthedocs.io/latest/).

## Configuration

The integration is always active but requires environment variables to function. The provider and model are both configurable at runtime.

| Variable              | Required             | Default        | Description                                               |
| --------------------- | -------------------- | -------------- | --------------------------------------------------------- |
| `WAGTAIL_AI_PROVIDER` | No                   | `openai`       | [any-llm](https://docs.mozilla.ai/any-llm/) provider name |
| `WAGTAIL_AI_MODEL`    | No                   | `gpt-4.1-mini` | Model identifier for the chosen provider                  |
| `OPENAI_API_KEY`      | When using OpenAI    | —              | API key read directly by the OpenAI SDK                   |
| `ANTHROPIC_API_KEY`   | When using Anthropic | —              | API key read directly by the Anthropic SDK                |

## Examples

**OpenAI (default):**

```
WAGTAIL_AI_PROVIDER=openai
WAGTAIL_AI_MODEL=gpt-4.1-mini
OPENAI_API_KEY=sk-...
```

**Anthropic:**

```
WAGTAIL_AI_PROVIDER=anthropic
WAGTAIL_AI_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

For a full list of supported providers and their model identifiers, see the [any-llm documentation](https://docs.mozilla.ai/any-llm/).
