import psycopg2

def create_tables(cur):
    try:
        #deleting existing tables
        cur.execute('''DROP TABLE IF EXISTS ReviewTopic;
        DROP TABLE IF EXISTS Topic;
        DROP TABLE IF EXISTS Review;
        DROP TABLE IF EXISTS Product;''')

        #creating tables
        cur.execute('''CREATE TABLE Product
            (productID int PRIMARY KEY,
        	name text,
            type text,
            metascore int,
            userscore numeric,
            producer text,
            releaseDate date,
            summary text,
            sales numeric
            );
        CREATE TABLE Review
            (reviewID int PRIMARY KEY,
        	type boolean,
            author text,
            dateCreated date,
            score int,
            summary text,
            product int);''')
    except (Exception, psycopg2.Error) as error:
        print ("Error while creating database structure", error)