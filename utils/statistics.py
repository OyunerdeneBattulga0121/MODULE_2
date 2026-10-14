import pandas as pd # type: ignore

def get_basic_stats(df: pd.DataFrame, year: int):
    """
    Өгөгдсөн жилийн датаны үндсэн статистик мэдээллийг хэвлэх функц.
    """
    print(f"\n================ [{year}] ОНИЙ СТАТИСТИК МЭДЭЭЛЭЛ ================")
    print(f"• Нийт мөр (ажиглалт) болон хувьсагчдын тоо: {df.shape}")
    
    print("\n• Тоон хувьсагчдын үндсэн статистик (describe):")
    # describe() нь дундаж, хамгийн бага/их, стандарт хазайлт зэргийг гаргана
    print(df.describe().T[['count', 'mean', 'std', 'min', 'max']].head(10))
    
    print("\n• Хоосон уттуудын байдал (Null values count per column):")
    null_counts = df.isnull().sum()
    print(null_counts[null_counts > 0].head(10) if not null_counts[null_counts > 0].empty else "Хоосон утга байхгүй.")
    print("=" * 60)