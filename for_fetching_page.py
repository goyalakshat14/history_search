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
 		self.ready = False
	def set(self,urls):
		self.urls = urls

	def run(self):
		self.index = load_obj(pickle_name_idx)
		self.proccd_url = load_obj(pickle_name_proccd_url)
		no_url = len(self.urls)
		i=1
		beforeRqst = time.time()
		for item in self.urls:
			url = item["url"]
			# print(str(i)+"/"+str(no_url))
			# print(url)
			if not any(x in url for x in tabo):
				try:
					if not url in self.proccd_url:
						r = requests.get(url = url)
						html = clean_me(r.text)
						for text in html:
							if not text in self.index:
								self.index[text] = []
							
							self.index[text].append(item)
						self.proccd_url.add(url)
				except Exception as ex:
					print(ex)
			i+=1
		save_obj(self.index,pickle_name_idx)
		save_obj(self.proccd_url,pickle_name_proccd_url)
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
		return {}
	elif name==pickle_name_proccd_url:
		return set()


def clean_me(html):
	# beforeBS = time.time()
	soup = BeautifulSoup(html,"lxml") # create a new bs4 object from the html data loaded
	for script in soup(["script", "style"]): # remove all javascript and stylesheet code
		script.extract()
	
	text = soup.get_text()

	lines = (line.strip() for line in text.splitlines())
	chunks = (phrase.strip().lower() for line in lines for phrase in line.split("  "))
	text = ' '.join(chunk for chunk in chunks if chunk)
	word_tokens = word_tokenize(text)
	filtered_sentence = [w for w in word_tokens if not w in stop_words]
	text = list(set(filtered_sentence))
	text = list(set([lmtzr.lemmatize(word) for word in text]))
	return text

def retrieve(queries):
	word_tokens = word_tokenize(queries)
	filtered_sentence = [w for w in word_tokens if not w in stop_words]
	text = list(set(filtered_sentence))
	text = list(set([lmtzr.lemmatize(word) for word in text]))

	to_return = []
	order = {}
	for tex in text:
		if tex in indexing.index:
			for item in indexing.index[tex]: 
				if item["url"] in order:
					order[item["url"]][1] += 1
				else:
					order[item["url"]] = [item,1]

	for value in order.values():
		temp = [value[0],value[1]]
		to_return.append(temp)

	to_return = sorted(to_return, key=lambda x:x[1], reverse=True)
	return [row[0] for row in to_return]

		


@app.route('/', methods=['POST'])
@cross_origin()
def indexi():
	# print(type(request.json))
	urls = json.loads(request.data)
	urls = urls["urls"]
	
	indexing.set(urls)
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
	to_return = {"ready" : indexing.ready}
	urls = retrieve(queries)
	# print(urls)
	to_return["urls"] = urls
	return jsonify(msg=to_return)

indexing = MyThread()
if __name__ == '__main__':
	app.run(host= '0.0.0.0', debug=True, port=5000)
	
