# MaïsMap — Scientific Methodology

## Geographic Grid

- **Resolution:** 0.5° × 0.5° (~55 km at 10°N latitude)
- **Justification:** Matches the native resolution of NASA POWER (0.5°). Using a finer grid would imply precision not supported by the source data.
- **Study area:** Northern and Far North Cameroon — 13°–16°E, 7.5°–12.5°N
- **Cell count:** 60 cells per year (6 lon × 10 lat)
- **Coordinate system:** EPSG:4326 (WGS84), coordinate order [longitude, latitude]

> ⚠️ A 0.5° grid cannot capture local microclimatic variation. Results represent regional-scale patterns only.

---

## Rainy-Season Onset — Sivakumar (1988) / AGRHYMET Method

**Definition:** The first day after April 1 (DOY 91) on which cumulative rainfall over 3 consecutive days reaches or exceeds 20 mm, provided that no dry spell of 7 or more consecutive days occurs in the following 30 days.

**Parameters:**
| Parameter | Value | Source |
|---|---|---|
| Earliest onset date | April 1 (DOY 91) | AGRHYMET |
| Trigger rainfall | ≥ 20 mm over 3 days | Sivakumar (1988) |
| Invalidating dry spell | ≥ 7 consecutive dry days | AGRHYMET |
| Validation window | 30 days after trigger | AGRHYMET |
| Dry day threshold | < 1 mm/day | Standard |

**Reference:** Sivakumar, M.V.K. (1988). Predicting rainy season potential from the onset of rains in Southern Sahelian and Sudanian climatic zones of West Africa. *Agricultural and Forest Meteorology*, 42(4), 295–305.

---

## False Start

**Definition:** A false start occurs when the first rainfall trigger (≥ 20 mm over 3 days after April 1) is followed by a dry spell of ≥ 10 consecutive days within the next 30 days.

**Distinction from onset:** The onset algorithm requires *no* 7-day dry spell in 30 days. The false-start algorithm specifically detects a *10-day* dry spell — a stricter condition that identifies cases where farmers who sowed at the trigger would face crop failure.

**Parameters:**
| Parameter | Value |
|---|---|
| Post-trigger dry spell | ≥ 10 consecutive days |
| Check window | 30 days after trigger |

---

## Dry Spells

**Definition:** Maximum number of consecutive days with rainfall < 1 mm within the agricultural season (onset DOY to onset + 120 days).

**Thresholds:**
| Level | Days | Agronomic significance |
|---|---|---|
| Critical | ≥ 10 days | Significant stress during establishment |
| Severe | ≥ 15 days | High risk of crop failure |

**Season window:** 120 days from onset (approximate maize growing period in this zone).

---

## Heat Stress

**Definition:** Count of days with maximum temperature (Tmax) exceeding 35°C within the season window.

**Threshold:** 35°C — above this temperature, maize pollen viability is significantly reduced.

**Source:** CIMMYT heat-stress guidelines; Schlenker & Roberts (2009).

**Variable used:** NASA POWER T2M_MAX (maximum temperature at 2 m).

> Note: T2M_MAX is measured at 2 m height. Canopy temperatures may differ. This threshold is an approximation.

---

## Risk Model

**Formula:**

```
score = 0.40 × false_start_score + 0.35 × dry_spell_score + 0.25 × heat_score
```

Each component is normalised to 0–100 before weighting.

**Component normalisation:**
- False start: 100 if true, 0 if false
- Dry spell: 0–60 (proportional below critical), 60 at critical, 100 at severe+
- Heat: 0–60 (proportional below moderate), 60 at moderate, 100 at high+

**Risk classes:**
| Score | Class |
|---|---|
| 0–33 | LOW (Faible) |
| 34–66 | MEDIUM (Modéré) |
| 67–100 | HIGH (Élevé) |

**Weight rationale:** False start is the primary risk for sowing failure in the Sudano-Sahelian zone. Dry spells during establishment are secondary. Heat stress is tertiary given that temperatures in this zone are already near the threshold throughout the season.

> ⚠️ These weights are provisional and have not been validated against observed crop yield data. They are documented in `config/thresholds.py` and can be adjusted.

---

## Sowing Recommendations

Recommendations are generated from the combination of onset date, false-start status and risk class. They use cautious language and explicitly state that they must be confirmed with local agricultural extension services.

**This tool does not guarantee a sowing date.**

---

## Missing Data

- Missing rainfall values from NASA POWER are flagged as `None` and are **not** replaced with zero.
- Missing temperature values are excluded from heat-day counts.
- Cells with missing onset data are reported as "no onset detected" rather than assigned a default date.
- Missing indicator values in the risk model are treated conservatively as moderate risk (score = 50).
