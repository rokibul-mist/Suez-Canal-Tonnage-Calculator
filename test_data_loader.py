import sys, os
sys.path.insert(0, '.')
from core.offset_reader import read_offset_file
from core.simpson_engine import calculate_underdeck_tonnage
from core.bulbous_bow_engine import calculate_bulbous_bow_tonnage
from core.forecastle_engine import calculate_forecastle_tonnage
from core.hatch_coaming_engine import calculate_hatch_coamings
from core.superstructure_engine import calculate_superstructure_tonnage

# Read test data
offset_path = 'Suez_Offset_Template_M_V_TERVEL.xlsx'
if not os.path.exists(offset_path):
    offset_path = os.path.join('uploaded_offsets', 'Suez_Offset_Template_M_V_TERVEL.xlsx')

parsed = read_offset_file(offset_path)
v_info = parsed.get("vessel_info", {})
v_info["vessel_name"] = "M/V TERVEL"
v_info["nationality"] = "MALTA"
v_info["kind_of_ship"] = "BULK CARRIER"

udt = calculate_underdeck_tonnage(parsed, lbp=186.10, default_depth=17.80)
bulb = calculate_bulbous_bow_tonnage(l_bulb=5.0, dx_body=1.5, l_nose=2.0, dy=1.0, parsed_data=parsed, has_bulbous=True)
fc = calculate_forecastle_tonnage(parsed_data=parsed, imported_height=2.60, lbp=186.10, has_forecastle=True)
hatch = calculate_hatch_coamings()
superstr = calculate_superstructure_tonnage(fallback_to_default=True)

print("Data loaded successfully.")
print(f"UDT Tons: {udt['underdeck_tonnage']}")
print(f"Bulb Tons: {bulb['method_A']['tonnage']}")
print(f"Forecastle Tons: {fc['forecastle_tonnage']}")
print(f"Hatch Tons: {hatch['excess_tonnage']}")
print(f"Superstructure Tons: {superstr['round_houses_tonnage']}")
