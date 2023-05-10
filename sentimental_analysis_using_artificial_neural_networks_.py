# -*- coding: utf-8 -*-
"""Sentimental analysis using Artificial Neural Networks .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1O7xatSI2WINxZCxfvvXLg13CxF_e6dRY

## Twitter sentimetal anlysis through  a sample of "rolex watches" tweets Using Artificial Neural Networks.
"""

!pip install snscrape
import snscrape.modules.twitter as sntwitter
import pandas as pd
import numpy as np

query = "iphone 11"
tweets = []
limit = 5000


for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    
    # print(vars(tweet))
    # break
    if len(tweets) == limit:
        break
    else:
        tweets.append([tweet.date, tweet.username, tweet.content])
        
df = pd.DataFrame(tweets, columns=['Date','Username', 'Tweet'])
df.head()

# Check random tweet
df['Tweet'][66]

#df['Date'] = df['Date'].dt.strftime('%d')
#get rid of links and hashtags
df["Tweet"] = df["Tweet"].apply(lambda x : ' '.join([s for s in x.split(' ') if s.find('@') == -1 and s.find('www') == -1 and s.find('https') == -1]))

#get rid of non-ascii characters
df = df.replace(r'\W+', ' ', regex=True)
df['Tweet'][66]

!pip install spacytextblob

# Next i carried out the sentimental analysis on the Tweets using the latest version of spacy
# installing it
!pip install spacytextblob
!pip install spacy
!python -m textblob.download_corpora
!python -m spacy download en_core_web_sm

# Next i run the sentiment analysis on the tweets and appended the score to our dataframe:
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe("spacytextblob")

df['sentiment'] = df['Tweet'].apply(lambda x : nlp(x)._.polarity)
df = df.sort_values('sentiment').reset_index(drop=True)
df.head()

df

# Convert the sentiments to categorical data where values more than 0 are positive sentiments and values less than 0 are negative sentiments.


df['sentiment'] = ['positive' if sentiment > 0 else 'negative' for sentiment in df['sentiment']]

# create binary to represent positive and negative.
df['sentiment'] = np.select(
    [
        df['sentiment'] == "positive",
        df['sentiment'] == "negative"
    ],
    [
        1,
        0
    ]
)
df

# Apply first level cleaning
import re
import string

#This function converts to lower-case, removes square bracket, removes numbers and punctuation
def text_clean_1(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    return text

cleaned1 = lambda x: text_clean_1(x)
# Let's take a look at the updated text
df['cleaned_Tweets'] = pd.DataFrame(df.Tweet.apply(cleaned1))
df.head(10)

# Apply a second round of cleaning
def text_clean_2(text):
    text = re.sub('[‘’“”…]', '', text)
    text = re.sub('\n', '', text)
    return text

cleaned2 = lambda x: text_clean_2(x)
# Let's take a look at the updated text
df['cleaned_Tweets2'] = pd.DataFrame(df.Tweet.apply(cleaned1))
df.head(10)

# Artificial Neural Network Keras libaries imports

from keras.preprocessing.text import one_hot
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers.core import Activation, Dropout, Dense
from keras.layers import Flatten
from keras.layers import GlobalMaxPooling1D
from keras.layers.embeddings import Embedding
from sklearn.model_selection import train_test_split
from keras.preprocessing.text import Tokenizer

from keras.layers import InputLayer, Conv1D, Dense, Flatten, MaxPooling1D, LSTM

# Feature selection and extraction
X = df.cleaned_Tweets2
y = df.sentiment
# A count of the distribution of the sentiments 
print(np.unique(y, return_counts=True))

# Creating the Training and test sets with training set having 80%
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# Create a word to index dictionary
tokenizer = Tokenizer(num_words=10000)
tokenizer.fit_on_texts(X_train)

X_train = tokenizer.texts_to_sequences(X_train)
X_test = tokenizer.texts_to_sequences(X_test)

# Adding 1 because of reserved 0 index
vocab_size = len(tokenizer.word_index) + 1

maxlen = 100

X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)

!wget https://huggingface.co/stanfordnlp/glove/resolve/main/glove.6B.zip
!unzip glove*.zip
!pwd

from numpy import array
from numpy import asarray
from numpy import zeros

embeddings_dictionary = dict()
glove_file = open('glove.6B.100d.txt', encoding='utf-8')

for line in glove_file:
    records = line.split()
    word = records[0]
    vector_dimensions = asarray(records[1:], dtype='float32')
    embeddings_dictionary [word] = vector_dimensions
glove_file.close()

embedding_matrix = zeros((vocab_size, 100))
for word, index in tokenizer.word_index.items():
    embedding_vector = embeddings_dictionary.get(word)
    if embedding_vector is not None:
        embedding_matrix[index] = embedding_vector

"""## Text Classification with a Convolutional Neural Network"""

model = Sequential()
embedding_layer = Embedding(vocab_size, 100, weights=[embedding_matrix], input_length=maxlen , trainable=False)
model.add(embedding_layer)
model.add(Conv1D(filters=128, kernel_size=2, activation='relu'))
model.add(Dropout(0.5))
model.add(MaxPooling1D(pool_size=2))
model.add(Flatten())
model.add(Dense(12, activation='sigmoid'))
model.add(Dense(1, activation='sigmoid'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
print(model.summary())

history = model.fit(X_train, y_train, validation_data=(X_test,y_test), batch_size=128, epochs=10, verbose=1)

score = model.evaluate(X_test, y_test, verbose=1)

print("Test Score:", score[0])
print("Test Accuracy:", score[1])

import matplotlib.pyplot as plt

plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])

plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train','test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])

plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train','test'], loc='upper left')
plt.show()

"""## Text Classification with Recurrent Neural Network (LSTM)"""

model1 = Sequential()
embedding_layer = Embedding(vocab_size, 100, weights=[embedding_matrix], input_length=maxlen , trainable=False)
model1.add(embedding_layer)
model1.add(LSTM(128))
model1.add(Dense(12, activation='sigmoid'))
model1.add(Dense(1, activation='sigmoid'))


model1.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])
print(model1.summary())

history1 = model1.fit(X_train, y_train, batch_size=128, epochs=6, verbose=1, validation_split=0.2)

score = model1.evaluate(X_test, y_test, verbose=1)

print("Test Score:", score[0])
print("Test Accuracy:", score[1])

import matplotlib.pyplot as plt

plt.plot(history1.history['acc'])
plt.plot(history1.history['val_acc'])

plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train','test'], loc='upper left')
plt.show()

plt.plot(history1.history['loss'])
plt.plot(history1.history['val_loss'])

plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train','test'], loc='upper left')
plt.show()

"""## Testing the Models."""

# Enter tweet to predict sentiment
instance = "Rolex lovers are the worst people"
print(instance)
instance = tokenizer.texts_to_sequences(instance)

# CNN Prediction

flat_list = []
for sublist in instance:
    for item in sublist:
        flat_list.append(item)

flat_list = [flat_list]

instance = pad_sequences(flat_list, padding='post', maxlen=maxlen)

prediction = model.predict(instance)[0][0]
print(prediction)
# If the value is less than 0.5, the sentiment is considered negative where as if the value is greater than 0.5, the sentiment is considered as positive.
prediction = [1 if prediction > 0.5 else 0][0]
if prediction == 1:
  print(" Sentiment is Positive")
else:
  print(" Sentiment is Negative")

# LSTM Prediction

flat_list = []
for sublist in instance:
    for item in sublist:
        flat_list.append(item)

flat_list = [flat_list]

instance = pad_sequences(flat_list, padding='post', maxlen=maxlen)

prediction = model1.predict(instance)[0][0]
print(prediction)
# If the value is less than 0.5, the sentiment is considered negative where as if the value is greater than 0.5, the sentiment is considered as positive.
prediction = [1 if prediction > 0.5 else 0][0]
if prediction == 1:
  print(" Sentiment is Positive")
else:
  print(" Sentiment is Negative")