let currentConfigId = null;
let currentFolder = 'inbox';
let currentEmailId = null;
let allEmails = [];
let currentEtablissementId = null;
let etablissements = [];

document.addEventListener('DOMContentLoaded', async () => {
    await loadEtablissements();
    
    document.getElementById('index-client-checkbox').addEventListener('change', (e) => {
        document.getElementById('client-email-index').style.display = e.target.checked ? 'block' : 'none';
    });
    
    document.getElementById('search-emails').addEventListener('input', (e) => {
        filterEmails(e.target.value);
    });
});

async function loadEtablissements() {
    try {
        const response = await fetch('/api/etablissements?actif_only=true');
        etablissements = await response.json();
        
        if (etablissements.length > 0) {
            currentEtablissementId = etablissements[0].id;
            await loadMailConfigs();
        }
    } catch (error) {
        showAlert('Erreur lors du chargement des établissements', 'danger');
        console.error(error);
    }
}

async function loadMailConfigs() {
    if (!currentEtablissementId) {
        return;
    }
    
    try {
        const response = await fetch(`/api/mail-configs?etablissement_id=${currentEtablissementId}`);
        const configs = await response.json();
        
        const select = document.getElementById('mail-config-select');
        select.innerHTML = '<option value="">Choisir un compte...</option>';
        
        configs.forEach(config => {
            const option = document.createElement('option');
            option.value = config.id;
            option.textContent = `${config.nom_config} (${config.email_address})`;
            if (config.actif) {
                option.selected = true;
            }
            select.appendChild(option);
        });
        
        if (configs.length > 0 && configs[0].actif) {
            currentConfigId = configs[0].id;
            loadFolders();
        }
    } catch (error) {
        showAlert('Erreur lors du chargement des configurations mail', 'danger');
        console.error(error);
    }
}

function loadFolders() {
    const select = document.getElementById('mail-config-select');
    currentConfigId = select.value ? parseInt(select.value) : null;
    
    if (currentConfigId) {
        selectFolder('inbox');
    }
}

async function selectFolder(folder) {
    currentFolder = folder;
    
    document.querySelectorAll('.folder-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-folder="${folder}"]`).classList.add('active');
    
    const folderTitles = {
        'inbox': '📥 Boîte de réception',
        'sent': '📤 Envoyés',
        'draft': '📝 Brouillons',
        'trash': '🗑️ Corbeille'
    };
    
    document.getElementById('folder-title').textContent = folderTitles[folder];
    
    await loadEmails();
}

async function loadEmails() {
    if (!currentConfigId) {
        document.getElementById('emails-list-container').innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #9ca3af;">
                <p style="font-size: 1.125rem;">Sélectionnez un compte mail pour commencer</p>
            </div>
        `;
        return;
    }
    
    try:
        const response = await fetch(`/api/mail/emails/${currentConfigId}?folder=${currentFolder}&limit=100&etablissement_id=${currentEtablissementId}`);
        allEmails = await response.json();
        
        displayEmails(allEmails);
        updateUnreadCounts();
    } catch (error) {
        showAlert('Erreur lors du chargement des emails', 'danger');
        console.error(error);
    }
}

function displayEmails(emails) {
    const container = document.getElementById('emails-list-container');
    
    if (emails.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 3rem; color: #9ca3af;">
                <p style="font-size: 1.125rem;">Aucun email dans ce dossier</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = emails.map(email => `
        <div class="email-item ${!email.is_read ? 'unread' : ''}" onclick="openEmail(${email.id})">
            <div class="email-item-header">
                <div class="email-item-subject">${escapeHtml(email.subject || '(Sans objet)')}</div>
                <div class="email-item-date">${formatDate(email.date_sent || email.date_received)}</div>
            </div>
            <div class="email-item-from">
                ${currentFolder === 'sent' ? 'À: ' + escapeHtml(email.to_email || '') : 'De: ' + escapeHtml(email.from_email || '')}
            </div>
            <div class="email-item-preview">
                ${escapeHtml((email.body_text || email.body_html || '').substring(0, 100))}...
            </div>
        </div>
    `).join('');
}

function filterEmails(searchTerm) {
    const term = searchTerm.toLowerCase();
    const filtered = allEmails.filter(email => 
        (email.subject || '').toLowerCase().includes(term) ||
        (email.from_email || '').toLowerCase().includes(term) ||
        (email.to_email || '').toLowerCase().includes(term) ||
        (email.body_text || '').toLowerCase().includes(term)
    );
    displayEmails(filtered);
}

async function openEmail(emailId) {
    try {
        const response = await fetch(`/api/mail/email/${emailId}?etablissement_id=${currentEtablissementId}`);
        const email = await response.json();
        
        currentEmailId = emailId;
        
        document.getElementById('email-detail-subject').textContent = email.subject || '(Sans objet)';
        document.getElementById('email-detail-from').textContent = email.from_email || '';
        document.getElementById('email-detail-to').textContent = email.to_email || '';
        document.getElementById('email-detail-date').textContent = formatDate(email.date_sent || email.date_received);
        
        const bodyContainer = document.getElementById('email-detail-body');
        if (email.body_html) {
            bodyContainer.innerHTML = email.body_html;
        } else {
            bodyContainer.textContent = email.body_text || '';
        }
        
        document.getElementById('email-detail-modal').classList.add('active');
        
        await loadEmails();
    } catch (error) {
        showAlert('Erreur lors de l\'ouverture de l\'email', 'danger');
        console.error(error);
    }
}

function closeEmailDetailModal() {
    document.getElementById('email-detail-modal').classList.remove('active');
    currentEmailId = null;
}

function composeNewEmail() {
    if (!currentConfigId) {
        showAlert('Veuillez sélectionner un compte mail', 'warning');
        return;
    }
    
    document.getElementById('compose-form').reset();
    document.getElementById('client-email-index').style.display = 'none';
    document.getElementById('compose-modal').classList.add('active');
}

function closeComposeModal() {
    document.getElementById('compose-modal').classList.remove('active');
}

async function sendEmail(event) {
    event.preventDefault();
    
    if (!currentConfigId) {
        showAlert('Veuillez sélectionner un compte mail', 'warning');
        return;
    }
    
    const formData = {
        config_id: currentConfigId,
        etablissement_id: currentEtablissementId,
        to_email: document.getElementById('to-email').value,
        cc_email: document.getElementById('cc-email').value || null,
        bcc_email: document.getElementById('bcc-email').value || null,
        subject: document.getElementById('subject').value,
        body_html: formatEmailBody(document.getElementById('email-body').value)
    };
    
    if (document.getElementById('index-client-checkbox').checked) {
        formData.client_email_indexed = document.getElementById('client-email-index').value;
    }
    
    try {
        const response = await fetch('/api/mail/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('Email envoyé avec succès', 'success');
            closeComposeModal();
            await loadEmails();
        } else {
            showAlert(result.error || 'Erreur lors de l\'envoi', 'danger');
        }
    } catch (error) {
        showAlert('Erreur lors de l\'envoi de l\'email', 'danger');
        console.error(error);
    }
}

async function fetchNewEmails() {
    if (!currentConfigId) {
        showAlert('Veuillez sélectionner un compte mail', 'warning');
        return;
    }
    
    try {
        showAlert('Récupération des emails en cours...', 'info');
        
        const response = await fetch(`/api/mail/fetch/${currentConfigId}?etablissement_id=${currentEtablissementId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(result.message, 'success');
            await loadEmails();
        } else {
            showAlert(result.error || 'Erreur lors de la récupération', 'danger');
        }
    } catch (error) {
        showAlert('Erreur lors de la récupération des emails', 'danger');
        console.error(error);
    }
}

async function replyToEmail() {
    if (!currentEmailId) return;
    
    try {
        const response = await fetch(`/api/mail/email/${currentEmailId}`);
        const email = await response.json();
        
        closeEmailDetailModal();
        
        document.getElementById('to-email').value = email.from_email || '';
        document.getElementById('subject').value = 'Re: ' + (email.subject || '');
        
        const originalBody = email.body_text || email.body_html || '';
        const replyBody = `\n\n--- Message original ---\nDe: ${email.from_email}\nDate: ${formatDate(email.date_sent || email.date_received)}\n\n${originalBody}`;
        
        document.getElementById('email-body').value = replyBody;
        
        document.getElementById('compose-modal').style.display = 'flex';
    } catch (error) {
        showAlert('Erreur lors de la préparation de la réponse', 'danger');
        console.error(error);
    }
}

async function moveEmailToTrash() {
    if (!currentEmailId) return;
    
    if (!confirm('Voulez-vous vraiment déplacer cet email vers la corbeille ?')) {
        return;
    }
    
    try:
        const response = await fetch(`/api/mail/email/${currentEmailId}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                folder: 'trash',
                etablissement_id: currentEtablissementId
            })
        });
        
        if (response.ok) {
            showAlert('Email déplacé vers la corbeille', 'success');
            closeEmailDetailModal();
            await loadEmails();
        } else {
            showAlert('Erreur lors du déplacement', 'danger');
        }
    } catch (error) {
        showAlert('Erreur lors du déplacement de l\'email', 'danger');
        console.error(error);
    }
}

function updateUnreadCounts() {
    const unreadInbox = allEmails.filter(e => e.folder === 'inbox' && !e.is_read).length;
    document.getElementById('unread-inbox').textContent = unreadInbox;
}

function formatEmailBody(text) {
    return text.replace(/\n/g, '<br>');
}

function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
        return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays < 7) {
        return date.toLocaleDateString('fr-FR', { weekday: 'short', hour: '2-digit', minute: '2-digit' });
    } else {
        return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alertId = 'alert-' + Date.now();
    
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type}" role="alert" style="margin-bottom: 1rem;">
            ${message}
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.remove();
        }
    }, 5000);
}
