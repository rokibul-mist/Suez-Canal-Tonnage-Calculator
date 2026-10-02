"""
Simpson Calculation Engine for Suez Canal Under Deck Tonnage (UDT)
Performs transverse Simpson integration across waterlines and longitudinal integration across stations.

SCA Rule Reference:
  - 1 Suez Ton = 100 cubic feet = 2.832 m3 (official SCA Moorsom System)
  - Longitudinal: 21 stations, spacing dx = LBP / 20, factors [1,4,2,...,4,1]
  - Transverse: Simpson's 1st Rule across waterlines, h = D / (n-1)
"""

# Official SCA conversion constant: 1 Suez Ton = 100 cu.ft = 2.832 m3
SUEZ_TON_M3 = 2.832

def generate_simpson_1st_multipliers(n_points):
    """
    Generates Simpson 1st Rule multipliers [1, 4, 2, 4, 2 ... 4, 1] for an odd number of points (even intervals).
    """
    if n_points < 3 or n_points % 2 == 0:
        # Fallback or standard for even: trapezoidal or simpson + 3/8
        multipliers = [1]
        for i in range(1, n_points - 1):
            multipliers.append(4 if i % 2 != 0 else 2)
        multipliers.append(1)
        return multipliers
    
    multipliers = [1]
    for i in range(1, n_points - 1):
        multipliers.append(4 if i % 2 != 0 else 2)
    multipliers.append(1)
    return multipliers

def get_waterline_height(wl_name, depth_m=17.80):
    """
    Returns height above baseline (Z in meters) for standard waterlines or Upper Deck.
    """
    wl_clean = wl_name.lower().replace(" ", "").replace("_", "")
    if "bl" in wl_clean or "baseline" in wl_clean:
        return 0.000
    if "upperdeck" in wl_clean or "deck" in wl_clean:
        return round(depth_m, 3)
    if "wl" in wl_clean:
        num_str = wl_clean.replace("wl", "")
        try:
            return round(float(num_str) / 1000.0, 3)
        except ValueError:
            pass
    return 0.000

def calculate_transverse_station_area(station_name, waterlines, hb_dict, depth=17.80):
    """
    Calculates the cross-sectional area of a single transverse station using Simpson's 1st Rule.
    hb_dict: {wl_name: half_breadth_in_mm}
    """
    n_points = len(waterlines)
    factors = generate_simpson_1st_multipliers(n_points)
    
    rows = []
    sum_products = 0.0

    for idx, (wl, factor) in enumerate(zip(waterlines, factors)):
        raw_hb = hb_dict.get(wl)
        if isinstance(raw_hb, (int, float)):
            hb_m = raw_hb / 1000.0
        elif isinstance(raw_hb, list) and len(raw_hb) > 0:
            hb_m = raw_hb[0] / 1000.0
        else:
            hb_m = 0.0

        b_m = 2.0 * hb_m
        prod = b_m * factor
        sum_products += prod
        wl_height_m = get_waterline_height(wl, depth_m=depth)

        rows.append({
            "point": idx + 1,
            "waterline": wl,
            "waterline_height_m": round(wl_height_m, 3),
            "half_breadth_m": round(hb_m, 3),
            "breadth_m": round(b_m, 3),
            "factor": factor,
            "product": round(prod, 3)
        })

    # Common interval h = Depth / (n_points - 1)
    intervals = max(1, n_points - 1)
    h = depth / float(intervals)
    h_over_3 = h / 3.0
    area = h_over_3 * sum_products

    return {
        "station_name": station_name,
        "depth_m": round(depth, 3),
        "intervals": intervals,
        "h_m": round(h, 4),
        "h_over_3": round(h_over_3, 4),
        "sum_products": round(sum_products, 3),
        "area_m2": round(area, 3),
        "rows": rows
    }

def calculate_underdeck_tonnage(parsed_data, lbp=186.10, default_depth=17.80):
    """
    Integrates all transverse stations, then integrates longitudinally from St. 0 to St. 20.
    Adds aft transom appendix volume.
    Computes total Under Deck Volume (m3) and Under Deck Tonnage (UDT).
    """
    stations = parsed_data["stations"]
    waterlines = parsed_data["waterlines"]
    hb_data = parsed_data["half_breadths"]
    ht_data = parsed_data["heights"]

    # 1. Transverse Area for all stations
    station_results = {}
    sac_curve = [] # Sectional Area Curve points

    # Helper: determine station depth from Upper Deck Height
    for st in stations:
        st_heights = ht_data.get(st, {})
        d_val = default_depth
        for k, v in st_heights.items():
            if "upper deck height" in k.lower():
                if isinstance(v, (int, float)) and v > 0:
                    d_val = v / 1000.0
                break

        res = calculate_transverse_station_area(st, waterlines, hb_data.get(st, {}), depth=d_val)
        station_results[st] = res

    # 2. Main Hull Longitudinal Simpson Integration: Station 0 to Station 20
    # Standard 21 main stations (spacing dx = Lbp / 20)
    main_20_st_names = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                        "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]

    long_factors = [1, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 2, 4, 1]
    dx = lbp / 20.0
    dx_over_3 = dx / 3.0

    long_rows = []
    long_sum_products = 0.0

    for idx, (st_num, factor) in enumerate(zip(main_20_st_names, long_factors)):
        pos_x = idx * dx
        st_res = station_results.get(st_num) or station_results.get(f"St. {st_num}")
        area = st_res["area_m2"] if st_res else 0.0
        depth = st_res["depth_m"] if st_res else default_depth
        prod = area * factor
        long_sum_products += prod

        long_rows.append({
            "station_num": st_num,
            "station_name": f"St. {st_num}",
            "position_x": round(pos_x, 3),
            "depth_m": round(depth, 3),
            "area_m2": round(area, 3),
            "factor": factor,
            "product": round(prod, 3),
            "remark": "AP" if st_num == "0" else ("Midship" if st_num == "10" else ("FP" if st_num == "20" else ""))
        })

        sac_curve.append({
            "x": round(pos_x, 2),
            "area": round(area, 2),
            "station": f"St. {st_num}"
        })

    # Main Hull Enclosed Volume
    main_hull_volume = dx_over_3 * long_sum_products

    # 3. Transom Appendix Volume (Aft of AP to Transom, typically -4.50 m)
    transom_area = station_results.get("Transom", {}).get("area_m2", 0.0)
    st0_area = station_results.get("0", {}).get("area_m2", 0.0)
    transom_length = 4.50 # default 4.50 m aft of AP
    transom_volume = ((transom_area + st0_area) / 2.0) * transom_length

    # Total Under Deck Volume & UDT
    total_underdeck_volume = main_hull_volume + transom_volume
    underdeck_tonnage = total_underdeck_volume / SUEZ_TON_M3

    return {
        "lbp": lbp,
        "dx": round(dx, 3),
        "dx_over_3": round(dx_over_3, 4),
        "main_hull_sum_products": round(long_sum_products, 3),
        "main_hull_volume": round(main_hull_volume, 3),
        "transom_area": round(transom_area, 3),
        "st0_area": round(st0_area, 3),
        "transom_length": round(transom_length, 3),
        "transom_volume": round(transom_volume, 3),
        "total_underdeck_volume": round(total_underdeck_volume, 3),
        "underdeck_tonnage": round(underdeck_tonnage, 2),
        "long_rows": long_rows,
        "station_results": station_results,
        "sac_curve": sac_curve
    }
