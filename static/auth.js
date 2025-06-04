// static/auth.js

const loginForm = document.getElementById('loginForm');
const errorDiv = document.getElementById('error-message');

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
            credentials: 'include'  // Cookie’yi almak için
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
