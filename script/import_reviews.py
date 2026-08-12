import sqlite3
from pathlib import Path

import pandas as pd

# ==========================================
# DATABASE
# ==========================================

conn = sqlite3.connect("C:\\Users\\USER\\Desktop\\project\\database\\electronics_ai.db")
cursor = conn.cursor()


# ==========================================
# MENCARI PRODUCT ID
# ==========================================

def get_product_id(product_name):

    cursor.execute(
        """
        SELECT id
        FROM products
        WHERE LOWER(name)=LOWER(?)
        """,
        (product_name,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return None


# ==========================================
# IMPORT REVIEW
# ==========================================

def import_reviews(folder_path,
                   source,
                   review_column,
                   username_column=None,
                   date_column=None):

    folder = Path(folder_path)

    total_review = 0

    print("=" * 60)
    print(f"IMPORT {source}")
    print("=" * 60)

    for csv_file in folder.glob("*.csv"):

        product_name = csv_file.stem

        product_id = get_product_id(product_name)

        if product_id is None:

            print(f"[WARNING] Product tidak ditemukan : {product_name}")
            continue

        df = pd.read_csv(csv_file)

        imported = 0

        for _, row in df.iterrows():

            username = None
            review_date = None

            if username_column:
                username = row[username_column]

            if date_column:
                review_date = row[date_column]

            cursor.execute("""
                INSERT INTO reviews
                (
                    product_id,
                    username,
                    review_date,
                    review,
                    source,
                    language
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (

                product_id,
                username,
                review_date,
                row[review_column],
                source,
                "English"

            ))

            imported += 1

        total_review += imported

        print(f"✓ {product_name} ({imported} reviews)")

    print("-" * 60)
    print(f"Total Review {source} : {total_review}")
    print()


# ==========================================
# SMARTPHONE
# ==========================================

import_reviews(

    folder_path="C:\\Users\\USER\\Desktop\\project\\data\\hp\\reviews",

    source="GSMArena",

    username_column="uname2",

    date_column="upost",

    review_column="uopin"

)


# ==========================================
# LAPTOP
# ==========================================

import_reviews(

    folder_path="C:\\Users\\USER\\Desktop\\project\\data\\laptop\\reviews",

    source="Flipkart",

    review_column="review"

)


# ==========================================
# SIMPAN DATABASE
# ==========================================

conn.commit()

conn.close()

print("=" * 60)
print("SEMUA REVIEW BERHASIL DIIMPORT")
print("=" * 60)