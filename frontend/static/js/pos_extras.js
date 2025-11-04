let currentSejour = null;
let currentExtras = [];
let cart = [];
let allSejours = [];
let etablissements = [];

document.addEventListener('DOMContentLoaded', function() {
    loadEtablissements();
    loadSejoursPOS();
});

async function loadEtablissements() {
    try {
        const response = await fetch('/api/etablissements?actif_only=true');
        etablissements = await response.json();
        
        const filterSelect = document.getElementById('filterEtablissementPOS');
        filterSelect.innerHTML = '<option value="">Tous les établissements</option>';
        
        etablissements.forEach(etab => {
            const option = new Option(etab.nom_etablissement, etab.id);
            filterSelect.add(option);
        });
    } catch (error) {
        console.error('Erreur chargement établissements:', error);
    }
}

async function loadSejoursPOS() {
    try {
        const response = await fetch('/api/sejours');
        const data = await response.json();
        allSejours = data.filter(s => s.statut === 'active');
        displaySejoursList(allSejours);
    } catch (error) {
        console.error('Erreur chargement séjours:', error);
    }
}

function displaySejoursList(sejours) {
    const container = document.getElementById('sejoursListPOS');
    
    if (sejours.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 1rem;">Aucun séjour actif trouvé</p>';
        return;
    }
    
    container.innerHTML = sejours.map(sejour => `
        <div class="sejour-item ${currentSejour && currentSejour.id === sejour.id ? 'selected' : ''}" 
             onclick="selectSejour(${sejour.id})">
            <div><strong>${sejour.numero_reservation || 'N/A'}</strong></div>
            <div style="font-size: 0.875rem; color: #6b7280;">
                ${sejour.contact_prenom || ''} ${sejour.contact_nom || 'N/A'}<br>
                ${sejour.nom_etablissement || 'N/A'}
            </div>
        </div>
    `).join('');
}

async function selectSejour(sejourId) {
    try {
        const response = await fetch(`/api/sejours/${sejourId}`);
        const data = await response.json();
        
        // La réponse a la structure {sejour: {...}, personnes: [...], chambres: [...]}
        // On extrait le séjour tout en gardant l'accès aux autres données
        if (data.sejour) {
            currentSejour = data.sejour;
            // Attacher aussi les autres données pour compatibilité avec d'autres parties de l'UI
            // IMPORTANT: Utiliser les noms standards sans underscore pour la compatibilité
            currentSejour.personnes = data.personnes || [];
            currentSejour.chambres = data.chambres || [];
        } else {
            // Fallback si la structure est différente
            currentSejour = data;
        }
        
        document.querySelectorAll('.sejour-item').forEach(item => {
            item.classList.remove('selected');
        });
        event.target.closest('.sejour-item').classList.add('selected');
        
        displaySejourInfo();
        loadExtrasPOS();
        loadExistingConsommations();
    } catch (error) {
        console.error('Erreur sélection séjour:', error);
        alert('Erreur lors de la sélection du séjour');
    }
}

function displaySejourInfo() {
    if (!currentSejour) return;
    
    const infoCard = document.getElementById('sejourInfoCard');
    const infoContent = document.getElementById('sejourInfo');
    
    const isClosed = currentSejour.statut === 'closed' || currentSejour.closed_at;
    const statusBadge = isClosed 
        ? '<span style="background: #ef4444; color: white; padding: 0.25rem 0.75rem; border-radius: 0.5rem; font-size: 0.875rem; margin-left: 0.5rem;">🔒 Clôturé</span>'
        : '<span style="background: #10b981; color: white; padding: 0.25rem 0.75rem; border-radius: 0.5rem; font-size: 0.875rem; margin-left: 0.5rem;">✓ Actif</span>';
    
    infoCard.style.display = 'block';
    infoContent.innerHTML = `
        <div style="margin-bottom: 0.75rem;"><strong>N° Séjour:</strong> ${currentSejour.numero_reservation || 'N/A'} ${statusBadge}</div>
        <div style="margin-bottom: 0.5rem;"><strong>Client:</strong> ${currentSejour.contact_prenom || ''} ${currentSejour.contact_nom || 'N/A'}</div>
        <div style="margin-bottom: 0.5rem;"><strong>Établissement:</strong> ${currentSejour.nom_etablissement || 'N/A'}</div>
        <div style="margin-bottom: 0.5rem;"><strong>Dates:</strong> ${formatDate(currentSejour.date_arrivee)} → ${formatDate(currentSejour.date_depart)}</div>
        <div><strong>Hébergement:</strong> ${parseFloat(currentSejour.facture_hebergement || 0).toFixed(2)} MAD</div>
        ${isClosed ? `<div style="margin-top: 0.75rem; padding: 0.5rem; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 0.5rem; font-size: 0.875rem; color: #991b1b;">Ce séjour est clôturé. Les modifications ne sont plus possibles.</div>` : ''}
    `;
}

async function loadExtrasPOS() {
    if (!currentSejour) {
        document.getElementById('extrasListPOS').innerHTML = 
            '<p style="text-align: center; color: #666;">Sélectionnez un séjour</p>';
        return;
    }
    
    const etablissementId = document.getElementById('filterEtablissementPOS').value || 
                            currentSejour.etablissement_id;
    
    try {
        const url = `/api/extras?etablissement_id=${etablissementId}&actif_only=true`;
        const response = await fetch(url);
        currentExtras = await response.json();
        displayExtrasGrid(currentExtras);
    } catch (error) {
        console.error('Erreur chargement extras:', error);
    }
}

function displayExtrasGrid(extras) {
    const container = document.getElementById('extrasListPOS');
    
    if (extras.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">Aucun extra disponible</p>';
        return;
    }
    
    container.innerHTML = extras.map(extra => `
        <div class="extra-card" onclick="addToCart(${extra.id})">
            <h4>${extra.nom}</h4>
            <div class="price">${parseFloat(extra.prix_unitaire).toFixed(2)} MAD</div>
            <div class="unit">${extra.unite_mesure}</div>
            ${extra.description ? `<div style="font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;">${extra.description}</div>` : ''}
        </div>
    `).join('');
}

function addToCart(extraId) {
    if (!currentSejour) {
        alert('Veuillez d\'abord sélectionner un séjour');
        return;
    }
    
    // Vérifier si le séjour est clôturé
    if (currentSejour.statut === 'closed' || currentSejour.closed_at) {
        alert('Ce séjour est clôturé. Impossible d\'ajouter des extras.');
        return;
    }
    
    const extra = currentExtras.find(e => e.id === extraId);
    if (!extra) return;
    
    const existingItem = cart.find(item => item.extra_id === extraId && !item.is_saved);
    
    if (existingItem) {
        existingItem.quantite++;
        existingItem.montant_total = existingItem.quantite * existingItem.prix_unitaire;
    } else {
        cart.push({
            extra_id: extraId,
            nom: extra.nom,
            prix_unitaire: parseFloat(extra.prix_unitaire),
            unite_mesure: extra.unite_mesure,
            quantite: 1,
            montant_total: parseFloat(extra.prix_unitaire),
            is_saved: false
        });
    }
    
    updateCartDisplay();
}

function updateCartDisplay() {
    const container = document.getElementById('cartItems');
    const btnSave = document.getElementById('btnSaveCart');
    const btnClose = document.getElementById('btnCloseSejour');
    const btnInvoice = document.getElementById('btnGenerateInvoice');
    
    const isClosed = currentSejour && (currentSejour.statut === 'closed' || currentSejour.closed_at);
    
    if (cart.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">Le panier est vide</p>';
        btnSave.disabled = true;
        btnClose.disabled = true;
        btnInvoice.disabled = true;
        document.getElementById('subtotal').textContent = '0.00 MAD';
        document.getElementById('totalAmount').textContent = '0.00 MAD';
        return;
    }
    
    container.innerHTML = cart.map((item, index) => {
        const statusBadge = item.is_saved 
            ? '<span style="background: #10b981; color: white; padding: 0.15rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; margin-left: 0.5rem;">✓ Enregistré</span>'
            : '<span style="background: #f59e0b; color: white; padding: 0.15rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; margin-left: 0.5rem;">Nouveau</span>';
        
        // Désactiver les boutons si le séjour est clôturé
        const buttonsDisabled = isClosed ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : '';
        
        return `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.nom} ${statusBadge}</div>
                    <div class="cart-item-price">${item.prix_unitaire.toFixed(2)} MAD / ${item.unite_mesure}</div>
                </div>
                <div class="cart-item-controls">
                    <button class="qty-btn" onclick="updateQuantity(${index}, -1)" ${buttonsDisabled}>-</button>
                    <div class="qty-display">${item.quantite}</div>
                    <button class="qty-btn" onclick="updateQuantity(${index}, 1)" ${buttonsDisabled}>+</button>
                    <button class="btn-remove" onclick="removeFromCart(${index})" ${buttonsDisabled}>✕</button>
                </div>
            </div>
            <div style="text-align: right; padding: 0.25rem 0.75rem; color: #6b7280; font-size: 0.875rem;">
                Sous-total: ${item.montant_total.toFixed(2)} MAD
            </div>
        `;
    }).join('');
    
    const total = cart.reduce((sum, item) => sum + item.montant_total, 0);
    document.getElementById('subtotal').textContent = total.toFixed(2) + ' MAD';
    document.getElementById('totalAmount').textContent = total.toFixed(2) + ' MAD';
    
    // Vérifier s'il y a des items non enregistrés
    const hasUnsavedItems = cart.some(item => !item.is_saved);
    btnSave.disabled = !hasUnsavedItems || isClosed;
    
    btnClose.disabled = hasUnsavedItems || cart.length === 0 || isClosed;
    btnInvoice.disabled = !isClosed;
}

async function updateQuantity(index, delta) {
    if (index < 0 || index >= cart.length) return;
    
    const item = cart[index];
    item.quantite += delta;
    
    if (item.quantite <= 0) {
        // Si c'est un item enregistré, on le supprime du serveur
        if (item.is_saved && item.sejour_extra_id) {
            if (confirm('Supprimer cette consommation?')) {
                try {
                    const response = await fetch(`/api/sejours/extras/${item.sejour_extra_id}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        cart.splice(index, 1);
                    } else {
                        alert('Erreur lors de la suppression');
                        item.quantite -= delta; // Annuler le changement
                    }
                } catch (error) {
                    console.error('Erreur:', error);
                    alert('Erreur lors de la suppression');
                    item.quantite -= delta; // Annuler le changement
                }
            } else {
                item.quantite -= delta; // Annuler le changement
            }
        } else {
            cart.splice(index, 1);
        }
    } else {
        item.montant_total = item.quantite * item.prix_unitaire;
        if (item.is_saved) {
            item.quantite_changed = true;
        }
    }
    
    updateCartDisplay();
}

async function removeFromCart(index) {
    if (index < 0 || index >= cart.length) return;
    
    const item = cart[index];
    
    // Si c'est un item enregistré, on le supprime du serveur
    if (item.is_saved && item.sejour_extra_id) {
        if (!confirm('Supprimer cette consommation?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/sejours/extras/${item.sejour_extra_id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                cart.splice(index, 1);
                updateCartDisplay();
            } else {
                alert('Erreur lors de la suppression');
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur lors de la suppression');
        }
    } else {
        cart.splice(index, 1);
        updateCartDisplay();
    }
}

function clearCart() {
    if (cart.length === 0) return;
    
    if (confirm('Vider le panier?')) {
        cart = [];
        updateCartDisplay();
    }
}

async function saveConsommations() {
    if (!currentSejour || cart.length === 0) {
        alert('Aucune consommation à enregistrer');
        return;
    }
    
    const unsavedItems = cart.filter(item => !item.is_saved);
    const savedItems = cart.filter(item => item.is_saved);
    
    if (unsavedItems.length === 0 && savedItems.length > 0) {
        alert('Toutes les consommations sont déjà enregistrées');
        return;
    }
    
    if (!confirm(`Enregistrer ${unsavedItems.length} nouvelle(s) consommation(s)?`)) {
        return;
    }
    
    try {
        // Enregistrer les nouveaux items
        for (const item of unsavedItems) {
            const response = await fetch(`/api/sejours/${currentSejour.id}/extras`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    extra_id: item.extra_id,
                    quantite: item.quantite
                })
            });
            
            if (!response.ok) {
                throw new Error('Erreur lors de l\'enregistrement');
            }
        }
        
        // Mettre à jour les items existants qui ont changé
        for (const item of savedItems) {
            if (item.quantite_changed) {
                const response = await fetch(`/api/sejours/extras/${item.sejour_extra_id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        quantite: item.quantite
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Erreur lors de la mise à jour');
                }
            }
        }
        
        alert('✓ Consommations enregistrées avec succès!');
        loadExistingConsommations();
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'enregistrement des consommations');
    }
}

async function loadExistingConsommations() {
    if (!currentSejour) return;
    
    try {
        const response = await fetch(`/api/sejours/${currentSejour.id}/extras`);
        const existingExtras = await response.json();
        
        // Charger les consommations existantes dans le panier
        cart = existingExtras.map(extra => ({
            sejour_extra_id: extra.sejour_extra_id,
            extra_id: extra.id,
            nom: extra.nom,
            prix_unitaire: parseFloat(extra.prix_unitaire),
            unite_mesure: extra.unite_mesure,
            quantite: parseFloat(extra.quantite),
            montant_total: parseFloat(extra.montant_total),
            is_saved: true  // Marquer comme déjà enregistré
        }));
        
        updateCartDisplay();
        console.log('Consommations existantes chargées:', existingExtras.length);
    } catch (error) {
        console.error('Erreur chargement consommations:', error);
    }
}

async function closeSejour() {
    if (!currentSejour) {
        alert('Veuillez sélectionner un séjour');
        return;
    }
    
    if (!confirm(`Clôturer le séjour ${currentSejour.numero_reservation}?\n\nAprès clôture, vous ne pourrez plus modifier les consommations.`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/sejours/${currentSejour.id}/close`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            alert('✓ ' + data.message);
            // Recharger le séjour pour mettre à jour le statut
            currentSejour.statut = 'closed';
            currentSejour.closed_at = new Date().toISOString();
            displaySejourInfo();
            updateCartDisplay();
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de clôturer le séjour'));
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la clôture du séjour');
    }
}

async function generateInvoice() {
    if (!currentSejour) {
        alert('Veuillez sélectionner un séjour');
        return;
    }
    
    try {
        const response = await fetch(`/api/sejours/${currentSejour.id}/facture`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `facture_${currentSejour.numero_reservation}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            alert('✓ Facture générée avec succès!');
        } else {
            alert('Erreur lors de la génération de la facture');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la génération de la facture');
    }
}

function searchSejours() {
    const searchTerm = document.getElementById('sejourSearch').value.toLowerCase();
    
    if (!searchTerm) {
        displaySejoursList(allSejours);
        return;
    }
    
    const filtered = allSejours.filter(sejour => 
        (sejour.numero_reservation && sejour.numero_reservation.toLowerCase().includes(searchTerm)) ||
        (sejour.contact_nom && sejour.contact_nom.toLowerCase().includes(searchTerm)) ||
        (sejour.contact_prenom && sejour.contact_prenom.toLowerCase().includes(searchTerm))
    );
    
    displaySejoursList(filtered);
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR');
}
