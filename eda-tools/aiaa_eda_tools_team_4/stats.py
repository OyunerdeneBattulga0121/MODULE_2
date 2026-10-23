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
