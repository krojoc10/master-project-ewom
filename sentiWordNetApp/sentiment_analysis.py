from database_connection import connect_database, load_data_from_db
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.corpus import sentiwordnet
from nltk.tokenize import word_tokenize
import numpy as np
import datetime

#function to classify words according to pos-tag
def nltk_pos_tagger(nltkTag):
    if nltkTag.startswith('J'):
        return wordnet.ADJ
    elif nltkTag.startswith('V'):
        return wordnet.VERB
    elif nltkTag.startswith('N'):
        return wordnet.NOUN
    elif nltkTag.startswith('R'):
        return wordnet.ADV
    else:          
        return None

#function to get sentiment for each word - tag pair
def get_sentiment(word, tag):
    #classify words according to pos-tag
    tag = nltk_pos_tagger(tag)
    
    #return empty list if tag is None
    if tag is None:
        return []

    #lemmatize word, return empty list if lemma is empty
    lemmatizer = WordNetLemmatizer()
    lemma = lemmatizer.lemmatize(word, pos=tag)
    if not lemma:
        return []

    #get according synsets from wordnet, return empty list if no sysets are found
    synsets = wordnet.synsets(lemma, pos=tag)
    if not synsets:
        return []

    #take the most common synset to get the according synset from sentiwordnet
    synset = synsets[0]
    synset = sentiwordnet.senti_synset(synset.name())

    #return synset scores
    return [synset.pos_score(), synset.neg_score()]

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

#calculate review sentiment scores
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': calculate review sentiment scores')
data_dict = data.to_dict('records')
reviewSentimentScores = []
for review in data_dict:
    #tokenize words
    list = word_tokenize(review['reviewText'])
    #get pos-tag for every word
    posTags = nltk.pos_tag(list)
    #get sentiment scores for all word-tag pairs
    wordSentiments = [get_sentiment(x,y) for (x,y) in posTags]
    #sum up positive and negative scores
    pos = 0
    neg = 0
    count = 0
    for score in wordSentiments:
        try:
            pos = pos + score[0]  
            neg = neg + score[1]
            count = count + 1
        except:
            #continue if list is empty
            continue
    #append review sentiment score
    try:
        reviewSentimentScores.append((pos - neg) / count)
    except:
        reviewSentimentScores.append(None)

#add sentiment score to dataframe
data['sentimentScore'] = reviewSentimentScores
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': review sentiment scores added')

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': extract sentiment from sentiment score, sentiment label from meta/user-score and compare')
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
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': finished')

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