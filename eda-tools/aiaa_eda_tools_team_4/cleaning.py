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



def group_rate(df: pd.DataFrame, by, flag: str, weight: str = None) -> pd.DataFrame:
    """Бүлэг бүрт flag (0/1) баганын эзлэх хувийг тооцно.

    weight өгвөл судалгааны жингээр жинлэнэ (АХС-д заавал).
    Ажилгүйдлийн түвшинд зөвхөн ажиллах хүчний мөрүүдийг дамжуулна.
    Буцаах: rate_pct (жинлэсэн %), n (жинлээгүй мөрийн тоо).
    """
    d = df.dropna(subset=[flag])
    w = d[weight] if weight else pd.Series(1.0, index=d.index)
    tmp = pd.DataFrame({"x": d[flag].astype(float) * w, "w": w})
    keys = [d[b] for b in ([by] if isinstance(by, str) else by)]
    g = tmp.groupby(keys, observed=True)
    out = pd.DataFrame({
        "rate_pct": (g["x"].sum() / g["w"].sum() * 100).round(1),
        "n": g.size(),
    })
    return out.reset_index()


def labour_indicators(df: pd.DataFrame, by, status: str = "lf_status",
                      weight: str = None) -> pd.DataFrame:
    """Ажиллах хүчний гурван гол түвшинг бүлгээр тооцно (15+ насны мөрүүд).

    status баганын утга: "employed", "unemployed", "outside".
    """
    d = df.dropna(subset=[status]).copy()
    d["_w"] = d[weight] if weight else 1.0
    d["_emp"] = (d[status] == "employed") * d["_w"]
    d["_unemp"] = (d[status] == "unemployed") * d["_w"]
    keys = [by] if isinstance(by, str) else list(by)
    g = d.groupby(keys, observed=True)
    pop, emp, une = g["_w"].sum(), g["_emp"].sum(), g["_unemp"].sum()
    lf = emp + une
    out = pd.DataFrame({
        "lfpr": lf / pop * 100,                              # оролцоо
        "emp_rate": emp / pop * 100,                         # хөдөлмөр эрхлэлт
        "unemp_rate": une / lf.replace(0, np.nan) * 100,     # ажилгүйдэл
        "n": g.size(),
    }).round(1)
    return out.reset_index()
