import sqlite3
import pandas as pd

conn = sqlite3.connect("electronics_ai.db")
cursor = conn.cursor()

# ===========================================
# SMARTPHONE
# ===========================================

hp_df = pd.read_excel("./hp/spec/Spek_HP.xlsx")

for _, row in hp_df.iterrows():

    product_id = int(row["product_id"])
    product_name = row["Merk_HP"]
    brand = product_name.split()[0]

    # products
    cursor.execute("""
        INSERT OR REPLACE INTO products
        (id, name, brand, category)
        VALUES (?, ?, ?, ?)
    """, (
        product_id,
        product_name,
        brand,
        "Smartphone"
    ))

    # smartphone_specs
    cursor.execute("""
        INSERT OR REPLACE INTO smartphone_specs (
            product_id,
            chipset,
            cpu,
            gpu,
            ram,
            storage,
            display_type,
            display_size,
            resolution,
            refresh_rate,
            rear_camera,
            front_camera,
            battery,
            charging,
            os,
            weight,
            fingerprint,
            network,
            waterproof
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        product_id,
        row["chipset"],
        row["cpu"],
        row["gpu"],
        row["ram"],
        row["storage"],
        row["display_type"],
        row["display_size"],
        row["resolution"],
        row["refresh_rate"],
        row["rear_camera"],
        row["front_camera"],
        row["battery"],
        row["charging"],
        row["os"],
        row["weight"],
        row["fingerprint"],
        row["network"],
        row["waterproof"]

    ))

print("Smartphone berhasil diimport.")

# ===========================================
# LAPTOP
# ===========================================

laptop_df = pd.read_excel("./laptop/spec/Spek_laptop.xlsx")

for _, row in laptop_df.iterrows():

    product_id = int(row["product_id"])
    product_name = row["product_name"]
    brand = product_name.split()[0]

    # products
    cursor.execute("""
        INSERT OR REPLACE INTO products
        (id, name, brand, category)
        VALUES (?, ?, ?, ?)
    """, (
        product_id,
        product_name,
        brand,
        "Laptop"
    ))

    # laptop_specs
    cursor.execute("""
        INSERT OR REPLACE INTO laptop_specs (
            product_id,
            cpu,
            gpu,
            gpu_memory,
            ram,
            storage,
            display_size,
            display_panel,
            resolution,
            refresh_rate,
            battery,
            weight,
            os,
            camera
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        product_id,
        row["cpu"],
        row["gpu"],
        row["gpu_memory"],
        row["ram"],
        row["storage"],
        row["display_size"],
        row["display_panel"],
        row["resolution"],
        row["refresh_rate"],
        row["battery"],
        row["weight"],
        row["os"],
        row["camera"]

    ))

print("Laptop berhasil diimport.")

conn.commit()
conn.close()

print("Semua produk berhasil diimport.")