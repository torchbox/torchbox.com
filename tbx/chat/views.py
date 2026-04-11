import json
import logging
import re
from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from asgiref.sync import sync_to_async
from django_ai_core.llm import LLMService

from .indexes import ContentPagesIndex


# ============================================================================
# TYPE DEFINITIONS
# ============================================================================

type ConversationHistory = list[dict[str, str]]

logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# These should be moved elsewhere, but are kept here to keep the diff small for
# code review.
# ============================================================================


def parse_llm_suggestions(raw_text: str) -> list[str]:
    """
    Parse the LLM output into a list of up to five clean question strings.
    Accepts comma-separated text, newline lists, or a JSON array/object.
    """
    if not raw_text:
        return []

    # Try JSON first
    candidates = []
    try:
        data = json.loads(raw_text)
        if isinstance(data, list):
            candidates = [str(item) for item in data]
        elif isinstance(data, dict):
            if "questions" in data and isinstance(data["questions"], list):
                candidates = [str(item) for item in data["questions"]]
            else:
                # Flatten dict values as a last resort
                candidates = [
                    str(v) for v in data.values() if isinstance(v, str | int | float)
                ]
    except Exception:
        # Not JSON - fall through to text parsing
        logger.debug("Non-JSON response detected")

    if not candidates:
        # Unify separators and split. Models might return commas or newlines.
        unified = raw_text.replace("\n", ",")
        candidates = [part.strip() for part in unified.split(",") if part.strip()]

    # Clean bullets/numbering and stray quotes
    cleaned = []
    for item in candidates:
        s = item.strip().strip('"').strip("'")
        s = re.sub(r"^\s*(?:[-*•]|\d+[\.)])\s*", "", s)
        if s:
            cleaned.append(s)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for s in cleaned:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)

    return unique[:5]


# ============================================================================
# VIEW FUNCTIONS (called by URLs)
# ============================================================================


@never_cache
def chat_view(request):
    """
    Serves the main HTML page for the Ask interface.
    """
    # Allow pre-filling the query from GET param `q` for deep links
    prefill = request.GET.get("q", "")
    return render(
        request, "patterns/pages/chat/chat_page.html", {"prefill_query": prefill}
    )


# ============================================================================
# RESPONSE HELPERS (build streaming response components)
# ============================================================================


@sync_to_async
def get_source_json(source) -> str:
    """
    Asynchronously converts a source page object to a JSON string.
    """
    logger.debug("Fetching source %s", source.title)
    source_dict = {
        "title": source.title,
        "parent_title": source.get_parent().title,
        "url": source.get_url(),
    }
    return json.dumps(source_dict)


class RAGResponse:
    """
    Response object mimicking wagtail-vector-index aquery() response.
    Provides async iteration over LLM response chunks and access to source pages.
    """

    def __init__(self, response_stream, sources):
        self._stream = response_stream
        self.sources = sources
        self._response_started = False

    @property
    def response(self):
        """
        Async generator yielding text chunks from the LLM response.
        """
        return self._generate_response()

    async def _generate_response(self):
        """Internal generator for streaming response chunks."""
        async for chunk in self._stream:
            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    yield delta.content


@sync_to_async
def search_and_build_context(
    query: str, conversation_history: ConversationHistory, limit: int
):
    """
    Synchronous helper to search documents and build RAG context.
    Wrapped with sync_to_async for use in async functions.

    Uses hybrid search: combines last user question with current query
    to handle conversational references like "them", "it", "that", etc.
    """
    # Build search query from conversation context
    search_query = query
    if conversation_history:
        # Find the last user message
        last_user_msg = next(
            (msg for msg in reversed(conversation_history) if msg["role"] == "user"),
            None,
        )
        if last_user_msg:
            search_query = f"{last_user_msg['content']} {query}"

    # 1. Search for relevant documents
    index = ContentPagesIndex()
    documents = index.search_documents(search_query)

    # 2. Get the sources from documents and apply limit
    # This is not done earlier because the limit seems to get lost in
    # django-ai-core's queryset magic
    sources = list(documents.as_sources())[:limit]

    # 3. Build RAG context from documents
    context_parts = []
    for doc in documents:
        # Each doc has .content attribute with the text
        context_parts.append(doc.content)

    context = "\n\n".join(context_parts)

    return context, sources


async def rag_query(
    query: str, conversation_history: ConversationHistory | None = None, limit: int = 8
):
    """
    Perform RAG query using django-ai-core with optional conversation history.
    Replaces wagtail-vector-index's aquery() method.

    Args:
        query: Current user question
        conversation_history: List of prior messages [{"role": "user/assistant", "content": "..."}]
        limit: Number of documents to retrieve

    Returns a RAGResponse object with:
      - response: async generator of text chunks
      - sources: list of source pages
    """
    if conversation_history is None:
        conversation_history = []

    # Search documents and build context (sync operations wrapped with sync_to_async)
    context, sources = await search_and_build_context(
        query, conversation_history, limit
    )  # type: ignore (Pyright doesn't recognise @sync_to_async)

    # Build the message array with context in system message
    messages = [
        {
            "role": "system",
            "content": f"{settings.ASK_APP_QUERY_PROMPT}\n\nRelevant context:\n{context}",
        },
    ]

    # Add conversation history (if any)
    messages.extend(conversation_history)

    # Add current query
    messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    # Get streaming LLM response
    llm_service = LLMService.create(
        provider=settings.DJANGO_AI_CORE_COMPLETION_PROVIDER,
        model=settings.DJANGO_AI_CORE_COMPLETION_MODEL,
    )

    # Note: acompletion returns a coroutine, we need to await it to get the async generator
    response_stream = await llm_service.client.acompletion(
        model=llm_service.model, messages=messages, stream=True
    )

    # Return response object
    return RAGResponse(response_stream, sources)


async def sse_stream(
    query: str, conversation_history: ConversationHistory, session_key: str
):
    """
    An asynchronous generator that yields Server-Sent Events for the RAG query.

    Args:
        query: Current user question
        conversation_history: List of prior messages from Redis
        session_key: Django session key for storing conversation
    """
    try:
        yield b"event: start\n"
        yield b"data: \n\n"

        # Perform RAG query with conversation history
        response = await rag_query(query, conversation_history, limit=8)

        for source in response.sources:
            yield b"event: source\n"
            source_data = await get_source_json(source=source)  # type: ignore (Pyright doesn't recognise @sync_to_async)
            for line in source_data.splitlines():
                yield f"data: {line}\n".encode()
                logger.debug("source line %s", line)
            yield b"\n"

        # Accumulate assistant response for storage
        assistant_response = ""
        async for chunk in response.response:
            assistant_response += chunk
            yield b"event: chat\n"
            yield f"data: {quote(chunk or '')}\n".encode()
            yield b"\n"
            logger.debug("chunk %s", chunk)

        # Store conversation in Redis
        conversation_history.append({"role": "user", "content": query})
        conversation_history.append(
            {"role": "assistant", "content": assistant_response}
        )
        cache_key = f"conversation:{session_key}"
        await sync_to_async(cache.set)(
            cache_key,
            conversation_history,
            timeout=3600,
        )
        logger.debug(
            "Stored conversation to Redis (key: %s): %d messages",
            cache_key,
            len(conversation_history),
        )

        yield b"event: end\n"
        yield b"data: \n\n"

    except Exception:
        logger.exception("Error returning streaming response")
        yield b"event: chat\n"
        yield f"data: {quote('[Error returning the response]')}\n".encode()
        yield b"\n"
        yield b"event: server-error\n\n"


# ============================================================================
# VIEW FUNCTIONS continued (API endpoints)
# TODO: Move to separate module
# ============================================================================


async def stream_view(request):
    """
    The main asynchronous view that handles the streaming HTTP response.
    """
    query = request.GET.get("query", "")

    # Ensure session exists and get session key
    if not request.session.session_key:
        await sync_to_async(request.session.create)()

    session_key = request.session.session_key
    logger.debug("Session key: %s", session_key)

    # Load conversation history from Redis
    cache_key = f"conversation:{session_key}"
    conversation_history = await sync_to_async(cache.get)(cache_key, [])
    logger.debug(
        "Loaded conversation history from Redis: %d messages", len(conversation_history)
    )

    return StreamingHttpResponse(
        sse_stream(query, conversation_history, session_key),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-store"},
    )


@never_cache
def clear_conversation_view(request):
    """
    Clear the conversation history from Redis.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    if request.session.session_key:
        cache_key = f"conversation:{request.session.session_key}"
        cache.delete(cache_key)
        logger.debug("Deleted conversation from Redis (key: %s)", cache_key)
    else:
        logger.debug("No session key, nothing to delete from Redis")

    return JsonResponse({"status": "cleared"})


@never_cache
def suggested_questions_view(request):
    """
    Generates LLM-powered follow-up questions based on conversation history.
    Accepts POST with 'question', 'response', and 'conversation_history' (JSON or form-encoded).
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    question = ""
    response_text = ""
    conversation_history = []

    # Support JSON and form-encoded payloads
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            payload = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            payload = {}
        question = payload.get("question", "")
        response_text = payload.get("response", "")
        conversation_history = payload.get("conversation_history", [])
    else:
        question = request.POST.get("question", "")
        response_text = request.POST.get("response", "")
        # conversation_history not supported in form-encoded for simplicity

    # Default fallback suggestions if LLM call fails or output is unusable
    default_suggestions = [
        "Who should I get in touch with if I have a question about Wagtail services?"
        "What work have Torchbox.com done for other clients?"
    ]

    # Retrieve relevant search descriptions to enrich the prompt context
    relevant_topics = []
    try:
        if question:
            index = ContentPagesIndex()
            search_results = index.search_sources(
                question, overfetch_multiplier=4, max_overfetch_iterations=3
            )[:8]  # Limit to 8 results
            for result in search_results:
                try:
                    desc = getattr(result, "search_description", None)
                except Exception:
                    desc = None
                if isinstance(desc, str) and desc.strip():
                    relevant_topics.append(desc.strip())
    except Exception:
        relevant_topics = []

    # Build system message with instructions and relevant topics
    system_content = (
        "You generate follow-up questions that a potential client might ask a chatbot serving the Torchbox.com website. "
        "The user is a someone browsing the Torchbox.com website and may have questions about the services we offer, the work we have done, the people who work here, or the blog posts we have written."
        "Generate 5 succinct, relevant suggested follow-up questions in simple British English suitable for a UK public audience. "
        "Your questions should flow naturally from the conversation. "
        "Return your questions as a single comma-separated list with no context or explanation."
    )
    if relevant_topics:
        topics_text = "\n".join(f"- {t}" for t in relevant_topics)
        system_content += f"\n\nRelevant topics to consider:\n{topics_text}"

    # Build message array with conversation structure
    messages = [{"role": "system", "content": system_content}]

    # Add conversation history (if any)
    if conversation_history:
        messages.extend(conversation_history)

    # Add current Q&A pair
    if question:
        messages.append({"role": "user", "content": question})
    if response_text:
        messages.append({"role": "assistant", "content": response_text})

    # Request follow-up questions
    messages.append(
        {
            "role": "user",
            "content": "Based on this conversation, suggest 5 follow-up questions.",
        }
    )

    logger.debug("Generating suggestions with %d messages", len(messages))

    suggestions = []
    error = None
    try:
        # Lazy import to avoid loading 90MB litellm during startup
        import litellm

        llm_response = litellm.completion(
            model=settings.LITELLM_COMPLETION_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=256,
            timeout=15,
        )

        # Extract content in OpenAI-compatible response
        content = ""
        try:
            # litellm returns a dict structured like OpenAI
            choices = (
                llm_response.get("choices") if isinstance(llm_response, dict) else None
            )
            if choices and len(choices) > 0:
                message = choices[0].get("message", {})
                content = message.get("content", "")
            elif hasattr(llm_response, "choices"):
                # Fallback attribute style
                content = getattr(llm_response.choices[0].message, "content", "")
        except Exception:
            content = str(llm_response) if llm_response is not None else ""

        suggestions = parse_llm_suggestions(content)
        if len(suggestions) < 5:
            # Top up with defaults without duplicates
            for d in default_suggestions:
                if len(suggestions) >= 5:
                    break
                if d.lower() not in {s.lower() for s in suggestions}:
                    suggestions.append(d)
    except Exception:
        logger.exception("Error generating suggestions")
        error = "Error generating suggestions"
        suggestions = default_suggestions

    return JsonResponse(
        {
            "questions": suggestions,
            "received": {"question": question, "response_length": len(response_text)},
            **({"error": error} if error else {}),
        }
    )
