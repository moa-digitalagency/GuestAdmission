"""
Service pour l'export PDF de la liste des clients
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime
from typing import Optional
from ..config.database import get_db_connection


class ClientsExportService:
    """Service pour générer l'export PDF des clients"""
    
    @staticmethod
    def generate_clients_pdf(search_filter: str = '', 
                            pays_filter: str = '', 
                            type_piece_filter: str = '') -> BytesIO:
        """Générer un PDF de la liste des clients"""
        
        clients = ClientsExportService._get_filtered_clients(
            search_filter, pays_filter, type_piece_filter
        )
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph("📋 Liste des Clients", title_style))
        
        filters_applied = []
        if search_filter:
            filters_applied.append(f"Recherche: {search_filter}")
        if pays_filter:
            filters_applied.append(f"Pays: {pays_filter}")
        if type_piece_filter:
            filters_applied.append(f"Type pièce: {type_piece_filter}")
        
        if filters_applied:
            filter_text = "Filtres appliqués: " + " | ".join(filters_applied)
            story.append(Paragraph(filter_text, styles['Normal']))
        
        story.append(Paragraph(f"Date d'export: {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
        story.append(Paragraph(f"Total: {len(clients)} client(s)", styles['Normal']))
        story.append(Spacer(1, 10*mm))
        
        data = [
            ['Nom', 'Prénom', 'Email', 'Téléphone', 'Pays', 'Type pièce', 'N° pièce']
        ]
        
        for client in clients:
            data.append([
                client.get('nom', 'N/A') or 'N/A',
                client.get('prenom', 'N/A') or 'N/A',
                client.get('email', 'N/A') or 'N/A',
                client.get('telephone', 'N/A') or 'N/A',
                client.get('pays', 'N/A') or 'N/A',
                client.get('type_piece', 'N/A') or 'N/A',
                client.get('numero_piece', 'N/A') or 'N/A'
            ])
        
        col_widths = [35*mm, 35*mm, 50*mm, 35*mm, 35*mm, 30*mm, 35*mm]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')])
        ]))
        story.append(table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def _get_filtered_clients(search_filter: str = '',
                             pays_filter: str = '',
                             type_piece_filter: str = ''):
        """Récupérer les clients avec filtres appliqués"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = 'SELECT * FROM personnes WHERE 1=1'
        params = []
        
        if search_filter:
            query += ' AND (LOWER(nom) LIKE %s OR LOWER(prenom) LIKE %s OR LOWER(email) LIKE %s)'
            search_pattern = f'%{search_filter.lower()}%'
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if pays_filter:
            query += ' AND pays = %s'
            params.append(pays_filter)
        
        if type_piece_filter:
            query += ' AND type_piece = %s'
            params.append(type_piece_filter)
        
        query += ' ORDER BY nom, prenom'
        
        cur.execute(query, params)
        clients = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [dict(c) for c in clients] if clients else []
