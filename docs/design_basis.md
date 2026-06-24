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
- Design choice: 4500 MVA assumed as 90% of the 3-phase fault level (5000 MVA)
  ,a conservative engineering approximation used when utility zero-sequence
  source impedance data is unavailable.
- Limitation: actual SLG fault level requires zero-sequence impedance data
  from the serving utility (WAPA/WACM). This value should be verified against
  real utility interconnection data before use in a real protection study.

### System Base Power: Sbase = 10MVA
- Selected Sbase = 10 MVA because of the system largest MVA rating is 10MVA and
 the all other equipment rating have signifcantly lesser MVA ratings.
- Since T1's nameplate rating is also 10 MVA, the scaling factor comes as unity. 
This helps in calculating per unit values while doing load flow analysis.

### Utility Voltage: 69 kV
- According to ANSI C84.1 Table 1; 69kV is an industrial standard voltage rating
 in sub-transmission voltage class.
- It is appropriate for an industrial substation in the WACM region served by WAPA.

### T1_Secondary: 13.8kV
- 13.8kV is a standard ANSI C84.1 distribution voltage class, the 69kV/13.8kV ratio 
gives a clean 5:1 turns ratio simplifying per-unit calculations.
- 13.8kV specifically is preferred over other distribution voltages for industrial 
applications because it aligns with NEMA MG1 standard motor voltage classes, allowing
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
- Feeder Peak demand for IEEE 13-BUS system from every new load gives 4054 kVA at 0.855 power factor.
- According to IEEE C57.91: In continous operation of a transformer, the load rating
should not exceed 80% of nameplate rating.
- Minimum Rating: 4054/0.80 = 5067kVA
- Next Standard size above the minimum rating per IEEE C57.12.10 is 7500kVA, which gives peak load of 54%,
providing room for thermal margin and load growth

### Bridging Transformer Impedance: Z% = 5.75%
- Per IEEE C57.12.36-2017 impedance table, for transformers in the 5000–10000 kVA range
- Primary voltage 13.8kV corresponds to standard BIL of 110 kV per IEEE C57.12.00
- At this kVA and BIL class, standard impedance voltage is 5.75%

### Bridging Transformer Resistance: R% = 0.5%
- Same as T1, mid-range value for a typical liquid-immersed transformer, in absence of nameplate
- Must be replaced with actual nameplate data before used in real protection or arc flash analysis,
measured per IEEE C57.12.90

### MCC_VOLTAGE_KV = 0.48
- Standard voltage rating as per ANSI C84.1
- Industrial utilization voltage for large motor loads 
- Higher voltage, reduces current for same power. Hence, less ohmic losses and smaller conductors
- Sits below the 600V NEC/OSHA low-to-medium voltage boundary, avoiding strict insulation requirements.

### Lighting_Voltage_KV = 0.208
- Standard voltage rating as per ANSI C84.1
- 208V in three phase gives 120V line-neutral voltage.
- Serves both three phase and standard 120V single phase loads from same transformer
- Standard rating for office, lighting and mixed commerical loads.
