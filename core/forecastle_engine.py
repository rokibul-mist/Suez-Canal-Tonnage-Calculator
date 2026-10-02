"""
Forecastle Deck Calculation Engine
Computes cross-sectional areas and longitudinal Simpson integration for Forecastle Deck Space.
Uses meters exclusively (no millimeter columns).
Full breadth B = 2 * Half-Breadth (FCS).
Area = Full Breadth * Forecastle Height.
Integrates across all stations possessing Forecastle Deck values:
Full stations, Half stations, and Overhang stations (St. A, St. B).
"""

# Official SCA conversion constant: 1 Suez Ton = 100 cu.ft = 2.832 m3
SUEZ_TON_M3 = 2.832

def calculate_forecastle_tonnage(
    parsed_data=None, 
    imported_height=2.600, 
    lbp=186.10, 
    column_name="Upper Deck Side",
    start_station=None,
    end_station=None,
    custom_rows=None,
    has_forecastle=True
):
    """
    Computes Forecastle Tonnage using:
    - Selected half-breadth column from offset table (column_name, e.g. 'Upper Deck Side')
    - Imported / user-specified Forecastle Height (m)
    - Full breadth B (m) = 2 * Half-Breadth
    - Sectional Area A (m2) = Breadth * Height
    - Longitudinal Simpson integration across all forecastle stations.
    """
    if not has_forecastle:
        return {
            "imported_height": 0.0,
            "dx_standard": 0.0,
            "dx_over_3": 0.0,
            "sum_products": 0.0,
            "forecastle_volume": 0.0,
            "forecastle_tonnage": 0.0,
            "column_used": column_name,
            "rows": [],
            "breakdown": {
                "body_volume": 0.0,
                "body_tonnage": 0.0,
                "overhang_volume": 0.0,
                "overhang_tonnage": 0.0,
                "apex_volume": 0.0,
                "apex_tonnage": 0.0,
            }
        }

    # If user provided explicit custom rows, calculate directly from them
    if custom_rows and len(custom_rows) > 0:
        rows = []
        sum_products = 0.0
        for r in custom_rows:
            hb_m = float(r.get("half_breadth_m", 0.0))
            h_m = float(r.get("height_m", imported_height))
            b_m = 2.0 * hb_m
            area_m2 = b_m * h_m
            factor = float(r.get("factor", 1.0))
            product = area_m2 * factor
            sum_products += product
            rows.append({
                "station": r.get("station", ""),
                "station_type": r.get("station_type", ""),
                "position_x": round(float(r.get("position_x", 0.0)), 3),
                "half_breadth_m": round(hb_m, 3),
                "breadth_m": round(b_m, 3),
                "height_m": round(h_m, 3),
                "area_m2": round(area_m2, 3),
                "factor": factor,
                "product": round(product, 3),
                "remark": r.get("remark", "")
            })
        dx_standard = lbp / 20.0
        dx_over_3 = dx_standard / 3.0
        forecastle_volume = dx_over_3 * sum_products
        forecastle_tonnage = forecastle_volume / SUEZ_TON_M3
        return {
            "imported_height": round(imported_height, 3),
            "dx_standard": round(dx_standard, 3),
            "dx_over_3": round(dx_over_3, 4),
            "sum_products": round(sum_products, 3),
            "forecastle_volume": round(forecastle_volume, 3),
            "forecastle_tonnage": round(forecastle_tonnage, 2),
            "column_used": column_name,
            "rows": rows,
            "breakdown": {
                "body_volume": round(forecastle_volume, 3),
                "body_tonnage": round(forecastle_tonnage, 2),
                "overhang_volume": 0.0,
                "overhang_tonnage": 0.0,
                "apex_volume": 0.0,
                "apex_tonnage": 0.0,
            }
        }

    # If no offset data is loaded in the session and no custom rows, return clean empty
    if not parsed_data or not parsed_data.get("half_breadths"):
        return {
            "imported_height": 0.0,
            "dx_standard": 0.0,
            "dx_over_3": 0.0,
            "sum_products": 0.0,
            "forecastle_volume": 0.0,
            "forecastle_tonnage": 0.0,
            "column_used": column_name,
            "rows": [],
            "breakdown": {
                "body_volume": 0.0,
                "body_tonnage": 0.0,
                "overhang_volume": 0.0,
                "overhang_tonnage": 0.0,
                "apex_volume": 0.0,
                "apex_tonnage": 0.0,
            }
        }

    dx_standard = lbp / 20.0 # 9.305 m
    dx_half = dx_standard / 2.0 # 4.6525 m

    # Forecastle integration stations sequence: St 17 to St B
    default_offsets = [
        ("Station 17",   lbp * (17.0 / 20.0), "Aft Boundary",   0.0,    "Aft Bulkhead reference"),
        ("Station 18",   lbp * (18.0 / 20.0), "Full Station",   0.5,    "Forecastle Body Aft End"),
        ("Station 18.5", lbp * (18.5 / 20.0), "Half Station",   2.0,    "Intermediate Half Station"),
        ("Station 19",   lbp * (19.0 / 20.0), "Full Station",   1.0,    "Forecastle Body Section"),
        ("Station 19.5", lbp * (19.5 / 20.0), "Half Station",   2.0,    "Intermediate Half Station"),
        ("Station 20",   lbp * (20.0 / 20.0), "FP Station",     0.5,    "Forward Perpendicular (FP)"),
        ("Station A",    lbp + 1.500,         "Stem Overhang",  0.2418, "Stem Overhang (+1.50 m fwd of FP)"),
        ("Station B",    lbp + 3.000,         "Foremost Apex",  0.0,    "Foremost Tip (+3.00 m fwd of FP, B=0)")
    ]

    # Filter by start_station and end_station if provided
    if start_station or end_station:
        st_names = [st[0].replace("Station ", "").replace(" (FP)", "").strip() for st in default_offsets]
        idx_start = 0
        idx_end = len(default_offsets) - 1
        if start_station:
            clean_start = str(start_station).replace("Station ", "").strip()
            if clean_start in st_names:
                idx_start = st_names.index(clean_start)
        if end_station:
            clean_end = str(end_station).replace("Station ", "").strip()
            if clean_end in st_names:
                idx_end = st_names.index(clean_end)
        if idx_start <= idx_end:
            default_offsets = default_offsets[idx_start:idx_end + 1]

    rows = []
    sum_products = 0.0

    # Extract dynamically from parsed_data using selected column_name
    hb_table = parsed_data.get("half_breadths", {})

    for st_name, x_pos, st_type, factor, rem in default_offsets:
        raw_st = st_name.replace("Station ", "").replace(" (FP)", "").strip()
        st_dict = hb_table.get(raw_st, {})

        # 1. First priority: Exact match on selected column_name
        hb_val = None
        if column_name and column_name in st_dict:
            hb_val = st_dict[column_name]
        
        # 2. Second priority: search column_name case-insensitively
        if hb_val is None and column_name:
            c_low = column_name.lower()
            for k, v in st_dict.items():
                if k.lower() == c_low or c_low in k.lower():
                    hb_val = v
                    break

        # 3. Third priority: look for forecastle or upper deck
        if hb_val is None:
            for k, v in st_dict.items():
                if "forecastle" in k.lower() or "upper deck" in k.lower():
                    hb_val = v
                    break

        # If found as integer/float mm, convert to meters
        hb_m = 0.0
        if isinstance(hb_val, (int, float)):
            hb_m = (hb_val / 1000.0) if hb_val > 50 else float(hb_val)
        elif isinstance(hb_val, list) and len(hb_val) > 0 and isinstance(hb_val[0], (int, float)):
            hb_m = (hb_val[0] / 1000.0) if hb_val[0] > 50 else float(hb_val[0])

        b_m = 2.0 * hb_m
        area_m2 = b_m * imported_height
        product = area_m2 * factor
        sum_products += product

        rows.append({
            "station": st_name,
            "station_type": st_type,
            "position_x": round(x_pos, 3),
            "half_breadth_m": round(hb_m, 3),
            "breadth_m": round(b_m, 3),
            "height_m": round(imported_height, 3),
            "area_m2": round(area_m2, 3),
            "factor": factor,
            "product": round(product, 3),
            "remark": rem
        })

    # Longitudinal integration using standard (dx / 3) factor:
    dx_over_3 = dx_standard / 3.0
    forecastle_volume = dx_over_3 * sum_products
    forecastle_tonnage = forecastle_volume / SUEZ_TON_M3

    # Direct sub-interval breakdowns for engineering transparency
    if len(rows) >= 8:
        a18 = rows[1]["area_m2"]
        a18_5 = rows[2]["area_m2"]
        a19 = rows[3]["area_m2"]
        a19_5 = rows[4]["area_m2"]
        a20 = rows[5]["area_m2"]
        a_a = rows[6]["area_m2"]
        a_b = rows[7]["area_m2"]

        vol_body = (dx_half / 3.0) * (a18 * 1.0 + a18_5 * 4.0 + a19 * 2.0 + a19_5 * 4.0 + a20 * 1.0)
        vol_overhang = (1.500 / 2.0) * (a20 + a_a)
        vol_apex = (1.500 / 2.0) * (a_a + a_b)
    else:
        vol_body = forecastle_volume
        vol_overhang = 0.0
        vol_apex = 0.0

    return {
        "imported_height": round(imported_height, 3),
        "dx_standard": round(dx_standard, 3),
        "dx_over_3": round(dx_over_3, 4),
        "sum_products": round(sum_products, 3),
        "forecastle_volume": round(forecastle_volume, 3),
        "forecastle_tonnage": round(forecastle_tonnage, 2),
        "rows": rows,
        "breakdown": {
            "body_volume": round(vol_body, 3),
            "body_tonnage": round(vol_body / SUEZ_TON_M3, 2),
            "overhang_volume": round(vol_overhang, 3),
            "overhang_tonnage": round(vol_overhang / SUEZ_TON_M3, 2),
            "apex_volume": round(vol_apex, 3),
            "apex_tonnage": round(vol_apex / SUEZ_TON_M3, 2),
        }
    }
