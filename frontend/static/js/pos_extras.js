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
        currentSejour = await response.json();
        
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
    
    infoCard.style.display = 'block';
    infoContent.innerHTML = `
        <div style="margin-bottom: 0.5rem;"><strong>N° Séjour:</strong> ${currentSejour.numero_reservation || 'N/A'}</div>
        <div style="margin-bottom: 0.5rem;"><strong>Client:</strong> ${currentSejour.contact_prenom || ''} ${currentSejour.contact_nom || 'N/A'}</div>
        <div style="margin-bottom: 0.5rem;"><strong>Établissement:</strong> ${currentSejour.nom_etablissement || 'N/A'}</div>
        <div style="margin-bottom: 0.5rem;"><strong>Dates:</strong> ${formatDate(currentSejour.date_arrivee)} → ${formatDate(currentSejour.date_depart)}</div>
        <div><strong>Hébergement:</strong> ${parseFloat(currentSejour.facture_hebergement || 0).toFixed(2)} MAD</div>
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
    
    const extra = currentExtras.find(e => e.id === extraId);
    if (!extra) return;
    
    const existingItem = cart.find(item => item.extra_id === extraId);
    
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
            montant_total: parseFloat(extra.prix_unitaire)
        });
    }
    
    updateCartDisplay();
}

function updateCartDisplay() {
    const container = document.getElementById('cartItems');
    const btnSave = document.getElementById('btnSaveCart');
    const btnInvoice = document.getElementById('btnGenerateInvoice');
    
    if (cart.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">Le panier est vide</p>';
        btnSave.disabled = true;
        btnInvoice.disabled = true;
        document.getElementById('subtotal').textContent = '0.00 MAD';
        document.getElementById('totalAmount').textContent = '0.00 MAD';
        return;
    }
    
    container.innerHTML = cart.map((item, index) => `
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-name">${item.nom}</div>
                <div class="cart-item-price">${item.prix_unitaire.toFixed(2)} MAD / ${item.unite_mesure}</div>
            </div>
            <div class="cart-item-controls">
                <button class="qty-btn" onclick="updateQuantity(${index}, -1)">-</button>
                <div class="qty-display">${item.quantite}</div>
                <button class="qty-btn" onclick="updateQuantity(${index}, 1)">+</button>
                <button class="btn-remove" onclick="removeFromCart(${index})">✕</button>
            </div>
        </div>
        <div style="text-align: right; padding: 0.25rem 0.75rem; color: #6b7280; font-size: 0.875rem;">
            Sous-total: ${item.montant_total.toFixed(2)} MAD
        </div>
    `).join('');
    
    const total = cart.reduce((sum, item) => sum + item.montant_total, 0);
    document.getElementById('subtotal').textContent = total.toFixed(2) + ' MAD';
    document.getElementById('totalAmount').textContent = total.toFixed(2) + ' MAD';
    
    btnSave.disabled = false;
    btnInvoice.disabled = false;
}

function updateQuantity(index, delta) {
    if (index < 0 || index >= cart.length) return;
    
    cart[index].quantite += delta;
    
    if (cart[index].quantite <= 0) {
        cart.splice(index, 1);
    } else {
        cart[index].montant_total = cart[index].quantite * cart[index].prix_unitaire;
    }
    
    updateCartDisplay();
}

function removeFromCart(index) {
    if (index >= 0 && index < cart.length) {
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
    
    if (!confirm(`Enregistrer ${cart.length} consommation(s) pour le séjour ${currentSejour.numero_reservation}?`)) {
        return;
    }
    
    try {
        for (const item of cart) {
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
        
        alert('✓ Consommations enregistrées avec succès!');
        cart = [];
        updateCartDisplay();
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
        
        console.log('Consommations existantes:', existingExtras);
    } catch (error) {
        console.error('Erreur chargement consommations:', error);
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
