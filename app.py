"""
Suez Canal Tonnage Calculator Software - Flask Application Server
Hosts the engineering tool, REST API endpoints, and report generator.
"""
import os
import sys
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from core.template_generator import generate_offset_template, DEFAULT_STATIONS, DEFAULT_WATERLINES, DEFAULT_BUTTOCKS
from core.offset_reader import read_offset_file
from core.simpson_engine import calculate_underdeck_tonnage
from core.bulbous_bow_engine import calculate_bulbous_bow_tonnage
from core.forecastle_engine import calculate_forecastle_tonnage
from core.forecastle_excel_builder import build_single_table_forecastle_workbook
from core.bulbous_excel_builder import build_four_tables_bulbous_workbook
from core.hatch_coaming_engine import calculate_hatch_coamings
from core.hatch_excel_builder import build_hatch_coaming_workbook
from core.superstructure_engine import calculate_superstructure_tonnage, parse_superstructure_excel, DEFAULT_SUPERSTRUCTURE_SPACES
from core.superstructure_excel_builder import build_superstructure_workbook
from core.master_excel_builder import build_complete_master_workbook
from core.professional_report import generate_pdf_table_report, generate_html_table_report

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Storage folders inside Suez_Tonnage_Tool
GENERATED_DIR = os.path.join(BASE_DIR, "generated_templates")
UPLOADED_DIR  = os.path.join(BASE_DIR, "uploaded_offsets")
EXPORTED_DIR  = os.path.join(BASE_DIR, "exported_reports")

for d in [GENERATED_DIR, UPLOADED_DIR, EXPORTED_DIR]:
    os.makedirs(d, exist_ok=True)

# Application state cache
APP_STATE = {
    "parsed_offsets": None,
    "udt_results": None,
    "bulb_results": None,
    "forecastle_results": None,
    "hatch_results": None,
    "superstructure_results": None,
}

def get_or_load_offsets():
    # Only return actual session data in memory. NEVER load disk files behind user's back!
    return APP_STATE.get("parsed_offsets")

def ensure_udt_results():
    return APP_STATE.get("udt_results")

def compute_and_update_overall_tonnage():
    """
    Computes overall Suez Canal Gross Tonnage and Net Tonnage combining:
    - Under Deck Tonnage (UDT)
    - Bulbous Bow Tonnage (Method A)
    - Forecastle Deck Tonnage
    - Hatch Coamings Excess Tonnage
    - Round Houses / Superstructures Tonnage & Deductions
    """
    udt = APP_STATE.get("udt_results") or {}
    bulb = APP_STATE.get("bulb_results") or {}
    fc = APP_STATE.get("forecastle_results") or {}
    hatch = APP_STATE.get("hatch_results") or {}
    super_res = APP_STATE.get("superstructure_results") or {}

    udt_vol = float(udt.get("total_underdeck_volume", 0.0) or 0.0)
    udt_ton = float(udt.get("underdeck_tonnage", 0.0) or 0.0)

    has_bulb = bulb.get("has_bulbous", True) if bulb else False
    mA = bulb.get("method_A", {}) if bulb else {}
    bulb_vol = float(mA.get("total_volume", 0.0) or 0.0) if has_bulb else 0.0
    bulb_ton = float(mA.get("tonnage", 0.0) or 0.0) if has_bulb else 0.0

    fc_vol = float(fc.get("forecastle_volume", 0.0) or 0.0)
    fc_ton = float(fc.get("forecastle_tonnage", 0.0) or 0.0)

    hatch_exc_vol = float(hatch.get("excess_volume", 0.0) or 0.0)
    hatch_exc_ton = float(hatch.get("excess_tonnage", 0.0) or 0.0)

    rh_vol = float(super_res.get("total_addition_volume", 0.0) or 0.0)
    rh_ton = float(super_res.get("total_addition_tonnage", 0.0) or 0.0)

    gross_vol = udt_vol + bulb_vol + fc_vol + hatch_exc_vol + rh_vol
    gross_ton = udt_ton + bulb_ton + fc_ton + hatch_exc_ton + rh_ton

    off_vol = float(super_res.get("officer_accommodation_volume", 0.0) or 0.0)
    off_ton = float(super_res.get("officer_accommodation_tonnage", 0.0) or 0.0)
    crew_vol = float(super_res.get("crew_accommodation_volume", 0.0) or 0.0)
    crew_ton = float(super_res.get("crew_accommodation_tonnage", 0.0) or 0.0)
    work_vol = float(super_res.get("working_ship_volume", 0.0) or 0.0)
    work_ton = float(super_res.get("working_ship_tonnage", 0.0) or 0.0)
    prop_vol = float(super_res.get("propelling_power_volume", 0.0) or 0.0)
    prop_ton = float(super_res.get("propelling_power_tonnage", 0.0) or 0.0)

    # SCA Rule (Art. 94): Non-propelling deductions CANNOT EXCEED 10% of Gross Tonnage
    non_prop_raw_ton = off_ton + crew_ton + work_ton
    non_prop_raw_vol = off_vol + crew_vol + work_vol
    non_prop_cap = round(gross_ton * 0.10, 2)
    non_prop_was_capped = non_prop_raw_ton > non_prop_cap
    if non_prop_was_capped:
        ratio = non_prop_cap / non_prop_raw_ton if non_prop_raw_ton > 0 else 1.0
        off_ton_eff = round(off_ton * ratio, 2)
        crew_ton_eff = round(crew_ton * ratio, 2)
        work_ton_eff = round(work_ton * ratio, 2)
        off_vol_eff = round(off_ton_eff * 2.832, 3)
        crew_vol_eff = round(crew_ton_eff * 2.832, 3)
        work_vol_eff = round(work_ton_eff * 2.832, 3)
        non_prop_ton_capped = off_ton_eff + crew_ton_eff + work_ton_eff
        non_prop_vol_capped = off_vol_eff + crew_vol_eff + work_vol_eff
    else:
        non_prop_ton_capped = non_prop_raw_ton
        non_prop_vol_capped = non_prop_raw_vol
        off_ton_eff, crew_ton_eff, work_ton_eff = off_ton, crew_ton, work_ton
        off_vol_eff, crew_vol_eff, work_vol_eff = off_vol, crew_vol, work_vol

    # SCA Rule (Art. 94.D): Propelling power deduction CANNOT EXCEED 50% of Gross Tonnage
    prop_ton_cap = round(gross_ton * 0.50, 2)
    prop_ton_capped = min(prop_ton, prop_ton_cap)
    prop_vol_capped = round(prop_ton_capped * 2.832, 3)
    prop_was_capped = prop_ton > prop_ton_cap

    tot_ded_vol = non_prop_vol_capped + prop_vol_capped
    tot_ded_ton = non_prop_ton_capped + prop_ton_capped

    net_vol = max(0.0, gross_vol - tot_ded_vol)
    net_ton = max(0.0, gross_ton - tot_ded_ton)

    summary = {
        "udt": {"volume": round(udt_vol, 3), "tonnage": round(udt_ton, 2)},
        "bulbous": {"volume": round(bulb_vol, 3), "tonnage": round(bulb_ton, 2), "has_bulbous": has_bulb},
        "forecastle": {"volume": round(fc_vol, 3), "tonnage": round(fc_ton, 2)},
        "hatches": {"volume": round(hatch_exc_vol, 3), "tonnage": round(hatch_exc_ton, 2)},
        "round_houses": {"volume": round(rh_vol, 3), "tonnage": round(rh_ton, 2)},
        "gross_tonnage": {"volume": round(gross_vol, 3), "tonnage": round(gross_ton, 2)},
        "deductions": {
            "officers": {"volume": round(off_vol_eff, 3), "tonnage": round(off_ton_eff, 2)},
            "crew": {"volume": round(crew_vol_eff, 3), "tonnage": round(crew_ton_eff, 2)},
            "working_ship": {"volume": round(work_vol_eff, 3), "tonnage": round(work_ton_eff, 2)},
            "non_propelling_cap": {
                "applied": non_prop_was_capped,
                "limit_10pct": round(non_prop_cap, 2),
                "original_tonnage": round(non_prop_raw_ton, 2)
            },
            "propelling_power": {
                "volume": round(prop_vol_capped, 3),
                "tonnage": round(prop_ton_capped, 2),
                "original_tonnage": round(prop_ton, 2),
                "cap_applied": prop_was_capped,
                "cap_limit_50pct": round(prop_ton_cap, 2)
            },
            "total": {"volume": round(tot_ded_vol, 3), "tonnage": round(tot_ded_ton, 2)}
        },
        "net_tonnage": {"volume": round(net_vol, 3), "tonnage": round(net_ton, 2)}
    }
    APP_STATE["overall_tonnage_summary"] = summary
    return summary

@app.route("/api/get_overall_tonnage", methods=["GET"])
def api_get_overall_tonnage():
    return jsonify({"success": True, "data": compute_and_update_overall_tonnage()})

@app.route("/api/clear_all_data", methods=["POST"])
def api_clear_all_data():
    for k in APP_STATE:
        APP_STATE[k] = None
    return jsonify({"success": True})

@app.route("/")
def index():
    return render_template("index.html")

# -----------------------------------------------------------------
# 1. Generate Blank Template API
# -----------------------------------------------------------------
@app.route("/api/generate_template", methods=["POST"])
def api_generate_template():
    try:
        data = request.json or {}
        v_name = data.get("vessel_name", "NEW_VESSEL")
        filename = f"Suez_Offset_Template_{secure_filename(v_name)}.xlsx"
        out_path = os.path.join(GENERATED_DIR, filename)

        generate_offset_template(
            out_path,
            vessel_name=v_name,
            lbp=data.get("lbp", 186.10),
            breadth=data.get("breadth", 32.26),
            depth=data.get("depth", 17.80),
            stations=data.get("stations"),
            waterlines=data.get("waterlines"),
            buttocks=data.get("buttocks")
        )

        return jsonify({
            "success": True,
            "filename": filename,
            "download_url": f"/download/generated/{filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 2. Upload / Read Offset Spreadsheet API
# -----------------------------------------------------------------
@app.route("/api/upload_offsets", methods=["POST"])
def api_upload_offsets():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "Empty filename"}), 400

        fname = secure_filename(file.filename)
        save_path = os.path.join(UPLOADED_DIR, fname)
        file.save(save_path)

        parsed = read_offset_file(save_path)
        APP_STATE["parsed_offsets"] = parsed
        APP_STATE["udt_results"] = None

        return jsonify({"success": True, "data": parsed})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# Load Preset M/V TERVEL Offsets API
# -----------------------------------------------------------------
@app.route("/api/load_sample", methods=["POST"])
def api_load_sample():
    try:
        sample_path = os.path.join(PARENT_DIR, "Suez_Shipyard_Offsets_Calculator.xlsx")
        if not os.path.exists(sample_path):
            sample_path = os.path.join(UPLOADED_DIR, "Suez_Offset_Template_M_V_TERVEL.xlsx")
        if not os.path.exists(sample_path):
            sample_path = os.path.join(GENERATED_DIR, "Suez_Offset_Template_M_V_TERVEL.xlsx")

        parsed = read_offset_file(sample_path)
        APP_STATE["parsed_offsets"] = parsed
        return jsonify({"success": True, "data": parsed})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 2b. Save Web Offset Grid API
# -----------------------------------------------------------------
@app.route("/api/save_web_offsets", methods=["POST"])
def api_save_web_offsets():
    try:
        req = request.json or {}
        stations = req.get("stations") or DEFAULT_STATIONS
        waterlines = req.get("waterlines") or DEFAULT_WATERLINES
        buttocks = req.get("buttocks") or DEFAULT_BUTTOCKS
        half_breadths = req.get("half_breadths") or {}
        heights = req.get("heights") or {}
        vessel_info = req.get("vessel_info") or {}

        parsed = {
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

        APP_STATE["parsed_offsets"] = parsed
        APP_STATE["udt_results"] = None

        return jsonify({"success": True, "data": parsed})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 2c. Get Standard Shipyard Offsets API
# -----------------------------------------------------------------
@app.route("/api/get_standard_offsets", methods=["GET"])
def api_get_standard_offsets():
    try:
        sample_path = os.path.join(PARENT_DIR, "Suez_Shipyard_Offsets_Calculator.xlsx")
        if not os.path.exists(sample_path):
            sample_path = os.path.join(UPLOADED_DIR, "Suez_Offset_Template_M_V_TERVEL.xlsx")
        if not os.path.exists(sample_path):
            sample_path = os.path.join(GENERATED_DIR, "Suez_Offset_Template_M_V_TERVEL.xlsx")

        parsed = read_offset_file(sample_path)
        return jsonify({"success": True, "data": parsed})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 2d. Auto-Save Full Application State API
# -----------------------------------------------------------------
@app.route("/api/autosave", methods=["POST"])
def api_autosave():
    try:
        data = request.json or {}
        
        # 1. Update Ship Particulars & Features
        if "ship_particulars" in data:
            if not APP_STATE.get("parsed_offsets"):
                APP_STATE["parsed_offsets"] = {
                    "vessel_info": {},
                    "stations": [],
                    "waterlines": [],
                    "buttocks": [],
                    "half_breadths": {},
                    "heights": {}
                }
            v_info = APP_STATE["parsed_offsets"].setdefault("vessel_info", {})
            for k, v in data["ship_particulars"].items():
                v_info[k] = v

        # 2. Update Web Offsets if provided
        if "offsets" in data and data["offsets"]:
            off = data["offsets"]
            if not APP_STATE.get("parsed_offsets"):
                APP_STATE["parsed_offsets"] = {
                    "vessel_info": {},
                    "stations": [],
                    "waterlines": [],
                    "buttocks": [],
                    "half_breadths": {},
                    "heights": {}
                }
            if off.get("half_breadths") or off.get("heights"):
                APP_STATE["parsed_offsets"]["half_breadths"] = off.get("half_breadths", {})
                APP_STATE["parsed_offsets"]["heights"] = off.get("heights", {})
                if off.get("stations"): APP_STATE["parsed_offsets"]["stations"] = off["stations"]
                if off.get("waterlines"): APP_STATE["parsed_offsets"]["waterlines"] = off["waterlines"]
                if off.get("buttocks"): APP_STATE["parsed_offsets"]["buttocks"] = off["buttocks"]

        # 3. Update Bulbous Bow parameters ONLY if explicitly calculated
        if "bulbous" in data and data["bulbous"] and data["bulbous"].get("calculated"):
            b = data["bulbous"]
            APP_STATE["bulb_results"] = calculate_bulbous_bow_tonnage(
                l_bulb=float(b.get("l_bulb", 5.0)),
                dx_body=float(b.get("dx_body", 1.5)),
                l_nose=float(b.get("l_nose", 2.0)),
                dy=float(b.get("dy", 1.0)),
                custom_data=b.get("custom_data"),
                parsed_data=APP_STATE.get("parsed_offsets"),
                has_bulbous=b.get("has_bulbous", True)
            )

        # 4. Update Forecastle parameters ONLY if explicitly calculated
        if "forecastle" in data and data["forecastle"] and data["forecastle"].get("calculated"):
            fc = data["forecastle"]
            fc_h = float(fc.get("height", 2.60))
            parsed = APP_STATE.get("parsed_offsets")
            v_info_temp = parsed.get("vessel_info", {}) if parsed else {}
            APP_STATE["forecastle_results"] = calculate_forecastle_tonnage(
                parsed_data=parsed, 
                imported_height=fc_h, 
                lbp=float(v_info_temp.get("lbp", 186.10)),
                column_name=fc.get("column_name", "Upper Deck Side"),
                start_station=fc.get("start_station"),
                end_station=fc.get("end_station"),
                custom_rows=fc.get("custom_rows"),
                has_forecastle=fc.get("has_forecastle", True)
            )

        # 5. Update Hatches ONLY if provided and calculated
        if "hatches" in data and data["hatches"] and data.get("hatches_calculated"):
            APP_STATE["hatch_results"] = calculate_hatch_coamings(hatches_list=data["hatches"])

        # 6. Update Superstructures ONLY if provided and calculated
        if "superstructures" in data and data["superstructures"] and data.get("superstructures_calculated"):
            APP_STATE["superstructure_results"] = calculate_superstructure_tonnage(spaces_list=data["superstructures"])

        overall = compute_and_update_overall_tonnage()
        return jsonify({"success": True, "saved_at": data.get("timestamp"), "overall_tonnage": overall})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 3. Calculate Under Deck Tonnage API
# -----------------------------------------------------------------
@app.route("/api/calculate_udt", methods=["POST"])
def api_calculate_udt():
    try:
        parsed = get_or_load_offsets()
        if not parsed:
            return jsonify({"success": False, "error": "No offset dataset loaded. Please upload your offset Excel file in Step 2."}), 400

        req = request.json or {}
        v_info = parsed.get("vessel_info", {})
        
        lbp = 186.10
        try:
            if req.get("lbp") and float(req.get("lbp")) > 0:
                lbp = float(req["lbp"])
            elif v_info.get("lbp") and float(v_info.get("lbp")) > 0:
                lbp = float(v_info["lbp"])
        except (ValueError, TypeError):
            pass

        depth = 17.80
        try:
            if req.get("depth") and float(req.get("depth")) > 0:
                depth = float(req["depth"])
            elif v_info.get("depth") and float(v_info.get("depth")) > 0:
                depth = float(v_info["depth"])
        except (ValueError, TypeError):
            pass

        if "vessel_info" in parsed:
            parsed["vessel_info"]["lbp"] = lbp
            parsed["vessel_info"]["depth"] = depth
            for k in ["vessel_name", "nationality", "kind_of_ship", "official_number"]:
                if req.get(k):
                    parsed["vessel_info"][k] = req[k]

        udt_res = calculate_underdeck_tonnage(parsed, lbp=lbp, default_depth=depth)
        APP_STATE["udt_results"] = udt_res
        overall = compute_and_update_overall_tonnage()

        return jsonify({"success": True, "data": udt_res, "overall_tonnage": overall})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 4. Calculate Bulbous Bow API
# -----------------------------------------------------------------
@app.route("/api/calculate_bulbous", methods=["POST"])
def api_calculate_bulbous():
    try:
        req = request.json or {}
        has_bulbous = req.get("has_bulbous", True)
        if isinstance(has_bulbous, str):
            has_bulbous = has_bulbous.lower() in ["true", "1", "yes"]

        l_bulb = float(req.get("l_bulb", 5.0))
        dx_body = float(req.get("dx_body", 1.5))
        l_nose = float(req.get("l_nose", 2.0))
        dy = float(req.get("dy", 1.0))

        custom_data = req.get("custom_data")
        parsed = APP_STATE.get("parsed_offsets")
        bulb_res = calculate_bulbous_bow_tonnage(
            l_bulb=l_bulb, dx_body=dx_body, l_nose=l_nose, dy=dy, 
            custom_data=custom_data, parsed_data=parsed, has_bulbous=has_bulbous
        )
        APP_STATE["bulb_results"] = bulb_res

        # Refresh the dedicated 4-Table Bulbous Bow Excel file
        bb_excel1 = os.path.join(PARENT_DIR, "Bulbous_Bow_Tonnage_Calculation.xlsx")
        bb_excel2 = os.path.join(EXPORTED_DIR, "Bulbous_Bow_Tonnage_Calculation.xlsx")
        try:
            build_four_tables_bulbous_workbook(bb_excel1)
            build_four_tables_bulbous_workbook(bb_excel2)
        except Exception:
            pass

        overall = compute_and_update_overall_tonnage()
        return jsonify({"success": True, "data": bulb_res, "overall_tonnage": overall})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 4b. Export Bulbous Bow 4-Table Excel API
# -----------------------------------------------------------------
@app.route("/api/export_bulbous_excel", methods=["POST"])
def api_export_bulbous_excel():
    try:
        filename = "Bulbous_Bow_Tonnage_Calculation.xlsx"
        out_path = os.path.join(EXPORTED_DIR, filename)
        parent_path = os.path.join(PARENT_DIR, filename)
        build_four_tables_bulbous_workbook(out_path)
        build_four_tables_bulbous_workbook(parent_path)
        return jsonify({
            "success": True,
            "filename": filename,
            "download_url": f"/download/exported/{filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 4b. Calculate Forecastle Tonnage API
# -----------------------------------------------------------------
@app.route("/api/calculate_forecastle", methods=["POST"])
def api_calculate_forecastle():
    try:
        req = request.json or {}
        imported_height = float(req.get("height", 2.60))

        if not APP_STATE.get("parsed_offsets"):
            get_or_load_offsets()

        parsed = APP_STATE.get("parsed_offsets")
        v_info = parsed.get("vessel_info", {}) if parsed else {}
        lbp = 186.10
        if req.get("lbp") and float(req.get("lbp")) > 0:
            lbp = float(req["lbp"])
        elif v_info.get("lbp") and float(v_info.get("lbp")) > 0:
            lbp = float(v_info["lbp"])

        col_name = req.get("column_name", "Upper Deck Side")
        has_fc = req.get("has_forecastle", True)
        if isinstance(has_fc, str):
            has_fc = has_fc.lower() in ["true", "1", "yes"]

        fc_res = calculate_forecastle_tonnage(
            parsed_data=parsed, 
            imported_height=imported_height, 
            lbp=lbp,
            column_name=col_name,
            start_station=req.get("start_station"),
            end_station=req.get("end_station"),
            custom_rows=req.get("custom_rows"),
            has_forecastle=has_fc
        )
        APP_STATE["forecastle_results"] = fc_res

        # Also refresh the standalone Excel files
        fc_excel1 = os.path.join(PARENT_DIR, "Forecastle_Deck_Tonnage_Calculation.xlsx")
        fc_excel2 = os.path.join(EXPORTED_DIR, "Forecastle_Deck_Tonnage_Calculation.xlsx")
        try:
            build_single_table_forecastle_workbook(fc_excel1, imported_height=imported_height)
            build_single_table_forecastle_workbook(fc_excel2, imported_height=imported_height)
        except Exception:
            pass

        overall = compute_and_update_overall_tonnage()
        return jsonify({"success": True, "data": fc_res, "overall_tonnage": overall})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 4c. Calculate Cargo Hatchways & Coamings API
# -----------------------------------------------------------------
@app.route("/api/calculate_hatches", methods=["POST"])
def api_calculate_hatches():
    try:
        req = request.json or {}
        hatches = req.get("hatches", None)
        
        # Calculate dynamic pre-hatch gross tonnage: UDT + Bulbous + Forecastle + Round Houses
        udt_ton = float((APP_STATE.get("udt_results") or {}).get("underdeck_tonnage", 0.0) or 0.0)
        bulb_mA = (APP_STATE.get("bulb_results") or {}).get("method_A", {})
        bulb_ton = float(bulb_mA.get("tonnage", 0.0) or 0.0)
        fc_ton = float((APP_STATE.get("forecastle_results") or {}).get("forecastle_tonnage", 0.0) or 0.0)
        rh_ton = float((APP_STATE.get("superstructure_results") or {}).get("total_addition_tonnage", 0.0) or 0.0)
        pre_ton_calc = udt_ton + bulb_ton + fc_ton + rh_ton
        pre_hatch_tonnage = float(req.get("pre_hatch_tonnage") or (pre_ton_calc if pre_ton_calc > 0 else 32500.0))

        hatch_res = calculate_hatch_coamings(hatches_list=hatches, pre_hatch_gross_tonnage=pre_hatch_tonnage)
        APP_STATE["hatch_results"] = hatch_res

        # Refresh standalone Hatch Excel files
        hc_excel1 = os.path.join(PARENT_DIR, "Hatch_Coaming_Tonnage_Calculation.xlsx")
        hc_excel2 = os.path.join(EXPORTED_DIR, "Hatch_Coaming_Tonnage_Calculation.xlsx")
        try:
            build_hatch_coaming_workbook(hc_excel1, hatches=hatches, pre_hatch_tonnage=pre_hatch_tonnage)
            build_hatch_coaming_workbook(hc_excel2, hatches=hatches, pre_hatch_tonnage=pre_hatch_tonnage)
        except Exception:
            pass

        overall = compute_and_update_overall_tonnage()
        return jsonify({"success": True, "data": hatch_res, "overall_tonnage": overall})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 4d. Export Hatch Coaming Excel API
# -----------------------------------------------------------------
@app.route("/api/export_hatch_excel", methods=["POST"])
def api_export_hatch_excel():
    try:
        req = request.json or {}
        hatches = req.get("hatches", None)
        pre_hatch_tonnage = float(req.get("pre_hatch_tonnage", 32500.0))

        filename = "Hatch_Coaming_Tonnage_Calculation.xlsx"
        out_path = os.path.join(EXPORTED_DIR, filename)
        parent_path = os.path.join(PARENT_DIR, filename)

        build_hatch_coaming_workbook(out_path, hatches=hatches, pre_hatch_tonnage=pre_hatch_tonnage)
        try:
            build_hatch_coaming_workbook(parent_path, hatches=hatches, pre_hatch_tonnage=pre_hatch_tonnage)
        except Exception:
            pass

        return jsonify({
            "success": True,
            "filename": filename,
            "download_url": f"/download/exported/{filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 4c. Calculate Superstructures API
# -----------------------------------------------------------------
@app.route("/api/calculate_superstructure", methods=["POST"])
def api_calculate_superstructure():
    try:
        data = request.json or {}
        spaces = data.get("spaces", None)
        res = calculate_superstructure_tonnage(spaces_list=spaces)
        APP_STATE["superstructure_results"] = res
        overall = compute_and_update_overall_tonnage()
        return jsonify({"success": True, "data": res, "overall_tonnage": overall})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 4c-2. Upload & Parse Superstructure Excel API
# -----------------------------------------------------------------
@app.route("/api/upload_superstructure_excel", methods=["POST"])
def api_upload_superstructure_excel():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "Empty filename"}), 400

        fname = secure_filename(file.filename)
        save_path = os.path.join(UPLOADED_DIR, fname)
        file.save(save_path)

        spaces = parse_superstructure_excel(save_path)
        res = calculate_superstructure_tonnage(spaces_list=spaces)
        APP_STATE["superstructure_results"] = res
        overall = compute_and_update_overall_tonnage()

        return jsonify({
            "success": True,
            "filename": fname,
            "spaces_count": len(spaces),
            "spaces": spaces,
            "data": res,
            "overall_tonnage": overall
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 4c-3. Get Default 53-Space GA Schedule
# -----------------------------------------------------------------
@app.route("/api/get_default_superstructures", methods=["GET"])
def api_get_default_superstructures():
    try:
        return jsonify({
            "success": True,
            "spaces_count": len(DEFAULT_SUPERSTRUCTURE_SPACES),
            "spaces": DEFAULT_SUPERSTRUCTURE_SPACES
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# -----------------------------------------------------------------
# 4d. Export Superstructure Dedicated Excel API
# -----------------------------------------------------------------
@app.route("/api/export_superstructure_excel", methods=["POST"])
def api_export_superstructure_excel():
    try:
        data = request.json or {}
        spaces = data.get("spaces", None)
        filename = "Superstructure_Tonnage_Calculation.xlsx"
        out_path = os.path.join(EXPORTED_DIR, filename)
        parent_path = os.path.join(PARENT_DIR, filename)

        build_superstructure_workbook(out_path, spaces=spaces)
        try:
            build_superstructure_workbook(parent_path, spaces=spaces)
        except Exception:
            pass

        return jsonify({
            "success": True,
            "filename": filename,
            "download_url": f"/download/exported/{filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 5. Export Master Excel API
# -----------------------------------------------------------------
@app.route("/api/export_master_excel", methods=["POST"])
def api_export_master_excel():
    try:
        filename = "Suez_Canal_Master_Calculation_Workbook.xlsx"
        out_path = os.path.join(EXPORTED_DIR, filename)

        build_complete_master_workbook(out_path)
        return jsonify({
            "success": True,
            "filename": filename,
            "download_url": f"/download/exported/{filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 6. Export Professional Tables-Only PDF Report API
# -----------------------------------------------------------------
@app.route("/api/export_pdf_report", methods=["POST"])
def api_export_pdf_report():
    try:
        filename = "Suez_Canal_Official_Tables_Report.pdf"
        out_path = os.path.join(EXPORTED_DIR, filename)
        alt_path = os.path.join(BASE_DIR, "exported", filename)

        req = request.json or {}

        # Ensure UDT state
        ensure_udt_results()

        # Dynamic Bulbous Bow calculation if requested
        if "has_bulbous" in req:
            has_b = req.get("has_bulbous", True)
            if isinstance(has_b, str):
                has_b = has_b.lower() in ["true", "1", "yes"]
            if not has_b:
                APP_STATE["bulb_results"] = None
            elif req.get("custom_data") or not APP_STATE.get("bulb_results"):
                parsed = APP_STATE.get("parsed_offsets")
                APP_STATE["bulb_results"] = calculate_bulbous_bow_tonnage(
                    l_bulb=float(req.get("l_bulb", 5.0)),
                    dx_body=float(req.get("dx_body", 1.5)),
                    l_nose=float(req.get("l_nose", 2.0)),
                    dy=float(req.get("dy", 1.0)),
                    custom_data=req.get("custom_data"),
                    parsed_data=parsed,
                    has_bulbous=True
                )

        # Dynamic Forecastle calculation if requested
        if "has_forecastle" in req or "fc_height" in req:
            has_f = req.get("has_forecastle", True)
            if isinstance(has_f, str):
                has_f = has_f.lower() in ["true", "1", "yes"]
            if not has_f:
                APP_STATE["forecastle_results"] = None
            elif req.get("custom_rows") or not APP_STATE.get("forecastle_results"):
                fc_h = float(req.get("fc_height", 2.60))
                parsed = APP_STATE.get("parsed_offsets")
                v_info_temp = parsed.get("vessel_info", {}) if parsed else {}
                APP_STATE["forecastle_results"] = calculate_forecastle_tonnage(
                    parsed_data=parsed, 
                    imported_height=fc_h, 
                    lbp=float(v_info_temp.get("lbp", 186.10) or 186.10),
                    column_name=req.get("column_name", "Upper Deck Side"),
                    start_station=req.get("start_station", "17"),
                    end_station=req.get("end_station", "B"),
                    custom_rows=req.get("custom_rows"),
                    has_forecastle=True
                )

        # Dynamic Hatch Coamings calculation if requested
        if "hatches" in req:
            if req["hatches"]:
                APP_STATE["hatch_results"] = calculate_hatch_coamings(hatches_list=req["hatches"])
            else:
                APP_STATE["hatch_results"] = None

        # Dynamic Superstructures calculation if requested
        if "superstructures" in req:
            if req["superstructures"]:
                APP_STATE["superstructure_results"] = calculate_superstructure_tonnage(spaces_list=req["superstructures"])
            else:
                APP_STATE["superstructure_results"] = None

        parsed_offsets = APP_STATE.get("parsed_offsets") or {}
        v_info = dict(parsed_offsets.get("vessel_info") or {})
        for key in ["vessel_name", "nationality", "kind_of_ship", "official_number", "signal_letters",
                    "port_of_registry", "keel_laying_date", "built_where", "material_of_hull",
                    "builder", "engine_type", "date_of_launch", "propellers", "hull_note",
                    "lbp", "breadth", "depth", "has_bulbous", "has_forecastle", "has_hatches", "has_roundhouses"]:
            if key in req:
                val = req[key]
                if isinstance(val, str) and val.lower() in ["true", "false", "yes", "no"]:
                    val = val.lower() in ["true", "yes"]
                v_info[key] = val

        has_bulb = v_info.get("has_bulbous", True)
        has_fc = v_info.get("has_forecastle", True)
        has_hatches = v_info.get("has_hatches", True)
        has_rh = v_info.get("has_roundhouses", True)

        bulb_data = APP_STATE.get("bulb_results") if has_bulb else None
        fc_data = APP_STATE.get("forecastle_results") if has_fc else None
        hatch_data = APP_STATE.get("hatch_results") if has_hatches else None
        super_data = APP_STATE.get("superstructure_results") if has_rh else None
        if not has_rh and super_data:
            super_data = dict(super_data)
            super_data["round_houses_tonnage"] = 0.0
            super_data["round_houses_volume"] = 0.0
            super_data["total_addition_volume"] = 0.0
            super_data["total_addition_tonnage"] = 0.0

        generate_pdf_table_report(
            out_path, 
            APP_STATE["udt_results"], 
            bulb_data, 
            v_info, 
            forecastle_data=fc_data,
            hatch_data=hatch_data,
            superstructure_data=super_data
        )

        try:
            generate_pdf_table_report(
                alt_path, 
                APP_STATE["udt_results"], 
                bulb_data, 
                v_info, 
                forecastle_data=fc_data,
                hatch_data=hatch_data,
                superstructure_data=super_data
            )
        except Exception:
            pass

        return jsonify({
            "success": True,
            "filename": filename,
            "download_url": f"/download/exported/{filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# 7. Export Professional Tables-Only HTML Report API
# -----------------------------------------------------------------
@app.route("/api/export_html_report", methods=["POST"])
def api_export_html_report():
    try:
        filename = "Suez_Canal_Official_Tables_Report.html"
        out_path = os.path.join(EXPORTED_DIR, filename)
        alt_path = os.path.join(BASE_DIR, "exported", filename)

        req = request.json or {}

        # Ensure UDT state
        ensure_udt_results()

        # Dynamic Bulbous Bow calculation if requested
        if "has_bulbous" in req:
            has_b = req.get("has_bulbous", True)
            if isinstance(has_b, str):
                has_b = has_b.lower() in ["true", "1", "yes"]
            if not has_b:
                APP_STATE["bulb_results"] = None
            elif req.get("custom_data") or not APP_STATE.get("bulb_results"):
                parsed = APP_STATE.get("parsed_offsets")
                APP_STATE["bulb_results"] = calculate_bulbous_bow_tonnage(
                    l_bulb=float(req.get("l_bulb", 5.0)),
                    dx_body=float(req.get("dx_body", 1.5)),
                    l_nose=float(req.get("l_nose", 2.0)),
                    dy=float(req.get("dy", 1.0)),
                    custom_data=req.get("custom_data"),
                    parsed_data=parsed,
                    has_bulbous=True
                )

        # Dynamic Forecastle calculation if requested
        if "has_forecastle" in req or "fc_height" in req:
            has_f = req.get("has_forecastle", True)
            if isinstance(has_f, str):
                has_f = has_f.lower() in ["true", "1", "yes"]
            if not has_f:
                APP_STATE["forecastle_results"] = None
            elif req.get("custom_rows") or not APP_STATE.get("forecastle_results"):
                fc_h = float(req.get("fc_height", 2.60))
                parsed = APP_STATE.get("parsed_offsets")
                v_info_temp = parsed.get("vessel_info", {}) if parsed else {}
                APP_STATE["forecastle_results"] = calculate_forecastle_tonnage(
                    parsed_data=parsed, 
                    imported_height=fc_h, 
                    lbp=float(v_info_temp.get("lbp", 186.10) or 186.10),
                    column_name=req.get("column_name", "Upper Deck Side"),
                    start_station=req.get("start_station", "17"),
                    end_station=req.get("end_station", "B"),
                    custom_rows=req.get("custom_rows"),
                    has_forecastle=True
                )

        # Dynamic Hatch Coamings calculation if requested
        if "hatches" in req:
            if req["hatches"]:
                APP_STATE["hatch_results"] = calculate_hatch_coamings(hatches_list=req["hatches"])
            else:
                APP_STATE["hatch_results"] = None

        # Dynamic Superstructures calculation if requested
        if "superstructures" in req:
            if req["superstructures"]:
                APP_STATE["superstructure_results"] = calculate_superstructure_tonnage(spaces_list=req["superstructures"])
            else:
                APP_STATE["superstructure_results"] = None

        parsed_offsets = APP_STATE.get("parsed_offsets") or {}
        v_info = dict(parsed_offsets.get("vessel_info") or {})
        for key in ["vessel_name", "nationality", "kind_of_ship", "official_number", "signal_letters",
                    "port_of_registry", "keel_laying_date", "built_where", "material_of_hull",
                    "builder", "engine_type", "date_of_launch", "propellers", "hull_note",
                    "lbp", "breadth", "depth", "has_bulbous", "has_forecastle", "has_hatches", "has_roundhouses"]:
            if key in req:
                val = req[key]
                if isinstance(val, str) and val.lower() in ["true", "false", "yes", "no"]:
                    val = val.lower() in ["true", "yes"]
                v_info[key] = val

        has_bulb = v_info.get("has_bulbous", True)
        has_fc = v_info.get("has_forecastle", True)
        has_hatches = v_info.get("has_hatches", True)
        has_rh = v_info.get("has_roundhouses", True)

        bulb_data = APP_STATE.get("bulb_results") if has_bulb else None
        fc_data = APP_STATE.get("forecastle_results") if has_fc else None
        hatch_data = APP_STATE.get("hatch_results") if has_hatches else None
        super_data = APP_STATE.get("superstructure_results") if has_rh else None
        if not has_rh and super_data:
            super_data = dict(super_data)
            super_data["round_houses_tonnage"] = 0.0
            super_data["round_houses_volume"] = 0.0
            super_data["total_addition_volume"] = 0.0
            super_data["total_addition_tonnage"] = 0.0

        generate_html_table_report(
            out_path, 
            APP_STATE["udt_results"], 
            bulb_data, 
            v_info, 
            forecastle_data=fc_data,
            hatch_data=hatch_data,
            superstructure_data=super_data
        )

        try:
            generate_html_table_report(
                alt_path, 
                APP_STATE["udt_results"], 
                bulb_data, 
                v_info, 
                forecastle_data=fc_data,
                hatch_data=hatch_data,
                superstructure_data=super_data
            )
        except Exception:
            pass

        return jsonify({
            "success": True,
            "filename": filename,
            "view_url": f"/view_report/{filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# -----------------------------------------------------------------
# Download & View Routes
# -----------------------------------------------------------------
@app.route("/download/<folder>/<filename>")
def download_file(folder, filename):
    target_dir = GENERATED_DIR if folder == "generated" else EXPORTED_DIR
    return send_from_directory(target_dir, filename, as_attachment=True)

@app.route("/view_report/<filename>")
def view_report(filename):
    return send_from_directory(EXPORTED_DIR, filename)

if __name__ == "__main__":
    port = 5000
    print(f"\n=======================================================")
    print(f"  Suez Canal Tonnage Calculator Software Server")
    print(f"  Running locally at: http://localhost:{port}")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)
