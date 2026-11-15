# MaïsMap — Limitations and Uncertainty

## Data Limitations

1. **Synthetic demo data** — The current dataset is entirely synthetic. It was generated with plausible statistical properties but does not represent real historical conditions. All results displayed in demo mode are illustrative only.

2. **Spatial resolution** — NASA POWER operates at 0.5° (~55 km). This resolution cannot capture:
   - Local topographic effects
   - Microclimatic variation between villages
   - Field-level soil heterogeneity
   - Urban heat islands

3. **Reanalysis uncertainty** — NASA POWER PRECTOTCORR and T2M_MAX are derived from the MERRA-2 reanalysis model, not direct station measurements. Reanalysis products can differ significantly from local observations, particularly for precipitation in complex terrain.

4. **Missing station data** — Northern Cameroon has sparse meteorological station coverage. The reanalysis grid cannot be validated against dense local observations.

## Methodological Limitations

5. **Onset definition** — The Sivakumar (1988) method was developed for West African Sahelian conditions. Its applicability to the specific agroclimatic zones of Northern Cameroon has not been formally validated in this project.

6. **Risk model weights** — The weights (false start 40%, dry spell 35%, heat 25%) are provisional. They have not been calibrated against observed crop yield data or validated by agronomists familiar with this specific region.

7. **Heat stress threshold** — The 35°C Tmax threshold is a general guideline for maize pollen viability. Actual heat stress depends on humidity, duration, crop growth stage and variety.

8. **Season window** — The 120-day season window is an approximation. Actual maize growing periods vary by variety, sowing date and local conditions.

9. **False start definition** — The 10-day post-trigger dry spell threshold is a reasonable agronomic assumption but has not been validated against observed false-start events in this region.

## Application Limitations

10. **No forecast capability** — MaïsMap analyzes historical data only. It does not produce seasonal forecasts or climate projections.

11. **No field-level advice** — Recommendations are at the 0.5° grid scale. They cannot account for field-level variation in soil type, drainage or microclimate.

12. **No variety-specific guidance** — The analysis does not differentiate between maize varieties with different heat tolerance, drought tolerance or growing periods.

13. **Offline operation** — When NASA POWER is unavailable, the application falls back to cached or demo data. The data currency indicator shows the last update date.

## Uncertainty Communication

All risk scores and sowing recommendations in MaïsMap are accompanied by:
- Explicit data-source labels (demo vs. real)
- Spatial resolution disclaimers
- Cautious language ("conditions suggest", "confirm with local services")
- Visible warnings about the prototype nature of the tool

**MaïsMap is a decision-support prototype. It does not replace local agricultural extension services, seasonal forecasts from national meteorological agencies, or professional agronomic advice.**
