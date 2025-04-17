// script.js

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("rideFormModal");
    const addRideBtn = document.querySelector("button[onclick='openModal()']");
    const cancelBtn = modal ? modal.querySelector("button[type='button']") : null;

    window.openModal = function () {
        if (modal) modal.style.display = "block";
    };

    window.closeModal = function () {
        if (modal) modal.style.display = "none";
    };

    // Optional: Close modal if clicking outside of it
    window.onclick = function (event) {
        if (event.target === modal) {
            closeModal();
        }
    };

    if (cancelBtn) {
        cancelBtn.addEventListener("click", closeModal);
    }
});
