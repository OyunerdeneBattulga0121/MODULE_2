"""
АХС-2024: Ажиллах хүчний бүтэц ба цалингийн шинжилгээ
Ажиллуулах: python lfs_2024_analysis.py [data.csv] [гаралтын_хавтас]
Шаардлага: pandas, numpy, matplotlib
"""
import sys
import os
import numpy as np  # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore

CSV = sys.argv[1] if len(sys.argv) > 1 else "data.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "outputs_2024"
os.makedirs(OUT, exist_ok=True)
YES = "Тийм"
MALE, FEMALE = "Эрэгтэй", "Эмэгтэй"
# Боловсролын түвшин: доороос дээш эрэмбэ
EDU_ORDER = ["Боловсролгүй", "Бага", "Суурь", "Бүрэн дунд",
             "Техникийн болон мэргэжлийн", "Тусгай мэргэжлийн дунд",
             "Дипломын дээд", "Бакалаврын дээд", "Магистр", "Доктор"]
AGE_BINS = [15, 25, 35, 45, 55, 65, 200]
AGE_LABELS = ["15-24", "25-34", "35-44", "45-54", "55-64", "65+"]


def section(title):
    print("\n" + "=" * 60 + f"\n{title}\n" + "=" * 60)


def wmedian(x, w):
    """Жинлэсэн median"""
    o = np.argsort(x.values)
    x, w = x.values[o], w.values[o]
    c = np.cumsum(w)
    return x[np.searchsorted(c, c[-1] / 2)]


def wmean(x, w):
    """Жинлэсэн дундаж"""
    return np.average(x, weights=w)


# ---------------------------------------------------------------
# 1. Өгөгдөл унших
# ---------------------------------------------------------------
section("1. Өгөгдөл унших")
df = pd.read_csv(CSV, low_memory=False)
print("Бүх мөр:", df.shape)

# Зөвхөн 2024 он (year багана 24.0 гэж хадгалагдсан)
df = df[df["year"].isin([24, 2024])].copy()
print("2024 оны мөр:", len(df))

# ---------------------------------------------------------------
# 2. 15+ насаар шүүх
# ---------------------------------------------------------------
section("2. 15+ насаар шүүх")
df = df[df["a05"] >= 15].copy()
df = df.rename(columns={"weighty_cal_Y": "w"})  # жингийн багана
print("15+ насны хүн:", len(df))

# ---------------------------------------------------------------
# 3. Ажиллах хүчний статус тодорхойлох
# ---------------------------------------------------------------
section("3. Ажиллах хүчний статус")
# Ажиллагч: сүүлийн 7 хоногт цалинтай ажил/бизнес/өрхийн аж ахуй/тусалсан,
# эсвэл түр эзгүй (буцаж хийхээр хүлээгдэж буй ажилтай)
emp = (df["b04"] == YES) | (df["b05"] == YES) | (df["b06"] == YES) | (df["c01"] == YES)
# Ажил хайсан: сүүлийн 30 хоногт ажил эсвэл бизнес эхлүүлэхээр оролдсон
search = (df["h01a"] == YES) | (df["h01b"] == YES)
# Ажилгүй (энгийн): ажиллагч биш + ажил хайсан
unemp = ~emp & search
# Ажилгүй (ILO, хатуу): дээр нь ирэх 14 хоногт ажиллахад бэлэн
unemp_strict = unemp & (df["h11"] == YES)

df["status"] = np.select([emp, unemp], ["Ажиллагч", "Ажилгүй"], "Ажиллах хүчний гаднах")
df["in_lf"] = df["status"] != "Ажиллах хүчний гаднах"
print(df["status"].value_counts())

# ---------------------------------------------------------------
# 4. Ажиллах хүчний үзүүлэлт (жинтэй ба жингүй)
# ---------------------------------------------------------------
section("4. Ажиллах хүчний бүтэц (Q1)")


def lf_rates(g, weighted):
    w = g["w"] if weighted else pd.Series(1.0, index=g.index)
    pop = w.sum()
    lf = w[g["in_lf"]].sum()
    e = w[g["status"] == "Ажиллагч"].sum()
    u = w[g["status"] == "Ажилгүй"].sum()
    return pd.Series({
        "Оролцоо %": 100 * lf / pop,
        "Ажилгүйдэл %": 100 * u / lf,
        "Хөдөлмөр эрхлэлт %": 100 * e / pop,
    })


rows = {}
for name, weighted in [("Жингүй", False), ("Жинтэй", True)]:
    rows[(name, "Бүгд")] = lf_rates(df, weighted)
    for s, g in df.groupby("a03"):
        rows[(name, s)] = lf_rates(g, weighted)
lf_table = pd.DataFrame(rows).T.round(1)
print(lf_table)

# Ажилгүйдлийн хатуу (ILO) хувилбар, жингүй
u_strict_rate = 100 * unemp_strict.sum() / df["in_lf"].sum()
print(f"\nХатуу ILO ажилгүйдэл (14 хоногт бэлэн): {u_strict_rate:.1f}% (жингүй)")

# Насны бүлгээр оролцоо (жинтэй)
df["age_grp"] = pd.cut(df["a05"], AGE_BINS, right=False, labels=AGE_LABELS)
part_age = df.groupby("age_grp", observed=True).apply(
    lambda g: 100 * g.loc[g["in_lf"], "w"].sum() / g["w"].sum())
print("\nОролцоо насны бүлгээр (жинтэй, %):")
print(part_age.round(1))

# ---------------------------------------------------------------
# 5. Цалингийн өгөгдөл цэвэрлэх
# ---------------------------------------------------------------
section("5. Цалингийн өгөгдөл цэвэрлэх")
# Сарын цалинтай, бэлэн мөнгөөр авсан, 0-ээс их утгатай хүмүүс (f02: мянган ₮)
wage = df[(df["f01"] == "Тийм, мөнгөн хэлбэрээр авсан")
          & (df["f03"] == "Нэг сард")
          & (df["f02"] > 0)].copy()
wage["wage_m"] = wage["f02"] / 1000  # сая ₮ болгох
print("Сарын цалинтай ажилтан:", len(wage))
print("Хоосон жин:", wage["w"].isna().sum())
wage["edu"] = pd.Categorical(wage["a28"], EDU_ORDER, ordered=True)

# ---------------------------------------------------------------
# 6. Цалингийн тархалт (Q2)
# ---------------------------------------------------------------
section("6. Цалингийн тархалт (Q2), сая ₮")
x, w = wage["wage_m"], wage["w"]
desc = pd.Series({
    "n": len(x),
    "Median (жингүй)": x.median(),
    "Mean (жингүй)": x.mean(),
    "Q1": x.quantile(.25),
    "Q3": x.quantile(.75),
    "Std": x.std(),
    "Median (жинтэй)": wmedian(x, w),
    "Mean (жинтэй)": wmean(x, w),
    "Skew (хазайлт)": x.skew(),
}).round(2)
print(desc)
# Бөөрөнхийлсөн утгын давтамж (1.0, 1.5, 2.0 гэх мэт)
print("\nХамгийн олон давтагдсан цалин (сая ₮):")
print(x.round(2).value_counts().head(5))

# ---------------------------------------------------------------
# 7. Бүлгээр харьцуулах (Q3)
# ---------------------------------------------------------------
section("7. Цалингийн ялгаа (Q3), median сая ₮")


def group_table(col):
    g = wage.groupby(col, observed=True)
    return pd.DataFrame({
        "n": g.size(),
        "Median (жингүй)": g["wage_m"].median(),
        "Median (жинтэй)": g.apply(lambda d: wmedian(d["wage_m"], d["w"])),
    }).round(2)


wage["age_grp"] = pd.cut(wage["a05"], AGE_BINS, right=False, labels=AGE_LABELS)
t_sex = group_table("a03")
t_edu = group_table("edu")
t_age = group_table("age_grp")
for title, t in [("Хүйсээр", t_sex), ("Боловсролоор", t_edu), ("Насаар", t_age)]:
    print(f"\n{title}:\n{t}")

# Хүйсийн цалингийн зөрүү
m = t_sex.loc[MALE, "Median (жингүй)"]
f = t_sex.loc[FEMALE, "Median (жингүй)"]
print(f"\nЭмэгтэйчүүдийн median цалин эрэгтэйчүүдээс {100 * (m - f) / m:.0f}%-иар бага")
print("Анхаар: n < 50 бүлгийн дүн найдвар багатай.")

# ---------------------------------------------------------------
# 8. График (4 ширхэг)
# ---------------------------------------------------------------
section("8. График зурах")
colors = {MALE: "steelblue", FEMALE: "orange"}

# График 1: ажиллах хүчний оролцоо хүйсээр (жинтэй)
fig, ax = plt.subplots(figsize=(6, 5))
vals = [lf_table.loc[("Жинтэй", s), "Оролцоо %"] for s in (MALE, FEMALE)]
ax.bar([MALE, FEMALE], vals, color=[colors[MALE], colors[FEMALE]])
ax.set(title="Ажиллах хүчний оролцоо, хүйсээр (2024)", ylabel="Оролцооны түвшин (%)", ylim=(0, 100))
for i, v in enumerate(vals):
    ax.text(i, v + 1, f"{v:.1f}", ha="center")
fig.savefig(f"{OUT}/1_participation.png", dpi=150, bbox_inches="tight")

# График 2: цалингийн гистограмм
fig, ax = plt.subplots(figsize=(7, 5))
ax.hist(x[x < 6], bins=60, color="steelblue", edgecolor="white")
ax.axvline(x.median(), color="red", ls="--", label=f"Median {x.median():.2f}")
ax.axvline(x.mean(), color="green", ls="--", label=f"Mean {x.mean():.2f}")
ax.set(title="Сарын цалингийн тархалт (2024)", xlabel="Сарын цалин (сая ₮, 6-аас доош)", ylabel="Хүний тоо")
ax.legend()
fig.savefig(f"{OUT}/2_wage_hist.png", dpi=150, bbox_inches="tight")

# График 3: median цалин хүйсээр
fig, ax = plt.subplots(figsize=(6, 5))
v = [t_sex.loc[s, "Median (жингүй)"] for s in (MALE, FEMALE)]
ax.bar([MALE, FEMALE], v, color=[colors[MALE], colors[FEMALE]])
ax.set(title="Median сарын цалин, хүйсээр (2024)", ylabel="Median цалин (сая ₮)")
for i, val in enumerate(v):
    ax.text(i, val + 0.02, f"{val:.2f}", ha="center")
fig.savefig(f"{OUT}/3_wage_sex.png", dpi=150, bbox_inches="tight")

# График 4: median цалин боловсролоор (n-тэй)
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(t_edu.index.astype(str), t_edu["Median (жингүй)"], color="steelblue")
for i, (val, n) in enumerate(zip(t_edu["Median (жингүй)"], t_edu["n"])):
    ax.text(val + 0.02, i, f"{val:.2f} (n={n})", va="center", fontsize=8)
ax.set(title="Median сарын цалин, боловсролоор (2024)", xlabel="Median цалин (сая ₮)")
ax.set_xlim(0, t_edu["Median (жингүй)"].max() * 1.25)
fig.savefig(f"{OUT}/4_wage_edu.png", dpi=150, bbox_inches="tight")
plt.close("all")

# ---------------------------------------------------------------
# 9. Хүснэгтүүдийг CSV болгон хадгалах
# ---------------------------------------------------------------
lf_table.to_csv(f"{OUT}/table_labour_force.csv", encoding="utf-8-sig")
desc.to_csv(f"{OUT}/table_wage_desc.csv", encoding="utf-8-sig")
t_sex.to_csv(f"{OUT}/table_wage_sex.csv", encoding="utf-8-sig")
t_edu.to_csv(f"{OUT}/table_wage_edu.csv", encoding="utf-8-sig")
t_age.to_csv(f"{OUT}/table_wage_age.csv", encoding="utf-8-sig")
print(f"Графикууд болон хүснэгтүүд '{OUT}/' хавтсанд хадгалагдлаа.")