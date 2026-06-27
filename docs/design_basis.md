# Design Basis

Combined Substation + IEEE 13-Bus Feeder Protection Coordination Study

## Design Parameter Basis

### T1 Transformer Impedance: 8% Z
- Standard reference: ANSI/IEEE C57.12.10
- Default for this voltage/Basic Insulation Level class (450kV): 8.5% (without LTC)
- Design choice: 8% selected slightly below default to reduce secondary
  voltage drop; manufacturable upon specification with manufacturer agreement
- Confirmation required: short-circuit study must verify secondary fault
  current stays within switchgear interrupting ratings

### Utility Fault Level: 5000 MVA at 69kV (3 Phase)
- Standard reference: IEEE Std 141-1993 (Red Book), Section 4.3.1
- Documented typical range: 1,000–5,000 MVA for transmission-level services
- Design choice: upper-bound conservative assumption, correct practice for
  equipment sizing since it produces the maximum fault current the switchgear
  must interrupt
- Source: WACM (Western Area Power Administration – Rocky Mountain Region),
  the actual balancing authority for Fort Collins, CO

### Utility Single-Phase Fault Level: 4500 MVA at 69kV
- Standard reference: IEEE Std 141-1993, Section 4.3.1; IEEE Std 551-2006
  (Violet Book) for symmetrical component methodology
- Basis: Single-line-to-ground fault current requires symmetrical component
  analysis (Z1 + Z2 + Z0 in series). At the 69kV utility bus, the delta
  primary winding of T1 blocks zero-sequence current propagation per
  symmetrical components theory, making SLG fault MVA lower than 3-phase MVA.
- Design choice: 4500 MVA assumed as 90% of the 3-phase fault level (5000 MVA),
  a conservative engineering approximation used when utility zero-sequence
  source impedance data is unavailable.
- Limitation: actual SLG fault level requires zero-sequence impedance data
  from the serving utility (WAPA/WACM). This value should be verified against
  real utility interconnection data before use in a real protection study.

### System Base Power: Sbase = 10 MVA
- Selected Sbase = 10 MVA because the system's largest MVA rating is 10 MVA and
  all other equipment ratings have significantly lesser MVA ratings.
- Since T1's nameplate rating is also 10 MVA, the scaling factor comes as unity.
  This helps in calculating per unit values while doing load flow analysis.

### Utility Voltage: 69 kV
- According to ANSI C84.1 Table 1, 69kV is a standard voltage rating
  in the sub-transmission voltage class.
- It is appropriate for an industrial substation in the WACM region served by WAPA.

### T1 Secondary Voltage: 13.8 kV
- 13.8kV is a standard ANSI C84.1 distribution voltage class. The 69kV/13.8kV ratio
  gives a clean 5:1 turns ratio simplifying per-unit calculations.
- 13.8kV is preferred over other distribution voltages for industrial applications
  because it aligns with NEMA MG1 standard motor voltage classes, allowing
  direct connection of large motors without additional transformation.

### T1 Transformer MVA Rating: 10 MVA (ONAF) / 7.5 MVA (ONAN)
- Standard reference: IEEE Std C57.12.00-2021 (general requirements),
  IEEE Std C57.12.10-2017 (liquid-immersed power transformers),
  IEEE Std C57.12.36-2017 (distribution substation transformers)
- Typical range: 5–20 MVA for industrial/commercial substation transformers
  at this voltage class, per IEEE C57.12.00 and C57.12.36 documentation
- Design choice: 10 MVA selected as mid-range value within the documented
  typical range, consistent with an industrial facility requiring significant
  distribution capacity while remaining within the standard substation
  transformer size class
- ONAF rating (10 MVA) used for fault calculations and equipment sizing
  since it represents maximum deliverable power and therefore worst-case
  fault current per IEEE Std 141 short-circuit methodology
- ONAN rating (7.5 MVA) is the self-cooled continuous rating and applies
  to thermal loading studies, which are outside current project scope
- Cooling class designation per IEEE Std C57.12.00-2021, Section on
  Cooling Class Designations

### T1 Winding Resistance: %R = 0.5%
- %R represents the transformer winding resistance expressed as a
  percentage of base impedance. It governs I²R (copper/load) losses
  when current flows through the windings.
- Standard reference: IEEE C57.12.90 defines the factory acceptance
  test procedure for measuring and verifying load losses. The actual
  %R value is specific to the manufacturer's design and is stated on
  the transformer nameplate after factory testing.
- Design assumption: 0.5% is used as a typical mid-range assumption
  for a 10 MVA liquid-immersed power transformer in the absence of
  real nameplate data. This gives X/R = 7.984/0.5 = 15.97, which is
  consistent with typical power transformer X/R ratios of 10-20 cited
  in IEEE Std 141 for short-circuit asymmetry calculations.
- Limitation: this value must be replaced with actual manufacturer
  nameplate data before use in a real protection or arc flash study.

### Bridging Transformer Rating: 7500 kVA
- Feeder peak demand for IEEE 13-bus system calculated from published
  load data gives 4054 kVA at 0.855 power factor.
- Per IEEE C57.91: in continuous operation, transformer load should
  not exceed 80% of nameplate rating.
- Minimum rating: 4054 / 0.80 = 5067 kVA
- Next standard preferred size per IEEE C57.12.10-2017 is 7500 kVA,
  giving a peak loading of 54% — providing thermal margin and load growth headroom.

### Bridging Transformer Impedance: Z% = 5.75%
- Per IEEE C57.12.36-2017 impedance table, for transformers in the 5000–10000 kVA range
- Primary voltage 13.8kV corresponds to standard BIL of 110 kV per IEEE C57.12.00
- At this kVA and BIL class, standard impedance voltage is 5.75%

### Bridging Transformer Resistance: R% = 0.5%
- Same assumption as T1 — mid-range value for a typical liquid-immersed
  transformer in the absence of nameplate data
- Must be replaced with actual nameplate data before use in a real
  protection or arc flash study, measured per IEEE C57.12.90

### MCC Utilization Voltage: 0.48 kV
- Standard voltage rating per ANSI C84.1
- Industrial utilization voltage for large motor loads
- Higher voltage reduces current for the same power demand,
  resulting in smaller conductors and lower I²R losses
- Sits below the 600V NEC/OSHA low-to-medium voltage boundary,
  avoiding more stringent insulation requirements

### Lighting/Office Voltage: 0.208 kV
- Standard voltage rating per ANSI C84.1
- 208V three-phase gives 120V line-to-neutral voltage
- Serves both three-phase office equipment and standard 120V
  single-phase receptacles from the same transformer
- Standard utilization voltage for office, lighting, and mixed commercial loads

## Relay Curve Equation and Constants

Equation: t = TD × [A / ((I/Ip)^p - 1) + B]

Where:
- t  = relay operating time (seconds)
- TD = time dial setting
- I  = fault current (A)
- Ip = pickup current setting (A)
- A, B, p = curve shape constants per IEEE C37.112

Curve selected: U1 (Moderately Inverse) — SEL-351S designation
Constants per IEEE C37.112-1996, Table 1:
  A = 0.0515, B = 0.1140, p = 0.02

Primary standard: IEEE Std C37.112-1996 / C37.112-2018
  (paywalled: https://ieeexplore.ieee.org/document/8635630)

Constants independently confirmed in:
  Stojanovic & Djuric, "Table Based Algorithm for Inverse-Time
  Overcurrent Relay," Journal of Electrical Engineering, Vol 65,
  No. 4, 2014, Table 1.
  Free access: https://scispace.com/pdf/inverse-time-overcurrent-relay-c001qnhvoy.pdf

SEL-351S relay implementation: U1 curve (Moderately Inverse),
  Table 9.3, SEL-351S Instruction Manual.
  Note: exact equation form in SEL manual could not be verified
  from a freely accessible source — should be confirmed against
  the actual relay manual before commissioning.

Limitation: The placement of B relative to TD (inside vs outside
  the TD multiplier) differs between some secondary sources. The
  form used here (B inside the TD bracket) follows the most
  commonly cited interpretation of IEEE C37.112. For a real relay
  study, verify against the manufacturer's programming manual.

## Relay Settings Basis

### Pickup Current Selection (IEEE 242-2001)
- CB1: 1.5 × T1 full load current (418A) = 627A → 630A
- CB2: 1.5 × Bridge transformer full load current (1040A) = 1560A

### Time Dial Derivation
- CB2 TD derived by targeting 0.3s trip time at Bus 650 maximum
  fault current (8677A referred to 4.16kV side)
- CB1 TD derived by requiring t_CB1 ≥ t_CB2 + CTI at the same
  fault current referred to 13.8kV side
- CTI = 0.3s per IEEE 242-2001