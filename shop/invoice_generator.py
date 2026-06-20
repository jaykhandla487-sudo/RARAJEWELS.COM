from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

def generate_pdf_invoice(order):
    """
    Generates a premium, luxury-styled PDF invoice for a given order.
    """
    buffer = io.BytesIO()
    
    # Setup document
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=36, 
        leftMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom colors
    gold_color = colors.HexColor('#D4AF37')
    dark_bg = colors.HexColor('#111111')
    light_gold = colors.HexColor('#FAF7EC')
    text_dark = colors.HexColor('#222222')
    text_muted = colors.HexColor('#666666')
    
    # Typography Styles
    title_style = ParagraphStyle(
        'InvTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=gold_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'InvSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.white,
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        'InvHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=gold_color,
        spaceBefore=10,
        spaceAfter=5
    )
    
    normal_style = ParagraphStyle(
        'InvNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=text_dark,
        leading=12
    )

    bold_style = ParagraphStyle(
        'InvBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=text_dark,
        leading=12
    )
    
    # 1. Header Banner (Black background with Gold brand name)
    header_data = [
        [
            Paragraph("RARA JEWELS", title_style),
            Paragraph("<b>INVOICE</b><br/>Invoice No: " + order.order_number + "<br/>Date: " + order.created_at.strftime('%d-%b-%Y'), ParagraphStyle('HeaderRight', parent=styles['Normal'], fontName='Helvetica', fontSize=9, textColor=colors.white, alignment=2, leading=12))
        ]
    ]
    
    header_table = Table(header_data, colWidths=[270, 250])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), dark_bg),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 15))
    
    # 2. Billing & Shipping Details Table
    address_parts = order.shipping_address.split('\n')
    addr_line = "<br/>".join([part.strip() for part in address_parts if part.strip()])
    
    details_data = [
        [
            Paragraph("<b>Seller Info:</b><br/>Rara Jewels Corporate Office<br/>Luxury Tower, Sector 4<br/>Mumbai, Maharashtra, 400001<br/>Email: sales@rarajewels.com<br/>Mobile: +91 99999 99999", normal_style),
            Paragraph(f"<b>Shipped To:</b><br/>{addr_line}", normal_style)
        ]
    ]
    
    details_table = Table(details_data, colWidths=[260, 260])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_gold),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1, gold_color),
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 20))
    
    # 3. Items Summary Table
    items_header = [
        Paragraph("<b>Sr.</b>", bold_style),
        Paragraph("<b>Product Details</b>", bold_style),
        Paragraph("<b>Qty</b>", bold_style),
        Paragraph("<b>Unit Price (INR)</b>", bold_style),
        Paragraph("<b>Total (INR)</b>", bold_style)
    ]
    
    table_data = [items_header]
    
    for idx, item in enumerate(order.items.all(), 1):
        row = [
            Paragraph(str(idx), normal_style),
            Paragraph(f"<b>{item.product.name}</b>", normal_style),
            Paragraph(str(item.quantity), normal_style),
            Paragraph(f"{item.price:.2f}", normal_style),
            Paragraph(f"{item.subtotal:.2f}", normal_style)
        ]
        table_data.append(row)
        
    # Totals rows
    table_data.append([
        "", "", "", 
        Paragraph("<b>Subtotal:</b>", normal_style), 
        Paragraph(f"{order.subtotal:.2f}", normal_style)
    ])
    
    if order.discount_amount > 0:
        coupon_str = f" ({order.coupon.code})" if order.coupon else ""
        table_data.append([
            "", "", "", 
            Paragraph(f"<b>Discount{coupon_str}:</b>", normal_style), 
            Paragraph(f"-{order.discount_amount:.2f}", normal_style)
        ])
        
    table_data.append([
        "", "", "", 
        Paragraph("<b>Shipping:</b>", normal_style), 
        Paragraph(f"{order.shipping_charge:.2f}", normal_style)
    ])
    
    table_data.append([
        "", "", "", 
        Paragraph("<b>Grand Total:</b>", bold_style), 
        Paragraph(f"<b>{order.total_price:.2f}</b>", bold_style)
    ])
    
    items_table = Table(table_data, colWidths=[30, 250, 40, 100, 100])
    items_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1.5, gold_color),
        ('LINEBELOW', (0,1), (-1,-5), 0.5, colors.HexColor('#E0E0E0')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F5F5F5')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('LINEABOVE', (3,-4), (4,-4), 1, gold_color), # Above grand total
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 30))
    
    # 4. Footer notes
    footer_style = ParagraphStyle(
        'InvFooter',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=text_muted,
        alignment=1
    )
    story.append(Paragraph("Thank you for shopping with Rara Jewels! The epitome of premium imitation jewelry.", footer_style))
    story.append(Paragraph("This is a computer-generated invoice. No signature is required.", footer_style))
    
    doc.build(story)
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
