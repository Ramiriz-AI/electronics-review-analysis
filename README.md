# AI-Powered Electronics Review Analysis

An AI-powered web application for analyzing smartphone and laptop reviews using Natural Language Processing (NLP), sentiment analysis, aspect extraction, and Large Language Models (LLMs).

The application allows users to search for electronic products and explore product information, specifications, customer reviews, sentiment analysis results, aspect-based insights, and AI-generated summaries.

---

## Features

* Search for smartphone and laptop products
* Search suggestions while typing
* View product information
* View product specifications
* Display customer reviews
* Sentiment analysis of product reviews
* Aspect extraction from reviews
* Aspect-based sentiment analysis
* Sentiment visualization
* Identify product strengths and weaknesses
* AI-generated product review summaries
* Cached AI summaries stored in SQLite
* Interactive web dashboard built with Streamlit

---

## System Workflow

```text
Product & Review Data
        │
        ▼
SQLite Database
        │
        ▼
Text Preprocessing
        │
        ▼
Sentiment Analysis
        │
        ▼
Aspect Extraction
        │
        ▼
Aspect-Based Sentiment Analysis
        │
        ▼
AI Summary Generation
        │
        ▼
Store Results in SQLite
        │
        ▼
Streamlit Dashboard
```

---

## Technologies Used

### Programming Language

* Python

### Data Processing

* Pandas

### Database

* SQLite

### Natural Language Processing

* spaCy
* Hugging Face Transformers

### Sentiment Analysis Model

The project uses:

```text
cardiffnlp/twitter-roberta-base-sentiment-latest
```

The model classifies reviews into three sentiment categories:

* Positive
* Neutral
* Negative

### Aspect Extraction

Product aspects are extracted from reviews using spaCy.

Examples of extracted aspects include:

* Battery
* Camera
* Display
* Screen
* Performance
* RAM
* Storage
* Software
* Design
* Build
* Speaker

### Large Language Model

* Ollama
* Qwen

Qwen is used to generate product review summaries based on aspect-based sentiment analysis results.

### Dashboard

* Streamlit
* Plotly

---

## Sentiment Analysis

Customer reviews are processed and classified into three categories:

```text
Positive
Neutral
Negative
```

The sentiment analysis results are stored in the SQLite database and displayed in the dashboard.

---

## Aspect Extraction

The system extracts important product aspects from customer reviews.

For example:

```text
Review:
"The battery is good but the camera quality is disappointing."

Extracted Aspects:

- Battery
- Camera
```

The extracted aspects are then associated with sentiment information.

This allows the system to identify which parts of a product are commonly mentioned positively or negatively by users.

---

## Aspect-Based Analysis

The system analyzes sentiment distribution for each product aspect.

Example:

```text
Battery
Positive: 4
Neutral: 10
Negative: 15
```

Based on the sentiment comparison, the application can identify:

### Strengths

Aspects where positive sentiment is more dominant.

### Weaknesses

Aspects where negative sentiment is more dominant.

---

## AI-Generated Product Summary

The project uses Qwen to generate an AI summary based on aspect sentiment statistics.

The generated summary includes:

```text
Kelebihan
Kekurangan
Kesimpulan
```

To improve performance, generated summaries are stored in the SQLite database.

The application checks whether a summary already exists for a selected product.

```text
User Selects Product
        │
        ▼
Check product_summary
        │
        ▼
Summary Available?
       / \
      /   \
    Yes    No
     │      │
     ▼      ▼
Display   Generate
Summary   AI Summary
             │
             ▼
        Save to Database
```

For the deployed version of the application, previously generated summaries can be directly retrieved from the database without running the LLM again.

---

## Database Structure

The project uses SQLite as the main database.

Main tables include:

```text
products
reviews
sentiments
aspects
product_summary
```

### Products

Stores product information.

Example fields:

```text
id
name
brand
category
release_year
price
image_url
```

### Reviews

Stores customer reviews.

Example fields:

```text
id
product_id
username
review_date
review
source
language
```

### Sentiments

Stores sentiment analysis results for each review.

Example fields:

```text
review_id
sentiment
confidence
```

### Aspects

Stores extracted product aspects and their sentiment information.

Example fields:

```text
review_id
aspect
sentiment
```

### Product Summary

Stores AI-generated summaries.

Example fields:

```text
product_id
summary
```

---

## Project Structure

```text
electronics-review-analysis/
│
├── dashboard_hp/
│   └── app.py
│
├── database/
│   └── electronics_ai.db
│
├── script/
│   ├── create_database.py
│   ├── preprocessing.py
│   ├── sentiment.py
│   ├── aspect.py
│   ├── ai_summary.py
│   └── qwen_summary.py
│
├── data/
│   ├── hp/
│   └── laptop/
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

Move into the project directory:

```bash
cd YOUR_REPOSITORY
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run dashboard_hp/app.py
```

---

## Requirements

For the deployed dashboard, the main dependencies are:

```text
streamlit
pandas
plotly
```

The complete NLP and AI processing pipeline may additionally use:

```text
transformers
torch
spacy
tqdm
ollama
```

The RoBERTa model is used during sentiment analysis, spaCy is used for aspect extraction, and Qwen is used for AI summary generation.

---

## Dashboard Features

Users can:

1. Search for a smartphone or laptop.
2. Select a product from search suggestions.
3. View product information.
4. View product specifications.
5. Read customer reviews.
6. View sentiment analysis results.
7. Explore aspect-based sentiment insights.
8. Identify product strengths and weaknesses.
9. Read an AI-generated product summary.

---

## Example Application Flow

```text
User Searches "ASU"
        │
        ▼
Search Suggestions
        │
        ▼
ASUS Laptop / ASUS Smartphone
        │
        ▼
User Selects Product
        │
        ├── Product Information
        │
        ├── Specifications
        │
        ├── Customer Reviews
        │
        ├── Sentiment Analysis
        │
        ├── Aspect Analysis
        │
        └── AI Summary
```

---

## Future Improvements

Possible future improvements include:

* Support for additional electronics categories
* Real-time review collection
* Improved aspect extraction
* More accurate aspect-based sentiment analysis
* Product comparison features
* Product recommendation system
* Cloud-based LLM integration
* User authentication
* Advanced analytics and filtering

---

## Author

**Ramiriz**

Computer Science Student

---

## Project Purpose

This project was developed as a portfolio project to explore the integration of:

* Database systems
* Natural Language Processing
* Sentiment Analysis
* Aspect Extraction
* Large Language Models
* Data Visualization
* Interactive Web Applications

The project demonstrates an end-to-end workflow, from raw product review data processing to AI-powered insights displayed through an interactive dashboard.
