import { io } from 'socket.io-client';

// use https in prod but http when local
const URL = process.env.NODE_ENV === 'production' ? 'wss://gamesby.jeffr.ee:8443' : 'http://localhost:9069';

export const socket = io(URL, {autoConnect: true});



