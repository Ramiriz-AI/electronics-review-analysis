import sqlite3
import spacy
from tqdm import tqdm

from preprocessing import clean_text

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Aspect lexicon
ASPECTS = {
    # Smartphone
    "battery",
    "battery life",
    "camera",
    "front camera",
    "rear camera",
    "display",
    "screen",
    "refresh rate",
    "brightness",
    "charging",
    "fast charging",
    "wireless charging",
    "processor",
    "performance",
    "cpu",
    "gpu",
    "ram",
    "storage",
    "memory",
    "speaker",
    "audio",
    "microphone",
    "wifi",
    "bluetooth",
    "signal",
    "network",
    "software",
    "os",
    "android",
    "fingerprint",
    "fingerprint sensor",
    "face unlock",
    "design",
    "build",
    "weight",

    # Laptop
    "keyboard",
    "touchpad",
    "trackpad",
    "fan",
    "cooling",
    "temperature",
    "heat",
    "hinge",
    "port",
    "ports",
    "usb",
    "hdmi",
    "webcam"
}

# Database
conn = sqlite3.connect(
    r"C:\Users\USER\Desktop\project\database\electronics_ai.db"
)
cursor = conn.cursor()

# Kosongkan tabel agar tidak duplikat
cursor.execute("DELETE FROM aspects")

# Ambil review
cursor.execute("""
SELECT id, review
FROM reviews
""")

reviews = cursor.fetchall()

for review_id, review in tqdm(reviews):

    review = clean_text(review)

    doc = nlp(review)

    found_aspects = set()

    # Cek noun phrase (misalnya "battery life")
    for chunk in doc.noun_chunks:

        phrase = chunk.text.lower().strip()

        if phrase in ASPECTS:
            found_aspects.add(phrase)

    # Cek kata tunggal (misalnya "battery")
    for token in doc:

        lemma = token.lemma_.lower()

        if lemma in ASPECTS:
            found_aspects.add(lemma)

    # Simpan ke database
    for aspect in found_aspects:

        cursor.execute("""
        INSERT INTO aspects
        (
            review_id,
            aspect
        )
        VALUES (?, ?)
        """, (review_id, aspect))

conn.commit()
conn.close()

print("Aspect extraction selesai.")