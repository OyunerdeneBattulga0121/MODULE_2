import os
import pandas as pd # type: ignore
from utils.cleaner import clean_dataframe
from utils.statistics import get_basic_stats

def main():
    # Шалгахыг хүссэн онуудын жагсаалт
    years = [2023, 2024, 2025]
    
    for year in years:
        # Жил тус бүрийн хавтас доторх data.csv файлын зам
        file_path = f"./{year}/data.csv"
        
        if not os.path.exists(file_path):
            print(f"\n[Анхааруулга] {file_path} файл олдсонгүй! Эхлээд create_py.py ажиллуулж үүсгэнэ үү.")
            continue
            
        print(f"\n\n{'='*20} {year} ОНЫ ДАТАТАЙ АЖИЛЛАЖ БАЙНА {'='*20}")
        
        # 1. Датаг уншиж ачаалах
        try:
            df = pd.read_csv(file_path, low_memory=False)
            print(f"Амжилттай уншигдлаа. Мөрийн тоо: {len(df)}")
        except Exception as e:
            print(f"Файлыг уншихад алдаа гарлаа: {e}")
            continue
            
        # 2. Статистик мэдээллийг харах
        get_basic_stats(df, year)
        
        # 3. Датаг цэвэрлэх (Null болон дубликат засах)
        # Эх дата файл/датафреймийг өөрчлөхгүй байх үүднээс хуулбарт ажиллана.
        cleaned_df = clean_dataframe(df.copy(deep=True))
        
        # 4. Шаардлагатай гэж үзвэл цэвэрлэсэн датагаа шинээр хадгалж болно
        output_path = f"./{year}/cleaned_data.csv"
        cleaned_df.to_csv(output_path, index=False)
        print(f"-> Цэвэрлэсэн датаг {output_path} руу амжилттай хадчихав.")

if __name__ == "__main__":
    main()