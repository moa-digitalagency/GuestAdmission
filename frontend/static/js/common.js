async function loadUserInfo() {
    try {
        const response = await fetch('/api/current-user');
        if (response.ok) {
            const user = await response.json();
            const userNameElement = document.getElementById('userName');
            if (userNameElement) {
                userNameElement.textContent = `${user.prenom} ${user.nom}`;
            }
        }
    } catch (error) {
        console.error('Erreur chargement utilisateur:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadUserInfo);
} else {
    loadUserInfo();
}
