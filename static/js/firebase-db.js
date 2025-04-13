import { database } from './firebase-config.js';
import { 
  ref, 
  set, 
  push, 
  onValue, 
  update,
  serverTimestamp,
  off
} from "https://www.gstatic.com/firebasejs/11.6.0/firebase-database.js";

// Ride sharing functions
export const addRide = (rideData) => {
  const ridesRef = ref(database, 'rides');
  const newRideRef = push(ridesRef);
  return set(newRideRef, {
    ...rideData,
    createdAt: serverTimestamp(),
    createdBy: auth.currentUser.uid
  });
};

export const getRides = (callback) => {
  const ridesRef = ref(database, 'rides');
  return onValue(ridesRef, (snapshot) => {
    const rides = [];
    snapshot.forEach((childSnapshot) => {
      rides.push({
        id: childSnapshot.key,
        ...childSnapshot.val()
      });
    });
    callback(rides);
  });
};

// Chat functions
export const sendChatMessage = (receiverId, message) => {
  const messagesRef = ref(database, 'messages');
  const newMessageRef = push(messagesRef);
  
  return set(newMessageRef, {
    senderId: auth.currentUser.uid,
    receiverId,
    message,
    timestamp: serverTimestamp(),
    read: false
  });
};

export const listenForMessages = (otherUserId, callback) => {
  const messagesRef = ref(database, 'messages');
  const listener = onValue(messagesRef, (snapshot) => {
    const messages = [];
    snapshot.forEach((childSnapshot) => {
      const msg = childSnapshot.val();
      if ((msg.senderId === auth.currentUser.uid && msg.receiverId === otherUserId) ||
          (msg.senderId === otherUserId && msg.receiverId === auth.currentUser.uid)) {
        messages.push({
          id: childSnapshot.key,
          ...msg
        });
      }
    });
    callback(messages);
  });
  
  return () => off(messagesRef, 'value', listener);
};