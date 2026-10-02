"""
Bulbous Bow Calculation Engine
Computes cross-sectional areas using buttock cutting lines (C.L., 1000BL, 2000BL)
and longitudinal integration across the bulbous bow length.

SCA Method A (Ship Drawing Exact Geometry):
  - Body volume: V_body = (dx_body / 3) x (A_20*1 + A_A*4 + A_B*1)
  - Nose cap (conical): V_nose = (pi / 6) x A_B x L_nose
  - 1 Suez Ton = 2.832 m3
"""
import math

# Official SCA conversion constant: 1 Suez Ton = 100 cu.ft = 2.832 m3
SUEZ_TON_M3 = 2.832

DEFAULT_BULB_DATA = {
    "st20": {
        "title": "Station 20 (FP)",
        "x_pos": 0.000,
        "cl":   {"up": 10.700, "low": 0.701},
        "b1000":{"up": 9.223,  "low": 1.064},
        "b2000":{"up": 8.388,  "low": 1.734},
    },
    "stA": {
        "title": "Station A",
        "x_pos": 1.500,
        "cl":   {"up": 8.795,  "low": 1.312},
        "b1000":{"up": 8.252,  "low": 1.846},
        "b2000":{"up": 7.173,  "low": 2.988},
    },
    "stB": {
        "title": "Station B",
        "x_pos": 3.000,
        "cl":   {"up": 8.133,  "low": 2.224},
        "b1000":{"up": 7.148,  "low": 3.201},
        "b2000":{"up": 0.000,  "low": 0.000}, # bulb inside 1576 mm half-breadth
    }
}

def calculate_station_bulb_area(st_key, st_dict, dy=1.000):
    """
    Calculates transverse bulb area using Simpson's 1st Rule cutting buttocks.
    Supports either dynamic buttocks list or default CL, 1000BL, 2000BL.
    """
    dy_over_3 = dy / 3.0
    
    if "buttocks" in st_dict and st_dict["buttocks"]:
        raw_buttocks = st_dict["buttocks"]
        buttocks = []
        for b in raw_buttocks:
            name = b.get("name", "Buttock")
            y_m = float(b.get("y_m", b.get("y", 0.0)))
            z_up = float(b.get("z_upper", b.get("up", 0.0)))
            z_low = float(b.get("z_lower", b.get("low", 0.0)))
            factor = float(b.get("factor", b.get("multiplier", 1)))
            buttocks.append((name, y_m, z_up, z_low, factor))
    else:
        cl_data = st_dict.get("cl", {})
        b1_data = st_dict.get("b1000", {})
        b2_data = st_dict.get("b2000", {})
        buttocks = [
            ("Centerline (C.L.)", 0.000, float(cl_data.get("up", 0.0)), float(cl_data.get("low", 0.0)), 1),
            ("1000 B.L.",         1.000, float(b1_data.get("up", 0.0)), float(b1_data.get("low", 0.0)), 4),
            ("2000 B.L.",         2.000, float(b2_data.get("up", 0.0)), float(b2_data.get("low", 0.0)), 1),
        ]

    rows = []
    sum_prod = 0.0

    for name, y_m, z_up, z_low, factor in buttocks:
        depth = max(0.0, z_up - z_low)
        prod = depth * factor
        sum_prod += prod

        rows.append({
            "name": name,
            "y_m": y_m,
            "y": y_m,
            "z_upper": round(z_up, 3),
            "z_lower": round(z_low, 3),
            "z": round(z_up, 3),
            "depth_m": round(depth, 3),
            "depth": round(depth, 3),
            "half_breadth": round(depth / 2.0, 3),
            "full_breadth": round(depth, 3),
            "factor": factor,
            "multiplier": factor,
            "product": round(prod, 3)
        })

    half_area = dy_over_3 * sum_prod
    total_area = 2.0 * half_area

    title = st_dict.get("title", f"Station {st_key}")
    x_pos = float(st_dict.get("x_pos", 0.0))

    return {
        "title": title,
        "name": title,
        "x_pos": x_pos,
        "dy": dy,
        "dy_over_3": round(dy_over_3, 4),
        "sum_prod": round(sum_prod, 3),
        "sum_products": round(sum_prod, 3),
        "half_area": round(half_area, 3),
        "total_area": round(total_area, 3),
        "rows": rows,
        "points": rows
    }

def get_empty_bulbous_results(has_bulbous=True):
    return {
        "has_bulbous": has_bulbous,
        "l_bulb": 0.0,
        "dx_body": 0.0,
        "l_nose": 0.0,
        "dy": 0.0,
        "method_A": {
            "name": "Method A (Ship Drawing Exact Geometry)",
            "body_interval": 0.0,
            "body_rows": [],
            "body_sum": 0.0,
            "body_volume": 0.0,
            "nose_volume": 0.0,
            "total_volume": 0.0,
            "tonnage": 0.0,
        },
        "method_B": {
            "name": "Method B (Standard SCA Equal Division over 5.0m)",
            "interval": 0.0,
            "sum": 0.0,
            "total_volume": 0.0,
            "tonnage": 0.0,
            "products": []
        },
        "method_C": {
            "name": "Method C (Forward Extension from St. A to Tip)",
            "interval": 0.0,
            "sum": 0.0,
            "total_volume": 0.0,
            "tonnage": 0.0
        },
        "areas": {
            "st20": {"title": "Station 20 (FP)", "total_area": 0.0, "sum_products": 0.0, "rows": []},
            "stA":  {"title": "Station A",       "total_area": 0.0, "sum_products": 0.0, "rows": []},
            "stB":  {"title": "Station B",       "total_area": 0.0, "sum_products": 0.0, "rows": []},
        },
        "transverse_stations": {
            "st20": {"title": "Station 20 (FP)", "total_area": 0.0, "sum_products": 0.0, "rows": []},
            "stA":  {"title": "Station A",       "total_area": 0.0, "sum_products": 0.0, "rows": []},
            "stB":  {"title": "Station B",       "total_area": 0.0, "sum_products": 0.0, "rows": []},
        }
    }

def extract_bulbous_data_from_offsets(
    parsed_data,
    st1="20", st2="A", st3="B",
    bt1="C.L.", bt2="1000 B.L.", bt3="2000 B.L.",
    dy=1.000, dx_body=1.500
):
    """
    Extracts transverse bulb cutting coordinates from parsed offset table.
    Looks in heights and half_breadths for specified stations and buttocks.
    Supports composite values like [701, 10700], '701/10700', or numeric heights.
    """
    if not parsed_data:
        return None

    hts = parsed_data.get("heights", {})
    hbs = parsed_data.get("half_breadths", {})

    def parse_cell(val):
        if val is None or val == "":
            return {"up": 0.0, "low": 0.0}
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            try:
                p0 = float(val[0])
                p1 = float(val[1])
                l_m = p0 / 1000.0 if p0 > 50 else p0
                u_m = p1 / 1000.0 if p1 > 50 else p1
                return {"low": min(l_m, u_m), "up": max(l_m, u_m)}
            except (ValueError, TypeError):
                pass
        if isinstance(val, (int, float)):
            v = float(val)
            return {"up": v / 1000.0 if v > 50 else v, "low": 0.0}
        s = str(val).strip()
        if "/" in s:
            parts = s.split("/")
            try:
                p0 = float(parts[0].strip() or 0)
                p1 = float(parts[1].strip() or 0)
                low_m = p0 / 1000.0 if p0 > 50 else p0
                up_m = p1 / 1000.0 if p1 > 50 else p1
                return {"low": min(low_m, up_m), "up": max(low_m, up_m)}
            except (ValueError, TypeError):
                pass
        try:
            v = float(s)
            return {"up": v / 1000.0 if v > 50 else v, "low": 0.0}
        except ValueError:
            return {"up": 0.0, "low": 0.0}

    def get_cell(st, bt):
        st_clean = str(st).replace("Station ", "").replace(" (FP)", "").strip()
        # Search heights table
        for s_key in [st_clean, f"Station {st_clean}", str(st)]:
            if s_key in hts:
                st_map = hts[s_key]
                for b_cand in [bt, bt.replace(" ", ""), bt.lower()]:
                    for k, v in st_map.items():
                        if k.lower() == b_cand.lower() or b_cand.lower() in k.lower():
                            if v not in [None, ""]:
                                return parse_cell(v)
        # Search half_breadths table as secondary
        for s_key in [st_clean, f"Station {st_clean}", str(st)]:
            if s_key in hbs:
                st_map = hbs[s_key]
                for b_cand in [bt, bt.replace(" ", ""), bt.lower()]:
                    for k, v in st_map.items():
                        if k.lower() == b_cand.lower() or b_cand.lower() in k.lower():
                            if v not in [None, ""]:
                                return parse_cell(v)
        return {"up": 0.0, "low": 0.0}

    st_keys = [st1, st2, st3]
    bt_keys = [bt1, bt2, bt3]
    multipliers = [1, 4, 1]

    data = {}
    total_non_zero = 0.0
    for idx, st in enumerate(st_keys):
        st_id = ["st20", "stA", "stB"][idx]
        title = f"Station {st}"
        x_pos = 0.0 if idx == 0 else (dx_body * idx)
        buttocks = []
        for b_idx, bt in enumerate(bt_keys):
            cell = get_cell(st, bt)
            depth = max(0.0, cell["up"] - cell["low"])
            total_non_zero += depth
            buttocks.append({
                "name": bt,
                "y_m": b_idx * dy,
                "up": round(cell["up"], 3),
                "low": round(cell["low"], 3),
                "factor": multipliers[b_idx]
            })
        data[st_id] = {
            "title": title,
            "x_pos": x_pos,
            "buttocks": buttocks
        }

    if total_non_zero <= 0.0:
        return None

    return data

def calculate_bulbous_bow_tonnage(
    l_bulb=5.000,
    dx_body=1.500,
    l_nose=2.000,
    dy=1.000,
    custom_data=None,
    parsed_data=None,
    has_bulbous=True,
    fallback_to_default=False
):
    """
    Performs complete bulbous bow calculation:
      - Option for whether the vessel has a bulbous bow or not (has_bulbous)
      - Transverse areas for St. 20, St. A, St. B (or selected stations)
      - Extracts directly from parsed_data (Offset Table) if custom_data is omitted.
      - NEVER falls back to default values unless fallback_to_default=True.
    """
    if not has_bulbous:
        return get_empty_bulbous_results(has_bulbous=False)

    data = None
    if custom_data:
        data = custom_data
    elif parsed_data:
        data = extract_bulbous_data_from_offsets(parsed_data, dy=dy, dx_body=dx_body)

    if not data:
        if fallback_to_default:
            data = DEFAULT_BULB_DATA
        else:
            return get_empty_bulbous_results(has_bulbous=True)

    keys = list(data.keys())
    k1 = "st20" if "st20" in data else keys[0]
    k2 = "stA"  if "stA" in data  else (keys[1] if len(keys) > 1 else k1)
    k3 = "stB"  if "stB" in data  else (keys[2] if len(keys) > 2 else k2)

    area_20 = calculate_station_bulb_area(k1, data[k1], dy=dy)
    area_A  = calculate_station_bulb_area(k2, data[k2], dy=dy)
    area_B  = calculate_station_bulb_area(k3, data[k3], dy=dy)

    a20 = area_20["total_area"]
    aA  = area_A["total_area"]
    aB  = area_B["total_area"]

    t1 = area_20.get("title", "Station 20 (FP)")
    t2 = area_A.get("title",  "Station A")
    t3 = area_B.get("title",  "Station B")

    # -------------------------------------------------------------
    # Method A: Ship Drawing Exact Geometry (St. 20 to B + Nose Cap)
    # -------------------------------------------------------------
    body_products = [
        {"st": t1, "x": area_20.get("x_pos", 0.000), "area": a20, "factor": 1, "prod": round(a20 * 1, 3)},
        {"st": t2, "x": area_A.get("x_pos", dx_body), "area": aA,  "factor": 4, "prod": round(aA * 4, 3)},
        {"st": t3, "x": area_B.get("x_pos", dx_body * 2.0), "area": aB,  "factor": 1, "prod": round(aB * 1, 3)},
    ]
    body_sum = a20 * 1 + aA * 4 + aB * 1
    body_volume = (dx_body / 3.0) * body_sum

    # Nose cap (SCA Method A: conical/parabolic terminal cap)
    # Formula: V_nose = (pi / 6) x A_B x L_nose  [SCA Appendix 1]
    nose_volume = (math.pi / 6.0) * aB * l_nose

    total_volume_A = body_volume + nose_volume
    tonnage_A = total_volume_A / SUEZ_TON_M3

    # -------------------------------------------------------------
    # Method B: Standard SCA 3-Station Equal Division over full bulb length
    # Uses same stations but equal spacing over l_bulb
    # -------------------------------------------------------------
    dx_B = l_bulb / 2.0  # Equal spacing for 3-point Simpson
    sum_B = a20 * 1 + aA * 4 + aB * 1
    total_volume_B = (dx_B / 3.0) * sum_B
    tonnage_B = total_volume_B / SUEZ_TON_M3

    # -------------------------------------------------------------
    # Method C: Forward Extension from Station A to tip (2 intervals)
    # -------------------------------------------------------------
    sum_C = aA * 1 + aB * 4 + 0.0 * 1
    total_volume_C = (dx_B / 3.0) * sum_C
    tonnage_C = total_volume_C / SUEZ_TON_M3

    return {
        "has_bulbous": True,
        "l_bulb": l_bulb,
        "dx_body": dx_body,
        "l_nose": l_nose,
        "dy": dy,
        "areas": {
            "st20": area_20,
            "stA": area_A,
            "stB": area_B,
        },
        "transverse_stations": {
            "St_20": area_20,
            "St_A":  area_A,
            "St_B":  area_B,
            "st20":  area_20,
            "stA":   area_A,
            "stB":   area_B,
        },
        "method_A": {
            "name": "Method A (Ship Drawing Exact Geometry)",
            "body_interval": dx_body,
            "body_rows": body_products,
            "body_sum": round(body_sum, 3),
            "body_volume": round(body_volume, 3),
            "nose_volume": round(nose_volume, 3),
            "total_volume": round(total_volume_A, 3),
            "tonnage": round(tonnage_A, 2),
        },
        "method_B": {
            "name": "Method B (Standard SCA Equal Division over 5.0m)",
            "interval": round(dx_B, 3),
            "sum": round(sum_B, 3),
            "total_volume": round(total_volume_B, 3),
            "tonnage": round(tonnage_B, 2),
        },
        "method_C": {
            "name": "Method C (Forward Extension from St. A to Tip)",
            "interval": round(dx_B, 3),
            "sum": round(sum_C, 3),
            "total_volume": round(total_volume_C, 3),
            "tonnage": round(tonnage_C, 2),
        }
    }
