/* author: ijkilchenko@gmail.com
MIT license */

var template = $('#template').html(); // Hidden mustache template div. 
Mustache.parse(template);

// Save the jQuery objects to use later so jQuery doesn't have to re-query the dom. 
var $resultsList = $("#resultsList");
var $helpTips = $("#helpTips");
var $searchText = $("#searchText");
var $loadingIcon = $("#loadingIcon");
var $nothing = $("#nothing");
var $notReady = $("#notReady")

var resultSelectedIndex = 0; // Index of the active result (in green)., 
var lastMsg;
var lastSearchText = "";


// function handleResponse(message) {
//   updateResultsInPopup(message)
// }

// function handleError(error) {
//   console.log('Error: ${error}');
// }

function updateResultsInPopup(msg) {
	lastMsg = msg; // Save message (to be used when popup is reopened on a tab).
	// resultSelectedIndex = 0; // Set first result to be the active result (in green).
	
	console.log(lastSearchText)
	toSave = {'lastMsg' : msg.msg, "lastSearchText" : lastSearchText}
	console.log(toSave)
	var sending = browser.runtime.sendMessage({type: "save",
    	msg:toSave
  	});
  	sending.then();

	render(msg); // Update the mustache template.
}

function render(msg) {

	/* Partition the results into active and non-active results. */
	// var results = []
	var resultsBeforeSelected = [];
	var resultsSelected = [];
	var resultsAfterSelected = [];
	for (var i = 0; i < msg.msg.length; i++) {
		if(msg.msg[i].title == "")
			msg.msg[i].title = msg.msg[i].url

		resultsBeforeSelected.push(msg.msg[i])
	}

	// console.log("constructing msg");
	if(msg.msg == "not ready")
	{
		$resultsList.hide();
		$notReady.show();
		$nothing.hide();
		return;
	}
	var numResults = msg.msg.length;
	
	if (numResults > 0) {

		$resultsList.show();
		var EXACT_RESULT_THRESHOLD = 99;
		if (numResults > EXACT_RESULT_THRESHOLD) { // Whenever we get more than N results, we do not display the actual number.
			numResults = 'Many';
		}
		// console.log("yo homey this is th data I am sending back");
		var rendered = Mustache.render(template, {msg: {numResults : numResults,
			resultsBeforeSelected: resultsBeforeSelected, resultsSelected: resultsSelected, resultsAfterSelected: resultsAfterSelected}});
		$resultsList.html(rendered);
	} else{
		$resultsList.hide();
		$nothing.show();
		$notReady.hide();
	}
	$loadingIcon.hide(); // Popup is updated with results so hide the loadingIcon. 
}

function sendAndReceive() {
	var searchText = $searchText.val();

	if (searchText == "fuzbal help") { // If our searchText indicates we want to bring up the help menu. 
		$resultsList.hide(); // Hide the resultsList and show the helpTips instead. 
		$nothing.hide();
		$helpTips.show();
		$searchText.select();
		$notReady.hide();
	} else {
		$helpTips.hide(); // Make sure to hide the helpTips always when help menu is not indicated. 
		$nothing.hide();
		$notReady.hide();
		$loadingIcon.show();
		$resultsList.show();

  		var xhttp = new XMLHttpRequest();
    	xhttp.onload = function() {
      	var strings = JSON.parse(this.responseText)

	      	if (this.readyState == 4 && this.status == 200) {
	        	if(strings.msg.ready!=true)
	          		updateResultsInPopup({msg:"not ready"})
		        // console.log(strings.msg["urls"])

		        // console.log("in the search thing")
		        // console.log({msg:strings.msg["urls"]});
		        lastSearchText = searchText;
		        updateResultsInPopup({msg:strings.msg["urls"]});

      		}
    	};

	    xhttp.open("GET", "http://127.0.0.1:5000/query?query="+searchText, true);
	    xhttp.send();
	}
}

$('#searchText').keypress(function(e) {
	var keynum = e.keyCode||e.which;
	if(keynum == 13) {
		  sendAndReceive(); // Perform a search when a click and paste action is detected. 
	}
 
});
/* Do something special when the help icon is clicked. */
$("#help").on("click", function(e) {
	$searchText.val("fuzbal help");
	sendAndReceive();
});

function pageAction(message){
	// console.log(message)
	if(message)
	{
		$searchText.val(message.lastSearchText);
		$searchText.focus();
		render({msg:message.lastMsg});
	}
	else
	{
		$searchText.val("");
		$searchText.focus();
	}
}

/* Run this block when the popup is opened. */
window.onpageshow = function() {
	// console.log(lastSearchText)
	var sending = browser.runtime.sendMessage({type: "retr"
  	});
  	sending.then(pageAction);
};
