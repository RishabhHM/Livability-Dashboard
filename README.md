# Boston Regional Livability Dashboard

A comprehensive data visualization dashboard analyzing livability metrics across Boston zip codes, providing composite scores based on crime, education, transit, housing, lifestyle, and diversity factors.

---

## 📋 Project Overview

This dashboard helps users evaluate and compare Boston neighborhoods by analyzing seven key variables that contribute to overall livability. The project uses publicly available data sources and employs a weighted scoring methodology to create an objective, data-driven assessment of each zip code.

**Region**: Boston, Massachusetts (Suffolk County)  
**Scope**: ~34 residential zip codes  
**Dashboard Tool**: Tableau Public  
**Data Processing**: Python 3.8+

---

## 🎯 Key Features

### Interactive Visualizations
- **Choropleth Map**: Color-coded zip codes based on composite livability scores
- **Variable Selector**: Dynamic rankings by any individual metric (Crime, Schools, Transit, etc.)
- **Score Cards**: Detailed breakdown showing all seven variables for selected zip codes
- **Grouped Bar Chart**: Side-by-side comparison of all variables across zip codes
- **Top 10 Rankings**: Best-performing zip codes with customizable ranking criteria

### Composite Scoring System
The dashboard calculates a weighted composite score (0-10 scale) based on:
- **Crime/Safety** (25%)
- **School Quality** (20%)
- **Housing Affordability** (20%)
- **Transit Accessibility** (15%)
- **Lifestyle** (10%)
- **Diversity** (10%)

---

## 📊 Variables & Methodology

### 1. Crime/Safety Score (25% weight)
**Data Source**: Boston Police Department Crime Incident Reports  
**Methodology**: 
- Calculated crimes per capita (per 1,000 residents)
- Lower crime rate = higher score
- Normalized to 0-10 scale, then inverted

**Citation**:
```
Boston Police Department. (2024). Crime Incident Reports. 
    Retrieved from https://data.boston.gov/dataset/crime-incident-reports
```

### 2. School Quality Score (20% weight)
**Data Source**: Niche.com School Rankings  
**Methodology**:
- Collected letter grades (A+ through F) for public schools in each zip code
- Converted to numeric scores using standardized scale
- Averaged across all schools in zip code

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
Niche.com. (2024). K-12 Schools Rankings. 
    Retrieved from https://www.niche.com/k12/search/best-schools/
```

### 3. Housing Affordability Score (20% weight)
**Data Source**: U.S. Census Bureau American Community Survey (ACS)  
**Methodology**:
- Used median home values and median gross rent
- Lower cost = higher score (inverted normalization)
- Combined home value (60%) and rent (40%)

**Citation**:
```
U.S. Census Bureau. (2023). American Community Survey 5-Year Estimates, 
    Tables B25077 (Median Home Value) and B25064 (Median Gross Rent). 
    Retrieved from https://data.census.gov/
```

### 4. Transit Accessibility Score (15% weight)
**Data Source**: MBTA GTFS Data  
**Methodology**:
- Counted MBTA stations (subway, commuter rail) within each zip code
- Counted major bus routes serving the zip code
- Normalized to 0-10 scale based on total transit options

**Citation**:
```
Massachusetts Bay Transportation Authority. (2024). GTFS Static Feed. 
    Retrieved from https://www.mbta.com/developers/gtfs
```

### 5. Lifestyle Score (10% weight)
**Data Source**: Niche.com Neighborhood Rankings  
**Methodology**:
- Composite of three sub-metrics from Niche:
  - Nightlife (A+ through F grades)
  - Outdoor Activities (A+ through F grades)
  - Health & Fitness (A+ through F grades)
- Each converted to numeric using grade scale
- Final score = average of three components

**Citation**:
```
Niche.com. (2024). Places to Live: Boston Zip Code Rankings. 
    Retrieved from https://www.niche.com/places-to-live/
```

### 6. Diversity Score (10% weight)
**Data Source**: U.S. Census Bureau ACS  
**Methodology**:
- Calculated Shannon Diversity Index across three dimensions:
  - **Racial/Ethnic Diversity**: 7 categories (White, Black, Asian, Hispanic, etc.)
  - **Educational Diversity**: 5 levels (Less than HS through Graduate degree)
  - **Age Diversity**: 5 age groups (0-17, 18-34, 35-54, 55-74, 75+)
- Shannon Index formula: H = -Σ(pi × ln(pi))
- Final score = average of three indices, normalized to 0-10 scale

**Citations**:
```
U.S. Census Bureau. (2023). American Community Survey 5-Year Estimates, 
    Table B02001 (Race). Retrieved from https://data.census.gov/

U.S. Census Bureau. (2023). American Community Survey 5-Year Estimates, 
    Table B15003 (Educational Attainment). Retrieved from https://data.census.gov/

U.S. Census Bureau. (2023). American Community Survey 5-Year Estimates, 
    Table B01001 (Sex by Age). Retrieved from https://data.census.gov/
```

### Composite Score Calculation
```python
composite_score = (crime_score × 0.25) + 
                  (school_score × 0.20) + 
                  (housing_score × 0.20) + 
                  (transit_score × 0.15) + 
                  (lifestyle_score × 0.10) + 
                  (diversity_score × 0.10)
```

**Score Tiers**:
- **Excellent**: 8.0 - 10.0 (Dark Green)
- **Good**: 7.0 - 7.9 (Light Green)
- **Average**: 6.0 - 6.9 (Yellow)
- **Below Average**: 5.0 - 5.9 (Orange)
- **Poor**: 0.0 - 4.9 (Red)

---

## 🗂️ Project Structure

```
boston-livability-dashboard/
│
├── data/
│   ├── raw/                          # Raw data files
│   │   ├── crime_data.csv
│   │   ├── school_ratings.csv
│   │   ├── census_housing.csv
│   │   ├── mbta_stations.csv
│   │   ├── lifestyle_niche.csv
│   │   └── census_diversity.csv
│   │
│   ├── processed/                    # Cleaned and normalized data
│   │   └── boston_livability_final.csv
│   │
│   └── geospatial/                   # Shapefiles
│       └── boston_zipcodes.shp
│
├── scripts/                          # Python data collection scripts
│   ├── step1_collect_boundaries.py
│   ├── step2_collect_crime_data.py
│   ├── step3_collect_school_data.py
│   ├── step4_collect_transit_data.py
│   ├── step5_collect_housing_data.py
│   ├── step6_collect_lifestyle_data.py
│   ├── step7_collect_diversity_data.py
│   ├── step8_calculate_scores.py
│   └── step9_export_for_tableau.py
│
├── tableau/
│   └── boston_dashboard.twbx        # Tableau workbook
│
├── documentation/
│   ├── methodology.pdf               # Detailed methodology explanation
│   └── data_dictionary.md            # Variable definitions
│
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
└── LICENSE
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Tableau Desktop or Tableau Public (latest version)
- Git (for cloning repository)

### Python Dependencies
```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
pandas>=1.3.0
geopandas>=0.10.0
requests>=2.26.0
beautifulsoup4>=4.9.3
census>=0.8.17
shapely>=1.8.0
jupyter>=1.0.0
```

### Data Collection
Run the Python scripts in order:
```bash
# Step 1: Get zip code boundaries
python scripts/step1_collect_boundaries.py

# Step 2: Collect crime data
python scripts/step2_collect_crime_data.py

# Step 3: Collect school data
python scripts/step3_collect_school_data.py

# Step 4: Collect transit data
python scripts/step4_collect_transit_data.py

# Step 5: Collect housing data
python scripts/step5_collect_housing_data.py

# Step 6: Collect lifestyle data (from Niche)
python scripts/step6_collect_lifestyle_data.py

# Step 7: Collect diversity data
python scripts/step7_collect_diversity_data.py

# Step 8: Calculate all scores
python scripts/step8_calculate_scores.py

# Step 9: Export final dataset
python scripts/step9_export_for_tableau.py
```

### Tableau Dashboard Setup
1. Open Tableau Desktop/Public
2. Connect to data source: `data/processed/boston_livability_final.csv`
3. Import the workbook: `tableau/boston_dashboard.twbx`
4. Refresh data connections if needed

---

## 📈 Dashboard Components

### 1. **Main Map View**
- Choropleth visualization of composite scores
- Color gradient from red (poor) to green (excellent)
- Click on zip code to filter other visualizations

### 2. **Variable Selector Ranking**
- Interactive parameter control
- Select which metric to rank by (Composite, Crime, Schools, etc.)
- Shows Top 10 zip codes for selected metric
- Horizontal bar chart with score labels

### 3. **Score Cards**
- Seven individual score cards
- Color-coded by performance (red/yellow/green)
- Displays score and performance indicator (✓ Excellent, ⚠ Good, etc.)
- Updates based on zip code selection from map

### 4. **Grouped Bar Chart**
- Side-by-side comparison of all seven variables
- Each variable represented by distinct color
- Sorted by composite score (highest to lowest)
- Helps identify strengths and weaknesses of each neighborhood

### 5. **Data Table**
- Sortable, filterable table view
- Shows all zip codes with all metrics
- Export functionality for further analysis

---

## Scoring

### Weighting Rationale
- **Crime (25%)**: Primary concern for most users, fundamental to livability
- **Schools (20%)**: Critical for families, long-term property value
- **Housing (20%)**: Affordability directly impacts accessibility
- **Transit (15%)**: Important for car-free living, but not universal priority
- **Lifestyle (10%)**: Nice-to-have amenities, subjective preferences
- **Diversity (10%)**: Community character, less directly impactful on daily life

---



## 🛠️ Troubleshooting

### Common Issues

**Issue**: Census API not responding  
**Solution**: Check API key, verify Census server status at https://www.census.gov/data/developers/updates.html

**Issue**: Niche data collection failing  
**Solution**: Website structure may have changed; update BeautifulSoup selectors in scraping script

**Issue**: Tableau map not displaying zip codes  
**Solution**: Ensure ZCTA (ZIP Code Tabulation Area) shapefiles are properly loaded; try regenerating from Census TIGER files

**Issue**: Scores not calculating correctly  
**Solution**: Check for missing data in source CSV files; review normalization formulas in `step8_calculate_scores.py`

---

## 📝 Limitations & Considerations

1. **Zip Code Boundaries**: Uses Census ZCTA boundaries which may not match USPS zip codes exactly
2. **Score Subjectivity**: Weighting scheme reflects general priorities but may not match individual preferences
3. **Data Timeliness**: Some datasets updated more frequently than others
4. **Niche Grades**: Based on Niche's proprietary methodology; may not reflect all user priorities
5. **Crime Reporting**: Reported crime may not capture all incidents; reporting rates vary by neighborhood
6. **School Quality**: Grades don't capture all aspects of educational quality (arts, sports, special programs)
7. **Transit Score**: Doesn't account for service frequency or reliability
8. **Lifestyle Metrics**: Subjective ratings from Niche may not reflect individual preferences

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional variables (air quality, walkability, restaurant density)
- Real-time data integration
- Machine learning for personalized recommendations
- Mobile-responsive dashboard version

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

**Data Licenses**:
- Census data: Public domain (U.S. Government)
- Crime data: Open Data Commons (City of Boston)
- MBTA data: Public domain
- Niche data: Used in accordance with fair use for educational purposes

---

## 👤 Author

**Rishabh Madani**  
Data Analytics Student  
[Your Email] | [Your GitHub] | [Your LinkedIn]

---

## 🙏 Acknowledgments

- U.S. Census Bureau for comprehensive demographic data
- Boston Police Department for transparent crime reporting
- MBTA for open transit data
- Niche.com for education and lifestyle ratings
- Tableau Public for visualization platform
- Professor [Name] and [Course Code] for project guidance

---

## 📚 References

### Academic Sources
- Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, 27(3), 379-423.
- Florida, R. (2019). *The New Urban Crisis: How Our Cities Are Increasing Inequality*. Basic Books.

### Technical Documentation
- Tableau. (2024). *Tableau Desktop User Guide*. Retrieved from https://help.tableau.com
- GeoPandas. (2024). *GeoPandas Documentation*. Retrieved from https://geopandas.org

### Data Sources
All data sources are cited in APA format throughout this document and on the dashboard.

---

**Last Updated**: December 2024  
**Dashboard Version**: 1.0  
**Data Current As Of**: December 2024