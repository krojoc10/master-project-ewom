from pymongo import MongoClient
import pandas as pd

def connect_database():
    #connect to database
    client = MongoClient('localhost', 27017)
    db = client['test']

    return db

def load_data_from_db(db):
    #get data records as list
    dataRecords = list(db.product_reviews.find())

    #create dataframe from dataRecords
    criticReviews = pd.json_normalize(dataRecords, 'criticReviews', ['_id', 'sales'])
    criticReviews['reviewType'] = 'critic'
    userReviews = pd.json_normalize(dataRecords, 'userReviews', ['_id', 'sales'])
    userReviews['reviewType'] = 'user'
    df = pd.concat([criticReviews, userReviews])
    df = df.reset_index()
    df = df.drop(columns=['index'])

    return df