from typing import TypedDict

from app.client.custom_embedding_client import CustomEmbeddingClient
from app.repository.qdrant.column_qdrant_repository import ColumnQdrantRepository


class AgentRuntimeContext(TypedDict):
    embedding_client : CustomEmbeddingClient
    column_qdrant_repository: ColumnQdrantRepository