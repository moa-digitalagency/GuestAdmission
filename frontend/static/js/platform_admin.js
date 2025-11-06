// Platform Admin Dashboard JavaScript

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadTenants();
    showSection('dashboard');
});

window.showSection = function(sectionName) {
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
                <label>Type de chambre</label>
                <input type="text" name="chambre_type_0" placeholder="ex: Standard, Suite, Deluxe">
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

function createTenant() {
    const form = document.getElementById('createTenantForm');
    const formData = new FormData(form);
    
    const chambres = [];
    const chambreRows = document.querySelectorAll('.chambre-row');
    chambreRows.forEach(row => {
        const index = row.getAttribute('data-chambre-index');
        const nom = formData.get(`chambre_nom_${index}`);
        const type_chambre = formData.get(`chambre_type_${index}`);
        const capacite = formData.get(`chambre_capacite_${index}`);
        const prix = formData.get(`chambre_prix_${index}`);
        
        if (nom && nom.trim()) {
            chambres.push({
                nom: nom,
                type_chambre: type_chambre || '',
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
            numero_identification: formData.get('numero_identification'),
            logo_url: formData.get('logo_url'),
            pays: formData.get('pays'),
            ville: formData.get('ville'),
            adresse: formData.get('adresse'),
            telephone: formData.get('telephone'),
            whatsapp: formData.get('whatsapp'),
            email: formData.get('email_etablissement'),
            devise: formData.get('devise'),
            taux_taxe_sejour: parseFloat(formData.get('taux_taxe_sejour')) || 0,
            taux_tva: parseFloat(formData.get('taux_tva')) || 0,
            taux_charge_plateforme: parseFloat(formData.get('taux_charge_plateforme')) || 0,
            format_numero_reservation: formData.get('format_numero_reservation'),
            mode_tarification: formData.get('mode_tarification'),
            prix_global_nuitee: parseFloat(formData.get('prix_global_nuitee')) || null
        },
        admin: {
            username: formData.get('admin_username'),
            password: formData.get('admin_password'),
            nom: formData.get('admin_nom'),
            prenom: formData.get('admin_prenom'),
            email: formData.get('admin_email'),
            telephone: formData.get('admin_telephone')
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

// ============= WIZARD MULTI-ÉTAPES =============

let currentWizardStep = 1;
const totalWizardSteps = 4;

function openCreateTenantModal() {
    const modal = document.getElementById('createTenantModal');
    modal.classList.add('active');
    currentWizardStep = 1;
    showWizardStep(1);
    loadPays();
    initChambresContainer();
}

function closeCreateTenantModal() {
    const modal = document.getElementById('createTenantModal');
    modal.classList.remove('active');
    document.getElementById('createTenantForm').reset();
    currentWizardStep = 1;
}

function showWizardStep(step) {
    for (let i = 1; i <= totalWizardSteps; i++) {
        const stepContent = document.getElementById(`wizardStep${i}`);
        const stepNumber = document.querySelector(`.wizard-step[data-step="${i}"] .wizard-step-number`);
        
        if (stepContent) {
            stepContent.style.display = i === step ? 'block' : 'none';
        }
        
        if (stepNumber) {
            stepNumber.classList.remove('active', 'completed');
            if (i < step) {
                stepNumber.classList.add('completed');
            } else if (i === step) {
                stepNumber.classList.add('active');
            }
        }
    }
    
    const btnPrevious = document.getElementById('btnPrevious');
    const btnNext = document.getElementById('btnNext');
    const btnSubmit = document.getElementById('btnSubmit');
    
    btnPrevious.style.display = step > 1 ? 'inline-block' : 'none';
    btnNext.style.display = step < totalWizardSteps ? 'inline-block' : 'none';
    btnSubmit.style.display = step === totalWizardSteps ? 'inline-block' : 'none';
    
    if (step === 3) {
        updateStep3Info();
    }
    
    if (step === 4) {
        generateRecapitulatif();
    }
}

function nextStep() {
    if (!validateCurrentStep()) {
        return;
    }
    
    if (currentWizardStep < totalWizardSteps) {
        currentWizardStep++;
        showWizardStep(currentWizardStep);
    }
}

function previousStep() {
    if (currentWizardStep > 1) {
        currentWizardStep--;
        showWizardStep(currentWizardStep);
    }
}

function validateCurrentStep() {
    if (currentWizardStep === 1) {
        const nomCompte = document.getElementById('nom_compte').value.trim();
        const nomEtab = document.getElementById('nom_etablissement').value.trim();
        const pays = document.getElementById('pays').value;
        const ville = document.getElementById('ville').value;
        
        if (!nomCompte || !nomEtab || !pays || !ville) {
            showNotification('Veuillez remplir tous les champs obligatoires (Nom du compte, Établissement, Pays, Ville)', 'error');
            return false;
        }
        
        const modeTarif = document.querySelector('input[name="mode_tarification"]:checked').value;
        if (modeTarif === 'ETABLISSEMENT') {
            const prixGlobal = document.getElementById('prix_global_nuitee').value;
            if (!prixGlobal || prixGlobal <= 0) {
                showNotification('Veuillez indiquer le prix global par nuitée', 'error');
                return false;
            }
        }
    }
    
    if (currentWizardStep === 2) {
        const username = document.getElementById('admin_username').value.trim();
        const email = document.getElementById('admin_email').value.trim();
        const password = document.getElementById('admin_password').value;
        const confirmPassword = document.getElementById('admin_password_confirm').value;
        const prenom = document.getElementById('admin_prenom').value.trim();
        const nom = document.getElementById('admin_nom').value.trim();
        
        if (!username || !email || !password || !prenom || !nom) {
            showNotification('Veuillez remplir tous les champs obligatoires de l\'administrateur', 'error');
            return false;
        }
        
        if (password !== confirmPassword) {
            showNotification('Les mots de passe ne correspondent pas', 'error');
            return false;
        }
        
        if (password.length < 6) {
            showNotification('Le mot de passe doit contenir au moins 6 caractères', 'error');
            return false;
        }
    }
    
    if (currentWizardStep === 3) {
        const chambresRows = document.querySelectorAll('.chambre-row');
        if (chambresRows.length === 0) {
            showNotification('Veuillez ajouter au moins une chambre', 'error');
            return false;
        }
        
        let hasValidChambre = false;
        for (const row of chambresRows) {
            const index = row.getAttribute('data-chambre-index');
            const nom = document.querySelector(`[name="chambre_nom_${index}"]`).value.trim();
            if (nom) {
                hasValidChambre = true;
                break;
            }
        }
        
        if (!hasValidChambre) {
            showNotification('Veuillez renseigner au moins une chambre avec un nom', 'error');
            return false;
        }
    }
    
    return true;
}

function loadPays() {
    fetch('/api/pays')
        .then(response => response.json())
        .then(pays => {
            const select = document.getElementById('pays');
            select.innerHTML = '<option value="">Sélectionnez un pays</option>';
            pays.forEach(p => {
                const option = document.createElement('option');
                option.value = p.code;
                option.textContent = p.nom;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erreur lors du chargement des pays:', error);
        });
}

function loadVillesForPays() {
    const paysCode = document.getElementById('pays').value;
    const villeSelect = document.getElementById('ville');
    
    if (!paysCode) {
        villeSelect.innerHTML = '<option value="">Sélectionnez d\'abord un pays</option>';
        return;
    }
    
    fetch(`/api/villes/${paysCode}`)
        .then(response => response.json())
        .then(villes => {
            villeSelect.innerHTML = '<option value="">Sélectionnez une ville</option>';
            villes.forEach(ville => {
                const option = document.createElement('option');
                option.value = ville;
                option.textContent = ville;
                villeSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erreur lors du chargement des villes:', error);
            villeSelect.innerHTML = '<option value="">Erreur de chargement</option>';
        });
}

function togglePrixGlobal() {
    const modeTarif = document.querySelector('input[name="mode_tarification"]:checked').value;
    const prixGlobalGroup = document.getElementById('prixGlobalGroup');
    const prixGlobalInput = document.getElementById('prix_global_nuitee');
    
    if (modeTarif === 'ETABLISSEMENT') {
        prixGlobalGroup.style.display = 'block';
        prixGlobalInput.required = true;
    } else {
        prixGlobalGroup.style.display = 'none';
        prixGlobalInput.required = false;
    }
}

function initChambresContainer() {
    const container = document.getElementById('chambresContainer');
    container.innerHTML = '';
    chambreCounter = 0;
    addChambreRow();
}

function updateStep3Info() {
    const nomEtab = document.getElementById('nom_etablissement').value || '-';
    const modeTarif = document.querySelector('input[name="mode_tarification"]:checked').value;
    const modeTarifText = modeTarif === 'CHAMBRE' ? 'Prix fixe par chambre' : 'Prix global établissement';
    
    document.getElementById('recapEtablissement').textContent = nomEtab;
    document.getElementById('recapModeTarif').textContent = modeTarifText;
    
    const modeTarifInfo = document.getElementById('modeTarifInfo');
    if (modeTarif === 'ETABLISSEMENT') {
        const prixGlobal = document.getElementById('prix_global_nuitee').value;
        modeTarifInfo.innerHTML = `Mode de tarification: <strong>${modeTarifText}</strong> - Prix: ${prixGlobal || '0'} ${document.getElementById('devise').value || 'MAD'}`;
    } else {
        modeTarifInfo.innerHTML = `Mode de tarification: <strong>${modeTarifText}</strong>`;
    }
    
    const chambresContainer = document.getElementById('chambresContainer');
    if (chambresContainer.children.length === 0) {
        initChambresContainer();
    }
}

function generateRecapitulatif() {
    const etablissementDetails = `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
            <div><strong>Compte:</strong> ${document.getElementById('nom_compte').value || '-'}</div>
            <div><strong>Établissement:</strong> ${document.getElementById('nom_etablissement').value || '-'}</div>
            <div><strong>N° identification:</strong> ${document.getElementById('numero_identification').value || '-'}</div>
            <div><strong>Pays:</strong> ${document.getElementById('pays').selectedOptions[0]?.text || '-'}</div>
            <div><strong>Ville:</strong> ${document.getElementById('ville').value || '-'}</div>
            <div><strong>Téléphone:</strong> ${document.getElementById('telephone').value || '-'}</div>
            <div><strong>WhatsApp:</strong> ${document.getElementById('whatsapp').value || '-'}</div>
            <div><strong>Email:</strong> ${document.getElementById('email_etablissement').value || '-'}</div>
            <div><strong>Devise:</strong> ${document.getElementById('devise').value || '-'}</div>
            <div><strong>Taxe séjour:</strong> ${document.getElementById('taux_taxe_sejour').value || '0'}%</div>
            <div><strong>TVA:</strong> ${document.getElementById('taux_tva').value || '0'}%</div>
            <div><strong>Charge plateforme:</strong> ${document.getElementById('taux_charge_plateforme').value || '0'}%</div>
            <div style="grid-column: 1 / -1;"><strong>Mode tarification:</strong> ${document.querySelector('input[name="mode_tarification"]:checked').value === 'CHAMBRE' ? 'Prix par chambre' : 'Prix global établissement'}</div>
            ${document.querySelector('input[name="mode_tarification"]:checked').value === 'ETABLISSEMENT' ? `<div style="grid-column: 1 / -1;"><strong>Prix global/nuit:</strong> ${document.getElementById('prix_global_nuitee').value || '0'} ${document.getElementById('devise').value || 'MAD'}</div>` : ''}
        </div>
    `;
    
    const adminDetails = `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
            <div><strong>Username:</strong> ${document.getElementById('admin_username').value || '-'}</div>
            <div><strong>Email:</strong> ${document.getElementById('admin_email').value || '-'}</div>
            <div><strong>Prénom:</strong> ${document.getElementById('admin_prenom').value || '-'}</div>
            <div><strong>Nom:</strong> ${document.getElementById('admin_nom').value || '-'}</div>
            <div><strong>Téléphone:</strong> ${document.getElementById('admin_telephone').value || '-'}</div>
            <div><strong>Accès tableau de bord:</strong> ${document.getElementById('admin_page_acces').checked ? 'Oui' : 'Non'}</div>
        </div>
    `;
    
    let chambresHTML = '';
    const chambresRows = document.querySelectorAll('.chambre-row');
    const modeTarif = document.querySelector('input[name="mode_tarification"]:checked').value;
    
    chambresRows.forEach(row => {
        const index = row.getAttribute('data-chambre-index');
        const nom = document.querySelector(`[name="chambre_nom_${index}"]`)?.value;
        const capacite = document.querySelector(`[name="chambre_capacite_${index}"]`)?.value;
        const prix = document.querySelector(`[name="chambre_prix_${index}"]`)?.value;
        const type = document.querySelector(`[name="chambre_type_${index}"]`)?.value;
        
        if (nom && nom.trim()) {
            chambresHTML += `
                <div style="padding: 0.75rem; background: #f9fafb; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                    <div><strong>${nom}</strong> - Capacité: ${capacite || '2'} ${type ? `- Type: ${type}` : ''}</div>
                    ${modeTarif === 'CHAMBRE' ? `<div style="color: #6b7280; font-size: 0.875rem;">Prix: ${prix || '0'} ${document.getElementById('devise').value || 'MAD'}/nuit</div>` : ''}
                </div>
            `;
        }
    });
    
    if (!chambresHTML) {
        chambresHTML = '<p style="color: #6b7280; font-style: italic;">Aucune chambre configurée</p>';
    }
    
    document.getElementById('recapEtablissementDetails').innerHTML = etablissementDetails;
    document.getElementById('recapAdminDetails').innerHTML = adminDetails;
    document.getElementById('recapChambresDetails').innerHTML = chambresHTML;
}

let chambreCounter = 0;

function addChambreRow() {
    const container = document.getElementById('chambresContainer');
    const modeTarif = document.querySelector('input[name="mode_tarification"]:checked').value;
    const newRow = document.createElement('div');
    newRow.className = 'form-grid chambre-row';
    newRow.setAttribute('data-chambre-index', chambreCounter);
    newRow.style.marginBottom = '1rem';
    newRow.style.padding = '1rem';
    newRow.style.background = '#f9fafb';
    newRow.style.borderRadius = '0.5rem';
    newRow.innerHTML = `
        <div class="form-group">
            <label>Nom/Numéro de la chambre *</label>
            <input type="text" name="chambre_nom_${chambreCounter}" placeholder="ex: Chambre 101">
        </div>
        <div class="form-group">
            <label>Type de chambre</label>
            <select name="chambre_type_${chambreCounter}">
                <option value="">Sélectionnez...</option>
                <option value="Standard">Standard</option>
                <option value="Deluxe">Deluxe</option>
                <option value="Suite">Suite</option>
                <option value="Familiale">Familiale</option>
                <option value="Double">Double</option>
                <option value="Simple">Simple</option>
            </select>
        </div>
        <div class="form-group">
            <label>Capacité</label>
            <input type="number" name="chambre_capacite_${chambreCounter}" min="1" value="2">
        </div>
        ${modeTarif === 'CHAMBRE' ? `
        <div class="form-group">
            <label>Prix par nuitée</label>
            <input type="number" name="chambre_prix_${chambreCounter}" min="0" step="0.01" placeholder="0.00">
        </div>
        ` : ''}
        <div class="form-group" style="display: flex; align-items: flex-end;">
            <button type="button" class="btn btn-danger btn-small" onclick="removeChambreRow(${chambreCounter})">🗑 Supprimer</button>
        </div>
    `;
    container.appendChild(newRow);
    chambreCounter++;
}

function removeChambreRow(index) {
    const row = document.querySelector(`.chambre-row[data-chambre-index="${index}"]`);
    if (row) {
        row.remove();
    }
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
        const type = formData.get(`chambre_type_${index}`);
        
        if (nom && nom.trim()) {
            chambres.push({
                nom: nom,
                capacite: parseInt(capacite) || 2,
                prix_par_nuit: parseFloat(prix) || 0,
                type: type || null
            });
        }
    });
    
    const data = {
        tenant: {
            nom_compte: formData.get('nom_compte'),
            notes: formData.get('notes') || ''
        },
        etablissement: {
            nom_etablissement: formData.get('nom_etablissement'),
            numero_identification: formData.get('numero_identification'),
            logo_url: formData.get('logo_url'),
            pays: document.getElementById('pays').selectedOptions[0]?.text || formData.get('pays'),
            ville: formData.get('ville'),
            adresse: formData.get('adresse'),
            telephone: formData.get('telephone'),
            whatsapp: formData.get('whatsapp'),
            email: formData.get('email_etablissement'),
            devise: formData.get('devise'),
            taux_taxe_sejour: parseFloat(formData.get('taux_taxe_sejour')) || null,
            taux_tva: parseFloat(formData.get('taux_tva')) || null,
            taux_charge_plateforme: parseFloat(formData.get('taux_charge_plateforme')) || null,
            format_numero_reservation: formData.get('format_numero_reservation') || 'RES-{YYYY}{MM}{DD}-{NUM}',
            mode_tarification: formData.get('mode_tarification') || 'CHAMBRE',
            prix_global_nuitee: formData.get('mode_tarification') === 'ETABLISSEMENT' ? parseFloat(formData.get('prix_global_nuitee')) : null
        },
        admin: {
            username: formData.get('admin_username'),
            email: formData.get('admin_email'),
            password: formData.get('admin_password'),
            nom: formData.get('admin_nom'),
            prenom: formData.get('admin_prenom'),
            telephone: formData.get('admin_telephone'),
            page_acces: formData.get('admin_page_acces') === 'on'
        },
        chambres: chambres
    };
    
    fetch('/api/platform-admin/tenants', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showNotification('✓ Compte client créé avec succès!', 'success');
            closeCreateTenantModal();
            loadTenants();
            loadStats();
        } else {
            showNotification('❌ Erreur: ' + (result.error || 'Erreur inconnue'), 'error');
        }
    })
    .catch(error => {
        console.error('Error creating tenant:', error);
        showNotification('❌ Erreur lors de la création du compte', 'error');
    });
}
