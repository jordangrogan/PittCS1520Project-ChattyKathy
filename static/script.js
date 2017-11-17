var timeoutID;
var timeout = 1000;
var room_id = getQueryVariable("room");
console.log("Room ID: " + room_id);

function setup() {
	/* Press the submit button to submit chat message */
	document.getElementById("submit").addEventListener("click", makePost, true);

	/* Press enter while in the text box to submit chat message */
	/* https://stackoverflow.com/questions/14542062/eventlistener-enter-key */
	document.getElementById("message").addEventListener("keypress", function (e) {
	  var key = e.which || e.keyCode;
	  if (key === 13) { // 13 is enter
	  	makePost();
	  }
	});

	document.getElementById("message").focus(); // Set focus to the message's textbox

	adjustScroll(); // Adjust the messages window to be scrolled to the bottom

	timeoutID = window.setTimeout(poller, timeout);
}

function makePost() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	var message = document.getElementById("message").value;
	httpRequest.onreadystatechange = function() { handlePost(httpRequest, message) };

	httpRequest.open("POST", "/api/messages/");

	var data = {};
	data["room_id"] = room_id;
	data["message"] = message;

	httpRequest.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

	httpRequest.send(JSON.stringify(data));
}

function handlePost(httpRequest, message) { /* need second parameter? */
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status >= 200 && httpRequest.status < 300) {
			document.getElementById("message").value = ""; // Clear input of message textbox
			document.getElementById("message").focus(); // Set focus to the message textbox
		} else {
			alert("There was a problem with the post request.");
		}
	}
}

function poller() {
	var httpRequest = new XMLHttpRequest();

	if (!httpRequest) {
		alert('Giving up :( Cannot create an XMLHTTP instance');
		return false;
	}

	httpRequest.onreadystatechange = function() { handlePoll(httpRequest) }; // Listener on http request to listen for changes to the state
	httpRequest.open("GET", "/api/messages/?room_id="+room_id);
	httpRequest.send();
}

function handlePoll(httpRequest) {
	if (httpRequest.readyState === XMLHttpRequest.DONE) {
		if (httpRequest.status === 200) {

			var rows = JSON.parse(httpRequest.responseText); // Parse the response of the json object we got back
			for (var i = 0; i < rows.length; i++) { // add all the rows from the response
				addMessage(rows[i]["username"], rows[i]["message"]);
				adjustScroll(); // Adjust the messages window to be scrolled to the bottom
			}

			timeoutID = window.setTimeout(poller, timeout);

		} else if(httpRequest.status === 404) { /* The room has been deleted. */
			window.location = "/error?error=1";
		} else if(httpRequest.status === 403) { /* The user entered another room, kick them out of this one. */
			window.location = "/error?error=2";
		} else {
			alert("There was a problem with the poll request.  you'll need to refresh the page to recieve updates again!");
		}
	}
}

/*	Adds message to the messages table */
function addMessage(username, message) {
	var tableRef = document.getElementById("messages");
	var newRow   = tableRef.insertRow();
	console.log("adding row: " + username);
	var usernameCell, messageCell, usernameText, messagetext;
	usernameCell  = newRow.insertCell();
	usernameCell.className = "username";
	usernameText  = document.createTextNode(username + ":");
	usernameCell.appendChild(usernameText);
	messageCell  = newRow.insertCell();
	messageText  = document.createTextNode(message);
	messageCell.appendChild(messageText);
}

/* 	Keep the messages container div scrolled to the bottom when new messages are available
 		https://stackoverflow.com/questions/270612/scroll-to-bottom-of-div */
function adjustScroll() {
	var messagesContainerDiv = document.getElementById("messagesContainer");
	messagesContainerDiv.scrollTop = messagesContainerDiv.scrollHeight;
}

/* 	Function to get URL query arguements, from:
		https://css-tricks.com/snippets/javascript/get-url-variables/ */
function getQueryVariable(variable)
{
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
       }
       return(false);
}

window.addEventListener("load", setup, true);
