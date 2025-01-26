import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

def get_elasticsearch_client():
    """
    Initialize and return an Elasticsearch client.
    """
    # Local connection
    es = Elasticsearch(hosts=["http://localhost:9200"])

    es = Elasticsearch(
        cloud_id = os.getenv("ELASTICSEARCH_CLOUD_ID"),
        basic_auth=(os.getenv("ELASTICSEARCH_USER"), os.getenv("ELASTICSEARCH_PASSWD"))
    )

    if es.ping():
        print("Connected to Elasticsearch!")
    else:
        print("Failed to connect to Elasticsearch.")
    return es
