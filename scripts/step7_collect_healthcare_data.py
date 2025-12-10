"""
Step 7: Collect healthcare access data for Boston zip codes
Data source: Suffolk County hospitals CSV (from CMS data)
Measures: Distance to nearest hospital, density of hospitals within radius
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import numpy as np
from geopy.distance import geodesic

DATA_DIR = Path("data")
HEALTHCARE_DIR = DATA_DIR / "healthcare"
HEALTHCARE_DIR.mkdir(exist_ok=True)


def load_hospitals():
    """
    Load hospitals from Suffolk County hospitals CSV
    """
    print("\n" + "=" * 70)
    print("LOADING SUFFOLK COUNTY HOSPITALS")
    print("=" * 70)
    
    hospitals_file = HEALTHCARE_DIR / "suffolk_hospitals.csv"
    
    if not hospitals_file.exists():
        print(f"✗ Error: {hospitals_file} not found")
        print(f"\nPlease create the file with the following structure:")
        print("name,address,city,zip_code,lat,lon,tier,rating,hospital_type")
        print("\nSave it as: data/healthcare/suffolk_hospitals.csv")
        return None
    
    try:
        df_hospitals = pd.read_csv(hospitals_file)
        print(f"✓ Loaded {len(df_hospitals)} hospitals from CSV")
        
        # Validate required columns
        required_cols = ['name', 'lat', 'lon', 'tier']
        missing_cols = [col for col in required_cols if col not in df_hospitals.columns]
        
        if missing_cols:
            print(f"✗ Missing required columns: {missing_cols}")
            return None
        
        # Create GeoDataFrame
        gdf_hospitals = gpd.GeoDataFrame(
            df_hospitals,
            geometry=gpd.points_from_xy(df_hospitals.lon, df_hospitals.lat),
            crs='EPSG:4326'
        )
        
        print(f"\nBreakdown by tier:")
        tier_counts = gdf_hospitals['tier'].value_counts().sort_index()
        for tier, count in tier_counts.items():
            tier_name = {1: 'Major Teaching', 2: 'Community', 3: 'Specialty/Rehab'}.get(tier, f'Tier {tier}')
            print(f"  Tier {tier} ({tier_name}): {count}")
        
        return gdf_hospitals
        
    except Exception as e:
        print(f"✗ Error loading hospitals: {e}")
        return None


def calculate_zip_centroids(gdf_zips):
    """
    Calculate centroid (center point) of each ZIP code
    """
    print("\n" + "=" * 70)
    print("CALCULATING ZIP CODE CENTROIDS")
    print("=" * 70)
    
    gdf_zips = gdf_zips.to_crs('EPSG:4326')
    
    gdf_zips['centroid'] = gdf_zips.geometry.centroid
    gdf_zips['centroid_lat'] = gdf_zips['centroid'].y
    gdf_zips['centroid_lon'] = gdf_zips['centroid'].x
    
    print(f"✓ Calculated centroids for {len(gdf_zips)} ZIP codes")
    
    return gdf_zips


def calculate_healthcare_access(gdf_zips, gdf_hospitals):
    """
    Calculate healthcare access metrics for each ZIP code
    """
    print("\n" + "=" * 70)
    print("CALCULATING HEALTHCARE ACCESS METRICS")
    print("=" * 70)
    
    results = []
    
    for idx, zip_row in gdf_zips.iterrows():
        zip_code = zip_row['zip_code']
        zip_center = (zip_row['centroid_lat'], zip_row['centroid_lon'])
        
        distances = []
        tier1_distances = []
        
        for _, hosp_row in gdf_hospitals.iterrows():
            hosp_location = (hosp_row['lat'], hosp_row['lon'])
            distance = geodesic(zip_center, hosp_location).miles
            
            distances.append({
                'hospital': hosp_row['name'],
                'distance': distance,
                'tier': hosp_row['tier']
            })
            
            if hosp_row['tier'] == 1:
                tier1_distances.append(distance)
        
        nearest = min(distances, key=lambda x: x['distance'])
        nearest_tier1_dist = min(tier1_distances) if tier1_distances else None
        
        hospitals_within_2mi = sum(1 for d in distances if d['distance'] <= 2)
        hospitals_within_3mi = sum(1 for d in distances if d['distance'] <= 3)
        hospitals_within_5mi = sum(1 for d in distances if d['distance'] <= 5)
        tier1_within_5mi = sum(1 for d in distances if d['distance'] <= 5 and d['tier'] == 1)
        
        results.append({
            'zip_code': zip_code,
            'nearest_hospital': nearest['hospital'],
            'nearest_hospital_dist': nearest['distance'],
            'nearest_tier1_dist': nearest_tier1_dist,
            'hospitals_within_2mi': hospitals_within_2mi,
            'hospitals_within_3mi': hospitals_within_3mi,
            'hospitals_within_5mi': hospitals_within_5mi,
            'tier1_within_5mi': tier1_within_5mi
        })
    
    df_healthcare = pd.DataFrame(results)
    
    print(f"✓ Calculated access metrics for {len(df_healthcare)} ZIP codes")
    
    return df_healthcare


def calculate_healthcare_scores(df_healthcare):
    """
    Calculate healthcare access scores
    """
    print("\n" + "=" * 70)
    print("CALCULATING HEALTHCARE ACCESS SCORES")
    print("=" * 70)
    
    def normalize_and_invert_distance(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([5.0] * len(series), index=series.index)
        normalized = (series - min_val) / (max_val - min_val)
        return (1 - normalized) * 10
    
    def normalize_count(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([5.0] * len(series), index=series.index)
        return ((series - min_val) / (max_val - min_val)) * 10
    
    df_healthcare['nearest_hospital_score'] = normalize_and_invert_distance(
        df_healthcare['nearest_hospital_dist']
    )
    
    df_healthcare['nearest_tier1_score'] = normalize_and_invert_distance(
        df_healthcare['nearest_tier1_dist']
    )
    
    df_healthcare['density_score'] = normalize_count(
        df_healthcare['hospitals_within_5mi']
    )
    
    df_healthcare['tier1_access_score'] = normalize_count(
        df_healthcare['tier1_within_5mi']
    )
    
    df_healthcare['overall_healthcare_score'] = (
        df_healthcare['nearest_tier1_score'] * 0.40 +
        df_healthcare['nearest_hospital_score'] * 0.25 +
        df_healthcare['density_score'] * 0.20 +
        df_healthcare['tier1_access_score'] * 0.15
    )
    
    print("✓ Healthcare scores calculated")
    
    print("\n" + "-" * 70)
    print("HEALTHCARE ACCESS SUMMARY (Scale: 10 = Best Access, 0 = Worst)")
    print("-" * 70)
    print(f"\nAverage healthcare score: {df_healthcare['overall_healthcare_score'].mean():.2f} / 10")
    print(f"Best access:  {df_healthcare['overall_healthcare_score'].max():.2f} (ZIP: {df_healthcare.loc[df_healthcare['overall_healthcare_score'].idxmax(), 'zip_code']})")
    print(f"Worst access: {df_healthcare['overall_healthcare_score'].min():.2f} (ZIP: {df_healthcare.loc[df_healthcare['overall_healthcare_score'].idxmin(), 'zip_code']})")
    
    print(f"\nDistance to nearest hospital:")
    print(f"  Closest: {df_healthcare['nearest_hospital_dist'].min():.2f} miles (ZIP: {df_healthcare.loc[df_healthcare['nearest_hospital_dist'].idxmin(), 'zip_code']})")
    print(f"  Farthest: {df_healthcare['nearest_hospital_dist'].max():.2f} miles (ZIP: {df_healthcare.loc[df_healthcare['nearest_hospital_dist'].idxmax(), 'zip_code']})")
    
    print(f"\nZip codes by healthcare access tier:")
    print(f"  Excellent (8.0-10.0): {(df_healthcare['overall_healthcare_score'] >= 8.0).sum()}")
    print(f"  Good (6.0-7.9):       {((df_healthcare['overall_healthcare_score'] >= 6.0) & (df_healthcare['overall_healthcare_score'] < 8.0)).sum()}")
    print(f"  Average (4.0-5.9):    {((df_healthcare['overall_healthcare_score'] >= 4.0) & (df_healthcare['overall_healthcare_score'] < 6.0)).sum()}")
    print(f"  Below Avg (2.0-3.9):  {((df_healthcare['overall_healthcare_score'] >= 2.0) & (df_healthcare['overall_healthcare_score'] < 4.0)).sum()}")
    print(f"  Poor (0.0-1.9):       {(df_healthcare['overall_healthcare_score'] < 2.0).sum()}")
    
    return df_healthcare


def main():
    print("\n" + "=" * 70)
    print("STEP 7: COLLECT AND PROCESS HEALTHCARE ACCESS DATA")
    print("=" * 70)
    
    print("\nLoading Boston zip codes from Step 1...")
    zip_geo_path = DATA_DIR / "suffolk_zipcodes.geojson"
    
    if not zip_geo_path.exists():
        print(f"✗ Error: {zip_geo_path} not found")
        print("Please run step1_get_zipcode_boundaries.py first")
        return
    
    gdf_zips = gpd.read_file(zip_geo_path)
    print(f"✓ Loaded {len(gdf_zips)} zip codes")
    
    gdf_hospitals = load_hospitals()
    
    if gdf_hospitals is None:
        print("\n✗ Cannot proceed without hospital data")
        return
    
    gdf_zips = calculate_zip_centroids(gdf_zips)
    
    df_healthcare = calculate_healthcare_access(gdf_zips, gdf_hospitals)
    
    df_healthcare = calculate_healthcare_scores(df_healthcare)
    
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    output_file = HEALTHCARE_DIR / "healthcare_scores_by_zipcode.csv"
    output_columns = [
        'zip_code', 'nearest_hospital', 'nearest_hospital_dist', 'nearest_tier1_dist',
        'hospitals_within_2mi', 'hospitals_within_3mi', 'hospitals_within_5mi', 'tier1_within_5mi',
        'nearest_hospital_score', 'nearest_tier1_score', 'density_score', 
        'tier1_access_score', 'overall_healthcare_score'
    ]
    df_healthcare[output_columns].to_csv(output_file, index=False)
    print(f"\n✓ Saved healthcare scores: {output_file}")
    
    print("\n" + "=" * 70)
    print("TOP 5 ZIP CODES BY HEALTHCARE ACCESS")
    print("=" * 70)
    top_5 = df_healthcare.nlargest(5, 'overall_healthcare_score')[
        ['zip_code', 'nearest_hospital', 'nearest_hospital_dist', 'hospitals_within_5mi', 'overall_healthcare_score']
    ]
    print(top_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("BOTTOM 5 ZIP CODES BY HEALTHCARE ACCESS")
    print("=" * 70)
    bottom_5 = df_healthcare.nsmallest(5, 'overall_healthcare_score')[
        ['zip_code', 'nearest_hospital', 'nearest_hospital_dist', 'hospitals_within_5mi', 'overall_healthcare_score']
    ]
    print(bottom_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("STEP 7 COMPLETE ✓")
    print("=" * 70)
    print(f"\nProcessed healthcare data for {len(df_healthcare)} zip codes")
    print(f"Used {len(gdf_hospitals)} Suffolk County hospitals")
    print(f"\nRemaining steps:")


if __name__ == "__main__":
    main()