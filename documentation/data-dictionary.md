# Data Dictionary
## Suffolk County Livability Dashboard

**Last Updated**: December 2025
**Dataset Version**: 1.0  
**Final Dataset**: `suffolk_livability_summary.csv` (34 ZIP codes × 45+ variables)

<br>

## Overview

This data dictionary describes all variables in the Suffolk County Livability Dashboard. Data comes from 6 authoritative sources, processed through 9 Python scripts, resulting in a comprehensive livability assessment for 34 Suffolk County ZIP codes.

<br>

## Geographic Identifiers

| Field Name | Type | Description | Example | Source |
|------------|------|-------------|---------|--------|
| `zip_code` | String | 5-digit ZIP code | "02134" | Census ZCTA |
| `area_sq_mi` | Float | Land area in square miles | 1.26 | Census TIGER (calculated) |

<br>

## Crime/Safety Variables (22.5% weight)

| Field Name | Type | Range | Description | Calculation |
|------------|------|-------|-------------|-------------|
| `total_crimes` | Integer | 0-5000 | Total reported incidents (2021-2024) | Boston PD data |
| `violent_crimes` | Integer | 0-500 | Violent crime count | Keyword classification |
| `property_crimes` | Integer | 0-4500 | Property crime count | Keyword classification |
| `crimes_per_sq_mi` | Float | 0-3000 | **Crimes per square mile** (NOT per capita) | total_crimes / area_sq_mi |
| `violent_per_sq_mi` | Float | 0-300 | Violent crimes per square mile | violent_crimes / area_sq_mi |
| `property_per_sq_mi` | Float | 0-2500 | Property crimes per square mile | property_crimes / area_sq_mi |
| `crime_score` | Float | 0-10 | Total crime density score (inverted) | Normalized, inverted |
| `violent_score` | Float | 0-10 | Violent crime density score (inverted) | Normalized, inverted |
| `property_score` | Float | 0-10 | Property crime density score (inverted) | Normalized, inverted |
| `overall_crime_score` | Float | 0-10 | **Weighted composite** | (crime × 0.40) + (violent × 0.35) + (property × 0.25) |


**Crime Classification Keywords**:
- **Violent**: ASSAULT, HOMICIDE, MURDER, ROBBERY, RAPE, SEX OFFENSE, KIDNAPPING, SHOOTING, STABBING, THREATS
- **Property**: LARCENY, BURGLARY, THEFT, STOLEN, BREAKING & ENTERING, AUTO THEFT, VANDALISM, ARSON, SHOPLIFTING, TRESPASSING

**Important**: Scores are **area-based**, not per capita. Lower crime density → higher score.

<br>

## School Quality Variables (15.0% weight)

| Field Name | Type | Range | Description | Source |
|------------|------|-------|-------------|--------|
| `school_grade` | String | A+ to F | Niche letter grade for public schools | Niche.com (manual) |
| `school_score` | Float | 0-10 | Numeric conversion of grade | Calculated |

**Grade Conversion Scale**:
```
A+ = 10.0    B+ = 7.5     C+ = 5.0     D+ = 2.5
A  = 9.0     B  = 6.5     C  = 4.0     D  = 1.5
A- = 8.5     B- = 6.0     C- = 3.5     D- = 1.0
                                        F  = 0.5
```

<br>

## Transit Accessibility Variables (15.0% weight)

| Field Name | Type | Range | Description | Source |
|------------|------|-------|-------------|--------|
| `total_stops` | Integer | 0-50 | MBTA stations/stops in ZIP | MBTA GTFS |
| `stops_per_sq_mi` | Float | 0-25 | Transit density | total_stops / area_sq_mi |
| `transit_score` | Float | 0-10 | Stop count score | Normalized |
| `transit_density_score` | Float | 0-10 | Density score | Normalized |
| `overall_transit_score` | Float | 0-10 | **Weighted composite** | (transit × 0.6) + (density × 0.4) |

<br>

## Housing Affordability Variables (10.0% weight)

| Field Name | Type | Range | Description | Source |
|------------|------|-------|-------------|--------|
| `median_home_value` | Integer | 200K-1.5M | Median home sale price (USD) | Census ACS |
| `median_rent` | Integer | 800-3500 | Median monthly rent (USD) | Census ACS |
| `median_household_income` | Integer | 30K-150K | Median household income (USD) | Census ACS |
| `price_to_income_ratio` | Float | 3-15 | Home price / income | Calculated |
| `rent_to_income_ratio` | Float | 0.2-0.6 | Annual rent / income | Calculated |
| `home_value_score` | Float | 0-10 | Home affordability (inverted) | Normalized, inverted |
| `rent_score` | Float | 0-10 | Rent affordability (inverted) | Normalized, inverted |
| `price_income_score` | Float | 0-10 | Price-to-income score (inverted) | Normalized, inverted |
| `overall_housing_score` | Float | 0-10 | **Weighted composite** | (home × 0.40) + (rent × 0.35) + (price_income × 0.25) |

**Important**: Lower cost → higher score (inverted scoring). Affordability relative to Suffolk County only.

<br>

## Lifestyle Variables (17.0% weight)

| Field Name | Type | Range | Description | Source |
|------------|------|-------|-------------|--------|
| `nightlife` | String | A+ to F | Niche nightlife grade | Niche.com (manual) |
| `health` | String | A+ to F | Niche health & fitness grade | Niche.com (manual) |
| `outdoor` | String | A+ to F | Niche outdoor activities grade | Niche.com (manual) |
| `nightlife_score` | Float | 0-10 | Numeric conversion | Calculated |
| `health_score` | Float | 0-10 | Numeric conversion | Calculated |
| `outdoor_score` | Float | 0-10 | Numeric conversion | Calculated |
| `overall_lifestyle_score` | Float | 0-10 | **Average of 3 components** | (nightlife + health + outdoor) / 3 |

**Uses same grade conversion scale as schools.**

<br>

## Healthcare Access Variables (13.0% weight)

| Field Name | Type | Range | Description | Source |
|------------|------|-------|-------------|--------|
| `nearest_hospital` | String | Text | Name of closest hospital | Manual hospital list |
| `nearest_hospital_dist` | Float | 0-5 | Miles to nearest hospital | Calculated (geodesic) |
| `nearest_tier1_dist` | Float | 0-5 | Miles to nearest Tier 1 hospital | Calculated |
| `hospitals_within_2mi` | Integer | 0-10 | Hospitals within 2-mile radius | Counted |
| `hospitals_within_3mi` | Integer | 0-12 | Hospitals within 3-mile radius | Counted |
| `hospitals_within_5mi` | Integer | 0-15 | Hospitals within 5-mile radius | Counted |
| `tier1_within_5mi` | Integer | 0-8 | Tier 1 hospitals within 5mi | Counted |
| `nearest_hospital_score` | Float | 0-10 | Distance score (inverted) | Normalized, inverted |
| `nearest_tier1_score` | Float | 0-10 | Tier 1 distance score (inverted) | Normalized, inverted |
| `density_score` | Float | 0-10 | Hospital density score | Normalized |
| `tier1_access_score` | Float | 0-10 | Tier 1 access score | Normalized |
| `overall_healthcare_score` | Float | 0-10 | **Weighted composite** | (tier1 × 0.40) + (nearest × 0.25) + (density × 0.20) + (tier1_access × 0.15) |

**Hospital Tiers**:
- **Tier 1**: Major teaching hospitals (Mass General, Brigham & Women's, etc.)
- **Tier 2**: Community hospitals
- **Tier 3**: Specialty/rehabilitation facilities

<br>

## Diversity Variables (7.5% weight)

| Field Name | Type | Range | Description | Source |
|------------|------|-------|-------------|--------|
| `total_pop` | Integer | 500-50K | Total resident population | Census ACS |
| `white` | Integer | 100-30K | White population count | Census ACS |
| `black` | Integer | 0-25K | Black/African American count | Census ACS |
| `asian` | Integer | 0-10K | Asian population count | Census ACS |
| `other` | Integer | 0-5K | Other races count | Census ACS |
| `two_or_more` | Integer | 0-2K | Two or more races count | Census ACS |
| `pct_white` | Float | 0-100 | Percent White | (white / total_pop) × 100 |
| `pct_black` | Float | 0-100 | Percent Black | (black / total_pop) × 100 |
| `pct_asian` | Float | 0-100 | Percent Asian | (asian / total_pop) × 100 |
| `pct_other` | Float | 0-100 | Percent Other | (other / total_pop) × 100 |
| `pct_two_or_more` | Float | 0-100 | Percent Two or More | (two_or_more / total_pop) × 100 |
| `diversity_index` | Float | 0-1.61 | Shannon Diversity Index | H = -Σ(pi × ln(pi)) |
| `diversity_score` | Float | 0-10 | Normalized diversity | (H / ln(5)) × 10 |

**Shannon Index Interpretation**:
- **Higher H** = more diverse (even distribution across groups)
- **Lower H** = less diverse (concentration in one group)
- **Maximum** = ln(5) = 1.609 (perfectly equal distribution)

<br>

## Composite Score Variables

| Field Name | Type | Range | Description | Calculation |
|------------|------|-------|-------------|-------------|
| `composite_score` | Float | 0-10 | **Overall livability score** | Weighted sum of 7 variables |
| `tier` | String | 5 categories | Classification label | Threshold-based |

**Composite Score Formula**:
```python
composite_score = (crime_score × 0.225) + 
                  (lifestyle_score × 0.170) + 
                  (school_score × 0.150) + 
                  (transit_score × 0.150) + 
                  (healthcare_score × 0.130) +
                  (housing_score × 0.100) + 
                  (diversity_score × 0.075)
```

**Tier Classifications**:
- **Excellent**: 8.0 ≤ score ≤ 10.0
- **Good**: 7.0 ≤ score < 8.0
- **Average**: 6.0 ≤ score < 7.0
- **Below Average**: 5.0 ≤ score < 6.0
- **Poor**: 0.0 ≤ score < 5.0

<br>

---
---

## Data Quality & Processing

### Missing Data Handling
- **Special ZIP codes**: Non-residential ZIPs (02133 - PO Box only) have limited data
- **Census N/A codes**: -66666666, -99999999, -88888888 replaced with estimates or null
- **Imputation**: Missing housing data filled with neighborhood-based estimates
- **Weighted adjustments**: Composite scores auto-adjust when variables missing

### Data Validation
All scores validated for:
- Range: 0 ≤ score ≤ 10
- No negative values
- Weights sum to 100%
- Composite matches weighted formula

<br>

---
---

## File Formats

### Primary Dataset

**Filename**: `suffolk_livability_summary.csv`  
**Format**: CSV (UTF-8 encoding)  
**Rows**: 34 (one per ZIP code)  
**Columns**: 45+  
**Size**: ~75 KB

### Geographic Data

**Filename**: `suffolk_zipcodes.geojson`  
**Format**: GeoJSON  
**Coordinate System**: WGS84 (EPSG:4326)  
**Features**: 34 polygons

<br>

---
---

## Usage Notes

1. **Normalization Scope**: All scores normalized **within Suffolk County only**. Not comparable to national data.

2. **Temporal Consistency**: 
   - Crime: 2021-2024 (3 years)
   - Census: 2018-2023 (ACS 5-year)
   - Schools/Lifestyle: 2023-2024 academic year
   - Transit/Healthcare: Current as of late 2024

3. **Aggregation Level**: ZIP code level masks within-ZIP variation

4. **Rounding**: Display values rounded to 2 decimals; full precision retained in calculations

5. **Area-Based Crime**: Crime calculated per square mile, NOT per capita

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 2025 | Initial release - 7 variables, 34 ZIP codes |