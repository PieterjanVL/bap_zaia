import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
import requests
import json
import io
import struct
from fastavro import schemaless_reader
from kafka import KafkaConsumer
import timeit
import csv

SCHEMA_REGISTRY_URL = 'http://localhost:8081'
# Initialize Chroma client
client = chromadb.HttpClient(host='localhost', port=8000)

# Get or create a collection
collection = client.get_or_create_collection(name="chroma_768_webshop", metadata={"hnsw:space": "cosine"})

# Initialize embeddings
embeddings = HuggingFaceEmbeddings()


def add_data_to_chroma(text: str, id:str):
    # Generate the embedding for the text
    vector = embeddings.embed_query(text)

    # Add the vector, ID, and metadata to ChromaDB
    collection.add(
        embeddings=[vector],
        metadatas=[{"customer": text}],  # Metadata should be a dictionary
        ids=[id]
    )


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
    'kafka_postgres_.webshop.customer',
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
                f"Customer #{deserialized_message['id']} is {deserialized_message['firstname']} "
                f"{deserialized_message['lastname']}, born on {deserialized_message['dateofbirth']}. "
                f"They are {deserialized_message['gender']} and can be contacted via email at {deserialized_message['email']}. "
                f"They reside at the address with ID #{deserialized_message['currentaddressid']}."
            )
            id = "customer_id: " + str(deserialized_message["id"])
            add_data_to_chroma(text, id)

            record_count += 1
            if record_count == 1000:
                break  # Stop after processing 143 records

        except Exception as e:
            print(f"Failed to deserialize message: {e}")

    return record_count

# Calculate and print the elapsed time
elapsed_time = timeit.timeit(process_messages, number=1)
print(f"Time taken to process messages: {elapsed_time:.2f} seconds")

# Save the result to CSV
with open('chroma-768.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["1000", f"{elapsed_time:.2f}"])
