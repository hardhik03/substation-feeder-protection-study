"""
Scenario definitions for parametric analysis.
Each scenario tests a different system configuration or contingency.

Scenario 1: Normal operation     — baseline, real WACM demand profile
Scenario 2: ONAN contingency     — T1 derated to 7.5 MVA (cooling fans failed)
Scenario 3: Unbalanced loading   — concentrated load on heaviest phase
"""

SCENARIOS = {
    "normal_operation": {
        "description": "Normal operating conditions — real WACM demand profile",
        "t1_kva": 10000,        # ONAF rating — full capacity
        "t1_pct_r": 0.5,
        "load_phase_multipliers": {1: 1.0, 2: 1.0, 3: 1.0},  # balanced
        "results_subfolder": "scenario_normal",
    },
    "onan_contingency": {
        "description": "T1 derated to ONAN rating — cooling fans failed",
        "t1_kva": 7500,         # ONAN rating — self-cooled only
        "t1_pct_r": 0.5,
        "load_phase_multipliers": {1: 1.0, 2: 1.0, 3: 1.0},  # balanced
        "results_subfolder": "scenario_onan",
    },
    "unbalanced_loading": {
        "description": "Unbalanced loading — Phase A concentrated at 140%",
        "t1_kva": 10000,        # ONAF rating — full capacity
        "t1_pct_r": 0.5,
        "load_phase_multipliers": {1: 1.4, 2: 0.9, 3: 0.7},  # phase A heavy
        "results_subfolder": "scenario_unbalanced",
    },
}