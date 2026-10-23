# aiaa-eda-tools

AI Academy Asia: EDA хийх туслах функцууд.

## Суулгах
```bash
pip install aiaa-eda-tools          # Colab дээр: !pip install -q aiaa-eda-tools
```
Байршуулахаас өмнө GitHub-аас шууд:
```bash
pip install git+https://github.com/<ахлагч>/aiaa-eda-tools.git
```

## Ашиглах
```python
import aiaa_eda_tools as et

et.missing_report(df)
et.basic_stats(df["score"])
et.group_rate(df, "credit_history", "loan_approved")
et.plot_hist(df, "score", path="figures/hist.png")   # path өгвөл файлд хадгална
```

## Функцууд
| Модуль | Функц | Юу хийдэг | Хариуцагч |
|---|---|---|---|
| `cleaning.py` | `missing_report(df)` | Багана бүрийн хоосон утгын тоо ба хувь | Гишүүн 1 |
| | `iqr_outliers(x)` | 1.5 × IQR дүрмээр outlier | Гишүүн 1 |
| `stats.py` | `basic_stats(x)` | n, дундаж, медиан, std, min, max | Гишүүн 2 |
| | `group_rate(df, by, target)` | Бүлэг бүрийн тоо ба дундаж | Гишүүн 2 |
| `plots.py` | `plot_hist(df, col, path=None)` | Histogram, дундаж ба медианы шугам | Гишүүн 3 |
| | `plot_box(df, x, y, path=None)` | Бүлгийн boxplot | Гишүүн 3 |
| | `plot_corr(df, path=None)` | Корреляцийн heatmap | Гишүүн 3 |
| `extra.py` | `plot_scatter(df, x, y, hue, path=None)` | Scatter, бүлгээр өнгөлсөн | Гишүүн 4 |

## Бүтэц
```
aiaa-eda-tools/
├── pyproject.toml          сангийн паспорт (Гишүүн 4)
├── README.md
├── requirements-dev.txt    build, twine
└── aiaa_eda_tools/
    ├── __init__.py         (Гишүүн 4)
    ├── cleaning.py         (Гишүүн 1)
    ├── stats.py            (Гишүүн 2)
    ├── plots.py            (Гишүүн 3)
    └── extra.py            (Гишүүн 4)
```

## Хөгжүүлэх
```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: python -m venv .venv && .venv\Scripts\activate
pip install -e .                                       # засварлах горимоор суулгана
pip install -r requirements-dev.txt
```
Git: хүн бүр өөрийн branch, **зөвхөн өөрийн файлаа** commit хийж Pull Request нээнэ.
```bash
git checkout -b bat
git add aiaa_eda_tools/stats.py
git commit -m "stats: basic_stats, group_rate"
git push origin bat
```

## Байршуулах (ахлагч)
[pypi.org](https://pypi.org/account/register/) дээр бүртгүүлж, 2FA асааж, API token авна.
```bash
python -m build
python -m twine check dist/*
python -m twine upload dist/*        # username: __token__, password: pypi-... token
```
Үүний дараа хэн ч `pip install aiaa-eda-tools` гэж суулгана. Шинэ хувилбар: `pyproject.toml`-ийн `version`-ийг өсгөж, `dist/`-ийг устгаад дахин. Ижил хувилбарыг дахин байршуулж болохгүй.
