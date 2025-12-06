"""
PDF Generator for BMC Uruguay Quotations.
Generates professional PDF quotes using ReportLab.
"""

import os
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

class PDFGenerator:
    def __init__(self, output_dir="quotations"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def generate_quote(self, quote_data):
        """
        Generates a PDF quote from a dictionary of quote data.
        Returns the absolute path to the generated PDF.
        """
        quote_id = quote_data.get("id", f"COT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        filename = f"Cotizacion_{quote_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # --- Header ---
        # Add Logo if exists (placeholder for now)
        # if os.path.exists("logo.png"):
        #    im = Image("logo.png", width=4*cm, height=2*cm)
        #    story.append(im)
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER
        )
        story.append(Paragraph("COTIZACIÓN", title_style))
        story.append(Spacer(1, 12))
        
        # Header Info
        header_data = [
            ["Fecha:", datetime.datetime.now().strftime("%d/%m/%Y")],
            ["Cotización #:", quote_id],
            ["Validez:", "15 días"]
        ]
        t_header = Table(header_data, colWidths=[3*cm, 5*cm])
        t_header.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        story.append(t_header)
        story.append(Spacer(1, 24))
        
        # --- Customer Info ---
        cliente = quote_data.get("cliente", {})
        story.append(Paragraph("Información del Cliente", styles['Heading3']))
        customer_text = f"""
        <b>Nombre:</b> {cliente.get('nombre', 'N/A')}<br/>
        <b>Teléfono:</b> {cliente.get('telefono', 'N/A')}<br/>
        <b>Email:</b> {cliente.get('email', 'N/A')}<br/>
        <b>Dirección:</b> {cliente.get('direccion', 'N/A')}
        """
        story.append(Paragraph(customer_text, styles['Normal']))
        story.append(Spacer(1, 24))
        
        # --- Items Table ---
        story.append(Paragraph("Detalle de Productos", styles['Heading3']))
        
        specs = quote_data.get("especificaciones", {})
        
        # Prepare table data
        table_data = [
            ["Producto", "Descripción", "Cantidad", "Precio Unit.", "Total"]
        ]
        
        product_name = specs.get('producto', 'Producto Genérico').title()
        desc = f"Espesor: {specs.get('espesor', 'N/A')}\nColor: {specs.get('color', 'N/A')}"
        # Calculate area if strictly needed for quantity, or use logic from data
        area = float(specs.get('largo_metros', 0)) * float(specs.get('ancho_metros', 0))
        qty = f"{area:.2f} m²"
        
        price_total = float(quote_data.get('precio_total', 0))
        price_unit = float(quote_data.get('precio_metro_cuadrado', 0))
        
        table_data.append([
            product_name,
            desc,
            qty,
            f"USD {price_unit:.2f}",
            f"USD {price_total:.2f}"
        ])
        
        # Table Style
        t_items = Table(table_data, colWidths=[4*cm, 5*cm, 2.5*cm, 2.5*cm, 3*cm])
        t_items.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ecf0f1')),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(t_items)
        story.append(Spacer(1, 12))
        
        # --- Total ---
        total_style = ParagraphStyle(
            'TotalStyle',
            parent=styles['Heading2'],
            alignment=TA_RIGHT,
            textColor=colors.HexColor('#2c3e50')
        )
        story.append(Paragraph(f"Total: USD {price_total:.2f}", total_style))
        story.append(Spacer(1, 36))
        
        # --- Terms ---
        story.append(Paragraph("Términos y Condiciones", styles['Heading4']))
        terms = """
        1. Los precios están expresados en Dólares Americanos (USD).<br/>
        2. La entrega de la mercadería se coordinará una vez confirmado el pago.<br/>
        3. Esta cotización no implica reserva de stock.<br/>
        4. BMC Uruguay garantiza la calidad de todos sus productos.
        """
        story.append(Paragraph(terms, styles['Normal']))
        
        # Build
        doc.build(story)
        return os.path.abspath(filepath)

# Test execution
if __name__ == "__main__":
    test_data = {
        "id": "TEST-001",
        "cliente": {"nombre": "Juan Perez", "telefono": "099123456"},
        "especificaciones": {
            "producto": "isodec", "espesor": "100mm", "color": "Blanco", 
            "largo_metros": 10, "ancho_metros": 5
        },
        "precio_total": 1500.00,
        "precio_metro_cuadrado": 30.00
    }
    generator = PDFGenerator()
    path = generator.generate_quote(test_data)
    print(f"PDF generado en: {path}")
