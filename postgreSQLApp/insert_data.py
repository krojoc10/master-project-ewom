import pandas as pd

def insert_product_data(df, cur):
    #insert data into database
    productRecord = [tuple(x) for x in df.to_numpy()]
    productInsertQuery = '''INSERT INTO Product
        (productID, name, type, metascore, userscore, producer, releaseDate, summary, sales)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    cur.executemany(productInsertQuery, productRecord)