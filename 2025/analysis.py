import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(r"C:\Users\bolor\Documents\MOGULE_2\2025\data.csv")
print(df.head())
print(df.shape())
print(df.describe())
print(df.columns())
print(df.dtypes())

