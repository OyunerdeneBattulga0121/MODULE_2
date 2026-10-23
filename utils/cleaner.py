import pandas as pd # type: ignore

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Датаны дубликат мөрийг арилгах болон хоосон (null) утгуудыг бөглөх функц.
    Эх өгөгдлийг өөрчлөхгүйгээр ажиллахын тулд хуулбарыг ашиглана.
    """
    print("-> Дата цэвэрлэгээ эхэлж байна...")

    working_df = df.copy(deep=True)

    # 1. Дубликат мөрүүдийг шалгаж устгах
    initial_rows = len(working_df)
    working_df = working_df.drop_duplicates()
    removed_rows = initial_rows - len(working_df)
    print(f"   - Устгасан давхардсан мөрийн тоо: {removed_rows}")

    # 2. Null (хоосон) утгуудыг бөглөх
    for col in working_df.columns:
        # Хэрэв багана нь тоон төрөлтэй бол медиан утгаар бөглөх
        if pd.api.types.is_numeric_dtype(working_df[col]):
            median_val = working_df[col].median()
            working_df[col] = working_df[col].fillna(median_val)
        else:
            # Текст эсвэл бусад төрөлтэй бол 'Тодорхойгүй' гэсэн утгаар бөглөх
            working_df[col] = working_df[col].fillna('Тодорхойгүй')

    print("-> Дата цэвэрлэгээ дууслаа.")
    return working_df

"""Тоон шинжилгээний функцууд (Гишүүн 1)."""
import numpy as np
import pandas as pd


def basic_stats(df: pd.DataFrame, cols=None) -> pd.DataFrame:
    """n, дутуу, дундаж, медиан, std (ddof=1), min, Q1, Q3, max, хазгай."""
    num = df[cols] if cols is not None else df.select_dtypes("number")
    out = pd.DataFrame({
        "n": num.count(),
        "missing": num.isna().sum(),
        "mean": num.mean(),
        "median": num.median(),
        "std": num.std(),
        "min": num.min(),
        "q1": num.quantile(0.25),
        "q3": num.quantile(0.75),
        "max": num.max(),
        "skew": num.skew(),
    })
    return out.round(2)


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