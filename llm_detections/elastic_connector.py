import os
from elasticsearch import Elasticsearch
from datetime import datetime


# Elasticsearch configuration
ES_CLIENT = Elasticsearch(
    "http://localhost:9200",
    basic_auth=(os.getenv("ELASTIC_USER"), os.getenv("ELASTIC_PASSWORD")),
)
FAKE_UUID = "73330bca-9ec9-4569-ba3f-005751b63250"


def log_to_elasticsearch(log_data: dict):
    """Log the request and response data to Elasticsearch."""
    log_data.update({"@timestamp": datetime.now(), "connectorId": FAKE_UUID})
    res = ES_CLIENT.index(index="azure-openai-logs", body=log_data)
    print(f"Logged to Elasticsearch with result: {res['result']}")
