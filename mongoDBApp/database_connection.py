from pymongo import MongoClient

def connect_database():
    #connect to 
    client = MongoClient('localhost', 27017)
    db = client.test
    return db