const loginForm = document.getElementById('loginForm');
const errorDiv = document.getElementById('error-message');

if (loginForm) {
  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    errorDiv.style.display = 'none';
    errorDiv.textContent = '';

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await fetch('/users/token', {
        method: 'POST',
        body: formData,
        credentials: 'include' // To receive cookie
      });
      const data = await response.json();

      if (!response.ok) {
        errorDiv.textContent = data.detail || 'Login failed';
        errorDiv.style.display = 'block';
        return;
      }

      // JWT is now in the cookie; redirect to dashboard
      window.location.href = '/users/dashboard';
    } catch (err) {
      console.error('Login error:', err);
      errorDiv.textContent = 'Failed to connect to the server';
      errorDiv.style.display = 'block';
    }
  });
}

// --- CREATE SHIPMENT PROCESS ---
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
        alert('Shipment created successfully!');
        createForm.reset();
      } else if (response.status === 401) {
        alert('Unauthorized access. Please log in again.');
        window.location.href = '/users/login';
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || 'Server error'}`);
      }
    } catch (err) {
      console.error('Shipment creation error:', err);
      alert('Failed to connect to the server');
    }
  });
}

// --- LOGOUT PROCESS ---
const logoutBtns = document.querySelectorAll('.logout-btn');

if (logoutBtns.length > 0) {
  async function logout() {
    try {
      await fetch('/users/logout', {
        method: 'GET',
        credentials: 'include'
      });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      window.location.href = '/users/login';
    }
  }

  logoutBtns.forEach(btn => {
    btn.addEventListener('click', logout);
  });
}
