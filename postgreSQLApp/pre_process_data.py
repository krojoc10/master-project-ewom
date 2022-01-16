from numpy import int64
import pandas as pd
import numpy as np

def review_files_to_df():
    #converting review input files to dataframes
    try:
        movieReviewData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\final_data\metacritic-movie-reviews-scrapy-data.json')
        gameReviewData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\final_data\metacritic-game-reviews-scrapy-data.json')
        albumReviewData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\final_data\metacritic-album-reviews-scrapy-data.json')
    except:
        print("Invalid file names")

    #merge review data and add productID
    reviewData = pd.concat([movieReviewData, gameReviewData, albumReviewData])
    reviewData.insert(0, 'productID', range(0, len(reviewData))) 
    reviewData['productID'] = reviewData['productID'].astype(int64)
    reviewData.index = reviewData['productID']

    return reviewData

def clean_product_data(df):
    #extract product data from data frame
    productData = df.drop(columns=['productUrlSegment', 'criticReviews', 'userReviews'])

    #clean missing values for userscore
    productData['userscore'].replace({'tbd': None}, inplace=True)

    #convert releaseDate to date format
    productData['releaseDate'].replace({'TBA': None}, inplace=True)
    productData['releaseDate'] = pd.to_datetime(productData['releaseDate'], format='%B %d, %Y', errors='coerce')

    #set data types
    productData = productData.astype({'productID': 'int64', 'productName': 'object', 'type': 'object', 'metascore': 'int64', 'userscore': 'float64', 'producer': 'object', 'releaseDate': 'datetime64', 'summary': 'object', 'sales': 'float64'})

    #final clean
    productData = productData.replace({np.NaN: None})
    productData = productData.drop_duplicates(subset=['productID'])

    return productData

def add_movie_sales_to_product_data(df):
    #converting sales input file to dataframes
    try:
        movieSalesData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\final_data\boxofficemojo-movie-sales-scrapy-data.json')
    except:
        print("Invalid file name")

    #prepare keys for matching
    df['releaseYear'] = df['releaseDate'].str.extract(r', (\d*)')
    df['movieName'] = df['productName']
    movieSalesData['releaseYear'] = movieSalesData['releaseYear'].astype(str)

    #add sales to product data based on name and release year
    df = pd.merge(left=df, right=movieSalesData, how='left', on=['movieName', 'releaseYear'])

    #clean new values
    df = df.drop(columns=['releaseYear', 'movieName'])
    df['sales'] = df['sales'].str.replace(r'$', '', regex=True)
    df['sales'] = df['sales'].str.replace(r',', '', regex=True)
    df['sales'] = df['sales'].astype(float)

    return df

def add_game_sales_to_product_data(df):
    #converting sales input file to dataframes
    try:
        gameSalesData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\final_data\vgChartz-game-sales-scrapy-data.json')
    except:
        print("Invalid file name")

    #removing rows with empty sales
    gameSalesData['sales'].replace({'N/A': None}, inplace=True)
    gameSalesData['sales'].replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=[None, None], regex=True, inplace=True)
    gameSalesData['sales'].replace({'0.00m': None}, inplace=True)
    gameSalesData = gameSalesData.dropna()

    #prepare keys for matching
    df['platform'] = df['productUrlSegment'].str.extract(r'(.*)\/')
    df['platform'] = df['platform'].replace({'playstation': 'PS', 'dreamcast': 'DC', 'gamecube': 'GC', 'playstation-3': 'PS3', 'xbox': 'XB', 'pc': 'PC', 'playstation-2': 'PS2', 'xbox-360': 'X360', 'switch': 'NS', 'wii-u': 'WiiU', 'psp': 'PSP', '3ds': '3DS', 'ds': 'DS', 'xbox-one': 'XOne', 'nintendo-64': 'N64', 'playstation-4': 'PS4', 'playstation-5': 'PS5', 'wii': 'Wii', 'playstation-vita': 'PSV', 'xbox-series-x': 'XS', 'game-boy-advance': 'GBA'})
    df['gameName'] = df['productName']
    gameSalesData['gameName'] = gameSalesData['gameName'].str.strip()
    gameSalesData = gameSalesData.drop(columns=['releaseDate'])
    
    #add sales to product data
    df = pd.merge(left=df, right=gameSalesData, how='left', on=['gameName', 'platform'])

    #clean new values
    df['sales'] = df['sales'].str.replace(r'm', '')
    df['sales'] = df['sales'].astype(float)
    df['sales'] = df['sales'] * 1000000
    df = df.drop(columns=['platform', 'gameName'])

    return df

def add_album_sales_to_product_data(df):
    df['sales'] = None

    return df

def extract_reviews_to_df(df):
    #remove unnecessary columns
    df = df.drop(columns=['productName', 'type', 'metascore', 'userscore', 'producer', 'releaseDate', 'summary', 'productUrlSegment'])

    #convert df to dict and create empty review list
    df_dict = df.to_dict('records')
    review_list = []

    #loop through df_dict and append reviews to review_list
    for row in df_dict:
        productID = row['productID']
        for review in row['criticReviews']:
            review.update({'productID': productID, 'type': 'criticReview'})
            review_list.append(review)
        for review in row['userReviews']:
            review.update({'productID': productID, 'type': 'userReview'})
            review_list.append(review)

    #convert review_list to df
    reviews = pd.DataFrame(review_list)

    #add reviewID
    reviews.insert(0, 'reviewID', range(0, len(reviews))) 
    reviews['reviewID'] = reviews['reviewID'].astype(int64)
    reviews.index = reviews['reviewID']

    return reviews

def clean_review_data(df):
    #drop rows with empty data
    df = df.dropna(subset=['author', 'score', 'reviewText'])

    #clean review text
    df['reviewText'] = df['reviewText'].str.strip()

    #convert releaseDate to date format
    df['dateCreated'] = pd.to_datetime(df['dateCreated'], format='%b %d, %Y', errors='coerce')

    #set data types
    df = df.astype({'reviewID': 'int64', 'author': 'object', 'score': 'int64', 'reviewText': 'object', 'productID': 'int64', 'type': 'object', 'dateCreated': 'datetime64'})

    #final clean
    df = df.replace({np.NaN: None})
    df = df[['reviewID', 'type', 'author', 'dateCreated', 'score', 'reviewText', 'productID']]

    return df