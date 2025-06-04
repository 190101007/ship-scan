// static/auth.js

// --- LOGIN İŞLEMİ ---
const loginForm = document.getElementById('loginForm');
const errorDiv = document.getElementById('error-message');

if (loginForm) {
  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    // Hata mesajını gizle
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch('/users/token', {
        method: 'POST',
        body: formData,
        credentials: 'include' // Cookie’yi almak için
      });
      const data = await response.json();

      if (!response.ok) {
        errorDiv.textContent = data.detail || 'Login başarısız';
        errorDiv.style.display = 'block';
        return;
      }

      // Artık JWT cookie’de; sadece dashboard’a yönlendir
      window.location.href = '/users/dashboard';
    } catch (err) {
      console.error('Login sırasında hata:', err);
      errorDiv.textContent = 'Sunucu ile bağlantı kurulamadı';
      errorDiv.style.display = 'block';
    }
  });
}

// --- CREATE SHIPMENT İŞLEMLERİ ---
const createForm = document.getElementById('createShipmentForm');

if (createForm) {
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
        headers: { 'Content-Type': 'application/json' },
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
}

// --- LOGOUT İŞLEMİ ---
const logoutBtns = document.querySelectorAll('.logout-btn');

if (logoutBtns.length > 0) {
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
}

