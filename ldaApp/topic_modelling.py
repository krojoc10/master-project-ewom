from database_connection import connect_database, load_data_from_db
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import gensim
import gensim.corpora as corpora
from gensim.models import CoherenceModel
import datetime
import re

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

#build model
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': build model')
lda_model = gensim.models.LdaMulticore(corpus=corpus,
                                       id2word=id2word,
                                       num_topics=10,
                                       random_state=100,
                                       chunksize=100,
                                       passes=10,
                                       per_word_topics=True)
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ': model built')

#save model to disk
path_to_model = ""
lda_model.save(path_to_model)

#compute coherence score
coherence_model_lda = CoherenceModel(model=lda_model, texts=reviews, dictionary=id2word, coherence='c_v')
coherence_lda = coherence_model_lda.get_coherence()
print(coherence_lda)