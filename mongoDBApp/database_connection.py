from pymongo import MongoClient

def connect_database():
    #connect to database
    client = MongoClient('localhost', 27017)
    db = client['test']

    #drop collection if existent
    col = db['product_reviews']
    col.drop()

    return db