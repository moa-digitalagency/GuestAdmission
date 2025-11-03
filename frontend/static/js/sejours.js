let sejours = [];
let etablissements = [];
let allSejours = [];

function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

async function loadEtablissements() {
    try {
        const response = await fetch('/api/etablissements?actif_only=true');
        etablissements = await response.json();
        
        const filterEtab = document.getElementById('filterEtablissement');
        if (filterEtab) {
            filterEtab.innerHTML = '<option value="">Tous les établissements</option>';
            etablissements.forEach(etab => {
                const option = new Option(etab.nom_etablissement, etab.id);
                filterEtab.add(option);
            });
        }
    } catch (error) {
        console.error('Erreur chargement établissements:', error);
    }
}

async function loadSejours() {
    try {
        const response = await fetch('/api/sejours');
        allSejours = await response.json();
        sejours = allSejours;
        applyFilters();
    } catch (error) {
        console.error('Erreur chargement séjours:', error);
        showAlert('Erreur lors du chargement des séjours', 'error');
    }
}

function applyFilters() {
    const filterEtab = document.getElementById('filterEtablissement');
    const filterStatut = document.getElementById('filterStatut');
    const filterNumero = document.getElementById('filterNumero');
    const filterDateDebut = document.getElementById('filterDateDebut');
    const filterDateFin = document.getElementById('filterDateFin');
    
    let filtered = [...allSejours];
    
    if (filterEtab && filterEtab.value) {
        filtered = filtered.filter(s => s.etablissement_id == filterEtab.value);
    }
    
    if (filterStatut && filterStatut.value) {
        filtered = filtered.filter(s => s.statut === filterStatut.value);
    }
    
    if (filterNumero && filterNumero.value) {
        const search = filterNumero.value.toLowerCase();
        filtered = filtered.filter(s => 
            (s.numero_reservation && s.numero_reservation.toLowerCase().includes(search)) ||
            (s.contact_nom && s.contact_nom.toLowerCase().includes(search)) ||
            (s.contact_prenom && s.contact_prenom.toLowerCase().includes(search))
        );
    }
    
    if (filterDateDebut && filterDateDebut.value) {
        filtered = filtered.filter(s => s.date_arrivee >= filterDateDebut.value);
    }
    
    if (filterDateFin && filterDateFin.value) {
        filtered = filtered.filter(s => s.date_depart <= filterDateFin.value);
    }
    
    sejours = filtered;
    renderSejours();
}

function renderSejours() {
    const container = document.getElementById('sejoursContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (sejours.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">Aucun séjour trouvé.</p>';
        return;
    }
    
    sejours.forEach(sejour => {
        const card = document.createElement('div');
        const statutClass = sejour.statut === 'terminee' ? 'sejour-termine' : 
                           sejour.statut === 'active' ? 'sejour-actif' : 'sejour-annule';
        card.className = `sejour-card ${statutClass}`;
        
        const statutBadge = sejour.statut === 'terminee' ? 
            '<span class="badge badge-termine">Terminé</span>' :
            sejour.statut === 'active' ?
            '<span class="badge badge-actif">Actif</span>' :
            '<span class="badge badge-annule">Annulé</span>';
        
        card.innerHTML = `
            <div class="sejour-header">
                <h3>${sejour.numero_reservation || 'N/A'}</h3>
                ${statutBadge}
            </div>
            <div class="sejour-body">
                <p><strong>🏢 Établissement:</strong> ${sejour.nom_etablissement || 'N/A'}</p>
                <p><strong>👤 Contact:</strong> ${sejour.contact_prenom || ''} ${sejour.contact_nom || 'N/A'}</p>
                <p><strong>📅 Arrivée:</strong> ${formatDate(sejour.date_arrivee)} | <strong>📅 Départ:</strong> ${formatDate(sejour.date_depart)}</p>
                <p><strong>🛏️ Nuits:</strong> ${sejour.nombre_jours || 'N/A'} | <strong>💰 Total:</strong> ${parseFloat(sejour.facture_hebergement || 0).toFixed(2)} MAD</p>
            </div>
            <div class="sejour-actions">
                <button class="btn-primary" onclick="viewSejour(${sejour.id})">Voir détails</button>
                <button class="btn-danger" onclick="deleteSejour(${sejour.id})">Supprimer</button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function viewSejour(id) {
    window.location.href = `/sejour/${id}`;
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

function resetFilters() {
    const filterEtab = document.getElementById('filterEtablissement');
    const filterStatut = document.getElementById('filterStatut');
    const filterNumero = document.getElementById('filterNumero');
    const filterDateDebut = document.getElementById('filterDateDebut');
    const filterDateFin = document.getElementById('filterDateFin');
    
    if (filterEtab) filterEtab.value = '';
    if (filterStatut) filterStatut.value = '';
    if (filterNumero) filterNumero.value = '';
    if (filterDateDebut) filterDateDebut.value = '';
    if (filterDateFin) filterDateFin.value = '';
    
    applyFilters();
}

function printSejoursList() {
    const printContent = generatePrintableList();
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<html><head><title>Liste des Séjours</title>');
    printWindow.document.write('<style>');
    printWindow.document.write(`
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { text-align: center; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; font-weight: bold; }
        .badge-actif { color: #16a34a; font-weight: bold; }
        .badge-termine { color: #6b7280; font-weight: bold; }
        .badge-annule { color: #dc2626; font-weight: bold; }
        @media print {
            button { display: none; }
        }
    `);
    printWindow.document.write('</style></head><body>');
    printWindow.document.write(printContent);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}

function generatePrintableList() {
    let html = '<h1>Liste des Séjours</h1>';
    html += `<p>Date d'impression: ${new Date().toLocaleString('fr-FR')}</p>`;
    html += `<p>Nombre de séjours: ${sejours.length}</p>`;
    
    html += '<table>';
    html += '<thead><tr>';
    html += '<th>N° Séjour</th>';
    html += '<th>Établissement</th>';
    html += '<th>Contact</th>';
    html += '<th>Arrivée</th>';
    html += '<th>Départ</th>';
    html += '<th>Nuits</th>';
    html += '<th>Statut</th>';
    html += '<th>Montant</th>';
    html += '</tr></thead>';
    html += '<tbody>';
    
    sejours.forEach(sejour => {
        const statutClass = sejour.statut === 'terminee' ? 'badge-termine' :
                           sejour.statut === 'active' ? 'badge-actif' : 'badge-annule';
        const statutText = sejour.statut === 'terminee' ? 'Terminé' :
                          sejour.statut === 'active' ? 'Actif' : 'Annulé';
        
        html += '<tr>';
        html += `<td>${sejour.numero_reservation || 'N/A'}</td>`;
        html += `<td>${sejour.nom_etablissement || 'N/A'}</td>`;
        html += `<td>${sejour.contact_prenom || ''} ${sejour.contact_nom || 'N/A'}</td>`;
        html += `<td>${formatDate(sejour.date_arrivee)}</td>`;
        html += `<td>${formatDate(sejour.date_depart)}</td>`;
        html += `<td>${sejour.nombre_jours || 'N/A'}</td>`;
        html += `<td><span class="${statutClass}">${statutText}</span></td>`;
        html += `<td>${parseFloat(sejour.facture_hebergement || 0).toFixed(2)} MAD</td>`;
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    return html;
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        loadEtablissements();
        loadSejours();
    });
} else {
    loadEtablissements();
    loadSejours();
}
