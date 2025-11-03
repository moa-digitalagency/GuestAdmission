async function loadClients() {
    try {
        const response = await fetch('/api/personnes');
        const clients = await response.json();
        renderClients(clients);
    } catch (error) {
        console.error('Erreur chargement clients:', error);
    }
}

function renderClients(clients) {
    const container = document.getElementById('clientsContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (clients.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem;">Aucun client enregistré.</p>';
        return;
    }
    
    clients.forEach(client => {
        const card = document.createElement('div');
        card.className = 'client-card';
        card.innerHTML = `
            <h3>${client.prenom} ${client.nom}</h3>
            <p><strong>Email:</strong> ${client.email || 'N/A'}</p>
            <p><strong>Téléphone:</strong> ${client.telephone || 'N/A'}</p>
            <p><strong>Pays:</strong> ${client.pays || 'N/A'}</p>
        `;
        container.appendChild(card);
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadClients);
} else {
    loadClients();
}
