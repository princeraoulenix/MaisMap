import json
for yr in [2020,2021,2022,2023]:
    d=json.load(open(f'data/processed/grid_{yr}.geojson'))
    props=[f['properties'] for f in d['features']]
    fs=sum(1 for p in props if p.get('false_start'))
    rc={c: sum(1 for p in props if p.get('risk_class')==c) for c in ['LOW','MEDIUM','HIGH']}
    onsets=[p['season_onset_date'] for p in props if p.get('season_onset_date')]
    rain=[p['seasonal_rain_mm'] for p in props if p.get('seasonal_rain_mm')]
    heat=[p['heat_days'] for p in props if p.get('heat_days') is not None]
    dry=[p['dry_spell_days'] for p in props if p.get('dry_spell_days') is not None]
    om=round(sum(onsets)/len(onsets)) if onsets else None
    rm=round(sum(rain)/len(rain)) if rain else None
    hm=round(sum(heat)/len(heat),1) if heat else None
    dm=round(sum(dry)/len(dry),1) if dry else None
    print(yr, 'n='+str(len(props)), 'fs='+str(fs), str(rc), 'onset='+str(om), 'rain='+str(rm), 'heat='+str(hm), 'dry='+str(dm))
