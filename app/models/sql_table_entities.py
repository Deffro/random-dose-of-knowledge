import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    reddit_post_id = Column(String)
    title = Column(String)
    score = Column(Integer)
    created = Column(String)
    upvote_ratio = Column(Float)
    thumbnail = Column(String)
    url = Column(String)
    permalink = Column(String)
    total_awards_received = Column(Integer)
    num_comments = Column(Integer)
    subreddit = Column(String)
    timestamp_accessed = Column(String)

