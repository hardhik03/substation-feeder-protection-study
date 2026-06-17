"""
Single source of truth for all electrical parameters in the combined
Substation + IEEE 13-Bus Feeder Protection Coordination Study.

Every generator script (per-unit tables, .dss model files, relay setting
sheets) imports from here. Change a value once, regenerate everything
downstream — never hand-edit a number inside a generated file directly.
"""

# --- System-wide base (must stay constant across every voltage level) ---
SBASE_MVA = 10.0

# --- Utility / Source ---
UTILITY_VOLTAGE_KV = 69.0
UTILITY_FAULT_MVA_3PH = 5000.0
UTILITY_FAULT_MVA_1PH = 4500.0

# --- T1: Main Substation Transformer (69kV / 13.8kV) ---
T1_RATING_MVA = 10.0
T1_PRIMARY_KV = 69.0
T1_SECONDARY_KV = 13.8
T1_PCT_Z = 8.0
T1_PCT_R = 0.5

# --- Bridging Transformer (13.8kV / 4.16kV) -- NEW, feeds the IEEE 13-bus model ---
BRIDGE_RATING_KVA = 5000.0
BRIDGE_PRIMARY_KV = T1_SECONDARY_KV
BRIDGE_SECONDARY_KV = 4.16
BRIDGE_PCT_Z = 5.5      # realistic value; the standalone IEEE13 case fakes near-zero Z
BRIDGE_PCT_R = 0.5

# --- Downstream substation distribution (480V / 208V) ---
MCC_VOLTAGE_KV = 0.48
LIGHTING_VOLTAGE_KV = 0.208

# --- Voltage levels feeding the per-unit base table (label -> kV) ---
VOLTAGE_LEVELS_KV = {
    "Utility": UTILITY_VOLTAGE_KV,
    "Substation Bus": T1_SECONDARY_KV,
    "Feeder Bridge": BRIDGE_SECONDARY_KV,
    "MCC Utilization": MCC_VOLTAGE_KV,
    "Lighting/Office": LIGHTING_VOLTAGE_KV,
}

NOTES = {
    "Utility": f"Substation incoming, {UTILITY_FAULT_MVA_3PH:.0f} MVA fault level",
    "Substation Bus": "T1 secondary, also feeder source side",
    "Feeder Bridge": "IEEE 13-bus nominal voltage, bridge transformer secondary",
    "MCC Utilization": "Substation 480V distribution",
    "Lighting/Office": "Substation 208V distribution",
}