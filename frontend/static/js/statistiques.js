async function loadStatistiques() {
    try {
        const [sejoursResp, clientsResp, etabsResp, chambresResp] = await Promise.all([
            fetch('/api/sejours'),
            fetch('/api/personnes'),
            fetch('/api/etablissements'),
            fetch('/api/chambres')
        ]);
        
        const sejours = await sejoursResp.json();
        const clients = await clientsResp.json();
        const etablissements = await etabsResp.json();
        const chambres = await chambresResp.json();
        
        document.getElementById('totalSejours').textContent = sejours.length;
        document.getElementById('totalClients').textContent = clients.length;
        document.getElementById('totalEtablissements').textContent = etablissements.length;
        document.getElementById('totalChambres').textContent = chambres.length;
        
        const today = new Date().toISOString().split('T')[0];
        const sejoursActifs = sejours.filter(s => s.date_debut <= today && s.date_fin >= today);
        document.getElementById('sejoursActifs').textContent = sejoursActifs.length;
        
        const chambresOccupees = chambres.filter(c => !c.disponible);
        document.getElementById('chambresOccupees').textContent = chambresOccupees.length;
        
    } catch (error) {
        console.error('Erreur chargement statistiques:', error);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadStatistiques);
} else {
    loadStatistiques();
}
