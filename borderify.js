document.body.style.border = "5px solid red";



function handleResponse(message) {
  console.log(message);
}

function handleError(error) {
  console.log(`Error: ${error}`);
}

function notifyBackgroundPage(query) {
	console.log("Hello i am alive");
  	var sending = browser.runtime.sendMessage({type: "search",
    	query:query
  	});
  	sending.then(handleResponse, handleError);  
}

browser.runtime.onMessage.addListener(function(request,sender,sendResponse){
	if(request.type== "query"){
		notifyBackgroundPage(request.query)
	}
});