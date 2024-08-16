import { useEffect, useState } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

function Data_Stream() {
    const [displayText, setDisplayText] = useState('');
    const [websocketUrl, setWebsocketUrl] = useState('ws://localhost:8080/ws');
    const {
        sendJsonMessage,
        lastJsonMessage,
        readyState,
    } = useWebSocket(websocketUrl, {
        onOpen: () => console.log('opened'),
        shouldReconnect: () => true,
    });

    const connectionStatus = {
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState];

    const handleInputChange = (event: any) => {
        const inputText = event.target.value;
        if (/\s$/.test(inputText)) {
            if (readyState == ReadyState.OPEN) {
                console.log({ text: inputText });
                sendJsonMessage({ text: inputText });
            }
        }
    };

    useEffect(() => {
        if (lastJsonMessage) {
            setDisplayText(JSON.stringify(lastJsonMessage, undefined, 2))
        }
    }, [lastJsonMessage])

    return (
        <div style={{margin: '20px'}}>
            <h2>Private AI Streaming Example</h2>
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
                <span style={{ padding: '5px', backgroundColor: readyState === ReadyState.OPEN ? '#d4edda' : '#f8d7da', color: readyState !== ReadyState.OPEN ? '#155724' : '#721c24', borderRadius: '5px' }}>
                    {connectionStatus}
                </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '20px' }}>
                <textarea
                    style={{ width: '50%', height: '500px', resize: 'none', padding: '10px' }}
                    onChange={handleInputChange}
                />
                <div style={{ width: '50%', height: '500px', border: '1px solid #ccc', padding: '10px' }}>
                    <pre>{displayText}</pre>
                </div>
            </div>
        </div>
    );
}

export default Data_Stream;
