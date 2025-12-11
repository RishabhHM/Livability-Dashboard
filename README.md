# Suffolk County Livability Dashboard

A comprehensive data visualization dashboard analyzing livability metrics across 34 Suffolk County (Boston area) ZIP codes, providing composite scores based on seven weighted variables:
- Crime
- Lifestyle
- Housing
- Schools
- Transit
- Healthcare
- Diversity

**Live Dashboard**: [View on Tableau Public](https://public.tableau.com/views/LivabilityDashboard/SuffolkCountyLivabilitybyZIPCode)
<br>

---
---

## 📋 Project Overview

This interactive dashboard helps users evaluate and compare Suffolk County neighborhoods by analyzing seven key variables that contribute to overall livability. The project uses publicly available data sources and employs a weighted scoring methodology to create an objective, data-driven assessment of each zip code.

**Region**: Suffolk County, Massachusetts (Boston and surrounding areas)  
**Scope**: 34 residential zip codes  
**Dashboard Tool**: Tableau Public/Desktop  
**Data Processing**: Python 3.8+  
**Last Updated**: December 10, 2025

<br>

---
---

## 🎯 Key Features

### Interactive Visualizations
- **Choropleth Map**: Color-coded ZIP codes with viz-in-tooltip showing detailed breakdown
- **Top 5 Rankings**: Dynamic rankings with variable selector parameter
- **Hover Details**: Complete 7-variable score breakdown appears on map hover
- **Interactive Filtering**: Rank by any metric (Crime, Schools, Transit, Housing, etc.)

### Composite Scoring System
Weighted composite score (0-10 scale) calculated from:

| Variable | Weight | Metric Type |
|----------|--------|-------------|
| Crime/Safety | 22.5% | Crimes per square mile (area-based) |
| Lifestyle | 17.0% | Composite of nightlife, outdoor, fitness |
| School Quality | 15.0% | Niche.com letter grades |
| Transit Access | 15.0% | MBTA stops per ZIP |
| Healthcare | 13.0% | Distance + density of hospitals |
| Housing Affordability | 10.0% | Median home value + rent (inverted) |
| Diversity | 7.5% | Shannon Diversity Index (racial/ethnic) |
| Total | 100%

<br>

---
---

## 📊 Metrics & Methodology

### 1. Crime/Safety Score (22.5% weight)

**Data Source**: Boston Police Department Crime Incident Reports (2023-Present)

**Methodology**:
- Calculated as **crimes per square mile** (area-based density)
- Classified crimes into three categories:
  - Violent crimes (assault, robbery, homicide, etc.)
  - Property crimes (larceny, burglary, theft, vandalism, etc.)
  - Other crimes
- Normalized 0-10 scale (inverted: lower crime = higher score)

**Citation**:
```
Boston Police Department. (2024). Crime Incident Reports. 
    Retrieved from https://data.boston.gov/dataset/crime-incident-reports
```

---


### 2. Lifestyle Score (17.0% weight)

**Data Source**: Niche.com Places to Live Rankings

**Methodology**:
- Composite of three Niche grades: Nightlife + Health & Fitness + Outdoor Activities
- Converted letter grades (A+ to F) to numeric (10.0 to 0.5)
- Average of three components

**Grade Conversion Scale**:
```python
'A+': 10.0, 'A': 9.0, 'A-': 8.5
'B+': 7.5, 'B': 6.5, 'B-': 6.0
'C+': 5.0, 'C': 4.0, 'C-': 3.5
'D+': 2.5, 'D': 1.5, 'D-': 1.0
'F': 0.5
```

**Citation**:
```
Niche.com. - Places To Live. 
    Retrieved from https://www.niche.com/places-to-live/
```

---

### 3. School Quality Score (15.0% weight)

**Data Source**: Niche.com Places to Live Rankings

**Methodology**:
- Letter grades for public schools in each ZIP
- Converted using same scale as lifestyle
- Averaged across schools in ZIP (by Niche)

**Citation**:
```
Niche.com. - Places To Live. 
    Retrieved from https://www.niche.com/places-to-live/
```

---

### 4. Transit Accessibility Score (15.0% weight)

**Data Source**: MBTA GTFS (General Transit Feed Specification)

**Methodology**:
- Counted MBTA stations (subway, light rail, commuter rail) per ZIP
- Calculated stops per square mile
- Normalized 0-10 scale

**Formula**:
```python
overall_transit_score = (transit_score × 0.6) + 
                        (transit_density_score × 0.4)
```

**Citation**: 
```
Massachusetts Bay Transportation Authority. (2024). GTFS Static Feed. Retrieved from https://www.mbta.com/developers/gtfs
```

---

### 5. Healthcare Access Score (13.0% weight)

**Data Source**: Suffolk County Hospitals (manually compiled from CMS data)

**Methodology**:
- Calculated distance to nearest hospital (by tier)
- Counted hospitals within 2mi, 3mi, 5mi radius
- Tier 1 = Major Teaching, Tier 2 = Community, Tier 3 = Specialty

**Formula**:
```python
overall_healthcare_score = (nearest_tier1_score × 0.40) + 
                           (nearest_hospital_score × 0.25) + 
                           (density_score × 0.20) + 
                           (tier1_access_score × 0.15)
```

**Citations**:
```
- Centers for Medicare & Medicaid Services. (2024). Hospital General Information. Retrieved from https://data.cms.gov/
```

---

### 6. Housing Affordability Score (10.0% weight)

**Data Source**: U.S. Census Bureau American Community Survey (ACS) 5-Year Estimates

**Methodology**:
- Median home value and median gross rent
- Normalized 0-10 (inverted: lower cost = higher score)

**Formula**:
```python
overall_housing_score = (home_value_score × 0.40) + 
                        (rent_score × 0.35) + 
                        (price_to_income_score × 0.25)
```

**Citation**:
```
U.S. Census Bureau. (2023). American Community Survey 5-Year Estimates, 
    Tables B25077 (Median Home Value) and B25064 (Median Gross Rent). 
    Retrieved from https://data.census.gov/
```

---

### 7. Diversity Score (7.5% weight)

**Data Source**: U.S. Census Bureau ACS

**Methodology**:
- Shannon Diversity Index for racial/ethnic composition
- 5 categories: White, Black, Asian, Other, Two or More Races
- Formula: H = -Σ(pi × ln(pi))
- Normalized to 0-10 scale (max H = ln(5) = 1.609)

**Citations**:
```
U.S. Census Bureau. (2023). American Community Survey 5-Year Estimates, Table B02001 (Race). Retrieved from https://data.census.gov/
```

---

### Composite Score Calculation

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
- **Excellent**: 8.0 - 10.0
- **Good**: 7.0 - 7.9
- **Average**: 6.0 - 6.9
- **Below Average**: 5.0 - 5.9
- **Poor**: 0.0 - 4.9

**Important**: All scores normalized **within Suffolk County only**. A score of 10 = best in county, not absolute national excellence.

<br>

---
---

## 💡 Weighting Rationale

### Why These Weights?

**Crime (22.5%)** - Highest weight
- Safety is fundamental to all aspects of daily life
- Universal concern regardless of demographics
- Affects property values, walkability, peace of mind
- Research: Maslow's hierarchy places safety as basic need

**Lifestyle (17.0%)** - Second highest
- Daily quality of life compounds over time
- Mental health directly tied to neighborhood amenities
- Modern urban residents prioritize lifestyle highly
- Research: "Third places" critical for wellbeing (Oldenburg, 1989)

**School Quality (15.0%)** & **Transit Access (15.0%)** - Tied importance
- Schools: Critical for ~60% of households with children
- Transit: Essential for sustainable urban living
- Both affect economic mobility and accessibility
- Users can filter by either when personally prioritizing

**Healthcare (13.0%)** - Essential service
- Basic need, particularly for families and elderly
- Emergency response time can be life-or-death
- Note: Suffolk County has uniformly strong access (limited variation)

**Housing (10.0%)** - Lower than expected because:
- Affordability is income-relative (not captured in data)
- Urban residents demonstrate willingness to pay premiums for location
- Users seeking maximum affordability can filter by housing score specifically
- Trade-off people consciously make for desirable neighborhoods

**Diversity (7.5%)** - Lowest weight
- Highly subjective individual preference
- Enriches community but less directly impacts daily logistics
- Cultural value varies significantly by person
- Important but not logistically determinant

### Alternative Weighting Scenarios

Users with different priorities might prefer:
- **Families**: Crime 25%, Schools 25%, Housing 20%, Transit 15%, Others 15%
- **Young Professionals**: Lifestyle 25%, Transit 20%, Crime 20%, Housing 15%, Others 20%
- **Retirees**: Crime 30%, Healthcare 20%, Lifestyle 20%, Housing 15%, Others 15%

<br>

---
---

## 🗂️ Project Structure

```
Livability-Dashboard/
│
├── README.md                     # This file
├── LICENSE                       # MIT License
├── requirements.txt              # Python dependencies
│
├── scripts/                      # Data collection & processing
│   ├── setup_project.py
│   ├── step1_get_zipcode_boundaries.py
│   ├── step2_collect_crime_data.py
│   ├── step3_collect_school_data.py
│   ├── step4_collect_transit_data.py
│   ├── step5_collect_housing_data.py
│   ├── step6_collect_diversity_data.py
│   ├── step7_collect_healthcare_data.py
│   ├── step8_process_lifestyle_data.py
│   └── step9_merge_all_data.py
│
├── data/                         # All data files
│   ├── suffolk_county_zip.csv   # ZIP list
│   ├── suffolk_zipcodes.geojson # Geographic boundaries
│   ├── suffolk_zipcodes_info.csv
│   ├── niche_data.csv            # Manually collected Niche grades
│   │
│   ├── raw_zcta/                 # Census ZCTA shapefiles
│   ├── crime/                    # Crime data & scores
│   ├── schools/                  # School scores
│   ├── transit/                  # Transit data (GTFS)
│   ├── housing/                  # Housing scores
│   ├── diversity/                # Diversity scores
│   ├── healthcare/               # Healthcare scores
│   └── lifestyle/                # Lifestyle scores
│
├── outputs/                      # Final outputs
│   └── tableau_data/
│       ├── suffolk_livability_summary.csv
│       ├── suffolk_scores_only.csv
│       └── DATA_DICTIONARY.txt
│
├── assets/                       # Images, screenshots
│
└── documentation/                # Additional docs
    ├── Project_Summary.pdf
    └── Data_Dictionary.md

```

<br>

---
---

## 📊 Key Findings

### Score Distribution
- **Range**: 5.363 to 8.257
- **Mean**: ~7.0
- **Most common tier**: Good (7.0-7.9)
- **Distribution**: Slightly left-skewed (most ZIPs score well)

### Top 5 ZIP Codes
Based on composite livability scores:
1. **02215** - Urban core with strong lifestyle
2. **02115** - Healthcare hub
3. **02135** - Balanced across metrics
4. **02130** - Diverse, family-friendly
5. **02134** - Student-oriented, affordable lifestyle

### Notable Patterns
- **Safety**: Suburban fringe areas score highest (lower crime density)
- **Lifestyle**: Urban core dominates
- **Transit**: Strong correlation with proximity to Red/Orange/Green Lines
- **Housing**: Clear trade-off between location and affordability
- **Healthcare**: Uniformly excellent (Boston's hospital concentration)
- **Diversity**: Dorchester, Roxbury, Allston lead

<br>

---
---

## 📝 Limitations

### Data Limitations
1. **Temporal snapshot**: 2023-2024 data; neighborhoods evolve
2. **ZIP aggregation**: Variation within large ZIPs not captured
3. **ZCTA vs. USPS**: Census boundaries may not match postal codes exactly
4. **Special ZIPs excluded**: PO Box-only and unique-entity ZIPs not analyzed

### Methodological Limitations
5. **Weighting subjectivity**: Reflects general priorities, not individual preferences
6. **Relative scoring**: Normalized within Suffolk County only—not comparable to other regions
7. **Area-based crime**: May slightly penalize dense urban cores with high foot traffic
8. **Missing nuance**: Quantitative scores cannot capture neighborhood character, community feel

### Variable-Specific Limitations
9. **Crime**: Based on reported crimes only; reporting rates vary
10. **Schools**: Niche's proprietary methodology; doesn't capture all quality aspects
11. **Transit**: Counts stations but not service frequency or reliability
12. **Housing**: Based on medians; individual affordability varies widely
13. **Lifestyle**: Subjective Niche ratings may not match personal preferences
14. **Healthcare**: Measures access, not quality of care
15. **Diversity**: Shannon Index measures distribution, not integration or inclusivity

<br>

---
---

## 👤 Author

**Rishabh Madani**  
**Additional Links**:
- Tableau Public: [Live Dashboard](https://public.tableau.com/views/LivabilityDashboard/SuffolkCountyLivabilitybyZIPCode)

<br>

---
---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

**Data Licenses**:
- Census data: Public domain (U.S. Government)
- Crime data: Open Data Commons (City of Boston)
- MBTA data: Public domain (MassDOT)
- Niche data: Used in accordance with fair use for educational purposes

---

**Last Updated**: December 10, 2025 <br>
**Dashboard Version**: 1.0