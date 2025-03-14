from datetime import datetime, timedelta

import pytest
from pymongo import MongoClient
from qdrant_client import QdrantClient


class TestDatabaseOperations:
    @pytest.fixture(scope="class")
    def setup_mongodb(self):
        # Setup MongoDB client
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo_client["your_database_name"]
        self.collection = self.db["your_collection_name"]

        # Insert test data
        today = datetime.now().date()
        self.collection.insert_many(
            [
                {"data": "test1", "update_date": today},
                {"data": "test2", "update_date": today},
                {"data": "test3", "update_date": today},
                {"data": "test4", "update_date": today - timedelta(days=1)},  # Not today
            ]
        )

        yield  # This allows the test to run

        # Teardown
        self.collection.delete_many({})  # Clean up the collection
        self.mongo_client.close()

    def test_fetch_data_from_mongodb(self, setup_mongodb):
        # Fetch documents with today's date
        today = datetime.now().date()
        fetched_documents = list(self.collection.find({"update_date": today}))

        # Assert that we have the expected number of documents
        assert len(fetched_documents) == 3  # Expecting 3 documents with today's date

    @pytest.fixture(scope="class")
    def setup_qdrant(self):
        # Setup Qdrant client
        self.qdrant_client = QdrantClient(url="http://localhost:6333")
        self.collection_name = "your_qdrant_collection_name"

        # Ensure the collection exists
        self.qdrant_client.recreate_collection(self.collection_name)

        yield  # This allows the test to run

        # Teardown
        self.qdrant_client.delete_collection(self.collection_name)

    def test_insert_documents_to_qdrant(self, setup_mongodb, setup_qdrant):
        # Fetch documents from MongoDB
        today = datetime.now().date()
        documents = list(self.collection.find({"update_date": today}))

        # Prepare data for Qdrant
        vectors = [{"id": str(doc["_id"]), "vector": [0.1, 0.2, 0.3], "payload": doc} for doc in documents]

        # Insert into Qdrant
        self.qdrant_client.upsert(collection_name=self.collection_name, points=vectors)

        # Verify insertion
        qdrant_documents = self.qdrant_client.retrieve(
            collection_name=self.collection_name, ids=[str(doc["_id"]) for doc in documents]
        )
        assert len(qdrant_documents) == len(documents)  # Ensure all documents are inserted
