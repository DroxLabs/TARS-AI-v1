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

