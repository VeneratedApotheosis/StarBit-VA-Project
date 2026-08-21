const WebSocket = require('ws');
const protobuf = require('protobufjs');
const readline = require('readline');

async function connectClient() {
    const root = await protobuf.load('frames.proto');
    const Frame = root.lookupType('pipecat.Frame'); 

    const ws = new WebSocket('ws://localhost:7860/ws', {
        headers: {
            origin: 'http://localhost'
        }
    });

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
        prompt: 'User: '
    });

    ws.on('open', () => {
        rl.prompt();
        
        rl.on('line', (line) => {
            const payload = {
                transcription: {
                    text: line,
                    userId: 'user',
                    timestamp: Date.now().toString()
                }
            };
            const message = Frame.create(payload);
            ws.send(Frame.encode(message).finish());
        });
    });

    ws.on('message', (data) => {
        const decodedFrame = Frame.decode(data);
        
        // Extract text from Pipecat TextFrame
        if (decodedFrame.text && decodedFrame.text.text) {
            console.log('\nBot:', decodedFrame.text.text);
            rl.prompt();
        }
    });

    ws.on('close', () => {
        console.log('\nConnection closed.');
        rl.close();
        process.exit(0);
    });

    ws.on('error', (error) => {
        console.error('\nWebSocket Error:', error);
    });
}

connectClient();