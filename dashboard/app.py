import html
import re
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_searchbox import st_searchbox
# from ai_summary import generate_summary, save_summary

# ---------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="ElectroLens AI — Analisis Spek & Review Elektronik",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
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
# GAYA VISUAL (Modern Clean Dashboard, Light Mode Konsisten)
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

:root {
    --bg:          #F4F6FA;
    --surface:     #FFFFFF;
    --surface-alt: #F8FAFC;
    --border:      #E2E8F0;
    --border-hover:#CBD5E1;
    --text:        #0F172A;
    --text-sec:    #334155;
    --text-mute:   #64748B;
    --accent:      #2563EB;
    --accent-dark: #1D4ED8;
    --accent-bg:   #EFF6FF;
    --accent-bdr:  #BFDBFE;
    --good:        #059669;
    --good-bg:     #ECFDF5;
    --good-bdr:    #A7F3D0;
    --warn:        #D97706;
    --warn-bg:     #FFFBEB;
    --warn-bdr:    #FDE68A;
    --bad:         #DC2626;
    --bad-bg:      #FEF2F2;
    --bad-bdr:     #FECACA;
    --shadow-sm:   0 1px 3px rgba(15, 23, 42, 0.04), 0 1px 2px rgba(15, 23, 42, 0.02);
    --shadow-md:   0 4px 16px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
}

/* Constrain main container so wide layout looks balanced and centered */
.block-container {
    max-width: 1180px !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

/* Plotly Chart Card Container */
[data-testid="stPlotlyChart"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    padding: 0.5rem 0.6rem !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden !important;
}

/* Horizontal Radio Pills for Category Filter (Desktop & Mobile Friendly) */
div[data-testid="stRadio"] > div[role="radiogroup"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    gap: 0.5rem !important;
    background: var(--surface) !important;
    padding: 0.35rem !important;
    border-radius: 14px !important;
    border: 1px solid var(--border) !important;
    width: fit-content !important;
    max-width: 100% !important;
    box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 0.4rem 0.9rem !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    border: 1px solid transparent !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    background: var(--accent-bg) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"],
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background: var(--accent) !important;
    color: #FFFFFF !important;
    box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p,
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.02em;
    color: var(--text) !important;
}

/* Paksa warna teks bawaan Streamlit tetap gelap dan tajam */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stText"],
label,
.stMarkdown,
.stMarkdown p {
    color: var(--text);
}

/* Search & Text Inputs */
div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1.5px solid var(--border) !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.95rem !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: var(--text-mute) !important;
    opacity: 1;
}
div[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-bg) !important;
}

/* Selectbox styling */
div[data-baseweb="select"] > div {
    background-color: var(--surface) !important;
    border-radius: 12px !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    color: var(--text) !important;
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 0.55rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.16s ease !important;
}
.stButton > button p {
    color: var(--text) !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--accent-bg) !important;
    transform: translateY(-1px);
    box-shadow: var(--shadow-md) !important;
}
.stButton > button:hover p {
    color: var(--accent) !important;
}

/* Hero Banner */
.hero-wrap {
    background: linear-gradient(135deg, #FFFFFF 0%, #EFF6FF 100%);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 2.2rem 2rem 1.8rem 2rem;
    margin-bottom: 1.2rem;
    text-align: center;
    box-shadow: var(--shadow-md);
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: var(--accent-bg);
    color: var(--accent) !important;
    border: 1px solid var(--accent-bdr);
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 0.3rem 0.85rem;
    border-radius: 999px;
    margin-bottom: 0.8rem;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.25rem;
    font-weight: 700;
    margin: 0 0 0.45rem 0;
    color: var(--text) !important;
    line-height: 1.2;
}
.hero-sub {
    color: var(--text-mute) !important;
    margin: 0 auto 1.1rem auto;
    max-width: 600px;
    font-size: 0.98rem;
    line-height: 1.55;
}
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 0.75rem;
    flex-wrap: wrap;
}
.hero-stat-pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.32rem 0.85rem;
    font-size: 0.8rem;
    color: var(--text-sec) !important;
    font-weight: 500;
}
.hero-stat-pill b {
    color: var(--accent) !important;
    font-family: 'JetBrains Mono', monospace;
}

/* Section Header */
.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.3rem 0.75rem;
    margin: 1.8rem 0 0.85rem 0;
}
.section-label {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--accent) !important;
    display: flex;
    align-items: center;
    gap: 0.45rem;
    margin: 0;
}
.section-sub {
    font-size: 0.82rem;
    color: var(--text-mute) !important;
}

/* Product Detail Hero Card */
.product-card {
    background: var(--surface) !important;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 1.6rem 1.8rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
    box-shadow: var(--shadow-md);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 1rem;
}
.product-badges {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    margin-bottom: 0.55rem;
    flex-wrap: wrap;
}
.badge-cat {
    background: var(--accent-bg);
    color: var(--accent) !important;
    border: 1px solid var(--accent-bdr);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.22rem 0.7rem;
    border-radius: 999px;
}
.badge-brand {
    background: var(--surface-alt);
    color: var(--text-sec) !important;
    border: 1px solid var(--border);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.22rem 0.7rem;
    border-radius: 999px;
}
.product-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.85rem;
    font-weight: 700;
    margin: 0;
    color: var(--text) !important;
    line-height: 1.2;
}
.stat-row {
    display: flex;
    gap: 1.25rem;
    margin-top: 0.85rem;
    flex-wrap: wrap;
}
.stat-item {
    background: var(--surface-alt);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.4rem 0.75rem;
    color: var(--text-sec) !important;
    font-size: 0.84rem;
}
.stat-item b {
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace;
}

/* Product Score Box inside Header */
.score-box {
    background: var(--good-bg);
    border: 1px solid var(--good-bdr);
    border-radius: 16px;
    padding: 0.85rem 1.25rem;
    text-align: center;
    min-width: 135px;
}
.score-box.warn {
    background: var(--warn-bg);
    border-color: var(--warn-bdr);
}
.score-box.bad {
    background: var(--bad-bg);
    border-color: var(--bad-bdr);
}
.score-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--good) !important;
    line-height: 1.1;
}
.score-box.warn .score-val { color: var(--warn) !important; }
.score-box.bad .score-val { color: var(--bad) !important; }
.score-lbl {
    font-size: 0.74rem;
    font-weight: 600;
    color: var(--text-sec) !important;
    margin-top: 0.2rem;
}

/* Structured AI Summary Cards */
.ai-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
}
@media (max-width: 768px) {
    .ai-grid { grid-template-columns: 1fr; }
}
.ai-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow-sm);
}
.ai-box.pros {
    border-top: 4px solid var(--good);
    background: linear-gradient(180deg, #F2FDF9 0%, #FFFFFF 45%);
}
.ai-box.cons {
    border-top: 4px solid var(--bad);
    background: linear-gradient(180deg, #FEF5F5 0%, #FFFFFF 45%);
}
.ai-box.verdict {
    border-left: 4px solid var(--accent);
    background: linear-gradient(90deg, #EFF6FF 0%, #FFFFFF 50%);
}
.ai-box-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    margin: 0 0 0.55rem 0;
    display: flex;
    align-items: center;
    gap: 0.45rem;
}
.ai-box.pros .ai-box-title { color: var(--good) !important; }
.ai-box.cons .ai-box-title { color: var(--bad) !important; }
.ai-box.verdict .ai-box-title { color: var(--accent) !important; }
.ai-box-body {
    font-size: 0.92rem;
    line-height: 1.65;
    color: var(--text-sec) !important;
    margin: 0;
}

/* KPI Metric Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.85rem;
    margin-bottom: 1rem;
}
@media (max-width: 768px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    box-shadow: var(--shadow-sm);
}
.kpi-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}
.kpi-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-mute) !important;
}
.kpi-pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
}
.kpi-pct.pos { background: var(--good-bg); color: var(--good) !important; }
.kpi-pct.neu { background: var(--warn-bg); color: var(--warn) !important; }
.kpi-pct.neg { background: var(--bad-bg); color: var(--bad) !important; }
.kpi-pct.tot { background: var(--accent-bg); color: var(--accent) !important; }
.kpi-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--text) !important;
    line-height: 1.15;
}
.kpi-bar-bg {
    height: 6px;
    background: var(--bg);
    border-radius: 999px;
    margin-top: 0.65rem;
    overflow: hidden;
}
.kpi-bar-fill {
    height: 100%;
    border-radius: 999px;
}

/* Aspect Highlight Pills */
.aspect-summary-bar {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.85rem;
    margin-bottom: 0.85rem;
}
@media (max-width: 768px) {
    .aspect-summary-bar { grid-template-columns: 1fr; }
}
.aspect-pill-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.9rem 1.1rem;
    box-shadow: var(--shadow-sm);
}
.aspect-pill-head {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.5rem;
}
.aspect-pill-head.good { color: var(--good) !important; }
.aspect-pill-head.bad { color: var(--bad) !important; }
.chip-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}
.aspect-chip {
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.24rem 0.65rem;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}
.aspect-chip.good {
    background: var(--good-bg);
    color: var(--good) !important;
    border: 1px solid var(--good-bdr);
}
.aspect-chip.bad {
    background: var(--bad-bg);
    color: var(--bad) !important;
    border: 1px solid var(--bad-bdr);
}

/* Specs Grid */
.spek-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 0.75rem;
    background: var(--surface) !important;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
}
.spek-item {
    padding: 0.7rem 0.85rem;
    border-radius: 12px;
    background: var(--surface-alt) !important;
    border: 1px solid var(--border);
    transition: border-color 0.15s ease;
}
.spek-item:hover {
    border-color: var(--accent-bdr);
}
.spek-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-mute) !important;
    margin-bottom: 0.2rem;
}
.spek-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text) !important;
    word-break: break-word;
}

/* Review Cards */
.review-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.85rem;
    margin-top: 0.5rem;
}
@media (max-width: 768px) {
    .review-grid { grid-template-columns: 1fr; }
}
.review-card {
    background: var(--surface) !important;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    box-shadow: var(--shadow-sm);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.review-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.55rem;
}
.review-user-wrap {
    display: flex;
    align-items: center;
    gap: 0.55rem;
}
.review-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: var(--accent-bg);
    color: var(--accent) !important;
    border: 1px solid var(--accent-bdr);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.82rem;
    flex-shrink: 0;
}
.review-name {
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text) !important;
    line-height: 1.2;
}
.review-meta {
    color: var(--text-mute) !important;
    font-size: 0.74rem;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.1rem;
}
.sent-badge {
    font-size: 0.73rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 999px;
    white-space: nowrap;
}
.sent-badge.Positive {
    background: var(--good-bg);
    color: var(--good) !important;
    border: 1px solid var(--good-bdr);
}
.sent-badge.Neutral {
    background: var(--warn-bg);
    color: var(--warn) !important;
    border: 1px solid var(--warn-bdr);
}
.sent-badge.Negative {
    background: var(--bad-bg);
    color: var(--bad) !important;
    border: 1px solid var(--bad-bdr);
}
.review-text {
    font-size: 0.89rem;
    line-height: 1.6;
    color: var(--text-sec) !important;
    margin-bottom: 0.6rem;
}
.review-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    margin-top: auto;
    padding-top: 0.45rem;
    border-top: 1px dashed var(--border);
}
.review-tag {
    font-size: 0.7rem;
    font-weight: 500;
    background: var(--surface-alt);
    color: var(--text-mute) !important;
    border: 1px solid var(--border);
    padding: 0.12rem 0.5rem;
    border-radius: 6px;
}

/* Catalog Card on Home */
.catalog-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.05rem 1.15rem;
    margin-bottom: 0.35rem;
    box-shadow: var(--shadow-sm);
}
.catalog-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.35rem;
}
.catalog-brand {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent) !important;
}
.catalog-cat {
    font-size: 0.72rem;
    color: var(--text-mute) !important;
    background: var(--surface-alt);
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    border: 1px solid var(--border);
}
.catalog-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.02rem;
    font-weight: 700;
    color: var(--text) !important;
    margin-bottom: 0.55rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.catalog-stats {
    display: flex;
    justify-content: space-between;
    font-size: 0.78rem;
    color: var(--text-mute) !important;
}
.catalog-stats b {
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-sec) !important;
}

.empty-hint {
    text-align: center;
    color: var(--text-mute) !important;
    background: var(--surface);
    border: 1px dashed var(--border);
    border-radius: 16px;
    padding: 2.2rem 1rem;
    font-size: 0.92rem;
}

/* =========================================================
   RESPONSIVE BREAKPOINTS (DESKTOP, TABLET, MOBILE)
   ========================================================= */

/* Desktop Large (>= 1024px): 3-column spec grid */
@media (min-width: 1024px) {
    .spek-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}

/* Tablet (<= 992px) */
@media (max-width: 992px) {
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1.15rem !important;
        padding-right: 1.15rem !important;
    }
    .hero-wrap {
        padding: 1.75rem 1.4rem 1.4rem 1.4rem;
    }
    .hero-title {
        font-size: 1.85rem;
    }
    .product-title {
        font-size: 1.55rem;
    }
    .spek-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

/* Mobile & Phablet (<= 640px) */
@media (max-width: 640px) {
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
    .hero-wrap {
        padding: 1.25rem 0.95rem 1.1rem 0.95rem;
        border-radius: 16px;
        margin-bottom: 0.9rem;
    }
    .hero-badge {
        font-size: 0.68rem;
        padding: 0.24rem 0.65rem;
    }
    .hero-title {
        font-size: 1.4rem;
    }
    .hero-sub {
        font-size: 0.86rem;
        margin-bottom: 0.85rem;
    }
    .hero-stats {
        gap: 0.45rem;
    }
    .hero-stat-pill {
        font-size: 0.73rem;
        padding: 0.24rem 0.65rem;
    }
    .section-header {
        flex-direction: column;
        align-items: flex-start;
        margin: 1.35rem 0 0.65rem 0;
    }
    .section-label {
        font-size: 0.8rem;
    }
    .section-sub {
        font-size: 0.76rem;
    }
    .product-card {
        padding: 1.15rem 1.05rem;
        border-radius: 16px;
        flex-direction: column;
        align-items: stretch;
    }
    .product-title {
        font-size: 1.35rem;
    }
    .stat-row {
        gap: 0.45rem;
        margin-top: 0.65rem;
    }
    .stat-item {
        font-size: 0.78rem;
        padding: 0.32rem 0.6rem;
        flex: 1 1 auto;
    }
    .score-box {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.7rem 1rem;
        border-radius: 12px;
    }
    .score-val {
        font-size: 1.35rem;
    }
    .score-lbl {
        margin-top: 0;
        font-size: 0.8rem;
    }
    .ai-box {
        padding: 1rem 1.05rem;
        border-radius: 14px;
    }
    .ai-box-body {
        font-size: 0.86rem;
    }
    .kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.6rem;
    }
    .kpi-card {
        padding: 0.85rem 0.9rem;
        border-radius: 14px;
    }
    .kpi-val {
        font-size: 1.35rem;
    }
    .kpi-label {
        font-size: 0.74rem;
    }
    .kpi-pct {
        font-size: 0.68rem;
        padding: 0.1rem 0.4rem;
    }
    .spek-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.55rem;
        padding: 0.85rem;
        border-radius: 14px;
    }
    .spek-item {
        padding: 0.55rem 0.65rem;
    }
    .spek-label {
        font-size: 0.7rem;
    }
    .spek-value {
        font-size: 0.8rem;
    }
    .review-card {
        padding: 0.9rem 1rem;
        border-radius: 14px;
    }
    .review-head {
        flex-wrap: wrap;
    }
    .review-text {
        font-size: 0.85rem;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        width: 100% !important;
        justify-content: space-between !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        flex: 1 1 auto !important;
        justify-content: center !important;
        text-align: center !important;
        padding: 0.38rem 0.5rem !important;
        font-size: 0.8rem !important;
    }
}

/* Extra Small Mobile (<= 400px) */
@media (max-width: 400px) {
    .spek-grid {
        grid-template-columns: 1fr;
    }
}
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
        check_same_thread=False,
    )


conn = get_connection()


# ===================================
# PARSE & FORMAT RINGKASAN AI
# ===================================
def parse_ai_summary(summary: str):
    """
    Memecah teks summary AI menjadi 3 bagian terstruktur:
    (kelebihan, kekurangan, kesimpulan, fallback_html)
    """
    if not summary:
        return None, None, None, ""

    clean = html.escape(str(summary))
    clean = re.sub(r"^\s*##\s*Ringkasan\s*", "", clean, flags=re.IGNORECASE)

    clean = re.sub(r"#{2,3}\s*Kelebihan\s*", "\n[[KELEBIHAN]]\n", clean, flags=re.IGNORECASE)
    clean = re.sub(r"#{2,3}\s*Kekurangan\s*", "\n[[KEKURANGAN]]\n", clean, flags=re.IGNORECASE)
    clean = re.sub(r"#{2,3}\s*Kesimpulan\s*", "\n[[KESIMPULAN]]\n", clean, flags=re.IGNORECASE)

    sections = {"KELEBIHAN": [], "KEKURANGAN": [], "KESIMPULAN": [], "OTHER": []}
    current = "OTHER"

    for raw_line in clean.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        if line == "[[KELEBIHAN]]":
            current = "KELEBIHAN"
        elif line == "[[KEKURANGAN]]":
            current = "KEKURANGAN"
        elif line == "[[KESIMPULAN]]":
            current = "KESIMPULAN"
        else:
            sections[current].append(line)

    kelebihan = " ".join(sections["KELEBIHAN"]).strip()
    kekurangan = " ".join(sections["KEKURANGAN"]).strip()
    kesimpulan = " ".join(sections["KESIMPULAN"]).strip()
    other = " ".join(sections["OTHER"]).strip()

    return kelebihan, kekurangan, kesimpulan, other


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
# LOAD REVIEW (WITH SENTIMENT & ASPECTS)
# ===============================
@st.cache_data
def load_reviews():
    query = """
    SELECT
        r.id,
        r.product_id,
        r.username AS nama_user,
        r.review,
        r.review_date AS tanggal,
        r.source,
        s.sentiment,
        s.confidence,
        GROUP_CONCAT(DISTINCT a.aspect) AS aspects_list
    FROM reviews r
    LEFT JOIN sentiments s ON r.id = s.review_id
    LEFT JOIN aspects a ON r.id = a.review_id
    GROUP BY r.id
    """
    df = pd.read_sql_query(query, conn)

    def convert_date(x):
        if pd.isna(x):
            return pd.NaT
        for fmt in ("%d %b %Y", "%d-%b-%y", "%Y-%m-%d"):
            try:
                return pd.to_datetime(x, format=fmt)
            except Exception:
                pass
        return pd.to_datetime(x, errors="coerce")

    df["tanggal"] = df["tanggal"].apply(convert_date)
    df["sentiment"] = df["sentiment"].fillna("Neutral").str.strip().str.title()
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
    df["sentiment"] = df["sentiment"].str.strip().str.title()
    return df


products_df = load_products()
products_df["display_name"] = products_df.apply(
    lambda x: f"💻 {x['name']}" if x["category"].lower() == "laptop" else f"📱 {x['name']}",
    axis=1,
)

produk_dict = dict(zip(products_df["display_name"], products_df["id"]))

spec_df = load_specs()
reviews_df = load_reviews()
summary_df = load_summary()
sentiment_df = load_sentiment()
aspect_df = load_aspect()


# ---------------------------------------------------------
# STATE MANAGEMENT
# ---------------------------------------------------------
if "selected_product_id" not in st.session_state:
    st.session_state.selected_product_id = None
if "searchbox_version" not in st.session_state:
    st.session_state.searchbox_version = 0
if "last_searchbox_val" not in st.session_state:
    st.session_state.last_searchbox_val = None
if "jumlah_review_tampil" not in st.session_state:
    st.session_state.jumlah_review_tampil = 6
if "katalog_kategori" not in st.session_state:
    st.session_state.katalog_kategori = "Semua"


def pilih_produk(product_id):
    if st.session_state.selected_product_id != product_id:
        st.session_state.jumlah_review_tampil = 6
    st.session_state.selected_product_id = product_id


def reset_ke_katalog():
    st.session_state.selected_product_id = None
    st.session_state.last_searchbox_val = None
    st.session_state.searchbox_version += 1
    st.session_state.jumlah_review_tampil = 6


# ---------------------------------------------------------
# HERO + SEARCH BAR
# ---------------------------------------------------------
def search_products(searchterm: str):
    if not searchterm:
        return products_df["display_name"].tolist()
    hasil = products_df[
        products_df["display_name"].str.contains(searchterm, case=False, na=False)
        | products_df["brand"].str.contains(searchterm, case=False, na=False)
    ]
    return hasil["display_name"].tolist()


total_produk_count = len(products_df)
total_review_count = len(reviews_df)
total_aspect_count = int(aspect_df["total"].sum()) if not aspect_df.empty else 0

st.markdown(
    f"""
    <div class="hero-wrap">
        <div class="hero-badge">✨ AI-Powered Electronics Review Intelligence</div>
        <h1 class="hero-title">🔍 Cari & Analisis Produk Elektronik</h1>
        <p class="hero-sub">
            Eksplorasi spesifikasi lengkap, distribusi sentimen pengguna, analisis per aspek,
            serta ringkasan kelebihan & kekurangan berbasis AI untuk smartphone dan laptop.
        </p>
        <div class="hero-stats">
            <span class="hero-stat-pill">📦 <b>{total_produk_count}</b> Perangkat</span>
            <span class="hero-stat-pill">💬 <b>{total_review_count:,}</b> Ulasan Pengguna</span>
            <span class="hero-stat-pill">🏷️ <b>{total_aspect_count:,}</b> Aspek Terpetakan</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

selected = st_searchbox(
    search_products,
    placeholder="Ketik nama smartphone, laptop, atau brand (misal: Samsung, iPhone, ASUS, MacBook)...",
    clear_on_submit=False,
    key=f"product_searchbox_{st.session_state.searchbox_version}",
)

if selected and selected != st.session_state.last_searchbox_val:
    st.session_state.last_searchbox_val = selected
    pilih_produk(produk_dict[selected])


# ---------------------------------------------------------
# HALAMAN DETAIL PRODUK
# ---------------------------------------------------------
product_id = st.session_state.selected_product_id

if product_id:
    prod_meta = products_df[products_df["id"] == product_id].iloc[0]
    produk_nama = prod_meta["name"]
    produk_brand = prod_meta["brand"]
    produk_kategori = prod_meta["category"]
    produk_icon = "💻" if produk_kategori.lower() == "laptop" else "📱"

    spek_produk = spec_df[spec_df["id"] == product_id]
    spek_row = spek_produk.iloc[0] if not spek_produk.empty else None

    review_produk = reviews_df[reviews_df["product_id"] == product_id]
    sentiment_produk = sentiment_df[sentiment_df["product_id"] == product_id]
    aspect_produk = aspect_df[aspect_df["product_id"] == product_id]

    # Top bar navigasi kembali
    nav_col1, nav_col2 = st.columns([1, 3])
    with nav_col1:
        if st.button("← Kembali ke Katalog Perangkat"):
            reset_ke_katalog()
            st.rerun()

    # Hitung metrik sentimen utama
    total_positive = int(sentiment_produk.loc[sentiment_produk["sentiment"] == "Positive", "total"].sum())
    total_neutral = int(sentiment_produk.loc[sentiment_produk["sentiment"] == "Neutral", "total"].sum())
    total_negative = int(sentiment_produk.loc[sentiment_produk["sentiment"] == "Negative", "total"].sum())
    total_semua_sent = total_positive + total_neutral + total_negative

    pos_pct = round((total_positive / total_semua_sent) * 100, 1) if total_semua_sent > 0 else 0.0
    neu_pct = round((total_neutral / total_semua_sent) * 100, 1) if total_semua_sent > 0 else 0.0
    neg_pct = round((total_negative / total_semua_sent) * 100, 1) if total_semua_sent > 0 else 0.0

    score_class = ""
    if pos_pct < 40:
        score_class = "bad"
    elif pos_pct < 60:
        score_class = "warn"

    tgl_terbaru = review_produk["tanggal"].max()
    tgl_terbaru_str = tgl_terbaru.strftime("%d %b %Y") if pd.notna(tgl_terbaru) else "-"
    sources_str = ", ".join(review_produk["source"].dropna().unique().tolist()) or "-"

    # ===================================
    # 1. PRODUCT HERO CARD
    # ===================================
    st.markdown(
        f"""
        <div class="product-card">
            <div>
                <div class="product-badges">
                    <span class="badge-cat">{produk_icon} {html.escape(produk_kategori)}</span>
                    <span class="badge-brand">🏷️ {html.escape(produk_brand)}</span>
                </div>
                <p class="product-title">{html.escape(produk_nama)}</p>
                <div class="stat-row">
                    <div class="stat-item">💬 <b>{len(review_produk)}</b> ulasan dianalisis</div>
                    <div class="stat-item">🗓️ Ulasan terbaru: <b>{tgl_terbaru_str}</b></div>
                    <div class="stat-item">🌐 Sumber: <b>{html.escape(sources_str)}</b></div>
                </div>
            </div>
            <div class="score-box {score_class}">
                <div class="score-val">{pos_pct}%</div>
                <div class="score-lbl">Sentimen Positif</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ===================================
    # 2. RINGKASAN AI (3-CARD STRUCTURED)
    # ===================================
    st.markdown(
        """
        <div class="section-header">
            <div class="section-label">🤖 Ringkasan Analisis AI (Qwen LLM)</div>
            <div class="section-sub">Disintesis otomatis dari ekstraksi sentimen per aspek</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    summary_cursor = conn.cursor()
    summary_cursor.execute(
        "SELECT summary FROM product_summary WHERE product_id = ?",
        (product_id,),
    )
    summary_result = summary_cursor.fetchone()

    if summary_result and summary_result[0]:
        kelebihan, kekurangan, kesimpulan, other_txt = parse_ai_summary(summary_result[0])

        if kelebihan or kekurangan or kesimpulan:
            pros_html = kelebihan if kelebihan else "Tidak ada catatan kelebihan spesifik."
            cons_html = kekurangan if kekurangan else "Tidak ada keluhan dominan yang tercatat."
            st.markdown(
                f"""
                <div class="ai-grid">
                    <div class="ai-box pros">
                        <div class="ai-box-title">✅ Kelebihan Utama</div>
                        <p class="ai-box-body">{pros_html}</p>
                    </div>
                    <div class="ai-box cons">
                        <div class="ai-box-title">⚠️ Kekurangan & Keluhan</div>
                        <p class="ai-box-body">{cons_html}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if kesimpulan:
                st.markdown(
                    f"""
                    <div class="ai-box verdict">
                        <div class="ai-box-title">💡 Kesimpulan Akhir</div>
                        <p class="ai-box-body">{kesimpulan}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f"""
                <div class="ai-box verdict">
                    <div class="ai-box-title">🤖 Ringkasan Produk</div>
                    <p class="ai-box-body">{other_txt}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Ringkasan AI belum tersedia untuk produk ini.")

    # ===================================
    # 3. KPI SENTIMENT CARDS
    # ===================================
    st.markdown(
        """
        <div class="section-header">
            <div class="section-label">📊 Ikhtisar Sentimen & Aspek</div>
            <div class="section-sub">Klasifikasi menggunakan model RoBERTa & ekstraksi aspek spaCy</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-label">💬 Total Ulasan</span>
                    <span class="kpi-pct tot">100%</span>
                </div>
                <div class="kpi-val">{total_semua_sent}</div>
                <div class="kpi-bar-bg">
                    <div class="kpi-bar-fill" style="width: 100%; background: #2563EB;"></div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-label">😊 Positive</span>
                    <span class="kpi-pct pos">{pos_pct}%</span>
                </div>
                <div class="kpi-val">{total_positive}</div>
                <div class="kpi-bar-bg">
                    <div class="kpi-bar-fill" style="width: {pos_pct}%; background: #10B981;"></div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-label">😐 Neutral</span>
                    <span class="kpi-pct neu">{neu_pct}%</span>
                </div>
                <div class="kpi-val">{total_neutral}</div>
                <div class="kpi-bar-bg">
                    <div class="kpi-bar-fill" style="width: {neu_pct}%; background: #F59E0B;"></div>
                </div>
            </div>
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-label">😞 Negative</span>
                    <span class="kpi-pct neg">{neg_pct}%</span>
                </div>
                <div class="kpi-val">{total_negative}</div>
                <div class="kpi-bar-bg">
                    <div class="kpi-bar-fill" style="width: {neg_pct}%; background: #EF4444;"></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ===================================
    # 4. CHARTS: OVERALL SENTIMENT & ASPECT SENTIMENT
    # ===================================
    chart_col1, chart_col2 = st.columns([4, 6], gap="medium")

    with chart_col1:
        st.markdown("**🎯 Proporsi Sentimen Keseluruhan**")
        if sentiment_produk.empty:
            st.markdown('<div class="empty-hint">Belum ada data sentiment.</div>', unsafe_allow_html=True)
        else:
            fig_overall = px.pie(
                sentiment_produk,
                names="sentiment",
                values="total",
                hole=0.58,
                color="sentiment",
                category_orders={"sentiment": ["Positive", "Neutral", "Negative"]},
                color_discrete_map={
                    "Positive": "#10B981",
                    "Neutral": "#F59E0B",
                    "Negative": "#EF4444",
                },
            )
            fig_overall.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>Jumlah: %{value} review (%{percent})<extra></extra>",
                marker=dict(line=dict(color="#FFFFFF", width=2)),
            )
            fig_overall.update_layout(
                height=380,
                margin=dict(l=15, r=15, t=20, b=20),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(family="Inter, sans-serif", color="#0F172A", size=13),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.12,
                    xanchor="center",
                    x=0.5,
                    font=dict(color="#0F172A"),
                ),
                annotations=[
                    dict(
                        text=f"<b>{total_semua_sent}</b><br><span style='font-size:11px;color:#64748B'>Ulasan</span>",
                        x=0.5,
                        y=0.5,
                        font_size=18,
                        showarrow=False,
                        font=dict(color="#0F172A"),
                    )
                ],
            )
            st.plotly_chart(
                fig_overall,
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )

    with chart_col2:
        st.markdown("**📈 Distribusi Sentimen per Aspek Fitur**")
        if aspect_produk.empty:
            st.markdown('<div class="empty-hint">Belum ada data aspect sentiment.</div>', unsafe_allow_html=True)
        else:
            chart = (
                aspect_produk.pivot_table(
                    index="aspect", columns="sentiment", values="total", fill_value=0
                )
                .reset_index()
            )
            for col in ["Positive", "Neutral", "Negative"]:
                if col not in chart.columns:
                    chart[col] = 0

            chart["aspect_label"] = chart["aspect"].astype(str).str.title()
            chart["Total"] = chart["Positive"] + chart["Neutral"] + chart["Negative"]
            chart = chart.sort_values("Total", ascending=True)

            # Tampilkan top 5 aspek paling sering dibahas + sisanya tetap rapi di chart
            fig_aspect = px.bar(
                chart,
                y="aspect_label",
                x=["Positive", "Neutral", "Negative"],
                orientation="h",
                barmode="stack",
                color_discrete_map={
                    "Positive": "#10B981",
                    "Neutral": "#F59E0B",
                    "Negative": "#EF4444",
                },
            )
            fig_aspect.update_layout(
                height=max(380, len(chart) * 28),
                xaxis_title="Jumlah Penyebutan dalam Review",
                yaxis_title=None,
                legend_title=None,
                margin=dict(l=10, r=15, t=15, b=20),
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(family="Inter, sans-serif", color="#0F172A", size=12),
                xaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0"),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color="#0F172A"),
                ),
            )
            st.plotly_chart(
                fig_aspect,
                use_container_width=True,
                config={"displayModeBar": False, "responsive": True},
            )

    # Highlight Aspek Terkuat vs Terlemah dalam bentuk chip ringkas
    if not aspect_produk.empty:
        top_pos_df = chart[chart["Positive"] > chart["Negative"]].sort_values("Positive", ascending=False).head(6)
        top_neg_df = chart[chart["Negative"] > chart["Positive"]].sort_values("Negative", ascending=False).head(6)

        pos_chips = "".join(
            f'<span class="aspect-chip good">👍 {html.escape(r["aspect_label"])} (+{int(r["Positive"])})</span>'
            for _, r in top_pos_df.iterrows()
        ) or '<span style="color:#64748B;font-size:0.82rem;">Belum ada aspek dominan positif</span>'

        neg_chips = "".join(
            f'<span class="aspect-chip bad">👎 {html.escape(r["aspect_label"])} (-{int(r["Negative"])})</span>'
            for _, r in top_neg_df.iterrows()
        ) or '<span style="color:#64748B;font-size:0.82rem;">Belum ada aspek dominan negatif</span>'

        st.markdown(
            f"""
            <div class="aspect-summary-bar">
                <div class="aspect-pill-box">
                    <div class="aspect-pill-head good">🌟 Aspek Paling Dipuji</div>
                    <div class="chip-list">{pos_chips}</div>
                </div>
                <div class="aspect-pill-box">
                    <div class="aspect-pill-head bad">🔧 Aspek Paling Dikeluhkan</div>
                    <div class="chip-list">{neg_chips}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ===================================
    # 5. SPESIFIKASI LENGKAP
    # ===================================
    st.markdown(
        """
        <div class="section-header">
            <div class="section-label">⚙️ Spesifikasi Teknis Perangkat</div>
            <div class="section-sub">Detail perangkat keras & fitur bawaan</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if spek_row is None:
        st.info("Spesifikasi belum tersedia untuk produk ini.")
    else:
        items_html = ""
        for kolom_nama, (icon, label_bagus) in SPEK_LABELS.items():
            if kolom_nama in spek_row.index and pd.notna(spek_row[kolom_nama]):
                val_str = str(spek_row[kolom_nama]).strip()
                if val_str:
                    items_html += (
                        f'<div class="spek-item">'
                        f'<div class="spek-label">{icon} {html.escape(label_bagus)}</div>'
                        f'<div class="spek-value">{html.escape(val_str)}</div>'
                        f"</div>"
                    )
        st.markdown(f'<div class="spek-grid">{items_html}</div>', unsafe_allow_html=True)

    # ===================================
    # 6. REVIEW PENGGUNA (DENGAN FILTER SENTIMEN & KATA KUNCI)
    # ===================================
    st.markdown(
        """
        <div class="section-header">
            <div class="section-label">💬 Eksplorasi Ulasan Pengguna</div>
            <div class="section-sub">Filter berdasarkan kata kunci, sentimen, atau urutan waktu</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f_col1, f_col2, f_col3 = st.columns([2.2, 1.2, 1.2])
    with f_col1:
        cari_review = st.text_input(
            "cari_review",
            placeholder="🔎 Cari kata kunci di dalam ulasan (misal: battery, screen, camera, gaming)...",
            label_visibility="collapsed",
        )
    with f_col2:
        filter_sentimen = st.selectbox(
            "Filter Sentimen",
            options=["Semua Sentimen", "Positive", "Neutral", "Negative"],
            label_visibility="collapsed",
        )
    with f_col3:
        urutkan_review = st.selectbox(
            "Urutkan",
            options=["Terbaru", "Terlama", "Confidence Tertinggi"],
            label_visibility="collapsed",
        )

    tampil_review = review_produk.copy()
    if cari_review:
        tampil_review = tampil_review[
            tampil_review["review"].str.contains(cari_review, case=False, na=False)
            | tampil_review["aspects_list"].fillna("").str.contains(cari_review, case=False, na=False)
        ]
    if filter_sentimen != "Semua Sentimen":
        tampil_review = tampil_review[tampil_review["sentiment"] == filter_sentimen]

    if urutkan_review == "Terbaru":
        tampil_review = tampil_review.sort_values("tanggal", ascending=False, na_position="last")
    elif urutkan_review == "Terlama":
        tampil_review = tampil_review.sort_values("tanggal", ascending=True, na_position="last")
    elif urutkan_review == "Confidence Tertinggi":
        tampil_review = tampil_review.sort_values("confidence", ascending=False, na_position="last")

    if tampil_review.empty:
        st.markdown(
            '<div class="empty-hint">Tidak ada ulasan yang cocok dengan filter pencarian Anda.</div>',
            unsafe_allow_html=True,
        )
    else:
        jumlah_tampil = st.session_state.get("jumlah_review_tampil", 6)
        potongan_review = tampil_review.head(jumlah_tampil)

        sent_icon_map = {"Positive": "😊 Positive", "Neutral": "😐 Neutral", "Negative": "😞 Negative"}
        cards_html = []

        for _, r in potongan_review.iterrows():
            tgl = r["tanggal"].strftime("%d %b %Y") if pd.notna(r["tanggal"]) else "-"
            user_str = str(r["nama_user"]).strip() if pd.notna(r["nama_user"]) and str(r["nama_user"]).strip() else "Anonim"
            inisial = html.escape(user_str[0].upper())
            teks = html.escape(str(r["review"]).replace("\n", " ").strip())
            sent_val = r["sentiment"] if r["sentiment"] in sent_icon_map else "Neutral"
            sent_label = sent_icon_map[sent_val]
            src_str = html.escape(str(r["source"])) if pd.notna(r["source"]) else ""

            tags_html = ""
            if pd.notna(r["aspects_list"]) and str(r["aspects_list"]).strip():
                aspect_items = [a.strip() for a in str(r["aspects_list"]).split(",") if a.strip()]
                tags_badges = "".join(
                    f'<span class="review-tag">🏷️ {html.escape(a.title())}</span>'
                    for a in aspect_items[:6]
                )
                tags_html = f'<div class="review-tags">{tags_badges}</div>'

            cards_html.append(
                f'<div class="review-card">'
                f'  <div>'
                f'    <div class="review-head">'
                f'      <div class="review-user-wrap">'
                f'        <div class="review-avatar">{inisial}</div>'
                f'        <div>'
                f'          <div class="review-name">{html.escape(user_str)}</div>'
                f'          <div class="review-meta">{tgl} • {src_str}</div>'
                f'        </div>'
                f'      </div>'
                f'      <span class="sent-badge {sent_val}">{sent_label}</span>'
                f'    </div>'
                f'    <div class="review-text">{teks}</div>'
                f'  </div>'
                f'  {tags_html}'
                f'</div>'
            )

        st.markdown(
            f'<div class="review-grid">{"".join(cards_html)}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 0.75rem'></div>", unsafe_allow_html=True)
        if len(tampil_review) > jumlah_tampil:
            sisa = len(tampil_review) - jumlah_tampil
            btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
            with btn_col2:
                if st.button(f"👇 Tampilkan lebih banyak ulasan ({sisa} ulasan lagi)"):
                    st.session_state.jumlah_review_tampil = jumlah_tampil + 6
                    st.rerun()

# ---------------------------------------------------------
# HALAMAN KATALOG AWAL (KETIKA BELUM ADA PRODUK DIPILIH)
# ---------------------------------------------------------
else:
    st.markdown(
        """
        <div class="section-header">
            <div class="section-label">🗂️ Katalog Perangkat Tersedia</div>
            <div class="section-sub">Pilih salah satu perangkat di bawah atau gunakan kotak pencarian di atas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filter Kategori (Semua / Smartphone / Laptop) — responsif di Desktop & Mobile
    opsi_kat = ["✨ Semua (20)", "📱 Smartphone (10)", "💻 Laptop (10)"]
    map_kat = {
        "✨ Semua (20)": "Semua",
        "📱 Smartphone (10)": "Smartphone",
        "💻 Laptop (10)": "Laptop",
    }
    pilihan_label = st.radio(
        "Kategori Perangkat",
        options=opsi_kat,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.katalog_kategori = map_kat[pilihan_label]

    katalog_df = products_df.copy()
    if st.session_state.katalog_kategori != "Semua":
        katalog_df = katalog_df[
            katalog_df["category"].str.lower() == st.session_state.katalog_kategori.lower()
        ]

    # Precompute jumlah review & % positif per produk untuk kartu katalog
    rev_counts = reviews_df.groupby("product_id").size().to_dict()
    pos_counts = (
        sentiment_df[sentiment_df["sentiment"] == "Positive"]
        .set_index("product_id")["total"]
        .to_dict()
    )
    tot_sent_counts = sentiment_df.groupby("product_id")["total"].sum().to_dict()

    cols_per_row = 3
    rows = [katalog_df.iloc[i : i + cols_per_row] for i in range(0, len(katalog_df), cols_per_row)]

    for row_df in rows:
        grid_cols = st.columns(cols_per_row, gap="medium")
        for idx, (_, prod) in enumerate(row_df.iterrows()):
            pid = prod["id"]
            p_name = prod["name"]
            p_brand = prod["brand"]
            p_cat = prod["category"]
            p_icon = "💻" if p_cat.lower() == "laptop" else "📱"
            n_rev = rev_counts.get(pid, 0)
            n_pos = pos_counts.get(pid, 0)
            n_tot = tot_sent_counts.get(pid, 0)
            pct_pos = round((n_pos / n_tot) * 100) if n_tot > 0 else 0

            with grid_cols[idx]:
                st.markdown(
                    f"""
                    <div class="catalog-card">
                        <div class="catalog-top">
                            <span class="catalog-brand">{html.escape(p_brand)}</span>
                            <span class="catalog-cat">{p_icon} {html.escape(p_cat)}</span>
                        </div>
                        <div class="catalog-name" title="{html.escape(p_name)}">{html.escape(p_name)}</div>
                        <div class="catalog-stats">
                            <span>💬 <b>{n_rev}</b> review</span>
                            <span>😊 <b>{pct_pos}%</b> positif</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Lihat Analisis →", key=f"pilih_prod_{pid}"):
                    pilih_produk(pid)
                    st.rerun()
