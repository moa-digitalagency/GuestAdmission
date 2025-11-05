let selectedClients = new Set();
let allClients = [];

document.addEventListener('DOMContentLoaded', function() {
    loadClients();
    loadNewsletterHistory();
    loadSendGridConfig();
});

function showTab(tabName) {
    document.querySelectorAll('.newsletter-tab').forEach(tab => {
        tab.style.display = 'none';
    });
    
    const tabs = {
        'compose': 'composeTab',
        'history': 'historyTab',
        'config': 'configTab'
    };
    
    const tabId = tabs[tabName];
    if (tabId) {
        document.getElementById(tabId).style.display = 'block';
    }
    
    if (tabName === 'history') {
        loadNewsletterHistory();
    } else if (tabName === 'config') {
        loadSendGridConfig();
    }
}

function loadClients() {
    fetch('/api/newsletters/clients')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allClients = data.clients;
                renderClientsList(allClients);
            } else {
                document.getElementById('clientsList').innerHTML = 
                    `<tr><td colspan="6" style="text-align: center; color: #ef4444;">Erreur: ${data.error}</td></tr>`;
            }
        })
        .catch(error => {
            console.error('Error loading clients:', error);
            document.getElementById('clientsList').innerHTML = 
                '<tr><td colspan="6" style="text-align: center; color: #ef4444;">Erreur de chargement</td></tr>';
        });
}

function renderClientsList(clients) {
    const tbody = document.getElementById('clientsList');
    
    if (clients.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #6b7280;">Aucun client avec email</td></tr>';
        return;
    }
    
    tbody.innerHTML = clients.map(client => `
        <tr>
            <td style="text-align: center;">
                <input type="checkbox" 
                    class="client-checkbox" 
                    data-email="${client.email}"
                    data-client-id="${client.id}"
                    onchange="updateSelectedClients()">
            </td>
            <td>${client.nom || '-'}</td>
            <td>${client.prenom || '-'}</td>
            <td>${client.email}</td>
            <td>${client.pays || '-'}</td>
            <td>${client.ville || '-'}</td>
        </tr>
    `).join('');
}

function toggleSelectAllClients() {
    const selectAll = document.getElementById('selectAllClients').checked;
    const headerCheckbox = document.getElementById('headerCheckbox');
    
    headerCheckbox.checked = selectAll;
    
    document.querySelectorAll('.client-checkbox').forEach(checkbox => {
        checkbox.checked = selectAll;
    });
    
    updateSelectedClients();
}

function updateSelectedClients() {
    selectedClients.clear();
    
    document.querySelectorAll('.client-checkbox:checked').forEach(checkbox => {
        selectedClients.add(checkbox.dataset.email);
    });
    
    const selectAllCheckbox = document.getElementById('selectAllClients');
    const headerCheckbox = document.getElementById('headerCheckbox');
    const totalCheckboxes = document.querySelectorAll('.client-checkbox').length;
    const checkedCheckboxes = document.querySelectorAll('.client-checkbox:checked').length;
    
    selectAllCheckbox.checked = checkedCheckboxes === totalCheckboxes && totalCheckboxes > 0;
    headerCheckbox.checked = selectAllCheckbox.checked;
    
    document.getElementById('selectedCount').innerHTML = 
        `<strong>${selectedClients.size}</strong> destinataire(s) sélectionné(s)`;
}

function sendNewsletter() {
    const subject = document.getElementById('newsletterSubject').value.trim();
    const content = document.getElementById('newsletterContent').value.trim();
    const contentType = document.getElementById('contentType').value;
    
    if (!subject) {
        alert('❌ Veuillez saisir un sujet');
        return;
    }
    
    if (!content) {
        alert('❌ Veuillez saisir un contenu');
        return;
    }
    
    if (selectedClients.size === 0) {
        alert('❌ Veuillez sélectionner au moins un destinataire');
        return;
    }
    
    if (!confirm(`Voulez-vous vraiment envoyer cette newsletter à ${selectedClients.size} destinataire(s) ?`)) {
        return;
    }
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳ Envoi en cours...';
    
    fetch('/api/newsletters/send', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            subject: subject,
            content: content,
            content_type: contentType,
            recipient_emails: Array.from(selectedClients)
        })
    })
    .then(response => response.json())
    .then(data => {
        btn.disabled = false;
        btn.textContent = '📤 Envoyer la newsletter';
        
        if (data.success) {
            alert(`✅ ${data.message}`);
            resetNewsletterForm();
            showTab('history');
        } else {
            alert(`❌ Erreur: ${data.error}`);
        }
    })
    .catch(error => {
        btn.disabled = false;
        btn.textContent = '📤 Envoyer la newsletter';
        console.error('Error sending newsletter:', error);
        alert('❌ Erreur lors de l\'envoi de la newsletter');
    });
}

function resetNewsletterForm() {
    document.getElementById('newsletterForm').reset();
    selectedClients.clear();
    document.querySelectorAll('.client-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    document.getElementById('selectAllClients').checked = false;
    document.getElementById('headerCheckbox').checked = false;
    updateSelectedClients();
}

function updateEditorPlaceholder() {
    const contentType = document.getElementById('contentType').value;
    const helpText = document.getElementById('editorHelp');
    const textarea = document.getElementById('newsletterContent');
    
    if (contentType === 'markdown') {
        helpText.textContent = 'Utilisez la syntaxe Markdown pour formater votre contenu (# Titre, **gras**, *italique*, etc.)';
        textarea.placeholder = '# Titre de votre newsletter\n\nVotre contenu en **Markdown**...';
    } else {
        helpText.textContent = 'Vous pouvez utiliser les balises HTML pour formater votre contenu.';
        textarea.placeholder = '<h1>Titre de votre newsletter</h1>\n<p>Votre contenu HTML...</p>';
    }
}

function loadNewsletterHistory() {
    fetch('/api/newsletters')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderNewsletterHistory(data.newsletters);
            } else {
                document.getElementById('historyList').innerHTML = 
                    `<tr><td colspan="5" style="text-align: center; color: #ef4444;">Erreur: ${data.error}</td></tr>`;
            }
        })
        .catch(error => {
            console.error('Error loading newsletter history:', error);
            document.getElementById('historyList').innerHTML = 
                '<tr><td colspan="5" style="text-align: center; color: #ef4444;">Erreur de chargement</td></tr>';
        });
}

function renderNewsletterHistory(newsletters) {
    const tbody = document.getElementById('historyList');
    
    if (newsletters.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #6b7280;">Aucune newsletter envoyée</td></tr>';
        return;
    }
    
    tbody.innerHTML = newsletters.map(newsletter => {
        const statusBadge = newsletter.status === 'sent' 
            ? '<span class="badge badge-green">✓ Envoyée</span>'
            : newsletter.status === 'failed'
            ? '<span class="badge badge-red">✗ Échec</span>'
            : '<span class="badge badge-yellow">⏳ En cours</span>';
        
        const sentBy = newsletter.sent_by_prenom && newsletter.sent_by_nom
            ? `${newsletter.sent_by_prenom} ${newsletter.sent_by_nom}`
            : newsletter.sent_by_username || '-';
        
        const recipientCount = newsletter.recipient_emails ? newsletter.recipient_emails.length : 0;
        
        return `
            <tr>
                <td>${new Date(newsletter.sent_at).toLocaleString('fr-FR')}</td>
                <td>${newsletter.subject}</td>
                <td>${recipientCount} destinataire(s)</td>
                <td>${statusBadge}</td>
                <td>${sentBy}</td>
            </tr>
        `;
    }).join('');
}

function loadSendGridConfig() {
    fetch('/api/newsletters/config')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.config) {
                const config = data.config;
                document.getElementById('fromEmail').value = config.from_email || '';
                document.getElementById('fromName').value = config.from_name || '';
                
                if (config.has_api_key) {
                    document.getElementById('sendgridApiKey').placeholder = '••••••••••••••••••••••••••••••';
                }
                
                if (config.active) {
                    document.getElementById('configStatus').innerHTML = `
                        <div style="background: #f0fdf4; padding: 1rem; border-radius: 6px; border-left: 4px solid #22c55e;">
                            <strong style="color: #166534;">✅ Configuration SendGrid active</strong>
                            <p style="margin: 0.5rem 0 0 0; color: #166534;">Votre configuration SendGrid est opérationnelle.</p>
                        </div>
                    `;
                } else {
                    document.getElementById('configStatus').innerHTML = `
                        <div style="background: #fef3c7; padding: 1rem; border-radius: 6px; border-left: 4px solid #f59e0b;">
                            <strong style="color: #92400e;">⚠️ Configuration SendGrid non configurée</strong>
                            <p style="margin: 0.5rem 0 0 0; color: #92400e;">Veuillez configurer SendGrid pour envoyer des newsletters.</p>
                        </div>
                    `;
                }
            } else {
                document.getElementById('configStatus').innerHTML = `
                    <div style="background: #fef3c7; padding: 1rem; border-radius: 6px; border-left: 4px solid #f59e0b;">
                        <strong style="color: #92400e;">⚠️ Aucune configuration trouvée</strong>
                        <p style="margin: 0.5rem 0 0 0; color: #92400e;">Veuillez configurer SendGrid pour envoyer des newsletters.</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error loading SendGrid config:', error);
        });
}

function saveSendGridConfig() {
    const apiKey = document.getElementById('sendgridApiKey').value.trim();
    const fromEmail = document.getElementById('fromEmail').value.trim();
    const fromName = document.getElementById('fromName').value.trim();
    
    if (!apiKey && document.getElementById('sendgridApiKey').placeholder === 'SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx') {
        alert('❌ Veuillez saisir une clé API SendGrid');
        return;
    }
    
    if (!fromEmail) {
        alert('❌ Veuillez saisir un email expéditeur');
        return;
    }
    
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳ Test en cours...';
    
    const payload = {
        from_email: fromEmail,
        from_name: fromName
    };
    
    if (apiKey) {
        payload.sendgrid_api_key = apiKey;
    }
    
    fetch('/api/newsletters/config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        btn.disabled = false;
        btn.textContent = '💾 Enregistrer et tester';
        
        if (data.success) {
            alert(`✅ ${data.message}\n\nUn email de test a été envoyé à ${fromEmail}`);
            loadSendGridConfig();
        } else {
            alert(`❌ Erreur: ${data.error}`);
        }
    })
    .catch(error => {
        btn.disabled = false;
        btn.textContent = '💾 Enregistrer et tester';
        console.error('Error saving SendGrid config:', error);
        alert('❌ Erreur lors de l\'enregistrement de la configuration');
    });
}
