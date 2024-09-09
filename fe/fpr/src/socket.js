import { io } from 'socket.io-client';

// "undefined" means the URL will be computed from the `window.location` object
const URL = process.env.NODE_ENV === 'production' ? 'wss://gamesby.jeffr.ee:8443' : 'http://localhost:9069';

export const socket = io(URL, {autoConnect: true});



