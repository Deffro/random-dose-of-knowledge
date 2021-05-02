import uvicorn
import pandas as pd
from utils import reddit_api
from sqlalchemy.orm import Session
from models import sql_table_entities
from db.database import engine, get_db
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Depends, status, Request, Form


app = FastAPI()  # initialize fastapi instance
templates = Jinja2Templates(directory='templates')  # define the templates directory for Jinja2 to look at
app.mount("/static", StaticFiles(directory="static"), name="static")  # define the directory for the static files
sql_table_entities.Base.metadata.create_all(engine)  # create all sql tables (empty) if they don't exist


# landing page. includes only the title, buttons and the plot
@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('index.html', {
        'request': request})


# page after getting the request from the form. it is the same directory as the index, so it basically reloads
# and displays new info on the page
@app.post("/", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def learn(request: Request, subreddit: str = Form('todayilearned'), db: Session = Depends(get_db)):
    # get the result of a request on the reddit api as json. a random post from the specified subreddit
    res = reddit_api.get_reddit(subreddit=subreddit)
    # get preprocessed post data as a dictionary
    data = reddit_api.get_post_details(res)
    # insert post data in sql table
    data_for_post = sql_table_entities.Post(reddit_post_id=data['reddit_post_id'], title=data['title'],
                                            score=data['score'], created=data['created'],
                                            upvote_ratio=data['upvote_ratio'], thumbnail=data['thumbnail'],
                                            url=data['url'],
                                            permalink=data['permalink'], num_comments=data['num_comments'],
                                            total_awards_received=data['total_awards_received'],
                                            subreddit=data['subreddit'], timestamp_accessed=data['timestamp_accessed'])
    db.add(data_for_post)
    db.commit()
    db.refresh(data_for_post)

    # read table of posts and create the cumulative plot in the static folder, so it will be rendered later in jinja
    posts = pd.read_sql('posts', engine)
    reddit_api.create_cumsum_plot(posts)

    # get preprocessed post comment data as a pd DataFrame
    comments = reddit_api.get_comments_details(res)

    # insert each comment in db
    for i, row in comments.iterrows():
        data_for_comment = sql_table_entities.Comment(reddit_comment_id=row['reddit_comment_id'],
                                                      score=row['score'], body=row['body'],
                                                      total_awards_received=row['total_awards_received'],
                                                      owner=data_for_post)  # for 1:N relationship
        db.add(data_for_comment)
        db.commit()
        db.refresh(data_for_comment)

    return templates.TemplateResponse('index.html', {
        'request': request, 'title': data['title'], 'score': data['score'], 'created': data['created'],
        'thumbnail': data['thumbnail'], 'url': data['url'],
        'upvote_ratio': data['upvote_ratio'], 'permalink': data['permalink'],
        'total_awards_received': data['total_awards_received'], 'num_comments': data['num_comments'],
        'comments': comments  # comments is a pd DataFrame. Everything else is a single value
    })


if __name__ == "__main__":
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=False, root_path="/")
