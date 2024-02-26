import {
    Admin,
    Resource,
    EditGuesser,
    defaultLightTheme,
    defaultDarkTheme,
    
} from 'react-admin';
import ChatBubbleIcon from '@mui/icons-material/ChatBubble';

import PI_Stream from './stream/PI_Stream';
 
function App() {
    return (
        <Admin
            lightTheme={defaultLightTheme}
            darkTheme={defaultDarkTheme}
        >
    
            <Resource
                name="webSocket"
                list={PI_Stream}
                icon={ChatBubbleIcon}
            />
            <Resource name="tags" recordRepresentation={tag => tag.name.en} />
        </Admin>
    );
}

export default App;
