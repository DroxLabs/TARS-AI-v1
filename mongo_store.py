from pymongo import MongoClient, errors
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

class MongoStore:
    def __init__(self, connection_string='your_connection_string_here', db_name='test', collection_name='totalcosts'):
        self.connection_string = connection_string
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            # Attempt to fetch server info to confirm connection
            self.client.server_info()
            print("Connected to MongoDB server successfully.")
        except errors.ServerSelectionTimeoutError as err:
            print(f"Failed to connect to server: {err}")
        except errors.ConnectionFailure as err:
            print(f"Connection failure: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")

    def add_cost(self, cost, description, user):
        """
        Inserts a document with the current date and time, cost, description, and user into the collection.
        """
        try:
            document = {
                "date": datetime.now(),
                "cost": cost,
                "description": description,
                "user": user
            }
            result = self.collection.insert_one(document)
            print(f"Document inserted with id: {result.inserted_id}")
            return result
        except Exception as err:
            print(f"An error occurred while adding cost: {err}")
            return None

