
//for populating the dictionary of words in the history
function onGot(historyItems) {
  for (item of historyItems) {
    console.log(item)
    // console.log(item.url);
    // console.log(item.title);
    
    var xhttp = new XMLHttpRequest();
  	xhttp.onload = function() {
      console.log(this.status);
    	if (this.readyState == 4 && this.status == 200) {
        // console.log(this.responseText)
        var splitted = this.responseText.split("\n")
    	  for(var line in splitted){
          var temp = splitted[line].split(" ")
         for(var text in temp){
            // console.log(temp[text]); 
            if(temp[text] in index){
              index[temp[text]][item.lastVisitTime] = item;
            }
            else{
              index[temp[text]] = {};
              index[temp[text]][item.lastVisitTime] = item;
            }
        }
      }
      
    	}
    };

    xhttp.open("GET", "http://127.0.0.1:5000/?url="+item.url, true);
  	
    console.log("sending request");
  	xhttp.send(null);
  }
  ready = true;

}
var ready = false

var index = {};

var searching = browser.history.search({
   text: "",
   startTime: 0,
   maxResults: 50
});

searching.then(onGot);


//for listening to any request
browser.runtime.onMessage.addListener(function(request,sender,sendResponse){
  console.log(ready);
  if(request.type == "search" && ready ==true)
  {

    console.log("yoho someone needs to know I am alive :"+request.greeting);
    console.log(request.query)
    console.log(index)
    if(request.query in index){
      console.log("hello")
      console.log(index[request.query])
      sendResponse({msg:index[request.query]});
    }
    // sendResponse({msg:"I am fine my darling"});
  }
    sendResponse("not ready");
});
