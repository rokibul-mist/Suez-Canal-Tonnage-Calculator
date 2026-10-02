"""
Professional Tables-Only Report Generator
Generates clean, official, structured PDF and HTML reports containing ONLY calculation tables.
Complies with Suez Canal Authority (SCA) Rules of Navigation.
Replicates the official Certificate Cover Page format.
100% Black and White / Monochrome. Pure standard ASCII/Unicode English.
All typography in Times New Roman.
All units formatted with superscripts (m², m³).
No empty pages: tables flow naturally with KeepTogether protection.
No redundant Remarks columns.
Note section details What Was Done and What Was Obtained.
"""

# Official SCA conversion constant: 1 Suez Ton = 100 cu.ft = 2.832 m³
SUEZ_TON_M3 = 2.832
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, KeepTogether, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

# Strictly Black and White / Monochrome Grayscale Palette
BLACK        = colors.black
WHITE        = colors.white
DARK_GRAY    = colors.HexColor("#222222")
MID_GRAY     = colors.HexColor("#E0E0E0")
LIGHT_GRAY   = colors.HexColor("#F5F5F5")
BORDER_BLACK = colors.black
BORDER_GRAY  = colors.HexColor("#666666")

REPORT_HTML_CSS = """
  @page { size: A4 portrait; margin: 10mm; }
  body { font-family: 'Times New Roman', Times, Georgia, serif; margin: 12px auto; max-width: 195mm; color: #000; background: #fff; line-height: 1.3; }
  h1 { color: #000; font-size: 14px; margin-bottom: 6px; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 4px; font-family: 'Times New Roman', Times, Georgia, serif; }
  h2 { color: #000; font-size: 12px; margin-top: 14px; margin-bottom: 6px; text-transform: uppercase; border-bottom: 1px solid #000; padding-bottom: 2px; font-family: 'Times New Roman', Times, Georgia, serif; }
  h3 { color: #000; font-size: 10px; margin-top: 10px; margin-bottom: 4px; text-transform: uppercase; font-weight: bold; font-family: 'Times New Roman', Times, Georgia, serif; }
  table { width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 9px; font-family: 'Times New Roman', Times, Georgia, serif; page-break-inside: avoid; }
  th, td { border: 1px solid #000; padding: 3px 5px; font-family: 'Times New Roman', Times, Georgia, serif; }
  th { background: #000; color: #fff; font-weight: bold; text-align: center; }
  .sub-hdr { background: #E0E0E0; color: #000; font-weight: bold; }
  .text-right { text-align: right; }
  .text-center { text-align: center; }
  .text-left { text-align: left; }
  .highlight { background: #EAEAEA; font-weight: bold; color: #000; }
  .accent { background: #F5F5F5; font-weight: bold; color: #000; }
  .alt-row:nth-child(even) { background: #FAFAFA; }
  .station-container { display: flex; flex-direction: column; gap: 10px; margin-bottom: 14px; }
  .station-box { width: 100%; page-break-inside: avoid; }
  .cert-header { text-align: center; font-weight: bold; font-size: 12px; margin-bottom: 10px; font-family: 'Times New Roman', Times, Georgia, serif; }
  .three-col-header { width: 100%; margin-bottom: 8px; }
  .three-col-header td { border: none; text-align: center; padding: 2px; }
  .three-col-header .underlined { border-bottom: 1.5px solid #000; font-weight: bold; font-size: 11px; padding-bottom: 3px; }
  .three-col-header .sublabel { font-size: 8px; text-transform: uppercase; padding-top: 2px; }
  .note-box { border: 1px solid #000; margin-bottom: 8px; display: flex; font-size: 8.5px; line-height: 1.35; background: #fff; font-family: 'Times New Roman', Times, Georgia, serif; }
  .note-title-cell { background: #F5F5F5; font-weight: bold; text-align: center; padding: 8px 4px; border-right: 1px solid #000; display: flex; align-items: center; justify-content: center; width: 95px; min-width: 95px; font-size: 9px; font-family: 'Times New Roman', Times, Georgia, serif; }
  .note-content-cell { padding: 6px 10px; font-family: 'Times New Roman', Times, Georgia, serif; }
  .note-content-cell p { margin: 0 0 4px 0; }
  @media print {
    body { margin: 0; max-width: 100%; }
    .page-break { page-break-before: always; }
  }
"""

def generate_pdf_table_report(output_pdf_path, udt_data, bulb_data, vessel_info, forecastle_data=None, hatch_data=None, superstructure_data=None):
    """
    Builds a professional multi-page PDF report containing structured naval architecture calculation tables.
    100% Times New Roman.
    No empty pages.
    No Remarks columns.
    Superscript units (m², m³).
    Note section includes What Was Done and What Was Obtained.
    """
    if os.path.dirname(output_pdf_path):
        os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=10*mm,
        rightMargin=10*mm,
        topMargin=8*mm,
        bottomMargin=8*mm
    )

    title_style = ParagraphStyle(
        'TableTitle',
        fontName='Times-Bold',
        fontSize=9.5,
        leading=12,
        textColor=BLACK,
        spaceAfter=4,
        spaceBefore=6,
        keepWithNext=True
    )

    cert_title_style = ParagraphStyle(
        'CertTitle',
        fontName='Times-Bold',
        fontSize=11,
        leading=14,
        alignment=1,
        textColor=BLACK,
        spaceAfter=2
    )

    elements = []
    udt_data = udt_data or {}

    # =========================================================================
    # PREPARE DATA & TONNAGE TOTALS
    # =========================================================================
    v_name = vessel_info.get("vessel_name", "PATRONUS")
    nationality = vessel_info.get("nationality", "BAHAMAS")
    kind_of_ship = vessel_info.get("kind_of_ship", "BULK CARRIER")
    official_num = vessel_info.get("official_number", "7000085")
    signal_letters = vessel_info.get("signal_letters", "C6R 2092")
    port_registry = vessel_info.get("port_of_registry", "NASSAU")
    keel_date = vessel_info.get("keel_laying_date", "7 JUNE 2006")
    built_where = vessel_info.get("built_where", "COCHIN, INDIA")
    material_hull = vessel_info.get("material_of_hull", "STEEL")
    builder = vessel_info.get("builder", "COCHIN SHIPYARD LTD")
    engine = vessel_info.get("engine_type", "DIESEL ENGINE : ONE")
    launch_date = vessel_info.get("date_of_launch", "")
    propellers = vessel_info.get("propellers", "SCREW PROPELLER : ONE")
    hull_note = vessel_info.get("hull_note", "CSL HULL NO. 017")

    lbp = float(vessel_info.get("lbp", 170.872) or 170.872)
    b_mld = float(vessel_info.get("breadth", 28.00) or 28.00)
    d_mld = float(vessel_info.get("depth", 14.00) or 14.00)

    has_bulb = vessel_info.get("has_bulbous", True) if "has_bulbous" in vessel_info else (bulb_data.get("has_bulbous", True) if bulb_data else False)
    has_fc = vessel_info.get("has_forecastle", True)
    has_hatches = vessel_info.get("has_hatches", True)
    has_roundhouses = vessel_info.get("has_roundhouses", True)

    udt_vol = float(udt_data.get("total_underdeck_volume", 0.0) or 0.0)
    udt_tons = float(udt_data.get("underdeck_tonnage", 0.0) or 0.0)

    if has_bulb and bulb_data:
        bulb_vol = float(bulb_data.get("method_A", {}).get("total_volume", 0.0) or 0.0)
        bulb_tons = float(bulb_data.get("method_A", {}).get("tonnage", 0.0) or 0.0)
    else:
        bulb_vol = 0.0
        bulb_tons = 0.0

    if has_fc and forecastle_data:
        fc_vol = float(forecastle_data.get("forecastle_volume", 0.0) or 0.0)
        fc_tons = float(forecastle_data.get("forecastle_tonnage", 0.0) or 0.0)
    else:
        fc_vol = 0.0
        fc_tons = 0.0

    if has_hatches and hatch_data:
        hatch_exc_vol = float(hatch_data.get("excess_volume", 0.0) or 0.0)
        hatch_exc_tons = float(hatch_data.get("excess_tonnage", 0.0) or 0.0)
    else:
        hatch_exc_vol = 0.0
        hatch_exc_tons = 0.0

    if has_roundhouses and superstructure_data:
        tot_rh_vol = float(superstructure_data.get("round_houses_volume", 0.0) or 0.0)
        tot_rh_ton = float(superstructure_data.get("round_houses_tonnage", 0.0) or 0.0)
        off_v = float(superstructure_data.get("officer_accommodation_volume", 0.0) or 0.0)
        off_acc_ton = float(superstructure_data.get("officer_accommodation_tonnage", 0.0) or 0.0)
        crew_v = float(superstructure_data.get("crew_accommodation_volume", 0.0) or 0.0)
        crew_acc_ton = float(superstructure_data.get("crew_accommodation_tonnage", 0.0) or 0.0)
        work_v = float(superstructure_data.get("working_ship_volume", 0.0) or 0.0)
        work_ship_ton = float(superstructure_data.get("working_ship_tonnage", 0.0) or 0.0)
        prop_v = float(superstructure_data.get("propelling_power_volume", 0.0) or 0.0)
        prop_power_ton = float(superstructure_data.get("propelling_power_tonnage", 0.0) or 0.0)
        tot_d_v = float(superstructure_data.get("total_deduction_volume", 0.0) or 0.0)
        tot_ded_ton = float(superstructure_data.get("total_deduction_tonnage", 0.0) or 0.0)
    else:
        tot_rh_vol = 0.0
        tot_rh_ton = 0.0
        off_v = 0.0
        off_acc_ton = 0.0
        crew_v = 0.0
        crew_acc_ton = 0.0
        work_v = 0.0
        work_ship_ton = 0.0
        prop_v = 0.0
        prop_power_ton = 0.0
        tot_d_v = 0.0
        tot_ded_ton = 0.0

    bulb_cover_tons = bulb_tons if (has_bulb and bulb_tons > 0) else 0.0
    fc_cover_tons = fc_tons if (has_fc and fc_tons > 0) else 0.0
    rh_cover_tons = tot_rh_ton if (has_roundhouses and tot_rh_ton > 0) else 0.0
    hatch_cover_tons = hatch_exc_tons if (has_hatches and hatch_exc_tons > 0) else 0.0

    gross_tonnage = udt_tons + bulb_cover_tons + fc_cover_tons + rh_cover_tons + hatch_cover_tons
    net_tonnage = max(0.0, gross_tonnage - tot_ded_ton)
    gross_vol = udt_vol + bulb_vol + fc_vol + tot_rh_vol + hatch_exc_vol
    net_vol = max(0.0, gross_vol - tot_d_v)

    # =========================================================================
    # SECTION 1: OFFICIAL CERTIFICATE COVER PAGE (A4 PORTRAIT)
    # =========================================================================
    elements.append(Paragraph("CALCULATION SHEETS<br/>FOR<br/>SUEZ CANAL TONNAGE MEASUREMENT", cert_title_style))
    elements.append(Spacer(1, 2*mm))

    hdr_3col_data = [
        [nationality, kind_of_ship, f'"{v_name}"'],
        ["NATIONALITY", "KIND OF SHIP", "NAME OF SHIP"]
    ]
    t_3col = Table(hdr_3col_data, colWidths=[63.3*mm, 63.4*mm, 63.3*mm])
    t_3col.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9.5),
        ('FONTSIZE', (0, 1), (-1, 1), 7),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, BLACK),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(t_3col)
    elements.append(Spacer(1, 1.8*mm))

    part_box_data = [
        ["OFFICIAL NUMBER", "SIGNAL LETTERS", "PORT OF REGISTRY", "KEEL LAYING DATE"],
        [official_num, signal_letters, port_registry, keel_date],
        ["BUILT WHERE: " + built_where, "", "MATERIAL OF HULL: " + material_hull, ""],
        ["NAME OF BUILDER: " + builder, "", "TYPE AND NUMBER OF ENGINE: " + engine, ""],
        ["DATE OF LAUNCH: " + launch_date, "", "KIND AND NUMBER OF PROPELLERS: " + propellers, ""]
    ]
    t_part = Table(part_box_data, colWidths=[47.5*mm, 47.5*mm, 47.5*mm, 47.5*mm])
    t_part.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
        ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
        ('ALIGN', (0, 2), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, 0), 6.5),
        ('FONTNAME', (0, 1), (-1, 1), 'Times-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 7.5),
        ('FONTNAME', (0, 2), (-1, -1), 'Times-Bold'),
        ('FONTSIZE', (0, 2), (-1, -1), 7),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (2, 2), (3, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (2, 3), (3, 3)),
        ('SPAN', (0, 4), (1, 4)),
        ('SPAN', (2, 4), (3, 4)),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
    ]))
    elements.append(t_part)
    elements.append(Spacer(1, 1.8*mm))

    dim_box_data = [
        ["MAIN DIMENSIONS", "", ""],
        ["LENGTH", f"{lbp:.3f}", "M"],
        ["BREADTH", f"{b_mld:.2f}", "M"],
        ["DEPTH", f"{d_mld:.2f}", "M"]
    ]
    t_dim = Table(dim_box_data, colWidths=[70*mm, 95*mm, 25*mm])
    t_dim.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
        ('SPAN', (0, 0), (-1, 0)),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (0, -1), 'Times-Bold'),
        ('FONTSIZE', (0, 1), (0, -1), 7),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('FONTNAME', (1, 1), (1, -1), 'Times-Bold'),
        ('FONTSIZE', (1, 1), (1, -1), 7),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ('FONTSIZE', (2, 1), (2, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
    ]))
    elements.append(t_dim)
    elements.append(Spacer(1, 1.8*mm))

    summary_two_col = [
        ["GROSS TONNAGE", f"{gross_tonnage:,.2f}", "NET TONNAGE", f"{net_tonnage:,.2f}"],
        ["UNDER THE TONNAGE DECK", f"{udt_tons:,.2f}", "DEDUCTED SPACES :", ""],
        ["BULBOUS BOW", f"{bulb_cover_tons:,.2f}" if bulb_cover_tons > 0 else "-", "OFFICER'S ACCOMMODATION", f"{off_acc_ton:,.2f}" if off_acc_ton > 0 else "-"],
        ["FORECASTLE DECK", f"{fc_cover_tons:,.2f}" if fc_cover_tons > 0 else "-", "CREW'S ACCOMMODATION", f"{crew_acc_ton:,.2f}" if crew_acc_ton > 0 else "-"],
        ["ROUND HOUSES, ETC.", f"{rh_cover_tons:,.2f}" if rh_cover_tons > 0 else "-", "USED IN WORKING THE SHIP", f"{work_ship_ton:,.2f}" if work_ship_ton > 0 else "-"],
        ["HATCH WAYS", f"{hatch_cover_tons:,.2f}" if hatch_cover_tons > 0 else "-", "DEDUCTION FOR PROPELLING POWER", f"{prop_power_ton:,.2f}" if prop_power_ton > 0 else "-"],
        ["", "", "TOTAL DEDUCTIONS", f"{tot_ded_ton:,.2f}"],
    ]
    t_sum_2col = Table(summary_two_col, colWidths=[55*mm, 40*mm, 55*mm, 40*mm])
    t_sum_2col.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), MID_GRAY),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('ALIGN', (2, 0), (2, 0), 'LEFT'),
        ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
        ('FONTNAME', (2, 1), (2, 1), 'Times-Bold'),
        ('FONTNAME', (2, 6), (3, 6), 'Times-Bold'),
        ('BACKGROUND', (2, 6), (3, 6), LIGHT_GRAY),
    ]))
    elements.append(t_sum_2col)
    elements.append(Spacer(1, 2.5*mm))

    # Clean, structured Note & Calculation Detail (What was done & What was obtained)
    note_header_style = ParagraphStyle(
        'NoteHeader',
        fontName='Times-Bold',
        fontSize=7.0,
        leading=9.5,
        alignment=1,
        textColor=BLACK
    )
    note_meta_style = ParagraphStyle(
        'NoteMeta',
        fontName='Times-Roman',
        fontSize=6.8,
        leading=8.6,
        textColor=BLACK,
        spaceAfter=2
    )
    note_sec_style = ParagraphStyle(
        'NoteSec',
        fontName='Times-Roman',
        fontSize=6.6,
        leading=8.6,
        textColor=BLACK,
        spaceAfter=2.2
    )

    note_elements = [
        Paragraph(f"<b>SHIP RECORD:</b> {hull_note} &nbsp;&nbsp;|&nbsp;&nbsp; <b>REGULATORY STANDARD:</b> <i>Suez Canal Authority (SCA) Rules of Navigation (Arts. 92&ndash;94 &amp; Appendix 1)</i> &nbsp;&nbsp;|&nbsp;&nbsp; <b>UNIT:</b> 1 Suez Moorsom Ton = 100 cu.ft = <b>2.832 m&sup3;</b>", note_meta_style),
        Paragraph("<b>1. MEASUREMENT PROCEDURES EXECUTED (WHAT WAS DONE):</b><br/>"
                  "&bull; <b>Under Deck Tonnage (UDT):</b> Computed via Simpson's 1st Rule over 21 transverse stations (dx = LBP / 20) with 16 vertical intervals per station (h = D / 16). Transom appendix volume aft of AP included.<br/>"
                  "&bull; <b>Appendages &amp; Enclosed Superstructures:</b> Bulbous bow calculated per SCA Method A (transverse cuts at St. 20, A, B and forward conical nose cap V<sub>nose</sub> = (&pi;/6)&times;A<sub>B</sub>&times;L<sub>nose</sub>). Forecastle deck integrated from transverse offsets. Cargo hatchways excess calculated applying 0.5% (5&permil;) Gross Tonnage statutory allowance. Round houses enclosed spaces schedule aggregated.<br/>"
                  "&bull; <b>Gross &amp; Net Tonnage:</b> Gross Tonnage obtained by summing UDT and all additions; Net Tonnage obtained by deducting statutory spaces (Officers, Crew, Navigation, and Propelling Power capped at &le; 50% GT).", note_sec_style),
        Paragraph("<b>2. SUMMARY OF CALCULATED VALUES &amp; TONNAGES (WHAT WAS OBTAINED):</b><br/>"
                  f"&bull; <b>Under Deck Tonnage (UDT):</b> Volume = <b>{udt_vol:,.2f} m&sup3;</b> &nbsp;&rArr;&nbsp; Tonnage = <b>{udt_tons:,.2f} Suez Tons</b><br/>"
                  f"&bull; <b>Bulbous Bow:</b> Volume = <b>{bulb_vol:,.2f} m&sup3;</b> &nbsp;&rArr;&nbsp; Tonnage = <b>{bulb_cover_tons:,.2f} Suez Tons</b>" + (f" <i>(Fitted)</i>" if (has_bulb and bulb_tons > 0) else " <i>(None / Exempt)</i>") + "<br/>"
                  f"&bull; <b>Forecastle Deck:</b> Volume = <b>{fc_vol:,.2f} m&sup3;</b> &nbsp;&rArr;&nbsp; Tonnage = <b>{fc_cover_tons:,.2f} Suez Tons</b>" + (f" <i>(Fitted)</i>" if (has_fc and fc_tons > 0) else " <i>(None / Exempt)</i>") + "<br/>"
                  f"&bull; <b>Cargo Hatchways Excess:</b> Volume = <b>{hatch_exc_vol:,.2f} m&sup3;</b> &nbsp;&rArr;&nbsp; Tonnage = <b>{hatch_cover_tons:,.2f} Suez Tons</b>" + (f" <i>(Excess over 0.5% GT)</i>" if (has_hatches and hatch_exc_tons > 0) else " <i>(Exempt within 0.5% GT)</i>") + "<br/>"
                  f"&bull; <b>Round Houses / Deckhouses:</b> Volume = <b>{tot_rh_vol:,.2f} m&sup3;</b> &nbsp;&rArr;&nbsp; Tonnage = <b>{rh_cover_tons:,.2f} Suez Tons</b><br/>"
                  f"&bull; <b>TOTAL SUEZ CANAL GROSS TONNAGE (GT):</b> Volume = <b>{gross_vol:,.2f} m&sup3;</b> &nbsp;&rArr;&nbsp; <b>Gross Tonnage = {gross_tonnage:,.2f} Suez Tons</b><br/>"
                  f"&bull; <b>TOTAL STATUTORY DEDUCTIONS:</b> Deducted Volume = <b>{tot_d_v:,.2f} m&sup3;</b> &nbsp;&rArr;&nbsp; <b>Total Deductions = {tot_ded_ton:,.2f} Suez Tons</b><br/>"
                  f"&bull; <b>FINAL SUEZ CANAL NET TONNAGE (NT):</b> Net Volume = <b>{net_vol:,.2f} m&sup3;</b> &nbsp;&rArr;&nbsp; <b>Net Tonnage = {net_tonnage:,.2f} Suez Tons</b>", note_sec_style)
    ]

    note_data = [
        [Paragraph("<b>NOTE<br/>&amp;<br/>CALCULATION<br/>DETAIL</b>", note_header_style), note_elements]
    ]
    t_note = Table(note_data, colWidths=[28*mm, 162*mm])
    t_note.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('VALIGN', (1, 0), (1, 0), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('BACKGROUND', (0, 0), (0, 0), LIGHT_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (1, 0), (1, 0), 4),
        ('RIGHTPADDING', (1, 0), (1, 0), 4),
    ]))
    elements.append(t_note)
    elements.append(PageBreak())

    # =========================================================================
    # SECTION 2: UNDERDECK SUEZ TONNAGE CALCULATION
    # =========================================================================
    # Part 2A: Volume Calculation (Remarks column removed, widths redistributed to 190mm)
    elements.append(Paragraph("Underdeck Suez Tonnage Calculation — Main Hull Volume", title_style))

    long_headers = ["Station", "Name", "Position X (m)", "Depth D (m)", "Area A (m²)", "Factor", "Product A × M"]
    table2_rows = [long_headers]

    for row in udt_data.get("long_rows", []):
        table2_rows.append([
            str(row["station_num"]),
            row["station_name"],
            f"{row['position_x']:.3f}",
            f"{row['depth_m']:.3f}",
            f"{row['area_m2']:,.2f}",
            str(row["factor"]),
            f"{row['product']:,.2f}"
        ])

    sum_prod = udt_data.get('main_hull_sum_products', 0)
    dx3_val = udt_data.get('dx_over_3', 3.1017)
    mh_vol = udt_data.get('main_hull_volume', 0)
    tr_vol = udt_data.get('transom_volume', 0)
    tot_vol = udt_data.get('total_underdeck_volume', 0)
    udt_tons = udt_data.get('underdeck_tonnage', 0)

    table2_rows.append([f"Sum of Products: Σ = Σ (A_i × M_i)", "", "", "", "", "", f"{sum_prod:,.2f}"])
    table2_rows.append([f"Main Hull Volume: V_hull = (dx / 3) × Σ = ({dx3_val:.4f}) × {sum_prod:,.2f}", "", "", "", "", "", f"{mh_vol:,.2f} m³"])
    table2_rows.append([f"Transom Appendix Volume: V_transom (Aft of AP to St. 0)", "", "", "", "", "", f"{tr_vol:,.2f} m³"])
    table2_rows.append([f"Total Under Deck Volume: V_UDT = V_hull + V_transom", "", "", "", "", "", f"{tot_vol:,.2f} m³"])
    table2_rows.append([f"Under Deck Suez Moorsom Tonnage: UDT = V_UDT / 2.832", "", "", "", "", "", f"{udt_tons:,.2f} Suez Tons"])

    n2 = len(table2_rows)
    t2 = Table(table2_rows, colWidths=[16*mm, 26*mm, 26*mm, 26*mm, 30*mm, 18*mm, 48*mm])
    t2_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('BACKGROUND', (0, 0), (-1, 0), BLACK),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6.8),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
        ('ALIGN', (6, 1), (6, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
    ]
    if n2 - 6 >= 1:
        t2_style.append(('ROWBACKGROUNDS', (0, 1), (-1, n2 - 6), [WHITE, LIGHT_GRAY]))
    for r_idx in range(n2 - 5, n2):
        t2_style.append(('SPAN', (0, r_idx), (5, r_idx)))
        t2_style.append(('ALIGN', (0, r_idx), (0, r_idx), 'LEFT'))
        t2_style.append(('FONTNAME', (0, r_idx), (-1, r_idx), 'Times-Bold'))
        t2_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), MID_GRAY))
        t2_style.append(('ALIGN', (6, r_idx), (6, r_idx), 'RIGHT'))

    t2.setStyle(TableStyle(t2_style))
    elements.append(t2)
    elements.append(Spacer(1, 4*mm))

    # Part 2B: Calculation of All Station Areas (Flow naturally without forced 2-per-page breaks)
    transverse_tables = udt_data.get("station_results") or udt_data.get("transverse_tables", {})
    st_keys = list(transverse_tables.keys())

    elements.append(Paragraph("Calculation of Transverse Station Areas", title_style))

    def create_station_table_flowable(st_key):
        st_data = transverse_tables[st_key]
        st_name = st_data.get("station_name", str(st_key))
        depth_val = st_data.get("depth_m", st_data.get("depth", 17.80))
        h_val = st_data.get("h_m", st_data.get("h", depth_val / 16.0))
        h3_val = st_data.get("h_over_3", h_val / 3.0)
        sum_p = st_data.get("sum_products", 0.0)
        tot_a = st_data.get("area_m2", st_data.get("total_area", 0.0))
        pts = st_data.get("rows") or st_data.get("points", [])

        t_rows = [
            [f"Station {st_name} — Depth D = {depth_val:.3f} m | Interval h = D/16 = {h_val:.4f} m | 1/3 h = {h3_val:.4f} m", "", "", "", "", "", ""],
            ["Pt", "Waterline", "Height Z (m)", "Half-B (m)", "Breadth (m)", "Factor", "Product B × M"]
        ]
        for pt in pts:
            pt_no = pt.get("point", pt.get("pt", ""))
            wl_name = pt.get("waterline", pt.get("wl", ""))
            z_val = pt.get("waterline_height_m", pt.get("z", 0.0))
            half_b = pt.get("half_breadth_m", pt.get("half_b", 0.0))
            full_b = pt.get("breadth_m", pt.get("breadth", 0.0))
            factor = pt.get("factor", 1)
            product = pt.get("product", 0.0)
            t_rows.append([
                str(pt_no),
                str(wl_name),
                f"{z_val:.3f}",
                f"{half_b:.3f}",
                f"{full_b:.3f}",
                str(factor),
                f"{product:.3f}"
            ])
        t_rows.append(["Sum of Products: Σ = Σ (Breadth × Factor)", "", "", "", "", "", f"{sum_p:.3f}"])
        t_rows.append([f"Transverse Area: A_i = (h_i / 3) × Σ = ({h_val:.4f} / 3) × {sum_p:.3f}", "", "", "", "", "", f"{tot_a:.2f} m²"])

        nr = len(t_rows)
        t_st = Table(t_rows, colWidths=[14*mm, 34*mm, 28*mm, 28*mm, 28*mm, 22*mm, 36*mm])
        t_style = [
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('SPAN', (0, 0), (-1, 0)),
            ('BACKGROUND', (0, 0), (-1, 0), BLACK),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7.0),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BACKGROUND', (0, 1), (-1, 1), DARK_GRAY),
            ('TEXTCOLOR', (0, 1), (-1, 1), WHITE),
            ('FONTNAME', (0, 1), (-1, 1), 'Times-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 6.5),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 2), (4, -1), 'RIGHT'),
            ('ALIGN', (6, 2), (6, -1), 'RIGHT'),
            ('FONTSIZE', (0, 2), (-1, -1), 6.2),
            ('ROWBACKGROUNDS', (0, 2), (-1, nr - 3), [WHITE, LIGHT_GRAY]),
            ('SPAN', (0, nr - 2), (5, nr - 2)),
            ('SPAN', (0, nr - 1), (5, nr - 1)),
            ('BACKGROUND', (0, nr - 2), (-1, -1), MID_GRAY),
            ('FONTNAME', (0, nr - 2), (-1, -1), 'Times-Bold'),
            ('ALIGN', (0, nr - 2), (0, -1), 'LEFT'),
            ('ALIGN', (6, nr - 2), (6, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 0.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
        ]
        t_st.setStyle(TableStyle(t_style))
        return t_st

    for st_key in st_keys:
        t_flow = create_station_table_flowable(st_key)
        elements.append(KeepTogether([t_flow, Spacer(1, 3.5*mm)]))

    # =========================================================================
    # SECTION 3: BULBOUS BOW TONNAGE CALCULATION (If enabled)
    # =========================================================================
    if has_bulb and bulb_data:
        elements.append(Paragraph("Bulbous Bow Tonnage Calculation — Method A", title_style))
        trans_stations = bulb_data.get("transverse_stations") or bulb_data.get("areas") or {}
        st20_info = trans_stations.get("St_20") or trans_stations.get("st20") or {}
        stA_info  = trans_stations.get("St_A")  or trans_stations.get("stA")  or {}
        stB_info  = trans_stations.get("St_B")  or trans_stations.get("stB")  or {}

        def build_bulb_station_table(st_info, st_title):
            dy_val = st_info.get("dy", 1.0)
            rows = [
                [f"{st_title} | dy = {dy_val:.2f} m", "", "", "", "", "", ""],
                ["Buttock Line", "Half-Breadth Y (m)", "Upper Z (m)", "Lower Z (m)", "Depth D (m)", "Factor", "Product D × M"]
            ]
            for pt in (st_info.get("rows") or st_info.get("points") or []):
                rows.append([
                    pt.get("name", ""),
                    f"{pt.get('y_m', pt.get('y', 0.0)):.3f}",
                    f"{pt.get('z_upper', pt.get('z', 0.0)):.3f}",
                    f"{pt.get('z_lower', 0.0):.3f}",
                    f"{pt.get('depth_m', pt.get('depth', 0.0)):.3f}",
                    str(pt.get("factor", pt.get("multiplier", 1))),
                    f"{pt.get('product', 0.0):.3f}"
                ])
            sp = st_info.get("sum_prod", st_info.get("sum_products", 0.0))
            dy_val = st_info.get("dy", 1.0)
            area_val = st_info.get("total_area", 0.0)

            rows.append(["Sum of Products: Σ = Σ (Depth × Factor)", "", "", "", "", "", f"{sp:.3f}"])
            rows.append([f"Transverse Area: A_bulb = (dy / 3) × Σ × 2 = ({dy_val:.2f} / 3) × {sp:.3f} × 2", "", "", "", "", "", f"{area_val:.3f} m²"])

            nr_b = len(rows)
            t_b = Table(rows, colWidths=[30*mm, 26*mm, 24*mm, 24*mm, 26*mm, 24*mm, 36*mm])
            t_b_style = [
                ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
                ('SPAN', (0, 0), (-1, 0)),
                ('BACKGROUND', (0, 0), (-1, 0), BLACK),
                ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
                ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7.0),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BACKGROUND', (0, 1), (-1, 1), DARK_GRAY),
                ('TEXTCOLOR', (0, 1), (-1, 1), WHITE),
                ('FONTNAME', (0, 1), (-1, 1), 'Times-Bold'),
                ('FONTSIZE', (0, 1), (-1, 1), 6.5),
                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 2), (4, -1), 'RIGHT'),
                ('ALIGN', (6, 2), (6, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
                ('ROWBACKGROUNDS', (0, 2), (-1, nr_b - 3), [WHITE, LIGHT_GRAY]),
                ('SPAN', (0, nr_b - 2), (5, nr_b - 2)),
                ('SPAN', (0, nr_b - 1), (5, nr_b - 1)),
                ('BACKGROUND', (0, nr_b - 2), (-1, -1), MID_GRAY),
                ('FONTNAME', (0, nr_b - 2), (-1, -1), 'Times-Bold'),
                ('ALIGN', (0, nr_b - 2), (0, -1), 'LEFT'),
                ('ALIGN', (6, nr_b - 2), (6, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 0.6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0.6),
            ]
            t_b.setStyle(TableStyle(t_b_style))
            return t_b

        # 3 Station Area Tables
        elements.append(KeepTogether([build_bulb_station_table(st20_info, "Station 20 Transverse Area Calculation (FP - Aft Bound of Bulb)"), Spacer(1, 2.5*mm)]))
        elements.append(KeepTogether([build_bulb_station_table(stA_info, "Station A Transverse Area Calculation (Intermediate Bulb Station)"), Spacer(1, 2.5*mm)]))
        elements.append(KeepTogether([build_bulb_station_table(stB_info, "Station B Transverse Area Calculation (Fore Bulb Station)"), Spacer(1, 2.5*mm)]))

        # 4th Table: Longitudinal Integration Table (Remarks column removed, widths redistributed to 190mm)
        rows_long = [
            ["Station", "Position X (m)", "Transverse Area (m²)", "Factor", "Product A × M"]
        ]
        a20 = st20_info.get("total_area", 0.0)
        aA  = stA_info.get("total_area", 0.0)
        aB  = stB_info.get("total_area", 0.0)

        rows_long.append(["Station 20", "0.000", f"{a20:.3f}", "1", f"{a20 * 1:.3f}"])
        rows_long.append(["Station A",  "1.500", f"{aA:.3f}",  "4", f"{aA * 4:.3f}"])
        rows_long.append(["Station B",  "3.000", f"{aB:.3f}",  "1", f"{aB * 1:.3f}"])

        mA = bulb_data.get("method_A", {})
        sum_p = mA.get("body_sum", 0)
        dx_val = mA.get("dx_body", 1.500)
        body_v = mA.get("body_volume", 0)
        nose_v = mA.get("nose_volume", 0)
        tot_v = mA.get("total_volume", 0)
        ton_val = mA.get("tonnage", 0)

        rows_long.append(["Sum of Products: Σ = Station 20 to Station B", "", "", "", f"{sum_p:.3f}"])
        rows_long.append([f"Main Bulb Body Volume: V_body = (dx / 3) × Σ = ({dx_val:.2f} / 3) × {sum_p:.3f}", "", "", "", f"{body_v:.3f} m³"])
        rows_long.append([f"Forward Nose Cap Volume: V_nose = (π / 6) × A_B × L_nose", "", "", "", f"{nose_v:.3f} m³"])
        rows_long.append([f"Total Bulbous Bow Volume: V_bulb = V_body + V_nose", "", "", "", f"{tot_v:.3f} m³"])
        rows_long.append([f"Bulbous Bow Suez Moorsom Tonnage: T_bulb = V_bulb / 2.832", "", "", "", f"{ton_val:.2f} Suez Tons"])

        n_long = len(rows_long)
        t_long = Table(rows_long, colWidths=[35*mm, 35*mm, 40*mm, 25*mm, 55*mm])
        t_long_style = [
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('BACKGROUND', (0, 0), (-1, 0), BLACK),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6.8),
            ('TOPPADDING', (0, 0), (-1, -1), 1.0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.0),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
            ('ROWBACKGROUNDS', (0, 1), (-1, n_long - 6), [WHITE, LIGHT_GRAY]),
        ]
        for r_idx in range(n_long - 5, n_long):
            t_long_style.append(('SPAN', (0, r_idx), (3, r_idx)))
            t_long_style.append(('ALIGN', (0, r_idx), (0, r_idx), 'LEFT'))
            t_long_style.append(('FONTNAME', (0, r_idx), (-1, r_idx), 'Times-Bold'))
            t_long_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), MID_GRAY))
            t_long_style.append(('ALIGN', (4, r_idx), (4, r_idx), 'RIGHT'))

        t_long.setStyle(TableStyle(t_long_style))
        elements.append(KeepTogether([t_long, Spacer(1, 4*mm)]))

    # =========================================================================
    # SECTION 4: FORECASTLE TONNAGE CALCULATION (If enabled)
    # =========================================================================
    if has_fc and forecastle_data:
        elements.append(Paragraph("Forecastle Tonnage Calculation", title_style))
        fc_headers = ["No.", "Station", "Station Type", "Position X (m)", "Half-B y (m)", "Full B (m)", "Height H (m)", "Area A (m²)", "Factor", "Product A × M"]
        fc_rows = [fc_headers]
        for idx, r in enumerate(forecastle_data.get("rows", []), start=1):
            fc_rows.append([
                str(idx),
                r.get("station", ""),
                r.get("station_type", ""),
                f"{r.get('position_x', 0):.3f}",
                f"{r.get('half_breadth_m', 0):.3f}",
                f"{r.get('breadth_m', 0):.3f}",
                f"{r.get('height_m', 0):.3f}",
                f"{r.get('area_m2', 0):.3f}",
                f"{r.get('factor', 0)}",
                f"{r.get('product', 0):.3f}"
            ])

        fc_sum = forecastle_data.get("sum_products", 0)
        fc_dx3 = forecastle_data.get("dx_over_3", 3.1017)
        fc_vol = forecastle_data.get("forecastle_volume", 0)
        fc_ton = forecastle_data.get("forecastle_tonnage", 0)

        fc_rows.append(["Sum of Products: Σ_fc = Station 18 to Station A", "", "", "", "", "", "", "", f"{fc_sum:,.3f}", ""])
        fc_rows.append([f"Forecastle Volume: V_fc = (dx / 3) × Σ_fc = {fc_dx3:.4f} × {fc_sum:,.3f}", "", "", "", "", "", "", "", f"{fc_vol:,.2f} m³", ""])
        fc_rows.append([f"Forecastle Suez Moorsom Tonnage: T_fc = V_fc / 2.832", "", "", "", "", "", "", "", f"{fc_ton:,.2f} Suez Tons", ""])

        n_fc = len(fc_rows)
        t_fc = Table(fc_rows, colWidths=[9*mm, 16*mm, 18*mm, 20*mm, 19*mm, 19*mm, 17*mm, 21*mm, 13*mm, 38*mm])
        t_fc_style = [
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('BACKGROUND', (0, 0), (-1, 0), BLACK),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6.5),
            ('TOPPADDING', (0, 0), (-1, -1), 1.0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.0),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (7, -1), 'RIGHT'),
            ('ALIGN', (9, 1), (9, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
            ('ROWBACKGROUNDS', (0, 1), (-1, n_fc - 4), [WHITE, LIGHT_GRAY]),
        ]
        for r_idx in range(n_fc - 3, n_fc):
            t_fc_style.append(('SPAN', (0, r_idx), (7, r_idx)))
            t_fc_style.append(('ALIGN', (0, r_idx), (0, r_idx), 'LEFT'))
            t_fc_style.append(('FONTNAME', (0, r_idx), (-1, r_idx), 'Times-Bold'))
            t_fc_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), MID_GRAY))
            t_fc_style.append(('SPAN', (8, r_idx), (9, r_idx)))
            t_fc_style.append(('ALIGN', (8, r_idx), (8, r_idx), 'RIGHT'))

        t_fc.setStyle(TableStyle(t_fc_style))
        elements.append(KeepTogether([t_fc, Spacer(1, 4*mm)]))

    # =========================================================================
    # SECTION 5: CARGO HATCHWAYS TONNAGE CALCULATION (If enabled)
    # =========================================================================
    if has_hatches and hatch_data:
        elements.append(Paragraph("Cargo Hatchways Tonnage Calculation", title_style))
        h_headers = ["No.", "Hatchway Description", "Length L (m)", "Breadth B (m)", "Height H (m)", "Volume V (m³)", "Tonnage (Suez Tons)"]
        h_rows = [h_headers]
        for r in hatch_data.get("rows", []):
            h_rows.append([
                str(r["no"]),
                r["name"],
                f"{r['length_m']:.3f}",
                f"{r['breadth_m']:.3f}",
                f"{r['height_m']:.3f}",
                f"{r['volume_m3']:,.3f}",
                f"{r['tonnage']:,.2f}"
            ])

        tot_h_vol = hatch_data.get("total_volume", 0.0)
        tot_h_ton = hatch_data.get("total_tonnage", 0.0)
        allow_ton = hatch_data.get("allowance_tonnage", 0.0)
        allow_vol = round(allow_ton * SUEZ_TON_M3, 2)
        exc_ton = hatch_data.get("excess_tonnage", 0.0)
        exc_vol = hatch_data.get("excess_volume", 0.0)

        h_rows.append(["Total Aggregate Hatchways: V_hatch = Σ (L × B × H)", "", "", "", "", f"{tot_h_vol:,.3f} m³", f"{tot_h_ton:,.2f} Suez Tons"])
        h_rows.append(["SCA Statutory Hatch Allowance (0.5% Gross): V_allow = 0.005 × V_Gross", "", "", "", "", f"{allow_vol:,.2f} m³", f"{allow_ton:,.2f} Suez Tons"])
        h_rows.append(["Excess Cargo Hatchways Tonnage: V_excess = max(0, V_hatch - V_allow)", "", "", "", "", f"{exc_vol:,.2f} m³", f"{exc_ton:,.2f} Suez Tons"])

        nh = len(h_rows)
        t_h = Table(h_rows, colWidths=[10*mm, 56*mm, 24*mm, 24*mm, 24*mm, 26*mm, 26*mm])
        t_h_style = [
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('BACKGROUND', (0, 0), (-1, 0), BLACK),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 1.4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.4),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (6, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
            ('ROWBACKGROUNDS', (0, 1), (-1, nh - 4), [WHITE, LIGHT_GRAY]),
        ]
        for r_idx in range(nh - 3, nh):
            t_h_style.append(('SPAN', (0, r_idx), (4, r_idx)))
            t_h_style.append(('ALIGN', (0, r_idx), (0, r_idx), 'LEFT'))
            t_h_style.append(('FONTNAME', (0, r_idx), (-1, r_idx), 'Times-Bold'))
            t_h_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), MID_GRAY))
            t_h_style.append(('ALIGN', (5, r_idx), (6, r_idx), 'RIGHT'))

        t_h.setStyle(TableStyle(t_h_style))
        elements.append(KeepTogether([t_h, Spacer(1, 4*mm)]))

    # =========================================================================
    # SECTION 6: ROUND HOUSES TONNAGE CALCULATION (If enabled)
    # =========================================================================
    if has_roundhouses and superstructure_data:
        cell_style = ParagraphStyle(
            'CellTextSuper',
            fontName='Times-Roman',
            fontSize=6.0,
            leading=7.2,
            textColor=BLACK
        )
        s_headers = ["No.", "Deck Level", "Space Description", "Qty", "Length L (m)", "Breadth B (m)", "Height H (m)", "Form k", "Volume (m³)", "Tonnage (Suez Tons)"]
        s_rows = [s_headers]
        for r in superstructure_data.get("rows", []):
            deck_txt = str(r.get("deck_level", ""))
            if len(deck_txt) > 22:
                deck_txt = deck_txt.replace("Accommodation", "Accom.").replace("Captain", "Capt.")
            s_rows.append([
                str(r["no"]),
                Paragraph(deck_txt, cell_style),
                Paragraph(str(r["space_group"]), cell_style),
                str(r.get("qty", 1)),
                f"{r['length_m']:.2f}",
                f"{r['breadth_m']:.2f}",
                f"{r['height_m']:.2f}",
                f"{r['form_factor']:.3f}",
                f"{r['volume_m3']:,.3f}",
                f"{r['tonnage']:,.2f}"
            ])

        s_rows.append(["Total Aggregate Round Houses: V_RH = Σ (Qty × L × B × H × k)", "", "", "", "", "", "", "", f"{tot_rh_vol:,.3f} m³", f"{tot_rh_ton:,.2f} Suez Tons"])
        s_rows.append(["Round Houses Suez Moorsom Tonnage: T_RH = V_RH / 2.832 (Added to Gross)", "", "", "", "", "", "", "", f"{tot_rh_vol:,.3f} m³", f"{tot_rh_ton:,.2f} Suez Tons"])

        ns_rows = len(s_rows)
        t_s = Table(s_rows, colWidths=[8*mm, 26*mm, 42*mm, 10*mm, 17*mm, 17*mm, 17*mm, 14*mm, 20*mm, 19*mm])
        t_s_style = [
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('BACKGROUND', (0, 0), (-1, 0), BLACK),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6.0),
            ('TOPPADDING', (0, 0), (-1, -1), 0.75),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.75),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ('ALIGN', (4, 1), (8, -1), 'RIGHT'),
            ('ALIGN', (9, 1), (9, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
            ('ROWBACKGROUNDS', (0, 1), (-1, ns_rows - 3), [WHITE, LIGHT_GRAY]),
        ]
        for r_idx in range(ns_rows - 2, ns_rows):
            t_s_style.append(('SPAN', (0, r_idx), (7, r_idx)))
            t_s_style.append(('ALIGN', (0, r_idx), (0, r_idx), 'LEFT'))
            t_s_style.append(('FONTNAME', (0, r_idx), (-1, r_idx), 'Times-Bold'))
            t_s_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), MID_GRAY))
            t_s_style.append(('ALIGN', (8, r_idx), (8, r_idx), 'RIGHT'))
            t_s_style.append(('ALIGN', (9, r_idx), (9, r_idx), 'RIGHT'))

        t_s.setStyle(TableStyle(t_s_style))
        elements.append(KeepTogether([Paragraph("Round Houses Tonnage Calculation", title_style), t_s, Spacer(1, 2*mm)]))

    # =========================================================================
    # SECTION 7: SUEZ CANAL GROSS TONNAGE ADDITION CALCULATION
    # =========================================================================
    th_hdr_center = ParagraphStyle(
        'TblHdrCenter',
        fontName='Times-Bold',
        fontSize=7.0,
        leading=8.8,
        alignment=1,
        textColor=WHITE
    )
    th_hdr_left = ParagraphStyle(
        'TblHdrLeft',
        fontName='Times-Bold',
        fontSize=7.0,
        leading=8.8,
        alignment=0,
        textColor=WHITE
    )

    gt_headers = [
        Paragraph("Item / Component Description", th_hdr_left),
        Paragraph("Statutory Regulation", th_hdr_center),
        Paragraph("Enclosed Volume<br/>(m&sup3;)", th_hdr_center),
        Paragraph("Suez Tonnage<br/>(Suez Tons)", th_hdr_center)
    ]
    gt_rows = [gt_headers]

    gt_rows.append([
        "Under the Tonnage Deck",
        "SCA Rules Art. 93 Para 1",
        f"{udt_vol:,.3f}",
        f"{udt_tons:,.2f}"
    ])
    gt_rows.append([
        "Bulbous Bow",
        "SCA Appendix 1",
        f"{bulb_vol:,.3f}" if has_bulb and bulb_tons > 0 else "-",
        f"{bulb_tons:,.2f}" if has_bulb and bulb_tons > 0 else "-"
    ])
    gt_rows.append([
        "Forecastle Deck",
        "SCA Rules Art. 93 Para 2",
        f"{fc_vol:,.3f}" if has_fc and fc_tons > 0 else "-",
        f"{fc_tons:,.2f}" if has_fc and fc_tons > 0 else "-"
    ])
    gt_rows.append([
        "Excess Cargo Hatchways",
        "SCA Rules Art. 93 Para 3",
        f"{hatch_exc_vol:,.3f}" if has_hatches and hatch_exc_tons > 0 else "-",
        f"{hatch_exc_tons:,.2f}" if has_hatches and hatch_exc_tons > 0 else "-"
    ])
    gt_rows.append([
        "Round Houses, etc.",
        "SCA Rules Art. 93 Para 4",
        f"{tot_rh_vol:,.3f}" if has_roundhouses and tot_rh_ton > 0 else "-",
        f"{tot_rh_ton:,.2f}" if has_roundhouses and tot_rh_ton > 0 else "-"
    ])
    gt_rows.append([
        "TOTAL SUEZ CANAL GROSS TONNAGE",
        "SCA Certificate Gross",
        f"{gross_vol:,.3f}",
        f"{gross_tonnage:,.2f}"
    ])

    ngt = len(gt_rows)
    t_gt = Table(gt_rows, colWidths=[65*mm, 45*mm, 40*mm, 40*mm])
    t_gt_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('BACKGROUND', (0, 0), (-1, 0), BLACK),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.0),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
        ('ROWBACKGROUNDS', (0, 1), (-1, ngt - 2), [WHITE, LIGHT_GRAY]),
        ('BACKGROUND', (0, ngt - 1), (-1, ngt - 1), MID_GRAY),
        ('FONTNAME', (0, ngt - 1), (-1, ngt - 1), 'Times-Bold'),
    ]
    t_gt.setStyle(TableStyle(t_gt_style))

    # =========================================================================
    # SECTION 8: SUEZ CANAL NET TONNAGE DEDUCTION CALCULATION
    # =========================================================================
    nt_headers = [
        Paragraph("Statutory Deduction Space", th_hdr_left),
        Paragraph("SCA Statutory Regulation", th_hdr_center),
        Paragraph("Deducted Volume<br/>(m&sup3;)", th_hdr_center),
        Paragraph("Deducted Tonnage<br/>(Suez Tons)", th_hdr_center)
    ]
    nt_rows = [nt_headers]

    nt_rows.append([
        "Officer's Accommodation",
        "SCA Rules Art. 94 Para 1",
        f"{off_v:,.3f}" if off_acc_ton > 0 else "-",
        f"{off_acc_ton:,.2f}" if off_acc_ton > 0 else "-"
    ])
    nt_rows.append([
        "Crew's Accommodation",
        "SCA Rules Art. 94 Para 1",
        f"{crew_v:,.3f}" if crew_acc_ton > 0 else "-",
        f"{crew_acc_ton:,.2f}" if crew_acc_ton > 0 else "-"
    ])
    nt_rows.append([
        "Spaces Used in Working the Ship",
        "SCA Rules Art. 94 Para 2",
        f"{work_v:,.3f}" if work_ship_ton > 0 else "-",
        f"{work_ship_ton:,.2f}" if work_ship_ton > 0 else "-"
    ])
    nt_rows.append([
        "Deduction for Propelling Power",
        "SCA Rules Art. 94 Para 3",
        f"{prop_v:,.3f}" if prop_power_ton > 0 else "-",
        f"{prop_power_ton:,.2f}" if prop_power_ton > 0 else "-"
    ])
    nt_rows.append([
        "TOTAL STATUTORY DEDUCTIONS",
        "SCA Art. 94 Summary",
        f"{tot_d_v:,.3f}" if tot_ded_ton > 0 else "-",
        f"{tot_ded_ton:,.2f}"
    ])
    nt_rows.append([
        "SUEZ CANAL NET TONNAGE",
        "SCA Certificate Net",
        "-",
        f"{net_tonnage:,.2f}"
    ])

    nnt = len(nt_rows)
    t_nt = Table(nt_rows, colWidths=[65*mm, 45*mm, 40*mm, 40*mm])
    t_nt_style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('BACKGROUND', (0, 0), (-1, 0), BLACK),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.0),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_BLACK),
        ('ROWBACKGROUNDS', (0, 1), (-1, nnt - 3), [WHITE, LIGHT_GRAY]),
        ('BACKGROUND', (0, nnt - 2), (-1, nnt - 1), MID_GRAY),
        ('FONTNAME', (0, nnt - 2), (-1, nnt - 1), 'Times-Bold'),
    ]
    t_nt.setStyle(TableStyle(t_nt_style))

    # Keep Gross and Net summary tables together
    elements.append(KeepTogether([
        Paragraph("Suez Canal Gross Tonnage Addition Calculation", title_style),
        t_gt,
        Spacer(1, 4*mm),
        Paragraph("Suez Canal Net Tonnage Deduction Calculation", title_style),
        t_nt
    ]))

    doc.build(elements)
    return output_pdf_path

def generate_html_table_report(output_html_path, udt_data, bulb_data, vessel_info, forecastle_data=None, hatch_data=None, superstructure_data=None):
    """
    Builds a standalone printable HTML report replicating the official Certificate Cover Page format.
    Structured cleanly into the 8 official calculation sections.
    """
    udt_data = udt_data or {}
    v_name = vessel_info.get("vessel_name", "PATRONUS")
    nationality = vessel_info.get("nationality", "BAHAMAS")
    kind_of_ship = vessel_info.get("kind_of_ship", "BULK CARRIER")
    official_num = vessel_info.get("official_number", "7000085")
    signal_letters = vessel_info.get("signal_letters", "C6R 2092")
    port_registry = vessel_info.get("port_of_registry", "NASSAU")
    keel_date = vessel_info.get("keel_laying_date", "7 JUNE 2006")
    built_where = vessel_info.get("built_where", "COCHIN, INDIA")
    material_hull = vessel_info.get("material_of_hull", "STEEL")
    builder = vessel_info.get("builder", "COCHIN SHIPYARD LTD")
    engine = vessel_info.get("engine_type", "DIESEL ENGINE : ONE")
    launch_date = vessel_info.get("date_of_launch", "")
    propellers = vessel_info.get("propellers", "SCREW PROPELLER : ONE")
    hull_note = vessel_info.get("hull_note", "CSL HULL NO. 017")

    lbp = float(vessel_info.get("lbp", 170.872) or 170.872)
    b_mld = float(vessel_info.get("breadth", 28.00) or 28.00)
    d_mld = float(vessel_info.get("depth", 14.00) or 14.00)

    has_bulb = vessel_info.get("has_bulbous", True) if "has_bulbous" in vessel_info else (bulb_data.get("has_bulbous", True) if bulb_data else False)
    has_fc = vessel_info.get("has_forecastle", True)
    has_hatches = vessel_info.get("has_hatches", True)
    has_roundhouses = vessel_info.get("has_roundhouses", True)

    udt_vol = float(udt_data.get("total_underdeck_volume", 0.0) or 0.0)
    udt_tons = float(udt_data.get("underdeck_tonnage", 0.0) or 0.0)

    if has_bulb and bulb_data:
        bulb_vol = float(bulb_data.get("method_A", {}).get("total_volume", 0.0) or 0.0)
        bulb_tons = float(bulb_data.get("method_A", {}).get("tonnage", 0.0) or 0.0)
    else:
        bulb_vol = 0.0
        bulb_tons = 0.0

    if has_fc and forecastle_data:
        fc_vol = float(forecastle_data.get("forecastle_volume", 0.0) or 0.0)
        fc_tons = float(forecastle_data.get("forecastle_tonnage", 0.0) or 0.0)
    else:
        fc_vol = 0.0
        fc_tons = 0.0

    if has_hatches and hatch_data:
        hatch_exc_vol = float(hatch_data.get("excess_volume", 0.0) or 0.0)
        hatch_exc_tons = float(hatch_data.get("excess_tonnage", 0.0) or 0.0)
    else:
        hatch_exc_vol = 0.0
        hatch_exc_tons = 0.0

    if has_roundhouses and superstructure_data:
        tot_rh_vol = float(superstructure_data.get("round_houses_volume", 0.0) or 0.0)
        tot_rh_ton = float(superstructure_data.get("round_houses_tonnage", 0.0) or 0.0)
        off_v = float(superstructure_data.get("officer_accommodation_volume", 0.0) or 0.0)
        off_acc_ton = float(superstructure_data.get("officer_accommodation_tonnage", 0.0) or 0.0)
        crew_v = float(superstructure_data.get("crew_accommodation_volume", 0.0) or 0.0)
        crew_acc_ton = float(superstructure_data.get("crew_accommodation_tonnage", 0.0) or 0.0)
        work_v = float(superstructure_data.get("working_ship_volume", 0.0) or 0.0)
        work_ship_ton = float(superstructure_data.get("working_ship_tonnage", 0.0) or 0.0)
        prop_v = float(superstructure_data.get("propelling_power_volume", 0.0) or 0.0)
        prop_power_ton = float(superstructure_data.get("propelling_power_tonnage", 0.0) or 0.0)
        tot_d_v = float(superstructure_data.get("total_deduction_volume", 0.0) or 0.0)
        tot_ded_ton = float(superstructure_data.get("total_deduction_tonnage", 0.0) or 0.0)
    else:
        tot_rh_vol = 0.0
        tot_rh_ton = 0.0
        off_v = 0.0
        off_acc_ton = 0.0
        crew_v = 0.0
        crew_acc_ton = 0.0
        work_v = 0.0
        work_ship_ton = 0.0
        prop_v = 0.0
        prop_power_ton = 0.0
        tot_d_v = 0.0
        tot_ded_ton = 0.0

    bulb_cover_tons = bulb_tons if (has_bulb and bulb_tons > 0) else 0.0
    fc_cover_tons = fc_tons if (has_fc and fc_tons > 0) else 0.0
    rh_cover_tons = tot_rh_ton if (has_roundhouses and tot_rh_ton > 0) else 0.0
    hatch_cover_tons = hatch_exc_tons if (has_hatches and hatch_exc_tons > 0) else 0.0

    gross_tonnage = udt_tons + bulb_cover_tons + fc_cover_tons + rh_cover_tons + hatch_cover_tons
    net_tonnage = max(0.0, gross_tonnage - tot_ded_ton)
    gross_vol = udt_vol + bulb_vol + fc_vol + tot_rh_vol + hatch_exc_vol
    net_vol = max(0.0, gross_vol - tot_d_v)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Suez Canal Tonnage Measurement - {v_name}</title>
<style>
{REPORT_HTML_CSS}
</style>
</head>
<body>

<!-- SECTION 1: CERTIFICATE COVER PAGE -->
<div class="cert-header">
  CALCULATION SHEETS<br/>
  FOR<br/>
  SUEZ CANAL TONNAGE MEASUREMENT
</div>

<table class="three-col-header">
  <tr>
    <td style="width: 33%;"><div class="underlined">{nationality}</div><div class="sublabel">NATIONALITY</div></td>
    <td style="width: 34%;"><div class="underlined">{kind_of_ship}</div><div class="sublabel">KIND OF SHIP</div></td>
    <td style="width: 33%;"><div class="underlined">"{v_name}"</div><div class="sublabel">NAME OF SHIP</div></td>
  </tr>
</table>

<table>
  <tr class="sub-hdr">
    <th>OFFICIAL NUMBER</th><th>SIGNAL LETTERS</th><th>PORT OF REGISTRY</th><th>KEEL LAYING DATE</th>
  </tr>
  <tr class="text-center font-bold">
    <td>{official_num}</td><td>{signal_letters}</td><td>{port_registry}</td><td>{keel_date}</td>
  </tr>
  <tr>
    <td colspan="2"><strong>BUILT WHERE:</strong> {built_where}</td>
    <td colspan="2"><strong>MATERIAL OF HULL:</strong> {material_hull}</td>
  </tr>
  <tr>
    <td colspan="2"><strong>NAME OF BUILDER:</strong> {builder}</td>
    <td colspan="2"><strong>TYPE AND NUMBER OF ENGINE:</strong> {engine}</td>
  </tr>
  <tr>
    <td colspan="2"><strong>DATE OF LAUNCH:</strong> {launch_date}</td>
    <td colspan="2"><strong>KIND AND NUMBER OF PROPELLERS:</strong> {propellers}</td>
  </tr>
</table>

<table>
  <tr class="sub-hdr">
    <th colspan="3">MAIN DIMENSIONS</th>
  </tr>
  <tr>
    <td style="width: 50%;" class="text-center"><strong>LENGTH</strong></td>
    <td style="width: 40%;" class="text-right"><strong>{lbp:.3f}</strong></td>
    <td style="width: 10%;">M</td>
  </tr>
  <tr>
    <td class="text-center"><strong>BREADTH</strong></td>
    <td class="text-right"><strong>{b_mld:.2f}</strong></td>
    <td>M</td>
  </tr>
  <tr>
    <td class="text-center"><strong>DEPTH</strong></td>
    <td class="text-right"><strong>{d_mld:.2f}</strong></td>
    <td>M</td>
  </tr>
</table>

<table>
  <tr class="highlight">
    <th style="width: 25%; text-align: left; background: #e0e0e0; color: #000;">GROSS TONNAGE</th>
    <th style="width: 25%; text-align: right; background: #e0e0e0; color: #000;">{gross_tonnage:,.2f}</th>
    <th style="width: 25%; text-align: left; background: #e0e0e0; color: #000;">NET TONNAGE</th>
    <th style="width: 25%; text-align: right; background: #e0e0e0; color: #000;">{net_tonnage:,.2f}</th>
  </tr>
  <tr>
    <td>UNDER THE TONNAGE DECK</td>
    <td class="text-right">{udt_tons:,.2f}</td>
    <td colspan="2"><strong>DEDUCTED SPACES :</strong></td>
  </tr>
  <tr>
    <td>BULBOUS BOW</td>
    <td class="text-right">{f"{bulb_cover_tons:,.2f}" if bulb_cover_tons > 0 else "-"}</td>
    <td>OFFICER'S ACCOMMODATION</td>
    <td class="text-right">{f"{off_acc_ton:,.2f}" if off_acc_ton > 0 else "-"}</td>
  </tr>
  <tr>
    <td>FORECASTLE DECK</td>
    <td class="text-right">{f"{fc_cover_tons:,.2f}" if fc_cover_tons > 0 else "-"}</td>
    <td>CREW'S ACCOMMODATION</td>
    <td class="text-right">{f"{crew_acc_ton:,.2f}" if crew_acc_ton > 0 else "-"}</td>
  </tr>
  <tr>
    <td>ROUND HOUSES, ETC.</td>
    <td class="text-right">{f"{rh_cover_tons:,.2f}" if rh_cover_tons > 0 else "-"}</td>
    <td>USED IN WORKING THE SHIP</td>
    <td class="text-right">{f"{work_ship_ton:,.2f}" if work_ship_ton > 0 else "-"}</td>
  </tr>
  <tr>
    <td>HATCH WAYS</td>
    <td class="text-right">{f"{hatch_cover_tons:,.2f}" if hatch_cover_tons > 0 else "-"}</td>
    <td>DEDUCTION FOR PROPELLING POWER</td>
    <td class="text-right">{f"{prop_power_ton:,.2f}" if prop_power_ton > 0 else "-"}</td>
  </tr>
  <tr class="highlight">
    <td>&nbsp;</td><td></td>
    <td><strong>TOTAL DEDUCTIONS</strong></td>
    <td class="text-right"><strong>{tot_ded_ton:,.2f}</strong></td>
  </tr>
</table>

<div class="note-box">
  <div class="note-title-cell">
    NOTE<br/>&amp;<br/>CALCULATION<br/>DETAIL
  </div>
  <div class="note-content-cell">
    <p><strong>SHIP RECORD:</strong> {hull_note} &nbsp;&nbsp;|&nbsp;&nbsp; <strong>REGULATORY STANDARD:</strong> <em>Suez Canal Authority (SCA) Rules of Navigation (Arts. 92&ndash;94 &amp; Appendix 1)</em> &nbsp;&nbsp;|&nbsp;&nbsp; <strong>UNIT:</strong> 1 Suez Moorsom Ton = 100 cu.ft = <strong>2.832 m&sup3;</strong></p>
    <p><strong>1. MEASUREMENT PROCEDURES EXECUTED (WHAT WAS DONE):</strong><br/>
    &bull; <strong>Under Deck Tonnage (UDT):</strong> Computed via Simpson's 1st Rule over 21 transverse stations (dx = LBP / 20) with 16 vertical intervals per station (h = D / 16). Transom appendix volume aft of AP included.<br/>
    &bull; <strong>Appendages &amp; Enclosed Superstructures:</strong> Bulbous bow calculated per SCA Method A (transverse cuts at St. 20, A, B and forward conical nose cap V<sub>nose</sub> = (&pi;/6)&times;A<sub>B</sub>&times;L<sub>nose</sub>). Forecastle deck integrated from transverse offsets. Cargo hatchways excess calculated applying 0.5% (5&permil;) Gross Tonnage statutory allowance. Round houses enclosed spaces schedule aggregated.<br/>
    &bull; <strong>Gross &amp; Net Tonnage:</strong> Gross Tonnage obtained by summing UDT and all additions; Net Tonnage obtained by deducting statutory spaces (Officers, Crew, Navigation, and Propelling Power capped at &le; 50% GT).</p>
    <p><strong>2. SUMMARY OF CALCULATED VALUES &amp; TONNAGES (WHAT WAS OBTAINED):</strong><br/>
    &bull; <strong>Under Deck Tonnage (UDT):</strong> Volume = <strong>{udt_vol:,.2f} m&sup3;</strong> &nbsp;&rArr;&nbsp; Tonnage = <strong>{udt_tons:,.2f} Suez Tons</strong><br/>
    &bull; <strong>Bulbous Bow:</strong> Volume = <strong>{bulb_vol:,.2f} m&sup3;</strong> &nbsp;&rArr;&nbsp; Tonnage = <strong>{bulb_cover_tons:,.2f} Suez Tons</strong><br/>
    &bull; <strong>Forecastle Deck:</strong> Volume = <strong>{fc_vol:,.2f} m&sup3;</strong> &nbsp;&rArr;&nbsp; Tonnage = <strong>{fc_cover_tons:,.2f} Suez Tons</strong><br/>
    &bull; <strong>Cargo Hatchways Excess:</strong> Volume = <strong>{hatch_exc_vol:,.2f} m&sup3;</strong> &nbsp;&rArr;&nbsp; Tonnage = <strong>{hatch_cover_tons:,.2f} Suez Tons</strong><br/>
    &bull; <strong>Round Houses / Deckhouses:</strong> Volume = <strong>{tot_rh_vol:,.2f} m&sup3;</strong> &nbsp;&rArr;&nbsp; Tonnage = <strong>{rh_cover_tons:,.2f} Suez Tons</strong><br/>
    &bull; <strong>TOTAL SUEZ CANAL GROSS TONNAGE (GT):</strong> Volume = <strong>{gross_vol:,.2f} m&sup3;</strong> &nbsp;&rArr;&nbsp; <strong>Gross Tonnage = {gross_tonnage:,.2f} Suez Tons</strong><br/>
    &bull; <strong>TOTAL STATUTORY DEDUCTIONS:</strong> Deducted Volume = <strong>{tot_d_v:,.2f} m&sup3;</strong> &nbsp;&rArr;&nbsp; <strong>Total Deductions = {tot_ded_ton:,.2f} Suez Tons</strong><br/>
    &bull; <strong>FINAL SUEZ CANAL NET TONNAGE (NT):</strong> Net Volume = <strong>{net_vol:,.2f} m&sup3;</strong> &nbsp;&rArr;&nbsp; <strong>Net Tonnage = {net_tonnage:,.2f} Suez Tons</strong></p>
  </div>
</div>

<div class="page-break"></div>

<!-- SECTION 2: UNDERDECK SUEZ TONNAGE CALCULATION -->
<h2>Underdeck Suez Tonnage Calculation</h2>
<h3>Under the Tonnage Deck Volume Calculation</h3>
<table>
  <tr>
    <th>STATION</th><th>NAME</th><th>POSITION X (m)</th><th>DEPTH D (m)</th><th>AREA (m&sup2;)</th><th>FACTOR</th><th>PRODUCT A &times; M</th>
  </tr>
"""
    for r in udt_data.get("long_rows", []):
        html += f"""  <tr class="alt-row">
    <td class="text-center">{r['station_num']}</td><td>{r['station_name']}</td><td class="text-right">{r['position_x']:.3f}</td>
    <td class="text-right">{r['depth_m']:.3f}</td><td class="text-right">{r['area_m2']:,.2f}</td><td class="text-center">{r['factor']}</td>
    <td class="text-right">{r['product']:,.2f}</td>
  </tr>\n"""

    sum_p = udt_data.get('main_hull_sum_products', 0)
    dx3_val = udt_data.get('dx_over_3', 3.1017)
    mh_v = udt_data.get('main_hull_volume', 0)
    tr_v = udt_data.get('transom_volume', 0)
    tot_v = udt_data.get('total_underdeck_volume', 0)
    udt_t = udt_data.get('underdeck_tonnage', 0)

    html += f"""  <tr class="highlight">
    <td colspan="6" class="text-left"><strong>Sum of Products: &Sigma; = Station 0 to Station 20</strong></td>
    <td class="text-right"><strong>{sum_p:,.2f}</strong></td>
  </tr>
  <tr>
    <td colspan="6" class="text-left">Main Hull Volume: V_hull = (dx / 3) &times; &Sigma; = {dx3_val:.4f} &times; {sum_p:,.2f}</td>
    <td class="text-right"><strong>{mh_v:,.2f} m&sup3;</strong></td>
  </tr>
  <tr>
    <td colspan="6" class="text-left">Transom Appendix Volume: V_transom (Aft of AP to St. 0)</td>
    <td class="text-right"><strong>{tr_v:,.2f} m&sup3;</strong></td>
  </tr>
  <tr class="highlight">
    <td colspan="6" class="text-left"><strong>Total Under Deck Volume: V_UDT = V_hull + V_transom</strong></td>
    <td class="text-right"><strong>{tot_v:,.2f} m&sup3;</strong></td>
  </tr>
  <tr class="highlight">
    <td colspan="6" class="text-left"><strong>Under Deck Suez Moorsom Tonnage: UDT = V_UDT / 2.832</strong></td>
    <td class="text-right"><strong>{udt_t:,.2f} Suez Tons</strong></td>
  </tr>
</table>

<h3>Calculation of Transverse Station Areas</h3>
<div class="station-container">
"""
    transverse_tables = udt_data.get("station_results") or udt_data.get("transverse_tables", {})
    for st_key, st_data in transverse_tables.items():
        st_name = st_data.get("station_name", str(st_key))
        depth_val = st_data.get("depth_m", st_data.get("depth", 17.80))
        h_val = st_data.get("h_m", st_data.get("h", depth_val / 16.0))
        h3_val = st_data.get("h_over_3", h_val / 3.0)
        sum_p = st_data.get("sum_products", 0.0)
        tot_a = st_data.get("area_m2", st_data.get("total_area", 0.0))
        pts = st_data.get("rows") or st_data.get("points", [])

        html += f"""  <div class="station-box">
    <table>
      <tr><th colspan="7">Station {st_name}</th></tr>
      <tr class="sub-hdr"><td colspan="3">Depth D: {depth_val:.3f} m</td><td colspan="4">1/3 h: {h3_val:.4f} m</td></tr>
      <tr><th>Pt</th><th>Waterline</th><th>Height Z (m)</th><th>Half-B (m)</th><th>Breadth (m)</th><th>Factor</th><th>Product</th></tr>
"""
        for pt in pts:
            pt_no = pt.get("point", pt.get("pt", ""))
            wl_name = pt.get("waterline", pt.get("wl", ""))
            z_val = pt.get("waterline_height_m", pt.get("z", 0.0))
            half_b = pt.get("half_breadth_m", pt.get("half_b", 0.0))
            full_b = pt.get("breadth_m", pt.get("breadth", 0.0))
            factor = pt.get("factor", 1)
            product = pt.get("product", 0.0)
            html += f"""      <tr class="alt-row"><td class="text-center">{pt_no}</td><td>{wl_name}</td><td class="text-right">{z_val:.3f}</td><td class="text-right">{half_b:.3f}</td><td class="text-right">{full_b:.3f}</td><td class="text-center">{factor}</td><td class="text-right">{product:.3f}</td></tr>\n"""

        html += f"""      <tr class="highlight"><td colspan="6">Sum of Products: &Sigma; = &Sigma; (Breadth &times; Factor)</td><td class="text-right"><strong>{sum_p:.3f}</strong></td></tr>
      <tr class="highlight"><td colspan="6">Station Area: A_i = (h_i / 3) &times; &Sigma;</td><td class="text-right"><strong>{tot_a:.2f} m&sup2;</strong></td></tr>
    </table>
  </div>\n"""

    html += "</div>\n"

    # SECTION 3: BULBOUS BOW (HTML)
    if has_bulb and bulb_data:
        html += """<h2>Bulbous Bow Tonnage Calculation &mdash; Method A</h2>\n"""
        trans_stations = bulb_data.get("transverse_stations") or bulb_data.get("areas") or {}
        st20_info = trans_stations.get("St_20") or trans_stations.get("st20") or {}
        stA_info  = trans_stations.get("St_A")  or trans_stations.get("stA")  or {}
        stB_info  = trans_stations.get("St_B")  or trans_stations.get("stB")  or {}

        def build_html_bulb_st(st_info, st_title):
            h_out = f"""  <div class="station-box">
    <table>
      <tr><th colspan="7">{st_title}</th></tr>
      <tr><th>Buttock Line</th><th>Half-Breadth Y (m)</th><th>Upper Z (m)</th><th>Lower Z (m)</th><th>Depth D (m)</th><th>Factor</th><th>Product</th></tr>\n"""
            for pt in (st_info.get("rows") or st_info.get("points") or []):
                h_out += f"""      <tr class="alt-row"><td>{pt.get('name','')}</td><td class="text-right">{pt.get('y_m',0.0):.3f}</td><td class="text-right">{pt.get('z_upper',0.0):.3f}</td><td class="text-right">{pt.get('z_lower',0.0):.3f}</td><td class="text-right">{pt.get('depth_m',0.0):.3f}</td><td class="text-center">{pt.get('factor',1)}</td><td class="text-right">{pt.get('product',0.0):.3f}</td></tr>\n"""
            sp = st_info.get("sum_prod", 0.0)
            area_val = st_info.get("total_area", 0.0)
            h_out += f"""      <tr class="highlight"><td colspan="6">Sum of Products: &Sigma;</td><td class="text-right"><strong>{sp:.3f}</strong></td></tr>
      <tr class="highlight"><td colspan="6">Transverse Area: A_bulb</td><td class="text-right"><strong>{area_val:.3f} m&sup2;</strong></td></tr>
    </table>
  </div>\n"""
            return h_out

        html += build_html_bulb_st(st20_info, "Station 20 Transverse Area (Aft Bound of Bulb)")
        html += build_html_bulb_st(stA_info,  "Station A Transverse Area (Intermediate Station)")
        html += build_html_bulb_st(stB_info,  "Station B Transverse Area (Fore Station)")

        # Longitudinal Bulb Table
        mA = bulb_data.get("method_A", {})
        a20 = st20_info.get("total_area", 0.0)
        aA  = stA_info.get("total_area", 0.0)
        aB  = stB_info.get("total_area", 0.0)
        sum_p = mA.get("body_sum", 0)
        body_v = mA.get("body_volume", 0)
        nose_v = mA.get("nose_volume", 0)
        tot_v = mA.get("total_volume", 0)
        ton_val = mA.get("tonnage", 0)

        html += f"""  <table>
    <tr><th>STATION</th><th>POSITION X (m)</th><th>TRANSVERSE AREA (m&sup2;)</th><th>FACTOR</th><th>PRODUCT A &times; M</th></tr>
    <tr><td class="text-center">Station 20</td><td class="text-right">0.000</td><td class="text-right">{a20:.3f}</td><td class="text-center">1</td><td class="text-right">{a20*1:.3f}</td></tr>
    <tr><td class="text-center">Station A</td><td class="text-right">1.500</td><td class="text-right">{aA:.3f}</td><td class="text-center">4</td><td class="text-right">{aA*4:.3f}</td></tr>
    <tr><td class="text-center">Station B</td><td class="text-right">3.000</td><td class="text-right">{aB:.3f}</td><td class="text-center">1</td><td class="text-right">{aB*1:.3f}</td></tr>
    <tr class="highlight"><td colspan="4">Sum of Products: &Sigma; = Station 20 to Station B</td><td class="text-right"><strong>{sum_p:.3f}</strong></td></tr>
    <tr><td colspan="4">Main Bulb Body Volume: V_body</td><td class="text-right"><strong>{body_v:.3f} m&sup3;</strong></td></tr>
    <tr><td colspan="4">Forward Nose Cap Volume: V_nose = (&pi; / 6) &times; A_B &times; L_nose</td><td class="text-right"><strong>{nose_v:.3f} m&sup3;</strong></td></tr>
    <tr class="highlight"><td colspan="4"><strong>Total Bulbous Bow Volume: V_bulb = V_body + V_nose</strong></td><td class="text-right"><strong>{tot_v:.3f} m&sup3;</strong></td></tr>
    <tr class="highlight"><td colspan="4"><strong>Bulbous Bow Suez Moorsom Tonnage: T_bulb = V_bulb / 2.832</strong></td><td class="text-right"><strong>{ton_val:.2f} Suez Tons</strong></td></tr>
  </table>\n"""

    # SECTION 4: FORECASTLE (HTML)
    if has_fc and forecastle_data:
        html += """<h2>Forecastle Tonnage Calculation</h2>
<table>
  <tr><th>No.</th><th>STATION</th><th>TYPE</th><th>POSITION X (m)</th><th>HALF-B y (m)</th><th>FULL B (m)</th><th>HEIGHT H (m)</th><th>AREA (m&sup2;)</th><th>FACTOR</th><th>PRODUCT</th></tr>\n"""
        for idx, r in enumerate(forecastle_data.get("rows", []), start=1):
            html += f"""  <tr class="alt-row"><td class="text-center">{idx}</td><td>{r.get('station','')}</td><td>{r.get('station_type','')}</td><td class="text-right">{r.get('position_x',0):.3f}</td><td class="text-right">{r.get('half_breadth_m',0):.3f}</td><td class="text-right">{r.get('breadth_m',0):.3f}</td><td class="text-right">{r.get('height_m',0):.3f}</td><td class="text-right">{r.get('area_m2',0):.3f}</td><td class="text-center">{r.get('factor',0)}</td><td class="text-right">{r.get('product',0):.3f}</td></tr>\n"""
        fc_sum = forecastle_data.get("sum_products", 0)
        fc_vol = forecastle_data.get("forecastle_volume", 0)
        fc_ton = forecastle_data.get("forecastle_tonnage", 0)
        html += f"""  <tr class="highlight"><td colspan="8">Sum of Products: &Sigma;_fc</td><td colspan="2" class="text-right"><strong>{fc_sum:,.3f}</strong></td></tr>
  <tr><td colspan="8">Forecastle Volume: V_fc</td><td colspan="2" class="text-right"><strong>{fc_vol:,.2f} m&sup3;</strong></td></tr>
  <tr class="highlight"><td colspan="8"><strong>Forecastle Suez Moorsom Tonnage: T_fc = V_fc / 2.832</strong></td><td colspan="2" class="text-right"><strong>{fc_ton:,.2f} Suez Tons</strong></td></tr>
</table>\n"""

    # SECTION 5: HATCHWAYS (HTML)
    if has_hatches and hatch_data:
        html += """<h2>Cargo Hatchways Tonnage Calculation</h2>
<table>
  <tr><th>No.</th><th>HATCHWAY DESCRIPTION</th><th>LENGTH L (m)</th><th>BREADTH B (m)</th><th>HEIGHT H (m)</th><th>VOLUME V (m&sup3;)</th><th>TONNAGE (Suez Tons)</th></tr>\n"""
        for r in hatch_data.get("rows", []):
            html += f"""  <tr class="alt-row"><td class="text-center">{r['no']}</td><td>{r['name']}</td><td class="text-right">{r['length_m']:.3f}</td><td class="text-right">{r['breadth_m']:.3f}</td><td class="text-right">{r['height_m']:.3f}</td><td class="text-right">{r['volume_m3']:,.3f}</td><td class="text-right">{r['tonnage']:,.2f}</td></tr>\n"""
        tot_h_vol = hatch_data.get("total_volume", 0.0)
        tot_h_ton = hatch_data.get("total_tonnage", 0.0)
        allow_ton = hatch_data.get("allowance_tonnage", 0.0)
        allow_vol = round(allow_ton * SUEZ_TON_M3, 2)
        exc_ton = hatch_data.get("excess_tonnage", 0.0)
        exc_vol = hatch_data.get("excess_volume", 0.0)
        html += f"""  <tr class="highlight"><td colspan="5">Total Aggregate Hatchways: V_hatch</td><td class="text-right"><strong>{tot_h_vol:,.3f} m&sup3;</strong></td><td class="text-right"><strong>{tot_h_ton:,.2f} Suez Tons</strong></td></tr>
  <tr><td colspan="5">SCA Statutory Hatch Allowance (0.5% Gross): V_allow</td><td class="text-right"><strong>{allow_vol:,.2f} m&sup3;</strong></td><td class="text-right"><strong>{allow_ton:,.2f} Suez Tons</strong></td></tr>
  <tr class="highlight"><td colspan="5"><strong>Excess Cargo Hatchways Tonnage: V_excess</strong></td><td class="text-right"><strong>{exc_vol:,.2f} m&sup3;</strong></td><td class="text-right"><strong>{exc_ton:,.2f} Suez Tons</strong></td></tr>
</table>\n"""

    # SECTION 6: ROUND HOUSES (HTML)
    if has_roundhouses and superstructure_data:
        html += """<h2>Round Houses Tonnage Calculation</h2>
<table>
  <tr><th>No.</th><th>DECK LEVEL</th><th>SPACE DESCRIPTION</th><th>QTY</th><th>LENGTH L (m)</th><th>BREADTH B (m)</th><th>HEIGHT H (m)</th><th>FORM k</th><th>VOLUME (m&sup3;)</th><th>TONNAGE (Suez Tons)</th></tr>\n"""
        for r in superstructure_data.get("rows", []):
            html += f"""  <tr class="alt-row"><td class="text-center">{r['no']}</td><td>{r.get('deck_level','')}</td><td>{r.get('space_group','')}</td><td class="text-center">{r.get('qty',1)}</td><td class="text-right">{r['length_m']:.2f}</td><td class="text-right">{r['breadth_m']:.2f}</td><td class="text-right">{r['height_m']:.2f}</td><td class="text-right">{r['form_factor']:.3f}</td><td class="text-right">{r['volume_m3']:,.3f}</td><td class="text-right">{r['tonnage']:,.2f}</td></tr>\n"""
        html += f"""  <tr class="highlight"><td colspan="8">Total Aggregate Round Houses: V_RH</td><td class="text-right"><strong>{tot_rh_vol:,.3f} m&sup3;</strong></td><td class="text-right"><strong>{tot_rh_ton:,.2f} Suez Tons</strong></td></tr>
</table>\n"""

    # SECTION 7: GROSS TONNAGE (HTML - 4 columns)
    html += f"""<h2>Suez Canal Gross Tonnage Addition Calculation</h2>
<table>
  <tr><th>ITEM / COMPONENT DESCRIPTION</th><th>STATUTORY REGULATION</th><th>ENCLOSED VOLUME (m&sup3;)</th><th>SUEZ TONNAGE (Suez Tons)</th></tr>
  <tr><td>Under the Tonnage Deck</td><td>SCA Rules Art. 93 Para 1</td><td class="text-right">{udt_vol:,.3f}</td><td class="text-right">{udt_tons:,.2f}</td></tr>
  <tr><td>Bulbous Bow</td><td>SCA Appendix 1</td><td class="text-right">{f"{bulb_vol:,.3f}" if has_bulb and bulb_tons > 0 else "-"}</td><td class="text-right">{f"{bulb_tons:,.2f}" if has_bulb and bulb_tons > 0 else "-"}</td></tr>
  <tr><td>Forecastle Deck</td><td>SCA Rules Art. 93 Para 2</td><td class="text-right">{f"{fc_vol:,.3f}" if has_fc and fc_tons > 0 else "-"}</td><td class="text-right">{f"{fc_tons:,.2f}" if has_fc and fc_tons > 0 else "-"}</td></tr>
  <tr><td>Excess Cargo Hatchways</td><td>SCA Rules Art. 93 Para 3</td><td class="text-right">{f"{hatch_exc_vol:,.3f}" if has_hatches and hatch_exc_tons > 0 else "-"}</td><td class="text-right">{f"{hatch_exc_tons:,.2f}" if has_hatches and hatch_exc_tons > 0 else "-"}</td></tr>
  <tr><td>Round Houses, etc.</td><td>SCA Rules Art. 93 Para 4</td><td class="text-right">{f"{tot_rh_vol:,.3f}" if has_roundhouses and tot_rh_ton > 0 else "-"}</td><td class="text-right">{f"{tot_rh_ton:,.2f}" if has_roundhouses and tot_rh_ton > 0 else "-"}</td></tr>
  <tr class="highlight"><td><strong>TOTAL SUEZ CANAL GROSS TONNAGE</strong></td><td>SCA Certificate Gross</td><td class="text-right"><strong>{gross_vol:,.3f}</strong></td><td class="text-right"><strong>{gross_tonnage:,.2f}</strong></td></tr>
</table>\n"""

    # SECTION 8: NET TONNAGE (HTML - 4 columns)
    html += f"""<h2>Suez Canal Net Tonnage Deduction Calculation</h2>
<table>
  <tr><th>STATUTORY DEDUCTION SPACE</th><th>SCA STATUTORY REGULATION</th><th>DEDUCTED VOLUME (m&sup3;)</th><th>DEDUCTED TONNAGE (Suez Tons)</th></tr>
  <tr><td>Officer's Accommodation</td><td>SCA Rules Art. 94 Para 1</td><td class="text-right">{f"{off_v:,.3f}" if off_acc_ton > 0 else "-"}</td><td class="text-right">{f"{off_acc_ton:,.2f}" if off_acc_ton > 0 else "-"}</td></tr>
  <tr><td>Crew's Accommodation</td><td>SCA Rules Art. 94 Para 1</td><td class="text-right">{f"{crew_v:,.3f}" if crew_acc_ton > 0 else "-"}</td><td class="text-right">{f"{crew_acc_ton:,.2f}" if crew_acc_ton > 0 else "-"}</td></tr>
  <tr><td>Spaces Used in Working the Ship</td><td>SCA Rules Art. 94 Para 2</td><td class="text-right">{f"{work_v:,.3f}" if work_ship_ton > 0 else "-"}</td><td class="text-right">{f"{work_ship_ton:,.2f}" if work_ship_ton > 0 else "-"}</td></tr>
  <tr><td>Deduction for Propelling Power</td><td>SCA Rules Art. 94 Para 3</td><td class="text-right">{f"{prop_v:,.3f}" if prop_power_ton > 0 else "-"}</td><td class="text-right">{f"{prop_power_ton:,.2f}" if prop_power_ton > 0 else "-"}</td></tr>
  <tr class="highlight"><td><strong>TOTAL STATUTORY DEDUCTIONS</strong></td><td>SCA Art. 94 Summary</td><td class="text-right"><strong>{f"{tot_d_v:,.3f}" if tot_ded_ton > 0 else "-"}</strong></td><td class="text-right"><strong>{tot_ded_ton:,.2f}</strong></td></tr>
  <tr class="highlight"><td><strong>SUEZ CANAL NET TONNAGE</strong></td><td>SCA Certificate Net</td><td>-</td><td class="text-right"><strong>{net_tonnage:,.2f}</strong></td></tr>
</table>

</body>
</html>
"""
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_html_path
