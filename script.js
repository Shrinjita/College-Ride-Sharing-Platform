// Toggle Chatroom
function toggleChatroom() {
    let chatroom = document.querySelector(".chat-container");
    chatroom.style.display = (chatroom.style.display === "none" || chatroom.style.display === "") ? "block" : "none";
}

// Toggle SOS Modal
function toggleSOS() {
    let sosModal = document.getElementById("sosModal");
    sosModal.style.display = (sosModal.style.display === "none" || sosModal.style.display === "") ? "block" : "none";
}
// Function to toggle Sign-In modal
function toggleSignIn() {
    let modal = document.getElementById("signInModal");
    modal.style.display = (modal.style.display === "none" || modal.style.display === "") ? "block" : "none";
}

// Function to toggle Register modal
function toggleRegister() {
    let modal = document.getElementById("registerModal");
    modal.style.display = (modal.style.display === "none" || modal.style.display === "") ? "block" : "none";
}

// 🚀 Modify Sign-In Function to Redirect Admin
function signIn() {
    let username = document.getElementById("signInUsername").value.trim();
    let password = document.getElementById("signInPassword").value.trim();

    let storedUser = localStorage.getItem(username);

    if (storedUser) {
        let userData = JSON.parse(storedUser);
        let storedPassword = userData.password;

        if (password === storedPassword) {
            alert("Login successful!");
            toggleSignIn();

            // 🚀 Redirect Admin
            if (userData.registerNo === "RA2211047010017") {
                window.location.href = "admin.html";
            }
        } else {
            alert("Incorrect password.");
        }
    } else {
        alert("Username not found. Please Register.");
    }
}

// 🚀 Function to verify Register Number
function verifyRegisterNo() {
    let registerNo = document.getElementById("registerNumber").value.trim();

    if (!registerNo.startsWith("RA2211047010") || parseInt(registerNo.slice(-4)) < 1 || parseInt(registerNo.slice(-4)) > 50) {
        alert("Invalid Register Number!");
        return;
    }

    alert("Register Number Verified! Please set your Username and Password.");
    document.getElementById("registerFields").style.display = "block"; // Show Username & Password Fields
}

// 🚀 Function to register user after verification
function registerUser() {
    let username = document.getElementById("registerUsername").value.trim();
    let password = document.getElementById("registerPassword").value.trim();
    let registerNo = document.getElementById("registerNumber").value.trim();

    if (!username || !password) {
        alert("Please enter both Username and Password.");
        return;
    }

    localStorage.setItem(username, JSON.stringify({ registerNo, password }));
    alert("Registration successful! You can now sign in.");
    toggleRegister();
}


document.addEventListener("DOMContentLoaded", function () {
    // Function to show/hide manual input field when "Other" is selected
    function toggleCustomInput(type) {
        let selectElement = document.getElementById(type);
        let inputElement = document.getElementById(type + "Custom");

        if (selectElement.value === "custom") {
            inputElement.style.display = "block";
            inputElement.value = ""; // Clear previous input
            inputElement.focus();
        } else {
            inputElement.style.display = "none";
        }
    }

    // Function to add a new ride record to the table
    function addRecord() {
        let pickupSelect = document.getElementById("pickup");
        let dropSelect = document.getElementById("drop");
        let genderSelect = document.getElementById("gender");

        let pickupLocation = pickupSelect.value === "custom"
            ? document.getElementById("pickupCustom").value
            : pickupSelect.value;

        let dropLocation = dropSelect.value === "custom"
            ? document.getElementById("dropCustom").value
            : dropSelect.value;

        let gender = genderSelect.value;
        let time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        if (!pickupLocation || !dropLocation) {
            alert("Please select or enter both Pickup and Drop locations.");
            return;
        }

        let tableBody = document.getElementById("ridesData");
        let newRow = document.createElement("tr");

        newRow.innerHTML = `
            <td>${pickupLocation}</td>
            <td>${dropLocation}</td>
            <td>${gender.charAt(0).toUpperCase() + gender.slice(1)}</td>
            <td>${time}</td>
        `;

        tableBody.appendChild(newRow);
        
        // Reset form
        pickupSelect.value = "";
        dropSelect.value = "";
        genderSelect.value = "any";
        document.getElementById("pickupCustom").style.display = "none";
        document.getElementById("dropCustom").style.display = "none";
    }

    // Attach functions to window for global access
    window.toggleCustomInput = toggleCustomInput;
    window.addRecord = addRecord;
});
