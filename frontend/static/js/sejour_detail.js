// Récupérer l'ID du séjour depuis l'élément de la page
const sejourIdElement = document.getElementById('sejourId');
const sejourId = sejourIdElement ? parseInt(sejourIdElement.value) : null;

let currentSejour = null;
let availableExtras = [];

document.addEventListener('DOMContentLoaded', function() {
    if (sejourId) {
        loadSejourDetails();
        loadAvailableExtras();
    }
});

async function loadSejourDetails() {
    try {
        const response = await fetch(`/api/sejours/${sejourId}`);
        const data = await response.json();
        currentSejour = data;
        
        displaySejourInfo(data.sejour);
        displayEtablissementInfo(data.etablissement);
        displayChambres(data.chambres);
        displayPersonnes(data.personnes);
        displayExtras(data.extras);
        displayFinancialSummary(data.sejour, data.extras);
    } catch (error) {
        console.error('Erreur lors du chargement du séjour:', error);
    }
}

function displaySejourInfo(sejour) {
    const statutBadge = document.getElementById('sejourStatutBadge');
    const badgeClass = sejour.statut === 'active' ? 'badge-active' : 
                       sejour.statut === 'terminee' ? 'badge-termine' : 'badge-annule';
    const statutText = sejour.statut === 'active' ? 'Actif' : 
                      sejour.statut === 'terminee' ? 'Terminé' : 'Annulé';
    statutBadge.innerHTML = `<span class="badge-sejour ${badgeClass}">${statutText}</span>`;
    
    const html = `
        <div class="info-grid">
            <div class="info-item">
                <label>Numéro de séjour</label>
                <div class="value">${sejour.numero_reservation}</div>
            </div>
            <div class="info-item">
                <label>Date d'arrivée</label>
                <div class="value">${formatDate(sejour.date_arrivee)}</div>
            </div>
            <div class="info-item">
                <label>Date de départ</label>
                <div class="value">${formatDate(sejour.date_depart)}</div>
            </div>
            <div class="info-item">
                <label>Nombre de jours</label>
                <div class="value">${sejour.nombre_jours || 'N/A'}</div>
            </div>
            ${sejour.observations ? `
            <div class="info-item" style="grid-column: 1 / -1;">
                <label>Observations</label>
                <div class="value">${sejour.observations}</div>
            </div>
            ` : ''}
        </div>
    `;
    
    document.getElementById('sejourInfo').innerHTML = html;
}

function displayEtablissementInfo(etablissement) {
    if (!etablissement) {
        document.getElementById('etablissementInfo').innerHTML = '<p>Aucune information</p>';
        return;
    }
    
    const html = `
        <div class="info-grid">
            <div class="info-item">
                <label>Nom</label>
                <div class="value">${etablissement.nom_etablissement}</div>
            </div>
            <div class="info-item">
                <label>Ville</label>
                <div class="value">${etablissement.ville || 'N/A'}</div>
            </div>
            <div class="info-item">
                <label>Téléphone</label>
                <div class="value">${etablissement.telephone || 'N/A'}</div>
            </div>
            <div class="info-item">
                <label>Email</label>
                <div class="value">${etablissement.email || 'N/A'}</div>
            </div>
        </div>
    `;
    
    document.getElementById('etablissementInfo').innerHTML = html;
}

function displayChambres(chambres) {
    if (!chambres || chambres.length === 0) {
        document.getElementById('chambresInfo').innerHTML = '<p>Aucune chambre assignée</p>';
        return;
    }
    
    const html = `
        <div class="chambres-list">
            ${chambres.map(chambre => `
                <div class="chambre-card">
                    <h4>${chambre.nom}</h4>
                    <p><strong>Capacité:</strong> ${chambre.capacite} personne(s)</p>
                    ${chambre.description ? `<p>${chambre.description}</p>` : ''}
                </div>
            `).join('')}
        </div>
    `;
    
    document.getElementById('chambresInfo').innerHTML = html;
}

function displayPersonnes(personnes) {
    if (!personnes || personnes.length === 0) {
        document.getElementById('personnesInfo').innerHTML = '<p>Aucune personne enregistrée</p>';
        return;
    }
    
    const html = `
        <div class="personnes-list">
            ${personnes.map(personne => `
                <div class="personne-card ${personne.est_contact_principal ? 'border-primary' : ''}">
                    <h4>${personne.prenom} ${personne.nom} ${personne.est_contact_principal ? '⭐ (Contact principal)' : ''}</h4>
                    <p><strong>Email:</strong> ${personne.email || 'N/A'}</p>
                    <p><strong>Téléphone:</strong> ${personne.telephone || 'N/A'}</p>
                    <p><strong>Pays:</strong> ${personne.pays || 'N/A'}</p>
                    ${personne.chambre_nom ? `<p><strong>Chambre:</strong> ${personne.chambre_nom}</p>` : ''}
                </div>
            `).join('')}
        </div>
    `;
    
    document.getElementById('personnesInfo').innerHTML = html;
}

function displayExtras(extras) {
    if (!extras || extras.length === 0) {
        document.getElementById('extrasInfo').innerHTML = '<p style="text-align: center; color: #666;">Aucun extra facturé</p>';
        return;
    }
    
    const html = `
        <div>
            ${extras.map(extra => `
                <div class="extra-item">
                    <div>
                        <strong>${extra.nom}</strong> <small>(${extra.unite_mesure})</small>
                        <br><small>Quantité: ${extra.quantite} × ${parseFloat(extra.prix_unitaire).toFixed(2)} MAD</small>
                    </div>
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <strong>${parseFloat(extra.montant_total).toFixed(2)} MAD</strong>
                        <button class="btn-icon no-print" onclick="removeExtra(${extra.sejour_extra_id})" title="Retirer">
                            🗑️
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    document.getElementById('extrasInfo').innerHTML = html;
}

function displayFinancialSummary(sejour, extras) {
    const hebergement = parseFloat(sejour.facture_hebergement || 0);
    const plateforme = parseFloat(sejour.charge_plateforme || 0);
    const taxe = parseFloat(sejour.taxe_sejour || 0);
    const totalExtras = extras ? extras.reduce((sum, e) => sum + parseFloat(e.montant_total || 0), 0) : 0;
    const total = hebergement + plateforme + taxe + totalExtras;
    
    const html = `
        <div class="financial-summary">
            <div class="financial-row">
                <span>Facture d'hébergement:</span>
                <span>${hebergement.toFixed(2)} MAD</span>
            </div>
            <div class="financial-row">
                <span>Charges plateforme:</span>
                <span>${plateforme.toFixed(2)} MAD</span>
            </div>
            <div class="financial-row">
                <span>Taxe de séjour:</span>
                <span>${taxe.toFixed(2)} MAD</span>
            </div>
            <div class="financial-row">
                <span>Extras:</span>
                <span>${totalExtras.toFixed(2)} MAD</span>
            </div>
            <div class="financial-row total">
                <span>Total:</span>
                <span>${total.toFixed(2)} MAD</span>
            </div>
        </div>
    `;
    
    document.getElementById('financialSummary').innerHTML = html;
}

async function loadAvailableExtras() {
    try {
        const response = await fetch('/api/extras?actif_only=true');
        availableExtras = await response.json();
        
        const select = document.getElementById('selectExtra');
        if (select) {
            select.innerHTML = '<option value="">Sélectionner un extra</option>';
            availableExtras.forEach(extra => {
                const option = new Option(
                    `${extra.nom} - ${parseFloat(extra.prix_unitaire).toFixed(2)} MAD (${extra.unite_mesure})`,
                    extra.id
                );
                select.add(option);
            });
        }
    } catch (error) {
        console.error('Erreur lors du chargement des extras:', error);
    }
}

function showAddExtraModal() {
    const form = document.getElementById('addExtraForm');
    if (form) form.reset();
    
    const preview = document.getElementById('extraPreview');
    if (preview) preview.style.display = 'none';
    
    const modal = document.getElementById('addExtraModal');
    if (modal) modal.classList.add('active');
}

function closeAddExtraModal() {
    const modal = document.getElementById('addExtraModal');
    if (modal) modal.classList.remove('active');
}

function updateExtraPreview() {
    const selectExtra = document.getElementById('selectExtra');
    const quantiteInput = document.getElementById('extraQuantite');
    const preview = document.getElementById('extraPreview');
    
    if (!selectExtra || !quantiteInput || !preview) return;
    
    const extraId = selectExtra.value;
    const quantite = parseInt(quantiteInput.value) || 1;
    
    if (!extraId) {
        preview.style.display = 'none';
        return;
    }
    
    const extra = availableExtras.find(e => e.id == extraId);
    if (extra) {
        const prix = parseFloat(extra.prix_unitaire);
        const total = prix * quantite;
        
        document.getElementById('previewPrixUnitaire').textContent = `${prix.toFixed(2)} MAD`;
        document.getElementById('previewMontantTotal').textContent = `${total.toFixed(2)} MAD`;
        preview.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const selectExtra = document.getElementById('selectExtra');
    const quantiteInput = document.getElementById('extraQuantite');
    
    if (selectExtra) selectExtra.addEventListener('change', updateExtraPreview);
    if (quantiteInput) quantiteInput.addEventListener('input', updateExtraPreview);
    
    const addExtraForm = document.getElementById('addExtraForm');
    if (addExtraForm) {
        addExtraForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const selectExtra = document.getElementById('selectExtra');
            const quantiteInput = document.getElementById('extraQuantite');
            
            const data = {
                extra_id: parseInt(selectExtra.value),
                quantite: parseInt(quantiteInput.value)
            };
            
            try {
                const response = await fetch(`/api/sejours/${sejourId}/extras`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Extra ajouté avec succès');
                    closeAddExtraModal();
                    loadSejourDetails();
                } else {
                    alert('Erreur lors de l\'ajout de l\'extra');
                }
            } catch (error) {
                console.error('Erreur:', error);
                alert('Erreur lors de l\'ajout de l\'extra');
            }
        });
    }
});

async function removeExtra(sejourExtraId) {
    if (!confirm('Êtes-vous sûr de vouloir retirer cet extra ?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/sejours/extras/${sejourExtraId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Extra retiré avec succès');
            loadSejourDetails();
        } else {
            alert('Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression');
    }
}

function printSejourDetail() {
    window.print();
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}
