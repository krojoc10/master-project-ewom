from numpy import int64
import pandas as pd

def review_files_to_df():
    #converting review input files to dataframes
    try:
        movieReviewData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\metacritic-movie-reviews-scrapy-data.json')
        gameReviewData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\metacritic-game-reviews-scrapy-data.json')
        albumReviewData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\metacritic-album-reviews-scrapy-data.json')
    except:
        print("Invalid file names")

    #merge review data and add productID
    reviewData = pd.concat([movieReviewData, gameReviewData, albumReviewData])
    reviewData.insert(0, 'productID', range(1, len(reviewData) + 1)) 
    reviewData['productID'] = reviewData['productID'].astype(int64)
    reviewData.index = reviewData['productID']

    return reviewData

def clean_product_data(df):
    #extract product data from data frame
    productData = df.drop(columns=['productUrlSegment', 'criticReviews', 'userReviews'])

    #clean missing values for userscore
    productData['userscore'].replace({'tbd': None}, inplace=True)

    #set data types
    productData = productData.astype({'productID': 'int64', 'productName': 'object', 'type': 'object', 'metascore': 'int64', 'userscore': 'float64', 'producer': 'object', 'summary': 'object'})

    return productData

def add_movie_sales_to_product_data(df):
    #converting sales input file to dataframes
    try:
        movieSalesData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\boxofficemojo-movie-sales-scrapy-data.json')
    except:
        print("Invalid file name")

    #removing duplicates
    movieSalesData.drop_duplicates(subset='movieName', inplace=True)

    #add sales to product data
    df = pd.merge(left=df, right=movieSalesData, how='left', left_on='productName', right_on='movieName')

    #clean new values
    df = df.drop(columns=['movieName'])
    df['sales'] = df['sales'].str.replace(r'$', '')
    df['sales'] = df['sales'].str.replace(r',', '')
    df['sales'] = df['sales'].astype(float)

    return df

def add_game_sales_to_product_data(df):
    #converting sales input file to dataframes
    try:
        gameSalesData = pd.read_json(r'C:\Users\kropf\Documents\master-project-ewom\scrapingResults\vgChartz-game-sales-scrapy-data.json')
    except:
        print("Invalid file name")

    #removing rows with empty sales and duplicates
    gameSalesData['sales'].replace({'N/A': None}, inplace=True)
    gameSalesData['sales'].replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=[None, None], regex=True, inplace=True)
    gameSalesData['sales'].replace({'0.00m': None}, inplace=True)
    gameSalesData = gameSalesData.dropna()
    gameSalesData.drop_duplicates(subset='gameName', inplace=True)

    #clean name column
    gameSalesData['gameName'] = gameSalesData['gameName'].str.strip()
    
    #add sales to product data
    df = pd.merge(left=df, right=gameSalesData, how='left', left_on='productName', right_on='gameName')

    #clean new values
    df['sales'] = df['sales'].str.replace(r'm', '')
    df['sales'] = df['sales'].astype(float)
    df['sales'] = df['sales'] * 1000000
    df = df.drop(columns=['gameName', 'publisher'])

    return df
