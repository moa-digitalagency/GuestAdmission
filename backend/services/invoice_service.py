"""
Service pour la génération de factures PDF
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Optional
from ..config.database import get_db_connection
import os
import requests


class InvoiceService:
    """Service pour générer des factures PDF"""
    
    @staticmethod
    def generate_sejour_invoice(sejour_id: int) -> BytesIO:
        """Générer une facture PDF pour un séjour"""
        
        sejour_data = InvoiceService._get_sejour_data(sejour_id)
        if not sejour_data:
            raise ValueError(f"Séjour {sejour_id} non trouvé")
        
        # Vérifier que le séjour est clôturé
        if sejour_data.get('statut') != 'closed' and not sejour_data.get('closed_at'):
            raise ValueError("La facture ne peut être générée que pour un séjour clôturé")
        
        etablissement = InvoiceService._get_etablissement_data(sejour_data['etablissement_id'])
        extras = InvoiceService._get_sejour_extras(sejour_id)
        personnes = InvoiceService._get_sejour_personnes(sejour_id)
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        if etablissement.get('logo_url'):
            try:
                logo_path = etablissement['logo_url']
                img = None
                
                if logo_path.startswith('http://') or logo_path.startswith('https://'):
                    response = requests.get(logo_path, timeout=5)
                    if response.status_code == 200:
                        logo_temp = BytesIO(response.content)
                        img = Image(logo_temp, width=60*mm, height=30*mm, kind='proportional')
                else:
                    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    full_logo_path = os.path.join(base_dir, logo_path.lstrip('/'))
                    if os.path.exists(full_logo_path):
                        img = Image(full_logo_path, width=60*mm, height=30*mm, kind='proportional')
                
                if img:
                    img.hAlign = 'CENTER'
                    story.append(img)
                    story.append(Spacer(1, 5*mm))
            except Exception as e:
                print(f"Erreur lors du chargement du logo: {e}")
        
        story.append(Paragraph(f"FACTURE N° {sejour_data.get('numero_reservation', 'N/A')}", title_style))
        story.append(Spacer(1, 10*mm))
        
        info_etablissement = [
            [Paragraph("<b>Établissement:</b>", styles['Normal']), 
             Paragraph(etablissement.get('nom_etablissement', 'N/A'), styles['Normal'])],
            [Paragraph("<b>Adresse:</b>", styles['Normal']), 
             Paragraph(etablissement.get('adresse', 'N/A') or 'N/A', styles['Normal'])],
            [Paragraph("<b>Ville:</b>", styles['Normal']), 
             Paragraph(f"{etablissement.get('ville', 'N/A')}, {etablissement.get('pays', 'N/A')}", styles['Normal'])],
            [Paragraph("<b>Téléphone:</b>", styles['Normal']), 
             Paragraph(etablissement.get('telephone', 'N/A') or 'N/A', styles['Normal'])],
            [Paragraph("<b>Email:</b>", styles['Normal']), 
             Paragraph(etablissement.get('email', 'N/A') or 'N/A', styles['Normal'])],
        ]
        
        if etablissement.get('numero_identification'):
            info_etablissement.append([
                Paragraph("<b>N° Identification:</b>", styles['Normal']),
                Paragraph(etablissement['numero_identification'], styles['Normal'])
            ])
        
        etablissement_table = Table(info_etablissement, colWidths=[50*mm, 90*mm])
        etablissement_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eff6ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(etablissement_table)
        story.append(Spacer(1, 8*mm))
        
        contact_principal = personnes[0] if personnes else {}
        
        info_client = [
            [Paragraph("<b>Client:</b>", styles['Normal']), 
             Paragraph(f"{contact_principal.get('prenom', '')} {contact_principal.get('nom', 'N/A')}", styles['Normal'])],
            [Paragraph("<b>Email:</b>", styles['Normal']), 
             Paragraph(contact_principal.get('email', 'N/A') or 'N/A', styles['Normal'])],
            [Paragraph("<b>Téléphone:</b>", styles['Normal']), 
             Paragraph(contact_principal.get('telephone', 'N/A') or 'N/A', styles['Normal'])],
            [Paragraph("<b>Pays:</b>", styles['Normal']), 
             Paragraph(contact_principal.get('pays', 'N/A') or 'N/A', styles['Normal'])],
        ]
        
        client_table = Table(info_client, colWidths=[50*mm, 90*mm])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0fdf4')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(client_table)
        story.append(Spacer(1, 8*mm))
        
        story.append(Paragraph("Détails du Séjour", heading_style))
        
        date_arrivee = sejour_data.get('date_arrivee', '')
        date_depart = sejour_data.get('date_depart', '')
        if date_arrivee:
            date_arrivee = datetime.strptime(str(date_arrivee), '%Y-%m-%d').strftime('%d/%m/%Y')
        if date_depart:
            date_depart = datetime.strptime(str(date_depart), '%Y-%m-%d').strftime('%d/%m/%Y')
        
        sejour_info = [
            [Paragraph("<b>Date d'arrivée:</b>", styles['Normal']), date_arrivee or 'N/A'],
            [Paragraph("<b>Date de départ:</b>", styles['Normal']), date_depart or 'N/A'],
            [Paragraph("<b>Nombre de nuits:</b>", styles['Normal']), str(sejour_data.get('nombre_jours', 'N/A'))],
        ]
        
        sejour_table = Table(sejour_info, colWidths=[50*mm, 90*mm])
        sejour_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef3c7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sejour_table)
        story.append(Spacer(1, 8*mm))
        
        story.append(Paragraph("Facturation", heading_style))
        
        data = [
            ['Description', 'Qté', 'Prix Unit.', 'Total'],
        ]
        
        facture_hebergement = float(sejour_data.get('facture_hebergement', 0) or 0)
        data.append([
            'Hébergement',
            str(sejour_data.get('nombre_jours', 1)),
            f"{facture_hebergement / max(sejour_data.get('nombre_jours', 1), 1):.2f} {etablissement.get('devise', 'MAD')}",
            f"{facture_hebergement:.2f} {etablissement.get('devise', 'MAD')}"
        ])
        
        total_extras = 0
        for extra in extras:
            montant = float(extra.get('montant_total', 0) or 0)
            total_extras += montant
            data.append([
                f"{extra.get('nom', 'Extra')} ({extra.get('unite_mesure', 'unité')})",
                str(extra.get('quantite', 1)),
                f"{float(extra.get('prix_unitaire', 0)):.2f} {etablissement.get('devise', 'MAD')}",
                f"{montant:.2f} {etablissement.get('devise', 'MAD')}"
            ])
        
        charge_plateforme = float(sejour_data.get('charge_plateforme', 0) or 0)
        if charge_plateforme > 0:
            data.append([
                'Frais de plateforme',
                '1',
                f"{charge_plateforme:.2f} {etablissement.get('devise', 'MAD')}",
                f"{charge_plateforme:.2f} {etablissement.get('devise', 'MAD')}"
            ])
        
        taxe_sejour = float(sejour_data.get('taxe_sejour', 0) or 0)
        if taxe_sejour > 0:
            data.append([
                'Taxe de séjour',
                '1',
                f"{taxe_sejour:.2f} {etablissement.get('devise', 'MAD')}",
                f"{taxe_sejour:.2f} {etablissement.get('devise', 'MAD')}"
            ])
        
        total_general = facture_hebergement + total_extras + charge_plateforme + taxe_sejour
        
        data.append(['', '', '', ''])
        data.append(['', '', 'TOTAL', f"{total_general:.2f} {etablissement.get('devise', 'MAD')}"])
        
        table = Table(data, colWidths=[80*mm, 25*mm, 35*mm, 35*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -3), colors.beige),
            ('GRID', (0, 0), (-1, -3), 0.5, colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('ALIGN', (2, -1), (-1, -1), 'CENTER'),
        ]))
        story.append(table)
        
        story.append(Spacer(1, 15*mm))
        
        footer_text = f"""
        <para align=center>
        <font size=8 color="#6b7280">
        Facture générée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}<br/>
        Merci pour votre confiance!
        </font>
        </para>
        """
        story.append(Paragraph(footer_text, styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def _get_sejour_data(sejour_id: int) -> Optional[Dict]:
        """Récupérer les données du séjour"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM reservations WHERE id = %s', (sejour_id,))
        sejour = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(sejour) if sejour else None
    
    @staticmethod
    def _get_etablissement_data(etablissement_id: int) -> Dict:
        """Récupérer les données de l'établissement"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('SELECT * FROM etablissements WHERE id = %s', (etablissement_id,))
        etablissement = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(etablissement) if etablissement else {}
    
    @staticmethod
    def _get_sejour_extras(sejour_id: int) -> List[Dict]:
        """Récupérer les extras du séjour"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT e.nom, e.prix_unitaire, e.unite_mesure, 
                   se.quantite, se.montant_total
            FROM sejours_extras se
            JOIN extras e ON se.extra_id = e.id
            WHERE se.reservation_id = %s
            ORDER BY se.date_ajout
        ''', (sejour_id,))
        
        extras = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [dict(e) for e in extras] if extras else []
    
    @staticmethod
    def _get_sejour_personnes(sejour_id: int) -> List[Dict]:
        """Récupérer les personnes du séjour"""
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            SELECT nom, prenom, email, telephone, pays
            FROM personnes
            WHERE reservation_id = %s
            ORDER BY est_contact_principal DESC, id
        ''', (sejour_id,))
        
        personnes = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [dict(p) for p in personnes] if personnes else []
