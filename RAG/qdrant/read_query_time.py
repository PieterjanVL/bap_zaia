from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
import timeit
import csv

neighbors = [1, 1, 10, 100, 1000, 5000, 10000, 20000, 30000, 35000, 40000, 45000]

client = QdrantClient(url="http://localhost:6333")

#768:
embeddings = HuggingFaceEmbeddings()

#384:
#model_name = "sentence-transformers/all-MiniLM-L6-v2"
#embeddings = HuggingFaceEmbeddings(model_name=model_name)

def read_query(question: str, collection_name: str, total_neighbors: int):
    vector = embeddings.embed_query(question)
    search_result = client.search(
        collection_name=collection_name, query_vector=vector, limit=total_neighbors
    )

for i in neighbors:
    time_taken = timeit.timeit(lambda: read_query("What is the phone number of customer John Doe?", "qdrant_768_webshop", i), number=1)
    print(f"Neighbors: {i}, Time: {time_taken} seconds")

    with open('../analyse/query_db/qdrant-query-time-768.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([i, f"{time_taken:.2f}"])
