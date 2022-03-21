# -*- coding: utf-8 -*-
"""LSTMModel.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1N9fyufhxo-6MQbDIk5JtAO76QtQJadYF
"""

#import of important Libraries
import numpy
import pandas as pd
import sys
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint
import regex as re
from numpy import character

"""# Data Loading"""

from google.colab import drive
drive.mount("/content/drive")

file = open('/content/drive/MyDrive/Workbook1.txt').read()

"""# Tokenization

filter the list of tokens and only keep the tokens that aren't in a list of Stop Words, or common words that provide little information about the sentence in question. I do this by using lambda to make a quick throwaway function and only assign the words to our variable if they aren't in a list of Stop Words provided by NLTK.Created the below function to handle it
"""

def tokenize_words(input):
    # lowercase everything to standardize it
    input = input.lower()

    # instantiate the tokenizer
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(input)

    # if the created token isn't in the stop words, make it part of "filtered"
    filtered = filter(lambda token: token not in stopwords.words('english'), tokens)
    return " ".join(filtered)

import nltk
nltk.download('stopwords')

"""Call the function on my data file"""

# preprocess the input data, make tokens
processed_inputs = tokenize_words(file)

"""convert the characters in our input to numbers for NN. I sort the list of the set of all characters that appear in the input text, then use the enumerate function to get numbers which represent the characters. then create a dictionary that stores the keys and values, or the characters and the numbers that represent them:"""

chars = sorted(list(set(processed_inputs)))
char_to_num = dict((c, i) for i, c in enumerate(chars))

"""I need the total length of our inputs and total length of the set of characters for later data prep, so I store these in a variable. Just so i get an idea of if my process of converting words to characters has worked thus far, I print the length of our variables:"""

input_len = len(processed_inputs)
vocab_len = len(chars)
print ("Total number of characters:", input_len)
print ("Total vocab:", vocab_len)

from sklearn.model_selection import train_test_split, cross_val_score

"""Now that I've transformed the data into the form it needs to be in, I begin making a dataset out of it, which I'll feed into the network. I need to define how long I want an individual sequence (one complete mapping of inputs characters as integers) to be. I set a length of 100 for now, and declare empty lists to store my input and output data:"""

seq_length = 100
x_data = []
y_data = []

"""I go through the entire list of inputs and convert the characters to numbers. I do this with a for loop. This will create a bunch of sequences where each sequence starts with the next character in the input data, beginning with the first character"""

# loop through inputs, start at the beginning and go until we hit
# the final character we can create a sequence out of
for i in range(0, input_len - seq_length, 1):
    # Define input and output sequences
    # Input is the current character plus desired sequence length
    in_seq = processed_inputs[i:i + seq_length]

    # Out sequence is the initial character plus total sequence length
    out_seq = processed_inputs[i + seq_length]

    # We now convert list of characters to integers based on
    # previously and add the values to our lists
    x_data.append([char_to_num[char] for char in in_seq])
    y_data.append(char_to_num[out_seq])

"""I have  input sequences of characters and output, which is the character that should come after the sequence ends. The training data features and labels, are stored as x_data and y_data. saved total number of sequences and check to see how many total input sequences I have:"""

n_patterns = len(x_data)
print ("Total Patterns:", n_patterns)

"""# Converting the Sequence"""



"""convert the input sequences into a processed numpy array that the network can use. Also convert the numpy array values into floats so that the sigmoid activation function  the network uses can interpret them and output probabilities."""

X = numpy.reshape(x_data, (n_patterns, seq_length, 1))
X = X/float(vocab_len)

y = np_utils.to_categorical(y_data)

"""# LSTM Model

specify the LSTM model to make (a sequential one), and then add our first layer. Used dropout to prevent overfitting, followed by another layer or two. Then added the final layer, a densely connected layer that will output a probability about what the next character in the sequence will be:
"""

model = Sequential()
model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(256, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(128))
model.add(Dropout(0.2))
model.add(Dense(y.shape[1], activation='softmax'))

"""# Model Compilation"""

model.compile(loss='categorical_crossentropy', optimizer='adam')

"""It took the model quite a while to train, and for this reason I save the weights and reload them when the training is finished. I set a checkpoint to save the weights to, and then make them the callbacks for future model."""

filepath = "model_weights_saved.hdf5"
checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
desired_callbacks = [checkpoint]

"""# Model Fitting

The loss was decreasing gradully by 18th epoch but started increasing again after it
"""

model.fit(X, y, epochs=20, batch_size=256, callbacks=desired_callbacks)

"""After it has finished training, I specify the file name and load in the weights. Then recompile the model with the saved weights:"""

filename = "model_weights_saved.hdf5"
model.load_weights(filename)
model.compile(loss='categorical_crossentropy', optimizer='adam')

"""Since I converted the characters to numbers earlier, I define a dictionary variable that will convert the output of the model back into numbers:"""

num_to_char = dict((i, c) for i, c in enumerate(chars))

"""To generate characters, i provide our trained model with a random seed character that it can generate a sequence of characters from:"""

start = numpy.random.randint(0, len(x_data) - 1)
pattern = x_data[start]
print("Random Seed:")
print("\"", ''.join([num_to_char[value] for value in pattern]), "\"")

!pip install rouge

for i in range(100):
    x = numpy.reshape(pattern, (1, len(pattern), 1))
    x = x / float(vocab_len)
    prediction = model.predict(x, verbose=0)
    index = numpy.argmax(prediction)
    result = num_to_char[index]

    sys.stdout.write(result)

    pattern.append(index)
    pattern = pattern[1:len(pattern)]

"""# Rouge """

# calculating ROGUE score , percsion and recall on a sample text
# passing a sample text from the data to see how model regenerate the text
from rouge import Rouge 
# Generated text
result= "pounds approved physician diet usually special diet prescribed craniotomy normal well balanced diet "
# origional text
reference = "The patient was admitted on [**2128-5-5**], and underwent right frontal craniotomy for excision of rightfrontal mass without intraoperative complication."

rouge = Rouge()
scores = rouge.get_scores(result, reference)
scores