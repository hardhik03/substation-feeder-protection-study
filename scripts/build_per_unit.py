import sys
sys.path.insert(0, "config")
from system_parameters import SBASE_MVA, VOLTAGE_LEVELS_KV, NOTES

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
ws = wb.active
ws.title = "Per-Unit Base Values"

headers = ["Voltage Level", "Vbase (kV)", "Sbase (MVA)", "Zbase (\u03a9)", "Ibase (A)", "Notes"]
ws.append(headers)

new_row_label = "Feeder Bridge"  # highlight whichever level is the newest addition
new_row_idx = None

for i, (label, vbase) in enumerate(VOLTAGE_LEVELS_KV.items(), start=2):
    ws.cell(row=i, column=1, value=label)
    ws.cell(row=i, column=2, value=vbase)
    ws.cell(row=i, column=3, value=SBASE_MVA)
    ws.cell(row=i, column=4, value=f"=B{i}^2/C{i}")
    ws.cell(row=i, column=5, value=f"=C{i}*1000/(SQRT(3)*B{i})")
    ws.cell(row=i, column=6, value=NOTES.get(label, ""))
    if label == new_row_label:
        new_row_idx = i

header_font = Font(name="Arial", bold=True, color="FFFFFF")
header_fill = PatternFill("solid", start_color="1B3A6B")
for cell in ws[1]:
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

last_row = 1 + len(VOLTAGE_LEVELS_KV)
for i in range(2, last_row + 1):
    ws.cell(row=i, column=2).font = Font(name="Arial", color="0000FF")
    ws.cell(row=i, column=3).font = Font(name="Arial", color="0000FF")
    ws.cell(row=i, column=4).font = Font(name="Arial", color="000000")
    ws.cell(row=i, column=5).font = Font(name="Arial", color="000000")
    ws.cell(row=i, column=1).font = Font(name="Arial")
    ws.cell(row=i, column=6).font = Font(name="Arial", italic=True, size=9)
    ws.cell(row=i, column=4).number_format = '0.0000'
    ws.cell(row=i, column=5).number_format = '#,##0.0'

if new_row_idx:
    new_row_fill = PatternFill("solid", start_color="FFFF00")
    for col in range(1, 7):
        ws.cell(row=new_row_idx, column=col).fill = new_row_fill

widths = [26, 12, 12, 14, 14, 50]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[chr(64+i)].width = w

wb.save("per_unit_base_values.xlsx")
print("saved, driven entirely by config/system_parameters.py")