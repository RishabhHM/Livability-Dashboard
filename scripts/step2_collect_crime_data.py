"""
Step 2: Automatically collect crime data for Boston zip codes
Data source: Boston Police Department Crime Incident Reports
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path("data")
CRIME_DIR = DATA_DIR / "crime"
CRIME_DIR.mkdir(exist_ok=True)

    
def load_local_crime_data():
    print("\n" + "=" * 70)
    print("LOADING LOCAL CRIME DATA")
    print("=" * 70)
    
    local_csv = CRIME_DIR / "boston_crime.csv"
    
    if not local_csv.exists():
        print(f"✗ Error: {local_csv} not found")
        print(f"Please save the crime data CSV as: {local_csv}")
        return pd.DataFrame()
    
    print(f"\nReading local crime file: {local_csv}")
    
    try:
        df = pd.read_csv(local_csv, low_memory=False)
        print(f"✓ Loaded {len(df):,} crime records from local file")
        
        print(f"\nColumns found ({len(df.columns)} total):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        print("\n" + "-" * 70)
        print("CHECKING OFFENSE DATA")
        print("-" * 70)
        
        offense_cols = [col for col in df.columns if 'OFFENSE' in col.upper() or 'CRIME' in col.upper()]
        print(f"\nOffense-related columns found: {offense_cols}")
        
        for col in offense_cols:
            non_null = df[col].notna().sum()
            print(f"\n{col}:")
            print(f"  Non-null values: {non_null:,} ({non_null/len(df)*100:.1f}%)")
            print(f"  Sample values: {df[col].dropna().unique()[:5].tolist()}")
        
        return df
        
    except Exception as e:
        print(f"✗ Error reading CSV: {e}")
        return pd.DataFrame()


def clean_and_process_crime_data(df):
    print("\n" + "=" * 70)
    print("CLEANING AND PROCESSING CRIME DATA")
    print("=" * 70)
    
    print(f"\nInitial records: {len(df):,}")
    
    print("\nChecking required columns...")
    required_cols = ['OCCURRED_ON_DATE', 'Lat', 'Long', 'OFFENSE_DESCRIPTION']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"✗ Missing columns: {missing_cols}")
        print(f"Available columns: {df.columns.tolist()}")
        return pd.DataFrame()
    
    print("✓ All required columns present")
    
    df = df.copy()
    
    print("\nRemoving records without coordinates...")
    before = len(df)
    df = df.dropna(subset=['Lat', 'Long'])
    after = len(df)
    print(f"✓ Removed {before - after:,} records without coordinates ({after:,} remaining)")
    
    print("\nParsing dates...")
    df['OCCURRED_ON_DATE'] = pd.to_datetime(df['OCCURRED_ON_DATE'], errors='coerce')
    
    if df['OCCURRED_ON_DATE'].dt.tz is not None:
        df['OCCURRED_ON_DATE'] = df['OCCURRED_ON_DATE'].dt.tz_localize(None)
    
    df = df.dropna(subset=['OCCURRED_ON_DATE'])
    print(f"✓ Valid date records: {len(df):,}")
    
    # Determine data date range
    min_date = df['OCCURRED_ON_DATE'].min()
    max_date = df['OCCURRED_ON_DATE'].max()
    print(f"\nData date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    
    # Use all available data if it's already recent, otherwise filter last 3 years
    three_years_ago = pd.Timestamp(datetime.now() - timedelta(days=3*365))
    
    if min_date >= three_years_ago:
        print(f"✓ Using all {len(df):,} records (data is already from last 3 years)")
    else:
        before = len(df)
        df = df[df['OCCURRED_ON_DATE'] >= three_years_ago]
        print(f"✓ Filtered to last 3 years: {len(df):,} records (removed {before - len(df):,} older records)")
    
    df['year'] = df['OCCURRED_ON_DATE'].dt.year
    
    print("\nClassifying crime types...")
    
    df['OFFENSE_DESCRIPTION'] = df['OFFENSE_DESCRIPTION'].fillna('UNKNOWN')
    
    unique_offenses = df['OFFENSE_DESCRIPTION'].unique()
    print(f"Number of unique offense descriptions: {len(unique_offenses)}")
    print(f"Sample descriptions: {unique_offenses[:10].tolist()}")
    
    df['OFFENSE_DESCRIPTION'] = df['OFFENSE_DESCRIPTION'].astype(str).str.upper().str.strip()
    
    violent_keywords = [
        'ASSAULT', 'HOMICIDE', 'MURDER', 'ROBBERY', 'RAPE', 
        'SEX OFFENSE', 'KIDNAPPING', 'HUMAN TRAFFICKING', 
        'MANSLAUGHTER', 'SHOOTING', 'STABBING', 'THREATS'
    ]
    
    property_keywords = [
        'LARCENY', 'BURGLARY', 'THEFT', 'STOLEN', 'BREAKING & ENTERING',
        'AUTO THEFT', 'VANDALISM', 'ARSON', 'SHOPLIFTING', 
        'TRESPASSING', 'PROPERTY DAMAGE', 'B & E'
    ]
    
    df['crime_category'] = 'Other'
    
    for keyword in violent_keywords:
        mask = df['OFFENSE_DESCRIPTION'].str.contains(keyword, case=False, na=False)
        df.loc[mask, 'crime_category'] = 'Violent'
    
    for keyword in property_keywords:
        mask = df['OFFENSE_DESCRIPTION'].str.contains(keyword, case=False, na=False)
        df.loc[mask & (df['crime_category'] != 'Violent'), 'crime_category'] = 'Property'
    
    violent_count = (df['crime_category'] == 'Violent').sum()
    property_count = (df['crime_category'] == 'Property').sum()
    other_count = (df['crime_category'] == 'Other').sum()
    
    print(f"  - Violent crimes:  {violent_count:,} ({violent_count/len(df)*100:.1f}%)")
    print(f"  - Property crimes: {property_count:,} ({property_count/len(df)*100:.1f}%)")
    print(f"  - Other crimes:    {other_count:,} ({other_count/len(df)*100:.1f}%)")
    
    if violent_count == 0 and property_count == 0:
        print("\n⚠ WARNING: No violent or property crimes classified!")
        print("Top 10 offense descriptions in data:")
        print(df['OFFENSE_DESCRIPTION'].value_counts().head(10))
    else:
        print("\n✓ Crime classification successful!")
        print("\nTop violent crime types:")
        print(df[df['crime_category'] == 'Violent']['OFFENSE_DESCRIPTION'].value_counts().head(5))
        print("\nTop property crime types:")
        print(df[df['crime_category'] == 'Property']['OFFENSE_DESCRIPTION'].value_counts().head(5))
    
    return df


def map_crimes_to_zipcodes(df_crime, gdf_zips):
    print("\n" + "=" * 70)
    print("MAPPING CRIMES TO ZIP CODES")
    print("=" * 70)
    
    print("\nCreating spatial points from crime coordinates...")
    gdf_crime = gpd.GeoDataFrame(
        df_crime,
        geometry=gpd.points_from_xy(df_crime.Long, df_crime.Lat),
        crs='EPSG:4326'
    )
    print(f"✓ Created {len(gdf_crime):,} spatial points")
    
    print("\nAligning coordinate reference systems...")
    gdf_zips_aligned = gdf_zips.to_crs('EPSG:4326')
    
    print("Performing spatial join...")
    gdf_crime = gpd.sjoin(
        gdf_crime,
        gdf_zips_aligned[['zip_code', 'geometry']],
        how='left',
        predicate='within'
    )
    
    before = len(gdf_crime)
    gdf_crime = gdf_crime.dropna(subset=['zip_code'])
    after = len(gdf_crime)
    
    print(f"✓ Mapped {after:,} crimes to zip codes")
    print(f"  ({before - after:,} crimes outside target zip codes)")
    
    return gdf_crime


def calculate_crime_scores(gdf_crime, gdf_zips):
    print("\n" + "=" * 70)
    print("CALCULATING CRIME SCORES BY ZIP CODE")
    print("=" * 70)
    
    print("\nAggregating crime statistics by zip code...")
    
    crime_stats = gdf_crime.groupby('zip_code').agg({
        'INCIDENT_NUMBER': 'count',
        'crime_category': lambda x: (x == 'Violent').sum()
    }).rename(columns={
        'INCIDENT_NUMBER': 'total_crimes',
        'crime_category': 'violent_crimes'
    })
    
    crime_stats['property_crimes'] = gdf_crime[gdf_crime['crime_category'] == 'Property'].groupby('zip_code').size()
    crime_stats['property_crimes'] = crime_stats['property_crimes'].fillna(0).astype(int)
    crime_stats['violent_crimes'] = crime_stats['violent_crimes'].astype(int)
    
    print(f"✓ Aggregated data for {len(crime_stats)} zip codes with crimes")
    
    # Check for missing zip codes
    all_zips = set(gdf_zips['zip_code'].unique())
    zips_with_crimes = set(crime_stats.index)
    missing_zips = all_zips - zips_with_crimes
    
    if missing_zips:
        print(f"\n⚠ WARNING: {len(missing_zips)} zip codes have NO crime data:")
        print(f"  Missing ZIPs: {sorted(list(missing_zips))}")
        
        # Add missing zip codes with zero crimes
        for zip_code in missing_zips:
            crime_stats.loc[zip_code] = {
                'total_crimes': 0,
                'violent_crimes': 0,
                'property_crimes': 0
            }
        print(f"✓ Added missing zip codes with 0 crimes")
    
    crime_stats = crime_stats.merge(
        gdf_zips[['zip_code', 'area_sq_mi']].drop_duplicates('zip_code'),
        on='zip_code',
        how='right'
    )
    
    # Fill NaN values for zip codes with no crimes
    crime_stats['total_crimes'] = crime_stats['total_crimes'].fillna(0).astype(int)
    crime_stats['violent_crimes'] = crime_stats['violent_crimes'].fillna(0).astype(int)
    crime_stats['property_crimes'] = crime_stats['property_crimes'].fillna(0).astype(int)
    
    crime_stats['crimes_per_sq_mi'] = crime_stats['total_crimes'] / crime_stats['area_sq_mi']
    crime_stats['violent_per_sq_mi'] = crime_stats['violent_crimes'] / crime_stats['area_sq_mi']
    crime_stats['property_per_sq_mi'] = crime_stats['property_crimes'] / crime_stats['area_sq_mi']
    
    print("\nNormalizing crime scores to 0-10 scale (10 = safest, 0 = least safe)...")
    
    def normalize_and_invert(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([5.0] * len(series), index=series.index)
        normalized = (series - min_val) / (max_val - min_val)
        return (1 - normalized) * 10
    
    crime_stats['crime_score'] = normalize_and_invert(crime_stats['crimes_per_sq_mi'])
    crime_stats['violent_score'] = normalize_and_invert(crime_stats['violent_per_sq_mi'])
    crime_stats['property_score'] = normalize_and_invert(crime_stats['property_per_sq_mi'])
    
    # Overall crime score: weighted combination of all three metrics
    # Total crime (40%) + Violent (35%) + Property (25%)
    crime_stats['overall_crime_score'] = (
        crime_stats['crime_score'] * 0.40 +
        crime_stats['violent_score'] * 0.35 +
        crime_stats['property_score'] * 0.25
    )
    
    print("✓ Crime scores calculated")
    
    print("\n" + "-" * 70)
    print("CRIME SCORE SUMMARY (Scale: 10 = Safest, 0 = Least Safe)")
    print("-" * 70)
    print(f"\nTotal zip codes processed: {len(crime_stats)}")
    print(f"Zip codes with crimes: {len(zips_with_crimes)}")
    print(f"Zip codes with zero crimes: {len(missing_zips)}")
    print(f"\nAverage overall crime score: {crime_stats['overall_crime_score'].mean():.2f} / 10")
    print(f"Highest score (safest):      {crime_stats['overall_crime_score'].max():.2f} (ZIP: {crime_stats['overall_crime_score'].idxmax()})")
    print(f"Lowest score (least safe):   {crime_stats['overall_crime_score'].min():.2f} (ZIP: {crime_stats['overall_crime_score'].idxmin()})")
    
    print(f"\nCrime rate range:")
    print(f"  Lowest:  {crime_stats['crimes_per_sq_mi'].min():.1f} crimes/sq mi (ZIP: {crime_stats['crimes_per_sq_mi'].idxmin()})")
    print(f"  Highest: {crime_stats['crimes_per_sq_mi'].max():.1f} crimes/sq mi (ZIP: {crime_stats['crimes_per_sq_mi'].idxmax()})")
    
    print(f"\nZip codes by safety tier:")
    print(f"  Excellent (8.0-10.0): {(crime_stats['overall_crime_score'] >= 8.0).sum()}")
    print(f"  Good (6.0-7.9):       {((crime_stats['overall_crime_score'] >= 6.0) & (crime_stats['overall_crime_score'] < 8.0)).sum()}")
    print(f"  Average (4.0-5.9):    {((crime_stats['overall_crime_score'] >= 4.0) & (crime_stats['overall_crime_score'] < 6.0)).sum()}")
    print(f"  Below Avg (2.0-3.9):  {((crime_stats['overall_crime_score'] >= 2.0) & (crime_stats['overall_crime_score'] < 4.0)).sum()}")
    print(f"  Poor (0.0-1.9):       {(crime_stats['overall_crime_score'] < 2.0).sum()}")
    
    crime_stats = crime_stats.reset_index()
    
    return crime_stats


def main():
    print("\n" + "=" * 70)
    print("STEP 2: COLLECT AND PROCESS CRIME DATA")
    print("=" * 70)
    
    print("\nLoading Boston zip codes from Step 1...")
    zip_info_path = DATA_DIR / "suffolk_zipcodes_info.csv"
    zip_geo_path = DATA_DIR / "suffolk_zipcodes.geojson"
    
    if not zip_geo_path.exists():
        print(f"✗ Error: {zip_geo_path} not found")
        print("Please run step1_get_zipcode_boundaries.py first")
        return
    
    gdf_zips = gpd.read_file(zip_geo_path)
    print(f"✓ Loaded {len(gdf_zips)} zip codes")
    
    df_crime = load_local_crime_data()
    
    if df_crime.empty:
        print("✗ Failed to load crime data")
        print(f"Please ensure boston_crime.csv is in: {CRIME_DIR}/")
        return
    
    df_crime = clean_and_process_crime_data(df_crime)
    
    if df_crime.empty:
        print("✗ No valid crime data after cleaning")
        return
    
    gdf_crime = map_crimes_to_zipcodes(df_crime, gdf_zips)
    
    crime_scores = calculate_crime_scores(gdf_crime, gdf_zips)
    
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    output_detailed = CRIME_DIR / "crime_incidents_by_zipcode.csv"
    gdf_crime[['zip_code', 'OCCURRED_ON_DATE', 'OFFENSE_DESCRIPTION', 
                'crime_category', 'Lat', 'Long']].to_csv(output_detailed, index=False)
    print(f"\n✓ Saved detailed crime incidents: {output_detailed}")
    
    output_scores = CRIME_DIR / "crime_scores_by_zipcode.csv"
    score_columns = [
        'zip_code', 'total_crimes', 'violent_crimes', 'property_crimes', 
        'area_sq_mi', 'crimes_per_sq_mi', 'violent_per_sq_mi', 'property_per_sq_mi',
        'crime_score', 'violent_score', 'property_score', 'overall_crime_score'
    ]
    crime_scores[score_columns].to_csv(output_scores, index=False)
    print(f"✓ Saved crime scores: {output_scores}")
    
    print("\n" + "=" * 70)
    print("TOP 5 SAFEST ZIP CODES (Highest Crime Score)")
    print("=" * 70)
    top_5 = crime_scores.nlargest(5, 'overall_crime_score')[
        ['zip_code', 'total_crimes', 'violent_crimes', 'property_crimes', 'overall_crime_score']
    ]
    print(top_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("TOP 5 LEAST SAFE ZIP CODES (Lowest Crime Score)")
    print("=" * 70)
    bottom_5 = crime_scores.nsmallest(5, 'overall_crime_score')[
        ['zip_code', 'total_crimes', 'violent_crimes', 'property_crimes', 'overall_crime_score']
    ]
    print(bottom_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("STEP 2 COMPLETE ✓")
    print("=" * 70)
    print(f"\nProcessed crime data for {len(crime_scores)} zip codes")


if __name__ == "__main__":
    main()