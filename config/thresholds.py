# MaïsMap — Agronomic and analytical thresholds
# Sources: FAO guidelines for Sahelian/Sudanian zone maize; AGRHYMET methodology

# --- Rainy-season onset (Sivakumar 1988 / AGRHYMET method) ---
# Onset: first day after April 1 with >= ONSET_RAIN_MM over ONSET_DAYS consecutive days,
# not followed by a dry spell >= ONSET_DRY_DAYS within the next ONSET_WINDOW days.
ONSET_START_DOY = 91          # April 1 — earliest plausible onset
ONSET_RAIN_MM = 20.0          # mm over the trigger window
ONSET_DAYS = 3                # consecutive days for the trigger
ONSET_DRY_DAYS = 7            # dry-spell length that invalidates onset
ONSET_WINDOW = 30             # days after trigger to check for dry spell

# --- False start ---
# A false start occurs when an apparent onset is followed by >= FALSE_START_DRY_DAYS
# consecutive days with < DRY_DAY_THRESHOLD mm within FALSE_START_WINDOW days.
FALSE_START_DRY_DAYS = 10
FALSE_START_WINDOW = 30
DRY_DAY_THRESHOLD = 1.0       # mm — below this a day is considered dry

# --- Dry spells ---
# Maximum consecutive dry days within the growing season (onset to onset + 120 days)
DRY_SPELL_CRITICAL = 10       # days — agronomically critical for maize
DRY_SPELL_SEVERE = 15         # days — severe stress

# --- Heat stress ---
# Tmax threshold for heat stress on maize (pollen viability affected above 35 °C)
HEAT_STRESS_TMAX = 35.0       # °C
HEAT_DAYS_MODERATE = 10       # days above threshold — moderate concern
HEAT_DAYS_HIGH = 20           # days above threshold — high concern

# --- Risk model weights (must sum to 1.0) ---
# Rationale: false start is the primary risk for sowing failure in this zone;
# dry spells during establishment are secondary; heat stress is tertiary.
RISK_WEIGHT_FALSE_START = 0.40
RISK_WEIGHT_DRY_SPELL = 0.35
RISK_WEIGHT_HEAT = 0.25

# Risk class boundaries (score 0–100)
RISK_LOW_MAX = 33
RISK_MEDIUM_MAX = 66
