import sqlite3

# ==========================
# Membuat koneksi database
# ==========================
conn = sqlite3.connect("electronics_ai.db")
cursor = conn.cursor()

# ==========================
# PRODUCTS
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    release_year INTEGER,
    price REAL,
    image_url TEXT
)
""")

# ==========================
# SMARTPHONE SPECS
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS smartphone_specs (
    product_id INTEGER PRIMARY KEY,
    chipset TEXT,
    cpu TEXT,
    gpu TEXT,
    ram TEXT,
    storage TEXT,
    display_type TEXT,
    display_size TEXT,
    resolution TEXT,
    refresh_rate TEXT,
    rear_camera TEXT,
    front_camera TEXT,
    battery TEXT,
    charging TEXT,
    os TEXT,
    weight TEXT,
    fingerprint TEXT,
    network TEXT,
    waterproof TEXT,

    FOREIGN KEY(product_id) REFERENCES products(id)
)
""")

# ==========================
# LAPTOP SPECS
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS laptop_specs (
    product_id INTEGER PRIMARY KEY,
    cpu TEXT,
    gpu TEXT,
    gpu_memory TEXT,
    ram TEXT,
    storage TEXT,
    display_size TEXT,
    display_panel TEXT,
    resolution TEXT,
    refresh_rate TEXT,
    battery TEXT,
    weight TEXT,
    os TEXT,
    camera TEXT,

    FOREIGN KEY(product_id) REFERENCES products(id)
)
""")

# ==========================
# REVIEWS
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    username TEXT,
    review_date TEXT,
    review TEXT NOT NULL,
    source TEXT NOT NULL,
    language TEXT,

    FOREIGN KEY(product_id) REFERENCES products(id)
)
""")

# ==========================
# SENTIMENT ANALYSIS
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS sentiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    sentiment TEXT NOT NULL,
    confidence REAL,

    FOREIGN KEY(review_id) REFERENCES reviews(id)
)
""")

# ==========================
# ASPECT-BASED SENTIMENT
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS aspects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    aspect TEXT NOT NULL,
    sentiment TEXT NOT NULL,

    FOREIGN KEY(review_id) REFERENCES reviews(id)
)
""")

# ==========================
# Simpan perubahan
# ==========================
conn.commit()
conn.close()

print("===================================")
print(" Database berhasil dibuat!")
print("===================================")
print("Tabel:")
print("- products")
print("- smartphone_specs")
print("- laptop_specs")
print("- reviews")
print("- sentiments")
print("- aspects")