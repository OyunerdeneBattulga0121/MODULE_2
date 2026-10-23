"""Гишүүн 2: basic_stats, group_rate"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def basic_stats(x):
    """Тоон массивын үндсэн статистик."""
    x = np.array(x)
    return {"n": len(x),
            "mean": round(float(x.mean()), 2),
            "median": float(np.median(x)),
            "std": round(float(x.std(ddof=1)), 2),
            "min": float(x.min()),
            "max": float(x.max())}


def group_rate(df, by, target):
    """Бүлэг бүрийн хүний тоо ба target-ийн дундаж."""
    return df.groupby(by)[target].agg(["count", "mean"]).round(2)


# Shows the percent, rounded to 1 decimal.
def percent(part, whole):
    return np.round(np.divide(part, whole) * 100, 1)


# Count, median and mean of target for each group (extra adds more, e.g. ["std"])
def group_stats(df, by, target, extra=()):
    return df.groupby(by, observed=True)[target].agg(["count", "median", "mean", *extra])


# Participation, unemployment and employment rates (%)
def labour_rates(df, status_col="status", employed="Employed", unemployed="Unemployed"):
    n_emp = np.count_nonzero(df[status_col] == employed)
    n_unemp = np.count_nonzero(df[status_col] == unemployed)
    labour = n_emp + n_unemp
    return pd.Series({
        "Participation %": percent(labour, len(df)),
        "Unemployment %": percent(n_unemp, labour),
        "Employment %": percent(n_emp, len(df)),
    })
