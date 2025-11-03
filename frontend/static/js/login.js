const form = document.getElementById('loginForm');
const alertContainer = document.getElementById('alert-container');

function showAlert(message, type = 'error') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            });
            
            if (response.ok) {
                window.location.href = '/dashboard';
            } else {
                const data = await response.json();
                showAlert(data.error || 'Erreur de connexion', 'error');
            }
        } catch (error) {
            console.error('Erreur:', error);
            showAlert('Erreur de connexion', 'error');
        }
    });
}
