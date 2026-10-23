
# LFS-2024: Labour force and wage analysis, using the aiaa-eda-tools-team-4 library
# Install once: pip install aiaa-eda-tools-team-4
# Run: python index.py

from pathlib import Path

import numpy as np
import pandas as pd

from aiaa_eda_tools_team_4.cleaning import missing_report
from aiaa_eda_tools_team_4.stats import basic_stats, group_stats, labour_rates, iqr_bounds
from aiaa_eda_tools_team_4.plots import plot_hist, plot_bar, plot_box, plot_line, plot_corr

# Settings for this year's data (column names differ between survey years)
YEAR = 2024
WEIGHT_COL = "weighty_cal_Y"
PERSON_KEY = ["PSU", "ssu", "quarter", "p01"]   # columns that identify one person

DATA_PATH = Path(__file__).resolve().parent / "data.csv"
OUT_DIR = DATA_PATH.parent / "outputs"
OUT_DIR.mkdir(exist_ok=True)

YES = "Тийм"
MONTHLY = "Нэг сард"
CASH = "Тийм, мөнгөн хэлбэрээр авсан"

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
SEXES = ["Male", "Female"]
AGE_BINS = [15, 25, 35, 45, 55, 65, 101]
AGE_LABELS = ["15–24", "25–34", "35–44", "45–54", "55–64", "65+"]


# Section names
def section(title):
    print("\n" + "=" * 60 + f"\n{title}\n" + "=" * 60)


# Tiim gesen muriig yes bolgodog
def any_yes(data, cols):
    return np.any(data[cols].to_numpy() == YES, axis=1)


# 1. Load data

section("1. Load data")
df = pd.read_csv(DATA_PATH, low_memory=False)
df["sex"] = df["a03"].map(SEX_EN)
df["education"] = df["a28"].map(EDU_EN)
print(df.shape)
print(df.head())

# 2. Important columns and infos

section("2. Key columns")
cols = PERSON_KEY + ["a03", "a05", "a28", "axcaimagcode", "e04", "f02", "f03", WEIGHT_COL]
df[cols].info()
print(missing_report(df[cols]))

for col in ["e04", "sex", "education", "axcaimagcode", "f03"]:
    print(f"\n{col}:")
    print(df[col].value_counts(dropna=False))


# 3. Data cleaning

section("3. Data cleaning")
print("Duplicate rows:", df.duplicated().sum())
print(f"Duplicate persons ({' + '.join(PERSON_KEY)}):", df.duplicated(subset=PERSON_KEY).sum())

# Wage sample: wage reported, above 0, monthly wage, education known
wage = df[df["f01"] == CASH]
print("Wage reported:", len(wage), "| of which zero wage:", (wage["f02"] == 0).sum())
wage = wage[(wage["f02"] > 0) & (wage["f03"] == MONTHLY)]
print("Above 0 and monthly:", len(wage))
print(missing_report(wage[["a03", "a05", "a28", "axcaimagcode", WEIGHT_COL]]))
wage = wage.dropna(subset=["a28"]).copy()
print("Final wage sample:", len(wage))

# Outliers (IQR rule) — counted only, not removed
b = iqr_bounds(wage["f02"])
print(f"\nQ1: {b['q1']}  Q3: {b['q3']}  IQR: {b['iqr']}")
print(f"Lower bound: {b['lower']}  Upper bound: {b['upper']}")
print("Low outliers:", (wage["f02"] < b["lower"]).sum())
print("High outliers:", (wage["f02"] > b["upper"]).sum())


# 4. Wage distribution (thousand MNT)

section("4. Wage distribution (thousand MNT)")
for name, value in basic_stats(wage["f02"]).items():
    print(f"{name}: {value}")
print("Mode:", wage["f02"].mode()[0])
print("Variance:", round(wage["f02"].var(), 1))
print("Range:", np.ptp(wage["f02"]))

plot_hist(wage, "f02", path=OUT_DIR / "hist_wage.png", bins=50,
          title=f"Monthly wage distribution ({YEAR})",
          xlabel="Monthly wage (thousand MNT)", ylabel="Number of people", show=False)


# 5. Wages by group: sex, education, age

section("5. Wages by group")
sex = group_stats(wage, "sex", "f02", extra=["std"])
print(sex)

edu = group_stats(wage, "education", "f02").reindex(EDU_ORDER)
print(edu)

wage["age_group"] = pd.cut(wage["a05"], bins=AGE_BINS, labels=AGE_LABELS, right=False)
age = group_stats(wage, "age_group", "f02")
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

print("\nTotal:")
print(labour_rates(lf))
lf_sex = lf.groupby("sex")[["status"]].apply(labour_rates)
print("\nBy sex:")
print(lf_sex)


# 7. Save charts (every plot function from the library's plots.py)

section("7. Charts")
sex_colors = {"Male": "steelblue", "Female": "orange"}

# plot_bar: the 3 labour force rates, male vs female
rates_long = lf_sex.reset_index().melt(id_vars="sex", var_name="indicator", value_name="rate")
plot_bar(rates_long, x="indicator", y="rate", hue="sex", palette=sex_colors,
         path=OUT_DIR / "bar_labour_rates_sex.png", ylim=(0, 100),
         title=f"Labour force rates by sex ({YEAR})",
         xlabel="", ylabel="Rate (%)", show=False)

# plot_box: wage spread for each education level (y cut at 1.5x the IQR upper bound)
plot_box(wage, x="education", y="f02", order=EDU_ORDER, rotate=40,
         ylim=(0, b["upper"] * 1.5), path=OUT_DIR / "box_wage_edu.png",
         title=f"Monthly wage by education ({YEAR})",
         xlabel="", ylabel="Monthly wage (thousand MNT)", show=False)

# plot_line: median wage across age groups, one line per sex
age_sex = group_stats(wage, ["age_group", "sex"], "f02").reset_index()
age_sex["age_group"] = age_sex["age_group"].astype(str)
plot_line(age_sex, x="age_group", y="median", hue="sex", palette=sex_colors,
          path=OUT_DIR / "line_wage_age_sex.png",
          title=f"Median monthly wage by age and sex ({YEAR})",
          xlabel="Age group", ylabel="Median wage (thousand MNT)", show=False)

# plot_corr: how wage, age and working hours move together
numeric = wage[["f02", "a05", "g01t", "g02t"]].rename(columns={
    "f02": "Wage", "a05": "Age", "g01t": "Usual hours/week", "g02t": "Actual hours/week"})
plot_corr(numeric, path=OUT_DIR / "corr_wage_age_hours.png",
          title=f"Correlation: wage, age, hours ({YEAR})", show=False)

print("Charts saved to:", OUT_DIR)
