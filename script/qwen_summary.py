import sqlite3
import ollama

# ==============================
# Koneksi Database
# ==============================

conn = sqlite3.connect(
    r"C:\Users\USER\Desktop\project\database\electronics_ai.db"
)

cursor = conn.cursor()

product_id = 1

# ==============================
# Ambil Statistik Aspect
# ==============================

cursor.execute("""
SELECT
    aspect,
    SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END) AS positive,
    SUM(CASE WHEN sentiment='Neutral' THEN 1 ELSE 0 END) AS neutral,
    SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END) AS negative
FROM aspects a
JOIN reviews r
ON a.review_id = r.id
WHERE r.product_id = ?
GROUP BY aspect
ORDER BY aspect
""", (product_id,))

rows = cursor.fetchall()

positive_aspects = []
negative_aspects = []

for aspect, pos, neu, neg in rows:

    pos = pos or 0
    neu = neu or 0
    neg = neg or 0

    if pos > neg:
        positive_aspects.append(
            f"- {aspect} ({pos} positif, {neg} negatif)"
        )

    elif neg > pos:
        negative_aspects.append(
            f"- {aspect} ({neg} negatif, {pos} positif)"
        )

# ==============================
# Susun Prompt
# ==============================

prompt = f"""
Kamu adalah analis review produk elektronik.

Berikut hasil analisis sentimen per aspek.

Aspek yang menjadi kelebihan:

{chr(10).join(positive_aspects)}

Aspek yang menjadi kekurangan:

{chr(10).join(negative_aspects)}

Tugasmu hanya membuat ringkasan.

Jangan menghitung ulang statistik.
Jangan mengubah angka.
Jangan menambahkan aspek baru.

Gunakan format berikut.

## Ringkasan

### Kelebihan
Jelaskan secara singkat kelebihan produk berdasarkan aspek positif.

### Kekurangan
Jelaskan secara singkat kekurangan produk berdasarkan aspek negatif.

### Kesimpulan
Berikan kesimpulan singkat maksimal 100 kata.
"""

# ==============================
# Kirim ke Qwen
# ==============================

response = ollama.chat(
    model="qwen3:4b-instruct",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

summary = response["message"]["content"]

# ==============================
# Simpan ke Database
# ==============================

cursor.execute("""
CREATE TABLE IF NOT EXISTS product_summary(
    product_id INTEGER PRIMARY KEY,
    summary TEXT
)
""")

cursor.execute("""
INSERT OR REPLACE INTO product_summary
(product_id, summary)
VALUES (?, ?)
""", (
    product_id,
    summary
))

conn.commit()

print(summary)

conn.close()