from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url="http://localhost:6333")


def add_768_collection():
    client.create_collection(
        collection_name="qdrant_768_webshop",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )


def add_384_collection():
    client.create_collection(
        collection_name="qdrant_384_webshop",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )




add_384_collection()
add_768_collection()
