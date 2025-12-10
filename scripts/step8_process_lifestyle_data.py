"""
Step 8: Process lifestyle data from Niche.com
Lifestyle = Nightlife + Health & Fitness + Outdoor Activities
Data source: Manually collected Niche.com grades
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
LIFESTYLE_DIR = DATA_DIR / "lifestyle"
LIFESTYLE_DIR.mkdir(exist_ok=True)

GRADE_TO_SCORE = {
    'A+': 10.0, 'A': 9.0, 'A-': 8.5,
    'B+': 7.5, 'B': 6.5, 'B-': 6.0,
    'C+': 5.0, 'C': 4.0, 'C-': 3.5,
    'D+': 2.5, 'D': 1.5, 'D-': 1.0,
    'F': 0.5, '-': None
}


def convert_grade_to_score(grade):
    """
    Convert letter grade to numeric score
    """
    if pd.isna(grade) or grade == '-':
        return None
    
    grade = str(grade).strip().upper()
    return GRADE_TO_SCORE.get(grade, None)


def load_niche_data():
    """
    Load manually collected Niche data
    """
    print("\n" + "=" * 70)
    print("LOADING NICHE DATA")
    print("=" * 70)
    
    niche_file = DATA_DIR / "niche_data.csv"
    
    if not niche_file.exists():
        print(f"✗ Error: {niche_file} not found")
        print("\nPlease save your Niche data as: data/niche_data.csv")
        print("Required columns: zip_code, nightlife, health, outdoor")
        return None
    
    try:
        df = pd.read_csv(niche_file)
        print(f"✓ Loaded Niche data for {len(df)} ZIP codes")
        
        df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)
        
        print(f"\nColumns found: {df.columns.tolist()}")
        
        required_cols = ['zip_code', 'nightlife', 'health', 'outdoor']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"✗ Missing columns: {missing_cols}")
            return None
        
        print("✓ Required columns present")
        
        return df
        
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return None


def process_lifestyle_data(df_niche):
    """
    Process lifestyle data
    Lifestyle = Nightlife + Health & Fitness + Outdoor Activities
    """
    print("\n" + "=" * 70)
    print("PROCESSING LIFESTYLE DATA")
    print("=" * 70)
    
    df_lifestyle = df_niche[['zip_code', 'nightlife', 'health', 'outdoor']].copy()
    
    print("\nConverting lifestyle grades to scores...")
    df_lifestyle['nightlife_score'] = df_lifestyle['nightlife'].apply(convert_grade_to_score)
    df_lifestyle['health_score'] = df_lifestyle['health'].apply(convert_grade_to_score)
    df_lifestyle['outdoor_score'] = df_lifestyle['outdoor'].apply(convert_grade_to_score)
    
    print(f"✓ Nightlife: {df_lifestyle['nightlife_score'].notna().sum()} valid scores")
    print(f"✓ Health & Fitness: {df_lifestyle['health_score'].notna().sum()} valid scores")
    print(f"✓ Outdoor Activities: {df_lifestyle['outdoor_score'].notna().sum()} valid scores")
    
    print("\nCalculating composite lifestyle scores...")
    
    lifestyle_scores = []
    
    for idx, row in df_lifestyle.iterrows():
        scores = [row['nightlife_score'], row['health_score'], row['outdoor_score']]
        valid_scores = [s for s in scores if pd.notna(s)]
        
        if len(valid_scores) > 0:
            lifestyle_scores.append(sum(valid_scores) / len(valid_scores))
        else:
            lifestyle_scores.append(None)
    
    df_lifestyle['overall_lifestyle_score'] = lifestyle_scores
    
    missing_count = df_lifestyle['overall_lifestyle_score'].isna().sum()
    if missing_count > 0:
        print(f"⚠ {missing_count} ZIP codes have no lifestyle data")
        special_zips = df_lifestyle[df_lifestyle['overall_lifestyle_score'].isna()]['zip_code'].tolist()
        print(f"  Special ZIPs (non-residential): {special_zips}")
    
    valid_count = df_lifestyle['overall_lifestyle_score'].notna().sum()
    print(f"✓ Calculated lifestyle scores for {valid_count} ZIP codes")
    
    print("\n" + "-" * 70)
    print("LIFESTYLE SCORE SUMMARY (Scale: 10 = Best, 0 = Worst)")
    print("-" * 70)
    
    df_valid = df_lifestyle[df_lifestyle['overall_lifestyle_score'].notna()]
    
    print(f"\nZIPs with lifestyle data: {len(df_valid)}")
    print(f"Average lifestyle score: {df_valid['overall_lifestyle_score'].mean():.2f} / 10")
    print(f"Highest score: {df_valid['overall_lifestyle_score'].max():.2f} (ZIP: {df_valid.loc[df_valid['overall_lifestyle_score'].idxmax(), 'zip_code']})")
    print(f"Lowest score:  {df_valid['overall_lifestyle_score'].min():.2f} (ZIP: {df_valid.loc[df_valid['overall_lifestyle_score'].idxmin(), 'zip_code']})")
    
    print(f"\nZip codes by lifestyle tier:")
    print(f"  Excellent (8.5-10.0): {(df_valid['overall_lifestyle_score'] >= 8.5).sum()}")
    print(f"  Good (6.5-8.4):       {((df_valid['overall_lifestyle_score'] >= 6.5) & (df_valid['overall_lifestyle_score'] < 8.5)).sum()}")
    print(f"  Average (5.0-6.4):    {((df_valid['overall_lifestyle_score'] >= 5.0) & (df_valid['overall_lifestyle_score'] < 6.5)).sum()}")
    print(f"  Below Average (0-4.9): {(df_valid['overall_lifestyle_score'] < 5.0).sum()}")
    
    print("\nComponent score averages:")
    print(f"  Nightlife: {df_lifestyle['nightlife_score'].mean():.2f} / 10")
    print(f"  Health & Fitness: {df_lifestyle['health_score'].mean():.2f} / 10")
    print(f"  Outdoor Activities: {df_lifestyle['outdoor_score'].mean():.2f} / 10")
    
    return df_lifestyle


def main():
    print("\n" + "=" * 70)
    print("STEP 8: COLLECT AND PROCESS LIFESTYLE DATA")
    print("=" * 70)
    
    df_niche = load_niche_data()
    
    if df_niche is None:
        print("\n✗ Cannot proceed without Niche data")
        return
    
    df_lifestyle = process_lifestyle_data(df_niche)
    
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    output_file = LIFESTYLE_DIR / "lifestyle_scores_by_zipcode.csv"
    output_columns = [
        'zip_code', 'nightlife', 'health', 'outdoor',
        'nightlife_score', 'health_score', 'outdoor_score', 'overall_lifestyle_score'
    ]
    df_lifestyle[output_columns].to_csv(output_file, index=False)
    print(f"\n✓ Saved lifestyle scores: {output_file}")
    
    print("\n" + "=" * 70)
    print("TOP 5 ZIP CODES BY LIFESTYLE")
    print("=" * 70)
    df_valid = df_lifestyle[df_lifestyle['overall_lifestyle_score'].notna()]
    top_5 = df_valid.nlargest(5, 'overall_lifestyle_score')[
        ['zip_code', 'nightlife', 'health', 'outdoor', 'overall_lifestyle_score']
    ]
    print(top_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("BOTTOM 5 ZIP CODES BY LIFESTYLE")
    print("=" * 70)
    bottom_5 = df_valid.nsmallest(5, 'overall_lifestyle_score')[
        ['zip_code', 'nightlife', 'health', 'outdoor', 'overall_lifestyle_score']
    ]
    print(bottom_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("STEP 8 COMPLETE ✓")
    print("=" * 70)
    print(f"\nProcessed lifestyle data for {len(df_lifestyle)} ZIP codes")


if __name__ == "__main__":
    main()