# Wagtail AI

AI-assisted content editing in the Wagtail admin, powered by [wagtail-ai](https://wagtail-ai.readthedocs.io/latest/).

## Configuration

Off by default. With the flag off, nothing from wagtail-ai or the LLM SDKs is imported.

| Variable                 | Required             | Default      | Description                                                             |
| ------------------------ | -------------------- | ------------ | ----------------------------------------------------------------------- |
| `WAGTAIL_AI_ENABLED`     | Yes, to turn it on   | `false`      | Set to `true` to enable Wagtail AI                                      |
| `OPENAI_API_KEY`         | Yes                  | —            | OpenAI key. Always needed, because the rich text AI button uses OpenAI  |
| `WAGTAIL_AI_MODEL_ID`    | No                   | `gpt-6-luna` | Model for the rich text AI button, as known to the `llm` package        |
| `WAGTAIL_AI_TOKEN_LIMIT` | No                   | `8192`       | Token limit for `WAGTAIL_AI_MODEL_ID`, used to split long text          |
| `WAGTAIL_AI_PROVIDER`    | No                   | `openai`     | [any-llm](https://docs.mozilla.ai/any-llm/) provider for agent features |
| `WAGTAIL_AI_MODEL`       | No                   | `gpt-6-luna` | Model for agent features, for the chosen provider                       |
| `ANTHROPIC_API_KEY`      | When using Anthropic | —            | Anthropic key, if `WAGTAIL_AI_PROVIDER=anthropic`                       |

wagtail-ai has two separate configs, and `base.py` sets both:

- **`BACKENDS`**, used by the rich text AI button, goes through the [`llm`](https://llm.datasette.io/) package. Only OpenAI models are installed for it.
- **`PROVIDERS`**, used by agent features such as content feedback, goes through any-llm and can use any supported provider.

## Where editors see it

- **AI button (wand icon) in the rich text toolbar**, on fields that use the default editor (no `features` argument), such as a Showcase block paragraph's **Summary**.
- **Content feedback** in the page editor's **Checks** side panel.
- **AI agent settings** in the **Settings** menu, and the button's prompts in their own admin menu item.

AI title and description panels and image description aren't set up in this project.

## Local development

Either pass the environment variables when starting the server:

```
docker compose exec -e WAGTAIL_AI_ENABLED=true -e OPENAI_API_KEY=sk-... web python manage.py runserver 0.0.0.0:8000
```

Or copy the Wagtail AI block from `tbx/settings/local.py.example` into your `local.py`, uncomment it and set `LOCAL_TESTING_OPENAI_API_KEY`. Copy the whole block: `local.py` loads after `base.py` has built `INSTALLED_APPS` and the rich text features, and its `WAGTAIL_AI` replaces the one from `base.py`.

On Wagtail 8 the rich text toolbar only appears while the cursor is in the field.

## Notes for developers

- **App order.** `wagtail_ai` must come before `wagtail.admin` in `INSTALLED_APPS`. It overrides Wagtail admin templates, including the Checks side panel, and loses them silently otherwise.
- **Rich text features.** The project defines its own `DEFAULT_RICH_TEXT_FEATURES`, so `base.py` appends `"ai"` to it when the flag is on. Fields using `NO_HEADING_RICH_TEXT_FEATURES` or `PARAGRAPH_RICH_TEXT_FEATURES` don't get the button. Add `"ai"` to those lists, behind the flag, to offer it there.
- **Memory.** The provider SDK loads the first time an AI feature is used, not at startup, and stays in that worker's memory afterwards.

## Troubleshooting

A failed AI button shows `POST /admin/ai/text_completion/ 500` in the browser console, often followed by `Minified React error #200`, which can be ignored. The real error is in the runserver console:

- **`KeyError: 'BACKENDS'`:** `WAGTAIL_AI` has no `BACKENDS`, usually because `local.py` defines only `PROVIDERS`.
- **`openai.AuthenticationError` (401):** the OpenAI key is missing or wrong.
- **`NoTokenLimitFound`:** a custom `BACKENDS` config has no `TOKEN_LIMIT` for a model wagtail-ai doesn't know.
