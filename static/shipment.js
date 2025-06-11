document.addEventListener("DOMContentLoaded", function () {
    const shipmentForm = document.getElementById("createShipmentForm");
    if (!shipmentForm) return;

    const senderAddressDiv = document.getElementById("sender_address_group");
    const senderAddressInput = document.getElementById("sender_address");
    const errorMsgDiv = document.getElementById("error_message");

    shipmentForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const payload = {
            sender_name: shipmentForm.sender_name.value,
            sender_phone: shipmentForm.sender_phone.value,
            sender_address: shipmentForm.sender_address.value,
            receiver_name: shipmentForm.receiver_name.value,
            receiver_phone: shipmentForm.receiver_phone.value,
            receiver_address: shipmentForm.receiver_address.value,
        };

        try {
            const res = await fetch("/shipments/create", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                const data = await res.json();
                window.location.href = data.redirect || "/users/dashboard";
            } else {
                const errorData = await res.json();
                if (errorData.detail === "add_sender") {
                    senderAddressDiv.classList.remove("hidden");
                    senderAddressInput.required = true;
                    errorMsgDiv.classList.remove("hidden");
                    errorMsgDiv.innerText = "Sender not found. Please enter the address!";
                } else {
                    errorMsgDiv.classList.remove("hidden");
                    errorMsgDiv.innerText = errorData.detail || "An error occurred.";
                }
            }
        } catch (e) {
            errorMsgDiv.classList.remove("hidden");
            errorMsgDiv.innerText = "An error occurred.";
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    if (!loginForm) return;

    const errorDiv = document.getElementById("error-message");

    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const username = loginForm.username.value;
        const password = loginForm.password.value;

        try {
            const res = await fetch("/users/token", {
                method: "POST",
                headers: {"Content-Type": "application/x-www-form-urlencoded"},
                body: new URLSearchParams({
                    username,
                    password,
                })
            });
            if (res.ok) {
                window.location.href = "/users/dashboard";
            } else {
                const data = await res.json();
                errorDiv.style.display = "block";
                errorDiv.innerText = data.detail || "Login failed.";
            }
        } catch {
            errorDiv.style.display = "block";
            errorDiv.innerText = "Login failed. Server error.";
        }
    });
});
