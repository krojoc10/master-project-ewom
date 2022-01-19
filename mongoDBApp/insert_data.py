def insert_data(data, db):
    #drop collection if existent
    col = db['product_reviews']
    col.drop()

    #insert data into database
    db.product_reviews.insert_many(data.to_dict('records'))