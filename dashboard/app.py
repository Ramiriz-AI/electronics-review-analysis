import pandas as pd
import streamlit as st
import plotly.express as px
import sqlite3
import re
import html
from streamlit_searchbox import st_searchbox
from pathlib import Path
# from ai_summary import generate_summary, save_summary

# ---------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cari Produk — Spek & Review",
    page_icon="🔍",
    layout="centered",
)

# Label & icon yang enak dibaca untuk tiap kolom spek (nama kolom mentah -> tampilan)
SPEK_LABELS = {
    "chipset": ("🧩", "Chipset"),
    "cpu": ("⚙️", "CPU"),
    "gpu": ("🎮", "GPU"),
    "gpu_memory": ("🎛️", "VRAM GPU"),
    "ram": ("💾", "RAM"),
    "storage": ("📦", "Penyimpanan"),
    "display_type": ("🖥️", "Tipe Layar"),
    "display_size": ("📐", "Ukuran Layar"),
    "resolution": ("🔲", "Resolusi"),
    "refresh_rate": ("🔄", "Refresh Rate"),
    "rear_camera": ("📷", "Kamera Belakang"),
    "front_camera": ("🤳", "Kamera Depan"),
    "camera": ("📷", "Kamera"),
    "battery": ("🔋", "Baterai"),
    "charging": ("⚡", "Pengisian Daya"),
    "os": ("🤖", "Sistem Operasi"),
    "weight": ("⚖️", "Berat"),
    "fingerprint": ("🔒", "Fingerprint"),
    "network": ("📶", "Jaringan"),
    "waterproof": ("💧", "Ketahanan Air"),
}


# ---------------------------------------------------------
# GAYA VISUAL (satu tone warna, tipografi konsisten)
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

:root{
    --bg:        #F4F5F7;
    --surface:   #FFFFFF;
    --border:    #E3E5EA;
    --text:      #14161A;
    --text-mute: #6E7280;
    --accent:    #3454D1;
    --accent-bg: #EEF1FC;
    --good:      #1E8E63;
    --good-bg:   #E9F7F1;
    --bad:       #C0392B;
    --bad-bg:    #FBEDEB;
}

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; color: var(--text) !important; }
.stApp { background: var(--bg) !important; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; color: var(--text) !important; }

/* paksa semua teks bawaan streamlit (label, markdown, dsb) pakai warna gelap kita,
   supaya tidak ketimpa dark-mode bawaan browser/Streamlit */
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stText"], label, .stMarkdown, .stMarkdown p {
    color: var(--text) !important;
}

/* search box */
div[data-testid="stTextInput"] input {
    border-radius: 999px;
    border: 1.5px solid var(--border);
    padding: 0.85rem 1.4rem;
    font-size: 1.05rem;
    background: var(--surface) !important;
    color: var(--text) !important;
    box-shadow: 0 2px 10px rgba(20,22,26,0.04);
}
div[data-testid="stTextInput"] input::placeholder { color: var(--text-mute) !important; opacity: 1; }
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-bg);
}

/* chip buttons (daftar produk) */
div[data-testid="column"] .stButton button {
    width: 100%;
    border-radius: 999px;
    border: 1.5px solid var(--border);
    background: var(--surface) !important;
    color: var(--text) !important;
    font-weight: 500;
    padding: 0.5rem 0.8rem;
    transition: all 0.15s ease;
}
div[data-testid="column"] .stButton button p { color: var(--text) !important; }
div[data-testid="column"] .stButton button:hover {
    border-color: var(--accent);
    color: var(--accent) !important;
    background: var(--accent-bg) !important;
}
div[data-testid="column"] .stButton button:hover p { color: var(--accent) !important; }

/* tombol biasa (bukan chip di grid kolom), misal "Cari Perangkat lain" & "tampilkan lebih banyak" */
.stButton button {
    color: var(--text) !important;
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 999px !important;
}
.stButton button p { color: var(--text) !important; }
.stButton button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}
.stButton button:hover p { color: var(--accent) !important; }

.hero-title { text-align:center; font-size:2.1rem; font-weight:700; margin-bottom:0.2rem; color: var(--text) !important; }
.hero-sub { text-align:center; color:var(--text-mute) !important; margin-bottom:1.6rem; font-size:0.98rem; }

.section-label {
    font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:0.78rem;
    letter-spacing:0.08em; text-transform:uppercase; color:var(--accent) !important;
    margin: 1.8rem 0 0.6rem 0;
}

.product-card {
    background: var(--surface) !important; border:1px solid var(--border); border-radius:18px;
    padding:1.4rem 1.6rem; margin-bottom:0.6rem;
}
.product-title { font-family:'Space Grotesk',sans-serif; font-size:1.6rem; font-weight:700; margin:0; color: var(--text) !important; }
.stat-row { display:flex; gap:1.6rem; margin-top:0.6rem; flex-wrap:wrap; }
.stat-item { color:var(--text-mute) !important; font-size:0.9rem; }
.stat-item b { color:var(--text) !important; font-family:'JetBrains Mono',monospace; }

.spek-grid {
    display:grid; grid-template-columns: repeat(2, 1fr); gap:0.65rem;
    background:var(--surface) !important; border:1px solid var(--border); border-radius:18px;
    padding:1.2rem;
}
.spek-item { padding:0.55rem 0.7rem; border-radius:12px; background:var(--bg) !important; }
.spek-label { font-size:0.76rem; color:var(--text-mute) !important; margin-bottom:0.15rem; }
.spek-value { font-family:'JetBrains Mono',monospace; font-size:0.92rem; font-weight:500; color: var(--text) !important; }

.ai-card {
    background: var(--accent-bg) !important; border:1px solid #D6DEFA; border-radius:18px;
    padding:1.3rem 1.5rem; line-height:1.65; font-size:0.97rem; color: var(--text) !important;
}
.ai-card-empty {
    background: var(--surface) !important; border:1px dashed var(--border); border-radius:18px;
    padding:1.3rem 1.5rem; color:var(--text-mute) !important; font-size:0.9rem;
}

.review-card {
    background:var(--surface) !important; border:1px solid var(--border); border-radius:16px;
    padding:1rem 1.2rem; margin-bottom:0.6rem;
}
.review-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;}
.review-name { font-weight:600; font-size:0.9rem; color: var(--text) !important; }
.review-date { color:var(--text-mute) !important; font-size:0.78rem; font-family:'JetBrains Mono',monospace; }
.review-text { font-size:0.92rem; line-height:1.55; color: var(--text) !important; }

.empty-hint { text-align:center; color:var(--text-mute) !important; padding:2rem 0; font-size:0.92rem; }
</style>
""", unsafe_allow_html=True)


BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "electronics_ai.db"


# ===================================
# DATABASE CONNECTION
# ===================================

@st.cache_resource
def get_connection():

    return sqlite3.connect(
        str(DB_PATH),
        check_same_thread=False
    )


conn = get_connection()

# ===================================
# FORMAT RINGKASAN AI
# ===================================

def format_ai_summary(summary):

    if not summary:
        return ""

    # Escape HTML agar isi summary aman ditampilkan
    summary = html.escape(str(summary))

    # Bersihkan heading utama jika ada
    summary = re.sub(
        r'^\s*##\s*Ringkasan\s*',
        '',
        summary,
        flags=re.IGNORECASE
    )

    # ===================================
    # Pisahkan heading meskipun Qwen
    # tidak memberi newline
    # ===================================

    # Contoh yang ditangani:
    #
    # ### Kelebihan
    # Produk bagus
    #
    # ATAU
    #
    # ### Kelebihan Produk bagus
    #
    summary = re.sub(
        r'###\s*Kelebihan\s*',
        r'\n[[KELEBIHAN]]\n',
        summary,
        flags=re.IGNORECASE
    )

    summary = re.sub(
        r'###\s*Kekurangan\s*',
        r'\n[[KEKURANGAN]]\n',
        summary,
        flags=re.IGNORECASE
    )

    summary = re.sub(
        r'###\s*Kesimpulan\s*',
        r'\n[[KESIMPULAN]]\n',
        summary,
        flags=re.IGNORECASE
    )

    # Jika ada format ##, bukan ###
    summary = re.sub(
        r'##\s*Kelebihan\s*',
        r'\n[[KELEBIHAN]]\n',
        summary,
        flags=re.IGNORECASE
    )

    summary = re.sub(
        r'##\s*Kekurangan\s*',
        r'\n[[KEKURANGAN]]\n',
        summary,
        flags=re.IGNORECASE
    )

    summary = re.sub(
        r'##\s*Kesimpulan\s*',
        r'\n[[KESIMPULAN]]\n',
        summary,
        flags=re.IGNORECASE
    )

    # Bersihkan newline berlebihan
    summary = re.sub(
        r'\n{2,}',
        '\n',
        summary
    )

    # Pecah menjadi baris
    lines = summary.split('\n')

    result = []
    paragraph = []

    def add_paragraph():

        nonlocal paragraph

        if paragraph:

            text = " ".join(paragraph).strip()

            if text:
                result.append(
                    f"<p>{text}</p>"
                )

            paragraph = []

    # ===================================
    # Buat HTML
    # ===================================

    for line in lines:

        line = line.strip()

        if not line:
            add_paragraph()
            continue

        if line == "[[KELEBIHAN]]":

            add_paragraph()

            result.append(
                "<h2>Kelebihan</h2>"
            )

        elif line == "[[KEKURANGAN]]":

            add_paragraph()

            result.append(
                "<h2>Kekurangan</h2>"
            )

        elif line == "[[KESIMPULAN]]":

            add_paragraph()

            result.append(
                "<h2>Kesimpulan</h2>"
            )

        else:

            paragraph.append(line)

    add_paragraph()

    return "\n".join(result)

# ===============================
# LOAD PRODUCT
# ===============================
@st.cache_data
def load_products():

    query = """
    SELECT
        id,
        brand,
        name,
        category
    FROM products
    ORDER BY brand, name
    """

    return pd.read_sql_query(query, conn)


# ===============================
# LOAD SPECIFICATION
# ===============================
@st.cache_data
def load_specs():
    query = """
    SELECT
        p.id,
        p.brand,
        p.name,

        s.chipset,
        s.cpu,
        s.gpu,
        NULL AS gpu_memory,
        s.ram,
        s.storage,
        s.display_type,
        s.display_size,
        s.resolution,
        s.refresh_rate,
        s.rear_camera,
        s.front_camera,
        NULL AS camera,
        s.battery,
        s.charging,
        s.os,
        s.weight,
        s.fingerprint,
        s.network,
        s.waterproof

    FROM products p
    JOIN smartphone_specs s
    ON p.id = s.product_id

    UNION ALL

    SELECT
        p.id,
        p.brand,
        p.name,

        NULL AS chipset,
        l.cpu,
        l.gpu,
        l.gpu_memory,
        l.ram,
        l.storage,
        l.display_panel AS display_type,
        l.display_size,
        l.resolution,
        l.refresh_rate,
        NULL AS rear_camera,
        NULL AS front_camera,
        l.camera,
        l.battery,
        NULL AS charging,
        l.os,
        l.weight,
        NULL AS fingerprint,
        NULL AS network,
        NULL AS waterproof

    FROM products p
    JOIN laptop_specs l
    ON p.id = l.product_id
    """
    return pd.read_sql_query(query, conn)


# ===============================
# LOAD REVIEW
# ===============================
@st.cache_data
def load_reviews():

    query = """
    SELECT
        id,
        product_id,
        username AS nama_user,
        review,
        review_date AS tanggal
    FROM reviews
    """

    df = pd.read_sql_query(query, conn)
    def convert_date(x):
        if pd.isna(x):
            return pd.NaT

        for fmt in ("%d %b %Y", "%d-%b-%y", "%Y-%m-%d"):
            try:
                return pd.to_datetime(x, format=fmt)
            except:
                pass

        return pd.to_datetime(x, errors="coerce")


    df["tanggal"] = df["tanggal"].apply(convert_date)

    return df


# ===============================
# LOAD AI SUMMARY
# ===============================
@st.cache_data
def load_summary():
    query = """
    SELECT
        product_id,
        summary
    FROM product_summary
    """
    return pd.read_sql_query(query, conn)


# ===============================
# LOAD SENTIMENT
# ===============================
@st.cache_data
def load_sentiment():
    query = """
    SELECT
        r.product_id,
        s.sentiment,
        COUNT(*) AS total
    FROM sentiments s
    JOIN reviews r
    ON s.review_id = r.id
    GROUP BY r.product_id, s.sentiment
    """
    df = pd.read_sql_query(query, conn)
    # samakan ke Title Case ("positive" -> "Positive") karena data di DB huruf kecil
    df["sentiment"] = df["sentiment"].str.strip().str.title()
    return df


# ===============================
# LOAD ASPECT
# ===============================
@st.cache_data
def load_aspect():
    query = """
    SELECT
        r.product_id,
        a.aspect,
        a.sentiment,
        COUNT(*) AS total
    FROM aspects a
    JOIN reviews r
    ON a.review_id = r.id
    GROUP BY
        r.product_id,
        a.aspect,
        a.sentiment
    """
    df = pd.read_sql_query(query, conn)
    # samakan ke Title Case ("negative" -> "Negative") karena data di DB huruf kecil
    df["sentiment"] = df["sentiment"].str.strip().str.title()
    return df


products_df = load_products()

products_df["display_name"] = products_df.apply(
    lambda x:
        f"💻 {x['name']}"
        if x["category"].lower() == "laptop"
        else f"📱 {x['name']}",
    axis=1
)

produk_dict = dict(
    zip(
        products_df["display_name"],
        products_df["id"]
    )
)

spec_df = load_specs()
reviews_df = load_reviews()
summary_df = load_summary()
sentiment_df = load_sentiment()
aspect_df = load_aspect()


# ---------------------------------------------------------
# STATE
# ---------------------------------------------------------
if "selected_product_id" not in st.session_state:
    st.session_state.selected_product_id = None


def pilih_produk(product_id):
    st.session_state.selected_product_id = product_id


# ---------------------------------------------------------
# HERO + SEARCH
# ---------------------------------------------------------

def search_products(searchterm: str):

    if not searchterm:
        return []

    hasil = products_df[
        products_df["display_name"].str.contains(
            searchterm,
            case=False,
            na=False
        )
    ]

    return hasil["display_name"].tolist()

st.markdown(
    '<div class="hero-title">🔍 Cari Produk Elektronik</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-sub">Cari smartphone atau laptop berdasarkan nama produk.</div>',
    unsafe_allow_html=True,
)

selected = st_searchbox(
    search_products,
    placeholder="Cari smartphone atau laptop...",
    clear_on_submit=False,
)

if selected:

    product_id = produk_dict[selected]
    pilih_produk(product_id)


# ---------------------------------------------------------
# HALAMAN DETAIL PRODUK
# ---------------------------------------------------------
product_id = st.session_state.selected_product_id

if product_id:
    produk = products_df[products_df["id"] == product_id]["display_name"].iloc[0]
    spek_produk = spec_df[spec_df["id"] == product_id]
    if spek_produk.empty:
        spek_row = None
    else:
        spek_row = spek_produk.iloc[0]

    review_produk = reviews_df[reviews_df["product_id"] == product_id]
    summary_row = summary_df[summary_df["product_id"] == product_id]
    sentiment_produk = sentiment_df[sentiment_df["product_id"] == product_id]
    aspect_produk = aspect_df[aspect_df["product_id"] == product_id]

    # ===================================
    # 1. PRODUCT CARD
    # ===================================
    tgl_terbaru = review_produk["tanggal"].max()
    tgl_terbaru_str = tgl_terbaru.strftime("%d %b %Y") if pd.notna(tgl_terbaru) else "-"

    st.markdown(f"""
    <div class="product-card">
        <p class="product-title">{produk}</p>
        <div class="stat-row">
            <div class="stat-item">💬 <b>{len(review_produk)}</b> review terkumpul</div>
            <div class="stat-item">🗓️ Review terbaru <b>{tgl_terbaru_str}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===================================
    # RINGKASAN AI
    # ===================================

    st.markdown(
        '<div class="section-label">🤖 RINGKASAN AI</div>',
        unsafe_allow_html=True
    )

    summary_cursor = conn.cursor()

    summary_cursor.execute("""
        SELECT summary
        FROM product_summary
        WHERE product_id = ?
    """, (product_id,))

    summary_result = summary_cursor.fetchone()


    # ===================================
    # TAMPILKAN SUMMARY
    # ===================================

    if summary_result and summary_result[0]:

        summary = summary_result[0]

        formatted_summary = format_ai_summary(summary)

        st.markdown(
            f"""
            <div class="ai-card">
                {formatted_summary}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.info(
            "Ringkasan AI belum tersedia untuk produk ini."
        )

    # ===================================
    # 3. METRIC POSITIVE / NEUTRAL / NEGATIVE
    # ===================================
    st.markdown('<div class="section-label">🔢 Ringkasan Sentiment</div>', unsafe_allow_html=True)

    total_positive = int(sentiment_produk.loc[sentiment_produk["sentiment"] == "Positive", "total"].sum())
    total_neutral = int(sentiment_produk.loc[sentiment_produk["sentiment"] == "Neutral", "total"].sum())
    total_negative = int(sentiment_produk.loc[sentiment_produk["sentiment"] == "Negative", "total"].sum())

    col_pos, col_neu, col_neg = st.columns(3)
    col_pos.metric("😊 Positive", total_positive)
    col_neu.metric("😐 Neutral", total_neutral)
    col_neg.metric("😞 Negative", total_negative)

    # ===================================
    # 4. OVERALL SENTIMENT
    # ===================================
    st.markdown('<div class="section-label">📊 Overall Sentiment</div>', unsafe_allow_html=True)

    if sentiment_produk.empty:
        st.markdown('<div class="empty-hint">Belum ada data sentiment untuk produk ini.</div>', unsafe_allow_html=True)
    else:
        fig_overall = px.pie(
            sentiment_produk,
            names="sentiment",
            values="total",
            color="sentiment",
            color_discrete_map={
                "Positive": "#2ecc71",
                "Neutral": "#f1c40f",
                "Negative": "#e74c3c",
            },
        )
        fig_overall.update_traces(textposition="inside", textinfo="percent+label")
        fig_overall.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="#F4F5F7",
            plot_bgcolor="#F4F5F7",
            font=dict(color="#14161A"),
            legend=dict(font=dict(color="#14161A")),
        )
        st.plotly_chart(fig_overall, use_container_width=True)

    # ===================================
    # 5. ASPECT SENTIMENT (horizontal stacked bar)
    # ===================================
    st.markdown('<div class="section-label">📈 Aspect Sentiment</div>', unsafe_allow_html=True)

    if aspect_produk.empty:
        st.markdown('<div class="empty-hint">Belum ada data aspect sentiment untuk produk ini.</div>', unsafe_allow_html=True)
    else:
        chart = (
            aspect_produk
            .pivot_table(index="aspect", columns="sentiment", values="total", fill_value=0)
            .reset_index()
        )

        # pastikan semua kolom sentiment ada
        for col in ["Positive", "Neutral", "Negative"]:
            if col not in chart.columns:
                chart[col] = 0

        # urutkan berdasarkan jumlah review
        chart["Total"] = chart["Positive"] + chart["Neutral"] + chart["Negative"]
        chart = chart.sort_values("Total", ascending=True)

        fig_aspect = px.bar(
            chart,
            y="aspect",
            x=["Positive", "Neutral", "Negative"],
            orientation="h",
            barmode="stack",
            color_discrete_map={
                "Positive": "#2ecc71",
                "Neutral": "#f1c40f",
                "Negative": "#e74c3c",
            },
        )
        fig_aspect.update_layout(
            height=max(400, len(chart) * 35),
            xaxis_title="Jumlah Review",
            yaxis_title="Aspect",
            legend_title="Sentiment",
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="#F4F5F7",
            plot_bgcolor="#F4F5F7",
            font=dict(color="#14161A"),
            legend=dict(font=dict(color="#14161A")),
        )
        st.plotly_chart(fig_aspect, use_container_width=True)

    # ===================================
    # 6. SPESIFIKASI
    # ===================================
    st.markdown(
        '<div class="section-label">⚙️ Spesifikasi</div>',
        unsafe_allow_html=True
    )

    if spek_row is None:

        st.info("Spesifikasi belum tersedia untuk produk ini.")

    else:

        items_html = ""

        for kolom_nama, (icon, label_bagus) in SPEK_LABELS.items():

            if kolom_nama in spek_row.index and pd.notna(spek_row[kolom_nama]):

                items_html += (
                    f'<div class="spek-item">'
                    f'<div class="spek-label">{icon} {label_bagus}</div>'
                    f'<div class="spek-value">{spek_row[kolom_nama]}</div>'
                    f'</div>'
                )

        st.markdown(
            f'<div class="spek-grid">{items_html}</div>',
            unsafe_allow_html=True
        )

    # ===================================
    # 7. REVIEW
    # ===================================
    st.markdown('<div class="section-label">💬 Review Pengguna</div>', unsafe_allow_html=True)

    cari_review = st.text_input(
        "cari_review", placeholder="Cari kata kunci di dalam review...", label_visibility="collapsed",
    )
    tampil_review = review_produk
    if cari_review:
        tampil_review = tampil_review[tampil_review["review"].str.contains(cari_review, case=False, na=False)]

    if tampil_review.empty:
        st.markdown('<div class="empty-hint">Tidak ada review yang cocok.</div>', unsafe_allow_html=True)
    else:
        jumlah_tampil = st.session_state.get("jumlah_review_tampil", 6)
        for _, r in tampil_review.head(jumlah_tampil).iterrows():
            tgl = r["tanggal"].strftime("%d %b %Y") if pd.notna(r["tanggal"]) else "-"
            teks = str(r["review"]).replace("\n", " ").strip()
            st.markdown(f"""
            <div class="review-card">
                <div class="review-head">
                    <span class="review-name">👤 {r['nama_user']}</span>
                    <span class="review-date">{tgl}</span>
                </div>
                <div class="review-text">{teks}</div>
            </div>
            """, unsafe_allow_html=True)

        if len(tampil_review) > jumlah_tampil:
            if st.button(f"Tampilkan lebih banyak review ({len(tampil_review) - jumlah_tampil} lagi)"):
                st.session_state.jumlah_review_tampil = jumlah_tampil + 6
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Cari Perangkat lain"):
        st.session_state.selected_product_id = None
        st.session_state.jumlah_review_tampil = 6
        st.rerun()

elif st.session_state.selected_product_id is None:
    st.markdown(
        """
        <div class="empty-hint">
            🔍 Cari smartphone atau laptop pada kolom pencarian di atas.
        </div>
        """,
        unsafe_allow_html=True,
    )
