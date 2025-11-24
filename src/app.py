import asyncio
import sys

# Fix for Windows asyncio loop - Must be before other imports
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database import Article, Source, init_db
from scraper import NewsScraper
import plotly.express as px
from datetime import datetime, timedelta, date
import time

st.set_page_config(page_title="News Scraper & Analyzer", layout="wide", page_icon="📰")

# Database connection
Session = init_db()
session = Session()

def get_sources():
    return session.query(Source).all()

def get_articles(topic_filter=None, source_filter=None, sentiment_filter=None, date_range=None, category_filter=None):
    query = session.query(Article).order_by(desc(Article.published_date))
    
    if topic_filter:
        query = query.filter(Article.title.contains(topic_filter) | Article.content.contains(topic_filter))
    
    if source_filter:
        query = query.join(Source).filter(Source.name.in_(source_filter))
        
    if category_filter:
        # Join Source if not already joined (it might be joined by source_filter, but SQLAlchemy handles this usually or we can be explicit)
        # To be safe and simple, we can filter on Article.category if we trust it, or Source.category
        # Since we added category to Article, let's use that.
        query = query.filter(Article.category.in_(category_filter))
        
    if sentiment_filter:
        query = query.filter(Article.sentiment.in_(sentiment_filter))
        
    if date_range:
        # date_range is a tuple (start_date, end_date)
        if len(date_range) == 2:
            query = query.filter(Article.published_date >= date_range[0], Article.published_date <= date_range[1])

    return query.all()

# Custom CSS
st.markdown("""
<style>
    .article-card {
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .article-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
        text-decoration: none;
    }
    .article-meta {
        font-size: 0.85rem;
        color: #666;
        margin-bottom: 0.8rem;
    }
    .sentiment-badge {
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.75rem;
        font-weight: 600;
        color: white;
    }
    .sentiment-positive { background-color: #28a745; }
    .sentiment-negative { background-color: #dc3545; }
    .sentiment-neutral { background-color: #6c757d; }
</style>
""", unsafe_allow_html=True)

# Sidebar - Configuration & Actions
with st.sidebar:
    st.image("images/mrcb_logo.png", use_container_width=True)
    st.header("⚙️ Configuration")
    
    with st.expander("Add New Source"):
        new_name = st.text_input("Source Name")
        new_url = st.text_input("Source URL")
        requires_login = st.checkbox("Requires Login")
        include_external = st.checkbox("Include External Links (for aggregators like HN)", value=False)
        category = st.text_input("Category (e.g. Tech, Finance)", placeholder="Optional")
        
        login_url = ""
        username = ""
        password = ""
        u_selector = ""
        p_selector = ""
        
        if requires_login:
            login_url = st.text_input("Login URL")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            u_selector = st.text_input("Username CSS Selector")
            p_selector = st.text_input("Password CSS Selector")
        
        if st.button("Add Source"):
            if new_name and new_url:
                try:
                    new_source = Source(
                        name=new_name,
                        url=new_url,
                        requires_login=requires_login,
                        include_external=include_external,
                        category=category,
                        login_url=login_url,
                        username=username,
                        password=password,
                        username_selector=u_selector,
                        password_selector=p_selector
                    )
                    session.add(new_source)
                    session.commit()
                    st.success(f"Added {new_name}")
                    st.rerun()
                except Exception as e:
                    session.rollback()
                    if "UNIQUE constraint failed" in str(e):
                        st.error("A source with this URL already exists.")
                    else:
                        st.error(f"Error adding source: {e}")
            else:
                st.error("Name and URL are required")

    st.divider()

    with st.expander("Manage Sources"):
        sources = session.query(Source).all()
        if not sources:
            st.info("No sources added yet.")
        else:
            for source in sources:
                st.markdown(f"**{source.name}**")
                st.caption(f"{source.url}")

                # Edit: Category
                new_cat = st.text_input("Category", value=source.category if source.category else "", key=f"cat_{source.id}")
                if new_cat != (source.category if source.category else ""):
                    source.category = new_cat
                    session.commit()
                    st.success("Category updated!")
                    st.rerun()
                
                # Edit: Toggle External
                new_ext = st.checkbox("Include External", value=source.include_external, key=f"ext_{source.id}")
                if new_ext != source.include_external:
                    source.include_external = new_ext
                    session.commit()
                    st.success("Updated!")
                    st.rerun()
                
                # Delete
                if st.button("Delete", key=f"del_src_{source.id}"):
                    # Delete associated articles first
                    session.query(Article).filter_by(source_id=source.id).delete()
                    session.delete(source)
                    session.commit()
                    st.success(f"Deleted {source.name}")
                    st.rerun()
                st.divider()
    
    st.header("🚀 Actions")
    if st.button("Run Scraper", type="primary", width="stretch"):
        sources = get_sources()
        if not sources:
            st.warning("No sources configured.")
        else:
            with st.status("Scraping in progress...", expanded=True) as status:
                scraper = NewsScraper()
                progress_bar = st.progress(0)
                
                stats = {'count': 0}
                stats_placeholder = status.empty()
                
                def on_progress():
                    stats['count'] += 1
                    stats_placeholder.markdown(f"**Found {stats['count']} new articles...**")

                for i, source in enumerate(sources):
                    status.write(f"Scraping {source.name}...")
                    try:
                        scraper.scrape_source(source.id, on_progress=on_progress)
                    except Exception as e:
                        status.error(f"Error scraping {source.name}: {e}")
                    progress_bar.progress((i + 1) / len(sources))
                
                status.update(label=f"Scraping Complete! Found {stats['count']} new articles.", state="complete", expanded=False)
                scraper.close()
                time.sleep(1)
                st.rerun()

    if st.button("Clear All Data", type="secondary", width="stretch"):
        session.query(Article).delete()
        session.commit()
        st.success("Database cleared.")
        st.rerun()

# Main Dashboard
st.markdown("<p style='font-size: 14px; color: #666; margin-bottom: -10px;'>AI & Digital Transformation</p>", unsafe_allow_html=True)
st.title("📰 News Scraper & Analyzer")

# Filters
st.subheader("🔍 Filter & Explore")
c1, c2, c3, c4 = st.columns([2, 1, 1, 1])

with c1:
    search_query = st.text_input("Search Topics", placeholder="e.g. AI, Crypto, Politics")
with c2:
    available_sources = [s.name for s in get_sources()]
    source_filter = st.multiselect("Source", available_sources)
with c3:
    # Get unique categories
    categories = session.query(Source.category).distinct().all()
    available_categories = [c[0] for c in categories if c[0]]
    category_filter = st.multiselect("Category", available_categories)
    
    sentiment_filter = st.multiselect("Sentiment", ["Positive", "Neutral", "Negative"])
with c4:
    date_range = st.date_input("Date Range", [])

# Fetch Data (Filtered)
articles = get_articles(search_query, source_filter, sentiment_filter, date_range, category_filter)

# Top Metrics (Context-Aware)
total_articles = len(articles)
positive_count = len([a for a in articles if a.sentiment == 'Positive'])
negative_count = len([a for a in articles if a.sentiment == 'Negative'])

m1, m2, m3, m4 = st.columns(4)
m1.metric("Articles Found", total_articles)
m2.metric("Positive", positive_count, delta=f"{positive_count/total_articles*100:.1f}%" if total_articles else "0%")
m3.metric("Negative", negative_count, delta=f"-{negative_count/total_articles*100:.1f}%" if total_articles else "0%", delta_color="inverse")
m4.metric("Sources Active", len(set(a.source.name for a in articles if a.source)))

st.divider()

# Content Area
col_feed, col_charts = st.columns([2, 1])

with col_feed:
    st.subheader(f"Latest News ({len(articles)})")
    
    if not articles:
        st.info("No articles found matching your criteria.")
    
    for article in articles:
        sentiment_color = {
            "Positive": "sentiment-positive",
            "Negative": "sentiment-negative",
            "Neutral": "sentiment-neutral"
        }.get(article.sentiment, "sentiment-neutral")
        
        with st.container():
            st.markdown(f"""
            <div class="article-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <a href="{article.url}" target="_blank" class="article-title">{article.title}</a>
                    <span class="sentiment-badge {sentiment_color}">{article.sentiment}</span>
                </div>
                <div class="article-meta">
                    <span>📌 {article.source.name if article.source else 'Unknown'}</span>
                    <span style="background-color: #eee; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-left: 5px;">{article.category if article.category else 'Uncategorized'}</span> | 
                    <span>📅 {article.published_date.strftime('%Y-%m-%d %H:%M')}</span>
                </div>
                <p>{article.summary}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Delete button (Streamlit button needs to be outside HTML block)
            if st.button("Delete", key=f"del_{article.id}", help=f"Delete article {article.id}"):
                session.delete(article)
                session.commit()
                st.rerun()

with col_charts:
    st.subheader("📊 Analytics")
    
    # PDF Export
    from report_generator import create_pdf_report
    if articles:
        report_topic = search_query if search_query else "All Topics"
        pdf_data = create_pdf_report(articles, topic=report_topic)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_data,
            file_name=f"news_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    if articles:
        df = pd.DataFrame([{
            'Sentiment': a.sentiment,
            'Score': a.sentiment_score,
            'Source': a.source.name if a.source else 'Unknown',
            'Date': a.published_date.date()
        } for a in articles])
        
        # Sentiment Distribution
        fig_pie = px.pie(df, names='Sentiment', title='Sentiment Distribution', 
                         color='Sentiment', color_discrete_map={'Positive':'#28a745', 'Negative':'#dc3545', 'Neutral':'#6c757d'},
                         hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Sentiment by Source
        if len(df['Source'].unique()) > 1:
            fig_bar = px.histogram(df, x='Source', color='Sentiment', title='Sentiment by Source',
                                   color_discrete_map={'Positive':'#28a745', 'Negative':'#dc3545', 'Neutral':'#6c757d'})
            st.plotly_chart(fig_bar, use_container_width=True)




