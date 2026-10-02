"""
Forecastle Deck Space Tonnage Calculation Excel Generator
Generates a dedicated single official calculation table workbook for Forecastle Deck Space.
Complies with user instructions:
- Excludes the millimeter column (all dimensions strictly in meters).
- Includes all stations (Full stations 17, 18, 19, 20, Half stations 18.5, 19.5, and Overhang stations A, B).
- Full breadth B = 2 * Half-Breadth (FCS).
- Sectional Area A = Breadth * Height.
- Longitudinal Simpson integration across all stations with live Excel formulas.
100% pure standard ASCII English encoding.
"""
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Styles & Color Palette
NAVY       = PatternFill("solid", fgColor="1B365D")
HEADER_BLU = PatternFill("solid", fgColor="2B5B84")
SLATE_GRAY = PatternFill("solid", fgColor="455A64")
INPUT_YEL  = PatternFill("solid", fgColor="FFF9C4")
CALC_GRN   = PatternFill("solid", fgColor="E8F5E9")
ALERT_ORG  = PatternFill("solid", fgColor="FFE0B2")
LIGHT_GRAY = PatternFill("solid", fgColor="F5F5F5")
GROUP_HDR  = PatternFill("solid", fgColor="D0E1F9")
ACCENT_GRY = PatternFill("solid", fgColor="E0E0E0")
WHITE      = PatternFill("solid", fgColor="FFFFFF")

TITLE_FONT        = Font(name="Calibri", bold=True, size=13, color="FFFFFF")
SUB_WHITE_BOLD    = Font(name="Calibri", bold=True, color="FFFFFF", size=9)
SECTION_FONT      = Font(name="Calibri", bold=True, size=10, color="1B365D")
HEADER_WHITE_BOLD = Font(name="Calibri", bold=True, color="FFFFFF", size=9)
LABEL_BOLD        = Font(name="Calibri", bold=True, size=9)
BODY_REG          = Font(name="Calibri", size=9)
BODY_BOLD         = Font(name="Calibri", bold=True, size=9)
ITALIC_NOTE       = Font(name="Calibri", italic=True, size=8, color="555555")

THIN_BORDER = Border(
    left=Side(style="thin", color="CCCCCC"), right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"), bottom=Side(style="thin", color="CCCCCC"),
)
THICK_TOP_DOUBLE_BOTTOM = Border(
    left=Side(style="thin", color="CCCCCC"), right=Side(style="thin", color="CCCCCC"),
    top=Side(style="medium", color="1B365D"), bottom=Side(style="double", color="1B365D"),
)

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
RIGHT  = Alignment(horizontal="right",  vertical="center")

def style_c(ws, r, c, val=None, fill=None, font=None, align=None, border=THIN_BORDER, num_format=None):
    cell = ws.cell(row=r, column=c, value=val)
    if fill: cell.fill = fill
    if font: cell.font = font
    if align: cell.alignment = align
    if border: cell.border = border
    if num_format: cell.number_format = num_format
    return cell

def build_single_table_forecastle_workbook(output_path, imported_height=2.600):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Forecastle_Tonnage"
    ws.views.sheetView[0].showGridLines = True

    # 1. Main Title Block
    ws.merge_cells("A1:J1")
    style_c(ws, 1, 1, "SUEZ CANAL TONNAGE - FORECASTLE DECK CALCULATION TABLE", fill=NAVY, font=TITLE_FONT, align=CENTER)
    ws.row_dimensions[1].height = 28

    ws.merge_cells("A2:J2")
    style_c(ws, 2, 1, "Vessel: M/V TERVEL | Lbp = 186.10 m | B = 32.26 m | D = 17.80 m | Statutory Moorsom Tonnage (V / 2.83)", fill=HEADER_BLU, font=SUB_WHITE_BOLD, align=CENTER)
    ws.row_dimensions[2].height = 18

    ws.merge_cells("A3:J3")
    style_c(ws, 3, 1, "Procedure: Full Breadth B = 2 x Half-Breadth (m) | Sectional Area A = B x Height H | Simpson Longitudinal Integration along Forecastle Length", fill=LIGHT_GRAY, font=ITALIC_NOTE, align=LEFT)
    ws.row_dimensions[3].height = 18

    # -------------------------------------------------------------------------
    # PARAMETER / IMPORT CONFIGURATION BLOCK
    # -------------------------------------------------------------------------
    ws.merge_cells("A5:J5")
    style_c(ws, 5, 1, "1. FORECASTLE IMPORTED PARAMETERS & INTEGRATION SETUP", fill=GROUP_HDR, font=SECTION_FONT, align=LEFT)
    ws.row_dimensions[5].height = 20

    cfg_labels = [
        ("A6", "B6", "Imported Forecastle Height H (m):", "C6", imported_height, "0.000", INPUT_YEL, "Imported / user-specified Forecastle Height (applied across sections)"),
        ("A7", "B7", "Standard Common Interval dx (m):", "C7", 9.305, "0.000", LIGHT_GRAY, "Station spacing = Lbp / 20 = 9.305 m"),
        ("A8", "B8", "Half-Station Interval dx / 2 (m):", "C8", 4.6525, "0.0000", LIGHT_GRAY, "Half station spacing between St. 18, 18.5, 19, 19.5, 20"),
        ("A9", "B9", "Forecastle Extent:", "C9", "St. 18 to St. A (Overhang)", "@", LIGHT_GRAY, "Includes all stations possessing Forecastle Deck values"),
        ("A10", "B10", "Suez Canal Tonnage Divisor:", "C10", 2.83, "0.00", LIGHT_GRAY, "SCA Moorsom Tonnage divisor: 2.83 m3 / Ton"),
    ]

    for start_l, end_l, lbl, val_pos, val, fmt, bg, note in cfg_labels:
        r_num = int(start_l[1:])
        ws.merge_cells(f"{start_l}:{end_l}")
        style_c(ws, r_num, 1, lbl, fill=LIGHT_GRAY, font=LABEL_BOLD, align=LEFT)
        style_c(ws, r_num, 2, fill=LIGHT_GRAY, font=LABEL_BOLD, align=LEFT)
        style_c(ws, r_num, 3, val, fill=bg, font=BODY_BOLD, align=CENTER, num_format=fmt)
        ws.merge_cells(f"D{r_num}:J{r_num}")
        style_c(ws, r_num, 4, note, fill=WHITE, font=ITALIC_NOTE, align=LEFT)
        for c_idx in range(5, 11):
            style_c(ws, r_num, c_idx, fill=WHITE, font=ITALIC_NOTE, align=LEFT)
        ws.row_dimensions[r_num].height = 19

    # -------------------------------------------------------------------------
    # 2. COMPLETE FORECASTLE CALCULATION TABLE (METERS ONLY, NO MM COLUMN)
    # -------------------------------------------------------------------------
    curr_r = 12
    ws.merge_cells(f"A{curr_r}:J{curr_r}")
    style_c(ws, curr_r, 1, "2. FORECASTLE DECK CALCULATION TABLE (ALL STATIONS IN METERS)", fill=NAVY, font=Font(name="Calibri", bold=True, size=11, color="FFFFFF"), align=LEFT)
    ws.row_dimensions[curr_r].height = 22
    curr_r += 1

    headers = [
        ("No.", 6),
        ("Station", 14),
        ("Station Type", 18),
        ("Position X (m)", 16),
        ("Half-Breadth y (m)", 20),
        ("Full Breadth B (m)", 20),
        ("Height H (m)", 16),
        ("Section Area A (m2)", 20),
        ("Simpson Factor", 16),
        ("Product (A x Factor)", 22)
    ]

    for col_idx, (h_text, w) in enumerate(headers, start=1):
        style_c(ws, curr_r, col_idx, h_text, fill=SLATE_GRAY, font=HEADER_WHITE_BOLD, align=CENTER)
        ws.column_dimensions[get_column_letter(col_idx)].width = w
    ws.row_dimensions[curr_r].height = 26
    curr_r += 1

    # ALL STATIONS WITH FORECASTLE DECK DATA (Half-breadth directly in meters)
    all_stations = [
        (1, "Station 17",   "Aft Boundary",   158.185, 16.130, 0.0, "Aft Bulkhead reference (0.0 if forecastle starts at St. 18)"),
        (2, "Station 18",   "Full Station",   167.490, 16.130, 0.5, "Forecastle Body Aft End"),
        (3, "Station 18.5", "Half Station",   172.143, 14.578, 2.0, "Intermediate Half Station"),
        (4, "Station 19",   "Full Station",   176.795, 12.996, 1.0, "Forecastle Body Section"),
        (5, "Station 19.5", "Half Station",   181.448, 12.963, 2.0, "Intermediate Half Station"),
        (6, "Station 20",   "FP Station",     186.100,  9.647, 0.5, "Forward Perpendicular (FP)"),
        (7, "Station A",    "Stem Overhang",  187.600,  9.404, 0.2418, "Stem Overhang (+1.50 m fwd of FP)"),
        (8, "Station B",    "Foremost Apex",  189.100,  0.000, 0.0, "Foremost Tip (+3.00 m fwd of FP, B = 0)")
    ]

    st_start_r = curr_r
    for no, st_name, st_type, x_pos, hb_m, factor, rem in all_stations:
        r = curr_r
        # Col 1: No.
        style_c(ws, r, 1, no, fill=WHITE, font=BODY_REG, align=CENTER)
        # Col 2: Station
        style_c(ws, r, 2, st_name, fill=WHITE, font=BODY_BOLD, align=CENTER)
        # Col 3: Station Type
        style_c(ws, r, 3, st_type, fill=WHITE, font=BODY_REG, align=CENTER)
        # Col 4: Position X (m)
        style_c(ws, r, 4, x_pos, fill=WHITE, font=BODY_REG, align=RIGHT, num_format="0.000")
        # Col 5: Half-Breadth y (m) from offset table
        style_c(ws, r, 5, hb_m, fill=WHITE, font=BODY_REG, align=RIGHT, num_format="0.000")
        # Col 6: Full Breadth B (m) = 2 * Half-Breadth
        style_c(ws, r, 6, f"=2*E{r}", fill=CALC_GRN, font=BODY_BOLD, align=RIGHT, num_format="0.000")
        # Col 7: Imported Forecastle Height H (m) = $C$6
        style_c(ws, r, 7, f"=$C$6", fill=INPUT_YEL, font=BODY_BOLD, align=RIGHT, num_format="0.000")
        # Col 8: Section Area A (m2) = Breadth * Height
        style_c(ws, r, 8, f"=F{r}*G{r}", fill=CALC_GRN, font=BODY_BOLD, align=RIGHT, num_format="0.000")
        # Col 9: Simpson Factor
        style_c(ws, r, 9, factor, fill=WHITE, font=BODY_BOLD, align=CENTER, num_format="0.0000" if isinstance(factor, float) and factor != 0.5 and factor != 2.0 and factor != 1.0 and factor != 0.0 else "0.0")
        # Col 10: Product = Area * Factor
        style_c(ws, r, 10, f"=H{r}*I{r}", fill=CALC_GRN, font=BODY_BOLD, align=RIGHT, num_format="0.000")

        ws.row_dimensions[r].height = 20
        curr_r += 1
    st_end_r = curr_r - 1

    # -------------------------------------------------------------------------
    # SUMMARY ROWS INTEGRATED DIRECTLY AT THE BOTTOM OF THE TABLE
    # -------------------------------------------------------------------------
    sum_prod_r = curr_r
    ws.merge_cells(f"A{sum_prod_r}:I{sum_prod_r}")
    style_c(ws, sum_prod_r, 1, "SUM OF PRODUCTS (SUM) [ST. 18 TO ST. A]:", fill=ACCENT_GRY, font=LABEL_BOLD, align=RIGHT)
    for c in range(2, 10):
        style_c(ws, sum_prod_r, c, fill=ACCENT_GRY, font=LABEL_BOLD, align=RIGHT)
    style_c(ws, sum_prod_r, 10, f"=SUM(J{st_start_r}:J{st_end_r})", fill=ACCENT_GRY, font=Font(name="Calibri", bold=True, size=10), align=RIGHT, num_format="#,##0.000")
    ws.row_dimensions[sum_prod_r].height = 21
    curr_r += 1

    dx_r = curr_r
    ws.merge_cells(f"A{dx_r}:I{dx_r}")
    style_c(ws, dx_r, 1, "1/3 STANDARD COMMON INTERVAL (dx / 3):", fill=WHITE, font=BODY_BOLD, align=RIGHT)
    for c in range(2, 10):
        style_c(ws, dx_r, c, fill=WHITE, font=BODY_BOLD, align=RIGHT)
    style_c(ws, dx_r, 10, f"=C7/3", fill=CALC_GRN, font=BODY_REG, align=RIGHT, num_format="0.0000")
    ws.row_dimensions[dx_r].height = 20
    curr_r += 1

    vol_r = curr_r
    ws.merge_cells(f"A{vol_r}:I{vol_r}")
    style_c(ws, vol_r, 1, "FORECASTLE ENCLOSED VOLUME (m3) = (dx / 3) * SUM:", fill=GROUP_HDR, font=Font(name="Calibri", bold=True, size=10, color="1B365D"), align=RIGHT)
    for c in range(2, 10):
        style_c(ws, vol_r, c, fill=GROUP_HDR, font=Font(name="Calibri", bold=True, size=10, color="1B365D"), align=RIGHT)
    style_c(ws, vol_r, 10, f"=J{dx_r}*J{sum_prod_r}", fill=GROUP_HDR, font=Font(name="Calibri", bold=True, size=10, color="1B365D"), align=RIGHT, num_format="#,##0.000")
    ws.row_dimensions[vol_r].height = 22
    curr_r += 1

    ton_r = curr_r
    ws.merge_cells(f"A{ton_r}:I{ton_r}")
    style_c(ws, ton_r, 1, "FORECASTLE SUEZ MOORSOM TONNAGE (TONS) = Volume / 2.83:", fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=11, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM)
    for c in range(2, 10):
        style_c(ws, ton_r, c, fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=11, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM)
    style_c(ws, ton_r, 10, f"=J{vol_r}/C10", fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=11, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM, num_format="#,##0.00")
    ws.row_dimensions[ton_r].height = 26
    curr_r += 2

    # -------------------------------------------------------------------------
    # 3. DIRECT SUB-INTERVAL STEP-BY-STEP INTEGRATION BREAKDOWN
    # -------------------------------------------------------------------------
    ws.merge_cells(f"A{curr_r}:J{curr_r}")
    style_c(ws, curr_r, 1, "3. STEP-BY-STEP SUB-INTERVAL BREAKDOWN (DETAILED VERIFICATION)", fill=GROUP_HDR, font=SECTION_FONT, align=LEFT)
    ws.row_dimensions[curr_r].height = 20
    curr_r += 1

    headers_sub = [
        ("Sub-Section", 22),
        ("Station Range", 18),
        ("Stations Included", 24),
        ("Interval Spacing h (m)", 20),
        ("Integration Formula", 28),
        ("Sub-Volume (m3)", 18),
        ("Suez Tonnage (Tons)", 18),
        ("Remarks / Notes", 28)
    ]

    for col_idx, (h_text, w) in enumerate(headers_sub, start=1):
        style_c(ws, curr_r, col_idx, h_text, fill=SLATE_GRAY, font=HEADER_WHITE_BOLD, align=CENTER)
    ws.row_dimensions[curr_r].height = 24
    curr_r += 1

    sub_breakdowns = [
        ("Forecastle Body", "St. 18 to St. 20", "St. 18, 18.5, 19, 19.5, 20", 4.6525, "(h/3) * (A18 + 4*A18.5 + 2*A19 + 4*A19.5 + A20)",
         f"=(C8/3)*(H15*1 + H16*4 + H17*2 + H18*4 + H19*1)", f"=F{curr_r}/C10", "5 ordinates Simpson 1st Rule"),
        ("Stem Overhang", "St. 20 to St. A", "St. 20, St. A", 1.5000, "(h/2) * (A20 + AA)",
         f"=(1.5/2)*(H19 + H20)", f"=F{curr_r+1}/C10", "Trapezoidal forward overhang"),
        ("Foremost Apex (Optional)", "St. A to St. B", "St. A, St. B (B=0)", 1.5000, "(h/2) * (AA + AB)",
         f"=(1.5/2)*(H20 + H21)", f"=F{curr_r+2}/C10", "Foremost apex tip to St. B (B=0)")
    ]

    b_start_r = curr_r
    for title, s_rng, s_inc, h_val, f_desc, f_vol, f_ton, rem in sub_breakdowns:
        r = curr_r
        style_c(ws, r, 1, title, fill=WHITE, font=BODY_BOLD, align=LEFT)
        style_c(ws, r, 2, s_rng, fill=WHITE, font=BODY_REG, align=CENTER)
        style_c(ws, r, 3, s_inc, fill=WHITE, font=BODY_REG, align=LEFT)
        style_c(ws, r, 4, h_val, fill=WHITE, font=BODY_REG, align=RIGHT, num_format="0.0000")
        style_c(ws, r, 5, f_desc, fill=WHITE, font=ITALIC_NOTE, align=LEFT)
        style_c(ws, r, 6, f_vol, fill=CALC_GRN, font=BODY_BOLD, align=RIGHT, num_format="#,##0.000")
        style_c(ws, r, 7, f_ton, fill=CALC_GRN, font=BODY_BOLD, align=RIGHT, num_format="#,##0.00")
        style_c(ws, r, 8, rem, fill=WHITE, font=ITALIC_NOTE, align=LEFT)
        ws.row_dimensions[r].height = 20
        curr_r += 1

    # Total of St 18 to St A
    ws.merge_cells(f"A{curr_r}:E{curr_r}")
    style_c(ws, curr_r, 1, "TOTAL FORECASTLE (BODY + OVERHANG ST. 18 TO ST. A):", fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=10, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM)
    for c in range(2, 6):
        style_c(ws, curr_r, c, fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=10, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM)
    style_c(ws, curr_r, 6, f"=F{b_start_r}+F{b_start_r+1}", fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=10, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM, num_format="#,##0.000")
    style_c(ws, curr_r, 7, f"=F{curr_r}/C10", fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=11, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM, num_format="#,##0.00")
    ws.merge_cells(f"H{curr_r}:J{curr_r}")
    style_c(ws, curr_r, 8, "Primary recommended forecastle tonnage", fill=ALERT_ORG, font=ITALIC_NOTE, align=LEFT, border=THICK_TOP_DOUBLE_BOTTOM)
    for c in range(9, 11):
        style_c(ws, curr_r, c, fill=ALERT_ORG, font=ITALIC_NOTE, align=LEFT, border=THICK_TOP_DOUBLE_BOTTOM)
    ws.row_dimensions[curr_r].height = 24
    curr_r += 2

    # -------------------------------------------------------------------------
    # 4. VARIABLE IMPORTED HEIGHT (STATION-BY-STATION HEIGHT IMPORT)
    # -------------------------------------------------------------------------
    ws.merge_cells(f"A{curr_r}:J{curr_r}")
    style_c(ws, curr_r, 1, "4. ALTERNATIVE: VARIABLE HEIGHT IMPORT TABLE (STATION-SPECIFIC HEIGHTS IN METERS)", fill=SLATE_GRAY, font=Font(name="Calibri", bold=True, size=10, color="FFFFFF"), align=LEFT)
    ws.row_dimensions[curr_r].height = 20
    curr_r += 1

    headers_v = [
        ("No.", 6),
        ("Station", 14),
        ("Station Type", 18),
        ("Position X (m)", 16),
        ("Half-Breadth y (m)", 20),
        ("Full Breadth B (m)", 20),
        ("Imported Height H (m)", 20),
        ("Section Area A (m2)", 20),
        ("Simpson Factor", 16),
        ("Product (A x Factor)", 22)
    ]

    for col_idx, (h_text, w) in enumerate(headers_v, start=1):
        style_c(ws, curr_r, col_idx, h_text, fill=ACCENT_GRY, font=LABEL_BOLD, align=CENTER)
    ws.row_dimensions[curr_r].height = 24
    curr_r += 1

    var_stations = [
        (1, "Station 17",   "Aft Boundary",   158.185, 16.130, 2.400, 0.0),
        (2, "Station 18",   "Full Station",   167.490, 16.130, 2.400, 0.5),
        (3, "Station 18.5", "Half Station",   172.143, 14.578, 2.650, 2.0),
        (4, "Station 19",   "Full Station",   176.795, 12.996, 2.902, 1.0),
        (5, "Station 19.5", "Half Station",   181.448, 12.963, 2.796, 2.0),
        (6, "Station 20",   "FP Station",     186.100,  9.647, 2.646, 0.5),
        (7, "Station A",    "Stem Overhang",  187.600,  9.404, 2.661, 0.2418),
        (8, "Station B",    "Foremost Apex",  189.100,  0.000, 2.677, 0.0)
    ]

    v_start_r = curr_r
    for no, st_name, st_type, x_pos, hb_m, var_h, factor in var_stations:
        r = curr_r
        style_c(ws, r, 1, no, fill=WHITE, font=BODY_REG, align=CENTER)
        style_c(ws, r, 2, st_name, fill=WHITE, font=BODY_BOLD, align=CENTER)
        style_c(ws, r, 3, st_type, fill=WHITE, font=BODY_REG, align=CENTER)
        style_c(ws, r, 4, x_pos, fill=WHITE, font=BODY_REG, align=RIGHT, num_format="0.000")
        style_c(ws, r, 5, hb_m, fill=WHITE, font=BODY_REG, align=RIGHT, num_format="0.000")
        style_c(ws, r, 6, f"=2*E{r}", fill=CALC_GRN, font=BODY_BOLD, align=RIGHT, num_format="0.000")
        style_c(ws, r, 7, var_h, fill=INPUT_YEL, font=BODY_BOLD, align=RIGHT, num_format="0.000")
        style_c(ws, r, 8, f"=F{r}*G{r}", fill=CALC_GRN, font=BODY_BOLD, align=RIGHT, num_format="0.000")
        style_c(ws, r, 9, factor, fill=WHITE, font=BODY_BOLD, align=CENTER, num_format="0.0000" if isinstance(factor, float) and factor != 0.5 and factor != 2.0 and factor != 1.0 and factor != 0.0 else "0.0")
        style_c(ws, r, 10, f"=H{r}*I{r}", fill=CALC_GRN, font=BODY_BOLD, align=RIGHT, num_format="0.000")
        ws.row_dimensions[r].height = 20
        curr_r += 1
    v_end_r = curr_r - 1

    # Variable summary
    v_sum_r = curr_r
    ws.merge_cells(f"A{v_sum_r}:I{v_sum_r}")
    style_c(ws, v_sum_r, 1, "SUM OF PRODUCTS (VARIABLE IMPORTED HEIGHTS):", fill=ACCENT_GRY, font=LABEL_BOLD, align=RIGHT)
    for c in range(2, 10):
        style_c(ws, v_sum_r, c, fill=ACCENT_GRY, font=LABEL_BOLD, align=RIGHT)
    style_c(ws, v_sum_r, 10, f"=SUM(J{v_start_r}:J{v_end_r})", fill=ACCENT_GRY, font=Font(name="Calibri", bold=True, size=10), align=RIGHT, num_format="#,##0.000")
    ws.row_dimensions[v_sum_r].height = 20
    curr_r += 1

    v_vol_r = curr_r
    ws.merge_cells(f"A{v_vol_r}:I{v_vol_r}")
    style_c(ws, v_vol_r, 1, "ENCLOSED VOLUME (m3) = (dx / 3) * SUM:", fill=GROUP_HDR, font=Font(name="Calibri", bold=True, size=10, color="1B365D"), align=RIGHT)
    for c in range(2, 10):
        style_c(ws, v_vol_r, c, fill=GROUP_HDR, font=Font(name="Calibri", bold=True, size=10, color="1B365D"), align=RIGHT)
    style_c(ws, v_vol_r, 10, f"=(C7/3)*J{v_sum_r}", fill=GROUP_HDR, font=Font(name="Calibri", bold=True, size=10, color="1B365D"), align=RIGHT, num_format="#,##0.000")
    ws.row_dimensions[v_vol_r].height = 22
    curr_r += 1

    v_ton_r = curr_r
    ws.merge_cells(f"A{v_ton_r}:I{v_ton_r}")
    style_c(ws, v_ton_r, 1, "SUEZ CANAL TONNAGE (TONS) = Volume / 2.83:", fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=11, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM)
    for c in range(2, 10):
        style_c(ws, v_ton_r, c, fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=11, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM)
    style_c(ws, v_ton_r, 10, f"=J{v_vol_r}/C10", fill=ALERT_ORG, font=Font(name="Calibri", bold=True, size=11, color="B71C1C"), align=RIGHT, border=THICK_TOP_DOUBLE_BOTTOM, num_format="#,##0.00")
    ws.row_dimensions[v_ton_r].height = 26
    curr_r += 2

    if os.path.dirname(output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    return output_path

if __name__ == "__main__":
    out1 = "e:/Suaze tonnage calculator/Forecastle_Deck_Tonnage_Calculation.xlsx"
    out2 = "e:/Suaze tonnage calculator/Suez_Tonnage_Tool/exported_reports/Forecastle_Deck_Tonnage_Calculation.xlsx"
    build_single_table_forecastle_workbook(out1, imported_height=2.600)
    build_single_table_forecastle_workbook(out2, imported_height=2.600)
    print("Forecastle Deck Single Table (Meters Only) Workbook Generated Successfully!")
