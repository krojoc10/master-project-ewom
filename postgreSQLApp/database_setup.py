import pandas
from database_connection import connect_database, close_database
from create_tables import create_tables

#connect to database
conn = connect_database()
cur = conn.cursor()

#implementing db structure
create_tables(cur)

#reading files to dataframe
try:
    movieReviewData = pandas.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\metacritic-movie-reviews-scrapy-data.json')
except:
    print("Invalid file names")

#update database
conn.commit()

#closing database connection.
close_database(conn, cur)