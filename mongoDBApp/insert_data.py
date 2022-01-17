def insert_data(data, db):
    #insert data into database
    db.product_reviews.insert_many(data.to_dict('records'))