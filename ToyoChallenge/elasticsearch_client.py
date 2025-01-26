from elasticsearch import Elasticsearch

def get_elasticsearch_client():
    """
    Initialize and return an Elasticsearch client.
    """
    # Local connection
    es = Elasticsearch(hosts=["http://localhost:9200"])

    # Elastic Cloud (Uncomment and configure if using cloud)
    es = Elasticsearch(
        cloud_id="My_Elasticsearch_deployment:dXMtZWFzdC0yLmF3cy5lbGFzdGljLWNsb3VkLmNvbTo0NDMkNTdiMzdiNzU5NDg4NGVhNjkxZWViN2E2YmRiOGE1YTkkNzc5OWM3MTIxYTE2NDM3ZGJhNTdmYTdmMjVmY2MxYzQ=",
        basic_auth=("elastic", "uG22BS4JcmAWjg7y5rjUbiCJ")
    )

    if es.ping():
        print("Connected to Elasticsearch!")
    else:
        print("Failed to connect to Elasticsearch.")
    return es
