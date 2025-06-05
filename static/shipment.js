
const createForm = document.getElementById('createShipmentForm');
const logoutBtns = document.querySelectorAll('.logout-btn');

// Create Shipment
createForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = {
        sender_name: document.getElementById('sender_name').value.trim(),
        receiver_name: document.getElementById('receiver_name').value.trim(),
        receiver_phone: document.getElementById('receiver_phone').value.trim(),
        receiver_address: document.getElementById('receiver_address').value.trim()
    };
    try {
        const response = await fetch('/shipments/create', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'include',
            body: JSON.stringify(payload)
        });
        if (response.status === 201) {
            alert('Kargo başarıyla oluşturuldu!');
            createForm.reset();
        } else if (response.status === 401) {
            alert('Yetkisiz erişim. Lütfen tekrar giriş yapın.');
            window.location.href = '/users/login';
        } else {
            const errorData = await response.json();
            alert(`Hata: ${errorData.detail || 'Sunucu hatası'}`);
        }
    } catch (err) {
        console.error('Kargo oluşturma hatası:', err);
        alert('Sunucu ile bağlantı kurulamadı');
    }
});

async function logout() {
    try {
        await fetch('/users/logout', {
            method: 'GET',
            credentials: 'include'
        });
    } catch (err) {
        console.error('Logout hatası:', err);
    } finally {
        window.location.href = '/users/login';
    }
}

logoutBtns.forEach(btn => {
    btn.addEventListener('click', logout);
});
