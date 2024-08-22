import chromadb
from langchain.prompts import PromptTemplate
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain_huggingface import HuggingFaceEmbeddings

# Initialize Chroma client
client = chromadb.HttpClient(host="localhost", port=8000)

# Get or create a collection
collection = client.get_or_create_collection(name="chroma_768_webshop")

# Initialize embeddings
embeddings = HuggingFaceEmbeddings()


def ask_question(question: str):
    vector = embeddings.embed_query(question)

    response = collection.query(
        query_embeddings=[vector],
        n_results=200,
    )["metadatas"]

    repo_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    llm = HuggingFaceHub(
        repo_id=repo_id,
        model_kwargs={"temperature": 0.8, "top_k": 200},
        huggingfacehub_api_token="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",
    )

    template = """
        You are an assistant who answers simple questions. Use the following context to answer the question concisely.

        Context: {context}
        Question: {question}
        Answer: 

        """

    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    formatted_prompt = prompt.format(context=response, question=question)

    response = llm(formatted_prompt)
    # print(f"Response: {response}")
    return response


# print(ask_question("What is the email of Christian Pedersen?")) #christian.pedersen@example.com
# print(ask_question("What is the address of Christian Pedersen?")) #answer is wrong: The address of Christian Pedersen is 2070 Ringkøbingvej in the city of Aalborg S.Ø..

# print(ask_question("Give the address id that belongs to Christian Pedersen?")) #911
# print(ask_question("Give the details of address with id 911.")) #The answer is right: The address with ID 911 belongs to user #911. The address is 1046 Myllypuronkatu in the city of Honkajoki.


###Count:
# print(get_relevant_data("How many products do we have, count them and return the total."))
print(
    ask_question(
        "Can you provide the total number of products available in the inventory? Please count all products and return the total."
    )
)
