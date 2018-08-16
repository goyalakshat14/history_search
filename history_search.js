
var index = {};
var terms = {};
//for populating the dictionary of words in the history
function onGot(historyItems) {
  urls = []

  for (const [ key, value ] of Object.entries(historyItems)){
    urls.push(value)
  }

  var xhttp = new XMLHttpRequest();
  xhttp.onload = function() {
    if (this.readyState == 4 && this.status == 200) {
      // var strings = JSON.parse(this.responseText)
      console.log(this.responseText)
    }
  };

  xhttp.open("POST", "http://127.0.0.1:5000/", true);
  jo = {"urls":urls}
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.send(JSON.stringify(jo));
}

var searching = browser.history.search({
   text: "",
   startTime: 0,
   maxResults: 1000
});

searching.then(onGot);

var lastMsg={};

browser.runtime.onMessage.addListener(function(request,sender,sendResponse){

  if(request.type == "save"){
    // console.log("I am in save");
  // console.log(request.msg)
    lastMsg = request.msg
  }
});

browser.runtime.onMessage.addListener(function(request,sender,sendResponse){
  
  if(request.type == "retr")
  {
    // console.log("I am in retr");
    sendResponse(lastMsg)
  }  
  
});
  