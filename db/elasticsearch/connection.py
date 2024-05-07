import settings
from elasticsearch import Elasticsearch


def get_connection():
    return Elasticsearch([settings.ES_URL])
