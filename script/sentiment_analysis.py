import sqlite3

from transformers import pipeline

from tqdm import tqdm

from preprocessing import clean_text

# ==========================
# Load Model
# ==========================

print("Loading model...")

classifier = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

print("Model loaded.")

# ==========================
# Database
# ==========================

conn = sqlite3.connect("C:\\Users\\USER\\Desktop\\project\\database\\electronics_ai.db")

cursor = conn.cursor()

# ==========================
# Ambil review yang belum dianalisis
# ==========================

cursor.execute("""

SELECT id, review

FROM reviews

WHERE id NOT IN (

SELECT review_id

FROM sentiments

)

""")

reviews = cursor.fetchall()

print(f"{len(reviews)} review ditemukan.")

# ==========================
# Analisis
# ==========================

for review_id, review in tqdm(reviews, desc="Analisis Sentimen"):

    try:

        review = clean_text(review)

        if review == "":
            continue

        result = classifier(
            review,
            truncation=True,
            max_length=512
        )[0]

        sentiment = result["label"]

        confidence = float(result["score"])

        cursor.execute("""
        INSERT INTO sentiments
        (
            review_id,
            sentiment,
            confidence
        )
        VALUES (?, ?, ?)
        """,
        (
            review_id,
            sentiment,
            confidence
        ))

    except Exception as e:

        print(f"Review {review_id} gagal")
        print(e)

conn.commit()

conn.close()

print("Sentiment analysis selesai.")