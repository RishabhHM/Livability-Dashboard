"""
Step 5: Automatically collect housing affordability data for Boston zip codes
Data source: US Census American Community Survey (ACS) 5-Year Estimates
"""

import pandas as pd
import geopandas as gpd
import requests
from pathlib import Path
import os
from dotenv import load_dotenv

DATA_DIR = Path("data")
HOUSING_DIR = DATA_DIR / "housing"
HOUSING_DIR.mkdir(exist_ok=True)

load_dotenv()
CENSUS_API_KEY = os.getenv('CENSUS_API_KEY', '')

# ACS 5-Year Estimates (most recent available)
ACS_BASE_URL = "https://api.census.gov/data/2022/acs/acs5"


def get_census_housing_data(zip_codes):
    """
    Get housing data from Census ACS API
    """
    print("\n" + "=" * 70)
    print("FETCHING HOUSING DATA FROM US CENSUS ACS")
    print("=" * 70)
    
    if not CENSUS_API_KEY:
        print("\n⚠ WARNING: No Census API key found")
        print("You can get a free key at: https://api.census.gov/data/key_signup.html")
        print("Add it to .env file as: CENSUS_API_KEY=your_key_here")
        print("\nFalling back to synthetic data...")
        return pd.DataFrame()
    
    print(f"\nAPI Endpoint: {ACS_BASE_URL}")
    print(f"Requesting data for Massachusetts ZIP codes...")
    
    # Fetch data for all Massachusetts ZCTAs
    # Note: Census API uses "zip code tabulation area" (no "in state" clause for ZCTAs)
    params = {
        'get': 'NAME,B25077_001E,B25064_001E,B19013_001E',
        'for': 'zip code tabulation area:*',
        'key': CENSUS_API_KEY
    }
    
    try:
        response = requests.get(ACS_BASE_URL, params=params, timeout=30)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"✗ API returned status code: {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            return pd.DataFrame()
        
        content_type = response.headers.get('content-type', '')
        if 'json' not in content_type.lower():
            print(f"✗ API returned non-JSON response: {content_type}")
            print(f"Response text: {response.text[:500]}")
            return pd.DataFrame()
        
        data = response.json()
        
        if not data or len(data) <= 1:
            print("✗ No data returned from Census API")
            return pd.DataFrame()
        
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        
        print(f"✓ Retrieved data for {len(df)} ZIP codes from Census")
        
        # Rename columns
        df = df.rename(columns={
            'NAME': 'name',
            'zip code tabulation area': 'zip_code',
            'B25077_001E': 'median_home_value',
            'B25064_001E': 'median_rent',
            'B19013_001E': 'median_household_income'
        })
        
        # Filter for Massachusetts ZIP codes (02xxx) and our target ZIPs
        df = df[df['zip_code'].str.startswith('02', na=False)]
        df = df[df['zip_code'].isin(zip_codes)]
        
        print(f"✓ Filtered to {len(df)} target Suffolk County ZIP codes")
        
        if len(df) == 0:
            print("⚠ No matching ZIP codes found in Census data")
            return pd.DataFrame()
        
        # Convert to numeric
        for col in ['median_home_value', 'median_rent', 'median_household_income']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Handle Census "not available" codes
        # -66666666 = Data not available/suppressed due to small sample size
        # -99999999 = N/A (not applicable)
        # -88888888 = Data withheld
        
        print("\nHandling Census 'not available' codes...")
        
        na_codes = [-66666666, -99999999, -88888888, -666666666]
        problem_zips = []
        
        for col in ['median_home_value', 'median_rent', 'median_household_income']:
            mask = df[col].isin(na_codes)
            if mask.any():
                affected = df.loc[mask, 'zip_code'].tolist()
                problem_zips.extend(affected)
                print(f"  {col}: {mask.sum()} ZIP codes with N/A codes: {affected}")
                df.loc[mask, col] = None
        
        problem_zips = list(set(problem_zips))
        
        if problem_zips:
            print(f"\n⚠ ZIPs with missing Census data: {sorted(problem_zips)}")
            print("  These will be filled with neighborhood-based estimates")
            
            # Estimate values based on nearby ZIPs or neighborhood patterns
            estimates = {
                '02133': (450000, 1700, 55000),   # Small area, use modest estimates
                '02163': (580000, 2100, 72000),   # Near Hyde Park
                '02199': (825000, 3300, 105000),  # Back Bay/Fenway - expensive
                '02203': (680000, 2800, 88000),   # Near Back Bay
            }
            
            for zip_code, (home_val, rent, income) in estimates.items():
                if zip_code in problem_zips:
                    mask = df['zip_code'] == zip_code
                    if df.loc[mask, 'median_home_value'].isna().any():
                        df.loc[mask, 'median_home_value'] = home_val
                    if df.loc[mask, 'median_rent'].isna().any():
                        df.loc[mask, 'median_rent'] = rent
                    if df.loc[mask, 'median_household_income'].isna().any():
                        df.loc[mask, 'median_household_income'] = income
                    print(f"  ✓ Filled {zip_code} with neighborhood estimates")
        
        # Show sample
        print("\nSample data:")
        sample_cols = ['zip_code', 'median_home_value', 'median_rent', 'median_household_income']
        print(df[sample_cols].head().to_string(index=False))
        
        # Check for remaining missing data
        missing = df[['median_home_value', 'median_rent', 'median_household_income']].isna().sum()
        if missing.any():
            print(f"\n⚠ Warning: Some values still missing after imputation:")
            for col, count in missing[missing > 0].items():
                print(f"  {col}: {count} missing values")
        
        # Add source column to track which values were estimated
        df['data_source'] = 'census_api'
        if problem_zips:
            df.loc[df['zip_code'].isin(problem_zips), 'data_source'] = 'estimated'
        
        return df
        
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error: {e}")
        return pd.DataFrame()
    except ValueError as e:
        print(f"✗ JSON parsing error: {e}")
        print(f"Response content: {response.text[:500]}")
        return pd.DataFrame()
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return pd.DataFrame()


def create_synthetic_housing_data(zip_codes):
    """
    Create synthetic housing data based on Boston patterns
    Fallback if Census API fails
    """
    print("\n" + "=" * 70)
    print("CREATING SYNTHETIC HOUSING DATA")
    print("=" * 70)
    print("\n⚠ Using estimated housing values based on Boston patterns")
    
    # Typical Boston housing patterns (2023 estimates)
    synthetic_data = {
        # Downtown/Urban Core - Very expensive
        '02108': (850000, 3200, 95000),
        '02109': (780000, 3500, 105000),
        '02110': (820000, 3400, 98000),
        '02111': (720000, 3100, 92000),
        
        # Back Bay/Beacon Hill - Expensive
        '02113': (695000, 2900, 88000),
        '02114': (875000, 3600, 115000),
        '02115': (625000, 2400, 72000),
        '02116': (920000, 3800, 125000),
        
        # South End/Roxbury - Mid to High
        '02118': (680000, 2800, 85000),
        '02119': (550000, 2100, 68000),
        '02120': (615000, 2300, 75000),
        '02121': (485000, 1850, 58000),
        
        # Dorchester - Moderate
        '02122': (520000, 1950, 65000),
        '02124': (495000, 1800, 61000),
        '02125': (535000, 2000, 67000),
        '02126': (510000, 1900, 64000),
        
        # South Boston/Seaport - High
        '02127': (745000, 3000, 95000),
        '02128': (580000, 2200, 78000),
        '02129': (695000, 2750, 88000),
        
        # Jamaica Plain/Roslindale - Moderate to High
        '02130': (685000, 2600, 82000),
        '02131': (625000, 2350, 77000),
        '02132': (655000, 2500, 80000),
        
        # Special ZIPs
        '02133': (450000, 1700, 55000),
        
        # Allston/Brighton - Moderate
        '02134': (595000, 2250, 71000),
        '02135': (615000, 2300, 74000),
        
        # Hyde Park/Mattapan
        '02136': (525000, 1950, 66000),
        '02163': (580000, 2100, 72000),
        
        # Fenway/Back Bay
        '02199': (825000, 3300, 105000),
        '02203': (680000, 2800, 88000),
        
        # Seaport
        '02210': (895000, 3700, 118000),
        
        # Fenway/Longwood
        '02215': (645000, 2450, 76000),
    }
    
    results = []
    for zip_code in zip_codes:
        if zip_code in synthetic_data:
            home_val, rent, income = synthetic_data[zip_code]
        else:
            # Default values
            home_val, rent, income = 600000, 2300, 75000
        
        results.append({
            'zip_code': zip_code,
            'median_home_value': home_val,
            'median_rent': rent,
            'median_household_income': income,
            'source': 'synthetic'
        })
    
    df = pd.DataFrame(results)
    
    print(f"✓ Created synthetic data for {len(df)} zip codes")
    print("\nNote: These are estimates based on 2023 Boston housing market patterns.")
    print("For production use, collect real data from Census API or Zillow.")
    
    return df


def calculate_housing_scores(df_housing):
    """
    Calculate housing affordability scores
    Lower cost = higher score (more affordable)
    """
    print("\n" + "=" * 70)
    print("CALCULATING HOUSING AFFORDABILITY SCORES")
    print("=" * 70)
    
    # Handle missing data
    df_housing['median_home_value'] = df_housing['median_home_value'].fillna(df_housing['median_home_value'].median())
    df_housing['median_rent'] = df_housing['median_rent'].fillna(df_housing['median_rent'].median())
    df_housing['median_household_income'] = df_housing['median_household_income'].fillna(df_housing['median_household_income'].median())
    
    # Calculate affordability metrics
    # Price-to-Income Ratio (lower is better)
    df_housing['price_to_income_ratio'] = df_housing['median_home_value'] / df_housing['median_household_income']
    
    # Rent-to-Income Ratio (annual rent / annual income)
    df_housing['rent_to_income_ratio'] = (df_housing['median_rent'] * 12) / df_housing['median_household_income']
    
    print("\nNormalizing housing scores to 0-10 scale...")
    print("Note: Lower cost = Higher score (10 = most affordable)")
    
    def normalize_and_invert(series):
        """Normalize and invert so low cost = high score"""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([5.0] * len(series), index=series.index)
        normalized = (series - min_val) / (max_val - min_val)
        return (1 - normalized) * 10
    
    # Home value score (inverted - lower price = higher score)
    df_housing['home_value_score'] = normalize_and_invert(df_housing['median_home_value'])
    
    # Rent score (inverted - lower rent = higher score)
    df_housing['rent_score'] = normalize_and_invert(df_housing['median_rent'])
    
    # Price-to-income score (inverted - lower ratio = higher score)
    df_housing['price_income_score'] = normalize_and_invert(df_housing['price_to_income_ratio'])
    
    # Overall housing affordability score
    # Weight all three components
    df_housing['overall_housing_score'] = (
        df_housing['home_value_score'] * 0.40 +
        df_housing['rent_score'] * 0.35 +
        df_housing['price_income_score'] * 0.25
    )
    
    print("✓ Housing scores calculated")
    
    print("\n" + "-" * 70)
    print("HOUSING AFFORDABILITY SUMMARY (Scale: 10 = Most Affordable, 0 = Least)")
    print("-" * 70)
    print(f"\nAverage affordability score: {df_housing['overall_housing_score'].mean():.2f} / 10")
    print(f"Most affordable:  {df_housing['overall_housing_score'].max():.2f} (ZIP: {df_housing.loc[df_housing['overall_housing_score'].idxmax(), 'zip_code']})")
    print(f"Least affordable: {df_housing['overall_housing_score'].min():.2f} (ZIP: {df_housing.loc[df_housing['overall_housing_score'].idxmin(), 'zip_code']})")
    
    print(f"\nMedian home value range:")
    print(f"  Lowest:  ${df_housing['median_home_value'].min():,.0f} (ZIP: {df_housing.loc[df_housing['median_home_value'].idxmin(), 'zip_code']})")
    print(f"  Highest: ${df_housing['median_home_value'].max():,.0f} (ZIP: {df_housing.loc[df_housing['median_home_value'].idxmax(), 'zip_code']})")
    
    print(f"\nMedian rent range:")
    print(f"  Lowest:  ${df_housing['median_rent'].min():,.0f}/month (ZIP: {df_housing.loc[df_housing['median_rent'].idxmin(), 'zip_code']})")
    print(f"  Highest: ${df_housing['median_rent'].max():,.0f}/month (ZIP: {df_housing.loc[df_housing['median_rent'].idxmax(), 'zip_code']})")
    
    print(f"\nZip codes by affordability tier:")
    print(f"  Very Affordable (8.0-10.0): {(df_housing['overall_housing_score'] >= 8.0).sum()}")
    print(f"  Affordable (6.0-7.9):       {((df_housing['overall_housing_score'] >= 6.0) & (df_housing['overall_housing_score'] < 8.0)).sum()}")
    print(f"  Moderate (4.0-5.9):         {((df_housing['overall_housing_score'] >= 4.0) & (df_housing['overall_housing_score'] < 6.0)).sum()}")
    print(f"  Expensive (2.0-3.9):        {((df_housing['overall_housing_score'] >= 2.0) & (df_housing['overall_housing_score'] < 4.0)).sum()}")
    print(f"  Very Expensive (0.0-1.9):   {(df_housing['overall_housing_score'] < 2.0).sum()}")
    
    return df_housing


def main():
    print("\n" + "=" * 70)
    print("STEP 5: COLLECT AND PROCESS HOUSING DATA")
    print("=" * 70)
    
    print("\nLoading Boston zip codes from Step 1...")
    zip_geo_path = DATA_DIR / "suffolk_zipcodes.geojson"
    
    if not zip_geo_path.exists():
        print(f"✗ Error: {zip_geo_path} not found")
        print("Please run step1_get_zipcode_boundaries.py first")
        return
    
    gdf_zips = gpd.read_file(zip_geo_path)
    zip_codes = sorted(gdf_zips['zip_code'].unique().tolist())
    print(f"✓ Loaded {len(zip_codes)} zip codes")
    
    # Try Census API first
    print("\n" + "=" * 70)
    print("COLLECTION METHOD SELECTION")
    print("=" * 70)
    print("\nOptions:")
    print("1. Fetch from Census API (requires API key, most accurate)")
    print("2. Use synthetic data (instant, estimates based on market)")
    
    choice = input("\nEnter choice (1/2) [default: 1]: ").strip() or "1"
    
    if choice == "1":
        df_housing = get_census_housing_data(zip_codes)
        
        if df_housing.empty:
            print("\n⚠ Census API failed, falling back to synthetic data")
            df_housing = create_synthetic_housing_data(zip_codes)
    else:
        df_housing = create_synthetic_housing_data(zip_codes)
    
    # Calculate scores
    df_housing = calculate_housing_scores(df_housing)
    
    # Save outputs
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    output_file = HOUSING_DIR / "housing_scores_by_zipcode.csv"
    output_columns = [
        'zip_code', 'median_home_value', 'median_rent', 'median_household_income',
        'price_to_income_ratio', 'rent_to_income_ratio',
        'home_value_score', 'rent_score', 'price_income_score', 'overall_housing_score',
        'data_source'
    ]
    
    # Only include data_source if it exists
    if 'data_source' not in df_housing.columns:
        output_columns.remove('data_source')
    
    df_housing[output_columns].to_csv(output_file, index=False)
    print(f"\n✓ Saved housing scores: {output_file}")
    
    print("\n" + "=" * 70)
    print("TOP 5 MOST AFFORDABLE ZIP CODES")
    print("=" * 70)
    top_5 = df_housing.nlargest(5, 'overall_housing_score')[
        ['zip_code', 'median_home_value', 'median_rent', 'overall_housing_score']
    ]
    print(top_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("TOP 5 LEAST AFFORDABLE ZIP CODES (Most Expensive)")
    print("=" * 70)
    bottom_5 = df_housing.nsmallest(5, 'overall_housing_score')[
        ['zip_code', 'median_home_value', 'median_rent', 'overall_housing_score']
    ]
    print(bottom_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("STEP 5 COMPLETE ✓")
    print("=" * 70)
    print(f"\nProcessed housing data for {len(df_housing)} zip codes")

if __name__ == "__main__":
    main()