// static/auth.js

// 1) Login formu submit edildiğinde token alıp dashboard’ı JS ile yükleyen fonksiyon
async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const errorDiv = document.getElementById('error-message');

    errorDiv.style.display = 'none';
    errorDiv.textContent = '';

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch('/users/token', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (!response.ok) {
            // Sunucudan dönen hata mesajını göster
            errorDiv.textContent = data.detail || 'Login başarısız';
            errorDiv.style.display = 'block';
            return;
        }

        // Başarılı giriş => token’ı localStorage’a kaydet
        const token = data.access_token;
        localStorage.setItem('access_token', token);

        // Dashboard sayfasını token header’ı ile çek
        const dashResp = await fetch('/users/dashboard', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!dashResp.ok) {
            if (dashResp.status === 401 || dashResp.status === 403) {
                errorDiv.textContent = 'Yetkisiz erişim veya token geçersiz.';
            } else {
                errorDiv.textContent = 'Dashboard yüklenirken hata oluştu.';
            }
            errorDiv.style.display = 'block';
            return;
        }

        // Dashboard HTML’ini alıp mevcut sayfayı tamamen değiştiriyoruz
        const html = await dashResp.text();
        document.open();
        document.write(html);
        document.close();
    } catch (err) {
        console.error(err);
        errorDiv.textContent = 'Sunucuya ulaşılamadı veya beklenmeyen bir hata oluştu.';
        errorDiv.style.display = 'block';
    }
}

// 2) DOM yüklendiğinde login formu varsa submit event’ini bind et
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    if (form) {
        form.addEventListener('submit', handleLogin);
    }
});

// 3) “Logout” butonuna basıldığında token’ı silip login sayfasına yönlendir
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/users/login';
}

// 4) “Create Shipment” linkine tıklandığında token header ile /shipments/create-form isteği at
function goCreate() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        // Token yoksa login’e dön
        window.location.href = '/users/login';
        return;
    }
    fetch('/shipments/create-form', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => {
        if (res.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/users/login';
            return;
        }
        return res.text();
    })
    .then(html => {
        if (html) {
            document.open();
            document.write(html);
            document.close();
        }
    })
    .catch(err => {
        console.error(err);
        window.location.href = '/users/login';
    });
}

// 5) “Scan QR” linkine tıklandığında token header ile /shipments/qr_scan isteği at
function goScan() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/users/login';
        return;
    }
    fetch('/shipments/qr_scan', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => {
        if (res.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/users/login';
            return;
        }
        return res.text();
    })
    .then(html => {
        if (html) {
            document.open();
            document.write(html);
            document.close();
        }
    })
    .catch(err => {
        console.error(err);
        window.location.href = '/users/login';
    });
}
