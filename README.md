# The extension that enables you to remember the forgotten

1. `for_fetching_page.py` is the python server that processes the query and have the index of all the websites in your history.
2. `manifest.json` is the config file of your extension.
3. `history_search.js` is the backgrund script of extension that feed history links to firefox.
4. popup directory contains all the files related to the pop where you enter your query.
5. To run this extension first start the python server with :-  
	`python for_fetching_page.py`
6. now if you are using firefox then open the browser and type:  
	`about:debugging`
7. click on load Temporary add-on and select manifest.json file from this folder.  
8. else if you are using chrome then visit:  
	`chrome://extensions/` 
9. check the option developer mode.
10. click on load unpacked extension and select this folder to load the extension
11. you are good to go now give it some time to fetch all the links and click on the magnifying glass icon that will appear and start your journey down the memory lane.
