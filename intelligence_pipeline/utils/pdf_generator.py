"""PDF Generator module for creating clean, valid binary PDFs from text/metadata."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def convert_text_to_pdf(text: str, output_target: Union[str, Path, io.BytesIO]) -> bytes:
    """Converts structured text content into a valid, formatted PDF binary.
    
    Args:
        text: Plain text content to render.
        output_target: Path or file-like object or filename.

    Returns:
        bytes: Raw binary PDF content.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=4
    )

    label_style = ParagraphStyle(
        'DocLabel',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#2C5282')
    )

    value_style = ParagraphStyle(
        'DocValue',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1A202C')
    )

    story = []
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]

    # Filter out header if it starts with %PDF-1.4
    if lines and lines[0].startswith('%PDF'):
        lines = lines[1:]

    if lines:
        header_text = lines[0].lstrip('% ').strip()
        story.append(Paragraph(header_text, title_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3182CE'), spaceAfter=10))
        lines = lines[1:]

    table_data = []
    for line in lines:
        if line.startswith('%'):
            story.append(Paragraph(f"<i>{line.lstrip('%').strip()}</i>", body_style))
            story.append(Spacer(1, 4))
        elif ':' in line:
            parts = line.split(':', 1)
            k = parts[0].strip()
            v = parts[1].strip()
            table_data.append([Paragraph(k, label_style), Paragraph(v, value_style)])
        else:
            if table_data:
                t = Table(table_data, colWidths=[180, 340])
                t.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ]))
                story.append(t)
                story.append(Spacer(1, 6))
                table_data = []
            story.append(Paragraph(line, body_style))

    if table_data:
        t = Table(table_data, colWidths=[180, 340])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(t)

    doc.build(story)
    pdf_bytes = buffer.getvalue()

    if isinstance(output_target, (str, Path)):
        Path(output_target).write_bytes(pdf_bytes)

    return pdf_bytes
