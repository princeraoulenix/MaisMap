"""
GeoJSON validation for MaïsMap data contract.

Validates required fields, geometry, coordinate order, value ranges,
duplicates and data provenance. Never silently replaces missing data.
"""

REQUIRED_FIELDS = {
    "cell_id", "region", "year", "risk_class", "risk_score",
    "false_start", "dry_spell_days", "heat_days", "season_onset_date",
    "data_source",
}
VALID_RISK_CLASSES = {"LOW", "MEDIUM", "HIGH"}
VALID_REGIONS = {"Nord", "Extrême-Nord", "Adamaoua"}

# Northern Cameroon bounding box
LON_MIN, LON_MAX = 12.0, 17.0
LAT_MIN, LAT_MAX = 6.0, 13.5


def validate_geojson(geojson: dict) -> dict:
    """
    Validate a GeoJSON FeatureCollection against the MaïsMap data contract.

    Returns a report dict with:
      valid, invalid, missing_fields, duplicate_ids,
      out_of_range, unsupported_values, synthetic_count, real_count, issues
    """
    features = geojson.get("features", [])
    report = {
        "total": len(features),
        "valid": 0,
        "invalid": 0,
        "missing_fields": [],
        "duplicate_ids": [],
        "out_of_range": [],
        "unsupported_values": [],
        "synthetic_count": 0,
        "real_count": 0,
        "issues": [],
    }

    seen_ids = {}
    for i, feature in enumerate(features):
        props = feature.get("properties", {})
        geom  = feature.get("geometry", {})
        cell_issues = []

        # Required fields
        missing = REQUIRED_FIELDS - set(props.keys())
        if missing:
            cell_issues.append(f"Missing fields: {sorted(missing)}")
            report["missing_fields"].extend(sorted(missing))

        # Duplicate cell_id within same year
        key = (props.get("cell_id"), props.get("year"))
        if key in seen_ids:
            cell_issues.append(f"Duplicate cell_id {key}")
            report["duplicate_ids"].append(key)
        else:
            seen_ids[key] = i

        # Risk class
        rc = props.get("risk_class")
        if rc and rc not in VALID_RISK_CLASSES:
            cell_issues.append(f"Invalid risk_class: {rc!r}")
            report["unsupported_values"].append(f"risk_class={rc!r}")

        # Risk score range
        rs = props.get("risk_score")
        if rs is not None and not (0 <= rs <= 100):
            cell_issues.append(f"risk_score out of range: {rs}")
            report["out_of_range"].append(f"risk_score={rs}")

        # Geometry coordinate order [lon, lat]
        if geom.get("type") == "Polygon":
            coords = geom.get("coordinates", [[]])[0]
            for lon, lat in coords:
                if not (LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX):
                    cell_issues.append(
                        f"Coordinates outside study area: [{lon},{lat}]"
                    )
                    report["out_of_range"].append(f"coord=[{lon},{lat}]")
                    break

        # Data provenance
        src = str(props.get("data_source", "")).upper()
        if "SYNTHETIC" in src or "DEMO" in src or props.get("confidence") == "demo":
            report["synthetic_count"] += 1
        else:
            report["real_count"] += 1

        if cell_issues:
            report["invalid"] += 1
            report["issues"].append({"feature_index": i, "cell_id": props.get("cell_id"), "issues": cell_issues})
        else:
            report["valid"] += 1

    # Deduplicate lists for readability
    report["missing_fields"] = sorted(set(report["missing_fields"]))
    report["duplicate_ids"] = list(set(str(d) for d in report["duplicate_ids"]))

    return report
