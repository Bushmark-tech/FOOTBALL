import pandas as pd
try:
    df = pd.read_csv('data/football_data2.csv', encoding='latin-1', nrows=1)
    print("Columns:", list(df.columns))
except Exception as e:
    print(e)
