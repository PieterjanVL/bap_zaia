import csv
import timeit

from langchain_huggingface import HuggingFaceEmbeddings

from pinecone import Pinecone

neighbors = [1, 1, 10, 100, 1000, 5000, 10000]

# Initialize Pinecone
pc = Pinecone(api_key="1ab617f2-0258-4f13-a196-1ac7edcb623e")

# embeddings = HuggingFaceEmbeddings()

model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)


def read_query(question: str, name: str, neighbors: int):
    # Embed the question to generate a vector
    question_vector = embeddings.embed_query(question)

    index = pc.Index(name)
    query_response = index.query(
        vector=question_vector, top_k=neighbors, include_metadata=True
    )


for i in neighbors:
    time_taken = timeit.timeit(
        lambda: read_query(
            "What is the email of customer John Doe?", "pinecone-384-webshop", i
        ),
        number=1,
    )
    print(f"Neighbors: {i}, Time: {time_taken} seconds")

    with open(
        "../analyse/query_db/pinecone-query-time-384.csv", mode="a", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow([i, f"{time_taken:.2f}"])
