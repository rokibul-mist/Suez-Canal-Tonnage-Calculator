"""
Superstructure & Round Houses Tonnage Engine
Computes volume and Suez Moorsom Tonnage for all enclosed deckhouses, round houses, and compartments.
Classifies spaces into Gross Tonnage additions and Statutory Net Tonnage deductions:
  - OFFICER'S ACCOMMODATION
  - CREW'S ACCOMMODATION
  - USED IN WORKING THE SHIP
  - DEDUCTION FOR PROPELLING POWER
Complies strictly with Suez Canal Authority (SCA) Rules of Navigation.
100% pure standard ASCII English encoding.
"""

# Official SCA conversion constant: 1 Suez Ton = 100 cu.ft = 2.832 m3
SUEZ_TON_M3 = 2.832
import os
import openpyxl

DEFAULT_SUPERSTRUCTURE_SPACES = [
    {"deck_level": "Upper Platform", "space_group": "Steering Gear Room", "qty": 1, "length_m": 16.61, "breadth_m": 7.09, "height_m": 2.50, "form_factor": 0.88, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Upper Platform", "space_group": "Purifier Room", "qty": 1, "length_m": 9.88, "breadth_m": 9.74, "height_m": 2.50, "form_factor": 0.92, "deduction_category": "DEDUCTION FOR PROPELLING POWER", "action": "addition"},
    {"deck_level": "Upper Platform", "space_group": "Engine Control Room", "qty": 1, "length_m": 9.69, "breadth_m": 5.52, "height_m": 2.50, "form_factor": 1.00, "deduction_category": "DEDUCTION FOR PROPELLING POWER", "action": "addition"},
    {"deck_level": "Upper Platform", "space_group": "Spare Parts Room", "qty": 1, "length_m": 6.46, "breadth_m": 4.55, "height_m": 2.50, "form_factor": 1.00, "deduction_category": "DEDUCTION FOR PROPELLING POWER", "action": "addition"},
    {"deck_level": "Upper Platform", "space_group": "Workshop", "qty": 1, "length_m": 8.00, "breadth_m": 4.55, "height_m": 2.50, "form_factor": 1.00, "deduction_category": "DEDUCTION FOR PROPELLING POWER", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "CO2 Room", "qty": 1, "length_m": 6.86, "breadth_m": 6.13, "height_m": 2.40, "form_factor": 0.85, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Gymnasium / Recreation", "qty": 1, "length_m": 6.77, "breadth_m": 3.88, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Laundry / Drying Room", "qty": 1, "length_m": 4.81, "breadth_m": 2.25, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "WC / Lavatory", "qty": 1, "length_m": 1.96, "breadth_m": 2.25, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Deck Office", "qty": 1, "length_m": 4.14, "breadth_m": 4.07, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Seaman Cabins", "qty": 4, "length_m": 3.32, "breadth_m": 4.14, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Motorman Cabins", "qty": 2, "length_m": 3.14, "breadth_m": 4.14, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "A.C. Room", "qty": 1, "length_m": 6.03, "breadth_m": 5.55, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "DEDUCTION FOR PROPELLING POWER", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Dry Provision Store", "qty": 1, "length_m": 6.29, "breadth_m": 3.17, "height_m": 2.40, "form_factor": 0.90, "deduction_category": "NONE", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Meat Store -18C", "qty": 1, "length_m": 4.87, "breadth_m": 2.18, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "NONE", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Fish Store -18C", "qty": 1, "length_m": 4.87, "breadth_m": 2.18, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "NONE", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Vegetable Store +4C", "qty": 1, "length_m": 6.29, "breadth_m": 2.50, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "NONE", "action": "addition"},
    {"deck_level": "Upper Deck", "space_group": "Chief Engineer Office / Day Room", "qty": 1, "length_m": 4.87, "breadth_m": 3.59, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "General Store", "qty": 1, "length_m": 1.48, "breadth_m": 6.09, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "NONE", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Fire-Fighting Store", "qty": 1, "length_m": 3.14, "breadth_m": 6.09, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Boat Store", "qty": 1, "length_m": 0.80, "breadth_m": 2.85, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Crew Mess / Lounge", "qty": 1, "length_m": 7.89, "breadth_m": 6.06, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Hospital", "qty": 1, "length_m": 3.94, "breadth_m": 4.30, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Motorman Cabins", "qty": 2, "length_m": 3.95, "breadth_m": 4.30, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Galley", "qty": 1, "length_m": 7.09, "breadth_m": 6.06, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Cook Cabin", "qty": 1, "length_m": 3.94, "breadth_m": 4.30, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Seaman Cabins", "qty": 2, "length_m": 3.96, "breadth_m": 4.30, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Officers' Mess / Lounge", "qty": 1, "length_m": 4.78, "breadth_m": 6.06, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Accommodation Deck", "space_group": "Seaman Cabins", "qty": 3, "length_m": 3.33, "breadth_m": 5.26, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Accommodation Deck", "space_group": "Ordinary Store", "qty": 1, "length_m": 1.64, "breadth_m": 5.26, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "NONE", "action": "addition"},
    {"deck_level": "Accommodation Deck", "space_group": "Electrician Cabin", "qty": 1, "length_m": 3.88, "breadth_m": 5.26, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Accommodation Deck", "space_group": "Chief Motorman Cabin", "qty": 1, "length_m": 3.94, "breadth_m": 5.26, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Accommodation Deck", "space_group": "2nd Engineer Suite", "qty": 1, "length_m": 7.86, "breadth_m": 4.33, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Accommodation Deck", "space_group": "3rd Engineer Cabin", "qty": 1, "length_m": 3.85, "breadth_m": 4.33, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Accommodation Deck", "space_group": "Boatswain Cabin", "qty": 1, "length_m": 3.91, "breadth_m": 4.33, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "CREW'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Accommodation Deck", "space_group": "Chief Officer Suite", "qty": 1, "length_m": 7.82, "breadth_m": 4.33, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Captain Deck", "space_group": "4th Engineer Cabin", "qty": 1, "length_m": 4.01, "breadth_m": 5.20, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Captain Deck", "space_group": "Crew / Officer Office", "qty": 1, "length_m": 2.44, "breadth_m": 5.20, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Captain Deck", "space_group": "Linen / Ordinary Store", "qty": 1, "length_m": 1.44, "breadth_m": 5.20, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "NONE", "action": "addition"},
    {"deck_level": "Captain Deck", "space_group": "Pilot Cabin", "qty": 1, "length_m": 4.01, "breadth_m": 5.20, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Captain Deck", "space_group": "3rd Officer Cabin", "qty": 1, "length_m": 3.94, "breadth_m": 5.20, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Captain Deck", "space_group": "2nd Officer Cabin", "qty": 1, "length_m": 3.85, "breadth_m": 5.20, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Captain Deck", "space_group": "Chief Engineer Suite", "qty": 1, "length_m": 7.93, "breadth_m": 4.33, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Captain Deck", "space_group": "Meeting Room", "qty": 1, "length_m": 7.79, "breadth_m": 4.33, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Captain Deck", "space_group": "Captain Suite", "qty": 1, "length_m": 7.83, "breadth_m": 4.33, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "OFFICER'S ACCOMMODATION", "action": "addition"},
    {"deck_level": "Bridge Deck", "space_group": "Radio Room", "qty": 1, "length_m": 3.62, "breadth_m": 2.40, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Bridge Deck", "space_group": "Chart Rooms (combined)", "qty": 1, "length_m": 3.62, "breadth_m": 3.93, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Bridge Deck", "space_group": "Battery Room (radio/navigation)", "qty": 1, "length_m": 1.89, "breadth_m": 1.60, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Bridge Deck", "space_group": "Ordinary Store", "qty": 1, "length_m": 1.89, "breadth_m": 2.37, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "NONE", "action": "addition"},
    {"deck_level": "Bridge Deck", "space_group": "Wheelhouse (net)", "qty": 1, "length_m": 15.14, "breadth_m": 5.49, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "USED IN WORKING THE SHIP", "action": "addition"},
    {"deck_level": "Boat Deck", "space_group": "Engine Casing (measured segment)", "qty": 1, "length_m": 7.76, "breadth_m": 7.47, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "DEDUCTION FOR PROPELLING POWER", "action": "addition"},
    {"deck_level": "Accom. & Capt. Decks", "space_group": "Funnel Casing", "qty": 2, "length_m": 7.86, "breadth_m": 5.45, "height_m": 2.40, "form_factor": 1.00, "deduction_category": "DEDUCTION FOR PROPELLING POWER", "action": "addition"},
    {"deck_level": "Unresolved", "space_group": "Refrigerating Machinery Room", "qty": 1, "length_m": 0.00, "breadth_m": 0.00, "height_m": 0.00, "form_factor": 1.00, "deduction_category": "DEDUCTION FOR PROPELLING POWER", "action": "addition"}
]

def classify_deduction_category(space_name, nt_deduction=None):
    name = str(space_name).upper().strip()
    nt = str(nt_deduction).upper().strip() if nt_deduction else ""

    if nt == "NO" or "NOT AUTOMATIC" in nt:
        return "NONE"

    if "MACHINERY" in nt or any(k in name for k in ["ENGINE", "PURIFIER", "WORKSHOP", "SPARE PARTS", "FUNNEL", "REFRIGERATING"]):
        return "DEDUCTION FOR PROPELLING POWER"

    if any(k in name for k in ["OFFICER", "CAPTAIN", "ENGINEER"]):
        return "OFFICER'S ACCOMMODATION"

    if any(k in name for k in ["WHEELHOUSE", "CHART", "RADIO", "BATTERY", "STEERING", "CO2", "CO2", "FIRE-FIGHTING", "DECK OFFICE", "PILOT", "BOAT STORE"]):
        return "USED IN WORKING THE SHIP"

    if any(k in name for k in ["SEAMAN", "MOTORMAN", "BOATSWAIN", "ELECTRICIAN", "COOK", "MESS", "LOUNGE", "GALLEY", "HOSPITAL", "WC", "LAVATORY", "LAUNDRY", "DRYING", "GYMNASIUM", "RECREATION"]):
        return "CREW'S ACCOMMODATION"

    if "DEDUCT" in nt:
        return "USED IN WORKING THE SHIP"

    return "NONE"

def calculate_superstructure_tonnage(spaces_list=None, fallback_to_default=False):
    """
    Calculates Volume and Moorsom Tonnage:
      - Volume = Qty * L * B * H * Form Factor
      - Moorsom Tonnage = Volume / SUEZ_TON_M3
      - Aggregates Round Houses Volume & Tonnage (added to Gross Tonnage)
      - Breaks down Deductions into Certificate categories:
        1. OFFICER'S ACCOMMODATION
        2. CREW'S ACCOMMODATION
        3. USED IN WORKING THE SHIP
        4. DEDUCTION FOR PROPELLING POWER
    """
    if spaces_list is not None:
        items = spaces_list
    elif fallback_to_default:
        items = DEFAULT_SUPERSTRUCTURE_SPACES
    else:
        items = []

    rows = []
    tot_round_houses_vol = 0.0
    tot_round_houses_ton = 0.0

    cat_vols = {
        "OFFICER'S ACCOMMODATION": 0.0,
        "CREW'S ACCOMMODATION": 0.0,
        "USED IN WORKING THE SHIP": 0.0,
        "DEDUCTION FOR PROPELLING POWER": 0.0,
        "NONE": 0.0
    }

    for idx, s in enumerate(items, start=1):
        deck = str(s.get("deck_level", "Upper Deck")).strip()
        group = str(s.get("space_group", f"Space No. {idx}")).strip()
        qty = int(s.get("qty", 1) or 1)
        l = float(s.get("length_m", 0.0) or 0.0)
        b = float(s.get("breadth_m", 0.0) or 0.0)
        h = float(s.get("height_m", 0.0) or 0.0)
        factor = float(s.get("form_factor", 1.0) or 1.0)
        action = str(s.get("action", "addition")).strip().lower()
        if action not in ["addition", "deduction"]:
            action = "addition"

        cat = s.get("deduction_category")
        if not cat or cat not in cat_vols:
            cat = classify_deduction_category(group, s.get("nt_deduction"))

        vol = round(qty * l * b * h * factor, 3)
        ton = round(vol / SUEZ_TON_M3, 2) if vol > 0 else 0.0

        # All enclosed spaces form the Round Houses / Superstructure addition to Gross Tonnage
        tot_round_houses_vol += vol
        tot_round_houses_ton += ton

        if cat in cat_vols:
            cat_vols[cat] += vol

        rows.append({
            "no": idx,
            "deck_level": deck,
            "space_group": group,
            "qty": qty,
            "length_m": round(l, 2),
            "breadth_m": round(b, 2),
            "height_m": round(h, 2),
            "form_factor": round(factor, 3),
            "volume_m3": vol,
            "deduction_category": cat,
            "action": action,
            "tonnage": ton
        })

    officer_vol = round(cat_vols["OFFICER'S ACCOMMODATION"], 2)
    officer_ton = round(officer_vol / SUEZ_TON_M3, 2)

    crew_vol = round(cat_vols["CREW'S ACCOMMODATION"], 2)
    crew_ton = round(crew_vol / SUEZ_TON_M3, 2)

    working_vol = round(cat_vols["USED IN WORKING THE SHIP"], 2)
    working_ton = round(working_vol / SUEZ_TON_M3, 2)

    propelling_vol = round(cat_vols["DEDUCTION FOR PROPELLING POWER"], 2)
    propelling_ton = round(propelling_vol / SUEZ_TON_M3, 2)

    tot_ded_vol = round(officer_vol + crew_vol + working_vol + propelling_vol, 2)
    tot_ded_ton = round(officer_ton + crew_ton + working_ton + propelling_ton, 2)

    net_vol = round(tot_round_houses_vol - tot_ded_vol, 2)
    net_ton = round(tot_round_houses_ton - tot_ded_ton, 2)

    return {
        "num_spaces": len(rows),
        "rows": rows,
        "round_houses_volume": round(tot_round_houses_vol, 2),
        "round_houses_tonnage": round(tot_round_houses_ton, 2),
        "total_addition_volume": round(tot_round_houses_vol, 2),
        "total_addition_tonnage": round(tot_round_houses_ton, 2),
        "officer_accommodation_volume": officer_vol,
        "officer_accommodation_tonnage": officer_ton,
        "crew_accommodation_volume": crew_vol,
        "crew_accommodation_tonnage": crew_ton,
        "working_ship_volume": working_vol,
        "working_ship_tonnage": working_ton,
        "propelling_power_volume": propelling_vol,
        "propelling_power_tonnage": propelling_ton,
        "total_deduction_volume": tot_ded_vol,
        "total_deduction_tonnage": tot_ded_ton,
        "net_volume": net_vol,
        "net_tonnage": net_ton
    }

def parse_superstructure_excel(file_path_or_stream):
    """
    Parses a user-uploaded Excel workbook (such as Suez_Tonnage_Superstructure_Volumes.xlsx
    or exported template) and returns a list of standardized space dictionaries.
    """
    wb = openpyxl.load_workbook(file_path_or_stream, data_only=True)
    ws = None
    for name in ["Volume Calculator", "Superstructures", "Sheet1"]:
        if name in wb.sheetnames:
            ws = wb[name]
            break
    if ws is None:
        ws = wb.active

    spaces = []
    # Find header row
    header_row = 1
    for r in range(1, 10):
        c2 = str(ws.cell(row=r, column=2).value or "").lower()
        c4 = str(ws.cell(row=r, column=4).value or "").lower()
        if "space" in c2 or "length" in c4:
            header_row = r
            break

    for r in range(header_row + 1, ws.max_row + 1):
        space_name = ws.cell(row=r, column=2).value
        if not space_name or str(space_name).strip().startswith("Volume Summary") or str(space_name).strip().startswith("Total"):
            continue

        deck = ws.cell(row=r, column=1).value or "Upper Deck"
        qty = ws.cell(row=r, column=3).value or 1
        l = ws.cell(row=r, column=4).value or 0.0
        b = ws.cell(row=r, column=5).value or 0.0
        h = ws.cell(row=r, column=6).value or 0.0
        k = ws.cell(row=r, column=7).value or 1.0
        gt_treat = ws.cell(row=r, column=10).value or "ADD"
        nt_ded = ws.cell(row=r, column=11).value or "DEDUCT"

        try:
            qty_val = int(qty)
        except Exception:
            qty_val = 1

        try:
            l_val = float(l)
            b_val = float(b)
            h_val = float(h)
            k_val = float(k)
        except Exception:
            l_val, b_val, h_val, k_val = 0.0, 0.0, 0.0, 1.0

        cat = classify_deduction_category(space_name, nt_ded)

        spaces.append({
            "deck_level": str(deck).strip(),
            "space_group": str(space_name).strip(),
            "qty": qty_val,
            "length_m": round(l_val, 2),
            "breadth_m": round(b_val, 2),
            "height_m": round(h_val, 2),
            "form_factor": round(k_val, 3),
            "deduction_category": cat,
            "action": "addition"
        })

    return spaces
