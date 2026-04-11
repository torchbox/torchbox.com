from django.conf import settings

from django_ai_core.contrib.index import (
    CachedEmbeddingTransformer,
    CoreEmbeddingTransformer,
    VectorIndex,
    registry,
)
from django_ai_core.contrib.index.source import ModelSource
from django_ai_core.contrib.index.storage.pgvector import PgVectorProvider
from django_ai_core.llm import LLMService

from tbx.blog.models import BlogPage
from tbx.chat.models import CustomPgVectorEmbedding
from tbx.work.models import HistoricalWorkPage, WorkPage


def get_cached_embedding_transformer():
    """
    Lazy creation of `LLMService` instance, because it checks for
    `OPENAI_API_KEY`, which is not always available (e.g. during Docker build
    or in tests).
    """
    llm_embedding_service = LLMService.create(
        provider=settings.DJANGO_AI_CORE_EMBEDDING_PROVIDER,
        model=settings.DJANGO_AI_CORE_EMBEDDING_MODEL,
    )
    return CachedEmbeddingTransformer(
        base_transformer=CoreEmbeddingTransformer(llm_embedding_service),
    )


@registry.register()
class ContentPagesIndex(VectorIndex):
    sources = [
        ModelSource(model=HistoricalWorkPage),
        ModelSource(model=WorkPage),
        ModelSource(model=BlogPage),
    ]
    storage_provider = PgVectorProvider(model=CustomPgVectorEmbedding)

    @property
    def embedding_transformer(self):
        return get_cached_embedding_transformer()
