import psycopg2

def connect_database():
    try:
    #define db access
        connection = psycopg2.connect(user = input('Enter database user: '),
                                      password = input('Enter database password: '),
                                      host = "localhost",
                                      port = "5433",
                                      database = input('Enter database name: '))
        return connection
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)

def close_database(connection, cursor):
    if(connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")