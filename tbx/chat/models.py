from django_ai_core.contrib.index.storage.pgvector.models import BasePgVectorEmbedding
from pgvector.django import HnswIndex, VectorField


class CustomPgVectorEmbedding(BasePgVectorEmbedding):
    vector = VectorField(dimensions=1536)  # default for OpenAI text-embedding-3-small

    class Meta:
        indexes = [
            HnswIndex(
                name="vector_index",
                fields=["vector"],
                m=16,
                ef_construction=64,
                opclasses=["vector_l2_ops"],
            )
        ]
