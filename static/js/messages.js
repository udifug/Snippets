const messagesBox = document.getElementById('alertsFixedContainer');

messages = messagesBox.querySelectorAll('div');

function deleteMessage(message) {
    message.remove();
}

function deleteMessages() {
    let step = 1000;
    let numMessage = 1;
    for (let message of messages) {
        setTimeout(deleteMessage, 2000 + step * numMessage, message);
        numMessage++;
    }
}

deleteMessages();

