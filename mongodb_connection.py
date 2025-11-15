from pymongo import MongoClient
import os

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "dpc_project")

_client = MongoClient(MONGODB_URI)
_db = _client[MONGODB_DB_NAME]


def get_client() -> MongoClient:
    return _client


def get_db():
    return _db
