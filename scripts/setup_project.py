def create_project_structure():
    """
    Create all necessary directories for the project
    """
    
    # Define directory structure
    directories = [
        "data",
        "data/raw_zcta",
        "data/crime",
        "data/schools",
        "data/transit",
        "data/housing",
        "data/lifestyle",
        "data/diversity",
        "data/processed",
        "scripts",
        "outputs",
        "outputs/visualizations",
        "outputs/tableau_data",
        "logs"
    ]
    
    print("Creating project directory structure...")
    print("=" * 60)
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}/")