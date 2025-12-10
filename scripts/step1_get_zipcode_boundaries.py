"""
Step 1: Automatically fetch Boston zip code boundaries
No manual data entry - fully automated
"""

import pandas as pd
import geopandas as gpd
import requests
import zipfile
import io
from pathlib import Path
from tqdm import tqdm

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
ZIP_SHAPE_URL = "https://www2.census.gov/geo/tiger/TIGER2025/ZCTA520/tl_2025_us_zcta520.zip"


def fetch_census_zctas():
    """Download and load US Census ZCTA boundaries (2025)."""
    print("\n" + "=" * 70)
    print("FETCHING US CENSUS ZCTA BOUNDARIES (2025)")
    print("=" * 70)
    
    url = ZIP_SHAPE_URL
    raw_dir = DATA_DIR / "raw_zcta"
    raw_dir.mkdir(exist_ok=True)

    print(f"\n[1/3] Downloading ZCTA shapefile...")
    print(f"Source: {url}")
    
    # ---- Download Spatial File With Progress Bar ----
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))

        download_path = raw_dir / "zcta.zip"

        with open(download_path, "wb") as f, tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            desc="Downloading ZCTA shapefile"
        ) as pbar:

            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
    
    print("✓ Download complete")

    # ---- Extract ZIP File with Progress Bar ----
    print(f"\n[2/3] Extracting ZCTA files...")
    with zipfile.ZipFile(download_path, "r") as z:
        members = z.infolist()
        for member in tqdm(members, desc="Extracting ZCTA files"):
            z.extract(member, raw_dir)
    
    print("✓ Extraction complete")

    print(f"\n[3/3] Reading shapefile and filtering for Boston area (02xxx)...")
    shp = raw_dir / "tl_2025_us_zcta520.shp"
    gdf = gpd.read_file(shp)

    # Boston ZIPs start with 02xxx
    gdf = gdf[gdf["ZCTA5CE20"].str.startswith("02")].copy()
    gdf = gdf.rename(columns={"ZCTA5CE20": "zip_code"})

    # calculate area in sq miles
    gdf["area_sq_mi"] = gdf.to_crs(epsg=3857).area / 2.59e6
    
    print(f"✓ Found {len(gdf)} zip codes starting with '02'")

    return gdf[["zip_code", "area_sq_mi", "geometry"]]

def filter_suffolk_county_data():
    """Filter ZCTA data for Suffolk County (core Boston) zip codes."""
    print("\n" + "=" * 70)
    print("STEP 1: GET BOSTON ZIP CODE BOUNDARIES")
    print("=" * 70)
    
    gdf = fetch_census_zctas()

    print("\n" + "=" * 70)
    print("FILTERING FOR SUFFOLK COUNTY ZIP CODES")
    print("=" * 70)
    
    print(f"\nReading Suffolk County ZIP codes from: {DATA_DIR / 'suffolk_county_zip.csv'}")
    zip_df = pd.read_csv(DATA_DIR / "suffolk_county_zip.csv")
    zip_df = zip_df.loc[zip_df['Type'] == 'Standard', :]
    
    print(f"✓ Found {len(zip_df)} Standard ZIP codes in Suffolk County")
    
    # Extract Area ZIP codes as strings
    core_zips = set(zip_df["ZIP Code"].astype(str).str.zfill(5))
    
    print(f"\nFiltering ZCTA data for {len(core_zips)} core Boston ZIP codes...")

    # Filter GeoDataFrame using Area ZIP codes from CSV
    gdf_core = gdf[gdf["zip_code"].isin(core_zips)].copy()
    
    print(f"✓ Matched {len(gdf_core)} ZIP codes with spatial boundaries")

    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    # Geometric Output
    output_geojson = DATA_DIR / "suffolk_zipcodes.geojson"
    gdf_core.to_file(output_geojson, driver="GeoJSON")
    print(f"\n✓ Saved GeoJSON with geometry: {output_geojson}")

    # Non-Geometric Output
    output_csv = DATA_DIR / "suffolk_zipcodes_info.csv"
    gdf_core[["zip_code", "area_sq_mi"]].to_csv(output_csv, index=False)
    print(f"✓ Saved CSV with basic info: {output_csv}")

    print("\n" + "=" * 70)
    print("DATA SUMMARY")
    print("=" * 70)
    print(f"\nTotal ZIPs in Boston area (02xxx):    {len(gdf)}")
    print(f"Core Boston ZIPs (Suffolk County):     {len(gdf_core)}")
    print(f"Average area per ZIP:                  {gdf_core['area_sq_mi'].mean():.2f} sq mi")
    print(f"ZIP code range:                        {gdf_core['zip_code'].min()} - {gdf_core['zip_code'].max()}")
    
    print("\nCore Boston ZIP codes:")
    zip_list = sorted(gdf_core['zip_code'].tolist())
    for i in range(0, len(zip_list), 5):
        print("  " + ", ".join(zip_list[i:i+5]))
    
    print("\n" + "=" * 70)
    print("STEP 1 COMPLETE ✓")
    print("=" * 70)


if __name__ == "__main__":
    filter_suffolk_county_data()