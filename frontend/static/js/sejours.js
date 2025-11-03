let sejours = [];

function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

async function loadSejours() {
    try {
        const response = await fetch('/api/sejours');
        sejours = await response.json();
        renderSejours();
    } catch (error) {
        console.error('Erreur chargement séjours:', error);
        showAlert('Erreur lors du chargement des séjours', 'error');
    }
}

function renderSejours() {
    const container = document.getElementById('sejoursContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (sejours.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem;">Aucun séjour enregistré.</p>';
        return;
    }
    
    sejours.forEach(sejour => {
        const card = document.createElement('div');
        card.className = 'sejour-card';
        card.innerHTML = `
            <h3>${sejour.numero_reservation || 'N/A'}</h3>
            <p><strong>Client:</strong> ${sejour.client_nom || 'N/A'}</p>
            <p><strong>Dates:</strong> ${sejour.date_debut} au ${sejour.date_fin}</p>
            <p><strong>Statut:</strong> ${sejour.statut || 'N/A'}</p>
            <div class="button-group">
                <button class="btn btn-primary" onclick="viewSejour(${sejour.id})">Voir détails</button>
                <button class="btn btn-danger" onclick="deleteSejour(${sejour.id})">Supprimer</button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function viewSejour(id) {
    window.location.href = `/sejours/${id}`;
}

async function deleteSejour(id) {
    if (!confirm('Supprimer ce séjour?')) return;
    
    try {
        const response = await fetch(`/api/sejours/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showAlert('Séjour supprimé', 'success');
            loadSejours();
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la suppression', 'error');
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadSejours);
} else {
    loadSejours();
}
