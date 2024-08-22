from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
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

client = QdrantClient(url="http://localhost:6333")
embeddings = HuggingFaceEmbeddings()


def add_data_to_qdrant(text: str, id: int):
    vector = embeddings.embed_query(text)

    client.upsert(
        collection_name="qdrant_768_webshop",
        wait=True,
        points=[
            PointStruct(id=id, vector=vector, payload={"color": text}),
        ], )


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
    'kafka_postgres_.webshop.colors',
    bootstrap_servers=['localhost:9092', 'localhost:9093'],
    auto_offset_reset='earliest',  # Change to 'latest' if you want to start from the latest messages
    enable_auto_commit=False,
    group_id='my_group_id',
)

# Initialize the counter and start time
def process_messages():
    record_count = 0
    ID = 20000

    for message in consumer:
        try:
            deserialized_message = deserialize_avro_message(message.value)  # schema is fetched dynamically
            print("Deserialized message: ", deserialized_message)
            text = (
                f"Color #{deserialized_message['id']} is named '{deserialized_message['name']}' "
                f"and has an RGB code of {deserialized_message['rgb']}."
            )

            print(text)
            add_data_to_qdrant(text, ID)
            ID = ID + 1

            record_count += 1
            if record_count == 143:
                break  # Stop after processing 143 records

        except Exception as e:
            print(f"Failed to deserialize message: {e}")
    return record_count

# Calculate and print the elapsed time
elapsed_time = timeit.timeit(process_messages, number=1)
print(f"Time taken to process messages: {elapsed_time:.2f} seconds")

# Save the result to CSV
with open('qdrant-768.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["143", f"{elapsed_time:.2f}"])
