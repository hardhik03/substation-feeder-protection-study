# Substation Design + IEEE 13-Bus Feeder Protection Coordination Study

A parametric, end-to-end power systems analysis project modeling a complete
industrial distribution system from a 69kV utility source down to a standard
IEEE distribution test feeder, with real-time grid data integration and
protection coordination verified against IEEE standards.

## What this project does

Models a complete T&D system in one continuous circuit:
Utility (69kV, 5000 MVA fault level : WACM/WAPA, Fort Collins CO)
│
T1: 69kV/13.8kV, 10 MVA, Delta/Wye-Grounded (IEEE C57.12.10)
│
13.8kV Substation Bus
│
Bridge: 13.8kV/4.16kV, 7500 kVA (IEEE C57.12.36)
│
IEEE 13-Bus Distribution Test Feeder (Kersting/IEEE PES, 4.16kV)
│
SEL-351 relay protection coordinated end-to-end (IEEE C37.112, IEEE 242)

Runs a full analysis pipeline in one command:
1. Config validation against IEEE/ANSI design parameter limits
2. Real-time EIA WACM grid demand data fetch with outlier cleaning
3. 24-hour time-series load flow (OpenDSS)
4. Three-phase short circuit study across all key buses
5. Protection coordination with TCC curve generation
6. Regression testing to catch model breakage automatically

## Why this is different from a typical student project

- Every design parameter traces to a real IEEE/ANSI standard — no
  assumed or AI-generated values. See docs/design_basis.md.
- Load profile uses real hourly demand data from the EIA Open Data
  API (WACM balancing authority, the actual grid region for Fort
  Collins, CO), not assumed static loads.
- The IEEE 13-bus feeder uses the official EPRI/Kersting published
  test case, with the idealized infinite-bus source replaced by a
  real finite-impedance substation, showing the actual voltage impact
  of source impedance on feeder performance.
- The entire pipeline is config-driven and parametric: change one
  value in config/system_parameters.py and regenerate everything.

## Key results

- All buses within ANSI C84.1 Range A (0.95–1.05 pu) across all
  24 hours under real WACM demand profile
- Three-phase fault current at 13.8kV bus: 5068 A (121 MVA),
  verified against hand calculation within 0.6%
- Protection coordination passes at all fault current levels:
  minimum CTI = 0.631s (requirement: 0.3s per IEEE 242-2001)

## Tools and standards

| Tool/Standard | Purpose |
|---|---|
| OpenDSS (opendssdirect.py) | Power flow and fault study solver |
| Python (pandas, numpy, matplotlib) | Data processing, analysis, plotting |
| EIA Open Data API | Real-time WACM regional demand data |
| IEEE C57.12.00/10/36/90/91 | Transformer design basis |
| IEEE C37.112-1996/2018 | Relay curve equations and constants |
| IEEE Std 141 (Red Book) | Industrial power system design |
| IEEE Std 242 (Buff Book) | Protection coordination |
| ANSI C84.1 | Voltage tolerance limits |
| NEMA MG1 | Motor voltage class justification |

## Repository structure
├── config/

│   └── system_parameters.py    ← single source of truth for all parameters

├── models/

│   ├── substation_core.dss     ← utility source + T1 transformer

│   ├── ieee13_original/        ← untouched official EPRI/Kersting reference

│   ├── ieee13_bridged.dss      ← modified feeder (idealized source removed)

│   ├── master_combined.dss     ← top-level: ties the whole system together

│   └── loadshape_wacm.dss      ← generated from live EIA data

├── scripts/

│   ├── validate_config.py      ← parameter sanity checks

│   ├── build_loaddemand.py      ← EIA data fetch + LoadShape generation

│   ├── regression_test.py      ← automated voltage benchmark check

│   ├── run_loadflow.py         ← 24-hour time-series load flow

│   ├── run_short_circuit.py    ← fault study across key buses

│   └── run_protection_coordination.py  ← TCC + CTI verification

├── docs/

│   ├── design_basis.md         ← IEEE/ANSI reference for every parameter

│   └── results.md              ← analysis outputs and observations

├── results/                    ← generated plots and CSV exports

├── calculations/               ← per-unit base values spreadsheet

├── run_all.py                  ← single entry point: runs full pipeline

└── requirements.txt            ← pinned dependencies

## How to run

```bash
# 1. Clone the repo
git clone https://github.com/hardhik03/substation-feeder-protection-study.git
cd substation-feeder-protection-study

# 2. Create and activate virtual environment
python3 -m venv dss_env
source dss_env/bin/activate        # Mac/Linux
dss_env\Scripts\Activate.ps1      # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your EIA API key (free at https://www.eia.gov/opendata/)
echo "EIA_API_KEY=your_key_here" > .env

# 5. Run the full pipeline
python run_all.py
```

## References

- IEEE PES Distribution Test Feeder Working Group, 13-Node Test Feeder,
  approved at 2000 PES Summer Meeting. W.H. Kersting, NMSU.
- IEEE Std C57.12.00-2021, C57.12.10-2017, C57.12.36-2017, C57.12.90,
  C57.91 — Transformer standards
- IEEE Std C37.112-2018 : Inverse-Time Overcurrent Relay Equations
- IEEE Std 141-1993 (Red Book) : Industrial Power Distribution
- IEEE Std 242-2001 (Buff Book) : Protection and Coordination
- ANSI C84.1-2020 : Voltage Ratings
- NEMA MG1 : Motor and Generator Standards
- EIA Open Data API : https://www.eia.gov/opendata/
- Stojanovic & Djuric, Journal of Electrical Engineering, Vol 65,
  No. 4, 2014 : relay curve constants verification