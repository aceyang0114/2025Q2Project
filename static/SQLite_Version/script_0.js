const socket = io();

function sendData() {
    const input = document.getElementById('input');
    const text = input.value.trim();
    if (text === "") return;

    socket.emit('submit_data', { text: text });
    input.value = "";
}

socket.on('new_data', function(data) {
    const li = document.createElement('li');
    li.textContent = data.text;
    document.getElementById('messages').appendChild(li);
});
