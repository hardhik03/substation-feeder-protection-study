import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'config'))
from system_parameters import (
    SBASE_MVA, UTILITY_VOLTAGE_KV, UTILITY_FAULT_MVA_3PH,
    UTILITY_FAULT_MVA_1PH, T1_RATING_MVA, T1_PRIMARY_KV,
    T1_SECONDARY_KV, T1_PCT_Z, T1_PCT_R, BRIDGE_RATING_KVA,
    BRIDGE_PRIMARY_KV, BRIDGE_SECONDARY_KV, BRIDGE_PCT_Z, BRIDGE_PCT_R,
    MCC_VOLTAGE_KV, LIGHTING_VOLTAGE_KV
)

errors = []

# ── Basic sanity: all values must be positive ─────────────────────
for name, val in [
    ('SBASE_MVA', SBASE_MVA),
    ('UTILITY_VOLTAGE_KV', UTILITY_VOLTAGE_KV),
    ('UTILITY_FAULT_MVA_3PH', UTILITY_FAULT_MVA_3PH),
    ('UTILITY_FAULT_MVA_1PH', UTILITY_FAULT_MVA_1PH),
    ('T1_RATING_MVA', T1_RATING_MVA),
    ('T1_PCT_Z', T1_PCT_Z),
    ('T1_PCT_R', T1_PCT_R),
    ('BRIDGE_RATING_KVA', BRIDGE_RATING_KVA),
    ('BRIDGE_PCT_Z', BRIDGE_PCT_Z),
    ('BRIDGE_PCT_R', BRIDGE_PCT_R),
]:
    if val <= 0:
        errors.append(f'{name} must be positive, got {val}')

# ── Impedance triangle: %R cannot exceed %Z ───────────────────────
if T1_PCT_R >= T1_PCT_Z:
    errors.append(
        f'T1: %R ({T1_PCT_R}) must be less than %Z ({T1_PCT_Z}). '
        f'%X would be imaginary.'
    )

if BRIDGE_PCT_R >= BRIDGE_PCT_Z:
    errors.append(
        f'Bridge: %R ({BRIDGE_PCT_R}) must be less than %Z ({BRIDGE_PCT_Z}). '
        f'%X would be imaginary.'
    )

# ── Voltage levels must decrease downstream ───────────────────────
if T1_PRIMARY_KV <= T1_SECONDARY_KV:
    errors.append(
        f'T1 is a step-down transformer: primary ({T1_PRIMARY_KV} kV) '
        f'must be greater than secondary ({T1_SECONDARY_KV} kV)'
    )

if BRIDGE_PRIMARY_KV <= BRIDGE_SECONDARY_KV:
    errors.append(
        f'Bridge is a step-down transformer: primary ({BRIDGE_PRIMARY_KV} kV) '
        f'must be greater than secondary ({BRIDGE_SECONDARY_KV} kV)'
    )

# ── Single-phase fault MVA must be less than 3-phase ─────────────
if UTILITY_FAULT_MVA_1PH >= UTILITY_FAULT_MVA_3PH:
    errors.append(
        f'Single-phase fault MVA ({UTILITY_FAULT_MVA_1PH}) should be '
        f'less than 3-phase fault MVA ({UTILITY_FAULT_MVA_3PH}) '
        f'due to delta winding blocking zero-sequence current'
    )

# ── Sbase must not exceed T1 rating ──────────────────────────────
if SBASE_MVA > T1_RATING_MVA:
    errors.append(
        f'SBASE_MVA ({SBASE_MVA}) exceeds T1 rating ({T1_RATING_MVA} MVA). '
        f'Per-unit scaling factor would exceed unity.'
    )

# ── Report ────────────────────────────────────────────────────────
if errors:
    print('CONFIG VALIDATION FAILED:')
    for e in errors:
        print(f'  ✗ {e}')
    sys.exit(1)
else:
    print('CONFIG VALIDATION PASSED')
    print(f'All parameters physically consistent')
    sys.exit(0)