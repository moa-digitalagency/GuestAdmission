let allClients = [];
let filteredClients = [];

document.addEventListener('DOMContentLoaded', async function() {
    await loadClients();
    populateCountryFilter();
});

async function loadClients() {
    try {
        const response = await fetch('/api/personnes');
        allClients = await response.json();
        filteredClients = [...allClients];
        renderClients(filteredClients);
    } catch (error) {
        console.error('Erreur chargement clients:', error);
    }
}

function populateCountryFilter() {
    const paysSet = new Set();
    allClients.forEach(client => {
        if (client.pays) paysSet.add(client.pays);
    });
    
    const paysFilter = document.getElementById('paysFilter');
    Array.from(paysSet).sort().forEach(pays => {
        const option = document.createElement('option');
        option.value = pays;
        option.textContent = pays;
        paysFilter.appendChild(option);
    });
}

function applyFilters() {
    const searchText = document.getElementById('searchFilter').value.toLowerCase();
    const paysFilter = document.getElementById('paysFilter').value;
    const typePieceFilter = document.getElementById('typePieceFilter').value;
    
    filteredClients = allClients.filter(client => {
        const matchesSearch = !searchText || 
            (client.nom && client.nom.toLowerCase().includes(searchText)) ||
            (client.prenom && client.prenom.toLowerCase().includes(searchText)) ||
            (client.email && client.email.toLowerCase().includes(searchText));
        
        const matchesPays = !paysFilter || client.pays === paysFilter;
        const matchesTypePiece = !typePieceFilter || client.type_piece === typePieceFilter;
        
        return matchesSearch && matchesPays && matchesTypePiece;
    });
    
    renderClients(filteredClients);
}

function resetFilters() {
    document.getElementById('searchFilter').value = '';
    document.getElementById('paysFilter').value = '';
    document.getElementById('typePieceFilter').value = '';
    applyFilters();
}

async function renderClients(clients) {
    const tbody = document.getElementById('clientsBody');
    const resultsCount = document.getElementById('resultsCount');
    
    resultsCount.textContent = `${clients.length} client${clients.length !== 1 ? 's' : ''} trouvé${clients.length !== 1 ? 's' : ''}`;
    
    if (clients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 2rem;">Aucun client trouvé</td></tr>';
        return;
    }
    
    const sejourMap = {};
    try {
        const sejoursResp = await fetch('/api/sejours');
        const sejours = await sejoursResp.json();
        sejours.forEach(s => {
            sejourMap[s.id] = s.numero_reservation || `#${s.id}`;
        });
    } catch (error) {
        console.error('Erreur chargement séjours:', error);
    }
    
    tbody.innerHTML = clients.map(client => `
        <tr>
            <td>${client.nom || 'N/A'}</td>
            <td>${client.prenom || 'N/A'}</td>
            <td>${client.email || 'N/A'}</td>
            <td>${client.telephone || 'N/A'}</td>
            <td>${client.pays || 'N/A'}</td>
            <td>${client.type_piece || 'N/A'}</td>
            <td>${client.numero_piece || 'N/A'}</td>
            <td>
                ${client.reservation_id ? 
                    `<a href="/sejour/${client.reservation_id}">${sejourMap[client.reservation_id] || `#${client.reservation_id}`}</a>` : 
                    'N/A'}
            </td>
        </tr>
    `).join('');
}

async function exportClientsPDF() {
    try {
        const searchText = document.getElementById('searchFilter').value;
        const paysFilter = document.getElementById('paysFilter').value;
        const typePieceFilter = document.getElementById('typePieceFilter').value;
        
        const params = new URLSearchParams();
        if (searchText) params.append('search', searchText);
        if (paysFilter) params.append('pays', paysFilter);
        if (typePieceFilter) params.append('type_piece', typePieceFilter);
        
        const url = '/api/clients/export-pdf?' + params.toString();
        
        const response = await fetch(url, {
            method: 'GET'
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de l\'export PDF');
        }
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `clients_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
        
        alert('✓ Export PDF réussi!');
    } catch (error) {
        console.error('Erreur export PDF:', error);
        alert('Erreur lors de l\'export PDF');
    }
}
