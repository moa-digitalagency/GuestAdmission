let currentEtablissements = [];
let currentExtras = [];
let editingExtraId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadEtablissements();
    loadExtras();
});

async function loadEtablissements() {
    try {
        const response = await fetch('/api/etablissements?actif_only=false');
        const data = await response.json();
        currentEtablissements = data;
        
        const filterSelect = document.getElementById('filterEtablissement');
        const formSelect = document.getElementById('extraEtablissement');
        
        filterSelect.innerHTML = '<option value="">Tous les établissements</option>';
        formSelect.innerHTML = '<option value="">Sélectionner un établissement</option>';
        
        data.forEach(etablissement => {
            if (etablissement.actif) {
                const option1 = new Option(etablissement.nom_etablissement, etablissement.id);
                const option2 = new Option(etablissement.nom_etablissement, etablissement.id);
                filterSelect.add(option1);
                formSelect.add(option2);
            }
        });
        
        filterSelect.addEventListener('change', loadExtras);
    } catch (error) {
        console.error('Erreur lors du chargement des établissements:', error);
    }
}

async function loadExtras() {
    const etablissementId = document.getElementById('filterEtablissement').value;
    const url = etablissementId 
        ? `/api/extras?etablissement_id=${etablissementId}&actif_only=false`
        : '/api/extras?actif_only=false';
    
    try {
        const response = await fetch(url);
        const extras = await response.json();
        currentExtras = extras;
        displayExtras(extras);
    } catch (error) {
        console.error('Erreur lors du chargement des extras:', error);
        document.getElementById('extrasTable').innerHTML = 
            '<p style="color: red; text-align: center;">Erreur lors du chargement des extras</p>';
    }
}

function displayExtras(extras) {
    const container = document.getElementById('extrasTable');
    
    if (extras.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">Aucun extra trouvé</p>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Nom</th>
                    <th>Établissement</th>
                    <th>Prix unitaire</th>
                    <th>Unité</th>
                    <th>Statut</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${extras.map(extra => `
                    <tr>
                        <td><strong>${extra.nom}</strong><br>
                            <small style="color: #666;">${extra.description || ''}</small>
                        </td>
                        <td>${extra.nom_etablissement || 'N/A'}</td>
                        <td>${parseFloat(extra.prix_unitaire).toFixed(2)} MAD</td>
                        <td>${extra.unite_mesure}</td>
                        <td>
                            <span class="badge ${extra.actif ? 'badge-active' : 'badge-inactive'}">
                                ${extra.actif ? 'Actif' : 'Inactif'}
                            </span>
                        </td>
                        <td>
                            <button class="btn-icon" onclick="editExtra(${extra.id})" title="Modifier">
                                ✏️
                            </button>
                            <button class="btn-icon" onclick="deleteExtra(${extra.id})" title="Supprimer">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

function showAddExtraModal() {
    editingExtraId = null;
    document.getElementById('modalTitle').textContent = 'Ajouter un Extra';
    document.getElementById('extraForm').reset();
    document.getElementById('extraId').value = '';
    document.getElementById('extraActif').checked = true;
    document.getElementById('extraModal').style.display = 'flex';
}

function closeExtraModal() {
    document.getElementById('extraModal').style.display = 'none';
    editingExtraId = null;
}

async function editExtra(extraId) {
    try {
        const response = await fetch(`/api/extras/${extraId}`);
        const extra = await response.json();
        
        editingExtraId = extraId;
        document.getElementById('modalTitle').textContent = 'Modifier un Extra';
        document.getElementById('extraId').value = extra.id;
        document.getElementById('extraEtablissement').value = extra.etablissement_id;
        document.getElementById('extraNom').value = extra.nom;
        document.getElementById('extraDescription').value = extra.description || '';
        document.getElementById('extraPrix').value = extra.prix_unitaire;
        document.getElementById('extraUnite').value = extra.unite_mesure;
        document.getElementById('extraActif').checked = extra.actif;
        
        document.getElementById('extraModal').style.display = 'flex';
    } catch (error) {
        console.error('Erreur lors du chargement de l\'extra:', error);
        alert('Erreur lors du chargement de l\'extra');
    }
}

async function deleteExtra(extraId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet extra ?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/extras/${extraId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Extra supprimé avec succès');
            loadExtras();
        } else {
            alert('Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression');
    }
}

document.getElementById('extraForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const data = {
        etablissement_id: parseInt(document.getElementById('extraEtablissement').value),
        nom: document.getElementById('extraNom').value,
        description: document.getElementById('extraDescription').value,
        prix_unitaire: parseFloat(document.getElementById('extraPrix').value),
        unite_mesure: document.getElementById('extraUnite').value,
        actif: document.getElementById('extraActif').checked
    };
    
    try {
        const url = editingExtraId ? `/api/extras/${editingExtraId}` : '/api/extras';
        const method = editingExtraId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert(editingExtraId ? 'Extra modifié avec succès' : 'Extra créé avec succès');
            closeExtraModal();
            loadExtras();
        } else {
            alert('Erreur lors de l\'enregistrement');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'enregistrement');
    }
});

async function loadExtrasSummary() {
    const etablissementId = document.getElementById('filterEtablissement').value;
    if (!etablissementId) {
        alert('Veuillez sélectionner un établissement');
        return;
    }
    
    const dateDebut = document.getElementById('summaryDateDebut').value;
    const dateFin = document.getElementById('summaryDateFin').value;
    
    let url = `/api/extras/summary/${etablissementId}`;
    const params = [];
    if (dateDebut) params.push(`date_debut=${dateDebut}`);
    if (dateFin) params.push(`date_fin=${dateFin}`);
    if (params.length > 0) url += '?' + params.join('&');
    
    try {
        const response = await fetch(url);
        const summary = await response.json();
        displaySummary(summary);
    } catch (error) {
        console.error('Erreur lors du chargement du sommaire:', error);
    }
}

function displaySummary(summary) {
    const container = document.getElementById('extrasSummary');
    
    if (summary.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">Aucune donnée pour cette période</p>';
        return;
    }
    
    let totalGeneral = 0;
    
    const table = `
        <table class="summary-table">
            <thead>
                <tr>
                    <th>Extra</th>
                    <th>Utilisations</th>
                    <th>Quantité totale</th>
                    <th>Prix unitaire</th>
                    <th>Montant total</th>
                </tr>
            </thead>
            <tbody>
                ${summary.map(item => {
                    const montant = parseFloat(item.montant_total || 0);
                    totalGeneral += montant;
                    return `
                        <tr>
                            <td>${item.extra_nom} <small>(${item.unite_mesure})</small></td>
                            <td>${item.nombre_utilisations || 0}</td>
                            <td>${item.quantite_totale || 0}</td>
                            <td>${parseFloat(item.prix_unitaire || 0).toFixed(2)} MAD</td>
                            <td>${montant.toFixed(2)} MAD</td>
                        </tr>
                    `;
                }).join('')}
                <tr class="summary-total">
                    <td colspan="4" style="text-align: right;"><strong>Total général:</strong></td>
                    <td><strong>${totalGeneral.toFixed(2)} MAD</strong></td>
                </tr>
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}
