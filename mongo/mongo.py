from pymongo import MongoClient

from mongo.config import connection_string
from models.database import Database

client = MongoClient(connection_string)

def add_database(db: Database):
    if db.db_name in client.list_database_names():
        raise ValueError("Database already exists")

    new_db = client[db.db_name]
    new_collection = new_db[db.collection_name]
    if len(db.data) == 1:
        new_collection.insert_one(db.data[0])
    elif len(db.data) > 1:
        new_collection.insert_many(db.data)

def delete_database(db_name: str):
    client.drop_database(db_name)


