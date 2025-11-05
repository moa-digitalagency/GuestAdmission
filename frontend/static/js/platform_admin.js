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
    
    // Update sidebar links active state
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Update tab buttons (if they exist - for backwards compatibility)
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
    const sectionMap = {
        'dashboard': 'dashboardSection',
        'tenants': 'tenantsSection',
        'etablissements': 'etablissementsSection',
        'users': 'usersSection',
        'settings': 'settingsSection'
    };
    
    const sectionId = sectionMap[sectionName];
    const section = document.getElementById(sectionId);
    if (section) {
        section.style.display = 'block';
    }
    
    // Load data for the section
    if (sectionName === 'etablissements') {
        loadEtablissements();
    } else if (sectionName === 'users') {
        loadUsers();
    } else if (sectionName === 'settings') {
        loadPlatformSettings();
    }
}

function loadStats() {
    fetch('/api/platform-admin/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('statTenantsActifs').textContent = data.tenants_actifs || 0;
            document.getElementById('statEtablissementsActifs').textContent = data.etablissements_actifs || 0;
            document.getElementById('statTotalAdmins').textContent = data.total_admins || 0;
            document.getElementById('statTotalSejours').textContent = data.total_sejours || 0;
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
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1f2937;">${tenant.nb_sejours || 0}</div>
                            <small style="color: #6b7280;">Séjours</small>
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
                        ${user.nb_etablissements || 0} établissement(s)
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
    document.getElementById('chambresContainer').innerHTML = `
        <div class="form-grid chambre-row" data-chambre-index="0">
            <div class="form-group">
                <label>Nom de la chambre</label>
                <input type="text" name="chambre_nom_0" placeholder="ex: Chambre 101">
            </div>
            <div class="form-group">
                <label>Capacité</label>
                <input type="number" name="chambre_capacite_0" min="1" value="2">
            </div>
            <div class="form-group">
                <label>Prix par nuit</label>
                <input type="number" name="chambre_prix_0" min="0" step="0.01" placeholder="0.00">
            </div>
        </div>
    `;
}

let chambreCounter = 1;

function addChambreRow() {
    const container = document.getElementById('chambresContainer');
    const newRow = document.createElement('div');
    newRow.className = 'form-grid chambre-row';
    newRow.setAttribute('data-chambre-index', chambreCounter);
    newRow.innerHTML = `
        <div class="form-group">
            <label>Nom de la chambre</label>
            <input type="text" name="chambre_nom_${chambreCounter}" placeholder="ex: Chambre ${100 + chambreCounter}">
        </div>
        <div class="form-group">
            <label>Capacité</label>
            <input type="number" name="chambre_capacite_${chambreCounter}" min="1" value="2">
        </div>
        <div class="form-group">
            <label>Prix par nuit</label>
            <input type="number" name="chambre_prix_${chambreCounter}" min="0" step="0.01" placeholder="0.00">
        </div>
    `;
    container.appendChild(newRow);
    chambreCounter++;
}

function createTenant() {
    const form = document.getElementById('createTenantForm');
    const formData = new FormData(form);
    
    const chambres = [];
    const chambreRows = document.querySelectorAll('.chambre-row');
    chambreRows.forEach(row => {
        const index = row.getAttribute('data-chambre-index');
        const nom = formData.get(`chambre_nom_${index}`);
        const capacite = formData.get(`chambre_capacite_${index}`);
        const prix = formData.get(`chambre_prix_${index}`);
        
        if (nom && nom.trim()) {
            chambres.push({
                nom: nom,
                capacite: parseInt(capacite) || 2,
                prix_par_nuit: parseFloat(prix) || 0
            });
        }
    });
    
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
        },
        chambres: chambres
    };
    
    fetch('/api/platform-admin/tenants', {
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

// Platform Settings Management
function loadPlatformSettings() {
    fetch('/api/platform-settings')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.settings) {
                const settings = data.settings;
                document.getElementById('platform_name').value = settings.platform_name || '';
                document.getElementById('platform_logo_url').value = settings.platform_logo_url || '';
                document.getElementById('support_email').value = settings.support_email || '';
                document.getElementById('support_phone').value = settings.support_phone || '';
                document.getElementById('default_currency').value = settings.default_currency || 'MAD';
                document.getElementById('default_language').value = settings.default_language || 'fr';
                document.getElementById('maintenance_mode').checked = settings.maintenance_mode || false;
                document.getElementById('maintenance_message').value = settings.maintenance_message || '';
                document.getElementById('meta_title').value = settings.meta_title || '';
                document.getElementById('meta_description').value = settings.meta_description || '';
                document.getElementById('meta_keywords').value = settings.meta_keywords || '';
            }
        })
        .catch(error => {
            console.error('Error loading platform settings:', error);
            showNotification('Erreur lors du chargement des paramètres', 'error');
        });
}

function savePlatformSettings() {
    const settings = {
        platform_name: document.getElementById('platform_name').value,
        platform_logo_url: document.getElementById('platform_logo_url').value,
        support_email: document.getElementById('support_email').value,
        support_phone: document.getElementById('support_phone').value,
        default_currency: document.getElementById('default_currency').value,
        default_language: document.getElementById('default_language').value,
        maintenance_mode: document.getElementById('maintenance_mode').checked,
        maintenance_message: document.getElementById('maintenance_message').value,
        meta_title: document.getElementById('meta_title').value,
        meta_description: document.getElementById('meta_description').value,
        meta_keywords: document.getElementById('meta_keywords').value
    };
    
    fetch('/api/platform-settings', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('✅ Paramètres enregistrés avec succès', 'success');
        } else {
            showNotification('❌ Erreur: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error saving platform settings:', error);
        showNotification('❌ Erreur lors de l\'enregistrement', 'error');
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation CSS
if (!document.getElementById('notificationStyles')) {
    const style = document.createElement('style');
    style.id = 'notificationStyles';
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}
