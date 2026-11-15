# MaïsMap — AI and Generative Tool Disclosure
## NASA Space Apps Challenge 2026 | Team GeoWorks

---

## Tool Used

**Amazon Q Developer** (AWS AI coding assistant, IDE plugin)

---

## What Amazon Q Developer Was Used For

### Software Development
- Architecture design for the Python module structure
- Code generation for analysis modules (onset, false start, dry spell, heat stress,
  risk model, trends)
- Streamlit application layout and tab structure
- Folium map builder with popup templates
- Plotly chart functions
- Data pipeline for NASA POWER API fetching and caching
- SoilGrids API connector
- Crop rotation engine (strategy definitions, scoring functions)
- GeoJSON validator
- Test suite generation (46 tests)
- Bug identification and resolution (forward-reference bug, NameError, path issues)
- PPTX presentation generator script

### Documentation
- README drafting and revision
- Methodology documentation
- Data source documentation
- Limitations documentation
- NASA submission text drafting
- CHANGELOG

---

## What Amazon Q Developer Was NOT Used For

- Scientific validation of results against field data or observed crop yields
- Fabricating data, measurements, statistics, or farmer testimonials
- Generating NASA logos, mission identifiers, or official branding
- Producing the underlying agronomic knowledge — all thresholds, methods, and
  rotation assessments are cited from peer-reviewed literature and official sources
- Making decisions about the project concept, challenge selection, or team structure
- Accessing NASA APIs directly — all API calls were executed by the development
  environment with results verified by the team

---

## Verification Process

All AI-generated code was:
- Reviewed for correctness before use
- Tested against the 46-test automated suite
- Verified against actual API responses (NASA POWER confirmed live; SoilGrids
  confirmed returning null values for Northern Cameroon)
- Checked for scientific accuracy against cited literature

All AI-generated documentation was:
- Reviewed for factual accuracy
- Cross-checked against official NASA POWER documentation and agronomic sources
- Corrected where the AI produced inaccurate or unsupported claims

---

## Disclosure Statement

This project used Amazon Q Developer to accelerate software development and
documentation. The scientific methodology, data sources, and agronomic content
are based on published literature and real NASA data. The project concept,
challenge selection, and team decisions were made by Team GeoWorks. All
AI-assisted outputs were reviewed and verified before inclusion in the final
submission.
