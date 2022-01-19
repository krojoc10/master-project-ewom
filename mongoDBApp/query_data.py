from database_connection import connect_database
import datetime
import pandas as pd

#connect to database
startConnectionTime = datetime.datetime.now()
print(startConnectionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': connect to database')
db = connect_database()
endConnectionTime = datetime.datetime.now()
print(endConnectionTime.strftime("%m/%d/%Y, %H:%M:%S") + ': database connection established')
connectionTime = datetime.timedelta.total_seconds(endConnectionTime - startConnectionTime)

#get data records as list
startFindTime = datetime.datetime.now()
print(startFindTime.strftime("%m/%d/%Y, %H:%M:%S") + ': find data records')
dataRecords = list(db.product_reviews.find())
endFindTime = datetime.datetime.now()
print(endFindTime.strftime("%m/%d/%Y, %H:%M:%S") + ': data records found')
findTime = datetime.timedelta.total_seconds(endFindTime - startFindTime)

#create dataframe from dataRecords
startCreateDFTime = datetime.datetime.now()
print(startCreateDFTime.strftime("%m/%d/%Y, %H:%M:%S") + ': create dataframe with data records')
criticReviews = pd.json_normalize(dataRecords, 'criticReviews', ['productName', 'type', 'metascore', 'userscore', 'producer', 'releaseDate', 'summary', 'sales'])
userReviews = pd.json_normalize(dataRecords, 'userReviews', ['productName', 'type', 'metascore', 'userscore', 'producer', 'releaseDate', 'summary', 'sales'])
df = pd.concat([criticReviews, userReviews])
endCreateDFTime = datetime.datetime.now()
print(endCreateDFTime.strftime("%m/%d/%Y, %H:%M:%S") + ': dataframe created')
createDFTime = datetime.timedelta.total_seconds(endCreateDFTime - startCreateDFTime)

#calculate and print stats
stats = {
    'db_connection_time': connectionTime,
    'find_time': findTime,
    'create_dataframe_time': createDFTime
}

print(stats)