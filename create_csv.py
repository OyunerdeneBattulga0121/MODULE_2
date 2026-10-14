# pip install pandas pyreadstat
# pip install pandas
# python3 create_csv.py  

try:
    import pandas as pd  # type: ignore[import-not-found]
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "pandas is required to run this script. Install it with: pip install pandas pyreadstat"
    ) from exc

# Load the file
df_2025 = pd.read_stata('lfs_2025_mon.dta')
df_2024 = pd.read_spss('lfs_2024_mon.sav')
df_2023 = pd.read_spss('lfs_2023_mon.sav')

# Export the dataframe to a CSV file
df_2025.to_csv('./2025/data.csv', index=False)
df_2024.to_csv('./2024/data.csv', index=False)
df_2023.to_csv('./2023/data.csv', index=False)

print("Conversion complete! Saved")

