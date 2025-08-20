import re
import unidecode
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

sw = stopwords.words('spanish')
snow = SnowballStemmer('spanish')

def limpiar(text):
    return [snow.stem(unidecode.unidecode(w)) for w in re.findall(r'[a-záéíóúñ]+',str(text).lower()) if (len(w)>=2) and (w not in sw)]

def vector_w2v(text,vectorizer):
    return np.mean([vectorizer.wv[word] for word in text if word in vectorizer.wv.key_to_index],axis=0)

def is_on_topic(article, topic_vector, threshold):
    similarity = cosine_similarity([topic_vector], [article])[0][0]
    return similarity >= threshold

news = pd.read_excel('scraper.xlsx',index_col=0)
news = news[(news['error'].isnull())]
news['body'] = news['body'].apply(lambda x: limpiar(x))

tokens = []
for row in news['body']:
    tokens.append(row)

vectorizer = Word2Vec(sentences=tokens, vector_size=200, window=4, min_count=10, sg=0, epochs=30)
news['w2v'] = news['body'].apply(lambda x: vector_w2v(x,vectorizer))

topics = []
for word, _ in vectorizer.wv.most_similar('salud',topn=50):
    topics.append(word)

for word, _ in vectorizer.wv.most_similar('enfermed',topn=50):
    topics.append(word)
topic_vector = np.mean([vectorizer.wv[word] for word in topics if word in vectorizer.wv], axis=0)

threshold = 0.35

news['ontopic'] = news['w2v'].apply(lambda x: is_on_topic(x,topic_vector,threshold))