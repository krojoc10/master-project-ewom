import pandas as pd
from database_connection import connect_database, close_database
from create_tables import create_tables
from pre_process_data import review_files_to_df, add_movie_sales_to_product_data, clean_product_data, add_game_sales_to_product_data
from insert_data import insert_product_data

#connect to database
conn = connect_database()
cur = conn.cursor()

#implementing db structure
create_tables(cur)

#converting scraped review files to review dataframe
reviewData = review_files_to_df()

#filter movie data, clean it and add sales data
movieProductData = reviewData.where(reviewData['type']=='Movie').dropna()
movieProductData = clean_product_data(movieProductData)
movieProductData = add_movie_sales_to_product_data(movieProductData)

#filter game data, clean it and add sales data
gameProductData = reviewData.where(reviewData['type']=='Game').dropna()
gameProductData = clean_product_data(gameProductData)
gameProductData = add_game_sales_to_product_data(gameProductData)

#filter album data and clean it
albumProductData = reviewData.where(reviewData['type']=='Album').dropna()
albumProductData = clean_product_data(albumProductData)

#concenate product data
productData = pd.concat([movieProductData, gameProductData, albumProductData])

#insert product data into database
#insert_product_data(productData, cur)

#update database
conn.commit()

#closing database connection.
close_database(conn, cur)