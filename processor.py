# ==============================================================================
# Machine Data Preprocessing Pipeline (Sanitized Example)
# Public entry point: process_machine_files(input_prefix, output_prefix)
# ==============================================================================
import os
import re
import tempfile
import traceback
from pathlib import Path
import pandas as pd

# ==============================================================================
# CONFIGURATION
# ==============================================================================
POSSIBLE_ENCODINGS = ['utf-8', 'latin-1', 'cp1252']

SIGNAL_MAP = {
    "Deformation_Src": "Deform_Src",
    "Deformation_Dst": "Deform_Dst",
    "Frequency_Src":   "Freq_Src",
    "Frequency_Dst":   "Freq_Dst",
    "Current_Src":     "Current_Src",
    "Current_Dst":     "Current_Dst",
}

SIGNAL_COLUMNS_SHORT = list(SIGNAL_MAP.values())

METADATA_COLUMNS = [
    'TimeStamp', 'DMC', 'Source_Machine', 'Machine_Serial_Number',
    'User_ID', 'Bond_head', 'Bondheadserial_number',
    'Wire_Type', 'BondProgram', 'Wedge_Type', 'Guide_Type', 'Cutter_Type',
    'Holder', 'US_Factor', 'Device', 'Wire',
    'Wedge_Counter', 'Wedge_CounterMax', 'Guide_Counter', 'Guide_CounterMax',
    'Cutter_Counter', 'Cutter_CounterMax', 'Total_BONDS', 'Total_WIRES',
    'Total_Availability', 'Total_Utilization', 'Total_Production',
    'TD_Height_Src', 'TD_Force_Src', 'TD_Speed_Src',
    'TD_Height_Dst', 'TD_Force_Dst', 'TD_Speed_Dst',
    'Bond_Error_Number', 'Bond_Error_Code',
]

RUL_COLUMNS = ['Wedge_RUL_pct', 'Guide_RUL_pct', 'Cutter_RUL_pct']
ALL_CARRY_COLUMNS = METADATA_COLUMNS + ['Machine_Serial', 'Machine_Type', 'File_Date']

# ==============================================================================
# PART COUNTER (Example template logic)
# Format : PART_DEMO_260813_00001
# ==============================================================================
def _extract_serial_suffix(machine_serial: str) -> str:
    parts = str(machine_serial).strip().split('-')
    return parts[-1][-4:] if len(parts) > 1 else str(machine_serial)[-4:]

def _format_part_number(machine_serial: str, file_date: str, counter: int) -> str:
    suffix = _extract_serial_suffix(machine_serial)
    date_compact = str(file_date).replace('-', '')[2:]
    return f"PART_{suffix}_{date_compact}_{counter:05d}"

def _get_counter_filename(machine_serial: str, file_date: str) -> str:
    suffix = _extract_serial_suffix(machine_serial)
    date_compact = str(file_date).replace('-', '')[2:]
    return f"PART_counter_{suffix}_{date_compact}.txt"

def _load_counter(folder: str, machine_serial: str, file_date: str) -> int:
    try:
        fname = _get_counter_filename(machine_serial, file_date)
        with open(os.path.join(folder, fname), 'r') as f:
            return int(f.read().strip())
    except Exception:
        return 0

def _save_counter(folder: str, machine_serial: str, file_date: str, value: int):
    os.makedirs(folder, exist_ok=True)
    fname = _get_counter_filename(machine_serial, file_date)
    with open(os.path.join(folder, fname), 'w') as f:
        f.write(str(value))

def _detect_machine_info(filepath, encoding):
    # Fallback example parsing or generic placeholders
    serial = "DEMO-SERIAL-01"
    mtype = "MACHINE_MODEL_A"
    fdate = "2026-08-21"
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            first_line = f.readline().strip()
        m = re.search(r"Machine:\s*([\w\-]+),\s*Type:\s*([\w\-]+)\s+Date:\s*(\S+)", first_line)
        if m:
            serial, mtype, fdate = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
    except Exception:
        pass
    return serial, mtype, fdate

def _find_header_row(filepath, encoding):
    with open(filepath, 'r', encoding=encoding) as f:
        for line_idx, line in enumerate(f):
            for sep in ['\t', ';', ',']:
                if any(p.strip() == 'TimeStamp' for p in line.split(sep)):
                    return line_idx, sep
    return None, ';'

def _parse_samples(cell_value):
    if pd.isna(cell_value) or str(cell_value).strip() == "":
        return []
    result = []
    for part in str(cell_value).strip().split(","):
        try:
            result.append(float(part.strip()))
        except ValueError:
            pass
    return result

def _calc_rul_pct(counter_col, max_col, df):
    if counter_col not in df.columns or max_col not in df.columns:
        return pd.Series([pd.NA] * len(df), index=df.index)
    counter = pd.to_numeric(df[counter_col], errors='coerce')
    maximum = pd.to_numeric(df[max_col], errors='coerce')
    valid = maximum.notna() & (maximum > 0) & counter.notna()
    result = pd.Series([pd.NA] * len(df), index=df.index, dtype=object)
    result[valid] = ((1 - counter[valid] / maximum[valid]) * 100).round(2)
    return result

def process_machine_files(input_prefix: str, output_prefix: str) -> None:
    print(f"Processing data from {input_prefix} to {output_prefix} using generic template logic.")