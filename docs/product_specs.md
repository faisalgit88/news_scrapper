# Product Specifications: News Scraper & Analyzer

## 1. Overview
The News Scraper & Analyzer is a Python-based application designed to aggregate news articles from various sources, perform sentiment analysis, and present the data in an interactive dashboard. It supports dynamic websites using Playwright and offers categorization and filtering capabilities.

## 2. Technology Stack
- **Language**: Python 3.9+
- **User Interface**: Streamlit
- **Web Scraping**: Playwright (for dynamic content), BeautifulSoup (parsing)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Analysis**: TextBlob (Sentiment Analysis)
- **Visualization**: Plotly Express
- **Containerization**: Docker

## 3. Architecture
The application follows a modular structure:

- **`src/app.py`**: The main entry point and UI layer built with Streamlit. Handles user interaction, display, and configuration.
- **`src/scraper.py`**: Contains the `NewsScraper` class. Uses Playwright to navigate websites, handle logins, and extract article content.
- **`src/database.py`**: Defines the database schema and handles connection initialization.
- **`src/analyzer.py`**: Provides functions for analyzing article text (sentiment, summary).
- **`src/report_generator.py`**: Utility for generating PDF reports of scraped data.

## 4. Database Schema
The application uses a relational SQLite database (`data/news_data.db`) with two main tables:

### `sources`
Stores configuration for news websites.
- `id`: Integer, Primary Key
- `name`: String (e.g., "TechCrunch")
- `url`: String (Base URL)
- `requires_login`: Boolean
- `login_url`: String (Optional)
- `username`: String (Optional)
- `password`: String (Optional)
- `username_selector`: String (CSS selector for username field)
- `password_selector`: String (CSS selector for password field)
- `submit_selector`: String (CSS selector for submit button)
- `include_external`: Boolean (Follow links to external domains)
- `category`: String (e.g., "Tech", "Finance")

### `articles`
Stores scraped article data.
- `id`: Integer, Primary Key
- `title`: String
- `url`: String (Unique)
- `content`: Text
- `summary`: Text
- `published_date`: DateTime
- `source_id`: Integer (ForeignKey to `sources.id`)
- `sentiment`: String ("Positive", "Neutral", "Negative")
- `sentiment_score`: Float (-1.0 to 1.0)
- `category`: String (Inherited from Source)

## 5. Key Features
- **Dynamic Scraping**: Capable of scraping JavaScript-heavy websites and handling authentication.
- **Categorization**: Organize sources and articles by category (e.g., Tech, Politics).
- **Sentiment Analysis**: Automatically analyzes the tone of articles.
- **Interactive Dashboard**: Filter articles by source, category, sentiment, and date.
- **Source Management**: Add, edit, and delete news sources directly from the UI.
- **Background Processing**: Visual feedback during the scraping process.
