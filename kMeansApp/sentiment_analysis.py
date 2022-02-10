from database_connection import connect_database, load_data_from_db
import datetime
import pandas as pd
import numpy as np
from re import sub
import multiprocessing
from gensim.models.phrases import Phrases, Phraser
from gensim.models import Word2Vec
from sklearn.cluster import KMeans

#get data from database and save in dataframe
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': create dataframe with data from database')
db = connect_database()
data = load_data_from_db(db)
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': dataframe created')

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': start preprocessing')
#drop entries with empty review text
data = data[data['reviewText'] != 'None']

#convert reviewText to list of words
def text_to_word_list(text):
    text = str(text)
    text = text.lower()

    #clean text
    text = sub(r"[^A-Za-z0-9^,!?.\/'+]", " ", text)
    text = sub(r"\+", " plus ", text)
    text = sub(r",", " ", text)
    text = sub(r"\.", " ", text)
    text = sub(r"!", " ! ", text)
    text = sub(r"\?", " ? ", text)
    text = sub(r"'", " ", text)
    text = sub(r":", " : ", text)
    text = sub(r"\s{2,}", " ", text)

    text = text.split()

    return text

data.reviewText = data.reviewText.apply(lambda x: text_to_word_list(x))
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': preprocessing done')

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': create word2vec model')
#preparing data for word2vec training
sent = [row for row in data.reviewText]
phrases = Phrases(sent, min_count=1, progress_per=50000)
bigram = Phraser(phrases)
sentences = bigram[sent]

#create word2vec model
w2v_model = Word2Vec(min_count=3,
                     window=4,
                     vector_size=300,
                     sample=1e-5, 
                     alpha=0.03, 
                     min_alpha=0.0007, 
                     negative=20,
                     workers=multiprocessing.cpu_count()-1)

w2v_model.build_vocab(sentences, progress_per=50000)
w2v_model.train(sentences, total_examples=w2v_model.corpus_count, epochs=30, report_delay=1)
w2v_model.init_sims(replace=True)
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': word2vec model created')

#replace reviewText with bigrams
data.reviewText = data.reviewText.apply(lambda x: ' '.join(bigram[x]))

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': create k-means model')
#create kMeans model
word_vectors = w2v_model.wv
model = KMeans(n_clusters=2, max_iter=1000, random_state=True, n_init=50).fit(X=word_vectors.vectors.astype('double'))
positive_cluster_index = 1
positive_cluster_center = model.cluster_centers_[positive_cluster_index]
negative_cluster_center = model.cluster_centers_[1-positive_cluster_index]
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': k-means model created')

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': calculate sentiment score')
#calculate sentiment score based on distance to cluster centroids
wordSentiments = pd.DataFrame(word_vectors.index_to_key)
wordSentiments.columns = ['words']
wordSentiments['vectors'] = wordSentiments.words.apply(lambda x: word_vectors[f'{x}'])
wordSentiments['cluster'] = wordSentiments.vectors.apply(lambda x: model.predict([np.array(x)]))
wordSentiments.cluster = wordSentiments.cluster.apply(lambda x: x[0])
wordSentiments['cluster_value'] = [1 if i==positive_cluster_index else -1 for i in wordSentiments.cluster]
wordSentiments['closeness_score'] = wordSentiments.apply(lambda x: 1/(model.transform([x.vectors]).min()), axis=1)
wordSentiments['sentiment_coeff'] = wordSentiments.closeness_score * wordSentiments.cluster_value

#replace words with sentiment score
sentiment_dict = dict(zip(wordSentiments.words.values, wordSentiments.sentiment_coeff.values))

def replace_sentiment_words(word, sentiment_dict):
    try:
        out = sentiment_dict[word]
    except KeyError:
        out = 0
    return out
  
replaced_closeness_scores = data.reviewText.apply(lambda x: list(map(lambda y: replace_sentiment_words(y, sentiment_dict), x.split())))

#calculate review sentiment from sum of word sentiments
data['sentimentScore'] = replaced_closeness_scores.apply(lambda x: sum(x))
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': sentiment score calculated')

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': calculate performance metrics')
#create sentiment from sentiment score
conditions = [
    (data['sentimentScore'] < 0),
    (data['sentimentScore'] >= 0)
    ]
values = ['negative', 'positive']
data['sentiment'] = np.select(conditions, values)

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

#check if TP, FP, TN, or FN
conditions = [
    (data['sentiment'] == 'positive') & (data['sentimentLabel'] == 'positive'),
    (data['sentiment'] == 'positive') & (data['sentimentLabel'] == 'negative'),
    (data['sentiment'] == 'negative') & (data['sentimentLabel'] == 'negative'),
    (data['sentiment'] == 'negative') & (data['sentimentLabel'] == 'positive')
    ]
values = ['TP', 'FP', 'TN', 'FN']
data['sentimentResult'] = np.select(conditions, values)

#stats
accuracy = (len(data[data['sentimentResult'] == 'TP']) + len(data[data['sentimentResult'] == 'TN'])) / len(data[data['sentimentResult'] != None])
precision = len(data[data['sentimentResult'] == 'TP']) / (len(data[data['sentimentResult'] == 'TP']) + len(data[data['sentimentResult'] == 'FP']))
recall = len(data[data['sentimentResult'] == 'TP']) / (len(data[data['sentimentResult'] == 'TP']) + len(data[data['sentimentResult'] == 'FN']))
f1Score = 2 * (precision * recall) / (precision + recall)

stats = {
    'accuracy': accuracy,
    'precision': precision,
    'recall': recall,
    'f1-score': f1Score
}

print(stats)