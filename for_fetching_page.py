from flask import Flask, request, jsonify
import requests
import re
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
import time
import sys
import nltk
import cPickle as pickle
from threading import Thread
from pathlib2 import Path
from whoosh.index import create_in,open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
import os, os.path



if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
try:
	ix = open_dir("indexdir")
except Exception as ex:
	schema = Schema(title=TEXT(stored=True), url=ID(stored=True), content=TEXT(stored=True))
	ix = create_in("indexdir",schema)	



lmtzr = WordNetLemmatizer()
nltk.download('wordnet')

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

stop_words = set(stopwords.words('english'))

tabo = [".zip", ".mp4", ".mkv", ".jpeg", ".tar", ".gz", "google.", "youtube.", "amazon.", ".run", "gmail.", ".deb"]
pickle_name_idx = "indexing"
pickle_name_proccd_url = "proccd_url"


class MyThread(Thread):
	def __init__(self):
		Thread.__init__(self)
 		self.ready = True
	def set(self,urls,ix):
		self.urls = urls
		self.ix = ix

	def run(self):
		self.ready = False
		self.index = load_obj(pickle_name_idx)
		self.proccd_url = load_obj(pickle_name_proccd_url)
		self.prev_urls = set(self.proccd_url)
		no_url = len(self.urls)
		i=1
		beforeRqst = time.time()
		for item in self.urls:
			url = item["url"]
			print(str(i)+"/"+str(no_url))
			print(url)
			if not any(x in url for x in tabo):
				try:
					if not url in self.proccd_url:
						r = requests.get(url = url)
						html = clean_me(r.text)
						temp = [item,html]
						self.index.append(temp)
						self.proccd_url.add(url)
				except Exception as ex:
					print(ex)
			i+=1

		save_obj(self.index,pickle_name_idx)
		save_obj(self.proccd_url,pickle_name_proccd_url)
		writer = self.ix.writer()
		with app.app_context():
			from flask import jsonify
			for indexe in self.index:
				if not indexe[0]["url"] in  self.prev_urls:
					writer.add_document(title=indexe[0]["title"],
									 url=indexe[0]["url"], 
				                    content=indexe[1].encode('utf-8', 'ignore').decode("utf-8"))
		writer.commit()
		print("indexing done")
		self.ready = True
		# print(html)
		afterRqst = time.time()
		print("afterRqst " + str(afterRqst - beforeRqst))

def save_obj(obj, name):
	with open('pickled/'+ name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
	if Path('pickled/' + name + '.pkl').is_file():
		with open('pickled/' + name + '.pkl', 'rb') as f:
			return pickle.load(f)
	elif name==pickle_name_idx:
		return []
	elif name==pickle_name_proccd_url:
		return set()


def clean_me(html):
	soup = BeautifulSoup(html,"lxml") # create a new bs4 object from the html data loaded
	for script in soup(["script", "style"]): # remove all javascript and stylesheet code
		script.extract()
	
	text = soup.get_text()
	lines = (line.strip() for line in text.splitlines())
	chunks = (phrase.strip().lower() for line in lines for phrase in line.split("  "))
	text = ' '.join(chunk for chunk in chunks if chunk)

	

	
	# word_tokens = word_tokenize(text)
	# filtered_sentence = [w for w in word_tokens if not w in stop_words]
	# text = list(set(filtered_sentence))
	# text = list(set([lmtzr.lemmatize(word) for word in text]))
	return text

def retrieve(queries):
	with ix.searcher() as searcher:
		query = QueryParser("content", ix.schema).parse(queries)
		results = searcher.search(query)
		# for row in results:
		# 	print(row.highlights("content"))
		return [[row["title"], row["url"], row.highlights("content",top=1)] for row in results]

@app.route('/', methods=['POST'])
@cross_origin()
def indexi():
	# print(type(request.json))
	urls = json.loads(request.data)
	urls = urls["urls"]
	
	indexing.set(urls,ix)
	indexing.start()

	return "recieved"
	# return jsonify(results=texts)

@app.route('/query',methods=['get'])
@cross_origin()
def query():
	queries = request.args.get('query')
	# print(queries)
	if(not indexing.ready):
		to_return = { "ready" : indexing.ready}
		return jsonify(msg=to_return)
	else:
		to_return = {"ready" : indexing.ready}
		urls = retrieve(queries)
		# print(urls)
		to_return["urls"] = urls
		return jsonify(msg=to_return)

indexing = MyThread()
if __name__ == '__main__':
	app.run(host= '0.0.0.0', debug=True, port=5000,threaded=True)
	
