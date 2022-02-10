from database_connection import connect_database, load_data_from_db
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
import numpy as np
import datetime
import time

#get data from database and save in dataframe
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': create dataframe with data from database')
db = connect_database()
data = load_data_from_db(db)
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': dataframe created')

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': start preprocessing')
#drop entries with empty review text
data = data[data['reviewText'] != 'None']

#convert text to lowercase
data['reviewText'] = data['reviewText'].str.lower()

#remove stop words
stopWords = stopwords.words('english')
data['reviewText'] = data['reviewText'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stopWords)]))
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': preprocessing done')

#create sentiment label from review scores
data = data.dropna(subset=['score'])
data['score'] = data['score'].astype(int)
conditions = [
    (data['reviewType'] == 'critic') & (data['score'] < 50),
    (data['reviewType'] == 'critic') & (data['score'] >= 50),
    (data['reviewType'] == 'user') & (data['score'] < 5),
    (data['reviewType'] == 'user') & (data['score'] >= 5)
    ]
values = ['negative', 'positive', 'negative', 'positive']
data['sentimentLabel'] = np.select(conditions, values)

#split data into train and test
train_data, test_data = train_test_split(data, test_size=0.2)
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': preprocessing done')

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': vectorize review text')
#create feature vectors
vectorizer = TfidfVectorizer()
train_vectors = vectorizer.fit_transform(train_data['reviewText'])
test_vectors = vectorizer.transform(test_data['reviewText'])
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': review text vectorized')

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': train and test model')
#perform classification
classifier_linear = svm.SVC(kernel='linear')
t0 = time.time()
classifier_linear.fit(train_vectors, train_data['sentimentLabel'])
t1 = time.time()
prediction_linear = classifier_linear.predict(test_vectors)
t2 = time.time()
time_linear_train = t1-t0
time_linear_predict = t2-t1
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': model trained and tested')

#stats
print("Training time: %fs; Prediction time: %fs" % (time_linear_train, time_linear_predict))
report = classification_report(test_data['sentimentLabel'], prediction_linear, output_dict=True)
print('stats: ', report)