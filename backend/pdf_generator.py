"""
PDF Report Generation for Staylet Compliance Reports
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from io import BytesIO
from datetime import datetime, timezone

# Brand colors
BRAND_BLUE = colors.HexColor('#2563eb')
BRAND_GREEN = colors.HexColor('#059669')
BRAND_AMBER = colors.HexColor('#d97706')
BRAND_RED = colors.HexColor('#dc2626')
BRAND_SLATE = colors.HexColor('#64748b')
BRAND_DARK = colors.HexColor('#1e293b')

def get_status_color(status):
    """Get color based on compliance status."""
    status_colors = {
        'compliant': BRAND_GREEN,
        'expiring_soon': BRAND_AMBER,
        'overdue': BRAND_RED,
        'missing': BRAND_SLATE
    }
    return status_colors.get(status, BRAND_SLATE)

def get_status_label(status):
    """Get readable label for status."""
    labels = {
        'compliant': 'Compliant',
        'expiring_soon': 'Expiring Soon',
        'overdue': 'Overdue',
        'missing': 'Missing'
    }
    return labels.get(status, status.title())

def get_category_label(category):
    """Get readable label for category."""
    labels = {
        'gas_safety': 'Gas Safety Certificate',
        'eicr': 'EICR',
        'epc': 'EPC',
        'insurance': 'Insurance',
        'fire_risk_assessment': 'Fire Risk Assessment',
        'pat_testing': 'PAT Testing',
        'legionella': 'Legionella Risk Assessment',
        'smoke_co_alarms': 'Smoke/CO Alarms',
        'licence': 'Licence',
        'custom': 'Custom'
    }
    return labels.get(category, category.title())

def format_date(date_str):
    """Format ISO date string to readable format."""
    if not date_str:
        return 'Not set'
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%d %B %Y')
    except:
        return date_str

def days_until(date_str):
    """Calculate days until expiry."""
    if not date_str:
        return None
    try:
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        delta = (dt.date() - datetime.now(timezone.utc).date()).days
        return delta
    except:
        return None

def generate_compliance_report(property_data, compliance_records, tasks, documents, company_name=None):
    """
    Generate a PDF compliance report for a property.
    
    Args:
        property_data: Dict containing property details
        compliance_records: List of compliance record dicts
        tasks: List of task dicts
        documents: List of document dicts
        company_name: Optional company name for branding
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=BRAND_DARK,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=BRAND_SLATE,
        spaceAfter=20
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=BRAND_BLUE,
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=BRAND_DARK,
        spaceAfter=6
    )
    
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=9,
        textColor=BRAND_SLATE
    )
    
    # Build story
    story = []
    
    # Header
    header_text = company_name or 'Staylet'
    story.append(Paragraph(f"<font color='#2563eb'>{header_text}</font> - Compliance Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M')}", subtitle_style))
    
    # Property Details Section
    story.append(Paragraph("Property Details", section_style))
    
    property_info = [
        ['Property Name:', property_data.get('name', 'N/A')],
        ['Address:', property_data.get('address', 'N/A')],
        ['Postcode:', property_data.get('postcode', 'N/A')],
        ['UK Nation:', property_data.get('uk_nation', 'N/A').title()],
        ['Property Type:', property_data.get('property_type', 'N/A').title()],
    ]
    
    property_table = Table(property_info, colWidths=[100, 350])
    property_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), BRAND_SLATE),
        ('TEXTCOLOR', (1, 0), (1, -1), BRAND_DARK),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(property_table)
    story.append(Spacer(1, 10))
    
    # Compliance Summary Section
    story.append(Paragraph("Compliance Summary", section_style))
    
    # Count statuses
    status_counts = {'compliant': 0, 'expiring_soon': 0, 'overdue': 0, 'missing': 0}
    for record in compliance_records:
        status = record.get('compliance_status', 'compliant')
        if status in status_counts:
            status_counts[status] += 1
    
    summary_data = [
        ['Status', 'Count'],
        ['Compliant', str(status_counts['compliant'])],
        ['Expiring Soon', str(status_counts['expiring_soon'])],
        ['Overdue', str(status_counts['overdue'])],
    ]
    
    summary_table = Table(summary_data, colWidths=[150, 100])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#dcfce7')),  # Green
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#fef3c7')),  # Amber
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#fee2e2')),  # Red
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, BRAND_SLATE),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 10))
    
    # Compliance Records Section
    story.append(Paragraph("Compliance Records", section_style))
    
    if compliance_records:
        # Sort by status priority (overdue first, then expiring, then compliant)
        status_priority = {'overdue': 0, 'expiring_soon': 1, 'compliant': 2, 'missing': 3}
        sorted_records = sorted(compliance_records, key=lambda x: status_priority.get(x.get('compliance_status', 'compliant'), 4))
        
        records_data = [['Category', 'Title', 'Expiry Date', 'Days Left', 'Status']]
        
        for record in sorted_records:
            status = record.get('compliance_status', 'compliant')
            expiry = record.get('expiry_date')
            days = days_until(expiry)
            days_text = str(days) if days is not None else 'N/A'
            
            records_data.append([
                get_category_label(record.get('category', '')),
                record.get('title', 'Untitled'),
                format_date(expiry),
                days_text,
                get_status_label(status)
            ])
        
        records_table = Table(records_data, colWidths=[120, 130, 90, 60, 80])
        
        # Build table style
        table_style = [
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (3, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]
        
        # Color-code status column
        for i, record in enumerate(sorted_records, 1):
            status = record.get('compliance_status', 'compliant')
            if status == 'overdue':
                table_style.append(('TEXTCOLOR', (4, i), (4, i), BRAND_RED))
                table_style.append(('FONTNAME', (4, i), (4, i), 'Helvetica-Bold'))
            elif status == 'expiring_soon':
                table_style.append(('TEXTCOLOR', (4, i), (4, i), BRAND_AMBER))
                table_style.append(('FONTNAME', (4, i), (4, i), 'Helvetica-Bold'))
            else:
                table_style.append(('TEXTCOLOR', (4, i), (4, i), BRAND_GREEN))
        
        records_table.setStyle(TableStyle(table_style))
        story.append(records_table)
    else:
        story.append(Paragraph("No compliance records found for this property.", normal_style))
    
    story.append(Spacer(1, 10))
    
    # Tasks Section
    story.append(Paragraph("Outstanding Tasks", section_style))
    
    pending_tasks = [t for t in tasks if t.get('task_status') != 'completed']
    
    if pending_tasks:
        tasks_data = [['Task', 'Due Date', 'Priority', 'Status']]
        
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_tasks = sorted(pending_tasks, key=lambda x: priority_order.get(x.get('priority', 'medium'), 1))
        
        for task in sorted_tasks:
            tasks_data.append([
                task.get('title', 'Untitled'),
                format_date(task.get('due_date')),
                task.get('priority', 'medium').title(),
                task.get('task_status', 'pending').replace('_', ' ').title()
            ])
        
        tasks_table = Table(tasks_data, colWidths=[200, 100, 80, 100])
        tasks_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        story.append(tasks_table)
    else:
        story.append(Paragraph("No outstanding tasks for this property.", normal_style))
    
    story.append(Spacer(1, 10))
    
    # Documents Section
    story.append(Paragraph("Uploaded Documents", section_style))
    
    if documents:
        docs_data = [['Filename', 'Type', 'Uploaded']]
        
        for doc in documents:
            file_type = doc.get('file_type', 'Unknown')
            if '/' in file_type:
                file_type = file_type.split('/')[-1].upper()
            
            docs_data.append([
                doc.get('original_filename', 'Unknown'),
                file_type,
                format_date(doc.get('uploaded_at', ''))
            ])
        
        docs_table = Table(docs_data, colWidths=[250, 100, 130])
        docs_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_BLUE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        story.append(docs_table)
    else:
        story.append(Paragraph("No documents uploaded for this property.", normal_style))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        f"This report was generated by Staylet on {datetime.now().strftime('%d %B %Y at %H:%M')}. "
        "For the most up-to-date information, please log in to your Staylet account.",
        small_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
