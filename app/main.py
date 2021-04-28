from fastapi import FastAPI, Depends, status, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
import requests
import uvicorn
# from schemas import schemas
# from models import models
from db.database import engine, get_db
from sqlalchemy.orm import Session
from utils import reddit_api

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {
        'request': request})


@app.post("/", response_class=HTMLResponse)
def learn(request: Request, clicked: str = Form(...)):
    res = reddit_api.get_reddit(subreddit='todayilearned')
    post = res[0]['data']['children'][0]
    title = post['data']['title']
    score = post['data']['score']
    return templates.TemplateResponse('index.html', {
        'request': request, 'title': title, 'score': score})


if __name__ == "__main__":
    uvicorn.run('main:app', host='127.0.0.1', port=8080, reload=True)

