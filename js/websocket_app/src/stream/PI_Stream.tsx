import React, { useState } from 'react';

function PI_Stream() {
    const [displayText, setDisplayText] = useState('');
    const [websocket, setWebsocket] = useState(null);
    const [websocketUrl, setWebsocketUrl] = useState('ws://localhost:8080/ws');
    const [connectionStatus, setConnectionStatus] = useState('Not Connected'); // "Connected" or "Not Connected"

    const handleConnectDisconnect = () => {
        // Disconnect if already connected
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.close(); // This will trigger the onclose event
            return;
        }

        // Connect if not connected
        const ws = new WebSocket(websocketUrl);

        ws.onopen = () => {
            console.log('WebSocket connection established');
            setConnectionStatus('Connected');
        };

        ws.onmessage = (event) => {
            const response = JSON.parse(event.data);
            if (response.processed_text !== undefined) {
                setDisplayText(response.processed_text);
            }
        };

        ws.onerror = (error) => {
            console.log('WebSocket error:', error);
            setConnectionStatus('Not Connected');
        };

        ws.onclose = () => {
            console.log('WebSocket connection closed');
            setConnectionStatus('Not Connected');
        };

        setWebsocket(ws);
    };

    const handleInputChange = (event) => {
        const inputText = event.target.value;
        if (/\s$/.test(inputText)) {
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify({ text: inputText }));
            }
        }
    };

    return (
        <div>
            <h2>Streaming Example</h2>
            <div style={{ marginBottom: '20px' }}>
                <label htmlFor="websocketUrl" style={{ marginRight: '10px' }}>Private AI Websocket URL:</label>
                <input
                    id="websocketUrl"
                    type="text"
                    value={websocketUrl}
                    onChange={(e) => setWebsocketUrl(e.target.value)}
                    placeholder="WebSocket URL"
                    style={{ marginRight: '10px', padding: '5px', width: '300px' }}
                />
                <button onClick={handleConnectDisconnect} style={{ marginRight: '10px', padding: '5px 10px' }}>
                    {connectionStatus === 'Connected' ? 'Disconnect' : 'Connect'}
                </button>
                <span style={{ padding: '5px', backgroundColor: connectionStatus === 'Connected' ? '#d4edda' : '#f8d7da', color: connectionStatus === 'Connected' ? '#155724' : '#721c24', borderRadius: '5px' }}>
                    {connectionStatus}
                </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '20px' }}>
                <textarea
                    style={{ width: '30%', height: '500px', resize: 'none' }}
                    onChange={handleInputChange}
                />
                <div style={{ width: '30%', height: '500px', overflow: 'auto', border: '1px solid #ccc', padding: '10px' }}>
                    <p>{displayText}</p>
                </div>
            </div>
        </div>
    );
}

export default PI_Stream;
