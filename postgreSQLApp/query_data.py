from database_connection import connect_database, close_database
import psycopg2
import pandas as pd
import datetime

#connect to database
startConnectionTime = datetime.datetime.now()
print(startConnectionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': connect to database')
conn = connect_database()
cur = conn.cursor()
endConnectionTime = datetime.datetime.now()
print(endConnectionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': database connection established')
connectionTime = datetime.timedelta.total_seconds(endConnectionTime - startConnectionTime)

#select query
query = 'SELECT * FROM review LEFT JOIN product ON review.productID = product.productID;'

#execute query
startQueryExecutionTime = datetime.datetime.now()
print(startQueryExecutionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': execute select query')
try:
    cur.execute(query)
except (Exception, psycopg2.DatabaseError) as error:
    print("Error: %s" % error)
    cur.close()
endQueryExecutionTime = datetime.datetime.now()
print(endQueryExecutionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': select query executed')
queryExecutionTime = datetime.timedelta.total_seconds(endQueryExecutionTime - startQueryExecutionTime)
    
#get data records as tupples
startFetchTime = datetime.datetime.now()
print(startFetchTime.strftime("%m/%d/%Y, %H:%M:%S") + ': fetch data records and close database connection')
dataRecords = cur.fetchall()
close_database(conn, cur)
endFetchTime = datetime.datetime.now()
print(endFetchTime.strftime("%m/%d/%Y, %H:%M:%S") + ': data records fetched and database connection closed')
fetchTime = datetime.timedelta.total_seconds(endFetchTime - startFetchTime)

#create dataframe from dataRecords
startCreateDFTime = datetime.datetime.now()
print(startCreateDFTime.strftime("%m/%d/%Y, %H:%M:%S") + ': create dataframe with data records')
df = pd.DataFrame(dataRecords, columns=['reviewID', 'reviewType', 'reviewAuthor', 'reviewDate', 'reviewScore', 'reviewText', 'productID', 'productID_1', 'productName', 'productType', 'metascore', 'userscore', 'producer', 'releaseDate', 'productSummary', 'productSales'])
endCreateDFTime = datetime.datetime.now()
print(endCreateDFTime.strftime("%m/%d/%Y, %H:%M:%S") + ': dataframe created')
createDFTime = datetime.timedelta.total_seconds(endCreateDFTime - startCreateDFTime)

#calculate and print stats
stats = {
    'db_connection_time': connectionTime,
    'query_execution_time': queryExecutionTime,
    'fetch_time': fetchTime,
    'create_dataframe_time': createDFTime
}

print(stats)