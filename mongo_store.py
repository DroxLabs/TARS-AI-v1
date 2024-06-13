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

    def get_total_cost_for_day(self, date):
        """
        Calculates the total cost for the specified date.
        """
        try:
            start_date = datetime(date.year, date.month, date.day)
            end_date = start_date + timedelta(days=1)
            pipeline = [
                {"$match": {"date": {"$gte": start_date, "$lt": end_date}}},
                {"$group": {"_id": None, "total_cost": {"$sum": "$cost"}}}
            ]
            result = list(self.collection.aggregate(pipeline))
            if result:
                total_cost = result[0]["total_cost"]
            else:
                total_cost = 0
            return total_cost
        except errors.ServerSelectionTimeoutError as err:
            print(f"Failed to connect to server during aggregation: {err}")
            return None
        except Exception as err:
            print(f"An error occurred while calculating total cost: {err}")
            return None

def main():
    mongo_pass = os.getenv("mongo_pass")
    try:
        mongo_store = MongoStore(f'mongodb+srv://abdul_samad:{mongo_pass}@tars-backend.fvg1suu.mongodb.net/')
        mongo_store.add_cost(100.50, "Purchase of office supplies", 'bahawal#bahawl')
        mongo_store.add_cost(3.50, "soemthing", 'samad')

        specific_date = datetime(2024, 6, 13)
        total_cost = mongo_store.get_total_cost_for_day(specific_date)
        print("Total cost for the specified date:", total_cost)
    except Exception as e:
        print(f"An error occurred in the main function: {e}")
        raise e

if __name__ == "__main__":
    main()