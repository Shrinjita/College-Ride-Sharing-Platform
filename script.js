function toggleChatroom() {
    let chatroom = document.getElementById("chatroom");
    chatroom.style.display = (chatroom.style.display === "none" || chatroom.style.display === "") ? "block" : "none";
}

function sendMessage() {
    let input = document.getElementById("chatMessage");
    let messageText = input.value.trim();
    
    if (messageText !== "") {
        let messagesContainer = document.querySelector(".chat-messages");
        let newMessage = document.createElement("div");

        newMessage.classList.add("message", "sent"); // Add sent message class
        newMessage.textContent = messageText;

        messagesContainer.appendChild(newMessage);
        input.value = "";

        // Auto-scroll to the latest message
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Simulate received message after 1 second (for testing UI)
        setTimeout(receiveMessage, 1000);
    }
}

// Simulating an incoming message
function receiveMessage() {
    let messagesContainer = document.querySelector(".chat-messages");
    let newMessage = document.createElement("div");

    newMessage.classList.add("message", "received"); // Add received message class
    newMessage.textContent = "This is an automated reply.";

    messagesContainer.appendChild(newMessage);

    // Auto-scroll to the latest message
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addRecord() {
    let pickup = document.getElementById("pickup").value;
    let drop = document.getElementById("drop").value;
    let gender = document.getElementById("gender").value;
    
    if (pickup === "" || drop === "") {
        alert("Please enter both pickup and drop locations.");
        return;
    }
    
    let table = document.getElementById("recordTable");
    let newRow = table.insertRow();
    newRow.insertCell(0).textContent = pickup;
    newRow.insertCell(1).textContent = drop;
    newRow.insertCell(2).textContent = gender;
}

function toggleSOS() {
    const sosModal = document.getElementById("sosModal");
    sosModal.classList.toggle("active");
}
