import pandas as pd
import sqlite3
from textblob import TextBlob
conn = sqlite3.connect('reviev.db')
df = pd.read_sql('SELECT * FROM neatdata', conn)

#joining all functions to calculate the best and worst words

def bestworstwords(df):
    raw = df['bdy']
    converted = conversion(raw)
    cleandata = convert(converted)
    sentenceandwordsentiments = wordandsent(cleandata)
    words = word(sentenceandwordsentiments, cleandata)
    return words


def conversion(rev):
    e = []
    for i in rev:
        e.append(i)
    return e
#splitting into words
def convert(lst):
    return ' '.join(lst).split()

#converting into a blob to get sentiment

def wordandsent(cleandata):
    fin = []
    for i in cleandata:
        newblob = TextBlob(i)
        fin.append(newblob)
    senti = []
    for i in fin:
        fword = i.sentiment.polarity
        senti.append(fword)
    return (senti)

#finding the sentiment and its positionin the frame and appending the words at the same index into a new frame

def word(senti, cleandata):
    c, e, d, f = ([] for i in range(4))
    for i in senti:
        if i < 0:
            a = senti.index(i)
            c.append(a)
        elif i > 0.2:
            b = senti.index(i)
            e.append(b)
    for i in cleandata:
        if cleandata.index(i) in c:
            d.append(i)
        elif cleandata.index(i) in e:
            f.append(i)
    return 'Most Worst words:', d, "  Best words:", f


print(bestworstwords(df))
