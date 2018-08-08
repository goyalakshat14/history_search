from flask import Flask, request, jsonify
import requests
import re
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def cleanMe(html):
    soup = BeautifulSoup(html,"lxml") # create a new bs4 object from the html data loaded
    for script in soup(["script", "style"]): # remove all javascript and stylesheet code
        script.extract()
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip().lower() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = ' \n'.join(chunk for chunk in chunks if chunk)
    return text

@app.route('/')
@cross_origin()
def hello():
	url = request.args.get('url')
	r = requests.get(url = url)
	html = cleanMe(r.text)
	# print(html)
	
	return html

if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True, port=5000)
