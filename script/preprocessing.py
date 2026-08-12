import re
import html


def clean_text(text):
    """
    Membersihkan teks review tanpa mengubah makna.
    """

    if text is None:
        return ""

    text = str(text)

    # Decode HTML entities
    text = html.unescape(text)

    # Hapus URL
    text = re.sub(r"http\S+|www\S+", "", text)

    # Hapus HTML tag
    text = re.sub(r"<.*?>", " ", text)

    # Ubah newline, tab menjadi spasi
    text = re.sub(r"[\r\n\t]+", " ", text)

    # Hilangkan spasi berlebih
    text = re.sub(r"\s+", " ", text)

    # Hilangkan karakter NULL
    text = text.replace("\x00", "")

    # Trim
    text = text.strip()

    return text