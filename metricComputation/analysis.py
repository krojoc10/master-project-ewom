from database_connection import connect_database, load_data_from_db
import datetime
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import mstats
import matplotlib.pylab as plt

#get data from database and save in dataframe
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': create dataframe with data from database')
db = connect_database()
data = load_data_from_db(db)
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': dataframe created')

#calculate mean sentimentScore per product and merge with sales data
sentiScore = data[['_id', 'sentimentScore']].copy()
sentiScore = sentiScore.dropna(subset=['sentimentScore'])
sentiScore = sentiScore.groupby(['_id']).mean()
sales = data[['_id', 'sales']].copy()
sales = sales.drop_duplicates(subset=['_id'])
sales = sales.dropna(subset=['sales'])
sentiScoreSales = sentiScore.merge(sales, how='inner', on='_id')

#correlation testing: sentiment score - sales
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': Correlation analysis: Sentiment score - sales')
sentiScoreSales = sentiScoreSales.drop(columns=['_id'])
sentiScoreSales['sentimentScore'] = np.float64(sentiScoreSales['sentimentScore'])
sentiScoreSales['sales'] = np.float64(sentiScoreSales['sales'])
correlation, pValue = mstats.pearsonr(sentiScoreSales['sentimentScore'], sentiScoreSales['sales'])
print('correlation coefficient (r):')
print(correlation)
print('p-value:')
print('{:0.30f}'.format(pValue))

#calculate review breadth per product and merge with sales data
topicCon = data.drop(columns=['author', 'score', 'reviewText', 'sentimentScore', 'sales', 'reviewType', 'dateCreated'])
topicCon = topicCon.groupby(['_id']).mean()
topicCon['reviewBreadth'] = topicCon.count(axis=1)
reviewBreadthSales = topicCon.merge(sales, how='inner', on='_id')
reviewBreadthSales = reviewBreadthSales[['_id', 'reviewBreadth', 'sales']]

#correlation testing: sentiment score - sales
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': Correlation analysis: Review breadth - sales')
reviewBreadthSales = reviewBreadthSales.drop(columns=['_id'])
reviewBreadthSales['reviewBreadth'] = np.int64(reviewBreadthSales['reviewBreadth'])
reviewBreadthSales['sales'] = np.float64(reviewBreadthSales['sales'])
correlation, pValue = mstats.pearsonr(reviewBreadthSales['reviewBreadth'], reviewBreadthSales['sales'])
print('correlation coefficient (r):')
print(correlation)
print('p-value:')
print('{:0.30f}'.format(pValue))

#calculate topic depth
topicDepth = data.drop(columns=['author', 'score', 'reviewText', 'sentimentScore', 'sales', 'reviewType', 'dateCreated', '_id'])
topicDepth = topicDepth.notnull().sum()