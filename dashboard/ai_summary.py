import ollama


# ==========================================
# GENERATE SUMMARY DENGAN QWEN
# ==========================================

def generate_summary(conn, product_id):

    cursor = conn.cursor()

    # ==========================================
    # Ambil Statistik Aspect
    # ==========================================

    cursor.execute("""
    SELECT
        aspect,

        SUM(
            CASE
                WHEN sentiment = 'Positive' THEN 1
                ELSE 0
            END
        ) AS positive,

        SUM(
            CASE
                WHEN sentiment = 'Neutral' THEN 1
                ELSE 0
            END
        ) AS neutral,

        SUM(
            CASE
                WHEN sentiment = 'Negative' THEN 1
                ELSE 0
            END
        ) AS negative

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
                f"- {aspect} "
                f"({pos} positif, {neg} negatif)"
            )

        elif neg > pos:

            negative_aspects.append(
                f"- {aspect} "
                f"({neg} negatif, {pos} positif)"
            )

    # ==========================================
    # Tidak ada data
    # ==========================================

    if not positive_aspects and not negative_aspects:

        return (
            "Belum tersedia cukup data untuk membuat "
            "ringkasan AI pada produk ini."
        )

    # ==========================================
    # Prompt
    # ==========================================

    prompt = f"""
Kamu adalah analis review produk elektronik.

Berikut hasil analisis sentimen per aspek.

ASPEK YANG MENJADI KELEBIHAN:

{chr(10).join(positive_aspects)}

ASPEK YANG MENJADI KEKURANGAN:

{chr(10).join(negative_aspects)}

Buat ringkasan berdasarkan data tersebut.

ATURAN:
- Gunakan Bahasa Indonesia.
- Jangan menghitung ulang statistik.
- Jangan mengubah angka.
- Jangan menambahkan aspek baru.
- Jangan membuat informasi yang tidak terdapat dalam data.
- Jangan menyebutkan aspek yang tidak tersedia.
- Maksimal 200 kata.

Gunakan format:

### Kelebihan
Jelaskan aspek positif.

### Kekurangan
Jelaskan aspek negatif.

### Kesimpulan
Berikan kesimpulan singkat berdasarkan data.
"""

    # ==========================================
    # QWEN
    # ==========================================

    response = ollama.chat(
        model="qwen3:4b-instruct",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0.2
        }
    )

    return response["message"]["content"]


# ==========================================
# SIMPAN SUMMARY
# ==========================================

def save_summary(conn, product_id, summary):

    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO product_summary
    (
        product_id,
        summary
    )
    VALUES (?, ?)
    """, (
        product_id,
        summary
    ))

    conn.commit()