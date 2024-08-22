from qdrant_client import QdrantClient
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate

client = QdrantClient(url="http://localhost:6333")
embeddings = HuggingFaceEmbeddings()

def get_relevant_data(question: str):
    vector = embeddings.embed_query(question)
    search_result = client.search(
        collection_name="qdrant_768_webshop", query_vector=vector, limit=800
    )

    context = [point.payload for point in search_result]

    #return payloads

    repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    llm = HuggingFaceHub(
        repo_id=repo_id,
        model_kwargs={"temperature": 0.8, "top_k": 300},
        huggingfacehub_api_token="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"
    )

    template = """
            You are an assistant who answers simple questions. Use the following context to answer the question concisely.

            Context: {context}
            Question: {question}
            Answer: 

            """

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )

    formatted_prompt = prompt.format(context=context, question=question)

    response = llm(formatted_prompt)
    # print(f"Response: {response}")
    return response

###Where:
#print(get_relevant_data("What is the email of Christian Pedersen?")) #christian.pedersen@example.com
#print(get_relevant_data("What is the address of Christian Pedersen?")) #answer is wrong: The address of Christian Pedersen is 2070 Ringkøbingvej in the city of Aalborg S.Ø..

#print(get_relevant_data("Give the address id that belongs to Christian Pedersen?")) #911
#print(get_relevant_data("Give the details of address with id 911.")) #The answer is right: The address with ID 911 belongs to user #911. The address is 1046 Myllypuronkatu in the city of Honkajoki.


###Count:
#print(get_relevant_data("How many products do we have, count them and return the total."))
print(get_relevant_data("Can you provide the total number of products available in the inventory? Please count all products and return the total."))