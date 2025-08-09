import pandas as pd
print("Reading original large CSV...")
df = pd.read_csv('online_retail_II.csv')
print(f"Original dataset has {len(df)} rows.")
sample_df = df.sample(n=100000, random_state=42)
print(f"Sampled dataset has {len(sample_df)} rows.")
sample_df.to_csv('online_retail_sampled.csv', index=False)
print("Successfully created 'online_retail_sampled.csv'.")