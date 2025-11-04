let currentEtablissementId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    loadStats();
    loadEtablissements();
});

async function loadUserInfo() {
    try {
        const response = await fetch('/api/current-user');
        const user = await response.json();
        document.getElementById('userInfo').textContent = `${user.prenom} ${user.nom} (${user.role})`;
    } catch (error) {
        console.error('Erreur lors du chargement des informations utilisateur:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/super-admin/stats');
        const stats = await response.json();
        
        document.getElementById('statEtablissementsActifs').textContent = stats.etablissements_actifs;
        document.getElementById('statTotalEtablissements').textContent = stats.total_etablissements;
        document.getElementById('statTotalAdmins').textContent = stats.total_admins;
        document.getElementById('statTotalReservations').textContent = stats.total_reservations;
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
    }
}

async function loadEtablissements() {
    try {
        const response = await fetch('/api/super-admin/etablissements');
        const etablissements = await response.json();
        
        const container = document.getElementById('etablissementsList');
        container.innerHTML = '';
        
        etablissements.forEach(etab => {
            const card = document.createElement('div');
            card.className = 'col-md-4 mb-3';
            card.innerHTML = `
                <div class="card etablissement-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">
                            ${etab.nom_etablissement}
                            <span class="badge ${etab.actif ? 'badge-actif' : 'badge-inactif'} float-end">
                                ${etab.actif ? 'Actif' : 'Inactif'}
                            </span>
                        </h5>
                        <p class="card-text">
                            <small class="text-muted">
                                <i class="bi bi-geo-alt"></i> ${etab.ville || 'N/A'}, ${etab.pays || 'N/A'}<br>
                                <i class="bi bi-telephone"></i> ${etab.telephone || 'N/A'}<br>
                                <i class="bi bi-envelope"></i> ${etab.email || 'N/A'}
                            </small>
                        </p>
                        <div class="d-grid gap-2">
                            <button class="btn btn-sm btn-primary" onclick="manageUsers(${etab.id})">
                                <i class="bi bi-people"></i> Gérer les utilisateurs
                            </button>
                            <button class="btn btn-sm btn-success" onclick="manageChambres(${etab.id})">
                                <i class="bi bi-door-open"></i> Gérer les chambres
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Erreur lors du chargement des établissements:', error);
    }
}

async function createEtablissement() {
    const form = document.getElementById('createEtablissementForm');
    const formData = new FormData(form);
    
    const etablissementData = {
        nom_etablissement: formData.get('nom_etablissement'),
        numero_identification: formData.get('numero_identification'),
        pays: formData.get('pays'),
        ville: formData.get('ville'),
        adresse: formData.get('adresse'),
        telephone: formData.get('telephone'),
        email: formData.get('email'),
        devise: formData.get('devise'),
        taux_taxe_sejour: parseFloat(formData.get('taux_taxe_sejour')),
        taux_tva: parseFloat(formData.get('taux_tva')),
        taux_charge_plateforme: 15.0
    };
    
    const adminData = {
        username: formData.get('admin_username'),
        password: formData.get('admin_password'),
        nom: formData.get('admin_nom'),
        prenom: formData.get('admin_prenom'),
        email: formData.get('admin_email')
    };
    
    try {
        const response = await fetch('/api/super-admin/etablissements', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                etablissement: etablissementData,
                admin: adminData
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Établissement créé avec succès!');
            bootstrap.Modal.getInstance(document.getElementById('createEtablissementModal')).hide();
            form.reset();
            loadStats();
            loadEtablissements();
        } else {
            alert('Erreur: ' + (result.error || 'Une erreur est survenue'));
        }
    } catch (error) {
        console.error('Erreur lors de la création:', error);
        alert('Erreur lors de la création de l\'établissement');
    }
}

async function manageUsers(etablissementId) {
    currentEtablissementId = etablissementId;
    
    try {
        const response = await fetch(`/api/super-admin/etablissements/${etablissementId}/users`);
        const users = await response.json();
        
        const usersList = document.getElementById('usersList');
        usersList.innerHTML = '<div class="table-responsive"><table class="table table-striped"><thead><tr><th>Nom d\'utilisateur</th><th>Nom</th><th>Prénom</th><th>Email</th><th>Actions</th></tr></thead><tbody id="usersTableBody"></tbody></table></div>';
        
        const tbody = document.getElementById('usersTableBody');
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.nom || ''}</td>
                <td>${user.prenom || ''}</td>
                <td>${user.email || ''}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="removeUser(${user.id})">
                        <i class="bi bi-trash"></i> Retirer
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        new bootstrap.Modal(document.getElementById('manageUsersModal')).show();
    } catch (error) {
        console.error('Erreur lors du chargement des utilisateurs:', error);
    }
}

function showAddUserForm() {
    document.getElementById('addUserForm').style.display = 'block';
}

function hideAddUserForm() {
    document.getElementById('addUserForm').style.display = 'none';
    document.getElementById('newUserUsername').value = '';
    document.getElementById('newUserPassword').value = '';
    document.getElementById('newUserNom').value = '';
    document.getElementById('newUserPrenom').value = '';
    document.getElementById('newUserEmail').value = '';
}

async function addUserToEtablissement() {
    const userData = {
        username: document.getElementById('newUserUsername').value,
        password: document.getElementById('newUserPassword').value,
        nom: document.getElementById('newUserNom').value,
        prenom: document.getElementById('newUserPrenom').value,
        email: document.getElementById('newUserEmail').value
    };
    
    if (!userData.username || !userData.password) {
        alert('Nom d\'utilisateur et mot de passe requis');
        return;
    }
    
    try {
        const response = await fetch(`/api/super-admin/etablissements/${currentEtablissementId}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Utilisateur créé avec succès!');
            hideAddUserForm();
            manageUsers(currentEtablissementId);
        } else {
            alert('Erreur: ' + (result.error || 'Une erreur est survenue'));
        }
    } catch (error) {
        console.error('Erreur lors de la création de l\'utilisateur:', error);
        alert('Erreur lors de la création de l\'utilisateur');
    }
}

async function removeUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir retirer cet utilisateur?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/super-admin/etablissements/${currentEtablissementId}/users/${userId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Utilisateur retiré avec succès!');
            manageUsers(currentEtablissementId);
        } else {
            alert('Erreur lors de la suppression de l\'utilisateur');
        }
    } catch (error) {
        console.error('Erreur lors de la suppression:', error);
        alert('Erreur lors de la suppression de l\'utilisateur');
    }
}

async function manageChambres(etablissementId) {
    currentEtablissementId = etablissementId;
    
    try {
        const response = await fetch(`/api/super-admin/etablissements/${etablissementId}/chambres`);
        const chambres = await response.json();
        
        const chambresList = document.getElementById('chambresList');
        chambresList.innerHTML = '<div class="table-responsive"><table class="table table-striped"><thead><tr><th>Nom</th><th>Capacité</th><th>Prix/nuit</th><th>Statut</th></tr></thead><tbody id="chambresTableBody"></tbody></table></div>';
        
        const tbody = document.getElementById('chambresTableBody');
        chambres.forEach(chambre => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${chambre.nom}</td>
                <td>${chambre.capacite}</td>
                <td>${chambre.prix_par_nuit} ${chambre.devise || ''}</td>
                <td>${chambre.statut}</td>
            `;
            tbody.appendChild(row);
        });
        
        new bootstrap.Modal(document.getElementById('manageChambresModal')).show();
    } catch (error) {
        console.error('Erreur lors du chargement des chambres:', error);
    }
}

function showAddChambreForm() {
    document.getElementById('addChambreForm').style.display = 'block';
}

function hideAddChambreForm() {
    document.getElementById('addChambreForm').style.display = 'none';
    document.getElementById('newChambreNom').value = '';
    document.getElementById('newChambreCapacite').value = '2';
    document.getElementById('newChambrePrix').value = '';
    document.getElementById('newChambreStatut').value = 'disponible';
    document.getElementById('newChambreDescription').value = '';
}

async function addChambreToEtablissement() {
    const chambreData = {
        nom: document.getElementById('newChambreNom').value,
        capacite: parseInt(document.getElementById('newChambreCapacite').value),
        prix_par_nuit: parseFloat(document.getElementById('newChambrePrix').value),
        statut: document.getElementById('newChambreStatut').value,
        description: document.getElementById('newChambreDescription').value
    };
    
    if (!chambreData.nom) {
        alert('Nom de la chambre requis');
        return;
    }
    
    try {
        const response = await fetch(`/api/super-admin/etablissements/${currentEtablissementId}/chambres`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(chambreData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            alert('Chambre créée avec succès!');
            hideAddChambreForm();
            manageChambres(currentEtablissementId);
        } else {
            alert('Erreur: ' + (result.error || 'Une erreur est survenue'));
        }
    } catch (error) {
        console.error('Erreur lors de la création de la chambre:', error);
        alert('Erreur lors de la création de la chambre');
    }
}
