import pandas as pd
import os
import sys

# Force UTF-8 for stdout/stderr to avoid UnicodeEncodeError with emojis on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LARGE_REJECTED = os.path.join(BASE_DIR, "data", "rejected_2007_to_2018Q4.csv")
SAMPLED_REJECTED = os.path.join(BASE_DIR, "data", "rejected_lite.csv")

def sample_rejected_data(n=150000):
    print(f"🔍 Sampling {n} rows from {LARGE_REJECTED}...")
    
    if not os.path.exists(LARGE_REJECTED):
        print(f"❌ File not found: {LARGE_REJECTED}")
        return

    # Using chunksize to be memory efficient
    chunks = pd.read_csv(LARGE_REJECTED, chunksize=50000, low_memory=False)
    
    sampled_chunks = []
    total_rows = 0
    
    for chunk in chunks:
        # We take a fraction of each chunk to get a distributed sample
        # Total rows in the large file is roughly 27M. 
        # 150k / 27M = 0.0055
        sample_size = min(len(chunk), int(n / 540) + 1) # Estimated fraction
        sampled_chunks.append(chunk.sample(min(len(chunk), sample_size)))
        total_rows += len(sampled_chunks[-1])
        if total_rows >= n:
            break
            
    df_sampled = pd.concat(sampled_chunks).head(n)
    
    print(f"✅ Successfully sampled {len(df_sampled)} rows.")
    
    # Save to CSV
    df_sampled.to_csv(SAMPLED_REJECTED, index=False)
    print(f"💾 Saved to: {SAMPLED_REJECTED}")

if __name__ == "__main__":
    sample_rejected_data()
