"""
Generate a synthetic, compliant Bank Muscat statement PDF for functional testing and validation.
Incorporates OMR 3-decimal currency, bilingual headers, reference numbers,
multi-line narrations, and complete balance reconciliation.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_bank_muscat_pdf(output_path: str = "data/raw/bank_muscat_sample.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BankTitle",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#A31D24"),  # Bank Muscat Maroon/Red
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "SubTitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#333333")
    )
    cell_style = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontSize=8,
        leading=10
    )
    header_style = ParagraphStyle(
        "HeaderCell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        fontName="Helvetica-Bold",
        textColor=colors.whitesmoke
    )

    elements = []

    # Bank Header
    elements.append(Paragraph("<b>Bank Muscat SAOG</b> | بنك مسقط", title_style))
    elements.append(Paragraph("Account Statement / كشف حساب", subtitle_style))
    elements.append(Spacer(1, 10))

    # Account Metadata
    meta_data = [
        [
            Paragraph("<b>Account Name:</b> Ahmed bin Salim Al-Harthy", cell_style),
            Paragraph("<b>Branch:</b> Muscat Main Branch (0315)", cell_style)
        ],
        [
            Paragraph("<b>Account Number:</b> 0315-01234567-001", cell_style),
            Paragraph("<b>Currency:</b> OMR (Omani Rial)", cell_style)
        ],
        [
            Paragraph("<b>IBAN:</b> OM310000031501234567001", cell_style),
            Paragraph("<b>Statement Period:</b> 01/01/2025 to 31/01/2025", cell_style)
        ],
        [
            Paragraph("<b>Opening Balance:</b> 1,500.000 OMR", cell_style),
            Paragraph("<b>Closing Balance:</b> 2,199.500 OMR", cell_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[260, 260])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9F9F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor("#EEEEEE")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 15))

    # Transaction Table Header
    headers = [
        Paragraph("Date", header_style),
        Paragraph("Value Date", header_style),
        Paragraph("Description / Narration", header_style),
        Paragraph("Ref / Chq No", header_style),
        Paragraph("Debit (OMR)", header_style),
        Paragraph("Credit (OMR)", header_style),
        Paragraph("Balance (OMR)", header_style),
    ]

    # Transactions (3 decimal currency OMR)
    txns = [
        ("02/01/2025", "02/01/2025", "SALARY CREDIT PETROLEUM DEV OMAN\nEMPLOYEE ID PDO-99120", "FT2500291823", "", "850.500", "2,350.500"),
        ("05/01/2025", "05/01/2025", "ATM CASH WITHDRAWAL\nMUSCAT GRAND MALL ATM", "ATM-9921", "50.000", "", "2,300.500"),
        ("10/01/2025", "10/01/2025", "POS PURCHASE LULU HYPERMARKET\nBAUSHER STORE 12", "POS-88412", "45.250", "", "2,255.250"),
        ("15/01/2025", "15/01/2025", "UTILITY BILL PAYMENT OMANTEL\nACCOUNT 96899128", "OT99214", "25.750", "", "2,229.500"),
        ("20/01/2025", "20/01/2025", "FUNDS TRANSFER TO SALIM AL-BALUSHI\nFAMILY SUPPORT PAYMENT", "FT250204918", "100.000", "", "2,129.500"),
        ("25/01/2025", "25/01/2025", "DIVIDEND CREDIT OMINVEST SECURITIES\nANNUAL DISTRIBUTION 2024", "DIV8812", "", "70.500", "2,200.000"),
        ("31/01/2025", "31/01/2025", "MONTHLY SERVICE FEE\nACCOUNT MAINTENANCE CHARGE", "CHG001", "0.500", "", "2,199.500"),
    ]

    table_data = [headers]
    for row in txns:
        table_data.append([
            Paragraph(row[0], cell_style),
            Paragraph(row[1], cell_style),
            Paragraph(row[2], cell_style),
            Paragraph(row[3], cell_style),
            Paragraph(row[4], cell_style),
            Paragraph(row[5], cell_style),
            Paragraph(row[6], cell_style),
        ])

    col_widths = [55, 55, 170, 70, 55, 55, 62]
    t_txn = Table(table_data, colWidths=col_widths, repeatRows=1)
    t_txn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#A31D24")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#FDF7F7")]),
    ]))
    elements.append(t_txn)
    elements.append(Spacer(1, 15))

    # Statement Summary
    summary_text = (
        "<b>Total Debits:</b> 221.500 OMR &nbsp;&nbsp;|&nbsp;&nbsp; "
        "<b>Total Credits:</b> 921.000 OMR &nbsp;&nbsp;|&nbsp;&nbsp; "
        "<b>Closing Balance:</b> 2,199.500 OMR"
    )
    elements.append(Paragraph(summary_text, subtitle_style))
    elements.append(Spacer(1, 20))

    # Footer note
    footer_text = (
        "<i>This is a computer generated statement and requires no signature. "
        "Please notify Bank Muscat of any discrepancies within 15 days. "
        "Bank Muscat SAOG, P.O. Box 134, Ruwi, Postal Code 112, Sultanate of Oman.</i>"
    )
    elements.append(Paragraph(footer_text, ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7, textColor=colors.gray)))

    doc.build(elements)
    print(f"Bank Muscat synthetic statement generated at: {output_path}")


if __name__ == "__main__":
    generate_bank_muscat_pdf()
