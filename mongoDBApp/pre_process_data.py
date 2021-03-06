from numpy import int64
import pandas as pd
import numpy as np

def review_files_to_df():
    #converting review input files to dataframes
    try:
        movieReviewData = pd.read_json(input('Enter path to movie review data: '))
        gameReviewData = pd.read_json(input('Enter path to game review data: '))
        albumReviewData = pd.read_json(input('Enter path to album review data: '))
    except:
        print("Invalid file names")

    #merge review data and add productID
    reviewData = pd.concat([movieReviewData, gameReviewData, albumReviewData])

    return reviewData

def clean_data(df):
    #drop unnecessary columns
    df = df.drop(columns=['productUrlSegment'])

    #clean missing values for userscore
    df['userscore'].replace({'tbd': None}, inplace=True)

    #convert releaseDate to date format
    df['releaseDate'].replace({'TBA': None}, inplace=True)
    df['releaseDate'] = pd.to_datetime(df['releaseDate'], format='%B %d, %Y', errors='coerce')

    #convert df to dict
    df_dict = df.to_dict('records')

    #loop through df_dict and clean review data
    for row in df_dict:
        for review in row['criticReviews']:
            review.update({'reviewText': str(review['reviewText']).strip()})
        for review in row['userReviews']:
            review.update({'reviewText': str(review['reviewText']).strip(), 'dateCreated': pd.to_datetime(review['dateCreated'], format='%b %d, %Y', errors='coerce')})

    #convert df_dict to df
    df = pd.DataFrame(df_dict)

    #final clean
    df = df.replace({np.NaN: None})

    return df

def add_movie_sales_to_product_data(df):
    #converting sales input file to dataframes
    try:
        movieSalesData = pd.read_json(input('Enter path to movie sales data: '))
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
        gameSalesData = pd.read_json(input('Enter path to game sales data: '))
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