document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("createShipmentForm");
  const errorMessage = document.getElementById("error_message");
  const addressGroup = document.getElementById("sender_address_group");

  form.addEventListener("submit", async e => {
    e.preventDefault();
    errorMessage.classList.add("hidden");
    addressGroup.classList.add("hidden");

    const payload = {
      sender_name: document.getElementById("sender_name").value.trim(),
      sender_phone: document.getElementById("sender_phone").value.trim(),
      sender_address: document.getElementById("sender_address")?.value.trim(),
      receiver_name: document.getElementById("receiver_name").value.trim(),
      receiver_phone: document.getElementById("receiver_phone").value.trim(),
      receiver_address: document.getElementById("receiver_address").value.trim()
    };

    const res = await fetch("/shipments/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.status === 400 && data.detail === "add_sender") {
      errorMessage.classList.remove("hidden");
      addressGroup.classList.remove("hidden");
      return;
    }

    if (data.redirect) {
      window.location.href = data.redirect;
      return;
    }

    if (!res.ok) {
      alert(data.detail || "Error creating shipment");
      return;
    }

    alert(data.message);
    form.reset();
    errorMessage.classList.add("hidden");
    addressGroup.classList.add("hidden");
  });
});
