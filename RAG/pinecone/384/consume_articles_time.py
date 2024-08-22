from kafka import KafkaConsumer
from fastavro import schemaless_reader
import io
import requests
import json
import struct
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
import timeit
import csv

# Configuration for Schema Registry
SCHEMA_REGISTRY_URL = 'http://localhost:8081'

# Initialize Pinecone and Hugging Face embeddings
pc = Pinecone(api_key="1ab617f2-0258-4f13-a196-1ac7edcb623e")
model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)
id_counter = 1  # Start the ID counter

index_name = "pinecone-384-webshop"

# Get the Pinecone index
index = pc.Index(index_name)

def use_pinecone(text, id):
    # Generate vector for the text
    vector = embeddings.embed_query(text)

    upsert_response = index.upsert(vectors=[{
        "id": str(id),
        "values": vector,
        "metadata": {"article": text}
    }])
    print(f"Upserted vector for text: '{text}'")
    print("Upsert Response:", upsert_response)


def get_schema(schema_id):
    """Fetch the Avro schema from Schema Registry."""
    response = requests.get(f'{SCHEMA_REGISTRY_URL}/schemas/ids/{schema_id}')
    if response.status_code == 200:
        schema = response.json()['schema']
        return json.loads(schema)
    else:
        raise Exception(f"Failed to fetch schema {schema_id}: {response.text}")


def deserialize_avro_message(message):
    """Deserialize the Avro message using the provided schema."""
    bytes_reader = io.BytesIO(message)

    # Read magic byte and schema ID
    magic_byte = bytes_reader.read(1)  # Read the magic byte
    schema_id = struct.unpack('>I', bytes_reader.read(4))[0]  # Unpack schema ID as a 4-byte integer

    # Get schema from Schema Registry
    schema = get_schema(schema_id)
    bytes_reader.seek(5)  # Move reader position to the start of the actual data

    decoded_message = schemaless_reader(bytes_reader, schema)
    return decoded_message


# Kafka Consumer Setup
consumer = KafkaConsumer(
    'kafka_postgres_.webshop.articles',
    bootstrap_servers=['localhost:9092', 'localhost:9093'],
    auto_offset_reset='earliest',  # Change to 'latest' if you want to start from the latest messages
    enable_auto_commit=False,
    group_id='my_group_id',
)

# Initialize the counter and start time
def process_messages():
    record_count = 0

    for message in consumer:
        try:
            deserialized_message = deserialize_avro_message(message.value)  # schema is fetched dynamically
            print("Deserialized message: ", deserialized_message)
            text = (
                f"Article #{deserialized_message['id']} belongs to product #{deserialized_message['productid']} and has the color ID #{deserialized_message['colorid']}. "
                f"The size is {deserialized_message['size']} and the description is '{deserialized_message['description']}'. "
                f"The original price is {deserialized_message['originalprice']} and the reduced price is {deserialized_message['reducedprice']}. "
                f"The article has a tax rate of {deserialized_message['taxrate']}% and a discount percentage of {deserialized_message['discountinpercent']}%."
            )
            id = "article_id: " + str(deserialized_message["id"])
            use_pinecone(text, id)
            record_count += 1
            if record_count == 17730:
                break  # Stop after processing 143 records
        except Exception as e:
            print(f"Failed to deserialize message: {e}")
    return record_count

# Calculate and print the elapsed time
elapsed_time = timeit.timeit(process_messages, number=1)
print(f"Time taken to process messages: {elapsed_time:.2f} seconds")

# Save the result to CSV
with open('pinecone-384.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["17730", f"{elapsed_time:.2f}"])