import csv
import timeit

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

neighbors = [1, 1, 10, 100, 1000, 5000, 10000, 20000, 30000, 35000, 40000, 45000]

# Initialize Chroma client
client = chromadb.HttpClient(host="localhost", port=8000)

# Get or create a collection
# collection = client.get_or_create_collection(name="chroma_768_webshop")
collection = client.get_or_create_collection(name="chroma_384_webshop")

# Initialize embeddings
# embeddings = HuggingFaceEmbeddings()

model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)


def read_query(question: str, total_neighbors: int):
    vector = embeddings.embed_query(question)

    response = collection.query(
        query_embeddings=[vector],
        n_results=total_neighbors,
    )["metadatas"]


for i in neighbors:
    time_taken = timeit.timeit(
        lambda: read_query("What is the email of customer John Doe?", i), number=1
    )
    print(f"Neighbors: {i}, Time: {time_taken} seconds")

    with open(
        "../analyse/query_db/chroma-query-time-384.csv", mode="a", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow([i, f"{time_taken:.2f}"])
