// Tenant Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadTenantStats();
    loadMyEtablissements();
    loadMyEtablissementsForSelect();
});

function loadTenantStats() {
    fetch('/api/tenant/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('statsEtablissements').textContent = data.nb_etablissements || 0;
            document.getElementById('statsChambres').textContent = data.nb_chambres || 0;
            document.getElementById('statsReservations').textContent = data.nb_reservations || 0;
            document.getElementById('statsUsers').textContent = data.nb_users || 0;
        })
        .catch(error => console.error('Error loading stats:', error));
}

function loadMyEtablissements() {
    fetch('/api/tenant/etablissements')
        .then(response => response.json())
        .then(etablissements => {
            const tbody = document.getElementById('etablissementsBody');
            if (etablissements.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">Aucun établissement</td></tr>';
                return;
            }
            
            tbody.innerHTML = etablissements.map(etab => `
                <tr>
                    <td><strong>${etab.nom_etablissement}</strong></td>
                    <td>${etab.ville || '-'}</td>
                    <td>${etab.pays || '-'}</td>
                    <td>
                        <span class="badge bg-info" id="chambres-${etab.id}">...</span>
                    </td>
                    <td>
                        <span class="badge ${etab.actif ? 'bg-success' : 'bg-danger'}">
                            ${etab.actif ? 'Actif' : 'Inactif'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="viewEtablissement(${etab.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-success" onclick="manageChambres(${etab.id})">
                            <i class="bi bi-door-open"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
            
            // Load chamber count for each etablissement
            etablissements.forEach(etab => {
                loadChambresCount(etab.id);
            });
        })
        .catch(error => console.error('Error loading etablissements:', error));
}

function loadChambresCount(etablissementId) {
    fetch(`/api/tenant/etablissements/${etablissementId}/chambres`)
        .then(response => response.json())
        .then(chambres => {
            const badge = document.getElementById(`chambres-${etablissementId}`);
            if (badge) {
                badge.textContent = chambres.length;
            }
        })
        .catch(error => console.error(`Error loading chambres for etablissement ${etablissementId}:`, error));
}

function loadMyEtablissementsForSelect() {
    fetch('/api/tenant/etablissements')
        .then(response => response.json())
        .then(etablissements => {
            const select = document.getElementById('userEtablissementSelect');
            if (select) {
                select.innerHTML = etablissements.map(etab => 
                    `<option value="${etab.id}">${etab.nom_etablissement}</option>`
                ).join('');
            }
        })
        .catch(error => console.error('Error loading etablissements for select:', error));
}

function openAddEtablissementModal() {
    document.getElementById('addEtablissementModal').classList.add('active');
}

function closeAddEtablissementModal() {
    document.getElementById('addEtablissementModal').classList.remove('active');
    document.getElementById('addEtablissementForm').reset();
}

function addEtablissement() {
    const form = document.getElementById('addEtablissementForm');
    const formData = new FormData(form);
    
    const data = {
        nom_etablissement: formData.get('nom_etablissement'),
        ville: formData.get('ville'),
        pays: formData.get('pays'),
        email: formData.get('email'),
        adresse: formData.get('adresse'),
        telephone: formData.get('telephone'),
        devise: formData.get('devise')
    };
    
    fetch('/api/tenant/etablissements', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Établissement ajouté avec succès !');
            closeAddEtablissementModal();
            loadMyEtablissements();
            loadTenantStats();
            loadMyEtablissementsForSelect();
        } else {
            alert('Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erreur lors de l\'ajout de l\'établissement');
    });
}

function openManageUsersModal() {
    document.getElementById('manageUsersModal').classList.add('active');
    loadMyUsers();
}

function closeManageUsersModal() {
    document.getElementById('manageUsersModal').classList.remove('active');
    hideAddUserForm();
}

function loadMyUsers() {
    fetch('/api/tenant/users')
        .then(response => response.json())
        .then(users => {
            const tbody = document.getElementById('usersListBody');
            if (users.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">Aucun utilisateur</td></tr>';
                return;
            }
            
            tbody.innerHTML = users.map(user => `
                <tr>
                    <td>${user.nom || ''} ${user.prenom || ''}</td>
                    <td>${user.username}</td>
                    <td>${user.email || '-'}</td>
                    <td><small>${user.etablissements || '-'}</small></td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="removeUser(${user.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => console.error('Error loading users:', error));
}

function showAddUserForm() {
    document.getElementById('addUserFormContainer').style.display = 'block';
}

function hideAddUserForm() {
    document.getElementById('addUserFormContainer').style.display = 'none';
    document.getElementById('addUserForm').reset();
}

function addUser() {
    const form = document.getElementById('addUserForm');
    const formData = new FormData(form);
    
    const select = form.querySelector('[name="etablissement_ids"]');
    const etablissement_ids = Array.from(select.selectedOptions).map(option => parseInt(option.value));
    
    if (etablissement_ids.length === 0) {
        alert('Veuillez sélectionner au moins un établissement');
        return;
    }
    
    const data = {
        username: formData.get('username'),
        password: formData.get('password'),
        nom: formData.get('nom'),
        prenom: formData.get('prenom'),
        email: formData.get('email'),
        etablissement_ids: etablissement_ids
    };
    
    fetch('/api/tenant/users', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Utilisateur ajouté avec succès !');
            hideAddUserForm();
            loadMyUsers();
            loadTenantStats();
        } else {
            alert('Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erreur lors de l\'ajout de l\'utilisateur');
    });
}

function removeUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir retirer cet utilisateur ?')) {
        return;
    }
    
    fetch(`/api/tenant/users/${userId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Utilisateur retiré');
            loadMyUsers();
            loadTenantStats();
        } else {
            alert('Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erreur lors de la suppression');
    });
}

function viewEtablissement(etablissementId) {
    window.location.href = `/parametres?etablissement_id=${etablissementId}`;
}

function manageChambres(etablissementId) {
    // This would redirect to a chambres management page or open a modal
    alert(`Gestion des chambres pour l'établissement ${etablissementId} - À implémenter`);
}
