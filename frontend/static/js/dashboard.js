async function loadDashboardData() {
    try {
        const response = await fetch('/api/reservations');
        const reservations = await response.json();
        
        const today = new Date().toISOString().split('T')[0];
        const actives = reservations.filter(r => r.date_debut <= today && r.date_fin >= today);
        const aVenir = reservations.filter(r => r.date_debut > today);
        
        document.getElementById('sejoursActifs').textContent = actives.length;
        document.getElementById('sejoursAVenir').textContent = aVenir.length;
        document.getElementById('sejoursTotal').textContent = reservations.length;
        
        const recentContainer = document.getElementById('recentReservations');
        if (recentContainer) {
            const recent = reservations.slice(0, 5);
            recentContainer.innerHTML = recent.map(r => `
                <div class="reservation-item">
                    <strong>${r.numero_reservation || 'N/A'}</strong> - ${r.client_nom || 'N/A'}
                    <br><small>${r.date_debut} au ${r.date_fin}</small>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Erreur chargement dashboard:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadDashboardData);
} else {
    loadDashboardData();
}
