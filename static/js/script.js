// Import Firebase functions from modules
import { 
    registerUser, 
    signInUser, 
    signOutUser, 
    setupAuthListener 
  } from './firebase/firebase-auth.js';
  import { 
    addRide, 
    getRides, 
    sendChatMessage, 
    listenForMessages 
  } from './firebase/firebase-db.js';
  
  // DOM Elements
  const signInForm = document.getElementById('signInForm');
  const registerForm = document.getElementById('registerForm');
  const signOutBtn = document.getElementById('signOutBtn');
  const addRideForm = document.getElementById('addRideForm');
  const chatForm = document.getElementById('chatForm');
  
  // Global Variables
  let currentUser = null;
  let currentChatPartner = null;
  let unsubscribeMessages = null;
  
  // Initialize Auth Listener
  setupAuthListener((user) => {
    currentUser = user;
    if (user) {
      console.log('User logged in:', user.uid);
      showAuthenticatedUI();
      loadRides();
    } else {
      console.log('User logged out');
      showUnauthenticatedUI();
      if (unsubscribeMessages) {
        unsubscribeMessages();
        unsubscribeMessages = null;
      }
    }
  });
  
  // Event Listeners
  if (signInForm) {
    signInForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('signInEmail').value;
      const password = document.getElementById('signInPassword').value;
      
      try {
        await signInUser(email, password);
        signInForm.reset();
      } catch (error) {
        console.error('Sign in error:', error);
        alert(error.message);
      }
    });
  }
  
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('registerEmail').value;
      const password = document.getElementById('registerPassword').value;
      const registerNo = document.getElementById('registerNumber').value;
      
      try {
        await registerUser(email, password);
        // Additional user data can be saved to database here
        registerForm.reset();
      } catch (error) {
        console.error('Registration error:', error);
        alert(error.message);
      }
    });
  }
  
  if (signOutBtn) {
    signOutBtn.addEventListener('click', async () => {
      try {
        await signOutUser();
      } catch (error) {
        console.error('Sign out error:', error);
      }
    });
  }
  
  if (addRideForm) {
    addRideForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!currentUser) {
        alert('Please sign in to add a ride');
        return;
      }
      
      const pickup = document.getElementById('pickup').value;
      const drop = document.getElementById('drop').value;
      const gender = document.getElementById('gender').value;
      
      try {
        await addRide({
          pickup,
          drop,
          gender,
          time: new Date().toLocaleTimeString()
        });
        addRideForm.reset();
      } catch (error) {
        console.error('Add ride error:', error);
        alert('Failed to add ride: ' + error.message);
      }
    });
  }
  
  if (chatForm) {
    chatForm.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!currentUser || !currentChatPartner) return;
      
      const messageInput = document.getElementById('chatMessage');
      const message = messageInput.value.trim();
      
      if (message) {
        sendChatMessage(currentChatPartner, message)
          .then(() => {
            messageInput.value = '';
          })
          .catch(error => {
            console.error('Send message error:', error);
          });
      }
    });
  }
  
  // UI Functions
  function showAuthenticatedUI() {
    document.querySelectorAll('.auth-only').forEach(el => {
      el.style.display = 'block';
    });
    document.querySelectorAll('.unauth-only').forEach(el => {
      el.style.display = 'none';
    });
  }
  
  function showUnauthenticatedUI() {
    document.querySelectorAll('.auth-only').forEach(el => {
      el.style.display = 'none';
    });
    document.querySelectorAll('.unauth-only').forEach(el => {
      el.style.display = 'block';
    });
  }
  
  function loadRides() {
    getRides((rides) => {
      const ridesTable = document.getElementById('ridesTable');
      if (ridesTable) {
        ridesTable.innerHTML = rides.map(ride => `
          <tr>
            <td>${ride.pickup}</td>
            <td>${ride.drop}</td>
            <td>${ride.gender}</td>
            <td>${ride.time}</td>
            <td>
              <button class="contact-btn" data-user="${ride.createdBy}">
                Contact
              </button>
            </td>
          </tr>
        `).join('');
        
        // Add event listeners to contact buttons
        document.querySelectorAll('.contact-btn').forEach(btn => {
          btn.addEventListener('click', (e) => {
            const userId = e.target.getAttribute('data-user');
            startChat(userId);
          });
        });
      }
    });
  }
  
  function startChat(userId) {
    if (!currentUser) return;
    
    currentChatPartner = userId;
    const chatModal = document.getElementById('chatModal');
    
    // Unsubscribe previous listener if exists
    if (unsubscribeMessages) {
      unsubscribeMessages();
    }
    
    // Subscribe to new chat
    unsubscribeMessages = listenForMessages(userId, (messages) => {
      const chatMessages = document.getElementById('chatMessages');
      chatMessages.innerHTML = messages.map(msg => `
        <div class="message ${msg.senderId === currentUser.uid ? 'sent' : 'received'}">
          <div class="message-content">${msg.message}</div>
          <div class="message-time">
            ${new Date(msg.timestamp).toLocaleTimeString()}
          </div>
        </div>
      `).join('');
      
      // Scroll to bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;
    });
    
    // Show chat modal
    chatModal.style.display = 'block';
  }
  
  // Initialize the app
  document.addEventListener('DOMContentLoaded', () => {
    console.log('App initialized');
  });