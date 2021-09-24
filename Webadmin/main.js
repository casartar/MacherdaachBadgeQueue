
        // Globally initializes an mqtt variable
        const clientId = 'webadmin_' + Math.random().toString(16).substr(2, 8)
currentNumber = 0
const host = 'ws://ztl@ztl-mqtt.westeurope.azurecontainer.io:15675/ws'
var serverUrl   = 'ws://ztl@ztl-mqtt.westeurope.azurecontainer.io:15675/ws';     /* wss://mqtt.cumulocity.com/mqtt for a secure connection */
var device_name = "Webadmin";
var username    = "ztl";
var password    = "Ztl2019!";

var undeliveredMessages = [];
var temperature = 25;

// configure the client to Cumulocity
var client = new Paho.MQTT.Client(serverUrl, clientId);

// display all incoming messages
client.onMessageArrived = function (message) {
    log('Received operation "' + message.payloadString + '"');
    if (message.payloadString.indexOf("510") == 0) {
        log("Simulating device restart...");
        publish("s/us", "501,c8y_Restart");
        log("...restarting...");
        setTimeout(function() {
            publish("s/us", "503,c8y_Restart");
        }, 1000);
        log("...done...");
    }
};

// display all delivered messages
client.onMessageDelivered = function onMessageDelivered (message) {
    log('Message "' + message.payloadString + '" delivered');
    var undeliveredMessage = undeliveredMessages.pop();
    if (undeliveredMessage.onMessageDeliveredCallback) {
        undeliveredMessage.onMessageDeliveredCallback();
    }
};

function getStatus () {
  client.subscribe("macherdaach/queue/messageFromController");
  client.subscribe("macherdaach/queue/messageFromPlace");
  console.log('ready');
}

// send a message
function publish (topic, message, onMessageDeliveredCallback) {
    message = new Paho.MQTT.Message(message);
    message.destinationName = topic;
    message.qos = 2;
    undeliveredMessages.push({
        message: message,
        onMessageDeliveredCallback: onMessageDeliveredCallback
    });
    client.send(message);
}

// connect the client to Cumulocity
function init () {
    client.connect({
        userName: username,
        password: password,
        onSuccess: getStatus
    });
}

// display all messages on the page
function log (message) {
    document.getElementById('logger').insertAdjacentHTML('beforeend', '<div>' + message + '</div>');
}

init();
function nextUser(){
  
override = $('#nextnum').val();
if (override != currentNumber){
message= {
  "new_number":override
};
}else{
  message= {
  "new_number":currentNumber
};
currentNumber++;
}
publish('macherdaach/queue/messageFromPlace', 
JSON.stringify(message));
$('#nextnum').val(currentNumber);
console.log('NEXT')
}
function TableStart(tablenum){
  message = {
  "place_number": tablenum,
  "place_occupied": true
}
 publish('macherdaach/queue/messageFromPlace',JSON.stringify(message))
 $("#table-"+tablenum+'> span').addClass('bg-info');
}
function TableEnd(tablenum){
  message = {
  "place_number": tablenum,
  "place_occupied": false
}
 publish('macherdaach/queue/messageFromPlace',JSON.stringify(message));
$("#table-"+tablenum+'> span').removeClass('bg-info');
}