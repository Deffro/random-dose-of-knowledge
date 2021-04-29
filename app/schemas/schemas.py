from pydantic import BaseModel
from typing import Optional


class Post(BaseModel):
    title: str
    score: int
    created: str
    upvote_ratio: float
    thumbnail: str
    url_overridden_by_dest: str
    total_awards_received: int

    class Config:
        orm_mode = True

class Blog_title(BaseModel):
    title: str

    class Config:
        orm_mode = True
