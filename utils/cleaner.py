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