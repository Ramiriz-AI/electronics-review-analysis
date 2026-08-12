import sqlite3
import re

from transformers import pipeline
from tqdm import tqdm

from preprocessing import clean_text

print("Loading sentiment model...")

classifier = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

print("Model loaded.")

conn = sqlite3.connect(
    "C:\\Users\\USER\\Desktop\\project\\database\\electronics_ai.db"
)

cursor = conn.cursor()

cursor.execute("""
SELECT
    aspects.id,
    aspects.aspect,
    reviews.review
FROM aspects
JOIN reviews
ON aspects.review_id = reviews.id
WHERE aspects.sentiment IS NULL
""")

rows = cursor.fetchall()

print(f"{len(rows)} aspect ditemukan")

for aspect_id, aspect, review in tqdm(rows):

    review = clean_text(review)

    # Pecah review menjadi kalimat
    sentences = re.split(r"[.!?]", review)

    # Cari kalimat yang mengandung aspect
    target = ""

    for sentence in sentences:

        if aspect.lower() in sentence.lower():

            target = sentence.strip()

            break

    # Kalau tidak ketemu gunakan seluruh review
    if target == "":
        target = review

    result = classifier(
        target,
        truncation=True,
        max_length=512
    )[0]

    sentiment = result["label"].capitalize()

    cursor.execute("""
    UPDATE aspects
    SET sentiment = ?
    WHERE id = ?
    """, (sentiment, aspect_id))

conn.commit()
conn.close()

print("Aspect sentiment selesai.")