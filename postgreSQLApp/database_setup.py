from database_connection import connect_database, close_database
from create_tables import create_tables
from pre_process_data import review_files_to_df, add_movie_sales_to_product_data, clean_product_data, add_game_sales_to_product_data, add_album_sales_to_product_data
from insert_data import insert_product_data

#connect to database
conn = connect_database()
cur = conn.cursor()

#implementing db structure
create_tables(cur)

#converting scraped review files to review dataframe
reviewData = review_files_to_df()

#filter movie data, add sales data and clean
movieProductData = reviewData.where(reviewData['type']=='Movie').dropna(how='all')
movieProductData = add_movie_sales_to_product_data(movieProductData)
movieProductData = clean_product_data(movieProductData)

#insert movie data into database
insert_product_data(movieProductData, cur)

#filter game data, add sales data and clean
gameProductData = reviewData.where(reviewData['type']=='Game').dropna(how='all')
gameProductData = add_game_sales_to_product_data(gameProductData)
gameProductData = clean_product_data(gameProductData)

#insert game data into database
insert_product_data(gameProductData, cur)

#filter album data and clean
albumProductData = reviewData.where(reviewData['type']=='Album').dropna(how='all')
albumProductData = add_album_sales_to_product_data(albumProductData)
albumProductData = clean_product_data(albumProductData)

#insert album data into database
insert_product_data(albumProductData, cur)

#update database
conn.commit()

#closing database connection.
close_database(conn, cur)