from typing import List

from pymongo import MongoClient

client = MongoClient('mongodb://nraboy:password1234@localhost:27017/')

def rename_db(old_db_name, new_db_name):

    if new_db_name in client.list_database_names():
        return

    db = client[old_db_name]
    collections: List[str] = db.list_collections()
    for collection_name in collections:
        collection = db[collection_name]


