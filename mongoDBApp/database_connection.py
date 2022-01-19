from pymongo import MongoClient

def connect_database():
    #connect to database
    client = MongoClient('localhost', 27017)
    db = client['test']

    return db