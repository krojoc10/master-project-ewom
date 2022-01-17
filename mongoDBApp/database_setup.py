from database_connection import connect_database
from pre_process_data import review_files_to_df, add_movie_sales_to_product_data, add_game_sales_to_product_data, add_album_sales_to_product_data, clean_data
from insert_data import insert_data
import datetime
import pandas as pd

#connect to database
startConnectionTime = datetime.datetime.now()
print(startConnectionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': connect to database')
db = connect_database()
endConnectionTime = datetime.datetime.now()
print(endConnectionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': database connection established')
connectionTime = datetime.timedelta.total_seconds(endConnectionTime - startConnectionTime)

#importing files and pre-processing
startPreprocessingTime = datetime.datetime.now()
print(startPreprocessingTime.strftime("%m/%d/%Y, %H:%M:%S") + ': read files and pre-process data')

#converting scraped review files to review dataframe
reviewData = review_files_to_df()

#filter movie data and add sales data
movieData = reviewData.where(reviewData['type']=='Movie').dropna(how='all')
movieData = add_movie_sales_to_product_data(movieData)

#filter game data and add sales data
gameData = reviewData.where(reviewData['type']=='Game').dropna(how='all')
gameData = add_game_sales_to_product_data(gameData)

#filter album data and add sales data
albumData = reviewData.where(reviewData['type']=='Album').dropna(how='all')
albumData = add_album_sales_to_product_data(albumData)

#concatenate and clean data
data = pd.concat([movieData, gameData, albumData])
data = clean_data(data)

endPreprocessingTime = datetime.datetime.now()
print(endPreprocessingTime.strftime("%m/%d/%Y, %H:%M:%S") + ': data ready for database import')
preprocessingTime = datetime.timedelta.total_seconds(endPreprocessingTime - startPreprocessingTime)

#importing data into database
startDBImportTime = datetime.datetime.now()
print(startDBImportTime.strftime("%m/%d/%Y, %H:%M:%S") + ': start database import')

#insert data into database
insert_data(data, db)

endDBImportTime = datetime.datetime.now()
print(endDBImportTime.strftime("%m/%d/%Y, %H:%M:%S") + ': data successfully imported')
dbImportTime = datetime.timedelta.total_seconds(endDBImportTime - startDBImportTime)

#calculate and print stats
stats = {
    'db_connection_time': connectionTime,
    'pre-processing_time': preprocessingTime,
    'db_import_time': dbImportTime,
    'db_overall_time': connectionTime + dbImportTime
}

print(stats)