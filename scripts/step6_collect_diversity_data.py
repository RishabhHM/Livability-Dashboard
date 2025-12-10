"""
Step 6: Automatically collect diversity data for Boston zip codes
Data source: US Census American Community Survey (ACS) 5-Year Estimates
Calculates Shannon Diversity Index for race, education, and age
"""

import pandas as pd
import geopandas as gpd
import requests
from pathlib import Path
import numpy as np
import os
from dotenv import load_dotenv

DATA_DIR = Path("data")
DIVERSITY_DIR = DATA_DIR / "diversity"
DIVERSITY_DIR.mkdir(exist_ok=True)

load_dotenv()
CENSUS_API_KEY = os.getenv('CENSUS_API_KEY', '')

ACS_BASE_URL = "https://api.census.gov/data/2022/acs/acs5"


def calculate_shannon_diversity_index(proportions):
    """
    Calculate Shannon Diversity Index
    H = -Σ(pi * ln(pi))
    Higher H = more diverse
    """
    proportions = np.array(proportions)
    proportions = proportions[proportions > 0]
    
    if len(proportions) == 0:
        return 0
    
    H = -np.sum(proportions * np.log(proportions))
    return H


def get_census_diversity_data(zip_codes):
    """
    Get diversity data from Census ACS API
    """
    print("\n" + "=" * 70)
    print("FETCHING DIVERSITY DATA FROM US CENSUS ACS")
    print("=" * 70)
    
    if not CENSUS_API_KEY:
        print("\n⚠ WARNING: No Census API key found")
        print("Falling back to synthetic data...")
        return pd.DataFrame()
    
    print(f"\nAPI Endpoint: {ACS_BASE_URL}")
    print(f"Requesting demographic data for ZIP codes...")
    
    # Race variables (Table B02001)
    # B02001_001E: Total population
    # B02001_002E: White alone
    # B02001_003E: Black or African American alone
    # B02001_004E: American Indian and Alaska Native alone
    # B02001_005E: Asian alone
    # B02001_006E: Native Hawaiian and Other Pacific Islander alone
    # B02001_007E: Some other race alone
    # B02001_008E: Two or more races
    
    race_vars = [
        'B02001_001E',  # Total
        'B02001_002E',  # White
        'B02001_003E',  # Black
        'B02001_005E',  # Asian
        'B02001_007E',  # Other
        'B02001_008E',  # Two or more
    ]
    
    params = {
        'get': 'NAME,' + ','.join(race_vars),
        'for': 'zip code tabulation area:*',
        'key': CENSUS_API_KEY
    }
    
    try:
        response = requests.get(ACS_BASE_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"✗ API returned status code: {response.status_code}")
            return pd.DataFrame()
        
        data = response.json()
        
        if not data or len(data) <= 1:
            print("✗ No data returned")
            return pd.DataFrame()
        
        headers = data[0]
        rows = data[1:]
        
        df = pd.DataFrame(rows, columns=headers)
        
        print(f"✓ Retrieved data for {len(df)} ZIP codes")
        
        # Rename columns
        df = df.rename(columns={
            'NAME': 'name',
            'zip code tabulation area': 'zip_code',
            'B02001_001E': 'total_pop',
            'B02001_002E': 'white',
            'B02001_003E': 'black',
            'B02001_005E': 'asian',
            'B02001_007E': 'other',
            'B02001_008E': 'two_or_more',
        })
        
        # Filter for our target ZIP codes
        df = df[df['zip_code'].str.startswith('02', na=False)]
        df = df[df['zip_code'].isin(zip_codes)]
        
        print(f"✓ Filtered to {len(df)} target ZIP codes")
        
        if len(df) == 0:
            return pd.DataFrame()
        
        # Convert to numeric
        numeric_cols = ['total_pop', 'white', 'black', 'asian', 'other', 'two_or_more']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Handle Census N/A codes
        na_codes = [-66666666, -99999999, -88888888, -666666666]
        for col in numeric_cols:
            df[col] = df[col].replace(na_codes, np.nan)
        
        df['data_source'] = 'census_api'
        
        return df
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return pd.DataFrame()


def create_synthetic_diversity_data(zip_codes):
    """
    Create synthetic diversity data based on Boston patterns
    """
    print("\n" + "=" * 70)
    print("CREATING SYNTHETIC DIVERSITY DATA")
    print("=" * 70)
    print("\n⚠ Using estimated diversity based on Boston patterns")
    
    # Boston diversity patterns (approximate 2020 Census)
    synthetic_data = {
        # Downtown - High diversity
        '02108': (5000, 2500, 500, 1500, 300, 200),   # White, Black, Asian, Other, Two+
        '02109': (4500, 2800, 400, 1000, 200, 100),
        '02110': (3800, 1900, 600, 900, 300, 100),
        '02111': (7200, 3200, 1200, 2000, 500, 300),
        
        # Back Bay/Beacon Hill - Less diverse, affluent
        '02113': (4100, 2700, 300, 800, 200, 100),
        '02114': (9800, 7500, 500, 1200, 400, 200),
        '02115': (18500, 9000, 2500, 5500, 1000, 500),
        '02116': (15200, 11000, 800, 2500, 600, 300),
        
        # South End/Roxbury - High Black/Hispanic population
        '02118': (21600, 8000, 5500, 4500, 2500, 1100),
        '02119': (27500, 8000, 12000, 4000, 2500, 1000),
        '02120': (23400, 6500, 11000, 3500, 1800, 600),
        '02121': (34200, 6000, 22000, 2500, 2700, 1000),
        
        # Dorchester - Very diverse
        '02122': (29800, 10000, 8500, 6500, 3500, 1300),
        '02124': (48200, 12000, 25000, 6000, 3800, 1400),
        '02125': (33500, 11000, 14000, 4500, 3000, 1000),
        '02126': (33100, 9000, 17000, 3500, 2800, 800),
        
        # South Boston - Less diverse, Irish heritage
        '02127': (33800, 27000, 1200, 2800, 2000, 800),
        '02128': (36400, 25000, 1500, 6500, 2500, 900),
        '02129': (28400, 23000, 800, 2200, 1800, 600),
        
        # Jamaica Plain - Diverse
        '02130': (37700, 19000, 5500, 4500, 7000, 1700),
        '02131': (28200, 14000, 7500, 2500, 3500, 700),
        '02132': (31500, 20000, 4000, 3000, 3500, 1000),
        
        # Small/Special ZIPs
        '02133': (500, 300, 100, 50, 30, 20),
        
        # Allston/Brighton - Diverse, student population
        '02134': (29500, 16000, 2500, 7500, 2500, 1000),
        '02135': (40200, 24000, 3500, 8500, 3000, 1200),
        
        # Hyde Park/Mattapan
        '02136': (32600, 8000, 18000, 2500, 3200, 900),
        '02163': (3200, 1000, 1500, 300, 300, 100),
        
        # Fenway/Back Bay
        '02199': (14800, 9500, 1200, 3000, 800, 300),
        '02203': (2100, 1400, 200, 300, 150, 50),
        
        # Seaport
        '02210': (3500, 2500, 200, 500, 200, 100),
        
        # Fenway/Longwood
        '02215': (30500, 15000, 3500, 9000, 2500, 500),
    }
    
    results = []
    for zip_code in zip_codes:
        if zip_code in synthetic_data:
            total, white, black, asian, other, two_or_more = synthetic_data[zip_code]
        else:
            total, white, black, asian, other, two_or_more = (10000, 5500, 2000, 1500, 700, 300)
        
        results.append({
            'zip_code': zip_code,
            'total_pop': total,
            'white': white,
            'black': black,
            'asian': asian,
            'other': other,
            'two_or_more': two_or_more,
            'data_source': 'synthetic'
        })
    
    df = pd.DataFrame(results)
    print(f"✓ Created synthetic data for {len(df)} zip codes")
    
    return df


def calculate_diversity_scores(df_diversity):
    """
    Calculate diversity scores using Shannon Diversity Index
    """
    print("\n" + "=" * 70)
    print("CALCULATING DIVERSITY SCORES")
    print("=" * 70)
    
    # Fill missing values with 0
    race_cols = ['white', 'black', 'asian', 'other', 'two_or_more']
    for col in race_cols:
        df_diversity[col] = df_diversity[col].fillna(0)
    
    # Handle special ZIP codes with no residential population
    special_zips = ['02133']  # PO Box only, no residents
    
    print("\nCalculating racial/ethnic diversity using Shannon Index...")
    
    diversity_scores = []
    
    for idx, row in df_diversity.iterrows():
        zip_code = row['zip_code']
        total = row['total_pop']
        
        # Handle special non-residential ZIPs
        if zip_code in special_zips or pd.isna(total) or total == 0 or total < 100:
            print(f"  ⚠ {zip_code}: Special/non-residential ZIP (population: {total}), setting diversity to N/A")
            diversity_scores.append(np.nan)
            continue
        
        # Calculate proportions
        proportions = [
            row['white'] / total,
            row['black'] / total,
            row['asian'] / total,
            row['other'] / total,
            row['two_or_more'] / total,
        ]
        
        # Shannon Diversity Index
        H = calculate_shannon_diversity_index(proportions)
        
        diversity_scores.append(H)
    
    df_diversity['diversity_index'] = diversity_scores
    
    # Normalize to 0-10 scale
    # Max Shannon Index for 5 groups = ln(5) = 1.609
    max_H = np.log(5)
    df_diversity['diversity_score'] = (df_diversity['diversity_index'] / max_H) * 10
    
    # Calculate percentages for reference
    df_diversity['pct_white'] = (df_diversity['white'] / df_diversity['total_pop'] * 100).round(1)
    df_diversity['pct_black'] = (df_diversity['black'] / df_diversity['total_pop'] * 100).round(1)
    df_diversity['pct_asian'] = (df_diversity['asian'] / df_diversity['total_pop'] * 100).round(1)
    df_diversity['pct_other'] = (df_diversity['other'] / df_diversity['total_pop'] * 100).round(1)
    df_diversity['pct_two_or_more'] = (df_diversity['two_or_more'] / df_diversity['total_pop'] * 100).round(1)
    
    # Mark special ZIPs
    df_diversity.loc[df_diversity['zip_code'].isin(special_zips), 'data_source'] = 'special_zip'
    
    print("✓ Diversity scores calculated")
    
    # Filter out special ZIPs for statistics
    df_analysis = df_diversity[~df_diversity['zip_code'].isin(special_zips)].copy()
    
    print("\n" + "-" * 70)
    print("DIVERSITY SCORE SUMMARY (Scale: 10 = Most Diverse, 0 = Least)")
    print("-" * 70)
    print(f"\nZIPs analyzed: {len(df_analysis)} (excluding {len(special_zips)} special ZIPs)")
    print(f"Special ZIPs excluded: {', '.join(special_zips)}")
    print(f"\nAverage diversity score: {df_analysis['diversity_score'].mean():.2f} / 10")
    print(f"Most diverse:  {df_analysis['diversity_score'].max():.2f} (ZIP: {df_analysis.loc[df_analysis['diversity_score'].idxmax(), 'zip_code']})")
    print(f"Least diverse: {df_analysis['diversity_score'].min():.2f} (ZIP: {df_analysis.loc[df_analysis['diversity_score'].idxmin(), 'zip_code']})")
    
    print(f"\nZip codes by diversity tier:")
    print(f"  Very Diverse (8.0-10.0):    {(df_analysis['diversity_score'] >= 8.0).sum()}")
    print(f"  Diverse (6.0-7.9):          {((df_analysis['diversity_score'] >= 6.0) & (df_analysis['diversity_score'] < 8.0)).sum()}")
    print(f"  Moderate (4.0-5.9):         {((df_analysis['diversity_score'] >= 4.0) & (df_analysis['diversity_score'] < 6.0)).sum()}")
    print(f"  Less Diverse (2.0-3.9):     {((df_analysis['diversity_score'] >= 2.0) & (df_analysis['diversity_score'] < 4.0)).sum()}")
    print(f"  Least Diverse (0.0-1.9):    {(df_analysis['diversity_score'] < 2.0).sum()}")
    
    return df_diversity


def main():
    print("\n" + "=" * 70)
    print("STEP 6: COLLECT AND PROCESS DIVERSITY DATA")
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
    
    print("\n" + "=" * 70)
    print("COLLECTION METHOD SELECTION")
    print("=" * 70)
    print("\nOptions:")
    print("1. Fetch from Census API (requires API key)")
    print("2. Use synthetic data (estimates based on 2020 Census)")
    
    choice = input("\nEnter choice (1/2) [default: 1]: ").strip() or "1"
    
    if choice == "1" and CENSUS_API_KEY:
        df_diversity = get_census_diversity_data(zip_codes)
        
        if df_diversity.empty:
            print("\n⚠ Census API failed, falling back to synthetic data")
            df_diversity = create_synthetic_diversity_data(zip_codes)
    else:
        if choice == "1":
            print("\n⚠ No API key found, using synthetic data")
        df_diversity = create_synthetic_diversity_data(zip_codes)
    
    # Calculate scores
    df_diversity = calculate_diversity_scores(df_diversity)
    
    # Save outputs
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    output_file = DIVERSITY_DIR / "diversity_scores_by_zipcode.csv"
    output_columns = [
        'zip_code', 'total_pop', 'white', 'black', 'asian', 'other', 'two_or_more',
        'pct_white', 'pct_black', 'pct_asian', 'pct_other', 'pct_two_or_more',
        'diversity_index', 'diversity_score', 'data_source'
    ]
    
    if 'data_source' not in df_diversity.columns:
        output_columns.remove('data_source')
    
    df_diversity[output_columns].to_csv(output_file, index=False)
    print(f"\n✓ Saved diversity scores: {output_file}")
    
    print("\n" + "=" * 70)
    print("TOP 5 MOST DIVERSE ZIP CODES")
    print("=" * 70)
    top_5 = df_diversity.nlargest(5, 'diversity_score')[
        ['zip_code', 'pct_white', 'pct_black', 'pct_asian', 'diversity_score']
    ]
    print(top_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("TOP 5 LEAST DIVERSE ZIP CODES")
    print("=" * 70)
    bottom_5 = df_diversity.nsmallest(5, 'diversity_score')[
        ['zip_code', 'pct_white', 'pct_black', 'pct_asian', 'diversity_score']
    ]
    print(bottom_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("STEP 6 COMPLETE ✓")
    print("=" * 70)
    print(f"\nProcessed diversity data for {len(df_diversity)} zip codes")


if __name__ == "__main__":
    main()