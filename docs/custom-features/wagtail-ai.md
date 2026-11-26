# Wagtail AI

AI-assisted content editing in the Wagtail admin, powered by [wagtail-ai](https://wagtail-ai.readthedocs.io/latest/).

## Configuration

The integration is off by default. Set `WAGTAIL_AI_ENABLED=true` to add `wagtail_ai` to `INSTALLED_APPS`, load its settings and add the AI button to the default rich text editor. When the flag is off, nothing from wagtail-ai or the LLM SDKs is imported. The provider and model are both configurable at runtime.

| Variable              | Required             | Default      | Description                                               |
| --------------------- | -------------------- | ------------ | --------------------------------------------------------- |
| `WAGTAIL_AI_ENABLED`  | Yes, to turn it on   | `false`      | Set to `true` to enable Wagtail AI                        |
| `WAGTAIL_AI_PROVIDER` | No                   | `openai`     | [any-llm](https://docs.mozilla.ai/any-llm/) provider name |
| `WAGTAIL_AI_MODEL`    | No                   | `gpt-6-luna` | Model identifier for the chosen provider                  |
| `OPENAI_API_KEY`      | When using OpenAI    | —            | API key read directly by the OpenAI SDK                   |
| `ANTHROPIC_API_KEY`   | When using Anthropic | —            | API key read directly by the Anthropic SDK                |

## Examples

**OpenAI (default):**

```
WAGTAIL_AI_ENABLED=true
WAGTAIL_AI_PROVIDER=openai
WAGTAIL_AI_MODEL=gpt-6-luna
OPENAI_API_KEY=sk-...
```

**Anthropic:**

```
WAGTAIL_AI_ENABLED=true
WAGTAIL_AI_PROVIDER=anthropic
WAGTAIL_AI_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

For a full list of supported providers and their model identifiers, see the [any-llm documentation](https://docs.mozilla.ai/any-llm/).

## Where editors see it

With Wagtail AI enabled:

- **AI button in the rich text toolbar.** A wand icon in the toolbar sends the field's text to the model with one of the configured prompts. It only appears on rich text fields that use the default editor, i.e. fields with no `features` argument, such as the **Summary** field in a Showcase block's paragraphs. Fields that pass `NO_HEADING_RICH_TEXT_FEATURES` or `PARAGRAPH_RICH_TEXT_FEATURES` don't get it.
- **Content feedback.** The page editor's **Checks** side panel gets a "Content feedback" section that asks the model to review the page.
- **Admin settings.** The AI agent settings are in the **Settings** menu, and the prompts used by the AI button have their own admin menu item.

The AI title and description field panels (`AITitleFieldPanel`, `AIDescriptionFieldPanel`) and image description aren't set up in this project.

## Local development

You can turn Wagtail AI on locally in either of two ways.

**Environment variables.** Pass the flag and your API key when starting the server:

```
docker compose exec -e WAGTAIL_AI_ENABLED=true -e OPENAI_API_KEY=sk-... web python manage.py runserver 0.0.0.0:8000
```

**`local.py`.** Uncomment the Wagtail AI block in `tbx/settings/local.py.example` and copy it to your `local.py`, then add your own API key. Setting `WAGTAIL_AI_ENABLED = True` in `local.py` isn't enough on its own. `local.py` is loaded after `base.py` has already built `INSTALLED_APPS` and the rich text features, so the block installs the app and adds the `ai` feature itself.

To find the AI button, edit a page with a Showcase block (the home page or most service pages) and click into a paragraph's **Summary** field. On Wagtail 8 the rich text toolbar only appears while the cursor is in the field.

## Notes for developers

- **App order.** `wagtail_ai` has to come before `wagtail.admin` in `INSTALLED_APPS`. It overrides some Wagtail admin templates, including the Checks side panel, and Django uses the first matching template it finds. If it comes after `wagtail.admin`, Content feedback disappears without any error.
- **Rich text features.** The project defines its own `DEFAULT_RICH_TEXT_FEATURES`, so wagtail-ai can't add its `ai` feature to Wagtail's built-in defaults. `base.py` appends `"ai"` to `DEFAULT_RICH_TEXT_FEATURES` when the flag is on. To offer AI on other rich text fields, add `"ai"` to their feature list behind the same flag.
- **Memory.** `django-ai-core` 0.1.7 and later load the provider SDK the first time an AI feature is used, not at startup. A worker that has handled an AI request keeps that SDK in memory for the rest of its life.
