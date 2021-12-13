import psycopg2

def connect_database():
    try:
    #define db access
        connection = psycopg2.connect(user = "test",
                                      password = "test123",
                                      host = "localhost",
                                      port = "5433",
                                      database = "test")
        return connection
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)

def close_database(connection, cursor):
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")