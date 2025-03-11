document.addEventListener("DOMContentLoaded", function () {
    // Fetch available locations from backend API
    fetch("/api/locations")
        .then(response => response.json())
        .then(data => {
            const pickupSelect = document.getElementById("pickup-location");
            const dropSelect = document.getElementById("drop-location");
            data.locations.forEach(location => {
                let option = new Option(location, location);
                pickupSelect.add(option.cloneNode(true));
                dropSelect.add(option);
            });
        });

    // Handle booking form submission
    document.getElementById("book-btn").addEventListener("click", function () {
        const pickup = document.getElementById("pickup-location").value;
        const drop = document.getElementById("drop-location").value;
        const genderPref = document.getElementById("gender-preference").value;
        
        fetch("/api/book", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pickup, drop, genderPref })
        })
        .then(response => response.json())
        .then(data => updatePoolersTable(data.poolers));
    });

    // Update poolers table dynamically
    function updatePoolersTable(poolers) {
        const tableBody = document.getElementById("poolers-table").querySelector("tbody");
        tableBody.innerHTML = "";
        poolers.forEach(pooler => {
            const row = tableBody.insertRow();
            row.innerHTML = `
                <td>${pooler.pickup}</td>
                <td>${pooler.drop}</td>
                <td>${pooler.time}</td>
                <td>${pooler.gender}</td>
                <td><button class="chat-btn" onclick="openChat(${pooler.id})">Chat</button></td>
            `;
        });
    }

    // Emergency SOS Button
    document.getElementById("sos-btn").addEventListener("click", function () {
        alert("Emergency Alert Sent!");
        fetch("/api/sos", { method: "POST" });
    });
});

 // Function to handle booking form submission and add data to the poolers table
 document.getElementById('book-btn').addEventListener('click', function() {
    let pickupLocation = document.getElementById('pickup-location').value;
    let dropLocation = document.getElementById('drop-location').value;
    let genderPreference = document.querySelector('input[name="gender"]:checked').value;
    let vehicleChoice = document.getElementById('vehicle').value;
    let specialRequest = document.getElementById('special-request').value;
    let preferredTime = document.getElementById('time').value;
    let waitingTime = '10 mins';  // Default value

    // Create a new row in the table
    let table = document.getElementById('poolers-table').getElementsByTagName('tbody')[0];
    let newRow = table.insertRow(table.rows.length);

    newRow.innerHTML = `
        <td>${pickupLocation}</td>
        <td>${dropLocation}</td>
        <td>${waitingTime}</td>
        <td>${vehicleChoice}</td>
        <td>${specialRequest}</td>
        <td>${genderPreference}</td>
        <td><button class="chat-btn" onclick="openChat()">Chat Now</button></td>
    `;
});

// Function to open the chatbox
function openChat() {
    document.getElementById('chatbox-modal').style.display = 'block';
}

// Function to send a message in the chatbox
function sendMessage() {
    let chatContent = document.getElementById('chat-content');
    let message = document.getElementById('chat-input').value;
    if (message.trim() !== '') {
        let newMessage = document.createElement('div');
        newMessage.textContent = message;
        chatContent.appendChild(newMessage);
        document.getElementById('chat-input').value = '';
        chatContent.scrollTop = chatContent.scrollHeight;
    }
}

// Function to close the chatbox
function closeChat() {
    document.getElementById('chatbox-modal').style.display = 'none';
}