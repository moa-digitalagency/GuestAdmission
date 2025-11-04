let occupationChart, countriesChart, trendsChart;

document.addEventListener('DOMContentLoaded', function() {
    loadEtablissements();
    loadStatistics();
});

async function loadEtablissements() {
    try {
        const response = await fetch('/api/etablissements');
        const data = await response.json();
        
        const select = document.getElementById('etablissementFilter');
        select.innerHTML = '<option value="">Tous les établissements</option>';
        
        data.forEach(etab => {
            const option = document.createElement('option');
            option.value = etab.id;
            option.textContent = etab.nom_etablissement;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erreur:', error);
    }
}

async function loadStatistics() {
    const periode = document.getElementById('periodFilter').value;
    const etablissement = document.getElementById('etablissementFilter').value;
    
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - parseInt(periode));
    
    const params = new URLSearchParams();
    if (etablissement) params.append('etablissement_id', etablissement);
    params.append('date_debut', startDate.toISOString().split('T')[0]);
    params.append('date_fin', endDate.toISOString().split('T')[0]);
    
    await Promise.all([
        loadGlobalStats(),
        loadOccupancyRate(params),
        loadTopCountries(params),
        loadSejoursByOccupants(params),
        loadSejoursByRooms(params),
        loadRevenue(params),
        loadMonthlyTrends(params)
    ]);
}

async function loadGlobalStats() {
    try {
        const response = await fetch('/api/statistics/global');
        const data = await response.json();
        
        document.getElementById('totalSejours').textContent = data.total_sejours || 0;
        document.getElementById('totalClients').textContent = data.total_clients || 0;
        document.getElementById('totalEtablissements').textContent = data.total_etablissements || 0;
        document.getElementById('totalChambres').textContent = data.total_chambres || 0;
    } catch (error) {
        console.error('Erreur chargement stats globales:', error);
    }
}

async function loadOccupancyRate(params) {
    try {
        const response = await fetch('/api/statistics/occupancy?' + params);
        const data = await response.json();
        
        document.getElementById('totalChambresOcc').textContent = data.total_chambres || 0;
        document.getElementById('chambresOccupees').textContent = data.chambres_occupees || 0;
        document.getElementById('totalNuits').textContent = data.total_nuits || 0;
        document.getElementById('tauxOccupation').textContent = (data.taux_occupation || 0).toFixed(1) + '%';
        
        updateOccupationChart(data.taux_occupation || 0);
    } catch (error) {
        console.error('Erreur chargement taux occupation:', error);
    }
}

function updateOccupationChart(rate) {
    const ctx = document.getElementById('occupationChart');
    
    if (occupationChart) {
        occupationChart.destroy();
    }
    
    occupationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Occupé', 'Disponible'],
            datasets: [{
                data: [rate, 100 - rate],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(229, 231, 235, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed.toFixed(1) + '%';
                        }
                    }
                }
            }
        }
    });
}

async function loadTopCountries(params) {
    try {
        const response = await fetch('/api/statistics/countries?' + params);
        const countries = await response.json();
        
        const ctx = document.getElementById('countriesCanvas');
        
        if (countriesChart) {
            countriesChart.destroy();
        }
        
        const labels = countries.map(c => c.pays || 'Inconnu');
        const visiteurs = countries.map(c => c.nombre_visiteurs || 0);
        
        countriesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Nombre de visiteurs',
                    data: visiteurs,
                    backgroundColor: 'rgba(34, 197, 94, 0.8)',
                    borderColor: 'rgba(34, 197, 94, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    } catch (error) {
        console.error('Erreur chargement pays:', error);
    }
}

async function loadSejoursByOccupants(params) {
    try {
        const response = await fetch('/api/statistics/sejours-by-occupants?' + params);
        const sejours = await response.json();
        
        const tbody = document.getElementById('sejoursOccupantsTable');
        
        if (sejours.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Aucune donnée disponible</td></tr>';
            return;
        }
        
        tbody.innerHTML = sejours.map(s => `
            <tr>
                <td><a href="/sejour/${s.id}">${s.numero_reservation || 'N/A'}</a></td>
                <td>${s.nom_etablissement || 'N/A'}</td>
                <td>${formatDate(s.date_arrivee)}</td>
                <td>${formatDate(s.date_depart)}</td>
                <td><strong>${s.nombre_occupants || 0}</strong></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Erreur chargement séjours par occupants:', error);
    }
}

async function loadSejoursByRooms(params) {
    try {
        const response = await fetch('/api/statistics/sejours-by-rooms?' + params);
        const sejours = await response.json();
        
        const tbody = document.getElementById('sejoursChambresTable');
        
        if (sejours.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Aucune donnée disponible</td></tr>';
            return;
        }
        
        tbody.innerHTML = sejours.map(s => `
            <tr>
                <td><a href="/sejour/${s.id}">${s.numero_reservation || 'N/A'}</a></td>
                <td>${s.nom_etablissement || 'N/A'}</td>
                <td>${formatDate(s.date_arrivee)}</td>
                <td>${formatDate(s.date_depart)}</td>
                <td><strong>${s.nombre_chambres || 0}</strong></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Erreur chargement séjours par chambres:', error);
    }
}

async function loadRevenue(params) {
    try {
        const response = await fetch('/api/statistics/revenue?' + params);
        const data = await response.json();
        
        document.getElementById('revenueHebergement').textContent = formatCurrency(data.total_hebergement);
        document.getElementById('revenueExtras').textContent = formatCurrency(data.total_extras);
        document.getElementById('revenueCharges').textContent = formatCurrency(data.total_charges);
        document.getElementById('revenueTaxes').textContent = formatCurrency(data.total_taxes);
        document.getElementById('revenueTotal').textContent = formatCurrency(data.total_revenu);
    } catch (error) {
        console.error('Erreur chargement revenus:', error);
    }
}

async function loadMonthlyTrends(params) {
    try {
        const etablissement = document.getElementById('etablissementFilter').value;
        const url = '/api/statistics/monthly-trends?' + 
                   (etablissement ? 'etablissement_id=' + etablissement + '&' : '') + 
                   'months=12';
        
        const response = await fetch(url);
        const trends = await response.json();
        
        const ctx = document.getElementById('monthlyTrendsChart');
        
        if (trendsChart) {
            trendsChart.destroy();
        }
        
        trends.reverse();
        
        const labels = trends.map(t => {
            const [year, month] = t.mois.split('-');
            const date = new Date(year, month - 1);
            return date.toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' });
        });
        const sejours = trends.map(t => t.nombre_sejours || 0);
        const revenus = trends.map(t => parseFloat(t.revenu || 0));
        
        trendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Nombre de séjours',
                    data: sejours,
                    borderColor: 'rgba(59, 130, 246, 1)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    yAxisID: 'y',
                    tension: 0.3
                }, {
                    label: 'Revenus (MAD)',
                    data: revenus,
                    borderColor: 'rgba(16, 185, 129, 1)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    yAxisID: 'y1',
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Séjours'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Revenus (MAD)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Erreur chargement tendances:', error);
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
}

function formatCurrency(amount) {
    if (!amount && amount !== 0) return '0 MAD';
    return parseFloat(amount).toFixed(2) + ' MAD';
}
