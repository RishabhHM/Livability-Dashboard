"""
Step 9: Merge all collected data into final datasets for Tableau
Output 1: GeoJSON with all scores (for mapping)
Output 2: CSV with summary statistics (for charts/tables)
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path

DATA_DIR = Path("data")
OUTPUT_DIR = DATA_DIR / "processed"
TABLEAU_DIR = Path("outputs") / "tableau_data"
OUTPUT_DIR.mkdir(exist_ok=True)
TABLEAU_DIR.mkdir(exist_ok=True)


def load_all_scores():
    """
    Load all score datasets from previous steps
    """
    print("\n" + "=" * 70)
    print("LOADING ALL SCORE DATASETS")
    print("=" * 70)
    
    datasets = {}
    
    # Step 1: ZIP codes (base)
    print("\n[1/7] Loading ZIP code boundaries...")
    zip_file = DATA_DIR / "suffolk_zipcodes.geojson"
    if zip_file.exists():
        datasets['zips'] = gpd.read_file(zip_file)
        print(f"✓ Loaded {len(datasets['zips'])} ZIP codes")
    else:
        print(f"✗ Missing: {zip_file}")
        return None
    
    # Step 2: Crime scores
    print("\n[2/7] Loading crime scores...")
    crime_file = DATA_DIR / "crime" / "crime_scores_by_zipcode.csv"
    if crime_file.exists():
        datasets['crime'] = pd.read_csv(crime_file)
        datasets['crime']['zip_code'] = datasets['crime']['zip_code'].astype(str).str.zfill(5)
        print(f"✓ Loaded crime scores for {len(datasets['crime'])} ZIP codes")
    else:
        print(f"✗ Missing: {crime_file}")
        return None
    
    # Step 3: School scores
    print("\n[3/7] Loading school scores...")
    school_file = DATA_DIR / "schools" / "school_scores_by_zipcode.csv"
    if school_file.exists():
        datasets['schools'] = pd.read_csv(school_file)
        datasets['schools']['zip_code'] = datasets['schools']['zip_code'].astype(str).str.zfill(5)
        print(f"✓ Loaded school scores for {len(datasets['schools'])} ZIP codes")
    else:
        print(f"✗ Missing: {school_file}")
        return None
    
    # Step 4: Transit scores
    print("\n[4/7] Loading transit scores...")
    transit_file = DATA_DIR / "transit" / "transit_scores_by_zipcode.csv"
    if transit_file.exists():
        datasets['transit'] = pd.read_csv(transit_file)
        datasets['transit']['zip_code'] = datasets['transit']['zip_code'].astype(str).str.zfill(5)
        print(f"✓ Loaded transit scores for {len(datasets['transit'])} ZIP codes")
    else:
        print(f"✗ Missing: {transit_file}")
        return None
    
    # Step 5: Housing scores
    print("\n[5/7] Loading housing scores...")
    housing_file = DATA_DIR / "housing" / "housing_scores_by_zipcode.csv"
    if housing_file.exists():
        datasets['housing'] = pd.read_csv(housing_file)
        datasets['housing']['zip_code'] = datasets['housing']['zip_code'].astype(str).str.zfill(5)
        print(f"✓ Loaded housing scores for {len(datasets['housing'])} ZIP codes")
    else:
        print(f"✗ Missing: {housing_file}")
        return None
    
    # Step 6: Diversity scores
    print("\n[6/7] Loading diversity scores...")
    diversity_file = DATA_DIR / "diversity" / "diversity_scores_by_zipcode.csv"
    if diversity_file.exists():
        datasets['diversity'] = pd.read_csv(diversity_file)
        datasets['diversity']['zip_code'] = datasets['diversity']['zip_code'].astype(str).str.zfill(5)
        print(f"✓ Loaded diversity scores for {len(datasets['diversity'])} ZIP codes")
    else:
        print(f"✗ Missing: {diversity_file}")
        return None
    
    # Step 7: Healthcare scores
    print("\n[7/7] Loading healthcare scores...")
    healthcare_file = DATA_DIR / "healthcare" / "healthcare_scores_by_zipcode.csv"
    if healthcare_file.exists():
        datasets['healthcare'] = pd.read_csv(healthcare_file)
        datasets['healthcare']['zip_code'] = datasets['healthcare']['zip_code'].astype(str).str.zfill(5)
        print(f"✓ Loaded healthcare scores for {len(datasets['healthcare'])} ZIP codes")
    else:
        print(f"✗ Missing: {healthcare_file}")
        return None
    
    # Step 8: Lifestyle scores
    print("\n[8/8] Loading lifestyle scores...")
    lifestyle_file = DATA_DIR / "lifestyle" / "lifestyle_scores_by_zipcode.csv"
    if lifestyle_file.exists():
        datasets['lifestyle'] = pd.read_csv(lifestyle_file)
        datasets['lifestyle']['zip_code'] = datasets['lifestyle']['zip_code'].astype(str).str.zfill(5)
        print(f"✓ Loaded lifestyle scores for {len(datasets['lifestyle'])} ZIP codes")
    else:
        print(f"✗ Missing: {lifestyle_file}")
        return None
    
    print("\n✓ All datasets loaded successfully")
    
    return datasets


def merge_all_data(datasets):
    """
    Merge all datasets into single dataframe
    """
    print("\n" + "=" * 70)
    print("MERGING ALL DATASETS")
    print("=" * 70)
    
    # Start with ZIP codes as base
    gdf = datasets['zips'].copy()
    gdf['zip_code'] = gdf['zip_code'].astype(str).str.zfill(5)
    
    print(f"\nStarting with {len(gdf)} ZIP codes")
    print(f"Sample ZIP codes: {gdf['zip_code'].head().tolist()}")
    
    # Ensure all datasets have string zip_code with leading zeros
    for dataset_name in ['crime', 'schools', 'transit', 'housing', 'diversity', 'healthcare', 'lifestyle']:
        if dataset_name in datasets:
            datasets[dataset_name]['zip_code'] = datasets[dataset_name]['zip_code'].astype(str).str.zfill(5)
    
    # Merge crime scores
    print("\n[1/7] Merging crime scores...")
    crime_cols = ['zip_code', 'total_crimes', 'violent_crimes', 'property_crimes', 'overall_crime_score']
    gdf = gdf.merge(datasets['crime'][crime_cols], on='zip_code', how='left')
    matched = gdf['overall_crime_score'].notna().sum()
    print(f"✓ Merged crime data - {matched} ZIPs matched")
    
    # Merge school scores
    print("[2/7] Merging school scores...")
    school_cols = ['zip_code', 'school_grade', 'school_score']
    gdf = gdf.merge(datasets['schools'][school_cols], on='zip_code', how='left')
    matched = gdf['school_score'].notna().sum()
    print(f"✓ Merged school data - {matched} ZIPs matched")
    
    # Merge transit scores
    print("[3/7] Merging transit scores...")
    transit_cols = ['zip_code', 'total_stops', 'overall_transit_score']
    gdf = gdf.merge(datasets['transit'][transit_cols], on='zip_code', how='left')
    matched = gdf['overall_transit_score'].notna().sum()
    print(f"✓ Merged transit data - {matched} ZIPs matched")
    
    # Merge housing scores
    print("[4/7] Merging housing scores...")
    housing_cols = ['zip_code', 'median_home_value', 'median_rent', 'overall_housing_score']
    gdf = gdf.merge(datasets['housing'][housing_cols], on='zip_code', how='left')
    matched = gdf['overall_housing_score'].notna().sum()
    print(f"✓ Merged housing data - {matched} ZIPs matched")
    
    # Merge diversity scores
    print("[5/7] Merging diversity scores...")
    diversity_cols = ['zip_code', 'total_pop', 'pct_white', 'pct_black', 'pct_asian', 'diversity_score']
    gdf = gdf.merge(datasets['diversity'][diversity_cols], on='zip_code', how='left')
    matched = gdf['diversity_score'].notna().sum()
    print(f"✓ Merged diversity data - {matched} ZIPs matched")
    
    # Merge healthcare scores
    print("[6/7] Merging healthcare scores...")
    healthcare_cols = ['zip_code', 'nearest_hospital', 'nearest_hospital_dist', 
                       'hospitals_within_2mi', 'hospitals_within_5mi', 'overall_healthcare_score']
    gdf = gdf.merge(datasets['healthcare'][healthcare_cols], on='zip_code', how='left')
    matched = gdf['overall_healthcare_score'].notna().sum()
    print(f"✓ Merged healthcare data - {matched} ZIPs matched")
    
    # Merge lifestyle scores
    print("[7/7] Merging lifestyle scores...")
    lifestyle_cols = ['zip_code', 'nightlife', 'health', 'outdoor', 'overall_lifestyle_score']
    gdf = gdf.merge(datasets['lifestyle'][lifestyle_cols], on='zip_code', how='left')
    matched = gdf['overall_lifestyle_score'].notna().sum()
    print(f"✓ Merged lifestyle data - {matched} ZIPs matched")
    
    print(f"\n✓ Final dataset has {len(gdf)} ZIP codes with {len(gdf.columns)} columns")
    
    # Check for merge issues
    missing_scores = gdf[gdf['overall_crime_score'].isna()]['zip_code'].tolist()
    if missing_scores:
        print(f"\n⚠ WARNING: {len(missing_scores)} ZIP codes missing crime scores:")
        print(f"  {missing_scores}")
    
    return gdf


def calculate_composite_score(gdf):
    """
    Calculate final composite livability score
    Handle missing values by adjusting weights proportionally
    """
    print("\n" + "=" * 70)
    print("CALCULATING COMPOSITE LIVABILITY SCORES")
    print("=" * 70)
    
    print("\nBase weights:")
    print("  Crime:      22.5%")
    print("  Lifestyle:  17%")
    print("  Schools:    15%")
    print("  Transit:    15%")
    print("  Healthcare: 13%")
    print("  Housing:    10%")
    print("  Diversity:  7.5%")
    
    # Define weights
    weights = {
        'overall_crime_score': 0.225,
        'overall_lifestyle_score': 0.17,
        'school_score': 0.15,
        'overall_transit_score': 0.15,
        'overall_healthcare_score': 0.13,
        'overall_housing_score': 0.10,
        'diversity_score': 0.075
    }
    
    print("\nCalculating composite scores with adjusted weights for missing data...")
    
    composite_scores = []
    
    for idx, row in gdf.iterrows():
        weighted_sum = 0
        total_weight = 0
        
        # Only use available scores and their weights
        for col, weight in weights.items():
            score = row.get(col)
            if pd.notna(score):
                weighted_sum += score * weight
                total_weight += weight
        
        # Adjust to 0-10 scale by normalizing weights
        if total_weight > 0:
            composite = weighted_sum / total_weight * sum(weights.values())
            composite_scores.append(composite)
        else:
            composite_scores.append(None)
    
    gdf['composite_score'] = composite_scores
    
    # Classify into tiers
    def classify_tier(score):
        if pd.isna(score):
            return 'No Data'
        elif score >= 8.0:
            return 'Excellent'
        elif score >= 7.0:
            return 'Good'
        elif score >= 6.0:
            return 'Average'
        elif score >= 4.0:
            return 'Below Average'
        else:
            return 'Poor'
    
    gdf['tier'] = gdf['composite_score'].apply(classify_tier)
    
    print("✓ Composite scores calculated")
    
    # Summary
    df_valid = gdf[gdf['composite_score'].notna()]
    
    print("\n" + "-" * 70)
    print("COMPOSITE SCORE SUMMARY (Scale: 10 = Best, 0 = Worst)")
    print("-" * 70)
    print(f"\nZIPs with complete data: {len(df_valid)}")
    print(f"Average composite score: {df_valid['composite_score'].mean():.2f} / 10")
    print(f"Highest score: {df_valid['composite_score'].max():.2f} (ZIP: {df_valid.loc[df_valid['composite_score'].idxmax(), 'zip_code']})")
    print(f"Lowest score:  {df_valid['composite_score'].min():.2f} (ZIP: {df_valid.loc[df_valid['composite_score'].idxmin(), 'zip_code']})")
    
    # Check for scores > 10 (should not happen)
    over_10 = df_valid[df_valid['composite_score'] > 10]
    if len(over_10) > 0:
        print(f"\n⚠ WARNING: {len(over_10)} ZIP codes have composite score > 10:")
        for _, row in over_10.iterrows():
            print(f"  ZIP {row['zip_code']}: {row['composite_score']:.2f}")
    
    print(f"\nDistribution by tier:")
    tier_counts = gdf['tier'].value_counts()
    for tier in ['Excellent', 'Good', 'Average', 'Below Average', 'Poor', 'No Data']:
        count = tier_counts.get(tier, 0)
        if count > 0:
            print(f"  {tier:15s}: {count}")
    
    return gdf


def create_final_datasets(gdf):
    """
    Create final CSV for Tableau (GeoJSON already exists from Step 1)
    """
    print("\n" + "=" * 70)
    print("CREATING FINAL DATASET FOR TABLEAU")
    print("=" * 70)
    
    print("\nNote: Using existing suffolk_zipcodes.geojson from Step 1")
    print("This CSV will be joined with the GeoJSON in Tableau using zip_code")
    
    # Dataset: CSV summary statistics (no geometry)
    print("\n[Dataset 1] Creating CSV summary with all scores...")
    
    summary_cols = [
        'zip_code', 'area_sq_mi',
        'overall_crime_score', 'school_score', 'overall_transit_score',
        'overall_housing_score', 'diversity_score', 'overall_healthcare_score',
        'overall_lifestyle_score', 'composite_score', 'tier',
        'total_crimes', 'violent_crimes', 'property_crimes',
        'school_grade', 'total_stops',
        'median_home_value', 'median_rent', 'median_household_income',
        'total_pop', 'pct_white', 'pct_black', 'pct_asian',
        'nearest_hospital', 'nearest_hospital_dist', 'hospitals_within_2mi',
        'hospitals_within_3mi', 'hospitals_within_5mi',
        'nightlife', 'health', 'outdoor'
    ]
    
    available_cols = [col for col in summary_cols if col in gdf.columns]
    df_summary = gdf[available_cols].copy()
    
    if 'geometry' in df_summary.columns:
        df_summary = df_summary.drop(columns=['geometry'])
    
    output_csv = TABLEAU_DIR / "suffolk_livability_summary.csv"
    df_summary.to_csv(output_csv, index=False)
    print(f"✓ Saved CSV summary: {output_csv}")
    print(f"  Columns: {len(available_cols)}")
    print(f"  ZIP codes: {len(df_summary)}")
    
    # Dataset 2: Scores only (simplified)
    print("\n[Dataset 2] Creating simplified scores CSV...")
    
    scores_only_cols = [
        'zip_code', 'composite_score', 'tier',
        'overall_crime_score', 'school_score', 'overall_transit_score',
        'overall_housing_score', 'diversity_score', 'overall_healthcare_score',
        'overall_lifestyle_score'
    ]
    
    available_scores_cols = [col for col in scores_only_cols if col in gdf.columns]
    df_scores = gdf[available_scores_cols].copy()
    
    if 'geometry' in df_scores.columns:
        df_scores = df_scores.drop(columns=['geometry'])
    
    output_scores = TABLEAU_DIR / "suffolk_scores_only.csv"
    df_scores.to_csv(output_scores, index=False)
    print(f"✓ Saved scores-only CSV: {output_scores}")
    print(f"  Columns: {len(available_scores_cols)}")
    print(f"  ZIP codes: {len(df_scores)}")
    
    print("\n" + "-" * 70)
    print("TABLEAU WORKFLOW")
    print("-" * 70)
    print("\n1. Import: data/suffolk_zipcodes.geojson (for map)")
    print("2. Import: outputs/tableau_data/suffolk_livability_summary.csv (for data)")
    print("3. Join on: zip_code field")
    print("4. Create visualizations using merged data")
    
    return df_summary, df_scores


def main():
    print("\n" + "=" * 70)
    print("STEP 9: MERGE ALL DATA INTO FINAL DATASETS")
    print("=" * 70)
    
    # Load all datasets
    datasets = load_all_scores()
    
    if datasets is None:
        print("\n✗ Failed to load all required datasets")
        print("Please ensure all previous steps (1-8) have been completed")
        return
    
    # Merge everything
    gdf_merged = merge_all_data(datasets)
    
    # Calculate composite scores
    gdf_final = calculate_composite_score(gdf_merged)
    
    # Create final output files
    df_summary, df_scores = create_final_datasets(gdf_final)
    
    # Create data dictionary
    create_data_dictionary()
    
    # Display final rankings
    print("\n" + "=" * 70)
    print("TOP 10 ZIP CODES BY COMPOSITE LIVABILITY SCORE")
    print("=" * 70)
    
    df_valid = gdf_final[gdf_final['composite_score'].notna()].copy()
    if 'geometry' in df_valid.columns:
        df_valid = df_valid.drop(columns=['geometry'])
    
    top_10 = df_valid.nlargest(10, 'composite_score')[
        ['zip_code', 'composite_score', 'tier', 'overall_crime_score', 'school_score', 
         'overall_transit_score', 'overall_housing_score']
    ]
    print(top_10.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("BOTTOM 5 ZIP CODES BY COMPOSITE LIVABILITY SCORE")
    print("=" * 70)
    bottom_5 = df_valid.nsmallest(5, 'composite_score')[
        ['zip_code', 'composite_score', 'tier', 'overall_crime_score', 'school_score',
         'overall_transit_score', 'overall_housing_score']
    ]
    print(bottom_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("STEP 9 COMPLETE ✓")
    print("=" * 70)
    print(f"\nFinal datasets created:")
    print(f"  1. {TABLEAU_DIR / 'suffolk_livability_scores.geojson'}")
    print(f"  2. {TABLEAU_DIR / 'suffolk_livability_summary.csv'}")
    print(f"  3. {TABLEAU_DIR / 'suffolk_scores_only.csv'}")
    print(f"  4. {TABLEAU_DIR / 'DATA_DICTIONARY.txt'}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()