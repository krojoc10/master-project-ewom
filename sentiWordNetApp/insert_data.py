def insert_data(data, db):
    #split data into critic and user reviews
    criticReviews = data[data['reviewType'] == 'critic']
    userReviews = data[data['reviewType'] == 'user']
    #insert data into database
    criticReviews = criticReviews.to_dict('records')
    for row in criticReviews:
        db.product_reviews.update_one({'_id': row['_id'], 'criticReviews': {'$elemMatch': { 'author': row['author']}}}, {'$set': {'criticReviews.$.sentimentScore': row['sentimentScore']}})
    userReviews = userReviews.to_dict('records')
    for row in userReviews:
        db.product_reviews.update_one({'_id': row['_id'], 'userReviews': {'$elemMatch': { 'author': row['author']}}}, {'$set': {'userReviews.$.sentimentScore': row['sentimentScore']}})
     