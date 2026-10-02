"""
Offset Reader & Parser Module
Reads and validates filled shipyard offset spreadsheets (.xlsx).
"""
import openpyxl

def parse_offset_value(val):
    """Parses raw cell values (integers, floats, strings, dashes) to float or None."""
    if val is None:
        return None
    val_str = str(val).strip()
    if val_str in ["-", "", "None", "null"]:
        return None
    # Handle combined values like '701/10700'
    if "/" in val_str:
        parts = [p.strip() for p in val_str.split("/")]
        try:
            return [float(p) for p in parts]
        except ValueError:
            return val_str
    try:
        return float(val_str)
    except ValueError:
        return val_str

def read_offset_file(filepath):
    """
    Parses a user-filled offset spreadsheet.
    Returns structured data dictionary containing:
      - stations: list of station names
      - waterlines: list of waterline names
      - buttocks: list of buttock names
      - half_breadths: dict {station_name: {wl_name: value_in_mm}}
      - heights: dict {station_name: {bt_name: value_in_mm}}
      - vessel_particulars: dict of ship particulars if available
    """
    wb = openpyxl.load_workbook(filepath, data_only=True)
    
    # 1. Check for Lines_Table_Offsets sheet
    sheet_name = None
    for name in ["Lines_Table_Offsets", "Table_of_Offsets", "Offsets", "Sheet1"]:
        if name in wb.sheetnames:
            sheet_name = name
            break
    if not sheet_name:
        sheet_name = wb.sheetnames[0]
        
    ws = wb[sheet_name]

    # Find the header row (contains 'Station', 'BL', '500WL' etc.)
    header_row = None
    for r in range(1, 15):
        for c in range(1, 3):
            val = str(ws.cell(r, c).value or '').strip()
            if val.lower() == 'station':
                next_c2 = str(ws.cell(r + 1, 2).value or '').strip()
                if 'wl' in next_c2.lower() or 'bl' in next_c2.lower():
                    header_row = r + 1
                else:
                    header_row = r
                break
        if header_row:
            break

    if not header_row:
        header_row = 4 # default fallback

    # Scan column names
    col_headers = {}
    for c in range(1, ws.max_column + 1):
        h_val = ws.cell(header_row, c).value
        if h_val is not None:
            clean_h = str(h_val).replace("\n", " ").strip()
            col_headers[c] = clean_h

    # Identify waterlines vs buttocks columns
    waterlines = []
    buttocks = []
    wl_cols = {}
    bt_cols = {}

    for c, h in col_headers.items():
        if h.lower() == "station":
            continue
        # Underdeck waterlines strictly up to Upper Deck (excluding Forecastle Deck Side and Bulwarks)
        if ("wl" in h.lower() or h.lower() == "bl" or "upper deck" in h.lower()) and "forecastle" not in h.lower() and "bulwark" not in h.lower() and "height" not in h.lower():
            waterlines.append(h)
            wl_cols[h] = c
        elif "b.l." in h.lower() or "height" in h.lower() or "bottom" in h.lower() or h.lower() in ["c.l.", "cl"]:
            buttocks.append(h)
            bt_cols[h] = c

    # Read station rows
    stations = []
    half_breadths = {}
    heights = {}

    for r in range(header_row + 1, ws.max_row + 1):
        st_val = ws.cell(r, 1).value
        if st_val is None:
            continue
        st_name = str(st_val).strip()
        if not st_name or st_name.startswith(">") or "body" in st_name.lower():
            continue
        
        stations.append(st_name)
        half_breadths[st_name] = {}
        heights[st_name] = {}

        for wl, c in wl_cols.items():
            half_breadths[st_name][wl] = parse_offset_value(ws.cell(r, c).value)

        for bt, c in bt_cols.items():
            heights[st_name][bt] = parse_offset_value(ws.cell(r, c).value)

    # 2. Read Vessel Particulars if sheet exists
    vessel_info = {
        "vessel_name": "",
        "lbp": 186.10,
        "breadth": 32.26,
        "depth": 17.80,
        "bulb_length": 5.00
    }

    if "Vessel_Particulars" in wb.sheetnames:
        ws_vp = wb["Vessel_Particulars"]
        for r in range(1, ws_vp.max_row + 1):
            k = str(ws_vp.cell(r, 1).value or '').lower()
            v = ws_vp.cell(r, 2).value
            if "name" in k and v:
                vessel_info["vessel_name"] = str(v).strip()
            elif "perpendicular" in k or "lbp" in k:
                try: vessel_info["lbp"] = float(v)
                except: pass
            elif "breadth" in k:
                try: vessel_info["breadth"] = float(v)
                except: pass
            elif "depth" in k:
                try: vessel_info["depth"] = float(v)
                except: pass
            elif "bulb" in k:
                try: vessel_info["bulb_length"] = float(v)
                except: pass

    return {
        "vessel_info": vessel_info,
        "stations": stations,
        "waterlines": waterlines,
        "buttocks": buttocks,
        "half_breadths": half_breadths,
        "heights": heights,
        "total_stations": len(stations),
        "total_waterlines": len(waterlines),
        "total_buttocks": len(buttocks),
    }
