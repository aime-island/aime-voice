const WebSocket = require('ws');

let socket = new WebSocket('ws://localhost:9000/stream');

socket.on('open', () => {
    console.log('success');
    socket.send(JSON.stringify('start'));
});
socket.on('error', (e) => {
    console.log(e);
});
socket.on('close', () => {
    console.log('Tal socket disconnected');
});

socket.on('message', (message) => {
    console.log(message);
    //console.log();
});
