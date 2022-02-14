from bs4 import BeautifulSoup
import requests
import time
import json
import pandas as pd
import sqlite3
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains

#searchamazon will get the correct url using which we are going to scrape reviews using seleniumwebdriver

def search_amazon(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    act = ActionChains(driver)
    driver.implicitly_wait(2)
    num_page = driver.find_element_by_link_text('See all reviews').click()
    time.sleep(3)
#    driver.switch_to.window(driver.window_handles[0])
    num_page1 = driver.find_element_by_partial_link_text('Next page').click()
    time.sleep(3)
    num_page2 = driver.find_element_by_partial_link_text('Next page').click()
    time.sleep(3)
    a = driver.current_url
    b = str(a)
    c = b.replace('=3','= {x}') #parameterizing the url
    return c

#converting the url

convertedurl = search_amazon('https://www.amazon.in/Apple-New-iPhone-12-128GB/dp/B08L5TNJHG/')

conn = sqlite3.connect('reviev.db')
c = conn.cursor()
#creating SQLite Database and Table
c.execute('''CREATE TABLE rawdata
        (stles TEXT,
        verfy TEXT,
        prdct TEXT,
        titl TEXT,
        ratng REAL, 
        bdy TEXT);''') #for raw data

c.execute('''CREATE TABLE neatdata
        (color TEXT,
        size TEXT,
        Variant Text,
        verfy TEXT,
        titl TEXT,
        ratng REAL, 
        bdy TEXT);''') #for clean data

reviewsbox  = []
HEADERS = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/90.0.4430.212 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

def get_soup(url):
    r = requests.get(url, params={'wait': 5}, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_reviews(soup):
    reviews = soup.find_all('div', {'data-hook': 'review'})
    try:
        for item in reviews:
            review = {
            'styles': item.find('a', {'data-hook': 'format-strip'}).text.strip(),
            'verify': item.find('span', {'data-hook': 'avp-badge'}).text.strip(),
            'product': soup.title.text.replace('Amazon.in', ''),
            'title': item.find('a', {'data-hook': 'review-title'}).text.strip(),
            'rating': float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()),
            'body': item.find('span', {'data-hook': 'review-body'}).text.strip(),
            }
            c.execute('''
                INSERT INTO
                rawdata
                    (stles,verfy,prdct,titl,ratng,bdy)
                VALUES
                    (:styles, :verify, :product, :title, :rating, :body)''', review)
            conn.commit()

    except:
        pass

for x in range(1,99):
    soup = get_soup(convertedurl)
    time.sleep(5)
    print(f'getting page no. {x}')
    get_reviews(soup)
    if not soup.find('li', {'class': 'a-disabled-a-last'}):
        pass
    else:
        break

rawdataframe = pd.read_sql('SELECT * FROM rawdata', conn)

#splitting the styles column into three different columns and inserting into dataframe
def style_splitter(df):
    raw = df['stles']
    sorted = []
    for i in raw:
        delimiter = re.sub("((Colour\:\s|\(PRODUCT\))|Size\sname\:|Pattern\sname\:)", ',', i)
        splitted = re.compile("\,+").split(delimiter)
        cleaneddata = list(filter(lambda el: el != "", splitted))
        sorted.append(cleaneddata)
    new_df = pd.DataFrame(columns=['color', 'size', 'model'], data=sorted)
    df1 = df.drop(['stles','bdy'], axis=1)
    fin = pd.concat([df1, new_df], axis=1)
    final = fin.dropna()
    return final

#cleaning the reviews and normalising it as per the basic english rules
def review_cleaner(semidone):
    texts = semidone['bdy']
    import re
    no_alphan = re.compile(r'[\W]')
    no_asc = re.compile(r'[^a-z0-1\s]')
    def normaliz(texts):
        normalized_texts = []
        for text in texts:
            lower = text.lower()
            no_punctu = no_alphan.sub(r' ',lower)
            no_non_ascii = no_asc.sub(r'', no_punctu)
            normalized_texts.append(no_non_ascii)
        return normalized_texts
    train_reviw = normaliz(texts)
    sortedreview = pd.DataFrame(train_reviw,columns=['bdy'])
    return sortedreview

#after preprocessing on data comverting it to final dataframe to make a new table
def final_joining(df):
    sortdata = style_splitter(df)
    sortreview = review_cleaner(df)
    finaldata = pd.concat([sortdata, sortreview], axis=1)
    return finaldata

neatdataframe = final_joining(rawdataframe)
print(neatdataframe.head())
neatdataframe.to_sql('neatdata', conn, if_exists='replace', index = False)
sorteddata = pd.read_sql('SELECT * FROM neatdata', conn)

print(sorteddata.head(5))