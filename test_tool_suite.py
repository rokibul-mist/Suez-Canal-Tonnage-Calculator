import os
import sys

tool_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(tool_dir, ".."))
sys.path.insert(0, tool_dir)
sys.path.insert(0, parent_dir)

from core.template_generator import generate_offset_template
from core.offset_reader import read_offset_file
from core.simpson_engine import calculate_underdeck_tonnage
from core.bulbous_bow_engine import calculate_bulbous_bow_tonnage
from core.professional_report import generate_pdf_table_report, generate_html_table_report
from core.master_excel_builder import build_complete_master_workbook

print("1. Testing Template Generator...")
tpl_path = os.path.join(tool_dir, "generated_templates", "Test_Offset_Template.xlsx")
generate_offset_template(tpl_path, vessel_name="TEST VESSEL")
print("   Generated template:", tpl_path)

print("2. Testing Offset Reader...")
offset_sample = os.path.join(parent_dir, "Suez_Shipyard_Offsets_Calculator.xlsx")
parsed = read_offset_file(offset_sample)
print(f"   Parsed {parsed['total_stations']} stations, {parsed['total_waterlines']} waterlines, {parsed['total_buttocks']} buttocks.")

print("3. Testing Simpson UDT Engine...")
udt_res = calculate_underdeck_tonnage(parsed)
print(f"   Under Deck Volume:  {udt_res['total_underdeck_volume']:,.2f} m3")
print(f"   Under Deck Tonnage: {udt_res['underdeck_tonnage']:,.2f} Suez Tons")

print("4. Testing Bulbous Bow Engine...")
bulb_res = calculate_bulbous_bow_tonnage(l_bulb=5.0, dx_body=1.5, l_nose=2.0)
print(f"   Bulbous Volume:  {bulb_res['method_A']['total_volume']:,.3f} m3")
print(f"   Bulbous Tonnage: {bulb_res['method_A']['tonnage']:,.2f} Suez Tons")

print("5. Testing Professional PDF & HTML Report Generator...")
pdf_path = os.path.join(tool_dir, "exported_reports", "Test_Tables_Report.pdf")
html_path = os.path.join(tool_dir, "exported_reports", "Test_Tables_Report.html")
generate_pdf_table_report(pdf_path, udt_res, bulb_res, parsed['vessel_info'])
generate_html_table_report(html_path, udt_res, bulb_res, parsed['vessel_info'])
print("   Generated PDF:", pdf_path)
print("   Generated HTML:", html_path)

print("6. Testing Master Excel Workbook Builder...")
xls_path = os.path.join(tool_dir, "exported_reports", "Test_Master_Calculation_Workbook.xlsx")
build_complete_master_workbook(xls_path)
print("   Generated Master Excel:", xls_path)

print("\nALL 6 CORE MODULES TESTED AND PASSED PERFECTLY!")
