"""
Hatch Coaming Calculation Engine
Computes enclosed volume and Suez Moorsom Tonnage for cargo hatchways and coamings.
Complies with Suez Canal Authority (SCA) Rules of Navigation (0.5% / 5 per 1000 statutory allowance rule).
100% pure standard ASCII English encoding.
"""

# Official SCA conversion constant: 1 Suez Ton = 100 cu.ft = 2.832 m3
SUEZ_TON_M3 = 2.832

DEFAULT_HATCHES = [
    {"name": "No. 1 Cargo Hatchway", "length": 15.20, "breadth": 14.00, "height": 1.80},
    {"name": "No. 2 Cargo Hatchway", "length": 17.60, "breadth": 16.00, "height": 1.80},
    {"name": "No. 3 Cargo Hatchway", "length": 17.60, "breadth": 16.00, "height": 1.80},
    {"name": "No. 4 Cargo Hatchway", "length": 17.60, "breadth": 16.00, "height": 1.80},
    {"name": "No. 5 Cargo Hatchway", "length": 17.60, "breadth": 16.00, "height": 1.80},
]

def calculate_hatch_coamings(hatches_list=None, pre_hatch_gross_tonnage=32500.0):
    """
    Calculates volume and Moorsom tonnage for each cargo hatch coaming:
      - Volume = Length x Breadth x Height
      - Moorsom Tonnage = Volume / SUEZ_TON_M3
      - Total Aggregate Hatchway Volume & Tonnage
      - Statutory 0.5% (5/1000) Allowance = 0.005 x Pre-Hatch Gross Tonnage
      - Excess Hatchway Tonnage added to Gross = max(0.0, Total Tonnage - Allowance)
    """
    items = hatches_list if hatches_list is not None else DEFAULT_HATCHES

    rows = []
    total_volume = 0.0
    total_tonnage = 0.0

    for idx, h in enumerate(items, start=1):
        name = h.get("name") or f"No. {idx} Cargo Hatchway"
        l = float(h.get("length", 0.0))
        b = float(h.get("breadth", 0.0))
        ht = float(h.get("height", 0.0))

        vol = l * b * ht
        ton = vol / SUEZ_TON_M3 if vol > 0 else 0.0

        total_volume += vol
        total_tonnage += ton

        rows.append({
            "no": idx,
            "name": name,
            "length_m": round(l, 3),
            "breadth_m": round(b, 3),
            "height_m": round(ht, 3),
            "volume_m3": round(vol, 3),
            "tonnage": round(ton, 2)
        })

    allowance_tonnage = round(pre_hatch_gross_tonnage * 0.005, 2)
    excess_tonnage = round(max(0.0, total_tonnage - allowance_tonnage), 2)
    excess_volume = round(excess_tonnage * SUEZ_TON_M3, 2)

    return {
        "num_hatches": len(rows),
        "rows": rows,
        "total_volume": round(total_volume, 3),
        "total_tonnage": round(total_tonnage, 2),
        "pre_hatch_gross_tonnage": round(pre_hatch_gross_tonnage, 2),
        "allowance_tonnage": allowance_tonnage,
        "excess_tonnage": excess_tonnage,
        "excess_volume": excess_volume
    }
