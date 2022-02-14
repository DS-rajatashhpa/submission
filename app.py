from flask import Flask, render_template, url_for,request,redirect
from textblob import TextBlob
import pandas as pd
import sqlite3
from textblob.classifiers import NaiveBayesClassifier, NLTKClassifier
app = Flask(__name__)

#converting datframe into list of values and looping through them to convert them into blobs for analysis
#text blobs are strings with additional nlp benifits
def sentiment(data):
    review = data['body']
    a= []
    c= []
    for i in review:
        textblob = TextBlob(i)
        a.append(textblob)
    for i in textblob.sentences:
        c = i.sentiment
        print(c)
    if c.polarity < 0:
        return 1
    else:
        return 0

#base url
@app.route('/')
def home():
    return render_template('home.html')

#enter review to predict their sentiments
@app.route('/predict',methods = ['POST'])
def predict():
    if request.method == 'POST':
        message = request.form['message']
        data = [message]
        frame = pd.DataFrame([data], columns= ['body'])
        a = sentiment(frame)
    return render_template('results.html', prediction = a)

@app.route('/form', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        qury = request.form['search']
        return redirect(url_for("review", query=qury))
    else:
        return render_template('index.html')

#displaying the results of the query into an unordered list of items using jinja2 features

@app.route('/<query>', methods=['GET','POST'])
def review(query):
    conn = sqlite3.connect('reviev.db', check_same_thread=False)
    c = conn.cursor()
    size1 = query.rjust(len(query)+1)
    color = query
    model=query.rjust(len(query)+1)
    a = []
    c.execute("SELECT bdy FROM neatdata WHERE size = ? OR color = ? OR model= ?",[size1,color,model])
    items = c.fetchall()
    for i in items:
        a.append(i)
    return render_template('result.html', A=a)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    app.secret_key = b'_5#y2L"F4Q8z\n\xec2]/'
