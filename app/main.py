from fastapi import FastAPI, Depends, status, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
import requests
import uvicorn
from schemas import schemas
from models import sql_table_entities
from db.database import engine, get_db
from sqlalchemy.orm import Session
from utils import reddit_api
import pandas as pd


app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")
sql_table_entities.Base.metadata.create_all(engine)


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {
        'request': request})


@app.post("/", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def learn(request: Request, subreddit: str = Form('todayilearned'), db: Session = Depends(get_db)):
    res = reddit_api.get_reddit(subreddit=subreddit)
    data = reddit_api.get_post_details(res)
    data_for_db = sql_table_entities.Post(reddit_post_id=data['reddit_post_id'], title=data['title'],
                                          score=data['score'], created=data['created'],
                                          upvote_ratio=data['upvote_ratio'], thumbnail=data['thumbnail'],
                                          url=data['url'],
                                          permalink=data['permalink'], num_comments=data['num_comments'],
                                          total_awards_received=data['total_awards_received'],
                                          subreddit=data['subreddit'], timestamp_accessed=data['timestamp_accessed'])
    db.add(data_for_db)
    db.commit()
    db.refresh(data_for_db)

    posts = pd.read_sql('posts', engine)
    reddit_api.create_cumsum_plot(posts)

    return templates.TemplateResponse('index.html', {
        'request': request, 'title': data['title'], 'score': data['score'], 'created': data['created'],
        'thumbnail': data['thumbnail'], 'url': data['url'],
        'upvote_ratio': data['upvote_ratio'], 'permalink': data['permalink'],
        'total_awards_received': data['total_awards_received'], 'num_comments': data['num_comments'],
        })


if __name__ == "__main__":
    uvicorn.run('main:app', host='127.0.0.1', port=8080, reload=True, root_path="/")

