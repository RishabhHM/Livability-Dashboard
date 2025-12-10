"""
Step 4: Automatically collect transit access data for Boston zip codes
Data source: MBTA GTFS (General Transit Feed Specification)
"""

import pandas as pd
import geopandas as gpd
import requests
from pathlib import Path
import zipfile
import io
from tqdm import tqdm

DATA_DIR = Path("data")
TRANSIT_DIR = DATA_DIR / "transit"
TRANSIT_DIR.mkdir(exist_ok=True)

MBTA_GTFS_URL = "https://cdn.mbta.com/MBTA_GTFS.zip"


def download_mbta_gtfs():
    """
    Download MBTA GTFS data (all transit stops and routes)
    """
    print("\n" + "=" * 70)
    print("DOWNLOADING MBTA GTFS DATA")
    print("=" * 70)
    
    print(f"\nDownloading from: {MBTA_GTFS_URL}")
    
    try:
        response = requests.get(MBTA_GTFS_URL, stream=True, timeout=120)
        response.raise_for_status()
        
        total = int(response.headers.get('content-length', 0))
        
        zip_data = io.BytesIO()
        
        with tqdm(total=total, unit='B', unit_scale=True, desc='Downloading GTFS') as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    zip_data.write(chunk)
                    pbar.update(len(chunk))
        
        print("✓ Download complete")
        
        print("\nExtracting GTFS files...")
        with zipfile.ZipFile(zip_data) as z:
            z.extractall(TRANSIT_DIR / "gtfs")
        
        print(f"✓ Extracted to: {TRANSIT_DIR / 'gtfs'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error downloading GTFS: {e}")
        return False


def load_gtfs_stops():
    """
    Load MBTA stops from GTFS data
    """
    print("\n" + "=" * 70)
    print("LOADING MBTA TRANSIT STOPS")
    print("=" * 70)
    
    stops_file = TRANSIT_DIR / "gtfs" / "stops.txt"
    
    if not stops_file.exists():
        print(f"✗ File not found: {stops_file}")
        print("Please download GTFS data first")
        return pd.DataFrame()
    
    try:
        df_stops = pd.read_csv(stops_file)
        print(f"✓ Loaded {len(df_stops):,} transit stops")
        
        print(f"\nColumns: {df_stops.columns.tolist()}")
        
        # Filter for stations (exclude child stops)
        if 'location_type' in df_stops.columns:
            stations = df_stops[df_stops['location_type'] == 1]
            print(f"✓ Found {len(stations):,} stations (excluding sub-stops)")
            df_stops = stations
        
        # Show stop types if available
        if 'stop_name' in df_stops.columns:
            print(f"\nSample stops:")
            print(df_stops['stop_name'].head(10).tolist())
        
        return df_stops
        
    except Exception as e:
        print(f"✗ Error loading stops: {e}")
        return pd.DataFrame()


def load_gtfs_routes():
    """
    Load MBTA routes from GTFS data
    """
    print("\n" + "=" * 70)
    print("LOADING MBTA ROUTES")
    print("=" * 70)
    
    routes_file = TRANSIT_DIR / "gtfs" / "routes.txt"
    
    if not routes_file.exists():
        print(f"✗ File not found: {routes_file}")
        return pd.DataFrame()
    
    try:
        df_routes = pd.read_csv(routes_file)
        print(f"✓ Loaded {len(df_routes)} routes")
        
        # Categorize routes by type
        if 'route_type' in df_routes.columns:
            route_types = {
                0: 'Light Rail (Green Line)',
                1: 'Subway (Red, Orange, Blue)',
                2: 'Commuter Rail',
                3: 'Bus',
                4: 'Ferry'
            }
            
            print("\nRoute breakdown:")
            for route_type, count in df_routes['route_type'].value_counts().items():
                type_name = route_types.get(route_type, f'Type {route_type}')
                print(f"  {type_name}: {count}")
        
        return df_routes
        
    except Exception as e:
        print(f"✗ Error loading routes: {e}")
        return pd.DataFrame()


def map_stops_to_zipcodes(df_stops, gdf_zips):
    """
    Map transit stops to zip codes using spatial join
    """
    print("\n" + "=" * 70)
    print("MAPPING TRANSIT STOPS TO ZIP CODES")
    print("=" * 70)
    
    if 'stop_lat' not in df_stops.columns or 'stop_lon' not in df_stops.columns:
        print("✗ Missing latitude/longitude columns")
        return pd.DataFrame()
    
    print("\nCreating spatial points from stop coordinates...")
    gdf_stops = gpd.GeoDataFrame(
        df_stops,
        geometry=gpd.points_from_xy(df_stops.stop_lon, df_stops.stop_lat),
        crs='EPSG:4326'
    )
    print(f"✓ Created {len(gdf_stops):,} spatial points")
    
    print("\nAligning coordinate reference systems...")
    gdf_zips_aligned = gdf_zips.to_crs('EPSG:4326')
    
    print("Performing spatial join...")
    gdf_stops = gpd.sjoin(
        gdf_stops,
        gdf_zips_aligned[['zip_code', 'geometry']],
        how='left',
        predicate='within'
    )
    
    before = len(gdf_stops)
    gdf_stops_in_zips = gdf_stops.dropna(subset=['zip_code'])
    after = len(gdf_stops_in_zips)
    
    print(f"✓ Mapped {after:,} stops to zip codes")
    print(f"  ({before - after:,} stops outside target zip codes)")
    
    return gdf_stops_in_zips


def calculate_transit_scores(gdf_stops, gdf_zips):
    """
    Calculate transit access scores for each zip code
    """
    print("\n" + "=" * 70)
    print("CALCULATING TRANSIT ACCESS SCORES")
    print("=" * 70)
    
    print("\nAggregating transit stops by zip code...")
    
    transit_stats = gdf_stops.groupby('zip_code').agg({
        'stop_id': 'count',
        'stop_name': lambda x: list(x.unique())
    }).rename(columns={
        'stop_id': 'total_stops',
        'stop_name': 'stop_names'
    })
    
    print(f"✓ Aggregated data for {len(transit_stats)} zip codes with transit")
    
    # Check for missing zip codes
    all_zips = set(gdf_zips['zip_code'].unique())
    zips_with_transit = set(transit_stats.index)
    missing_zips = all_zips - zips_with_transit
    
    if missing_zips:
        print(f"\n⚠ {len(missing_zips)} zip codes have NO transit stops:")
        print(f"  Missing ZIPs: {sorted(list(missing_zips))}")
        
        for zip_code in missing_zips:
            transit_stats.loc[zip_code] = {
                'total_stops': 0,
                'stop_names': []
            }
        print(f"✓ Added missing zip codes with 0 stops")
    
    transit_stats = transit_stats.merge(
        gdf_zips[['zip_code', 'area_sq_mi']].drop_duplicates('zip_code'),
        on='zip_code',
        how='right'
    )
    
    transit_stats['total_stops'] = transit_stats['total_stops'].fillna(0).astype(int)
    
    # Calculate stop density
    transit_stats['stops_per_sq_mi'] = transit_stats['total_stops'] / transit_stats['area_sq_mi']
    
    print("\nNormalizing transit scores to 0-10 scale...")
    
    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series([5.0] * len(series), index=series.index)
        return ((series - min_val) / (max_val - min_val)) * 10
    
    transit_stats['transit_score'] = normalize(transit_stats['total_stops'])
    transit_stats['transit_density_score'] = normalize(transit_stats['stops_per_sq_mi'])
    
    # Overall transit score: average of count and density
    transit_stats['overall_transit_score'] = (
        transit_stats['transit_score'] * 0.6 +
        transit_stats['transit_density_score'] * 0.4
    )
    
    print("✓ Transit scores calculated")
    
    print("\n" + "-" * 70)
    print("TRANSIT SCORE SUMMARY (Scale: 10 = Best Access, 0 = Worst)")
    print("-" * 70)
    print(f"\nTotal zip codes processed: {len(transit_stats)}")
    print(f"Zip codes with transit: {len(zips_with_transit)}")
    print(f"Zip codes without transit: {len(missing_zips)}")
    print(f"\nAverage transit score: {transit_stats['overall_transit_score'].mean():.2f} / 10")
    print(f"Best access:  {transit_stats['overall_transit_score'].max():.2f} (ZIP: {transit_stats['overall_transit_score'].idxmax()})")
    print(f"Worst access: {transit_stats['overall_transit_score'].min():.2f} (ZIP: {transit_stats['overall_transit_score'].idxmin()})")
    
    print(f"\nTransit stop range:")
    print(f"  Most stops:  {transit_stats['total_stops'].max():.0f} stops (ZIP: {transit_stats['total_stops'].idxmax()})")
    print(f"  Least stops: {transit_stats['total_stops'].min():.0f} stops (ZIP: {transit_stats['total_stops'].idxmin()})")
    
    print(f"\nZip codes by transit access tier:")
    print(f"  Excellent (8.0-10.0): {(transit_stats['overall_transit_score'] >= 8.0).sum()}")
    print(f"  Good (6.0-7.9):       {((transit_stats['overall_transit_score'] >= 6.0) & (transit_stats['overall_transit_score'] < 8.0)).sum()}")
    print(f"  Average (4.0-5.9):    {((transit_stats['overall_transit_score'] >= 4.0) & (transit_stats['overall_transit_score'] < 6.0)).sum()}")
    print(f"  Below Avg (2.0-3.9):  {((transit_stats['overall_transit_score'] >= 2.0) & (transit_stats['overall_transit_score'] < 4.0)).sum()}")
    print(f"  Poor (0.0-1.9):       {(transit_stats['overall_transit_score'] < 2.0).sum()}")
    
    transit_stats = transit_stats.reset_index()
    
    return transit_stats


def main():
    print("\n" + "=" * 70)
    print("STEP 4: COLLECT AND PROCESS TRANSIT DATA")
    print("=" * 70)
    
    print("\nLoading Boston zip codes from Step 1...")
    zip_geo_path = DATA_DIR / "suffolk_zipcodes.geojson"
    
    if not zip_geo_path.exists():
        print(f"✗ Error: {zip_geo_path} not found")
        print("Please run step1_get_zipcode_boundaries.py first")
        return
    
    gdf_zips = gpd.read_file(zip_geo_path)
    print(f"✓ Loaded {len(gdf_zips)} zip codes")
    
    # Download GTFS data
    gtfs_exists = (TRANSIT_DIR / "gtfs" / "stops.txt").exists()
    
    if not gtfs_exists:
        print("\nGTFS data not found. Downloading...")
        success = download_mbta_gtfs()
        if not success:
            print("\n✗ Failed to download GTFS data")
            return
    else:
        print("\n✓ GTFS data already downloaded")
    
    # Load transit data
    df_stops = load_gtfs_stops()
    if df_stops.empty:
        print("✗ No transit stops loaded")
        return
    
    df_routes = load_gtfs_routes()
    
    # Map stops to zip codes
    gdf_stops = map_stops_to_zipcodes(df_stops, gdf_zips)
    
    if gdf_stops.empty:
        print("✗ No stops mapped to zip codes")
        return
    
    # Calculate scores
    transit_scores = calculate_transit_scores(gdf_stops, gdf_zips)
    
    # Save outputs
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    output_stops = TRANSIT_DIR / "transit_stops_by_zipcode.csv"
    gdf_stops[['zip_code', 'stop_id', 'stop_name', 'stop_lat', 'stop_lon']].to_csv(output_stops, index=False)
    print(f"\n✓ Saved transit stops: {output_stops}")
    
    output_scores = TRANSIT_DIR / "transit_scores_by_zipcode.csv"
    score_columns = [
        'zip_code', 'total_stops', 'area_sq_mi', 'stops_per_sq_mi',
        'transit_score', 'transit_density_score', 'overall_transit_score'
    ]
    transit_scores[score_columns].to_csv(output_scores, index=False)
    print(f"✓ Saved transit scores: {output_scores}")
    
    print("\n" + "=" * 70)
    print("TOP 5 ZIP CODES BY TRANSIT ACCESS")
    print("=" * 70)
    top_5 = transit_scores.nlargest(5, 'overall_transit_score')[
        ['zip_code', 'total_stops', 'stops_per_sq_mi', 'overall_transit_score']
    ]
    print(top_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("BOTTOM 5 ZIP CODES BY TRANSIT ACCESS")
    print("=" * 70)
    bottom_5 = transit_scores.nsmallest(5, 'overall_transit_score')[
        ['zip_code', 'total_stops', 'stops_per_sq_mi', 'overall_transit_score']
    ]
    print(bottom_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("STEP 4 COMPLETE ✓")
    print("=" * 70)
    print(f"\nProcessed transit data for {len(transit_scores)} zip codes")

if __name__ == "__main__":
    main()