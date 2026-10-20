
# LFS-2025: Labour force and wage analysis
# Run: python analysis.py

from pathlib import Path
 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
 
DATA_PATH = Path(r"C:\Users\bolor\Documents\MOGULE_2\2025\data.csv")
OUT_DIR = DATA_PATH.parent / "outputs"
OUT_DIR.mkdir(exist_ok=True)
 
YES = "Тийм"
MONTHLY = "Нэг сард"

SEX_EN = {"Эрэгтэй": "Male", "Эмэгтэй": "Female"}
EDU_EN = {
    "Боловсролгүй": "No education",
    "Бага": "Primary",
    "Суурь": "Lower secondary",
    "Бүрэн дунд": "Upper secondary",
    "Техникийн болон мэргэжлийн": "Technical & vocational",
    "Тусгай мэргэжлийн дунд": "Specialized secondary",
    "Дипломын дээд": "Diploma",
    "Бакалаврын дээд": "Bachelor's",
    "Магистр": "Master's",
    "Доктор": "Doctorate",
}
EDU_ORDER = list(EDU_EN.values())
AGE_BINS = [15, 25, 35, 45, 55, 65, 101]
AGE_LABELS = ["15–24", "25–34", "35–44", "45–54", "55–64", "65+"]
 
# Section names 
def section(title):
    print("\n" + "=" * 60 + f"\n{title}\n" + "=" * 60)
 
# Tiim gesen muriig yes bolgodog 
def any_yes(data, cols):
    return np.any(data[cols].to_numpy() == YES, axis=1)
 
# Shows the percent.
def percent(part, whole):
    
    return np.round(np.divide(part, whole) * 100, 1)
 
# Wage count, median and mean for each group
def wage_by(data, col, extra=()):
    return data.groupby(col, observed=True)["f02"].agg(["count", "median", "mean", *extra])
 
# Save the current chart to the outputs folder and close it. 
def save_chart(filename):
    plt.savefig(OUT_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close()
 
# Makes a bar chart
def bar_chart(labels, values, title, value_label, filename,
              color="blue", horizontal=False, figsize=(7,3), ylim=None):
    plt.figure(figsize=figsize)
    if horizontal:
        plt.barh(labels, values, color=color)
        plt.xlabel(value_label)
    else:
        plt.bar(labels, values, color=color)
        plt.ylabel(value_label)
        if ylim:
            plt.ylim(ylim)
    plt.title(title)
    save_chart(filename)
 
 

# 1. Load data

section("1. Load data")
df = pd.read_csv(DATA_PATH, low_memory=False)
df["sex"] = df["a03"].map(SEX_EN)
df["education"] = df["a28"].map(EDU_EN)
print(df.shape)
print(df.head())
 
# 2. Important columns and infos

section("2. Key columns")
cols = ["axc_id", "a03", "a05", "a28", "axcaimagcode", "e04", "f02", "f03", "weight_cal_y"]
df[cols].info()
 
for col in ["e04", "sex", "education", "axcaimagcode", "f03"]:
    print(f"\n{col}:")
    print(df[col].value_counts(dropna=False))
 

# 3. Data cleaning

section("3. Data cleaning")
print("Duplicate rows:", df.duplicated().sum())
print("Duplicate persons (axc_id + p01):", df.duplicated(subset=["axc_id", "p01"]).sum())
 
# Wage sample: wage reported, above 0, monthly wage, education known
wage = df[df["f02"].notna()]
print("Wage reported:", len(wage), "| of which zero wage:", (wage["f02"] == 0).sum())
wage = wage[(wage["f02"] > 0) & (wage["f03"] == MONTHLY)]
print("Above 0 and monthly:", len(wage))
print(wage[["a03", "a05", "a28", "axcaimagcode", "weight_cal_y"]].isnull().sum())
wage = wage.dropna(subset=["a28"]).copy()
print("Final wage sample:", len(wage))
 
# Outliers (IQR rule) — counted only, not removed
q1, q3 = np.percentile(wage["f02"], [25, 75])
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
print(f"\nQ1: {q1}  Q3: {q3}  IQR: {iqr}")
print(f"Lower bound: {lower}  Upper bound: {upper}")
print("Low outliers:", (wage["f02"] < lower).sum())
print("High outliers:", (wage["f02"] > upper).sum())
 

# 4. Wage distribution (thousand MNT)

section("4. Wage distribution (thousand MNT)")
print(wage["f02"].describe())
print("Median:", wage["f02"].median())
print("Mode:", wage["f02"].mode()[0])
print("Variance:", round(wage["f02"].var(), 1))
print("Std:", round(wage["f02"].std(), 1))
print("Range:", np.ptp(wage["f02"]))
 
plt.figure(figsize=(10, 5))
plt.hist(wage["f02"], bins=50, color="steelblue", edgecolor="white")
plt.axvline(wage["f02"].mean(), color="red", linestyle="--", label="Mean")
plt.axvline(wage["f02"].median(), color="green", linestyle="-", label="Median")
plt.title("Monthly wage distribution (2025)")
plt.xlabel("Monthly wage (thousand MNT)")
plt.ylabel("Number of people")
plt.legend()
save_chart("hist_wage.png")
 

# 5. Wages by group: sex, education, age

section("5. Wages by group")
sex = wage_by(wage, "sex", extra=["std"])
print(sex)
 
edu = wage_by(wage, "education").reindex(EDU_ORDER)
print(edu)
 
wage["age_group"] = pd.cut(wage["a05"], bins=AGE_BINS, labels=AGE_LABELS, right=False)
age = wage_by(wage, "age_group")
print(age)
 

# 6. Labour force indicators (age 15+)

section("6. Labour force")
lf = df[df["a05"] >= 15].copy()
 
employed = lf["e04"].notna()                                   # e04 is asked only of employed people
search = any_yes(lf, ["h01a", "h01b", "h02"])                 # looked for work
avail = any_yes(lf, ["h10", "h11"])                           # available to work
unemployed = ~employed & search & avail
 
lf["status"] = np.select([employed, unemployed], ["Employed", "Unemployed"], default="Outside")
print(pd.crosstab(lf["sex"], lf["status"], margins=True))
 
# P
# articipation, unemployment and employment rates (%).
def rates(group):
    n_emp = np.count_nonzero(group["status"] == "Employed")
    n_unemp = np.count_nonzero(group["status"] == "Unemployed")
    labour = n_emp + n_unemp
    return pd.Series({
        "Participation %": percent(labour, len(group)),
        "Unemployment %": percent(n_unemp, labour),
        "Employment %": percent(n_emp, len(group)),
    })
 
 
print("\nTotal:")
print(rates(lf))
lf_sex = lf.groupby("sex")[["status"]].apply(rates)
print("\nBy sex:")
print(lf_sex)
 

# 7. Save charts

section("7. Charts")
sexes = ["Male", "Female"]
colors = ["blue", "orange"]
 
bar_chart(sexes, lf_sex.loc[sexes, "Participation %"],
          "Labour force participation by sex (2025)", "Participation rate (%)",
          "bar_participation.png", color=colors, ylim=(0, 100))
 
bar_chart(sexes, sex.loc[sexes, "median"],
          "Median monthly wage by sex (2025)", "Median wage (thousand MNT)",
          "bar_wage_sex.png", color=colors)
 
bar_chart(edu.index, edu["median"],
          "Median monthly wage by education (2025)", "Median wage (thousand MNT)",
          "bar_wage_edu.png", horizontal=True, figsize=(9, 6))
 
print("Charts saved to:", OUT_DIR)
 