// Platform Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadTenants();
    showSection('dashboard');
});

function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Update tab buttons
    document.querySelectorAll('.platform-tab').forEach(tab => {
        if (tab.dataset.section === sectionName) {
            tab.classList.remove('btn-secondary');
            tab.classList.add('btn-primary', 'active');
        } else {
            tab.classList.remove('btn-primary', 'active');
            tab.classList.add('btn-secondary');
        }
    });
    
    // Show selected section
    const section = document.getElementById(sectionName + 'Section');
    if (section) {
        section.style.display = 'block';
    }
    
    // Load data for the section
    if (sectionName === 'etablissements') {
        loadEtablissements();
    } else if (sectionName === 'users') {
        loadUsers();
    }
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
                container.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: #6b7280;">Aucun compte client</div>';
                return;
            }
            
            container.innerHTML = tenants.map(tenant => `
                <div class="dotted-section ${tenant.actif ? 'section-green' : 'section-orange'}" style="transition: transform 0.2s;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <div>
                            <h3 style="margin: 0 0 0.5rem 0; color: #1f2937;">${tenant.nom_compte}</h3>
                            <small style="color: #6b7280;">
                                Créé le ${new Date(tenant.date_creation).toLocaleDateString('fr-FR')}
                            </small>
                        </div>
                        <span class="badge ${tenant.actif ? 'badge-green' : 'badge-yellow'}">
                            ${tenant.actif ? '✓ Actif' : '⏸ Inactif'}
                        </span>
                    </div>
                    <hr style="border: none; border-top: 2px dotted ${tenant.actif ? '#22c55e' : '#f97316'}; margin: 1rem 0;">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                        <div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1f2937;">${tenant.nb_etablissements || 0}</div>
                            <small style="color: #6b7280;">Établissements</small>
                        </div>
                        <div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1f2937;">${tenant.nb_chambres || 0}</div>
                            <small style="color: #6b7280;">Chambres</small>
                        </div>
                        <div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1f2937;">${tenant.nb_reservations || 0}</div>
                            <small style="color: #6b7280;">Réservations</small>
                        </div>
                    </div>
                    ${tenant.notes ? `<p style="margin-top: 1rem; color: #6b7280; font-size: 0.875rem;">${tenant.notes}</p>` : ''}
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
                container.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 2rem; color: #6b7280;">Aucun établissement</div>';
                return;
            }
            
            container.innerHTML = etablissements.map(etab => `
                <div class="dotted-section ${etab.actif ? 'section-blue' : 'section-orange'}">
                    <h3 style="margin: 0 0 0.5rem 0;">${etab.nom_etablissement}</h3>
                    <p style="color: #6b7280; margin: 0.5rem 0;">
                        ${etab.ville || ''} ${etab.pays || ''}
                    </p>
                    <span class="badge ${etab.actif ? 'badge-green' : 'badge-yellow'}">
                        ${etab.actif ? '✓ Actif' : '⏸ Inactif'}
                    </span>
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
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: #6b7280;">Aucun utilisateur</td></tr>';
                return;
            }
            
            tbody.innerHTML = users.map(user => `
                <tr>
                    <td>${user.nom || '-'}</td>
                    <td>${user.prenom || '-'}</td>
                    <td>${user.email || '-'}</td>
                    <td>${user.username}</td>
                    <td>
                        ${user.etablissements && user.etablissements.length > 0 
                            ? user.etablissements.map(e => e.nom_etablissement).join(', ') 
                            : '-'}
                    </td>
                    <td>
                        <div class="actions">
                            <button class="btn btn-small btn-primary" onclick="editUser(${user.id})">✏️ Éditer</button>
                        </div>
                    </td>
                </tr>
            `).join('');
        })
        .catch(error => console.error('Error loading users:', error));
}

function openCreateTenantModal() {
    document.getElementById('createTenantModal').classList.add('active');
}

function closeCreateTenantModal() {
    document.getElementById('createTenantModal').classList.remove('active');
    document.getElementById('createTenantForm').reset();
}

function createTenant() {
    const form = document.getElementById('createTenantForm');
    const formData = new FormData(form);
    
    const data = {
        nom_compte: formData.get('nom_compte'),
        notes: formData.get('notes'),
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
    
    fetch('/api/platform-admin/create-tenant', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('✓ Compte client créé avec succès!');
            closeCreateTenantModal();
            loadTenants();
            loadStats();
        } else {
            alert('❌ Erreur: ' + (result.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Error creating tenant:', error);
        alert('❌ Erreur lors de la création du compte');
    });
}

function editUser(userId) {
    alert('Fonctionnalité d\'édition en développement pour l\'utilisateur #' + userId);
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    const modal = document.getElementById('createTenantModal');
    if (event.target === modal) {
        closeCreateTenantModal();
    }
});
