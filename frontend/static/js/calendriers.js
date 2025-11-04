let currentEtablissements = [];
let currentCalendars = [];
let editingCalendarId = null;
let currentReservations = [];
let viewMode = 'list';

document.addEventListener('DOMContentLoaded', function() {
    loadEtablissements();
    loadCalendars();
    loadReservations();
});

async function loadEtablissements() {
    try {
        const response = await fetch('/api/etablissements?actif_only=false');
        const data = await response.json();
        currentEtablissements = data;
        
        const filterSelect = document.getElementById('filterEtablissement');
        const formSelect = document.getElementById('calendarEtablissement');
        
        filterSelect.innerHTML = '<option value="">Tous les établissements</option>';
        formSelect.innerHTML = '<option value="">Sélectionner un établissement</option>';
        
        data.forEach(etablissement => {
            if (etablissement.actif) {
                const option1 = new Option(etablissement.nom_etablissement, etablissement.id);
                const option2 = new Option(etablissement.nom_etablissement, etablissement.id);
                filterSelect.add(option1);
                formSelect.add(option2);
            }
        });
        
        filterSelect.addEventListener('change', function() {
            loadCalendars();
            loadReservations();
        });
    } catch (error) {
        console.error('Erreur lors du chargement des établissements:', error);
    }
}

async function loadCalendars() {
    const etablissementId = document.getElementById('filterEtablissement').value;
    const url = etablissementId 
        ? `/api/calendriers?etablissement_id=${etablissementId}`
        : '/api/calendriers';
    
    try {
        const response = await fetch(url);
        const calendars = await response.json();
        currentCalendars = calendars;
        displayCalendars(calendars);
    } catch (error) {
        console.error('Erreur lors du chargement des calendriers:', error);
        document.getElementById('calendarsTable').innerHTML = 
            '<p style="color: red; text-align: center;">Erreur lors du chargement des calendriers</p>';
    }
}

function displayCalendars(calendars) {
    const container = document.getElementById('calendarsTable');
    
    if (calendars.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">Aucun calendrier configuré</p>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Nom</th>
                    <th>Établissement</th>
                    <th>Plateforme</th>
                    <th>Dernière synchro</th>
                    <th>Statut</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${calendars.map(cal => {
                    const lastSync = cal.derniere_synchronisation 
                        ? new Date(cal.derniere_synchronisation).toLocaleString('fr-FR')
                        : 'Jamais';
                    const statusBadge = getStatusBadge(cal.statut_derniere_synchro);
                    const platformBadge = getPlatformBadge(cal.plateforme);
                    
                    return `
                    <tr>
                        <td><strong>${cal.nom}</strong></td>
                        <td>${cal.nom_etablissement || 'N/A'}</td>
                        <td>${platformBadge}</td>
                        <td>${lastSync}</td>
                        <td>${statusBadge}</td>
                        <td>
                            <button class="btn-icon" onclick="synchronizeCalendar(${cal.id})" title="Synchroniser">
                                🔄
                            </button>
                            <button class="btn-icon" onclick="editCalendar(${cal.id})" title="Modifier">
                                ✏️
                            </button>
                            <button class="btn-icon" onclick="deleteCalendar(${cal.id})" title="Supprimer">
                                🗑️
                            </button>
                        </td>
                    </tr>
                `}).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

function getPlatformBadge(plateforme) {
    const badges = {
        'airbnb': '<span class="badge badge-airbnb">Airbnb</span>',
        'booking': '<span class="badge badge-booking">Booking.com</span>',
        'autre': '<span class="badge badge-autre">Autre</span>'
    };
    return badges[plateforme] || badges['autre'];
}

function getStatusBadge(statut) {
    const badges = {
        'succès': '<span class="badge badge-success">Succès</span>',
        'jamais': '<span class="badge badge-warning">Jamais synchronisé</span>',
        'aucune_reservation': '<span class="badge badge-warning">Aucune réservation</span>',
        'erreur': '<span class="badge badge-error">Erreur</span>'
    };
    return badges[statut] || '<span class="badge badge-warning">Inconnu</span>';
}

function showAddCalendarModal() {
    editingCalendarId = null;
    document.getElementById('modalTitle').textContent = 'Ajouter un Calendrier';
    document.getElementById('calendarForm').reset();
    document.getElementById('calendarId').value = '';
    document.getElementById('calendarActif').checked = true;
    document.getElementById('calendarModal').classList.add('active');
}

function closeCalendarModal() {
    document.getElementById('calendarModal').classList.remove('active');
    editingCalendarId = null;
}

async function editCalendar(calendarId) {
    try {
        const response = await fetch(`/api/calendriers/${calendarId}`);
        const calendar = await response.json();
        
        editingCalendarId = calendarId;
        document.getElementById('modalTitle').textContent = 'Modifier le Calendrier';
        document.getElementById('calendarId').value = calendar.id;
        document.getElementById('calendarEtablissement').value = calendar.etablissement_id;
        document.getElementById('calendarNom').value = calendar.nom;
        document.getElementById('calendarPlateforme').value = calendar.plateforme;
        document.getElementById('calendarUrl').value = calendar.ical_url;
        document.getElementById('calendarActif').checked = calendar.actif;
        
        document.getElementById('calendarModal').classList.add('active');
    } catch (error) {
        console.error('Erreur lors du chargement du calendrier:', error);
        alert('Erreur lors du chargement du calendrier');
    }
}

async function deleteCalendar(calendarId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce calendrier et toutes ses réservations importées ?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/calendriers/${calendarId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Calendrier supprimé avec succès');
            loadCalendars();
            loadReservations();
        } else {
            alert('Erreur lors de la suppression');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression');
    }
}

async function synchronizeCalendar(calendarId) {
    const btn = event.target;
    btn.disabled = true;
    btn.textContent = '⏳';
    
    try {
        const response = await fetch(`/api/calendriers/${calendarId}/synchroniser`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            loadCalendars();
            loadReservations();
        } else {
            alert('Erreur: ' + result.message);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la synchronisation');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔄';
    }
}

document.getElementById('calendarForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const data = {
        etablissement_id: parseInt(document.getElementById('calendarEtablissement').value),
        nom: document.getElementById('calendarNom').value,
        plateforme: document.getElementById('calendarPlateforme').value,
        ical_url: document.getElementById('calendarUrl').value,
        actif: document.getElementById('calendarActif').checked
    };
    
    try {
        const url = editingCalendarId ? `/api/calendriers/${editingCalendarId}` : '/api/calendriers';
        const method = editingCalendarId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert(editingCalendarId ? 'Calendrier modifié avec succès' : 'Calendrier créé avec succès');
            closeCalendarModal();
            loadCalendars();
        } else {
            alert('Erreur lors de l\'enregistrement');
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'enregistrement');
    }
});

function toggleView() {
    viewMode = viewMode === 'list' ? 'calendar' : 'list';
    const tableView = document.getElementById('reservationsTable');
    const calendarView = document.getElementById('reservationsCalendar');
    const viewIcon = document.getElementById('viewIcon');
    const viewText = document.getElementById('viewText');
    
    if (viewMode === 'calendar') {
        tableView.style.display = 'none';
        calendarView.style.display = 'block';
        viewIcon.textContent = '📋';
        viewText.textContent = 'Vue Liste';
    } else {
        tableView.style.display = 'block';
        calendarView.style.display = 'none';
        viewIcon.textContent = '📅';
        viewText.textContent = 'Vue Calendrier';
    }
    
    displayReservations(currentReservations);
}

async function loadReservations() {
    const etablissementId = document.getElementById('filterEtablissement').value;
    if (!etablissementId) {
        currentReservations = [];
        document.getElementById('reservationsTable').innerHTML = 
            '<p style="text-align: center; color: #666;">Sélectionnez un établissement</p>';
        document.getElementById('reservationsCalendar').innerHTML = 
            '<p style="text-align: center; color: #666;">Sélectionnez un établissement</p>';
        return;
    }
    
    const url = `/api/reservations-ical?etablissement_id=${etablissementId}`;
    
    try {
        const response = await fetch(url);
        const reservations = await response.json();
        currentReservations = reservations;
        displayReservations(reservations);
    } catch (error) {
        console.error('Erreur lors du chargement des réservations:', error);
        currentReservations = [];
        document.getElementById('reservationsTable').innerHTML = 
            '<p style="color: red; text-align: center;">Erreur lors du chargement des réservations</p>';
        document.getElementById('reservationsCalendar').innerHTML = 
            '<p style="color: red; text-align: center;">Erreur lors du chargement des réservations</p>';
    }
}

function displayReservations(reservations) {
    if (viewMode === 'list') {
        displayReservationsTable(reservations);
    } else {
        displayReservationsCalendar(reservations);
    }
}

function displayReservationsTable(reservations) {
    const container = document.getElementById('reservationsTable');
    
    if (reservations.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">Aucune réservation importée</p>';
        return;
    }
    
    const table = `
        <table>
            <thead>
                <tr>
                    <th>Titre</th>
                    <th>Calendrier</th>
                    <th>Plateforme</th>
                    <th>Date d'arrivée</th>
                    <th>Date de départ</th>
                    <th>Nuits</th>
                </tr>
            </thead>
            <tbody>
                ${reservations.map(res => {
                    const dateDebut = new Date(res.date_debut).toLocaleDateString('fr-FR');
                    const dateFin = new Date(res.date_fin).toLocaleDateString('fr-FR');
                    const nuits = Math.ceil((new Date(res.date_fin) - new Date(res.date_debut)) / (1000 * 60 * 60 * 24));
                    const platformBadge = getPlatformBadge(res.plateforme);
                    
                    return `
                    <tr>
                        <td><strong>${res.titre}</strong></td>
                        <td>${res.calendrier_nom}</td>
                        <td>${platformBadge}</td>
                        <td>${dateDebut}</td>
                        <td>${dateFin}</td>
                        <td>${nuits} nuit(s)</td>
                    </tr>
                `}).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = table;
}

function displayReservationsCalendar(reservations) {
    const container = document.getElementById('reservationsCalendar');
    
    if (reservations.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">Aucune réservation importée</p>';
        return;
    }
    
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    const monthStart = new Date(currentYear, currentMonth, 1);
    const monthEnd = new Date(currentYear, currentMonth + 1, 0);
    
    const monthNames = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
    
    const firstDayOfWeek = monthStart.getDay();
    const daysInMonth = monthEnd.getDate();
    
    let calendarHTML = `
        <div style="background: #fff; border-radius: 1rem; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.3rem; font-weight: 600; color: #1f2937;">${monthNames[currentMonth]} ${currentYear}</h3>
            </div>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.5rem; margin-bottom: 0.5rem;">
                <div style="text-align: center; font-weight: 600; color: #6b7280; padding: 0.5rem;">Dim</div>
                <div style="text-align: center; font-weight: 600; color: #6b7280; padding: 0.5rem;">Lun</div>
                <div style="text-align: center; font-weight: 600; color: #6b7280; padding: 0.5rem;">Mar</div>
                <div style="text-align: center; font-weight: 600; color: #6b7280; padding: 0.5rem;">Mer</div>
                <div style="text-align: center; font-weight: 600; color: #6b7280; padding: 0.5rem;">Jeu</div>
                <div style="text-align: center; font-weight: 600; color: #6b7280; padding: 0.5rem;">Ven</div>
                <div style="text-align: center; font-weight: 600; color: #6b7280; padding: 0.5rem;">Sam</div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.5rem;">
    `;
    
    for (let i = 0; i < firstDayOfWeek; i++) {
        calendarHTML += '<div style="padding: 1rem;"></div>';
    }
    
    for (let day = 1; day <= daysInMonth; day++) {
        const currentDate = new Date(currentYear, currentMonth, day);
        const dateStr = currentDate.toISOString().split('T')[0];
        
        const dayReservations = reservations.filter(res => {
            const resStart = new Date(res.date_debut);
            const resEnd = new Date(res.date_fin);
            return currentDate >= resStart && currentDate < resEnd;
        });
        
        const isToday = day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear();
        
        let dayStyle = 'padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 0.5rem; min-height: 80px; position: relative;';
        if (isToday) {
            dayStyle += ' background: #eff6ff; border-color: #3b82f6;';
        } else if (dayReservations.length > 0) {
            dayStyle += ' background: #fef3c7; border-color: #f59e0b;';
        }
        
        calendarHTML += `
            <div style="${dayStyle}">
                <div style="font-weight: 600; color: #374151; margin-bottom: 0.25rem;">${day}</div>
                ${dayReservations.slice(0, 2).map(res => `
                    <div style="background: #fee2e2; color: #991b1b; padding: 0.25rem; border-radius: 0.25rem; font-size: 0.75rem; margin-bottom: 0.25rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${res.titre} - ${res.calendrier_nom}">
                        ${res.plateforme === 'airbnb' ? '🏠' : res.plateforme === 'booking' ? '🏨' : '📅'} ${res.calendrier_nom}
                    </div>
                `).join('')}
                ${dayReservations.length > 2 ? `<div style="font-size: 0.75rem; color: #6b7280;">+${dayReservations.length - 2} autre(s)</div>` : ''}
            </div>
        `;
    }
    
    calendarHTML += `
            </div>
        </div>
    `;
    
    container.innerHTML = calendarHTML;
}
