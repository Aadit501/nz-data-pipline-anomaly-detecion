import pandas as pd
from sqlalchemy import create_engine, text
import os
from pathlib import Path

# Configure paths
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
DB_PATH = BASE_DIR / "data" / "database.db"

def load_csv_to_sqlite(csv_filename: str = "Dataset.csv", table_name: str = "raw_vehicles"):
    """
    Load CSV file into SQLite database
    """
    csv_path = RAW_DATA_DIR / csv_filename
    
    if not csv_path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")
    
    print(f"Loading file: {csv_path}")
    
    # Create database engine
    engine = create_engine(f'sqlite:///{DB_PATH}')
    
    # Read and load in chunks
    chunk_size = 100_000
    total_rows = 0
    
    for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=chunk_size, low_memory=False)):
        if i == 0:
            chunk.to_sql(table_name, engine, if_exists='replace', index=False)
        else:
            chunk.to_sql(table_name, engine, if_exists='append', index=False)
        
        total_rows += len(chunk)
        print(f"  Loaded chunk {i+1} - Total rows: {total_rows:,}")
    
    print(f"\n✅ Successfully loaded {total_rows:,} rows into table '{table_name}'")
    print(f"Database created at: {DB_PATH}")
    
    # Show table info
    with engine.connect() as conn:
        # Fixed: Use text() for raw SQL
        result = conn.execute(text("SELECT COUNT(*) FROM raw_vehicles")).fetchone()
        print(f"Total rows in database: {result[0]}")
        
        # Show column names
        cols = conn.execute(text("PRAGMA table_info(raw_vehicles)")).fetchall()
        print("\nFirst 15 columns in table:")
        for col in cols[:15]:
            print(f"  - {col[1]}")

if __name__ == "__main__":
    load_csv_to_sqlite()