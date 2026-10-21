import os 

import matplotlib.pyplot as plt  # type: ignore
import numpy as np # type: ignore
import pandas as pd # type: ignore


def _weighted_median(values, weights):
    valid = values.notna() & weights.notna() & (weights > 0) 
    values = values[valid]
    weights = weights[valid]
    if values.empty: 
        return np.nan 

    order = np.argsort(values.to_numpy()) 
    sorted_values = values.to_numpy()[order] 
    sorted_weights = weights.to_numpy()[order] 
    midpoint = sorted_weights.sum() / 2 
    return sorted_values[np.searchsorted(np.cumsum(sorted_weights), midpoint)] 


def run_additional_analysis(df, wage, output_dir):
    """Нас, хүйсээр ажиллах хүч болон цалингийн нэмэлт шинжилгээ хийнэ.""" 
    os.makedirs(output_dir, exist_ok=True) 

    age_sex_rows = [] 
    groups = df.dropna(subset=["age_grp", "a03"]).groupby( 
        ["age_grp", "a03"], observed=True 
    )
    for (age_group, sex), group in groups:
        weights = group["w"].where(group["w"] > 0, 0).fillna(0)
        population = weights.sum()
        labour_force = weights[group["in_lf"]].sum()
        employed = weights[group["status"] == "Ажиллагч"].sum()
        unemployed = weights[group["status"] == "Ажилгүй"].sum()

        age_sex_rows.append({
            "Насны бүлэг": str(age_group),
            "Хүйс": sex, 
            "Хүн амын жинтэй тоо": population, 
            "Ажиллах хүчний жинтэй тоо": labour_force, 
            "Ажиллагчийн жинтэй тоо": employed, 
            "Ажилгүй хүний жинтэй тоо": unemployed, 
            "Оролцоо %": 100 * labour_force / population if population else np.nan, 
            "Хөдөлмөр эрхлэлт %": 100 * employed / population if population else np.nan, 
            "Ажилгүйдэл %": 100 * unemployed / labour_force if labour_force else np.nan, 
        })

    age_sex_table = pd.DataFrame(age_sex_rows)
    age_sex_table.to_csv( 
        os.path.join(output_dir, "table_lf_age_sex.csv"), 
        index=False, 
        encoding="utf-8-sig", 
    ) 
    print("\nНэмэлт шинжилгээ: нас, хүйсээр ажиллах хүчний үзүүлэлт (жинтэй, %)") 
    print(age_sex_table[[ 
        "Насны бүлэг", "Хүйс", "Оролцоо %", "Хөдөлмөр эрхлэлт %", "Ажилгүйдэл %", 
    ]].round(1).to_string(index=False)) 

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True) 
    measures = [ 
        ("Оролцоо %", "Ажиллах хүчний оролцоо"), 
        ("Хөдөлмөр эрхлэлт %", "Хөдөлмөр эрхлэлт"), 
        ("Ажилгүйдэл %", "Ажилгүйдэл"), 
    ] 
    for ax, (column, title) in zip(axes, measures): 
        for sex, group in age_sex_table.groupby("Хүйс", sort=False): 
            ax.plot(group["Насны бүлэг"], group[column], marker="o", label=sex) 
        ax.set_title(title) 
        ax.set_ylabel("%") 
        ax.grid(axis="y", alpha=0.3) 
        ax.tick_params(axis="x", rotation=45) 
    axes[0].legend(title="Хүйс") 
    fig.suptitle("Нас, хүйсээр ажиллах хүчний үзүүлэлт (2024, жинтэй)") 
    fig.tight_layout() 
    fig.savefig( 
        os.path.join(output_dir, "5_lf_rates_age_sex.png"), 
        dpi=150, 
        bbox_inches="tight", 
    ) 
    plt.close(fig) 

    wage_rows = [] 
    wage_groups = wage.dropna(subset=["age_grp", "a03"]).groupby( 
        ["age_grp", "a03"], observed=True 
    ) 
    for (age_group, sex), group in wage_groups: 
        wage_rows.append({ 
            "Насны бүлэг": str(age_group), 
            "Хүйс": sex, 
            "n": len(group), 
            "Median (жингүй)": group["wage_m"].median(), 
            "Median (жинтэй)": _weighted_median(group["wage_m"], group["w"]), 
        }) 

    wage_age_sex_table = pd.DataFrame(wage_rows) 
    wage_age_sex_table.to_csv( 
        os.path.join(output_dir, "table_wage_age_sex.csv"), 
        index=False, 
        encoding="utf-8-sig", 
    ) 
    print("\nНэмэлт шинжилгээ: нас, хүйсээр сарын median цалин (сая ₮)") 
    print(wage_age_sex_table.round(2).to_string(index=False)) 

    fig, ax = plt.subplots(figsize=(9, 5)) 
    for sex, group in wage_age_sex_table.groupby("Хүйс", sort=False): 
        ax.plot( 
            group["Насны бүлэг"], 
            group["Median (жингүй)"], 
            marker="o", 
            label=sex, 
        ) 
    ax.set( 
        title="Нас, хүйсээр сарын median цалин (2024)", 
        xlabel="Насны бүлэг", 
        ylabel="Median цалин (сая ₮)", 
    ) 
    ax.grid(axis="y", alpha=0.3) 
    ax.legend(title="Хүйс") 
    fig.tight_layout() 
    fig.savefig( 
        os.path.join(output_dir, "6_wage_age_sex.png"), 
        dpi=150, 
        bbox_inches="tight", 
    ) 
    plt.close(fig) 