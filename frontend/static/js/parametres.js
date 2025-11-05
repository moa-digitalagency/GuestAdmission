console.log('✅ Script parametres.js chargé - DÉBUT');

let etablissements = [];
let chambres = [];
let personnels = [];
let countriesData = [];
let editingEtablissement = null;

function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
}

async function loadCountries() {
    try {
        const response = await fetch('/static/data/countries.json');
        countriesData = await response.json();
    } catch (error) {
        console.error('Erreur chargement pays:', error);
    }
}

function populateCountrySelect(selectElement, selectedValue = '') {
    selectElement.innerHTML = '<option value="">Sélectionner un pays...</option>';
    countriesData.forEach(country => {
        const option = document.createElement('option');
        option.value = country.name;
        option.textContent = `${country.flag} ${country.name}`;
        if (country.cities) {
            option.dataset.cities = JSON.stringify(country.cities);
        }
        selectElement.appendChild(option);
    });
    if (selectedValue) {
        selectElement.value = selectedValue;
    }
}

function populateVilleSelect(paysSelect, villeSelect, selectedVille = '') {
    const selectedOption = paysSelect.options[paysSelect.selectedIndex];
    villeSelect.innerHTML = '<option value="">Sélectionner une ville...</option>';
    
    if (selectedOption && selectedOption.dataset.cities) {
        try {
            const cities = JSON.parse(selectedOption.dataset.cities);
            cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                villeSelect.appendChild(option);
            });
            villeSelect.disabled = false;
            if (selectedVille) {
                setTimeout(() => { villeSelect.value = selectedVille; }, 10);
            }
        } catch (e) {
            villeSelect.disabled = true;
        }
    } else {
        villeSelect.disabled = true;
    }
}

async function loadEtablissements() {
    try {
        const response = await fetch('/api/etablissements?actif_only=false');
        if (!response.ok) {
            throw new Error(`Erreur chargement établissements: ${response.status}`);
        }
        etablissements = await response.json();
        renderEtablissements();
    } catch (error) {
        console.error('Erreur chargement établissements:', error);
        const container = document.getElementById('etablissements-container');
        container.innerHTML = '<p style="text-align: center; color: #dc2626; padding: 2rem;">❌ Erreur lors du chargement des établissements. Veuillez actualiser la page.</p>';
    }
}

function renderEtablissements() {
    const container = document.getElementById('etablissements-container');
    container.innerHTML = '';
    
    if (etablissements.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">Aucun établissement. Cliquez sur "Ajouter un établissement" pour commencer.</p>';
        return;
    }
    
    etablissements.forEach((etab, index) => {
        const card = document.createElement('div');
        card.className = 'dotted-section section-green';
        card.style.marginBottom = '1.5rem';
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #059669;">
                    ${etab.actif ? '🏢' : '⭕'} ${etab.nom_etablissement || 'Nouvel établissement'}
                </h3>
                <div style="display: flex; gap: 0.5rem;">
                    <button type="button" class="btn btn-primary btn-small" onclick="editEtablissement(${etab.id})">
                        ✏️ Modifier
                    </button>
                    <button type="button" class="btn ${etab.actif ? 'btn-secondary' : 'btn-success'} btn-small" onclick="toggleEtablissementStatus(${etab.id})">
                        ${etab.actif ? '🚫 Désactiver' : '✅ Activer'}
                    </button>
                    <button type="button" class="btn btn-danger btn-small" onclick="deleteEtablissement(${etab.id})">
                        🗑️ Supprimer
                    </button>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; color: #374151;">
                <div>
                    <strong>Pays:</strong> ${etab.pays || 'Non défini'}
                </div>
                <div>
                    <strong>Ville:</strong> ${etab.ville || 'Non définie'}
                </div>
                <div>
                    <strong>Téléphone:</strong> ${etab.telephone || 'Non défini'}
                </div>
                <div>
                    <strong>Email:</strong> ${etab.email || 'Non défini'}
                </div>
                <div>
                    <strong>Devise:</strong> ${etab.devise || 'MAD'}
                </div>
                <div>
                    <strong>Statut:</strong> <span style="color: ${etab.actif ? '#059669' : '#dc2626'};">${etab.actif ? 'Actif' : 'Inactif'}</span>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

async function addEtablissement() {
    console.log('✅ addEtablissement appelée');
    showEtablissementModal(null);
}

async function editEtablissement(id) {
    try {
        const response = await fetch(`/api/etablissements/${id}`);
        const etab = await response.json();
        showEtablissementModal(etab);
    } catch (error) {
        console.error('Erreur chargement établissement:', error);
        showAlert('Erreur lors du chargement de l\'établissement', 'error');
    }
}

async function deleteEtablissement(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet établissement ? Cette action est irréversible.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/etablissements/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('Établissement supprimé avec succès', 'success');
            loadEtablissements();
        } else {
            showAlert('Erreur lors de la suppression', 'error');
        }
    } catch (error) {
        console.error('Erreur suppression:', error);
        showAlert('Erreur lors de la suppression', 'error');
    }
}

async function toggleEtablissementStatus(id) {
    try {
        const response = await fetch(`/api/etablissements/${id}`);
        const etab = await response.json();
        
        const updateResponse = await fetch(`/api/etablissements/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ...etab, actif: !etab.actif })
        });
        
        if (updateResponse.ok) {
            showAlert(`Établissement ${!etab.actif ? 'activé' : 'désactivé'} avec succès`, 'success');
            loadEtablissements();
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du changement de statut', 'error');
    }
}

function showEtablissementModal(etab) {
    const isEdit = etab !== null;
    editingEtablissement = etab;
    
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center; overflow-y: auto; padding: 2rem;';
    modal.id = 'etablissementModal';
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 12px; max-width: 900px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 2rem; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2 style="margin: 0;">${isEdit ? '✏️ Modifier l\'établissement' : '➕ Nouvel établissement'}</h2>
                <button type="button" onclick="closeModal()" class="btn btn-secondary btn-small">✖ Fermer</button>
            </div>
            
            <form id="etablissementForm">
                <div class="dotted-section section-blue" style="margin-bottom: 1.5rem;">
                    <h3>📝 Informations générales</h3>
                    <div class="form-grid">
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_nom">Nom de l'établissement *</label>
                            <input type="text" id="etab_nom" value="${etab?.nom_etablissement || ''}" required>
                        </div>
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_numero">Numéro d'identification (ICE, SIRET, EIN, etc.)</label>
                            <input type="text" id="etab_numero" value="${etab?.numero_identification || ''}" placeholder="Ex: ICE001234567890">
                        </div>
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_logo_file">Logo de l'établissement</label>
                            <input type="file" id="etab_logo_file" accept="image/*" style="padding: 0.5rem;">
                            <input type="hidden" id="etab_logo_url" value="${etab?.logo_url || ''}">
                            <div id="etab_logo_preview" style="margin-top: 1rem;">
                                ${etab?.logo_url ? `<img src="${etab.logo_url}" alt="Logo" style="max-width: 200px; max-height: 100px; border: 2px solid #e5e7eb; border-radius: 8px; padding: 0.5rem;">` : ''}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="dotted-section section-green" style="margin-bottom: 1.5rem;">
                    <h3>📍 Localisation</h3>
                    <div class="form-grid">
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_pays">Pays *</label>
                            <select id="etab_pays" required>
                                <option value="">Sélectionner un pays...</option>
                            </select>
                        </div>
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_ville">Ville</label>
                            <select id="etab_ville">
                                <option value="">Sélectionner une ville...</option>
                            </select>
                        </div>
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_adresse">Adresse complète</label>
                            <textarea id="etab_adresse" rows="3">${etab?.adresse || ''}</textarea>
                        </div>
                    </div>
                </div>
                
                <div class="dotted-section section-purple" style="margin-bottom: 1.5rem;">
                    <h3>📞 Contact</h3>
                    <div class="form-grid">
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_telephone">Téléphone</label>
                            <input type="tel" id="etab_telephone" value="${etab?.telephone || ''}" placeholder="+212 XXX XXX XXX">
                        </div>
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_whatsapp">WhatsApp</label>
                            <input type="tel" id="etab_whatsapp" value="${etab?.whatsapp || ''}" placeholder="+212 XXX XXX XXX">
                        </div>
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_email">Email</label>
                            <input type="email" id="etab_email" value="${etab?.email || ''}" placeholder="contact@etablissement.com">
                        </div>
                    </div>
                </div>
                
                <div class="dotted-section section-orange" style="margin-bottom: 1.5rem;">
                    <h3>💰 Tarification</h3>
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="etab_devise">Devise *</label>
                            <select id="etab_devise" required>
                                <option value="MAD" ${!etab || etab.devise === 'MAD' ? 'selected' : ''}>MAD - Dirham marocain</option>
                                <option value="EUR" ${etab?.devise === 'EUR' ? 'selected' : ''}>EUR - Euro</option>
                                <option value="USD" ${etab?.devise === 'USD' ? 'selected' : ''}>USD - Dollar américain</option>
                                <option value="GBP" ${etab?.devise === 'GBP' ? 'selected' : ''}>GBP - Livre sterling</option>
                                <option value="CHF" ${etab?.devise === 'CHF' ? 'selected' : ''}>CHF - Franc suisse</option>
                                <option value="CAD" ${etab?.devise === 'CAD' ? 'selected' : ''}>CAD - Dollar canadien</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="etab_taxe_sejour">Taxe de séjour (%)</label>
                            <input type="number" id="etab_taxe_sejour" step="0.01" value="${etab?.taux_taxe_sejour || 0}">
                        </div>
                        <div class="form-group">
                            <label for="etab_tva">TVA (%)</label>
                            <input type="number" id="etab_tva" step="0.01" value="${etab?.taux_tva || 0}">
                        </div>
                        <div class="form-group">
                            <label for="etab_charge_plateforme">Charge plateforme (%)</label>
                            <input type="number" id="etab_charge_plateforme" step="0.01" value="${etab?.taux_charge_plateforme || 0}">
                        </div>
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label for="etab_format_numero">Format de numéro de séjour</label>
                            <input type="text" id="etab_format_numero" value="${etab?.format_numero_reservation || 'RES-{YYYY}{MM}{DD}-{NUM}'}">
                            <small style="color: #6b7280; display: block; margin-top: 0.25rem;">
                                Variables: {YYYY} = année, {MM} = mois, {DD} = jour, {NUM} = numéro séquentiel
                            </small>
                        </div>
                    </div>
                </div>
                
                <div class="button-group">
                    <button type="submit" class="btn btn-success">💾 Enregistrer</button>
                    <button type="button" onclick="closeModal()" class="btn btn-secondary">Annuler</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    populateCountrySelect(document.getElementById('etab_pays'), etab?.pays || '');
    
    const paysSelect = document.getElementById('etab_pays');
    const villeSelect = document.getElementById('etab_ville');
    
    paysSelect.addEventListener('change', () => {
        populateVilleSelect(paysSelect, villeSelect);
    });
    
    if (etab?.pays) {
        setTimeout(() => {
            populateVilleSelect(paysSelect, villeSelect, etab?.ville || '');
        }, 50);
    }
    
    document.getElementById('etab_logo_file').addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('logo', file);
            
            try {
                const response = await fetch('/api/etablissements/upload-logo', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                if (result.success) {
                    document.getElementById('etab_logo_url').value = result.logo_url;
                    document.getElementById('etab_logo_preview').innerHTML = `
                        <img src="${result.logo_url}" alt="Logo" style="max-width: 200px; max-height: 100px; border: 2px solid #e5e7eb; border-radius: 8px; padding: 0.5rem;">
                    `;
                    showAlert('✅ Logo téléchargé avec succès!', 'success');
                } else {
                    showAlert('❌ ' + result.error, 'error');
                }
            } catch (error) {
                console.error('Erreur upload logo:', error);
                showAlert('❌ Erreur lors du téléchargement du logo', 'error');
            }
        }
    });
    
    document.getElementById('etablissementForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveEtablissement();
    });
}

function closeModal() {
    const modal = document.getElementById('etablissementModal');
    if (modal) {
        modal.remove();
    }
    editingEtablissement = null;
}

async function saveEtablissement() {
    const data = {
        nom_etablissement: document.getElementById('etab_nom').value,
        numero_identification: document.getElementById('etab_numero').value,
        logo_url: document.getElementById('etab_logo_url').value,
        pays: document.getElementById('etab_pays').value,
        ville: document.getElementById('etab_ville').value,
        adresse: document.getElementById('etab_adresse').value,
        telephone: document.getElementById('etab_telephone').value,
        whatsapp: document.getElementById('etab_whatsapp').value,
        email: document.getElementById('etab_email').value,
        devise: document.getElementById('etab_devise').value,
        taux_taxe_sejour: parseFloat(document.getElementById('etab_taxe_sejour').value) || 0,
        taux_tva: parseFloat(document.getElementById('etab_tva').value) || 0,
        taux_charge_plateforme: parseFloat(document.getElementById('etab_charge_plateforme').value) || 0,
        format_numero_reservation: document.getElementById('etab_format_numero').value,
        actif: editingEtablissement?.actif !== false
    };
    
    try {
        const url = editingEtablissement 
            ? `/api/etablissements/${editingEtablissement.id}`
            : '/api/etablissements';
        const method = editingEtablissement ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert(`Établissement ${editingEtablissement ? 'modifié' : 'créé'} avec succès!`, 'success');
            closeModal();
            loadEtablissements();
        } else {
            const errorData = await response.json();
            showAlert(`Erreur: ${errorData.error || 'Erreur inconnue'}`, 'error');
        }
    } catch (error) {
        console.error('Erreur sauvegarde:', error);
        showAlert('Erreur lors de la sauvegarde', 'error');
    }
}

async function loadChambres() {
    try {
        const response = await fetch('/api/chambres');
        chambres = await response.json();
        renderChambres();
    } catch (error) {
        console.error('Erreur chargement chambres:', error);
    }
}

function renderChambres() {
    const container = document.getElementById('chambres-container');
    container.innerHTML = '';
    
    if (chambres.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">Aucune chambre. Cliquez sur "Ajouter une chambre" pour commencer.</p>';
        return;
    }
    
    chambres.forEach(chambre => {
        const etab = etablissements.find(e => e.id === chambre.etablissement_id);
        const isDisponible = chambre.statut === 'disponible';
        const card = document.createElement('div');
        card.className = 'dotted-section section-purple';
        card.style.marginBottom = '1.5rem';
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #7c3aed;">
                    ${isDisponible ? '🏠' : '⭕'} ${chambre.nom}
                </h3>
                <div style="display: flex; gap: 0.5rem;">
                    <button type="button" class="btn btn-primary btn-small" onclick="editChambre(${chambre.id})">
                        ✏️ Modifier
                    </button>
                    <button type="button" class="btn btn-danger btn-small" onclick="deleteChambre(${chambre.id})">
                        🗑️ Supprimer
                    </button>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; color: #374151;">
                <div>
                    <strong>Établissement:</strong> ${etab?.nom_etablissement || 'N/A'}
                </div>
                <div>
                    <strong>Description:</strong> ${chambre.description || 'N/A'}
                </div>
                <div>
                    <strong>Capacité:</strong> ${chambre.capacite || 'N/A'} pers.
                </div>
                <div>
                    <strong>Prix/nuit:</strong> ${chambre.prix_par_nuit || 0} MAD
                </div>
                <div>
                    <strong>Statut:</strong> <span style="color: ${isDisponible ? '#059669' : '#dc2626'};">${isDisponible ? 'Disponible' : 'Occupée'}</span>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

async function addChambre() {
    console.log('✅ addChambre appelée');
    showChambreModal(null);
}

async function editChambre(id) {
    try {
        const response = await fetch(`/api/chambres/${id}`);
        const chambre = await response.json();
        showChambreModal(chambre);
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement de la chambre', 'error');
    }
}

async function deleteChambre(id) {
    if (!confirm('Supprimer cette chambre?')) return;
    
    try {
        const response = await fetch(`/api/chambres/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showAlert('Chambre supprimée', 'success');
            loadChambres();
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la suppression', 'error');
    }
}

function showChambreModal(chambre) {
    const isEdit = chambre !== null;
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 2rem;';
    modal.id = 'chambreModal';
    
    const etablissementsActifs = etablissements.filter(e => e.actif);
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 12px; max-width: 600px; width: 100%; padding: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2 style="margin: 0;">${isEdit ? '✏️ Modifier la chambre' : '➕ Nouvelle chambre'}</h2>
                <button type="button" onclick="closeChambreModal()" class="btn btn-secondary btn-small">✖ Fermer</button>
            </div>
            <form id="chambreForm">
                <div class="form-grid">
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Établissement *</label>
                        <select id="chambre_etab" required>
                            <option value="">Sélectionner...</option>
                            ${etablissementsActifs.map(e => `<option value="${e.id}" ${chambre?.etablissement_id === e.id ? 'selected' : ''}>${e.nom_etablissement}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Numéro *</label>
                        <input type="text" id="chambre_numero" value="${chambre?.nom?.split(' - ')[0] || ''}" required>
                    </div>
                    <div class="form-group">
                        <label>Type *</label>
                        <select id="chambre_type" required>
                            <option value="Simple" ${chambre?.description === 'Simple' ? 'selected' : ''}>Simple</option>
                            <option value="Double" ${chambre?.description === 'Double' ? 'selected' : ''}>Double</option>
                            <option value="Suite" ${chambre?.description === 'Suite' ? 'selected' : ''}>Suite</option>
                            <option value="Familiale" ${chambre?.description === 'Familiale' ? 'selected' : ''}>Familiale</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Capacité</label>
                        <input type="number" id="chambre_capacite" value="${chambre?.capacite || 2}">
                    </div>
                    <div class="form-group">
                        <label>Prix par nuit</label>
                        <input type="number" id="chambre_prix" step="0.01" value="${chambre?.prix_par_nuit || 0}">
                    </div>
                </div>
                <div class="button-group">
                    <button type="submit" class="btn btn-success">💾 Enregistrer</button>
                    <button type="button" onclick="closeChambreModal()" class="btn btn-secondary">Annuler</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('chambreForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveChambre(chambre);
    });
}

function closeChambreModal() {
    const modal = document.getElementById('chambreModal');
    if (modal) modal.remove();
}

async function saveChambre(chambre) {
    const numero = document.getElementById('chambre_numero').value;
    const type = document.getElementById('chambre_type').value;
    
    const data = {
        etablissement_id: parseInt(document.getElementById('chambre_etab').value),
        nom: `${numero} - ${type}`,
        description: type,
        capacite: parseInt(document.getElementById('chambre_capacite').value),
        prix_par_nuit: parseFloat(document.getElementById('chambre_prix').value),
        statut: chambre?.statut || 'disponible'
    };
    
    try {
        const url = chambre ? `/api/chambres/${chambre.id}` : '/api/chambres';
        const method = chambre ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Chambre enregistrée!', 'success');
            closeChambreModal();
            loadChambres();
        } else {
            const errorData = await response.json();
            showAlert(`Erreur: ${errorData.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la sauvegarde', 'error');
    }
}

async function loadPersonnels() {
    try {
        const response = await fetch('/api/personnels');
        personnels = await response.json();
        renderPersonnels();
    } catch (error) {
        console.error('Erreur chargement personnels:', error);
    }
}

function renderPersonnels() {
    const container = document.getElementById('personnels-container');
    container.innerHTML = '';
    
    if (personnels.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #6b7280; padding: 2rem;">Aucun personnel. Cliquez sur "Ajouter un personnel" pour commencer.</p>';
        return;
    }
    
    personnels.forEach(personnel => {
        const card = document.createElement('div');
        card.className = 'dotted-section section-orange';
        card.style.marginBottom = '1.5rem';
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: #f97316;">
                    👤 ${personnel.prenom} ${personnel.nom}
                </h3>
                <div style="display: flex; gap: 0.5rem;">
                    <button type="button" class="btn btn-primary btn-small" onclick="editPersonnel(${personnel.id})">
                        ✏️ Modifier
                    </button>
                    <button type="button" class="btn btn-danger btn-small" onclick="deletePersonnel(${personnel.id})">
                        🗑️ Supprimer
                    </button>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; color: #374151;">
                <div>
                    <strong>Email:</strong> ${personnel.email || 'N/A'}
                </div>
                <div>
                    <strong>Téléphone:</strong> ${personnel.telephone || 'N/A'}
                </div>
                <div>
                    <strong>Rôle:</strong> ${personnel.role || 'N/A'}
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

async function addPersonnel() {
    console.log('✅ addPersonnel appelée');
    showPersonnelModal(null);
}

async function editPersonnel(id) {
    try {
        const response = await fetch(`/api/personnels/${id}`);
        const personnel = await response.json();
        showPersonnelModal(personnel);
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors du chargement du personnel', 'error');
    }
}

async function deletePersonnel(id) {
    if (!confirm('Supprimer ce personnel?')) return;
    
    try {
        const response = await fetch(`/api/personnels/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showAlert('Personnel supprimé', 'success');
            loadPersonnels();
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la suppression', 'error');
    }
}

function showPersonnelModal(personnel) {
    const isEdit = personnel !== null;
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 2rem;';
    modal.id = 'personnelModal';
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 12px; max-width: 600px; width: 100%; padding: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2 style="margin: 0;">${isEdit ? '✏️ Modifier le personnel' : '➕ Nouveau personnel'}</h2>
                <button type="button" onclick="closePersonnelModal()" class="btn btn-secondary btn-small">✖ Fermer</button>
            </div>
            <form id="personnelForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Prénom *</label>
                        <input type="text" id="personnel_prenom" value="${personnel?.prenom || ''}" required>
                    </div>
                    <div class="form-group">
                        <label>Nom *</label>
                        <input type="text" id="personnel_nom" value="${personnel?.nom || ''}" required>
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Email</label>
                        <input type="email" id="personnel_email" value="${personnel?.email || ''}">
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Téléphone</label>
                        <input type="tel" id="personnel_telephone" value="${personnel?.telephone || ''}">
                    </div>
                    <div class="form-group" style="grid-column: 1 / -1;">
                        <label>Rôle</label>
                        <input type="text" id="personnel_role" value="${personnel?.role || ''}">
                    </div>
                </div>
                <div class="button-group">
                    <button type="submit" class="btn btn-success">💾 Enregistrer</button>
                    <button type="button" onclick="closePersonnelModal()" class="btn btn-secondary">Annuler</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    document.getElementById('personnelForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await savePersonnel(personnel);
    });
}

function closePersonnelModal() {
    const modal = document.getElementById('personnelModal');
    if (modal) modal.remove();
}

async function savePersonnel(personnel) {
    const data = {
        prenom: document.getElementById('personnel_prenom').value,
        nom: document.getElementById('personnel_nom').value,
        email: document.getElementById('personnel_email').value,
        telephone: document.getElementById('personnel_telephone').value,
        role: document.getElementById('personnel_role').value
    };
    
    try {
        const url = personnel ? `/api/personnels/${personnel.id}` : '/api/personnels';
        const method = personnel ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showAlert('Personnel enregistré!', 'success');
            closePersonnelModal();
            loadPersonnels();
        } else {
            const errorData = await response.json();
            showAlert(`Erreur: ${errorData.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('Erreur lors de la sauvegarde', 'error');
    }
}

async function loadDemoData() {
    if (!confirm('⚠️ Charger les données de démonstration? Cela ajoutera des établissements, chambres, séjours et clients de test.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/load-demo-data', {
            method: 'POST'
        });
        
        if (response.ok) {
            showAlert('✅ Données de démonstration chargées avec succès!', 'success');
            loadEtablissements();
            loadChambres();
        } else {
            const data = await response.json();
            showAlert('❌ Erreur: ' + (data.error || 'Erreur inconnue'), 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('❌ Erreur lors du chargement des données', 'error');
    }
}

function showResetOptions() {
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center; padding: 2rem;';
    modal.id = 'resetOptionsModal';
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 12px; max-width: 600px; width: 100%; padding: 2rem; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2 style="margin: 0;">🗑️ Réinitialisation sélective</h2>
                <button type="button" onclick="closeResetModal()" class="btn btn-secondary btn-small">✖ Fermer</button>
            </div>
            
            <p style="color: #6b7280; margin-bottom: 1.5rem;">Sélectionnez les données à supprimer:</p>
            
            <div style="display: flex; flex-direction: column; gap: 1rem;">
                <label style="display: flex; align-items: center; padding: 1rem; background: #f9fafb; border-radius: 0.5rem; cursor: pointer;">
                    <input type="checkbox" id="reset_sejours" style="margin-right: 0.75rem; width: 18px; height: 18px;">
                    <span><strong>Séjours et clients</strong> - Supprime tous les séjours et leurs clients associés</span>
                </label>
                
                <label style="display: flex; align-items: center; padding: 1rem; background: #f9fafb; border-radius: 0.5rem; cursor: pointer;">
                    <input type="checkbox" id="reset_chambres" style="margin-right: 0.75rem; width: 18px; height: 18px;">
                    <span><strong>Chambres</strong> - Supprime toutes les chambres</span>
                </label>
                
                <label style="display: flex; align-items: center; padding: 1rem; background: #f9fafb; border-radius: 0.5rem; cursor: pointer;">
                    <input type="checkbox" id="reset_etablissements" style="margin-right: 0.75rem; width: 18px; height: 18px;">
                    <span><strong>Établissements</strong> - Supprime tous les établissements (sauf le principal)</span>
                </label>
            </div>
            
            <div class="button-group" style="margin-top: 1.5rem;">
                <button type="button" onclick="executeResetSelection()" class="btn btn-danger">Supprimer la sélection</button>
                <button type="button" onclick="closeResetModal()" class="btn btn-secondary">Annuler</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closeResetModal() {
    const modal = document.getElementById('resetOptionsModal');
    if (modal) {
        modal.remove();
    }
}

async function executeResetSelection() {
    const resetSejours = document.getElementById('reset_sejours').checked;
    const resetChambres = document.getElementById('reset_chambres').checked;
    const resetEtablissements = document.getElementById('reset_etablissements').checked;
    
    if (!resetSejours && !resetChambres && !resetEtablissements) {
        showAlert('⚠️ Veuillez sélectionner au moins une catégorie', 'error');
        return;
    }
    
    const items = [];
    if (resetSejours) items.push('séjours et clients');
    if (resetChambres) items.push('chambres');
    if (resetEtablissements) items.push('établissements');
    
    if (!confirm(`⚠️ Confirmer la suppression de: ${items.join(', ')}? Cette action est irréversible!`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/reset-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                reset_sejours: resetSejours,
                reset_chambres: resetChambres,
                reset_etablissements: resetEtablissements
            })
        });
        
        if (response.ok) {
            showAlert('✅ Données supprimées avec succès!', 'success');
            closeResetModal();
            loadEtablissements();
            loadChambres();
        } else{
            const data = await response.json();
            showAlert('❌ Erreur: ' + (data.error || 'Erreur inconnue'), 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('❌ Erreur lors de la suppression', 'error');
    }
}

async function resetAllData() {
    if (!confirm('⚠️ ATTENTION! Cela supprimera TOUTES les données (établissements, chambres, séjours, clients). L\'utilisateur admin sera conservé. Continuer?')) {
        return;
    }
    
    if (!confirm('⚠️ Dernière confirmation: êtes-vous ABSOLUMENT SÛR? Cette action est IRRÉVERSIBLE!')) {
        return;
    }
    
    try {
        const response = await fetch('/api/reset-all-data', {
            method: 'POST'
        });
        
        if (response.ok) {
            showAlert('✅ Toutes les données ont été réinitialisées!', 'success');
            loadEtablissements();
            loadChambres();
        } else {
            const data = await response.json();
            showAlert('❌ Erreur: ' + (data.error || 'Erreur inconnue'), 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('❌ Erreur lors de la réinitialisation', 'error');
    }
}

async function loadMailConfigs() {
    if (etablissements.length === 0) {
        return;
    }
    
    try {
        const allConfigs = [];
        for (const etab of etablissements) {
            const response = await fetch(`/api/mail-configs?etablissement_id=${etab.id}`);
            const configs = await response.json();
            if (Array.isArray(configs)) {
                allConfigs.push(...configs);
            }
        }
        
        const configs = allConfigs;
        
        const container = document.getElementById('mail-configs-container');
        if (!container) return;
        
        if (configs.length === 0) {
            container.innerHTML = '<p style="color: #9ca3af; text-align: center; padding: 2rem;">Aucune configuration mail. Cliquez sur "Ajouter" pour commencer.</p>';
            return;
        }
        
        container.innerHTML = configs.map(config => `
            <div style="background: white; padding: 1.5rem; border-radius: 0.75rem; border: 2px solid #e5e7eb; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #111827;">
                        ${config.actif ? '✅' : '⭕'} ${config.nom_config}
                    </h3>
                    <div style="display: flex; gap: 0.5rem;">
                        <button onclick="editMailConfig(${config.id})" class="btn btn-primary btn-sm">
                            ✏️ Modifier
                        </button>
                        <button onclick="deleteMailConfig(${config.id})" class="btn btn-danger btn-sm">
                            🗑️ Supprimer
                        </button>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; font-size: 0.875rem;">
                    <div>
                        <strong>Email:</strong> ${config.email_address}
                    </div>
                    <div>
                        <strong>SMTP:</strong> ${config.smtp_host}:${config.smtp_port}
                    </div>
                    ${config.pop_host ? `
                        <div>
                            <strong>POP:</strong> ${config.pop_host}:${config.pop_port}
                        </div>
                    ` : ''}
                    <div>
                        <strong>Statut:</strong> ${config.actif ? '<span style="color: #059669;">Actif</span>' : '<span style="color: #dc2626;">Inactif</span>'}
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erreur chargement configs mail:', error);
        showAlert('❌ Erreur lors du chargement des configurations mail', 'error');
    }
}

function addMailConfig() {
    const modalHTML = `
        <div id="mail-config-modal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
            <div style="background: white; border-radius: 0.75rem; width: 90%; max-width: 700px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 1.5rem; border-bottom: 2px solid #e5e7eb;">
                    <h3 style="margin: 0;">📧 Nouvelle Configuration Mail</h3>
                    <button onclick="closeMailConfigModal()" style="background: none; border: none; font-size: 2rem; cursor: pointer; color: #6b7280;">&times;</button>
                </div>
                <div style="padding: 1.5rem;">
                    <form id="mail-config-form" onsubmit="saveMailConfig(event)">
                        <div class="form-group">
                            <label>Nom de la configuration</label>
                            <input type="text" id="mail-nom-config" class="form-control" required>
                        </div>
                        
                        <div class="form-group">
                            <label>Adresse email</label>
                            <input type="email" id="mail-email-address" class="form-control" required>
                        </div>
                        
                        <div class="form-group">
                            <label>Établissement</label>
                            <select id="mail-etablissement" class="form-control" required>
                                <option value="">Sélectionner...</option>
                                ${etablissements.map(e => `<option value="${e.id}">${e.nom}</option>`).join('')}
                            </select>
                        </div>
                        
                        <h4 style="margin: 1.5rem 0 1rem 0; color: #3b82f6;">Paramètres SMTP (Envoi)</h4>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                            <div class="form-group">
                                <label>Hôte SMTP</label>
                                <input type="text" id="mail-smtp-host" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label>Port SMTP</label>
                                <input type="number" id="mail-smtp-port" class="form-control" value="587" required>
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                            <div class="form-group">
                                <label>Nom d'utilisateur SMTP</label>
                                <input type="text" id="mail-smtp-username" class="form-control" required>
                            </div>
                            <div class="form-group">
                                <label>Mot de passe SMTP</label>
                                <input type="password" id="mail-smtp-password" class="form-control" required>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="mail-smtp-tls" checked>
                                Utiliser TLS
                            </label>
                        </div>
                        
                        <h4 style="margin: 1.5rem 0 1rem 0; color: #22c55e;">Paramètres POP3 (Réception)</h4>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                            <div class="form-group">
                                <label>Hôte POP3</label>
                                <input type="text" id="mail-pop-host" class="form-control">
                            </div>
                            <div class="form-group">
                                <label>Port POP3</label>
                                <input type="number" id="mail-pop-port" class="form-control" value="995">
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                            <div class="form-group">
                                <label>Nom d'utilisateur POP3</label>
                                <input type="text" id="mail-pop-username" class="form-control">
                            </div>
                            <div class="form-group">
                                <label>Mot de passe POP3</label>
                                <input type="password" id="mail-pop-password" class="form-control">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="mail-pop-ssl" checked>
                                Utiliser SSL
                            </label>
                        </div>
                        
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="mail-actif" checked>
                                Configuration active
                            </label>
                        </div>
                        
                        <div style="display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem;">
                            <button type="button" onclick="closeMailConfigModal()" class="btn btn-secondary">
                                Annuler
                            </button>
                            <button type="submit" class="btn btn-success">
                                💾 Enregistrer
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

async function saveMailConfig(event) {
    event.preventDefault();
    
    const formData = {
        nom_config: document.getElementById('mail-nom-config').value,
        email_address: document.getElementById('mail-email-address').value,
        etablissement_id: parseInt(document.getElementById('mail-etablissement').value),
        smtp_host: document.getElementById('mail-smtp-host').value,
        smtp_port: parseInt(document.getElementById('mail-smtp-port').value),
        smtp_username: document.getElementById('mail-smtp-username').value,
        smtp_password: document.getElementById('mail-smtp-password').value,
        smtp_use_tls: document.getElementById('mail-smtp-tls').checked,
        pop_host: document.getElementById('mail-pop-host').value || null,
        pop_port: parseInt(document.getElementById('mail-pop-port').value) || 995,
        pop_username: document.getElementById('mail-pop-username').value || null,
        pop_password: document.getElementById('mail-pop-password').value || null,
        pop_use_ssl: document.getElementById('mail-pop-ssl').checked,
        actif: document.getElementById('mail-actif').checked
    };
    
    try {
        const response = await fetch('/api/mail-configs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showAlert('✅ Configuration mail créée avec succès!', 'success');
            closeMailConfigModal();
            await loadMailConfigs();
        } else {
            const data = await response.json();
            showAlert('❌ Erreur: ' + (data.error || 'Erreur inconnue'), 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('❌ Erreur lors de l\'enregistrement', 'error');
    }
}

async function deleteMailConfig(configId) {
    if (!confirm('Voulez-vous vraiment supprimer cette configuration mail ?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/mail-configs/${configId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showAlert('✅ Configuration supprimée avec succès!', 'success');
            await loadMailConfigs();
        } else {
            const data = await response.json();
            showAlert('❌ Erreur: ' + (data.error || 'Erreur inconnue'), 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showAlert('❌ Erreur lors de la suppression', 'error');
    }
}

function editMailConfig(configId) {
    showAlert('⚠️ Fonctionnalité de modification en cours de développement', 'info');
}

function closeMailConfigModal() {
    const modal = document.getElementById('mail-config-modal');
    if (modal) {
        modal.remove();
    }
}

(async function() {
    console.log('🚀 Initialisation de la page paramètres...');
    try {
        console.log('📁 Chargement des pays...');
        await loadCountries();
        console.log('✅ Pays chargés:', countriesData.length);
        
        console.log('🏢 Chargement des établissements...');
        await loadEtablissements();
        console.log('✅ Établissements chargés:', etablissements.length);
        
        console.log('🏠 Chargement des chambres...');
        await loadChambres();
        console.log('✅ Chambres chargées:', chambres.length);
        
        console.log('👥 Chargement des personnels...');
        await loadPersonnels();
        console.log('✅ Personnels chargés');
        
        console.log('📧 Chargement des configs mail...');
        await loadMailConfigs();
        console.log('✅ Configs mail chargées');
        
        console.log('✨ Initialisation terminée avec succès');
    } catch (error) {
        console.error('❌ Erreur lors du chargement initial:', error);
        showAlert('❌ Erreur lors du chargement de la page: ' + error.message, 'error');
    }
})();

console.log('✅ Script parametres.js chargé - FIN');
console.log('✅ Fonctions définies:', typeof addEtablissement, typeof addChambre, typeof addPersonnel);
