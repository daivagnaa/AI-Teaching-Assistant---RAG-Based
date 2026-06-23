import faiss
import numpy as np
import pandas as pd

df = pd.read_pickle("metadata.pkl")

print(df.shape)
print(df.columns)
print(df)