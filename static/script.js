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

// Function to handle Sign-In
function signIn() {
    let username = document.getElementById("signInUsername").value;
    let password = document.getElementById("signInPassword").value;

    if (username === "admin" && password === "password") { // Replace with actual database check
        alert("Login successful!");
        toggleSignIn();
    } else {
        alert("Invalid credentials. Please try again.");
    }
}

// Function to verify Register Number
function verifyRegisterNo() {
    let registerNo = document.getElementById("registerNumber").value;
    let validRegisterNos = ["2023001", "2023002", "2023003"]; // Replace with actual database check

    if (validRegisterNos.includes(registerNo)) {
        document.getElementById("registerFields").style.display = "block";
    } else {
        alert("Invalid Register Number!");
    }
}

// Function to register user
function registerUser() {
    let username = document.getElementById("registerUsername").value;
    let password = document.getElementById("registerPassword").value;

    if (username && password) {
        alert("Registration successful! You can now sign in.");
        toggleRegister();
    } else {
        alert("Please fill in all fields.");
    }
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
