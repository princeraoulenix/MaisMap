"""
Crop Rotation Engine for MaïsMap.

Compares three agronomically documented rotation strategies for Northern Cameroon.
All assessments are based on published agronomic literature and are clearly labeled
as evidence-based hypotheses, not field-validated measurements.

Sources:
- MINADER (2023). Guide technique de production du maïs au Cameroun.
- Dugje et al. (2009). Farmers' Guide to Cowpea Production in West Africa. IITA.
- Bationo et al. (2012). Soil Organic Carbon Dynamics, Functions and Management in
  West African Agro-ecosystems. Springer.
- Kamara et al. (2014). Maize-cowpea intercropping in the Sudan Savanna zone of
  West Africa. Experimental Agriculture.
- FAO (2018). Crop Water Requirements. FAO Irrigation and Drainage Paper 56.
"""

# ── Documented crop calendar for Northern Cameroon (Sudano-Sahelian zone) ────
# Source: MINADER agricultural calendar for North and Far North regions
CROP_CALENDARS = {
    "maize": {
        "sowing_window": "May–June (Nord), June (Extreme-Nord)",
        "growing_days": "90–120 days",
        "harvest": "September–October",
        "water_req_mm": "500–800",  # FAO Irrigation Paper 56
        "heat_tolerance": "Moderate — sensitive above 35°C at flowering",
        "drought_tolerance": "Low during establishment and flowering",
    },
    "cowpea": {
        "sowing_window": "June–July (after maize establishment)",
        "growing_days": "60–90 days",
        "harvest": "September–October",
        "water_req_mm": "300–500",
        "heat_tolerance": "Good — tolerates up to 40°C",
        "drought_tolerance": "Good — deep rooting system",
        "n_fixation_kg_ha": "40–200",  # Dugje et al. 2009 — wide range, site-dependent
    },
    "groundnut": {
        "sowing_window": "May–June",
        "growing_days": "90–120 days",
        "harvest": "September–October",
        "water_req_mm": "400–600",
        "heat_tolerance": "Good",
        "drought_tolerance": "Moderate",
        "n_fixation_kg_ha": "40–150",  # Bationo et al. 2012
    },
    "sorghum": {
        "sowing_window": "June–July",
        "growing_days": "100–130 days",
        "harvest": "October–November",
        "water_req_mm": "400–650",
        "heat_tolerance": "Very good — C4 crop",
        "drought_tolerance": "Very good",
    },
}

# ── Three rotation strategies ─────────────────────────────────────────────────
ROTATION_STRATEGIES = {
    "A": {
        "id": "A",
        "name": "Baseline — Maize monoculture",
        "name_fr": "Référence — Monoculture de maïs",
        "sequence": ["Maize", "Maize", "Maize"],
        "description": (
            "Continuous maize cultivation, the dominant system in Northern Cameroon. "
            "Documented by MINADER as the most common smallholder practice in the Nord "
            "and Extreme-Nord regions."
        ),
        "climate_suitability": "Moderate — dependent on reliable onset and absence of false starts",
        "soil_compatibility": "Moderate — depletes nitrogen and organic matter over time",
        "water_demand": "High (500–800 mm/season)",
        "nitrogen_contribution": "None — requires external nitrogen inputs",
        "soil_organic_matter": "Declining trend under continuous cultivation without residue management",
        "erosion_protection": "Low during establishment; moderate at canopy closure",
        "pest_disease_risk": "High — continuous host for Striga, stem borers, and soil pathogens",
        "growing_season_fit": "Good — single season matches the unimodal rainfall pattern",
        "market_suitability": "Good — established maize market in Northern Cameroon",
        "operational_feasibility": "High — familiar to farmers, established input supply chains",
        "benefits": [
            "Familiar to farmers — low learning curve",
            "Established market and price information",
            "Single crop management simplicity",
        ],
        "risks": [
            "Soil nitrogen depletion without fertilizer",
            "High Striga weed pressure under continuous cultivation",
            "Vulnerability to false starts and dry spells",
            "No income diversification",
        ],
        "confidence": "High — documented local practice",
        "data_gaps": ["Actual yield data for this specific grid", "Fertilizer use rates"],
    },
    "B": {
        "id": "B",
        "name": "Maize–Cowpea rotation",
        "name_fr": "Rotation maïs–niébé",
        "sequence": ["Maize", "Cowpea", "Maize"],
        "description": (
            "Alternating maize with cowpea (Vigna unguiculata), a locally grown legume "
            "with documented nitrogen-fixation potential. Cowpea is widely cultivated in "
            "Northern Cameroon and is well-adapted to the Sudano-Sahelian climate. "
            "This rotation is recommended by IITA for West African smallholders."
        ),
        "climate_suitability": "Good — cowpea is more drought-tolerant than maize",
        "soil_compatibility": "Good — cowpea improves nitrogen availability for subsequent maize",
        "water_demand": "Moderate (maize 500–800 mm; cowpea 300–500 mm)",
        "nitrogen_contribution": (
            "Potential: 40–200 kg N/ha from cowpea fixation (Dugje et al. 2009). "
            "Actual contribution is highly variable and depends on soil pH, rhizobium "
            "populations, and management. This is an agronomic hypothesis, not a "
            "measured value for this specific location."
        ),
        "soil_organic_matter": (
            "Potential improvement from cowpea residues and root biomass. "
            "Magnitude is site-dependent and not quantified here."
        ),
        "erosion_protection": "Moderate — cowpea provides ground cover during the season",
        "pest_disease_risk": "Reduced Striga pressure — cowpea is not a Striga host",
        "growing_season_fit": "Good — cowpea fits the same unimodal season",
        "market_suitability": "Good — cowpea has local and regional markets in Northern Cameroon",
        "operational_feasibility": "Moderate — requires cowpea seed access and basic knowledge",
        "benefits": [
            "Potential nitrogen contribution reducing fertilizer needs (hypothesis)",
            "Reduced Striga weed pressure",
            "Income diversification through cowpea sales",
            "Improved diet diversity (cowpea protein)",
            "Better drought resilience in cowpea years",
        ],
        "risks": [
            "Cowpea yield variability under heat stress",
            "Nitrogen fixation may be limited by soil acidity or rhizobium absence",
            "Cowpea market price volatility",
            "Requires additional seed and management knowledge",
        ],
        "confidence": "Moderate — supported by regional literature; not validated locally",
        "data_gaps": [
            "Local rhizobium populations",
            "Actual N fixation rates for this soil type",
            "Cowpea market prices in target departments",
        ],
    },
    "C": {
        "id": "C",
        "name": "Diversified cereal–legume rotation",
        "name_fr": "Rotation céréales–légumineuses diversifiée",
        "sequence": ["Maize", "Cowpea", "Sorghum"],
        "description": (
            "A three-crop rotation combining maize, cowpea, and sorghum. Sorghum is "
            "well-adapted to the drier conditions of the Extreme-Nord and provides "
            "greater resilience in years with late or unreliable rainfall onset. "
            "This strategy increases crop diversity and reduces dependence on a single "
            "crop's performance."
        ),
        "climate_suitability": (
            "Good — sorghum's superior drought tolerance provides a safety net "
            "in high-risk years. Particularly relevant for Extreme-Nord cells."
        ),
        "soil_compatibility": "Good — diverse root systems and residues benefit soil structure",
        "water_demand": "Variable — sorghum (400–650 mm) is more water-efficient than maize",
        "nitrogen_contribution": (
            "Cowpea year provides potential nitrogen contribution (see Strategy B). "
            "Sorghum year does not fix nitrogen."
        ),
        "soil_organic_matter": (
            "Potentially improved by diverse crop residues. "
            "Sorghum produces high residue biomass. Magnitude not quantified."
        ),
        "erosion_protection": "Good — sorghum's dense canopy and root system protect soil",
        "pest_disease_risk": "Reduced — crop diversity breaks pest and disease cycles",
        "growing_season_fit": (
            "Good for Nord region. Sorghum's longer growing period (100–130 days) "
            "may be marginal in the shortest-season cells of Extreme-Nord."
        ),
        "market_suitability": "Moderate — sorghum market less developed than maize in some areas",
        "operational_feasibility": "Moderate — requires management of three different crops",
        "benefits": [
            "Maximum crop diversity and income diversification",
            "Sorghum provides drought resilience in high-risk years",
            "Reduced pest and disease pressure through rotation",
            "Potential soil health improvement from diverse residues",
            "Reduced total water demand compared to continuous maize",
        ],
        "risks": [
            "Increased management complexity",
            "Sorghum market less reliable than maize in some departments",
            "Three-year rotation requires longer planning horizon",
            "Sorghum growing period may be too long for northernmost cells",
        ],
        "confidence": "Moderate — supported by regional literature; not validated locally",
        "data_gaps": [
            "Sorghum market prices by department",
            "Actual growing season length in northernmost cells",
            "Farmer capacity for three-crop management",
        ],
    },
}

# ── Farmer priority weights ───────────────────────────────────────────────────
PRIORITY_DIMENSIONS = {
    "water_conservation":   {"A": 0.3, "B": 0.6, "C": 0.7},
    "soil_fertility":       {"A": 0.2, "B": 0.7, "C": 0.6},
    "income_diversification": {"A": 0.3, "B": 0.7, "C": 0.8},
    "drought_resilience":   {"A": 0.3, "B": 0.6, "C": 0.8},
    "reduced_erosion":      {"A": 0.3, "B": 0.5, "C": 0.7},
    "lower_inputs":         {"A": 0.3, "B": 0.6, "C": 0.5},
}
# Scores are relative (0–1), not absolute measurements.
# They represent qualitative assessments based on agronomic literature.


def score_strategies(priorities: dict[str, float]) -> dict[str, float]:
    """
    Score each strategy given farmer priority weights.

    Parameters
    ----------
    priorities : dict mapping priority name to weight (0–1)
        e.g. {"water_conservation": 0.8, "soil_fertility": 0.5}

    Returns
    -------
    dict mapping strategy id to weighted score (0–100)
    """
    total_weight = sum(priorities.values())
    if total_weight == 0:
        return {"A": 0.0, "B": 0.0, "C": 0.0}

    scores = {"A": 0.0, "B": 0.0, "C": 0.0}
    for priority, weight in priorities.items():
        if priority in PRIORITY_DIMENSIONS:
            for sid in ["A", "B", "C"]:
                scores[sid] += weight * PRIORITY_DIMENSIONS[priority][sid]

    # Normalize to 0–100
    for sid in scores:
        scores[sid] = round(scores[sid] / total_weight * 100, 1)

    return scores


def climate_suitability_score(risk_class: str, false_start: bool,
                               dry_spell_days: int, strategy_id: str) -> dict:
    """
    Assess how well a strategy fits the observed climate conditions for a cell.

    Returns a dict with score (0–100) and explanation.
    """
    # Base scores by strategy
    base = {"A": 50, "B": 65, "C": 75}
    score = base[strategy_id]
    notes = []

    if false_start:
        if strategy_id == "A":
            score -= 20
            notes.append("False start significantly increases maize sowing risk")
        elif strategy_id == "B":
            score -= 10
            notes.append("False start affects maize year; cowpea year more resilient")
        else:
            score -= 5
            notes.append("False start affects maize year; sorghum year provides resilience")

    if dry_spell_days and dry_spell_days >= 15:
        if strategy_id == "A":
            score -= 15
            notes.append("Severe dry spell — maize monoculture highly vulnerable")
        elif strategy_id == "B":
            score -= 8
            notes.append("Severe dry spell — cowpea more tolerant than maize")
        else:
            score -= 5
            notes.append("Severe dry spell — sorghum provides drought buffer")

    if risk_class == "HIGH":
        if strategy_id == "A":
            score -= 10
        notes.append(f"High overall risk environment")

    score = max(0, min(100, score))
    label = "Favorable" if score >= 65 else "Moderate" if score >= 40 else "Challenging"

    return {
        "score": score,
        "label": label,
        "notes": notes if notes else ["No specific climate concerns identified"],
    }
