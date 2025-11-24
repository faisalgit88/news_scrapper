from newspaper import Article as NewsArticle
from textblob import TextBlob
import nltk

# Download necessary NLTK data (quietly)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

def analyze_article(url, html_content=None):
    """
    Extracts summary and sentiment from an article.
    If html_content is provided, it uses that (useful if scraped via Playwright).
    Otherwise, it downloads from the URL (fallback).
    """
    article = NewsArticle(url)
    
    if html_content:
        article.set_html(html_content)
        article.parse()
    else:
        article.download()
        article.parse()
        
    try:
        article.nlp()
    except Exception:
        # Fallback if NLP fails or needs more data
        pass

    summary = article.summary
    if not summary:
        # Fallback summary if nlp() didn't produce one or failed
        summary = article.text[:500] + "..." if len(article.text) > 500 else article.text

    blob = TextBlob(article.text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        sentiment = "Positive"
    elif polarity < -0.1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
        
    return {
        "title": article.title,
        "text": article.text,
        "summary": summary,
        "sentiment": sentiment,
        "sentiment_score": polarity,
        "publish_date": article.publish_date
    }
