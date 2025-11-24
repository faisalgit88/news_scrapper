from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    login_url = Column(String, nullable=True)
    username_selector = Column(String, nullable=True)
    password_selector = Column(String, nullable=True)
    submit_selector = Column(String, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    requires_login = Column(Boolean, default=False)
    include_external = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    articles = relationship("Article", back_populates="source")

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True) # Positive, Neutral, Negative
    sentiment_score = Column(Integer, nullable=True) # -1 to 1 (scaled)
    category = Column(String, nullable=True)
    published_date = Column(DateTime, default=datetime.utcnow)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    source_id = Column(Integer, ForeignKey('sources.id'))
    source = relationship("Source", back_populates="articles")

def init_db(db_path=None):
    if db_path is None:
        # Default to ../data/news_data.db relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        db_path = f'sqlite:///{os.path.join(data_dir, "news_data.db")}'
        
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

if __name__ == "__main__":
    init_db()
