"""
Step 3: Process school quality data from Niche.com
Data source: Manually collected Niche.com Public Schools grades
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
SCHOOL_DIR = DATA_DIR / "schools"
SCHOOL_DIR.mkdir(exist_ok=True)

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
        print("Required columns: zip_code, school, nightlife, health, outdoor")
        return None
    
    try:
        df = pd.read_csv(niche_file)
        print(f"✓ Loaded Niche data for {len(df)} ZIP codes")
        
        df['zip_code'] = df['zip_code'].astype(str).str.zfill(5)
        
        print(f"\nColumns found: {df.columns.tolist()}")
        
        required_cols = ['zip_code', 'school']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"✗ Missing columns: {missing_cols}")
            return None
        
        print("✓ Required columns present")
        
        return df
        
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return None


def process_school_data(df_niche):
    """
    Process school quality data
    """
    print("\n" + "=" * 70)
    print("PROCESSING SCHOOL QUALITY DATA")
    print("=" * 70)
    
    df_schools = df_niche[['zip_code', 'school']].copy()
    df_schools = df_schools.rename(columns={'school': 'school_grade'})
    
    print("\nConverting school grades to scores...")
    df_schools['school_score'] = df_schools['school_grade'].apply(convert_grade_to_score)
    
    missing_count = df_schools['school_score'].isna().sum()
    if missing_count > 0:
        print(f"⚠ {missing_count} ZIP codes have no school data")
        special_zips = df_schools[df_schools['school_score'].isna()]['zip_code'].tolist()
        print(f"  Special ZIPs (non-residential): {special_zips}")
    
    valid_count = df_schools['school_score'].notna().sum()
    print(f"✓ Converted {valid_count} school grades to scores")
    
    print("\n" + "-" * 70)
    print("SCHOOL SCORE SUMMARY (Scale: 10 = Best, 0 = Worst)")
    print("-" * 70)
    
    df_valid = df_schools[df_schools['school_score'].notna()]
    
    print(f"\nZIPs with school data: {len(df_valid)}")
    print(f"Average school score: {df_valid['school_score'].mean():.2f} / 10")
    print(f"Highest score: {df_valid['school_score'].max():.2f} (ZIP: {df_valid.loc[df_valid['school_score'].idxmax(), 'zip_code']})")
    print(f"Lowest score:  {df_valid['school_score'].min():.2f} (ZIP: {df_valid.loc[df_valid['school_score'].idxmin(), 'zip_code']})")
    
    print("\nGrade distribution:")
    grade_counts = df_schools['school_grade'].value_counts().sort_index()
    for grade, count in grade_counts.items():
        score = GRADE_TO_SCORE.get(grade, 'N/A')
        print(f"  {grade:3s} ({score}): {count}")
    
    print(f"\nZip codes by school quality tier:")
    print(f"  Excellent (A-range, 8.5-10.0): {(df_valid['school_score'] >= 8.5).sum()}")
    print(f"  Good (B-range, 6.0-8.4):       {((df_valid['school_score'] >= 6.0) & (df_valid['school_score'] < 8.5)).sum()}")
    print(f"  Average (C-range, 3.5-5.9):    {((df_valid['school_score'] >= 3.5) & (df_valid['school_score'] < 6.0)).sum()}")
    print(f"  Below Average (D-F, 0-3.4):    {(df_valid['school_score'] < 3.5).sum()}")
    
    return df_schools


def main():
    print("\n" + "=" * 70)
    print("STEP 3: COLLECT AND PROCESS SCHOOL DATA")
    print("=" * 70)
    
    df_niche = load_niche_data()
    
    if df_niche is None:
        print("\n✗ Cannot proceed without Niche data")
        return
    
    df_schools = process_school_data(df_niche)
    
    print("\n" + "=" * 70)
    print("SAVING OUTPUT FILES")
    print("=" * 70)
    
    output_file = SCHOOL_DIR / "school_scores_by_zipcode.csv"
    df_schools.to_csv(output_file, index=False)
    print(f"\n✓ Saved school scores: {output_file}")
    
    print("\n" + "=" * 70)
    print("TOP 5 ZIP CODES BY SCHOOL QUALITY")
    print("=" * 70)
    df_valid = df_schools[df_schools['school_score'].notna()]
    top_5 = df_valid.nlargest(5, 'school_score')[['zip_code', 'school_grade', 'school_score']]
    print(top_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("BOTTOM 5 ZIP CODES BY SCHOOL QUALITY")
    print("=" * 70)
    bottom_5 = df_valid.nsmallest(5, 'school_score')[['zip_code', 'school_grade', 'school_score']]
    print(bottom_5.to_string(index=False))
    
    print("\n" + "=" * 70)
    print("STEP 3 COMPLETE ✓")
    print("=" * 70)
    print(f"\nProcessed school data for {len(df_schools)} ZIP codes")


if __name__ == "__main__":
    main()