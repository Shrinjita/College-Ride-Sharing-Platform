// Initialize Firebase
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-auth.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/11.6.0/firebase-database.js";

const firebaseConfig = {
  apiKey: "AIzaSyA8drNIznpNGlNyciAFLrH_rSQJ8KNnNnQ",
  authDomain: "college-ride-sharing-pla-82e4a.firebaseapp.com",
  databaseURL: "https://college-ride-sharing-pla-82e4a-default-rtdb.firebaseio.com",
  projectId: "college-ride-sharing-pla-82e4a",
  storageBucket: "college-ride-sharing-pla-82e4a.firebasestorage.app",
  messagingSenderId: "135652323113",
  appId: "1:135652323113:web:858407787b270af05e1138"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const database = getDatabase(app);

export { auth, database };