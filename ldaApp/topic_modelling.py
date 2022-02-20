from database_connection import connect_database, load_data_from_db
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import gensim
import gensim.corpora as corpora
from gensim.models import CoherenceModel
import datetime
import re
import matplotlib.pylab as plt

#get data from database and save in dataframe
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': create dataframe with data from database')
db = connect_database()
data = load_data_from_db(db)
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': dataframe created')

print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': start preprocessing')
#drop entries with empty review text
data = data[data['reviewText'] != 'None']

#convert text to lowercase
reviews = data['reviewText'].str.lower()

#remove punctuation
reviews = reviews.map(lambda x: re.sub('[,\.!?]', '', x))

#remove stop words
stopWords = stopwords.words('english')
reviews = reviews.apply(lambda x: ' '.join([word for word in x.split() if word not in (stopWords)]))

#tokenize text
reviews = reviews.apply(lambda x: word_tokenize(x))
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': preprocessing done')

#create dictionary and corpus
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': create dictionary and corpus')
id2word = corpora.Dictionary(reviews)
corpus = [id2word.doc2bow(review) for review in reviews]
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': dictionary and corpus created')

#evaluate models based on different number of topics
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': evaluate models')
def model_evaluation(k):
    #build model
    lda_model = gensim.models.LdaModel(corpus=corpus,
                                    id2word=id2word,
                                    num_topics=k,
                                    chunksize=10000,
                                    passes=1,
                                    per_word_topics=True)
    #compute coherence score
    coherence_model_lda = CoherenceModel(model=lda_model, corpus=corpus, coherence='u_mass')
    return coherence_model_lda.get_coherence()

min_topics = 205
max_topics = 255
step_size = 5
topics_range = range(min_topics, max_topics, step_size)

modelResults = {}

for k in topics_range:
    c = model_evaluation(k)
    modelResults.update({k:c})
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': models evaluated')

#print and plot results
print(modelResults)
x, y = zip(*modelResults.items())
plt.plot(x, y)
plt.show()