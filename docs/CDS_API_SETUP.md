# CDS API Setup

The Copernicus CDS migrated to a new platform in Sept 2024. Old keys do not work.

1. Register at https://cds.climate.copernicus.eu/
2. Open the ERA5 single-levels dataset page, scroll to the Download tab,
   and accept the licence (otherwise every request returns HTTP 403).
3. Copy your Personal Access Token from https://cds.climate.copernicus.eu/profile
   (a ~40-char string, NO colon — not the old UID:KEY format).
4. Create `~/.cdsapirc` with exactly two lines:

   url: https://cds.climate.copernicus.eu/api
   key: <your-token>

5. `pip install --upgrade 'cdsapi>=0.7.7'`
6. Verify: `python scripts/01_test_cds_setup.py`

| Symptom | Fix |
|---|---|
| 403 Forbidden | Accept ERA5 licence (step 2) |
| Authentication failed | Old UID:KEY in .cdsapirc → use PAT |
| "request too large" | Already handled: 02 downloads in monthly chunks |
