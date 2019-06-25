from nltk.corpus import stopwords
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from nltk.collocations import *
from nltk.tokenize import RegexpTokenizer
import datetime
import itertools
try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")

qoute_page = []
count_dict = {}

count_dict["phrases"] = []
count_dict["total"] = []

# to search
print("Enter a google search: ")
query = input()
print("Enter number of search result you want: ")
Num_results = input()
for j in search(query, tld="com", num= 10, stop= int(Num_results) , pause=3.5):
    qoute_page.append(j)
print(qoute_page)
for i ,  url in enumerate(qoute_page):

    count_dict["count_ {}".format(url)] = []
for i ,  url in enumerate(qoute_page):

    req = requests.get(url)
    print(req)
    html = req.text
    soup = BeautifulSoup(html, "html5lib")
    text = soup.body('style')
    for tag in text:
        tag.decompose()
    text = soup.body('table')
    for t in text:
        t.decompose()
    text = soup.body('script')
    for t in text:
        t.decompose()
    try:
        text = soup.find('div').getText()
    except Exception as e:
        print(e)
        print("the website you are trying to reach is blocking scraping")
    newtxt =  re.sub('[0-9]+<[^<]+?>', '', text)
    newtxt1 = re.sub("\d+", "", newtxt)
    tokenizer = RegexpTokenizer('\w+')
    tokens = tokenizer.tokenize(str(newtxt1))
    extra_stopwords = ['http', 'https', 'www', 'fr', 'com', 'io', 'org', 'co', 'jo', 'edu', 'news', 'html', 'htm', \
     'github', 'youtube', 'google', 'blog', 'watch', 'de', 'le', 'la', 'en', 'sur', 'vous', 'les', \
     'ajouter', 'README', 'md', 'et', 'PROCESS', 'CMYK', 'des', 'chargement', 'playlists', 'endobj', \
     'obj', 'est', 'use', 'using', 'will', 'web', 'pour', 'du', 'une', 'que','displaypricelist','displayprice']

    stop_words = stopwords.words('english') + extra_stopwords
    french_stopwords = stopwords.words('french') + extra_stopwords
    filtered_sentence = [w.lower() for w in tokens if not w in set(stop_words).union(french_stopwords) and len(w) > 3 and len(w) < 20 and not w.isdigit()]
    trifinder = TrigramCollocationFinder.from_words(filtered_sentence, window_size=5)
    Bifinder = BigramCollocationFinder.from_words(filtered_sentence)

    for p , c in zip(trifinder.ngram_fd.items(),Bifinder.ngram_fd.items()):
        if p not in count_dict["phrases"]:
            count_dict["phrases"].append(p[0])
            count_dict["phrases"].append(c[0])
            count_dict["total"].append(p[1])
            count_dict["total"].append(c[1])
            for j in range(len(qoute_page)):
                if j == i :
                    count_dict["count_ {}".format(url)].append(p[1])
                    count_dict["count_ {}".format(url)].append(c[1])
                else:
                    count_dict["count_ {}".format(url)].append(0)
        else:

            index = count_dict["phrases"].index(p[0])
            count_dict["count_ {}".format(url)][index] = c[1]
            count_dict["total"][index] += c[1]
tridf = pd.DataFrame.from_dict(count_dict, orient='index').transpose().reset_index()
#tridf = tridf.transpose()
tridf = tridf.dropna(axis='rows')
tridf = tridf.sort_values(by='total', ascending=False, na_position='first')
print(tridf.iloc[:,1:])

if not len(tridf) == 0:
    tridf.iloc[:,1:].to_csv(str(query) + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '.csv')
else:
    print("Cannot find any result or the website are blocking scrapers")