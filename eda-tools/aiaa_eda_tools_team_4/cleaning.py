"""Гишүүн 1: missing_report, iqr_outliers"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def missing_report(df):
    """Багана бүрийн хоосон утгын тоо ба хувь."""
    n = df.isnull().sum()
    return pd.DataFrame({"missing": n, "percent": (n / len(df) * 100).round(1)})


def iqr_outliers(x):
    """1.5 x IQR дүрмээр outlier утгуудыг буцаана."""
    x = np.array(x)
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    return x[(x < q1 - 1.5 * iqr) | (x > q3 + 1.5 * iqr)]
