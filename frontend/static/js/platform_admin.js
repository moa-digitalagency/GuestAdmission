// Platform Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    loadStats();
    loadTenants();
    setupSidebarNavigation();
});

function loadUserInfo() {
    fetch('/api/current-user')
        .then(response => response.json())
        .then(data => {
            document.getElementById('userInfo').textContent = `${data.nom || ''} ${data.prenom || ''} (${data.role})`;
        })
        .catch(error => console.error('Error loading user info:', error));
}

function loadStats() {
    fetch('/api/platform-admin/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('statTenantsActifs').textContent = data.tenants_actifs || 0;
            document.getElementById('statEtablissementsActifs').textContent = data.etablissements_actifs || 0;
            document.getElementById('statTotalAdmins').textContent = data.total_admins || 0;
            document.getElementById('statTotalReservations').textContent = data.total_reservations || 0;
        })
        .catch(error => console.error('Error loading stats:', error));
}

function loadTenants() {
    fetch('/api/platform-admin/tenants')
        .then(response => response.json())
        .then(tenants => {
            const container = document.getElementById('tenantsList');
            if (tenants.length === 0) {
                container.innerHTML = '<div class="col-12"><p class="text-center">Aucun compte client</p></div>';
                return;
            }
            
            container.innerHTML = tenants.map(tenant => `
                <div class="col-md-6 mb-3">
                    <div class="card tenant-card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h5 class="card-title">${tenant.nom_compte}</h5>
                                    <p class="card-text">
                                        <small class="text-muted">
                                            Créé le ${new Date(tenant.date_creation).toLocaleDateString('fr-FR')}
                                        </small>
                                    </p>
                                </div>
                                <span class="badge ${tenant.actif ? 'badge-actif' : 'badge-inactif'}">
                                    ${tenant.actif ? 'Actif' : 'Inactif'}
                                </span>
                            </div>
                            <hr>
                            <div class="row text-center">
                                <div class="col-4">
                                    <strong>${tenant.nb_etablissements || 0}</strong>
                                    <br><small>Établissements</small>
                                </div>
                                <div class="col-4">
                                    <strong>${tenant.nb_chambres || 0}</strong>
                                    <br><small>Chambres</small>
                                </div>
                                <div class="col-4">
                                    <strong>${tenant.nb_reservations || 0}</strong>
                                    <br><small>Réservations</small>
                                </div>
                            </div>
                            ${tenant.notes ? `<p class="mt-2 mb-0"><small>${tenant.notes}</small></p>` : ''}
                        </div>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error loading tenants:', error));
}

function loadEtablissements() {
    fetch('/api/platform-admin/etablissements')
        .then(response => response.json())
        .then(etablissements => {
            const container = document.getElementById('etablissementsList');
            if (etablissements.length === 0) {
                container.innerHTML = '<div class="col-12"><p class="text-center">Aucun établissement</p></div>';
                return;
            }
            
            container.innerHTML = etablissements.map(etab => `
                <div class="col-md-4 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">${etab.nom_etablissement}</h5>
                            <p class="card-text">
                                <small>${etab.ville || ''} ${etab.pays || ''}</small>
                            </p>
                            <span class="badge ${etab.actif ? 'badge-actif' : 'badge-inactif'}">
                                ${etab.actif ? 'Actif' : 'Inactif'}
                            </span>
                        </div>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error loading etablissements:', error));
}

function loadUsers() {
    fetch('/api/platform-admin/users')
        .then(response => response.json())
        .then(users => {
            const tbody = document.getElementById('usersList');
            if (users.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">Aucun utilisateur</td></tr>';
                return;
            }
            
            tbody.innerHTML = users.map(user => `
                <tr>
                    <td>${user.nom || '-'}</td>
                    <td>${user.prenom || '-'}</td>
                    <td>${user.email || '-'}</td>
                    <td>${user.username}</td>
                    <td>${user.nb_etablissements || 0}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => console.error('Error loading users:', error));
}

function setupSidebarNavigation() {
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.addEventListener('click', function() {
            document.querySelectorAll('.sidebar-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            const section = this.dataset.section;
            document.querySelectorAll('.content-section').forEach(s => s.style.display = 'none');
            
            if (section === 'dashboard') {
                document.getElementById('dashboardSection').style.display = 'block';
            } else if (section === 'tenants') {
                document.getElementById('tenantsSection').style.display = 'block';
                loadTenants();
            } else if (section === 'etablissements') {
                document.getElementById('etablissementsSection').style.display = 'block';
                loadEtablissements();
            } else if (section === 'users') {
                document.getElementById('usersSection').style.display = 'block';
                loadUsers();
            }
        });
    });
}

function createTenant() {
    const form = document.getElementById('createTenantForm');
    const formData = new FormData(form);
    
    const data = {
        tenant: {
            nom_compte: formData.get('nom_compte'),
            notes: formData.get('notes')
        },
        etablissement: {
            nom_etablissement: formData.get('nom_etablissement'),
            ville: formData.get('ville'),
            pays: formData.get('pays'),
            email: formData.get('email')
        },
        admin: {
            username: formData.get('admin_username'),
            password: formData.get('admin_password'),
            nom: formData.get('admin_nom'),
            prenom: formData.get('admin_prenom'),
            email: formData.get('admin_email')
        }
    };
    
    fetch('/api/platform-admin/tenants', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Compte client créé avec succès !');
            bootstrap.Modal.getInstance(document.getElementById('createTenantModal')).hide();
            form.reset();
            loadTenants();
            loadStats();
        } else {
            alert('Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erreur lors de la création du compte');
    });
}

function deleteUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
        return;
    }
    
    fetch(`/api/platform-admin/users/${userId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Utilisateur supprimé');
            loadUsers();
        } else {
            alert('Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erreur lors de la suppression');
    });
}
