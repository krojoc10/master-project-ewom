from database_connection import connect_database, close_database
from create_tables import create_tables
from pre_process_data import review_files_to_df, add_movie_sales_to_product_data, clean_product_data, add_game_sales_to_product_data, add_album_sales_to_product_data, extract_reviews_to_df, clean_review_data
from insert_data import insert_product_data, insert_review_data
import datetime

#connect to database
startConnectionTime = datetime.datetime.now()
print(startConnectionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': connect to database')
conn = connect_database()
cur = conn.cursor()
endConnectionTime = datetime.datetime.now()
print(endConnectionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': database connection established')
connectionTime = datetime.timedelta.total_seconds(endConnectionTime - startConnectionTime)

#implementing db scheme
startCreateDBSchemeTime = datetime.datetime.now()
print(startCreateDBSchemeTime.strftime("%m/%d/%Y, %H:%M:%S") + ': create database scheme')
create_tables(cur)
endCreateDBSchemeTime = datetime.datetime.now()
print(endCreateDBSchemeTime.strftime("%m/%d/%Y, %H:%M:%S") + ': database scheme implemented')
createDBSchemeTime = datetime.timedelta.total_seconds(endCreateDBSchemeTime - startCreateDBSchemeTime)

#importing files and pre-processing
startPreprocessingTime = datetime.datetime.now()
print(startPreprocessingTime.strftime("%m/%d/%Y, %H:%M:%S") + ': read files and pre-process data')

#converting scraped review files to review dataframe
reviewData = review_files_to_df()

#filter movie data, add sales data and clean
movieProductData = reviewData.where(reviewData['type']=='Movie').dropna(how='all')
movieProductData = add_movie_sales_to_product_data(movieProductData)
movieProductData = clean_product_data(movieProductData)

#filter game data, add sales data and clean
gameProductData = reviewData.where(reviewData['type']=='Game').dropna(how='all')
gameProductData = add_game_sales_to_product_data(gameProductData)
gameProductData = clean_product_data(gameProductData)

#filter album data and clean
albumProductData = reviewData.where(reviewData['type']=='Album').dropna(how='all')
albumProductData = add_album_sales_to_product_data(albumProductData)
albumProductData = clean_product_data(albumProductData)

#extract reviews as dataframe and clean
reviews = extract_reviews_to_df(reviewData)
reviews = clean_review_data(reviews)

endPreprocessingTime = datetime.datetime.now()
print(endPreprocessingTime.strftime("%m/%d/%Y, %H:%M:%S") + ': data ready for database import')
preprocessingTime = datetime.timedelta.total_seconds(endPreprocessingTime - startPreprocessingTime)

#importing data into database
startDBImportTime = datetime.datetime.now()
print(startDBImportTime.strftime("%m/%d/%Y, %H:%M:%S") + ': start database import')

#insert movie data into database
insert_product_data(movieProductData, cur)

#insert game data into database
insert_product_data(gameProductData, cur)

#insert album data into database
insert_product_data(albumProductData, cur)

#insert review data into database
insert_review_data(reviews, cur)

endDBImportTime = datetime.datetime.now()
print(endDBImportTime.strftime("%m/%d/%Y, %H:%M:%S") + ': data successfully imported')
dbImportTime = datetime.timedelta.total_seconds(endDBImportTime - startDBImportTime)

#update database
startCommitTime = datetime.datetime.now()
print(startCommitTime.strftime("%m/%d/%Y, %H:%M:%S") + ': commit changes and close database connection')
conn.commit()

#closing database connection
close_database(conn, cur)
endCommitTime = datetime.datetime.now()
print(endCommitTime.strftime("%m/%d/%Y, %H:%M:%S") + ': changes commited and database connection closed')
commitTime = datetime.timedelta.total_seconds(endCommitTime - startCommitTime)

#calculate and print stats
stats = {
    'db_connection_time': connectionTime,
    'db_scheme_time': createDBSchemeTime,
    'pre-processing_time': preprocessingTime,
    'db_import_time': dbImportTime,
    'db_commit_time': commitTime,
    'db_overall_time': connectionTime + createDBSchemeTime + dbImportTime + commitTime
}

print(stats)